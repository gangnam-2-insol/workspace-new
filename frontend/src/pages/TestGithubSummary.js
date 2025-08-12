import React, { useState } from 'react';

const TestGithubSummary = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!username.trim()) {
      setError('GitHub 아이디 또는 GitHub URL을 입력하세요');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/github/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim() })
      });
      const data = await res.json();
      if (!res.ok) {
        // 백엔드에서 detail만 내려올 수도 있으니 보강
        const msg = data?.message || data?.detail || '요약 요청 실패';
        throw new Error(msg);
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
        <div style={{ 
      minHeight: '100vh',
      background: '#f8f9fa',
      padding: '20px'
    }}>
      <div style={{ 
        maxWidth: 900, 
        margin: '0 auto', 
        fontFamily: 'Arial, sans-serif' 
      }}>
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
        </div>

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
              minWidth: '120px'
            }}
            onMouseOver={(e) => !loading && (e.target.style.transform = 'translateY(-2px)')}
            onMouseOut={(e) => !loading && (e.target.style.transform = 'translateY(0)')}
          >
            {loading ? '⏳ 분석 중...' : '🚀 분석하기'}
          </button>
        </form>
      </div>

      {error && (
        <div style={{ 
          background: '#fee', 
          color: '#c33', 
          padding: '15px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          border: '1px solid #fcc',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span style={{ fontSize: '20px' }}>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div style={{ 
          background: 'white', 
          borderRadius: '12px', 
          padding: '25px', 
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
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
              <div style={{ fontWeight: 'bold', color: '#333' }}>{result.source}</div>
            </div>
          </div>
          
          <div>
            <h3 style={{ 
              margin: '0 0 20px 0', 
              color: '#333', 
              fontSize: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              📋 상세 분석 결과
            </h3>
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
                           <div style={{ 
                             padding: '15px', 
                             background: '#e8f4f8', 
                             borderRadius: '8px',
                             border: '1px solid #d1ecf1',
                             color: '#0c5460'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🎯 주제</div>
                             <div style={{ fontWeight: 'bold' }}>{summary.주제}</div>
                           </div>
                           
                           <div style={{ 
                             padding: '15px', 
                             background: '#f8f9fa', 
                             borderRadius: '8px',
                             border: '1px solid #dee2e6',
                             color: '#495057'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>⚙️ 기술 스택</div>
                             <div style={{ fontWeight: 'bold' }}>
                               {Array.isArray(summary['기술 스택']) ? summary['기술 스택'].join(', ') : summary['기술 스택']}
                             </div>
                           </div>
                           
                           <div style={{ 
                             padding: '15px', 
                             background: '#e8f5e8', 
                             borderRadius: '8px',
                             border: '1px solid #d4edda',
                             color: '#155724'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🚀 주요 기능</div>
                             <div style={{ fontWeight: 'bold' }}>
                               {Array.isArray(summary['주요 기능']) ? summary['주요 기능'].join(', ') : summary['주요 기능']}
                             </div>
                           </div>
                           
                           <div style={{ 
                             padding: '15px', 
                             background: '#fff3cd', 
                             borderRadius: '8px',
                             border: '1px solid #ffeaa7',
                             color: '#856404'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🏗️ 아키텍처 구조</div>
                             <div style={{ fontWeight: 'bold' }}>{summary['아키텍처 구조'] || '정보 없음'}</div>
                           </div>
                           
                           <div style={{ 
                             padding: '15px', 
                             background: '#f8f9fa', 
                             borderRadius: '8px',
                             border: '1px solid #dee2e6',
                             color: '#495057'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>📚 외부 라이브러리</div>
                             <div style={{ fontWeight: 'bold' }}>
                               {(() => {
                                 const libraries = summary['외부 라이브러리'];
                                 if (!libraries || (Array.isArray(libraries) && libraries.length === 0) || libraries === '') {
                                   return '정보 없음';
                                 }
                                 return Array.isArray(libraries) ? libraries.join(', ') : libraries;
                               })()}
                             </div>
                           </div>
                           
                           <div style={{ 
                             padding: '15px', 
                             background: '#e2e3e5', 
                             borderRadius: '8px',
                             border: '1px solid #d6d8db',
                             color: '#383d41'
                           }}>
                             <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🤖 LLM 모델 정보</div>
                             <div style={{ fontWeight: 'bold' }}>{summary['LLM 모델 정보'] || '정보 없음'}</div>
                           </div>
                         </div>
                        
                        <div style={{ 
                          marginTop: '20px', 
                          padding: '15px', 
                          background: '#f8f9fa', 
                          borderRadius: '8px',
                          textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>🔗 레포지토리 링크</div>
                          <a 
                            href={summary['레포 주소']} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{ 
                              color: '#2c3e50', 
                              textDecoration: 'none',
                              fontWeight: 'bold',
                              fontSize: '16px'
                            }}
                          >
                            {summary['레포 주소']}
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
                          <div style={{ 
                            padding: '15px', 
                            background: '#e8f4f8', 
                            borderRadius: '8px',
                            border: '1px solid #d1ecf1',
                            color: '#0c5460'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🎯 주제</div>
                            <div style={{ fontWeight: 'bold' }}>{summaries.주제}</div>
                          </div>
                          
                          <div style={{ 
                            padding: '15px', 
                            background: '#f8f9fa', 
                            borderRadius: '8px',
                            border: '1px solid #dee2e6',
                            color: '#495057'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>⚙️ 기술 스택</div>
                            <div style={{ fontWeight: 'bold' }}>
                              {Array.isArray(summaries['기술 스택']) ? summaries['기술 스택'].join(', ') : summaries['기술 스택']}
                            </div>
                          </div>
                          
                          <div style={{ 
                            padding: '15px', 
                            background: '#e8f5e8', 
                            borderRadius: '8px',
                            border: '1px solid #d4edda',
                            color: '#155724'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🚀 주요 기능</div>
                            <div style={{ fontWeight: 'bold' }}>
                              {Array.isArray(summaries['주요 기능']) ? summaries['주요 기능'].join(', ') : summaries['주요 기능']}
                            </div>
                          </div>
                          
                          <div style={{ 
                            padding: '15px', 
                            background: '#fff3cd', 
                            borderRadius: '8px',
                            border: '1px solid #ffeaa7',
                            color: '#856404'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🏗️ 아키텍처 구조</div>
                            <div style={{ fontWeight: 'bold' }}>{summaries['아키텍처 구조'] || '정보 없음'}</div>
                          </div>
                          
                          <div style={{ 
                            padding: '15px', 
                            background: '#f8f9fa', 
                            borderRadius: '8px',
                            border: '1px solid #dee2e6',
                            color: '#495057'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>📚 외부 라이브러리</div>
                            <div style={{ fontWeight: 'bold' }}>
                              {(() => {
                                const libraries = summaries['외부 라이브러리'];
                                if (!libraries || (Array.isArray(libraries) && libraries.length === 0) || libraries === '') {
                                  return '정보 없음';
                                }
                                return Array.isArray(libraries) ? libraries.join(', ') : libraries;
                              })()}
                            </div>
                          </div>
                          
                          <div style={{ 
                            padding: '15px', 
                            background: '#e2e3e5', 
                            borderRadius: '8px',
                            border: '1px solid #d6d8db',
                            color: '#383d41'
                          }}>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '5px' }}>🤖 LLM 모델 정보</div>
                            <div style={{ fontWeight: 'bold' }}>{summaries['LLM 모델 정보'] || '정보 없음'}</div>
                          </div>
                        </div>
                        
                        <div style={{ 
                          marginTop: '20px', 
                          padding: '15px', 
                          background: '#f8f9fa', 
                          borderRadius: '8px',
                          textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>🔗 레포지토리 링크</div>
                          <a 
                            href={summaries['레포 주소']} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{ 
                              color: '#2c3e50', 
                              textDecoration: 'none',
                              fontWeight: 'bold',
                              fontSize: '16px'
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
      </div>
    </div>
  );
};

export default TestGithubSummary;


