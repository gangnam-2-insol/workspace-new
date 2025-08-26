import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const TestGithubSummary = ({ initialUsername = '', autoSubmit = false, applicant = null }) => {
  const [username, setUsername] = useState(initialUsername);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [showAllFields, setShowAllFields] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 5, step: '' });
  const [contentChanged, setContentChanged] = useState(false);
  const [showReanalysisButton, setShowReanalysisButton] = useState(false);

  // initialUsername이 변경되면 username 상태 업데이트
  useEffect(() => {
    if (initialUsername) {
      setUsername(initialUsername);
    }
  }, [initialUsername]);

  // autoSubmit이 true이고 username이 있으면 자동으로 요약 실행
  useEffect(() => {
    if (autoSubmit && username && !loading && !result) {
      handleIntegratedAnalysis();
    }
  }, [autoSubmit, username, loading, result]);

  // GitHub URL 파싱 함수 (백엔드와 동일한 로직)
  const parseGithubUrl = (url) => {
    if (!url || !url.startsWith('https://github.com/')) {
      return null;
    }
    
    try {
      const parsed = new URL(url);
      const parts = parsed.pathname.split('/').filter(p => p);
      
      if (parts.length >= 2) {
        return { username: parts[0], repo_name: parts[1] };
      } else if (parts.length === 1) {
        return { username: parts[0], repo_name: null };
      }
    } catch (error) {
      console.error('URL 파싱 오류:', error);
    }
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!username.trim()) {
      setError('GitHub 아이디 또는 GitHub URL을 입력하세요');
      return;
    }
    
    setLoading(true);
    await handleIntegratedAnalysis();
  };

  const handleForceReanalysis = async () => {
    setError('');
    setResult(null);
    setContentChanged(false);
    setShowReanalysisButton(false);
    setLoading(true);
    
    try {
      let requestData = { 
        username: username.trim(),
        applicant_id: applicant?._id || null,
        force_reanalysis: true
      };
      
      if (username.trim().startsWith('https://github.com/')) {
        const parsed = parseGithubUrl(username.trim());
        if (parsed) {
          requestData.username = parsed.username;
          if (parsed.repo_name) {
            requestData.repo_name = parsed.repo_name;
          }
        }
      }
      
      const res = await fetch((process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/github/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '재분석 중 오류가 발생했습니다.');
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleIntegratedAnalysis = async () => {
    setProgress({ current: 1, total: 5, step: 'GitHub 프로필 정보 확인 중...' });
    
    try {
      // URL 파싱하여 요청 데이터 구성
      let requestData = { 
        username: username.trim(),
        applicant_id: applicant?._id || null,
        force_reanalysis: false
      };
      
      if (username.trim().startsWith('https://github.com/')) {
        const parsed = parseGithubUrl(username.trim());
        if (parsed) {
          requestData.username = parsed.username;
          if (parsed.repo_name) {
            requestData.repo_name = parsed.repo_name;
          }
        }
      }
      
      // 2단계: 레포지토리 정보 수집
      setProgress({ current: 2, total: 5, step: '레포지토리 정보 수집 중...' });
      
      const res = await fetch((process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/github/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
      
      // 3단계: 코드 분석
      setProgress({ current: 3, total: 5, step: '코드 구조 및 언어 분석 중...' });
      
      const data = await res.json();
      if (!res.ok) {
        // 개선된 오류 메시지 처리
        let errorMessage = '분석 중 오류가 발생했습니다.';
        
        if (data?.detail) {
          if (data.detail.includes('404') || data.detail.includes('찾을 수 없습니다')) {
            if (data.detail.includes('사용자')) {
              errorMessage = 'GitHub 사용자를 찾을 수 없습니다. 사용자명을 확인해주세요.';
            } else if (data.detail.includes('리포지토리') || data.detail.includes('저장소')) {
            errorMessage = '레포지토리를 찾을 수 없습니다. URL과 접근 권한을 확인해주세요.';
            } else {
              errorMessage = '요청한 리소스를 찾을 수 없습니다. URL을 확인해주세요.';
            }
          } else if (data.detail.includes('403') || data.detail.includes('권한')) {
            errorMessage = '비공개 레포지토리입니다. 접근 권한이 필요합니다.';
          } else if (data.detail.includes('rate limit') || data.detail.includes('제한')) {
            errorMessage = 'GitHub API 제한에 도달했습니다. 잠시 후 다시 시도해주세요.';
          } else if (data.detail.includes('timeout') || data.detail.includes('시간 초과')) {
            errorMessage = '요청이 시간 초과되었습니다. 네트워크 상태를 확인해주세요.';
          } else {
            errorMessage = data.detail;
          }
        } else if (data?.message) {
          errorMessage = data.message;
        }
        
        throw new Error(errorMessage);
      }
      
      // 4단계: 아키텍처 분석 (특정 레포지토리가 있는 경우)
      if (requestData.repo_name) {
        setProgress({ current: 4, total: 5, step: 'AI 기반 아키텍처 분석 중...' });
      }
      
      // 5단계: 결과 생성
      setProgress({ current: 5, total: 5, step: '분석 결과 생성 중...' });
      
      // 콘텐츠 변경 감지 및 캐시 상태 확인
      if (data.source === 'cached') {
        console.log('캐시된 결과 사용됨');
        setContentChanged(false);
        setShowReanalysisButton(false);
      } else {
        console.log('새로운 분석 결과');
        setContentChanged(data.content_changed || false);
        setShowReanalysisButton(data.content_changed || false);
        
        if (data.content_changed && data.changes_detected) {
          console.log('감지된 변경 사항:', data.changes_detected);
        }
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setProgress({ current: 0, total: 5, step: '' });
    }
  };



  return (
        <div style={{ 
          minHeight: '100vh',
          background: '#f8f9fa',
          // padding: '20px'
        }}>
          <style>
            {`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}
          </style>
          <div style={{ 
            maxWidth: 900, 
            margin: '0 auto', 
            fontFamily: 'Arial, sans-serif' 
          }}>
            {!autoSubmit && (
              <div style={{ 
                background: '#2c3e50', 
                color: 'white', 
                padding: '30px', 
                borderRadius: '12px', 
                marginBottom: '30px',
                textAlign: 'center'
              }}>
                <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>🔍 GitHub 프로젝트 상세 분석</h1>
                <p style={{ margin: '10px 0 0 0', opacity: 0.9 }}>AI 기반 프로젝트 아키텍처 및 기술 스택 분석</p>
                
                <div style={{ 
                  marginTop: '15px',
                  padding: '10px',
                  background: 'rgba(52, 152, 219, 0.2)',
                  borderRadius: '6px',
                  fontSize: '13px',
                  opacity: 0.9
                }}>
                  💡 통합 분석: 요약 분석과 아키텍처 분석이 자동으로 함께 수행됩니다.
                  <br />
                  특정 레포지토리 URL을 입력하면 더 상세한 아키텍처 분석이 포함됩니다.
                </div>
              </div>
            )}

          {!autoSubmit && (
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '25px', 
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              marginBottom: '25px'
            }}>
              <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <input
                    placeholder="GitHub 아이디 또는 GitHub URL을 입력하세요 (예: https://github.com/test/test_project)"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={{ 
                      width: '100%', 
                      padding: '15px 20px', 
                      borderRadius: '8px', 
                      border: '2px solid #e1e5e9',
                      fontSize: '16px',
                      outline: 'none',
                      transition: 'border-color 0.3s ease'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#2c3e50'}
                    onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={loading} 
                  style={{ 
                    padding: '15px 25px',
                    borderRadius: '8px',
                    border: 'none',
                    background: loading ? '#ccc' : '#2c3e50',
                    color: 'white',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'transform 0.2s ease',
                    minWidth: '120px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseOver={(e) => !loading && (e.target.style.transform = 'translateY(-2px)')}
                  onMouseOut={(e) => !loading && (e.target.style.transform = 'translateY(0)')}
                >
                  {loading ? (
                    <>
                      <div style={{ 
                        width: '16px', 
                        height: '16px', 
                        borderRadius: '50%', 
                        border: '2px solid white',
                        borderTop: '2px solid transparent',
                        animation: 'spin 1s linear infinite'
                      }} />
                      분석 중...
                    </>
                  ) : (
                    <>
                      <span>🚀</span>
                      분석하기
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* 진행 상황 표시 */}
          {loading && progress.current > 0 && (
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '20px', 
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              marginBottom: '20px',
              border: '1px solid #e1e5e9'
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                marginBottom: '12px'
              }}>
                <div style={{ 
                  width: '20px', 
                  height: '20px', 
                  borderRadius: '50%', 
                  border: '2px solid #2c3e50',
                  borderTop: '2px solid transparent',
                  animation: 'spin 1s linear infinite'
                }} />
                <span style={{ 
                  fontSize: '16px', 
                  fontWeight: '600', 
                  color: '#2c3e50' 
                }}>
                  {autoSubmit ? `${username}의 GitHub 분석 중...` : '분석 진행 중...'}
                </span>
              </div>
              
              <div style={{ marginBottom: '8px' }}>
                <div style={{ 
                  fontSize: '14px', 
                  color: '#666', 
                  marginBottom: '4px' 
                }}>
                  {progress.step}
                </div>
                <div style={{ 
                  width: '100%', 
                  height: '6px', 
                  backgroundColor: '#e1e5e9', 
                  borderRadius: '3px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    width: `${(progress.current / progress.total) * 100}%`,
                    height: '100%',
                    backgroundColor: '#2c3e50',
                    borderRadius: '3px',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
              
              <div style={{ 
                fontSize: '12px', 
                color: '#999',
                textAlign: 'right' 
              }}>
                {progress.current} / {progress.total} 단계
              </div>
            </div>
          )}

          {error && (
            <div style={{ 
              background: '#fee', 
              color: '#c33', 
              padding: '20px', 
              borderRadius: '12px', 
              marginBottom: '20px',
              border: '1px solid #fcc',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                gap: '12px',
                marginBottom: '12px'
              }}>
                <span style={{ fontSize: '20px', marginTop: '2px' }}>⚠️</span>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    marginBottom: '8px' 
                  }}>
                    분석 중 오류가 발생했습니다
                  </div>
                  <div style={{ 
                    fontSize: '14px', 
                    lineHeight: '1.5',
                    marginBottom: '12px'
                  }}>
                    {error}
                  </div>
                  
                  {/* 해결 방법 제안 */}
                  <div style={{ 
                    background: '#fff3cd', 
                    border: '1px solid #ffeaa7', 
                    borderRadius: '8px', 
                    padding: '12px',
                    fontSize: '13px',
                    color: '#856404'
                  }}>
                    <div style={{ fontWeight: '600', marginBottom: '4px' }}>💡 해결 방법:</div>
                    <ul style={{ margin: 0, paddingLeft: '16px' }}>
                      {error.includes('찾을 수 없습니다') && (
                        <li>GitHub URL이 올바른지 확인해주세요</li>
                      )}
                      {error.includes('비공개') && (
                        <li>비공개 레포지토리의 경우 접근 권한이 필요합니다</li>
                      )}
                      {error.includes('API 제한') && (
                        <li>잠시 후 다시 시도하거나 GitHub 토큰을 사용해주세요</li>
                      )}
                      {error.includes('시간 초과') && (
                        <li>네트워크 연결을 확인하고 다시 시도해주세요</li>
                      )}
                      <li>GitHub 아이디 또는 레포지토리 URL을 다시 입력해보세요</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '25px', 
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}>
              {/* 콘텐츠 변경 알림 및 재분석 버튼 */}
              {contentChanged && (
                <div style={{
                  background: '#fff3cd',
                  border: '1px solid #ffeaa7',
                  borderRadius: '8px',
                  padding: '15px',
                  marginBottom: '20px'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    marginBottom: result.changes_detected && result.changes_detected.length > 0 ? '10px' : '0'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '20px' }}>⚠️</span>
                      <span style={{ color: '#856404', fontWeight: 'bold' }}>
                        등록된 정보가 차이가 납니다
                      </span>
                    </div>
                    <button
                      onClick={handleForceReanalysis}
                      disabled={loading}
                      style={{
                        background: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '8px 16px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      {loading ? '재분석 중...' : '재분석'}
                    </button>
                  </div>
                  
                  {/* 변경 사항 목록 표시 */}
                  {result.changes_detected && result.changes_detected.length > 0 && (
                    <div style={{ 
                      background: 'rgba(255, 255, 255, 0.5)', 
                      borderRadius: '6px', 
                      padding: '10px',
                      marginTop: '10px'
                    }}>
                      <div style={{ color: '#856404', fontSize: '14px', fontWeight: 'bold', marginBottom: '5px' }}>
                        감지된 변경 사항:
                      </div>
                      <ul style={{ 
                        margin: 0, 
                        paddingLeft: '20px', 
                        color: '#856404',
                        fontSize: '13px'
                      }}>
                        {result.changes_detected.map((change, index) => (
                          <li key={index}>{change}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              {/* 캐시된 결과 알림 */}
              {result.source === 'cached' && (
                <div style={{
                  background: '#d1ecf1',
                  border: '1px solid #bee5eb',
                  borderRadius: '8px',
                  padding: '12px',
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <span style={{ fontSize: '16px' }}>💾</span>
                  <span style={{ color: '#0c5460', fontSize: '14px' }}>
                    캐시된 분석 결과를 사용합니다
                  </span>
                </div>
              )}
              <div style={{ 
                display: 'flex', 
                gap: '20px', 
                marginBottom: '25px',
                padding: '15px',
                background: '#f8f9fa',
                borderRadius: '8px'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>👤 프로필</div>
                  <a 
                    href={result.profileUrl} 
                    target="_blank" 
                    rel="noreferrer"
                                    style={{ 
                      color: '#2c3e50', 
                      textDecoration: 'none',
                      fontWeight: 'bold'
                    }}
                  >
                    {result.profileUrl}
                  </a>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>📊 분석 소스</div>
                  <div style={{ fontWeight: 'bold', color: '#333' }}>
                    {result.source === 'profile_readme' && '프로필 README 분석'}
                    {result.source === 'repos_meta' && '전체 레포지토리 분석'}
                    {result.source?.startsWith('repos_meta_filtered_') && `특정 레포지토리 분석 (${result.source.replace('repos_meta_filtered_', '')})`}
                    {result.source?.startsWith('repo_analysis_') && `특정 레포지토리 분석 (${result.source.replace('repo_analysis_', '')})`}
                    {!result.source?.includes('profile_readme') && !result.source?.includes('repos_meta') && !result.source?.startsWith('repo_analysis_') && !result.source?.startsWith('repos_meta_filtered_') && result.source}
                  </div>
                </div>
              </div>

              {/* 언어 사용량 차트 섹션 - 인터랙티브(Recharts) */}
              {result.language_stats && Object.keys(result.language_stats).length > 0 ? (
                <div style={{ 
                  marginBottom: '25px',
                  textAlign: 'center'
                }}>
                  <h3 style={{ 
                    margin: '0 0 20px 0', 
                    color: '#333', 
                    fontSize: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px'
                  }}>
                    📊 언어 사용량 분석
                  </h3>
                  {(() => {
                    const stats = result.language_stats || {};
                    const total = result.language_total_bytes || Object.values(stats).reduce((a, b) => a + b, 0);
                    const entries = Object.entries(stats).sort(([,a], [,b]) => b - a);
                    
                    // 글자 겹침 방지를 위한 자동 "기타" 조정 로직
                    const processChartData = (data, totalBytes) => {
                      const processed = [];
                      let othersValue = 0;
                      let othersLanguages = [];
                      
                      // 최소 비율 설정 (차트에서 라벨이 겹치지 않도록)
                      const MIN_PERCENTAGE = 5; // 5% 미만은 기타로 분류
                      const MAX_VISIBLE_ITEMS = 6; // 최대 6개 항목만 표시
                      
                      for (let i = 0; i < data.length; i++) {
                        const [name, value] = data[i];
                        const percentage = (value / totalBytes) * 100;
                        
                        // 기타 항목은 건너뛰기 (나중에 처리)
                        if (name === '기타') {
                          othersValue += value;
                          continue;
                        }
                        
                        // 조건 1: 5% 미만인 경우 기타로 분류
                        // 조건 2: 6개 이상의 항목이 있는 경우 작은 것들을 기타로 분류
                        if (percentage < MIN_PERCENTAGE || processed.length >= MAX_VISIBLE_ITEMS) {
                          othersValue += value;
                          othersLanguages.push({ name, value, percentage });
                        } else {
                          processed.push({ name, value });
                        }
                      }
                      
                      // 기타 항목이 있으면 추가 (단, 기타로 분류되는 항목이 하나뿐이면 기타로 분류하지 않음)
                      if (othersValue > 0 && othersLanguages.length > 1) {
                        processed.push({ 
                          name: '기타', 
                          value: othersValue,
                          othersLanguages: othersLanguages.sort((a, b) => b.percentage - a.percentage)
                        });
                      } else if (othersValue > 0 && othersLanguages.length === 1) {
                        // 기타로 분류되는 항목이 하나뿐이면 원래 언어명으로 표시
                        const singleLanguage = othersLanguages[0];
                        processed.push({ 
                          name: singleLanguage.name, 
                          value: singleLanguage.value
                        });
                      }
                      
                      return processed;
                    };
                    
                    const processed = processChartData(entries, total);

                    const COLORS = [
                      '#F7DF1E','#3178C6','#3776AB','#ED8B00','#00599C','#A8B9CC','#239120','#777BB4',
                      '#CC342D','#00ADD8','#DEA584','#FA7343','#7F52FF','#DC322F','#E34F26','#1572B6',
                      '#4FC08D','#61DAFB','#DD0031','#339933','#00B4AB','#6C757D'
                    ];

                    // 커스텀 라벨: 내부 텍스트 + 외부 꺾임 라벨 조합
                    const RADIAN = Math.PI / 180;
                    const renderCustomizedLabel = (props) => {
                      const { cx, cy, midAngle, innerRadius, outerRadius, percent, name } = props;
                      const label = `${(name || '').toUpperCase()} (${(percent * 100).toFixed(1)}%)`;
                      
                      // 조각의 각도 계산
                      const angle = percent * 360;
                      
                      // 내부 텍스트 렌더링 (모든 조각에 표시)
                      let innerText = null;
                      if (percent > 0.01) { // 1% 이상이면 표시
                        const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
                        const x = cx + radius * Math.cos(-midAngle * RADIAN);
                        const y = cy + radius * Math.sin(-midAngle * RADIAN);
                        
                        // 텍스트 길이에 따른 폰트 크기 조정
                        let fontSize = '12px';
                        if (angle > 60) fontSize = '14px';
                        else if (angle > 40) fontSize = '13px';
                        else if (angle > 20) fontSize = '13px';
                        else fontSize = '13px'; // 작은 조각들 (9px에서 10px로 증가)
                        
                        const percentage = (percent * 100).toFixed(1);
                        
                        innerText = (
                          <g>
                            {/* 비율만 표시 */}
                            <text 
                              x={x} 
                              y={y} 
                              fill="black" 
                              textAnchor="middle" 
                              dominantBaseline="central"
                              style={{ 
                                fontSize: fontSize,
                                fontWeight: 'normal'
                              }}
                            >
                              {percentage}%
                            </text>
                          </g>
                        );
                      }
                      
                      return (
                        <g>
                          {innerText}
                        </g>
                      );
                    };

                    // 커스텀 툴팁 (기타 조각에 하위 언어와 비율 표시)
                    const CustomTooltip = ({ active, payload }) => {
                      if (!active || !payload || payload.length === 0) return null;
                      const item = payload[0]?.payload || {};
                      const name = payload[0]?.name || item?.name;
                      const value = payload[0]?.value || item?.value || 0;
                      const header = `${name} (${((value/total)*100).toFixed(1)}%)`;
                      let detail = null;
                      
                      // 기타 항목인 경우 하위 언어들을 표시
                      if (name === '기타' && item.othersLanguages && item.othersLanguages.length > 0) {
                        const parts = item.othersLanguages
                          .map(({ name: langName, percentage }) => `${langName} (${percentage.toFixed(1)}%)`)
                          .join(', ');
                        detail = parts;
                      } else if (name === '기타' && result.original_language_stats) {
                        // 기존 로직 (백업용)
                        const originalEntries = Object.entries(result.original_language_stats)
                          .filter(([langName, langValue]) => {
                            const percentage = (langValue / result.language_total_bytes) * 100;
                            return percentage <= 3 || !processed.some(p => p.name === langName);
                          })
                          .sort(([,a], [,b]) => b - a);
                        
                        if (originalEntries.length > 0) {
                          const parts = originalEntries
                            .map(([n, v]) => `${n} (${((v/result.language_total_bytes)*100).toFixed(1)}%)`)
                            .join(', ');
                          detail = parts;
                        }
                      }
                      
                      return (
                        <div style={{ background: '#fff', border: '1px solid #e1e5e9', borderRadius: 8, padding: '8px 10px', boxShadow: '0 4px 10px rgba(0,0,0,0.08)' }}>
                          <div style={{ fontWeight: 700, color: '#333', marginBottom: detail ? 6 : 0 }}>{header}</div>
                          {detail && <div style={{ fontSize: 12, color: '#555', maxWidth: 260 }}>{detail}</div>}
                        </div>
                      );
                    };

                    if (processed.length > 0) {
                      return (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
                          <ResponsiveContainer width="60%" height={360}>
                            <PieChart key={`chart-${result?.source || 'new'}-${Date.now()}`}>
                              <Pie
                                data={processed}
                                dataKey="value"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                innerRadius={0}
                                outerRadius={130}
                                startAngle={90}
                                endAngle={-270}
                                isAnimationActive={true}
                                animationBegin={0}
                                animationDuration={900}
                                animationEasing="ease-out"
                                labelLine={false}
                                label={renderCustomizedLabel}
                              >
                                {processed.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                              </Pie>
                              <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                          </ResponsiveContainer>
                          
                          {/* 오른쪽 범례 */}
                          <div style={{ 
                            flex: 1, 
                            display: 'flex', 
                            flexDirection: 'column', 
                            gap: '12px',
                            padding: '20px'
                          }}>
                            {processed.map((entry, index) => (
                              <div key={index} style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '12px',
                                fontSize: '14px',
                                fontWeight: '500'
                              }}>
                                <div style={{ 
                                  width: '16px', 
                                  height: '16px', 
                                  backgroundColor: COLORS[index % COLORS.length],
                                  borderRadius: '3px'
                                }} />
                                <span style={{ color: '#333' }}>{entry.name}</span>
                                <span style={{ color: '#666', fontSize: '12px' }}>
                                  ({((entry.value / total) * 100).toFixed(1)}%)
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })()}
                  
                                {/* <div style={{ 
                    marginTop: '15px', 
                    textAlign: 'center',
                    fontSize: '14px',
                    color: '#666',
                    padding: '10px',
                    background: '#e8f4f8',
                    borderRadius: '8px',
                    border: '1px solid #d1ecf1'
                  }}>
                    💡 차트는 인터랙티브하게 동작하며, 처음 로드 시 회전 애니메이션이 적용됩니다.
                  </div> */}
                </div>
              ) : null}
              
              <div>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '20px'
                }}>
                  <h3 style={{ 
                    margin: 0, 
                    color: '#333', 
                    fontSize: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    📋 상세 분석 결과
                  </h3>
                  
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '12px',
                    fontSize: '14px'
                  }}>
                    <span style={{ color: '#666', fontSize: '13px' }}>
                      간단 보기
                    </span>
                    
                    {/* 스위치 컨테이너 */}
                    <div
                      onClick={() => setShowAllFields(!showAllFields)}
                      style={{
                        position: 'relative',
                        width: '48px',
                        height: '24px',
                        backgroundColor: showAllFields ? '#2c3e50' : '#ddd',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'background-color 0.3s ease',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '2px'
                      }}
                    >
                      {/* 스위치 핸들 */}
                      <div
                        style={{
                          width: '20px',
                          height: '20px',
                          backgroundColor: 'white',
                          borderRadius: '50%',
                          transform: showAllFields ? 'translateX(24px)' : 'translateX(0px)',
                          transition: 'transform 0.3s ease',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}
                      />
                    </div>
                    
                    <span style={{ color: '#666', fontSize: '13px' }}>
                      전체 보기
                    </span>
                  </div>
                </div>
                {(() => {
                  try {
                    const summaries = JSON.parse(result.summary);
                    return (
                      <div>
                        {Array.isArray(summaries) ? summaries.map((summary, index) => (
                          <div key={index} style={{ 
                            marginBottom: '25px', 
                            padding: '25px', 
                            border: '1px solid #e1e5e9', 
                            borderRadius: '12px',
                            background: 'white',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                            transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                          }}
                          onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
                          onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                          >
                            {summary.name && (
                                                        <h4 style={{ 
                                margin: '0 0 20px 0', 
                                color: '#333', 
                                fontSize: '18px',
                                borderBottom: '2px solid #2c3e50',
                                paddingBottom: '10px'
                              }}>
                                📁 {summary.name}
                              </h4>
                            )}
                            
                                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                              {/* 주제 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#e8f4f8', 
                                borderRadius: '8px',
                                border: '1px solid #d1ecf1',
                                color: (!summary.주제 || summary.주제 === '정보 없음') ? '#999' : '#0c5460',
                                opacity: (!summary.주제 || summary.주제 === '정보 없음') ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🎯 주제</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {summary.주제 || '정보 없음'}
                                </div>
                              </div>
                              
                              {/* 기술 스택 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#f8f9fa', 
                                borderRadius: '8px',
                                border: '1px solid #dee2e6',
                                color: (!summary['기술 스택'] || summary['기술 스택'] === '정보 없음' || 
                                  (Array.isArray(summary['기술 스택']) && summary['기술 스택'].length === 0)) ? '#999' : '#495057',
                                opacity: (!summary['기술 스택'] || summary['기술 스택'] === '정보 없음' || 
                                  (Array.isArray(summary['기술 스택']) && summary['기술 스택'].length === 0)) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>⚙️ 기술 스택</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const techStack = summary['기술 스택'];
                                    if (!techStack || techStack === '정보 없음' || 
                                        (Array.isArray(techStack) && techStack.length === 0)) {
                                      return '정보 없음';
                                    }
                                    return Array.isArray(techStack) ? techStack.join(', ') : techStack;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 주요 기능 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#e8f5e8', 
                                borderRadius: '8px',
                                border: '1px solid #d4edda',
                                color: (!summary['주요 기능'] || summary['주요 기능'] === '정보 없음' || 
                                  (Array.isArray(summary['주요 기능']) && summary['주요 기능'].length === 0)) ? '#999' : '#155724',
                                opacity: (!summary['주요 기능'] || summary['주요 기능'] === '정보 없음' || 
                                  (Array.isArray(summary['주요 기능']) && summary['주요 기능'].length === 0)) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🚀 주요 기능</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const features = summary['주요 기능'];
                                    if (!features || features === '정보 없음' || 
                                        (Array.isArray(features) && features.length === 0)) {
                                      return '정보 없음';
                                    }
                                    return Array.isArray(features) ? features.join(', ') : features;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 아키텍처 구조 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#fff3cd', 
                                borderRadius: '8px',
                                border: '1px solid #ffeaa7',
                                color: (!summary['아키텍처 구조'] || 
                                  summary['아키텍처 구조'] === '정보 없음' ||
                                  summary['아키텍처 구조'].includes('파악하기 어렵습니다') ||
                                  summary['아키텍처 구조'].includes('확인되지 않습니다')) ? '#999' : '#856404',
                                opacity: (!summary['아키텍처 구조'] || 
                                  summary['아키텍처 구조'] === '정보 없음' ||
                                  summary['아키텍처 구조'].includes('파악하기 어렵습니다') ||
                                  summary['아키텍처 구조'].includes('확인되지 않습니다')) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🏗️ 아키텍처 구조</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const archInfo = summary['아키텍처 구조'];
                                    if (!archInfo || archInfo === '정보 없음' ||
                                        archInfo.includes('파악하기 어렵습니다') ||
                                        archInfo.includes('확인되지 않습니다')) {
                                      return '정보 없음';
                                    }
                                    return archInfo;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 외부 라이브러리 - 전체 보기에서만 표시 */}
                              {showAllFields && (
                                <div style={{ 
                                  padding: '15px', 
                                  background: '#f8f9fa', 
                                  borderRadius: '8px',
                                  border: '1px solid #dee2e6',
                                  color: (() => {
                                    const libraries = summary['외부 라이브러리'];
                                    return !libraries || libraries === '정보 없음' || libraries === '' || 
                                      (Array.isArray(libraries) && libraries.length === 0);
                                  })() ? '#999' : '#495057',
                                  opacity: (() => {
                                    const libraries = summary['외부 라이브러리'];
                                    return !libraries || libraries === '정보 없음' || libraries === '' || 
                                      (Array.isArray(libraries) && libraries.length === 0);
                                  })() ? 0.6 : 1
                                }}>
                                  <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>📚 외부 라이브러리</div>
                                  <div style={{ fontWeight: 'bold' }}>
                                    {(() => {
                                      const libraries = summary['외부 라이브러리'];
                                      if (!libraries || libraries === '정보 없음' || libraries === '' || 
                                          (Array.isArray(libraries) && libraries.length === 0)) {
                                        return '정보 없음';
                                      }
                                      return Array.isArray(libraries) ? libraries.join(', ') : libraries;
                                    })()}
                                  </div>
                                </div>
                              )}
                              
                              {/* LLM 모델 정보 - 전체 보기에서만 표시 */}
                              {showAllFields && (
                                <div style={{ 
                                  padding: '15px', 
                                  background: '#e2e3e5', 
                                  borderRadius: '8px',
                                  border: '1px solid #d6d8db',
                                  color: (() => {
                                    const llmInfo = summary['LLM 모델 정보'];
                                    return !llmInfo || llmInfo === '정보 없음' ||
                                      llmInfo.includes('확인되지 않습니다') ||
                                      llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                      llmInfo.includes('파악하기 어렵습니다');
                                  })() ? '#999' : '#383d41',
                                  opacity: (() => {
                                    const llmInfo = summary['LLM 모델 정보'];
                                    return !llmInfo || llmInfo === '정보 없음' ||
                                      llmInfo.includes('확인되지 않습니다') ||
                                      llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                      llmInfo.includes('파악하기 어렵습니다');
                                  })() ? 0.6 : 1
                                }}>
                                  <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🤖 LLM 모델 정보</div>
                                  <div style={{ fontWeight: 'bold' }}>
                                    {(() => {
                                      const llmInfo = summary['LLM 모델 정보'];
                                      if (!llmInfo || llmInfo === '정보 없음' ||
                                          llmInfo.includes('확인되지 않습니다') ||
                                          llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                          llmInfo.includes('파악하기 어렵습니다')) {
                                        return '정보 없음';
                                      }
                                      return llmInfo;
                                    })()}
                                  </div>
                                </div>
                              )}
                            </div>
                            
                                                                              {/* 핵심파일 분석 정보 - UI에서 숨김 처리 */}
                              {/* 
                              {showAllFields && result.detailed_analysis && (
                                <div style={{ 
                                  marginTop: '20px', 
                                  padding: '15px', 
                                  background: 'linear-gradient(135deg, #f8f9fa 0%, #e8f4f8 100%)', 
                                  borderRadius: '8px',
                                  border: '2px solid #17a2b8'
                                }}>
                                  <h5 style={{ 
                                    margin: '0 0 15px 0', 
                                    color: '#2c3e50', 
                                    fontSize: '16px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px'
                                  }}>
                                    📄 핵심파일 분석 정보
                                  </h5>
                                  
                                  <div style={{ 
                                    fontSize: '12px', 
                                    color: '#666',
                                    textAlign: 'center',
                                    padding: '8px',
                                    background: 'rgba(255,255,255,0.8)',
                                    borderRadius: '6px',
                                    marginBottom: '15px'
                                  }}>
                                    💡 핵심파일 선별 조회를 통해 의존성, 프레임워크, 빌드 도구를 자동으로 감지했습니다.
                                  </div>
                                </div>
                              )}
                              */}
                            
                            {/* 레포지토리 링크 - 별도 섹션 */}
                            <div style={{ 
                              marginTop: '15px', 
                              padding: '15px', 
                              background: 'linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%)', 
                              borderRadius: '8px',
                              border: '2px solid #28a745',
                              textAlign: 'center'
                            }}>
                              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>🔗 레포지토리 링크</div>
                              <a 
                                href={summary['레포 주소'] || result.profileUrl} 
                                target="_blank" 
                                rel="noreferrer"
                                style={{ 
                                  color: '#2c3e50', 
                                  textDecoration: 'none',
                                  fontWeight: 'bold',
                                  fontSize: '16px',
                                  display: 'inline-block',
                                  padding: '8px 16px',
                                  background: 'rgba(255,255,255,0.9)',
                                  borderRadius: '6px',
                                  border: '1px solid #d1ecf1',
                                  transition: 'all 0.3s ease'
                                }}
                                onMouseOver={(e) => {
                                  e.target.style.transform = 'translateY(-2px)';
                                  e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                                }}
                                onMouseOut={(e) => {
                                  e.target.style.transform = 'translateY(0)';
                                  e.target.style.boxShadow = 'none';
                                }}
                              >
                                {summary['레포 주소'] || result.profileUrl}
                              </a>
                            </div>
                          </div>
                        )) : (
                          <div style={{ 
                            padding: '25px', 
                            border: '1px solid #e1e5e9', 
                            borderRadius: '12px',
                            background: 'white',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
                          }}>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                              {/* 주제 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#e8f4f8', 
                                borderRadius: '8px',
                                border: '1px solid #d1ecf1',
                                color: (!summaries.주제 || summaries.주제 === '정보 없음') ? '#999' : '#0c5460',
                                opacity: (!summaries.주제 || summaries.주제 === '정보 없음') ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🎯 주제</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {summaries.주제 || '정보 없음'}
                                </div>
                              </div>
                              
                              {/* 기술 스택 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#f8f9fa', 
                                borderRadius: '8px',
                                border: '1px solid #dee2e6',
                                color: (!summaries['기술 스택'] || summaries['기술 스택'] === '정보 없음' || 
                                (Array.isArray(summaries['기술 스택']) && summaries['기술 스택'].length === 0)) ? '#999' : '#495057',
                                opacity: (!summaries['기술 스택'] || summaries['기술 스택'] === '정보 없음' || 
                                (Array.isArray(summaries['기술 스택']) && summaries['기술 스택'].length === 0)) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>⚙️ 기술 스택</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const techStack = summaries['기술 스택'];
                                    if (!techStack || techStack === '정보 없음' || 
                                        (Array.isArray(techStack) && techStack.length === 0)) {
                                      return '정보 없음';
                                    }
                                    return Array.isArray(techStack) ? techStack.join(', ') : techStack;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 주요 기능 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#e8f5e8', 
                                borderRadius: '8px',
                                border: '1px solid #d4edda',
                                color: (!summaries['주요 기능'] || summaries['주요 기능'] === '정보 없음' || 
                                (Array.isArray(summaries['주요 기능']) && summaries['주요 기능'].length === 0)) ? '#999' : '#155724',
                                opacity: (!summaries['주요 기능'] || summaries['주요 기능'] === '정보 없음' || 
                                (Array.isArray(summaries['주요 기능']) && summaries['주요 기능'].length === 0)) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🚀 주요 기능</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const features = summaries['주요 기능'];
                                    if (!features || features === '정보 없음' || 
                                        (Array.isArray(features) && features.length === 0)) {
                                      return '정보 없음';
                                    }
                                    return Array.isArray(features) ? features.join(', ') : features;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 아키텍처 구조 */}
                              <div style={{ 
                                padding: '15px', 
                                background: '#fff3cd', 
                                borderRadius: '8px',
                                border: '1px solid #ffeaa7',
                                color: (!summaries['아키텍처 구조'] || 
                                  summaries['아키텍처 구조'] === '정보 없음' ||
                                  summaries['아키텍처 구조'].includes('파악하기 어렵습니다') ||
                                  summaries['아키텍처 구조'].includes('확인되지 않습니다')) ? '#999' : '#856404',
                                opacity: (!summaries['아키텍처 구조'] || 
                                  summaries['아키텍처 구조'] === '정보 없음' ||
                                  summaries['아키텍처 구조'].includes('파악하기 어렵습니다') ||
                                  summaries['아키텍처 구조'].includes('확인되지 않습니다')) ? 0.6 : 1
                              }}>
                                <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🏗️ 아키텍처 구조</div>
                                <div style={{ fontWeight: 'bold' }}>
                                  {(() => {
                                    const archInfo = summaries['아키텍처 구조'];
                                    if (!archInfo || archInfo === '정보 없음' ||
                                        archInfo.includes('파악하기 어렵습니다') ||
                                        archInfo.includes('확인되지 않습니다')) {
                                      return '정보 없음';
                                    }
                                    return archInfo;
                                  })()}
                                </div>
                              </div>
                              
                              {/* 외부 라이브러리 - 전체 보기에서만 표시 */}
                              {showAllFields && (
                                <div style={{ 
                                  padding: '15px', 
                                  background: '#f8f9fa', 
                                  borderRadius: '8px',
                                  border: '1px solid #dee2e6',
                                  color: (() => {
                                    const libraries = summaries['외부 라이브러리'];
                                    return !libraries || libraries === '정보 없음' || libraries === '' || 
                                      (Array.isArray(libraries) && libraries.length === 0);
                                  })() ? '#999' : '#495057',
                                  opacity: (() => {
                                    const libraries = summaries['외부 라이브러리'];
                                    return !libraries || libraries === '정보 없음' || libraries === '' || 
                                      (Array.isArray(libraries) && libraries.length === 0);
                                  })() ? 0.6 : 1
                                }}>
                                  <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>📚 외부 라이브러리</div>
                                  <div style={{ fontWeight: 'bold' }}>
                                    {(() => {
                                      const libraries = summaries['외부 라이브러리'];
                                      if (!libraries || libraries === '정보 없음' || libraries === '' || 
                                          (Array.isArray(libraries) && libraries.length === 0)) {
                                        return '정보 없음';
                                      }
                                      return Array.isArray(libraries) ? libraries.join(', ') : libraries;
                                    })()}
                                  </div>
                                </div>
                              )}
                              
                              {/* LLM 모델 정보 - 전체 보기에서만 표시 */}
                              {showAllFields && (
                                <div style={{ 
                                  padding: '15px', 
                                  background: '#e2e3e5', 
                                  borderRadius: '8px',
                                  border: '1px solid #d6d8db',
                                  color: (() => {
                                    const llmInfo = summaries['LLM 모델 정보'];
                                    return !llmInfo || llmInfo === '정보 없음' ||
                                      llmInfo.includes('확인되지 않습니다') ||
                                      llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                      llmInfo.includes('파악하기 어렵습니다');
                                  })() ? '#999' : '#383d41',
                                  opacity: (() => {
                                    const llmInfo = summaries['LLM 모델 정보'];
                                    return !llmInfo || llmInfo === '정보 없음' ||
                                      llmInfo.includes('확인되지 않습니다') ||
                                      llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                      llmInfo.includes('파악하기 어렵습니다');
                                  })() ? 0.6 : 1
                                }}>
                                  <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🤖 LLM 모델 정보</div>
                                  <div style={{ fontWeight: 'bold' }}>
                                    {(() => {
                                      const llmInfo = summaries['LLM 모델 정보'];
                                      if (!llmInfo || llmInfo === '정보 없음' ||
                                          llmInfo.includes('확인되지 않습니다') ||
                                          llmInfo.includes('직접적으로 확인되지 않습니다') ||
                                          llmInfo.includes('파악하기 어렵습니다')) {
                                        return '정보 없음';
                                      }
                                      return llmInfo;
                                    })()}
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {/* 레포지토리 링크 - 별도 섹션 */}
                            <div style={{ 
                              marginTop: '15px', 
                              padding: '15px', 
                              // background: 'linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%)', 
                              borderRadius: '8px',
                              // border: '2px solid #28a745',
                              textAlign: 'center'
                            }}>
                              <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>🔗 레포지토리 링크</div>
                              <a 
                                href={summaries['레포 주소']} 
                                target="_blank" 
                                rel="noreferrer"
                                style={{ 
                                  color: '#2c3e50', 
                                  textDecoration: 'none',
                                  fontWeight: 'bold',
                                  fontSize: '16px',
                                  display: 'inline-block',
                                  padding: '8px 16px',
                                  background: 'rgba(255,255,255,0.9)',
                                  borderRadius: '6px',
                                  // border: '1px solid #d1ecf1',
                                  transition: 'all 0.3s ease'
                                }}
                                onMouseOver={(e) => {
                                  e.target.style.transform = 'translateY(-2px)';
                                  e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                                }}
                                onMouseOut={(e) => {
                                  e.target.style.transform = 'translateY(0)';
                                  e.target.style.boxShadow = 'none';
                                }}
                              >
                                {summaries['레포 주소']}
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  } catch (e) {
                    // JSON 파싱 실패 시 기존 텍스트 형태로 표시
                    return (
                      <div style={{ 
                        padding: '20px', 
                        background: '#fff3cd', 
                        border: '1px solid #ffeaa7', 
                        borderRadius: '8px',
                        color: '#856404'
                      }}>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '10px', 
                          marginBottom: '15px',
                          fontSize: '18px',
                          fontWeight: 'bold'
                        }}>
                          <span>⚠️</span>
                          <span>원시 분석 결과</span>
                        </div>
                        <pre style={{ 
                          whiteSpace: 'pre-wrap', 
                          wordBreak: 'break-word',
                          margin: 0,
                          fontSize: '14px',
                          lineHeight: '1.5'
                        }}>
                          {result.summary}
                        </pre>
                      </div>
                    );
                  }
                })()}
              </div>
            </div>
          )}

          {/* AI 기반 아키텍처 분석 결과 - 맨 아래에 배치 */}
          {result && result.detailed_analysis?.architecture_analysis && result.detailed_analysis.architecture_analysis.total_repos_analyzed > 0 && (
            <div style={{ 
              marginTop: '20px', 
              padding: '20px', 
              background: 'linear-gradient(135deg, #f8f9fa 0%, #e8f4f8 100%)', 
              borderRadius: '12px',
              border: '2px solid #17a2b8'
            }}>
              <h5 style={{ 
                margin: '0 0 20px 0', 
                color: '#2c3e50', 
                fontSize: '18px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontWeight: 'bold'
              }}>
                🤖 AI 기반 아키텍처 분석 결과
              </h5>
              
              <div style={{ 
                fontSize: '12px', 
                color: '#666',
                textAlign: 'center',
                padding: '8px',
                background: 'rgba(255,255,255,0.8)',
                borderRadius: '6px',
                marginBottom: '20px'
              }}>
                총 {result.detailed_analysis.architecture_analysis.total_repos_analyzed}개 레포지토리에 대해 AI 기반 아키텍처 분석을 수행했습니다.
              </div>
              
              {result.detailed_analysis.architecture_analysis.architecture_results.map((arch, index) => (
                <div key={index} style={{ 
                  marginBottom: '20px',
                  padding: '15px',
                  background: 'white',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '15px'
                  }}>
                    <h6 style={{ 
                      margin: 0, 
                      color: '#2c3e50', 
                      fontSize: '16px',
                      fontWeight: 'bold'
                    }}>
                      📁 {arch.owner}/{arch.repo}
                    </h6>
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#666',
                      display: 'flex',
                      gap: '10px'
                    }}>
                      <span>⏱️ {arch.analysis_time.toFixed(2)}초</span>
                      <span>📄 {arch.opened_files.length}개 파일</span>
                    </div>
                  </div>
                  
                  {/* 분석 실패 메시지 */}
                  {arch.topic === '분석 실패' && (
                    <div style={{ 
                      marginBottom: '15px',
                      padding: '10px', 
                      background: '#f8d7da', 
                      borderRadius: '6px',
                      border: '1px solid #f5c6cb'
                    }}>
                      <div style={{ fontSize: '13px', color: '#721c24', marginBottom: '5px', fontWeight: 'bold' }}>⚠️ 분석 실패</div>
                      <div style={{ fontSize: '14px', color: '#721c24', lineHeight: '1.4' }}>
                        이 레포지토리의 아키텍처 분석에 실패했습니다. 기본 메타데이터 분석 결과를 참고해주세요.
                      </div>
                    </div>
                  )}
                  
                  {/* 분석 성공한 경우에만 상세 정보 표시 */}
                  {arch.topic !== '분석 실패' && (
                    <>
                      <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                        gap: '10px',
                        marginBottom: '15px'
                      }}>
                        {/* 기술 스택 */}
                        {arch.tech_stack && arch.tech_stack.length > 0 && (
                          <div style={{ 
                            padding: '10px', 
                            background: '#e3f2fd', 
                            borderRadius: '6px',
                            border: '1px solid #bbdefb'
                          }}>
                            <div style={{ fontSize: '13px', color: '#1976d2', marginBottom: '5px', fontWeight: 'bold' }}>⚙️ 기술 스택</div>
                            <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#0d47a1' }}>
                              {arch.tech_stack.join(', ')}
                            </div>
                          </div>
                        )}
                        
                        {/* 외부 라이브러리 */}
                        {arch.external_libs && arch.external_libs.length > 0 && (
                          <div style={{ 
                            padding: '10px', 
                            background: '#fff3cd', 
                            borderRadius: '6px',
                            border: '1px solid #ffeaa7'
                          }}>
                            <div style={{ fontSize: '13px', color: '#856404', marginBottom: '5px', fontWeight: 'bold' }}>📚 외부 라이브러리</div>
                            <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#856404' }}>
                              {arch.external_libs.slice(0, 5).join(', ')}
                              {arch.external_libs.length > 5 && ` 외 ${arch.external_libs.length - 5}개`}
                            </div>
                          </div>
                        )}
                        
                        {/* LLM 모델 */}
                        {arch.llm_models && arch.llm_models.length > 0 && (
                          <div style={{ 
                            padding: '10px', 
                            background: '#e8f5e8', 
                            borderRadius: '6px',
                            border: '1px solid #c8e6c9'
                          }}>
                            <div style={{ fontSize: '13px', color: '#155724', marginBottom: '5px', fontWeight: 'bold' }}>🤖 LLM 모델</div>
                            <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#155724' }}>
                              {arch.llm_models.join(', ')}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* 주요 기능 (아키텍처 구조에서 추출) */}
                      {arch.architecture && arch.architecture !== '분석 완료' && arch.architecture !== '분석 실패' && (
                        <div style={{ 
                          marginBottom: '15px',
                          padding: '10px', 
                          background: '#e8f5e8', 
                          borderRadius: '6px',
                          border: '1px solid #d4edda'
                        }}>
                          <div style={{ fontSize: '13px', color: '#155724', marginBottom: '5px', fontWeight: 'bold' }}>🚀 주요 기능</div>
                          <div style={{ fontSize: '14px', color: '#155724', lineHeight: '1.4' }}>
                            {arch.architecture.length > 200 ? arch.architecture.substring(0, 200) + '...' : arch.architecture}
                          </div>
                        </div>
                      )}
                      
                      {/* 아키텍처 구조 */}
                      {arch.architecture && arch.architecture !== '분석 완료' && arch.architecture !== '분석 실패' && (
                        <div style={{ 
                          padding: '12px', 
                          background: '#f8f9fa', 
                          borderRadius: '6px',
                          border: '1px solid #dee2e6',
                          fontSize: '13px',
                          lineHeight: '1.5',
                          color: '#495057',
                          marginBottom: '15px'
                        }}>
                          <div style={{ fontSize: '13px', color: '#495057', marginBottom: '5px', fontWeight: 'bold' }}>🏗️ 아키텍처 구조</div>
                          <div style={{ fontSize: '13px', lineHeight: '1.5' }}>
                            {arch.architecture}
                          </div>
                        </div>
                      )}
                      
                      {/* 분석된 파일 목록 - 상세 분석 결과 다음에 표시 */}
                      {arch.opened_files && arch.opened_files.length > 0 && (
                        <div style={{ 
                          padding: '10px', 
                          background: '#f8f9fa', 
                          borderRadius: '6px',
                          border: '1px solid #dee2e6'
                        }}>
                          <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px', fontWeight: 'bold' }}>📄 핵심파일 분석</div>
                          <div style={{ fontSize: '11px', color: '#666', lineHeight: '1.3' }}>
                            {arch.opened_files.slice(0, 8).join(', ')}
                            {arch.opened_files.length > 8 && ` 외 ${arch.opened_files.length - 8}개`}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
              
              <div style={{ 
                fontSize: '12px', 
                color: '#666',
                textAlign: 'center',
                padding: '8px',
                background: 'rgba(255,255,255,0.8)',
                borderRadius: '4px',
                border: '1px solid #e1e5e9'
              }}>
                💡 AI가 자동으로 필요한 파일들을 선택하여 깊이 있는 아키텍처 분석을 수행했습니다.
              </div>
            </div>
          )}

          {/* 토큰 사용량 표시 - 맨 아래에 배치 */}
          {result && result.token_usage && (
            <div style={{ 
              marginTop: '20px', 
              padding: '15px', 
              background: 'linear-gradient(135deg, #f8f9fa 0%, #e8f4f8 100%)', 
              borderRadius: '8px',
              border: '2px solid #28a745'
            }}>
              <h5 style={{ 
                margin: '0 0 15px 0', 
                color: '#2c3e50', 
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                📊 API 토큰 사용량
              </h5>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                gap: '15px'
              }}>
                {/* GitHub API 호출 수 */}
                <div style={{ 
                  padding: '12px', 
                  background: 'white', 
                  borderRadius: '6px',
                  border: '1px solid #dee2e6',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>🔗 GitHub API</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2c3e50' }}>
                    {result.token_usage.github_api_calls || 0}회 호출
                  </div>
                </div>
                
                {/* OpenAI API 호출 수 */}
                <div style={{ 
                  padding: '12px', 
                  background: 'white', 
                  borderRadius: '6px',
                  border: '1px solid #dee2e6',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>🤖 OpenAI API</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2c3e50' }}>
                    {result.token_usage.openai_api_calls || 0}회 호출
                  </div>
                </div>
                
                {/* OpenAI 토큰 사용량 */}
                <div style={{ 
                  padding: '12px', 
                  background: 'white', 
                  borderRadius: '6px',
                  border: '1px solid #dee2e6',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>🔤 토큰 사용량</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2c3e50' }}>
                    {result.token_usage.openai_tokens_used || 0} 토큰
                  </div>
                </div>
              </div>
              
              <div style={{ 
                fontSize: '12px', 
                color: '#666',
                textAlign: 'center',
                marginTop: '10px',
                padding: '8px',
                background: 'rgba(255,255,255,0.8)',
                borderRadius: '4px'
              }}>
                💡 API 호출 횟수와 토큰 사용량은 분석 품질과 비용을 추적하는 데 도움이 됩니다.
              </div>
            </div>
          )}
      </div>
    </div>
  );
};

export default TestGithubSummary;


 