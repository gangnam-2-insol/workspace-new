import React, { useState, useMemo } from 'react';
import styled from 'styled-components';
import { FiX, FiFileText, FiTrendingUp, FiCheckCircle, FiAlertCircle, FiXCircle } from 'react-icons/fi';
import CoverLetterAnalysis from './CoverLetterAnalysis';

const ModalOverlay = styled.div`
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

const ModalContent = styled.div`
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
`;

const ModalHeader = styled.div`
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;

  &:hover {
    background: #f3f4f6;
    color: #374151;
  }
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const ScoreSection = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  color: white;
`;

const ScoreTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  opacity: 0.9;
`;

const ScoreValue = styled.div`
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
`;

const ScoreSubtitle = styled.div`
  font-size: 14px;
  opacity: 0.8;
`;

const getScoreGrade = (score) => {
  if (score >= 8) return { label: '우수', color: '#16a34a', icon: <FiCheckCircle /> };
  if (score >= 6) return { label: '양호', color: '#f59e0b', icon: <FiTrendingUp /> };
  if (score >= 4) return { label: '보통', color: '#f97316', icon: <FiAlertCircle /> };
  return { label: '개선필요', color: '#dc2626', icon: <FiXCircle /> };
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

    if (scores.length === 0) return 0;

    const total = scores.reduce((sum, score) => sum + score, 0);
    return Math.round((total / scores.length) * 10) / 10;
  }, [processedData]);

  const scoreGrade = getScoreGrade(overallScore);

  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={(e) => e.target === e.currentTarget && onClose()}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>
            <FiFileText />
            {applicantName}님의 자소서 분석 결과
          </ModalTitle>
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>
        </ModalHeader>

        <ModalBody>
          {processedData ? (
            <>
              {/* 점수 섹션 */}
              <ScoreSection>
                <ScoreTitle>종합 점수</ScoreTitle>
                <ScoreValue>{Math.round(overallScore * 10)}점</ScoreValue>
                <ScoreSubtitle>
                  {scoreGrade.icon} {scoreGrade.label} 수준
                </ScoreSubtitle>
              </ScoreSection>

              {/* 분석 결과 */}
              <CoverLetterAnalysis
                analysisData={analysisData}
                applicant={{ name: applicantName, id: applicantId }}
              />

              {/* JSON 데이터 보기 (개발용) */}
              {process.env.NODE_ENV === 'development' && (
                <div style={{ marginTop: '24px' }}>
                  <button
                    onClick={() => setShowJson(!showJson)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#f3f4f6',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {showJson ? 'JSON 숨기기' : 'JSON 보기'}
                  </button>

                  {showJson && (
                    <pre style={{
                      marginTop: '12px',
                      padding: '16px',
                      backgroundColor: '#f9fafb',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                      fontSize: '12px',
                      overflow: 'auto',
                      maxHeight: '300px'
                    }}>
                      {JSON.stringify(analysisData, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
              <FiFileText size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
              <p>분석 데이터가 없습니다.</p>
              {onPerformAnalysis && (
                <button
                  onClick={onPerformAnalysis}
                  style={{
                    marginTop: '16px',
                    padding: '12px 24px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  분석 시작하기
                </button>
              )}
            </div>
          )}
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default CoverLetterAnalysisModal;
