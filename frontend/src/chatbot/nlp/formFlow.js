/**
 * 폼 플로우 관리 유틸리티
 */

// 페이지별 필드 순서 정의
const fieldOrders = {
  recruit_form: [
    'department', 'headcount', 'mainDuties', 'workHours', 
    'locationCity', 'salary', 'experience', 'contactEmail'
  ],
  resume_analysis: [
    'name', 'email', 'phone', 'education', 'experience', 'skills'
  ],
  portfolio_analysis: [
    'title', 'description', 'technologies', 'url', 'github'
  ]
};

// 페이지별 프롬프트 템플릿
const promptTemplates = {
  recruit_form: {
    department: '구인 부서를 알려주세요.',
    headcount: '채용 인원을 알려주세요.',
    mainDuties: '주요 업무를 설명해주세요.',
    workHours: '근무 시간을 알려주세요.',
    locationCity: '근무 위치를 알려주세요.',
    salary: '급여 조건을 알려주세요.',
    experience: '경력 요건을 알려주세요.',
    contactEmail: '연락처 이메일을 알려주세요.'
  }
};

/**
 * 초기 필드 반환
 * @param {string} pageId - 페이지 ID
 * @returns {string} 초기 필드명
 */
export const getInitialField = (pageId) => {
  const order = fieldOrders[pageId];
  return order ? order[0] : null;
};

/**
 * 다음 필드 반환
 * @param {string} pageId - 페이지 ID
 * @param {string} currentField - 현재 필드명
 * @returns {string} 다음 필드명
 */
export const getNextField = (pageId, currentField) => {
  const order = fieldOrders[pageId];
  if (!order) return null;
  
  const currentIndex = order.indexOf(currentField);
  if (currentIndex === -1 || currentIndex === order.length - 1) {
    return null;
  }
  
  return order[currentIndex + 1];
};

/**
 * 필드별 프롬프트 반환
 * @param {string} pageId - 페이지 ID
 * @param {string} fieldName - 필드명
 * @returns {string} 프롬프트 텍스트
 */
export const getPrompt = (pageId, fieldName) => {
  const templates = promptTemplates[pageId];
  return templates ? templates[fieldName] : `${fieldName}을(를) 입력해주세요.`;
};

