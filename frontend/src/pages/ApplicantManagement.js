import React, { useState, useEffect, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useSuspicion } from '../contexts/SuspicionContext';
import {
  FiUser,
  FiMail,
  FiPhone,
  FiFileText,
  FiSearch,
  FiCheck,
  FiX,
  FiStar,
  FiClock,
  FiFile,
  FiMessageSquare,
  FiCode,
  FiBarChart2,
  FiGitBranch,
  FiArrowLeft,
  FiTrendingUp
} from 'react-icons/fi';

// 분리된 컴포넌트들 import
import HeaderSection from './ApplicantManagement/components/HeaderSection';
import StatsSection from './ApplicantManagement/components/StatsSection';
import SearchFilterSection from './ApplicantManagement/components/SearchFilterSection';
import RankingSection from './ApplicantManagement/components/RankingSection';
import DetailedAnalysisModal from '../components/DetailedAnalysisModal';
import ResumeModal from '../components/ResumeModal';
import CoverLetterSummary from '../components/CoverLetterSummary';
import CoverLetterAnalysis from '../components/CoverLetterAnalysis';
import CoverLetterAnalysisModal from '../components/CoverLetterAnalysisModal';
import GithubSummaryPanel from './PortfolioSummary/GithubSummaryPanel';
import PortfolioSummaryPanel from './PortfolioSummary/PortfolioSummaryPanel';
import jobPostingApi from '../services/jobPostingApi';
import CoverLetterAnalysisApi from '../services/coverLetterAnalysisApi';
import MemoizedApplicantCard from '../components/ApplicantManagement/ApplicantCard';
import FilterModal from '../components/ApplicantManagement/FilterModal';
import ResumeUploadModal from '../components/ApplicantManagement/ResumeUploadModal';
import {
  calculateAverageScore,
  getResumeAnalysisLabel,
  getCoverLetterAnalysisLabel,
  getPortfolioAnalysisLabel,
  getStatusText,
  extractSkillsFromAnalysis,
  extractExperienceFromAnalysis,
  extractEducationFromAnalysis,
  extractRecommendationsFromAnalysis
} from '../utils/analysisHelpers';
import {
  applicantApi,
  documentApi,
  ocrApi,
  mailApi
} from '../services/applicantApi';

// 커스텀 훅들 import
import {
  useApplicantList,
  useSearchAndFilter,
  useSelectedApplicants,
  useModals,
  useDocumentModal,
  usePortfolio,
  useResumeUpload,
  useStats,
  useRanking,
  useJobPostings,
  useOtherStates
} from '../hooks/useApplicantManagement';

// 필터링 유틸리티 import
import {
  filterAndScoreApplicants,
  paginateApplicants,
  sortApplicants
} from '../utils/filterHelpers';

// 스타일 컴포넌트들을 명시적으로 import
import {
  Container,
  LoadingOverlay,
  LoadingSpinner,
  Wrapper,
  EmptyState,
} from './ApplicantManagement/styles/CommonStyles';

import {
  HeaderRowBoard,
  HeaderCheckbox,
  CheckboxInput,
  HeaderName,
  HeaderPosition,
  HeaderEmail,
  HeaderPhone,
  HeaderSkills,
  HeaderDate,
  HeaderScore,
  HeaderActions,
  SelectionInfo,
  NoResultsMessage,
  FixedActionBar,
  ActionButtonsGroup,
  ApplicantCheckbox,
} from './ApplicantManagement/styles/ApplicantHeaderStyles';

import {
  ApplicantCard,
  ApplicantHeader,
  ApplicantInfo,
  Avatar,
  ApplicantDetails,
  ApplicantName,
  ApplicantPosition,
  ApplicantDate,
  ApplicantEmail,
  ApplicantPhone,
  ContactItem,
  ApplicantSkills,
  SkillTag,
  ApplicantActions,
  StatusBadge,
  StatusSelect,
  StatusColumnWrapper,
  ActionButton,
  PassButton,
  PendingButton,
  RejectButton,
  ResumeViewButton,
} from './ApplicantManagement/styles/ApplicantCardStyles';

import {
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalTitle,
  CloseButton,
  ProfileSection,
  SectionTitle,
  ProfileGrid,
  ProfileItem,
  ProfileLabel,
  ProfileValue,
  SummarySection,
  SummaryTitle,
  SummaryText,
  DocumentButtons,
  DocumentButton,
  ResumeButton,
  DocumentModalOverlay,
  DocumentModalContent,
  DocumentModalHeader,
  DocumentModalTitle,
  DocumentCloseButton,
  DocumentHeaderActions,
  DocumentOriginalButton,
  DocumentContent,
  DocumentSection,
  DocumentSectionTitle,
  DocumentList,
  DocumentListItem,
  DocumentGrid,
  DocumentCard,
  DocumentCardTitle,
  DocumentCardText,
  SelectionGrid,
  SelectionCard,
  SelectionIcon,
  SelectionTitle,
  SelectionDesc,
  DocumentPreviewModal,
  DocumentPreviewContent,
  DocumentPreviewHeader,
  DocumentPreviewTitle,
  DocumentPreviewFooter,
  PreviewCloseButton,
  DocumentText,
  PreviewButton,
} from './ApplicantManagement/styles/ModalStyles';

import {
  PaginationContainer,
  PaginationButton,
  PageNumbers,
  PageNumber,
} from './ApplicantManagement/styles/PaginationStyles';

import {
  BoardContainer,
  BoardApplicantCard,
  BoardCardHeader,
  CardCheckbox,
  CardAvatar,
  BoardCardContent,
  CardName,
  CardPosition,
  CardDepartment,
  CardContact,
  CardSkills,
  CardScore,
  CardDate,
  BoardCardActions,
  CardActionButton,
  AiAnalysisSectionBoard,
  AiAnalysisTitleBoard,
  SuitabilityGraphBoard,
  CircularProgressBoard,
  PercentageTextBoard,
  SuitabilityValueBoard,
  BoardRankBadge,
  BoardAvatar,
  FixedPassButton,
  FixedPendingButton,
  FixedRejectButton,
} from './ApplicantManagement/styles/BoardViewStyles';

import {
  AiAnalysisSection,
  AiAnalysisTitle,
  AiAnalysisContent,
  SuitabilityGraph,
  CircularProgress,
  PercentageText,
  SuitabilityInfo,
  SuitabilityLabel,
  SuitabilityValue,
  ApplicantScoreBoard,
  ScoreBadge,
  RankBadge,
  TopRankBadge,
  AnalysisScoreDisplay,
  AnalysisScoreCircle,
  AnalysisScoreInfo,
  AnalysisScoreLabel,
  AnalysisScoreValue,
  SkillsSection,
  SkillsTitle,
  SkillsGrid,
  ApplicantsGrid,
  ApplicantsBoard,
} from './ApplicantManagement/styles/ApplicantActionsStyles';

import {
  ApplicantInfoContainer,
  InfoField,
  InfoLabel,
  InfoInput,
  ResumeFormActions,
  ResumeSubmitButton,
  DeleteButton,
  GithubInputContainer,
  GithubInput,
  GithubInputDescription,
  ApplicantRow,
  NameText,
  EmailText,
  PositionBadge,
  DepartmentText,
  ContactInfo,
  SkillsContainer,
  MoreSkills,
  NoSkills,
  AvgScore,
  ActionButtonGroup,
  CornerBadge,
  CardHeader,
  CardContent,
  InfoRow,
  CardActions,
} from './ApplicantManagement/styles/ApplicantInfoStyles';

// 중복된 import 제거됨 - 이제 네임스페이스로 import됨

// 디버깅을 위한 로그 함수
const DEBUG = process.env.NODE_ENV === 'development';
const log = (message, data = null) => {
  if (DEBUG) {
    console.log(`🔍 [ApplicantManagement] ${message}`, data || '');
  }
};

const logError = (message, error = null) => {
  if (DEBUG) {
    console.error(`❌ [ApplicantManagement] ${message}`, error || '');
  }
};

