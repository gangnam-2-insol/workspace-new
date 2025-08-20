import React from 'react';
import { FiGithub, FiExternalLink, FiStar, FiAward, FiCode, FiTrendingUp, FiUsers, FiCalendar } from 'react-icons/fi';

const PortfolioSummaryPanel = ({ portfolio }) => {
  if (!portfolio) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px 20px',
        color: 'var(--text-secondary)',
        fontSize: '16px'
      }}>
        <FiCode size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
        <div>포트폴리오 정보가 없습니다.</div>
        <div style={{ fontSize: '14px', marginTop: '8px' }}>
          지원자의 포트폴리오를 먼저 등록해주세요.
        </div>
      </div>
    );
  }

  // 포트폴리오 분석 점수 계산 (실제 데이터 기반)
  const calculateScore = () => {
    if (portfolio.analysis_score !== undefined) {
      return Math.min(100, Math.max(0, portfolio.analysis_score));
    }
    // 분석 점수가 없으면 프로젝트 수와 아이템 수를 기반으로 계산
    const projectCount = portfolio.items ? portfolio.items.length : 0;
    const baseScore = Math.min(100, projectCount * 25); // 프로젝트당 25점
    return baseScore;
  };

  const score = calculateScore();
  const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';
  const scoreLevel = score >= 80 ? '우수' : score >= 60 ? '양호' : '개선 필요';

  return (
    <div style={{ padding: '0 4px' }}>
      {/* 포트폴리오 개요 */}
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.1 }}>
          <FiCode size={120} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '700' }}>
              포트폴리오 분석 결과
            </h2>
            <p style={{ margin: '0 0 16px 0', opacity: 0.9, fontSize: '14px' }}>
              AI 기반 포트폴리오 종합 평가
            </p>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiCalendar size={16} />
                <span style={{ fontSize: '14px' }}>
                  등록일: {portfolio.created_at ? new Date(portfolio.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiTrendingUp size={16} />
                <span style={{ fontSize: '14px' }}>
                  버전: {portfolio.version || 1}
                </span>
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              borderRadius: '50%', 
              background: `conic-gradient(${scoreColor} ${score * 3.6}deg, rgba(255,255,255,0.2) 0deg)`,
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              marginBottom: '8px'
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                borderRadius: '50%', 
                background: 'rgba(255,255,255,0.1)',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontSize: '18px',
                fontWeight: '700'
              }}>
                {score}
              </div>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600' }}>{scoreLevel}</div>
          </div>
        </div>
      </div>

      {/* 분석 요약 */}
      {portfolio.summary && (
        <div style={{ 
          background: 'var(--bg-secondary)', 
          borderRadius: '12px', 
          padding: '20px', 
          marginBottom: '24px',
          border: '1px solid var(--border-color)'
        }}>
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '700', 
            margin: '0 0 12px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <FiStar style={{ color: '#f59e0b' }} />
            AI 분석 요약
          </h3>
          <p style={{ 
            margin: '0', 
            lineHeight: '1.6', 
            color: 'var(--text-primary)',
            fontSize: '14px'
          }}>
            {portfolio.summary}
          </p>
        </div>
      )}

      {/* 키워드 및 기술 스택 */}
      {(portfolio.keywords && portfolio.keywords.length > 0) || (portfolio.basic_info && portfolio.basic_info.position) && (
        <div style={{ 
          background: 'var(--bg-secondary)', 
          borderRadius: '12px', 
          padding: '20px', 
          marginBottom: '24px',
          border: '1px solid var(--border-color)'
        }}>
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '700', 
            margin: '0 0 12px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <FiCode style={{ color: '#3b82f6' }} />
            주요 정보
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {portfolio.keywords && portfolio.keywords.map((keyword, index) => (
              <span key={index} style={{
                background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600',
                boxShadow: '0 2px 4px rgba(59, 130, 246, 0.2)'
              }}>
                {keyword}
              </span>
            ))}
            {portfolio.basic_info && portfolio.basic_info.position && (
              <span style={{
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600',
                boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
              }}>
                {portfolio.basic_info.position}
              </span>
            )}
          </div>
        </div>
      )}

      {/* 포트폴리오 아이템들 */}
      {portfolio.items && portfolio.items.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <h3 style={{ 
            fontSize: '20px', 
            fontWeight: '700', 
            margin: '0 0 16px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <FiUsers style={{ color: '#10b981' }} />
            프로젝트 ({portfolio.items.length}개)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {portfolio.items.map((item, index) => (
              <div key={index} style={{ 
                background: 'var(--bg-secondary)', 
                borderRadius: '16px', 
                padding: '20px',
                border: '1px solid var(--border-color)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <h4 style={{ 
                    fontSize: '18px', 
                    fontWeight: '700', 
                    margin: '0',
                    color: 'var(--text-primary)'
                  }}>
                    {item.title || `프로젝트 ${index + 1}`}
                  </h4>
                  <span style={{
                    background: '#f3f4f6',
                    color: '#374151',
                    padding: '4px 8px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontWeight: '600',
                    textTransform: 'capitalize'
                  }}>
                    {item.type || 'project'}
                  </span>
                </div>
                
                {item.description && (
                  <p style={{ 
                    margin: '0 0 12px 0', 
                    color: 'var(--text-secondary)',
                    lineHeight: '1.5',
                    fontSize: '14px'
                  }}>
                    {item.description}
                  </p>
                )}

                {/* 아티팩트들 */}
                {item.artifacts && item.artifacts.length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      marginBottom: '8px',
                      color: 'var(--text-primary)'
                    }}>
                      관련 링크:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {item.artifacts.map((artifact, artifactIndex) => (
                        <a
                          key={artifactIndex}
                          href={artifact.url || artifact.file_id}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'var(--bg-primary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            padding: '6px 12px',
                            textDecoration: 'none',
                            color: 'var(--text-primary)',
                            fontSize: '12px',
                            fontWeight: '500',
                            transition: 'all 0.2s ease'
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.background = 'var(--bg-hover)';
                            e.target.style.transform = 'translateY(-1px)';
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.background = 'var(--bg-primary)';
                            e.target.style.transform = 'translateY(0)';
                          }}
                        >
                          {artifact.kind === 'repo' ? (
                            <FiGithub size={14} />
                          ) : (
                            <FiExternalLink size={14} />
                          )}
                          {artifact.filename || artifact.kind || '링크'}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 기본 정보 */}
      {portfolio.basic_info && (
        <div style={{ 
          background: 'var(--bg-secondary)', 
          borderRadius: '12px', 
          padding: '20px',
          border: '1px solid var(--border-color)'
        }}>
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '700', 
            margin: '0 0 16px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <FiAward style={{ color: '#8b5cf6' }} />
            추출된 정보
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {portfolio.basic_info.name && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>이름</div>
                <div style={{ fontSize: '14px', fontWeight: '600' }}>
                  {portfolio.basic_info.name}
                </div>
              </div>
            )}
            {portfolio.basic_info.email && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>이메일</div>
                <div style={{ fontSize: '14px', fontWeight: '600' }}>
                  {portfolio.basic_info.email}
                </div>
              </div>
            )}
            {portfolio.basic_info.phone && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>전화번호</div>
                <div style={{ fontSize: '14px', fontWeight: '600' }}>
                  {portfolio.basic_info.phone}
                </div>
              </div>
            )}
            {portfolio.basic_info.position && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>직무</div>
                <div style={{ fontSize: '14px', fontWeight: '600' }}>
                  {portfolio.basic_info.position}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 파일 메타데이터 */}
      {portfolio.file_metadata && (
        <div style={{ 
          background: 'var(--bg-secondary)', 
          borderRadius: '12px', 
          padding: '20px',
          marginTop: '16px',
          border: '1px solid var(--border-color)'
        }}>
          <h3 style={{ 
            fontSize: '16px', 
            fontWeight: '700', 
            margin: '0 0 12px 0',
            color: 'var(--text-secondary)'
          }}>
            파일 정보
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px', fontSize: '12px' }}>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>파일명:</span> {portfolio.file_metadata.filename || 'N/A'}
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>크기:</span> {portfolio.file_metadata.size ? `${(portfolio.file_metadata.size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>타입:</span> {portfolio.file_metadata.mime || 'N/A'}
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>상태:</span> 
              <span style={{ 
                color: portfolio.status === 'active' ? '#10b981' : '#ef4444',
                fontWeight: '600',
                marginLeft: '4px'
              }}>
                {portfolio.status === 'active' ? '활성' : '비활성'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioSummaryPanel;


