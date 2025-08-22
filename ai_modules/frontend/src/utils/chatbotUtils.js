// 챗봇 관련 유틸리티 함수들

// 메시지 타입 검증
export const isValidMessageType = (type) => {
  return ['user', 'bot', 'system'].includes(type);
};

// 메시지 포맷팅
export const formatMessage = (content, type = 'bot') => {
  return {
    content,
    type,
    timestamp: new Date(),
    id: `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  };
};

// 키워드 추출
export const extractKeywords = (text) => {
  const keywords = [];
  const lowerText = text.toLowerCase();
  
  // 기본 키워드들
  const basicKeywords = [
    '채용', '공고', '등록', '작성', '면접', '이력서', '지원자',
    '개발', '마케팅', '영업', '디자인', '기획', '인사',
    '신입', '경력', '인원', '급여', '위치', '업무'
  ];
  
  basicKeywords.forEach(keyword => {
    if (lowerText.includes(keyword)) {
      keywords.push(keyword);
    }
  });
  
  return [...new Set(keywords)];
};

// 페이지별 환영 메시지 생성
export const getWelcomeMessage = (page) => {
  const messages = {
    'dashboard': `안녕하세요! 대시보드에서 어떤 도움이 필요하신가요?

📊 현재 현황을 확인하거나 다음 질문들을 해보세요:
• "현재 등록된 채용공고는 몇 개인가요?"
• "지원자 통계를 보여주세요"
• "면접 일정을 확인해주세요"`,
    
    'job-posting': `채용공고 등록을 도와드리겠습니다! 🎯

다음 질문들을 해보세요:
• "채용공고 등록 방법을 알려주세요"
• "어떤 부서에서 채용하시나요?"
• "채용공고 작성 팁을 알려주세요"`,
    
    'resume': `이력서 관리에 대해 도움을 드리겠습니다! 📄

다음 질문들을 해보세요:
• "지원자 이력서를 어떻게 확인하나요?"
• "이력서 검토 방법을 알려주세요"`,
    
    'interview': `면접 관리에 대해 문의하실 내용이 있으신가요? 🎤

다음 질문들을 해보세요:
• "면접 일정을 확인해주세요"
• "면접 평가 방법을 알려주세요"`,
    
    'portfolio': `포트폴리오 분석에 대해 도움을 드리겠습니다! 💼

다음 질문들을 해보세요:
• "포트폴리오 분석 기능이 뭔가요?"
• "지원자 포트폴리오를 어떻게 확인하나요?"`,
    
    'cover-letter': `자기소개서 검증에 대해 문의하실 내용이 있으신가요? ✍️

다음 질문들을 해보세요:
• "자기소개서 검증 기능이 뭔가요?"
• "자소서 평가 방법을 알려주세요"`,
    
    'talent': `인재 추천에 대해 도움을 드리겠습니다! 👥

다음 질문들을 해보세요:
• "인재 추천 시스템이 어떻게 작동하나요?"
• "추천 인재를 확인하고 싶어요"`,
    
    'users': `사용자 관리에 대해 문의하실 내용이 있으신가요? 👤

다음 질문들을 해보세요:
• "사용자 목록을 확인해주세요"
• "새로운 사용자를 추가하고 싶어요"`,
    
    'settings': `설정에 대해 도움을 드리겠습니다! ⚙️

다음 질문들을 해보세요:
• "시스템 설정을 변경하고 싶어요"
• "알림 설정을 확인해주세요"`
  };
  
  return messages[page] || '안녕하세요! 어떤 도움이 필요하신가요?';
};

// 자동 스크롤 함수
export const scrollToBottom = (ref) => {
  if (ref && ref.current) {
    ref.current.scrollIntoView({ behavior: 'smooth' });
  }
};

// 입력값 검증
export const validateInput = (input) => {
  if (!input || typeof input !== 'string') {
    return false;
  }
  
  const trimmed = input.trim();
  return trimmed.length > 0 && trimmed.length <= 1000;
};

// 에러 메시지 생성
export const createErrorMessage = (error) => {
  return {
    type: 'bot',
    content: `죄송합니다. 오류가 발생했습니다: ${error.message || '알 수 없는 오류'}`,
    timestamp: new Date(),
    isError: true
  };
}; 