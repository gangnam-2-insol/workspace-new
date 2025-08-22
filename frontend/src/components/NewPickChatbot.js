import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMessageCircle, 
  FiX, 
  FiSend, 
  FiMinimize2, 
  FiMaximize2,
  FiTrash2,
  FiRefreshCw,
  FiHelpCircle,
  FiArrowRight,
  FiExternalLink,
  FiMessageSquare
} from 'react-icons/fi';
import pickChatbotApi from '../services/pickChatbotApi';

const ChatbotContainer = styled(motion.div)`
  position: fixed;
  bottom: 80px;
  right: 25px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

const ChatWindow = styled(motion.div)`
  width: 400px;
  height: 800px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 15px;

  @media (max-width: 480px) {
    width: 350px;
    height: 500px;
  }
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #2dd4bf 0%, #38bdf8 60%, #60a5fa 100%);
  color: #ffffff;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
`;

const HeaderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AgentIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
`;

const HeaderText = styled.div`
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
  p {
    margin: 0;
    font-size: 12px;
    opacity: 0.8;
  }
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  color: #ffffff;
  padding: 6px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.22);
  }
`;

const ChatBody = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageContainer = styled.div`
  display: flex;
  justify-content: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 8px;
`;

const Message = styled(motion.div)`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  
  ${props => props.$isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
  ` : `
    background: #f8f9fa;
    color: #333;
    border-bottom-left-radius: 4px;
  `}
`;

const SuggestionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SuggestionButton = styled.button`
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;

  &:hover {
    background: #0ea5e9;
    color: white;
  }
`;

const QuickActionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const QuickActionButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
`;

const ChatInput = styled.div`
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 25px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #667eea;
  }
`;

const SendButton = styled.button`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: visible;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 18px;
  border-bottom-left-radius: 4px;
  width: fit-content;
`;

const Dot = styled(motion.div)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
`;

const PageActionContainer = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
`;

const PageActionMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  
  span {
    font-size: 16px;
  }
`;

const PageActionButton = styled.button`
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

const FloatingButton = styled(motion.button)`
  position: fixed;
  bottom: 80px;
  right: 25px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2dd4bf 0%, #38bdf8 60%, #60a5fa 100%);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
  }
`;

