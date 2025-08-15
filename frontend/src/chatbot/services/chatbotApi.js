/**
 * 챗봇 API 서비스
 */

class ChatbotApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8010';
  }

  /**
   * 챗봇과 대화
   * @param {string} userInput - 사용자 입력
   * @param {Array} conversationHistory - 대화 히스토리
   * @param {string} selectedDirection - 선택된 방향
   * @param {object} formData - 폼 데이터
   * @param {string} page - 페이지 ID
   * @param {string} mode - AI 모드
   * @param {object} contextHints - 컨텍스트 힌트
   * @returns {Promise<object>} API 응답
   */
  async chat(userInput, conversationHistory, selectedDirection, formData, page, mode, contextHints) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          user_input: userInput,
          conversation_history: conversationHistory,
          selected_direction: selectedDirection,
          form_data: formData,
          page: page,
          mode: mode,
          context_hints: contextHints
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[ChatbotApiService] API 호출 실패:', error);
      throw error;
    }
  }

  /**
   * 테스트 모드 챗봇과 대화
   * @param {string} userInput - 사용자 입력
   * @param {Array} conversationHistory - 대화 히스토리
   * @returns {Promise<object>} API 응답
   */
  async testModeChat(userInput, conversationHistory) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/test-mode-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          conversation_history: conversationHistory
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[ChatbotApiService] 테스트 모드 API 호출 실패:', error);
      throw error;
    }
  }
}

export default new ChatbotApiService();
