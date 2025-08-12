/**
 * 자소서 분석 관련 유틸리티 함수들
 */

/**
 * 자소서 분석 데이터에서 기술 스택 정보를 추출합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {Array} 기술 스택 관련 피드백 배열
 */
export const extractSkillsFromCoverLetter = (analysisData) => {
  const skills = [];
  
  if (analysisData?.cover_letter_analysis) {
    const { cover_letter_analysis } = analysisData;
    
    // 키워드 다양성에서 기술 관련 피드백 추출
    if (cover_letter_analysis.keyword_diversity?.feedback) {
      skills.push(cover_letter_analysis.keyword_diversity.feedback);
    }
    
    // 직무 이해도에서 기술 관련 피드백 추출
    if (cover_letter_analysis.job_understanding?.feedback) {
      skills.push(cover_letter_analysis.job_understanding.feedback);
    }
  }
  
  return skills.length > 0 ? skills : ['기술 스택 정보를 추출할 수 없습니다.'];
};

/**
 * 자소서 분석 데이터에서 경험 정보를 추출합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {string} 경험 관련 피드백 문자열
 */
export const extractExperienceFromCoverLetter = (analysisData) => {
  const experiences = [];
  
  if (analysisData?.cover_letter_analysis) {
    const { cover_letter_analysis } = analysisData;
    
    // 독특한 경험에서 피드백 추출
    if (cover_letter_analysis.unique_experience?.feedback) {
      experiences.push(cover_letter_analysis.unique_experience.feedback);
    }
    
    // 경력 일치도에서 피드백 추출
    if (cover_letter_analysis.career_alignment?.feedback) {
      experiences.push(cover_letter_analysis.career_alignment.feedback);
    }
  }
  
  return experiences.length > 0 ? experiences.join(' ') : '경력 정보를 추출할 수 없습니다.';
};

/**
 * 자소서 분석 데이터에서 교육/학력 정보를 추출합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {string} 교육 관련 피드백 문자열
 */
export const extractEducationFromCoverLetter = (analysisData) => {
  if (analysisData?.cover_letter_analysis?.job_understanding?.feedback) {
    return analysisData.cover_letter_analysis.job_understanding.feedback;
  }
  return '학력 정보를 추출할 수 없습니다.';
};

/**
 * 자소서 분석 데이터에서 추천사항을 추출합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {Array} 추천사항 배열
 */
export const extractRecommendationsFromCoverLetter = (analysisData) => {
  if (analysisData?.cover_letter_analysis) {
    const itemCount = Object.keys(analysisData.cover_letter_analysis).length;
    const totalScore = analysisData.overall_summary.total_score;
    return [`자기소개서 분석 완료: 총 ${itemCount}개 항목 분석, 평균 점수 ${totalScore}/10점`];
  }
  
  return ['자기소개서 분석이 완료되었습니다.'];
};

/**
 * 자소서 분석 점수를 색상으로 변환합니다.
 * @param {number} score - 분석 점수 (0-10)
 * @returns {string} 색상 코드
 */
export const getCoverLetterScoreColor = (score) => {
  if (score >= 8.5) return '#10B981'; // Green
  if (score >= 7.0) return '#F59E0B'; // Yellow
  if (score >= 5.0) return '#EF4444'; // Red
  return '#6B7280'; // Gray
};

/**
 * 자소서 분석 점수에 따른 아이콘을 반환합니다.
 * @param {number} score - 분석 점수 (0-10)
 * @returns {string} 아이콘 이름
 */
export const getCoverLetterScoreIcon = (score) => {
  if (score >= 8.5) return 'excellent';
  if (score >= 7.0) return 'good';
  if (score >= 5.0) return 'warning';
  return 'poor';
};

/**
 * 자소서 분석 항목의 한국어 이름을 반환합니다.
 * @param {string} key - 분석 항목 키
 * @returns {string} 한국어 이름
 */
export const getCoverLetterItemName = (key) => {
  const itemNames = {
    // 현업 IT기업 자소서 평가 항목
    'tech_fit': '기술 적합성 (Tech Fit)',
    'job_understanding': '직무 이해도',
    'growth_potential': '성장 가능성',
    'teamwork_communication': '팀워크/커뮤니케이션',
    'motivation_company_fit': '동기/회사 이해도',
    'problem_solving': '문제 해결 능력',
    'performance_orientation': '성과 지향성',
    'grammar_expression': '문법 및 표현',
    
    // 기존 항목들 (하위 호환성 유지)
    'job_understanding': '직무 이해도',
    'unique_experience': '독특한 경험',
    'keyword_diversity': '키워드 다양성',
    'motivation_clarity': '동기 명확성',
    'writing_quality': '작성 품질',
    'career_alignment': '경력 일치도',
    'company_research': '회사 조사',
    'future_vision': '미래 비전',
    'communication_style': '소통 스타일'
  };
  
  return itemNames[key] || key;
};

/**
 * 자소서 분석 결과의 요약 정보를 생성합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {Object} 요약 정보 객체
 */
export const generateCoverLetterSummary = (analysisData) => {
  if (!analysisData?.cover_letter_analysis) {
    return {
      totalItems: 0,
      averageScore: 0,
      strengths: [],
      weaknesses: [],
      recommendations: []
    };
  }
  
  const { cover_letter_analysis, overall_summary } = analysisData;
  const items = Object.entries(cover_letter_analysis);
  
  const strengths = items
    .filter(([_, item]) => item.score >= 8.0)
    .map(([key, item]) => ({
      category: getCoverLetterItemName(key),
      score: item.score,
      feedback: item.feedback
    }));
  
  const weaknesses = items
    .filter(([_, item]) => item.score < 6.0)
    .map(([key, item]) => ({
      category: getCoverLetterItemName(key),
      score: item.score,
      feedback: item.feedback
    }));
  
  const recommendations = weaknesses.map(item => 
    `${item.category} 개선: ${item.feedback}`
  );
  
  return {
    totalItems: items.length,
    averageScore: overall_summary.total_score,
    strengths,
    weaknesses,
    recommendations
  };
};

/**
 * 자소서 분석 결과를 CSV 형식으로 변환합니다.
 * @param {Object} analysisData - 분석 결과 데이터
 * @returns {string} CSV 문자열
 */
export const exportCoverLetterAnalysisToCSV = (analysisData) => {
  if (!analysisData?.cover_letter_analysis) {
    return '';
  }
  
  const { cover_letter_analysis, overall_summary } = analysisData;
  const items = Object.entries(cover_letter_analysis);
  
  let csv = '항목,점수,피드백\n';
  csv += `전체 평점,${overall_summary.total_score},자기소개서 분석 결과\n`;
  
  items.forEach(([key, item]) => {
    const itemName = getCoverLetterItemName(key);
    csv += `${itemName},${item.score},${item.feedback}\n`;
  });
  
  return csv;
};
