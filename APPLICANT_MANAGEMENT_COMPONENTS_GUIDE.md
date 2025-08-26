# AI 채용 관리 시스템 - 지원자 관리 컴포넌트 모듈화 가이드

## 📋 개요

지원자 관리 페이지는 여러 독립적인 컴포넌트로 모듈화되어 있어 유지보수성과 재사용성을 높였습니다. 각 컴포넌트는 특정 기능을 담당하며, 독립적으로 개발, 테스트, 배포가 가능합니다.

## 🗂️ 모듈화 구조

```
frontend/src/
├── pages/ApplicantManagement/
│   ├── ApplicantManagement.js              # 메인 지원자 관리 컨테이너
│   ├── components/
│   │   ├── HeaderSection.js                # 헤더 섹션 컴포넌트
│   │   ├── StatsSection.js                 # 통계 섹션 컴포넌트
│   │   ├── SearchFilterSection.js          # 검색/필터 섹션 컴포넌트
│   │   ├── ApplicantGrid.js                # 지원자 그리드 컴포넌트
│   │   ├── ApplicantCard.js                # 개별 지원자 카드 컴포넌트
│   │   ├── ApplicantBoard.js               # 지원자 보드 뷰 컴포넌트
│   │   ├── ApplicantModal.js               # 지원자 상세 모달 컴포넌트
│   │   ├── DocumentViewer.js               # 문서 뷰어 컴포넌트
│   │   ├── RankingSystem.js                # 랭킹 시스템 컴포넌트
│   │   └── BulkActionBar.js                # 일괄 처리 액션바 컴포넌트
│   ├── hooks/
│   │   ├── useApplicantData.js             # 지원자 데이터 로딩 훅
│   │   ├── useApplicantFilter.js           # 지원자 필터링 훅
│   │   ├── useApplicantRanking.js          # 지원자 랭킹 훅
│   │   └── useApplicantActions.js          # 지원자 액션 훅
│   └── utils/
│       ├── applicantUtils.js               # 지원자 관련 유틸리티
│       ├── analysisUtils.js                # 분석 관련 유틸리티
│       └── rankingUtils.js                 # 랭킹 관련 유틸리티
└── services/
    └── applicantApi.js                     # 지원자 API 서비스
```

## 🎯 컴포넌트별 상세

### 1. HeaderSection 컴포넌트

#### 파일: `components/HeaderSection.js`
```javascript
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiUserPlus } from 'react-icons/fi';

const HeaderContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const HeaderLeft = styled.div`
  flex: 1;
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 16px;
`;

const NewResumeButton = styled(motion.button)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const HeaderSection = ({ onNewResumeClick }) => {
  return (
    <HeaderContainer>
      <HeaderContent>
        <HeaderLeft>
          <Title>지원자 관리</Title>
          <Subtitle>AI 기반 스마트 채용 관리</Subtitle>
        </HeaderLeft>
        <HeaderRight>
          <NewResumeButton
            onClick={onNewResumeClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiUserPlus size={16} />
            새 이력서 등록
          </NewResumeButton>
        </HeaderRight>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default HeaderSection;
```

**특징:**
- 헤더 정보 표시
- 새 이력서 등록 버튼
- Framer Motion 애니메이션

### 2. StatsSection 컴포넌트

#### 파일: `components/StatsSection.js`
```javascript
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import StatCard from './StatCard';

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`;

const StatsSection = ({ stats }) => {
  const statCards = [
    {
      title: '총 지원자',
      value: stats.total,
      change: '+12%',
      isPositive: true,
      icon: 'FiUsers',
      color: '#667eea',
      variant: 'total'
    },
    {
      title: '서류 합격',
      value: stats.passed,
      change: '+8%',
      isPositive: true,
      icon: 'FiCheckCircle',
      color: '#48bb78',
      variant: 'passed'
    },
    {
      title: '검토 대기',
      value: stats.waiting,
      change: '+15%',
      isPositive: true,
      icon: 'FiClock',
      color: '#ed8936',
      variant: 'waiting'
    },
    {
      title: '서류 불합격',
      value: stats.rejected,
      change: '-5%',
      isPositive: false,
      icon: 'FiX',
      color: '#e53e3e',
      variant: 'rejected'
    }
  ];

  return (
    <StatsGrid>
      {statCards.map((stat, index) => (
        <StatCard
          key={index}
          stat={stat}
          index={index}
        />
      ))}
    </StatsGrid>
  );
};

