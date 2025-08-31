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
    const startTime = Date.now();
    const sessionId = this.getSessionId();

    // 현재 페이지 정보 가져오기
    const currentPage = window.location.pathname.replace('/', '') || 'dashboard';

    console.group('🚀 [PICK-TALK API] 메시지 전송 시작');
    console.log('📝 메시지:', message);
    console.log('🔑 세션 ID:', sessionId);
    console.log('📄 현재 페이지:', currentPage);
    console.log('🌐 API URL:', `${this.baseUrl}/chat`);
    console.log('🕐 시작 시간:', new Date().toISOString());

    try {
      const requestBody = {
        message: message,
        session_id: sessionId,
        current_page: currentPage,
      };

      console.log('📤 [요청 데이터]:', requestBody);

      const fetchStart = Date.now();
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      const fetchTime = Date.now() - fetchStart;

      console.log('📊 [응답 정보]:', {
        상태코드: response.status,
        상태텍스트: response.statusText,
        네트워크시간: `${fetchTime}ms`,
        응답헤더: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [HTTP 오류]:', {
          상태: response.status,
          메시지: response.statusText,
          응답내용: errorText
        });
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const parseStart = Date.now();
      const data = await response.json();
      const parseTime = Date.now() - parseStart;
      const totalTime = Date.now() - startTime;

      console.log('📥 [응답 분석]:', {
        파싱시간: `${parseTime}ms`,
        총처리시간: `${totalTime}ms`,
        응답크기: JSON.stringify(data).length,
        응답구조: Object.keys(data),
        성공여부: data.success || 'N/A',
        신뢰도: data.confidence || 'N/A',
        툴사용: data.tool_results ? '있음' : '없음',
        페이지액션: data.page_action ? '있음' : '없음'
      });

      // 응답 품질 평가
      const hasMessage = data.response && data.response.length > 5;
      const hasActions = data.quick_actions && data.quick_actions.length > 0;
      const hasSuggestions = data.suggestions && data.suggestions.length > 0;

      const qualityScore = (hasMessage ? 3 : 0) + (hasActions ? 2 : 0) + (hasSuggestions ? 1 : 0);
      const qualityGrade = qualityScore >= 5 ? '높음' : qualityScore >= 3 ? '보통' : '낮음';

      console.log(`📈 [응답 품질] ${qualityGrade} (점수: ${qualityScore}/6)`);

      // 성능 분석
      if (totalTime > 10000) {
        console.warn('⚠️ [성능 경고] 응답시간 10초 초과:', totalTime + 'ms');
      } else if (totalTime > 5000) {
        console.warn('⚠️ [성능 주의] 응답시간 5초 초과:', totalTime + 'ms');
      } else {
        console.log('✅ [성능 양호] 응답시간 정상:', totalTime + 'ms');
      }

      console.groupEnd();
      return data;

    } catch (error) {
      const errorTime = Date.now() - startTime;

      console.error('❌ [API 오류 상세]:', {
        오류타입: error.name,
        오류메시지: error.message,
        실패시간: `${errorTime}ms`,
        세션ID: sessionId,
        원본메시지: message
      });

      console.groupEnd();
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

