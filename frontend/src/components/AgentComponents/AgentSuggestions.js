import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const SuggestionsContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SuggestionButton = styled(motion.button)`
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  color: #0ea5e9;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;

  &:hover {
    background: #0ea5e9;
    color: white;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const AgentSuggestions = ({ suggestions = [], onSuggestionClick, disabled = false }) => {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  const handleSuggestionClick = (suggestion) => {
    if (disabled || !onSuggestionClick) return;
    onSuggestionClick(suggestion);
  };

  return (
    <SuggestionsContainer>
      {suggestions.map((suggestion, index) => (
        <SuggestionButton
          key={index}
          onClick={() => handleSuggestionClick(suggestion)}
          disabled={disabled}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          {suggestion}
        </SuggestionButton>
      ))}
    </SuggestionsContainer>
  );
};

export default AgentSuggestions;
