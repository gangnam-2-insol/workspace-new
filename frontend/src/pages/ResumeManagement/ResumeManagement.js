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

  &.approved, &.최종합격, &.interview_scheduled {
    background-color: #dcfce7;
    color: #166534;
    border: 2px solid #22c55e;
  }

  &.pending, &.보류, &.reviewing {
    background-color: #fef3c7;
    color: #92400e;
    border: 2px solid #f59e0b;
  }

  &.rejected, &.서류불합격 {
    background-color: #fee2e2;
    color: #dc2626;
    border: 2px solid #ef4444;
  }

  &.reviewed, &.서류합격, &.passed {
    background-color: #dbeafe;
    color: #1e40af;
    border: 2px solid #3b82f6;
  }
`;



const getStatusText = (status) => {
  const statusMap = {
    pending: '보류',
    reviewed: '서류합격',
    approved: '최종합격',
    rejected: '서류불합격'
  };
  return statusMap[status] || '보류';
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

  // 이력서 데이터 로드
  useEffect(() => {
    const fetchResumes = async () => {
      try {
        setLoading(true);
        const response = await fetch((process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/resumes');
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
            <Button className="primary">
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
    </ResumeContainer>
  );
};

export default ResumeManagement;
