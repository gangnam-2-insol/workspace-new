import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled, { keyframes } from 'styled-components';

// ==========================================================
// AI 서비스 클래스: 백엔드 API와의 통신 담당
// ==========================================================
class AIChatbotService {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    this.sessionId = null;
    this.conversationHistory = [];
  }

  // AI 세션 시작
  async startSession(page, fields) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page,
          fields,
          mode: 'modal_assistant'
        })
      });

      if (!response.ok) {
        throw new Error('AI 세션 시작 실패');
      }

      const data = await response.json();
      this.sessionId = data.session_id;
      console.log('[AIChatbotService] 세션 시작:', this.sessionId);
      return data;
    } catch (error) {
      console.error('[AIChatbotService] 세션 시작 오류:', error);
      // 오프라인 모드로 전환
      return this.startOfflineSession(page, fields);
    }
  }

  // AI 메시지 전송
  async sendMessage(userInput, currentField, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          user_input: userInput,
          current_field: currentField?.key || null,
          context,
          mode: 'modal_assistant'
        })
      });

      if (!response.ok) {
        throw new Error('AI 메시지 전송 실패');
      }

      const data = await response.json();
      this.conversationHistory.push({
        type: 'user',
        content: userInput,
        timestamp: new Date()
      });
      this.conversationHistory.push({
        type: 'ai',
        content: data.message,
        timestamp: new Date()
      });

      return data;
    } catch (error) {
      console.error('[AIChatbotService] 메시지 전송 오류:', error);
      // 오프라인 모드로 처리
      return this.processOffline(userInput, currentField, context);
    }
  }

  // 필드 업데이트
  async updateField(field, value) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/update-field`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          field,
          value
        })
      });

      if (!response.ok) {
        throw new Error('필드 업데이트 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('[AIChatbotService] 필드 업데이트 오류:', error);
      return { success: false, error: error.message };
    }
  }

  // 오프라인 세션 시작
  startOfflineSession(page, fields) {
    console.log('[AIChatbotService] 오프라인 모드로 전환');
    this.sessionId = 'offline-' + Date.now();
    return {
      session_id: this.sessionId,
      mode: 'offline',
      message: '오프라인 모드로 전환되었습니다.'
    };
  }



  // 오프라인 메시지 처리 (순수 LLM 모델)
  processOffline(userInput, currentField, context) {
    console.log('[AIChatbotService] 오프라인 메시지 처리:', userInput);
    
    // 순수 LLM 응답 생성
    let message = '';
    let value = null;
    let needMoreDetail = true;
    let autoFillSuggestions = [];

    // 사용자 입력에 대한 자연스러운 응답
    if (currentField) {
      message = `현재 "${currentField.label}" 필드에 대해 입력해주세요.`;
    } else {
      message = '어떤 도움이 필요하신가요?';
    }

    return {
      message,
      value,
      needMoreDetail,
      autoFillSuggestions,
      mode: 'offline'
    };
  }

  // 세션 종료
  async endSession() {
    if (this.sessionId && !this.sessionId.startsWith('offline-')) {
      try {
        await fetch(`${this.baseURL}/api/chatbot/end`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: this.sessionId
          })
        });
      } catch (error) {
        console.error('[AIChatbotService] 세션 종료 오류:', error);
      }
    }
    this.sessionId = null;
    this.conversationHistory = [];
  }
}

// ==========================================================
// Helper Functions: 유틸리티 함수들
// ==========================================================



// 기본 필드 제안
const getFieldSuggestions = (fieldKey, formData = {}) => {
  switch (fieldKey) {
    case 'department':
      return ['개발팀', '기획팀', '마케팅팀', '디자인팀', '인사팀'];
    case 'headcount':
      return ['1명', '2명', '3명', '5명'];
    case 'mainDuties':
      return ['신규 웹 서비스 개발', '사용자 리서치 및 제품 기획', '브랜드 마케팅 전략 수립'];
    case 'requiredExperience':
      return ['React, Node.js 2년 이상', '데이터 분석 및 시각화', '영어 커뮤니케이션'];
    case 'preferredQualifications':
      return ['AWS 클라우드 경험', 'Git 협업 경험', '애자일 방법론 경험'];
    default:
      return [];
  }
};

// 파일 저장/다운로드 유틸리티
const getFormattedContent = (formData) => {
  const safeFormData = formData || {};
  
  const contentParts = [
    `**[채용공고 초안]**`,
    `----------------------------------------`,
    `**부서:** ${safeFormData.department || '미정'}`,
    `**인원:** ${safeFormData.headcount || '미정'}`,
    `**주요 업무:**\n${safeFormData.mainDuties || '미정'}\n`,
    `**필요 경험/기술:**\n${safeFormData.requiredExperience || '미정'}\n`,
    `**우대 사항:**\n${safeFormData.preferredQualifications || '없음'}\n`,
    `----------------------------------------`,
    `AI 채용공고 어시스턴트가 생성했습니다.`,
  ];
  return contentParts.join('\n');
};

const saveDraft = (formData) => {
  const draftContent = getFormattedContent(formData);
  try {
    localStorage.setItem('jobPostingDraft', draftContent);
    console.log('초안 저장됨:', draftContent);
    return { message: "✅ 초안이 성공적으로 저장되었습니다!" };
  } catch (error) {
    console.error('초안 저장 실패:', error);
    return { message: "❌ 초안 저장에 실패했습니다. 다시 시도해주세요." };
  }
};

const downloadPDF = (formData, format = 'pdf') => {
  const content = getFormattedContent(formData);
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `채용공고_초안.${format === 'text' ? 'txt' : format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return { message: `✅ 채용공고 초안이 ${format.toUpperCase()} 파일로 다운로드되었습니다!` };
};

