import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiUser,
  FiFileText,
  FiMessageSquare,
  FiCode,
  FiX,
  FiMail,
  FiPhone,
  FiCalendar,
  FiBriefcase,
  FiMapPin
} from 'react-icons/fi';

// 모달 오버레이
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

// 모달 컨텐츠
const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 16px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  width: 800px;
`;

// 모달 헤더
const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e2e8f0;
`;

// 모달 제목
const ModalTitle = styled.h2`
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
`;

// 닫기 버튼
const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: #718096;
  transition: all 0.2s ease;

  &:hover {
    background: #f7fafc;
    color: #2d3748;
  }
`;

// 모달 바디
const ModalBody = styled.div`
  padding: 24px;
  overflow-y: auto;
  flex: 1;
`;

// 프로필 섹션
const ProfileSection = styled.div`
  margin-bottom: 24px;
`;

// 섹션 제목
const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #4299e1;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 프로필 그리드
const ProfileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

// 프로필 아이템
const ProfileItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

// 프로필 라벨
const ProfileLabel = styled.label`
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

// 프로필 값
const ProfileValue = styled.div`
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
`;

// 기술스택 섹션
const SkillsSection = styled.div`
  margin-bottom: 24px;
`;

// 기술스택 그리드
const SkillsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

// 기술 태그
const SkillTag = styled.span`
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
`;

// 요약 섹션
const SummarySection = styled.div`
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
`;

// 요약 제목
const SummaryTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 요약 텍스트
const SummaryText = styled.p`
  font-size: 14px;
  color: #4a5568;
  line-height: 1.6;
  background: white;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #4299e1;
  margin: 0;
`;

// 분석 점수 표시
const AnalysisScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
`;

// 분석 점수 원형
const AnalysisScoreCircle = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
`;

// 분석 점수 정보
const AnalysisScoreInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

// 분석 점수 라벨
const AnalysisScoreLabel = styled.div`
  font-size: 12px;
  color: #718096;
  font-weight: 500;
`;

// 분석 점수 값
const AnalysisScoreValue = styled.div`
  font-size: 16px;
  color: #2d3748;
  font-weight: 600;
`;

// 문서 버튼들
const DocumentButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
`;

// 문서 버튼
const DocumentButton = styled.button`
  padding: 12px 24px;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
  }
`;

// 이력서 버튼 특별 스타일
const ResumeButton = styled(DocumentButton)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 600;
  font-size: 15px;
  padding: 14px 28px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  }
`;

// 삭제 버튼
const DeleteButton = styled.button`
  padding: 12px 24px;
  background: linear-gradient(135deg, #e53e3e, #c53030);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
  }
`;

const ApplicantDetailModal = ({ applicant, onClose, onResumeClick, onDocumentClick, onDelete }) => {
  if (!applicant) return null;

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
            <ModalTitle>지원자 상세 정보</ModalTitle>
            <CloseButton onClick={onClose}>&times;</CloseButton>
          </ModalHeader>

          <ModalBody>
            <ProfileSection>
              <SectionTitle>
                <FiUser size={20} />
                기본 정보
              </SectionTitle>
              <ProfileGrid>
                <ProfileItem>
                  <ProfileLabel>이름</ProfileLabel>
                  <ProfileValue>{applicant.name || '이름 없음'}</ProfileValue>
                </ProfileItem>
                <ProfileItem>
                  <ProfileLabel>경력</ProfileLabel>
                  <ProfileValue>{applicant.experience || '경력 정보 없음'}</ProfileValue>
                </ProfileItem>
                <ProfileItem>
                  <ProfileLabel>희망직책</ProfileLabel>
                  <ProfileValue>{applicant.position || '직무 미지정'}</ProfileValue>
                </ProfileItem>
                <ProfileItem>
                  <ProfileLabel>지원일</ProfileLabel>
                  <ProfileValue>
                    {applicant.application_date ?
                      new Date(applicant.application_date).toLocaleDateString('ko-KR') :
                      '날짜 없음'
                    }
                  </ProfileValue>
                </ProfileItem>
                {applicant.email && (
                  <ProfileItem>
                    <ProfileLabel>이메일</ProfileLabel>
                    <ProfileValue>{applicant.email}</ProfileValue>
                  </ProfileItem>
                )}
                {applicant.phone && (
                  <ProfileItem>
                    <ProfileLabel>전화번호</ProfileLabel>
                    <ProfileValue>{applicant.phone}</ProfileValue>
                  </ProfileItem>
                )}
              </ProfileGrid>
            </ProfileSection>

            {applicant.skills && (
              <SkillsSection>
                <SectionTitle>
                  <FiCode size={20} />
                  기술스택
                </SectionTitle>
                <SkillsGrid>
                  {Array.isArray(applicant.skills)
                    ? applicant.skills.map((skill, index) => (
                        <SkillTag key={index}>
                          {skill}
                        </SkillTag>
                      ))
                    : typeof applicant.skills === 'string'
                    ? applicant.skills.split(',').map((skill, index) => (
                        <SkillTag key={index}>
                          {skill.trim()}
                        </SkillTag>
                      ))
                    : null
                  }
                </SkillsGrid>
              </SkillsSection>
            )}

            <SummarySection>
              <SummaryTitle>
                <FiFileText size={20} />
                AI 분석 요약
              </SummaryTitle>

              {applicant.analysisScore && (
                <AnalysisScoreDisplay>
                  <AnalysisScoreCircle>
                    {Math.round(applicant.analysisScore)}
                  </AnalysisScoreCircle>
                  <AnalysisScoreInfo>
                    <AnalysisScoreLabel>AI 분석 점수</AnalysisScoreLabel>
                    <AnalysisScoreValue>{Math.round(applicant.analysisScore)}점</AnalysisScoreValue>
                  </AnalysisScoreInfo>
                </AnalysisScoreDisplay>
              )}

              {applicant.summary && (
                <SummaryText>
                  {applicant.summary}
                </SummaryText>
              )}
            </SummarySection>

            <DocumentButtons>
              <ResumeButton onClick={() => onResumeClick(applicant)}>
                <FiFileText size={16} />
                이력서
              </ResumeButton>
              <DocumentButton onClick={() => onDocumentClick('coverLetter', applicant)}>
                <FiMessageSquare size={16} />
                자소서
              </DocumentButton>
              <DocumentButton onClick={() => onDocumentClick('portfolio', applicant)}>
                <FiCode size={16} />
                포트폴리오
              </DocumentButton>
            </DocumentButtons>

            {onDelete && (
              <DeleteButton onClick={() => onDelete(applicant.id || applicant._id)}>
                <FiX size={16} />
                지원자 삭제
              </DeleteButton>
            )}
          </ModalBody>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default ApplicantDetailModal;
