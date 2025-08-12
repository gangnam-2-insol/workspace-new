import React from 'react';

const ChatbotRestartButton = ({ onRestart, currentStep, totalSteps, disabled = false }) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 16px',
      backgroundColor: '#f8fafc',
      borderRadius: '8px',
      margin: '8px 0',
      border: '1px solid #e2e8f0'
    }}>
      {/* 진행률 표시 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          fontSize: '12px',
          color: '#64748b',
          fontWeight: '500'
        }}>
          진행률: {currentStep}/{totalSteps}
        </div>
        <div style={{
          width: '60px',
          height: '4px',
          backgroundColor: '#e2e8f0',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${Math.min(100, (currentStep / totalSteps) * 100)}%`,
            height: '100%',
            backgroundColor: '#667eea',
            transition: 'width 0.3s ease'
          }} />
        </div>
      </div>

      {/* 재시작 버튼 */}
      <button
        onClick={onRestart}
        disabled={disabled}
        style={{
          padding: '6px 12px',
          fontSize: '11px',
          fontWeight: '500',
          backgroundColor: disabled ? '#f1f5f9' : '#fff',
          color: disabled ? '#94a3b8' : '#667eea',
          border: disabled ? '1px solid #e2e8f0' : '1px solid #667eea',
          borderRadius: '6px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.target.style.backgroundColor = '#667eea';
            e.target.style.color = 'white';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled) {
            e.target.style.backgroundColor = '#fff';
            e.target.style.color = '#667eea';
          }
        }}
      >
        🔄 처음부터
      </button>
    </div>
  );
};

export default ChatbotRestartButton;