// ==========================================================
// Styled Components: UI 스타일링 (기존 유지)
// ==========================================================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
`;

const loadingDots = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
`;

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
  height: 100%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  overflow: hidden;

  @media (max-width: 768px) {
    flex-direction: column;
    max-width: 95%;
    max-height: 95vh;
  }
`;

const FormSection = styled.div`
  flex: 1;
  padding: 24px;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;

  @media (max-width: 768px) {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    min-height: 200px;
  }
`;

const ChatbotSection = styled.div`
  width: 400px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  animation: ${slideIn} 0.5s ease-out;

  @media (max-width: 768px) {
    width: 100%;
    height: 60%;
    min-height: 300px;
  }
`;

const ChatbotHeader = styled.div`
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.1em;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0 5px;
  transition: transform 0.2s ease-in-out;

  &:hover {
    transform: rotate(90deg);
  }
`;

const ChatbotMessages = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
  background-color: #f0f2f5;

  &::-webkit-scrollbar {
    width: 8px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: #cbd5e0;
    border-radius: 4px;
  }
  &::-webkit-scrollbar-track {
    background-color: #f1f5f9;
  }
`;

const Message = styled.div`
  max-width: 85%;
  padding: 10px 15px;
  border-radius: 18px;
  line-height: 1.4;
  font-size: 0.9em;
  animation: ${fadeIn} 0.3s ease-out;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;

  ${props => props.type === 'user' ? `
    background-color: #e0e7ff;
    color: #333;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
  ` : `
    background-color: #ffffff;
    color: #2d3748;
    align-self: flex-start;
    border: 1px solid #e2e8f0;
    border-bottom-left-radius: 5px;
  `}
`;

const TypingIndicator = styled.div`
  display: flex;
  align-self: flex-start;
  padding: 10px 15px;
  border-radius: 18px;
  background: #ffffff;
  color: #2d3748;
  margin-top: 5px;
  animation: ${fadeIn} 0.3s ease-out;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);

  span {
    display: inline-block;
    width: 7px;
    height: 7px;
    background-color: #667eea;
    border-radius: 50%;
    margin: 0 2px;
    animation: ${loadingDots} 1.4s infinite ease-in-out both;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
`;

const ChatbotInput = styled.div`
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InputArea = styled.div`
  display: flex;
  gap: 10px;
`;

const TextArea = styled.textarea`
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 0.95em;
  resize: none;
  outline: none;
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  }
  &::placeholder {
    color: #a0aec0;
  }
  min-height: 40px;
  max-height: 120px;
  overflow-y: auto;
`;

const SendButton = styled.button`
  background: ${props => props.disabled ? '#e2e8f0' : '#667eea'};
  color: ${props => props.disabled ? '#a0aec0' : 'white'};
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 0.95em;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: background 0.2s ease, transform 0.1s ease;
  &:not(:disabled):hover {
    background: #5a67d8;
    transform: translateY(-1px);
  }
`;

const SuggestionsContainer = styled.div`
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
`;

const SuggestionsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
`;

const AutoFillButton = styled.button`
  background: ${props => props.disabled ? '#edf2f7' : '#f0f4ff'};
  color: ${props => props.disabled ? '#a0aec0' : '#4c51bf'};
  border: 1px solid ${props => props.disabled ? '#e2e8f0' : '#b3c7ff'};
  border-radius: 20px;
  padding: 8px 12px;
  font-size: 0.8em;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;

  &:not(:disabled):hover {
    background: #e0e9ff;
    border-color: #92aeff;
  }
`;



