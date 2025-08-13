import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';

/**
 * LangGraph 기반 AI 채팅봇 컴포넌트
 * 실제 LangGraph 라이브러리를 사용하는 Agent 시스템과 통신
 */

const ChatContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  border: 2px solid #667eea;
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: 10px 10px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ChatTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
`;

const LangGraphBadge = styled.span`
  background: #ff6b6b;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: bold;
`;

const ChatBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  animation: fadeIn 0.3s ease-in;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const MessageAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
`;

const UserAvatar = styled(MessageAvatar)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
`;

const BotAvatar = styled(MessageAvatar)`
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
  color: white;
`;

const MessageContent = styled.div`
  flex: 1;
  padding: 12px 16px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.4;
`;

const UserMessage = styled(MessageContent)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
`;

const BotMessage = styled(MessageContent)`
  background: #f8f9fa;
  color: #333;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
`;

const WorkflowTrace = styled.div`
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 8px 12px;
  margin-top: 8px;
  font-size: 12px;
  color: #856404;
  font-family: 'Courier New', monospace;
`;

const InputContainer = styled.div`
  padding: 16px;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 8px;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.3s ease;
  
  &:focus {
    border-color: #667eea;
  }
`;

const SendButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s ease-in-out infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const ToggleButton = styled.button`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: transform 0.2s ease;
  z-index: 999;
  
  &:hover {
    transform: scale(1.1);
  }
`;

const LangGraphChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemInfo, setSystemInfo] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // 시스템 정보 가져오기
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/chatbot/langgraph-info`);
        const data = await response.json();
        setSystemInfo(data);
        
        if (data.available) {
          // 시스템 정보를 첫 번째 메시지로 추가
          setMessages([{
            id: 'system-info',
            type: 'bot',
            content: `🤖 LangGraph Agent 시스템이 준비되었습니다!\n\n📋 사용 가능한 기능:\n• 정보 검색\n• 계산 도구\n• 채용공고 작성\n• 데이터베이스 조회\n• 일반 대화\n\n💡 자연스럽게 질문해보세요!`,
            timestamp: new Date(),
            workflowTrace: null
          }]);
        } else {
          setMessages([{
            id: 'system-error',
            type: 'bot',
            content: `❌ LangGraph 시스템을 사용할 수 없습니다.\n\n${data.message}`,
            timestamp: new Date(),
            workflowTrace: null
          }]);
        }
      } catch (error) {
        console.error('LangGraph 시스템 정보 조회 실패:', error);
        setMessages([{
          id: 'system-error',
          type: 'bot',
          content: '❌ LangGraph 시스템에 연결할 수 없습니다.',
          timestamp: new Date(),
          workflowTrace: null
        }]);
      }
    };

    fetchSystemInfo();
  }, [API_BASE_URL]);

  const sendMessage = useCallback(async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/langgraph-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: inputValue,
          conversation_history: messages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        })
      });

      const data = await response.json();

      if (response.ok) {
        // 워크플로우 추적 정보 추출
        let botContent = data.message;
        let workflowTrace = null;

        // 워크플로우 추적 정보가 포함되어 있는지 확인
        if (botContent.includes('🔍 워크플로우 추적:')) {
          const parts = botContent.split('🔍 워크플로우 추적:');
          botContent = parts[0].trim();
          workflowTrace = parts[1]?.trim() || null;
        }

        const botMessage = {
          id: `bot-${Date.now()}`,
          type: 'bot',
          content: botContent,
          timestamp: new Date(),
          workflowTrace: workflowTrace
        };

        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: `error-${Date.now()}`,
          type: 'bot',
          content: `❌ 오류가 발생했습니다: ${data.detail || '알 수 없는 오류'}`,
          timestamp: new Date(),
          workflowTrace: null
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('LangGraph 채팅 오류:', error);
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: 'bot',
        content: '❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.',
        timestamp: new Date(),
        workflowTrace: null
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, messages, isLoading, API_BASE_URL]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!isOpen) {
    return (
      <ToggleButton onClick={() => setIsOpen(true)} title="LangGraph 채팅봇 열기">
        🤖
      </ToggleButton>
    );
  }

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>LangGraph AI Assistant</ChatTitle>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <LangGraphBadge>LangGraph</LangGraphBadge>
          <button
            onClick={() => setIsOpen(false)}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              fontSize: '18px'
            }}
          >
            ✕
          </button>
        </div>
      </ChatHeader>

      <ChatBody>
        <MessagesContainer>
          {messages.map((message) => (
            <Message key={message.id}>
              {message.type === 'user' ? (
                <>
                  <UserAvatar>U</UserAvatar>
                  <UserMessage>
                    {message.content}
                    <div style={{ fontSize: '10px', opacity: 0.7, marginTop: '4px' }}>
                      {formatTime(message.timestamp)}
                    </div>
                  </UserMessage>
                </>
              ) : (
                <>
                  <BotAvatar>AI</BotAvatar>
                  <BotMessage>
                    {message.content}
                    {message.workflowTrace && (
                      <WorkflowTrace>
                        🔍 워크플로우: {message.workflowTrace}
                      </WorkflowTrace>
                    )}
                    <div style={{ fontSize: '10px', opacity: 0.7, marginTop: '4px' }}>
                      {formatTime(message.timestamp)}
                    </div>
                  </BotMessage>
                </>
              )}
            </Message>
          ))}
          
          {isLoading && (
            <Message>
              <BotAvatar>AI</BotAvatar>
              <BotMessage>
                <LoadingSpinner />
                <span style={{ marginLeft: '8px' }}>LangGraph 처리 중...</span>
              </BotMessage>
            </Message>
          )}
        </MessagesContainer>

        <InputContainer>
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="LangGraph AI에게 질문해보세요..."
            disabled={isLoading || !systemInfo?.available}
          />
          <SendButton 
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim() || !systemInfo?.available}
          >
            {isLoading ? <LoadingSpinner /> : '→'}
          </SendButton>
        </InputContainer>
      </ChatBody>
    </ChatContainer>
  );
};

export default LangGraphChatbot;
