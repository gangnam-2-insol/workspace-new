const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class PickChatbotApi {
  constructor() {
          this.baseUrl = `${API_BASE_URL}/pick-chatbot`;
    this.sessionId = null;
  }

  // 세션 ID 생성 또는 가져오기
  getSessionId() {
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
    }
    return this.sessionId;
  }

  // 세션 ID 생성
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // 세션 초기화
  resetSession() {
    this.sessionId = null;
  }

  // 챗봇과 대화
  async chat(message) {
    const sessionId = this.getSessionId();
    console.log('🔍 [DEBUG] 에이전트 API 호출:', {
      message,
      sessionId,
      url: `${this.baseUrl}/chat`
    });
    
    try {
      const requestBody = {
        message: message,
        session_id: sessionId,
      };
      
      console.log('🔍 [DEBUG] 요청 본문:', requestBody);
      
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('🔍 [DEBUG] 응답 상태:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 [DEBUG] HTTP 오류 응답:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const data = await response.json();
      console.log('🔍 [DEBUG] 응답 데이터:', data);
      return data;
    } catch (error) {
      console.error('🔍 [DEBUG] 에이전트 API 오류:', error);
      throw error;
    }
  }

  // 세션 정보 조회
  async getSession(sessionId) {
    try {
      const response = await fetch(`${this.baseUrl}/session/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('세션 조회 오류:', error);
      throw error;
    }
  }

  // 세션 삭제
  async deleteSession(sessionId) {
    try {
      const response = await fetch(`${this.baseUrl}/session/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('세션 삭제 오류:', error);
      throw error;
    }
  }

  // 모든 세션 목록 조회
  async listSessions() {
    try {
      const response = await fetch(`${this.baseUrl}/sessions`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('세션 목록 조회 오류:', error);
      throw error;
    }
  }
}

export default new PickChatbotApi();

