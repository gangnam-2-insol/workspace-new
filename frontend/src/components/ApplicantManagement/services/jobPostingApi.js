const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default {
  getJobPostings: async () => {
    const res = await fetch(`${API_BASE_URL}/api/job-postings`);
    if (!res.ok) throw new Error('채용공고 불러오기 실패');
    return await res.json();
  }
};

