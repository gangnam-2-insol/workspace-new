import React, { useState, useEffect } from 'react';
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
  FiTrendingUp,
  FiUsers,
  FiChevronRight
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

// 유사인재 추천 섹션
const RecommendationSection = styled.div`
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #bae6fd;
  margin-bottom: 32px;
`;

// 추천 카드 그리드 (한 줄에 3개씩)
const RecommendationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

// 추천 카드 (가로 레이아웃)
const RecommendationCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e0f2fe;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  min-height: 200px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 123, 191, 0.15);
    border-color: #0284c7;
  }
`;

// 추천 카드 헤더
const RecommendationCardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  flex-shrink: 0;
`;

// 추천 카드 이름
const RecommendationCardName = styled.div`
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 직무 배지
const PositionBadge = styled.span`
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
`;

// 추천 점수
const RecommendationScore = styled.div`
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
`;

// 추천 카드 정보
const RecommendationCardInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  flex-shrink: 0;
`;

// 경력과 기술을 나란히 배치하는 컨테이너
const ExperienceSkillsRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 12px;
  align-items: start;
`;

// AI 추천 이유 섹션
const AIReasonSection = styled.div`
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #e0f2fe;
  flex: 1;
  overflow: hidden;
`;

// AI 추천 이유 제목
const AIReasonTitle = styled.div`
  font-size: 14px;
  color: #0284c7;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

// AI 추천 이유 아이템
const AIReasonItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.3;

  &:last-child {
    margin-bottom: 0;
  }
`;

// AI 추천 이유 아이콘
const AIReasonIcon = styled.span`
  font-size: 14px;
  margin-top: 1px;
  flex-shrink: 0;
`;

// AI 추천 이유 텍스트
const AIReasonText = styled.div`
  color: #334155;
  font-size: 13px;
  line-height: 1.4;
  
  strong {
    font-weight: 600;
    color: #1e293b;
  }
`;

// 추천 카드 라벨
const RecommendationCardLabel = styled.div`
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 2px;
`;

// 추천 카드 값
const RecommendationCardValue = styled.div`
  font-size: 12px;
  color: #334155;
  font-weight: 600;
  line-height: 1.2;