const ApplicantManagement = () => {
  log('컴포넌트 초기화 시작');
  
  // 전역 표절 의심도 상태
  const { updateSuspicionData, setLoadingState, getSuspicionData, getLoadingState } = useSuspicion();

  // 커스텀 훅들을 사용하여 상태 관리
  const {
    applicants,
    setApplicants,
    isLoading,
    setIsLoading,
    currentPage,
    setCurrentPage,
    itemsPerPage,
    hasMore,
    setHasMore
  } = useApplicantList();

  const {
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
  } = useSearchAndFilter();

  const {
    selectedApplicant,
    setSelectedApplicant,
    selectedApplicants,
    setSelectedApplicants,
    selectAll,
    setSelectAll,
    hoveredApplicant,
    setHoveredApplicant
  } = useSelectedApplicants();

  const {
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
  } = useModals();

  const {
    documentModal,
    setDocumentModal
  } = useDocumentModal();

  const {
    portfolioView,
    setPortfolioView,
    portfolioData,
    setPortfolioData,
    isLoadingPortfolio,
    setIsLoadingPortfolio
  } = usePortfolio();

  const {
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
  } = useResumeUpload();

  const {
    stats,
    setStats
  } = useStats();

  const {
    isCalculatingRanking,
    setIsCalculatingRanking,
    rankingResults,
    setRankingResults
  } = useRanking();

  const {
    jobPostings,
    setJobPostings,
    selectedJobPostingId,
    setSelectedJobPostingId,
    visibleJobPostingsCount,
    setVisibleJobPostingsCount
  } = useJobPostings();

  const {
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
  } = useOtherStates();

  // 디버깅을 위한 상태 추적
  console.log('🔍 ApplicantManagement 상태 추적:', {
    applicantsCount: applicants.length,
    selectedJobPostingId,
    selectedJobPostingIdType: typeof selectedJobPostingId,
    jobPostingsCount: jobPostings.length,
    currentPage,
    itemsPerPage
  });



  // 채용공고 목록 가져오기
  const loadJobPostings = async () => {
    try {
      console.log('🔄 채용공고 목록 로딩 시작...');
      const data = await jobPostingApi.getJobPostings();
      console.log('📋 받은 채용공고 데이터:', data);
      console.log('📊 채용공고 개수:', Array.isArray(data) ? data.length : '배열이 아님');
      setJobPostings(data);
      console.log('✅ 채용공고 상태 업데이트 완료');
    } catch (error) {
      console.error('❌ 채용공고 목록 로드 실패:', error);
    }
  };

  // 메일 발송 핸들러
  const handleSendMail = useCallback(async (statusType) => {
    const statusMap = {
      'passed': '합격',
      'rejected': '불합격'
    };

    const statusText = statusMap[statusType];
    const targetApplicants = applicants.filter(applicant => {
      if (statusType === 'passed') {
        return applicant.status === '서류합격' || applicant.status === '최종합격';
      } else if (statusType === 'rejected') {
        return applicant.status === '서류불합격';
      }
      return false;
    });

    if (targetApplicants.length === 0) {
      alert(`${statusText}자가 없습니다.`);
      return;
    }

    const confirmed = window.confirm(
      `${targetApplicants.length}명의 ${statusText}자들에게 자동으로 메일을 보내시겠습니까?\n\n` +
      `- ${statusText}자 수: ${targetApplicants.length}명\n` +
      `- 메일 양식은 설정 페이지에서 관리됩니다.`
    );

    if (confirmed) {
      try {
        console.log(`📧 ${statusText}자들에게 메일 발송 시작:`, targetApplicants.length, '명');

        // 메일 발송 API 호출
        const result = await mailApi.sendBulkMail(statusType);

        if (result.success) {
          alert(`✅ ${result.success_count}명의 ${statusText}자들에게 메일이 성공적으로 발송되었습니다.\n\n실패: ${result.failed_count}건`);
        } else {
          alert(`❌ 메일 발송 실패: ${result.message}`);
        }

      } catch (error) {
        console.error('메일 발송 실패:', error);
        alert('메일 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    }
  }, [applicants]);

  // 채용공고별 랭킹 계산 함수
  const calculateJobPostingRanking = useCallback(async (jobPostingId) => {
    try {
      setIsCalculatingRanking(true);
      console.log('🎯 채용공고별 랭킹 계산 시작:', jobPostingId);
      console.log('📊 전체 지원자 수:', applicants.length);
      console.log('📊 지원자들의 job_posting_id:', applicants.map(app => ({ name: app.name, job_posting_id: app.job_posting_id })));
      console.log('🎯 찾고 있는 채용공고 ID:', jobPostingId);

      // 해당 채용공고에 속한 지원자들만 필터링
      const jobPostingApplicants = applicants.filter(applicant => {
        console.log('🔍 지원자 필터링 중:', {
          name: applicant.name,
          applicant_job_posting_id: applicant.job_posting_id,
          applicant_job_posting_id_type: typeof applicant.job_posting_id,
          selected_job_posting_id: jobPostingId,
          selected_job_posting_id_type: typeof jobPostingId,
          is_match: applicant.job_posting_id === jobPostingId
        });

        const matches = String(applicant.job_posting_id) === String(jobPostingId);
        if (matches) {
          console.log('✅ 매칭된 지원자:', applicant.name, 'job_posting_id:', applicant.job_posting_id);
        }
        return matches;
      });

      console.log('📊 해당 채용공고 지원자 수:', jobPostingApplicants.length);
      console.log('📊 필터링된 지원자들:', jobPostingApplicants.map(app => ({ name: app.name, job_posting_id: app.job_posting_id })));

      if (jobPostingApplicants.length === 0) {
        console.log('⚠️ 해당 채용공고에 지원자가 없습니다.');
        setRankingResults(null);
        // 세션 스토리지에서 랭킹 결과 삭제
        try {
          sessionStorage.removeItem('rankingResults');
        } catch (error) {
          console.error('랭킹 결과 세션 스토리지 삭제 실패:', error);
        }
        return;
      }

      // 랭킹 데이터 계산
      const rankingData = jobPostingApplicants.map(applicant => {
        let totalScore = 0;
        let maxPossibleScore = 0;

        // 프로젝트 마에스트로 점수 (analysisScore) - 100점 만점
        if (applicant.analysisScore !== undefined && applicant.analysisScore !== null) {
          totalScore = applicant.analysisScore;
          maxPossibleScore = 100;
        } else {
          // 기존 분석 데이터가 있는 경우 (하위 호환성)
          // 이력서 분석 점수 (30%)
          if (applicant.resume_analysis) {
            const resumeScore = calculateAverageScore(applicant.resume_analysis) * 0.3;
            totalScore += resumeScore;
            maxPossibleScore += 10 * 0.3;
          }

          // 자소서 분석 점수 (30%)
          if (applicant.cover_letter_analysis) {
            const coverLetterScore = calculateAverageScore(applicant.cover_letter_analysis) * 0.3;
            totalScore += coverLetterScore;
            maxPossibleScore += 10 * 0.3;
          }

          // 포트폴리오 분석 점수 (20%)
          if (applicant.portfolio_analysis) {
            const portfolioScore = calculateAverageScore(applicant.portfolio_analysis) * 0.2;
            totalScore += portfolioScore;
            maxPossibleScore += 10 * 0.2;
          }

          // 기본 점수 (20%) - 분석 데이터가 없는 경우를 위해
          const basicScore = 5 * 0.2; // 기본적으로 중간 점수
          totalScore += basicScore;
          maxPossibleScore += 10 * 0.2;

          // 최종 점수 (100점 만점)
          totalScore = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;
        }

        return {
          applicant,
          totalScore: Math.round(totalScore * 10) / 10,
          resumeScore: applicant.analysisScore || 0, // 프로젝트 마에스트로 점수 사용
          coverLetterScore: 0, // 현재 데이터에는 없음
          portfolioScore: 0, // 현재 데이터에는 없음
          keywordScore: 5, // 기본값
          rank: 0, // 순위는 나중에 설정
          rankText: '', // 순위 텍스트는 나중에 설정
          breakdown: {
            resume: applicant.analysisScore || 0,
            coverLetter: 0,
            portfolio: 0,
            keywordMatching: 5
          }
        };
      });

      // 점수별로 정렬 (내림차순)
      const sortedResults = rankingData.sort((a, b) => b.totalScore - a.totalScore);

      // 1,2,3위를 무조건 맨 앞에 배치하고, 나머지는 점수순으로 정렬
      const top3 = sortedResults.slice(0, 3);
      const rest = sortedResults.slice(3);

      // 나머지 지원자들을 점수순으로 정렬
      const sortedRest = rest.sort((a, b) => b.totalScore - a.totalScore);

      // 최종 결과: 1,2,3위 + 나머지
      const finalResults = [...top3, ...sortedRest];

      // 순위 설정 (메달 이모지)
      finalResults.forEach((result, index) => {
        result.rank = index + 1;
        if (index === 0) result.rankText = '🥇 1위';
        else if (index === 1) result.rankText = '🥈 2위';
        else if (index === 2) result.rankText = '🥉 3위';
        else result.rankText = `${index + 1}위`;
      });

      setRankingResults({
        results: finalResults,
        keyword: `채용공고: ${jobPostings.find(job => job._id === jobPostingId || job.id === jobPostingId)?.title || ''}`,
        totalCount: finalResults.length
      });

      console.log('✅ 채용공고별 랭킹 계산 완료:', finalResults.length, '명');
      console.log('🏆 1,2,3위:', finalResults.slice(0, 3).map(r => `${r.rankText} ${r.applicant.name} (${r.totalScore}점)`));

    } catch (error) {
      console.error('❌ 채용공고별 랭킹 계산 실패:', error);
      alert('랭킹 계산 중 오류가 발생했습니다.');
    } finally {
      setIsCalculatingRanking(false);
    }
  }, [applicants, jobPostings]);

  // 채용공고 선택 핸들러
  const handleJobPostingChange = useCallback(async (jobPostingId) => {
    console.log('🎯 handleJobPostingChange 호출됨:', {
      jobPostingId,
      jobPostingIdType: typeof jobPostingId,
      isEmpty: jobPostingId === '',
      isNull: jobPostingId === null,
      isUndefined: jobPostingId === undefined
    });
    console.log('📊 현재 지원자들의 job_posting_id:', applicants.map(app => ({ name: app.name, job_posting_id: app.job_posting_id })));
    console.log('📊 현재 채용공고 목록:', jobPostings.map(job => ({ title: job.title, id: job._id || job.id })));

    setSelectedJobPostingId(jobPostingId);
    setVisibleJobPostingsCount(5); // 채용공고 선택 시 표시 개수 초기화

    // 특정 채용공고를 선택했을 때 자동으로 랭킹 계산 활성화
    if (jobPostingId && jobPostingId !== '') {
      console.log('🎯 채용공고 선택됨, 자동 랭킹 계산 시작:', jobPostingId);

      // 즉시 랭킹 계산 실행
      calculateJobPostingRanking(jobPostingId);
    } else {
      // 전체 채용공고 선택 시 랭킹 초기화
      console.log('🎯 채용공고 선택 해제됨 - 랭킹 초기화 시작');
      setRankingResults(null);
      // 세션 스토리지에서 랭킹 결과 삭제
      try {
        sessionStorage.removeItem('rankingResults');
        console.log('✅ 세션 스토리지에서 랭킹 결과 삭제 완료');
      } catch (error) {
        console.error('랭킹 결과 세션 스토리지 삭제 실패:', error);
      }
      setSearchTerm('');
      console.log('✅ 전체 채용공고 선택 시 초기화 완료');
    }
  }, [calculateJobPostingRanking, applicants, jobPostings]);

  // 메모이제이션된 필터링된 지원자 목록 (순위 포함)
  const filteredApplicants = useMemo(() => {
    log('useMemo: filteredApplicants 계산 시작');
    const filters = {
      searchTerm,
      filterStatus,
      selectedJobs,
      selectedExperience,
      selectedStatus,
      selectedJobPostingId
    };
    const result = filterAndScoreApplicants(applicants, filters);
    log('useMemo: filteredApplicants 계산 완료', { count: result.length, filters });
    return result;
  }, [applicants, searchTerm, filterStatus, selectedJobs, selectedExperience, selectedStatus, selectedJobPostingId]);

  // selectedJobPostingId 변경 시 랭킹 결과 관리
  useEffect(() => {
    console.log('🔄 selectedJobPostingId 변경 감지:', {
      selectedJobPostingId,
      selectedJobPostingIdType: typeof selectedJobPostingId,
      hasRankingResults: !!rankingResults
    });

    if (!selectedJobPostingId || selectedJobPostingId === '') {
      // 전체 채용공고 선택 시 랭킹 결과 초기화
      if (rankingResults) {
        console.log('🚫 전체 채용공고 선택 - 랭킹 결과 초기화');
        setRankingResults(null);
        // 세션 스토리지에서 랭킹 결과 삭제
        try {
          sessionStorage.removeItem('rankingResults');
          console.log('✅ 세션 스토리지에서 랭킹 결과 삭제 완료');
        } catch (error) {
          console.error('랭킹 결과 세션 스토리지 삭제 실패:', error);
        }
      }
    }
  }, [selectedJobPostingId, rankingResults]);

  // 필터나 검색이 변경될 때 랭킹 결과 초기화 (채용공고 선택 시에는 제외)
  useEffect(() => {
    if (rankingResults && !selectedJobPostingId) {
      setRankingResults(null);
      // 세션 스토리지에서 랭킹 결과 삭제
      try {
        sessionStorage.removeItem('rankingResults');
      } catch (error) {
        console.error('랭킹 결과 세션 스토리지 삭제 실패:', error);
      }
      console.log('🔄 필터/검색 변경으로 랭킹 결과 초기화');
    }
  }, [searchTerm, filterStatus, selectedJobs, selectedExperience, selectedStatus]);

  // 컴포넌트 마운트 시 채용공고 목록 로드
  useEffect(() => {
    loadJobPostings();
  }, []);

  // 키워드 매칭 점수 계산 함수
  const calculateKeywordMatchingScore = useCallback((applicant, keyword) => {
    const keywordLower = keyword.toLowerCase();
    let score = 0;
    let matches = 0;

    // 이름에서 키워드 매칭
    if (applicant.name && applicant.name.toLowerCase().includes(keywordLower)) {
      score += 3;
      matches++;
    }

    // 직무에서 키워드 매칭
    if (applicant.position && applicant.position.toLowerCase().includes(keywordLower)) {
      score += 4;
      matches++;
    }

    // 기술스택에서 키워드 매칭
    if (applicant.skills) {
      const skills = Array.isArray(applicant.skills) ? applicant.skills : applicant.skills.split(',');
      skills.forEach(skill => {
        if (skill.trim().toLowerCase().includes(keywordLower)) {
          score += 5;
          matches++;
        }
      });
    }

    // 이력서 분석 피드백에서 키워드 매칭
    if (applicant.resume_analysis) {
      Object.values(applicant.resume_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 자소서 분석 피드백에서 키워드 매칭
    if (applicant.cover_letter_analysis) {
      Object.values(applicant.cover_letter_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 포트폴리오 분석 피드백에서 키워드 매칭
    if (applicant.portfolio_analysis) {
      Object.values(applicant.portfolio_analysis).forEach(item => {
        if (item && item.feedback && item.feedback.toLowerCase().includes(keywordLower)) {
          score += 2;
          matches++;
        }
      });
    }

    // 최대 10점으로 정규화
    return Math.min(score, 10);
  }, []);

  // 등수 텍스트 생성 함수
  const getRankText = useCallback((rank, total) => {
    if (rank === 1) return '🥇 1등';
    if (rank === 2) return '🥈 2등';
    if (rank === 3) return '🥉 3등';
    if (rank <= Math.ceil(total * 0.1)) return `🏅 ${rank}등`;
    if (rank <= Math.ceil(total * 0.3)) return `⭐ ${rank}등`;
    if (rank <= Math.ceil(total * 0.5)) return `✨ ${rank}등`;
    return `${rank}등`;
  }, []);



  // 키워드 랭킹 계산 함수
  const calculateKeywordRanking = useCallback(async () => {
    if (!searchTerm.trim()) {
      alert('검색어를 입력해주세요.');
      return;
    }

    if (filteredApplicants.length === 0) {
      alert('검색 결과가 없습니다. 다른 검색어나 필터 조건을 시도해보세요.');
      return;
    }

    try {
      setIsCalculatingRanking(true);
      console.log('🔍 키워드 랭킹 계산 시작:', searchTerm);
      console.log('📊 대상 지원자 수:', filteredApplicants.length);

      // 키워드와 관련된 점수 계산
      const rankingData = filteredApplicants.map(applicant => {
        let totalScore = 0;
        let keywordMatches = 0;
        let maxPossibleScore = 0;

        // 프로젝트 마에스트로 점수 (analysisScore) - 100점 만점
        if (applicant.analysisScore !== undefined && applicant.analysisScore !== null) {
          totalScore = applicant.analysisScore;
          maxPossibleScore = 100;
        } else {
          // 기존 분석 데이터가 있는 경우 (하위 호환성)
          // 이력서 분석 점수 (30%)
          if (applicant.resume_analysis) {
            const resumeScore = calculateAverageScore(applicant.resume_analysis) * 0.3;
            totalScore += resumeScore;
            maxPossibleScore += 10 * 0.3;
          }

          // 자소서 분석 점수 (30%)
          if (applicant.cover_letter_analysis) {
            const coverLetterScore = calculateAverageScore(applicant.cover_letter_analysis) * 0.3;
            totalScore += coverLetterScore;
            maxPossibleScore += 10 * 0.3;
          }

          // 포트폴리오 분석 점수 (20%)
          if (applicant.portfolio_analysis) {
            const portfolioScore = calculateAverageScore(applicant.portfolio_analysis) * 0.2;
            totalScore += portfolioScore;
            maxPossibleScore += 10 * 0.2;
          }

          // 키워드 매칭 점수 (20%)
          const keywordScore = calculateKeywordMatchingScore(applicant, searchTerm) * 0.2;
          totalScore += keywordScore;
          maxPossibleScore += 10 * 0.2;

          // 최종 점수 (100점 만점)
          totalScore = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;
        }

        return {
          applicant,
          totalScore: Math.round(totalScore * 10) / 10,
          keywordMatches,
          breakdown: {
            resume: applicant.analysisScore || 0, // 프로젝트 마에스트로 점수 사용
            coverLetter: 0, // 현재 데이터에는 없음
            portfolio: 0, // 현재 데이터에는 없음
            keywordMatching: Math.round(calculateKeywordMatchingScore(applicant, searchTerm) * 5) // 0.2 * 10 * 5 = 10점 만점
          }
        };
      });

      // 점수별 내림차순 정렬
      rankingData.sort((a, b) => b.totalScore - a.totalScore);

      // 등수 추가
      const rankedData = rankingData.map((item, index) => ({
        ...item,
        rank: index + 1,
        rankText: getRankText(index + 1, rankingData.length)
      }));

      // 세션 스토리지에 랭킹 결과 저장
      try {
        sessionStorage.setItem('rankingResults', JSON.stringify(rankedData));
        console.log('💾 세션 스토리지에 랭킹 결과 저장됨');
      } catch (error) {
        console.error('랭킹 결과 세션 스토리지 저장 실패:', error);
      }

      setRankingResults(rankedData);
      console.log('✅ 랭킹 계산 완료:', rankedData.length + '명');

      // 성공 메시지 표시
      const topRank = rankedData[0];
      if (topRank) {
        alert(`랭킹 계산이 완료되었습니다!\n\n🥇 1등: ${topRank.applicant.name} (${topRank.totalScore}점)\n📊 총 ${rankedData.length}명의 지원자에 대해 랭킹이 계산되었습니다.`);
      }

    } catch (error) {
      console.error('❌ 랭킹 계산 오류:', error);
      alert('랭킹 계산 중 오류가 발생했습니다.');
    } finally {
      setIsCalculatingRanking(false);
    }
  }, [searchTerm, filteredApplicants, calculateKeywordMatchingScore, getRankText]);

  // 메모이제이션된 페이지네이션된 지원자 목록 (랭킹 결과와 동일한 순서로 정렬)
  const paginatedApplicants = useMemo(() => {
    console.log('🔍 paginatedApplicants useMemo 실행됨');
    console.log('🔍 paginatedApplicants 입력값:', {
      selectedJobPostingId,
      selectedJobPostingIdType: typeof selectedJobPostingId,
      filteredApplicantsLength: filteredApplicants.length,
      currentPage,
      itemsPerPage,
      applicantsLength: applicants.length,
      hasRankingResults: !!rankingResults
    });

    const startIndex = (currentPage - 1) * itemsPerPage;

    // 채용공고가 선택되고 랭킹 결과가 있는 경우: 랭킹 순서와 동일하게 정렬
    if (selectedJobPostingId && rankingResults && rankingResults.results) {
      console.log('🔍 paginatedApplicants - 랭킹 결과 기반 정렬');

      // 랭킹 결과에서 지원자 ID 순서 추출
      const rankingOrder = rankingResults.results.map(result => result.applicant.id);
      console.log('🔍 랭킹 순서:', rankingOrder);

      // 필터링된 지원자들을 랭킹 순서대로 정렬
      const sortedApplicants = [...filteredApplicants].sort((a, b) => {
        const aRank = rankingOrder.indexOf(a.id);
        const bRank = rankingOrder.indexOf(b.id);

        // 둘 다 랭킹에 있는 경우: 랭킹 순서대로 정렬
        if (aRank !== -1 && bRank !== -1) {
          return aRank - bRank;
        }

        // 하나만 랭킹에 있는 경우: 랭킹에 있는 것이 앞으로
        if (aRank !== -1) return -1;
        if (bRank !== -1) return 1;

        // 둘 다 랭킹에 없는 경우: 최신순 정렬
        const dateA = new Date(a.created_at || a.appliedDate || new Date());
        const dateB = new Date(b.created_at || b.appliedDate || new Date());

        if (isNaN(dateA.getTime())) dateA.setTime(Date.now());
        if (isNaN(dateB.getTime())) dateB.setTime(Date.now());

        return dateB - dateA; // 최신순 (내림차순)
      });

      const result = sortedApplicants.slice(startIndex, startIndex + itemsPerPage);
      console.log('🔍 paginatedApplicants - 최종 결과 (랭킹 기반):', result.length, '명');
      return result;
    } else if (selectedJobPostingId) {
      // 채용공고가 선택되었지만 랭킹 결과가 없는 경우: 점수순 정렬
      console.log('🔍 paginatedApplicants - 점수순 정렬 (랭킹 결과 없음)');

      const jobPostingApplicants = applicants.filter(app => {
        const matches = String(app.job_posting_id) === String(selectedJobPostingId);
        return matches;
      });

      const sortedJobPostingApplicants = jobPostingApplicants
        .map(app => ({
          ...app,
          score: app.analysisScore || 0
        }))
        .sort((a, b) => b.score - a.score);

      // 상위 3명의 ID 목록 생성
      const top3Ids = sortedJobPostingApplicants.slice(0, 3).map(app => app.id);

      // 필터링된 지원자들을 순위 배지 우선으로 정렬
      const sortedApplicants = [...filteredApplicants].sort((a, b) => {
        const aRank = top3Ids.indexOf(a.id);
        const bRank = top3Ids.indexOf(b.id);

        // 둘 다 상위 3명에 있는 경우: 순위대로 정렬 (1등, 2등, 3등)
        if (aRank !== -1 && bRank !== -1) {
          return aRank - bRank;
        }

        // 하나만 상위 3명에 있는 경우: 상위 3명이 앞으로
        if (aRank !== -1) return -1;
        if (bRank !== -1) return 1;

        // 둘 다 상위 3명에 없는 경우: 최신순 정렬
        const dateA = new Date(a.created_at || a.appliedDate || new Date());
        const dateB = new Date(b.created_at || b.appliedDate || new Date());

        if (isNaN(dateA.getTime())) dateA.setTime(Date.now());
        if (isNaN(dateB.getTime())) dateB.setTime(Date.now());

        return dateB - dateA; // 최신순 (내림차순)
      });

      const result = sortedApplicants.slice(startIndex, startIndex + itemsPerPage);
      console.log('🔍 paginatedApplicants - 최종 결과 (점수순):', result.length, '명');
      return result;
    } else {
      // 채용공고가 선택되지 않은 경우: 최신순 정렬
      const sortedApplicants = [...filteredApplicants].sort((a, b) => {
        const dateA = new Date(a.created_at || a.appliedDate || new Date());
        const dateB = new Date(b.created_at || b.appliedDate || new Date());

        if (isNaN(dateA.getTime())) dateA.setTime(Date.now());
        if (isNaN(dateB.getTime())) dateB.setTime(Date.now());

        return dateB - dateA; // 최신순 (내림차순)
      });

      const result = sortedApplicants.slice(startIndex, startIndex + itemsPerPage);
      console.log('🔍 paginatedApplicants - 최종 결과 (최신순):', result.length, '명');
      return result;
    }
  }, [filteredApplicants, currentPage, itemsPerPage, selectedJobPostingId, applicants, rankingResults]);

  // 최적화된 통계 계산 (useMemo 사용)
  const optimizedStats = useMemo(() => {
    if (!applicants || applicants.length === 0) {
      return { total: 0, document_passed: 0, final_passed: 0, waiting: 0, rejected: 0 };
    }

    const stats = applicants.reduce((acc, applicant) => {
      acc.total++;

      switch (applicant.status) {
        case '서류합격':
          acc.document_passed++;
          break;
        case '최종합격':
          acc.final_passed++;
          break;
        case '보류':
          acc.waiting++;
          break;
        case '서류불합격':
          acc.rejected++;
          break;
        default:
          acc.waiting++; // 기본값은 보류로 처리
          break;
      }

      return acc;
    }, { total: 0, document_passed: 0, final_passed: 0, waiting: 0, rejected: 0 });

    return stats;
  }, [applicants]);

  // 초기 데이터 로드
  useEffect(() => {
    // 세션 스토리지 초기화 (새로운 데이터를 위해)
    sessionStorage.removeItem('applicants');
    sessionStorage.removeItem('applicantStats');

    // 랭킹 결과 복원 시도
    try {
      const savedRankingResults = sessionStorage.getItem('rankingResults');
      if (savedRankingResults) {
        const parsedRankingResults = JSON.parse(savedRankingResults);
        setRankingResults(parsedRankingResults);
        console.log('💾 세션 스토리지에서 랭킹 결과 복원됨');
      }
    } catch (error) {
      console.error('랭킹 결과 복원 실패:', error);
    }

    // API에서 새로운 데이터 로드
    loadApplicants();
    loadStats();
  }, []);

  // 최적화된 통계를 stats 상태에 반영
  useEffect(() => {
    if (optimizedStats) {
      setStats(optimizedStats);
    }
  }, [optimizedStats]);

  // 지원자 상태 변경 핸들러
  const handleApplicantStatusChange = useCallback((applicantId, newStatus) => {
    console.log(`🔄 지원자 상태 변경: ${applicantId} -> ${newStatus}`);

    // 로컬 상태 업데이트
    setApplicants(prevApplicants =>
      prevApplicants.map(applicant =>
        applicant.id === applicantId
          ? { ...applicant, status: newStatus }
          : applicant
      )
    );

    // 통계는 useMemo로 자동 재계산됨
  }, []);

  // 지원자 데이터 로드 (페이지네이션 지원)
  const loadApplicants = useCallback(async () => {
    try {
      setIsLoading(true);

      // 모든 지원자 데이터를 한 번에 가져오기 (페이지네이션은 클라이언트에서 처리)
      const apiApplicants = await applicantApi.getAllApplicants(0, 1000); // 최대 1000명까지 가져오기

      if (apiApplicants && apiApplicants.length > 0) {
        console.log(`✅ ${apiApplicants.length}명의 지원자 데이터 로드 완료`);
        console.log('🔍 첫 번째 지원자 데이터 확인:', {
          name: apiApplicants[0]?.name,
          email: apiApplicants[0]?.email,
          phone: apiApplicants[0]?.phone,
          fields: Object.keys(apiApplicants[0] || {})
        });
        setApplicants(apiApplicants);
        setHasMore(false); // 모든 데이터를 가져왔으므로 더 이상 로드할 필요 없음

        // 세션 스토리지에 지원자 데이터 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify(apiApplicants));
        } catch (error) {
          console.error('지원자 데이터 세션 스토리지 저장 실패:', error);
        }
      } else {
        console.log('⚠️ API에서 데이터를 찾을 수 없습니다.');
        setApplicants([]);
        setHasMore(false);

        // 빈 배열도 세션 스토리지에 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify([]));
        } catch (error) {
          console.error('빈 배열 세션 스토리지 저장 실패:', error);
        }
      }
    } catch (error) {
      console.error('❌ API 연결 실패:', error);
      setApplicants([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 통계 데이터 로드
  const loadStats = useCallback(async () => {
    try {
      const apiStats = await applicantApi.getApplicantStats();

      // 백엔드 통계 데이터를 프론트엔드 형식으로 변환
      const convertedStats = {
        total: apiStats.total_applicants || 0,
        document_passed: apiStats.status_distribution?.document_passed || 0,
        final_passed: apiStats.status_distribution?.final_passed || 0,
        waiting: apiStats.status_distribution?.pending || 0,
        rejected: apiStats.status_distribution?.rejected || 0
      };

      setStats(convertedStats);

      // 세션 스토리지에 통계 데이터 저장
      try {
        sessionStorage.setItem('applicantStats', JSON.stringify(convertedStats));
      } catch (error) {
        console.error('통계 데이터 세션 스토리지 저장 실패:', error);
      }
    } catch (error) {
      console.error('통계 데이터 로드 실패:', error);
      // 기본 통계 계산
      updateLocalStats();
    }
  }, []);

  // 로컬 통계 업데이트
  const updateLocalStats = useCallback(() => {
    setStats(optimizedStats);
  }, [optimizedStats]);

  // 지원자 상태 업데이트
  const handleUpdateStatus = useCallback(async (applicantId, newStatus) => {
    try {
      // 현재 지원자의 이전 상태 확인
      const currentApplicant = applicants.find(a => a.id === applicantId || a._id === applicantId);
      const previousStatus = currentApplicant ? currentApplicant.status : '지원';

      console.log(`🔄 상태 변경: ${previousStatus} → ${newStatus}`);

      // API 호출 시도 (실패해도 로컬 상태는 업데이트)
      try {
        await applicantApi.updateApplicantStatus(applicantId, newStatus);
        console.log(`✅ API 호출 성공`);
      } catch (apiError) {
        console.log(`⚠️ API 호출 실패, 로컬 상태만 업데이트:`, apiError.message);
      }

      // 로컬 상태 업데이트 및 통계 즉시 계산
      setApplicants(prev => {
        const updatedApplicants = (prev || []).map(applicant =>
          (applicant.id === applicantId || applicant._id === applicantId)
            ? { ...applicant, status: newStatus }
            : applicant
        );

        console.log(`📊 상태 업데이트:`, {
          이전상태: previousStatus,
          새상태: newStatus,
          지원자ID: applicantId
        });

        // 세션 스토리지에 업데이트된 데이터 저장
        try {
          sessionStorage.setItem('applicants', JSON.stringify(updatedApplicants));
          console.log('💾 세션 스토리지에 지원자 데이터 저장됨');
        } catch (error) {
          console.error('세션 스토리지 저장 실패:', error);
        }

        return updatedApplicants;
      });

      // 랭킹 결과도 업데이트 (별도로 처리하여 동기화 보장)
      setRankingResults(prevRanking => {
        if (prevRanking && prevRanking.results) {
          const updatedResults = prevRanking.results.map(result => {
            if (result.applicant.id === applicantId || result.applicant._id === applicantId) {
              console.log(`🔄 랭킹 결과 상태 업데이트: ${result.applicant.name} -> ${newStatus}`);
              return {
                ...result,
                applicant: {
                  ...result.applicant,
                  status: newStatus
                }
              };
            }
            return result;
          });

          const updatedRanking = { ...prevRanking, results: updatedResults };

          // 랭킹 결과도 세션 스토리지에 저장
          try {
            sessionStorage.setItem('rankingResults', JSON.stringify(updatedRanking));
            console.log('💾 세션 스토리지에 랭킹 결과 저장됨');
          } catch (error) {
            console.error('랭킹 결과 세션 스토리지 저장 실패:', error);
          }

          return updatedRanking;
        }
        return prevRanking;
      });

      // 통계 재계산을 위한 로그 (useMemo가 자동으로 실행됨)
      console.log('📊 통계 재계산 트리거됨');

      console.log(`✅ 지원자 ${applicantId}의 상태가 ${newStatus}로 업데이트되었습니다.`);
    } catch (error) {
      console.error('지원자 상태 업데이트 실패:', error);
    }
  }, [applicants]);



  const handleCardClick = async (applicant) => {
    setSelectedApplicant(applicant);
    setIsModalOpen(true);
    
    // 유사인재 추천 API 호출
    try {
      console.log('🚀 [ApplicantManagement] 유사인재 추천 API 호출 시작', applicant.id);
      const recommendationData = await applicantApi.getTalentRecommendations(applicant.id);
      console.log('✅ [ApplicantManagement] 유사인재 추천 완료:', recommendationData);
    } catch (error) {
      console.error('❌ [ApplicantManagement] 유사인재 추천 오류:', error);
    }
  };

  const handleResumeModalOpen = (applicant) => {
    setSelectedResumeApplicant(applicant);
    setIsResumeModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedApplicant(null);
    // 이력서 모달이 열려있으면 닫지 않음
  };

  const handleResumeModalClose = () => {
    setIsResumeModalOpen(false);
    setSelectedResumeApplicant(null);
  };

  // 자소서 분석 모달 관련 함수들
  const handleCoverLetterAnalysisModalOpen = async (applicant) => {
    setSelectedApplicantForCoverLetter(applicant);
    setIsCoverLetterAnalysisModalOpen(true);

    try {
      // 지원자의 자소서 데이터를 API에서 가져오기
      const applicantId = applicant._id || applicant.id;
      const coverLetterData = await CoverLetterAnalysisApi.getApplicantCoverLetter(applicantId);

      if (coverLetterData && coverLetterData.success) {
        setSelectedCoverLetterData(coverLetterData.data?.cover_letter_analysis || coverLetterData.data?.analysis_result?.cover_letter_analysis);
      } else {
        // API에서 데이터를 가져올 수 없는 경우 기존 데이터 사용
        setSelectedCoverLetterData(applicant.cover_letter_analysis || applicant.analysis_result?.cover_letter_analysis);
      }
    } catch (error) {
      console.error('자소서 데이터 로드 오류:', error);
      // 에러 발생 시 기존 데이터 사용
      setSelectedCoverLetterData(applicant.cover_letter_analysis || applicant.analysis_result?.cover_letter_analysis);
    }
  };

  const handleCoverLetterAnalysisModalClose = () => {
    setIsCoverLetterAnalysisModalOpen(false);
    setSelectedCoverLetterData(null);
    setSelectedApplicantForCoverLetter(null);
  };

  // 자소서 분석 수행 함수
  const handlePerformCoverLetterAnalysis = async (applicantId, analysisRequest = {}) => {
    try {
      const result = await CoverLetterAnalysisApi.analyzeApplicantCoverLetter(applicantId, analysisRequest);
      if (result && result.success) {
        setSelectedCoverLetterData(result.data?.cover_letter_analysis || result.data?.analysis_result?.cover_letter_analysis);
        return result;
      } else {
        throw new Error(result?.message || '자소서 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('자소서 분석 오류:', error);
      throw error;
    }
  };

  const handleDocumentClick = async (type, applicant) => {
    console.log('문서 클릭:', type, applicant);

    // applicant 객체에 _id가 없으면 id를 _id로 설정
    const applicantWithId = {
      ...applicant,
      _id: applicant._id || applicant.id
    };

    // 모달 먼저 열기
    setDocumentModal({ isOpen: true, type, applicant: applicantWithId, isOriginal: false, documentData: null, suspicionData: null, isLoadingSuspicion: type === 'coverLetter' });
    if (type === 'portfolio') {
      setPortfolioView('select');
    }

    // 각 문서 타입별로 해당 컬렉션에서 데이터 가져오기
    try {
      let documentData = null;
      const applicantId = applicantWithId._id;

      switch (type) {
        case 'resume':
          try {
            documentData = await documentApi.getResume(applicantId);
            console.log('✅ 이력서 데이터 로드 완료:', documentData);
          } catch (error) {
            console.error('❌ 이력서 데이터 로드 실패:', error);
          }
          break;

        case 'coverLetter':
          try {
            documentData = await documentApi.getCoverLetter(applicantId);
            console.log('✅ 자소서 데이터 로드 완료:', documentData);

            // 자소서 분석 수행
            try {
              const analysisData = await documentApi.getCoverLetterAnalysis(applicantId);
                documentData.analysis = analysisData.analysis || analysisData;
                console.log('✅ 자소서 분석 완료:', analysisData);
            } catch (analysisError) {
              console.error('❌ 자소서 분석 오류:', analysisError);
            }
          } catch (error) {
            console.error('❌ 자소서 데이터 로드 실패:', error);
          }
          break;

        case 'portfolio':
          try {
            documentData = await documentApi.getPortfolio(applicantId);
            console.log('✅ 포트폴리오 데이터 로드 완료:', documentData);
          } catch (error) {
            console.error('❌ 포트폴리오 데이터 로드 실패:', error);
          }
          break;
      }

      // 문서 데이터를 모달 상태에 저장
      if (documentData) {
        setDocumentModal(prev => ({
          ...prev,
          documentData
        }));
      }

    } catch (error) {
      console.error('❌ 문서 데이터 로드 오류:', error);
    }

    // 자소서 타입일 때만 표절 의심도 검사 자동 실행 (전역 상태에 저장)
    if (type === 'coverLetter') {
      console.log('🚀 [ApplicantManagement] 자소서 모달 열림 - 표절 의심도 검사 시작');
      console.log('- applicantId:', applicantWithId._id);
      console.log('- applicantName:', applicantWithId.name);
      
      setLoadingState(applicantWithId._id, true);
      
      try {
        console.log('🔍 자소서 표절 의심도 검사 시작...');
        console.log('- API 요청 URL:', `http://localhost:8000/api/coverletter/similarity-check/${applicantWithId._id}`);
        
        const suspicionResult = await applicantApi.checkCoverLetterSuspicion(applicantWithId._id);
        console.log('✅ 자소서 표절 의심도 검사 완료:', suspicionResult);
        console.log('- 응답 데이터 구조:', JSON.stringify(suspicionResult, null, 2));
        
        updateSuspicionData(applicantWithId._id, suspicionResult);
        console.log('💾 전역 상태에 표절 의심도 결과 저장 완료');
        
        // 저장된 데이터 검증
        const storedData = getSuspicionData(applicantWithId._id);
        console.log('📋 저장된 데이터 확인:', storedData);
      } catch (error) {
        console.error('❌ 자소서 표절 의심도 검사 실패:', error);
        console.error('- 에러 상세:', error.stack);
        updateSuspicionData(applicantWithId._id, {
          status: 'error',
          message: '표절 의심도 검사 중 오류가 발생했습니다: ' + error.message,
          error: error.message,
          fullError: error.stack
        });
      } finally {
        setLoadingState(applicantWithId._id, false);
        console.log('🏁 표절 의심도 검사 완료 - 로딩 상태 해제');
      }
    }
  };

  const handleOriginalClick = () => {
    setDocumentModal(prev => ({ ...prev, isOriginal: !prev.isOriginal }));
  };

  const handleCloseDocumentModal = () => {
    setDocumentModal({ isOpen: false, type: '', applicant: null, isOriginal: false, documentData: null, suspicionData: null, isLoadingSuspicion: false });
    setPortfolioView('select');
    setPortfolioData(null);
  };

  // 포트폴리오 데이터 가져오기
  const loadPortfolioData = async (applicantId) => {
    try {
      setIsLoadingPortfolio(true);
      console.log('포트폴리오 데이터를 불러오는 중...', applicantId);

      if (!applicantId) {
        console.error('지원자 ID가 없습니다');
        setPortfolioData(null);
        return;
      }

      const portfolio = await applicantApi.getPortfolioByApplicantId(applicantId);
      console.log('포트폴리오 데이터:', portfolio);

      setPortfolioData(portfolio);
    } catch (error) {
      console.error('포트폴리오 데이터 로드 오류:', error);
      setPortfolioData(null);
    } finally {
      setIsLoadingPortfolio(false);
    }
  };

  const handleSimilarApplicantClick = async (similarData) => {
    try {
      // 유사한 지원자의 ID를 사용해서 전체 지원자 정보를 가져옴
      const applicantData = await applicantApi.getApplicantById(similarData.resume_id);

        // 현재 모달의 타입을 기억해둠 (자소서에서 클릭했으면 자소서를, 이력서에서 클릭했으면 이력서를)
        const currentModalType = documentModal.type;

        // 현재 모달을 닫고 새로운 모달을 열기
    setDocumentModal({ isOpen: false, type: '', applicant: null, isOriginal: false, documentData: null, suspicionData: null, isLoadingSuspicion: false });

        // 약간의 딜레이 후에 새로운 모달 열기 (부드러운 전환을 위해)
        setTimeout(() => {
          setDocumentModal({
            isOpen: true,
            type: currentModalType, // 현재 모달의 타입을 유지
            applicant: applicantData,
            isOriginal: true,
            documentData: null,
            suspicionData: null,
            isLoadingSuspicion: false
          });
        }, 100);
    } catch (error) {
      console.error('지원자 정보 요청 중 오류:', error);
    }
  };

  const handleFilterClick = () => {
    setFilterModal(true);
  };

  const handleCloseFilterModal = () => {
    setFilterModal(false);
  };

  const handleJobChange = (job) => {
    setSelectedJobs(prev =>
      prev.includes(job)
        ? prev.filter(j => j !== job)
        : [...prev, job]
    );
  };

  const handleExperienceChange = (experience) => {
    setSelectedExperience(prev =>
      prev.includes(experience)
        ? prev.filter(e => e !== experience)
        : [...prev, experience]
    );
  };

  const handleStatusChange = (status) => {
    setSelectedStatus(prev =>
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  const handleApplyFilter = () => {
    setFilterModal(false);
  };

  const handleResetFilter = () => {
    setSelectedJobs([]);
    setSelectedExperience([]);
    setSelectedStatus([]);
    setFilterStatus('전체');
    setSearchTerm('');
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };

  // 지원자 삭제 핸들러
  const handleDeleteApplicant = async (applicantId) => {
    if (!window.confirm('정말로 이 지원자를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    try {
      await applicantApi.deleteApplicant(applicantId);
        console.log('✅ 지원자 삭제 성공');

        // 모달 닫기
        handleCloseModal();

        // 지원자 목록 새로고침
        setCurrentPage(1);
        loadApplicants();

        // 통계 업데이트
        loadStats();

        alert('지원자가 성공적으로 삭제되었습니다.');
    } catch (error) {
      console.error('❌ 지원자 삭제 오류:', error);
      alert('지원자 삭제 중 오류가 발생했습니다.');
    }
  };

  // 체크박스 관련 핸들러들
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedApplicants([]);
      setSelectAll(false);
    } else {
      setSelectedApplicants((paginatedApplicants || []).map(applicant => applicant.id));
      setSelectAll(true);
    }
  };

  const handleSelectApplicant = (applicantId) => {
    setSelectedApplicants(prev => {
      if (prev.includes(applicantId)) {
        const newSelected = prev.filter(id => id !== applicantId);
        setSelectAll(newSelected.length === paginatedApplicants.length);
        return newSelected;
      } else {
        const newSelected = [...prev, applicantId];
        setSelectAll(newSelected.length === paginatedApplicants.length);
        return newSelected;
      }
    });
  };

  const handleBulkStatusUpdate = async (newStatus) => {
    if (selectedApplicants.length === 0) {
      return;
    }

    try {
      // 선택된 모든 지원자의 상태를 일괄 업데이트
      for (const applicantId of selectedApplicants) {
        await handleUpdateStatus(applicantId, newStatus);
      }

      // 선택 해제
      setSelectedApplicants([]);
      setSelectAll(false);
    } catch (error) {
      console.error('일괄 상태 업데이트 실패:', error);
    }
  };

  // 현재 적용된 필터 상태 확인
  const hasActiveFilters = searchTerm !== '' ||
                          filterStatus !== '전체' ||
                          selectedJobs.length > 0 ||
                          selectedExperience.length > 0;

  // 필터 상태 텍스트 생성
  const getFilterStatusText = () => {
    const filters = [];
    if (searchTerm) filters.push(`검색: "${searchTerm}"`);
    if (filterStatus !== '전체') filters.push(`상태: ${filterStatus}`);
    if ((selectedJobs || []).length > 0) filters.push(`직무: ${(selectedJobs || []).join(', ')}`);
    if ((selectedExperience || []).length > 0) filters.push(`경력: ${(selectedExperience || []).join(', ')}`);
    return filters.join(' | ');
  };

  // 새 이력서 등록 핸들러들
  const handleNewResumeModalOpen = () => {
    setIsResumeModalOpen(true);
  };

  const handleNewResumeModalClose = () => {
    setIsResumeModalOpen(false);
    setResumeFile(null);
    setCoverLetterFile(null);
            setGithubUrl('');
    setIsAnalyzing(false);
    setAnalysisResult(null);
    setIsDragOver(false);
  };

  // 드래그 앤 드롭 이벤트 핸들러들
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      // 파일 타입 검증
      const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

      if (allowedTypes.includes(fileExtension)) {
        // 파일명으로 이력서인지 자기소개서인지 포트폴리오인지 판단
        const fileName = file.name.toLowerCase();
        if (fileName.includes('자기소개서') || fileName.includes('cover') || fileName.includes('coverletter')) {
          setCoverLetterFile(file);
          console.log('드래그 앤 드롭으로 자기소개서 파일이 업로드되었습니다:', file.name);
                  } else {
        setResumeFile(file);
          console.log('드래그 앤 드롭으로 이력서 파일이 업로드되었습니다:', file.name);
        }
      } else {
        alert('지원하지 않는 파일 형식입니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
      }
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResumeFile(file);
      // 파일명에서 기본 정보 추출 시도
      const fileName = file.name.toLowerCase();
      if (fileName.includes('이력서') || fileName.includes('resume')) {
        // 파일명에서 정보 추출 로직
        console.log('이력서 파일이 선택되었습니다:', file.name);
      }

      // 이력서 파일이 선택되면 자동으로 중복 체크 수행
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        setTimeout(() => checkExistingApplicant(), 500); // 0.5초 후 중복 체크
      }

      // 새로운 파일이 선택되면 교체 옵션 초기화
      setReplaceExisting(false);
    }
  };

  const handleCoverFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCoverLetterFile(file);
      // 파일명에서 기본 정보 추출 시도
      const fileName = file.name.toLowerCase();
      if (fileName.includes('자기소개서') || fileName.includes('cover') || fileName.includes('coverletter')) {
        // 파일명에서 정보 추출 로직
        console.log('자기소개서 파일이 선택되었습니다:', file.name);
      }

      // 다른 파일이 선택되면 기존 지원자 정보 초기화
      setExistingApplicant(null);
      // 교체 옵션도 초기화
      setReplaceExisting(false);
    }
  };

  const handleGithubUrlChange = (event) => {
    const url = event.target.value;
    setGithubUrl(url);

    // 깃허브 URL이 변경되면 기존 지원자 정보 초기화
    if (url.trim()) {
      setExistingApplicant(null);
      setReplaceExisting(false);
    }
  };

  const handleResumeDataChange = (field, value) => {
    setResumeData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSkillsChange = (skillsString) => {
    const skillsArray = skillsString.split(',').map(skill => skill.trim()).filter(skill => skill);
    setResumeData(prev => ({
      ...prev,
      skills: skillsArray
    }));
  };

  // 기존 지원자 검색 함수
  const checkExistingApplicant = async (files) => {
    try {
      console.log('🔍 중복 체크 시작...');
      setIsCheckingDuplicate(true);
      setExistingApplicant(null);

      // 파일에서 기본 정보 추출 시도
      let applicantInfo = {};

      if (resumeFile) {
        console.log('📄 이력서 파일로 중복 체크 수행:', resumeFile.name);
        const formData = new FormData();
        formData.append('resume_file', resumeFile);

        console.log('🌐 API 요청 전송: 중복 확인');

        try {
          const result = await ocrApi.checkDuplicate([resumeFile]);
          console.log('📋 API 응답 결과:', result);

          if (result.existing_applicant) {
            console.log('🔄 기존 지원자 발견:', result.existing_applicant);
            setExistingApplicant(result.existing_applicant);
            return result.existing_applicant;
          } else {
            console.log('✅ 새로운 지원자 - 중복 없음');
          }
        } catch (error) {
          console.error('❌ API 요청 실패:', error);
        }
      } else {
        console.log('⚠️ 이력서 파일이 없어서 중복 체크 건너뜀');
      }

      return null;
    } catch (error) {
      console.error('❌ 중복 체크 중 오류:', error);
      return null;
    } finally {
      setIsCheckingDuplicate(false);
    }
  };

  const handleResumeSubmit = async () => {
    try {
      console.log('🚀 통합 문서 업로드 시작');
      console.log('📁 선택된 파일들:', { resumeFile, coverLetterFile, githubUrl });

      // 최소 하나의 입력은 필요
      if (!resumeFile && !coverLetterFile && !githubUrl.trim()) {
        alert('이력서, 자기소개서, 또는 깃허브 주소 중 하나는 입력해주세요.');
        return;
      }

      // 기존 지원자가 이미 발견된 경우 확인
      if (existingApplicant) {
        let message = `기존 지원자 "${existingApplicant.name}"님을 발견했습니다.\n\n`;
        message += `현재 보유 서류:\n`;
        message += `이력서: ${existingApplicant.resume ? '✅ 있음' : '❌ 없음'}\n`;
        message += `자기소개서: ${existingApplicant.cover_letter ? '✅ 있음' : '❌ 없음'}\n`;
        message += `깃허브: ${existingApplicant.github_url ? '✅ 있음' : '❌ 없음'}\n\n`;

        // 업로드하려는 서류와 기존 서류 비교
        const duplicateDocuments = [];
        if (resumeFile && existingApplicant.resume) duplicateDocuments.push('이력서');
        if (coverLetterFile && existingApplicant.cover_letter) duplicateDocuments.push('자기소개서');
        if (githubUrl.trim() && existingApplicant.github_url) duplicateDocuments.push('깃허브');

        if (duplicateDocuments.length > 0) {
          message += `⚠️ 다음 서류는 이미 존재합니다:\n`;
          message += `${duplicateDocuments.join(', ')}\n\n`;
          message += `기존 파일을 새 파일로 교체하시겠습니까?\n`;
          message += `(교체하지 않으면 해당 서류는 업로드되지 않습니다)`;

          const shouldReplace = window.confirm(message);
          if (shouldReplace) {
            setReplaceExisting(true);
            console.log('🔄 교체 모드 활성화:', duplicateDocuments);
          } else {
            console.log('⏭️ 교체 모드 비활성화 - 중복 서류는 업로드되지 않음');
          }
        } else {
          message += `새로운 서류만 추가됩니다.`;
          const shouldContinue = window.confirm(message);
          if (!shouldContinue) {
            return;
          }
        }
      }

      // 파일 내용 미리보기 (디버깅용)
      if (resumeFile) {
        console.log('📄 이력서 파일 정보:', {
          name: resumeFile.name,
          size: resumeFile.size,
          type: resumeFile.type,
          lastModified: new Date(resumeFile.lastModified).toLocaleString()
        });
      }

      if (coverLetterFile) {
        console.log('📝 자기소개서 파일 정보:', {
          name: coverLetterFile.name,
          size: coverLetterFile.size,
          type: coverLetterFile.type,
          lastModified: new Date(coverLetterFile.lastModified).toLocaleString()
        });
      }

      if (githubUrl.trim()) {
        console.log('🔗 깃허브 URL:', githubUrl);
      }

      // 파일 유효성 검사 강화
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
              const maxSize = 50 * 1024 * 1024; // 50MB

      if (resumeFile) {
        if (!allowedTypes.includes(resumeFile.type) && !resumeFile.name.match(/\.(pdf|doc|docx|txt)$/i)) {
          alert('이력서 파일 형식이 지원되지 않습니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
          return;
        }
        if (resumeFile.size > maxSize) {
                      alert('이력서 파일 크기가 50MB를 초과합니다.');
          return;
        }
      }

      if (coverLetterFile) {
        if (!allowedTypes.includes(coverLetterFile.type) && !coverLetterFile.name.match(/\.(pdf|doc|docx|txt)$/i)) {
          alert('자기소개서 파일 형식이 지원되지 않습니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다.');
          return;
        }
        if (coverLetterFile.size > maxSize) {
                      alert('자기소개서 파일 크기가 50MB를 초과합니다.');
          return;
        }
      }

      // 깃허브 URL 유효성 검사
      if (githubUrl.trim()) {
        const githubUrlPattern = /^https?:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-._]+$/;
        if (!githubUrlPattern.test(githubUrl.trim())) {
          alert('올바른 깃허브 저장소 주소를 입력해주세요.\n예: https://github.com/username/repository');
          return;
        }
      }



      // 분석 시작
      setIsAnalyzing(true);
      setAnalysisResult(null);

      // 통합 업로드 API 호출
      console.log('📤 통합 업로드 API 호출 시작');
      console.log('⏱️ 타임아웃 설정: 10분 (600초)');

      const formData = new FormData();

      // 기존 지원자가 있는 경우 ID와 교체 옵션 포함
      if (existingApplicant) {
        formData.append('existing_applicant_id', existingApplicant._id);
        formData.append('replace_existing', replaceExisting.toString());
        console.log('🔄 기존 지원자 ID 포함:', existingApplicant._id);
        console.log('🔄 교체 옵션:', replaceExisting);

        // 교체 옵션에 따른 로그
        if (replaceExisting) {
          console.log('🔄 교체 모드 활성화 - 기존 서류를 새 서류로 교체');
        } else {
          console.log('⏭️ 교체 모드 비활성화 - 중복 서류는 업로드되지 않음');
        }
      }

      if (resumeFile) {
        console.log('📄 이력서 파일 전송:', {
          name: resumeFile.name,
          size: resumeFile.size,
          type: resumeFile.type
        });
        formData.append('resume_file', resumeFile);
      }
      if (coverLetterFile) {
        console.log('📝 자기소개서 파일 전송:', {
          name: coverLetterFile.name,
          size: coverLetterFile.size,
          type: coverLetterFile.type
        });
        formData.append('cover_letter_file', coverLetterFile);
      }
      if (githubUrl.trim()) {
        console.log('🔗 깃허브 URL 전송:', githubUrl);
        formData.append('github_url', githubUrl.trim());
      }

      const files = [];
      if (resumeFile) files.push(resumeFile);
      if (coverLetterFile) files.push(coverLetterFile);

      const result = await ocrApi.uploadMultipleDocuments(files, githubUrl.trim());
      console.log('✅ 통합 업로드 성공:', result);

      // 분석 결과 생성
      const analysisResult = {
        documentType: result.data.uploaded_documents.join(' + '),
        fileName: [resumeFile?.name, coverLetterFile?.name, githubUrl.trim() ? '깃허브 URL' : ''].filter(Boolean).join(', '),
        analysisDate: new Date().toLocaleString(),
        processingTime: 0,
        extractedTextLength: 0,
        analysisResult: result.data.results,
        uploadResults: Object.entries(result.data.results).map(([type, data]) => ({
          type: type === 'resume' ? 'resume' : type === 'cover_letter' ? 'cover_letter' : 'github',
          result: data
        })),
        applicant: result.data.results.resume?.applicant || result.data.results.cover_letter?.applicant || result.data.results.github?.applicant || null
      };

      setAnalysisResult(analysisResult);
      setIsAnalyzing(false);

      // 성공 메시지
      const uploadedDocs = result.data.uploaded_documents;
      const successMessage = uploadedDocs.length > 1
        ? `${uploadedDocs.join(', ')} 문서들이 성공적으로 업로드되었습니다!\n\n지원자: ${analysisResult.applicant?.name || 'N/A'}`
        : `${uploadedDocs[0] === 'resume' ? '이력서' : uploadedDocs[0] === 'cover_letter' ? '자기소개서' : '깃허브'}가 성공적으로 업로드되었습니다!\n\n지원자: ${analysisResult.applicant?.name || 'N/A'}`;

      alert(successMessage);

      // 지원자 목록 새로고침
      loadApplicants();

    } catch (error) {
      console.error('❌ 통합 문서 업로드 실패:', error);

      // 에러 타입별 상세 메시지
      let errorMessage = '문서 업로드에 실패했습니다.';

      if (error.name === 'AbortError') {
        errorMessage = '요청 시간이 초과되었습니다. (10분 제한)\n\n대용량 파일이나 여러 파일을 동시에 업로드할 때 시간이 오래 걸릴 수 있습니다.\n\n해결 방법:\n1. 파일 크기를 줄여보세요 (각 파일 10MB 이하 권장)\n2. 한 번에 하나씩 파일을 업로드해보세요\n3. 다시 시도해보세요';
      } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = '네트워크 연결에 실패했습니다.\n\n서버 상태를 확인해주세요.';
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = '서버에 연결할 수 없습니다.\n\n백엔드 서버가 실행 중인지 확인해주세요.';
      } else {
        errorMessage = `문서 업로드에 실패했습니다:\n${error.message}`;
      }

      console.error('🔍 에러 상세 정보:', {
        name: error.name,
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });

      alert(errorMessage);
      setIsAnalyzing(false);
    }
  };

  // 분석 데이터 추출 함수들은 analysisHelpers.js에서 import



  // 기존 문서 미리보기 함수
  const handlePreviewDocument = async (documentType) => {
    if (!existingApplicant) return;

    try {
      let documentId;
      let documentData;

      switch (documentType) {
        case 'resume':
          if (existingApplicant.resume) {
            documentId = existingApplicant.resume;
            // 이력서 데이터 가져오기
            try {
              documentData = await documentApi.getResume(existingApplicant._id);
            } catch (error) {
              console.error('이력서 데이터 가져오기 실패:', error);
            }
          }
          break;
        case 'cover_letter':
          if (existingApplicant.cover_letter) {
            documentId = existingApplicant.cover_letter;
            // 자기소개서 데이터 가져오기
            try {
              documentData = await documentApi.getCoverLetter(existingApplicant._id);
            } catch (error) {
              console.error('자기소개서 데이터 가져오기 실패:', error);
            }
          }
          break;
        case 'portfolio':
          if (existingApplicant.portfolio) {
            documentId = existingApplicant.portfolio;
            // 포트폴리오 데이터 가져오기
            try {
              documentData = await documentApi.getPortfolio(existingApplicant._id);
            } catch (error) {
              console.error('포트폴리오 데이터 가져오기 실패:', error);
            }
          }
          break;
        default:
          return;
      }

      if (documentData) {
        setPreviewDocument({
          type: documentType,
          data: documentData,
          applicantName: existingApplicant.name
        });
        setIsPreviewModalOpen(true);
      }
    } catch (error) {
      console.error('문서 미리보기 중 오류:', error);
      alert('문서를 불러올 수 없습니다.');
    }
  };

  // 문서 미리보기 모달 닫기
  const closePreviewModal = () => {
    setIsPreviewModalOpen(false);
    setPreviewDocument(null);
  };

  // 페이지네이션 함수들 (useCallback으로 최적화)
  const totalPages = useMemo(() => Math.ceil(filteredApplicants.length / itemsPerPage), [filteredApplicants.length, itemsPerPage]);

  // 디버깅 로그 (필요시에만 출력)
  // if (process.env.NODE_ENV === 'development') {
  //   console.log('🔍 페이지네이션 디버깅:', {
  //     totalApplicants: applicants?.length || 0,
  //     filteredApplicants: filteredApplicants?.length || 0,
  //     itemsPerPage,
  //     totalPages,
  //     currentPage
  //   });
  // }

  const handlePageChange = useCallback((pageNumber) => {
    setCurrentPage(pageNumber);
  }, []);

  const goToPreviousPage = useCallback(() => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  }, [currentPage, handlePageChange]);

  const goToNextPage = useCallback(() => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  }, [currentPage, totalPages, handlePageChange]);

  const goToFirstPage = useCallback(() => {
    handlePageChange(1);
  }, [handlePageChange]);

  const goToLastPage = useCallback(() => {
    handlePageChange(totalPages);
  }, [totalPages, handlePageChange]);

  return (
    <Container>
      <HeaderSection onNewResumeClick={handleNewResumeModalOpen} />

        {/* 로딩 상태 표시 */}
        {isLoading && (
          <LoadingOverlay>
            <LoadingSpinner>
              <div className="spinner"></div>
              <span>데이터를 불러오는 중...</span>
            </LoadingSpinner>
          </LoadingOverlay>
        )}

      <StatsSection stats={stats} onSendMail={handleSendMail} />

      <SearchFilterSection
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        selectedJobPostingId={selectedJobPostingId}
        handleJobPostingChange={handleJobPostingChange}
        jobPostings={jobPostings}
        visibleJobPostingsCount={visibleJobPostingsCount}
        setVisibleJobPostingsCount={setVisibleJobPostingsCount}
        hasActiveFilters={hasActiveFilters}
        getFilterStatusText={getFilterStatusText}
        handleFilterClick={handleFilterClick}
        viewMode={viewMode}
        handleViewModeChange={handleViewModeChange}
        isCalculatingRanking={isCalculatingRanking}
        calculateKeywordRanking={calculateKeywordRanking}
        calculateJobPostingRanking={calculateJobPostingRanking}
      />

      <RankingSection
        selectedJobPostingId={selectedJobPostingId}
        rankingResults={rankingResults}
        setRankingResults={setRankingResults}
        handleCardClick={handleCardClick}
        handleUpdateStatus={handleUpdateStatus}
      />

      {/* 게시판 보기 헤더 */}
      {viewMode === 'board' && (
        <>
          {/* 고정된 액션 바 */}
          <FixedActionBar>
            <SelectionInfo>
              <FiCheck size={14} />
              {selectedApplicants.length}개 선택됨
            </SelectionInfo>
            <ActionButtonsGroup>
              <FixedPassButton
                onClick={() => handleBulkStatusUpdate('서류합격')}
                disabled={selectedApplicants.length === 0}
              >
                <FiCheck size={12} />
                서류합격
              </FixedPassButton>
              <FixedPassButton
                onClick={() => handleBulkStatusUpdate('최종합격')}
                disabled={selectedApplicants.length === 0}
                style={{ backgroundColor: '#9c27b0' }}
              >
                <FiTrendingUp size={12} />
                최종합격
              </FixedPassButton>
              <FixedPendingButton
                onClick={() => handleBulkStatusUpdate('보류')}
                disabled={selectedApplicants.length === 0}
              >
                <FiClock size={12} />
                보류
              </FixedPendingButton>
              <FixedRejectButton
                onClick={() => handleBulkStatusUpdate('서류불합격')}
                disabled={selectedApplicants.length === 0}
              >
                <FiX size={12} />
                불합격
              </FixedRejectButton>
            </ActionButtonsGroup>
          </FixedActionBar>

          <HeaderRowBoard>
            <HeaderCheckbox>
              <CheckboxInput
                type="checkbox"
                checked={selectAll}
                onChange={handleSelectAll}
              />
            </HeaderCheckbox>
            <HeaderName>이름</HeaderName>
            <HeaderPosition>직무</HeaderPosition>
            <HeaderEmail>이메일</HeaderEmail>
            <HeaderPhone>전화번호</HeaderPhone>
            <HeaderSkills>기술스택</HeaderSkills>
            <HeaderDate>지원일</HeaderDate>
            <HeaderScore>총점</HeaderScore>
            <HeaderActions>상태</HeaderActions>
          </HeaderRowBoard>
        </>
      )}

      {viewMode === 'grid' ? (
        <Wrapper>
          <ApplicantsGrid viewMode={viewMode}>
            {(() => {
              console.log('🔍 렌더링 시작 - paginatedApplicants:', {
                length: paginatedApplicants.length,
                selectedJobPostingId,
                viewMode,
                currentPage,
                itemsPerPage
              });

              if (paginatedApplicants.length > 0) {
                console.log('🔍 렌더링할 지원자들:', paginatedApplicants.slice(0, 3).map(app => ({
                  id: app.id,
                  name: app.name,
                  job_posting_id: app.job_posting_id
                })));
              }

              return paginatedApplicants.length > 0 ? (
                paginatedApplicants.map((applicant, index) => {
                  // filteredApplicants에서 해당 지원자의 순위 가져오기
                  const filteredApplicant = filteredApplicants.find(app => app.id === applicant.id || app._id === applicant.id);
                  const rank = filteredApplicant?.rank || null;

                  return (
                    <MemoizedApplicantCard
                      key={applicant.id}
                      applicant={applicant}
                      onCardClick={handleCardClick}
                      onStatusUpdate={handleUpdateStatus}
                      getStatusText={getStatusText}
                      rank={rank}
                      selectedJobPostingId={selectedJobPostingId}
                      onStatusChange={handleApplicantStatusChange}
                    />
                  );
                })
            ) : (
              <EmptyState>
                <FiSearch size={48} />
                <h3>검색 결과가 없습니다</h3>
                                  <p>다른 검색어나 필터 조건을 시도해보세요.</p>
                </EmptyState>
            );
          })()}
          </ApplicantsGrid>

          {/* 페이지네이션 */}
          {totalPages > 0 && (
            <PaginationContainer>
              <PaginationButton
                onClick={goToFirstPage}
                disabled={currentPage === 1}
              >
                &lt;&lt;
              </PaginationButton>

              <PaginationButton
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
              >
                &lt;
              </PaginationButton>

              <PageNumbers>
                {(() => {
                  const pages = [];
                  const maxVisiblePages = 5;

                  // 현재 페이지를 중심으로 5개 페이지 계산
                  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
                  let endPage = startPage + maxVisiblePages - 1;

                  // 끝에 도달했을 때 조정
                  if (endPage > totalPages) {
                    endPage = totalPages;
                    startPage = Math.max(1, endPage - maxVisiblePages + 1);
                  }

                  // 페이지 번호들 생성
                  for (let i = startPage; i <= endPage; i++) {
                    pages.push(
                      <PageNumber
                        key={i}
                        onClick={() => handlePageChange(i)}
                        isActive={i === currentPage}
                      >
                        {i}
                      </PageNumber>
                    );
                  }

                  return pages;
                })()}
              </PageNumbers>

              <PaginationButton
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
              >
                &gt;
              </PaginationButton>

              <PaginationButton
                onClick={goToLastPage}
                disabled={currentPage === totalPages}
              >
                &gt;&gt;
              </PaginationButton>
            </PaginationContainer>
          )}
        </Wrapper>
      ) : (
        <Wrapper>
          <ApplicantsBoard>
            {paginatedApplicants.length > 0 ? (
              paginatedApplicants.map((applicant, index) => {
                // filteredApplicants에서 해당 지원자의 순위 가져오기
                const filteredApplicant = filteredApplicants.find(app => app.id === applicant.id || app._id === applicant.id);
                const rank = filteredApplicant?.rank || null;

                return (
                <BoardApplicantCard
                  key={applicant.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, duration: 0.1 }}
                  onClick={() => handleCardClick(applicant)}
                  onMouseEnter={() => setHoveredApplicant(applicant.id)}
                  onMouseLeave={() => setHoveredApplicant(null)}
                >
                  <ApplicantHeader>
                    <ApplicantCheckbox onClick={(e) => e.stopPropagation()}>
                      <CheckboxInput
                        type="checkbox"
                        checked={selectedApplicants.includes(applicant.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleSelectApplicant(applicant.id);
                        }}
                      />
                    </ApplicantCheckbox>
                    <ApplicantName>
                      {rank && rank <= 3 && selectedJobPostingId && (
                        <BoardRankBadge rank={rank} />
                      )}
                      {applicant.name}
                    </ApplicantName>
                    <ApplicantPosition>{applicant.position}</ApplicantPosition>
                    <ApplicantEmail>
                      <ContactItem>
                        <FiMail size={10} />
                        {applicant.email}
                      </ContactItem>
                    </ApplicantEmail>
                    <ApplicantPhone>
                      <ContactItem>
                        <FiPhone size={10} />
                        {applicant.phone}
                      </ContactItem>
                    </ApplicantPhone>
                    <ApplicantSkills>
                      {applicant.skills ? (
                        <>
                          {Array.isArray(applicant.skills)
                            ? applicant.skills.slice(0, 2).map((skill, skillIndex) => (
                                <SkillTag key={skillIndex}>
                                  {skill}
                                </SkillTag>
                              ))
                            : applicant.skills.split(',').slice(0, 2).map((skill, skillIndex) => (
                                <SkillTag key={skillIndex}>
                                  {skill.trim()}
                                </SkillTag>
                              ))
                          }
                          {Array.isArray(applicant.skills)
                            ? applicant.skills.length > 2 && (
                              <SkillTag>+{applicant.skills.length - 2}</SkillTag>
                            )
                            : applicant.skills.split(',').length > 2 && (
                              <SkillTag>+{applicant.skills.split(',').length - 2}</SkillTag>
                            )
                          }
                        </>
                      ) : (
                        <SkillTag>기술스택 없음</SkillTag>
                      )}
                    </ApplicantSkills>
                    <ApplicantDate>
                      {applicant.appliedDate || applicant.created_at
                        ? new Date(applicant.appliedDate || applicant.created_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                          }).replace(/\. /g, '.').replace(' ', '')
                        : '날짜 없음'
                      }
                    </ApplicantDate>
                    <ApplicantScoreBoard>
                      <ScoreBadge score={applicant.ranks?.total || 0}>
                        {applicant.ranks?.total || 0}점
                      </ScoreBadge>
                    </ApplicantScoreBoard>
                    <StatusColumnWrapper>
                      <StatusBadge
                        status={applicant.status}
                        small
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.08, ease: "easeOut" }}
                      >
                        {getStatusText(applicant.status)}
                      </StatusBadge>
                    </StatusColumnWrapper>
                  </ApplicantHeader>
                </BoardApplicantCard>
              );
            })          ) : (
              <EmptyState>
                <FiSearch size={48} />
                <h3>검색 결과가 없습니다</h3>
                <p>다른 검색어나 필터 조건을 시도해보세요.</p>
              </EmptyState>
            )}
          </ApplicantsBoard>

          {/* 페이지네이션 (보드 뷰) */}
          {totalPages > 0 && (
            <PaginationContainer>
              <PaginationButton
                onClick={goToFirstPage}
                disabled={currentPage === 1}
              >
                &lt;&lt;
              </PaginationButton>

              <PaginationButton
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
              >
                &lt;
              </PaginationButton>

              <PageNumbers>
                {(() => {
                  const pages = [];
                  const maxVisiblePages = 5;

                  // 현재 페이지를 중심으로 5개 페이지 계산
                  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
                  let endPage = startPage + maxVisiblePages - 1;

                  // 끝에 도달했을 때 조정
                  if (endPage > totalPages) {
                    endPage = totalPages;
                    startPage = Math.max(1, endPage - maxVisiblePages + 1);
                  }

                  // 페이지 번호들 생성
                  for (let i = startPage; i <= endPage; i++) {
                    pages.push(
                      <PageNumber
                        key={i}
                        onClick={() => handlePageChange(i)}
                        isActive={i === currentPage}
                      >
                        {i}
                      </PageNumber>
                    );
                  }

                  return pages;
                })()}
              </PageNumbers>

              <PaginationButton
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
              >
                &gt;
              </PaginationButton>

              <PaginationButton
                onClick={goToLastPage}
                disabled={currentPage === totalPages}
              >
                &gt;&gt;
              </PaginationButton>
            </PaginationContainer>
          )}
        </Wrapper>
      )}





      {/* 지원자 상세 모달 */}
      <AnimatePresence>
        {isModalOpen && selectedApplicant && (
          <ModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCloseModal}
          >
            <ModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalHeader>
                <ModalTitle>지원자 상세 정보</ModalTitle>
                <CloseButton onClick={handleCloseModal}>&times;</CloseButton>
              </ModalHeader>

              <ProfileSection>
                <SectionTitle>
                  <FiUser size={20} />
                  기본 정보
                </SectionTitle>
                <ProfileGrid>
                  <ProfileItem>
                    <ProfileLabel>이름</ProfileLabel>
                    <ProfileValue>{selectedApplicant.name}</ProfileValue>
                  </ProfileItem>
                  <ProfileItem>
                    <ProfileLabel>경력</ProfileLabel>
                    <ProfileValue>{selectedApplicant.experience}</ProfileValue>
                  </ProfileItem>
                  <ProfileItem>
                    <ProfileLabel>희망직책</ProfileLabel>
                    <ProfileValue>{selectedApplicant.position}</ProfileValue>
                  </ProfileItem>
                </ProfileGrid>
              </ProfileSection>

              <SkillsSection>
                <SkillsTitle>
                  <FiCode size={20} />
                  기술스택
                </SkillsTitle>
                <SkillsGrid>
                  {Array.isArray(selectedApplicant.skills)
                    ? selectedApplicant.skills.map((skill, index) => (
                        <SkillTag key={index}>
                          {skill}
                        </SkillTag>
                      ))
                    : typeof selectedApplicant.skills === 'string'
                    ? selectedApplicant.skills.split(',').map((skill, index) => (
                        <SkillTag key={index}>
                          {skill.trim()}
                        </SkillTag>
                      ))
                    : null
                  }
                </SkillsGrid>
              </SkillsSection>

              <SummarySection>
                <SummaryTitle>
                  <FiFile size={20} />
                  AI 분석 요약
                </SummaryTitle>

                {selectedApplicant.analysisScore && (
                  <AnalysisScoreDisplay>
                    <AnalysisScoreCircle>
                      {selectedApplicant.analysisScore}
                    </AnalysisScoreCircle>
                    <AnalysisScoreInfo>
                      <AnalysisScoreLabel>AI 분석 점수</AnalysisScoreLabel>
                      <AnalysisScoreValue>{selectedApplicant.analysisScore}점</AnalysisScoreValue>
                    </AnalysisScoreInfo>
                  </AnalysisScoreDisplay>
                )}

                <SummaryText>
                  {selectedApplicant.summary}
                </SummaryText>
              </SummarySection>

              <DocumentButtons>
                <ResumeButton onClick={() => handleResumeModalOpen(selectedApplicant)}>
                  <FiFileText size={16} />
                  이력서
                </ResumeButton>
                <DocumentButton onClick={() => handleDocumentClick('coverLetter', selectedApplicant)}>
                  <FiMessageSquare size={16} />
                  자소서
                </DocumentButton>
                <DocumentButton
                  onClick={() => handleCoverLetterAnalysisModalOpen(selectedApplicant)}
                  style={{ backgroundColor: '#667eea' }}
                >
                  <FiBarChart2 size={16} />
                  자소서 분석
                </DocumentButton>
                <DocumentButton
                  onClick={() => setShowDetailedAnalysis(true)}
                  style={{ backgroundColor: '#764ba2' }}
                >
                  <FiStar size={16} />
                  통합 분석
                </DocumentButton>
                <DocumentButton onClick={() => handleDocumentClick('portfolio', selectedApplicant)}>
                  <FiCode size={16} />
                  포트폴리오
                </DocumentButton>
              </DocumentButtons>

              <DeleteButton onClick={() => handleDeleteApplicant(selectedApplicant.id)}>
                <FiX size={16} />
                지원자 삭제
              </DeleteButton>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>

      {/* 문서 모달 */}
      <AnimatePresence>
        {documentModal.isOpen && documentModal.applicant && (
          <DocumentModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleCloseDocumentModal}
          >
            <DocumentModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <DocumentModalHeader>
                <DocumentModalTitle>
                  {documentModal.type === 'resume' && '이력서'}
                  {documentModal.type === 'coverLetter' && '자소서'}
                  {documentModal.type === 'portfolio' && '포트폴리오'}
                  - {documentModal.applicant.name}
                </DocumentModalTitle>
                <DocumentHeaderActions>
                  <DocumentOriginalButton onClick={handleOriginalClick}>
                    {documentModal.isOriginal ? '요약보기' : '원본보기'}
                  </DocumentOriginalButton>
                  <DocumentCloseButton onClick={handleCloseDocumentModal}>&times;</DocumentCloseButton>
                </DocumentHeaderActions>
              </DocumentModalHeader>

              <DocumentContent>
                {/* 포트폴리오: 선택 화면 */}
                {documentModal.type === 'portfolio' && portfolioView === 'select' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>포트폴리오 요약 방법 선택</DocumentSectionTitle>
                      <SelectionGrid>
                        <SelectionCard
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setPortfolioView('github')}
                        >
                          <SelectionIcon className="github">
                            <FiGitBranch />
                          </SelectionIcon>
                          <SelectionTitle>깃헙 요약</SelectionTitle>
                          <SelectionDesc>GitHub URL/아이디로 레포 분석 요약 보기</SelectionDesc>
                        </SelectionCard>
                        <SelectionCard
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            console.log('포트폴리오 버튼 클릭:', documentModal.applicant);
                            if (documentModal.applicant && documentModal.applicant._id) {
                              setPortfolioView('portfolio');
                              loadPortfolioData(documentModal.applicant._id);
                            } else {
                              console.error('지원자 ID가 없습니다:', documentModal.applicant);
                              alert('지원자 정보를 찾을 수 없습니다.');
                            }
                          }}
                        >
                          <SelectionIcon className="portfolio">
                            <FiCode />
                          </SelectionIcon>
                          <SelectionTitle>포트폴리오 요약</SelectionTitle>
                          <SelectionDesc>등록된 포트폴리오 정보 기반 요약 보기</SelectionDesc>
                        </SelectionCard>
                      </SelectionGrid>
                    </DocumentSection>
                  </>
                )}

                {/* 포트폴리오: 깃헙 요약 화면 */}
                {documentModal.type === 'portfolio' && portfolioView === 'github' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>
                        <button
                          onClick={() => setPortfolioView('select')}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            marginRight: 8,
                            color: 'var(--text-secondary)'
                          }}
                          aria-label="뒤로"
                        >
                          <FiArrowLeft />
                        </button>
                        깃헙 요약
                      </DocumentSectionTitle>
                      <GithubSummaryPanel />
                    </DocumentSection>
                  </>
                )}

                {/* 포트폴리오: 기존 포트폴리오 상세 */}
                {documentModal.type === 'portfolio' && portfolioView === 'portfolio' && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>
                        <button
                          onClick={() => setPortfolioView('select')}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            marginRight: 8,
                            color: 'var(--text-secondary)'
                          }}
                          aria-label="뒤로"
                        >
                          <FiArrowLeft />
                        </button>
                        포트폴리오
                      </DocumentSectionTitle>
                      {isLoadingPortfolio ? (
                        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                          <div>포트폴리오 데이터를 불러오는 중...</div>
                        </div>
                      ) : (
                        <PortfolioSummaryPanel portfolio={portfolioData} />
                      )}
                    </DocumentSection>
                  </>
                )}

                {/* 이력서 기존 로직 */}
                {documentModal.type === 'resume' && documentModal.isOriginal && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원자 기본정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>이름</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.name || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원 직무</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.position || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>부서</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.department || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.experience || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>기술스택</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.skills || '정보 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>상태</DocumentCardTitle>
                          <DocumentCardText>{getStatusText(documentModal.applicant.status)}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>평가 정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>성장배경</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.growthBackground || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원동기</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.motivation || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력사항</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.careerHistory || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>종합 점수</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.analysisScore || 0}점</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>분석 결과</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.analysisResult || '분석 결과 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원일시</DocumentCardTitle>
                          <DocumentCardText>{documentModal.applicant.created_at ? new Date(documentModal.applicant.created_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                          }).replace(/\. /g, '.').replace(' ', '') : 'N/A'}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>
                  </>
                )}

                {/* 자소서: cover_letters 컬렉션에서 정보 가져오기 */}
                {documentModal.type === 'coverLetter' && documentModal.isOriginal && documentModal.documentData && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>지원자 기본정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>이름</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.name || documentModal.applicant.name || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원 직무</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.position || documentModal.applicant.position || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>부서</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.department || documentModal.applicant.department || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.experience || documentModal.applicant.experience || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>기술스택</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.keywords?.join(', ') || documentModal.applicant.skills || '정보 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>상태</DocumentCardTitle>
                          <DocumentCardText>{getStatusText(documentModal.applicant.status)}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>평가 정보</DocumentSectionTitle>
                      <DocumentGrid>
                        <DocumentCard>
                          <DocumentCardTitle>성장배경</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.growthBackground || documentModal.applicant.growthBackground || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원동기</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.motivation || documentModal.applicant.motivation || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>경력사항</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.careerHistory || documentModal.applicant.careerHistory || 'N/A'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>종합 점수</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.analysisScore || documentModal.applicant.analysisScore || 0}점</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>분석 결과</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.basic_info?.analysisResult || documentModal.applicant.analysisResult || '분석 결과 없음'}</DocumentCardText>
                        </DocumentCard>
                        <DocumentCard>
                          <DocumentCardTitle>지원일시</DocumentCardTitle>
                          <DocumentCardText>{documentModal.documentData.created_at ? new Date(documentModal.documentData.created_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                          }).replace(/\. /g, '.').replace(' ', '') : (documentModal.applicant.created_at ? new Date(documentModal.applicant.created_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                          }).replace(/\. /g, '.').replace(' ', '') : 'N/A')}</DocumentCardText>
                        </DocumentCard>
                      </DocumentGrid>
                    </DocumentSection>

                    {/* 자소서 원본 내용 */}
                    {documentModal.documentData?.extracted_text && (
                      <DocumentSection>
                        <DocumentSectionTitle>자소서 내용</DocumentSectionTitle>
                        <DocumentCard>
                          <DocumentCardText style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                            {documentModal.documentData.extracted_text}
                          </DocumentCardText>
                        </DocumentCard>
                      </DocumentSection>
                    )}
                  </>
                )}

                {documentModal.type === 'resume' && !documentModal.isOriginal && documentModal.documentData && (
                    <DocumentSection>
                    <DocumentSectionTitle>이력서 내용</DocumentSectionTitle>
                    <DocumentCard>
                      <DocumentCardText>
                        {documentModal.documentData.extracted_text || '이력서 내용을 불러올 수 없습니다.'}
                      </DocumentCardText>
                    </DocumentCard>
                    </DocumentSection>
                )}



                {documentModal.type === 'portfolio' && documentModal.applicant.documents?.portfolio && (
                  <>
                    <DocumentSection>
                      <DocumentSectionTitle>프로젝트</DocumentSectionTitle>
                      {(documentModal.applicant.documents.portfolio.projects || []).map((project, index) => (
                        <DocumentCard key={index}>
                          <DocumentCardTitle>{project.title}</DocumentCardTitle>
                          <DocumentCardText>{project.description}</DocumentCardText>
                          <DocumentCardText><strong>기술스택:</strong> {(project.technologies || []).join(', ')}</DocumentCardText>
                          <DocumentCardText><strong>주요 기능:</strong></DocumentCardText>
                          <DocumentList>
                            {(project.features || []).map((feature, idx) => (
                              <DocumentListItem key={idx}>{feature}</DocumentListItem>
                            ))}
                          </DocumentList>
                          <DocumentCardText><strong>GitHub:</strong> <a href={project.github} target="_blank" rel="noopener noreferrer">{project.github}</a></DocumentCardText>
                          <DocumentCardText><strong>Demo:</strong> <a href={project.demo} target="_blank" rel="noopener noreferrer">{project.demo}</a></DocumentCardText>
                        </DocumentCard>
                      ))}
                    </DocumentSection>

                    <DocumentSection>
                      <DocumentSectionTitle>성과 및 수상</DocumentSectionTitle>
                      <DocumentList>
                        {(documentModal.applicant.documents.portfolio.achievements || []).map((achievement, index) => (
                          <DocumentListItem key={index}>{achievement}</DocumentListItem>
                        ))}
                      </DocumentList>
                    </DocumentSection>
                  </>
                )}

                {documentModal.type === 'coverLetter' && !documentModal.isOriginal && (
                  <>
                    {/* 자소서 원본 내용 섹션 */}
                    {documentModal.documentData?.extracted_text && (
                      <DocumentSection>
                        <DocumentSectionTitle>자소서 내용</DocumentSectionTitle>
                        <DocumentCard>
                          <DocumentCardText style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                            {documentModal.documentData.extracted_text}
                          </DocumentCardText>
                        </DocumentCard>
                      </DocumentSection>
                    )}

                    {/* 자소서 분석 결과 섹션 */}
                    <DocumentSection>
                      <DocumentSectionTitle>자소서 분석 결과</DocumentSectionTitle>
                      <CoverLetterAnalysis
                        analysisData={documentModal.documentData?.analysis || {
                          technical_suitability: { score: 75, feedback: '기술적합성에 대한 분석이 필요합니다.' },
                          job_understanding: { score: 80, feedback: '직무이해도에 대한 분석이 필요합니다.' },
                          growth_potential: { score: 85, feedback: '성장가능성에 대한 분석이 필요합니다.' },
                          teamwork_communication: { score: 70, feedback: '팀워크 및 커뮤니케이션에 대한 분석이 필요합니다.' },
                          motivation_company_fit: { score: 90, feedback: '지원동기/회사 가치관 부합도에 대한 분석이 필요합니다.' }
                        }}
                      />
                    </DocumentSection>

                    {/* 표절 의심도 검사는 백그라운드에서 실행됨 - CoverLetterValidation.js에서 결과 확인 */}
                  </>
                )}
              </DocumentContent>
            </DocumentModalContent>
          </DocumentModalOverlay>
        )}
      </AnimatePresence>

      {/* 필터 모달 */}
      <FilterModal
        isOpen={filterModal}
        onClose={handleCloseFilterModal}
        selectedJobs={selectedJobs}
        selectedExperience={selectedExperience}
        selectedStatus={selectedStatus}
        onJobChange={handleJobChange}
        onExperienceChange={handleExperienceChange}
        onStatusChange={handleStatusChange}
        onApplyFilter={handleApplyFilter}
        onResetFilter={handleResetFilter}
      />

      <ResumeUploadModal
        isOpen={isResumeModalOpen}
        onClose={handleResumeModalClose}
        resumeFile={resumeFile}
        coverLetterFile={coverLetterFile}
        githubUrl={githubUrl}
                      isDragOver={isDragOver}
        existingApplicant={existingApplicant}
        replaceExisting={replaceExisting}
        isAnalyzing={isAnalyzing}
        isCheckingDuplicate={isCheckingDuplicate}
        analysisResult={analysisResult}
        onFileChange={handleFileChange}
        onCoverFileChange={handleCoverFileChange}
        onGithubUrlChange={handleGithubUrlChange}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
        onReplaceExistingChange={(checked) => setReplaceExisting(checked)}
        onSubmit={handleResumeSubmit}
        onPreviewDocument={handlePreviewDocument}
      />

      {/* 상세 분석 모달 */}
      <DetailedAnalysisModal
        isOpen={showDetailedAnalysis}
        onClose={() => setShowDetailedAnalysis(false)}
        analysisData={{
          ...selectedApplicant,
          analysis_result: analysisResult,
          analysisScore: selectedApplicant?.analysisScore
        }}
        applicantName={selectedApplicant?.name || '지원자'}
      />

      {/* 새로운 이력서 모달 */}
      <ResumeModal
        isOpen={isResumeModalOpen}
        onClose={handleResumeModalClose}
        applicant={selectedResumeApplicant}
        onViewSummary={() => {
          handleResumeModalClose();
          // 요약보기 로직 추가
        }}
      />

      {/* 자소서 분석 모달 */}
      <CoverLetterAnalysisModal
        isOpen={isCoverLetterAnalysisModalOpen}
        onClose={handleCoverLetterAnalysisModalClose}
        analysisData={selectedCoverLetterData}
        applicantName={selectedApplicantForCoverLetter?.name || '지원자'}
        onPerformAnalysis={handlePerformCoverLetterAnalysis}
        applicantId={selectedApplicantForCoverLetter?._id || selectedApplicantForCoverLetter?.id}
      />

      {/* 문서 미리보기 모달 */}
      <AnimatePresence>
        {isPreviewModalOpen && previewDocument && (
          <DocumentPreviewModal
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <DocumentPreviewContent>
              <DocumentPreviewHeader>
                <DocumentPreviewTitle>
                  📄 {previewDocument.applicantName}님의 {
                    previewDocument.type === 'resume' ? '이력서' :
                    previewDocument.type === 'cover_letter' ? '자기소개서' :
                    '포트폴리오'
                  } 미리보기
                </DocumentPreviewTitle>
                <CloseButton onClick={closePreviewModal}>
                  <FiX size={20} />
                </CloseButton>
              </DocumentPreviewHeader>

              <div style={{ flex: 1, overflow: 'hidden' }}>
                {previewDocument.type === 'resume' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>📋 이력서 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '이력서 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}

                {previewDocument.type === 'cover_letter' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>📝 자기소개서 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '자기소개서 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}

                {previewDocument.type === 'portfolio' && (
                  <div>
                    <h4 style={{ padding: '20px 24px 0', margin: 0 }}>💼 포트폴리오 내용</h4>
                    <DocumentText>
                      {previewDocument.data.extracted_text || '포트폴리오 내용을 불러올 수 없습니다.'}
                    </DocumentText>
                  </div>
                )}
              </div>

              <DocumentPreviewFooter>
                <PreviewCloseButton onClick={closePreviewModal}>
                  닫기
                </PreviewCloseButton>
              </DocumentPreviewFooter>
            </DocumentPreviewContent>
          </DocumentPreviewModal>
        )}
      </AnimatePresence>
    </Container>
  );
};



// ApplicantInfoContainer, InfoField, InfoLabel, InfoInput, ResumeFormActions, ResumeSubmitButton, DeleteButton는 import됨

// DocumentPreviewModal, DocumentPreviewContent, DocumentPreviewHeader, DocumentPreviewTitle, DocumentPreviewFooter, PreviewCloseButton, DocumentText, PreviewButton는 import됨

// PaginationContainer, PaginationButton, PageNumbers, PageNumber, GithubInputContainer, GithubInput, GithubInputDescription는 import됨

// ApplicantRow, NameText, EmailText, PositionBadge, DepartmentText, ContactInfo, SkillsContainer, MoreSkills, NoSkills, AvgScore, ActionButtonGroup, CornerBadge, BoardAvatar는 import됨

// BoardContainer, BoardApplicantCard, BoardCardHeader, CardCheckbox, CardAvatar, BoardCardContent, CardName, CardPosition, CardDepartment, CardContact, CardSkills, CardScore, CardDate, BoardCardActions, CardActionButton는 import됨

export default ApplicantManagement;
