import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiPlay, FiRefreshCw, FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi';
import {
  analyzeResume,
  reanalyzeResume,
  generateAnalysisSummary,
  calculateScoreGrade
} from '../../services/aiAnalysisApi';

const AIAnalysisModal = ({
  isOpen,
  applicant,
  onClose,
  onAnalysisComplete
}) => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisType, setAnalysisType] = useState('openai');
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (isOpen && applicant) {
      // 기존 분석 결과가 있는지 확인
      if (applicant.ai_analysis) {
        setAnalysisResult(applicant.ai_analysis);
        setSummary(generateAnalysisSummary(applicant.ai_analysis));
      }
    }
  }, [isOpen, applicant]);

  const handleAnalyze = async () => {
    if (!applicant) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeResume(applicant.id, analysisType, false);
      setAnalysisResult(result);
      setSummary(generateAnalysisSummary(result));

      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReanalyze = async () => {
    if (!applicant) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await reanalyzeResume(applicant.id, analysisType);
      setAnalysisResult(result);
      setSummary(generateAnalysisSummary(result));

      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderScoreCard = (title, score, grade) => (
    <ScoreCard key={title}>
      <ScoreHeader>
        <ScoreTitle>{title}</ScoreTitle>
        <ScoreValue score={score}>{score}</ScoreValue>
      </ScoreHeader>
      <ScoreGrade grade={grade}>
        {grade.icon} {grade.label}
      </ScoreGrade>
    </ScoreCard>
  );

  const renderFeedbackSection = (title, items, type = 'default') => (
    <FeedbackSection>
      <FeedbackTitle>{title}</FeedbackTitle>
      <FeedbackList type={type}>
        {items.map((item, index) => (
          <FeedbackItem key={index} type={type}>
            {type === 'strengths' ? '✅' : type === 'improvements' ? '⚠️' : '💡'} {item}
          </FeedbackItem>
        ))}
      </FeedbackList>
    </FeedbackSection>
  );

  if (!isOpen || !applicant) return null;

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
          <ModalHeader>
            <ModalTitle>
              🤖 AI 이력서 분석 결과
            </ModalTitle>
            <CloseButton onClick={onClose}>
              <FiX />
            </CloseButton>
          </ModalHeader>

          <ModalBody>
            {/* 지원자 정보 */}
            <ApplicantInfo>
              <ApplicantName>{applicant.name}</ApplicantName>
              <ApplicantDetails>
                {applicant.position} • {applicant.department}
              </ApplicantDetails>
            </ApplicantInfo>

            {/* 분석 컨트롤 */}
            <AnalysisControls>
              <AnalysisTypeSelect
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value)}
                disabled={isAnalyzing}
              >
                <option value="openai">OpenAI GPT-4o-mini</option>
                <option value="huggingface">HuggingFace (로컬)</option>
              </AnalysisTypeSelect>

              <ControlButtons>
                {!analysisResult ? (
                  <AnalyzeButton onClick={handleAnalyze} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <>
                        <FiRefreshCw className="spinning" />
                        분석 중...
                      </>
                    ) : (
                      <>
                        <FiPlay />
                        분석 시작
                      </>
                    )}
                  </AnalyzeButton>
                ) : (
                  <ReanalyzeButton onClick={handleReanalyze} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <>
                        <FiRefreshCw className="spinning" />
                        재분석 중...
                      </>
                    ) : (
                      <>
                        <FiRefreshCw />
                        재분석
                      </>
                    )}
                  </ReanalyzeButton>
                )}
              </ControlButtons>
            </AnalysisControls>

            {/* 에러 메시지 */}
            {error && (
              <ErrorMessage>
                ❌ {error}
              </ErrorMessage>
            )}

            {/* 분석 결과 */}
            {summary && (
              <AnalysisResults>
                {/* 전체 점수 */}
                <OverallScore>
                  <OverallScoreCircle grade={summary.overall.grade}>
                    {summary.overall.score}
                  </OverallScoreCircle>
                  <OverallScoreInfo>
                    <OverallScoreLabel>전체 평가 점수</OverallScoreLabel>
                    <OverallScoreGrade>
                      {summary.overall.grade.icon} {summary.overall.grade.label} 등급
                    </OverallScoreGrade>
                  </OverallScoreInfo>
                </OverallScore>

                {/* 카테고리별 점수 */}
                <ScoreGrid>
                  {renderScoreCard('학력/전공', summary.categories.education.score, summary.categories.education.grade)}
                  {renderScoreCard('경력/경험', summary.categories.experience.score, summary.categories.experience.grade)}
                  {renderScoreCard('기술/역량', summary.categories.skills.score, summary.categories.skills.grade)}
                  {renderScoreCard('프로젝트/성과', summary.categories.projects.score, summary.categories.projects.grade)}
                  {renderScoreCard('성장/발전', summary.categories.growth.score, summary.categories.growth.grade)}

                  {/* 추가 점수 (HuggingFace 분석기인 경우) */}
                  {summary.additional.grammar && renderScoreCard('문법/표현', summary.additional.grammar.score, summary.additional.grammar.grade)}
                  {summary.additional.jobMatching && renderScoreCard('직무 적합성', summary.additional.jobMatching.score, summary.additional.jobMatching.grade)}
                </ScoreGrid>

                {/* 종합 피드백 */}
                <OverallFeedback>
                  <FeedbackTitle>📝 종합 피드백</FeedbackTitle>
                  <FeedbackContent>
                    {summary.feedback.overallFeedback}
                  </FeedbackContent>
                </OverallFeedback>

                {/* 강점 및 개선점 */}
                {summary.feedback.strengths.length > 0 &&
                  renderFeedbackSection('💪 주요 강점', summary.feedback.strengths, 'strengths')}

                {summary.feedback.improvements.length > 0 &&
                  renderFeedbackSection('🔧 개선이 필요한 부분', summary.feedback.improvements, 'improvements')}

                {summary.feedback.recommendations.length > 0 &&
                  renderFeedbackSection('💡 개선 권장사항', summary.feedback.recommendations, 'recommendations')}

                {/* 분석 정보 */}
                <AnalysisInfo>
                  <InfoItem>
                    <strong>분석 타입:</strong> {summary.analysisType === 'openai' ? 'OpenAI GPT-4o-mini' : 'HuggingFace (로컬)'}
                  </InfoItem>
                  <InfoItem>
                    <strong>분석 시간:</strong> {new Date(summary.createdAt).toLocaleString('ko-KR')}
                  </InfoItem>
                </AnalysisInfo>
              </AnalysisResults>
            )}

            {/* 분석 결과가 없는 경우 */}
            {!summary && !isAnalyzing && (
              <NoAnalysisMessage>
                📊 아직 AI 분석이 실행되지 않았습니다.
                <br />
                위의 "분석 시작" 버튼을 클릭하여 이력서를 분석해보세요.
              </NoAnalysisMessage>
            )}
          </ModalBody>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

