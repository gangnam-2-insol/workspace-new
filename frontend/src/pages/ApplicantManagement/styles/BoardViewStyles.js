import styled from 'styled-components';
import { motion } from 'framer-motion';

// 보드 뷰 스타일
export const BoardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
`;

export const BoardApplicantCard = styled(motion.div)`
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

export const BoardCardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

export const CardCheckbox = styled.div`
  position: relative;
  z-index: 2;
`;

export const CardAvatar = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 20px;
  margin: 0 auto 16px;
`;

export const BoardCardContent = styled.div`
  text-align: center;
`;

export const CardName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

export const CardPosition = styled.div`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  margin-bottom: 4px;
`;

export const CardDepartment = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
`;

export const CardContact = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
  align-items: center;
`;

export const CardSkills = styled.div`
  margin-bottom: 12px;
`;

export const CardScore = styled.div`
  margin-bottom: 8px;
`;

export const CardDate = styled.div`
  font-size: 11px;
  color: var(--text-light);
  margin-bottom: 16px;
`;

export const BoardCardActions = styled.div`
  display: flex;
  justify-content: center;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
`;

export const CardActionButton = styled.button`
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-1px);
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

// 보드 뷰 순위 배지
export const BoardRankBadge = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: white;
  margin-right: 8px;
  background: ${props => {
    if (props.rank === 1) return '#ef4444'; // 빨간색 (1위)
    if (props.rank === 2) return '#f59e0b'; // 주황색 (2위)
    if (props.rank === 3) return '#10b981'; // 초록색 (3위)
    if (props.rank <= 10) return '#3b82f6'; // 파란색 (4-10위)
    return '#6b7280'; // 회색 (11위 이상)
  }};

  &::before {
    content: '${props => {
      if (props.rank === 1) return '🥇';
      if (props.rank === 2) return '🥈';
      if (props.rank === 3) return '🥉';
      return props.rank.toString();
    }}';
  }
`;

// 보드 뷰 아바타
export const BoardAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  margin-right: 12px;
`;

// 보드 뷰 고정 액션 버튼들
export const FixedPassButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #16a34a;
    transform: translateY(-1px);
  }
`;

export const FixedPendingButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #d97706;
    transform: translateY(-1px);
  }
`;

export const FixedRejectButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #dc2626;
    transform: translateY(-1px);
  }
`;
