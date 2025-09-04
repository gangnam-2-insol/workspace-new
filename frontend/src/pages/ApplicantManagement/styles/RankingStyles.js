import styled from 'styled-components';

export const RankingResultsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
`;

export const RankingHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--primary-color);
`;

export const RankingTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
`;

export const RankingClearButton = styled.button`
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;

  &:hover {
    background: #e5e7eb;
    color: #374151;
    transform: translateY(-1px);
  }
`;

export const RankingTable = styled.div`
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  max-height: 400px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--background-secondary);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;

    &:hover {
      background: var(--text-secondary);
    }
  }
`;

export const RankingTableHeader = styled.div`
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 1fr 100px;
  gap: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
`;

export const RankingTableHeaderCell = styled.div`
  text-align: center;

  &:nth-child(1) { text-align: center; }
  &:nth-child(2) { text-align: left; }
  &:nth-child(3) { text-align: center; }
  &:nth-child(4) { text-align: center; }
  &:nth-child(5) { text-align: left; }
  &:nth-child(6) { text-align: center; }
`;

export const RankingTableBody = styled.div``;

export const RankingTableRow = styled.div`
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 1fr 100px;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    background: var(--background-secondary);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  &:last-child {
    border-bottom: none;
  }
`;

export const RankingTableCell = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  &:nth-child(2) { justify-content: flex-start; }
  &:nth-child(3) { justify-content: center; }
  &:nth-child(4) { justify-content: center; }
  &:nth-child(5) { justify-content: flex-start; }
  &:nth-child(6) { justify-content: center; }
`;

export const TotalScore = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color);
  background: linear-gradient(135deg, rgba(0, 200, 81, 0.1), rgba(0, 200, 81, 0.05));
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(0, 200, 81, 0.2);
`;

export const ScoreBreakdown = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
`;

export const ScoreItem = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 8px;

  span:first-child {
    color: var(--text-secondary);
    min-width: 60px;
  }

  span:last-child {
    font-weight: 600;
  }
`;

export const RankBadge = styled.span`
  padding: ${props => props.small ? '2px 6px' : '6px 12px'};
  border-radius: ${props => props.small ? '4px' : '8px'};
  font-size: ${props => props.small ? '10px' : '16px'};
  font-weight: 600;
  background: ${props => {
    if (props.rank === 1) return '#ef4444';
    if (props.rank === 2) return '#f59e0b';
    if (props.rank === 3) return '#10b981';
    if (props.rank <= 10) return '#3b82f6';
    return '#6b7280';
  }};
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
`;
