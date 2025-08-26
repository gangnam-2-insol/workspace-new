// 면접 관리 API (로컬 스토리지 기반)
import InterviewDatabase from '../database/mongodb.js';

class InterviewAPI {
  constructor() {
    this.db = new InterviewDatabase();
    this.initialized = false;
  }

  // 초기화
  async initialize() {
    if (!this.initialized) {
      const success = await this.db.connect();
      this.initialized = success;
      return success;
    }
    return true;
  }

  // 모든 지원자 조회
  async getAllApplicants() {
    await this.initialize();
    return await this.db.getAllApplicants();
  }

  // 지원자 추가
  async addApplicant(applicantData) {
    await this.initialize();
    
    // 데이터 검증
    if (!this.validateApplicantData(applicantData)) {
      throw new Error('지원자 데이터가 유효하지 않습니다.');
    }

    // 중복 검사
    const applicants = await this.db.getAllApplicants();
    const existingApplicant = applicants.find(a => 
      a.email === applicantData.email && 
      a.interviewDate === applicantData.interviewDate
    );

    if (existingApplicant) {
      throw new Error('같은 날짜에 같은 이메일의 지원자가 이미 존재합니다.');
    }

    // 시간 충돌 검사
    const timeConflict = await this.checkTimeConflict(
      applicantData.interviewDate,
      applicantData.interviewTime,
      applicantData.duration
    );

    if (timeConflict) {
      throw new Error('해당 시간에 다른 면접이 이미 예정되어 있습니다.');
    }

    return await this.db.addApplicant(applicantData);
  }

  // 지원자 업데이트
  async updateApplicant(id, updates) {
    await this.initialize();
    
    // 업데이트할 수 있는 필드 검증
    const allowedFields = [
      'name', 'position', 'email', 'phone', 'interviewDate', 
      'interviewTime', 'duration', 'status', 'type', 'platform',
      'aiScore', 'documents', 'questions', 'evaluation', 'feedback'
    ];

    const validUpdates = {};
    for (const field of allowedFields) {
      if (updates.hasOwnProperty(field)) {
        validUpdates[field] = updates[field];
      }
    }

    return await this.db.updateApplicant(id, validUpdates);
  }

  // 지원자 삭제
  async deleteApplicant(id) {
    await this.initialize();
    return await this.db.deleteApplicant(id);
  }

  // 날짜별 면접 조회
  async getInterviewsByDate(date) {
    await this.initialize();
    return await this.db.getInterviewsByDate(date);
  }

  // 상태별 지원자 조회
  async getApplicantsByStatus(status) {
    await this.initialize();
    return await this.db.getApplicantsByStatus(status);
  }

  // 검색 기능
  async searchApplicants(query) {
    await this.initialize();
    return await this.db.searchApplicants(query);
  }

  // 통계 조회
  async getStatistics() {
    await this.initialize();
    return await this.db.getStatistics();
  }

  // 데이터 검증
  validateApplicantData(data) {
    const requiredFields = ['name', 'position', 'email', 'phone', 'interviewDate', 'interviewTime'];
    
    for (const field of requiredFields) {
      if (!data[field] || data[field].trim() === '') {
        return false;
      }
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      return false;
    }

    // 전화번호 형식 검증
    const phoneRegex = /^[0-9-]+$/;
    if (!phoneRegex.test(data.phone)) {
      return false;
    }

    // 날짜 형식 검증
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(data.interviewDate)) {
      return false;
    }

    // 시간 형식 검증
    const timeRegex = /^\d{2}:\d{2}$/;
    if (!timeRegex.test(data.interviewTime)) {
      return false;
    }

    return true;
  }

  // 시간 충돌 검사
  async checkTimeConflict(date, time, duration) {
    const interviews = await this.getInterviewsByDate(date);
    
    const newStart = this.parseTime(time);
    const newEnd = newStart + this.parseDuration(duration);
    
    for (const interview of interviews) {
      const existingStart = this.parseTime(interview.interviewTime);
      const existingEnd = existingStart + this.parseDuration(interview.duration);
      
      // 시간 겹침 검사
      if (newStart < existingEnd && newEnd > existingStart) {
        return true;
      }
    }
    
    return false;
  }

  // 시간을 분으로 변환
  parseTime(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
  }

  // 소요시간을 분으로 변환
  parseDuration(duration) {
    const match = duration.match(/(\d+)분/);
    return match ? parseInt(match[1]) : 60;
  }

  // 배치 작업
  async batchOperation(operation, data) {
    await this.initialize();
    
    const results = [];
    for (const item of data) {
      try {
        let result;
        switch (operation) {
          case 'add':
            result = await this.addApplicant(item);
            break;
          case 'update':
            result = await this.updateApplicant(item.id, item.updates);
            break;
          case 'delete':
            result = await this.deleteApplicant(item.id);
            break;
          default:
            throw new Error('지원하지 않는 작업입니다.');
        }
        results.push({ success: true, data: result });
      } catch (error) {
        results.push({ success: false, error: error.message });
      }
    }
    
    return results;
  }

  // 데이터 백업
  async backupData() {
    await this.initialize();
    const allData = await this.getAllApplicants();
    return {
      timestamp: new Date().toISOString(),
      count: allData.length,
      data: allData
    };
  }

  // 데이터 복원
  async restoreData(backupData) {
    await this.initialize();
    
    // 기존 데이터 삭제 (로컬 스토리지 클리어)
    localStorage.removeItem(this.db.storageKey);
    
    // 백업 데이터 복원
    if (backupData.data && Array.isArray(backupData.data)) {
      const results = await this.batchOperation('add', backupData.data);
      return {
        success: true,
        restoredCount: results.filter(r => r.success).length,
        totalCount: backupData.data.length
      };
    }
    
    return { success: false, error: '유효하지 않은 백업 데이터입니다.' };
  }

  // 연결 해제
  async cleanup() {
    if (this.initialized) {
      await this.db.disconnect();
      this.initialized = false;
    }
  }
}

export default InterviewAPI; 