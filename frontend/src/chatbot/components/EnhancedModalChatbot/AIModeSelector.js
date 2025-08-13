import React from 'react';

const AIModeSelector = ({ onModeSelect, selectedMode, onTestModeClick }) => {
  const modes = [
    {
      id: 'individual_input',
      name: '개별입력모드',
      description: '각 필드를 하나씩 순서대로 입력',
      icon: '📝',
      color: '#667eea'
    },
    // {
    //   id: 'autonomous',
    //   name: '자율모드', 
    //   description: 'AI가 자동으로 모든 정보를 수집',
    //   icon: '🤖',
    //   color: '#764ba2'
    // },
    {
      id: 'langgraph',
      name: 'LangGraph모드',
      description: 'AI와 대화하며 채용공고 작성',
      icon: '💬',
      color: '#f093fb'
    }
  ];

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f8fafc',
      borderRadius: '12px',
      marginBottom: '20px'
    }}>
      <h3 style={{
        marginBottom: '16px',
        color: '#1f2937',
        fontSize: '18px',
        fontWeight: '600'
      }}>
        🤖 AI 어시스턴트 모드를 선택해주세요
      </h3>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '12px',
        maxWidth: '600px'
      }}>
        {modes.map((mode) => (
          <div
            key={mode.id}
            onClick={() => onModeSelect(mode.id)}
            style={{
              padding: '12px',
              backgroundColor: selectedMode === mode.id ? mode.color : 'white',
              color: selectedMode === mode.id ? 'white' : '#374151',
              borderRadius: '8px',
              border: `2px solid ${selectedMode === mode.id ? mode.color : '#e5e7eb'}`,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: selectedMode === mode.id 
                ? `0 4px 12px ${mode.color}40` 
                : '0 1px 4px rgba(0, 0, 0, 0.1)',
              transform: selectedMode === mode.id ? 'translateY(-1px)' : 'translateY(0)',
              position: 'relative',
              overflow: 'hidden',
              minHeight: '80px'
            }}
            onMouseEnter={(e) => {
              if (selectedMode !== mode.id) {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedMode !== mode.id) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.1)';
              }
            }}
          >
            {/* 선택 표시 */}
            {selectedMode === mode.id && (
              <div style={{
                position: 'absolute',
                top: '8px',
                right: '8px',
                width: '16px',
                height: '16px',
                backgroundColor: 'white',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                color: mode.color,
                fontWeight: 'bold'
              }}>
                ✓
              </div>
            )}
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '6px'
            }}>
              <span style={{
                fontSize: '16px',
                marginRight: '8px'
              }}>
                {mode.icon}
              </span>
              <h4 style={{
                margin: 0,
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {mode.name}
              </h4>
            </div>
            
            <p style={{
              margin: 0,
              fontSize: '11px',
              lineHeight: '1.3',
              opacity: selectedMode === mode.id ? 0.9 : 0.7
            }}>
              {mode.description}
            </p>
            
            {/* 모드별 추가 설명 */}
            {/* {mode.id === 'individual_input' && (
              <div style={{
                marginTop: '6px',
                padding: '4px 6px',
                backgroundColor: selectedMode === mode.id ? 'rgba(255,255,255,0.2)' : '#f3f4f6',
                borderRadius: '4px',
                fontSize: '9px',
                opacity: 0.8
              }}>
                예: "부서명을 입력해주세요" → "개발팀" → "다음 필드로..."
              </div>
            )} */}
            
            {mode.id === 'autonomous' && (
              <div style={{
                marginTop: '6px',
                padding: '4px 6px',
                backgroundColor: selectedMode === mode.id ? 'rgba(255,255,255,0.2)' : '#f3f4f6',
                borderRadius: '4px',
                fontSize: '9px',
                opacity: 0.8
              }}>
                예: "인천에서 개발팀 2명 뽑아요" → 모든 정보 자동 추출
              </div>
            )}
            
            {/* AI 어시스턴트 모드 주석 처리
            {mode.id === 'ai_assistant' && (
              <div style={{
                marginTop: '6px',
                padding: '4px 6px',
                backgroundColor: selectedMode === mode.id ? 'rgba(255,255,255,0.2)' : '#f3f4f6',
                borderRadius: '4px',
                fontSize: '9px',
                opacity: 0.8
              }}>
                예: "채용공고 작성 도와줘" → AI와 자유롭게 대화
              </div>
            )}
            */}
          </div>
        ))}
      </div>
      
      {selectedMode && (
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          backgroundColor: '#dbeafe',
          border: '1px solid #3b82f6',
          borderRadius: '8px',
          fontSize: '14px',
          color: '#1e40af'
        }}>
          ✅ <strong>{modes.find(m => m.id === selectedMode)?.name}</strong>이 선택되었습니다.
          이제 채용공고 작성을 시작할 수 있습니다!
        </div>
      )}
      
      {/* 테스트중 버튼 추가 */}
      {/* <div style={{
        marginTop: '16px',
        display: 'flex',
        justifyContent: 'center'
      }}>
        <div
          onClick={onTestModeClick}
          style={{
            padding: '8px 16px',
            backgroundColor: '#fef3c7',        // 연한 노란색 배경
            color: '#92400e',                  // 진한 주황색 텍스트
            borderRadius: '20px',              // 둥근 모서리
            border: '2px solid #f59e0b',       // 주황색 테두리
            cursor: 'pointer',
            transition: 'all 0.3s ease',       // 부드러운 애니메이션
            boxShadow: '0 1px 4px rgba(0, 0, 0, 0.1)',
            fontSize: '12px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-1px)';
            e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.1)';
          }}
        >
          <span style={{ fontSize: '14px' }}>🧪</span>
          테스트중123
        </div>
      </div> */}
    </div>
  );
};

export default AIModeSelector;

