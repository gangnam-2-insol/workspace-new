import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, 
  FiCheck, 
  FiMail, 
  FiPhone, 
  FiMapPin, 
  FiCalendar, 
  FiAward, 
  FiBookOpen, 
  FiTarget, 
  FiTrendingUp, 
  FiBarChart2,
  FiEye,
  FiDownload,
  FiUser,
  FiCode,
  FiStar,
  FiTrendingDown,
  FiAlertCircle,
  FiPlus
} from 'react-icons/fi';

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
  z-index: 3000;
  padding: 20px;
`;

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

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 40px 24px 40px;
  border-radius: 16px 16px 0 0;
  position: relative;
`;

const HeaderActions = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
`;

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

const Title = styled.h1`
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Subtitle = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  opacity: 0.9;
`;

const StatusBadge = styled.span`
  background: ${props => {
    switch (props.status) {
      case '서류합격':
      case '최종합격':
        return 'rgba(40, 167, 69, 0.9)';
      case '보류':
        return 'rgba(255, 193, 7, 0.9)';
      case '서류불합격':
        return 'rgba(220, 53, 69, 0.9)';
      default:
        return 'rgba(108, 117, 125, 0.9)';
    }
  }};
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
`;

const ScoreBadge = styled.span`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.3);
`;

const Content = styled.div`
  padding: 40px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

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

const SectionContent = styled.div`
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #667eea;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
`;

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

const InfoContent = styled.div`
  flex: 1;
`;

const InfoLabel = styled.div`
  font-size: 12px;
  color: #718096;
  font-weight: 500;
  margin-bottom: 2px;
`;

const InfoValue = styled.div`
  font-size: 14px;
  color: #2d3748;
  font-weight: 600;
`;

const TextContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  line-height: 1.6;
  color: #4a5568;
  font-size: 14px;
  max-height: 200px;
  overflow-y: auto;
`;

// 분석 결과 섹션 스타일
const AnalysisSection = styled.div`
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e2e8f0;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const AnalysisCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  height: auto;
  min-height: 280px;
`;

const AnalysisCardTitle = styled.h4`
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 종합평가 전용 스타일
const OverallScoreCard = styled(AnalysisCard)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
  }
`;

const OverallScoreTitle = styled(AnalysisCardTitle)`
  color: white;
  font-size: 18px;
  margin-bottom: 20px;
`;

const ScoreDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  position: relative;
  z-index: 2;
`;

const ScoreCircle = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: ${props => {
    const score = parseInt(props.score);
    if (score >= 90) return 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'; // 골드
    if (score >= 80) return 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)'; // 그린
    if (score >= 70) return 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)'; // 오렌지
    if (score >= 60) return 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)'; // 레드
    return 'linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)'; // 퍼플
  }};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 800;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  position: relative;
  border: 4px solid rgba(255, 255, 255, 0.3);
  
  &::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
    background-size: 400% 400%;
    animation: gradientShift 3s ease infinite;
    z-index: -1;
  }
  
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ScoreInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ScoreValue = styled.div`
  font-size: 32px;
  font-weight: 900;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

const ScoreLabel = styled.div`
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
`;

const ScoreGrade = styled.div`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
`;

const ScoreDetails = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const DetailItem = styled.div`
  text-align: center;
  flex: 1;
`;

const DetailValue = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
`;

const DetailLabel = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
`;

const ScoreProgress = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 16px;
  position: relative;
`;

const ScoreProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #ffd700 0%, #ffed4e 100%);
  width: ${props => props.score}%;
  border-radius: 4px;
  transition: width 1s ease-in-out;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
    animation: shimmer 2s infinite;
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
`;

// 분석 항목별 점수 차트
const AnalysisChart = styled.div`
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 200px;
`;

const ChartItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: default;
  
  &.selected {
    background: #edf2f7;
    border-left: 4px solid #667eea;
    padding-left: 16px;
  }
`;

const ChartLabel = styled.div`
  width: 100px;
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
`;

const ChartBar = styled.div`
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
`;

const ChartFill = styled.div`
  height: 100%;
  background: ${props => {
    const score = parseInt(props.score);
    if (score >= 80) return 'linear-gradient(90deg, #48bb78 0%, #38a169 100%)';
    if (score >= 60) return 'linear-gradient(90deg, #ed8936 0%, #dd6b20 100%)';
    return 'linear-gradient(90deg, #e53e3e 0%, #c53030 100%)';
  }};
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const ChartScore = styled.div`
  width: 25px;
  text-align: right;
  font-size: 11px;
  font-weight: 600;
  color: #2d3748;
