import { useState, useCallback } from 'react';

// 지원자 목록 관련 상태
export const useApplicantList = () => {
  const [applicants, setApplicants] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [hasMore, setHasMore] = useState(true);

  return {
    applicants,
    setApplicants,
    isLoading,
    setIsLoading,
    currentPage,
    setCurrentPage,
    itemsPerPage,
    hasMore,
    setHasMore
  };
};

// 검색 및 필터링 관련 상태
export const useSearchAndFilter = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('전체');
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState([]);
  const [viewMode, setViewMode] = useState('grid');

  return {
    searchTerm,
    setSearchTerm,
    filterStatus,
    setFilterStatus,
    selectedJobs,
    setSelectedJobs,
    selectedExperience,
    setSelectedExperience,
    selectedStatus,
    setSelectedStatus,
    viewMode,
    setViewMode
  };
};

// 선택된 지원자 관련 상태
export const useSelectedApplicants = () => {
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [selectedApplicants, setSelectedApplicants] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [hoveredApplicant, setHoveredApplicant] = useState(null);

  return {
    selectedApplicant,
    setSelectedApplicant,
    selectedApplicants,
    setSelectedApplicants,
    selectAll,
    setSelectAll,
    hoveredApplicant,
    setHoveredApplicant
  };
};

// 모달 관련 상태
export const useModals = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filterModal, setFilterModal] = useState(false);
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [isCoverLetterAnalysisModalOpen, setIsCoverLetterAnalysisModalOpen] = useState(false);

  return {
    isModalOpen,
    setIsModalOpen,
    filterModal,
    setFilterModal,
    isResumeModalOpen,
    setIsResumeModalOpen,
    isPreviewModalOpen,
    setIsPreviewModalOpen,
    isCoverLetterAnalysisModalOpen,
    setIsCoverLetterAnalysisModalOpen
  };
};

// 문서 모달 관련 상태
export const useDocumentModal = () => {
  const [documentModal, setDocumentModal] = useState({
    isOpen: false,
    type: '',
    applicant: null,
    isOriginal: false,
    similarityData: null,
    isLoadingSimilarity: false,
    documentData: null
  });

  return {
    documentModal,
    setDocumentModal
  };
};

// 포트폴리오 관련 상태
export const usePortfolio = () => {
  const [portfolioView, setPortfolioView] = useState('select');
  const [portfolioData, setPortfolioData] = useState(null);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);

  return {
    portfolioView,
    setPortfolioView,
    portfolioData,
    setPortfolioData,
    isLoadingPortfolio,
    setIsLoadingPortfolio
  };
};

// 이력서 업로드 관련 상태
export const useResumeUpload = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [coverLetterFile, setCoverLetterFile] = useState(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [documentType, setDocumentType] = useState('이력서');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [existingApplicant, setExistingApplicant] = useState(null);
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  return {
    resumeFile,
    setResumeFile,
    coverLetterFile,
    setCoverLetterFile,
    githubUrl,
    setGithubUrl,
    documentType,
    setDocumentType,
    isAnalyzing,
    setIsAnalyzing,
    analysisResult,
    setAnalysisResult,
    existingApplicant,
    setExistingApplicant,
    isCheckingDuplicate,
    setIsCheckingDuplicate,
    replaceExisting,
    setReplaceExisting,
    isDragOver,
    setIsDragOver
  };
};

// 통계 관련 상태
export const useStats = () => {
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    reviewing: 0,
    passed: 0,
    failed: 0,
    hired: 0
  });

  return {
    stats,
    setStats
  };
};

// 랭킹 관련 상태
export const useRanking = () => {
  const [isCalculatingRanking, setIsCalculatingRanking] = useState(false);
  const [rankingResults, setRankingResults] = useState(null);

  return {
    isCalculatingRanking,
    setIsCalculatingRanking,
    rankingResults,
    setRankingResults
  };
};

// 채용공고 관련 상태
export const useJobPostings = () => {
  const [jobPostings, setJobPostings] = useState([]);
  const [selectedJobPostingId, setSelectedJobPostingId] = useState('');
  const [visibleJobPostingsCount, setVisibleJobPostingsCount] = useState(5);

  return {
    jobPostings,
    setJobPostings,
    selectedJobPostingId,
    setSelectedJobPostingId,
    visibleJobPostingsCount,
    setVisibleJobPostingsCount
  };
};

// 기타 상태들
export const useOtherStates = () => {
  const [selectedResumeApplicant, setSelectedResumeApplicant] = useState(null);
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);
  const [resumeData, setResumeData] = useState({
    name: '',
    email: '',
    phone: '',
    experience: '',
    education: '',
    skills: []
  });
  const [previewDocument, setPreviewDocument] = useState(null);
  const [selectedCoverLetterData, setSelectedCoverLetterData] = useState(null);
  const [selectedApplicantForCoverLetter, setSelectedApplicantForCoverLetter] = useState(null);

  return {
    selectedResumeApplicant,
    setSelectedResumeApplicant,
    showDetailedAnalysis,
    setShowDetailedAnalysis,
    resumeData,
    setResumeData,
    previewDocument,
    setPreviewDocument,
    selectedCoverLetterData,
    setSelectedCoverLetterData,
    selectedApplicantForCoverLetter,
    setSelectedApplicantForCoverLetter
  };
};
