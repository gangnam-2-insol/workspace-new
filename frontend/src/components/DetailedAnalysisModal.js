import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck, FiAlertCircle, FiStar, FiTrendingUp, FiTrendingDown, FiFileText, FiMessageSquare, FiCode } from 'react-icons/fi';

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
  border-radius: 12px;
  padding: 32px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;

  &:hover {
    background: #f5f5f5;
    color: #333;
  }
`;

const Header = styled.div`
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 14px;
  color: #666;
  margin: 0;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
`;

const ScoreCircle = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
`;

const ScoreInfo = styled.div`
  flex: 1;
`;

const ScoreLabel = styled.div`
  font-size: 14px;
  opacity: 0.9;
`;

const OverallScoreValue = styled.div`
  font-size: 24px;
  font-weight: 700;
`;

const AnalysisSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ScoreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
`;

const ScoreCard = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const ScoreName = styled.div`
  font-weight: 600;
  color: #333;
  font-size: 14px;
`;

const ScoreValue = styled.div`
  font-weight: 700;
  color: ${props => {
    if (props.score >= 8) return '#28a745';
    if (props.score >= 6) return '#ffc107';
    return '#dc3545';
  }};
  font-size: 16px;
`;

const ScoreFeedback = styled.div`
  font-size: 13px;
  color: #666;
  line-height: 1.4;
`;

const RecommendationSection = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 24px;
`;

const RecommendationTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RecommendationList = styled.ul`
  margin: 0;
  padding-left: 20px;
`;

const RecommendationItem = styled.li`
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  line-height: 1.5;
`;

const getScoreIcon = (score) => {
  if (score >= 8) return <FiCheck color="#28a745" />;
  if (score >= 6) return <FiAlertCircle color="#ffc107" />;
  return <FiX color="#dc3545" />;
};

const getScoreColor = (score) => {
  if (score >= 8) return '#28a745';
  if (score >= 6) return '#ffc107';
  return '#dc3545';
};

const DetailedAnalysisModal = ({ isOpen, onClose, analysisData }) => {
  if (!isOpen || !analysisData) return null;

  const { detailedAnalysis } = analysisData;
  
  if (!detailedAnalysis) {
    return (
      <AnimatePresence>
        {isOpen && (
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
              <CloseButton onClick={onClose}>×</CloseButton>
              <Header>
                <Title>상세 분석 결과</Title>
                <Subtitle>분석 데이터를 찾을 수 없습니다.</Subtitle>
              </Header>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>
    );
  }

  const renderAnalysisSection = (title, data, icon) => {
    if (!data) return null;

    return (
      <AnalysisSection>
        <SectionTitle>
          {icon} {title}
        </SectionTitle>
        <ScoreGrid>
          {Object.entries(data).map(([key, value]) => (
            <ScoreCard key={key} score={value.score}>
              <ScoreHeader>
                <ScoreName>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</ScoreName>
                <ScoreValue score={value.score}>
                  {value.score}/10 {getScoreIcon(value.score)}
                </ScoreValue>
              </ScoreHeader>
              <ScoreFeedback>{value.feedback}</ScoreFeedback>
            </ScoreCard>
          ))}
        </ScoreGrid>
      </AnalysisSection>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
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
            <CloseButton onClick={onClose}>×</CloseButton>
            
            <Header>
              <Title>AI 상세 분석 결과</Title>
              <Subtitle>{analysisData.fileName} - {analysisData.analysisDate}</Subtitle>
            </Header>

            {(() => {
              const overall = (detailedAnalysis && detailedAnalysis.overall_summary) || { total_score: 0 };
              const total = typeof overall.total_score === 'number' ? overall.total_score : 0;
              return (
                <OverallScore>
                  <ScoreCircle>
                    {total}
                  </ScoreCircle>
                  <ScoreInfo>
                    <ScoreLabel>전체 평가 점수</ScoreLabel>
                    <ScoreValue>{total}/10</ScoreValue>
                  </ScoreInfo>
                </OverallScore>
              );
            })()}

            {/* 문서 타입에 따라 해당하는 분석 결과만 표시 */}
            {detailedAnalysis.resume_analysis && Object.keys(detailedAnalysis.resume_analysis).length > 0 && 
              renderAnalysisSection('이력서 분석', detailedAnalysis.resume_analysis, <FiFileText />)}
            {detailedAnalysis.cover_letter_analysis && Object.keys(detailedAnalysis.cover_letter_analysis).length > 0 && 
              renderAnalysisSection('자기소개서 분석', detailedAnalysis.cover_letter_analysis, <FiMessageSquare />)}
            {detailedAnalysis.portfolio_analysis && Object.keys(detailedAnalysis.portfolio_analysis).length > 0 && 
              renderAnalysisSection('포트폴리오 분석', detailedAnalysis.portfolio_analysis, <FiCode />)}

            <RecommendationSection>
              <RecommendationTitle>
                <FiStar /> 선택한 항목 요약
              </RecommendationTitle>
              <RecommendationList>
                {(() => {
                  // 문서 타입에 따라 다른 요약 내용 표시
                  if (detailedAnalysis.resume_analysis && Object.keys(detailedAnalysis.resume_analysis).length > 0) {
                    return (
                      <RecommendationItem>
                        이력서 분석 결과: 총 {Object.keys(detailedAnalysis.resume_analysis).length}개 항목을 분석했습니다. 
                        평균 점수는 {detailedAnalysis.overall_summary.total_score}/10점이며, 
                        {detailedAnalysis.overall_summary.total_score >= 8 ? '전반적으로 우수한 수준' : 
                         detailedAnalysis.overall_summary.total_score >= 6 ? '양호한 수준이지만 개선점이 있음' : 
                         '전반적인 개선이 필요함'}입니다.
                      </RecommendationItem>
                    );
                  } else if (detailedAnalysis.cover_letter_analysis && Object.keys(detailedAnalysis.cover_letter_analysis).length > 0) {
                    return (
                      <RecommendationItem>
                        자기소개서 분석 결과: 총 {Object.keys(detailedAnalysis.cover_letter_analysis).length}개 항목을 분석했습니다. 
                        평균 점수는 {detailedAnalysis.overall_summary.total_score}/10점이며, 
                        {detailedAnalysis.overall_summary.total_score >= 8 ? '매우 우수한 수준' : 
                         detailedAnalysis.overall_summary.total_score >= 6 ? '양호한 수준이지만 개선점이 있음' : 
                         '전반적인 개선이 필요함'}입니다.
                      </RecommendationItem>
                    );
                  } else if (detailedAnalysis.portfolio_analysis && Object.keys(detailedAnalysis.portfolio_analysis).length > 0) {
                    return (
                      <RecommendationItem>
                        포트폴리오 분석 결과: 총 {Object.keys(detailedAnalysis.portfolio_analysis).length}개 항목을 분석했습니다. 
                        평균 점수는 {detailedAnalysis.overall_summary.total_score}/10점이며, 
                        {detailedAnalysis.overall_summary.total_score >= 8 ? '매우 우수한 수준' : 
                         detailedAnalysis.overall_summary.total_score >= 6 ? '양호한 수준이지만 개선점이 있음' : 
                         '전반적인 개선이 필요함'}입니다.
                      </RecommendationItem>
                    );
                  } else {
                    return (
                      <RecommendationItem>
                        문서 분석이 완료되었습니다. 분석 결과를 확인하세요.
                      </RecommendationItem>
                    );
                  }
                })()}
              </RecommendationList>
            </RecommendationSection>
          </ModalContent>
        </ModalOverlay>
      )}
    </AnimatePresence>
  );
};

export default DetailedAnalysisModal;
