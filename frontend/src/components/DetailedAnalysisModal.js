import React, { useState, useEffect } from 'react';
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

const DocumentContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
`;

const AnalysisSection = styled.div`
  margin: 32px 0;
`;

const SectionTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
`;

const AnalysisItem = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid #28a745;
  transition: all 0.2s;

  &:hover {
    background: #e9ecef;
    transform: translateY(-2px);
  }

  &.warning {
    border-left-color: #ffc107;
  }

  &.danger {
    border-left-color: #dc3545;
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
  color: #495057;
  margin: 0;
`;

const ItemScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

const ScoreNumber = styled.span`
  font-size: 18px;
  color: #28a745;
`;

const ScoreMax = styled.span`
  font-size: 14px;
  color: #6c757d;
`;

const ItemDescription = styled.p`
  font-size: 13px;
  color: #6c757d;
  line-height: 1.5;
  margin: 0;
`;

const StatusIcon = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  background: #28a745;

  &.warning {
    background: #ffc107;
    color: #212529;
  }

  &.danger {
    background: #dc3545;
  }
`;

const DetailedAnalysisModal = ({ isOpen, onClose, applicantData }) => {
  const [showJson, setShowJson] = useState(false);
  const [jobPostingInfo, setJobPostingInfo] = useState(null);

  // 채용공고 정보 설정
  useEffect(() => {
    if (applicantData && applicantData.job_posting_info) {
      // 백엔드에서 이미 가져온 채용공고 정보 사용
      setJobPostingInfo(applicantData.job_posting_info);
    } else if (applicantData && applicantData.job_posting_id) {
      // 백엔드에서 가져오지 못한 경우 직접 API 호출
      const fetchJobPostingInfo = async () => {
        try {
          const response = await fetch(`/api/job-postings/${applicantData.job_posting_id}`);
          if (response.ok) {
            const jobPosting = await response.json();
            setJobPostingInfo(jobPosting);
          } else {
            console.log('채용공고 정보를 찾을 수 없습니다:', applicantData.job_posting_id);
          }
        } catch (error) {
          console.error('채용공고 정보 가져오기 실패:', error);
        }
      };
      fetchJobPostingInfo();
    }
  }, [isOpen, applicantData]);

  if (!isOpen || !applicantData) return null;

  // 분석 데이터 추출
  const analysisData = applicantData.analysis_result || applicantData.analysis || {};
  const resumeAnalysis = analysisData.resume_analysis || {};
  const coverLetterAnalysis = analysisData.cover_letter_analysis || {};

  // 전체 점수 계산
  const calculateOverallScore = () => {
    const allScores = [];

    // 이력서 분석 점수들
    Object.values(resumeAnalysis).forEach(item => {
      if (item && typeof item === 'object' && 'score' in item) {
        allScores.push(item.score);
      }
    });

    // 자기소개서 분석 점수들
    Object.values(coverLetterAnalysis).forEach(item => {
      if (item && typeof item === 'object' && 'score' in item) {
        allScores.push(item.score);
      }
    });

    if (allScores.length === 0) return 8; // 기본값

    const average = allScores.reduce((sum, score) => sum + score, 0) / allScores.length;
    return Math.round(average * 10) / 10; // 소수점 첫째자리까지
  };

  const overallScore = calculateOverallScore();

  // 점수에 따른 상태 및 아이콘 결정
  const getScoreStatus = (score) => {
    if (score >= 8) return { status: 'success', icon: <FiCheck /> };
    if (score >= 6) return { status: 'warning', icon: <FiAlertCircle /> };
    return { status: 'danger', icon: <FiAlertCircle /> };
  };

  // 이력서 분석 항목 라벨
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

  // 자기소개서 분석 항목 라벨
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

  // 파일명과 시간 추출
  const getFileNameAndTime = () => {
    if (applicantData.resume_file) {
      return `${applicantData.resume_file} - ${new Date().toLocaleString('ko-KR')}`;
    }
    return `${applicantData.applicant_name || '지원자'} - ${new Date().toLocaleString('ko-KR')}`;
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
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <CloseButton onClick={onClose}>
              <FiX />
            </CloseButton>

            <Header>
              <Title>AI 상세 분석 결과</Title>
              <Subtitle>{getFileNameAndTime()}</Subtitle>
              <HeaderActions>
                <ViewJsonButton onClick={() => setShowJson(!showJson)}>
                  <FiEye />
                  원본 JSON 보기
                </ViewJsonButton>
              </HeaderActions>
            </Header>

            <Content>
              {/* 지원공고 정보 */}
              {jobPostingInfo && (
                <JobPostingSection>
                  <JobPostingHeader>
                    <FiBriefcase size={18} color="#007bff" />
                    <JobPostingTitle>지원공고 정보</JobPostingTitle>
                  </JobPostingHeader>
                  <JobPostingInfo>
                    <JobPostingItem>
                      <JobPostingLabel>공고 제목</JobPostingLabel>
                      <JobPostingValue>{jobPostingInfo.title || '제목 없음'}</JobPostingValue>
                    </JobPostingItem>
                    <JobPostingItem>
                      <JobPostingLabel>회사명</JobPostingLabel>
                      <JobPostingValue>{jobPostingInfo.company || '회사명 없음'}</JobPostingValue>
                    </JobPostingItem>
                    <JobPostingItem>
                      <JobPostingLabel>근무지</JobPostingLabel>
                      <JobPostingValue>{jobPostingInfo.location || '근무지 없음'}</JobPostingValue>
                    </JobPostingItem>
                    <JobPostingItem>
                      <JobPostingLabel>공고 상태</JobPostingLabel>
                      <JobPostingValue>
                        {jobPostingInfo.status === 'published' ? '모집중' :
                         jobPostingInfo.status === 'closed' ? '마감' :
                         jobPostingInfo.status === 'draft' ? '임시저장' : '기타'}
                      </JobPostingValue>
                    </JobPostingItem>
                  </JobPostingInfo>
                </JobPostingSection>
              )}

              {/* 전체 평가 점수 */}
              <OverallScore>
                <ScoreCircle>{overallScore}</ScoreCircle>
                <ScoreInfo>
                  <ScoreLabel>전체 평가 점수</ScoreLabel>
                  <ScoreValue>{overallScore}/10</ScoreValue>
                </ScoreInfo>
              </OverallScore>

              {/* 자소서 내용 */}
              {applicantData.cover_letter_content && (
                <DocumentSection>
                  <DocumentHeader>
                    <FiFileText size={18} color="#28a745" />
                    <DocumentTitle>자기소개서 내용</DocumentTitle>
                  </DocumentHeader>
                  <DocumentContent>
                    {applicantData.cover_letter_content}
                  </DocumentContent>
                </DocumentSection>
              )}

              {/* 이력서 내용 */}
              {applicantData.resume_content && (
                <DocumentSection>
                  <DocumentHeader>
                    <FiFileText size={18} color="#007bff" />
                    <DocumentTitle>이력서 내용</DocumentTitle>
                  </DocumentHeader>
                  <DocumentContent>
                    {applicantData.resume_content}
                  </DocumentContent>
                </DocumentSection>
              )}

              {/* 이력서 분석 */}
              {Object.keys(resumeAnalysis).length > 0 && (
                <AnalysisSection>
                  <SectionTitle>이력서 분석</SectionTitle>
                  <AnalysisGrid>
                    {Object.entries(resumeAnalysis).map(([key, item]) => {
                      if (!item || typeof item !== 'object' || !('score' in item)) return null;

                      const { status, icon } = getScoreStatus(item.score);
                      const label = getResumeAnalysisLabel(key);

                      return (
                        <AnalysisItem key={key} className={status}>
                          <ItemHeader>
                            <ItemTitle>{label}</ItemTitle>
                            <ItemScore>
                              <ScoreNumber>{item.score}</ScoreNumber>
                              <ScoreMax>/10</ScoreMax>
                              <StatusIcon className={status}>
                                {icon}
                              </StatusIcon>
                            </ItemScore>
                          </ItemHeader>
                          <ItemDescription>
                            {item.feedback || `${label}에 대한 분석 결과입니다.`}
                          </ItemDescription>
                        </AnalysisItem>
                      );
                    })}
                  </AnalysisGrid>
                </AnalysisSection>
              )}

              {/* 자기소개서 분석 */}
              {Object.keys(coverLetterAnalysis).length > 0 && (
                <AnalysisSection>
                  <SectionTitle>자기소개서 분석</SectionTitle>
                  <AnalysisGrid>
                    {Object.entries(coverLetterAnalysis).map(([key, item]) => {
                      if (!item || typeof item !== 'object' || !('score' in item)) return null;

                      const { status, icon } = getScoreStatus(item.score);
                      const label = getCoverLetterAnalysisLabel(key);

                      return (
                        <AnalysisItem key={key} className={status}>
                          <ItemHeader>
                            <ItemTitle>{label}</ItemTitle>
                            <ItemScore>
                              <ScoreNumber>{item.score}</ScoreNumber>
                              <ScoreMax>/10</ScoreMax>
                              <StatusIcon className={status}>
                                {icon}
                              </StatusIcon>
                            </ItemScore>
                          </ItemHeader>
                          <ItemDescription>
                            {item.feedback || `${label}에 대한 분석 결과입니다.`}
                          </ItemDescription>
                        </AnalysisItem>
                      );
                    })}
                  </AnalysisGrid>
                </AnalysisSection>
              )}

              {/* JSON 데이터 표시 */}
              {showJson && (
                <AnalysisSection>
                  <SectionTitle>원본 분석 데이터</SectionTitle>
                  <pre style={{
                    background: '#f8f9fa',
                    padding: '16px',
                    borderRadius: '8px',
                    overflow: 'auto',
                    fontSize: '12px',
                    border: '1px solid #e9ecef'
                  }}>
                    {JSON.stringify(analysisData, null, 2)}
                  </pre>
                </AnalysisSection>
              )}
            </Content>
          </ModalContent>
        </ModalOverlay>
      )}
    </AnimatePresence>
  );
};

export default DetailedAnalysisModal;
