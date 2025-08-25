// 평균 점수 계산 함수
export const calculateAverageScore = (analysisData) => {
  if (!analysisData || typeof analysisData !== 'object') return 0;

  const scores = Object.values(analysisData)
    .filter(item => item && typeof item === 'object' && 'score' in item)
    .map(item => item.score);

  if (scores.length === 0) return 0;

  const total = scores.reduce((sum, score) => sum + score, 0);
  return Math.round((total / scores.length) * 10) / 10; // 소수점 첫째자리까지
};

// 이력서 분석 항목 라벨 함수
export const getResumeAnalysisLabel = (key) => {
  const labels = {
    basic_info_completeness: '기본정보 완성도',
    job_relevance: '직무 적합성',
    experience_clarity: '경력 명확성',
    tech_stack_clarity: '기술스택 명확성',
    project_recency: '프로젝트 최신성',
    achievement_metrics: '성과 지표',
    readability: '가독성',
    typos_and_errors: '오탈자',
    update_freshness: '최신성'
  };
  return labels[key] || key;
};

// 자기소개서 분석 항목 라벨 함수
export const getCoverLetterAnalysisLabel = (key) => {
  const labels = {
    motivation_relevance: '지원 동기',
    problem_solving_STAR: 'STAR 기법',
    quantitative_impact: '정량적 성과',
    job_understanding: '직무 이해도',
    unique_experience: '차별화 경험',
    logical_flow: '논리적 흐름',
    keyword_diversity: '키워드 다양성',
    sentence_readability: '문장 가독성',
    typos_and_errors: '오탈자'
  };
  return labels[key] || key;
};

// 포트폴리오 분석 항목 라벨 함수
export const getPortfolioAnalysisLabel = (key) => {
  const labels = {
    project_overview: '프로젝트 개요',
    tech_stack: '기술 스택',
    personal_contribution: '개인 기여도',
    achievement_metrics: '성과 지표',
    visual_quality: '시각적 품질',
    documentation_quality: '문서화 품질',
    job_relevance: '직무 관련성',
    unique_features: '독창적 기능',
    maintainability: '유지보수성'
  };
  return labels[key] || key;
};

// 상태 텍스트 매핑 함수
export const getStatusText = (status) => {
  const statusMap = {
    'pending': '보류',
    'approved': '최종합격',
    'rejected': '서류불합격',
    'reviewed': '서류합격',
    'reviewing': '보류',
    'passed': '서류합격',
    'interview_scheduled': '최종합격',
    '서류합격': '서류합격',
    '최종합격': '최종합격',
    '서류불합격': '서류불합격',
    '보류': '보류'
  };
  return statusMap[status] || '보류';
};

// 분석 데이터에서 스킬 추출
export const extractSkillsFromAnalysis = (analysisData, documentType) => {
  if (!analysisData || !analysisData.skills) return [];

  const skills = analysisData.skills;
  if (Array.isArray(skills)) {
    return skills;
  } else if (typeof skills === 'string') {
    return skills.split(',').map(skill => skill.trim()).filter(skill => skill);
  }

  return [];
};

// 분석 데이터에서 경력 추출
export const extractExperienceFromAnalysis = (analysisData, documentType) => {
  if (!analysisData || !analysisData.experience) return '';

  const experience = analysisData.experience;
  if (typeof experience === 'string') {
    return experience;
  } else if (typeof experience === 'object' && experience.text) {
    return experience.text;
  }

  return '';
};

// 분석 데이터에서 교육 추출
export const extractEducationFromAnalysis = (analysisData, documentType) => {
  if (!analysisData || !analysisData.education) return '';

  const education = analysisData.education;
  if (typeof education === 'string') {
    return education;
  } else if (typeof education === 'object' && education.text) {
    return education.text;
  }

  return '';
};

// 분석 데이터에서 추천사항 추출
export const extractRecommendationsFromAnalysis = (analysisData, documentType) => {
  if (!analysisData || !analysisData.recommendations) return [];

  const recommendations = analysisData.recommendations;
  if (Array.isArray(recommendations)) {
    return recommendations;
  } else if (typeof recommendations === 'string') {
    return recommendations.split('\n').filter(rec => rec.trim());
  }

  return [];
};
