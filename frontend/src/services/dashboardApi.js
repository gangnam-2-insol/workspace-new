const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// 대시보드용 API 서비스
const dashboardApi = {
  // 지원자 통계 조회
  getApplicantStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/stats/overview`);
      if (!response.ok) {
        throw new Error('지원자 통계 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 통계 조회 오류:', error);
      // 기본값 반환
      return {
        total_applicants: 0,
        status_distribution: {
          pending: 0,
          passed: 0,
          rejected: 0,
          reviewing: 0,
          interview_scheduled: 0
        },
        recent_applicants: 0,
        success_rate: 0
      };
    }
  },

  // 지원자 목록 조회 (최근 활동용)
  getRecentApplicants: async (limit = 10) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants?skip=0&limit=${limit}`);
      if (!response.ok) {
        throw new Error('최근 지원자 조회 실패');
      }
      const data = await response.json();
      return data.applicants || [];
    } catch (error) {
      console.error('최근 지원자 조회 오류:', error);
      return [];
    }
  },

  // 채용공고 통계 조회
  getJobPostingStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/job-postings/stats/overview`);
      if (!response.ok) {
        throw new Error('채용공고 통계 조회 실패');
      }
      const data = await response.json();
      return {
        total_job_postings: data.total_jobs || 0,
        active_job_postings: data.published_jobs || 0,
        total_applications: data.total_applicants || 0
      };
    } catch (error) {
      console.error('채용공고 통계 조회 오류:', error);
      return {
        total_job_postings: 0,
        active_job_postings: 0,
        total_applications: 0
      };
    }
  },

  // 월별 지원자 추이 데이터 생성
  generateMonthlyTrendData: (applicants) => {
    const months = ['1월', '2월', '3월', '4월', '5월', '6월'];
    const currentMonth = new Date().getMonth();

    return months.map((month, index) => {
      const monthIndex = (currentMonth - 5 + index + 12) % 12;
      const baseCount = 100 + (index * 30);
      const randomVariation = Math.floor(Math.random() * 50) - 25;

      return {
        name: month,
        지원자: Math.max(0, baseCount + randomVariation),
        합격: Math.max(0, Math.floor((baseCount + randomVariation) * 0.15))
      };
    });
  },

  // 상태별 분포 데이터 생성
  generateStatusDistributionData: (stats) => {
    const { status_distribution } = stats;

    if (!status_distribution) {
      return [
        { name: '서류 접수', value: 0, color: '#00c851' },
        { name: '면접 진행', value: 0, color: '#007bff' },
        { name: '최종 합격', value: 0, color: '#ff6b35' },
        { name: '불합격', value: 0, color: '#6c757d' }
      ];
    }

    return [
      {
        name: '서류 검토중',
        value: status_distribution.pending || 0,
        color: '#00c851'
      },
      {
        name: '면접 예정',
        value: status_distribution.interview_scheduled || 0,
        color: '#007bff'
      },
      {
        name: '합격',
        value: status_distribution.passed || 0,
        color: '#ff6b35'
      },
      {
        name: '불합격',
        value: status_distribution.rejected || 0,
        color: '#6c757d'
      },
      {
        name: '검토중',
        value: status_distribution.reviewing || 0,
        color: '#9c27b0'
      }
    ];
  },

  // 최근 활동 데이터 생성
  generateRecentActivities: (applicants) => {
    const activities = [];

    if (applicants.length > 0) {
      // 최근 지원자 등록 활동
      const recentApplicant = applicants[0];
      activities.push({
        title: `새로운 지원자 "${recentApplicant.name}"님이 등록되었습니다`,
        time: '5분 전',
        icon: 'FiUsers',
        color: '#00c851'
      });
    }

    // 기본 활동들 추가
    activities.push(
      {
        title: 'AI 면접 분석이 완료되었습니다',
        time: '15분 전',
        icon: 'FiVideo',
        color: '#007bff'
      },
      {
        title: '포트폴리오 분석 결과가 업데이트되었습니다',
        time: '1시간 전',
        icon: 'FiStar',
        color: '#ff6b35'
      },
      {
        title: '자소서 검증이 완료되었습니다',
        time: '2시간 전',
        icon: 'FiFileText',
        color: '#28a745'
      }
    );

    return activities;
  }
};

export default dashboardApi;
