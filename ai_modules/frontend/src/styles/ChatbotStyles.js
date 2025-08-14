import styled, { keyframes } from 'styled-components';

// 애니메이션 정의
export const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export const slideIn = keyframes`
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
`;

export const loadingDots = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
`;

// 공통 스타일 컴포넌트
export const ChatContainer = styled.div`
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
`;

export const ChatButton = styled.button`
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #667eea;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    background-color: #5a67d8;
  }
`;

export const ChatWindow = styled.div`
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  animation: ${fadeIn} 0.3s ease-out;
`;

export const ChatHeader = styled.div`
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const ChatInput = styled.div`
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
`;

export const Input = styled.input`
  flex: 1;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
  font-size: 14px;

  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
  }
`;

export const SendButton = styled.button`
  padding: 12px 24px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: #5a67d8;
  }

  &:disabled {
    background-color: #e5e7eb;
    cursor: not-allowed;
  }
`;