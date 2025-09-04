import styled from 'styled-components';

export const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea0a 0%, #764ba20a 100%);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

export const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  backdrop-filter: blur(10px);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => {
      switch (props.$variant) {
        case 'total': return 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))';
        case 'document_passed': return 'linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(34, 197, 94, 0.1))';
        case 'final_passed': return 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.1))';
        case 'waiting': return 'linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1))';
        case 'rejected': return 'linear-gradient(135deg, rgba(248, 113, 113, 0.1), rgba(239, 68, 68, 0.1))';
        default: return 'linear-gradient(135deg, rgba(229, 231, 235, 0.1), rgba(209, 213, 219, 0.1))';
      }
    }};
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: ${props => {
      switch (props.$variant) {
        case 'total': return 'linear-gradient(90deg, #667eea, #764ba2)';
        case 'document_passed': return 'linear-gradient(90deg, #4ade80, #22c55e)';
        case 'final_passed': return 'linear-gradient(90deg, #8b5cf6, #7c3aed)';
        case 'waiting': return 'linear-gradient(90deg, #fbbf24, #f59e0b)';
        case 'rejected': return 'linear-gradient(90deg, #f87171, #ef4444)';
        default: return 'linear-gradient(90deg, #e5e7eb, #d1d5db)';
      }
    }};
    box-shadow: 0 0 20px ${props => {
      switch (props.$variant) {
        case 'total': return 'rgba(102, 126, 234, 0.5)';
        case 'document_passed': return 'rgba(74, 222, 128, 0.5)';
        case 'final_passed': return 'rgba(139, 92, 246, 0.5)';
        case 'waiting': return 'rgba(251, 191, 36, 0.5)';
        case 'rejected': return 'rgba(248, 113, 113, 0.5)';
        default: return 'rgba(229, 231, 235, 0.5)';
      }
    }};
  }

  &:hover {
    transform: translateY(-12px) scale(1.05);
    box-shadow:
      0 20px 60px rgba(0, 0, 0, 0.15),
      0 0 0 1px rgba(255, 255, 255, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.8),
      0 0 30px ${props => {
        switch (props.$variant) {
          case 'total': return 'rgba(102, 126, 234, 0.3)';
          case 'document_passed': return 'rgba(74, 222, 128, 0.3)';
          case 'final_passed': return 'rgba(139, 92, 246, 0.3)';
          case 'waiting': return 'rgba(251, 191, 36, 0.3)';
          case 'rejected': return 'rgba(248, 113, 113, 0.3)';
          default: return 'rgba(229, 231, 235, 0.3)';
        }
      }};

    &::before {
      opacity: 1;
    }
  }

  &:active {
    transform: translateY(-6px) scale(1.02);
  }
`;

export const StatIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  margin-bottom: 24px;
  font-size: 28px;
  background: ${props => {
    switch (props.$variant) {
      case 'total': return 'linear-gradient(135deg, #667eea, #764ba2)';
      case 'document_passed': return 'linear-gradient(135deg, #4ade80, #22c55e)';
      case 'final_passed': return 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
      case 'waiting': return 'linear-gradient(135deg, #fbbf24, #f59e0b)';
      case 'rejected': return 'linear-gradient(135deg, #f87171, #ef4444)';
      default: return 'linear-gradient(135deg, #e5e7eb, #d1d5db)';
    }
  }};
  color: white;
  box-shadow:
    0 8px 24px ${props => {
      switch (props.$variant) {
        case 'total': return 'rgba(102, 126, 234, 0.4)';
        case 'document_passed': return 'rgba(74, 222, 128, 0.4)';
        case 'final_passed': return 'rgba(139, 92, 246, 0.4)';
        case 'waiting': return 'rgba(251, 191, 36, 0.4)';
        case 'rejected': return 'rgba(248, 113, 113, 0.4)';
        default: return 'rgba(229, 231, 235, 0.4)';
      }
    }},
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);

  ${StatCard}:hover & {
    transform: scale(1.15) rotate(5deg);
    box-shadow:
      0 12px 32px ${props => {
        switch (props.$variant) {
          case 'total': return 'rgba(102, 126, 234, 0.6)';
          case 'document_passed': return 'rgba(74, 222, 128, 0.6)';
          case 'final_passed': return 'rgba(139, 92, 246, 0.6)';
          case 'waiting': return 'rgba(251, 191, 36, 0.6)';
          case 'rejected': return 'rgba(248, 113, 113, 0.6)';
          default: return 'rgba(229, 231, 235, 0.6)';
        }
      }},
      inset 0 1px 0 rgba(255, 255, 255, 0.5);
  }
`;

export const StatContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const StatValue = styled.div`
  font-size: 42px;
  font-weight: 900;
  line-height: 1;
  color: #1a202c;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);

  ${StatCard}:hover & {
    transform: scale(1.1);
    color: ${props => {
      switch (props.$variant) {
        case 'total': return '#667eea';
        case 'document_passed': return '#4ade80';
        case 'final_passed': return '#8b5cf6';
        case 'waiting': return '#fbbf24';
        case 'rejected': return '#f87171';
        default: return '#1a202c';
      }
    }};
  }
`;

export const StatLabel = styled.div`
  font-size: 16px;
  font-weight: 700;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: all 0.3s ease;

  ${StatCard}:hover & {
    color: #2d3748;
    transform: translateX(4px);
  }
`;

export const StatPercentage = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #718096;
  margin-top: 8px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  border-radius: 16px;
  display: inline-block;
  width: fit-content;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;

  ${StatCard}:hover & {
    background: linear-gradient(135deg, #edf2f7, #e2e8f0);
    color: #4a5568;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

export const MailButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  opacity: 0;
  transform: translateY(-20px) scale(0.8);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);

  ${StatCard}:hover & {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  &:hover {
    background: linear-gradient(135deg, #5a67d8, #6b46c1);
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    transform: translateY(0) scale(1);
  }

  &:disabled:hover {
    transform: translateY(0) scale(1);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  }
`;
