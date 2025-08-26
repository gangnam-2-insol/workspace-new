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
  FiMapPin,
  FiCheck,
  FiClock,
  FiBarChart2,
  FiStar,
  FiTrash2,
  FiTarget,
  FiTrendingUp
} from 'react-icons/fi';

// 모달 오버레이
const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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
  max-width: 1200px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
`;

// 닫기 버튼
const CloseButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  background: #f8f9fa;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 12px;
  border-radius: 50%;
  transition: all 0.2s;
  z-index: 10;

  &:hover {
    background: #e9ecef;
    color: #333;
    transform: scale(1.1);
  }
`;

// 헤더
const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 40px 24px 40px;
  border-radius: 16px 16px 0 0;
  position: relative;
`;

// 헤더 액션 버튼들
const HeaderActions = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
`;

// 액션 버튼
const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(10px);

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-1px);
  }
`;

// 제목
const Title = styled.h1`
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

// 부제목
const Subtitle = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  opacity: 0.9;
`;

// AI 분석 점수 배지
const ScoreBadge = styled.span`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.3);
`;

// 컨텐츠
const Content = styled.div`
  padding: 40px;
`;

// 섹션
const Section = styled.div`
  margin-bottom: 32px;
`;

// 섹션 제목
const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
`;

// 섹션 컨텐츠
const SectionContent = styled.div`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #667eea;
`;

// 정보 그리드
const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
`;

// 정보 아이템
const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  }
`;

// 정보 아이콘
const InfoIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
`;

// 정보 컨텐츠
const InfoContent = styled.div`
  flex: 1;
`;

// 정보 라벨
const InfoLabel = styled.div`
  font-size: 12px;
  color: #718096;
  font-weight: 500;
  margin-bottom: 2px;
`;

// 정보 값
const InfoValue = styled.div`
  font-size: 14px;
  color: #2d3748;
  font-weight: 600;
`;

// 기술스택 그리드
const SkillsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

// 기술 태그
const SkillTag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
`;

// AI 분석 섹션
const AnalysisSection = styled.div`
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  margin-bottom: 32px;
`;

// 분석 점수 표시
const AnalysisScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
`;

// 분석 점수 원형
const AnalysisScoreCircle = styled.div`
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
`;

// 분석 점수 정보
const AnalysisScoreInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

// 분석 점수 라벨
const AnalysisScoreLabel = styled.div`
  font-size: 13px;
  color: #718096;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

// 분석 점수 값
const AnalysisScoreValue = styled.div`
  font-size: 18px;
  color: #2d3748;
  font-weight: 700;
`;

// 요약 텍스트
const SummaryText = styled.p`
  font-size: 15px;
  color: #4a5568;
  line-height: 1.7;
  background: white;
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #667eea;
  margin: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
`;

// 문서 버튼들
const DocumentButtons = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

// 문서 버튼
const DocumentButton = styled.button`
  padding: 14px 20px;
  background: white;
  color: #4a5568;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    border-color: #667eea;
    color: #667eea;
  }
`;

// 특별 버튼들
const SpecialButton = styled(DocumentButton)`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: transparent;
  font-weight: 700;
  font-size: 15px;
  padding: 16px 24px;

  &:hover {
    background: linear-gradient(135deg, #5a67d8, #6b46c1);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
`;

// 상태 변경 버튼들
const StatusButtons = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
`;

const StatusButton = styled.button`
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  }
`;

const PassButton = styled(StatusButton)`
  background: ${props => props.active ? '#10b981' : '#f3f4f6'};
  color: ${props => props.active ? 'white' : '#6b7280'};

  &:hover {
    background: #10b981;
    color: white;
  }
`;

const PendingButton = styled(StatusButton)`
  background: ${props => props.active ? '#f59e0b' : '#f3f4f6'};
  color: ${props => props.active ? 'white' : '#6b7280'};

  &:hover {
    background: #f59e0b;
    color: white;
  }
`;

const RejectButton = styled(StatusButton)`
  background: ${props => props.active ? '#ef4444' : '#f3f4f6'};
  color: ${props => props.active ? 'white' : '#6b7280'};

  &:hover {
    background: #ef4444;
    color: white;
  }
`;

// 삭제 버튼
const DeleteButton = styled.button`
  padding: 16px 24px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
    background: linear-gradient(135deg, #dc2626, #b91c1c);
  }
