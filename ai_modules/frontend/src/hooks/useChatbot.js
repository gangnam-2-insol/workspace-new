import { useState, useEffect, useCallback } from 'react';

const useChatbot = (apiUrl) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 웹소켓 연결 관리
  const [ws, setWs] = useState(null);
  
  useEffect(() => {
    const websocket = new WebSocket(apiUrl.replace('http', 'ws') + '/ws');
    
    websocket.onopen = () => {
      console.log('WebSocket Connected');
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        type: 'bot',
        content: data.message,
        timestamp: new Date()
      }]);
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setError('WebSocket connection failed');
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, [apiUrl]);

  // 메시지 전송 함수
  const sendMessage = useCallback(async (message) => {
    if (!message.trim()) return;

    setIsLoading(true);
    setError(null);

    // 사용자 메시지 추가
    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // WebSocket이 연결되어 있으면 WebSocket 사용
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          message: message,
          type: 'chat'
        }));
      } else {
        // WebSocket이 없으면 HTTP 요청
        const response = await fetch(`${apiUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            type: 'chat'
          }),
        });

        if (!response.ok) {
          throw new Error('API request failed');
        }

        const data = await response.json();
        
        setMessages(prev => [...prev, {
          type: 'bot',
          content: data.message,
          timestamp: new Date()
        }]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, ws]);

  // 대화 기록 초기화
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages
  };
};

export default useChatbot;