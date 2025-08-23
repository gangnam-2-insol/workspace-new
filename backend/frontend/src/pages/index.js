import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  FiUser, 
  FiMail, 
  FiPhone, 
  FiCalendar, 
  FiFileText, 
  FiEye, 
  FiDownload,
  FiSearch,
  FiFilter,
  FiCheck,
  FiX,
  FiStar,
  FiBriefcase,
  FiMapPin,
  FiClock,
  FiFile,
  FiMessageSquare,
  FiCode,
  FiGrid,
  FiList,
  FiBarChart2
} from 'react-icons/fi';
import DetailedAnalysisModal from '../../components/DetailedAnalysisModal';

// 스타일 컴포넌트 임포트
import * as S from './styles';
import * as A from './analysisStyles';
import * as M from './modalStyles';

// 유틸리티 함수들
import { 
  calculateAverageScore, 
  getResumeAnalysisLabel, 
  getCoverLetterAnalysisLabel, 
  getPortfolioAnalysisLabel 
} from './utils';

// API 서비스
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = {
  // 모든 지원자 조회 (페이지네이션 지원)
  getAllApplicants: async (skip = 0, limit = 50, status = null, position = null) => {
    try {
      console.log('🔍 API 호출 시도:', `${API_BASE_URL}/api/applicants`);
      
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
      });
      
      if (status) params.append('status', status);
      if (position) params.append('position', position);
      
      const response = await fetch(`${API_BASE_URL}/api/applicants?${params}`);
      console.log('📡 응답 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API 응답 오류:', errorText);
        throw new Error(`지원자 데이터 조회 실패: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ API 응답 데이터:', data);
      return data.applicants || [];
    } catch (error) {
      console.error('❌ 지원자 데이터 조회 오류:', error);
      throw error;
    }
  },

  // 지원자 상태 업데이트
  updateApplicantStatus: async (applicantId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (!response.ok) {
        throw new Error('지원자 상태 업데이트 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 상태 업데이트 오류:', error);
      throw error;
    }
  },

  // 지원자 통계 조회
  getApplicantStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/stats/overview`);
      if (!response.ok) {
        throw new Error('지원자 통계 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 통계 조회 오류:', error);
      throw error;
    }
  }
};

