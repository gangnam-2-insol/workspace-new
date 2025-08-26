import React from 'react';
import { FiSearch, FiFilter, FiGrid, FiList, FiBarChart2, FiX } from 'react-icons/fi';
import * as S from '../styles/SearchStyles';

const SearchFilterSection = ({
  searchTerm,
  setSearchTerm,
  selectedJobPostingId,
  handleJobPostingChange,
  jobPostings,
  visibleJobPostingsCount,
  setVisibleJobPostingsCount,
  hasActiveFilters,
  getFilterStatusText,
  handleFilterClick,
  viewMode,
  handleViewModeChange,
  isCalculatingRanking,
  calculateKeywordRanking,
  calculateJobPostingRanking
}) => {
  return (
    <S.SearchBar>
      <S.SearchSection>
        <S.JobPostingSelect
          value={selectedJobPostingId}
          onChange={(e) => {
            if (e.target.value === 'show-more') {
              setVisibleJobPostingsCount(prev => Math.min(prev + 5, jobPostings.length));
            } else {
              handleJobPostingChange(e.target.value);
            }
          }}
        >
          <option key="all" value="">전체 채용공고</option>
          {jobPostings.slice(0, visibleJobPostingsCount).map((job) => {
            const jobId = job._id || job.id;
            return (
              <option key={jobId} value={jobId}>
                {job.title}
              </option>
            );
          })}
          {visibleJobPostingsCount < jobPostings.length && (
            <option key="show-more" value="show-more" style={{ fontStyle: 'italic', color: '#666' }}>
              + 더보기 ({jobPostings.length - visibleJobPostingsCount}개)
            </option>
          )}
        </S.JobPostingSelect>

        <S.SearchInputContainer>
          <S.SearchInput
            type="text"
            placeholder={hasActiveFilters ? getFilterStatusText() : "지원자 이름,직무,기술스택을 입력하세요"}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && searchTerm.trim() && !isCalculatingRanking) {
                calculateKeywordRanking();
              }
            }}
          />
          {searchTerm && (
            <S.ClearButton
              onClick={() => setSearchTerm('')}
              title="검색어 지우기"
            >
              <FiX size={16} />
            </S.ClearButton>
          )}
        </S.SearchInputContainer>

        <S.FilterButton onClick={handleFilterClick} hasActiveFilters={hasActiveFilters}>
          <FiFilter size={16} />
          필터 {hasActiveFilters && <S.FilterBadge>{hasActiveFilters ? 1 : 0}</S.FilterBadge>}
        </S.FilterButton>

        <S.FilterButton
          onClick={() => {
            if (selectedJobPostingId) {
              calculateJobPostingRanking(selectedJobPostingId);
            } else if (searchTerm.trim()) {
              calculateKeywordRanking();
            } else {
              alert('채용공고를 선택하거나 검색어를 입력해주세요.');
            }
          }}
          disabled={isCalculatingRanking}
          style={{
            background: (selectedJobPostingId || searchTerm.trim()) ? 'var(--primary-color)' : 'var(--border-color)',
            color: (selectedJobPostingId || searchTerm.trim()) ? 'white' : 'var(--text-secondary)',
            cursor: (selectedJobPostingId || searchTerm.trim()) ? 'pointer' : 'not-allowed'
          }}
        >
          {isCalculatingRanking ? (
            <>
              <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid transparent', borderTop: '2px solid currentColor', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
              계산중...
            </>
          ) : (
            <>
              <FiBarChart2 size={16} />
              랭킹 계산
            </>
          )}
        </S.FilterButton>
      </S.SearchSection>

      <S.ViewModeSection>
        <S.ViewModeButton
          active={viewMode === 'grid'}
          onClick={() => handleViewModeChange('grid')}
        >
          <FiGrid size={14} />
          그리드
        </S.ViewModeButton>
        <S.ViewModeButton
          active={viewMode === 'board'}
          onClick={() => handleViewModeChange('board')}
        >
          <FiList size={14} />
          게시판
        </S.ViewModeButton>
      </S.ViewModeSection>
    </S.SearchBar>
  );
};

export default SearchFilterSection;
