import styled from 'styled-components';
import { motion } from 'framer-motion';

// 분석 결과 스타일 컴포넌트들
export const ResumeAnalysisSection = styled.div`
  margin-top: 24px;
  padding: 20px;
  background: var(--background-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

export const ResumeAnalysisTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
`;

export const ResumeAnalysisSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  
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
  
  span {
    color: var(--text-secondary);
    font-size: 14px;
  }
`;

export const ResumeAnalysisContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

export const ResumeAnalysisItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

export const ResumeAnalysisLabel = styled.span`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 80px;
`;

export const ResumeAnalysisValue = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
  flex: 1;
`;

export const ResumeAnalysisScore = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
`;

// 새로운 분석 섹션 스타일 컴포넌트들
export const ResumeAnalysisSubSection = styled.div`
  margin: 20px 0;
  padding: 16px;
  background: var(--background-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
`;

export const ResumeAnalysisSubTitle = styled.h4`
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
`;

export const ResumeAnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
`;

export const ResumeAnalysisGridItem = styled.div`
  padding: 12px;
  background: var(--background-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
`;

export const ResumeAnalysisGridLabel = styled.div`
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

export const ResumeAnalysisGridScore = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
  margin-bottom: 8px;
`;

export const ResumeAnalysisGridFeedback = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
`;