const SectionTitle = styled.h2`
  font-size: 1.5em;
  color: #2d3748;
  margin-bottom: 20px;
  border-bottom: 2px solid #edf2f7;
  padding-bottom: 10px;
`;

const FormField = styled.div`
  margin-bottom: 18px;

  label {
    display: block;
    font-size: 0.95em;
    color: #4a5568;
    margin-bottom: 6px;
    font-weight: 600;
  }

  input[type="text"],
  input[type="number"],
  textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cbd5e0;
    border-radius: 6px;
    font-size: 1em;
    color: #2d3748;
    background-color: #ffffff;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.04);
    transition: border-color 0.2s, box-shadow 0.2s;

    &:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }

    &:disabled {
      background-color: #f8fafc;
      color: #a0aec0;
      cursor: not-allowed;
    }
  }

  textarea {
    min-height: 80px;
    resize: vertical;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
`;

const ActionButton = styled.button`
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  ${props => props.$primary ? `
    background-color: #667eea;
    color: white;
    border: 1px solid #667eea;
    &:hover {
      background-color: #5a67d8;
      border-color: #5a67d8;
      transform: translateY(-1px);
    }
  ` : `
    background-color: #edf2f7;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    &:hover {
      background-color: #e2e8f0;
      transform: translateY(-1px);
    }
  `}
`;

// ==========================================================
// Main Component: EnhancedModalChatbot
// ==========================================================

