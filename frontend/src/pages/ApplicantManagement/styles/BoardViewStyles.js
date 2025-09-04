import styled from 'styled-components';
import { motion } from 'framer-motion';

// 보드 뷰 스타일
export const BoardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 0;
`;

export const BoardApplicantCard = styled(motion.div).attrs({
  id: 'applicant-management-applicant-card-board'
})`
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  height: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;

export const BoardCardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
`;

export const CardCheckbox = styled.div`
  position: relative;
  z-index: 2;
`;

export const CardAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

export const BoardCardContent = styled.div`
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  min-width: 0;
`;

export const CardName = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const CardPosition = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const CardDepartment = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const CardContact = styled.div`
  min-width: 180px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const CardSkills = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const CardScore = styled.div`
  min-width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const CardDate = styled.div`
  min-width: 90px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-secondary);
`;

export const BoardCardActions = styled.div`
  min-width: 100px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

export const CardActionButton = styled.button`
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
  color: var(--text-secondary);
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

// 보드 뷰 AI 분석 스타일
export const AiAnalysisSectionBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
`;

export const AiAnalysisTitleBoard = styled.h4`
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
`;

export const SuitabilityGraphBoard = styled.div`
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const CircularProgressBoard = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    ${props => {
      if (props.percentage >= 90) return '#10b981';
      if (props.percentage >= 80) return '#f59e0b';
      return '#ef4444';
    }} 0deg ${props => props.percentage * 3.6}deg,
    #e5e7eb ${props => props.percentage * 3.6}deg 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;

  &::before {
    content: '';
    position: absolute;
    width: 80%;
    height: 80%;
    background: white;
    border-radius: 50%;
  }
`;

export const PercentageTextBoard = styled.div`
  position: absolute;
  font-size: 8px;
  font-weight: 700;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

export const SuitabilityValueBoard = styled.div`
  font-size: 10px;
  font-weight: 600;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

// 추가적인 보드 뷰 스타일들
export const AiSuitabilityAvatarBoard = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => {
    if (props.percentage >= 90) return 'linear-gradient(135deg, #22c55e, #16a34a)';
    if (props.percentage >= 80) return 'linear-gradient(135deg, #eab308, #ca8a04)';
    return 'linear-gradient(135deg, #ef4444, #dc2626)';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 10px;
  text-align: center;
  line-height: 1;
`;

export const ApplicantDetailsBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  min-width: 0;
  overflow: hidden;
`;

export const ApplicantNameBoard = styled.h3`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 120px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const ApplicantPositionBoard = styled.p`
  color: var(--text-secondary);
  font-size: 12px;
  min-width: 120px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const ApplicantDateBoard = styled.p`
  color: var(--text-light);
  font-size: 11px;
  min-width: 90px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
`;

export const ApplicantEmailBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 180px;
  flex-shrink: 0;
`;

export const ApplicantPhoneBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  flex-shrink: 0;
`;

export const ApplicantSkillsBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  flex-shrink: 0;
`;

export const BoardRankBadge = styled.div`
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${props => {
    if (props.rank === 1) return 'linear-gradient(135deg, #ffd700, #ffed4e)';
    if (props.rank === 2) return 'linear-gradient(135deg, #c0c0c0, #e5e5e5)';
    if (props.rank === 3) return 'linear-gradient(135deg, #cd7f32, #daa520)';
    return 'linear-gradient(135deg, #6b7280, #9ca3af)';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

export const BoardAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

export const FixedPassButton = styled.button`
  padding: 4px 8px;
  border: 1px solid #28a745;
  border-radius: 4px;
  background: ${props => props.active ? '#28a745' : 'white'};
  color: ${props => props.active ? 'white' : '#28a745'};
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#218838' : '#28a745'};
    color: white;
  }
`;

export const FixedPendingButton = styled.button`
  padding: 4px 8px;
  border: 1px solid #ffc107;
  border-radius: 4px;
  background: ${props => props.active ? '#ffc107' : 'white'};
  color: ${props => props.active ? '#212529' : '#ffc107'};
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#e0a800' : '#ffc107'};
    color: ${props => props.active ? '#212529' : '#212529'};
  }
`;

export const FixedRejectButton = styled.button`
  padding: 4px 8px;
  border: 1px solid #dc3545;
  border-radius: 4px;
  background: ${props => props.active ? '#dc3545' : 'white'};
  color: ${props => props.active ? 'white' : '#dc3545'};
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#c82333' : '#dc3545'};
    color: white;
  }
`;