// Styled Components
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
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #e9ecef;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
`;

const CloseButton = styled.button`
  position: fixed;
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
  z-index: 3010;

  &:hover {
    background: #f8f9fa;
    color: #333;
  }
`;

const ModalBody = styled.div`
  padding: 32px;
`;

const ApplicantInfo = styled.div`
  text-align: center;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
`;

const ApplicantName = styled.h3`
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
`;

const ApplicantDetails = styled.p`
  margin: 0;
  font-size: 16px;
  color: #666;
`;

const AnalysisControls = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  flex-wrap: wrap;
`;

const AnalysisTypeSelect = styled.select`
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ControlButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const AnalyzeButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #00c851, #00a844);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 200, 81, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const ReanalyzeButton = styled(AnalyzeButton)`
  background: linear-gradient(135deg, #17a2b8, #138496);
`;

const ErrorMessage = styled.div`
  padding: 16px;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
  font-weight: 500;
`;

const AnalysisResults = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 16px;
  text-align: center;
`;

const OverallScoreCircle = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: white;
  background: ${props => props.grade.color};
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
`;

const OverallScoreInfo = styled.div`
  flex: 1;
`;

const OverallScoreLabel = styled.div`
  font-size: 18px;
  color: #666;
  margin-bottom: 8px;
`;

const OverallScoreGrade = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: #333;
`;

const ScoreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const ScoreCard = styled.div`
  padding: 20px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const ScoreHeader = styled.div`
  margin-bottom: 12px;
`;

const ScoreTitle = styled.div`
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
`;

const ScoreValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: ${props => {
    if (props.score >= 80) return '#28a745';
    if (props.score >= 60) return '#17a2b8';
    if (props.score >= 40) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreGrade = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: ${props => props.grade.color};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
`;

const OverallFeedback = styled.div`
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #00c851;
`;

const FeedbackSection = styled.div`
  padding: 20px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
`;

const FeedbackTitle = styled.h4`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
`;

const FeedbackList = styled.ul`
  margin: 0;
  padding: 0;
  list-style: none;
`;

const FeedbackItem = styled.li`
  padding: 8px 0;
  border-bottom: 1px solid #f1f3f4;
  color: #333;
  font-size: 14px;
  line-height: 1.5;

  &:last-child {
    border-bottom: none;
  }
`;

const FeedbackContent = styled.div`
  font-size: 16px;
  line-height: 1.6;
  color: #333;
`;

const AnalysisInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  font-size: 14px;
  color: #666;
`;

const InfoItem = styled.div`
  display: flex;
  gap: 8px;
`;

const NoAnalysisMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
  line-height: 1.6;
`;

export default AIAnalysisModal;
