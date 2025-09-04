/**
 * 차트 관련 유틸리티 함수들
 */

/**
 * 레이더 차트 데이터를 생성합니다
 * @param {Array} labels - 라벨 배열
 * @param {Array} data - 데이터 배열
 * @returns {Object} 레이더 차트 데이터
 */
export const createRadarChartData = (labels, data) => {
  return {
    labels,
    datasets: [{
      label: '분석 점수',
      data,
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderColor: '#3b82f6',
      borderWidth: 2,
      pointBackgroundColor: '#3b82f6',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 5
    }]
  };
};

/**
 * 바 차트 데이터를 생성합니다
 * @param {Object} analysisData - 분석 데이터
 * @returns {Object} 바 차트 데이터
 */
export const createBarChartData = (analysisData) => {
  const labels = [];
  const data = [];
  const colors = [];

  Object.entries(analysisData).forEach(([key, value]) => {
    if (value && typeof value === 'object' && 'score' in value) {
      labels.push(getAnalysisLabel(key));
      data.push(value.score);
      colors.push(getScoreColor(value.score));
    }
  });

  return {
    labels,
    datasets: [{
      label: '점수',
      data,
      backgroundColor: colors,
      borderColor: colors,
      borderWidth: 1
    }]
  };
};

/**
 * 점수에 따른 색상을 반환합니다
 * @param {number} score - 점수
 * @returns {string} 색상 코드
 */
export const getScoreColor = (score) => {
  if (score >= 8) return '#16a34a'; // 녹색
  if (score >= 6) return '#f59e0b'; // 노란색
  if (score >= 4) return '#f97316'; // 주황색
  return '#dc2626'; // 빨간색
};

/**
 * 점수에 따른 그라데이션을 반환합니다
 * @param {number} score - 점수
 * @returns {string} 그라데이션 CSS
 */
export const getScoreGradient = (score) => {
  if (score >= 8) {
    return 'linear-gradient(135deg, #16a34a, #22c55e)';
  } else if (score >= 6) {
    return 'linear-gradient(135deg, #f59e0b, #fbbf24)';
  } else if (score >= 4) {
    return 'linear-gradient(135deg, #f97316, #fb923c)';
  } else {
    return 'linear-gradient(135deg, #dc2626, #ef4444)';
  }
};

/**
 * 분석 항목 라벨을 가져옵니다
 * @param {string} key - 분석 항목 키
 * @returns {string} 라벨
 */
const getAnalysisLabel = (key) => {
  const labels = {
    motivation_relevance: '지원 동기',
    technical_suitability: '기술적 적합성',
    job_understanding: '직무 이해도',
    growth_potential: '성장 가능성',
    teamwork_communication: '팀워크 및 소통'
  };

  return labels[key] || key;
};
