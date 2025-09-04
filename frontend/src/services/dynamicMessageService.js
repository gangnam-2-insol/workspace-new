/**
 * 동적 메시지 생성 서비스
 * 사용자의 상황과 맥락에 따라 자연스러운 메시지를 생성합니다.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class DynamicMessageService {
  /**
   * 맥락에 맞는 메시지 생성
   * @param {Object} context - 사용자 컨텍스트 정보
   * @returns {Promise<Object>} 생성된 메시지
   */
  async generateContextualMessage(context) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dynamic-messages/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('동적 메시지 생성 중 오류:', error);
      // 오류 발생 시 기본 메시지 반환
      return {
        message: "안녕하세요! 무엇을 도와드릴까요? 😊",
        message_type: "fallback",
        context: context
      };
    }
  }

  /**
   * 후속 질문이나 안내 메시지 생성
   * @param {Object} context - 사용자 컨텍스트 정보
   * @returns {Promise<Object>} 생성된 메시지
   */
  async generateFollowUpMessage(context) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dynamic-messages/follow-up`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('후속 메시지 생성 중 오류:', error);
      return {
        message: "다음 단계를 진행해보시겠어요? 😊",
        message_type: "fallback",
        context: context
      };
    }
  }

  /**
   * 격려나 동기부여 메시지 생성
   * @param {Object} context - 사용자 컨텍스트 정보
   * @returns {Promise<Object>} 생성된 메시지
   */
  async generateEncouragementMessage(context) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dynamic-messages/encouragement`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('격려 메시지 생성 중 오류:', error);
      return {
        message: "잘 하고 있어요! 계속 진행해보세요 💫",
        message_type: "fallback",
        context: context
      };
    }
  }

  /**
   * 사용 가능한 메시지 템플릿 조회
   * @returns {Promise<Object>} 메시지 템플릿
   */
  async getMessageTemplates() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dynamic-messages/templates`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('메시지 템플릿 조회 중 오류:', error);
      return {
        greeting_templates: [],
        context_templates: {},
        tone_templates: {}
      };
    }
  }

  /**
   * 사용자 컨텍스트 정보 생성
   * @param {Object} userState - 사용자 상태 정보
   * @returns {Object} 컨텍스트 정보
   */
  createUserContext(userState = {}) {
    return {
      current_page: userState.currentPage || '',
      current_step: userState.currentStep || '',
      previous_input: userState.previousInput || {},
      user_tone: userState.userTone || 'friendly',
      completed_steps: userState.completedSteps || [],
      progress: userState.progress || 0.0,
      user_input: userState.userInput || ''
    };
  }

  /**
   * 채용공고 작성 단계별 컨텍스트 생성
   * @param {Object} jobData - 채용공고 데이터
   * @param {number} currentStep - 현재 단계
   * @returns {Object} 컨텍스트 정보
   */
  createJobPostingContext(jobData = {}, currentStep = 0) {
    const steps = ['title', 'department', 'experience', 'salary', 'location'];
    const completedSteps = [];

    // 완료된 단계들 확인
    if (jobData.title) completedSteps.push('title');
    if (jobData.department) completedSteps.push('department');
    if (jobData.experience) completedSteps.push('experience');
    if (jobData.salary) completedSteps.push('salary');
    if (jobData.location) completedSteps.push('location');

    const progress = completedSteps.length / steps.length;

    return {
      current_page: 'job_posting',
      current_step: steps[currentStep] || '',
      previous_input: jobData,
      user_tone: 'friendly',
      completed_steps: completedSteps,
      progress: progress
    };
  }

  /**
   * 이력서 분석 컨텍스트 생성
   * @param {string} status - 분석 상태
   * @returns {Object} 컨텍스트 정보
   */
  createResumeAnalysisContext(status = 'upload') {
    return {
      current_page: 'resume_analysis',
      current_step: status,
      previous_input: {},
      user_tone: 'friendly',
      completed_steps: [],
      progress: status === 'complete' ? 1.0 : 0.5
    };
  }

  /**
   * 지원자 관리 컨텍스트 생성
   * @param {string} action - 수행할 작업
   * @returns {Object} 컨텍스트 정보
   */
  createApplicantManagementContext(action = 'list') {
    return {
      current_page: 'applicant_management',
      current_step: action,
      previous_input: {},
      user_tone: 'friendly',
      completed_steps: [],
      progress: 0.0
    };
  }
}

// 싱글톤 인스턴스 생성
const dynamicMessageService = new DynamicMessageService();

export default dynamicMessageService;
