/**
 * 리액트 에이전트 API 서비스
 * PickTalk에서 사용할 수 있도록 모듈화
 */

import axios from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// 에이전트 API 클래스
class AgentApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.sessionId = null;
    this.currentState = 'initial';
  }

  // 세션 시작
  async startSession(userId = 'user_123', companyInfo = {}) {
    try {
      const response = await axios.post(`${this.baseURL}/api/react-agent/start-session`, {
        user_id: userId,
        company_info: companyInfo
      });

      if (response.data.session_id) {
        this.sessionId = response.data.session_id;
        this.currentState = response.data.state || 'initial';
      }

      return response.data;
    } catch (error) {
      console.error('에이전트 세션 시작 실패:', error);
      throw error;
    }
  }

  // 사용자 입력 처리
  async processInput(userInput, sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      if (!targetSessionId) {
        throw new Error('세션이 시작되지 않았습니다. 먼저 세션을 시작해주세요.');
      }

      const response = await axios.post(`${this.baseURL}/api/react-agent/process-input`, {
        session_id: targetSessionId,
        user_input: userInput
      });

      // 상태 업데이트
      if (response.data.state) {
        this.currentState = response.data.state;
      }

      return response.data;
    } catch (error) {
      console.error('에이전트 입력 처리 실패:', error);
      throw error;
    }
  }

  // LangGraph 에이전트 호출
  async callLangGraphAgent(message, conversationHistory = [], sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId || `session_${Date.now()}`;

      const response = await axios.post(`${this.baseURL}/api/langgraph-agent`, {
        message: message,
        conversation_history: conversationHistory,
        session_id: targetSessionId
      });

      return response.data;
    } catch (error) {
      console.error('LangGraph 에이전트 호출 실패:', error);
      throw error;
    }
  }

  // 채용공고 등록
  async registerJobPosting(jobData, sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      if (!targetSessionId) {
        throw new Error('세션이 시작되지 않았습니다.');
      }

      const response = await axios.post(`${this.baseURL}/api/job-posting-agent/register`, {
        session_id: targetSessionId,
        job_data: jobData
      });

      return response.data;
    } catch (error) {
      console.error('채용공고 등록 실패:', error);
      throw error;
    }
  }

  // 세션 종료
  async endSession(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      if (!targetSessionId) {
        return { success: true, message: '세션이 이미 종료되었습니다.' };
      }

      const response = await axios.post(`${this.baseURL}/api/react-agent/end-session`, {
        session_id: targetSessionId
      });

      // 로컬 세션 정리
      if (targetSessionId === this.sessionId) {
        this.sessionId = null;
        this.currentState = 'initial';
      }

      return response.data;
    } catch (error) {
      console.error('에이전트 세션 종료 실패:', error);
      throw error;
    }
  }

  // 세션 상태 조회
  async getSessionStatus(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      if (!targetSessionId) {
        return { state: 'no_session', message: '활성 세션이 없습니다.' };
      }

      const response = await axios.get(`${this.baseURL}/api/react-agent/session-status/${targetSessionId}`);
      return response.data;
    } catch (error) {
      console.error('세션 상태 조회 실패:', error);
      throw error;
    }
  }

  // 에이전트 도구 관리
  async getAvailableTools(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      const response = await axios.get(`${this.baseURL}/api/langgraph-agent/admin/tools?session_id=${targetSessionId}`);
      return response.data;
    } catch (error) {
      console.error('사용 가능한 도구 조회 실패:', error);
      throw error;
    }
  }

  // 에이전트 성능 모니터링
  async getPerformanceMetrics(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.sessionId;
      const response = await axios.get(`${this.baseURL}/api/job-posting-agent/performance/${targetSessionId}`);
      return response.data;
    } catch (error) {
      console.error('성능 메트릭 조회 실패:', error);
      throw error;
    }
  }

  // 현재 세션 정보 반환
  getCurrentSession() {
    return {
      sessionId: this.sessionId,
      currentState: this.currentState,
      isActive: !!this.sessionId
    };
  }

  // 세션 초기화
  resetSession() {
    this.sessionId = null;
    this.currentState = 'initial';
  }
}

// 싱글톤 인스턴스 생성
const agentApiService = new AgentApiService();

export default agentApiService;
