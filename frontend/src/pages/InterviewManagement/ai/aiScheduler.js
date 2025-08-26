// AI 기반 면접 시간 자동 스케줄링 (로컬 스토리지 기반)
import InterviewDatabase from '../database/mongodb.js';

class AIScheduler {
  constructor() {
    this.db = new InterviewDatabase();
    this.availableTimeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
      '16:00', '16:30', '17:00', '17:30'
    ];
    this.interviewDuration = 60; // 기본 60분
  }

  // 초기화
  async initialize() {
    return await this.db.connect();
  }

  // AI 스케줄링 로직 (외부 API 대신 규칙 기반)
  async callAI(prompt) {
    try {
      // 실제 AI API 대신 규칙 기반 로직 사용
      return this.getDefaultSchedulingLogic(prompt);
    } catch (error) {
      console.error('AI 스케줄링 오류:', error);
      return this.getDefaultSchedulingLogic(prompt);
    }
  }

  // 기본 스케줄링 로직
  getDefaultSchedulingLogic(prompt) {
    const keywords = prompt.toLowerCase();
    
    if (keywords.includes('긴급') || keywords.includes('urgent')) {
      return '가장 빠른 시간대 추천';
    } else if (keywords.includes('고급') || keywords.includes('senior') || keywords.includes('시니어')) {
      return '오전 시간대 추천 (집중도 높음)';
    } else if (keywords.includes('신입') || keywords.includes('junior') || keywords.includes('초급')) {
      return '오후 시간대 추천 (편안한 분위기)';
    } else if (keywords.includes('디자인') || keywords.includes('ui') || keywords.includes('ux')) {
      return '창의적인 작업이 가능한 시간대 추천';
    } else if (keywords.includes('데이터') || keywords.includes('분석') || keywords.includes('ai') || keywords.includes('ml')) {
      return '논리적 사고가 필요한 오전 시간대 추천';
    } else {
      return '일반적인 시간대 추천';
    }
  }

  // 면접 시간 자동 스케줄링
  async autoScheduleInterview(applicantData) {
    try {
      const { name, position, priority, preferredDate } = applicantData;
      
      // AI 스케줄링 요청
      const prompt = `
        지원자: ${name}
        직무: ${position}
        우선순위: ${priority || '보통'}
        선호 날짜: ${preferredDate}
        
        이 지원자에게 적합한 면접 시간을 추천해주세요.
        고려사항:
        - 직무의 특성
        - 지원자의 경력 수준
        - 기존 면접 일정과의 충돌 방지
        - 면접관의 가용 시간
      `;

      const aiRecommendation = await this.callAI(prompt);
      
      // 추천된 시간을 실제 사용 가능한 시간으로 변환
      const scheduledTime = await this.convertAIToTimeSlot(aiRecommendation, preferredDate);
      
      return {
        success: true,
        scheduledTime,
        aiRecommendation,
        reason: this.getSchedulingReason(aiRecommendation, position)
      };
    } catch (error) {
      console.error('자동 스케줄링 실패:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // AI 추천을 실제 시간대로 변환
  async convertAIToTimeSlot(aiRecommendation, preferredDate) {
    const recommendation = aiRecommendation.toLowerCase();
    
    // 시간대별 분류
    if (recommendation.includes('오전') || recommendation.includes('morning')) {
      return await this.findAvailableTimeSlot(preferredDate, 'morning');
    } else if (recommendation.includes('오후') || recommendation.includes('afternoon')) {
      return await this.findAvailableTimeSlot(preferredDate, 'afternoon');
    } else if (recommendation.includes('빠른') || recommendation.includes('urgent')) {
      return await this.findAvailableTimeSlot(preferredDate, 'earliest');
    } else {
      return await this.findAvailableTimeSlot(preferredDate, 'any');
    }
  }

  // 사용 가능한 시간대 찾기
  async findAvailableTimeSlot(date, timePreference) {
    try {
      // 해당 날짜의 기존 면접 조회
      const existingInterviews = await this.db.getInterviewsByDate(date);
      const bookedTimes = existingInterviews.map(interview => interview.interviewTime);
      
      let availableSlots = this.availableTimeSlots.filter(slot => 
        !bookedTimes.includes(slot)
      );

      // 시간대별 필터링
      switch (timePreference) {
        case 'morning':
          availableSlots = availableSlots.filter(slot => 
            slot < '12:00'
          );
          break;
        case 'afternoon':
          availableSlots = availableSlots.filter(slot => 
            slot >= '13:00'
          );
          break;
        case 'earliest':
          // 가장 빠른 시간
          break;
        default:
          // 모든 시간대
          break;
      }

      return availableSlots.length > 0 ? availableSlots[0] : null;
    } catch (error) {
      console.error('사용 가능한 시간대 찾기 실패:', error);
      return null;
    }
  }

  // 스케줄링 이유 생성
  getSchedulingReason(aiRecommendation, position) {
    const positionType = this.categorizePosition(position);
    
    switch (positionType) {
      case 'senior':
        return '고급 개발자이므로 오전 시간대를 추천합니다 (집중도 높음)';
      case 'junior':
        return '신입 개발자이므로 오후 시간대를 추천합니다 (편안한 분위기)';
      case 'design':
        return '디자이너이므로 창의적인 작업이 가능한 시간대를 추천합니다';
      case 'data':
        return '데이터 분석가이므로 논리적 사고가 필요한 오전 시간대를 추천합니다';
      default:
        return '일반적인 면접 시간대를 추천합니다';
    }
  }

  // 직무 분류
  categorizePosition(position) {
    const pos = position.toLowerCase();
    
    if (pos.includes('senior') || pos.includes('고급') || pos.includes('시니어')) {
      return 'senior';
    } else if (pos.includes('junior') || pos.includes('신입') || pos.includes('초급')) {
      return 'junior';
    } else if (pos.includes('design') || pos.includes('디자인') || pos.includes('ui') || pos.includes('ux')) {
      return 'design';
    } else if (pos.includes('data') || pos.includes('분석') || pos.includes('ai') || pos.includes('ml')) {
      return 'data';
    } else {
      return 'general';
    }
  }

  // 배치 스케줄링 (여러 지원자 동시 처리)
  async batchSchedule(applicants) {
    const results = [];
    
    for (const applicant of applicants) {
      const result = await this.autoScheduleInterview(applicant);
      results.push({
        applicant: applicant.name,
        ...result
      });
    }
    
    return results;
  }

  // 스케줄 최적화
  async optimizeSchedule(date) {
    try {
      const interviews = await this.db.getInterviewsByDate(date);
      
      // 면접 간격 최적화
      const optimizedSchedule = this.optimizeInterviewGaps(interviews);
      
      // 데이터베이스 업데이트
      for (const interview of optimizedSchedule) {
        await this.db.updateApplicant(interview.id, {
          interviewTime: interview.optimizedTime
        });
      }
      
      return {
        success: true,
        optimizedCount: optimizedSchedule.length
      };
    } catch (error) {
      console.error('스케줄 최적화 실패:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // 면접 간격 최적화
  optimizeInterviewGaps(interviews) {
    const sortedInterviews = interviews.sort((a, b) => 
      a.interviewTime.localeCompare(b.interviewTime)
    );
    
    const optimized = [];
    let currentTime = '09:00';
    
    for (const interview of sortedInterviews) {
      optimized.push({
        ...interview,
        optimizedTime: currentTime
      });
      
      // 다음 면접 시간 계산 (60분 간격)
      const [hours, minutes] = currentTime.split(':').map(Number);
      const nextTime = new Date(2024, 0, 1, hours, minutes + 60);
      currentTime = `${String(nextTime.getHours()).padStart(2, '0')}:${String(nextTime.getMinutes()).padStart(2, '0')}`;
    }
    
    return optimized;
  }

  // 연결 해제
  async cleanup() {
    await this.db.disconnect();
  }
}

export default AIScheduler; 