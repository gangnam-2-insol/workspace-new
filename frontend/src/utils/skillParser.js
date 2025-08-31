/**
 * 스킬 데이터 파싱 유틸리티
 * 백엔드에서 오는 다양한 형태의 스킬 데이터를 일관된 배열 형태로 변환
 */

/**
 * 스킬 데이터를 파싱하여 배열로 변환
 * @param {string|Array} skills - 파싱할 스킬 데이터
 * @returns {Array} 파싱된 스킬 배열
 */
export const parseSkills = (skills) => {
  if (!skills) return [];

  // 이미 배열인 경우
  if (Array.isArray(skills)) {
    return skills.filter(skill => skill && skill.trim());
  }

  // 문자열인 경우
  if (typeof skills === 'string') {
    const trimmed = skills.trim();

    // 빈 문자열인 경우
    if (!trimmed) return [];

    // 디버깅을 위한 로그 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 [스킬 파싱] 입력 데이터:', trimmed);
    }

    // 배열 형태인 경우 (JSON 또는 Python 리스트)
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      // JSON 배열 형태인지 확인 (큰따옴표 사용)
      if (trimmed.includes('"')) {
        try {
          const parsed = JSON.parse(trimmed);
          return Array.isArray(parsed) ? parsed.filter(skill => skill && skill.trim()) : [];
        } catch (error) {
          console.warn('스킬 JSON 파싱 실패, Python 리스트 형태로 파싱 시도:', error);
          return parsePythonListString(trimmed);
        }
      } else {
        // Python 리스트 형태 (작은따옴표 사용)
        return parsePythonListString(trimmed);
      }
    }

    // 쉼표로 구분된 문자열인 경우
    if (trimmed.includes(',')) {
      return trimmed.split(',')
        .map(skill => skill.trim().replace(/['"]/g, ''))
        .filter(skill => skill);
    }

    // 단일 스킬인 경우
    const result = [trimmed.replace(/['"]/g, '')];

    // 디버깅을 위한 로그 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 [스킬 파싱] 단일 스킬 결과:', result);
    }

    return result;
  }

  return [];
};

/**
 * Python 리스트 형태의 문자열을 파싱하는 함수
 * @param {string} pythonListString - Python 리스트 문자열 (예: "['Spring', 'MySQL', 'AWS']")
 * @returns {Array} 파싱된 스킬 배열
 */
const parsePythonListString = (pythonListString) => {
  try {
    // Python 리스트 형태의 문자열을 정규식으로 파싱
    // 작은따옴표나 큰따옴표로 둘러싸인 문자열들을 찾는 정규식
    const skillRegex = /['"]([^'"]+)['"]/g;
    const skills = [];
    let match;

    while ((match = skillRegex.exec(pythonListString)) !== null) {
      const skill = match[1].trim();
      if (skill && skill.length > 0) {
        skills.push(skill);
      }
    }

    // 정규식으로 파싱이 실패한 경우, 대괄호와 따옴표를 제거하고 쉼표로 분리 시도
    if (skills.length === 0) {
      const cleaned = pythonListString
        .replace(/[\[\]'"]/g, '') // 대괄호와 따옴표 제거
        .split(',')
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);

      return cleaned;
    }

    // 디버깅을 위한 로그 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 [스킬 파싱] Python 리스트 결과:', skills);
    }

    return skills;
  } catch (error) {
    console.warn('Python 리스트 파싱 실패:', error);
    return [];
  }
};

/**
 * 문자열에서 스킬을 추출하는 정규식 기반 파서
 * @param {string} skillString - 스킬 문자열
 * @returns {Array} 추출된 스킬 배열
 */
const extractSkillsFromString = (skillString) => {
  // 작은따옴표나 큰따옴표로 둘러싸인 문자열들을 찾는 정규식
  const skillRegex = /['"]([^'"]+)['"]/g;
  const skills = [];
  let match;

  while ((match = skillRegex.exec(skillString)) !== null) {
    const skill = match[1].trim();
    if (skill) {
      skills.push(skill);
    }
  }

  return skills;
};

/**
 * 스킬 배열을 사용자 친화적인 형태로 포맷팅
 * @param {Array} skills - 스킬 배열
 * @param {number} maxDisplay - 최대 표시 개수
 * @returns {Object} 포맷팅된 스킬 정보
 */
export const formatSkills = (skills, maxDisplay = 3) => {
  const parsedSkills = parseSkills(skills);

  return {
    displaySkills: parsedSkills.slice(0, maxDisplay),
    remainingCount: Math.max(0, parsedSkills.length - maxDisplay),
    totalCount: parsedSkills.length,
    allSkills: parsedSkills
  };
};

/**
 * 스킬 데이터 검증
 * @param {any} skills - 검증할 스킬 데이터
 * @returns {boolean} 유효한 스킬 데이터인지 여부
 */
export const isValidSkills = (skills) => {
  const parsed = parseSkills(skills);
  return parsed.length > 0;
};

/**
 * 스킬 데이터 정규화 (백엔드 전송용)
 * @param {Array} skills - 정규화할 스킬 배열
 * @returns {Array} 정규화된 스킬 배열
 */
export const normalizeSkills = (skills) => {
  if (!Array.isArray(skills)) return [];

  return skills
    .map(skill => skill?.toString().trim())
    .filter(skill => skill && skill.length > 0)
    .map(skill => skill.replace(/['"]/g, '')); // 따옴표 제거
};
