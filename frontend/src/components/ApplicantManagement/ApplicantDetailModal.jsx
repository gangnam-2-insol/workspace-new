import React from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import { FiX, FiFileText, FiEdit3, FiExternalLink } from 'react-icons/fi';
import { parseSkills } from '../../utils/skillParser';

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
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
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

const ModalBody = styled.div`
  padding: 0 24px 24px 24px;
`;

const ApplicantInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);

  &:last-child {
    border-bottom: none;
  }
`;

const InfoLabel = styled.span`
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 80px;
`;

const InfoValue = styled.span`
  color: var(--text-primary);
  text-align: right;
  flex: 1;
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    switch (props.status) {
      case '서류합격':
      case '면접합격':
      case '최종합격':
        return 'rgba(0, 200, 81, 0.1)';
      case '서류불합격':
      case '면접불합격':
      case '최종불합격':
        return 'rgba(255, 82, 82, 0.1)';
      default:
        return 'rgba(158, 158, 158, 0.1)';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case '서류합격':
      case '면접합격':
      case '최종합격':
        return 'var(--primary-color)';
      case '서류불합격':
      case '면접불합격':
      case '최종불합격':
        return '#ff5252';
      default:
        return '#9e9e9e';
    }
  }};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: white;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;

  &:hover {
    border-color: var(--primary-color);
    background: var(--primary-color);
    color: white;
  }

  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);

    &:hover {
      background: var(--primary-dark);
    }
  }
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

const ApplicantDetailModal = ({ isOpen, applicant, onClose, onResumeClick, onDocumentClick, onPortfolioClick }) => {
  if (!isOpen || !applicant) return null;

  const handleResumeClick = () => {
    onResumeClick(applicant);
  };

  const handleDocumentClick = (type) => {
    onDocumentClick(type, applicant);
  };

  const handlePortfolioClick = () => {
    onPortfolioClick(applicant);
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
          <ModalTitle>지원자 상세정보</ModalTitle>
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>
        </ModalHeader>

        <ModalBody>
          <ApplicantInfo>
            <InfoRow>
              <InfoLabel>이름</InfoLabel>
              <InfoValue>{applicant.name}</InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>이메일</InfoLabel>
              <InfoValue>{applicant.email}</InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>직무</InfoLabel>
              <InfoValue>{applicant.position || applicant.job_title}</InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>부서</InfoLabel>
              <InfoValue>{applicant.department || '-'}</InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>경력</InfoLabel>
              <InfoValue>{applicant.experience || applicant.years_of_experience || '-'}</InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>기술스택</InfoLabel>
              <InfoValue>
                {(() => {
                  const skills = parseSkills(applicant.skills || applicant.technical_skills);
                  return skills.length > 0 ? skills.join(', ') : '-';
                })()}
              </InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>상태</InfoLabel>
              <InfoValue>
                <StatusBadge status={applicant.status}>
                  {applicant.status || '지원'}
                </StatusBadge>
              </InfoValue>
            </InfoRow>
            <InfoRow>
              <InfoLabel>지원일시</InfoLabel>
              <InfoValue>
                {applicant.applied_at
                  ? new Date(applicant.applied_at).toLocaleDateString('ko-KR')
                  : applicant.created_at
                    ? new Date(applicant.created_at).toLocaleDateString('ko-KR')
                    : '-'}
              </InfoValue>
            </InfoRow>
          </ApplicantInfo>

          <ActionButtons>
            <ActionButton onClick={handleResumeClick}>
              <FiFileText size={16} />
              이력서 보기
            </ActionButton>
            <ActionButton onClick={() => handleDocumentClick('coverLetter')}>
              <FiEdit3 size={16} />
              자소서 보기
            </ActionButton>
            <ActionButton onClick={handlePortfolioClick}>
              <FiExternalLink size={16} />
              포트폴리오 보기
            </ActionButton>
          </ActionButtons>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default ApplicantDetailModal;
