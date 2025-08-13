import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiFileText, 
  FiDownload, 
  FiSmartphone, 
  FiEye, 
  FiSearch,
  FiFilter,
  FiPlus,
  FiCheckCircle,
  FiClock,
  FiAlertCircle
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText,
  StatusBadge
} from '../../components/DetailModal/DetailModal';

const ResumeContainer = styled.div`
  padding: 16px 0;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
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

const ResumeGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
`;

const ResumeBoard = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ResumeBoardCard = styled(motion.div)`
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
`;

const ResumeCard = styled(motion.div)`
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

const ResumeHeader = styled.div`
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

// StatusBadge is imported from DetailModal

const ResumeContent = styled.div`
  margin-bottom: 12px;
`;

const ResumeDetail = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const ResumeActions = styled.div`
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

const AnalysisResult = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const AnalysisTitle = styled.div`
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-size: 16px;
`;

const AnalysisScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 90) return '#22c55e'; // 초록
    if (props.score >= 80) return '#f59e0b'; // 노랑
    return '#ef4444'; // 빨강
  }};
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const ScoreText = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 30px;
`;

// 커스텀 StatusBadge 컴포넌트 추가
const CustomStatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  &.approved {
    background-color: #dcfce7;
    color: #166534;
    border: 2px solid #22c55e;
  }

  &.pending {
    background-color: #fef3c7;
    color: #92400e;
    border: 2px solid #f59e0b;
  }

  &.rejected {
    background-color: #fee2e2;
    color: #dc2626;
    border: 2px solid #ef4444;
  }

  &.reviewed {
    background-color: #dbeafe;
    color: #1e40af;
    border: 2px solid #3b82f6;
  }
