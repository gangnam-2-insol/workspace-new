/* 기본 API 모듈 */
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default {
  /* 전체 지원자(페이지네이션 포함) */
  getAllApplicants: async (skip = 0, limit = 50) => {
    const res = await fetch(`${API_BASE_URL}/api/applicants?skip=${skip}&limit=${limit}`);
    if (!res.ok) throw new Error('지원자 조회 실패');
    const data = await res.json();
    return data.applicants || [];
  },

  /* 상태 업데이트 */
  updateApplicantStatus: async (applicantId, newStatus) => {
    const res = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (!res.ok) throw new Error('업데이트 실패');
    return await res.json();
  },

  /* 전역 통계 */
  getStats: async () => {
    const res = await fetch(`${API_BASE_URL}/api/applicants/stats/overview`);
    if (!res.ok) throw new Error('통계 불러오기 실패');
    return await res.json();
  },

  /* 포트폴리오 데이터 */
  getPortfolioByApplicant: async (applicantId) => {
    const res = await fetch(`${API_BASE_URL}/api/portfolios/applicant/${applicantId}`);
    if (!res.ok) throw new Error('포트폴리오 불러오기 실패');
    return await res.json();
  }
};

