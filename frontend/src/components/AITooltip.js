import React, { useState, useEffect } from 'react';

const AITooltip = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // 페이지 로드 후 1초 뒤에 말풍선 표시
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // 화면 클릭 시 말풍선 숨기기
    const handleClick = () => {
      setIsVisible(false);
    };

    // 클릭 이벤트 리스너 추가
    document.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, []);

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '110px',
        right: '54px',
        zIndex: 1000,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
        transition: 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        pointerEvents: isVisible ? 'auto' : 'none'
      }}
    >
      {/* 말풍선 화살표 */}
      <div
        style={{
          position: 'absolute',
          bottom: '-18px',
          right: '20px',
          width: 0,
          height: '11px',
          borderLeft: '15px solid transparent',
          borderRight: '3px solid transparent',
          borderTop: '20px solid #333',
          zIndex: 10,
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.2s'
        }}
      />
      
      {/* 말풍선 내용 */}
      <div
        style={{
          backgroundColor: 'white',
          color: '#333',
          padding: '12px 16px',
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          maxWidth: '230px',
          textAlign: 'center',
          lineHeight: '1.4',
          border: '2px solid #333',
          position: 'relative',
          overflow: 'hidden',
          transform: isVisible ? 'scale(1)' : 'scale(0.9)',
          transition: 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }}
      >
        {/* 배경 장식 */}
        <div
          style={{
            position: 'absolute',
            top: '-10px',
            right: '-10px',
            width: '40px',
            height: '40px',
            background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            animation: isVisible ? 'pulse 2s infinite' : 'none',
            zIndex: 2
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: '-15px',
            left: '-15px',
            width: '30px',
            height: '30px',
            background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
            borderRadius: '50%',
            animation: isVisible ? 'pulse 2.5s infinite' : 'none',
            zIndex: 2
          }}
        />
        
        {/* 텍스트 */}
        <div style={{ position: 'relative', zIndex: 3 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '16px' }}>🤖</span>
            <span style={{ fontSize: '12px', fontWeight: '600' }}>AI 어시스턴트</span>
          </div>
          <div style={{ fontSize: '13px', fontWeight: '400' }}>
            AI와 대화하며 작업을 진행하세요
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.1);
          }
        }
      `}</style>
    </div>
  );
};

export default AITooltip; 