import styled from 'styled-components';

export const Header = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
`;

export const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const HeaderLeft = styled.div``;

export const HeaderRight = styled.div``;

export const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const Subtitle = styled.p`
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
`;

export const NewResumeButton = styled.button`
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;
