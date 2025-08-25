import { getStatusText } from './analysisHelpers';

// 검색 필터링 함수
export const matchesSearch = (applicant, searchTerm) => {
  if (!searchTerm) return true;

  const searchLower = searchTerm.toLowerCase();
  const skillsText = Array.isArray(applicant.skills)
    ? applicant.skills.join(', ')
    : applicant.skills || '';

  return (applicant.name || '').toLowerCase().includes(searchLower) ||
         (applicant.position || '').toLowerCase().includes(searchLower) ||
         (applicant.email || '').toLowerCase().includes(searchLower) ||
         skillsText.toLowerCase().includes(searchLower);
};

// 상태 필터링 함수
export const matchesStatus = (applicant, filterStatus, selectedStatus) => {
  // 기본 상태 필터링
  const matchesBasicStatus = filterStatus === '전체' ||
                           getStatusText(applicant.status) === filterStatus ||
                           applicant.status === filterStatus;

  // 선택된 상태 필터링
  const matchesSelectedStatus = selectedStatus.length === 0 ||
                               selectedStatus.includes(applicant.status);

  return matchesBasicStatus && matchesSelectedStatus;
};

// 직무 필터링 함수
export const matchesJob = (applicant, selectedJobs) => {
  if (selectedJobs.length === 0) return true;
  return selectedJobs.some(job => applicant.position.includes(job));
};

// 경력 필터링 함수
export const matchesExperience = (applicant, selectedExperience) => {
  if (selectedExperience.length === 0) return true;

  return selectedExperience.some(exp => {
    const experience = applicant.experience || '';

    switch (exp) {
      case '신입':
        return experience.includes('신입') || experience.includes('0년');
      case '1-3년':
        return experience.includes('1년') || experience.includes('2년') || experience.includes('3년');
      case '3-5년':
        return experience.includes('4년') || experience.includes('5년');
      case '5년이상':
        return experience.includes('6년') || experience.includes('7년') ||
               experience.includes('8년') || experience.includes('9년') || experience.includes('10년');
      default:
        return false;
    }
  });
};

// 채용공고 필터링 함수
export const matchesJobPosting = (applicant, selectedJobPostingId) => {
  if (!selectedJobPostingId) return true;

  const applicantJobId = applicant.job_posting_id;
  const selectedJobId = selectedJobPostingId;

  const matches = String(applicantJobId) === String(selectedJobId);

  // 기존과 동일한 로깅 추가
  if (selectedJobPostingId) {
    console.log('🔍 filteredApplicants 필터링:', {
      name: applicant.name,
      applicantJobId,
      applicantJobIdType: typeof applicantJobId,
      selectedJobId,
      selectedJobIdType: typeof selectedJobId,
      matches
    });
  }

  return matches;
};

// 점수 계산 함수
export const calculateApplicantScore = (applicant) => {
  // 프로젝트 마에스트로 점수 (analysisScore) - 100점 만점
  if (applicant.analysisScore !== undefined && applicant.analysisScore !== null) {
    return applicant.analysisScore;
  }

  // 기본 점수 (분석 데이터가 없는 경우)
  return 50;
};

// 지원자 필터링 및 점수 계산 메인 함수
export const filterAndScoreApplicants = (applicants, filters) => {
  const {
    searchTerm,
    filterStatus,
    selectedJobs,
    selectedExperience,
    selectedStatus,
    selectedJobPostingId
  } = filters;

  // 필터링
  const filtered = (applicants || []).filter(applicant => {
    return matchesSearch(applicant, searchTerm) &&
           matchesStatus(applicant, filterStatus, selectedStatus) &&
           matchesJob(applicant, selectedJobs) &&
           matchesExperience(applicant, selectedExperience) &&
           matchesJobPosting(applicant, selectedJobPostingId);
  });

  // 점수 계산 및 순위 매기기
  const applicantsWithScores = filtered.map(applicant => ({
    ...applicant,
    calculatedScore: calculateApplicantScore(applicant)
  }));

  // 필터링 결과 로그 (기존과 동일)
  if (selectedJobPostingId) {
    console.log(`📊 채용공고 ${selectedJobPostingId} 필터링 결과:`, {
      전체지원자: applicants.length,
      필터링된지원자: filtered.length,
      필터링된지원자목록: filtered.map(app => ({ name: app.name, job_posting_id: app.job_posting_id }))
    });
  } else {
    console.log('📊 전체 지원자 필터링 결과:', {
      전체지원자: applicants.length,
      필터링된지원자: filtered.length
    });
  }

  // 점수별로 정렬 (내림차순)
  const sortedApplicants = applicantsWithScores.sort((a, b) => b.calculatedScore - a.calculatedScore);

  // 순위 추가
  return sortedApplicants.map((applicant, index) => ({
    ...applicant,
    rank: index + 1
  }));
};

// 페이지네이션 함수
export const paginateApplicants = (applicants, currentPage, itemsPerPage) => {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return applicants.slice(startIndex, endIndex);
};

// 정렬 함수들
export const sortApplicants = (applicants, sortBy, sortOrder = 'desc') => {
  const sorted = [...applicants];

  switch (sortBy) {
    case 'name':
      sorted.sort((a, b) => {
        const nameA = (a.name || '').toLowerCase();
        const nameB = (b.name || '').toLowerCase();
        return sortOrder === 'asc' ? nameA.localeCompare(nameB) : nameB.localeCompare(nameA);
      });
      break;

    case 'date':
      sorted.sort((a, b) => {
        const dateA = new Date(a.created_at || a.updated_at || 0);
        const dateB = new Date(b.created_at || b.updated_at || 0);
        return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
      });
      break;

    case 'score':
      sorted.sort((a, b) => {
        const scoreA = a.calculatedScore || 0;
        const scoreB = b.calculatedScore || 0;
        return sortOrder === 'asc' ? scoreA - scoreB : scoreB - scoreA;
      });
      break;

    case 'rank':
      sorted.sort((a, b) => {
        const rankA = a.rank || 0;
        const rankB = b.rank || 0;
        return sortOrder === 'asc' ? rankA - rankB : rankB - rankA;
      });
      break;

    default:
      break;
  }

  return sorted;
};
