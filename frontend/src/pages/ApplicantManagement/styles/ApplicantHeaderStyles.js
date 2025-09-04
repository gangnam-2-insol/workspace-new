import styled from 'styled-components';

// 지원자 헤더 스타일
export const HeaderRow = styled.div`
  display: grid;
  grid-template-columns: 40px 2fr 1fr 1fr 1fr 1fr 120px 100px;
  gap: 16px;
  padding: 16px 20px;
  background: var(--background-secondary);
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  align-items: center;
  border-bottom: 2px solid var(--border-color);
`;

export const HeaderRowBoard = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  height: 36px;
  gap: 16px;
`;

export const ApplicantCheckbox = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const CheckboxInput = styled.input`
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-color);
`;

export const FixedActionBar = styled.div`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid var(--border-color);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
`;

export const ActionButtonsGroup = styled.div`
  display: flex;
  gap: 12px;
`;

export const FixedActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &.pass {
    background: #22c55e;
    color: white;
    &:hover {
      background: #16a34a;
    }
  }

  &.pending {
    background: #f59e0b;
    color: white;
    &:hover {
      background: #d97706;
    }
  }

  &.reject {
    background: #ef4444;
    color: white;
    &:hover {
      background: #dc2626;
    }
  }
`;

export const SelectionInfo = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
`;

export const NoResultsMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 16px;
`;

// 그리드 헤더 스타일
export const HeaderAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

export const HeaderName = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderPosition = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderDate = styled.div`
  min-width: 90px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

export const HeaderEmail = styled.div`
  min-width: 180px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderPhone = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderSkills = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderActions = styled.div`
  min-width: 100px;
  flex-shrink: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderScore = styled.div`
  min-width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

export const HeaderCheckbox = styled.div`
  min-width: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;
