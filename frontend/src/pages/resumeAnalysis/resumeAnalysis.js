const express = require('express');
const router = express.Router();
const { OpenAI } = require('openai');
const mongoose = require('mongoose');
const Resume = require('../models/Resume'); // Resume 모델

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// 회사 인재상/자격요건 RAG 예시 (실제론 DB나 파일에서 불러옴)
const departmentRequirements = {
  '프론트엔드': 'React, TypeScript, UI/UX 경험',
  '백엔드': 'Node.js, MongoDB, REST API 설계',
  // ... 기타 부서
};
const companyValues = '창의성, 협업, 성장 의지';

router.post('/analysis', async (req, res) => {
  const { resumeId, resumeText, department } = req.body;
  try {
    // RAG: 부서별 요구사항 + 회사 인재상
    const prompt = `
      아래는 회사의 인재상과 ${department} 부서의 자격요건입니다.
      [인재상] ${companyValues}
      [${department} 자격요건] ${departmentRequirements[department] || ''}
      아래 지원자의 이력서/자소서가 얼마나 부합하는지 100점 만점으로 평가하고, 근거를 설명해줘.
      [지원자 이력서/자소서]
      ${resumeText}
    `;

    // OpenAI API 호출
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 512,
    });

    // 결과 파싱 (예시: "점수: 87, 근거: ...")
    const resultText = completion.choices[0].message.content;
    const scoreMatch = resultText.match(/점수[:：]?\s?(\d+)/);
    const score = scoreMatch ? parseInt(scoreMatch[1], 10) : null;

    // MongoDB 저장
    await Resume.findByIdAndUpdate(resumeId, {
      analysisScore: score,
      analysisResult: resultText,
      analyzedAt: new Date()
    });

    res.json({ score, resultText });
  } catch (err) {
    res.status(500).json({ error: '분석 실패', details: err.message });
  }
});

module.exports = router;