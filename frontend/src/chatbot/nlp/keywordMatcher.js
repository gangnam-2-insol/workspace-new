/**
 * 키워드 매칭 유틸리티
 */

/**
 * 사용자 입력에서 키워드 매칭 확인
 * @param {string} userInput - 사용자 입력 텍스트
 * @param {Array} keywords - 매칭할 키워드 배열
 * @returns {boolean} 매칭 여부
 */
export const matchKeywords = (userInput, keywords) => {
  if (!userInput || !keywords || !Array.isArray(keywords)) {
    return false;
  }

  const normalizedInput = userInput.toLowerCase().replace(/\s+/g, '');
  
  return keywords.some(keyword => {
    const normalizedKeyword = keyword.toLowerCase().replace(/\s+/g, '');
    return normalizedInput.includes(normalizedKeyword);
  });
};

