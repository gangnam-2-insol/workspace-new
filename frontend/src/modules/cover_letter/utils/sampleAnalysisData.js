/**
 * 자소서 분석 샘플 데이터
 */

export const sampleAnalysisData = {
  overallScore: 8.2,
  analyzedAt: "2024-01-15T10:30:00Z",
  analysisResult: {
    motivation_relevance: {
      score: 8,
      feedback: "지원 동기가 명확하고 구체적으로 표현되었습니다. 회사의 비전과 개인의 목표가 잘 연결되어 있습니다."
    },
    technical_suitability: {
      score: 7,
      feedback: "기술적 경험이 잘 드러나지만 더 구체적인 사례가 필요합니다. 프로젝트 경험을 더 자세히 설명하면 좋겠습니다."
    },
    job_understanding: {
      score: 9,
      feedback: "직무에 대한 이해도가 매우 높습니다. 업무 내용과 요구사항을 정확히 파악하고 있습니다."
    },
    growth_potential: {
      score: 8,
      feedback: "학습 의지와 성장 가능성이 뛰어납니다. 새로운 기술에 대한 관심과 적극적인 태도가 돋보입니다."
    },
    teamwork_communication: {
      score: 7,
      feedback: "협업 경험이 잘 드러나지만 구체적인 소통 사례를 추가하면 더욱 좋겠습니다."
    }
  },
  recommendations: [
    {
      category: "technical_suitability",
      label: "기술적 적합성",
      score: 7,
      priority: "medium",
      message: "기술적 적합성 영역을 더욱 강화할 수 있습니다. (7/10점)"
    },
    {
      category: "teamwork_communication",
      label: "팀워크 및 소통",
      score: 7,
      priority: "medium",
      message: "팀워크 및 소통 영역을 더욱 강화할 수 있습니다. (7/10점)"
    }
  ],
  detailedAnalysis: "전반적으로 우수한 자소서입니다. 지원 동기가 명확하고 직무 이해도가 높으며, 성장 가능성도 뛰어납니다. 기술적 경험과 팀워크 관련 내용을 더 구체적으로 보완하면 완벽한 자소서가 될 것입니다."
};

export const sampleValidationData = {
  validationScore: 85,
  wordCount: 1200,
  charCount: 1150,
  lengthStatus: "good",
  structure: {
    paragraphCount: 5,
    sentenceCount: 25,
    avgParagraphLength: 240,
    avgSentenceLength: 48
  },
  grammarErrors: [],
  keywordAnalysis: {
    total: 7,
    matched: 5,
    matchRate: 71
  },
  plagiarismScore: 15,
  suspicionLevel: "LOW"
};
