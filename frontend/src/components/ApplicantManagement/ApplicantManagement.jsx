import React, { useState, useEffect, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { FiFileText } from 'react-icons/fi';
import useApplicants from './hooks/useApplicants';
import useStats from './hooks/useStats';
import useSelection from './hooks/useSelection';
import useFilters from './hooks/useFilters';
import useRanking from './hooks/useRanking';
import ApplicantCard from './components/ApplicantCard';
import ApplicantBoard from './components/ApplicantBoard';
import StatsCards from './components/StatsCards';
import SearchBarUI from './components/SearchBar';
import ApplicantManagementModals from './ApplicantManagementModals';
import * as S from './styles';
import * as U from './utils';

/* ---------- main component ---------- */
const ApplicantManagement = () => {
  /* 1. Data hooks */
  const { applicants, loading, reload } = useApplicants();
  const { stats, loading: statsLoading, reload: reloadStats } = useStats();

  /* 2. UI state */
  const [viewMode, setViewMode] = useState('grid');        // 'grid' | 'board'
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  /* 3. Selection utilities */
  const { selected, toggle, clear, selectAll, isAll } = useSelection();

  /* 4. Filter utilities */
  const {
    search,
    setSearch,
    jobPostings,
    selectedJob,
    setSelectedJob,
    jobs,
    setJobs,
    experience,
    setExperience,
    status,
    setStatus
  } = useFilters();

  /* 6. 페이지네이션 */
  const filteredApplicants = U.filterApplicants(applicants, {
    search,
    jobs,
    experience,
    status,
    job: selectedJob
  });

  /* 5. 랭킹 훅 */
  const { results: ranking, loading: rankLoading, calculateRanking } = useRanking(filteredApplicants, { search });

  const totalPages = Math.ceil(filteredApplicants.length / itemsPerPage);
  const paginated = filteredApplicants.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  /* 7. 모달 상태 */
  const [detailModal, setDetailModal] = useState({ isOpen: false, applicant: null });
  const [resumeModal, setResumeModal] = useState({ isOpen: false, applicant: null });
  const [documentModal, setDocumentModal] = useState({
    isOpen: false,
    type: '',
    applicant: null,
    documentData: null,
    similarityData: null,
    isLoadingSimilarity: false
  });
  const [newApplicantModal, setNewApplicantModal] = useState({
    isOpen: false,
    existingApplicant: null,
    isCheckingDuplicate: false
  });

  /* 8. 이벤트 핸들러 */
  const handleCardClick = useCallback((applicant) => {
    setDetailModal({ isOpen: true, applicant });
  }, []);

  const handleDetailModalClose = useCallback(() => {
    setDetailModal({ isOpen: false, applicant: null });
  }, []);

  const handleResumeModalOpen = useCallback(() => {
    setNewApplicantModal({ isOpen: true, existingApplicant: null, isCheckingDuplicate: false });
  }, []);

  const handleResumeModalClose = useCallback(() => {
    setNewApplicantModal({ isOpen: false, existingApplicant: null, isCheckingDuplicate: false });
  }, []);

  const handleDocumentModalOpen = useCallback((type, applicant) => {
    setDocumentModal({
      isOpen: true,
      type,
      applicant,
      documentData: null,
      similarityData: null,
      isLoadingSimilarity: false
    });
  }, []);

  const handleDocumentModalClose = useCallback(() => {
    setDocumentModal({
      isOpen: false,
      type: '',
      applicant: null,
      documentData: null,
      similarityData: null,
      isLoadingSimilarity: false
    });
  }, []);

  const handleNewApplicantSubmit = useCallback((result) => {
    // 새 지원자 등록 후 목록 새로고침
    reload();
    handleResumeModalClose();
  }, [reload, handleResumeModalClose]);

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  const handleJobChange = (jobId) => {
    setSelectedJob(jobId);
  };

  const handleFilterClick = () => {
    // 필터 모달 로직 구현 필요
    console.log('필터 모달 열기');
  };

  const handleRankClick = () => {
    calculateRanking();
  };

  const handleSearchChange = (value) => {
    setSearch(value);
    setCurrentPage(1); // 검색 시 첫 페이지로 이동
  };

  const hasActiveFilters = Boolean(search || jobs.length || experience.length || status.length);
  const filterStatusText = `검색 결과: ${filteredApplicants.length}개`;

  /* 9. UI 렌더링 */
  return (
    <S.Container>
      {/* Header + Loader */}
      <S.Header>
        <S.HeaderContent>
          <S.HeaderLeft>
            <S.Title>지원자 관리</S.Title>
            <S.Subtitle>채용 공고별 지원자 현황을 관리하고 검토하세요</S.Subtitle>
          </S.HeaderLeft>
          <S.HeaderRight>
            <S.NewResumeButton onClick={handleResumeModalOpen}>
              <FiFileText size={16} />새 지원자 등록
            </S.NewResumeButton>
          </S.HeaderRight>
        </S.HeaderContent>

        {loading && (
          <S.LoadingOverlay>
            <S.LoadingSpinner>
              <div className="spinner" />
              <span>데이터를 불러오는 중…</span>
            </S.LoadingSpinner>
          </S.LoadingOverlay>
        )}
      </S.Header>

      {/* 통계 카드 */}
      <S.StatsGrid>
        <StatsCards stats={stats} onSendMail={() => {}} />
      </S.StatsGrid>

      {/* 검색 / 필터 / 랭킹 컨트롤 */}
      <SearchBarUI
        filters={{
          search,
          jobPostings,
          selectedJob,
          jobs,
          experience,
          status
        }}
        viewMode={viewMode}
        setViewMode={handleViewModeChange}
        onJobSelect={handleJobChange}
        onFilterClick={handleFilterClick}
        onRankClick={handleRankClick}
        onSearchChange={handleSearchChange}
        hasActiveFilters={hasActiveFilters}
        filterStatusText={filterStatusText}
      />

             {rankLoading && <div style={{ textAlign: 'center', padding: '20px', fontSize: '16px', color: 'var(--text-secondary)' }}>랭킹 계산 중…</div>}

             {/* 랭킹 테이블 (있을 때) */}
       {ranking && ranking.length > 0 && (
         <div style={{
           background: 'white',
           borderRadius: '16px',
           padding: '24px',
           marginBottom: '24px',
           boxShadow: '0 4px 20px rgba(0,0,0,.08)',
           border: '1px solid var(--border-color)'
         }}>
           <h3>랭킹 결과</h3>
           <p>총 {ranking.length}명의 지원자가 랭킹되었습니다.</p>
         </div>
       )}

      {/* 그리드 vs 보드 */}
      {viewMode === 'grid' ? (
        <S.ApplicantsGrid>
          {paginated.map(app => (
            <ApplicantCard
              key={app.id}
              applicant={app}
              onClick={handleCardClick}
              selectedJob={selectedJob}
            />
          ))}
        </S.ApplicantsGrid>
             ) : (
         <S.ApplicantsBoard>
           <S.BoardHeader>
             <div>선택</div>
             <div>이름</div>
             <div>직무</div>
             <div>이메일</div>
             <div>전화번호</div>
             <div>기술스택</div>
             <div>상태</div>
             <div>점수</div>
           </S.BoardHeader>
           {paginated.map(app => (
             <ApplicantBoard
               key={app.id}
               applicant={app}
               onClick={handleCardClick}
               selected={selected}
               onSelectToggle={toggle}
               selectedJob={selectedJob}
             />
           ))}
         </S.ApplicantsBoard>
       )}

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <S.Pagination>
          <S.PaginationButton disabled={currentPage === 1} onClick={() => setCurrentPage(1)}>&lt;&lt;</S.PaginationButton>
          <S.PaginationButton disabled={currentPage === 1} onClick={() => setCurrentPage(p => Math.max(1, p - 1))}>&lt;</S.PaginationButton>
          <S.PaginationNumbers>
            {Array.from({ length: totalPages }, (_, i) => (
              <S.PaginationNumber key={i} isActive={currentPage === i + 1} onClick={() => setCurrentPage(i + 1)}>
                {i + 1}
              </S.PaginationNumber>
            ))}
          </S.PaginationNumbers>
          <S.PaginationButton disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}>&gt;</S.PaginationButton>
          <S.PaginationButton disabled={currentPage === totalPages} onClick={() => setCurrentPage(totalPages)}>&gt;&gt;</S.PaginationButton>
        </S.Pagination>
      )}

      {/* ================================= Modal 구간 ================================= */}
      <ApplicantManagementModals
        detailModal={detailModal}
        resumeModal={resumeModal}
        documentModal={documentModal}
        newApplicantModal={newApplicantModal}
        onDetailModalOpen={setDetailModal}
        onDetailModalClose={handleDetailModalClose}
        onResumeModalOpen={setResumeModal}
        onResumeModalClose={handleResumeModalClose}
        onDocumentModalOpen={handleDocumentModalOpen}
        onDocumentModalClose={handleDocumentModalClose}
        onNewApplicantModalOpen={setNewApplicantModal}
        onNewApplicantModalClose={handleResumeModalClose}
        onResumeSubmit={handleNewApplicantSubmit}
      />
    </S.Container>
  );
};

export default ApplicantManagement;
