// 로컬 스토리지 기반 데이터 관리 (MongoDB 대신)
class InterviewDatabase {
  constructor() {
    this.storageKey = 'interview_management_data';
    this.initialized = false;
  }

  // 초기화
  async connect() {
    try {
      // 로컬 스토리지에서 데이터 로드
      const existingData = localStorage.getItem(this.storageKey);
      if (!existingData) {
        // 초기 데이터 설정
        const initialData = [
          {
            id: 1,
            name: '김철수',
            position: '프론트엔드 개발자',
            email: 'kim***@gmail.com',
            phone: '010-****-1234',
            interviewDate: '2024-01-20',
            interviewTime: '14:00',
            duration: '60분',
            status: 'scheduled',
            type: '대면',
            platform: '회사 면접실',
            aiScore: 85,
            documents: {
              resume: {
                exists: true,
                summary: 'React, TypeScript, Next.js 경험 풍부. 3년간 프론트엔드 개발 경력.',
                keywords: ['React', 'TypeScript', 'Next.js', 'Redux', 'Tailwind CSS'],
                content: '상세 이력서 내용...'
              },
              portfolio: {
                exists: true,
                summary: 'GitHub에 15개 이상의 프로젝트 포트폴리오 보유.',
                keywords: ['GitHub', 'PWA', '반응형', 'UI/UX'],
                content: '포트폴리오 상세 내용...'
              },
              coverLetter: {
                exists: false,
                summary: '',
                keywords: [],
                content: ''
              }
            },
            questions: [],
            evaluation: {
              technicalScore: 85,
              communicationScore: 88,
              cultureScore: 82,
              overallScore: 85,
              memo: '기술적 이해도가 높고, 커뮤니케이션 능력도 우수합니다.',
              result: 'pending'
            },
            feedback: {
              sent: false,
              content: '',
              channel: 'email',
              sentAt: null
            }
          }
        ];
        localStorage.setItem(this.storageKey, JSON.stringify(initialData));
      }
      
      this.initialized = true;
      console.log('로컬 스토리지 데이터베이스 연결 성공');
      return true;
    } catch (error) {
      console.error('로컬 스토리지 연결 실패:', error);
      return false;
    }
  }

  // 연결 해제
  async disconnect() {
    this.initialized = false;
    console.log('로컬 스토리지 연결 해제');
  }

  // 모든 지원자 조회
  async getAllApplicants() {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('지원자 조회 실패:', error);
      return [];
    }
  }

  // 지원자 추가
  async addApplicant(applicant) {
    try {
      const applicants = await this.getAllApplicants();
      const newId = Math.max(...applicants.map(a => a.id), 0) + 1;
      const newApplicant = { ...applicant, id: newId };
      
      applicants.push(newApplicant);
      localStorage.setItem(this.storageKey, JSON.stringify(applicants));
      
      return newId;
    } catch (error) {
      console.error('지원자 추가 실패:', error);
      return null;
    }
  }

  // 지원자 업데이트
  async updateApplicant(id, updates) {
    try {
      const applicants = await this.getAllApplicants();
      const index = applicants.findIndex(a => a.id === id);
      
      if (index !== -1) {
        applicants[index] = { ...applicants[index], ...updates };
        localStorage.setItem(this.storageKey, JSON.stringify(applicants));
        return true;
      }
      return false;
    } catch (error) {
      console.error('지원자 업데이트 실패:', error);
      return false;
    }
  }

  // 지원자 삭제
  async deleteApplicant(id) {
    try {
      const applicants = await this.getAllApplicants();
      const filteredApplicants = applicants.filter(a => a.id !== id);
      
      if (filteredApplicants.length !== applicants.length) {
        localStorage.setItem(this.storageKey, JSON.stringify(filteredApplicants));
        return true;
      }
      return false;
    } catch (error) {
      console.error('지원자 삭제 실패:', error);
      return false;
    }
  }

  // 날짜별 면접 조회
  async getInterviewsByDate(date) {
    try {
      const applicants = await this.getAllApplicants();
      return applicants.filter(applicant => applicant.interviewDate === date);
    } catch (error) {
      console.error('날짜별 면접 조회 실패:', error);
      return [];
    }
  }

  // 면접 상태별 조회
  async getApplicantsByStatus(status) {
    try {
      const applicants = await this.getAllApplicants();
      return applicants.filter(applicant => applicant.status === status);
    } catch (error) {
      console.error('상태별 지원자 조회 실패:', error);
      return [];
    }
  }

  // 검색 기능
  async searchApplicants(query) {
    try {
      const applicants = await this.getAllApplicants();
      const lowerQuery = query.toLowerCase();
      
      return applicants.filter(applicant => 
        applicant.name.toLowerCase().includes(lowerQuery) ||
        applicant.position.toLowerCase().includes(lowerQuery) ||
        applicant.email.toLowerCase().includes(lowerQuery)
      );
    } catch (error) {
      console.error('검색 실패:', error);
      return [];
    }
  }

  // 통계 조회
  async getStatistics() {
    try {
      const applicants = await this.getAllApplicants();
      
      const stats = {
        scheduled: 0,
        inProgress: 0,
        completed: 0,
        cancelled: 0,
        totalScore: 0,
        totalCount: applicants.length
      };

      applicants.forEach(applicant => {
        const status = applicant.status;
        const score = applicant.aiScore || 0;
        
        if (stats.hasOwnProperty(status)) {
          stats[status]++;
        }
        stats.totalScore += score;
      });

      stats.averageScore = stats.totalCount > 0 
        ? Math.round(stats.totalScore / stats.totalCount) 
        : 0;

      return stats;
    } catch (error) {
      console.error('통계 조회 실패:', error);
      return {
        scheduled: 0,
        inProgress: 0,
        completed: 0,
        cancelled: 0,
        totalScore: 0,
        totalCount: 0,
        averageScore: 0
      };
    }
  }
}

export default InterviewDatabase; 