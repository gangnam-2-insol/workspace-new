import React from 'react';
import { FiSearch, FiFilter, FiBarChart2, FiGrid, FiList, FiX } from 'react-icons/fi';
import * as S from '../styles';

const SearchBarUI = ({ filters, viewMode, setViewMode, onJobSelect, onFilterClick, onRankClick, onSearchChange, hasActiveFilters, filterStatusText }) => {
  return (
    <S.SearchBar>
      <S.SearchSection>
        <select
          value={filters.selectedJob}
          onChange={e=>onJobSelect(e.target.value)}
          style={{
            padding: '12px 16px',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            fontSize: '14px',
            background: 'white',
            width: '250px',
            cursor: 'pointer'
          }}
        >
          <option value=''>전체 채용공고</option>
          {filters.jobPostings.map(job=>(
            <option key={job.id||job._id} value={job.id||job._id}>{job.title}</option>
          ))}
        </select>

        <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
          <S.SearchInput
            placeholder={hasActiveFilters?filterStatusText:"지원자 이름, 직무, 기술스택을 입력하세요"}
            value={filters.search}
            onChange={e=>onSearchChange(e.target.value)}
          />
          {filters.search && (
            <button
              onClick={()=>onSearchChange('')}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px',
                color: 'var(--text-secondary)'
              }}
            >
              <FiX size={16} />
            </button>
          )}
        </div>

        <S.FilterButton onClick={onFilterClick} active={hasActiveFilters}>
         <FiFilter size={16} /> 필터
         {hasActiveFilters && (
           <span style={{
             background: 'white',
             color: 'var(--primary-color)',
             borderRadius: '50%',
             width: '18px',
             height: '18px',
             display: 'flex',
             alignItems: 'center',
             justifyContent: 'center',
             fontSize: '10px',
             fontWeight: '600'
           }}>!</span>
         )}
        </S.FilterButton>

        <S.FilterButton onClick={onRankClick}>
         <FiBarChart2 size={16} /> 랭킹 계산
        </S.FilterButton>
      </S.SearchSection>

      <div style={{ display: 'flex', gap: '8px' }}>
        <S.ViewModeButton active={viewMode==='grid'} onClick={()=>setViewMode('grid')}>
          <FiGrid size={14}/>그리드
        </S.ViewModeButton>
        <S.ViewModeButton active={viewMode==='board'} onClick={()=>setViewMode('board')}>
          <FiList size={14}/>게시판
        </S.ViewModeButton>
      </div>
    </S.SearchBar>
  );
};

export default SearchBarUI;