`;

// 로딩 컴포넌트
const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #64748b;
  font-size: 14px;
  
  &::before {
    content: '';
    width: 20px;
    height: 20px;
    border: 2px solid #e2e8f0;
    border-top: 2px solid #0284c7;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 12px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 에러 메시지
const ErrorMessage = styled.div`
  color: #ef4444;
  font-size: 14px;
  padding: 20px;
  text-align: center;
  background: #fef2f2;
  border-radius: 12px;
  border: 1px solid #fecaca;
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
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [recommendationsError, setRecommendationsError] = useState(null);
  const [recommendationsLoaded, setRecommendationsLoaded] = useState(false); // 한 번 로드했는지 추적

  // 유사인재 추천 API 호출
  const fetchRecommendations = async () => {
    if (!applicant || (!applicant._id && !applicant.id)) return;
    
    // 이미 로드했거나 로딩 중이면 다시 로드하지 않음
    if (recommendationsLoaded || recommendationsLoading) {
      console.log('유사인재 추천 이미 로드됨 또는 로딩 중 - 스킵');
      return;
    }
    
    setRecommendationsLoading(true);
    setRecommendationsError(null);
    
    try {
      const applicantId = applicant._id || applicant.id;
      const response = await fetch(`/api/applicants/${applicantId}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('유사인재 추천을 가져오는데 실패했습니다.');
      }

      const data = await response.json();
      
      // 백엔드 응답 구조에 맞춰 데이터 처리
      if (data.status === 'success' && data.recommendations) {
        const recommendationData = data.recommendations.data || data.recommendations;
        if (recommendationData && recommendationData.results) {
          const results = recommendationData.results.slice(0, 5); // 최대 5개
          
          // LLM 분석 결과 파싱 및 결합
          if (recommendationData.llm_analysis && recommendationData.llm_analysis.success) {
            console.log('LLM 분석 원본:', recommendationData.llm_analysis);
            const llmAnalysisText = recommendationData.llm_analysis.analysis;
            const parsedAnalysis = parseLLMAnalysis(llmAnalysisText);
            console.log('파싱된 LLM 분석:', parsedAnalysis);
            
            // LLM 분석 결과를 각 지원자와 매칭
            results.forEach((result, index) => {
              const applicantName = result.applicant.name;
              
              // 정확한 매칭 시도
              if (parsedAnalysis[applicantName]) {
                result.llm_analysis = parsedAnalysis[applicantName];
                console.log(`${applicantName}에게 LLM 분석 결과 할당:`, parsedAnalysis[applicantName]);
              } else {
                // 정확한 매칭이 안 되면 유사한 이름 찾기 (공백, 대소문자 무시)
                const normalizedApplicantName = applicantName.trim().replace(/\s+/g, '');
                const matchingKey = Object.keys(parsedAnalysis).find(key => {
                  const normalizedKey = key.trim().replace(/\s+/g, '');
                  return normalizedKey === normalizedApplicantName;
                });
                
                if (matchingKey) {
                  result.llm_analysis = parsedAnalysis[matchingKey];
                  console.log(`${applicantName}에게 LLM 분석 결과 할당 (유사 매칭: ${matchingKey}):`, parsedAnalysis[matchingKey]);
                } else {
                  console.log(`${applicantName}에 대한 LLM 분석 결과 없음. 사용 가능한 키들:`, Object.keys(parsedAnalysis));
                }
              }
            });
          } else {
            console.log('LLM 분석 결과 없음 또는 실패');
          }
          
          setRecommendations(results);
        } else {
          setRecommendations([]);
        }
      } else {
        setRecommendations([]);
      }
    } catch (error) {
      console.error('유사인재 추천 오류:', error);
      setRecommendationsError(error.message);
      setRecommendations([]);
    } finally {
      setRecommendationsLoading(false);
      setRecommendationsLoaded(true); // 성공/실패 관계없이 한 번 시도했음을 표시
    }
  };

  // applicant가 변경될 때 캐시 리셋 및 유사인재 추천 로드
  useEffect(() => {
    if (applicant && applicant._id) {
      // 새로운 지원자인 경우에만 캐시 리셋
      const currentApplicantId = applicant._id || applicant.id;
      const isNewApplicant = !recommendationsLoaded || recommendations.length === 0;
      
      if (isNewApplicant) {
        setRecommendationsLoaded(false);
        setRecommendations([]);
        setRecommendationsError(null);
        
        // 약간의 딜레이를 두어 중복 호출 방지
        const timer = setTimeout(() => {
          fetchRecommendations();
        }, 100);
        
        return () => clearTimeout(timer);
      }
    }
  }, [applicant?._id]);

  // 추천 카드 클릭 핸들러
  const handleRecommendationClick = (recommendedApplicant) => {
    // 추천된 지원자의 상세 정보를 보여주거나 다른 액션 수행
    console.log('추천 지원자 클릭:', recommendedApplicant);
  };

  // LLM 분석 결과 파싱 함수
  const parseLLMAnalysis = (analysisText) => {
    const parsed = {};
    
    try {
      // "### 3. 각 유사 지원자별 상세 분석" 섹션 찾기
      const analysisSection = analysisText.split('### 3. 각 유사 지원자별 상세 분석')[1];
      if (!analysisSection) return parsed;
      
      // 각 지원자별 분석 블록으로 분할
      const applicantBlocks = analysisSection.split(/- \*\*([^*]+)\*\*/).filter(block => block.trim());
      
      for (let i = 0; i < applicantBlocks.length; i += 2) {
        let name = applicantBlocks[i]?.trim();
        const content = applicantBlocks[i + 1];
        
        if (name && content) {
          // 대괄호 제거 (예: [박지우] → 박지우)
          name = name.replace(/^\[|\]$/g, '').trim();
          
          // 각 항목 파싱 - 여러 줄에 걸친 내용도 처리
          const coreCommon = content.match(/🔍 \*\*핵심 공통점\*\*: ([^\n]+)/)?.[1]?.trim();
          const mainFeature = content.match(/💡 \*\*주요 특징\*\*: ([^\n]+)/)?.[1]?.trim();
          
          // 추천 이유 파싱 (이제 간결한 한 줄로 작성됨)
          const recommendReasonMatch = content.match(/⭐ \*\*추천 이유\*\*: ([^🎯]+)/);
          let recommendReason = recommendReasonMatch?.[1]?.trim();
          if (recommendReason) {
            // 기준 설명 부분 제거 (괄호로 둘러싸인 부분)
            recommendReason = recommendReason.replace(/\s*\(기준:.*?\)/g, '').trim();
            
            // 따옴표 제거 (앞뒤 따옴표)
            recommendReason = recommendReason.replace(/^["']|["']$/g, '').trim();
            
            // 끝에 있는 대시(-) 제거
            recommendReason = recommendReason.replace(/\s*-\s*$/, '').trim();
            
            // 남은 텍스트에서 불필요한 공백/줄바꿈 정리
            recommendReason = recommendReason.replace(/\s+/g, ' ').trim();
            
            // 템플릿 텍스트 제거
            if (recommendReason.startsWith('[') && recommendReason.endsWith(']')) {
              recommendReason = '추천 근거를 분석 중입니다...';
            }
          }
          
          const similarityFactor = content.match(/🎯 \*\*유사성 요인\*\*: ([^\n]+)/)?.[1]?.trim();
          
          parsed[name] = {
            coreCommon: coreCommon || '분석 중...',
            mainFeature: mainFeature || '분석 중...',
            recommendReason: recommendReason || '분석 중...',
            similarityFactor: similarityFactor || '분석 중...'
          };
          
          console.log(`파싱된 지원자: "${name}"`, parsed[name]);
        }
      }
    } catch (error) {
      console.error('LLM 분석 파싱 오류:', error);
    }
    
    return parsed;
  };

  // AI 추천 이유 생성 함수
  const generateAIReasons = (recommendation, targetApplicant) => {
    console.log('generateAIReasons 호출:', recommendation);
    
    // LLM 분석 결과가 있으면 우선 사용
    if (recommendation.llm_analysis) {
      console.log('LLM 분석 결과 사용:', recommendation.llm_analysis);
      const llm = recommendation.llm_analysis;
      return [
        {
          icon: '🔍',
          label: '핵심 공통점',
          text: llm.coreCommon
        },
        {
          icon: '💡',
          label: '주요 특징',
          text: llm.mainFeature
        },
        {
          icon: '⭐',
          label: '추천 이유',
          text: llm.recommendReason
        },
        {
          icon: '🎯',
          label: '유사성 요인',
          text: llm.similarityFactor
        }
      ];
    }

    // 폴백: 기존 클라이언트 사이드 생성 로직
    const recommended = recommendation.applicant;
    const targetPosition = targetApplicant.position || '';
    const targetSkills = Array.isArray(targetApplicant.skills) ? targetApplicant.skills : 
                        typeof targetApplicant.skills === 'string' ? targetApplicant.skills.split(',') : [];
    const recommendedSkills = Array.isArray(recommended.skills) ? recommended.skills : 
                             typeof recommended.skills === 'string' ? recommended.skills.split(',') : [];
    
    // 공통 기술스택 찾기
    const commonSkills = targetSkills.filter(skill => 
      recommendedSkills.some(recSkill => recSkill.trim().toLowerCase().includes(skill.trim().toLowerCase()))
    );

    // 유사성 점수를 바탕으로 추천 이유 생성
    const score = recommendation.final_score || 0;
    const vectorScore = recommendation.vector_score || 0;
    const keywordScore = recommendation.keyword_score || 0;
    
    const reasons = [];

    // 핵심 공통점
    if (recommended.position === targetPosition) {
      reasons.push({
        icon: '🔍',
        label: '핵심 공통점',
        text: `${targetPosition} 직무로 동일한 분야 지원`
      });
    } else if (commonSkills.length > 0) {
      reasons.push({
        icon: '🔍',
        label: '핵심 공통점',
        text: `${commonSkills.slice(0, 2).join(', ')} 등 기술스택 보유`
      });
    } else {
      reasons.push({
        icon: '🔍',
        label: '핵심 공통점',
        text: '유사한 역량과 경력 보유'
      });
    }

    // 주요 특징
    const experience = recommended.experience || '경력 정보 없음';
    const position = recommended.position || '직무 미지정';
    reasons.push({
      icon: '💡',
      label: '주요 특징',
      text: `${position} • ${experience}`
    });

    // 추천 이유
    if (vectorScore > keywordScore) {
      reasons.push({
        icon: '⭐',
        label: '추천 이유',
        text: '지원자 프로필 기반 높은 유사도 매칭'
      });
    } else if (keywordScore > vectorScore) {
      reasons.push({
        icon: '⭐',
        label: '추천 이유',
        text: '이력서 내용 기반 키워드 매칭'
      });
    } else {
      reasons.push({
        icon: '⭐',
        label: '추천 이유',
        text: '프로필과 이력서 종합 분석 결과'
      });
    }

    // 유사성 요인
    if (recommendation.search_methods && recommendation.search_methods.length > 1) {
      reasons.push({
        icon: '🎯',
        label: '유사성 요인',
        text: '다중 검색 방식으로 종합 검증됨'
      });
    } else if (recommendation.search_methods && recommendation.search_methods.includes('vector')) {
      reasons.push({
        icon: '🎯',
        label: '유사성 요인',
        text: '기술스택 및 경력 유사도가 핵심'
      });
    } else {
      reasons.push({
        icon: '🎯',
        label: '유사성 요인',
        text: '이력서 내용의 키워드 일치도가 높음'
      });
    }

    return reasons;
  };

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

            {/* 유사인재 추천 섹션 */}
            <RecommendationSection>
              <SectionTitle>
                <FiUsers size={20} />
                유사인재 추천
              </SectionTitle>

              {recommendationsLoading && (
                <LoadingSpinner>
                  유사한 인재를 찾고 있습니다...
                </LoadingSpinner>
              )}

              {recommendationsError && (
                <ErrorMessage>
                  {recommendationsError}
                </ErrorMessage>
              )}

              {!recommendationsLoading && !recommendationsError && recommendations.length > 0 && (
                <RecommendationGrid>
                  {recommendations.map((recommendation, index) => (
                    <RecommendationCard 
                      key={recommendation.applicant._id || index}
                      onClick={() => handleRecommendationClick(recommendation.applicant)}
                    >
                      <RecommendationCardHeader>
                        <RecommendationCardName>
                          <span>{recommendation.applicant.name || '이름 없음'}</span>
                          {recommendation.applicant.position && (
                            <PositionBadge>{recommendation.applicant.position}</PositionBadge>
                          )}
                        </RecommendationCardName>
                        <RecommendationScore>
                          {Math.round((recommendation.final_score || 0) * 100)}%
                        </RecommendationScore>
                      </RecommendationCardHeader>
                      
                      <RecommendationCardInfo>
                        <ExperienceSkillsRow>
                          <div>
                            <RecommendationCardLabel>경력</RecommendationCardLabel>
                            <RecommendationCardValue>
                              {recommendation.applicant.experience || '정보 없음'}
                            </RecommendationCardValue>
                          </div>
                          
                          {recommendation.applicant.skills && (
                            <div>
                              <RecommendationCardLabel>주요 기술</RecommendationCardLabel>
                              <RecommendationCardValue>
                                {Array.isArray(recommendation.applicant.skills) 
                                  ? recommendation.applicant.skills.slice(0, 2).join(', ')
                                  : typeof recommendation.applicant.skills === 'string'
                                  ? recommendation.applicant.skills.split(',').slice(0, 2).join(', ')
                                  : '기술스택 정보 없음'
                                }
                                {((Array.isArray(recommendation.applicant.skills) && recommendation.applicant.skills.length > 2) ||
                                  (typeof recommendation.applicant.skills === 'string' && recommendation.applicant.skills.split(',').length > 2)) && 
                                  ' 외'}
                              </RecommendationCardValue>
                            </div>
                          )}
                        </ExperienceSkillsRow>
                        
                      </RecommendationCardInfo>

                      {/* AI 추천 이유 섹션 */}
                      <AIReasonSection>
                        <AIReasonTitle>
                          <FiBarChart2 size={14} />
                          AI 인재 추천 이유
                        </AIReasonTitle>
                        {generateAIReasons(recommendation, applicant).map((reason, reasonIndex) => (
                          <AIReasonItem key={reasonIndex}>
                            <AIReasonIcon>{reason.icon}</AIReasonIcon>
                            <AIReasonText>
                              <strong>{reason.label}:</strong> {reason.text}
                            </AIReasonText>
                          </AIReasonItem>
                        ))}
                      </AIReasonSection>
                    </RecommendationCard>
                  ))}
                </RecommendationGrid>
              )}

              {!recommendationsLoading && !recommendationsError && recommendations.length === 0 && (
                <div style={{ 
                  padding: '40px', 
                  textAlign: 'center', 
                  color: '#64748b',
                  background: 'white',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0'
                }}>
                  유사한 인재를 찾을 수 없습니다.
                </div>
              )}
            </RecommendationSection>

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
                 자소서 표절 의심도 검사
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