export default StatsSection;
```

**특징:**
- 4개 통계 카드 그리드
- 반응형 레이아웃
- StatCard 컴포넌트 재사용

### 3. SearchFilterSection 컴포넌트

#### 파일: `components/SearchFilterSection.js`
```javascript
import React from 'react';
import styled from 'styled-components';
import { FiSearch, FiFilter, FiGrid, FiList } from 'react-icons/fi';

const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
`;

const SearchSection = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
`;

const SearchInputContainer = styled.div`
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  padding-right: 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
  font-weight: 500;
  color: var(--text-primary);

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const JobPostingSelect = styled.select`
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  width: 250px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const ViewModeSection = styled.div`
  display: flex;
  gap: 8px;
`;

const ViewModeButton = styled.button`
  padding: 8px 12px;
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-secondary)'};
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.2s;

  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.active ? 'white' : 'var(--primary-color)'};
  }
`;

const FilterButton = styled.button`
  padding: 12px 16px;
  background: ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'white'};
  color: ${props => props.hasActiveFilters ? 'white' : 'var(--text-primary)'};
  border: 1px solid ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.hasActiveFilters ? 'white' : 'var(--primary-color)'};
  }
`;

const SearchFilterSection = ({
  searchTerm,
  onSearchChange,
  jobPostings,
  selectedJobPostingId,
  onJobPostingChange,
  viewMode,
  onViewModeChange,
  hasActiveFilters,
  onFilterClick
}) => {
  return (
    <SearchBar>
      <SearchSection>
        <SearchInputContainer>
          <SearchInput
            type="text"
            placeholder="지원자 이름, 직무, 이메일로 검색..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </SearchInputContainer>

        <JobPostingSelect
          value={selectedJobPostingId}
          onChange={(e) => onJobPostingChange(e.target.value)}
        >
          <option value="">전체 채용공고</option>
          {jobPostings.map(job => (
            <option key={job._id} value={job._id}>
              {job.title}
            </option>
          ))}
        </JobPostingSelect>
      </SearchSection>

      <ViewModeSection>
        <ViewModeButton
          active={viewMode === 'grid'}
          onClick={() => onViewModeChange('grid')}
        >
          <FiGrid size={14} />
          그리드
        </ViewModeButton>
        <ViewModeButton
          active={viewMode === 'board'}
          onClick={() => onViewModeChange('board')}
        >
          <FiList size={14} />
          보드
        </ViewModeButton>
      </ViewModeSection>

      <FilterButton
        hasActiveFilters={hasActiveFilters}
        onClick={onFilterClick}
      >
        <FiFilter size={16} />
        필터
        {hasActiveFilters && <span>●</span>}
      </FilterButton>
    </SearchBar>
  );
};

export default SearchFilterSection;
```

**특징:**
- 검색 입력 필드
- 채용공고 선택 드롭다운
- 뷰 모드 전환 버튼
- 필터 버튼

### 4. ApplicantCard 컴포넌트

#### 파일: `components/ApplicantCard.js`
```javascript
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  FiMail,
  FiPhone,
  FiCalendar,
  FiCode,
  FiCheck,
  FiX,
  FiClock
} from 'react-icons/fi';

const Card = styled(motion.div)`
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const ApplicantInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #00a844);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
`;

const ApplicantDetails = styled.div`
  flex: 1;
`;

const ApplicantName = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ApplicantPosition = styled.p`
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
`;

const StatusBadge = styled.span`
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  background: ${props => {
    switch (props.status) {
      case '서류합격':
      case 'passed': return '#e8f5e8';
      case '서류불합격':
      case 'rejected': return '#ffe8e8';
      case '최종합격':
      case 'approved': return '#d1ecf1';
      case '보류':
      case 'pending': return '#fff8dc';
      default: return '#f8f9fa';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case '서류합격':
      case 'passed': return '#28a745';
      case '서류불합격':
      case 'rejected': return '#dc3545';
      case '최종합격':
      case 'approved': return '#0c5460';
      case '보류':
      case 'pending': return '#856404';
      default: return '#6c757d';
    }
  }};
`;

const CardContent = styled.div`
  margin-bottom: 12px;
`;

const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-secondary);
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
`;

const ActionButton = styled.button`
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

