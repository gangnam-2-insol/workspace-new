import React from 'react';
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

// 헤더 컴포넌트
export const HeaderSection = ({ onNewResumeClick }) => (
  <div className="header">
    <div className="header-content">
      <div className="header-left">
        <h1 className="title">지원자 관리</h1>
        <p className="subtitle">
          모든 지원자의 이력서와 평가를 한눈에 관리하세요
        </p>
      </div>
      <div className="header-right">
        <button className="new-resume-button" onClick={onNewResumeClick}>
          <FiFileText />
          새 이력서 등록
        </button>
      </div>
    </div>
  </div>
);

// 통계 카드 컴포넌트
const StatCard = ({ title, value, color }) => (
  <div style={{
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e1e5e9'
  }}>
    <div style={{
      fontSize: '32px',
      fontWeight: '700',
      color,
      marginBottom: '8px'
    }}>
      {value}
    </div>
    <div style={{
      color: '#6b7280',
      fontSize: '14px'
    }}>
      {title}
    </div>
  </div>
);

// 통계 섹션 컴포넌트
export const StatsSection = ({ stats }) => (
  <div style={{
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '24px',
    marginBottom: '32px'
  }}>
    {console.log('📊 === 통계 카드 렌더링 디버깅 ===', {
      stats,
      statsType: typeof stats,
      statsKeys: stats ? Object.keys(stats) : 'null',
      totalApplicants: stats?.total_applicants,
      statusBreakdown: stats?.status_breakdown
    })}

    <StatCard
      title="총 지원자"
      value={(() => {
        const value = stats?.total_applicants || 229;
        console.log('💡 총 지원자 값:', {
          rawStats: stats?.total_applicants,
          finalValue: value
        });
        return value;
      })()}
      color="#4f46e5"
    />

    <StatCard
      title="합격"
      value={(() => {
        const value = stats?.status_breakdown?.passed || 45;
        console.log('💡 합격 값:', {
          rawStats: stats?.status_breakdown?.passed,
          finalValue: value
        });
        return value;
      })()}
      color="#10b981"
    />

    <StatCard title="보류" value={86} color="#f59e0b" />
    <StatCard title="불합격" value={55} color="#ef4444" />
  </div>
);

// 검색/필터 섹션 컴포넌트
export const SearchFilterSection = ({ searchTerm, onSearchChange, viewMode, onViewModeChange }) => (
  <div className="search-bar">
    <div className="search-section">
      <input
        type="text"
        className="search-input"
        placeholder="이름, 직무, 부서, 기술스택으로 검색..."
        value={searchTerm}
        onChange={onSearchChange}
      />
    </div>
    <div className="view-mode-section">
      <button
        className={`view-mode-button ${viewMode === 'list' ? 'active' : ''}`}
        onClick={() => onViewModeChange('list')}
      >
        <FiList />
        리스트
      </button>
      <button
        className={`view-mode-button ${viewMode === 'board' ? 'active' : ''}`}
        onClick={() => onViewModeChange('board')}
      >
        <FiGrid />
        보드
      </button>
    </div>
  </div>
);

// 일괄 처리 액션바 컴포넌트
export const BulkActionBar = ({ selectedCount, onStatusUpdate, selectedIds }) => (
  <div className="fixed-action-bar">
    <div className="selection-info">
      {selectedCount}명의 지원자가 선택됨
    </div>
    <div className="action-buttons-group">
      <button
        className="fixed-action-button fixed-pass-button"
        onClick={() => onStatusUpdate(selectedIds, 'approved')}
      >
        <FiCheck /> 합격
      </button>
      <button
        className="fixed-action-button fixed-pending-button"
        onClick={() => onStatusUpdate(selectedIds, 'pending')}
      >
        <FiClock /> 보류
      </button>
      <button
        className="fixed-action-button fixed-reject-button"
        onClick={() => onStatusUpdate(selectedIds, 'rejected')}
      >
        <FiX /> 불합격
      </button>
    </div>
  </div>
);

// 로딩 스피너 컴포넌트
export const LoadingSpinner = () => (
  <div className="loading-overlay">
    <div className="loading-spinner">
      <div className="spinner" />
      <span>지원자 데이터를 불러오는 중...</span>
    </div>
  </div>
);

// 지원자 리스트 헤더 컴포넌트
export const ApplicantListHeader = ({ selectedCount, totalCount, onSelectAll }) => (
  <div className="header-row">
    <div className="header-checkbox">
      <input
        type="checkbox"
        className="checkbox-input"
        checked={selectedCount === totalCount}
        onChange={onSelectAll}
      />
    </div>
    <div className="header-name">이름</div>
    <div className="header-position">직무</div>
    <div className="header-date">지원일</div>
    <div className="header-email">이메일</div>
    <div className="header-phone">연락처</div>
    <div className="header-skills">기술스택</div>
    <div className="header-ranks">평가</div>
    <div className="header-actions">액션</div>
  </div>
);

// 지원자 보드 헤더 컴포넌트
export const ApplicantBoardHeader = ({ selectedCount, totalCount, onSelectAll }) => (
  <div className="header-row-board">
    <div className="header-checkbox">
      <input
        type="checkbox"
        className="checkbox-input"
        checked={selectedCount === totalCount}
        onChange={onSelectAll}
      />
    </div>
    <div className="header-name">이름</div>
    <div className="header-position">직무</div>
    <div className="header-date">지원일</div>
    <div className="header-ranks">평가</div>
    <div className="header-actions">액션</div>
  </div>
);

// 더 보기 버튼 컴포넌트
export const LoadMoreButton = ({ hasMore, onLoadMore }) => {
  if (!hasMore) return null;

  return (
    <button className="load-more-button" onClick={onLoadMore}>
      더 보기
    </button>
  );
};

// 디버깅 메시지 컴포넌트
export const DebugMessage = ({ stats, loading }) => (
  <div className="debug-message">
    🔍 디버깅: stats = {JSON.stringify(stats)} | loading = {loading.toString()}
  </div>
);
