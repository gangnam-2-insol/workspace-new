import React, { useState, useEffect } from 'react';

const TitleRecommendationModal = ({ 
  isOpen, 
  onClose, 
  formData, 
  onTitleSelect,
  onDirectInput 
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [selectedTitle, setSelectedTitle] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // API URL 설정
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // 모달이 열릴 때 AI 제목 추천 요청
  useEffect(() => {
    if (isOpen && formData) {
      generateTitleRecommendations();
    }
  }, [isOpen, formData]);

  const generateTitleRecommendations = async () => {
    if (!formData) return;

    setIsLoading(true);
    setError(null);

    try {
      // 폼 데이터를 텍스트로 변환
      const formContent = Object.entries(formData)
        .filter(([key, value]) => value && value.toString().trim())
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n');

      console.log('[TitleRecommendationModal] 제목 추천 요청:', formContent);

      const response = await fetch(`${API_BASE_URL}/api/pick-chatbot/generate-title`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_data: formData,
          content: formContent
        })
      });

      if (!response.ok) {
        throw new Error(`서버 응답 오류: ${response.status}`);
      }

      const data = await response.json();
      console.log('[TitleRecommendationModal] AI 제목 추천 응답:', data);

      if (data.titles && Array.isArray(data.titles)) {
        setRecommendations(data.titles);
      } else {
        // 기본 제목 생성 (4가지 컨셉)
        setRecommendations([
          { concept: "신입친화형", title: `함께 성장할 ${formData.position || '직무'} 신입을 찾습니다` },
          { concept: "전문가형", title: `전문성을 발휘할 ${formData.position || '직무'} 인재 모집` },
          { concept: "일반형", title: `${formData.department || '부서'} ${formData.position || '직무'} 채용` },
          { concept: "일반형 변형", title: `${formData.company || '회사'} ${formData.department || '부서'} 구인` }
        ]);
      }
    } catch (error) {
      console.error('[TitleRecommendationModal] 제목 추천 오류:', error);
      
      // 오류 메시지 개선
      let errorMessage = '제목 추천 중 오류가 발생했습니다.';
      if (error.message.includes('Failed to fetch')) {
        errorMessage = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.';
      } else if (error.message.includes('500')) {
        errorMessage = '서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      } else if (error.message.includes('404')) {
        errorMessage = '제목 추천 서비스를 찾을 수 없습니다.';
      }
      
      setError(errorMessage);
      
      // 오류 시 기본 제목들 제공 (4가지 컨셉)
      const defaultTitles = [
        { 
          concept: "신입친화형", 
          title: `함께 성장할 ${formData.position || formData.department || '직무'} 신입을 찾습니다`,
          description: "신입 지원자들이 매력적으로 느낄 수 있는 제목"
        },
        { 
          concept: "전문가형", 
          title: `전문성을 발휘할 ${formData.position || formData.department || '직무'} 인재 모집`,
          description: "경력자들이 전문성을 발휘할 수 있다고 느끼는 제목"
        },
        { 
          concept: "일반형", 
          title: `${formData.department || '부서'} ${formData.position || '직무'} 채용`,
          description: "일반적인 채용공고 제목"
        },
        { 
          concept: "창의형", 
          title: `혁신을 이끌 ${formData.position || formData.department || '인재'}를 찾습니다`,
          description: "독특하고 눈에 띄는 제목"
        }
      ];
      
      setRecommendations(defaultTitles);
      
      // 사용자에게 오류 상황 안내
      console.log('[TitleRecommendationModal] 기본 제목으로 대체됨');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTitleSelect = (titleObj) => {
    const title = typeof titleObj === 'object' ? titleObj.title : titleObj;
    setSelectedTitle(title);
    setCustomTitle(''); // 추천 제목 선택 시 직접 입력 초기화
  };

  const handleCustomTitleChange = (e) => {
    setCustomTitle(e.target.value);
    setSelectedTitle(''); // 직접 입력 시 추천 제목 선택 해제
  };

  const handleConfirm = () => {
    const finalTitle = customTitle.trim() || selectedTitle;
    
    if (!finalTitle) {
      alert('제목을 선택하거나 직접 입력해주세요.');
      return;
    }

    if (customTitle.trim()) {
      onDirectInput(finalTitle);
    } else {
      onTitleSelect(finalTitle);
    }
  };

  const handleCancel = () => {
    setSelectedTitle('');
    setCustomTitle('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          handleCancel();
        }
      }}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '16px',
          width: '90%',
          maxWidth: '600px',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          position: 'relative'
        }}
      >
        {/* 헤더 */}
        <div
          style={{
            padding: '24px 32px',
            borderBottom: '1px solid #e2e8f0',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '16px 16px 0 0'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
              🎯 채용공고 제목 추천
            </h3>
            <button
              onClick={handleCancel}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '24px',
                cursor: 'pointer',
                padding: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
              onMouseLeave={(e) => e.target.style.background = 'none'}
            >
              ×
            </button>
          </div>
        </div>

        {/* 콘텐츠 */}
        <div style={{ padding: '32px' }}>
          <div style={{ marginBottom: '24px' }}>
            <p style={{ 
              margin: '0 0 16px 0', 
              color: '#64748b', 
              fontSize: '14px',
              lineHeight: '1.5'
            }}>
              AI가 입력하신 정보를 분석하여 <strong>4가지 컨셉</strong>의 채용공고 제목을 추천해드립니다.<br/>
              🌱 신입친화형 | 💼 전문가형 | 📋 일반형 | 📝 일반형 변형<br/>
              추천 제목을 선택하거나 직접 입력하실 수 있습니다.
            </p>
          </div>

          {/* 로딩 상태 */}
          {isLoading && (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 0',
              color: '#667eea'
            }}>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ 
                  display: 'inline-block',
                  width: '40px',
                  height: '40px',
                  border: '3px solid #e2e8f0',
                  borderTop: '3px solid #667eea',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
              </div>
              <p style={{ margin: 0, fontSize: '14px' }}>
                AI가 제목을 생성하고 있습니다...
              </p>
            </div>
          )}

          {/* 오류 메시지 */}
          {error && (
            <div style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
              color: '#dc2626',
              fontSize: '14px',
              lineHeight: '1.5'
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>⚠️</span>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                    제목 추천 서비스 일시적 오류
                  </div>
                  <div>{error}</div>
                  <div style={{ 
                    marginTop: '8px', 
                    fontSize: '13px', 
                    color: '#6b7280',
                    fontStyle: 'italic'
                  }}>
                    기본 제목이 제공되었습니다. 직접 입력하거나 기본 제목을 선택해주세요.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI 추천 제목들 */}
          {!isLoading && recommendations.length > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <h4 style={{ 
                margin: '0 0 16px 0', 
                fontSize: '16px', 
                fontWeight: '600',
                color: '#1f2937'
              }}>
                🤖 AI 추천 제목
              </h4>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {recommendations.map((titleObj, index) => {
                  const title = typeof titleObj === 'object' ? titleObj.title : titleObj;
                  const concept = typeof titleObj === 'object' ? titleObj.concept : `추천 ${index + 1}번`;
                  
                  // 컨셉별 색상 및 아이콘 설정
                  const getConceptStyle = (concept) => {
                    switch(concept) {
                      case '신입친화형':
                        return { 
                          color: '#10b981', 
                          bgColor: '#ecfdf5', 
                          icon: '🌱',
                          borderColor: '#10b981'
                        };
                      case '전문가형':
                        return { 
                          color: '#8b5cf6', 
                          bgColor: '#f3e8ff', 
                          icon: '💼',
                          borderColor: '#8b5cf6'
                        };
                      case '일반형':
                        return { 
                          color: '#667eea', 
                          bgColor: '#e0e7ff', 
                          icon: '📋',
                          borderColor: '#667eea'
                        };
                      case '일반형 변형':
                        return { 
                          color: '#f59e0b', 
                          bgColor: '#fef3c7', 
                          icon: '📝',
                          borderColor: '#f59e0b'
                        };
                      default:
                        return { 
                          color: '#64748b', 
                          bgColor: '#f1f5f9', 
                          icon: '💡',
                          borderColor: '#64748b'
                        };
                    }
                  };
                  
                  const conceptStyle = getConceptStyle(concept);
                  const isSelected = selectedTitle === title;
                  
                  return (
                    <div
                      key={index}
                      onClick={() => handleTitleSelect(titleObj)}
                      style={{
                        padding: '16px',
                        border: `2px solid ${isSelected ? conceptStyle.borderColor : '#e2e8f0'}`,
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        backgroundColor: isSelected ? conceptStyle.bgColor : 'white',
                        position: 'relative'
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          e.target.style.borderColor = '#cbd5e0';
                          e.target.style.backgroundColor = '#f8fafc';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) {
                          e.target.style.borderColor = '#e2e8f0';
                          e.target.style.backgroundColor = 'white';
                        }
                      }}
                    >
                      {isSelected && (
                        <div style={{
                          position: 'absolute',
                          top: '12px',
                          right: '12px',
                          width: '20px',
                          height: '20px',
                          backgroundColor: conceptStyle.borderColor,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          ✓
                        </div>
                      )}
                      
                      {/* 컨셉 배지 */}
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        marginBottom: '8px',
                        padding: '4px 8px',
                        backgroundColor: conceptStyle.bgColor,
                        color: conceptStyle.color,
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '600'
                      }}>
                        <span>{conceptStyle.icon}</span>
                        {concept}
                      </div>
                      
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '500',
                        color: '#1f2937',
                        marginBottom: '4px',
                        lineHeight: '1.4'
                      }}>
                        {title}
                      </div>
                      
                      <div style={{
                        fontSize: '12px',
                        color: '#64748b'
                      }}>
                        {index + 1}번째 추천
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 직접 입력 */}
          <div style={{ marginBottom: '32px' }}>
            <h4 style={{ 
              margin: '0 0 16px 0', 
              fontSize: '16px', 
              fontWeight: '600',
              color: '#1f2937'
            }}>
              ✏️ 직접 입력
            </h4>
            
            <textarea
              value={customTitle}
              onChange={handleCustomTitleChange}
              placeholder="원하시는 제목을 직접 입력해주세요..."
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '16px',
                border: `2px solid ${customTitle ? '#667eea' : '#e2e8f0'}`,
                borderRadius: '12px',
                fontSize: '14px',
                resize: 'vertical',
                outline: 'none',
                transition: 'all 0.3s ease',
                fontFamily: 'inherit'
              }}
              onFocus={(e) => {
                if (!customTitle) {
                  e.target.style.borderColor = '#667eea';
                  e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
                }
              }}
              onBlur={(e) => {
                if (!customTitle) {
                  e.target.style.borderColor = '#e2e8f0';
                  e.target.style.boxShadow = 'none';
                }
              }}
            />
          </div>

          {/* 버튼 영역 */}
          <div style={{ 
            display: 'flex', 
            gap: '12px', 
            justifyContent: 'flex-end',
            paddingTop: '24px',
            borderTop: '1px solid #e2e8f0'
          }}>
            <button
              onClick={handleCancel}
              style={{
                padding: '12px 24px',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                backgroundColor: 'white',
                color: '#64748b',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#f8fafc';
                e.target.style.borderColor = '#cbd5e0';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'white';
                e.target.style.borderColor = '#e2e8f0';
              }}
            >
              취소
            </button>
            
            <button
              onClick={handleConfirm}
              disabled={!selectedTitle && !customTitle.trim()}
              style={{
                padding: '12px 24px',
                border: 'none',
                borderRadius: '8px',
                backgroundColor: (selectedTitle || customTitle.trim()) ? '#667eea' : '#e2e8f0',
                color: (selectedTitle || customTitle.trim()) ? 'white' : '#9ca3af',
                fontSize: '14px',
                fontWeight: '600',
                cursor: (selectedTitle || customTitle.trim()) ? 'pointer' : 'not-allowed',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (selectedTitle || customTitle.trim()) {
                  e.target.style.backgroundColor = '#5a67d8';
                  e.target.style.transform = 'translateY(-1px)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedTitle || customTitle.trim()) {
                  e.target.style.backgroundColor = '#667eea';
                  e.target.style.transform = 'translateY(0)';
                }
              }}
            >
              제목 적용하기
            </button>
          </div>
        </div>
      </div>

      {/* 회전 애니메이션 CSS */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default TitleRecommendationModal;
