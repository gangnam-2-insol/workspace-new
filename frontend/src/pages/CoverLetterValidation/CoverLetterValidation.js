   import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiEdit3, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiEye, 
  FiDownload,
  FiFileText,
  FiClock,
  FiPercent,
  FiXCircle,
  FiAlertTriangle,
  FiThumbsUp,
  FiTarget,
  FiSearch,
  FiCopy,
  FiShield,
  FiFilter
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

const CoverLetterContainer = styled.div`
  padding: 16px 0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const ViewModeButtons = styled.div`
  display: flex;
  gap: 4px;
  margin-left: 8px;
`;

const ViewModeButton = styled.button`
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-primary)'};
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition);
  font-size: 10px;
  
  &:hover {
    background: ${props => props.active ? 'var(--primary-color)' : 'var(--background-light)'};
  }
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  
  &.primary {
    background: var(--primary-color);
    color: white;
  }
  
  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 2px solid var(--border-color);
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-light);
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 10px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FilterButton = styled.button`
  padding: 10px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: var(--transition);
  font-size: 14px;
  
  &:hover {
    border-color: var(--primary-color);
  }
`;

const CoverLetterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 24px;
`;

const CoverLetterBoard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const CoverLetterCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 16px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 2px solid var(--border-color);
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-medium);
  }
`;

const CoverLetterBoardCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 12px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
  }
`;

const BoardCardContent = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
`;

const BoardCardActions = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const ApplicantInfo = styled.div`
  flex: 1;
`;

const ApplicantName = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ApplicantPosition = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 6px;
`;

const ValidationScore = styled.span`
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
  background: ${props => {
    if (props.score >= 90) return '#dcfce7'; // 연한 초록색
    if (props.score >= 80) return '#fef3c7'; // 연한 노란색
    return '#fee2e2'; // 연한 빨간색
  }};
  color: ${props => {
    if (props.score >= 90) return '#166534'; // 진한 초록색
    if (props.score >= 80) return '#92400e'; // 진한 노란색
    return '#dc2626'; // 진한 빨간색
  }};
  border: 2px solid ${props => {
    if (props.score >= 90) return '#22c55e';
    if (props.score >= 80) return '#f59e0b';
    return '#ef4444';
  }};
  min-width: 50px;
  text-align: center;
`;

const CardContent = styled.div`
  margin-bottom: 12px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
`;

const ValidationResult = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const ValidationTitle = styled.div`
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const ValidationMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
`;

const MetricItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MetricLabel = styled.span`
  font-size: 16px;
  color: var(--text-secondary);
  min-width: 80px;
  font-weight: 500;
`;

const MetricBar = styled.div`
  flex: 1;
  height: 10px;
  background: var(--border-color);
  border-radius: 5px;
  overflow: hidden;
`;

const MetricFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 90) return '#22c55e'; // 초록색
    if (props.score >= 80) return '#f59e0b'; // 노란색
    return '#ef4444'; // 빨간색
  }};
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const MetricValue = styled.span`
  font-size: 16px;
  color: var(--text-secondary);
  min-width: 35px;
  font-weight: 500;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  padding: 8px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const IssueList = styled.div`
  margin-top: 20px;
`;

const IssueItem = styled.div`
  padding: 16px 20px;
  border-radius: var(--border-radius);
  margin-bottom: 12px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: ${props => {
    if (props.severity === 'high') return '#fee2e2'; // 빨간색 배경
    if (props.severity === 'medium') return '#fef3c7'; // 노란색 배경
    return '#dcfce7'; // 초록색 배경
  }};
  border-left: 4px solid ${props => {
    if (props.severity === 'high') return '#ef4444'; // 빨간색
    if (props.severity === 'medium') return '#f59e0b'; // 노란색
    return '#22c55e'; // 초록색
  }};
  color: ${props => {
    if (props.severity === 'high') return '#991b1b'; // 진한 빨간색
    if (props.severity === 'medium') return '#92400e'; // 진한 노란색
    return '#166534'; // 진한 초록색
  }};
`;

const IssueIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: ${props => {
    if (props.severity === 'high') return '#ef4444'; // 빨간색
    if (props.severity === 'medium') return '#f59e0b'; // 노란색
    return '#22c55e'; // 초록색
  }};
  color: white;
  font-size: 14px;
`;

const IssueText = styled.span`
  flex: 1;
  font-weight: 500;
