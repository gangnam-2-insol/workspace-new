import React, { useState, useCallback, useEffect, useRef } from 'react';

const AIChatbot = ({
  isOpen,
  onClose,
  onNavigate = null
}) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showEndChat, setShowEndChat] = useState(false);
  const [endChatTimer, setEndChatTimer] = useState(null);
  const [countdown, setCountdown] = useState(3);
  const [suggestions, setSuggestions] = useState([
    '채용 정보',
    '지원하기',
    '회사 소개',
    '고객지원',
    '문의하기',
    '홈으로'
  ]);
  const messagesEndRef = useRef(null);
  const messagesRef = useRef([]);
  const inputRef = useRef(null);

  // messages 상태가 변경될 때마다 ref 업데이트
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // AI 응답 후 자동으로 입력 영역에 포커스
  useEffect(() => {
    if (!isLoading && messages.length > 0) {
      // 마지막 메시지가 AI 응답인 경우에만 포커스
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.type === 'bot') {
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
      }
    }
  }, [messages, isLoading]);

  // 초기 메시지 설정
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          type: 'bot',
          content: '안녕하세요! 무엇을 도와드릴까요? 키워드를 말씀해주시면 해당 페이지로 안내해드릴게요!',
          timestamp: new Date(),
          id: 'welcome'
        }
      ]);
    }
  }, [isOpen, messages.length]);

  // 모달이 열릴 때 플로팅 챗봇 숨기기
  useEffect(() => {
    if (isOpen) {
      // 플로팅 챗봇 숨기기
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'none';
      }

      // 커스텀 이벤트로 플로팅 챗봇에 알림
      window.dispatchEvent(new CustomEvent('hideFloatingChatbot'));
    } else {
      // 모달이 닫힐 때 플로팅 챗봇 다시 보이기
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'flex';
      }

      // 커스텀 이벤트로 플로팅 챗봇에 알림
      window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
    }
  }, [isOpen]);

  // 대화종료 타이머 정리
  useEffect(() => {
    return () => {
      if (endChatTimer) {
        clearTimeout(endChatTimer);
      }
    };
  }, [endChatTimer]);

  // 키워드 인식 함수
  const detectKeywords = useCallback((userInput) => {
    const keywords = {
      '채용': '/recruit',
      '구인': '/recruit',
      '채용공고': '/recruit',
      '구인공고': '/recruit',
      '공고': '/recruit',
      '지원': '/apply',
      '지원서': '/apply',
      '이력서': '/apply',
      '신청': '/apply',
      '회사': '/company',
      '기업': '/company',
      '소개': '/company',
      '정보': '/info',
      '안내': '/info',
      '도움': '/help',
      '고객지원': '/help',
      '문의': '/contact',
      '연락': '/contact',
      '메인': '/',
      '홈': '/',
      '첫페이지': '/'
    };

    const lowerInput = userInput.toLowerCase();
    for (const [keyword, path] of Object.entries(keywords)) {
      if (lowerInput.includes(keyword)) {
        console.log(`[AIChatbot] 키워드 감지: ${keyword} -> ${path}`);
        return { keyword, path };
      }
    }
    return null;
  }, []);

  const handleAIResponse = useCallback(async (userInput) => {
    if (!userInput.trim()) return;

    // 키워드 감지
    const keywordMatch = detectKeywords(userInput);
    if (keywordMatch && onNavigate) {
      console.log(`[AIChatbot] 페이지 이동: ${keywordMatch.path}`);
      
      // 키워드 감지 메시지 추가
      const keywordMessage = {
        type: 'bot',
        content: `"${keywordMatch.keyword}" 키워드를 감지했습니다. ${keywordMatch.path} 페이지로 이동합니다.`,
        timestamp: new Date(),
        id: `keyword-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };
      
      setMessages(prev => [...prev, {
        type: 'user',
        content: userInput,
        timestamp: new Date(),
        id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      }, keywordMessage]);
      
      // 잠시 후 페이지 이동
      setTimeout(() => {
        onNavigate(keywordMatch.path);
      }, 1500);
      
      setInputValue('');
      return;
    }

    // 사용자 메시지를 먼저 추가
    const userMessage = {
      type: 'user',
      content: userInput,
      timestamp: new Date(),
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    // 사용자 메시지를 즉시 UI에 추가
    setMessages(prev => [...prev, userMessage]);

    // 입력값을 클리어하고 로딩 상태 설정
    setInputValue('');
    setIsLoading(true);
    setShowSuggestions(false); // 추천 리스트 닫기

    try {
      const response = await fetch('/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          conversation_history: messagesRef.current.slice(-5).map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('[AIChatbot] AI 응답:', data);

      // AI 응답 메시지 추가
      const aiMessage = {
        type: 'bot',
        content: data.content || data.message,
        timestamp: new Date(),
        id: `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        responseType: data.response_type || 'conversation',
        selectableItems: data.selectable_items || [],
        suggestions: data.suggestions || []
      };

      // AI 응답 메시지만 추가 (사용자 메시지는 이미 추가됨)
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('[AIChatbot] AI 응답 처리 중 오류:', error);

      const errorMessage = {
        type: 'bot',
        content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date(),
        id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [detectKeywords, onNavigate]);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      handleAIResponse(inputValue);
    }
  }, [inputValue, isLoading, handleAIResponse]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    handleAIResponse(suggestion);
  }, [handleAIResponse]);

  const handleQuickSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    setShowSuggestions(false);
  }, []);

  const toggleSuggestions = useCallback(() => {
    setShowSuggestions(prev => !prev);
  }, []);

  const handleEndChat = useCallback(() => {
    setShowEndChat(true);
    setCountdown(3);
    
    // 1초마다 카운트다운
    const countdownInterval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    // 3초 후 자동으로 종료
    const timer = setTimeout(() => {
      setMessages([]);
      setInputValue('');
      setShowSuggestions(false);
      setShowEndChat(false);
      setCountdown(3);
      
      // 플로팅 챗봇 다시 보이기
      const floatingChatbot = document.querySelector('.floating-chatbot');
      if (floatingChatbot) {
        floatingChatbot.style.display = 'flex';
      }
      
      onClose();
    }, 3000);
    
    setEndChatTimer(timer);
  }, [onClose]);

  const handleCancelEndChat = useCallback(() => {
    setShowEndChat(false);
    setCountdown(3);
    if (endChatTimer) {
      clearTimeout(endChatTimer);
      setEndChatTimer(null);
    }
  }, [endChatTimer]);

  if (!isOpen) return null;

  return (
    <div
      className="ai-chatbot-overlay"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
    >
      <div
        className="ai-chatbot-container"
        style={{
          background: 'white',
          borderRadius: '16px',
          width: '90%',
          maxWidth: '600px',
          height: '95%',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          position: 'relative'
        }}
      >
        <div
          className="ai-chatbot-header"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '24px 32px',
            borderBottom: '1px solid #e2e8f0',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '16px 16px 0 0'
          }}
        >
          <h3 className="ai-chatbot-title" style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
            AI 챗봇
          </h3>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button
              className="ai-chatbot-end-chat-btn"
              onClick={handleEndChat}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'white',
                fontSize: '12px',
                cursor: 'pointer',
                padding: '6px 12px',
                borderRadius: '16px',
                transition: 'all 0.3s ease',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
            >
              대화종료
            </button>
            <button
              className="ai-chatbot-close-btn"
              onClick={() => {
                // 플로팅 챗봇 다시 표시
                const floatingChatbot = document.querySelector('.floating-chatbot');
                if (floatingChatbot) {
                  floatingChatbot.style.display = 'flex';
                }
                // 커스텀 이벤트로 플로팅 챗봇에 알림
                window.dispatchEvent(new CustomEvent('showFloatingChatbot'));
                // 원래 onClose 콜백 호출
                onClose();
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '24px',
                cursor: 'pointer',
                padding: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
              onMouseLeave={(e) => e.target.style.background = 'none'}
            >
              ×
            </button>
          </div>
        </div>

        <div
          className="ai-chatbot-body"
          style={{
            flex: 1,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <div
            className="ai-chatbot-messages-container"
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '20px',
              maxHeight: '60vh'
            }}
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={`ai-chatbot-message ai-chatbot-message-${message.type}`}
                style={{
                  marginBottom: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: message.type === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                <div
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    backgroundColor: message.type === 'user' ? '#667eea' : '#f1f5f9',
                    color: message.type === 'user' ? 'white' : '#1e293b',
                    fontSize: '14px',
                    lineHeight: '1.4',
                    wordBreak: 'break-word',
                    position: 'relative'
                  }}
                >
                  {message.content}
                  <div
                    style={{
                      fontSize: '11px',
                      opacity: 0.7,
                      marginTop: '4px',
                      textAlign: message.type === 'user' ? 'right' : 'left'
                    }}
                  >
                    {message.timestamp ? message.timestamp.toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div
                className="ai-chatbot-message ai-chatbot-message-bot"
                style={{
                  marginBottom: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start'
                }}
              >
                <div
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    backgroundColor: '#f1f5f9',
                    color: '#1e293b',
                    fontSize: '14px',
                    lineHeight: '1.4'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ display: 'flex', gap: '2px' }}>
                      <div
                        style={{
                          width: '4px',
                          height: '4px',
                          borderRadius: '50%',
                          backgroundColor: '#667eea',
                          animation: 'pulse 1.4s ease-in-out infinite both'
                        }}
                      />
                      <div
                        style={{
                          width: '4px',
                          height: '4px',
                          borderRadius: '50%',
                          backgroundColor: '#667eea',
                          animation: 'pulse 1.4s ease-in-out infinite both 0.2s'
                        }}
                      />
                      <div
                        style={{
                          width: '4px',
                          height: '4px',
                          borderRadius: '50%',
                          backgroundColor: '#667eea',
                          animation: 'pulse 1.4s ease-in-out infinite both 0.4s'
                        }}
                      />
                    </div>
                    <span>AI가 응답을 생성하고 있습니다...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 추천 메시지 영역 */}
          <div
            className="ai-chatbot-suggestions-container"
            style={{
              padding: '16px 20px',
              borderTop: '1px solid #e2e8f0',
              backgroundColor: '#f8fafc'
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px'
              }}
            >
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>
                추천 메시지
              </span>
              <button
                onClick={toggleSuggestions}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#667eea',
                  fontSize: '12px',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#e2e8f0'}
                onMouseLeave={(e) => e.target.style.background = 'none'}
              >
                {showSuggestions ? '접기' : '펼치기'}
              </button>
            </div>
            
            {showSuggestions && (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                  gap: '8px'
                }}
              >
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    style={{
                      background: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      padding: '8px 12px',
                      fontSize: '12px',
                      color: '#374151',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#f1f5f9';
                      e.target.style.borderColor = '#cbd5e0';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'white';
                      e.target.style.borderColor = '#e2e8f0';
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 입력 영역 */}
          <div
            className="ai-chatbot-input-container"
            style={{
              padding: '20px',
              borderTop: '1px solid #e2e8f0',
              backgroundColor: 'white'
            }}
          >
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="메시지를 입력하세요..."
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '24px',
                  fontSize: '14px',
                  resize: 'none',
                  minHeight: '48px',
                  maxHeight: '120px',
                  outline: 'none',
                  transition: 'all 0.3s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#667eea';
                  e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e2e8f0';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                style={{
                  background: inputValue.trim() && !isLoading ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#e2e8f0',
                  color: inputValue.trim() && !isLoading ? 'white' : '#9ca3af',
                  border: 'none',
                  borderRadius: '50%',
                  width: '48px',
                  height: '48px',
                  cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.3s ease',
                  fontSize: '18px'
                }}
                onMouseEnter={(e) => {
                  if (inputValue.trim() && !isLoading) {
                    e.target.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (inputValue.trim() && !isLoading) {
                    e.target.style.transform = 'scale(1)';
                  }
                }}
              >
                ➤
              </button>
            </form>
          </div>
        </div>

        {/* 대화종료 모달 */}
        {showEndChat && (
          <div
            className="ai-chatbot-end-chat-message"
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10000,
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
            }}
          >
            <div
              className="ai-chatbot-end-chat-content"
              style={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '16px',
                padding: '32px',
                textAlign: 'center',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                maxWidth: '400px',
                width: '90%'
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>🤖</div>
                <h3 style={{ margin: '0 0 8px 0', color: '#1e293b', fontSize: '18px' }}>
                  대화를 종료합니다
                </h3>
                <p style={{ margin: '0 0 16px 0', color: '#64748b', fontSize: '14px' }}>
                  {countdown}초 후 자동으로 종료됩니다.
                </p>
              </div>
              <button
                onClick={handleCancelEndChat}
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px 24px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => e.target.style.transform = 'translateY(-1px)'}
                onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
              >
                취소
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 80%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
          }
          40% {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
};

export default AIChatbot; 