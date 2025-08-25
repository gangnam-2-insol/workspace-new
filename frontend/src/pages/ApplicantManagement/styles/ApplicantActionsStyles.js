import styled from 'styled-components';

// AI 분석 관련 스타일
export const AiAnalysisSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: 8px;
`;

export const AiAnalysisTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
`;

export const AiAnalysisContent = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

export const SuitabilityGraph = styled.div`
  position: relative;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const CircularProgress = styled.div`
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

export const PercentageText = styled.div`
  position: absolute;
  font-size: 10px;
  font-weight: 700;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

export const SuitabilityInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

export const SuitabilityLabel = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

export const SuitabilityValue = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: ${props => {
    if (props.percentage >= 90) return '#10b981';
    if (props.percentage >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

// 점수 및 순위 스타일
export const ApplicantScoreBoard = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
`;

export const ScoreBadge = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: white;
  background: ${props => {
    if (props.score >= 90) return '#10b981';
    if (props.score >= 80) return '#f59e0b';
    if (props.score >= 70) return '#3b82f6';
    return '#6b7280';
  }};
`;

export const RankBadge = styled.span`
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

export const TopRankBadge = styled(RankBadge)`
  width: 24px;
  height: 24px;
  font-size: 14px;
`;

// 분석 점수 표시 스타일
export const AnalysisScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
`;

export const AnalysisScoreCircle = styled.div`
  position: relative;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: conic-gradient(
    ${props => {
      if (props.score >= 90) return '#10b981';
      if (props.score >= 80) return '#f59e0b';
      return '#ef4444';
    }} 0deg ${props => props.score * 3.6}deg,
    #e5e7eb ${props => props.score * 3.6}deg 360deg
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

export const AnalysisScoreInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

export const AnalysisScoreLabel = styled.div`
  font-size: 10px;
  color: var(--text-secondary);
`;

export const AnalysisScoreValue = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: ${props => {
    if (props.score >= 90) return '#10b981';
    if (props.score >= 80) return '#f59e0b';
    return '#ef4444';
  }};
`;

// 스킬 관련 스타일
export const SkillsSection = styled.div`
  margin-top: 16px;
`;

export const SkillsTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const SkillsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

export const SkillTag = styled.span`
  background: var(--primary-color);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
`;

// 그리드 및 보드 스타일
export const ApplicantsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
`;

export const ApplicantsBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
`;