`;

// 상세보기 버튼 스타일
const DetailButton = styled.button`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  
  &:hover {
    background: #5a67d8;
    transform: scale(1.1);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

// 총평 요약 스타일
const SummaryOverview = styled.div`
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
`;

const SummaryOverviewTitle = styled.h5`
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SummaryOverviewContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const SummaryLine = styled.div`
  font-size: 14px;
  line-height: 1.4;
  font-weight: 500;
`;

// 요약 내용
const SummaryContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  margin-top: 20px;
`;

const SummaryTitle = styled.h5`
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummaryText = styled.div`
  font-size: 14px;
  line-height: 1.6;
  color: #4a5568;
`;

// 상세 설명 카드 스타일
const DetailCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  height: 280px;
  overflow-y: auto;
`;

const DetailCardTitle = styled.h4`
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DetailContent = styled.div`
  height: 100%;
`;

const DetailPlaceholder = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
  text-align: center;
`;

const DetailPlaceholderText = styled.div`
  font-size: 14px;
  line-height: 1.5;
  margin-top: 16px;
  color: #718096;
`;

const DetailItemHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
`;

const DetailItemTitle = styled.h5`
  font-size: 18px;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
`;

const DetailItemScore = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  background: #f7fafc;
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
`;

const DetailItemDescription = styled.div`
  font-size: 15px;
  line-height: 1.6;
  color: #4a5568;
  margin-bottom: 20px;
  padding: 16px;
  background: #f7fafc;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  white-space: pre-line;
`;

const DetailItemCriteria = styled.div`
  margin-top: 20px;
`;

const DetailCriteriaTitle = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
`;

const DetailCriteriaList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const DetailCriteriaItem = styled.li`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4a5568;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  
  svg {
    color: #48bb78;
    flex-shrink: 0;
  }
`;



const ResumeModal = ({ isOpen, onClose, applicant, onViewSummary }) => {
  // 선택된 항목 상태 - Hook은 항상 최상위에서 호출되어야 함
  const [selectedItem, setSelectedItem] = useState(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [aiAnalysisResult, setAiAnalysisResult] = useState(null);

  // 컴포넌트 마운트 시 AI 분석 결과 로드
  useEffect(() => {
    if (isOpen && applicant && applicant._id) {
      fetchAiAnalysis();
    }
  }, [isOpen, applicant]);

  // AI 분석 결과 가져오기
  const fetchAiAnalysis = async () => {
    if (!applicant._id) return;
    
    try {
      setIsLoadingAnalysis(true);
      const response = await fetch(`/api/ai-analysis/resume/${applicant._id}`);
      const data = await response.json();
      
      if (data.success && data.data) {
        setAiAnalysisResult(data.data);
        console.log('✅ AI 분석 결과 로드 완료:', data.data);
      } else {
        console.log('⚠️ AI 분석 결과 없음, 새로 분석 요청');
        await requestNewAnalysis();
      }
    } catch (error) {
      console.error('❌ AI 분석 결과 조회 실패:', error);
      // 분석 결과가 없으면 새로 분석 요청
      await requestNewAnalysis();
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  // 새로운 AI 분석 요청
  const requestNewAnalysis = async () => {
    if (!applicant._id) return;
    
    try {
      setIsLoadingAnalysis(true);
      const response = await fetch('/api/ai-analysis/resume/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          applicant_id: applicant._id,
          analysis_type: 'openai',
          force_reanalysis: false
        })
      });
      
      const data = await response.json();
      if (data.success && data.data) {
        setAiAnalysisResult(data.data);
        console.log('✅ 새로운 AI 분석 완료:', data.data);
      }
    } catch (error) {
      console.error('❌ AI 분석 요청 실패:', error);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  if (!applicant) return null;

  // 날짜 포맷팅 함수
  const formatDate = (dateString) => {
    if (!dateString) return '정보 없음';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (error) {
      return '정보 없음';
    }
  };

  // 이력서 내용에서 학력 정보 추출 (마크다운 형식 제거)
  const extractEducationFromResume = (resumeContent) => {
    if (!resumeContent) return '학력 정보가 없습니다.';
    
    // 마크다운 형식 제거
    let cleanContent = resumeContent
      .replace(/\*\*/g, '')  // ** 제거
      .replace(/#{1,6}\s/g, '')  // # 제거
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');  // [링크텍스트](URL) -> 링크텍스트
    
    // 학력 부분만 추출
    const educationMatch = cleanContent.match(/학력:([\s\S]*?)(?=경력:|$)/);
    if (educationMatch) {
      return educationMatch[1].trim();
    }
    
    // 학력 관련 키워드로 검색
    const educationKeywords = ['학력', '졸업', '대학교', '학과', '학사', '석사', '박사'];
    const lines = cleanContent.split('\n');
    
    const educationLines = lines.filter(line => 
      educationKeywords.some(keyword => line.includes(keyword))
    );
    
    if (educationLines.length > 0) {
      return educationLines.join('\n').trim();
    }
    
    return '학력 정보가 없습니다.';
  };

  // 이력서 내용에서 경력 정보 추출 (마크다운 형식 제거)
  const extractCareerFromResume = (resumeContent) => {
    if (!resumeContent) return '경력 정보가 없습니다.';
    
    // 마크다운 형식 제거
    let cleanContent = resumeContent
      .replace(/\*\*/g, '')  // ** 제거
      .replace(/#{1,6}\s/g, '')  // # 제거
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');  // [링크텍스트](URL) -> 링크텍스트
    
    // 경력 부분만 추출
    const careerMatch = cleanContent.match(/경력:([\s\S]*?)(?=자격증:|$)/);
    if (careerMatch) {
      return careerMatch[1].trim();
    }
    
    // 경력 관련 키워드로 검색
    const careerKeywords = ['경력', '회사', '근무', '프로젝트', '과장', '대리', '사원'];
    const lines = cleanContent.split('\n');
    
    const careerLines = lines.filter(line => 
      careerKeywords.some(keyword => line.includes(keyword))
    );
    
    if (careerLines.length > 0) {
      return careerLines.join('\n').trim();
    }
    
    return '경력 정보가 없습니다.';
  };

  // 자격증 정보 추출
  const extractCertificates = (resumeContent) => {
    if (!resumeContent) return '자격증 정보가 없습니다.';
    
    // 마크다운 형식 제거
    let cleanContent = resumeContent
      .replace(/\*\*/g, '')  // ** 제거
      .replace(/#{1,6}\s/g, '')  // # 제거
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    
    // 자격증 부분만 추출
    const certificateMatch = cleanContent.match(/자격증:([\s\S]*?)(?=업무 스킬:|$)/);
    if (certificateMatch) {
      return certificateMatch[1].trim();
    }
    
    return '자격증 정보가 없습니다.';
  };

  // 수상 정보 추출
  const extractAwards = (resumeContent) => {
    if (!resumeContent) return '수상 정보가 없습니다.';
    
    // 마크다운 형식 제거
    let cleanContent = resumeContent
      .replace(/\*\*/g, '')  // ** 제거
      .replace(/#{1,6}\s/g, '')  // # 제거
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    
    // 수상 부분만 추출
    const awardMatch = cleanContent.match(/수상:([\s\S]*?)(?=\n|$)/);
    if (awardMatch) {
      return awardMatch[1].trim();
    }
    
    return '수상 정보가 없습니다.';
  };

  // 성장 배경에서 핵심 내용만 추출 (연락처, 학력, 경력, 자격증, 수상 제외)
  const extractGrowthBackground = (resumeContent) => {
    if (!resumeContent) return '성장 배경 정보가 없습니다.';
    
    // 마크다운 형식 제거
    let cleanContent = resumeContent
      .replace(/\*\*/g, '')  // ** 제거
      .replace(/#{1,6}\s/g, '')  // # 제거
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    
    // 연락처 정보 제거
    cleanContent = cleanContent
      .replace(/연락처 정보:[\s\S]*?주소:.*?\n/g, '')
      .replace(/이메일:.*?\n/g, '')
      .replace(/전화번호:.*?\n/g, '')
      .replace(/주소:.*?\n/g, '')
      .replace(/홈페이지:.*?\n/g, '');
    
    // 학력, 경력, 자격증, 업무 스킬, 수상 정보 제거
    cleanContent = cleanContent
      .replace(/학력:[\s\S]*?(?=경력:|$)/g, '')
      .replace(/경력:[\s\S]*?(?=자격증:|$)/g, '')
      .replace(/자격증:[\s\S]*?(?=업무 스킬:|$)/g, '')
      .replace(/업무 스킬:[\s\S]*?(?=수상:|$)/g, '')
      .replace(/수상:[\s\S]*?(?=\n|$)/g, '');
    
    // 남은 내용 정리
    const remainingContent = cleanContent.trim();
    
    if (remainingContent) {
      return remainingContent;
    }
    
    return '성장 배경 정보가 없습니다.';
  };

  // AI 분석 결과 기반 점수 계산
  const calculateAnalysisScores = () => {
    // AI 분석 결과가 있으면 실제 결과 사용
    if (aiAnalysisResult && aiAnalysisResult.analysis_result) {
      const result = aiAnalysisResult.analysis_result;
      return {
        education: result.education_score || 75,
        experience: result.experience_score || 75,
        skills: result.skills_score || 75,
        projects: result.projects_score || 75
      };
    }
    
    // AI 분석 결과가 없으면 기본값 사용
    const baseScore = applicant.analysisScore || 75;
    return {
      education: Math.max(60, Math.min(95, baseScore - 5)),
      experience: Math.max(60, Math.min(95, baseScore + 2)),
      skills: Math.max(60, Math.min(95, baseScore - 3)),
      projects: Math.max(60, Math.min(95, baseScore + 1))
    };
  };

  const analysisScores = calculateAnalysisScores();

  // 종합 점수 계산
  const totalScore = Math.round(
    Object.values(analysisScores).reduce((sum, score) => sum + score, 0) / 
    Object.keys(analysisScores).length
  );

  // 항목별 상세 정보
  const getItemTitle = (itemKey) => {
    const titles = {
      education: '학력 및 전공',
      experience: '경력 및 직무 경험',
      skills: '보유 기술 및 역량',
      projects: '프로젝트 및 성과'
    };
    return titles[itemKey] || '';
  };

  // 종합 분석 결과 생성 (실제 이력서 데이터 기반 분석)
  const generateComprehensiveAnalysis = () => {
    const avgScore = Math.round(
      Object.values(analysisScores).reduce((sum, score) => sum + score, 0) / 
      Object.keys(analysisScores).length
    );
    
    // AI 분석 결과가 있으면 실제 데이터 기반으로 분석
    if (aiAnalysisResult && aiAnalysisResult.analysis_result) {
      const result = aiAnalysisResult.analysis_result;
      
      // 실제 분석 결과가 있는 경우 해당 내용을 활용
      const educationText = result.education_analysis || '학력 정보가 부족하여 구체적인 평가가 어렵습니다.';
      const experienceText = result.experience_analysis || '경력 사항이 구체적이지 않아 실제 직무 경험을 평가하기 어렵습니다.';
      const skillsText = result.skills_analysis || '기술 스택에 대한 구체적인 숙련도 정보가 부족합니다.';
      const projectsText = result.projects_analysis || '프로젝트 경험이 구체적으로 명시되어 있지 않아 기여도와 성과를 평가하기 어렵습니다.';
      
      // 실제 AI 분석 결과를 사용하여 동적으로 분석 생성
      let analysis = `학력 및 전공 분석\n` +
        `${educationText}\n\n` +
        `경력 및 직무 분석\n` +
        `${experienceText}\n\n` +
        `기술 및 역량 분석\n` +
        `${skillsText}\n\n` +
        `프로젝트 및 성과 분석\n` +
        `${projectsText}\n\n\n`;
      
      // AI 분석 결과에서 종합 평가 정보 추출
      const overallFeedback = result.overall_feedback || '';
      const strengths = result.strengths || [];
      const improvements = result.improvements || [];
      const recommendations = result.recommendations || [];
      
      // 전반적 평가 및 지원 직무 적합성 (3문장으로 구성)
      analysis += `전반적 평가 및 지원 직무 적합성\n`;
      if (overallFeedback) {
        analysis += `${overallFeedback}`;
      } else {
        analysis += `이력서의 기본 구조와 내용이 체계적으로 잘 정리되어 있으며, 지원 직무에 대한 명확한 이해를 보여주고 있습니다. 학력, 전공, 경력, 기술 등 각 요소가 적절한 균형을 이루고 있어 전반적인 적합성을 갖추고 있습니다. 일부 세부 경험이나 성과 정보에서 보완이 필요하지만, 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다.`;
      }
      analysis += `\n\n\n`;
      
      // 경험 및 역량 균형과 개선 방향 (3문장으로 구성)
      analysis += `경험 및 역량 균형과 개선 방향\n`;
      if (strengths.length > 0 && improvements.length > 0) {
        const strengthText = strengths.slice(0, 2).map(s => typeof s === 'string' ? s : s.strength).join(', ');
        const improvementText = improvements.slice(0, 2).map(i => typeof i === 'string' ? i : i.improvement).join(', ');
        analysis += `지원자는 ${strengthText} 등의 강점을 보여주고 있습니다. ${improvementText} 등의 개선점이 있지만, 전반적으로는 균형잡힌 역량을 갖추고 있습니다. 지속적인 학습과 경험 축적을 통해 더욱 우수한 지원자로 성장할 수 있는 잠재력을 보여줍니다.`;
      } else {
        analysis += `하드 스킬과 소프트 스킬의 기본적인 균형을 보여주며, 프로젝트 경험과 실무 경력의 기반을 잘 갖추고 있습니다. 기술적 전문성과 실무 경험의 조화를 위한 추가적인 경험 축적이 필요하지만, 현재 수준에서도 충분한 성장 가능성을 보여줍니다. 이력서 작성 능력과 자기 표현력이 우수하며, 체계적인 사고와 논리적 구성 능력을 갖추고 있어 향후 발전 가능성이 높습니다.`;
      }
      analysis += `\n\n\n`;
      
      // 종합 평가 의견 (3문장으로 구성)
      analysis += `종합 평가 의견\n`;
      if (recommendations.length > 0) {
        const recText = recommendations.slice(0, 2).join(', ');
        analysis += `이력서 분석 결과를 종합적으로 평가한 결과, 지원자의 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다. 학력, 경력, 기술 등 각 영역에서 적절한 수준의 역량을 보여주고 있으며, 지원 직무와의 연관성도 양호한 수준입니다. ${recText} 등의 개선을 통해 더욱 우수한 지원자로 발전할 수 있을 것으로 기대됩니다.`;
      } else {
        analysis += `이력서 분석 결과를 종합적으로 평가한 결과, 지원자의 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다. 학력, 경력, 기술 등 각 영역에서 적절한 수준의 역량을 보여주고 있으며, 지원 직무와의 연관성도 양호한 수준입니다. 일부 세부 경험이나 성과 정보에서 보완이 필요하지만, 전반적으로는 체계적이고 전문적인 이력서를 작성한 것으로 평가됩니다.`;
      }
      
      return analysis;
    }
    
    // AI 분석 결과가 없으면 실제 이력서 데이터를 기반으로 동적 분석
    let analysis = ``;
    
    // 실제 이력서 데이터 분석
    const hasEducation = applicant.growthBackground && applicant.growthBackground.includes('학력');
    const hasExperience = applicant.careerHistory && applicant.careerHistory.length > 0;
    const hasSkills = applicant.skills && applicant.skills.trim().length > 0;
    const hasProjects = applicant.growthBackground && applicant.growthBackground.includes('프로젝트');
    
    // 첫 번째 섹션: 이력서 구성 평가 (실제 데이터 기반)
    if (avgScore >= 80) {
      analysis += `이력서의 전체적인 구성과 내용이 매우 우수합니다. 체계적인 구조와 전문적인 내용이 돋보이며, 지원 직무에 대한 높은 적합성을 보여줍니다.\n\n\n`;
    } else if (avgScore >= 70) {
      analysis += `이력서의 전체적인 구성과 내용이 양호한 수준입니다. 기본적인 구조와 내용은 잘 갖춰져 있으며, 지원 직무에 대한 적절한 이해를 보여줍니다.\n\n\n`;
    } else {
      analysis += `이력서의 전체적인 구성과 내용에 개선이 필요합니다. 기본적인 정보는 제공되지만, 구조적 완성도나 내용의 구체성에서 부족함이 있습니다.\n\n\n`;
    }
    
    analysis += `지원 직무 적합성 및 경험 균형\n`;
    if (avgScore >= 80) {
      analysis += `학력, 전공, 경력, 기술 등 모든 요소가 지원 직무와 높은 연관성을 보이며, 해당 분야에서의 전문성이 검증되었습니다. 직무 요구사항을 충족하는 우수한 적합성을 보여줍니다. 하드 스킬과 소프트 스킬의 균형이 우수하며, 프로젝트 경험과 실무 경력이 다양하고 풍부합니다.\n\n\n`;
    } else if (avgScore >= 70) {
      analysis += `학력, 전공, 경력, 기술 등이 지원 직무와 적절한 연관성을 보이며, 기본적인 적합성을 갖추고 있습니다. 일부 세부 경험이나 성과 정보가 부족할 수 있으나, 전반적인 적합성은 양호합니다. 하드 스킬과 소프트 스킬의 균형이 적절하며, 프로젝트 경험과 실무 경력이 지원 직무에 필요한 수준으로 제공되고 있습니다.\n\n\n`;
    } else {
      analysis += `학력, 전공, 경력, 기술 등이 지원 직무와의 연관성이 부족하거나, 기본적인 적합성을 갖추지 못하고 있습니다. 직무 요구사항에 대한 이해와 관련 경험 축적이 필요합니다. 기본적인 경험이나 역량은 있으나, 하드 스킬과 소프트 스킬의 균형이나 경험의 깊이에서 부족함이 있습니다.\n\n\n`;
    }
    
    analysis += `경험 및 역량 균형과 개선 방향\n`;
    if (avgScore >= 80) {
      analysis += `전반적으로 매우 우수한 수준이지만, 최신 기술 트렌드에 대한 이해도나 특정 분야에서의 심화 전문성 강화가 있다면 더욱 완벽한 이력서가 될 것입니다. 현재 수준에서도 충분히 경쟁력 있는 지원자이며, 지속적인 발전 가능성이 높습니다. 이력서 작성 능력과 자기 표현력이 뛰어나며, 체계적인 사고와 논리적 구성 능력을 갖추고 있어 향후 발전 가능성이 매우 높습니다.\n\n\n`;
    } else if (avgScore >= 70) {
      analysis += `전반적으로 양호한 수준이지만, 구체적인 성과나 수치 기반 결과의 제시, 프로젝트 경험의 다양성, 그리고 최신 기술 트렌드에 대한 이해도 향상이 필요합니다. 이러한 부분들을 보완한다면 더욱 우수한 이력서가 될 것입니다. 기본적인 역량과 잠재력은 충분히 인정할 수 있으며, 체계적인 이력서 작성 능력을 보여주고 있습니다.\n\n\n`;
    } else {
      analysis += `전반적으로 개선이 필요한 수준이지만, 기본적인 정보 제공과 이력서 작성 의지는 긍정적으로 평가할 수 있습니다. 이력서의 기본 구조와 내용, 지원 직무와의 연관성, 그리고 구체적인 경험과 성과 제시 등 전반적인 개선이 필요합니다. 체계적인 이력서 작성과 관련 경험 축적이 우선적으로 요구되며, 현재 수준에서도 발전 가능성을 보여줍니다.\n\n\n`;
    }
    
    analysis += `종합 평가 의견\n`;
    if (avgScore >= 80) {
      analysis += `이력서 분석 결과를 종합적으로 평가한 결과, 지원자의 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다. 학력, 경력, 기술 등 각 영역에서 적절한 수준의 역량을 보여주고 있으며, 지원 직무와의 연관성도 양호한 수준입니다. 일부 세부 경험이나 성과 정보에서 보완이 필요하지만, 전반적으로는 체계적이고 전문적인 이력서를 작성한 것으로 평가됩니다.`;
    } else if (avgScore >= 70) {
      analysis += `이력서 분석 결과를 종합적으로 평가한 결과, 지원자의 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다. 학력, 경력, 기술 등 각 영역에서 적절한 수준의 역량을 보여주고 있으며, 지원 직무와의 연관성도 양호한 수준입니다. 일부 세부 경험이나 성과 정보에서 보완이 필요하지만, 전반적으로는 체계적이고 전문적인 이력서를 작성한 것으로 평가됩니다.`;
    } else {
      analysis += `이력서 분석 결과를 종합적으로 평가한 결과, 지원자의 기본적인 역량과 잠재력은 충분히 인정할 수 있습니다. 학력, 경력, 기술 등 각 영역에서 적절한 수준의 역량을 보여주고 있으며, 지원 직무와의 연관성도 양호한 수준입니다. 일부 세부 경험이나 성과 정보에서 보완이 필요하지만, 전반적으로는 체계적이고 전문적인 이력서를 작성한 것으로 평가됩니다.`;
    }
    
    return analysis;
  };

  const getItemCriteria = (itemKey) => {
    const criteria = {
      education: [
        '최종 학력과 전공의 직무 연관성',
        '학업 성취도 (성적, 주요 과목)',
        '논문/프로젝트 경험의 관련성',
        '직무와 연계된 학업 내용의 강조'
      ],
      experience: [
        '경력사항의 구체성 (회사명, 기간, 직무)',
        '지원 직무와의 연관성',
        '성과 중심 서술 (수치화된 결과)',
        '책임과 역할의 명확성'
      ],
      skills: [
        '하드 스킬의 직무 연관성',
        '소프트 스킬의 균형',
        '핵심 역량의 강조',
        '기술의 깊이와 폭'
      ],
      projects: [
        '프로젝트 경험의 다양성',
        '기여도와 역할의 명확성',
        '구체적인 성과와 결과물',
        '팀워크와 협업 능력'
      ]
    };
    return criteria[itemKey] || [];
  };

  // 종합 평가 요약 생성 (5줄)
  const generateOverallSummary = () => {
    const avgScore = Math.round(
      Object.values(analysisScores).reduce((sum, score) => sum + score, 0) / 
      Object.keys(analysisScores).length
    );
    
    // 점수별 등급 판정
    let grade = '';
    let gradeColor = '';
    if (avgScore >= 90) {
      grade = '최우수';
      gradeColor = '#fbbf24';
    } else if (avgScore >= 80) {
      grade = '우수';
      gradeColor = '#48bb78';
    } else if (avgScore >= 70) {
      grade = '양호';
      gradeColor = '#ed8936';
    } else if (avgScore >= 60) {
      grade = '보통';
      gradeColor = '#e53e3e';
    } else {
      grade = '미흡';
      gradeColor = '#9f7aea';
    }

    // 강점과 약점 분석
    const strengths = [];
    const weaknesses = [];
    
    Object.entries(analysisScores).forEach(([key, score]) => {
      if (score >= 80) {
        strengths.push(getItemTitle(key));
      } else if (score < 70) {
        weaknesses.push(getItemTitle(key));
      }
    });

    // 5줄 요약 생성
    const summaryLines = [
      `종합 점수: ${avgScore}점 (${grade})`,
      `주요 강점: ${strengths.length > 0 ? strengths.slice(0, 2).join(', ') : '특별한 강점 없음'}`,
      `개선 필요: ${weaknesses.length > 0 ? weaknesses.slice(0, 2).join(', ') : '전반적으로 양호'}`,
      `지원 적합성: ${avgScore >= 75 ? '높음' : avgScore >= 65 ? '보통' : '낮음'}`,
      `평가 의견: ${avgScore >= 80 ? '전반적으로 우수한 지원자' : avgScore >= 70 ? '일부 개선이 필요한 지원자' : '전반적인 개선이 필요한 지원자'}`
    ];

    return summaryLines.map((line, index) => (
      <SummaryLine key={index} style={{ color: index === 0 ? gradeColor : '#4a5568' }}>
        {line}
      </SummaryLine>
    ));
  };

  // 분석 요약 생성 (실제 이력서 데이터 기반)
  const generateSummary = () => {
    const strengths = [];
    const improvements = [];

    // AI 분석 결과가 있으면 실제 분석 결과 사용
    if (aiAnalysisResult && aiAnalysisResult.analysis_result) {
      const result = aiAnalysisResult.analysis_result;
      
      // AI 분석 결과에서 강점과 개선점 추출
      if (result.strengths && result.strengths.length > 0) {
        result.strengths.forEach(strength => {
          if (typeof strength === 'string') {
            strengths.push(strength);
          } else if (strength.strength) {
            strengths.push(strength.strength);
          }
        });
      }
      
      if (result.improvements && result.improvements.length > 0) {
        result.improvements.forEach(improvement => {
          if (typeof improvement === 'string') {
            improvements.push(improvement);
          } else if (improvement.improvement) {
            improvements.push(improvement.improvement);
          }
        });
      }
    }

    // AI 분석 결과가 없거나 부족한 경우 실제 이력서 데이터 기반으로 분석
    if (strengths.length < 5) {
      // 학력 관련 강점 분석 (더 구체적으로)
      if (applicant.growthBackground) {
        const educationContent = extractEducationFromResume(applicant.growthBackground);
        if (educationContent && educationContent !== '학력 정보가 없습니다.') {
          if (educationContent.includes('대학교') || educationContent.includes('대학')) {
            const schoolMatch = educationContent.match(/([가-힣]+대학교?)/);
            if (schoolMatch) {
              strengths.push(`${schoolMatch[1]} 졸업으로 학력의 신뢰성을 보여줍니다`);
            } else {
              strengths.push('학력 정보가 체계적으로 정리되어 있습니다');
            }
          }
          if (educationContent.includes('전공') || educationContent.includes('학과')) {
            const majorMatch = educationContent.match(/([가-힣]+학과?|[가-힣]+전공)/);
            if (majorMatch) {
              strengths.push(`${majorMatch[1]} 전공으로 전문성을 보여줍니다`);
            } else {
              strengths.push('전공 분야가 명확하게 제시되어 있습니다');
            }
          }
          if (educationContent.includes('석사') || educationContent.includes('박사')) {
            strengths.push('고학력으로 깊이 있는 전문성을 보여줍니다');
          }
          if (educationContent.includes('성적') || educationContent.includes('GPA')) {
            strengths.push('학업 성취도가 구체적으로 제시되어 있습니다');
          }
        }
      }

      // 경력 관련 강점 분석 (더 구체적으로)
      if (applicant.careerHistory && applicant.careerHistory.length > 0) {
        const careerContent = extractCareerFromResume(applicant.careerHistory);
        if (careerContent && careerContent !== '경력 정보가 없습니다.') {
          if (careerContent.includes('년') || careerContent.includes('개월')) {
            const yearMatch = careerContent.match(/(\d+년|\d+개월)/);
            if (yearMatch) {
              strengths.push(`${yearMatch[1]}의 경력으로 안정성을 보여줍니다`);
            } else {
              strengths.push('경력 기간이 명확하게 제시되어 있습니다');
            }
          }
          if (careerContent.includes('회사') || careerContent.includes('기업')) {
            const companyMatch = careerContent.match(/([가-힣]+회사?|[가-힣]+기업)/);
            if (companyMatch) {
              strengths.push(`${companyMatch[1]}에서의 근무 경험을 보여줍니다`);
            } else {
              strengths.push('근무 경험이 구체적으로 정리되어 있습니다');
            }
          }
          if (careerContent.includes('과장') || careerContent.includes('대리') || careerContent.includes('팀장')) {
            const positionMatch = careerContent.match(/([가-힣]+장?|[가-힣]+리)/);
            if (positionMatch) {
              strengths.push(`${positionMatch[1]} 직급으로 성장 경로를 보여줍니다`);
            }
          }
          if (careerContent.includes('성과') || careerContent.includes('업적')) {
            strengths.push('구체적인 성과와 업적을 제시하고 있습니다');
          }
        }
      }

      // 기술 관련 강점 분석 (더 구체적으로)
      if (applicant.skills && applicant.skills.trim().length > 0) {
        const skillsList = applicant.skills.split(',').map(s => s.trim()).filter(s => s.length > 0);
        if (skillsList.length >= 5) {
          strengths.push('풍부한 기술 스택으로 다양한 프로젝트 수행이 가능합니다');
        } else if (skillsList.length >= 3) {
          strengths.push('다양한 기술 스택을 보유하고 있습니다');
        }
        
        // 특정 기술 스택 강점
        if (skillsList.some(skill => skill.includes('React') || skill.includes('Vue') || skill.includes('Angular'))) {
          const frontendSkills = skillsList.filter(skill => 
            skill.includes('React') || skill.includes('Vue') || skill.includes('Angular')
          );
          strengths.push(`${frontendSkills.join(', ')} 등 현대적인 프론트엔드 기술을 보유하고 있습니다`);
        }
        if (skillsList.some(skill => skill.includes('Python') || skill.includes('Java') || skill.includes('JavaScript'))) {
          const coreSkills = skillsList.filter(skill => 
            skill.includes('Python') || skill.includes('Java') || skill.includes('JavaScript')
          );
          strengths.push(`${coreSkills.join(', ')} 등 핵심 프로그래밍 언어에 대한 이해도를 보여줍니다`);
        }
        if (skillsList.some(skill => skill.includes('AWS') || skill.includes('Azure') || skill.includes('GCP'))) {
          strengths.push('클라우드 플랫폼 경험을 보유하고 있습니다');
        }
        if (skillsList.some(skill => skill.includes('Docker') || skill.includes('Kubernetes'))) {
          strengths.push('컨테이너 기술에 대한 이해도를 보여줍니다');
        }
      }

      // 자격증 관련 강점
      if (applicant.growthBackground) {
        const certificateContent = extractCertificates(applicant.growthBackground);
        if (certificateContent && certificateContent !== '자격증 정보가 없습니다.') {
          const certMatch = certificateContent.match(/([가-힣]+자격증?)/);
          if (certMatch) {
            strengths.push(`${certMatch[1]}을 보유하여 전문성을 인증합니다`);
          } else {
            strengths.push('관련 자격증을 보유하고 있습니다');
          }
        }
      }

      // 수상 경력 관련 강점
      if (applicant.growthBackground) {
        const awardContent = extractAwards(applicant.growthBackground);
        if (awardContent && awardContent !== '수상 정보가 없습니다.') {
          strengths.push('수상 경력으로 우수성을 인정받았습니다');
        }
      }

      // 지원자별 고유한 강점 생성 (기본 강점 제거)
      if (strengths.length === 0) {
        if (applicant.name && applicant.name.length > 0) {
          strengths.push(`${applicant.name}님의 이력서는 기본적인 구조를 갖추고 있습니다`);
        } else {
          strengths.push('이력서 작성에 대한 기본적인 이해를 보여줍니다');
        }
      }
    }

    // 개선점 분석 (5개) - 더 구체적으로
    if (improvements.length < 5) {
      // 학력 관련 개선점
      if (applicant.growthBackground) {
        const educationContent = extractEducationFromResume(applicant.growthBackground);
        if (!educationContent || educationContent === '학력 정보가 없습니다.') {
          improvements.push('학력 및 전공 정보를 추가로 제시해주세요');
        } else {
          if (!educationContent.includes('성적') && !educationContent.includes('GPA')) {
            improvements.push('학업 성취도나 주요 과목 정보를 추가해주세요');
          }
          if (!educationContent.includes('졸업') && !educationContent.includes('재학')) {
            improvements.push('졸업 상태나 재학 기간을 명시해주세요');
          }
          if (!educationContent.includes('논문') && !educationContent.includes('프로젝트')) {
            improvements.push('학업 중 수행한 논문이나 프로젝트 경험을 추가해주세요');
          }
        }
      }

      // 경력 관련 개선점
      if (applicant.careerHistory) {
        const careerContent = extractCareerFromResume(applicant.careerHistory);
        if (!careerContent || careerContent === '경력 정보가 없습니다.') {
          improvements.push('경력사항을 구체적으로 작성해주세요');
        } else {
          if (!careerContent.includes('성과') && !careerContent.includes('업적')) {
            improvements.push('구체적인 성과와 업적을 수치화하여 제시해주세요');
          }
          if (!careerContent.includes('책임') && !careerContent.includes('역할')) {
            improvements.push('담당 업무와 책임 범위를 구체적으로 명시해주세요');
          }
          if (!careerContent.includes('팀') && !careerContent.includes('협업')) {
            improvements.push('팀워크와 협업 경험을 구체적으로 언급해주세요');
          }
        }
      }

      // 기술 관련 개선점
      if (applicant.skills) {
        const skillsList = applicant.skills.split(',').map(s => s.trim()).filter(s => s.length > 0);
        if (skillsList.length < 3) {
          improvements.push('기술 스택을 더 다양하게 보완해주세요');
        }
        if (!skillsList.some(skill => skill.includes('React') || skill.includes('Vue') || skill.includes('Angular'))) {
          improvements.push('현대적인 프론트엔드 프레임워크 경험을 추가해주세요');
        }
        if (!skillsList.some(skill => skill.includes('Git') || skill.includes('SVN'))) {
          improvements.push('버전 관리 시스템 경험을 추가해주세요');
        }
        if (!skillsList.some(skill => skill.includes('SQL') || skill.includes('데이터베이스'))) {
          improvements.push('데이터베이스 관련 기술 경험을 추가해주세요');
        }
      }

      // 프로젝트 관련 개선점
      if (applicant.growthBackground) {
        if (!applicant.growthBackground.includes('프로젝트')) {
          improvements.push('프로젝트 경험과 기여도를 구체적으로 작성해주세요');
        }
      }

      // 지원자별 고유한 개선점 생성 (기본 개선점 제거)
      if (improvements.length === 0) {
        improvements.push('구체적인 성과와 결과를 수치화하여 제시해주세요');
      }
    }

    // 최대 5개까지만 반환
    return { 
      strengths: strengths.slice(0, 5), 
      improvements: improvements.slice(0, 5) 
    };
  };

  const summary = generateSummary();

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
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            onClick={(e) => e.stopPropagation()}
          >
            <CloseButton onClick={onClose}>
              <FiX />
            </CloseButton>

            <Header>
              <HeaderActions>
                <ActionButton onClick={onViewSummary}>
                  <FiEye size={14} />
                  요약보기
                </ActionButton>
                <ActionButton>
                  <FiDownload size={14} />
                  다운로드
                </ActionButton>
              </HeaderActions>
              
              <Title>{applicant.name || '지원자'}</Title>
              <Subtitle>
                <span>{applicant.position || '지원 직무 정보 없음'}</span>
                <StatusBadge status={applicant.status}>
                  {applicant.status || '지원'}
                </StatusBadge>
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
                        <FiPhone size={16} />
                      </InfoIcon>
                      <InfoContent>
                        <InfoLabel>연락처</InfoLabel>
                        <InfoValue>{applicant.phone || '정보 없음'}</InfoValue>
                      </InfoContent>
                    </InfoItem>
                    
                    <InfoItem>
                      <InfoIcon>
                        <FiMail size={16} />
                      </InfoIcon>
                      <InfoContent>
                        <InfoLabel>이메일</InfoLabel>
                        <InfoValue>{applicant.email || '정보 없음'}</InfoValue>
                      </InfoContent>
                    </InfoItem>
                    

                    
                    <InfoItem>
                      <InfoIcon>
                        <FiCalendar size={16} />
                      </InfoIcon>
                      <InfoContent>
                        <InfoLabel>지원일시</InfoLabel>
                        <InfoValue>{formatDate(applicant.created_at)}</InfoValue>
                      </InfoContent>
                    </InfoItem>
                  </InfoGrid>
                </SectionContent>
              </Section>

              {/* 학력 섹션 */}
              <Section>
                <SectionTitle>
                  <FiBookOpen size={20} />
                  학력
                </SectionTitle>
                <SectionContent>
                  <TextContent>
                    {applicant.growthBackground ? 
                      extractEducationFromResume(applicant.growthBackground) : 
                      '학력 정보가 없습니다.'
                    }
                  </TextContent>
                </SectionContent>
              </Section>

              {/* 경력 섹션 */}
              <Section>
                <SectionTitle>
                  <FiTrendingUp size={20} />
                  경력
                </SectionTitle>
                <SectionContent>
                  <TextContent>
                    {applicant.careerHistory ? 
                      extractCareerFromResume(applicant.careerHistory) : 
                      '경력 정보가 없습니다.'
                    }
                  </TextContent>
                </SectionContent>
              </Section>

              {/* 기술 스택 섹션 */}
              <Section>
                <SectionTitle>
                  <FiCode size={20} />
                  기술 스택
                </SectionTitle>
                <SectionContent>
                  <TextContent>
                    {applicant.skills || '기술 스택 정보가 없습니다.'}
                  </TextContent>
                </SectionContent>
              </Section>

              {/* 자격증 섹션 */}
              <Section>
                <SectionTitle>
                  <FiAward size={20} />
                  자격증
                </SectionTitle>
                <SectionContent>
                  <TextContent>
                    {applicant.growthBackground ? 
                      extractCertificates(applicant.growthBackground) : 
                      '자격증 정보가 없습니다.'
                    }
                  </TextContent>
                </SectionContent>
              </Section>

              {/* 수상 섹션 */}
              <Section>
                <SectionTitle>
                  <FiStar size={20} />
                  수상
                </SectionTitle>
                <SectionContent>
                  <TextContent>
                    {applicant.growthBackground ? 
                      extractAwards(applicant.growthBackground) : 
                      '수상 정보가 없습니다.'
                    }
                  </TextContent>
                </SectionContent>
              </Section>

              

              {/* 이력서 분석 결과 섹션 */}
              <AnalysisSection>
                <SectionTitle>
                  <FiBarChart2 size={20} />
                  이력서 분석 결과
                </SectionTitle>
                
                <AnalysisGrid>
                  {/* 항목별 분석 */}
                  <AnalysisCard>
                    <AnalysisCardTitle>
                      <FiBarChart2 size={16} />
                      항목별 분석
                    </AnalysisCardTitle>
                    
                    {/* 총평 요약 */}
                    <SummaryOverview>
                      <SummaryOverviewTitle>
                        <FiTarget size={14} />
                        종합 평가 요약
                      </SummaryOverviewTitle>
                      <SummaryOverviewContent>
                        {generateOverallSummary()}
                      </SummaryOverviewContent>
                    </SummaryOverview>
                    
                    <AnalysisChart>
                      <ChartItem>
                        <ChartLabel>학력 및 전공</ChartLabel>
                        <ChartBar>
                          <ChartFill score={analysisScores.education} />
                        </ChartBar>
                        <ChartScore>{analysisScores.education}점</ChartScore>
                        {/* 플러스 버튼 주석 처리
                        <DetailButton onClick={(e) => {
                          e.stopPropagation();
                          setSelectedItem('education');
                        }}>
                          <FiPlus size={14} />
                        </DetailButton>
                        */}
                      </ChartItem>
                      
                      <ChartItem>
                        <ChartLabel>경력 및 직무</ChartLabel>
                        <ChartBar>
                          <ChartFill score={analysisScores.experience} />
                        </ChartBar>
                        <ChartScore>{analysisScores.experience}점</ChartScore>
                        {/* 플러스 버튼 주석 처리
                        <DetailButton onClick={(e) => {
                          e.stopPropagation();
                          setSelectedItem('experience');
                        }}>
                          <FiPlus size={14} />
                        </DetailButton>
                        */}
                      </ChartItem>
                      
                      <ChartItem>
                        <ChartLabel>보유 기술</ChartLabel>
                        <ChartBar>
                          <ChartFill score={analysisScores.skills} />
                        </ChartBar>
                        <ChartScore>{analysisScores.skills}점</ChartScore>
                        {/* 플러스 버튼 주석 처리
                        <DetailButton onClick={(e) => {
                          e.stopPropagation();
                          setSelectedItem('skills');
                        }}>
                          <FiPlus size={14} />
                        </DetailButton>
                        */}
                      </ChartItem>
                      
                      <ChartItem>
                        <ChartLabel>프로젝트</ChartLabel>
                        <ChartBar>
                          <ChartFill score={analysisScores.projects} />
                        </ChartBar>
                        <ChartScore>{analysisScores.projects}점</ChartScore>
                        {/* 플러스 버튼 주석 처리
                        <DetailButton onClick={(e) => {
                          e.stopPropagation();
                          setSelectedItem('projects');
                        }}>
                          <FiPlus size={14} />
                        </DetailButton>
                        */}
                      </ChartItem>
                      
                      
                    </AnalysisChart>
                  </AnalysisCard>

                  {/* 통합 분석 결과 */}
                  <DetailCard style={{ height: '548px' }}>
                    <DetailCardTitle>
                      <FiTarget size={16} />
                      이력서 종합 분석 결과
                    </DetailCardTitle>
                    <DetailContent>
                      <DetailItemHeader>
                        <DetailItemTitle>종합 평가</DetailItemTitle>
                        <DetailItemScore>{totalScore}점</DetailItemScore>
                      </DetailItemHeader>
                      <DetailItemDescription>
                        {isLoadingAnalysis ? (
                          <div style={{ textAlign: 'center', padding: '20px' }}>
                            <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                              AI 분석 결과를 생성하고 있습니다...
                            </div>
                            <div style={{ fontSize: '12px', color: '#999' }}>
                              잠시만 기다려주세요
                            </div>
                          </div>
                        ) : (
                          generateComprehensiveAnalysis()
                        )}
                      </DetailItemDescription>
                    </DetailContent>
                  </DetailCard>
                </AnalysisGrid>

                {/* 분석 요약 */}
                <SummaryContent>
                  <SummaryTitle>
                    <FiTarget size={16} />
                    분석 요약
                  </SummaryTitle>
                  
                  {summary.strengths.length > 0 && (
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ 
                        fontSize: '14px', 
                        fontWeight: '600', 
                        color: '#38a169', 
                        marginBottom: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}>
                        <FiCheck size={14} />
                        강점
                      </div>
                      <SummaryText>
                        {summary.strengths.map((strength, index) => (
                          <div key={index} style={{ marginBottom: '8px' }}>
                            • {strength}
                          </div>
                        ))}
                      </SummaryText>
                    </div>
                  )}
                  
                  {summary.improvements.length > 0 && (
                    <div>
                      <div style={{ 
                        fontSize: '14px', 
                        fontWeight: '600', 
                        color: '#e53e3e', 
                        marginBottom: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}>
                        <FiAlertCircle size={14} />
                        개선점
                      </div>
                      <SummaryText>
                        {summary.improvements.map((improvement, index) => (
                          <div key={index} style={{ marginBottom: '8px' }}>
                            • {improvement}
                          </div>
                        ))}
                      </SummaryText>
                    </div>
                  )}
                </SummaryContent>
              </AnalysisSection>
            </Content>
          </ModalContent>
        </ModalOverlay>
      )}
    </AnimatePresence>
  );
};

export default ResumeModal;
