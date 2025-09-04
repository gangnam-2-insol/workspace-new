import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiArrowRight } from 'react-icons/fi';

const QuickActionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const QuickActionButton = styled(motion.button)`
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
  white-space: nowrap;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const ActionIcon = styled.span`
  font-size: 14px;
`;

const AgentQuickActions = ({ actions = [], onActionClick, disabled = false }) => {
  if (!actions || actions.length === 0) {
    return null;
  }

  const handleActionClick = (action) => {
    if (disabled || !onActionClick) return;
    onActionClick(action);
  };

  return (
    <QuickActionsContainer>
      {actions.map((action, index) => (
        <QuickActionButton
          key={index}
          onClick={() => handleActionClick(action)}
          disabled={disabled}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <ActionIcon>{action.icon}</ActionIcon>
          {action.title}
          <FiArrowRight size={12} />
        </QuickActionButton>
      ))}
    </QuickActionsContainer>
  );
};

export default AgentQuickActions;
