const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class JobPostingAPI {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/job-postings`;
  }

  // 채용공고 목록 조회
  async getJobPostings(params = {}) {
    try {
      const queryParams = new URLSearchParams();

      if (params.skip !== undefined) queryParams.append('skip', params.skip);
      if (params.limit !== undefined) queryParams.append('limit', params.limit);
      if (params.status) queryParams.append('status', params.status);
      if (params.company) queryParams.append('company', params.company);

      const url = `${this.baseURL}?${queryParams.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 목록 조회 실패:', error);
      throw error;
    }
  }

  // 채용공고 상세 조회
  async getJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 조회 실패:', error);
      throw error;
    }
  }

  // 채용공고 생성
  async createJobPosting(jobData) {
    try {
      const response = await fetch(this.baseURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 생성 실패:', error);
      throw error;
    }
  }

  // 채용공고 수정
  async updateJobPosting(jobId, updateData) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 수정 실패:', error);
      throw error;
    }
  }

  // 채용공고 삭제
  async deleteJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 삭제 실패:', error);
      throw error;
    }
  }

  // 채용공고 발행
  async publishJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}/publish`, {
        method: 'PATCH',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 발행 실패:', error);
      throw error;
    }
  }

  // 채용공고 마감
  async closeJobPosting(jobId) {
    try {
      const response = await fetch(`${this.baseURL}/${jobId}/close`, {
        method: 'PATCH',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 마감 실패:', error);
      throw error;
    }
  }

  // 채용공고 통계 조회
  async getJobPostingStats() {
    try {
      const response = await fetch(`${this.baseURL}/stats/overview`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('채용공고 통계 조회 실패:', error);
      throw error;
    }
  }

  // 에러 처리 헬퍼
  handleError(error) {
    if (error.response) {
      // 서버 응답이 있는 경우
      return {
        message: error.response.data?.detail || '서버 오류가 발생했습니다.',
        status: error.response.status
      };
    } else if (error.request) {
      // 요청은 보냈지만 응답이 없는 경우
      return {
        message: '서버에 연결할 수 없습니다.',
        status: 0
      };
    } else {
      // 요청 자체에 문제가 있는 경우
      return {
        message: error.message || '알 수 없는 오류가 발생했습니다.',
        status: 0
      };
    }
  }
}

export default new JobPostingAPI();
