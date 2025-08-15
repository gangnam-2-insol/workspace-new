/**
 * LangGraph API 서비스
 */

class LangGraphApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8010';
  }

  /**
   * LangGraph Agent 호출
   * @param {string} userInput - 사용자 입력
   * @param {Array} conversationHistory - 대화 히스토리
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<object>} API 응답
   */
  async callLangGraphAgent(userInput, conversationHistory, sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/langgraph/agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userInput,
          conversation_history: conversationHistory,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[LangGraphApiService] API 호출 실패:', error);
      throw error;
    }
  }

  /**
   * LangGraph 채용공고 등록 Agent 호출
   * @param {string} userInput - 사용자 입력
   * @param {Array} conversationHistory - 대화 히스토리
   * @param {string} sessionId - 세션 ID
   * @returns {Promise<object>} API 응답
   */
  async callLangGraphJobRegistration(userInput, conversationHistory, sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/langgraph/job-registration`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          conversation_history: conversationHistory,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[LangGraphApiService] 채용공고 등록 API 호출 실패:', error);
      throw error;
    }
  }

  /**
   * 추출된 필드 정보를 채용공고등록 폼에 전달
   * @param {object} extractedFields - 추출된 필드 정보
   */
  dispatchFieldUpdate(extractedFields) {
    try {
      console.log('[LangGraphApiService] dispatchFieldUpdate 호출됨');
      console.log('[LangGraphApiService] extractedFields:', extractedFields);
      console.log('[LangGraphApiService] extractedFields 타입:', typeof extractedFields);
      console.log('[LangGraphApiService] extractedFields 키 개수:', Object.keys(extractedFields).length);
      
      // LangGraphJobRegistration 컴포넌트용 이벤트
      const langGraphEvent = new CustomEvent('langGraphDataUpdate', {
        detail: {
          action: 'updateLangGraphData',
          data: extractedFields,
          timestamp: new Date().toISOString()
        }
      });
      
      console.log('[LangGraphApiService] langGraphEvent 생성:', langGraphEvent);
      console.log('[LangGraphApiService] langGraphEvent.detail:', langGraphEvent.detail);
      
      window.dispatchEvent(langGraphEvent);
      console.log('[LangGraphApiService] LangGraph 이벤트 전달 완료:', extractedFields);
      
      // 기존 TextBasedRegistration 컴포넌트용 이벤트 (하위 호환성)
      const textBasedEvent = new CustomEvent('langGraphDataUpdate', {
        detail: {
          extracted_fields: extractedFields,
          timestamp: new Date().toISOString()
        }
      });
      
      window.dispatchEvent(textBasedEvent);
      console.log('[LangGraphApiService] TextBased 이벤트 전달 완료:', extractedFields);
    } catch (error) {
      console.error('[LangGraphApiService] 필드 업데이트 이벤트 전달 실패:', error);
    }
  }
}

export default new LangGraphApiService();
