import styled from 'styled-components';

// 지원자 정보 스타일
export const ApplicantInfoContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const InfoField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const InfoLabel = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
`;

export const InfoInput = styled.input`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  background: white;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }

  &::placeholder {
    color: var(--text-secondary);
  }
`;

// 폼 액션 스타일
export const ResumeFormActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
`;

export const ResumeSubmitButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }

  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
    transform: none;
  }
`;

export const DeleteButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #dc2626;
    transform: translateY(-1px);
  }
`;

// 깃허브 입력 스타일
export const GithubInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const GithubInput = styled.input`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  background: white;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }

  &::placeholder {
    color: var(--text-secondary);
  }
`;

export const GithubInputDescription = styled.p`
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
`;

// 지원자 행 스타일
export const ApplicantRow = styled.div`
  display: grid;
  grid-template-columns: 40px 2fr 1fr 1fr 1fr 1fr 120px 100px;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: var(--background-secondary);
  }

  &:last-child {
    border-bottom: none;
  }
`;

export const NameText = styled.div`
  font-weight: 600;
  color: var(--text-primary);
`;

export const EmailText = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
`;

export const PositionBadge = styled.div`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
`;

export const DepartmentText = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
`;

export const ContactInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

export const SkillsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 250px;
  align-items: center;
`;

export const MoreSkills = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  &:hover {
    color: var(--primary-color);
  }
`;

export const NoSkills = styled.span`
  font-size: 12px;
  color: var(--text-light);
  font-style: italic;
`;

export const AvgScore = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }

  /* 기본 스타일 */
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;

  /* 고유 ID 기반 스타일링 */
  &[id*="ranking-badge-"] {
    /* 메달 아이콘 */
    &::before {
      content: "🏆";
      font-size: 14px;
    }
  }

  /* 특정 지원자 ID에 따른 개별 스타일링 */
  &[id="ranking-badge-1"] {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #333;
    &::before {
      content: "🥇";
    }
  }

  &[id="ranking-badge-2"] {
    background: linear-gradient(135deg, #c0c0c0, #e5e5e5);
    color: #333;
    &::before {
      content: "🥈";
    }
  }

  &[id="ranking-badge-3"] {
    background: linear-gradient(135deg, #cd7f32, #daa520);
    color: white;
    &::before {
      content: "🥉";
    }
  }

  /* 점수별 스타일링을 위한 클래스 기반 접근 */
  &.high-score {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    &::before {
      content: "⭐" !important;
    }
  }

  &.medium-score {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: white !important;
    &::before {
      content: "📊" !important;
    }
  }

  &.low-score {
    background: linear-gradient(135deg, #6b7280, #4b5563) !important;
    color: white !important;
    &::before {
      content: "📝" !important;
    }
  }

  &.no-score {
    background: linear-gradient(135deg, #9ca3af, #6b7280) !important;
    color: white !important;
    &::before {
      content: "❓" !important;
    }
  }
`;

export const ActionButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  justify-content: center;
`;

export const StatusActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-1px);
  }

  &.pending {
    &:hover {
      background: #fef3c7;
      border-color: #f59e0b;
      color: #d97706;
    }
  }

  &.rejected {
    &:hover {
      background: #fee2e2;
      border-color: #ef4444;
      color: #dc2626;
    }
  }

  &.passed {
    &:hover {
      background: #dcfce7;
      border-color: #10b981;
      color: #059669;
    }
  }
`;

export const CornerBadge = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${props => {
    if (props.rank === 1) return '#ef4444';
    if (props.rank === 2) return '#f59e0b';
    if (props.rank === 3) return '#10b981';
    if (props.rank <= 10) return '#3b82f6';
    return '#6b7280';
  }};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
`;

// 카드 관련 스타일
export const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

export const CardContent = styled.div`
  flex: 1;
`;

export const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

export const CardActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;
