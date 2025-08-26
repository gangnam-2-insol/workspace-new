import styled from 'styled-components';
import { motion } from 'framer-motion';

// 지원자 카드 스타일 - variant prop으로 통합
export const ApplicantCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    border-color: var(--primary-color);
  }
`;

export const ApplicantHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

export const ApplicantInfo = styled.div`
  flex: 1;
`;

export const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: ${props => props.variant === 'ai'
    ? 'linear-gradient(135deg, #667eea, #764ba2)'
    : 'linear-gradient(135deg, var(--primary-color), #00a844)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
  margin-right: 16px;
`;

export const ApplicantDetails = styled.div`
  display: flex;
  align-items: center;
`;

export const ApplicantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

export const ApplicantPosition = styled.div`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  margin-bottom: 4px;
`;

export const ApplicantDate = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantEmail = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
`;

export const ApplicantPhone = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
`;

export const ContactItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const ApplicantSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
`;

export const SkillTag = styled.span`
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
`;

export const ApplicantActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

// 상태 관련 스타일
export const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    switch (props.status) {
      case 'passed':
        return '#22c55e';
      case 'waiting':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  }};
  color: white;
`;

export const StatusSelect = styled.select`
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  background: white;
  cursor: pointer;
`;

export const StatusColumnWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 액션 버튼 스타일
export const ActionButton = styled.button`
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-1px);
  }
`;

export const PassButton = styled(ActionButton)`
  &:hover {
    border-color: #22c55e;
    color: #22c55e;
  }
`;

export const PendingButton = styled(ActionButton)`
  &:hover {
    border-color: #f59e0b;
    color: #f59e0b;
  }
`;

export const RejectButton = styled(ActionButton)`
  &:hover {
    border-color: #ef4444;
    color: #ef4444;
  }
`;

export const ResumeViewButton = styled(ActionButton)`
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;
