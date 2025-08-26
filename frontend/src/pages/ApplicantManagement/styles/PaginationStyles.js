import styled from 'styled-components';

// 페이지네이션 스타일
export const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 32px;
  margin-bottom: 0;
  gap: 16px;
  clear: both;
`;

export const PaginationButton = styled.button`
  background-color: transparent;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background-color: #f7fafc;
    border-color: #cbd5e0;
    color: #2d3748;
  }

  &:disabled {
    background-color: transparent;
    border-color: #e2e8f0;
    color: #cbd5e0;
    cursor: not-allowed;
  }
`;

export const PageNumbers = styled.div`
  display: flex;
  gap: 8px;
`;

export const PageNumber = styled.button`
  background-color: ${props => props.isActive ? '#4299e1' : 'transparent'};
  color: ${props => props.isActive ? 'white' : '#4a5568'};
  border: 1px solid ${props => props.isActive ? '#4299e1' : '#e2e8f0'};
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: ${props => props.isActive ? '600' : '500'};
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 40px;
  text-decoration: none;

  &:hover {
    background-color: ${props => props.isActive ? '#3182ce' : '#f7fafc'};
    border-color: ${props => props.isActive ? '#3182ce' : '#cbd5e0'};
    color: ${props => props.isActive ? 'white' : '#2d3748'};
  }

  &:disabled {
    background-color: transparent;
    border-color: #e2e8f0;
    color: #cbd5e0;
    cursor: default;
  }
`;
