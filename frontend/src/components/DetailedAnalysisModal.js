import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck, FiAlertCircle, FiStar, FiTrendingUp, FiTrendingDown, FiFileText, FiMessageSquare, FiCode, FiBarChart2, FiEye, FiBriefcase } from 'react-icons/fi';

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
  max-width: 1200px;
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
  background: #f8f9fa;
  padding: 24px 32px 16px 32px;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid #e9ecef;
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

const HeaderActions = styled.div`
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
`;

const ViewJsonButton = styled.button`
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

  &:hover {
    background: #5a6268;
  }
`;

const Content = styled.div`
  padding: 32px;
`;

const OverallScore = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 24px 0;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  text-align: center;
`;

const ScoreCircle = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  border: 3px solid rgba(255, 255, 255, 0.3);
`;

const ScoreInfo = styled.div`
  text-align: left;
`;

const ScoreLabel = styled.div`
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 4px;
`;

const ScoreValue = styled.div`
  font-size: 20px;
  font-weight: 600;
  opacity: 0.8;
`;

const JobPostingSection = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin: 24px 0;
  border-left: 4px solid #007bff;
`;

const JobPostingHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const JobPostingTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const JobPostingInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
`;

const JobPostingItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const JobPostingLabel = styled.span`
  font-size: 12px;
  color: #666;
  font-weight: 500;
`;

const JobPostingValue = styled.span`
  font-size: 14px;
  color: #333;
  font-weight: 500;
`;

const DocumentSection = styled.div`
  margin: 32px 0;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #28a745;
`;

const DocumentHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
`;

const DocumentTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
`;

const AnalysisItem = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid ${props => {
    const score = props.score;
    if (score >= 8) return '#28a745';
    if (score >= 6) return '#17a2b8';
    if (score >= 4) return '#ffc107';
    return '#dc3545';
  }};

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const ItemHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const ItemTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const ItemScore = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
`;

const ScoreNumber = styled.span`
  font-size: 16px;
  color: ${props => {
    const score = props.score;
    if (score >= 8) return '#28a745';
    if (score >= 6) return '#17a2b8';
    if (score >= 4) return '#ffc107';
    return '#dc3545';
  }};
`;

const ScoreMax = styled.span`
  font-size: 12px;
  color: #666;
`;

const ItemDescription = styled.p`
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  margin: 0;
`;

const StatusIcon = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
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
  max-height: 400px;
  overflow-y: auto;
`;

// 이력서 분석 항목 라벨 함수
const getResumeAnalysisLabel = (key) => {
  const labels = {
    basic_info_completeness: '기본정보 완성도',
    job_relevance: '직무 적합성',
    experience_clarity: '경력 명확성',
    tech_stack_clarity: '기술스택 명확성',
    project_recency: '프로젝트 최신성',
    achievement_metrics: '성과 지표',
    readability: '가독성',
    typos_and_errors: '오탈자',
    update_freshness: '최신성'
  };
  return labels[key] || key;
};

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
  return { grade: '개선필요', color: '#dc3545', icon: <FiTrendingDown /> };
};

