class AIChatbotService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  // AI 챗봇 세션 시작
  async startSession(page, fields) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page,
          fields,
          mode: 'modal_assistant'
        })
      });

      if (!response.ok) {
        throw new Error('세션 시작 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('AI 챗봇 세션 시작 오류:', error);
      throw error;
    }
  }

  // AI 챗봇과 대화
  async sendMessage(sessionId, userInput, currentField, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_input: userInput,
          current_field: currentField,
          context,
          mode: 'modal_assistant'
        })
      });

      if (!response.ok) {
        throw new Error('메시지 전송 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('AI 챗봇 메시지 전송 오류:', error);
      throw error;
    }
  }

  // 대화형 질문-답변 처리
  async handleConversation(sessionId, userInput, currentField, filledFields = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_input: userInput,
          current_field: currentField,
          filled_fields: filledFields,
          mode: 'conversational'
        })
      });

      if (!response.ok) {
        throw new Error('대화 처리 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('대화 처리 오류:', error);
      throw error;
    }
  }

  // 컨텍스트 기반 질문 생성
  async generateContextualQuestions(currentField, filledFields = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/generate-questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_field: currentField,
          filled_fields: filledFields
        })
      });

      if (!response.ok) {
        throw new Error('질문 생성 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('질문 생성 오류:', error);
      throw error;
    }
  }

  // 필드 자동 완성 제안
  async getSuggestions(field, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field,
          context
        })
      });

      if (!response.ok) {
        throw new Error('제안 가져오기 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('AI 제안 가져오기 오류:', error);
      throw error;
    }
  }

  // 필드 값 검증
  async validateField(field, value, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field,
          value,
          context
        })
      });

      if (!response.ok) {
        throw new Error('검증 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('필드 검증 오류:', error);
      throw error;
    }
  }

  // 스마트 자동 완성
  async smartAutoComplete(partialInput, field, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/autocomplete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          partial_input: partialInput,
          field,
          context
        })
      });

      if (!response.ok) {
        throw new Error('자동 완성 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('스마트 자동 완성 오류:', error);
      throw error;
    }
  }

  // 컨텍스트 기반 추천
  async getContextualRecommendations(currentField, filledFields = {}, context = {}) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_field: currentField,
          filled_fields: filledFields,
          context
        })
      });

      if (!response.ok) {
        throw new Error('추천 가져오기 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('컨텍스트 추천 오류:', error);
      throw error;
    }
  }

  // 실시간 필드 업데이트
  async updateFieldInRealTime(field, value, sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/update-field`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          field,
          value
        })
      });

      if (!response.ok) {
        throw new Error('필드 업데이트 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('실시간 필드 업데이트 오류:', error);
      throw error;
    }
  }

  // 세션 종료
  async endSession(sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/api/chatbot/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('세션 종료 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('세션 종료 오류:', error);
      throw error;
    }
  }

  // 오프라인 모드용 로컬 처리
  processOffline(userInput, field, context = {}) {
    // 오프라인에서도 기본적인 처리 가능
    const responses = {
      department: {
        message: '부서 정보를 확인했습니다. 몇 명을 채용하실 예정인가요?',
        value: userInput,
        suggestions: ['1명', '2명', '3명', '5명', '10명'],
        confidence: 0.8
      },
      headcount: {
        message: '채용 인원을 확인했습니다. 어떤 업무를 담당하게 될까요?',
        value: userInput,
        suggestions: ['개발', '디자인', '마케팅', '영업', '기획'],
        confidence: 0.9
      },
      workType: {
        message: '업무 내용을 확인했습니다. 근무 시간은 어떻게 되나요?',
        value: userInput,
        suggestions: ['09:00-18:00', '10:00-19:00', '유연근무제'],
        confidence: 0.7
      },
      workHours: {
        message: '근무 시간을 확인했습니다. 근무 위치는 어디인가요?',
        value: userInput,
        suggestions: ['서울', '부산', '대구', '인천', '대전'],
        confidence: 0.8
      },
      location: {
        message: '근무 위치를 확인했습니다. 급여 조건은 어떻게 되나요?',
        value: userInput,
        suggestions: ['면접 후 협의', '3000만원', '4000만원', '5000만원'],
        confidence: 0.6
      },
      salary: {
        message: '급여 조건을 확인했습니다. 마감일은 언제인가요?',
        value: userInput,
        suggestions: ['2024년 12월 31일', '2024년 11월 30일', '채용 시 마감'],
        confidence: 0.7
      },
      deadline: {
        message: '마감일을 확인했습니다. 연락처 이메일을 알려주세요.',
        value: userInput,
        suggestions: ['hr@company.com', 'recruit@company.com'],
        confidence: 0.8
      },
      email: {
        message: '이메일을 확인했습니다. 모든 정보 입력이 완료되었습니다!',
        value: userInput,
        suggestions: [],
        confidence: 0.9
      }
    };

    return responses[field] || {
      message: '정보를 확인했습니다. 다음 질문으로 넘어가겠습니다.',
      value: userInput,
      suggestions: [],
      confidence: 0.5
    };
  }

  // 대화형 질문-답변 오프라인 처리
  processConversationOffline(userInput, field, context = {}) {
    const conversationResponses = {
      department: {
        questions: [
          "개발팀은 어떤 업무를 하나요?",
          "마케팅팀은 어떤 역할인가요?",
          "영업팀의 주요 업무는?",
          "디자인팀은 어떤 일을 하나요?"
        ],
        answers: {
          "개발팀은 어떤 업무를 하나요?": "개발팀은 주로 웹/앱 개발, 시스템 구축, 기술 지원 등을 담당합니다. 프론트엔드, 백엔드, 풀스택 개발자로 구성되어 있으며, 최신 기술 트렌드를 반영한 개발을 진행합니다.",
          "마케팅팀은 어떤 역할인가요?": "마케팅팀은 브랜드 관리, 광고 캠페인 기획, 디지털 마케팅, 콘텐츠 제작, 고객 분석 등을 담당합니다. 온라인/오프라인 마케팅 전략을 수립하고 실행합니다.",
          "영업팀의 주요 업무는?": "영업팀은 신규 고객 발굴, 계약 체결, 고객 관계 관리, 매출 목표 달성 등을 담당합니다. B2B/B2C 영업, 해외 영업 등 다양한 영업 활동을 수행합니다.",
          "디자인팀은 어떤 일을 하나요?": "디자인팀은 UI/UX 디자인, 브랜드 디자인, 그래픽 디자인, 웹/앱 디자인 등을 담당합니다. 사용자 경험을 최우선으로 하는 디자인을 제작합니다."
        }
      },
      headcount: {
        questions: [
          "1명 채용하면 충분한가요?",
          "팀 규모는 어떻게 되나요?",
          "신입/경력 구분해서 채용하나요?",
          "계약직/정규직 중 어떤가요?"
        ],
        answers: {
          "1명 채용하면 충분한가요?": "현재 업무량과 향후 계획을 고려하여 결정하시면 됩니다. 초기에는 1명으로 시작하고, 필요에 따라 추가 채용을 고려해보세요.",
          "팀 규모는 어떻게 되나요?": "팀 규모는 업무 특성과 회사 규모에 따라 다릅니다. 소규모 팀(3-5명)부터 대규모 팀(10명 이상)까지 다양하게 구성됩니다.",
          "신입/경력 구분해서 채용하나요?": "업무 특성에 따라 신입/경력을 구분하여 채용하는 것이 일반적입니다. 신입은 성장 잠재력, 경력자는 즉시 투입 가능한 실력을 중시합니다.",
          "계약직/정규직 중 어떤가요?": "프로젝트 기반이면 계약직, 장기적 업무라면 정규직을 고려해보세요. 각각의 장단점을 비교하여 결정하시면 됩니다."
        }
      }
    };

    const fieldData = conversationResponses[field] || {
      questions: [
        "이 항목에 대해 궁금한 점이 있으신가요?",
        "더 자세한 설명이 필요하신가요?",
        "예시를 들어 설명해드릴까요?"
      ],
      answers: {
        "이 항목에 대해 궁금한 점이 있으신가요?": "해당 항목에 대해 더 구체적으로 설명드릴 수 있습니다. 어떤 부분이 궁금하신지 말씀해 주세요.",
        "더 자세한 설명이 필요하신가요?": "네, 더 자세한 설명을 제공해드릴 수 있습니다. 어떤 부분을 더 알고 싶으신가요?",
        "예시를 들어 설명해드릴까요?": "실제 예시를 통해 더 쉽게 이해하실 수 있도록 도와드리겠습니다."
      }
    };

    // 질문인지 답변인지 판단
    const isQuestion = fieldData.questions.some(q => userInput.includes(q) || q.includes(userInput));
    
    if (isQuestion) {
      // 질문에 대한 답변 제공
      const matchingQuestion = fieldData.questions.find(q => 
        userInput.includes(q) || q.includes(userInput)
      );
      return {
        message: fieldData.answers[matchingQuestion] || "해당 질문에 대한 답변을 준비 중입니다.",
        isConversation: true,
        suggestions: fieldData.questions.filter(q => q !== matchingQuestion)
      };
    } else {
      // 일반적인 답변 처리
      return this.processOffline(userInput, field, context);
    }
  }
}

export default new AIChatbotService(); 