const NewPickChatbot = ({ isOpen, onOpenChange }) => {
  // sessionStorage에서 상태 복원
  const getInitialMessages = () => {
    const savedMessages = sessionStorage.getItem('pickChatbotMessages');
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        // timestamp를 Date 객체로 변환
        return parsed.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
      } catch (e) {
        console.log('저장된 메시지 파싱 실패, 기본 메시지 사용');
      }
    }
    
    return [
      {
        id: 1,
        text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
        isUser: false,
        timestamp: new Date(),
        quickActions: [
          { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
          { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
          { title: "면접 관리", action: "navigate", target: "/interview", icon: "📅" }
        ]
      }
    ];
  };

  const [messages, setMessages] = useState(getInitialMessages);
  const [inputValue, setInputValue] = useState(sessionStorage.getItem('pickChatbotInput') || '');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 입력폼 포커스 함수
  const focusInput = () => {
    inputRef.current?.focus();
  };

  // sessionStorage에 상태 저장
  useEffect(() => {
    sessionStorage.setItem('pickChatbotMessages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    sessionStorage.setItem('pickChatbotInput', inputValue);
  }, [inputValue]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputValue.trim();
    if (!textToSend || isLoading) return;

    console.log('🔍 [DEBUG] 메시지 전송 시작:', textToSend);

    const userMessage = {
      id: Date.now(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    console.log('🔍 [DEBUG] 사용자 메시지 생성:', userMessage);

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('🔍 [DEBUG] API 호출 시작');
      // API 호출
      const response = await pickChatbotApi.chat(textToSend);
      console.log('🔍 [DEBUG] API 응답 받음:', response);
      
      const botMessage = {
        id: Date.now() + 1,
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        suggestions: response.suggestions || [],
        quickActions: response.quick_actions || [],
        pageAction: response.page_action || null
      };
      
      console.log('🔍 [DEBUG] 봇 메시지 생성:', botMessage);
      
      setMessages(prev => [...prev, botMessage]);
      
      // 페이지 액션이 있으면 자동 처리
                      if (botMessage.pageAction) {
                  console.log('🔍 [DEBUG] 페이지 액션 감지:', botMessage.pageAction);
                  setTimeout(() => {
                    if (botMessage.pageAction.action === 'navigate') {
                              // 챗창 상태를 유지하면서 페이지 이동
        sessionStorage.setItem('pickChatbotIsOpen', 'true');
                      window.location.href = botMessage.pageAction.target;
                    }
                  }, 2000); // 2초 후 자동 이동
                }
    } catch (error) {
      console.error('🔍 [DEBUG] 챗봇 API 오류:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        isUser: false,
        timestamp: new Date(),
        suggestions: ["다시 시도하기", "다른 질문하기"],
        quickActions: []
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.log('🔍 [DEBUG] 메시지 전송 완료');
      // 메시지 전송 완료 후 입력폼에 자동 포커스
      setTimeout(() => {
        focusInput();
      }, 100);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

      const handleQuickActionClick = (action) => {
      if (action.action === 'navigate') {
        // 챗창 상태를 유지하면서 페이지 이동
        sessionStorage.setItem('pickChatbotIsOpen', 'true');
        window.location.href = action.target;
      } else if (action.action === 'external') {
      // 외부 링크 열기
      window.open(action.target, '_blank');
    }
  };

  // 🚀 새 format_response_text 함수
  const formatResponseText = (text) => {
    if (!text) return text;

    // 1️⃣ 이모지 리스트 (섹션 구분용)
    const EMOJIS = ["📋", "💡", "🎯", "🔍", "📊", "🤝", "💼", "📝", "🚀", "💻"];
    
    // 2️⃣ 숫자 항목 정규식 (숫자. 뒤에 한 칸만 남김)
    const NUM_LIST_RE = /\b(\d+)\.\s+/g;
    
    // 3️⃣ 이모지 찾기
    const EMOJI_RE = new RegExp('(' + EMOJIS.map(emoji => emoji.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'g');

    // 0️⃣ 양쪽 공백 및 개행 정리
    let formattedText = text.trim();

    // 1️⃣ `**` 제거 (굵은 텍스트 표시가 필요 없으므로 없애줍니다)
    formattedText = formattedText.replace(/\*\*/g, '');

    // 2️⃣ 문장 끝(마침표·물음표·느낌표·한글 마침표) 뒤에 두 줄 빈 줄
    formattedText = formattedText.replace(/([.!?。])\s+/g, '$1\n\n');

    // 3️⃣ 불릿(•) 앞에 줄 바꿈
    formattedText = formattedText.replace(/• /g, '\n• ');

    // 4️⃣ 숫자 항목 1., 2. 앞에 줄 바꿈 **하지만** 번호 다음은 한 줄에 남김
    formattedText = formattedText.replace(NUM_LIST_RE, '$1. ');     // <-- 줄바꿈 대신 공백

    // 5️⃣ 이모지 앞에 두 줄 빈 줄
    formattedText = formattedText.replace(EMOJI_RE, '\n\n$1');

    // 6️⃣ 중복 빈 줄(3개 이상)을 2개로 정리
    formattedText = formattedText.replace(/\n{3,}/g, '\n\n');

    return formattedText;
  };



  // 강제 새로고침 감지 및 초기화 (수정)
  useEffect(() => {
    // 페이지 로드 시 강제 새로고침 감지
    const isHardRefresh = performance.navigation.type === 1 || 
                         (performance.getEntriesByType('navigation')[0] && 
                          performance.getEntriesByType('navigation')[0].type === 'reload');
    
    // Ctrl+F5 또는 F5로 강제 새로고침된 경우에만 초기화
    if (isHardRefresh) {
      console.log('🔍 강제 새로고침 감지됨 - 세션 초기화');
      sessionStorage.removeItem('pickChatbotMessages');
      sessionStorage.removeItem('pickChatbotInput');
      sessionStorage.removeItem('pickChatbotShouldReset');
      // 챗창 상태는 유지 (제거하지 않음)
      // sessionStorage.removeItem('pickChatbotIsOpen'); // 이 줄 제거
      
      // 컴포넌트 상태를 기본값으로 리셋
      const defaultMessage = {
        id: Date.now(),
        text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
        isUser: false,
        timestamp: new Date(),
        quickActions: [
          { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
          { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
          { title: "면접 관리", action: "navigate", target: "/interview", icon: "📅" }
        ]
      };
      setMessages([defaultMessage]);
      setInputValue('');
    }

    // beforeunload 이벤트로 일반 새로고침 감지 (수정)
    const handleBeforeUnload = () => {
      // 챗창 상태는 유지하고 메시지만 리셋
      sessionStorage.setItem('pickChatbotShouldReset', 'true');
      // 챗창 상태는 그대로 유지
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  // 챗봇이 열릴 때 입력폼에 자동 포커스
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        focusInput();
      }, 300);
    }
  }, [isOpen]);

  const clearChat = () => {
    pickChatbotApi.resetSession();
    const defaultMessage = {
      id: Date.now(),
      text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
      isUser: false,
      timestamp: new Date(),
      quickActions: [
        { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
        { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },
        { title: "면접 관리", action: "navigate", target: "/interview", icon: "📅" }
      ]
    };
    setMessages([defaultMessage]);
    setInputValue('');
    // sessionStorage도 초기화 (챗창 상태는 유지)
    sessionStorage.removeItem('pickChatbotMessages');
    sessionStorage.removeItem('pickChatbotInput');
    // 챗창 상태는 그대로 유지
  };

  return (
    <>
      {/* 플로팅 버튼 상태 */}
      <AnimatePresence>
        {isOpen === 'floating' && (
          <FloatingButton
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            onClick={() => {
              onOpenChange(true);
              sessionStorage.setItem('helpChatbotIsOpen', 'true');
            }}
            title="픽톡 열기"
          >
            💬
          </FloatingButton>
        )}
      </AnimatePresence>

      {/* 채팅창 상태 */}
      <AnimatePresence>
        {isOpen === true && (
          <ChatbotContainer
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
          <ChatWindow>
            <ChatHeader>
              <HeaderInfo>
                <AgentIcon>
                  💬
                </AgentIcon>
                <HeaderText>
                  <h3>픽톡</h3>
                  <p>AI 어시스턴트</p>
                </HeaderText>
              </HeaderInfo>
              <HeaderActions>
                <IconButton onClick={clearChat} title="대화 초기화">
                  <FiTrash2 size={16} />
                </IconButton>
                <IconButton onClick={() => {
                  // 플로팅 버튼 상태로 변경 (완전히 닫지 않고)
                  onOpenChange('floating');
                  sessionStorage.setItem('pickChatbotIsOpen', 'floating');
                }} title="최소화">
                  <FiMinimize2 size={18} />
                </IconButton>
              </HeaderActions>
            </ChatHeader>

            <ChatBody>
              {messages.map((message) => (
                <div key={message.id}>
                  <MessageContainer $isUser={message.isUser}>
                    <Message
                      $isUser={message.isUser}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      {message.isUser ? message.text : formatResponseText(message.text)}
                    </Message>
                  </MessageContainer>
                  
                  {/* 추천 질문 (최초 1회만 노출) */}
                  {!message.isUser && message.suggestions && message.suggestions.length > 0 && message.id === 1 && (
                    <SuggestionsContainer>
                      {message.suggestions.map((suggestion, index) => (
                        <SuggestionButton
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </SuggestionButton>
                      ))}
                    </SuggestionsContainer>
                  )}
                  
                  {/* 빠른 액션 */}
                  {!message.isUser && message.quickActions && message.quickActions.length > 0 && (
                    <QuickActionsContainer>
                      {message.quickActions.map((action, index) => (
                        <QuickActionButton
                          key={index}
                          onClick={() => handleQuickActionClick(action)}
                        >
                          <span>{action.icon}</span>
                          {action.title}
                          <FiArrowRight size={12} />
                        </QuickActionButton>
                      ))}
                    </QuickActionsContainer>
                  )}
                  

                </div>
              ))}
              
              {isLoading && (
                <MessageContainer $isUser={false}>
                  <LoadingDots>
                    <Dot
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    />
                    <Dot
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    />
                    <Dot
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    />
                  </LoadingDots>
                </MessageContainer>
              )}
              <div ref={messagesEndRef} />
            </ChatBody>

            <ChatInput>
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="메시지를 입력하세요..."
                disabled={isLoading}
              />
              <SendButton 
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading}
              >
                <FiSend size={18} />
              </SendButton>
            </ChatInput>
          </ChatWindow>
        </ChatbotContainer>
        )}
      </AnimatePresence>
    </>
  );
};

export default NewPickChatbot;
