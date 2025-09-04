import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

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

const AgentLoadingDots = () => {
  return (
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
  );
};

export default AgentLoadingDots;