const EnhancedModalChatbot = ({
  isOpen,
  onClose,
  fields = [],
  formData = {},
  onFieldUpdate,
  onComplete,
  aiAssistant = true,
  title = "AI 채용공고 어시스턴트"
}) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentField, setCurrentField] = useState(null);
  const [autoFillSuggestions, setAutoFillSuggestions] = useState([]);
  const [aiService] = useState(() => new AIChatbotService());
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const sendMessageRef = useRef(null);
  const fieldsRef = useRef(fields);
  const inputUpdateTimeout = useRef(null);

  


  // fields ref 업데이트
  useEffect(() => {
    fieldsRef.current = fields;
  }, [fields]);

  // 모달 열릴 때 AI 어시스턴트 시작
  useEffect(() => {
    if (isOpen && aiAssistant) {
      // startAIAssistant 함수를 직접 호출하지 않고 내부 로직을 실행
      const initializeAI = async () => {
        setIsLoading(true);
        
        try {
          // AI 세션 시작
          await aiService.startSession('job_posting', fieldsRef.current);
          
          if (!fieldsRef.current || fieldsRef.current.length === 0) {
            setMessages([{
              type: 'bot',
              content: "안녕하세요! 설정된 필드가 없습니다. 채용공고를 작성할 수 없습니다.",
              timestamp: new Date(),
              id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-no-fields`
            }]);
            setIsLoading(false);
            return;
          }

          const firstField = fieldsRef.current[0];
          setCurrentField(firstField);
          
          const welcomeMessage = {
            type: 'bot',
            content: `안녕하세요! 👋\n\n채용공고 작성을 도와드리겠습니다.\n\n먼저 **${firstField.label}**에 대해 알려주세요.`,
            timestamp: new Date(),
            id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-initial`
          };
          
          setMessages([welcomeMessage]);
          setAutoFillSuggestions(getFieldSuggestions(firstField.key, formData));
          
        } catch (error) {
          console.error('AI 어시스턴트 시작 오류:', error);
          setMessages([{
            type: 'bot',
            content: "AI 서비스에 연결할 수 없습니다. 오프라인 모드로 전환됩니다.",
            timestamp: new Date(),
            id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-error`
          }]);
        }
        
        setIsLoading(false);
        if (inputRef.current) {
          inputRef.current.focus();
        }
      };
      
      initializeAI();
    }
  }, [isOpen, aiAssistant, aiService]);

  // 메시지 업데이트 시 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 입력창 포커스
  useEffect(() => {
    if (!isLoading && inputRef.current && isOpen) {
      inputRef.current.focus();
    }
  }, [isLoading, isOpen]);

  // 메시지 전송 함수 정의
  const sendMessage = useCallback(async () => {
    const userMessageContent = inputValue.trim();
    if (!userMessageContent || isLoading || userMessageContent.length === 0) {
      return;
    }

    setIsLoading(true);
    setInputValue('');
    setAutoFillSuggestions([]);

    // 사용자 메시지 추가
    const newUserMessage = {
      type: 'user',
      content: userMessageContent,
      timestamp: new Date(),
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      // AI 서비스에 메시지 전송
      const aiResponse = await aiService.sendMessage(
        userMessageContent,
        currentField,
        { formData, currentFieldKey: currentField?.key }
      );

      // AI 응답 메시지 추가
      const newBotMessage = {
        type: 'bot',
        content: aiResponse.message,
        timestamp: new Date(),
        id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };
      setMessages(prev => [...prev, newBotMessage]);

      // 자동완성 제안 업데이트
      setAutoFillSuggestions(aiResponse.autoFillSuggestions || []);

      // 필드 업데이트 및 진행
      console.log("[DEBUG] ===== AI 응답 처리 시작 =====");
      console.log("[DEBUG] AI 응답:", aiResponse);
      console.log("[DEBUG] AI 응답 value:", aiResponse.value);
      console.log("[DEBUG] AI 응답 field:", aiResponse.field);
      console.log("[DEBUG] 현재 필드:", currentField);
      
      if (aiResponse.value !== null && aiResponse.value !== undefined) {
        const fieldKey = aiResponse.field || currentField?.key;
        console.log("[DEBUG] 필드 업데이트 실행:", fieldKey, aiResponse.value);
        console.log("[DEBUG] onFieldUpdate 함수 존재 여부:", !!onFieldUpdate);
        console.log("[DEBUG] onFieldUpdate 함수 타입:", typeof onFieldUpdate);
        
        if (onFieldUpdate) {
          console.log("[DEBUG] onFieldUpdate 함수 호출 시작");
          onFieldUpdate(fieldKey, aiResponse.value);
          console.log("[DEBUG] onFieldUpdate 함수 호출 완료");
        } else {
          console.log("[DEBUG] onFieldUpdate 함수가 없음!");
        }
        
        // 다음 필드로 이동
        if (!aiResponse.needMoreDetail && fieldsRef.current && fieldsRef.current.length > 0) {
          const currentIndex = fieldsRef.current.findIndex(f => f.key === currentField.key);
          if (currentIndex !== -1 && currentIndex < fieldsRef.current.length - 1) {
            const nextField = fieldsRef.current[currentIndex + 1];
            setCurrentField(nextField);
            setAutoFillSuggestions(getFieldSuggestions(nextField.key, formData));
          } else {
            setCurrentField(null);
            onComplete(formData);
          }
        }
      } else {
        console.log("[DEBUG] AI 응답에 value가 없음 - 폼 업데이트 안됨");
      }
      console.log("[DEBUG] ===== AI 응답 처리 완료 =====");

    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage = {
        type: 'bot',
        content: "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
        timestamp: new Date(),
        id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-error`
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [inputValue, isLoading, currentField, formData, onFieldUpdate, onComplete, aiService]);

  // sendMessage 함수를 ref에 저장
  sendMessageRef.current = sendMessage;

  // 키보드 이벤트 처리
  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && sendMessageRef.current) {
        sendMessageRef.current();
      }
    }
  }, [inputValue]);

  // 자동완성 클릭 처리
  const handleAutoFill = useCallback((suggestion) => {
    setInputValue(suggestion);
    // 자동완성 선택 시 즉시 필드 업데이트
    if (currentField) {
      onFieldUpdate(currentField.key, suggestion);
    }
    setTimeout(() => {
      if (sendMessageRef.current) {
        sendMessageRef.current();
      }
    }, 100);
  }, [currentField, onFieldUpdate]);


  // 모달이 열릴 때 챗봇 닫기
  useEffect(() => {
    if (isOpen) {
      console.log('EnhancedModalChatbot 모달이 열림 - 챗봇 닫기 이벤트 발생');
      const event = new CustomEvent('closeChatbot');
      window.dispatchEvent(event);
    }
  }, [isOpen]);

  // 모달 닫을 때 AI 세션 종료 및 타이머 정리
  useEffect(() => {
    return () => {
      if (isOpen) {
        aiService.endSession();
      }
      // 타이머 정리
      if (inputUpdateTimeout.current) {
        clearTimeout(inputUpdateTimeout.current);
      }
    };
  }, [isOpen, aiService]);

  console.log('[EnhancedModalChatbot] 렌더링, isOpen:', isOpen, 'aiAssistant:', aiAssistant);
  
  if (!isOpen) return null;

  return (
    <ModalOverlay key="enhanced-chatbot-overlay">
      <ModalContainer key="enhanced-chatbot-container">
        {/* Form Section */}
        <FormSection>
          <SectionTitle>채용공고 정보 입력</SectionTitle>
          <form>
            {fields && fields.length > 0 ? (
              fields.map(field => (
                <FormField key={field.key}>
                  <label htmlFor={field.key}>
                    {field.label}
                    {field.required && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
                    {currentField && currentField.key === field.key && (
                      <span style={{ 
                        color: '#667eea', 
                        marginLeft: '8px', 
                        fontSize: '0.9em',
                        fontWeight: 'bold'
                      }}>
                        🔄 진행 중...
                      </span>
                    )}
                  </label>
                  {field.type === 'textarea' ? (
                    <TextArea
                      id={field.key}
                      value={formData[field.key] || ''}
                      onChange={(e) => onFieldUpdate(field.key, e.target.value)}
                      disabled={false}
                      rows={4}
                      style={{
                        borderColor: currentField && currentField.key === field.key ? '#667eea' : '#cbd5e0',
                        boxShadow: currentField && currentField.key === field.key ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                  ) : (
                    <input
                      type={field.type}
                      id={field.key}
                      value={formData[field.key] || ''}
                      onChange={(e) => onFieldUpdate(field.key, e.target.value)}
                      disabled={false}
                      style={{
                        borderColor: currentField && currentField.key === field.key ? '#667eea' : '#cbd5e0',
                        boxShadow: currentField && currentField.key === field.key ? '0 0 0 3px rgba(102, 126, 234, 0.2)' : 'none'
                      }}
                    />
                  )}
                </FormField>
              ))
            ) : (
              <div style={{ 
                padding: '20px', 
                textAlign: 'center', 
                color: '#666',
                fontStyle: 'italic'
              }}>
                설정된 필드가 없습니다.
              </div>
            )}
            <ButtonGroup>
              <ActionButton onClick={() => saveDraft(formData)}>초안 저장</ActionButton>
              <ActionButton $primary onClick={() => downloadPDF(formData, 'pdf')}>PDF 다운로드</ActionButton>
            </ButtonGroup>
          </form>
        </FormSection>

        {/* Chatbot Section */}
        {aiAssistant && (
          <ChatbotSection>
            <ChatbotHeader>
              <span>AI 어시스턴트</span>
              <CloseButton onClick={onClose}>&times;</CloseButton>
            </ChatbotHeader>

            <ChatbotMessages>
              {messages.map((message) => (
                <Message key={message.id} type={message.type}>
                  {message.content.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < message.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </Message>
              ))}
              {isLoading && (
                <TypingIndicator>
                  <span></span><span></span><span></span>
                </TypingIndicator>
              )}
              <div ref={messagesEndRef} />
            </ChatbotMessages>

            <ChatbotInput>
              {/* 자동완성 제안 */}
              {autoFillSuggestions.length > 0 && (
                <SuggestionsContainer>
                  <div style={{
                    color: '#64748b',
                    fontSize: '0.85em',
                    marginBottom: '8px',
                    fontStyle: 'italic'
                  }}>
                    아래 중 하나를 선택하거나 직접 입력해주세요:
                  </div>
                  <SuggestionsGrid>
                    {autoFillSuggestions.map((suggestion) => (
                      <AutoFillButton
                        key={suggestion}
                        onClick={() => handleAutoFill(suggestion)}
                        disabled={isLoading}
                      >
                        <span>⚡</span>
                        {suggestion}
                      </AutoFillButton>
                    ))}
                  </SuggestionsGrid>
                </SuggestionsContainer>
              )}
              
              <InputArea>
                <TextArea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    setInputValue(newValue);
                    
                    // 실시간 필드 업데이트 (입력 중에도 반영)
                    if (currentField && newValue.trim().length > 0) {
                      // 약간의 지연을 두어 타이핑 중에는 업데이트하지 않음
                      clearTimeout(inputUpdateTimeout.current);
                      inputUpdateTimeout.current = setTimeout(() => {
                        onFieldUpdate(currentField.key, newValue.trim());
                      }, 500); // 0.5초 후 업데이트
                    }
                  }}
                  onKeyDown={handleKeyPress}
                  placeholder="궁금한 점을 물어보거나 답변을 입력하세요..."
                  rows={3}
                  disabled={isLoading}
                />
                <SendButton
                  onClick={() => sendMessageRef.current && sendMessageRef.current()}
                  disabled={isLoading || !inputValue.trim()}
                >
                  전송
                </SendButton>
              </InputArea>
            </ChatbotInput>
          </ChatbotSection>
        )}
      </ModalContainer>
    </ModalOverlay>
  );
};

export default EnhancedModalChatbot;
