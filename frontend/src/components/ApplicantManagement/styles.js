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
  font-weight: 500;
`;

// 검색 및 필터 스타일
export const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

export const SearchSection = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
`;

export const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;

  &::placeholder {
    color: var(--text-light);
    font-weight: 400;
  }

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    outline: none;
  }
`;

export const FilterButton = styled.button`
  padding: 12px 16px;
  background: ${({ active }) => active ? 'var(--primary-color)' : 'white'};
  color: ${({ active }) => active ? 'white' : 'var(--text-primary)'};
  border: 1px solid ${({ active }) => active ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: ${({ active }) => active ? 'white' : 'var(--primary-color)'};
    background: ${({ active }) => active ? 'var(--primary-dark)' : 'white'};
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
`;

export const ViewModeButton = styled.button`
  padding: 8px 12px;
  background: ${({ active }) => active ? 'var(--primary-color)' : 'white'};
  color: ${({ active }) => active ? 'white' : 'var(--text-secondary)'};
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
    color: ${({ active }) => active ? 'white' : 'var(--primary-color)'};
  }
`;

// 지원자 카드 스타일
export const ApplicantsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
`;

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

export const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

export const ApplicantInfo = styled.div`
  flex: 1;
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
`;

export const StatusBadge = styled.span`
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: ${({ status }) => {
    switch (status) {
      case '서류합격':
      case '최종합격':
        return '#10b981';
      case '보류':
        return '#f59e0b';
      case '서류불합격':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  }};
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
`;

export const CardContent = styled.div`
  margin-bottom: 16px;
`;

export const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-secondary);
`;

export const CardActions = styled.div`
  display: flex;
  gap: 8px;
  justify-content: center;
`;

export const ActionButton = styled.button`
  padding: 8px 12px;
  background: ${({ active, color }) => active ? (color || '#6b7280') : 'white'};
  color: ${({ active, color }) => active ? 'white' : (color || '#6b7280')};
  border: 1px solid ${({ color }) => color || '#6b7280'};
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ color }) => color || '#6b7280'};
    color: white;
    transform: translateY(-1px);
  }
`;

// 보드 뷰 스타일
export const ApplicantsBoard = styled.div`
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
`;

export const BoardHeader = styled.div`
  display: grid;
  grid-template-columns: 40px 1fr 120px 150px 120px 1fr 100px 100px;
  gap: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
`;

export const BoardRow = styled.div`
  display: grid;
  grid-template-columns: 40px 1fr 120px 150px 120px 1fr 100px 100px;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--background-secondary);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  &:last-child {
    border-bottom: none;
  }
`;

// 페이지네이션 스타일
export const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 40px 0;
  gap: 16px;
`;

export const PaginationButton = styled.button`
  background: transparent;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: #f7fafc;
    border-color: #cbd5e0;
    color: #2d3748;
  }

  &:disabled {
    background: transparent;
    border-color: #e2e8e0;
    color: #cbd5e0;
    cursor: not-allowed;
  }
`;

export const PaginationNumbers = styled.div`
  display: flex;
  gap: 8px;
`;

export const PaginationNumber = styled.button`
  background: ${props => props.active ? '#4299e1' : 'transparent'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  border: 1px solid ${props => props.active ? '#4299e1' : '#e2e8f0'};
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: ${props => props.active ? '600' : '500'};
  cursor: pointer;
  transition: all 0.2s;
  min-width: 40px;

  &:hover {
    background: ${props => props.active ? '#3182ce' : '#f7fafc'};
    border-color: ${props => props.active ? '#3182ce' : '#cbd5e0'};
    color: ${props => props.active ? 'white' : '#2d3748'};
  }
`;

// 모달 스타일
export const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
`;

export const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
`;

export const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
`;

export const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
`;

export const ModalCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

// 로딩 스타일
export const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 12px;
`;

export const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 500;

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
