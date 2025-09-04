/**
 * 자소서 검증 관련 유틸리티 함수들
 */

/**
 * 자소서 길이를 검증합니다
 * @param {string} content - 자소서 내용
 * @param {string} position - 지원 직무
 * @returns {Object} 길이 검증 결과
 */
export const validateLength = (content, position) => {
  const wordCount = content.trim().split(/\s+/).length;
  const charCount = content.length;

  let status = 'good';
  let message = '적절한 길이입니다.';

  if (wordCount < 300) {
    status = 'short';
    message = '자소서가 너무 짧습니다. 최소 300자 이상 작성해주세요.';
  } else if (wordCount > 2000) {
    status = 'long';
    message = '자소서가 너무 깁니다. 2000자 이내로 작성해주세요.';
  }

  return {
    wordCount,
    charCount,
    status,
    message
  };
};

/**
 * 자소서 구조를 분석합니다
 * @param {string} content - 자소서 내용
 * @returns {Object} 구조 분석 결과
 */
export const analyzeStructure = (content) => {
  const paragraphs = content.split('\n\n').filter(p => p.trim().length > 0);
  const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);

  const avgParagraphLength = paragraphs.length > 0
    ? Math.round(paragraphs.reduce((sum, p) => sum + p.length, 0) / paragraphs.length)
    : 0;

  const avgSentenceLength = sentences.length > 0
    ? Math.round(sentences.reduce((sum, s) => sum + s.trim().split(/\s+/).length, 0) / sentences.length)
    : 0;

  return {
    paragraphCount: paragraphs.length,
    sentenceCount: sentences.length,
    avgParagraphLength,
    avgSentenceLength
  };
};

/**
 * 문법 오류를 검사합니다 (간단한 검사)
 * @param {string} text - 검사할 텍스트
 * @returns {Array} 문법 오류 목록
 */
export const checkGrammarErrors = (text) => {
  const errors = [];

  // 간단한 문법 오류 검사
  if (text.includes('  ')) {
    errors.push({
      type: 'spacing',
      message: '연속된 공백이 있습니다.',
      severity: 'low'
    });
  }

  if (text.includes('..')) {
    errors.push({
      type: 'punctuation',
      message: '연속된 마침표가 있습니다.',
      severity: 'medium'
    });
  }

  return errors;
};

/**
 * 종합 검증 점수를 계산합니다
 * @param {Object} validationData - 검증 데이터
 * @returns {number} 종합 점수
 */
export const calculateValidationScore = (validationData) => {
  let score = 100;

  // 길이 점수 (20점)
  if (validationData.lengthStatus === 'short' || validationData.lengthStatus === 'long') {
    score -= 20;
  }

  // 문법 오류 점수 (30점)
  if (validationData.grammarErrors && validationData.grammarErrors.length > 0) {
    score -= validationData.grammarErrors.length * 5;
  }

  // 키워드 매칭 점수 (25점)
  if (validationData.keywordAnalysis) {
    const matchRate = validationData.keywordAnalysis.matchRate || 0;
    score -= Math.max(0, 25 - (matchRate * 0.25));
  }

  // 표절 점수 (25점)
  if (validationData.plagiarismScore > 30) {
    score -= 25;
  } else if (validationData.plagiarismScore > 15) {
    score -= 15;
  }

  return Math.max(0, Math.round(score));
};

/**
 * 검증 점수에 따른 색상을 반환합니다
 * @param {number} score - 검증 점수
 * @returns {string} 색상 코드
 */
export const getValidationScoreColor = (score) => {
  if (score >= 80) return '#16a34a'; // 녹색
  if (score >= 60) return '#f59e0b'; // 노란색
  return '#dc2626'; // 빨간색
};
