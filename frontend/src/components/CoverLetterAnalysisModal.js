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
  position: fixed;
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
  z-index: 3010;

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

  // 🔍 디버깅: 컴포넌트 마운트/업데이트 로그
  console.log('🚀 [CoverLetterAnalysisModal] 컴포넌트 렌더링:', {
    isOpen,
    applicantName,
    applicantId,
    hasAnalysisData: !!analysisData,
    analysisDataType: typeof analysisData,
    analysisDataKeys: analysisData ? Object.keys(analysisData) : [],
    timestamp: new Date().toISOString()
  });

  // 🔍 디버깅: props 변경 감지
  useEffect(() => {
    console.log('🔄 [CoverLetterAnalysisModal] Props 변경 감지:', {
      isOpen,
      applicantName,
      applicantId,
      analysisDataChanged: !!analysisData,
      analysisDataStructure: analysisData ? {
        keys: Object.keys(analysisData),
        hasAnalysisResult: 'analysis_result' in analysisData,
        hasAnalysis: 'analysis' in analysisData,
        hasCoverLetterAnalysis: 'cover_letter_analysis' in analysisData
      } : null
    });
  }, [isOpen, applicantName, applicantId, analysisData]);

  // 분석 데이터 처리
  const processedData = useMemo(() => {
    console.log('🔍 [CoverLetterAnalysisModal] processedData 계산 시작:', {
      hasAnalysisData: !!analysisData,
      analysisDataStructure: analysisData ? Object.keys(analysisData) : [],
      timestamp: new Date().toISOString()
    });

    if (!analysisData) {
      console.log('❌ [CoverLetterAnalysisModal] analysisData가 없음');
      return null;
    }

    let analysisResult = null;

    // 🔍 디버깅: 데이터 구조 분석
    console.log('🔍 [CoverLetterAnalysisModal] 원본 데이터 구조 분석:', {
      hasAnalysisResult: 'analysis_result' in analysisData,
      hasAnalysis: 'analysis' in analysisData,
      hasCoverLetterAnalysis: 'cover_letter_analysis' in analysisData,
      isDirectAnalysis: typeof analysisData === 'object' && !('analysis_result' in analysisData) && !('analysis' in analysisData) && !('cover_letter_analysis' in analysisData),
      allKeys: Object.keys(analysisData),
      dataSize: JSON.stringify(analysisData).length
    });

    // 다양한 데이터 구조 지원
    if (analysisData.analysis_result) {
      analysisResult = analysisData.analysis_result;
      console.log('✅ [CoverLetterAnalysisModal] analysis_result 사용');
    } else if (analysisData.analysis) {
      analysisResult = analysisData.analysis;
      console.log('✅ [CoverLetterAnalysisModal] analysis 사용');
    } else if (analysisData.cover_letter_analysis) {
      analysisResult = analysisData.cover_letter_analysis;
      console.log('✅ [CoverLetterAnalysisModal] cover_letter_analysis 사용');
    } else {
      analysisResult = analysisData;
      console.log('✅ [CoverLetterAnalysisModal] 직접 데이터 사용');
    }

    // 자기소개서 분석 결과 디버깅
    if (analysisResult) {
      console.log('📊 [자기소개서 분석 데이터 처리]:', {
        원본구조: Object.keys(analysisData),
        처리된구조: Object.keys(analysisResult),
        데이터크기: JSON.stringify(analysisResult).length,
        점수필드수: Object.keys(analysisResult).filter(key => key.includes('score')).length,
        분석항목수: Object.keys(analysisResult).length,
        전체데이터샘플: JSON.stringify(analysisResult).substring(0, 200) + '...'
      });

      // 각 분석 항목별 상세 정보
      Object.entries(analysisResult).forEach(([key, value]) => {
        if (value && typeof value === 'object' && 'score' in value) {
          console.log(`  📋 ${key}: 점수 ${value.score}, 피드백 ${value.feedback?.length || 0}자, 설명 ${value.description?.length || 0}자`);
        } else if (value && typeof value === 'object') {
          console.log(`  📋 ${key}: 객체 (score 없음) - ${Object.keys(value).join(', ')}`);
        } else {
          console.log(`  📋 ${key}: ${typeof value} - ${value}`);
        }
      });
    } else {
      console.log('❌ [CoverLetterAnalysisModal] analysisResult가 null');
    }

    console.log('✅ [CoverLetterAnalysisModal] processedData 계산 완료:', {
      hasProcessedData: !!processedData,
      processedDataKeys: processedData ? Object.keys(processedData) : []
    });

    return analysisResult;
  }, [analysisData]);

  // 전체 점수 계산
  const overallScore = useMemo(() => {
    if (!processedData) return 0;

    const scores = Object.values(processedData)
      .filter(item => item && typeof item === 'object' && 'score' in item)
      .map(item => item.score);

    // 점수 계산 디버깅
    console.log('🧮 [점수 계산]:', {
      추출된점수들: scores,
      점수개수: scores.length,
      평균점수: scores.length > 0 ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(2) : 'N/A'
    });

    if (scores.length === 0) {
      console.log('⚠️ [점수 계산] 점수 데이터가 없어 기본값 8점 사용');
      return 8; // 기본값
    }

    const total = scores.reduce((sum, score) => sum + score, 0);
    const finalScore = Math.round((total / scores.length) * 10) / 10;

    console.log('✅ [CoverLetterAnalysisModal] 최종 점수 계산 완료:', {
      총합: total,
      점수개수: scores.length,
      평균: total / scores.length,
      최종점수: finalScore
    });

    return finalScore;
  }, [processedData]);

  // 차트 데이터 생성
  const chartData = useMemo(() => {
    console.log('🔍 [CoverLetterAnalysisModal] 차트 데이터 생성 시작:', {
      hasProcessedData: !!processedData,
      processedDataKeys: processedData ? Object.keys(processedData) : []
    });

    if (!processedData) {
      console.log('❌ [CoverLetterAnalysisModal] processedData가 없어서 차트 데이터 null 반환');
      return null;
    }

    const labels = [];
    const scores = [];
    const colors = [];
    const chartDetails = [];

    Object.entries(processedData).forEach(([key, value]) => {
      console.log(`🔍 [CoverLetterAnalysisModal] 차트용 ${key} 항목 분석:`, {
        hasScore: value && typeof value === 'object' && 'score' in value,
        score: value && typeof value === 'object' && 'score' in value ? value.score : 'N/A',
        label: getCoverLetterAnalysisLabel(key)
      });

      if (value && typeof value === 'object' && 'score' in value) {
        const label = getCoverLetterAnalysisLabel(key);
        const score = value.score;

        labels.push(label);
        scores.push(score);

        // 점수별 색상
        let color;
        if (score >= 8) color = 'rgba(40, 167, 69, 0.8)';
        else if (score >= 6) color = 'rgba(23, 162, 184, 0.8)';
        else if (score >= 4) color = 'rgba(255, 193, 7, 0.8)';
        else color = 'rgba(220, 53, 69, 0.8)';

        colors.push(color);
        chartDetails.push({ key, label, score, color });
        console.log(`  ✅ 차트에 추가: ${label} - ${score}점 (${color})`);
      } else {
        console.log(`  ❌ 차트에서 제외: ${key} (점수 없음)`);
      }
    });

    const chartResult = {
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

    console.log('✅ [CoverLetterAnalysisModal] 차트 데이터 생성 완료:', {
      라벨개수: labels.length,
      점수개수: scores.length,
      색상개수: colors.length,
      차트상세: chartDetails,
      차트구조: {
        labels: labels,
        scores: scores,
        colors: colors
      }
    });

    return chartResult;
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
    console.log('🔍 [CoverLetterAnalysisModal] 분석 수행 함수 호출:', {
      hasOnPerformAnalysis: !!onPerformAnalysis,
      applicantId,
      isAnalyzing,
      timestamp: new Date().toISOString()
    });

    if (!onPerformAnalysis || !applicantId) {
      console.log('❌ [CoverLetterAnalysisModal] 분석 수행 불가:', {
        hasOnPerformAnalysis: !!onPerformAnalysis,
        hasApplicantId: !!applicantId
      });
      return;
    }

    console.log('🚀 [CoverLetterAnalysisModal] 분석 시작:', {
      applicantId,
      applicantName
    });

    setIsAnalyzing(true);
    try {
      await onPerformAnalysis(applicantId);
      console.log('✅ [CoverLetterAnalysisModal] 분석 완료:', {
        applicantId,
        applicantName
      });
    } catch (error) {
      console.error('❌ [CoverLetterAnalysisModal] 자소서 분석 오류:', {
        error: error.message,
        stack: error.stack,
        applicantId,
        applicantName
      });
      alert('자소서 분석에 실패했습니다: ' + error.message);
    } finally {
      setIsAnalyzing(false);
      console.log('🏁 [CoverLetterAnalysisModal] 분석 프로세스 종료:', {
        applicantId,
        applicantName
      });
    }
  };

  if (!isOpen) {
    console.log('❌ [CoverLetterAnalysisModal] 모달이 닫혀있어서 렌더링하지 않음');
    return null;
  }

  console.log('🎨 [CoverLetterAnalysisModal] 모달 렌더링 시작:', {
    isOpen,
    applicantName,
    applicantId,
    hasProcessedData: !!processedData,
    overallScore,
    hasChartData: !!chartData,
    isAnalyzing,
    timestamp: new Date().toISOString()
  });

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
            <Title>자소서 표절 의심도 검사</Title>
            <Subtitle>{applicantName}님의 자소서 표절 의심도 결과</Subtitle>
          </Header>

          <Content>

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

                  if (isLoading || !suspicionResult) {
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
                    // 자소서가 없는 경우에 대한 특별한 UI
                    if (suspicionResult.isNoCoverLetter) {
                      return (
                        <div style={{
                          padding: '24px',
                          textAlign: 'center',
                          backgroundColor: '#fef3c7',
                          border: '2px solid #f59e0b',
                          borderRadius: '12px',
                          color: '#92400e'
                        }}>
                          <div style={{ fontSize: '32px', marginBottom: '16px' }}>📝</div>
                          <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                            자소서가 등록되지 않았습니다
                          </div>
                          <div style={{ fontSize: '14px', marginBottom: '16px' }}>
                            {suspicionResult.message}
                          </div>
                          <div style={{
                            fontSize: '12px',
                            color: '#a16207',
                            backgroundColor: '#fef3c7',
                            padding: '8px 12px',
                            borderRadius: '6px',
                            border: '1px solid #f59e0b'
                          }}>
                            💡 자소서를 먼저 업로드한 후 표절 의심도 검사를 진행해주세요.
                          </div>
                        </div>
                      );
                    }

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
          </Content>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default CoverLetterAnalysisModal;

