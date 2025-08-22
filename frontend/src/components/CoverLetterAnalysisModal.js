import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiEye, FiFileText, FiStar, FiTrendingUp, FiTrendingDown } from 'react-icons/fi';
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
  max-width: 1000px;
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

const OverallScore = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 24px 0 32px 0;
  padding: 32px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  border: 2px solid #e9ecef;
`;

const ScoreCircle = styled(motion.div)`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: white;
  border: 4px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
`;

const ScoreInfo = styled.div`
  text-align: left;
`;

const ScoreLabel = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
`;

const ScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
`;

const RadarChartSection = styled(motion.div)`
  margin: 32px 0;
`;

const SectionTitle = styled.h3`
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 3px solid #667eea;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ChartContainer = styled.div`
  background: #f8f9fa;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e9ecef;
  margin-bottom: 24px;
`;

const ChartWrapper = styled.div`
  height: 500px;
  position: relative;
  margin: 20px 0;
`;

const ChartDescription = styled.p`
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
`;

const AnalysisGrid = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  border-left: 4px solid #667eea;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }

  &.excellent {
    border-left-color: #28a745;
  }

  &.good {
    border-left-color: #17a2b8;
  }

  &.average {
    border-left-color: #ffc107;
  }

  &.poor {
    border-left-color: #dc3545;
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
  color: #28a745;
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
  background: #28a745;

  &.excellent {
    background: #28a745;
  }

  &.good {
    background: #17a2b8;
  }

  &.average {
    background: #ffc107;
    color: #212529;
  }

  &.poor {
    background: #dc3545;
  }
`;

