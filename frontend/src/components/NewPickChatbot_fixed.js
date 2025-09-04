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
  height: 85%;
  right: 25px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

// 배경 오버레이 추가
const BackgroundOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  z-index: 999;
  cursor: pointer;
`;

const ChatWindow = styled(motion.div)`
  width: 400px;
  height: 100%;
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
          { title: "채용공고 조회", action: "chat", message: "채용공고 목록을 보여주세요", icon: "📋" },
          { title: "지원자 통계", action: "chat", message: "지원자 통계를 보여주세요", icon: "📊" },
          { title: "메일 발송", action: "chat", message: "메일 템플릿을 보여주세요", icon: "📧" }
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
    const startTime = Date.now();
    const textToSend = messageText || inputValue.trim();
    if (!textToSend || isLoading) return;

    console.group('🚀 [PICK-TALK FRONTEND] 메시지 전송 프로세스');
    console.log('📝 전송 메시지:', textToSend);

    const userMessage = {
      id: Date.now(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await pickChatbotApi.chat(textToSend);
      console.log('✅ API 응답 수신 완료');

      const botMessage = {
        id: Date.now() + 1,
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        suggestions: response.suggestions || [],
        quickActions: response.quick_actions || [],
        pageAction: response.page_action || null
      };

      setMessages(prev => [...prev, botMessage]);

      // 페이지 액션이 있으면 자동 처리
      if (botMessage.pageAction) {
        console.log('🔍 [DEBUG] 페이지 액션 감지:', botMessage.pageAction);

        const handlePageAction = () => {
          if (botMessage.pageAction.action === 'navigate') {
            const pageAction = botMessage.pageAction;
            console.log('🎯 [페이지 네비게이션] 부드러운 이동 시작:', pageAction);

            if (pageAction.auto_fill_data) {
              sessionStorage.setItem('autoFillJobPostingData', JSON.stringify(pageAction.auto_fill_data));
            }
            sessionStorage.setItem('pickChatbotIsOpen', 'true');

            if (window.handlePageAction && pageAction.path) {
              window.handlePageAction(`changePage:${pageAction.path.replace('/', '')}`);
            } else if (pageAction.path) {
              window.location.href = pageAction.path;
            }
          } else if (botMessage.pageAction.action === 'openAIJobRegistration') {
            sessionStorage.setItem('pickChatbotIsOpen', 'true');
            if (botMessage.pageAction.auto_fill_data) {
              const autoFillParam = encodeURIComponent(JSON.stringify(botMessage.pageAction.auto_fill_data));
              window.location.href = `/job-posting?autoFill=${autoFillParam}`;
            } else {
              window.location.href = '/job-posting';
            }
          }
        };

        // 페이지 액션이 있으면 사용자에게 부드러운 안내
        if (botMessage.pageAction.message || botMessage.pageAction.action === 'navigate') {
          console.log('🎯 [페이지 이동] 조건 충족 - 자동 이동 시작');
          const actionMessage = botMessage.pageAction.message || "페이지로 이동합니다";
          const navigationMessage = {
            id: Date.now() + 2,
            text: `✨ ${actionMessage}\n\n🌟 **3초 후 자동으로 페이지 이동됩니다**`,
            isUser: false,
            timestamp: new Date(),
            isNavigationPrompt: true,
            pageAction: botMessage.pageAction,
            suggestions: [
              "🚀 지금 바로 이동하기"
            ],
            quickActions: [
              { title: "🚀 지금 이동", action: "navigate_smooth", target: botMessage.pageAction.path, icon: "🚀" }
            ]
          };

          setMessages(prev => [...prev, navigationMessage]);

          // 카운트다운 표시
          let countdown = 3;
          const countdownInterval = setInterval(() => {
            if (countdown > 0) {
              setMessages(prev => prev.map(msg =>
                msg.id === navigationMessage.id
                  ? { ...msg, text: `✨ ${actionMessage}\n\n🌟 **${countdown}초 후 자동으로 페이지 이동됩니다**` }
                  : msg
              ));
              countdown--;
            } else {
              clearInterval(countdownInterval);
              handlePageAction();
            }
          }, 1000);
        } else {
          setTimeout(handlePageAction, 2000);
        }
      }
    } catch (error) {
      console.error('❌ 에러 발생:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "죄송합니다. 일시적인 오류가 발생했습니다.",
        isUser: false,
        timestamp: new Date(),
        suggestions: ["다시 시도하기", "다른 질문하기"],
        quickActions: [],
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      console.groupEnd();
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
    console.log('🎯 [SUGGESTION CLICK] 클릭된 제안:', suggestion);

    if (suggestion === "🚀 지금 바로 이동하기" || suggestion === "페이지로 이동하기") {
      console.log('✨ [부드러운 이동] 사용자가 즉시 이동 선택');
      const currentMessage = messages[messages.length - 1];
      if (currentMessage && currentMessage.isNavigationPrompt && currentMessage.pageAction) {
        const pageAction = currentMessage.pageAction;
        if (pageAction.action === 'navigate') {
          if (pageAction.auto_fill_data) {
            sessionStorage.setItem('autoFillJobPostingData', JSON.stringify(pageAction.auto_fill_data));
          }
          sessionStorage.setItem('pickChatbotIsOpen', 'true');

          if (window.handlePageAction && pageAction.path) {
            window.handlePageAction(`changePage:${pageAction.path.replace('/', '')}`);
          } else {
            window.location.href = pageAction.path;
          }
        } else if (pageAction.action === 'openAIJobRegistration') {
          sessionStorage.setItem('pickChatbotIsOpen', 'true');
          if (pageAction.auto_fill_data) {
            const autoFillParam = encodeURIComponent(JSON.stringify(pageAction.auto_fill_data));
            window.location.href = `/job-posting?autoFill=${autoFillParam}`;
          } else {
            window.location.href = '/job-posting';
          }
        }
        return;
      }
    }

    // 기존 제안 처리 로직
    handleSendMessage(suggestion);
  };

  const handleQuickActionClick = (action) => {
    if (action.action === 'navigate') {
      sessionStorage.setItem('pickChatbotIsOpen', 'true');
      window.location.href = action.target;
    } else if (action.action === 'external') {
      window.open(action.target, '_blank');
    } else if (action.action === 'openAIJobRegistration') {
      sessionStorage.setItem('pickChatbotIsOpen', 'true');
      if (action.auto_fill_data) {
        const autoFillParam = encodeURIComponent(JSON.stringify(action.auto_fill_data));
        window.location.href = `/job-posting?autoFill=${autoFillParam}`;
      } else {
        window.location.href = '/job-posting';
      }
    } else if (action.action === 'register_job_posting') {
      // 등록하기 버튼 클릭 시
      handleSendMessage('등록하기');
    } else if (action.action === 'cancel_job_posting') {
      // 취소 버튼 클릭 시
      handleSendMessage('취소할게요');
    } else if (action.action === 'chat') {
      // 채팅 메시지 전송
      if (action.message) {
        handleSendMessage(action.message);
      }
    }
  };

  // 텍스트 포맷팅 함수
  const formatResponseText = (text) => {
    if (!text) return text;

    const EMOJIS = ["📋", "💡", "🎯", "🔍", "📊", "🤝", "💼", "📝", "🚀", "💻"];
    const NUM_LIST_RE = /\b(\d+)\.\s+/g;
    const EMOJI_RE = new RegExp('(' + EMOJIS.map(emoji => emoji.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'g');

    let formattedText = text.trim();
    formattedText = formattedText.replace(/\*\*/g, '');
    formattedText = formattedText.replace(/([.!?。])\s+/g, '$1\n\n');
    formattedText = formattedText.replace(/• /g, '\n• ');
    formattedText = formattedText.replace(NUM_LIST_RE, '$1. ');
    formattedText = formattedText.replace(EMOJI_RE, '\n\n$1');
    formattedText = formattedText.replace(/\n{3,}/g, '\n\n');

    return formattedText;
  };

  // 강제 새로고침 감지 및 초기화
  useEffect(() => {
    const isHardRefresh = performance.navigation.type === 1 ||
                         (performance.getEntriesByType('navigation')[0] &&
                          performance.getEntriesByType('navigation')[0].type === 'reload');

    if (isHardRefresh) {
      console.log('🔍 강제 새로고침 감지됨 - 세션 초기화');
      sessionStorage.removeItem('pickChatbotMessages');
      sessionStorage.removeItem('pickChatbotInput');
      sessionStorage.removeItem('pickChatbotShouldReset');

      const defaultMessage = {
        id: Date.now(),
        text: "안녕하세요! AI 채용 관리 시스템의 픽톡입니다. 무엇을 도와드릴까요?",
        isUser: false,
        timestamp: new Date(),
        quickActions: [
          { title: "채용공고 등록", action: "navigate", target: "/job-posting", icon: "📝" },
          { title: "지원자 관리", action: "navigate", target: "/applicants", icon: "👥" },

        ]
      };
      setMessages([defaultMessage]);
      setInputValue('');
    }

    const handleBeforeUnload = () => {
      sessionStorage.setItem('pickChatbotShouldReset', 'true');
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

      ]
    };
    setMessages([defaultMessage]);
    setInputValue('');
    sessionStorage.removeItem('pickChatbotMessages');
    sessionStorage.removeItem('pickChatbotInput');
  };

  // 배경 클릭 핸들러
  const handleBackgroundClick = (e) => {
    if (e.target === e.currentTarget) {
      onOpenChange('floating');
      sessionStorage.setItem('pickChatbotIsOpen', 'floating');
    }
  };

  return (
    <>
      {/* 플로팅 버튼 - 항상 표시 */}
      <FloatingButton
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        onClick={() => {
          onOpenChange(true);
          sessionStorage.setItem('pickChatbotIsOpen', 'true');
        }}
        title="픽톡 열기"
        style={{ display: isOpen === true ? 'none' : 'flex' }}
      >
        💬
      </FloatingButton>

      {/* 채팅창 상태 */}
      <AnimatePresence>
        {isOpen === true && (
          <>
            {/* 배경 오버레이 */}
            <BackgroundOverlay
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={handleBackgroundClick}
            />
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
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default NewPickChatbot;
