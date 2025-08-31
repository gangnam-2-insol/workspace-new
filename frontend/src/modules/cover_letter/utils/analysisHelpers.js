/**
 * 자소서 분석 관련 유틸리티 함수들
 */

import { ANALYSIS_LABELS, SCORE_GRADES } from '../types/coverLetterTypes';

/**
 * 분석 데이터에서 전체 점수를 계산합니다
 * @param {Object} analysisData - 분석 데이터
 * @returns {number} 전체 점수
 */
export const calculateOverallScore = (analysisData) => {
  if (!analysisData) return 0;

  let analysisResult = null;

  // 다양한 데이터 구조 지원
  if (analysisData.analysis_result) {
    analysisResult = analysisData.analysis_result;
  } else if (analysisData.analysis) {
    analysisResult = analysisData.analysis;
  } else if (analysisData.cover_letter_analysis) {
    analysisResult = analysisData.cover_letter_analysis;
  } else {
    analysisResult = analysisData;
  }

  if (!analysisResult) return 0;

  const scores = Object.values(analysisResult)
    .filter(item => item && typeof item === 'object' && 'score' in item)
    .map(item => item.score);

  if (scores.length === 0) return 8; // 기본값

  const total = scores.reduce((sum, score) => sum + score, 0);
  return Math.round((total / scores.length) * 10) / 10;
};

/**
 * 분석 항목의 라벨을 가져옵니다
 * @param {string} key - 분석 항목 키
 * @returns {string} 라벨
 */
export const getAnalysisLabel = (key) => {
  return ANALYSIS_LABELS[key] || key;
};

/**
 * 점수에 따른 등급을 가져옵니다
 * @param {number} score - 점수
 * @returns {Object} 등급 정보
 */
export const getScoreGrade = (score) => {
  for (const [grade, info] of Object.entries(SCORE_GRADES)) {
    if (score >= info.min && score <= info.max) {
      return { grade, ...info };
    }
  }
  return { grade: 'UNKNOWN', label: '알 수 없음', color: '#6c757d' };
};

/**
 * 분석 데이터를 차트용 데이터로 변환합니다
 * @param {Object} analysisData - 분석 데이터
 * @returns {Object} 차트 데이터
 */
export const convertToChartData = (analysisData) => {
  if (!analysisData) return { labels: [], data: [] };

  let analysisResult = null;

  // 다양한 데이터 구조 지원
  if (analysisData.analysis_result) {
    analysisResult = analysisData.analysis_result;
  } else if (analysisData.analysis) {
    analysisResult = analysisData.analysis;
  } else if (analysisData.cover_letter_analysis) {
    analysisResult = analysisData.cover_letter_analysis;
  } else {
    analysisResult = analysisData;
  }

  if (!analysisResult) return { labels: [], data: [] };

  // 분석 항목을 시계 방향 순서로 정렬 (12시부터 시작)
  const analysisOrder = [
    'motivation_relevance',      // 12시 방향 (상단)
    'technical_suitability',     // 2시 방향 (우상단)
    'job_understanding',         // 4시 방향 (우하단)
    'growth_potential',          // 8시 방향 (좌하단)
    'teamwork_communication'     // 10시 방향 (좌상단)
  ];

  const labels = [];
  const data = [];

  // 고정된 순서로 데이터 처리
  analysisOrder.forEach(key => {
    const value = analysisResult[key];
    if (value && typeof value === 'object' && 'score' in value) {
      labels.push(getAnalysisLabel(key));
      data.push(value.score);
    }
  });

  // 나머지 항목들도 추가 (순서가 없는 경우)
  Object.entries(analysisResult).forEach(([key, value]) => {
    if (!analysisOrder.includes(key) && value && typeof value === 'object' && 'score' in value) {
      labels.push(getAnalysisLabel(key));
      data.push(value.score);
    }
  });

  return { labels, data };
};

/**
 * 분석 데이터를 정리하고 표준화합니다
 * @param {Object} rawData - 원본 분석 데이터
 * @returns {Object} 정리된 분석 데이터
 */
export const normalizeAnalysisData = (rawData) => {
  if (!rawData) return null;

  let analysisResult = null;

  // 다양한 데이터 구조 지원
  if (rawData.analysis_result) {
    analysisResult = rawData.analysis_result;
  } else if (rawData.analysis) {
    analysisResult = rawData.analysis;
  } else if (rawData.cover_letter_analysis) {
    analysisResult = rawData.cover_letter_analysis;
  } else {
    analysisResult = rawData;
  }

  return analysisResult;
};

/**
 * 분석 항목별 피드백을 가져옵니다
 * @param {Object} analysisData - 분석 데이터
 * @param {string} category - 분석 카테고리
 * @returns {string} 피드백
 */
export const getCategoryFeedback = (analysisData, category) => {
  const normalizedData = normalizeAnalysisData(analysisData);
  if (!normalizedData || !normalizedData[category]) {
    return '분석 데이터가 없습니다.';
  }

  return normalizedData[category].feedback || '피드백이 없습니다.';
};

/**
 * 분석 항목별 점수를 가져옵니다
 * @param {Object} analysisData - 분석 데이터
 * @param {string} category - 분석 카테고리
 * @returns {number} 점수
 */
export const getCategoryScore = (analysisData, category) => {
  const normalizedData = normalizeAnalysisData(analysisData);
  if (!normalizedData || !normalizedData[category]) {
    return 0;
  }

  return normalizedData[category].score || 0;
};

/**
 * 개선 권장사항을 생성합니다
 * @param {Object} analysisData - 분석 데이터
 * @returns {Array} 권장사항 배열
 */
export const generateRecommendations = (analysisData) => {
  const normalizedData = normalizeAnalysisData(analysisData);
  if (!normalizedData) return [];

  const recommendations = [];

  Object.entries(normalizedData).forEach(([key, value]) => {
    if (value && typeof value === 'object' && 'score' in value) {
      const score = value.score;
      const label = getAnalysisLabel(key);

      if (score < 6) {
        recommendations.push({
          category: key,
          label: label,
          score: score,
          priority: 'high',
          message: `${label} 영역에서 개선이 필요합니다. (${score}/10점)`
        });
      } else if (score < 8) {
        recommendations.push({
          category: key,
          label: label,
          score: score,
          priority: 'medium',
          message: `${label} 영역을 더욱 강화할 수 있습니다. (${score}/10점)`
        });
      }
    }
  });

  return recommendations.sort((a, b) => a.score - b.score);
};