const DetailedAnalysisModal = ({ isOpen, onClose, analysisData, applicantName = '지원자' }) => {
  const [showJson, setShowJson] = useState(false);

  // 분석 데이터 처리
  const processedData = useMemo(() => {
    if (!analysisData) return null;

    let resumeAnalysis = null;
    let coverLetterAnalysis = null;

    // 다양한 데이터 구조 지원
    if (analysisData.resume_analysis) {
      resumeAnalysis = analysisData.resume_analysis;
    } else if (analysisData.analysis_result?.resume_analysis) {
      resumeAnalysis = analysisData.analysis_result.resume_analysis;
    }

    if (analysisData.cover_letter_analysis) {
      coverLetterAnalysis = analysisData.cover_letter_analysis;
    } else if (analysisData.analysis_result?.cover_letter_analysis) {
      coverLetterAnalysis = analysisData.analysis_result.cover_letter_analysis;
    }

    return { resumeAnalysis, coverLetterAnalysis };
  }, [analysisData]);

  // 전체 점수 계산
  const overallScore = useMemo(() => {
    if (!processedData) return 0;

    const allScores = [];

    // 이력서 분석 점수
    if (processedData.resumeAnalysis) {
      Object.values(processedData.resumeAnalysis)
        .filter(item => item && typeof item === 'object' && 'score' in item)
        .forEach(item => allScores.push(item.score));
    }

    // 자소서 분석 점수
    if (processedData.coverLetterAnalysis) {
      Object.values(processedData.coverLetterAnalysis)
        .filter(item => item && typeof item === 'object' && 'score' in item)
        .forEach(item => allScores.push(item.score));
    }

    if (allScores.length === 0) return 8; // 기본값

    const total = allScores.reduce((sum, score) => sum + score, 0);
    return Math.round((total / allScores.length) * 10) / 10;
  }, [processedData]);

  const scoreGrade = getScoreGrade(overallScore);

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
            <Title>통합 분석 결과</Title>
            <Subtitle>{applicantName}님의 이력서 + 자소서 종합 분석</Subtitle>
            <HeaderActions>
              <ViewJsonButton onClick={() => setShowJson(!showJson)}>
                <FiEye />
                {showJson ? 'JSON 숨기기' : 'JSON 보기'}
              </ViewJsonButton>
            </HeaderActions>
          </Header>

          <Content>
            {/* 전체 평가 점수 */}
            <OverallScore>
              <ScoreCircle>
                {overallScore}
              </ScoreCircle>
              <ScoreInfo>
                <ScoreLabel>전체 평가 점수</ScoreLabel>
                <ScoreValue>{overallScore}/10점 ({scoreGrade.grade} 등급)</ScoreValue>
              </ScoreInfo>
            </OverallScore>

            {/* 채용공고 정보 */}
            {analysisData?.job_posting && (
              <JobPostingSection>
                <JobPostingHeader>
                  <FiBriefcase />
                  <JobPostingTitle>지원 채용공고</JobPostingTitle>
                </JobPostingHeader>
                <JobPostingInfo>
                  <JobPostingItem>
                    <JobPostingLabel>직무</JobPostingLabel>
                    <JobPostingValue>{analysisData.job_posting.title || 'N/A'}</JobPostingValue>
                  </JobPostingItem>
                  <JobPostingItem>
                    <JobPostingLabel>회사</JobPostingLabel>
                    <JobPostingValue>{analysisData.job_posting.company || 'N/A'}</JobPostingValue>
                  </JobPostingItem>
                  <JobPostingItem>
                    <JobPostingLabel>지역</JobPostingLabel>
                    <JobPostingValue>{analysisData.job_posting.location || 'N/A'}</JobPostingValue>
                  </JobPostingItem>
                </JobPostingInfo>
              </JobPostingSection>
            )}

            {/* 이력서 분석 결과 */}
            {processedData?.resumeAnalysis && (
              <DocumentSection>
                <DocumentHeader>
                  <FiFileText />
                  <DocumentTitle>이력서 분석 결과</DocumentTitle>
                </DocumentHeader>
                <AnalysisGrid>
                  {Object.entries(processedData.resumeAnalysis).map(([key, value]) => {
                    if (!value || typeof value !== 'object' || !('score' in value)) return null;

                    const score = value.score;
                    const grade = getScoreGrade(score);

                    return (
                      <AnalysisItem key={key} score={score}>
                        <ItemHeader>
                          <ItemTitle>
                            {getResumeAnalysisLabel(key)}
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
              </DocumentSection>
            )}

            {/* 자소서 분석 결과 */}
            {processedData?.coverLetterAnalysis && (
              <DocumentSection>
                <DocumentHeader>
                  <FiMessageSquare />
                  <DocumentTitle>자소서 분석 결과</DocumentTitle>
                </DocumentHeader>
                <AnalysisGrid>
                  {Object.entries(processedData.coverLetterAnalysis).map(([key, value]) => {
                    if (!value || typeof value !== 'object' || !('score' in value)) return null;

                    const score = value.score;
                    const grade = getScoreGrade(score);

                    return (
                      <AnalysisItem key={key} score={score}>
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
              </DocumentSection>
            )}

            {/* JSON 원본 데이터 */}
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

export default DetailedAnalysisModal;
