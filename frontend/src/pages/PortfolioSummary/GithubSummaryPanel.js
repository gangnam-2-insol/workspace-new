import React, { useState, useEffect } from 'react';
import TestGithubSummary from '../TestGithubSummary';

const GithubSummaryPanel = ({ applicant }) => {
  const [githubUrl, setGithubUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 지원자의 GitHub URL 설정
  useEffect(() => {
    if (applicant && applicant.github_url) {
      const url = applicant.github_url;
      
      // GitHub URL이면 그대로 사용, 아니면 사용자명으로 처리
      if (url.includes('github.com/')) {
        setGithubUrl(url);
      } else {
        // URL이 아닌 경우 사용자명으로 처리
        setGithubUrl(url);
      }
    }
  }, [applicant]);

  // GitHub URL이 있으면 자동으로 요약 실행
  useEffect(() => {
    if (githubUrl && !isLoading) {
      setIsLoading(true);
      // TestGithubSummary 컴포넌트에 URL 전달
    }
  }, [githubUrl]);

  return (
    <div style={{ border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
      {githubUrl ? (
        <TestGithubSummary 
          initialUsername={githubUrl}
          autoSubmit={true}
          applicant={applicant}
        />
      ) : (
        <div style={{ 
          padding: '40px 20px', 
          textAlign: 'center',
          color: '#666'
        }}>
          <div style={{ fontSize: '16px', marginBottom: '12px' }}>
            GitHub 정보가 없습니다
          </div>
          <div style={{ fontSize: '14px' }}>
            지원자의 GitHub URL이 등록되어 있지 않습니다.
          </div>
        </div>
      )}
    </div>
  );
};

export default GithubSummaryPanel;