`;

const ApplicantDetailModal = ({ 
  applicant, 
  onClose, 
  onResumeClick, 
  onDocumentClick, 
  onDelete,
  onStatusUpdate,
  onCoverLetterAnalysis,
  onDetailedAnalysis
}) => {
  if (!applicant) return null;

  const handleStatusUpdate = (newStatus) => {
    if (onStatusUpdate) {
      onStatusUpdate(applicant.id || applicant._id, newStatus);
    }
  };

  // 상태 텍스트 변환 함수
  const getStatusText = (status) => {
    switch (status) {
      case 'passed':
        return '서류합격';
      case 'pending':
        return '보류';
      case 'rejected':
        return '서류불합격';
      default:
        return status || '지원';
    }
  };

  // 현재 상태 확인
  const currentStatus = applicant.status;

  return (
    <AnimatePresence>
      <ModalOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <ModalContent
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <CloseButton onClick={onClose}>
            <FiX />
          </CloseButton>

          <Header>
            <HeaderActions>
              <ActionButton>
                <FiBarChart2 size={14} />
                분석보기
              </ActionButton>
              <ActionButton>
                <FiStar size={14} />
                즐겨찾기
              </ActionButton>
            </HeaderActions>
            
            <Title>지원자 상세 정보</Title>
            <Subtitle>
              <span>{applicant.name || '이름 없음'}</span>
              {applicant.analysisScore && (
                <ScoreBadge>
                  AI 점수: {Math.round(applicant.analysisScore)}점
                </ScoreBadge>
              )}
            </Subtitle>
          </Header>

          <Content>
            {/* 기본 정보 섹션 */}
            <Section>
              <SectionTitle>
                <FiUser size={20} />
                기본 정보
              </SectionTitle>
              <SectionContent>
                <InfoGrid>
                  <InfoItem>
                    <InfoIcon>
                      <FiUser size={16} />
                    </InfoIcon>
                    <InfoContent>
                      <InfoLabel>이름</InfoLabel>
                      <InfoValue>{applicant.name || '이름 없음'}</InfoValue>
                    </InfoContent>
                  </InfoItem>
                  
                  <InfoItem>
                    <InfoIcon>
                      <FiTrendingUp size={16} />
                    </InfoIcon>
                    <InfoContent>
                      <InfoLabel>경력</InfoLabel>
                      <InfoValue>{applicant.experience || '경력 정보 없음'}</InfoValue>
                    </InfoContent>
                  </InfoItem>
                  
                  <InfoItem>
                    <InfoIcon>
                      <FiTarget size={16} />
                    </InfoIcon>
                    <InfoContent>
                      <InfoLabel>희망직책</InfoLabel>
                      <InfoValue>{applicant.position || '직무 미지정'}</InfoValue>
                    </InfoContent>
                  </InfoItem>
                  
                  <InfoItem>
                    <InfoIcon>
                      <FiCalendar size={16} />
                    </InfoIcon>
                    <InfoContent>
                      <InfoLabel>지원일</InfoLabel>
                      <InfoValue>
                        {applicant.application_date || applicant.appliedDate || applicant.created_at ?
                          new Date(applicant.application_date || applicant.appliedDate || applicant.created_at).toLocaleDateString('ko-KR') :
                          '날짜 없음'
                        }
                      </InfoValue>
                    </InfoContent>
                  </InfoItem>
                  
                  {applicant.email && (
                    <InfoItem>
                      <InfoIcon>
                        <FiMail size={16} />
                      </InfoIcon>
                      <InfoContent>
                        <InfoLabel>이메일</InfoLabel>
                        <InfoValue>{applicant.email}</InfoValue>
                      </InfoContent>
                    </InfoItem>
                  )}
                  
                  {applicant.phone && (
                    <InfoItem>
                      <InfoIcon>
                        <FiPhone size={16} />
                      </InfoIcon>
                      <InfoContent>
                        <InfoLabel>전화번호</InfoLabel>
                        <InfoValue>{applicant.phone}</InfoValue>
                      </InfoContent>
                    </InfoItem>
                  )}
                </InfoGrid>
              </SectionContent>
            </Section>

            {/* 기술스택 섹션 */}
            {applicant.skills && (
              <Section>
                <SectionTitle>
                  <FiCode size={20} />
                  기술스택
                </SectionTitle>
                <SectionContent>
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
                </SectionContent>
              </Section>
            )}

            {/* AI 분석 요약 섹션 */}
            <AnalysisSection>
              <SectionTitle>
                <FiBarChart2 size={20} />
                AI 분석 요약
              </SectionTitle>

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
            </AnalysisSection>

            {/* 문서 버튼들 */}
            <DocumentButtons>
              <SpecialButton onClick={() => onResumeClick(applicant)}>
                <FiFileText size={18} />
                이력서
              </SpecialButton>
              <DocumentButton onClick={() => onDocumentClick('coverLetter', applicant)}>
                <FiMessageSquare size={18} />
                자소서
              </DocumentButton>
                             <DocumentButton onClick={() => onCoverLetterAnalysis && onCoverLetterAnalysis(applicant)}>
                 <FiBarChart2 size={18} />
                 자소서 분석
               </DocumentButton>
               <DocumentButton onClick={() => onDetailedAnalysis && onDetailedAnalysis()}>
                 <FiStar size={18} />
                 통합 분석
               </DocumentButton>
              <DocumentButton onClick={() => onDocumentClick('portfolio', applicant)}>
                <FiCode size={18} />
                포트폴리오
              </DocumentButton>
            </DocumentButtons>

            {/* 삭제 버튼 */}
            {onDelete && (
              <DeleteButton onClick={() => onDelete(applicant.id || applicant._id)}>
                <FiTrash2 size={18} />
                지원자 삭제
              </DeleteButton>
            )}
          </Content>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default ApplicantDetailModal;
