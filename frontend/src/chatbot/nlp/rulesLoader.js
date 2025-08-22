/**
 * 룰셋 로더 유틸리티
 */

/**
 * 룰셋 로드
 * @param {object} rulesConfig - 룰셋 설정 객체
 * @returns {object} 로드된 룰셋
 */
export const loadRules = async (rulesConfig) => {
  try {
    // rulesConfig가 이미 객체인 경우 그대로 반환
    if (typeof rulesConfig === 'object' && rulesConfig !== null) {
      return rulesConfig;
    }
    
    // 문자열인 경우 JSON 파싱 시도
    if (typeof rulesConfig === 'string') {
      return JSON.parse(rulesConfig);
    }
    
    console.warn('[rulesLoader] 유효하지 않은 rulesConfig:', rulesConfig);
    return {};
  } catch (error) {
    console.error('[rulesLoader] 룰셋 로드 실패:', error);
    return {};
  }
};

/**
 * 맥락에 따른 룰셋 반환
 * @param {object} rules - 로드된 룰셋
 * @param {string} context - 맥락
 * @returns {object} 맥락별 룰셋
 */
export const getRulesForContext = (rules, context) => {
  if (!rules || !context) {
    return null;
  }

  return rules[context] || rules.default || null;
};

