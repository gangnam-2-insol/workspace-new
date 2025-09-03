import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { FiX, FiGithub, FiFileText, FiExternalLink, FiCheckCircle, FiAlertCircle, FiBrain } from 'react-icons/fi';
import AIAnalysisModal from './AIAnalysisModal';

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
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
  padding: 32px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
`;

const CloseButton = styled.button`
  position: fixed;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  z-index: 3010;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const DocumentContent = styled.div`
  margin-top: 24px;
`;

const ApplicantInfo = styled.div`
  background: var(--background-secondary);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoLabel = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const InfoValue = styled.span`
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
`;

const PortfolioSelection = styled.div`
  margin-bottom: 24px;
`;

const SelectionTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  color: var(--text-primary);
`;

const SelectionGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 8px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const SelectionCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: white;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 81, 0.1);
  }

  &.selected {
    border-color: var(--primary-color);
    background: rgba(0, 200, 81, 0.05);
  }
`;

const SelectionIcon = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 22px;
  color: white;

  &.github {
    background: linear-gradient(135deg, #24292e, #57606a);
  }

  &.portfolio {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
`;

const SelectionTitle2 = styled.h4`
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text-primary);
`;

const SelectionDescription = styled.p`
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
`;

const DocumentView = styled.div`
  background: var(--background-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
`;

const ViewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const ViewTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
`;

const ViewToggle = styled.div`
  display: flex;
  gap: 8px;
`;

const ToggleButton = styled.button`
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-primary)'};
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;

  &:hover {
    border-color: var(--primary-color);
  }
`;

const DocumentText = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
`;

const SimilarityResult = styled.div`
  background: ${props => props.isSimilar ? 'rgba(255, 82, 82, 0.1)' : 'rgba(0, 200, 81, 0.1)'};
  border: 1px solid ${props => props.isSimilar ? '#ff5252' : 'var(--primary-color)'};
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SimilarityIcon = styled.div`
  font-size: 20px;
  color: ${props => props.isSimilar ? '#ff5252' : 'var(--primary-color)'};
`;

const SimilarityText = styled.div`
  color: ${props => props.isSimilar ? '#ff5252' : 'var(--primary-color)'};
  font-weight: 600;
