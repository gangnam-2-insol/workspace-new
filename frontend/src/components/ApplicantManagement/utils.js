/* 날짜 포맷 */
export const formatDate = (dateStr) =>
  dateStr
    ? new Date(dateStr).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    : '날짜 없음';

/* 상태 텍스트 변환 */
export const statusMap = {
  pending: '보류',
  approved: '최종합격',
  rejected: '서류불합격',
  reviewed: '서류합격',
  reviewing: '보류',
  passed: '서류합격',
  interview_scheduled: '최종합격',
  서류합격: '서류합격',
  최종합격: '최종합격',
  서류불합격: '서류불합격',
  보류: '보류'
};
export const getStatusText = (s) => statusMap[s] ?? '보류';

/* 필터링 헬퍼(간단)
   실제 프로젝트에서는 더 정교하게 구현
*/
export const filterApplicants = (applicants, { search, jobs, experience, status, job }) => {
  return applicants.filter((app) => {
    if (search) {
      const term = search.toLowerCase();
      const fields = [app.name, app.position, app.email, ...(app.skills || [])].map(v => String(v).toLowerCase());
      if (!fields.some(v => v.includes(term))) return false;
    }
    if (jobs.length && !jobs.some(j => app.position.includes(j))) return false;
    if (experience.length && !experience.includes(app.experience)) return false;
    if (status.length && !status.includes(app.status)) return false;
    if (job && app.job_posting_id !== job) return false;
    return true;
  });
};