`;

// 새로운 컴포넌트들
const KeywordSection = styled.div`
  margin-top: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: var(--border-radius);
  border: 1px solid #e2e8f0;
`;

const KeywordTitle = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const KeywordMatch = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 16px;
`;

const MatchCount = styled.span`
  background: #22c55e;
  color: white;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 600;
`;

const KeywordList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
`;

const KeywordTag = styled.span`
  background: ${props => props.matched ? '#dcfce7' : '#fef3c7'};
  color: ${props => props.matched ? '#166534' : '#92400e'};
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid ${props => props.matched ? '#22c55e' : '#f59e0b'};
`;

const PlagiarismSection = styled.div`
  margin-top: 20px;
  padding: 20px;
  background: ${props => props.score > 90 ? '#dcfce7' : props.score > 80 ? '#fef3c7' : '#fee2e2'};
  border-radius: var(--border-radius);
  border-left: 4px solid ${props => props.score > 90 ? '#22c55e' : props.score > 80 ? '#f59e0b' : '#ef4444'};
`;

const PlagiarismTitle = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PlagiarismScore = styled.div`
  font-size: 22px;
  font-weight: 700;
  color: ${props => props.score > 90 ? '#166534' : props.score > 80 ? '#92400e' : '#dc2626'};
  margin-bottom: 10px;