const PassButton = styled(ActionButton)`
  background: ${props => props.active ? '#28a745' : 'white'};
  color: ${props => props.active ? 'white' : '#28a745'};
  border-color: #28a745;

  &:hover {
    background: ${props => props.active ? '#218838' : '#28a745'};
    border-color: #28a745;
    color: white;
  }
`;

const PendingButton = styled(ActionButton)`
  background: ${props => props.active ? '#ffc107' : 'white'};
  color: ${props => props.active ? '#212529' : '#ffc107'};
  border-color: #ffc107;

  &:hover {
    background: ${props => props.active ? '#e0a800' : '#ffc107'};
    border-color: #ffc107;
    color: #212529;
  }
`;

const RejectButton = styled(ActionButton)`
  background: ${props => props.active ? '#dc3545' : 'white'};
  color: ${props => props.active ? 'white' : '#dc3545'};
  border-color: #dc3545;

  &:hover {
    background: ${props => props.active ? '#c82333' : '#dc3545'};
    border-color: #dc3545;
    color: white;
  }
`;

const TopRankBadge = styled.div`
  position: absolute;
  top: -17px;
  left: -12px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: white;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 3px solid white;
  background: ${props => {
    if (props.rank === 1) return '#ef4444';
    if (props.rank === 2) return '#f59e0b';
    if (props.rank === 3) return '#10b981';
    return '#6b7280';
  }};
`;

const ApplicantCard = ({
  applicant,
  onCardClick,
  onStatusUpdate,
  getStatusText,
  rank,
  selectedJobPostingId
}) => {
  const handleStatusUpdate = async (newStatus) => {
    try {
      await onStatusUpdate(applicant.id, newStatus);
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
    }
  };

  return (
    <Card
      onClick={() => onCardClick(applicant)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {rank && rank <= 3 && selectedJobPostingId && (
        <TopRankBadge rank={rank} />
      )}

      <CardHeader>
        <ApplicantInfo>
          <Avatar>
            {applicant.name ? applicant.name.charAt(0) : '?'}
          </Avatar>
          <ApplicantDetails>
            <ApplicantName>{applicant.name}</ApplicantName>
            <ApplicantPosition>{applicant.position}</ApplicantPosition>
          </ApplicantDetails>
        </ApplicantInfo>
        <StatusBadge status={applicant.status}>
          {getStatusText(applicant.status)}
        </StatusBadge>
      </CardHeader>

      <CardContent>
        <InfoRow>
          <FiMail />
          <span>{applicant.email || '이메일 정보 없음'}</span>
        </InfoRow>
        <InfoRow>
          <FiPhone />
          <span>{applicant.phone || '전화번호 정보 없음'}</span>
        </InfoRow>
        <InfoRow>
          <FiCalendar />
          <span>
            {applicant.appliedDate || applicant.created_at
              ? new Date(applicant.appliedDate || applicant.created_at)
                  .toLocaleDateString('ko-KR')
              : '지원일 정보 없음'
            }
          </span>
        </InfoRow>
        <InfoRow>
          <FiCode />
          <span>
            {Array.isArray(applicant.skills)
              ? applicant.skills.join(', ')
              : applicant.skills || '기술 정보 없음'
            }
          </span>
        </InfoRow>
      </CardContent>

      <CardActions>
        <PassButton
          active={applicant.status === '서류합격' || applicant.status === '최종합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류합격');
          }}
        >
          <FiCheck />
          합격
        </PassButton>
        <PendingButton
          active={applicant.status === '보류'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('보류');
          }}
        >
          <FiClock />
          보류
        </PendingButton>
        <RejectButton
          active={applicant.status === '서류불합격'}
          onClick={(e) => {
            e.stopPropagation();
            handleStatusUpdate('서류불합격');
          }}
        >
          <FiX />
          불합격
        </RejectButton>
      </CardActions>
    </Card>
  );
};

export default React.memo(ApplicantCard);
```

**특징:**
- React.memo를 통한 성능 최적화
- 순위 배지 표시 (상위 3명)
- 상태 변경 버튼
- 호버 애니메이션

## 🔧 커스텀 훅

### 1. useApplicantData 훅

#### 파일: `hooks/useApplicantData.js`
```javascript
import { useState, useEffect, useCallback } from 'react';
import applicantApi from '../../services/applicantApi';

