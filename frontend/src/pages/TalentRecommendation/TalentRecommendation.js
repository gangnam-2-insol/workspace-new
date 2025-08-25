import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiUsers, 
  FiStar, 
  FiEye, 
  FiMessageSquare, 
  FiDownload,
  FiFilter,
  FiSearch,
  FiCheckCircle,
  FiZap,
  FiX
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText
} from '../../components/DetailModal/DetailModal';

const TalentContainer = styled.div`
  padding: 24px 0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  
  &.primary {
    background: var(--primary-color);
    color: white;
  }
  
  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-light);
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FilterButton = styled.button`
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--transition);
  
  &:hover {
    border-color: var(--primary-color);
  }
`;

const TalentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
`;

const TalentCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 1px solid var(--border-color);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const TalentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const TalentInfo = styled.div`
  flex: 1;
`;

const TalentName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const TalentPosition = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const MatchScore = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    if (props.score >= 90) return '#d4edda';
    if (props.score >= 80) return '#d1ecf1';
    if (props.score >= 70) return '#fff3cd';
    return '#f8d7da';
  }};
  color: ${props => {
    if (props.score >= 90) return '#155724';
    if (props.score >= 80) return '#0c5460';
    if (props.score >= 70) return '#856404';
    return '#721c24';
  }};
`;

const TalentDetails = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const SkillsList = styled.div`
  margin-bottom: 16px;
`;

const SkillTag = styled.span`
  display: inline-block;
  padding: 4px 8px;
  background: var(--background-secondary);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  margin-right: 6px;
  margin-bottom: 6px;
`;

const RecommendationReason = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
`;

const TalentActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
  
  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }
`;

// AI 추천 이유 모달 스타일
const AIRecommendationModal = styled(motion.div)`
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
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
`;

const ModalHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: var(--transition);
  
  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  
  &::after {
    content: '';
    width: 32px;
    height: 32px;
    border: 3px solid var(--border-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const RecommendationSection = styled.div`
  margin-bottom: 24px;
`;

const SectionHeader = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
`;

const RecommendationText = styled.div`
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  white-space: pre-line;
`;

// 샘플 데이터
const talents = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    experience: '3년',
    education: '컴퓨터공학과',
    location: '서울',
    matchScore: 95,
    skills: ['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'Redux'],
    recommendationReason: '• 모던 React 생태계 전문\n• 풍부한 프로젝트 경험\n• 높은 기술 스택 일치도',
    lastActive: '2024-01-15',
    portfolioScore: 92,
    interviewScore: 88
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    experience: '5년',
    education: '소프트웨어공학과',
    location: '경기',
    matchScore: 88,
    skills: ['Node.js', 'Python', 'Django', 'PostgreSQL', 'Docker'],
    recommendationReason: '• 우수한 시스템 설계 능력\n• 성능 최적화 전문\n• 다양한 백엔드 기술 보유',
    lastActive: '2024-01-14',
    portfolioScore: 89,
    interviewScore: 92
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    experience: '2년',
    education: '디자인학과',
    location: '서울',
    matchScore: 82,
    skills: ['Figma', 'Adobe XD', 'Sketch', 'InVision', 'Principle'],
    recommendationReason: '• 창의적 디자인 감각\n• 사용자 중심 UX 사고\n• 프로토타이핑 전문 도구 활용',
    lastActive: '2024-01-13',
    portfolioScore: 85,
    interviewScore: 78
  },
  {
    id: 4,
    name: '정수진',
    position: '데이터 엔지니어',
    experience: '4년',
    education: '통계학과',
    location: '부산',
    matchScore: 90,
    skills: ['Python', 'Spark', 'Hadoop', 'Airflow', 'Kubernetes'],
    recommendationReason: '• 대용량 데이터 처리 전문\n• ML 파이프라인 구축 능력\n• 클라우드 인프라 운영 경험',
    lastActive: '2024-01-12',
    portfolioScore: 94,
    interviewScore: 91
  }
];