`;

const modalVariants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 }
};

const overlayVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};

const DocumentModal = ({
  isOpen,
  type,
  applicant,
  documentData,
  similarityData,
  isLoadingSimilarity,
  onClose,
  onPortfolioViewChange
}) => {
  const [portfolioView, setPortfolioView] = useState('select');
  const [viewMode, setViewMode] = useState('summary'); // 'summary' | 'original'
  const [isAIAnalysisModalOpen, setIsAIAnalysisModalOpen] = useState(false);

  useEffect(() => {
    if (isOpen && type === 'portfolio') {
      setPortfolioView('select');
    }
  }, [isOpen, type]);

  if (!isOpen || !applicant) return null;

  const handlePortfolioViewSelect = (view) => {
    setPortfolioView(view);
    if (onPortfolioViewChange) {
      onPortfolioViewChange(view);
    }
  };

  const getDocumentTitle = () => {
    switch (type) {
      case 'resume': return '이력서 보기';
      case 'coverLetter': return '자기소개서 보기';
      case 'portfolio': return '포트폴리오 보기';
      default: return '문서 보기';
    }
  };

  const renderPortfolioSelection = () => {
    if (type !== 'portfolio') return null;

    return (
      <PortfolioSelection>
        <SelectionTitle>포트폴리오 뷰 선택</SelectionTitle>
        <SelectionGrid>
          <SelectionCard
            className={portfolioView === 'github' ? 'selected' : ''}
            onClick={() => handlePortfolioViewSelect('github')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <SelectionIcon className="github">
              <FiGithub />
            </SelectionIcon>
            <SelectionTitle2>GitHub 요약</SelectionTitle2>
            <SelectionDescription>
              GitHub 활동 내역과 기여도를 요약하여 보여줍니다.
            </SelectionDescription>
          </SelectionCard>
          <SelectionCard
            className={portfolioView === 'portfolio' ? 'selected' : ''}
            onClick={() => handlePortfolioViewSelect('portfolio')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <SelectionIcon className="portfolio">
              <FiFileText />
            </SelectionIcon>
            <SelectionTitle2>기존 포트폴리오 요약</SelectionTitle2>
            <SelectionDescription>
              업로드된 포트폴리오 파일을 요약하여 보여줍니다.
            </SelectionDescription>
          </SelectionCard>
        </SelectionGrid>
      </PortfolioSelection>
    );
  };

  const renderDocumentContent = () => {
    if (type === 'portfolio' && portfolioView === 'select') return null;

    return (
      <DocumentView>
        <ViewHeader>
          <ViewTitle>
            {type === 'portfolio' ? '포트폴리오 내용' : '문서 내용'}
          </ViewTitle>
          {type === 'coverLetter' && (
            <ViewToggle>
              <ToggleButton
                active={viewMode === 'summary'}
                onClick={() => setViewMode('summary')}
              >
                요약보기
              </ToggleButton>
              <ToggleButton
                active={viewMode === 'original'}
                onClick={() => setViewMode('original')}
              >
                원본보기
              </ToggleButton>
            </ViewToggle>
          )}
        </ViewHeader>

        <DocumentText>
          {documentData ? (
            <>
                        {/* 이력서 분석 결과 표시 */}
          {type === 'resume' && (
            <div style={{ marginBottom: '20px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #e9ecef' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: '0', color: '#495057', fontSize: '16px' }}>📊 이력서 분석 결과</h4>
                <button
                  onClick={() => setIsAIAnalysisModalOpen(true)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    background: 'linear-gradient(135deg, #00c851, #00a844)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-1px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(0, 200, 81, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  <FiBrain size={14} />
                  AI 분석
                </button>
              </div>

              {documentData.analysisResult ? (
                <>
                  <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                    {documentData.analysisResult}
                  </div>
                  {documentData.analysisScore && (
                    <div style={{ marginTop: '12px', padding: '8px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                      <strong>분석 점수: {documentData.analysisScore}/100</strong>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ fontSize: '14px', color: '#666', textAlign: 'center', padding: '20px' }}>
                  아직 이력서 분석이 실행되지 않았습니다.
                  <br />
                  AI 분석 버튼을 클릭하여 상세한 분석을 받아보세요.
                </div>
              )}
            </div>
          )}

              {/* 문서 내용 표시 */}
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ margin: '0 0 12px 0', color: '#495057', fontSize: '16px' }}>📄 문서 내용</h4>
                {documentData.extracted_text || documentData.content || documentData.text || '내용이 없습니다.'}
              </div>

              {/* 추가 정보 표시 */}
              {type === 'resume' && (
                <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #e9ecef' }}>
                  <h4 style={{ margin: '0 0 12px 0', color: '#495057', fontSize: '16px' }}>ℹ️ 추가 정보</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '14px' }}>
                    {documentData.skills && (
                      <div>
                        <strong>기술 스택:</strong> {documentData.skills}
                      </div>
                    )}
                    {documentData.experience && (
                      <div>
                        <strong>경력:</strong> {documentData.experience}
                      </div>
                    )}
                    {documentData.growthBackground && (
                      <div>
                        <strong>성장 배경:</strong> {documentData.growthBackground}
                      </div>
                    )}
                    {documentData.motivation && (
                      <div>
                        <strong>지원 동기:</strong> {documentData.motivation}
                      </div>
                    )}
                    {documentData.careerHistory && (
                      <div>
                        <strong>경력 사항:</strong> {documentData.careerHistory}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
<<<<<<< Updated upstream
            '문서를 불러오는 중...'
=======
            '문서를 불러오는 중.'
>>>>>>> Stashed changes
          )}
        </DocumentText>

        {type === 'coverLetter' && similarityData && (
          <SimilarityResult isSimilar={similarityData.similarity_score > 0.7}>
            <SimilarityIcon>
              {similarityData.similarity_score > 0.7 ? <FiAlertCircle /> : <FiCheckCircle />}
            </SimilarityIcon>
            <SimilarityText>
              유사도 점수: {(similarityData.similarity_score * 100).toFixed(1)}%
              {similarityData.similarity_score > 0.7
                ? ' (높은 유사도 - 주의 필요)'
                : ' (정상 범위)'}
            </SimilarityText>
          </SimilarityResult>
        )}
      </DocumentView>
    );
  };

  return (
    <ModalOverlay
      variants={overlayVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      onClick={onClose}
    >
      <ModalContent
        variants={modalVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        onClick={(e) => e.stopPropagation()}
      >
        <ModalHeader>
          <ModalTitle>{getDocumentTitle()}</ModalTitle>
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>
        </ModalHeader>

        <DocumentContent>
          <ApplicantInfo>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>이름</InfoLabel>
                <InfoValue>{applicant.name}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>지원 직무</InfoLabel>
                <InfoValue>{applicant.position || applicant.job_title}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>상태</InfoLabel>
                <InfoValue>{applicant.status || '지원'}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>지원일시</InfoLabel>
                <InfoValue>
                  {applicant.applied_at
                    ? new Date(applicant.applied_at).toLocaleDateString('ko-KR')
                    : applicant.created_at
                      ? new Date(applicant.created_at).toLocaleDateString('ko-KR')
                      : '-'}
                </InfoValue>
              </InfoItem>
            </InfoGrid>
          </ApplicantInfo>

          {renderPortfolioSelection()}
          {renderDocumentContent()}
        </DocumentContent>
      </ModalContent>

      {/* AI 분석 모달 */}
      <AIAnalysisModal
        isOpen={isAIAnalysisModalOpen}
        applicant={applicant}
        onClose={() => setIsAIAnalysisModalOpen(false)}
        onAnalysisComplete={(result) => {
          console.log('✅ AI 분석 완료:', result);
          // 분석 완료 후 필요한 처리
          setIsAIAnalysisModalOpen(false);
        }}
      />
    </ModalOverlay>
  );
};

export default DocumentModal;
