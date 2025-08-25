import styled from 'styled-components';
import { motion } from 'framer-motion';

export const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
`;

export const StatCard = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }

  ${props => {
    switch (props.$variant) {
      case 'total':
        return `
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        `;
      case 'document_passed':
        return `
          background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
          color: white;
        `;
      case 'final_passed':
        return `
          background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
          color: white;
        `;
      case 'waiting':
        return `
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
          color: white;
        `;
      case 'rejected':
        return `
          background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
          color: white;
        `;
      default:
        return `
          background: white;
          color: var(--text-primary);
        `;
    }
  }}
`;

export const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
`;

export const StatContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

export const StatValue = styled(motion.div)`
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
`;

export const StatLabel = styled.div`
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
`;

export const StatPercentage = styled.div`
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
`;

export const MailButton = styled.button`
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.2);
  color: inherit;
  border: none;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;
