import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  overflow: hidden;
`;

const FormSection = styled.div`
  flex: 1;
  padding: 24px;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
`;

const ChatbotSection = styled.div`
  width: 400px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
`;

const ChatbotHeader = styled.div`
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChatbotMessages = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div`
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 85%;
  word-wrap: break-word;
  white-space: pre-wrap;
  
  ${props => props.type === 'user' ? `
    background: #3b82f6;
    color: white;
    align-self: flex-end;
    margin-left: auto;
  ` : `
    background: white;
    color: #1f2937;
    align-self: flex-start;
    border: 1px solid #e5e7eb;
  `}
`;

const ChatbotInput = styled.div`
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: white;
`;

const InputArea = styled.div`
  display: flex;
  gap: 8px;
`;

const TextArea = styled.textarea`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: #3b82f6;
  }
`;

const SendButton = styled.button`
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const AutoFillButton = styled.button`
  margin-top: 8px;
  width: 100%;
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const QuickQuestionButton = styled.button`
  margin: 4px;
  padding: 6px 12px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }
`;

const EnhancedModalChatbot = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  fields = [],
  onFieldUpdate,
  onComplete,
  aiAssistant = true 
}) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentField, setCurrentField] = useState(null);
  const [autoFillSuggestions, setAutoFillSuggestions] = useState([]);
  const [quickQuestions, setQuickQuestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 모달이 열릴 때 AI 어시스턴트 시작
  useEffect(() => {
    if (isOpen && aiAssistant) {
      startAIAssistant();
    }
  }, [isOpen, aiAssistant]);

  // 메시지 스크롤 자동화
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startAIAssistant = async () => {
    if (fields.length === 0) return;
    
    const firstField = fields[0];
    setCurrentField(firstField);
    
    const welcomeMessage = {
      type: 'bot',
      content: `안녕하세요! ${title} 작성을 도와드리겠습니다. 🤖\n\n먼저 ${firstField.label}에 대해 알려주세요.`,
      timestamp: new Date()
    };
    
    setMessages([welcomeMessage]);
    
    // 첫 번째 필드에 대한 빠른 질문들 생성
    generateQuickQuestions(firstField);
  };

  const generateQuickQuestions = (field) => {
    const questionsMap = {
      department: [
        "개발팀은 어떤 업무를 하나요?",
        "마케팅팀은 어떤 역할인가요?",
        "영업팀의 주요 업무는?",
        "디자인팀은 어떤 일을 하나요?"
      ],
      headcount: [
        "1명 채용하면 충분한가요?",
        "팀 규모는 어떻게 되나요?",
        "신입/경력 구분해서 채용하나요?",
        "계약직/정규직 중 어떤가요?"
      ],
      workType: [
        "웹 개발은 어떤 기술을 사용하나요?",
        "앱 개발은 iOS/Android 둘 다인가요?",
        "디자인은 UI/UX 모두인가요?",
        "마케팅은 온라인/오프라인 모두인가요?"
      ],
      workHours: [
        "유연근무제는 어떻게 운영되나요?",
        "재택근무 가능한가요?",
        "야근이 많은 편인가요?",
        "주말 근무가 있나요?"
      ],
      location: [
        "원격근무는 얼마나 가능한가요?",
        "출장이 많은 편인가요?",
        "해외 지사 근무 가능한가요?",
        "지방 근무는 어떤가요?"
      ],
      salary: [
        "연봉 협의는 언제 하나요?",
        "성과급은 어떻게 지급되나요?",
        "인센티브 제도가 있나요?",
        "연봉 인상은 언제 하나요?"
      ],
      jobTitle: [
        "공고 제목을 어떻게 작성해야 할까요?",
        "어떤 제목이 매력적일까요?",
        "검색에 잘 걸리는 제목은?",
        "회사명을 포함해야 하나요?"
      ],
      jobContent: [
        "공고 내용을 어떻게 작성해야 할까요?",
        "어떤 정보를 포함해야 하나요?",
        "회사 소개는 어떻게 쓸까요?",
        "업무 내용은 구체적으로 써야 하나요?"
      ]
    };
    
    const questions = questionsMap[field.key] || [
      "이 항목에 대해 궁금한 점이 있으신가요?",
      "더 자세한 설명이 필요하신가요?",
      "예시를 들어 설명해드릴까요?"
    ];
    
    setQuickQuestions(questions);
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // AI 응답 시뮬레이션 (실제로는 API 호출)
      const aiResponse = await simulateAIResponse(inputValue, currentField, fieldHistory[currentField.key]);

      const botMessage = {
        type: 'bot',
        content: aiResponse.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      // 자동 입력 제안이 있는 경우
      if (aiResponse.suggestions && aiResponse.suggestions.length > 0) {
        setAutoFillSuggestions(aiResponse.suggestions);
      }

      // 답변 누적 (필드별로)
      setFieldHistory(prev => ({
        ...prev,
        [currentField.key]: [...(prev[currentField.key] || []), inputValue]
      }));

      // 추가 정보가 필요하면 currentField 유지, 아니면 다음 단계로 이동
      if (aiResponse.needMoreDetail) {
        // currentField 유지 (추가 답변 대기)
        setIsLoading(false);
        return;
      } else {
        // 값 저장
        onFieldUpdate?.(currentField.key, aiResponse.value);
        setAutoFillSuggestions([]);
        // 다음 필드로 이동
        const currentIndex = fields.findIndex(f => f.key === currentField.key);
        if (currentIndex < fields.length - 1) {
          const nextField = fields[currentIndex + 1];
          setCurrentField(nextField);
          generateQuickQuestions(nextField);
        } else {
          // 마지막 필드면 완료
          onComplete?.({});
        }
        setIsLoading(false);
      }
    } catch (e) {
      setIsLoading(false);
    }
  };

  // 필드별 답변 히스토리
  const [fieldHistory, setFieldHistory] = useState({});

  // simulateAIResponse 개선: needMoreDetail 플래그 추가
  const simulateAIResponse = async (userInput, field, history = []) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    const lowerInput = userInput.toLowerCase();

    // 예시: department에서 추가 정보가 필요하면 needMoreDetail true 반환
    if (field.key === 'department') {
      if (!['프론트엔드', '백엔드', '풀스택', '모바일', '기획', '디자인', '마케팅', '영업'].some(k => lowerInput.includes(k))) {
        // 추가 정보 필요
        return {
          message: generateDepartmentResponse(lowerInput),
          value: history.concat([userInput]).join(' '),
          suggestions: generateDepartmentSuggestions(lowerInput),
          needMoreDetail: true
        };
      } else {
        // 충분한 정보
        return {
          message: `좋아요! ${userInput} 부서로 등록하겠습니다. 이제 채용 인원에 대해 알려주세요.`,
          value: userInput,
          suggestions: [],
          needMoreDetail: false
        };
      }
    }
    // 나머지 필드도 필요시 비슷하게 적용 가능
    // 기본 응답
    const responses = {
      headcount: {
        message: generateHeadcountResponse(lowerInput),
        value: extractHeadcountValue(userInput),
        suggestions: generateHeadcountSuggestions(lowerInput),
        needMoreDetail: false
      },
      mainDuties: {
        message: generateMainDutiesResponse(lowerInput),
        value: userInput,
        suggestions: generateMainDutiesSuggestions(lowerInput),
        needMoreDetail: false
      },
      workHours: {
        message: generateWorkHoursResponse(lowerInput),
        value: extractWorkHoursValue(userInput),
        suggestions: generateWorkHoursSuggestions(lowerInput),
        needMoreDetail: false
      },
      locationCity: {
        message: generateLocationResponse(lowerInput),
        value: extractLocationValue(userInput),
        suggestions: generateLocationSuggestions(lowerInput),
        needMoreDetail: false
      },
      salary: {
        message: generateSalaryResponse(lowerInput),
        value: extractSalaryValue(userInput),
        suggestions: generateSalarySuggestions(lowerInput),
        needMoreDetail: false
      },
      deadline: {
        message: generateDeadlineResponse(lowerInput),
        value: extractDeadlineValue(userInput),
        suggestions: generateDeadlineSuggestions(lowerInput),
        needMoreDetail: false
      },
      contactEmail: {
        message: generateEmailResponse(lowerInput),
        value: extractEmailValue(userInput),
        suggestions: generateEmailSuggestions(lowerInput),
        needMoreDetail: false
      },
      jobTitle: {
        message: generateJobTitleResponse(lowerInput),
        value: userInput,
        suggestions: [],
        needMoreDetail: false
      },
      jobContent: {
        message: generateJobContentResponse(lowerInput),
        value: userInput,
        suggestions: [],
        needMoreDetail: false
      }
    };
    return responses[field.key] || {
      message: generateGenericResponse(lowerInput, field),
      value: userInput,
      suggestions: [],
      needMoreDetail: false
    };
  };

  // 부서 관련 응답 생성
  const generateDepartmentResponse = (input) => {
    if (input.includes('개발') || input.includes('dev')) {
      return '개발팀이시군요! 🚀\n\n개발팀은 보통 프론트엔드, 백엔드, 풀스택으로 나뉘는데요. 어떤 개발 분야를 찾고 계신가요?\n\n• 프론트엔드: React, Vue.js, Angular\n• 백엔드: Java, Python, Node.js\n• 풀스택: 전체 개발 가능\n• 모바일: iOS, Android\n\n어떤 기술 스택을 사용하실 예정인가요?';
    } else if (input.includes('마케팅') || input.includes('marketing')) {
      return '마케팅팀이시군요! 📢\n\n마케팅팀은 다양한 역할이 있어요:\n\n• 디지털 마케팅: SNS, 광고, SEO\n• 브랜드 마케팅: 브랜드 전략, 콘텐츠\n• 성장 마케팅: 데이터 분석, A/B 테스트\n• B2B 마케팅: 기업 대상 마케팅\n\n어떤 마케팅 분야를 찾고 계신가요?';
    } else if (input.includes('디자인') || input.includes('design')) {
      return '디자인팀이시군요! 🎨\n\n디자인팀도 여러 분야가 있어요:\n\n• UI/UX 디자인: 사용자 경험 설계\n• 그래픽 디자인: 브랜딩, 포스터\n• 제품 디자인: 하드웨어 제품\n• 웹 디자인: 웹사이트, 앱\n\n어떤 디자인 분야를 찾고 계신가요?';
    } else if (input.includes('영업') || input.includes('sales')) {
      return '영업팀이시군요! 💼\n\n영업팀은 회사 수익에 직접적인 영향을 주는 중요한 팀이에요:\n\n• 내부 영업: 사무실에서 전화/이메일\n• 외부 영업: 고객사 방문\n• B2B 영업: 기업 대상\n• B2C 영업: 개인 대상\n\n어떤 영업 형태를 찾고 계신가요?';
    } else {
      return `'${input}' 부서를 찾고 계시는군요! 👍\n\n이 부서에서 어떤 역할을 담당하게 될까요? 구체적인 업무 내용을 알려주시면 더 정확한 채용공고를 작성할 수 있어요.`;
    }
  };

  // 채용 인원 관련 응답 생성
  const generateHeadcountResponse = (input) => {
    if (input.includes('1명') || input.includes('한 명')) {
      return '1명 채용이시군요! 👤\n\n1명 채용은 보통:\n\n• 특정 기술을 가진 전문가\n• 팀에 부족한 역할 보충\n• 새로운 프로젝트 담당자\n\n어떤 경력 수준을 찾고 계신가요? (신입/경력)';
    } else if (input.includes('2명') || input.includes('두 명')) {
      return '2명 채용이시군요! 👥\n\n2명 채용은 보통:\n\n• 팀 확장을 위한 인력\n• 선후배 관계로 구성\n• 서로 다른 전문 분야\n\n어떤 조합으로 구성하고 싶으신가요?';
    } else if (input.includes('3명') || input.includes('세 명')) {
      return '3명 채용이시군요! 👥👤\n\n3명은 작은 팀을 구성할 수 있는 규모예요:\n\n• 팀 리더 1명 + 실무자 2명\n• 각각 다른 전문 분야\n• 프로젝트별 담당\n\n어떤 역할 분담을 생각하고 계신가요?';
    } else {
      return `'${input}'명 채용이시군요! 👍\n\n이 정도 규모면 팀을 구성하거나 프로젝트를 담당할 수 있을 것 같아요. 어떤 경력 수준을 찾고 계신가요?`;
    }
  };

  // 업무 내용 관련 응답 생성
  const generateMainDutiesResponse = (input) => {
    if (input.includes('개발') || input.includes('코딩') || input.includes('프로그래밍')) {
      return '개발 업무를 담당하게 되시는군요! 💻\n\n개발 업무는 보통:\n\n• 웹/앱 개발\n• 데이터베이스 설계\n• API 개발\n• 테스트 및 디버깅\n\n어떤 기술 스택을 사용하실 예정인가요?';
    } else if (input.includes('디자인') || input.includes('UI') || input.includes('UX')) {
      return '디자인 업무를 담당하게 되시는군요! 🎨\n\n디자인 업무는 보통:\n\n• UI/UX 설계\n• 프로토타입 제작\n• 사용자 리서치\n• 디자인 시스템 구축\n\n어떤 디자인 도구를 사용하실 예정인가요?';
    } else if (input.includes('마케팅') || input.includes('광고') || input.includes('홍보')) {
      return '마케팅 업무를 담당하게 되시는군요! 📢\n\n마케팅 업무는 보통:\n\n• 캠페인 기획 및 실행\n• 콘텐츠 제작\n• 데이터 분석\n• 고객 관리\n\n어떤 마케팅 채널을 주로 사용하실 예정인가요?';
    } else {
      return `'${input}' 업무를 담당하게 되시는군요! 👍\n\n이 업무에서 가장 중요한 역량이나 경험이 있다면 알려주세요. 채용공고에 반영해드릴게요.`;
    }
  };

  // 근무 시간 관련 응답 생성
  const generateWorkHoursResponse = (input) => {
    if (input.includes('유연') || input.includes('플렉스')) {
      return '유연근무제를 운영하시는군요! ⏰\n\n유연근무제는 좋은 선택이에요:\n\n• 업무 효율성 향상\n• 직원 만족도 증가\n• 일과 삶의 균형\n\n핵심 근무 시간은 어떻게 되나요? (예: 10:00-16:00)';
    } else if (input.includes('재택') || input.includes('원격') || input.includes('홈오피스')) {
      return '재택근무를 허용하시는군요! 🏠\n\n재택근무는 요즘 트렌드예요:\n\n• 업무 집중도 향상\n• 출퇴근 시간 절약\n• 코로나 대응\n\n재택근무 비율은 어떻게 되나요? (예: 주 2-3일)';
    } else if (input.includes('야근') || input.includes('오버타임')) {
      return '야근이 있는 환경이시군요! 🌙\n\n야근에 대해 솔직하게 말씀해주셔서 좋아요:\n\n• 야근 수당 지급\n• 대체 휴가 제공\n• 야근 최소화 노력\n\n야근은 보통 어떤 상황에서 발생하나요?';
    } else {
      return `'${input}' 근무 시간이시군요! 👍\n\n이 근무 시간에 대해 궁금한 점이 있으시면 언제든 물어보세요. 퇴근 시간이나 점심 시간은 어떻게 되나요?`;
    }
  };

  // 위치 관련 응답 생성
  const generateLocationResponse = (input) => {
    if (input.includes('서울') || input.includes('강남') || input.includes('홍대')) {
      return '서울에서 근무하시는군요! 🏢\n\n서울은 다양한 장점이 있어요:\n\n• 대중교통 편리\n• 다양한 기업 문화\n• 네트워킹 기회\n\n구체적으로 어느 지역인가요? (예: 강남, 홍대, 여의도)';
    } else if (input.includes('부산') || input.includes('대구') || input.includes('인천')) {
      return '지방에서 근무하시는군요! 🏙️\n\n지방 근무의 장점:\n\n• 생활비 절약\n• 여유로운 생활\n• 지역 특화 업무\n\n구체적으로 어느 지역인가요?';
    } else if (input.includes('원격') || input.includes('재택') || input.includes('홈오피스')) {
      return '원격근무를 허용하시는군요! 🌐\n\n원격근무는 요즘 필수예요:\n\n• 지역 제약 없음\n• 다양한 인재 확보\n• 업무 효율성 향상\n\n원격근무 비율은 어떻게 되나요?';
    } else {
      return `'${input}'에서 근무하시는군요! 👍\n\n이 지역에서 근무할 때의 장점이나 특별한 점이 있다면 알려주세요.`;
    }
  };

  // 급여 관련 응답 생성
  const generateSalaryResponse = (input) => {
    if (input.includes('협의') || input.includes('면접')) {
      return '급여는 협의로 결정하시는군요! 💰\n\n협의 방식은 좋은 선택이에요:\n\n• 경력과 역량에 맞춤\n• 시장 수준 고려\n• 성과 연동 가능\n\n어떤 기준으로 협의하실 예정인가요?';
    } else if (input.includes('만원') || input.includes('천만')) {
      return '구체적인 급여를 제시하시는군요! 💰\n\n투명한 급여 제시는 좋아요:\n\n• 지원자들이 명확히 파악\n• 적합한 인재 유치\n• 회사 신뢰도 향상\n\n성과급이나 인센티브는 별도인가요?';
    } else {
      return `'${input}' 급여 조건이시군요! 👍\n\n이 급여에 대해 궁금한 점이 있으시면 언제든 물어보세요. 성과급이나 복리후생은 어떻게 되나요?`;
    }
  };

  // 마감일 관련 응답 생성
  const generateDeadlineResponse = (input) => {
    if (input.includes('채용') || input.includes('시')) {
      return '채용 시 마감이시군요! ⏰\n\n채용 시 마감은 유연한 방식이에요:\n\n• 적합한 인재 찾을 때까지\n• 시급한 포지션\n• 계속적인 채용\n\n대략적인 기간은 어떻게 되나요?';
    } else if (input.includes('년') || input.includes('월') || input.includes('일')) {
      return '구체적인 마감일을 정하시는군요! 📅\n\n명확한 마감일은 좋아요:\n\n• 지원자들이 계획 수립\n• 채용 일정 관리\n• 효율적인 채용 진행\n\n마감일 이후에도 채용이 계속되나요?';
    } else {
      return `'${input}' 마감일이시군요! 👍\n\n이 마감일에 대해 궁금한 점이 있으시면 언제든 물어보세요.`;
    }
  };

  // 이메일 관련 응답 생성
  const generateEmailResponse = (input) => {
    if (input.includes('@')) {
      return '이메일을 입력해주셨군요! 📧\n\n이메일은 채용 관련 소통에 사용될 예정이에요:\n\n• 지원자 문의 응답\n• 면접 일정 안내\n• 최종 결과 통보\n\n이메일로 받을 수 있는 문의 유형을 알려드릴까요?';
    } else {
      return '이메일 주소를 입력해주세요! 📧\n\n이메일은 채용 과정에서 중요한 소통 수단이에요. 회사 이메일이나 담당자 이메일을 입력해주세요.';
    }
  };

  // 공고 제목 관련 응답 생성
  const generateJobTitleResponse = (input) => {
    if (input.includes('추천') || input.includes('제목') || input.includes('어떻게')) {
      return '채용공고 제목을 추천해드릴게요! 📝\n\n좋은 제목의 핵심 요소:\n\n• 명확한 포지션 (예: "React 개발자", "UI/UX 디자이너")\n• 회사명 포함 (예: "ABC기업 React 개발자 모집")\n• 매력적인 키워드 (예: "성장하는", "혁신적인")\n\n어떤 부서에서 어떤 역할을 찾고 계신가요? 구체적으로 알려주시면 맞춤형 제목을 추천해드릴게요!';
    } else if (input.includes('개발') || input.includes('프로그래머') || input.includes('엔지니어')) {
      return '개발자 채용공고 제목을 추천해드릴게요! 💻\n\n추천 제목들:\n\n• "[회사명] React 개발자 모집"\n• "성장하는 스타트업에서 함께할 개발자"\n• "혁신적인 서비스를 만들어갈 개발자"\n• "풀스택 개발자 (React + Node.js)"\n\n어떤 기술 스택을 사용하실 예정인가요?';
    } else if (input.includes('마케팅') || input.includes('홍보')) {
      return '마케팅 담당자 채용공고 제목을 추천해드릴게요! 📢\n\n추천 제목들:\n\n• "[회사명] 디지털 마케터 모집"\n• "브랜드 성장을 이끌 마케터"\n• "데이터 기반 마케팅 전문가"\n• "콘텐츠 마케터 (SNS 운영)"\n\n어떤 마케팅 분야를 찾고 계신가요?';
    } else if (input.includes('디자인') || input.includes('design')) {
      return '디자이너 채용공고 제목을 추천해드릴게요! 🎨\n\n추천 제목들:\n\n• "[회사명] UI/UX 디자이너 모집"\n• "사용자 경험을 설계할 디자이너"\n• "브랜드 아이덴티티를 만드는 디자이너"\n• "웹/앱 디자이너 (Figma, Sketch)"\n\n어떤 디자인 분야를 찾고 계신가요?';
    } else if (input.includes('신입') || input.includes('주니어')) {
      return '신입/주니어 채용공고 제목을 추천해드릴게요! 🌱\n\n추천 제목들:\n\n• "[회사명] 신입 개발자 모집 (대졸 신입)"\n• "함께 성장할 주니어 개발자"\n• "신입 디자이너 모집 (포트폴리오 필수)"\n• "주니어 마케터 모집 (성장 의지 우대)"\n\n어떤 분야의 신입/주니어를 찾고 계신가요?';
    } else if (input.includes('풀스택') || input.includes('fullstack')) {
      return '풀스택 개발자 채용공고 제목을 추천해드릴게요! 🔧\n\n추천 제목들:\n\n• "[회사명] 풀스택 개발자 모집 (React + Node.js)"\n• "프론트엔드/백엔드 모두 가능한 개발자"\n• "풀스택 개발자 (Vue.js + Python)"\n• "전체 개발 가능한 개발자 모집"\n\n어떤 기술 스택을 사용하실 예정인가요?';
    } else {
      return `'${input}' 관련 채용공고 제목을 추천해드릴게요! 📝\n\n좋은 제목의 특징:\n\n• 명확하고 구체적\n• 회사 브랜딩 반영\n• 지원자에게 매력적\n• 검색 최적화\n\n더 구체적인 정보를 알려주시면 맞춤형 제목을 추천해드릴게요!`;
    }
  };

  // 공고 내용 관련 응답 생성
  const generateJobContentResponse = (input) => {
    if (input.includes('추천') || input.includes('내용') || input.includes('어떻게')) {
      return '채용공고 내용을 추천해드릴게요! 📄\n\n좋은 공고 내용의 구조:\n\n1. **회사 소개** - 회사의 비전과 문화\n2. **업무 내용** - 구체적인 역할과 책임\n3. **자격 요건** - 필수/우대 사항\n4. **근무 조건** - 근무시간, 위치, 급여\n5. **복리후생** - 보험, 휴가, 교육 등\n\n어떤 정보를 먼저 작성하고 싶으신가요? 회사 소개부터 시작할까요?';
    } else if (input.includes('회사') || input.includes('소개')) {
      return '회사 소개 부분을 작성해드릴게요! 🏢\n\n추천 템플릿:\n\n"[회사명]은 [핵심 가치/비전]을 추구하는 [업종] 기업입니다.\n\n우리는 [주요 성과/특징]을 통해 [목표]를 달성하고 있으며, [회사 문화/환경]을 중시합니다.\n\n이번 채용을 통해 [기대하는 역할]을 담당할 인재를 찾고 있습니다."\n\n회사명과 주요 특징을 알려주시면 맞춤형 소개를 작성해드릴게요!';
    } else if (input.includes('업무') || input.includes('일')) {
      return '업무 내용 부분을 작성해드릴게요! 💼\n\n추천 템플릿:\n\n"주요 업무:\n• [구체적인 업무 1]\n• [구체적인 업무 2]\n• [구체적인 업무 3]\n\n담당 프로젝트:\n• [프로젝트명/서비스명] 개발 및 운영\n• [관련 기술/도구] 활용\n• 팀 협업 및 커뮤니케이션"\n\n어떤 업무를 담당하게 될까요? 구체적으로 알려주세요!';
    } else if (input.includes('자격') || input.includes('요건')) {
      return '자격 요건 부분을 작성해드릴게요! ✅\n\n추천 템플릿:\n\n"필수 요건:\n• [학력/경력] 이상\n• [필수 기술/자격] 보유\n• [관련 경험] 경험자\n\n우대 사항:\n• [추가 기술/자격] 보유자\n• [관련 프로젝트] 경험자\n• [언어/자격증] 보유자"\n\n어떤 자격 요건을 설정하고 싶으신가요?';
    } else if (input.includes('복리후생') || input.includes('복리')) {
      return '복리후생 부분을 작성해드릴게요! 🎁\n\n추천 템플릿:\n\n"복리후생:\n• 4대보험 및 퇴직연금\n• 연차휴가 및 반차제도\n• 경조사 지원 및 생일 축하금\n• 교육비 지원 및 도서구입비\n• 점심식대 지원\n• 야근식대 및 교통비 지원\n• 건강검진 및 단체상해보험"\n\n어떤 복리후생을 제공하실 예정인가요?';
    } else if (input.includes('근무') || input.includes('조건')) {
      return '근무 조건 부분을 작성해드릴게요! ⏰\n\n추천 템플릿:\n\n"근무 조건:\n• 근무시간: 09:00-18:00 (점심시간 12:00-13:00)\n• 근무형태: 정규직 (수습기간 3개월)\n• 근무지: [회사 주소]\n• 급여: 연봉 협의 (경력에 따라 차등)\n• 근무일: 월~금 (주5일 근무)"\n\n어떤 근무 조건을 설정하실 예정인가요?';
    } else {
      return `'${input}' 관련 공고 내용을 작성해드릴게요! 📄\n\n좋은 공고 내용의 핵심:\n\n• 명확하고 구체적인 정보\n• 지원자 입장에서의 매력\n• 회사의 진정성과 투명성\n• 행동 유도 (지원 방법)\n\n어떤 부분부터 작성하고 싶으신가요?`;
    }
  };

  // 일반적인 응답 생성
  const generateGenericResponse = (input, field) => {
    return `'${input}'에 대해 알려주셨군요! 👍\n\n이 정보를 바탕으로 채용공고를 작성해드릴게요. 다른 궁금한 점이 있으시면 언제든 물어보세요.`;
  };

  // 값 추출 함수들
  const extractDepartmentValue = (input) => {
    const departments = ['개발', '마케팅', '디자인', '영업', '기획', '인사', '회계', '운영'];
    for (const dept of departments) {
      if (input.includes(dept)) return dept;
    }
    return input;
  };

  const extractHeadcountValue = (input) => {
    const numbers = input.match(/\d+/);
    return numbers ? `${numbers[0]}명` : input;
  };

  const extractWorkHoursValue = (input) => {
    if (input.includes('유연')) return '유연근무제';
    if (input.includes('재택')) return '재택근무 가능';
    return input;
  };

  const extractLocationValue = (input) => {
    const cities = ['서울', '부산', '대구', '인천', '대전', '광주', '울산'];
    for (const city of cities) {
      if (input.includes(city)) return city;
    }
    return input;
  };

  const extractSalaryValue = (input) => {
    return input;
  };

  const extractDeadlineValue = (input) => {
    return input;
  };

  const extractEmailValue = (input) => {
    return input;
  };

  // 제안 생성 함수들
  const generateDepartmentSuggestions = (input) => {
    if (input.includes('개발')) return ['프론트엔드', '백엔드', '풀스택', '모바일'];
    if (input.includes('마케팅')) return ['디지털마케팅', '브랜드마케팅', '성장마케팅', 'B2B마케팅'];
    if (input.includes('디자인')) return ['UI/UX', '그래픽디자인', '제품디자인', '웹디자인'];
    return ['개발', '마케팅', '디자인', '영업', '기획'];
  };

  const generateHeadcountSuggestions = (input) => {
    return ['1명', '2명', '3명', '5명', '10명'];
  };

  const generateMainDutiesSuggestions = (input) => {
    if (input.includes('개발')) return ['웹개발', '앱개발', '백엔드개발', '데이터분석'];
    if (input.includes('디자인')) return ['UI설계', 'UX리서치', '프로토타입', '디자인시스템'];
    return ['업무기획', '프로젝트관리', '고객관리', '데이터분석'];
  };

  const generateWorkHoursSuggestions = (input) => {
    return ['09:00-18:00', '10:00-19:00', '유연근무제', '재택근무'];
  };

  const generateLocationSuggestions = (input) => {
    return ['서울', '부산', '대구', '인천', '대전', '원격근무'];
  };

  const generateSalarySuggestions = (input) => {
    return ['면접 후 협의', '3000만원', '4000만원', '5000만원'];
  };

  const generateDeadlineSuggestions = (input) => {
    return ['2024년 12월 31일', '2024년 11월 30일', '채용 시 마감'];
  };

  const generateEmailSuggestions = (input) => {
    return ['hr@company.com', 'recruit@company.com'];
  };

  const handleAutoFill = (suggestion) => {
    onFieldUpdate?.(currentField.key, suggestion);
    setAutoFillSuggestions([]);
    
    // 다음 필드로 이동
    const currentIndex = fields.findIndex(f => f.key === currentField.key);
    if (currentIndex < fields.length - 1) {
      const nextField = fields[currentIndex + 1];
      setCurrentField(nextField);
      
      // 다음 필드에 대한 빠른 질문들 생성
      generateQuickQuestions(nextField);
    }
  };

  const handleQuickQuestion = (question) => {
    setInputValue(question);
    sendMessage();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContainer onClick={(e) => e.stopPropagation()}>
        <FormSection>
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '24px', fontWeight: '600' }}>
              {title}
            </h2>
            {aiAssistant && (
              <p style={{ color: '#6b7280', fontSize: '14px', margin: 0 }}>
                AI 어시스턴트가 입력을 도와드립니다. 오른쪽 채팅창에서 궁금한 점을 물어보세요!
              </p>
            )}
          </div>
          {children}
        </FormSection>
        
        {aiAssistant && (
          <ChatbotSection>
            <ChatbotHeader>
              <span>🤖 AI 어시스턴트</span>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  onClick={() => {
                    setMessages([]);
                    startAIAssistant();
                  }}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '12px',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  }}
                >
                  새로고침
                </button>
                <button
                  onClick={onClose}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '14px',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  }}
                >
                  <span style={{ fontSize: '12px' }}>닫기</span>
                  <span style={{ fontSize: '16px' }}>✕</span>
                </button>
              </div>
            </ChatbotHeader>
            
            <ChatbotMessages>
              {messages.map((message, index) => (
                <Message key={index} type={message.type}>
                  {message.content}
                </Message>
              ))}
              {isLoading && (
                <Message type="bot">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ 
                      width: '16px', 
                      height: '16px', 
                      border: '2px solid #e5e7eb',
                      borderTop: '2px solid #3b82f6',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                    AI가 응답하고 있습니다...
                  </div>
                </Message>
              )}
              <div ref={messagesEndRef} />
            </ChatbotMessages>
            
            <ChatbotInput>
              {/* 빠른 질문 버튼들 */}
              {quickQuestions.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 8px 0' }}>
                    💡 빠른 질문:
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {quickQuestions.map((question, index) => (
                      <QuickQuestionButton
                        key={index}
                        onClick={() => handleQuickQuestion(question)}
                        disabled={isLoading}
                      >
                        {question}
                      </QuickQuestionButton>
                    ))}
                  </div>
                </div>
              )}
              
              <InputArea>
                <TextArea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="궁금한 점을 물어보거나 답변을 입력하세요..."
                  rows={3}
                  disabled={isLoading}
                />
                <SendButton
                  onClick={sendMessage}
                  disabled={isLoading || !inputValue.trim()}
                >
                  전송
                </SendButton>
              </InputArea>
              
              {autoFillSuggestions.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 8px 0' }}>
                    추천 답변:
                  </p>
                  {autoFillSuggestions.map((suggestion, index) => (
                    <AutoFillButton
                      key={index}
                      onClick={() => handleAutoFill(suggestion)}
                      disabled={isLoading}
                    >
                      <span>⚡</span>
                      {suggestion}
                    </AutoFillButton>
                  ))}
                </div>
              )}
            </ChatbotInput>
          </ChatbotSection>
        )}
      </ModalContainer>
    </ModalOverlay>
  );
};

export default EnhancedModalChatbot; 