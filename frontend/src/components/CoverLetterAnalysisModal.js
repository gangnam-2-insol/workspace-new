import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiEye, FiFileText, FiStar, FiTrendingUp, FiTrendingDown, FiCheck, FiAlertCircle, FiXCircle, FiBarChart2, FiShield } from 'react-icons/fi';
import { useSuspicion } from '../contexts/SuspicionContext';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  max-width: 1200px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  z-index: 10;

  &:hover {
    background: #f5f5f5;
    color: #333;
  }
`;

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 32px 24px 32px;
  border-radius: 16px 16px 0 0;
  position: relative;
  overflow: hidden;
`;

const HeaderBackground = styled.div`
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;

  @keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const Title = styled.h2`
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  position: relative;
  z-index: 1;
`;

const Subtitle = styled.p`
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
  position: relative;
  z-index: 1;
`;

const Content = styled.div`
  padding: 32px;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin: 24px 0 32px 0;
  padding: 32px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  border: 2px solid #dee2e6;
`;

const ScoreCircle = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: ${props => {
    const score = props.score;
    if (score >= 8) return 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
    if (score >= 6) return 'linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%)';
    if (score >= 4) return 'linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)';
    return 'linear-gradient(135deg, #dc3545 0%, #e83e8c 100%)';
  }};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: white;
  border: 4px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

const ScoreInfo = styled.div`
  text-align: left;
`;

const ScoreLabel = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
`;

const ScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #212529;
`;

const ScoreDescription = styled.div`
  font-size: 14px;
  color: #6c757d;
  margin-top: 4px;
`;

const ChartContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin: 24px 0;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
`;

const ChartTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 16px 0;
  text-align: center;
`;

const ChartWrapper = styled.div`
  position: relative;
  max-width: 600px;
  margin: 0 auto;

  canvas {
    display: block !important;
    margin: 0 auto !important;
  }
`;

const ChartDescription = styled.p`
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
`;

const AnalysisGrid = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 32px;
`;

