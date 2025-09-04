import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const MessageContainer = styled(motion.div)`
  display: flex;
  justify-content: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 16px;
`;

const Message = styled.div`
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

const AgentIcon = styled.span`
  margin-right: 8px;
  font-size: 16px;
`;

const UserIcon = styled.span`
  margin-left: 8px;
  font-size: 16px;
`;

const MessageTimestamp = styled.div`
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: ${props => props.$isUser ? 'right' : 'left'};
`;

const AgentMessage = ({ message, isUser, timestamp, showTimestamp = true }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <MessageContainer
      $isUser={isUser}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Message $isUser={isUser}>
        {!isUser && <AgentIcon>🤖</AgentIcon>}
        {message}
        {isUser && <UserIcon>👤</UserIcon>}

        {showTimestamp && (
          <MessageTimestamp $isUser={isUser}>
            {formatTime(timestamp)}
          </MessageTimestamp>
        )}
      </Message>
    </MessageContainer>
  );
};

export default AgentMessage;