export const useApplicantData = () => {
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);

  const loadApplicants = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const apiApplicants = await applicantApi.getAllApplicants(0, 1000);

      if (apiApplicants && apiApplicants.length > 0) {
        setApplicants(apiApplicants);
        setHasMore(false);

        // 세션 스토리지에 저장
        sessionStorage.setItem('applicants', JSON.stringify(apiApplicants));
      } else {
        setApplicants([]);
        setHasMore(false);
        sessionStorage.setItem('applicants', JSON.stringify([]));
      }
    } catch (error) {
      console.error('지원자 데이터 로드 실패:', error);
      setError(error.message);
      setApplicants([]);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateApplicantStatus = useCallback(async (applicantId, newStatus) => {
    try {
      await applicantApi.updateApplicantStatus(applicantId, newStatus);

      setApplicants(prev => prev.map(applicant =>
        applicant.id === applicantId
          ? { ...applicant, status: newStatus }
          : applicant
      ));

      // 세션 스토리지 업데이트
      const updatedApplicants = applicants.map(applicant =>
        applicant.id === applicantId
          ? { ...applicant, status: newStatus }
          : applicant
      );
      sessionStorage.setItem('applicants', JSON.stringify(updatedApplicants));
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
      throw error;
    }
  }, [applicants]);

  useEffect(() => {
    loadApplicants();
  }, [loadApplicants]);

  return {
    applicants,
    loading,
    error,
    hasMore,
    loadApplicants,
    updateApplicantStatus
  };
};
```

**특징:**
- 지원자 데이터 로딩 로직
- 상태 업데이트 로직
- 세션 스토리지 캐싱
- 에러 처리

### 2. useApplicantFilter 훅

#### 파일: `hooks/useApplicantFilter.js`
```javascript
import { useState, useMemo, useCallback } from 'react';

export const useApplicantFilter = (applicants) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('전체');
  const [selectedJobPostingId, setSelectedJobPostingId] = useState('');
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState([]);

  const filteredApplicants = useMemo(() => {
    return applicants.filter(applicant => {
      const searchLower = searchTerm.toLowerCase();
      const skillsText = Array.isArray(applicant.skills)
        ? applicant.skills.join(', ')
        : applicant.skills || '';

      const matchesSearch = (applicant.name || '').toLowerCase().includes(searchLower) ||
                          (applicant.position || '').toLowerCase().includes(searchLower) ||
                          (applicant.email || '').toLowerCase().includes(searchLower) ||
                          skillsText.toLowerCase().includes(searchLower);

      const matchesStatus = filterStatus === '전체' ||
                           getStatusText(applicant.status) === filterStatus;

      const matchesSelectedStatus = selectedStatus.length === 0 ||
                                   selectedStatus.includes(applicant.status);

      const matchesJob = selectedJobs.length === 0 ||
                        selectedJobs.some(job => applicant.position.includes(job));

      const matchesExperience = selectedExperience.length === 0 ||
                              selectedExperience.some(exp => {
                                if (exp === '신입') return applicant.experience.includes('신입');
                                if (exp === '1-3년') return applicant.experience.includes('1년') || applicant.experience.includes('2년') || applicant.experience.includes('3년');
                                if (exp === '3-5년') return applicant.experience.includes('4년') || applicant.experience.includes('5년');
                                if (exp === '5년이상') return applicant.experience.includes('6년') || applicant.experience.includes('7년') || applicant.experience.includes('8년') || applicant.experience.includes('9년') || applicant.experience.includes('10년');
                                return false;
                              });

      const matchesJobPosting = !selectedJobPostingId ||
                               applicant.job_posting_id === selectedJobPostingId;

      return matchesSearch && matchesStatus && matchesSelectedStatus &&
             matchesJob && matchesExperience && matchesJobPosting;
    });
  }, [applicants, searchTerm, filterStatus, selectedJobs, selectedExperience, selectedStatus, selectedJobPostingId]);

  const hasActiveFilters = searchTerm !== '' ||
                          filterStatus !== '전체' ||
                          selectedJobs.length > 0 ||
                          selectedExperience.length > 0 ||
                          selectedStatus.length > 0 ||
                          selectedJobPostingId !== '';

  const resetFilters = useCallback(() => {
    setSearchTerm('');
    setFilterStatus('전체');
    setSelectedJobPostingId('');
    setSelectedJobs([]);
    setSelectedExperience([]);
    setSelectedStatus([]);
  }, []);

  return {
    searchTerm,
    setSearchTerm,
    filterStatus,
    setFilterStatus,
    selectedJobPostingId,
    setSelectedJobPostingId,
    selectedJobs,
    setSelectedJobs,
    selectedExperience,
    setSelectedExperience,
    selectedStatus,
    setSelectedStatus,
    filteredApplicants,
    hasActiveFilters,
    resetFilters
  };
};

