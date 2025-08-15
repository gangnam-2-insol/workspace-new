import styled from 'styled-components';
import { motion } from 'framer-motion';

// 기본 레이아웃 스타일
export const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

export const Header = styled.div`
  margin-bottom: 32px;
`;

export const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

export const HeaderLeft = styled.div`
  flex: 1;
`;

export const HeaderRight = styled.div`
  display: flex;
  align-items: center;
`;

export const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 16px;
`;

// 버튼 스타일
export const NewResumeButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

// 로딩 인디케이터
export const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 500;
  margin-top: 8px;
`;

// 통계 카드 스타일
export const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

export const StatCard = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

export const StatValue = styled(motion.div)`
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
`;

export const StatLabel = styled.div`
  color: var(--text-secondary);
  font-size: 14px;
`;

// 검색바 스타일
export const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  justify-content: space-between;
`;

export const SearchSection = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
`;

export const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: var(--primary-color);
  }
`;

// 뷰 모드 스타일
export const ViewModeSection = styled.div`
  display: flex;
  gap: 8px;
`;

export const ViewModeButton = styled.button`
  padding: 8px 12px;
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.active ? 'white' : 'var(--primary-color)'};
  }
`;

// 헤더 행 스타일
export const HeaderRow = styled.div`
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
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

// 헤더 컬럼 스타일
export const HeaderAvatar = styled.div`
  width: 28px;
  flex-shrink: 0;
`;

export const HeaderName = styled.div`
  min-width: 90px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderPosition = styled.div`
  min-width: 110px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderDate = styled.div`
  min-width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

export const HeaderEmail = styled.div`
  min-width: 160px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderPhone = styled.div`
  min-width: 110px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
`;

export const HeaderSkills = styled.div`
  min-width: 140px;
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

export const HeaderRanks = styled.div`
  min-width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 12px;
`;

// 체크박스 스타일
export const HeaderCheckbox = styled.div`
  min-width: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const ApplicantCheckbox = styled.div`
  min-width: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const CheckboxInput = styled.input`
  width: 16px;
  height: 16px;
  accent-color: var(--primary-color);
  cursor: pointer;
`;

// 액션 바 스타일
export const FixedActionBar = styled.div`
  position: sticky;
  top: 0;
  background: var(--background-secondary);
  padding: 12px 24px;
  margin: 0 -24px 16px -24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
`;

export const ActionButtonsGroup = styled.div`
  display: flex;
  gap: 8px;
`;

export const FixedActionButton = styled.button`
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

export const FixedPassButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#28a745' : 'white'};
  color: ${props => props.active ? 'white' : '#28a745'};
  border-color: #28a745;
  
  &:hover {
    background: ${props => props.active ? '#218838' : '#28a745'};
    border-color: ${props => props.active ? '#1e7e34' : '#28a745'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

export const FixedPendingButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#ffc107' : 'white'};
  color: ${props => props.active ? '#212529' : '#ffc107'};
  border-color: #ffc107;
  
  &:hover {
    background: ${props => props.active ? '#e0a800' : '#ffc107'};
    border-color: ${props => props.active ? '#d39e00' : '#ffc107'};
    color: ${props => props.active ? '#212529' : '#212529'};
  }
`;

export const FixedRejectButton = styled(FixedActionButton)`
  background: ${props => props.active ? '#dc3545' : 'white'};
  color: ${props => props.active ? 'white' : '#dc3545'};
  border-color: #dc3545;
  
  &:hover {
    background: ${props => props.active ? '#c82333' : '#dc3545'};
    border-color: ${props => props.active ? '#bd2130' : '#dc3545'};
    color: ${props => props.active ? 'white' : 'white'};
  }
`;

export const SelectionInfo = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 로딩 관련 스타일
export const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const LoadingSpinner = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  
  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 추가 버튼 스타일
export const LoadMoreButton = styled.button`
  width: 100%;
  padding: 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 24px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
`;

export const EndMessage = styled.div`
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 24px;
`;