const ApplicantManagement = () => {
  // 상태 관리
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('list');
  const [selectedApplicants, setSelectedApplicants] = useState([]);
  const [showNewResumeModal, setShowNewResumeModal] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [positionFilter, setPositionFilter] = useState('all');

  // 데이터 로딩
  const loadApplicants = useCallback(async () => {
    try {
      console.log('지원자 데이터를 불러오는 중...');
      const data = await api.getAllApplicants(page * 20, 20, statusFilter, positionFilter);
      
      if (page === 0) {
        setApplicants(data);
      } else {
        setApplicants(prev => [...prev, ...data]);
      }
      
      setHasMore(data.length === 20);
    } catch (error) {
      console.error('❌ API 연결 실패:', error);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, positionFilter]);

  const loadStats = useCallback(async () => {
    try {
      const statsData = await api.getApplicantStats();
      setStats(statsData);
    } catch (error) {
      console.error('통계 데이터 로딩 실패:', error);
    }
  }, []);

  useEffect(() => {
    loadApplicants();
    loadStats();
  }, [loadApplicants, loadStats]);

  // 필터링된 지원자 목록
  const filteredApplicants = useMemo(() => {
    return applicants.filter(applicant => {
      const searchLower = searchTerm.toLowerCase();
      return (
        applicant.name?.toLowerCase().includes(searchLower) ||
        applicant.position?.toLowerCase().includes(searchLower) ||
        applicant.department?.toLowerCase().includes(searchLower) ||
        applicant.skills?.toLowerCase().includes(searchLower)
      );
    });
  }, [applicants, searchTerm]);

  // 이벤트 핸들러
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  const handleApplicantSelect = (id) => {
    setSelectedApplicants(prev => {
      if (prev.includes(id)) {
        return prev.filter(appId => appId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedApplicants(filteredApplicants.map(app => app.id));
    } else {
      setSelectedApplicants([]);
    }
  };

  const handleStatusChange = async (ids, newStatus) => {
    try {
      await Promise.all(ids.map(id => api.updateApplicantStatus(id, newStatus)));
      loadApplicants();
      setSelectedApplicants([]);
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
    }
  };

  const handleShowAnalysis = (applicant) => {
    setSelectedApplicant(applicant);
    setShowAnalysisModal(true);
  };

  const handleLoadMore = () => {
    setPage(prev => prev + 1);
  };

  // 렌더링
  if (loading) {
    return (
      <S.LoadingOverlay>
        <S.LoadingSpinner>
          <div className="spinner" />
          <span>지원자 데이터를 불러오는 중...</span>
        </S.LoadingSpinner>
      </S.LoadingOverlay>
    );
  }

  return (
    <S.Container>
      <S.Header>
        <S.HeaderContent>
          <S.HeaderLeft>
            <S.Title>지원자 관리</S.Title>
            <S.Subtitle>
              모든 지원자의 이력서와 평가를 한눈에 관리하세요
            </S.Subtitle>
          </S.HeaderLeft>
          <S.HeaderRight>
            <S.NewResumeButton onClick={() => setShowNewResumeModal(true)}>
              <FiFileText />
              새 이력서 등록
            </S.NewResumeButton>
          </S.HeaderRight>
        </S.HeaderContent>
      </S.Header>

      <S.StatsGrid>
        {stats && (
          <>
            <S.StatCard>
              <S.StatValue>{stats.total_applicants}</S.StatValue>
              <S.StatLabel>총 지원자</S.StatLabel>
            </S.StatCard>
            <S.StatCard>
              <S.StatValue>{stats.status_breakdown?.pending || 0}</S.StatValue>
              <S.StatLabel>검토 대기</S.StatLabel>
            </S.StatCard>
            <S.StatCard>
              <S.StatValue>{stats.status_breakdown?.approved || 0}</S.StatValue>
              <S.StatLabel>서류 통과</S.StatLabel>
            </S.StatCard>
            <S.StatCard>
              <S.StatValue>{stats.success_rate}%</S.StatValue>
              <S.StatLabel>합격률</S.StatLabel>
            </S.StatCard>
          </>
        )}
      </S.StatsGrid>

      <S.SearchBar>
        <S.SearchSection>
          <S.SearchInput
            type="text"
            placeholder="이름, 직무, 부서, 기술스택으로 검색..."
            value={searchTerm}
            onChange={handleSearch}
          />
        </S.SearchSection>
        <S.ViewModeSection>
          <S.ViewModeButton
            active={viewMode === 'list'}
            onClick={() => handleViewModeChange('list')}
          >
            <FiList />
            리스트
          </S.ViewModeButton>
          <S.ViewModeButton
            active={viewMode === 'board'}
            onClick={() => handleViewModeChange('board')}
          >
            <FiGrid />
            보드
          </S.ViewModeButton>
        </S.ViewModeSection>
      </S.SearchBar>

      {selectedApplicants.length > 0 && (
        <S.FixedActionBar>
          <S.SelectionInfo>
            {selectedApplicants.length}명의 지원자가 선택됨
          </S.SelectionInfo>
          <S.ActionButtonsGroup>
            <S.FixedPassButton
              onClick={() => handleStatusChange(selectedApplicants, 'approved')}
            >
              <FiCheck /> 합격
            </S.FixedPassButton>
            <S.FixedPendingButton
              onClick={() => handleStatusChange(selectedApplicants, 'pending')}
            >
              <FiClock /> 보류
            </S.FixedPendingButton>
            <S.FixedRejectButton
              onClick={() => handleStatusChange(selectedApplicants, 'rejected')}
            >
              <FiX /> 불합격
            </S.FixedRejectButton>
          </S.ActionButtonsGroup>
        </S.FixedActionBar>
      )}

      {viewMode === 'list' ? (
        <>
          <S.HeaderRow>
            <S.HeaderCheckbox>
              <S.CheckboxInput
                type="checkbox"
                checked={selectedApplicants.length === filteredApplicants.length}
                onChange={handleSelectAll}
              />
            </S.HeaderCheckbox>
            <S.HeaderName>이름</S.HeaderName>
            <S.HeaderPosition>직무</S.HeaderPosition>
            <S.HeaderDate>지원일</S.HeaderDate>
            <S.HeaderEmail>이메일</S.HeaderEmail>
            <S.HeaderPhone>연락처</S.HeaderPhone>
            <S.HeaderSkills>기술스택</S.HeaderSkills>
            <S.HeaderRanks>평가</S.HeaderRanks>
            <S.HeaderActions>액션</S.HeaderActions>
          </S.HeaderRow>
          {/* 지원자 목록 렌더링 */}
        </>
      ) : (
        <S.HeaderRowBoard>
          <S.HeaderCheckbox>
            <S.CheckboxInput
              type="checkbox"
              checked={selectedApplicants.length === filteredApplicants.length}
              onChange={handleSelectAll}
            />
          </S.HeaderCheckbox>
          <S.HeaderName>이름</S.HeaderName>
          <S.HeaderPosition>직무</S.HeaderPosition>
          <S.HeaderDate>지원일</S.HeaderDate>
          <S.HeaderRanks>평가</S.HeaderRanks>
          <S.HeaderActions>액션</S.HeaderActions>
        </S.HeaderRowBoard>
      )}

      {hasMore && (
        <S.LoadMoreButton onClick={handleLoadMore}>
          더 보기
        </S.LoadMoreButton>
      )}

      {showAnalysisModal && selectedApplicant && (
        <DetailedAnalysisModal
          applicant={selectedApplicant}
          onClose={() => setShowAnalysisModal(false)}
        />
      )}
    </S.Container>
  );
};

export default ApplicantManagement;