const getStatusText = (status) => {
  const statusMap = {
    'pending': '보류',
    'approved': '최종합격',
    'rejected': '서류불합격',
    'reviewed': '서류합격',
    'reviewing': '보류',
    'passed': '서류합격',
    'interview_scheduled': '최종합격',
    '서류합격': '서류합격',
    '최종합격': '최종합격',
    '서류불합격': '서류불합격',
    '보류': '보류'
  };
  return statusMap[status] || '보류';
};
```

**특징:**
- 복합 필터링 로직
- 메모이제이션을 통한 성능 최적화
- 필터 상태 관리
- 필터 초기화 기능

## 🎯 모듈화의 장점

### 1. **재사용성**
- 각 컴포넌트를 다른 페이지에서도 사용 가능
- Props 기반 데이터 전달로 유연성 확보

### 2. **유지보수성**
- 기능별로 분리되어 수정이 용이
- 독립적인 테스트 가능

### 3. **성능 최적화**
- 필요한 컴포넌트만 리렌더링
- 메모이제이션을 통한 최적화

### 4. **개발 효율성**
- 팀원별로 컴포넌트 분담 개발 가능
- 병렬 개발 환경 구축

## 🔄 메인 컨테이너

#### 파일: `ApplicantManagement.js` (모듈화 후)
```javascript
import React from 'react';
import styled from 'styled-components';
import { useApplicantData } from './hooks/useApplicantData';
import { useApplicantFilter } from './hooks/useApplicantFilter';
import HeaderSection from './components/HeaderSection';
import StatsSection from './components/StatsSection';
import SearchFilterSection from './components/SearchFilterSection';
import ApplicantGrid from './components/ApplicantGrid';
import ApplicantModal from './components/ApplicantModal';

const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const LoadingMessage = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  font-size: 18px;
  color: #666;
`;

const ApplicantManagement = () => {
  const {
    applicants,
    loading,
    error,
    updateApplicantStatus
  } = useApplicantData();

  const {
    searchTerm,
    setSearchTerm,
    selectedJobPostingId,
    setSelectedJobPostingId,
    filteredApplicants,
    hasActiveFilters,
    // ... 기타 필터 상태들
  } = useApplicantFilter(applicants);

  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid');

  if (loading) {
    return (
      <Container>
        <LoadingMessage>
          지원자 데이터를 불러오는 중...
        </LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <LoadingMessage>
          데이터 로딩 중 오류가 발생했습니다: {error}
        </LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <HeaderSection onNewResumeClick={() => {/* 새 이력서 등록 로직 */}} />
      <StatsSection stats={calculateStats(applicants)} />
      <SearchFilterSection
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        selectedJobPostingId={selectedJobPostingId}
        onJobPostingChange={setSelectedJobPostingId}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        hasActiveFilters={hasActiveFilters}
        onFilterClick={() => {/* 필터 모달 로직 */}}
      />
      <ApplicantGrid
        applicants={filteredApplicants}
        viewMode={viewMode}
        onCardClick={(applicant) => {
          setSelectedApplicant(applicant);
          setIsModalOpen(true);
        }}
        onStatusUpdate={updateApplicantStatus}
      />
      {isModalOpen && selectedApplicant && (
        <ApplicantModal
          applicant={selectedApplicant}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedApplicant(null);
          }}
        />
      )}
    </Container>
  );
};

export default ApplicantManagement;
```

**특징:**
- 컴포넌트 조합으로 구성
- 훅을 통한 데이터 관리
- 로딩 및 에러 상태 처리

## 🚀 모듈화 구현 단계

### 1단계: 컴포넌트 분리
- 기존 ApplicantManagement.js에서 각 섹션을 별도 컴포넌트로 분리
- Props 인터페이스 정의

### 2단계: 커스텀 훅 생성
- 데이터 로딩 로직을 훅으로 분리
- 필터링 로직을 훅으로 분리

### 3단계: 스타일 분리
- 각 컴포넌트별 스타일 파일 생성
- 공통 스타일 변수 정의

### 4단계: 테스트 작성
- 각 컴포넌트별 단위 테스트
- 훅 테스트 코드 작성

---

**버전**: 1.0.0
**마지막 업데이트**: 2025년 1월