const CoverLetterAnalysisModal = ({ isOpen, onClose, coverLetterData, analysisData }) => {
  const [chartData, setChartData] = useState(null);
  const [isChartReady, setIsChartReady] = useState(false);

  useEffect(() => {
    if (isOpen && analysisData) {
      // 차트 데이터 준비
      prepareChartData();
      // 차트 애니메이션을 위한 지연
      setTimeout(() => setIsChartReady(true), 500);
    } else {
      setIsChartReady(false);
    }
  }, [isOpen, analysisData]);

  const prepareChartData = () => {
    if (!analysisData) return;

    const coverLetterAnalysis = analysisData.cover_letter_analysis || {};
    
    // 9개 평가 항목 데이터 구성
    const chartData = {
      labels: [
        '직무 적합성 (Job Fit)',
        '기술 스택 일치 여부',
        '경험한 프로젝트 관련성',
        '핵심 기술 역량 (Tech Competency)',
        '경력 및 성과 (Experience & Impact)',
        '문제 해결 능력 (Problem-Solving)',
        '커뮤니케이션/협업 (Collaboration)',
        '성장 가능성/학습 능력 (Growth Potential)',
        '자소서 표현력/논리성 (Clarity & Grammar)'
      ],
      datasets: [
        {
          label: '자소서 분석 점수',
          data: [
            coverLetterAnalysis.motivation_relevance?.score || 75,
            coverLetterAnalysis.job_understanding?.score || 75,
            coverLetterAnalysis.unique_experience?.score || 75,
            coverLetterAnalysis.quantitative_impact?.score || 75,
            coverLetterAnalysis.problem_solving_STAR?.score || 75,
            coverLetterAnalysis.logical_flow?.score || 75,
            coverLetterAnalysis.keyword_diversity?.score || 75,
            coverLetterAnalysis.sentence_readability?.score || 75,
            coverLetterAnalysis.typos_and_errors?.score || 75
          ],
          backgroundColor: 'rgba(102, 126, 234, 0.2)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 3,
          pointBackgroundColor: 'rgba(102, 126, 234, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(102, 126, 234, 1)',
          pointRadius: 6,
          pointHoverRadius: 8,
          fill: true,
        },
      ],
    };

    setChartData(chartData);
  };

  const getScoreStatus = (score) => {
    if (score >= 85) return { status: 'excellent', icon: '⭐' };
    if (score >= 70) return { status: 'good', icon: '✓' };
    if (score >= 55) return { status: 'average', icon: '⚠️' };
    return { status: 'poor', icon: '❌' };
  };

  const getOverallScore = () => {
    if (!analysisData?.cover_letter_analysis) return 75;
    
    const scores = Object.values(analysisData.cover_letter_analysis)
      .filter(item => item && typeof item === 'object' && 'score' in item)
      .map(item => item.score);
    
    if (scores.length === 0) return 75;
    
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    return Math.round(average);
  };

  const overallScore = getOverallScore();

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        min: 0,
        ticks: {
          stepSize: 20,
          color: '#666',
          font: {
            size: 12,
          },
          callback: function(value) {
            return value + '점';
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        pointLabels: {
          color: '#333',
          font: {
            size: 11,
            weight: 'bold',
          },
          callback: function(value, index) {
            const words = value.split(' ');
            if (words.length > 4) {
              return words.slice(0, 3).join(' ') + '\n' + words.slice(3).join(' ');
            } else if (words.length > 2) {
              const mid = Math.ceil(words.length / 2);
              return words.slice(0, mid).join(' ') + '\n' + words.slice(mid).join(' ');
            }
            return value;
          }
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          title: function(context) {
            return context[0].label;
          },
          label: function(context) {
            return `점수: ${context.parsed.r}점`;
          },
          afterLabel: function(context) {
            const descriptions = [
              '지원 직무와의 연관성 및 적합성',
              'JD에 명시된 기술과 이력서 기술 스택 일치도',
              '경험한 프로젝트가 지원 포지션과의 관련성',
              '프로그래밍 언어, 프레임워크, DB 등 기술 역량',
              '단순 참여 vs 주도적 역할, 수치화된 성과',
              '문제 상황 → 해결 과정 → 성과 구조',
              '팀 프로젝트 경험, 협업 도구 사용 경험',
              '새로운 기술 학습/적용, 꾸준한 학습 습관',
              '글의 흐름, 논리적 전개, 맞춤법/문법'
            ];
            return descriptions[context.dataIndex] || '';
          }
        }
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'r',
      intersect: false
    },
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
          onClick={(e) => e.stopPropagation()}
          initial={{ scale: 0.9, opacity: 0, y: 50 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 50 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>

          <Header>
            <HeaderBackground />
            <Title>자기소개서 상세 분석</Title>
            <Subtitle>
              AI 기반 종합 평가 • {coverLetterData?.filename || '자기소개서'} 분석 결과
            </Subtitle>
          </Header>

          <Content>
            {/* 전체 점수 */}
            <OverallScore
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <ScoreCircle
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.4, duration: 0.6, type: "spring", stiffness: 200 }}
              >
                {overallScore}
              </ScoreCircle>
              <ScoreInfo>
                <ScoreLabel>자기소개서 종합 점수</ScoreLabel>
                <ScoreValue>{overallScore}/100점</ScoreValue>
              </ScoreInfo>
            </OverallScore>

            {/* 레이더 차트 */}
            <RadarChartSection
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <SectionTitle>
                <FiStar />
                9개 평가 항목 레이더 차트
              </SectionTitle>
              
              <ChartContainer>
                <ChartDescription>
                  각 항목을 클릭하면 상세 설명을 확인할 수 있습니다
                </ChartDescription>
                
                <ChartWrapper>
                  {chartData && isChartReady && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.8, duration: 0.6 }}
                    >
                      <Radar data={chartData} options={chartOptions} />
                    </motion.div>
                  )}
                </ChartWrapper>
              </ChartContainer>
            </RadarChartSection>

            {/* 상세 분석 항목들 */}
            <AnalysisGrid
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.0, duration: 0.5 }}
            >
              {chartData?.labels.map((label, index) => {
                const score = chartData.datasets[0].data[index];
                const { status, icon } = getScoreStatus(score);
                
                return (
                  <AnalysisItem
                    key={index}
                    className={status}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2 + index * 0.1, duration: 0.4 }}
                  >
                    <ItemHeader>
                      <ItemTitle>
                        {icon} {label}
                      </ItemTitle>
                      <ItemScore>
                        <ScoreNumber>{score}</ScoreNumber>
                        <ScoreMax>/100</ScoreMax>
                        <StatusIcon className={status}>
                          {status === 'excellent' ? '⭐' : 
                           status === 'good' ? '✓' : 
                           status === 'average' ? '⚠️' : '❌'}
                        </StatusIcon>
                      </ItemScore>
                    </ItemHeader>
                    <ItemDescription>
                      {getScoreDescription(label, score)}
                    </ItemDescription>
                  </AnalysisItem>
                );
              })}
            </AnalysisGrid>
          </Content>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

// 점수별 설명 함수
const getScoreDescription = (label, score) => {
  const descriptions = {
    '직무 적합성 (Job Fit)': '지원 직무와의 연관성 및 적합성을 평가합니다.',
    '기술 스택 일치 여부': 'JD에 명시된 기술과 이력서 기술 스택의 일치도를 분석합니다.',
    '경험한 프로젝트 관련성': '경험한 프로젝트가 지원 포지션과 얼마나 관련 있는지 평가합니다.',
    '핵심 기술 역량 (Tech Competency)': '프로그래밍 언어, 프레임워크, DB 등 기술 역량을 분석합니다.',
    '경력 및 성과 (Experience & Impact)': '주도적 역할과 수치화된 성과 제시 여부를 평가합니다.',
    '문제 해결 능력 (Problem-Solving)': '문제 상황 → 해결 과정 → 성과 구조를 분석합니다.',
    '커뮤니케이션/협업 (Collaboration)': '팀 프로젝트 경험과 협업 도구 사용 경험을 평가합니다.',
    '성장 가능성/학습 능력 (Growth Potential)': '새로운 기술 학습과 적응력을 분석합니다.',
    '자소서 표현력/논리성 (Clarity & Grammar)': '글의 품질과 논리적 구성을 평가합니다.'
  };
  
  return descriptions[label] || `${label}에 대한 상세 분석 결과입니다.`;
};

export default CoverLetterAnalysisModal;