const AnalysisItem = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid ${props => {
    const score = props.score;
    if (score >= 8) return '#28a745';
    if (score >= 6) return '#17a2b8';
    if (score >= 4) return '#ffc107';
    return '#dc3545';
  }};

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
`;

const ItemHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const ItemTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ItemScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

const ScoreNumber = styled.span`
  font-size: 20px;
  color: ${props => {
    const score = props.score;
    if (score >= 8) return '#28a745';
    if (score >= 6) return '#17a2b8';
    if (score >= 4) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreMax = styled.span`
  font-size: 14px;
  color: #6c757d;
`;

const ItemDescription = styled.p`
  font-size: 14px;
  color: #6c757d;
  line-height: 1.6;
  margin: 0;
`;

const StatusIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  background: ${props => {
    const score = props.score;
    if (score >= 8) return '#28a745';
    if (score >= 6) return '#17a2b8';
    if (score >= 4) return '#ffc107';
    return '#dc3545';
  }};
`;

const JsonViewer = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
`;

// 표절 의심도 섹션 스타일
const SuspicionSection = styled(motion.div)`
  margin-top: 32px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
`;

const SuspicionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
`;

const SuspicionTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SuspicionContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SuspicionResult = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: ${props => {
    const level = props.level;
    if (level === 'HIGH') return '#fef2f2';
    if (level === 'MEDIUM') return '#fffbeb';
    return '#f0fdf4';
  }};
  border: 2px solid ${props => {
    const level = props.level;
    if (level === 'HIGH') return '#dc2626';
    if (level === 'MEDIUM') return '#f59e0b';
    return '#16a34a';
  }};
  border-radius: 12px;
`;

const SuspicionLevel = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: ${props => {
    const level = props.level;
    if (level === 'HIGH') return '#dc2626';
    if (level === 'MEDIUM') return '#f59e0b';
    return '#16a34a';
  }};
`;

const SuspicionScore = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #6b7280;
`;

const SuspicionAnalysis = styled.div`
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  font-size: 14px;
  color: #6b7280;
  
  &::before {
    content: '';
    width: 24px;
    height: 24px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
`;

const ToggleButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 16px;

  &:hover {
    background: #5a6268;
  }
`;

const AnalyzeButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 16px;

  &:hover:not(:disabled) {
    background: #5a67d8;
  }

  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
  }
`;

// 자소서 분석 항목 라벨 함수
const getCoverLetterAnalysisLabel = (key) => {
  const labels = {
    motivation_relevance: '지원 동기',
    problem_solving_STAR: 'STAR 기법',
    quantitative_impact: '정량적 성과',
    job_understanding: '직무 이해도',
    unique_experience: '차별화 경험',
    logical_flow: '논리적 흐름',
    keyword_diversity: '키워드 다양성',
    sentence_readability: '문장 가독성',
    typos_and_errors: '오탈자'
  };
  return labels[key] || key;
};

// 점수별 등급 및 설명
const getScoreGrade = (score) => {
  if (score >= 8) return { grade: '우수', color: '#28a745', icon: <FiCheck /> };
  if (score >= 6) return { grade: '양호', color: '#17a2b8', icon: <FiTrendingUp /> };
  if (score >= 4) return { grade: '보통', color: '#ffc107', icon: <FiAlertCircle /> };
  return { grade: '개선필요', color: '#dc3545', icon: <FiXCircle /> };
};

const CoverLetterAnalysisModal = ({
  isOpen,
  onClose,
  analysisData,
  applicantName = '지원자',
  onPerformAnalysis,
  applicantId
}) => {
  const [showJson, setShowJson] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // 전역 표절 의심도 상태
  const { getSuspicionData, getLoadingState } = useSuspicion();

  // 분석 데이터 처리
  const processedData = useMemo(() => {
    if (!analysisData) return null;

    let analysisResult = null;

    // 다양한 데이터 구조 지원
    if (analysisData.analysis_result) {
      analysisResult = analysisData.analysis_result;
    } else if (analysisData.analysis) {
      analysisResult = analysisData.analysis;
    } else if (analysisData.cover_letter_analysis) {
      analysisResult = analysisData.cover_letter_analysis;
    } else {
      analysisResult = analysisData;
    }

    return analysisResult;
  }, [analysisData]);

  // 전체 점수 계산
  const overallScore = useMemo(() => {
    if (!processedData) return 0;

    const scores = Object.values(processedData)
      .filter(item => item && typeof item === 'object' && 'score' in item)
      .map(item => item.score);

    if (scores.length === 0) return 8; // 기본값

    const total = scores.reduce((sum, score) => sum + score, 0);
    return Math.round((total / scores.length) * 10) / 10;
  }, [processedData]);

  // 차트 데이터 생성
  const chartData = useMemo(() => {
    if (!processedData) return null;

    const labels = [];
    const scores = [];
    const colors = [];

    Object.entries(processedData).forEach(([key, value]) => {
      if (value && typeof value === 'object' && 'score' in value) {
        labels.push(getCoverLetterAnalysisLabel(key));
        scores.push(value.score);

        // 점수별 색상
        if (value.score >= 8) colors.push('rgba(40, 167, 69, 0.8)');
        else if (value.score >= 6) colors.push('rgba(23, 162, 184, 0.8)');
        else if (value.score >= 4) colors.push('rgba(255, 193, 7, 0.8)');
        else colors.push('rgba(220, 53, 69, 0.8)');
      }
    });

    return {
      labels,
      datasets: [
        {
          label: '자소서 분석 점수',
          data: scores,
          backgroundColor: colors.map(color => color.replace('0.8', '0.2')),
          borderColor: colors,
          borderWidth: 2,
          pointBackgroundColor: colors,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6,
        },
      ],
    };
  }, [processedData]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 2,
          color: '#666',
        },
        grid: {
          color: '#e9ecef',
        },
        pointLabels: {
          color: '#495057',
          font: {
            size: 12,
            weight: '600',
          },
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#fff',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `점수: ${context.parsed.r}/10`;
          },
        },
      },
    },
  };

  const scoreGrade = getScoreGrade(overallScore);

  // 분석 수행 함수
  const handlePerformAnalysis = async () => {
    if (!onPerformAnalysis || !applicantId) return;

    setIsAnalyzing(true);
    try {
      await onPerformAnalysis(applicantId);
    } catch (error) {
      console.error('자소서 분석 오류:', error);
      alert('자소서 분석에 실패했습니다: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <ModalOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <ModalContent
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>

          <Header>
            <HeaderBackground />
            <Title>자소서 상세 분석</Title>
            <Subtitle>{applicantName}님의 자소서 분석 결과</Subtitle>
          </Header>

          <Content>
            {/* 전체 점수 섹션 */}
            <OverallScore>
              <ScoreCircle score={overallScore}>
                {overallScore}
              </ScoreCircle>
              <ScoreInfo>
                <ScoreLabel>전체 평가 점수</ScoreLabel>
                <ScoreValue>{overallScore}/10점</ScoreValue>
                <ScoreDescription>
                  {scoreGrade.grade} 등급 - {scoreGrade.grade === '우수' ? '매우 우수한 자소서입니다' :
                    scoreGrade.grade === '양호' ? '양호한 자소서입니다' :
                    scoreGrade.grade === '보통' ? '개선이 필요한 부분이 있습니다' :
                    '전반적인 개선이 필요합니다'}
                </ScoreDescription>
              </ScoreInfo>
            </OverallScore>

            {/* 레이더 차트 섹션 */}
            {chartData && (
              <ChartContainer>
                <ChartTitle>9개 평가 항목 분석</ChartTitle>
                <ChartDescription>
                  지원 동기부터 문장 가독성까지 9개 항목을 종합적으로 분석한 결과입니다.
                </ChartDescription>
                <ChartWrapper>
                  <Radar data={chartData} options={chartOptions} height={400} />
                </ChartWrapper>
              </ChartContainer>
            )}

            {/* 상세 분석 항목 */}
            {processedData && (
              <AnalysisGrid
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                {Object.entries(processedData).map(([key, value], index) => {
                  if (!value || typeof value !== 'object' || !('score' in value)) return null;

                  const score = value.score;
                  const grade = getScoreGrade(score);

                  return (
                    <AnalysisItem
                      key={key}
                      score={score}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                    >
                      <ItemHeader>
                        <ItemTitle>
                          {getCoverLetterAnalysisLabel(key)}
                        </ItemTitle>
                        <ItemScore>
                          <ScoreNumber score={score}>{score}</ScoreNumber>
                          <ScoreMax>/10</ScoreMax>
                          <StatusIcon score={score}>
                            {grade.icon}
                          </StatusIcon>
                        </ItemScore>
                      </ItemHeader>
                      <ItemDescription>
                        {value.description || value.reason || '분석 결과가 없습니다.'}
                      </ItemDescription>
                    </AnalysisItem>
                  );
                })}
              </AnalysisGrid>
            )}

            {/* 표절 의심도 분석 결과 섹션 */}
            <SuspicionSection
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <SuspicionHeader>
                <FiShield size={24} color="#3b82f6" />
                <SuspicionTitle>
                  🤖 AI 분석 결과 - 표절 의심도 검사
                </SuspicionTitle>
              </SuspicionHeader>
              
              <SuspicionContent>
                {(() => {
                  const suspicionResult = getSuspicionData(applicantId);
                  const isLoading = getLoadingState(applicantId);
                  
                  // 디버깅 로그 추가
                  console.log('🔍 [CoverLetterAnalysisModal] 표절 의심도 상태 확인:');
                  console.log('- applicantId:', applicantId);
                  console.log('- suspicionResult:', suspicionResult);
                  console.log('- isLoading:', isLoading);
                  
                  if (isLoading) {
                    return (
                      <LoadingSpinner>
                        다른 자소서들과의 표절 의심도를 분석 중입니다...
                      </LoadingSpinner>
                    );
                  }
                  
                  if (!suspicionResult) {
                    return (
                      <div style={{ 
                        padding: '20px', 
                        textAlign: 'center', 
                        color: '#6b7280',
                        backgroundColor: '#f9fafb',
                        borderRadius: '8px',
                        border: '1px dashed #d1d5db'
                      }}>
                        <div style={{ fontSize: '18px', marginBottom: '8px' }}>🔄</div>
                        <div>표절 의심도 검사를 준비 중입니다...</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '8px' }}>
                          자소서 모달을 열면 자동으로 검사가 시작됩니다.
                        </div>
                      </div>
                    );
                  }
                  
                  if (suspicionResult.status === 'error') {
                    return (
                      <ErrorMessage>
                        ❌ {suspicionResult.message}
                      </ErrorMessage>
                    );
                  }
                  
                  // API 응답 구조 파싱
                  let analysisData = suspicionResult;
                  if (suspicionResult.plagiarism_result?.data?.suspicion_analysis) {
                    analysisData = suspicionResult.plagiarism_result.data.suspicion_analysis;
                  } else if (suspicionResult.data?.suspicion_analysis) {
                    analysisData = suspicionResult.data.suspicion_analysis;
                  } else if (suspicionResult.data) {
                    analysisData = suspicionResult.data;
                  }
                  
                  const suspicionLevel = analysisData.suspicion_level || 'UNKNOWN';
                  const suspicionScore = analysisData.suspicion_score_percent || (analysisData.suspicion_score * 100) || 0;
                  const analysis = analysisData.analysis || '분석 결과 없음';
                  const similarCount = analysisData.similar_count || 0;
                  
                  return (
                    <>
                      <SuspicionResult level={suspicionLevel}>
                        <div>
                          <SuspicionLevel level={suspicionLevel}>
                            표절 의심도: {suspicionLevel}
                          </SuspicionLevel>
                          {similarCount > 0 && (
                            <div style={{
                              fontSize: '14px',
                              color: '#dc2626',
                              fontWeight: '600',
                              marginTop: '4px'
                            }}>
                              📋 유사한 자소서 {similarCount}개 발견
                            </div>
                          )}
                        </div>
                        <SuspicionScore>
                          {suspicionScore.toFixed(1)}%
                        </SuspicionScore>
                      </SuspicionResult>
                      
                      <SuspicionAnalysis>
                        <strong>분석 내용:</strong><br />
                        {analysis}
                      </SuspicionAnalysis>
                    </>
                  );
                })()}
              </SuspicionContent>
            </SuspicionSection>

            {/* 분석 수행 버튼 */}
            {onPerformAnalysis && applicantId && (
              <AnalyzeButton
                onClick={handlePerformAnalysis}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <FiTrendingUp />
                    분석 중...
                  </>
                ) : (
                  <>
                    <FiBarChart2 />
                    자소서 분석 수행
                  </>
                )}
              </AnalyzeButton>
            )}

            {/* JSON 원본 데이터 보기 */}
            <ToggleButton onClick={() => setShowJson(!showJson)}>
              <FiEye />
              {showJson ? 'JSON 숨기기' : 'JSON 원본 데이터 보기'}
            </ToggleButton>

            {showJson && (
              <JsonViewer>
                <pre>{JSON.stringify(analysisData, null, 2)}</pre>
              </JsonViewer>
            )}
          </Content>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default CoverLetterAnalysisModal;

