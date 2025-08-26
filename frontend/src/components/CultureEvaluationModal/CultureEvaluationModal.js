import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiX, FiStar, FiCheck, FiRefreshCw } from 'react-icons/fi';

const Modal = styled.div`
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
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ApplicantInfo = styled.div`
  background: var(--background-secondary);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
`;

const ApplicantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
`;

const ApplicantDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
`;

const CultureSection = styled.div`
  margin-bottom: 24px;
`;

const CultureTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CultureCard = styled.div`
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
`;

const CultureHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const CultureName = styled.div`
  font-weight: 600;
  color: var(--text-primary);
`;

const ScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Score = styled.span`
  font-size: 18px;
  font-weight: 700;
  color: ${props => {
    if (props.score >= 80) return '#10b981';
    if (props.score >= 60) return '#f59e0b';
    return '#ef4444';
  }};
`;

const EvaluateButton = styled.button`
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-dark);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const CriteriaList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const CriteriaItem = styled.li`
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
  color: var(--text-primary);

  &:last-child {
    border-bottom: none;
  }

  &:before {
    content: "•";
    color: var(--primary-color);
    font-weight: bold;
    margin-right: 8px;
  }
`;

const FeedbackSection = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
`;

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const CultureEvaluationModal = ({ isOpen, onClose, applicant, jobPosting }) => {
  const [cultures, setCultures] = useState([]);
  const [evaluations, setEvaluations] = useState({});
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState({});

  useEffect(() => {
    if (isOpen) {
      loadCultures();
      loadExistingEvaluations();
    }
  }, [isOpen, applicant]);

  const loadCultures = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/?active_only=true`);
      if (response.ok) {
        const data = await response.json();
        setCultures(data);
      }
    } catch (error) {
      console.error('인재상 로딩 오류:', error);
    }
  };

  const loadExistingEvaluations = () => {
    if (applicant?.culture_scores) {
      setEvaluations(applicant.culture_scores);
    }
  };

  const evaluateCulture = async (cultureId) => {
    if (!applicant) return;

    setEvaluating(prev => ({ ...prev, [cultureId]: true }));

    try {
      // 지원자의 이력서와 자기소개서 텍스트 수집
      const resumeText = applicant.growthBackground || applicant.careerHistory || '';
      const coverLetterText = applicant.motivation || '';

      const response = await fetch(
        `${API_BASE_URL}/api/company-culture/evaluate/${applicant.id}/${cultureId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            resume_text: resumeText,
            cover_letter_text: coverLetterText
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        setEvaluations(prev => ({
          ...prev,
          [cultureId]: result
        }));
      } else {
        alert('평가 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('평가 오류:', error);
      alert('평가 중 오류가 발생했습니다.');
    } finally {
      setEvaluating(prev => ({ ...prev, [cultureId]: false }));
    }
  };

  const evaluateAllCultures = async () => {
    setLoading(true);

    try {
      for (const culture of cultures) {
        await evaluateCulture(culture.id);
      }
    } catch (error) {
      console.error('전체 평가 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  if (!isOpen) return null;

  return (
    <Modal onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>
            <FiStar size={20} />
            인재상 평가
          </ModalTitle>
          <CloseButton onClick={onClose}>
            <FiX size={20} />
          </CloseButton>
        </ModalHeader>

        {applicant && (
          <ApplicantInfo>
            <ApplicantName>{applicant.name}</ApplicantName>
            <ApplicantDetails>
              <div>직무: {applicant.position || 'N/A'}</div>
              <div>부서: {applicant.department || 'N/A'}</div>
              <div>경력: {applicant.experience || 'N/A'}</div>
              <div>상태: {applicant.status || 'N/A'}</div>
            </ApplicantDetails>
          </ApplicantInfo>
        )}

        <CultureSection>
          <CultureTitle>
            <FiStar size={16} />
            회사 인재상 평가
            <EvaluateButton
              onClick={evaluateAllCultures}
              disabled={loading}
              style={{ marginLeft: 'auto' }}
            >
              {loading ? (
                <LoadingSpinner />
              ) : (
                <FiRefreshCw size={14} />
              )}
              전체 평가
            </EvaluateButton>
          </CultureTitle>

          {cultures.length === 0 ? (
            <EmptyState>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏢</div>
              <h3>등록된 인재상이 없습니다</h3>
              <p>시스템 설정에서 회사 인재상을 먼저 등록해주세요.</p>
            </EmptyState>
          ) : (
            cultures.map((culture) => {
              const evaluation = evaluations[culture.id];
              const isEvaluating = evaluating[culture.id];

              return (
                <CultureCard key={culture.id}>
                  <CultureHeader>
                    <CultureName>{culture.name}</CultureName>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {evaluation && (
                        <ScoreDisplay>
                          <span>점수:</span>
                          <Score score={evaluation.score}>
                            {evaluation.score.toFixed(1)}점
                          </Score>
                        </ScoreDisplay>
                      )}
                      <EvaluateButton
                        onClick={() => evaluateCulture(culture.id)}
                        disabled={isEvaluating}
                      >
                        {isEvaluating ? (
                          <LoadingSpinner />
                        ) : (
                          <FiCheck size={14} />
                        )}
                        {evaluation ? '재평가' : '평가'}
                      </EvaluateButton>
                    </div>
                  </CultureHeader>

                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      {culture.description}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      가중치: {culture.weight}%
                    </div>
                  </div>

                  <CriteriaList>
                    {culture.criteria.map((criterion, index) => (
                      <CriteriaItem key={index}>{criterion}</CriteriaItem>
                    ))}
                  </CriteriaList>

                  {evaluation && evaluation.feedback && (
                    <FeedbackSection>
                      <strong>평가 피드백:</strong> {evaluation.feedback}
                    </FeedbackSection>
                  )}
                </CultureCard>
              );
            })
          )}
        </CultureSection>
      </ModalContent>
    </Modal>
  );
};

export default CultureEvaluationModal;
