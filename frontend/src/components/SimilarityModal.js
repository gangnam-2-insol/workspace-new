import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiUser, FiBriefcase, FiAward, FiTrendingUp, FiStar } from 'react-icons/fi';

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
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
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
  transition: var(--transition);
  
  &:hover {
    background: var(--background-light);
    color: var(--text-primary);
  }
`;

const Header = styled.div`
  margin-bottom: 24px;
  padding-right: 40px;
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
`;

const OriginalResume = styled.div`
  background: var(--background-light);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border-left: 4px solid var(--primary-color);
`;

const OriginalTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const OriginalInfo = styled.div`
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--text-secondary);
`;

const SimilarResumesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SimilarResumeCard = styled.div`
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  transition: var(--transition);
  cursor: pointer;
  
  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const SimilarResumeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const SimilarResumeTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SimilarityScore = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--primary-color);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
`;

const SimilarResumeInfo = styled.div`
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
`;

const SimilarResumeDetails = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
`;

const NoResults = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
`;

const NoResultsIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const NoResultsText = styled.p`
  font-size: 16px;
  margin: 0;
`;

const SimilarityModal = ({ isOpen, onClose, data, documentType = 'resume' }) => {
  if (!isOpen || !data) return null;

  const { original_resume, similar_resumes, total } = data;
  const docTypeName = documentType === 'resume' ? '이력서' : '자소서';

  const formatSimilarityScore = (score) => {
    return Math.round(score * 100);
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
            <CloseButton onClick={onClose}>
              <FiX />
            </CloseButton>
            
            <Header>
              <Title>
                <FiTrendingUp />
                유사도 검색 결과
              </Title>
              <Subtitle>
                {original_resume.name}님의 {docTypeName}와 유사한 {docTypeName} {total}건을 찾았습니다.
              </Subtitle>
            </Header>

            <OriginalResume>
              <OriginalTitle>
                <FiUser />
                기준 {docTypeName}
              </OriginalTitle>
              <OriginalInfo>
                <InfoItem>
                  <FiUser />
                  {original_resume.name}
                </InfoItem>
                {original_resume.position && (
                  <InfoItem>
                    <FiBriefcase />
                    {original_resume.position}
                  </InfoItem>
                )}
                {original_resume.department && (
                  <InfoItem>
                    <FiAward />
                    {original_resume.department}
                  </InfoItem>
                )}
              </OriginalInfo>
            </OriginalResume>

            {similar_resumes.length > 0 ? (
              <SimilarResumesList>
                {similar_resumes.map((item, index) => (
                  <SimilarResumeCard key={index}>
                    <SimilarResumeHeader>
                      <SimilarResumeTitle>
                        <FiUser />
                        {item.resume.name}
                      </SimilarResumeTitle>
                      <SimilarityScore>
                        <FiStar />
                        {formatSimilarityScore(item.similarity_score)}%
                      </SimilarityScore>
                    </SimilarResumeHeader>
                    
                    <SimilarResumeInfo>
                      {item.resume.position && (
                        <InfoItem>
                          <FiBriefcase />
                          {item.resume.position}
                        </InfoItem>
                      )}
                      {item.resume.department && (
                        <InfoItem>
                          <FiAward />
                          {item.resume.department}
                        </InfoItem>
                      )}
                    </SimilarResumeInfo>
                    
                    <SimilarResumeDetails>
                      {item.resume.experience && (
                        <div>경력: {item.resume.experience}</div>
                      )}
                      {item.resume.skills && (
                        <div>기술: {item.resume.skills}</div>
                      )}
                      {item.resume.resume_text && (
                        <div>내용: {item.resume.resume_text.substring(0, 100)}...</div>
                      )}
                    </SimilarResumeDetails>
                  </SimilarResumeCard>
                ))}
              </SimilarResumesList>
            ) : (
              <NoResults>
                <NoResultsIcon>🔍</NoResultsIcon>
                <NoResultsText>
                  유사한 {docTypeName}를 찾을 수 없습니다.
                </NoResultsText>
              </NoResults>
            )}
          </ModalContent>
        </ModalOverlay>
      )}
    </AnimatePresence>
  );
};

export default SimilarityModal;
