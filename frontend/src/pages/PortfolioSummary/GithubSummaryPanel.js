import React from 'react';
import TestGithubSummary from './TestGithubSummary';

const GithubSummaryPanel = () => {
  return (
    <div style={{ border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
      <TestGithubSummary />
    </div>
  );
};

export default GithubSummaryPanel;