`;



const getStatusText = (status) => {
  const statusMap = {
    pending: '검토 대기',
    reviewed: '검토 완료',
    approved: '승인',
    rejected: '거절'
  };
  return statusMap[status] || status;
};

const ResumeManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedResume, setSelectedResume] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'board'
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 필터 상태 추가
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [selectedScoreRanges, setSelectedScoreRanges] = useState([]);
  const [isNewResumeModalOpen, setIsNewResumeModalOpen] = useState(false);
  const [newResumeData, setNewResumeData] = useState({
    name: '',
    position: '',
    department: '',
    experience: '',
    skills: '',
    summary: '',
    coverLetter: ''
  });
  const [coverLetterAnalysis, setCoverLetterAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 이력서 데이터 로드
  useEffect(() => {
    const fetchResumes = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/resumes');
        if (!response.ok) {
          throw new Error('이력서 데이터를 불러오는데 실패했습니다.');
        }
        const data = await response.json();
        setResumes(data);
      } catch (err) {
        console.log('백엔드 연결 실패:', err.message);
        setResumes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchResumes();
  }, []);

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

  const handleScoreRangeToggle = (range) => {
    setSelectedScoreRanges(prev => 
      prev.includes(range) 
        ? prev.filter(r => r !== range)
        : [...prev, range]
    );
  };

  const filteredResumes = resumes.filter(resume => {
    const matchesSearch = resume.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         resume.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resume.department.toLowerCase().includes(searchTerm.toLowerCase());
    
    // 직무 필터링
    const matchesJob = selectedJobs.length === 0 || selectedJobs.some(job => 
      resume.position.toLowerCase().includes(job.toLowerCase())
    );
    
    // 경력 필터링
    const resumeExp = parseInt(resume.experience);
    const matchesExperience = selectedExperience.length === 0 || selectedExperience.some(exp => {
      if (exp === '1-3년') return resumeExp >= 1 && resumeExp <= 3;
      if (exp === '3-5년') return resumeExp >= 3 && resumeExp <= 5;
      if (exp === '5년이상') return resumeExp >= 5;
      return false;
    });
    
    return matchesSearch && matchesJob && matchesExperience;
  });

  // AI 적합도 높은 순으로 정렬
  const sortedResumes = filteredResumes.sort((a, b) => (b.analysisScore || 0) - (a.analysisScore || 0));

  const handleViewDetails = (resume) => {
    setSelectedResume(resume);
    setIsDetailModalOpen(true);
  };

  const handleCoverLetterAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      // 올바른 자소서 분석 API 호출 (포트 8001)
      const response = await fetch('http://localhost:8001/api/cover-letter/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newResumeData.coverLetter,
          position: newResumeData.position,
          department: newResumeData.department,
          analysis_type: 'basic'
        }),
      });

      if (!response.ok) {
        throw new Error('자소서 분석에 실패했습니다.');
      }
      
      const data = await response.json();
      console.log('자소서 분석 응답:', data); // 디버깅용
      
      if (data.success && data.analysis_result) {
        setCoverLetterAnalysis(data.analysis_result);
      } else {
        throw new Error(data.error_message || '자소서 분석 결과를 받을 수 없습니다.');
      }
    } catch (err) {
      console.error('자소서 분석 실패:', err);
      alert('자소서 분석에 실패했습니다: ' + err.message);
      
      // 에러 발생 시 테스트 데이터로 대체
      setCoverLetterAnalysis({
        analysis: {
          motivation_score: 7,
          motivation_feedback: "지원 동기가 명확하고 회사에 대한 이해도가 높습니다.",
          problem_solving_score: 6,
          problem_solving_feedback: "문제 해결 과정에 대한 구체적 서술이 필요합니다.",
          teamwork_score: 8,
          teamwork_feedback: "팀 프로젝트 경험이 풍부하고 협업 능력이 뛰어납니다.",
          technical_score: 7,
          technical_feedback: "기술 스택이 직무 요구사항과 잘 맞습니다.",
          growth_score: 8,
          growth_feedback: "지속적인 학습 의지와 미래 비전이 명확합니다."
        },
        overall_score: "7.2/10",
        strengths: ["명확한 지원 동기", "팀워크 능력", "성장 의지"],
        weaknesses: ["구체적 사례 부족", "정량적 성과 부족"],
        recommendations: ["STAR 방법론을 활용한 구체적 사례 추가", "정량적 성과 지표 포함"]
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveResume = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/resumes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newResumeData),
      });

      if (!response.ok) {
        throw new Error('이력서 저장에 실패했습니다.');
      }
      const data = await response.json();
      setResumes(prev => [...prev, data]); // 새로 저장된 이력서를 목록에 추가
      handleCloseModal(); // 모달 닫기 및 폼 초기화
      alert('이력서가 성공적으로 저장되었습니다!');
    } catch (err) {
      console.error('이력서 저장 실패:', err);
      alert('이력서 저장에 실패했습니다: ' + err.message);
    }
  };

  const handleCloseModal = () => {
    setIsNewResumeModalOpen(false);
    setNewResumeData({
      name: '',
      position: '',
      department: '',
      experience: '',
      skills: '',
      summary: '',
      coverLetter: ''
    });
    setCoverLetterAnalysis(null);
  };

  const handleTestAnalysis = () => {
    setCoverLetterAnalysis({
      analysis: {
        motivation_score: 8,
        motivation_feedback: "지원 동기가 명확하고 회사에 대한 이해도가 높습니다. React 개발자로서의 열정이 잘 드러납니다.",
        problem_solving_score: 7,
        problem_solving_feedback: "문제 해결 과정에 대한 구체적 서술이 필요하지만, 기술적 접근 방식은 우수합니다.",
        teamwork_score: 8,
        teamwork_feedback: "팀 프로젝트 경험이 풍부하고 협업 능력이 뛰어납니다. 원격 협업 경험도 보유하고 있습니다.",
        technical_score: 8,
        technical_feedback: "React, TypeScript 등 현대적인 기술 스택을 잘 활용하고 있으며, 성능 최적화에도 관심이 많습니다.",
        growth_score: 9,
        growth_feedback: "지속적인 학습 의지와 미래 비전이 명확합니다. 새로운 기술 습득에 적극적입니다."
      },
      overall_score: "8.0/10",
      strengths: [
        "명확한 지원 동기와 회사 이해도",
        "팀워크 능력과 협업 경험",
        "현대적인 기술 스택 활용",
        "지속적인 학습 의지",
        "성능 최적화에 대한 관심"
      ],
      weaknesses: [
        "구체적 문제 해결 사례 부족",
        "정량적 성과 지표 부족",
        "STAR 방법론 적용 미흡"
      ],
      recommendations: [
        "STAR 방법론을 활용한 구체적 문제 해결 사례 추가",
        "프로젝트 성과를 정량적 지표로 표현",
        "기술적 도전과 해결 과정을 더 상세히 서술"
      ]
    });
    setIsAnalyzing(false);
  };

  return (
    <ResumeContainer>
      <Header>
        <Title>이력서 관리</Title>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ 
            fontSize: '14px', 
            color: 'var(--text-secondary)', 
            backgroundColor: 'var(--background-light)', 
            padding: '4px 8px', 
            borderRadius: '4px' 
          }}>
            AI 적합도 순 정렬
          </span>
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
            <Button className="primary" onClick={() => setIsNewResumeModalOpen(true)}>
              <FiPlus />
              새 이력서 등록
            </Button>
          </ActionButtons>
        </div>
      </Header>

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

      {/* 로딩 상태 */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>이력서 데이터를 불러오는 중...</p>
        </div>
      )}

      {/* 에러 상태 */}
      {error && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'red' }}>
          <p>에러: {error}</p>
        </div>
      )}

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
            justifyContent: 'center' // x축 중앙 정렬
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
        <ResumeGrid>
          {sortedResumes.map((resume, index) => (
            <ResumeCard
              key={resume._id || resume.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <ResumeHeader>
                <ApplicantInfo>
                  <ApplicantName>{resume.name}</ApplicantName>
                  <ApplicantPosition>{resume.position}</ApplicantPosition>
                </ApplicantInfo>

              </ResumeHeader>

              <ResumeContent>
                <ResumeDetail>
                  <DetailLabel>희망부서:</DetailLabel>
                  <DetailValue>{resume.department}</DetailValue>
                </ResumeDetail>
                <ResumeDetail>
                  <DetailLabel>경력:</DetailLabel>
                  <DetailValue>{resume.experience}</DetailValue>
                </ResumeDetail>
                <ResumeDetail>
                  <DetailLabel>기술스택:</DetailLabel>
                  <DetailValue>{resume.skills}</DetailValue>
                </ResumeDetail>
              </ResumeContent>

              <AnalysisResult>
                <AnalysisTitle>AI 분석 결과</AnalysisTitle>
                <AnalysisScore>
                  <ScoreText>적합도</ScoreText>
                  <ScoreBar>
                    <ScoreFill score={resume.analysisScore || 0} />
                  </ScoreBar>
                  <ScoreText>{resume.analysisScore || 0}%</ScoreText>
                </AnalysisScore>
                <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '8px' }}>
                  {resume.analysisResult || '분석 결과가 없습니다.'}
                </div>
              </AnalysisResult>

              <ResumeActions>
                <ActionButton onClick={() => {
                  setSelectedResume(resume);
                  setIsDetailModalOpen(true);
                }}>
                  <FiEye />
                  상세보기
                </ActionButton>
                <ActionButton>
                  <FiDownload />
                  PDF 다운로드
                </ActionButton>
              </ResumeActions>
            </ResumeCard>
          ))}
        </ResumeGrid>
      ) : (
        <ResumeBoard>
          {sortedResumes.map((resume) => (
            <ResumeBoardCard key={resume._id || resume.id}>
              <BoardCardContent>
                <div>
                  <ApplicantName>{resume.name}</ApplicantName>
                  <ApplicantPosition>{resume.position}</ApplicantPosition>
                </div>
                <div style={{ display: 'flex', gap: '80px', alignItems: 'center', fontSize: '14px', color: 'var(--text-secondary)', flexWrap: 'nowrap', overflow: 'hidden' }}>
                  <span style={{ minWidth: '80px' }}>{resume.department}</span>
                  <span style={{ minWidth: '60px' }}>{resume.experience}</span>
                  <span style={{ minWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{resume.skills}</span>
                  <span style={{ minWidth: '60px' }}>{resume.analysisScore || 0}%</span>
                </div>
              </BoardCardContent>
              <BoardCardActions>
                <ActionButton onClick={() => handleViewDetails(resume)}>
                  <FiEye />
                  상세보기
                </ActionButton>
              </BoardCardActions>
            </ResumeBoardCard>
          ))}
        </ResumeBoard>
      )}

      {/* 이력서 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedResume(null);
        }}
        title={selectedResume ? `${selectedResume.name} 이력서 상세` : ''}
      >
        {selectedResume && (
          <>
            <DetailSection>
              <SectionTitle>기본 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>이름</DetailLabel>
                  <DetailValue>{selectedResume.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>직책</DetailLabel>
                  <DetailValue>{selectedResume.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>희망부서</DetailLabel>
                  <DetailValue>{selectedResume.department}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>경력</DetailLabel>
                  <DetailValue>{selectedResume.experience}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>기술스택</DetailLabel>
                  <DetailValue>{selectedResume.skills}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>요약</SectionTitle>
              <DetailText>
                {selectedResume.summary}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>

      {/* 새 이력서 등록 모달 */}
      {isNewResumeModalOpen && (
        <>
          {/* 오버레이 */}
          <div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(0,0,0,0.5)',
              zIndex: 1000
            }}
            onClick={handleCloseModal}
          />
          
          {/* 모달 */}
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1001,
            background: 'white',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            width: '90vw',
            maxWidth: '800px',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '24px'
            }}>
              <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#374151' }}>
                새 이력서 등록
              </h2>
              <button
                onClick={handleCloseModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#6b7280'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              {/* 왼쪽: 기본 정보 입력 */}
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#374151' }}>
                  기본 정보
                </h3>
                
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    이름 *
                  </label>
                  <input
                    type="text"
                    value={newResumeData.name}
                    onChange={(e) => setNewResumeData({...newResumeData, name: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                    placeholder="지원자 이름"
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    지원 직무 *
                  </label>
                  <input
                    type="text"
                    value={newResumeData.position}
                    onChange={(e) => setNewResumeData({...newResumeData, position: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                    placeholder="예: 프론트엔드 개발자"
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    희망 부서 *
                  </label>
                  <input
                    type="text"
                    value={newResumeData.department}
                    onChange={(e) => setNewResumeData({...newResumeData, department: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                    placeholder="예: 개발팀"
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    경력 *
                  </label>
                  <select
                    value={newResumeData.experience}
                    onChange={(e) => setNewResumeData({...newResumeData, experience: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="">경력 선택</option>
                    <option value="신입">신입</option>
                    <option value="1년">1년</option>
                    <option value="2년">2년</option>
                    <option value="3년">3년</option>
                    <option value="4년">4년</option>
                    <option value="5년">5년</option>
                    <option value="6년">6년</option>
                    <option value="7년">7년</option>
                    <option value="8년">8년</option>
                    <option value="9년">9년</option>
                    <option value="10년 이상">10년 이상</option>
                  </select>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    기술 스택
                  </label>
                  <input
                    type="text"
                    value={newResumeData.skills}
                    onChange={(e) => setNewResumeData({...newResumeData, skills: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                    placeholder="예: React, TypeScript, Node.js"
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    자기소개 요약
                  </label>
                  <textarea
                    value={newResumeData.summary}
                    onChange={(e) => setNewResumeData({...newResumeData, summary: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px',
                      minHeight: '80px',
                      resize: 'vertical'
                    }}
                    placeholder="지원자의 주요 경력과 역량을 간단히 요약"
                  />
                </div>
              </div>

              {/* 오른쪽: 자소서 입력 및 분석 */}
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#374151' }}>
                  자소서
                </h3>
                
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500' }}>
                    자소서 내용 *
                  </label>
                  <textarea
                    value={newResumeData.coverLetter}
                    onChange={(e) => setNewResumeData({...newResumeData, coverLetter: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '14px',
                      minHeight: '200px',
                      resize: 'vertical'
                    }}
                    placeholder="지원자의 자소서를 입력하세요..."
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <button
                    onClick={handleCoverLetterAnalysis}
                    disabled={!newResumeData.coverLetter || !newResumeData.position || !newResumeData.department || isAnalyzing}
                    style={{
                      width: '100%',
                      padding: '12px',
                      background: newResumeData.coverLetter && newResumeData.position && newResumeData.department && !isAnalyzing ? '#3b82f6' : '#9ca3af',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: newResumeData.coverLetter && newResumeData.position && newResumeData.department && !isAnalyzing ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s ease',
                      opacity: newResumeData.coverLetter && newResumeData.position && newResumeData.department && !isAnalyzing ? 1 : 0.6
                    }}
                  >
                    {isAnalyzing ? (
                      <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        <div style={{
                          width: '16px',
                          height: '16px',
                          border: '2px solid #ffffff',
                          borderTop: '2px solid transparent',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }} />
                        분석 중...
                      </span>
                    ) : (
                      '자소서 분석하기'
                    )}
                  </button>
                  
                  {/* 테스트 분석 버튼 */}
                  <button
                    onClick={handleTestAnalysis}
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '8px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    🧪 테스트 분석 결과 보기
                  </button>
                  
                  {(!newResumeData.coverLetter || !newResumeData.position || !newResumeData.department) && (
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', textAlign: 'center' }}>
                      자소서 내용, 지원 직무, 희망 부서를 모두 입력해주세요
                    </div>
                  )}
                </div>

                {/* 자소서 분석 결과 */}
                {coverLetterAnalysis && (
                  <div style={{
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '16px',
                    background: '#f9fafb'
                  }}>
                    <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>
                      🎯 자소서 분석 결과
                    </h4>
                    
                    {coverLetterAnalysis.analysis ? (
                      <div style={{ marginBottom: '16px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb'
                          }}>
                            <strong style={{ color: '#374151' }}>동기 및 열정</strong>
                            <div style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>
                              {coverLetterAnalysis.analysis.motivation_score}/10점
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', lineHeight: '1.4' }}>
                              {coverLetterAnalysis.analysis.motivation_feedback}
                            </div>
                          </div>
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb'
                          }}>
                            <strong style={{ color: '#374151' }}>문제해결 능력</strong>
                            <div style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>
                              {coverLetterAnalysis.analysis.problem_solving_score}/10점
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', lineHeight: '1.4' }}>
                              {coverLetterAnalysis.analysis.problem_solving_feedback}
                            </div>
                          </div>
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb'
                          }}>
                            <strong style={{ color: '#374151' }}>팀워크 및 협업</strong>
                            <div style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>
                              {coverLetterAnalysis.analysis.teamwork_score}/10점
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', lineHeight: '1.4' }}>
                              {coverLetterAnalysis.analysis.teamwork_feedback}
                            </div>
                          </div>
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb'
                          }}>
                            <strong style={{ color: '#374151' }}>기술적 역량</strong>
                            <div style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>
                              {coverLetterAnalysis.analysis.technical_score}/10점
                            </div>
                            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', lineHeight: '1.4' }}>
                              {coverLetterAnalysis.analysis.technical_feedback}
                            </div>
                          </div>
                        </div>
                        
                        <div style={{
                          background: 'white',
                          padding: '12px',
                          borderRadius: '6px',
                          border: '1px solid #e5e7eb',
                          marginBottom: '12px'
                        }}>
                          <strong style={{ color: '#374151' }}>성장 잠재력</strong>
                          <div style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', marginTop: '4px' }}>
                            {coverLetterAnalysis.analysis.growth_score}/10점
                          </div>
                          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px', lineHeight: '1.4' }}>
                            {coverLetterAnalysis.analysis.growth_feedback}
                          </div>
                        </div>

                        <div style={{
                          background: '#3b82f6',
                          color: 'white',
                          padding: '12px',
                          borderRadius: '6px',
                          textAlign: 'center',
                          marginBottom: '16px'
                        }}>
                          <strong>🎯 전체 점수: {coverLetterAnalysis.overall_score}</strong>
                        </div>

                        {coverLetterAnalysis.strengths && coverLetterAnalysis.strengths.length > 0 && (
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb',
                            marginBottom: '12px'
                          }}>
                            <strong style={{ color: '#10b981' }}>💪 강점</strong>
                            <ul style={{ margin: '8px 0', paddingLeft: '20px', fontSize: '12px', color: '#374151' }}>
                              {coverLetterAnalysis.strengths.map((strength, index) => (
                                <li key={index} style={{ marginBottom: '4px' }}>{strength}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {coverLetterAnalysis.weaknesses && coverLetterAnalysis.weaknesses.length > 0 && (
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb',
                            marginBottom: '12px'
                          }}>
                            <strong style={{ color: '#ef4444' }}>⚠️ 개선점</strong>
                            <ul style={{ margin: '8px 0', paddingLeft: '20px', fontSize: '12px', color: '#374151' }}>
                              {coverLetterAnalysis.weaknesses.map((weakness, index) => (
                                <li key={index} style={{ marginBottom: '4px' }}>{weakness}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {coverLetterAnalysis.recommendations && coverLetterAnalysis.recommendations.length > 0 && (
                          <div style={{
                            background: 'white',
                            padding: '12px',
                            borderRadius: '6px',
                            border: '1px solid #e5e7eb'
                          }}>
                            <strong style={{ color: '#f59e0b' }}>💡 개선 제안</strong>
                            <ul style={{ margin: '8px 0', paddingLeft: '20px', fontSize: '12px', color: '#374151' }}>
                              {coverLetterAnalysis.recommendations.map((rec, index) => (
                                <li key={index} style={{ marginBottom: '4px' }}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div style={{ color: '#6b7280', fontSize: '14px', textAlign: 'center', padding: '20px' }}>
                        <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
                        자소서 분석 결과를 불러오는 중입니다...
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* 하단 버튼들 */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px',
              marginTop: '24px',
              paddingTop: '24px',
              borderTop: '2px solid #e5e7eb'
            }}>
              <button
                onClick={handleCloseModal}
                style={{
                  padding: '10px 20px',
                  background: 'white',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
              <button
                onClick={handleSaveResume}
                disabled={!newResumeData.name || !newResumeData.position || !newResumeData.department || !newResumeData.experience}
                style={{
                  padding: '10px 20px',
                  background: newResumeData.name && newResumeData.position && newResumeData.department && newResumeData.experience ? '#10b981' : '#9ca3af',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: newResumeData.name && newResumeData.position && newResumeData.department && newResumeData.experience ? 'pointer' : 'not-allowed'
                }}
              >
                이력서 저장
              </button>
            </div>
          </div>
        </>
      )}
    </ResumeContainer>
  );
};

export default ResumeManagement; 