const TalentRecommendation = () => {
  const [selectedTalent, setSelectedTalent] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isAIRecommendationModalOpen, setIsAIRecommendationModalOpen] = useState(false);
  const [aiRecommendationData, setAIRecommendationData] = useState(null);
  const [isLoadingAIRecommendation, setIsLoadingAIRecommendation] = useState(false);

  // LLM API를 통해 AI 추천 이유 생성
  const generateAIRecommendation = async (talent) => {
    try {
      const response = await fetch('/api/llm/generate-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          talent: talent,
          baseCandidate: null // 기준 지원자 정보 (필요시 추가)
        }),
      });

      if (!response.ok) {
        throw new Error('AI 추천 이유 생성에 실패했습니다.');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('AI 추천 이유 생성 오류:', error);
      throw error;
    }
  };

  // AI 추천 이유 버튼 클릭 핸들러
  const handleAIRecommendationClick = async (talent) => {
    setSelectedTalent(talent);
    setIsAIRecommendationModalOpen(true);
    setIsLoadingAIRecommendation(true);
    setAIRecommendationData(null);

    try {
      const recommendation = await generateAIRecommendation(talent);
      setAIRecommendationData(recommendation);
    } catch (error) {
      setAIRecommendationData({
        error: true,
        message: 'AI 추천 이유를 생성하는데 실패했습니다. 다시 시도해주세요.'
      });
    } finally {
      setIsLoadingAIRecommendation(false);
    }
  };

  return (
    <TalentContainer>
      <Header>
        <Title>인재 추천</Title>
        <ActionButtons>
          <Button className="secondary">
            <FiFilter />
            필터 설정
          </Button>
          <Button className="primary">
            <FiUsers />
            추천 요청
          </Button>
        </ActionButtons>
      </Header>

      <SearchBar>
        <SearchInput
          type="text"
          placeholder="직무, 기술 스택, 경력으로 검색..."
        />
        <FilterButton>
          <FiFilter />
          필터
        </FilterButton>
      </SearchBar>

      <TalentGrid>
        {talents.map((talent, index) => (
          <TalentCard
            key={talent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <TalentHeader>
              <TalentInfo>
                <TalentName>{talent.name}</TalentName>
                <TalentPosition>{talent.position}</TalentPosition>
              </TalentInfo>
              <MatchScore score={talent.matchScore}>
                {talent.matchScore}% 매치
              </MatchScore>
            </TalentHeader>

            <TalentDetails>
              <DetailRow>
                <DetailLabel>경력:</DetailLabel>
                <DetailValue>{talent.experience}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>학력:</DetailLabel>
                <DetailValue>{talent.education}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>지역:</DetailLabel>
                <DetailValue>{talent.location}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>포트폴리오 점수:</DetailLabel>
                <DetailValue>{talent.portfolioScore}점</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>면접 점수:</DetailLabel>
                <DetailValue>{talent.interviewScore}점</DetailValue>
              </DetailRow>
            </TalentDetails>

            <SkillsList>
              <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                주요 기술:
              </div>
              {talent.skills.map((skill, sIndex) => (
                <SkillTag key={sIndex}>{skill}</SkillTag>
              ))}
            </SkillsList>

            <TalentActions>
              <ActionButton className="primary">
                <FiMessageSquare />
                연락하기
              </ActionButton>
              <ActionButton onClick={() => {
                setSelectedTalent(talent);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton onClick={() => handleAIRecommendationClick(talent)}>
                <FiZap />
                AI 추천 이유
              </ActionButton>
              <ActionButton>
                <FiDownload />
                프로필
              </ActionButton>
            </TalentActions>
          </TalentCard>
        ))}
      </TalentGrid>

      {/* 인재 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedTalent(null);
        }}
        title={selectedTalent ? `${selectedTalent.name} 인재 상세` : ''}
        onEdit={() => {
          // 수정 기능 구현
          console.log('인재 정보 수정:', selectedTalent);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('인재 정보 삭제:', selectedTalent);
        }}
      >
        {selectedTalent && (
          <>
            <DetailSection>
              <SectionTitle>기본 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>이름</DetailLabel>
                  <DetailValue>{selectedTalent.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지원 직무</DetailLabel>
                  <DetailValue>{selectedTalent.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>경력</DetailLabel>
                  <DetailValue>{selectedTalent.experience}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>학력</DetailLabel>
                  <DetailValue>{selectedTalent.education}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지역</DetailLabel>
                  <DetailValue>{selectedTalent.location}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>매치 점수</DetailLabel>
                  <DetailValue>{selectedTalent.matchScore}%</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>평가 점수</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>포트폴리오 점수</DetailLabel>
                  <DetailValue>{selectedTalent.portfolioScore}점</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>면접 점수</DetailLabel>
                  <DetailValue>{selectedTalent.interviewScore}점</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>주요 기술</SectionTitle>
              <DetailText>
                {selectedTalent.skills.map((skill, index) => (
                  <span key={index} style={{ 
                    display: 'inline-block',
                    margin: '4px',
                    padding: '4px 8px',
                    backgroundColor: '#e5e7eb',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}>
                    {skill}
                  </span>
                ))}
              </DetailText>
            </DetailSection>

            <DetailSection>
              <SectionTitle>추천 이유</SectionTitle>
              <DetailText>
                {selectedTalent.recommendationReason}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>

      {/* AI 추천 이유 모달 */}
      {isAIRecommendationModalOpen && (
        <AIRecommendationModal
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsAIRecommendationModalOpen(false);
              setAIRecommendationData(null);
              setSelectedTalent(null);
            }
          }}
        >
          <ModalContent
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", duration: 0.3 }}
          >
            <ModalHeader>
              <ModalTitle>
                <FiZap />
                AI 추천 이유
                {selectedTalent && ` - ${selectedTalent.name}`}
              </ModalTitle>
              <CloseButton
                onClick={() => {
                  setIsAIRecommendationModalOpen(false);
                  setAIRecommendationData(null);
                  setSelectedTalent(null);
                }}
              >
                <FiX />
              </CloseButton>
            </ModalHeader>
            
            <ModalBody>
              {isLoadingAIRecommendation ? (
                <LoadingSpinner />
              ) : aiRecommendationData?.error ? (
                <div style={{ 
                  color: '#dc2626', 
                  textAlign: 'center', 
                  padding: '20px',
                  fontSize: '14px'
                }}>
                  {aiRecommendationData.message}
                </div>
              ) : aiRecommendationData ? (
                <>
                  <RecommendationSection>
                    <SectionHeader>핵심 특징</SectionHeader>
                    <RecommendationText>
                      {aiRecommendationData.keyFeatures || '이 인재의 주요 특징을 분석하고 있습니다.'}
                    </RecommendationText>
                  </RecommendationSection>
                  
                  <RecommendationSection>
                    <SectionHeader>추천 이유</SectionHeader>
                    <RecommendationText>
                      {aiRecommendationData.recommendationReason || '추천 이유를 생성하고 있습니다.'}
                    </RecommendationText>
                  </RecommendationSection>
                  
                  <RecommendationSection>
                    <SectionHeader>적합성 분석</SectionHeader>
                    <RecommendationText>
                      {aiRecommendationData.fitAnalysis || '적합성을 분석하고 있습니다.'}
                    </RecommendationText>
                  </RecommendationSection>
                </>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '20px',
                  color: 'var(--text-secondary)'
                }}>
                  AI가 추천 이유를 생성 중입니다...
                </div>
              )}
            </ModalBody>
          </ModalContent>
        </AIRecommendationModal>
      )}
    </TalentContainer>
  );
};

export default TalentRecommendation; 