`;

const PlagiarismDetail = styled.div`
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
`;

// 샘플 데이터 업데이트
const coverLetters = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    submittedDate: '2024-01-15',
    wordCount: 1200,
    validationScore: 92,
    originality: 95,
    coherence: 88,
    grammar: 90,
    plagiarism: 98,
    contentStructure: 94,
    keywordMatch: 85,
    jobRelevance: 92,
    writingQuality: 88,
    analysis: '자소서의 구성이 체계적이고, 구체적인 경험을 잘 서술했습니다.',
    issues: [
      { text: '일부 문장이 다소 길어 가독성이 떨어집니다', severity: 'low', type: 'improvement' },
      { text: '특정 기술 스택에 대한 설명이 부족합니다', severity: 'medium', type: 'improvement' }
    ],
    keywords: {
      required: ['React', 'JavaScript', '협업', '프로젝트 경험', '사용자 경험', '성능 최적화', 'Git'],
      matched: ['React', 'JavaScript', '협업', '프로젝트 경험', '사용자 경험', 'Git'],
      total: 7,
      matchedCount: 6
    },
    plagiarismDetails: {
      score: 98,
      status: '우수',
      description: '표절 의심 구간이 없으며, 원문 작성이 확인되었습니다.'
    }
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    submittedDate: '2024-01-14',
    wordCount: 1500,
    validationScore: 85,
    originality: 90,
    coherence: 85,
    grammar: 88,
    plagiarism: 92,
    contentStructure: 88,
    keywordMatch: 78,
    jobRelevance: 85,
    writingQuality: 82,
    analysis: '기술적 경험을 잘 설명했으나, 일부 문장이 개선이 필요합니다.',
    issues: [
      { text: '문법 오류가 3건 발견되었습니다', severity: 'high', type: 'error' },
      { text: '다른 지원자와 유사한 표현이 사용되었습니다', severity: 'high', type: 'error' },
      { text: '프로젝트 결과에 대한 구체적 수치가 부족합니다', severity: 'medium', type: 'improvement' }
    ],
    keywords: {
      required: ['Java', 'Spring', '데이터베이스', 'API 설계', '성능 튜닝', '보안', '마이크로서비스'],
      matched: ['Java', 'Spring', '데이터베이스', 'API 설계'],
      total: 7,
      matchedCount: 4
    },
    plagiarismDetails: {
      score: 92,
      status: '양호',
      description: '일부 구간에서 유사한 표현이 발견되었으나, 전반적으로 양호합니다.'
    }
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    submittedDate: '2024-01-13',
    wordCount: 800,
    validationScore: 78,
    originality: 85,
    coherence: 75,
    grammar: 80,
    plagiarism: 88,
    contentStructure: 82,
    keywordMatch: 72,
    jobRelevance: 78,
    writingQuality: 75,
    analysis: '창의적인 아이디어는 좋으나, 구체적인 프로젝트 경험이 부족합니다.',
    issues: [
      { text: '자소서 길이가 너무 짧습니다', severity: 'high', type: 'error' },
      { text: '디자인 프로세스 설명이 부족합니다', severity: 'medium', type: 'improvement' },
      { text: '결과 지표가 구체적이지 않습니다', severity: 'medium', type: 'improvement' },
      { text: '사용자 피드백 반영 과정이 잘 서술되었습니다', severity: 'low', type: 'strength' }
    ],
    keywords: {
      required: ['Figma', '사용자 연구', '프로토타이핑', '디자인 시스템', '사용자 테스트', '접근성'],
      matched: ['Figma', '프로토타이핑'],
      total: 6,
      matchedCount: 2
    },
    plagiarismDetails: {
      score: 88,
      status: '주의',
      description: '일부 구간에서 다른 자소서와 유사한 표현이 발견되었습니다.'
    }
  }
];

const CoverLetterValidation = () => {
  const [selectedCoverLetter, setSelectedCoverLetter] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'board'
  const [searchTerm, setSearchTerm] = useState('');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  
  // 선택 분석 관련 상태
  const [isSelectiveMode, setIsSelectiveMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [isAnalysisModalOpen, setIsAnalysisModalOpen] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFilterApply = () => {
    setIsFilterOpen(false);
  };

  const handleFilterClose = () => {
    setIsFilterOpen(false);
  };

  const handleJobToggle = (job) => {
    setSelectedJobs(prev => 
      prev.includes(job) 
        ? prev.filter(j => j !== job)
        : [...prev, job]
    );
  };

  const handleExperienceToggle = (exp) => {
    setSelectedExperience(prev => 
      prev.includes(exp) 
        ? prev.filter(e => e !== exp)
        : [...prev, exp]
    );
  };

  const filteredCoverLetters = coverLetters.filter(coverLetter => {
    const matchesSearch = coverLetter.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         coverLetter.position.toLowerCase().includes(searchTerm.toLowerCase());
    
    // 직무 필터링
    const matchesJob = selectedJobs.length === 0 || selectedJobs.some(job => 
      coverLetter.position.toLowerCase().includes(job.toLowerCase())
    );
    
    // 경력 필터링 (글자 수를 경력으로 간주)
    const wordCount = coverLetter.wordCount;
    const matchesExperience = selectedExperience.length === 0 || selectedExperience.some(exp => {
      if (exp === '1-3년') return wordCount >= 800 && wordCount <= 1200;
      if (exp === '3-5년') return wordCount >= 1200 && wordCount <= 1500;
      if (exp === '5년이상') return wordCount >= 1500;
      return false;
    });
    
    return matchesSearch && matchesJob && matchesExperience;
  });

  // AI 추천순으로 정렬 (검증 점수 기준 내림차순)
  const sortedCoverLetters = filteredCoverLetters.sort((a, b) => b.validationScore - a.validationScore);

  const getIssueIcon = (type, severity) => {
    if (type === 'error') return <FiXCircle />;
    if (type === 'improvement') return <FiAlertTriangle />;
    if (type === 'strength') return <FiThumbsUp />;
    return <FiAlertCircle />;
  };

  const handleViewDetails = (coverLetter) => {
    setSelectedCoverLetter(coverLetter);
    setIsDetailModalOpen(true);
  };

  // 선택 분석 관련 함수들
  const handleSelectiveAnalysis = () => {
    setIsSelectiveMode(!isSelectiveMode);
    if (isSelectiveMode) {
      setSelectedItems([]);
    }
  };

  const handleItemSelect = (id) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  const handleAnalyzeSelected = async () => {
    if (selectedItems.length === 0) {
      alert('분석할 자소서를 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);
    
    // AI 분석 시뮬레이션
    setTimeout(() => {
      const results = selectedItems.map(id => {
        const coverLetter = coverLetters.find(cl => cl.id === id);
        return {
          id: id,
          name: coverLetter.name,
          position: coverLetter.position,
          plagiarismRate: Math.floor(Math.random() * 20) + 5, // 5-25%
          jobFit: Math.floor(Math.random() * 30) + 70, // 70-100%
          talentFit: Math.floor(Math.random() * 30) + 70, // 70-100%
          overallScore: Math.floor(Math.random() * 20) + 75, // 75-95%
          analysis: {
            plagiarism: '표절 의심도 분석 결과 양호합니다. 원본성 있는 내용으로 구성되어 있습니다.',
            jobFit: '지원 직무와 높은 적합성을 보입니다. 관련 경험과 기술이 잘 드러나 있습니다.',
            talentFit: '회사 인재상과 잘 맞습니다. 성장 의지와 협업 능력이 돋보입니다.',
            overall: '전반적으로 우수한 자소서입니다. 개선 여지가 있지만 충분히 경쟁력 있는 내용입니다.'
          }
        };
      });
      
      setAnalysisResults(results);
      setIsAnalysisModalOpen(true);
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <CoverLetterContainer>
      <Header>
        <Title>자소서 검증</Title>
        <ActionButtons>
          <ViewModeButtons>
            <ViewModeButton 
              active={viewMode === 'grid'} 
              onClick={() => setViewMode('grid')}
            >
              그리드
            </ViewModeButton>
            <ViewModeButton 
              active={viewMode === 'board'} 
              onClick={() => setViewMode('board')}
            >
              게시판
            </ViewModeButton>
          </ViewModeButtons>
          <Button 
            className={isSelectiveMode ? "primary" : "secondary"}
            onClick={handleSelectiveAnalysis}
          >
            <FiTarget />
            {isSelectiveMode ? '선택 모드 해제' : '선택 분석'}
          </Button>
          <Button className="secondary">
            <FiFileText />
            일괄 분석
          </Button>
        </ActionButtons>
      </Header>

      {isSelectiveMode && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '16px',
          padding: '12px 16px',
          backgroundColor: 'var(--primary-color)',
          color: 'white',
          borderRadius: '8px'
        }}>
          <span>선택된 항목: {selectedItems.length}개</span>
          <Button 
            className="primary"
            onClick={handleAnalyzeSelected}
            disabled={isAnalyzing}
            style={{ backgroundColor: 'white', color: 'var(--primary-color)' }}
          >
            {isAnalyzing ? '분석 중...' : '선택 항목 분석'}
          </Button>
        </div>
      )}

      <SearchBar>
        <SearchInput
          type="text"
          placeholder="지원자명 또는 직무로 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FilterButton onClick={() => setIsFilterOpen(true)}>
          <FiFilter />
          필터
        </FilterButton>
      </SearchBar>

      {/* 필터 모달 */}
      {isFilterOpen && (
        <>
          {/* 오버레이 */}
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.3)',
            zIndex: 999
          }} />
          {/* 가로형 필터 모달 */}
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1000,
            background: 'white',
            border: '2px solid #e5e7eb',
            borderRadius: '16px',
            padding: '24px 36px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            minWidth: '800px',
            maxWidth: '1000px',
            minHeight: '180px',
            display: 'flex',
            flexDirection: 'row',
            gap: '36px',
            alignItems: 'flex-start',
            justifyContent: 'center'
          }}>
            {/* 직무 필터 */}
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '12px', color: '#374151' }}>
                직무
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                {['프론트엔드', '백엔드', '풀스택', '데이터 분석', 'PM', 'UI/UX', 'DevOps', 'QA'].map(job => (
                  <label key={job} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                    <input
                      type="checkbox"
                      checked={selectedJobs.includes(job)}
                      onChange={() => handleJobToggle(job)}
                      style={{ width: '16px', height: '16px', minWidth: '16px', minHeight: '16px', maxWidth: '16px', maxHeight: '16px' }}
                    />
                    {job}
                  </label>
                ))}
              </div>
            </div>
            {/* 경력 필터 */}
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '12px', color: '#374151' }}>
                경력
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {['1-3년', '3-5년', '5년이상'].map(exp => (
                  <label key={exp} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                    <input
                      type="checkbox"
                      checked={selectedExperience.includes(exp)}
                      onChange={() => handleExperienceToggle(exp)}
                      style={{ width: '16px', height: '16px', minWidth: '16px', minHeight: '16px', maxWidth: '16px', maxHeight: '16px' }}
                    />
                    {exp}
                  </label>
                ))}
              </div>
            </div>

            {/* 적용 버튼 */}
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'flex-end', minWidth: '100px', height: '100%' }}>
              <Button 
                className="primary" 
                onClick={handleFilterApply}
                style={{ fontSize: '14px', padding: '12px 24px', marginTop: 'auto' }}
              >
                적용
              </Button>
            </div>
          </div>
        </>
      )}

      {viewMode === 'grid' ? (
        <CoverLetterGrid>
          {sortedCoverLetters.map((coverLetter, index) => (
            <CoverLetterCard
              key={coverLetter.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <CardHeader>
                <ApplicantInfo>
                  {isSelectiveMode && (
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(coverLetter.id)}
                      onChange={() => handleItemSelect(coverLetter.id)}
                      style={{
                        marginRight: '8px',
                        transform: 'scale(1.2)',
                        cursor: 'pointer'
                      }}
                    />
                  )}
                  <ApplicantName>{coverLetter.name}</ApplicantName>
                  <ApplicantPosition>{coverLetter.position}</ApplicantPosition>
                </ApplicantInfo>
                <ValidationScore score={coverLetter.validationScore}>
                  {coverLetter.validationScore}점
                </ValidationScore>
              </CardHeader>

              <CardContent>
                <DetailRow>
                  <DetailLabel>제출일:</DetailLabel>
                  <DetailValue>{coverLetter.submittedDate}</DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>글자 수:</DetailLabel>
                  <DetailValue>{coverLetter.wordCount}자</DetailValue>
                </DetailRow>
              </CardContent>

              <CardActions>
                <ActionButton onClick={() => {
                  setSelectedCoverLetter(coverLetter);
                  setIsDetailModalOpen(true);
                }}>
                  <FiEye />
                  상세보기
                </ActionButton>
                <ActionButton>
                  <FiDownload />
                  리포트
                </ActionButton>
              </CardActions>
            </CoverLetterCard>
          ))}
        </CoverLetterGrid>
      ) : (
        <CoverLetterBoard>
          {filteredCoverLetters.map((coverLetter) => (
            <CoverLetterBoardCard key={coverLetter.id}>
              <BoardCardContent>
                <div>
                  {isSelectiveMode && (
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(coverLetter.id)}
                      onChange={() => handleItemSelect(coverLetter.id)}
                      style={{
                        marginRight: '8px',
                        transform: 'scale(1.2)',
                        cursor: 'pointer'
                      }}
                    />
                  )}
                  <ApplicantName>{coverLetter.name}</ApplicantName>
                  <ApplicantPosition>{coverLetter.position}</ApplicantPosition>
                </div>
                <div style={{ display: 'flex', gap: '60px', alignItems: 'center' }}>
                  <span>제출일: {coverLetter.submittedDate}</span>
                  <span>글자수: {coverLetter.wordCount}자</span>
                  <ValidationScore score={coverLetter.validationScore}>
                    {coverLetter.validationScore}점
                  </ValidationScore>
                </div>
              </BoardCardContent>
              <BoardCardActions>
                <ActionButton onClick={() => handleViewDetails(coverLetter)}>
                  <FiEye />
                  상세보기
                </ActionButton>
              </BoardCardActions>
            </CoverLetterBoardCard>
          ))}
        </CoverLetterBoard>
      )}

      {/* 자소서 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedCoverLetter(null);
        }}
        title={selectedCoverLetter ? `${selectedCoverLetter.name} 자소서 상세` : ''}
      >

      {/* AI 분석 결과 모달 */}
      <DetailModal
        isOpen={isAnalysisModalOpen}
        onClose={() => {
          setIsAnalysisModalOpen(false);
          setAnalysisResults([]);
        }}
        title="AI 분석 결과"
        showActions={false}
      >
        {analysisResults.map((result, index) => (
          <DetailSection key={result.id}>
            <SectionTitle>{result.name} - {result.position}</SectionTitle>
            <DetailGrid>
              <DetailItem>
                <DetailLabel>표절 의심도</DetailLabel>
                <DetailValue style={{ color: result.plagiarismRate < 15 ? '#10b981' : '#f59e0b' }}>
                  {result.plagiarismRate}%
                </DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>직무적합성</DetailLabel>
                <DetailValue style={{ color: result.jobFit >= 80 ? '#10b981' : '#f59e0b' }}>
                  {result.jobFit}%
                </DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>인재상 적합도</DetailLabel>
                <DetailValue style={{ color: result.talentFit >= 80 ? '#10b981' : '#f59e0b' }}>
                  {result.talentFit}%
                </DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>종합 점수</DetailLabel>
                <DetailValue style={{ 
                  color: result.overallScore >= 85 ? '#10b981' : result.overallScore >= 75 ? '#f59e0b' : '#ef4444',
                  fontWeight: 'bold'
                }}>
                  {result.overallScore}점
                </DetailValue>
              </DetailItem>
            </DetailGrid>
            
            <DetailSection>
              <SectionTitle>상세 분석</SectionTitle>
              <DetailText>
                <strong>표절 의심도:</strong> {result.analysis.plagiarism}
              </DetailText>
              <DetailText>
                <strong>직무 적합성:</strong> {result.analysis.jobFit}
              </DetailText>
              <DetailText>
                <strong>인재상 적합성:</strong> {result.analysis.talentFit}
              </DetailText>
              <DetailText>
                <strong>종합 평가:</strong> {result.analysis.overall}
              </DetailText>
            </DetailSection>
            
            {index < analysisResults.length - 1 && (
              <hr style={{ margin: '24px 0', border: '1px solid #e5e7eb' }} />
            )}
          </DetailSection>
        ))}
      </DetailModal>
        {selectedCoverLetter && (
          <>
            <DetailSection>
              <SectionTitle>지원자 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>지원자명</DetailLabel>
                  <DetailValue>{selectedCoverLetter.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지원 직무</DetailLabel>
                  <DetailValue>{selectedCoverLetter.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>제출일</DetailLabel>
                  <DetailValue>{selectedCoverLetter.submittedDate}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>글자 수</DetailLabel>
                  <DetailValue>{selectedCoverLetter.wordCount}자</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>검증 점수</DetailLabel>
                  <DetailValue>{selectedCoverLetter.validationScore}점</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 검증 결과</SectionTitle>
              <ValidationMetrics>
                <MetricItem>
                  <MetricLabel>내용 구조</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.contentStructure} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.contentStructure}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>키워드 적합성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.keywordMatch} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.keywordMatch}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>직무 연관성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.jobRelevance} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.jobRelevance}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>문체 품질</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.writingQuality} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.writingQuality}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>문법/표현</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.grammar} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.grammar}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>표절 의심도</MetricLabel>
                  <MetricBar>
                    <MetricFill score={selectedCoverLetter.plagiarism} />
                  </MetricBar>
                  <MetricValue>{selectedCoverLetter.plagiarism}%</MetricValue>
                </MetricItem>
              </ValidationMetrics>
            </DetailSection>

            <DetailSection>
              <SectionTitle>키워드/직무 적합성</SectionTitle>
              <KeywordSection>
                <KeywordMatch>
                  <MatchCount>✅ {selectedCoverLetter.keywords.total}개 중 {selectedCoverLetter.keywords.matchedCount}개 일치</MatchCount>
                  <span style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>
                    ({selectedCoverLetter.keywords.matchedCount}/{selectedCoverLetter.keywords.total})
                  </span>
                </KeywordMatch>
                <KeywordList>
                  {selectedCoverLetter.keywords.required.map((keyword, idx) => (
                    <KeywordTag 
                      key={idx} 
                      matched={selectedCoverLetter.keywords.matched.includes(keyword)}
                    >
                      {keyword}
                    </KeywordTag>
                  ))}
                </KeywordList>
              </KeywordSection>
            </DetailSection>

            <DetailSection>
              <SectionTitle>표절 의심도 분석 결과</SectionTitle>
              <PlagiarismSection score={selectedCoverLetter.plagiarismDetails.score}>
                <PlagiarismScore score={selectedCoverLetter.plagiarismDetails.score}>
                  {selectedCoverLetter.plagiarismDetails.score}% - {selectedCoverLetter.plagiarismDetails.status}
                </PlagiarismScore>
                <PlagiarismDetail>
                  {selectedCoverLetter.plagiarismDetails.description}
                </PlagiarismDetail>
              </PlagiarismSection>
            </DetailSection>

            <DetailSection>
              <SectionTitle>분석 결과</SectionTitle>
              <DetailText>
                {selectedCoverLetter.analysis}
              </DetailText>
            </DetailSection>

            <DetailSection>
              <SectionTitle>개선 사항</SectionTitle>
              <DetailText>
                {selectedCoverLetter.issues.map((issue, index) => (
                  <div key={index} style={{ 
                    marginBottom: '16px', 
                    padding: '16px 20px', 
                    backgroundColor: issue.severity === 'high' ? '#fee2e2' : issue.severity === 'medium' ? '#fef3c7' : '#dcfce7',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#22c55e'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: issue.severity === 'high' ? '#991b1b' : issue.severity === 'medium' ? '#92400e' : '#166534'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#22c55e',
                      color: 'white',
                      fontSize: '14px'
                    }}>
                      {getIssueIcon(issue.type, issue.severity)}
                    </div>
                    <span style={{ fontWeight: '500', fontSize: '16px' }}>{issue.text}</span>
                  </div>
                ))}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </CoverLetterContainer>
  );
};

export default CoverLetterValidation; 