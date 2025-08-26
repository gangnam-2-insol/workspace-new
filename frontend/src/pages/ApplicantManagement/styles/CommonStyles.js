import styled from 'styled-components';
import { motion } from 'framer-motion';

// 기본 레이아웃 스타일
export const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

export const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 500;
  margin-top: 8px;
`;

export const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--primary-color);
  font-size: 16px;
  font-weight: 500;

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e2e8f0;
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const Wrapper = styled.div`
  min-height: 100vh;
  background: var(--background-primary);
`;

export const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
`;

// 기본 버튼 스타일
export const Button = styled.button`
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

  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
    transform: none;
  }
`;

// 기본 입력 필드 스타일
export const Input = styled.input`
  width: 100%;
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

// 기본 라벨 스타일
export const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: block;
`;
