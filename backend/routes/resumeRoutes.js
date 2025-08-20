const express = require('express');
const router = express.Router();
const Resume = require('../models/Resume');

// 더미 데이터 초기화
const initializeDummyData = async () => {
  try {
    const count = await Resume.countDocuments();
    if (count === 0) {
      const dummyData = [
        {
          name: '김철수',
          position: '프론트엔드 개발자',
          department: '개발팀',
          experience: '3년',
          skills: 'React, TypeScript, JavaScript, HTML/CSS, Node.js',
          summary: '프론트엔드 개발 경험 3년으로 React와 TypeScript를 주로 사용하여 웹 애플리케이션을 개발했습니다. 사용자 경험을 중시하며, 반응형 디자인과 성능 최적화에 능숙합니다. 팀 프로젝트에서 협업 경험이 풍부하며, 새로운 기술 학습에 적극적입니다.',
          analysisScore: 85,
          analysisResult: '기술 스택이 요구사항과 잘 맞으며, 프로젝트 경험이 풍부합니다.'
        },
        {
          name: '이영희',
          position: '백엔드 개발자',
          department: '개발팀',
          experience: '5년',
          skills: 'Java, Spring Boot, MySQL, Redis, Docker, AWS',
          summary: '백엔드 개발 경험 5년으로 Java와 Spring Boot를 주로 사용하여 안정적인 서버 애플리케이션을 구축했습니다. 데이터베이스 설계와 API 설계 경험이 풍부하며, 마이크로서비스 아키텍처에 대한 이해가 깊습니다. 성능 최적화와 보안에 중점을 두고 개발합니다.',
          analysisScore: 92,
          analysisResult: '시스템 설계 경험이 뛰어나고, 성능 최적화 능력이 우수합니다.'
        },
        {
          name: '박민수',
          position: 'UI/UX 디자이너',
          department: '디자인팀',
          experience: '2년',
          skills: 'Figma, Adobe XD, Photoshop, Illustrator, Sketch',
          summary: 'UI/UX 디자인 경험 2년으로 사용자 중심의 디자인을 추구합니다. Figma와 Adobe XD를 주로 사용하여 프로토타입을 제작하며, 사용자 리서치와 테스트를 통해 지속적으로 개선합니다. 브랜드 아이덴티티와 일관성 있는 디자인 시스템 구축에 능숙합니다.',
          analysisScore: 78,
          analysisResult: '창의적인 디자인 감각을 보유하고 있으며, 사용자 경험에 대한 이해가 깊습니다.'
        },
        {
          name: '정수진',
          position: '데이터 엔지니어',
          department: '데이터팀',
          experience: '4년',
          skills: 'Python, SQL, Apache Spark, Hadoop, AWS, Tableau',
          summary: '데이터 엔지니어링 경험 4년으로 대용량 데이터 처리와 분석 파이프라인 구축에 전문성을 가지고 있습니다. Python과 SQL을 주로 사용하며, 클라우드 환경에서의 데이터 처리 시스템 설계 경험이 풍부합니다. 비즈니스 인사이트 도출을 위한 데이터 시각화에도 능숙합니다.',
          analysisScore: 88,
          analysisResult: '데이터 처리 능력이 뛰어나며, 분석 파이프라인 구축 경험이 풍부합니다.'
        }
      ];

      await Resume.insertMany(dummyData);
      console.log('더미 데이터가 성공적으로 추가되었습니다.');
    }
  } catch (error) {
    console.error('더미 데이터 초기화 중 오류:', error);
  }
};

// 모든 이력서 조회
router.get('/', async (req, res) => {
  try {
    // 더미 데이터 초기화 확인
    await initializeDummyData();
    
    const resumes = await Resume.find().sort({ createdAt: -1 });
    res.json(resumes);
  } catch (error) {
    res.status(500).json({ message: '이력서 조회 중 오류가 발생했습니다.', error: error.message });
  }
});

// 특정 이력서 조회
router.get('/:id', async (req, res) => {
  try {
    const resume = await Resume.findById(req.params.id);
    if (!resume) {
      return res.status(404).json({ message: '이력서를 찾을 수 없습니다.' });
    }
    res.json(resume);
  } catch (error) {
    res.status(500).json({ message: '이력서 조회 중 오류가 발생했습니다.', error: error.message });
  }
});

// 새 이력서 생성
router.post('/', async (req, res) => {
  try {
    const { name, position, department, experience, skills, summary } = req.body;
    
    const newResume = new Resume({
      name,
      position,
      department,
      experience,
      skills,
      summary
    });

    const savedResume = await newResume.save();
    res.status(201).json(savedResume);
  } catch (error) {
    res.status(400).json({ message: '이력서 생성 중 오류가 발생했습니다.', error: error.message });
  }
});

// 이력서 수정
router.put('/:id', async (req, res) => {
  try {
    const { name, position, department, experience, skills, summary } = req.body;
    
    const updatedResume = await Resume.findByIdAndUpdate(
      req.params.id,
      {
        name,
        position,
        department,
        experience,
        skills,
        summary
      },
      { new: true, runValidators: true }
    );

    if (!updatedResume) {
      return res.status(404).json({ message: '이력서를 찾을 수 없습니다.' });
    }

    res.json(updatedResume);
  } catch (error) {
    res.status(400).json({ message: '이력서 수정 중 오류가 발생했습니다.', error: error.message });
  }
});

// 이력서 삭제
router.delete('/:id', async (req, res) => {
  try {
    const deletedResume = await Resume.findByIdAndDelete(req.params.id);
    
    if (!deletedResume) {
      return res.status(404).json({ message: '이력서를 찾을 수 없습니다.' });
    }

    res.json({ message: '이력서가 성공적으로 삭제되었습니다.' });
  } catch (error) {
    res.status(500).json({ message: '이력서 삭제 중 오류가 발생했습니다.', error: error.message });
  }
});

module.exports = router; 