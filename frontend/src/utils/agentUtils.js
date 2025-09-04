/**
 * 리액트 에이전트 유틸리티 함수들
 * PickTalk 컴포넌트에서 사용할 수 있도록 모듈화
 */

// 에이전트 상태 관리
export const AgentState = {
  INITIAL: 'initial',
  KEYWORD_EXTRACTION: 'keyword_extraction',
  TEMPLATE_SELECTION: 'template_selection',
  CONTENT_GENERATION: 'content_generation',
  REVIEW_EDIT: 'review_edit',
  FINAL_CONFIRMATION: 'final_confirmation'
};

// 에이전트 메시지 타입
export const MessageType = {
  USER: 'user',
  AGENT: 'agent',
  SYSTEM: 'system',
  ERROR: 'error',
  SUCCESS: 'success'
};

// 에이전트 응답 분석
export const analyzeAgentResponse = (response) => {
  const analysis = {
    hasKeywords: false,
    hasTemplates: false,
    hasGeneratedContent: false,
    hasPageAction: false,
    hasSuggestions: false,
    confidence: 0.8
  };

  if (response.extracted_keywords && response.extracted_keywords.length > 0) {
    analysis.hasKeywords = true;
  }

  if (response.recommended_templates && response.recommended_templates.length > 0) {
    analysis.hasTemplates = true;
  }

  if (response.generated_content) {
    analysis.hasGeneratedContent = true;
  }

  if (response.page_action) {
    analysis.hasPageAction = true;
  }

  if (response.suggestions && response.suggestions.length > 0) {
    analysis.hasSuggestions = true;
  }

  if (response.confidence) {
    analysis.confidence = response.confidence;
  }

  return analysis;
};

// 에이전트 상태별 다음 액션 추천
export const getNextActionsByState = (currentState, response) => {
  const actions = [];

  switch (currentState) {
    case AgentState.INITIAL:
      actions.push(
        { title: "채용공고 작성", action: "navigate", icon: "📝", params: { page: "job_posting" } },
        { title: "지원자 관리", action: "navigate", icon: "👥", params: { page: "applicants" } },
        { title: "대시보드", action: "navigate", icon: "📊", params: { page: "dashboard" } },
        { title: "채용공고 목록", action: "navigate", icon: "📋", params: { page: "recruitment" } }
      );
      break;

    case AgentState.KEYWORD_EXTRACTION:
      if (response.extracted_keywords && response.extracted_keywords.length > 0) {
        actions.push(
          { title: "채용공고 미리보기", action: "navigate", icon: "👁️", params: { page: "job_posting", tab: "preview" } },
          { title: "템플릿 선택", action: "navigate", icon: "📋", params: { page: "job_posting", tab: "templates" } },
          { title: "저장하기", action: "navigate", icon: "💾", params: { page: "job_posting", tab: "save" } }
        );
      }
      break;

    case AgentState.TEMPLATE_SELECTION:
      if (response.recommended_templates && response.recommended_templates.length > 0) {
        actions.push(
          { title: "채용공고 등록", action: "navigate", icon: "🚀", params: { page: "job_posting", tab: "register" } },
          { title: "내용 수정", action: "navigate", icon: "✏️", params: { page: "job_posting", tab: "edit" } },
          { title: "지원자 요구사항 설정", action: "navigate", icon: "⚙️", params: { page: "job_posting", tab: "requirements" } }
        );
      }
      break;

    case AgentState.CONTENT_GENERATION:
      actions.push(
        { title: "지원자 관리", action: "navigate", icon: "👥", params: { page: "applicants" } },
        { title: "인터뷰 일정", action: "navigate", icon: "📅", params: { page: "interview" } },
        { title: "통계 보기", action: "navigate", icon: "📊", params: { page: "dashboard" } }
      );
      break;

    case AgentState.REVIEW_EDIT:
      actions.push(
        { title: "채용공고 발행", action: "navigate", icon: "📢", params: { page: "job_posting", tab: "publish" } },
        { title: "설정 관리", action: "navigate", icon: "⚙️", params: { page: "settings" } },
        { title: "새 채용공고", action: "navigate", icon: "🆕", params: { page: "job_posting", tab: "new" } }
      );
      break;

    case AgentState.FINAL_CONFIRMATION:
      actions.push(
        { title: "지원자 모니터링", action: "navigate", icon: "📈", params: { page: "dashboard", tab: "applicants" } },
        { title: "채용 현황", action: "navigate", icon: "📊", params: { page: "dashboard", tab: "recruitment" } },
        { title: "회사 문화 관리", action: "navigate", icon: "🏢", params: { page: "company_culture" } }
      );
      break;

    default:
      actions.push(
        { title: "도움말", action: "help", icon: "❓" },
        { title: "처음부터", action: "restart", icon: "🔄" }
      );
  }

  return actions;
};

// 에이전트 응답 포맷팅
export const formatAgentResponse = (response, currentState) => {
  let formattedText = response.response || response.message || '';

  // 상태별 응답 강화
  if (currentState === AgentState.KEYWORD_EXTRACTION && response.extracted_keywords) {
    formattedText += `\n\n🔍 **추출된 키워드:**\n${response.extracted_keywords.map(kw => `• ${kw}`).join('\n')}`;
  }

  if (currentState === AgentState.TEMPLATE_SELECTION && response.recommended_templates) {
    formattedText += `\n\n📋 **추천 템플릿:**\n${response.recommended_templates.map((t, i) => `${i + 1}. ${t.name}`).join('\n')}`;
  }

  if (currentState === AgentState.CONTENT_GENERATION && response.generated_content) {
    formattedText += `\n\n📝 **생성된 내용:**\n${response.generated_content.title ? `제목: ${response.generated_content.title}\n` : ''}${response.generated_content.description ? `설명: ${response.generated_content.description}` : ''}`;
  }

  return formattedText;
};

// 에이전트 세션 관리
export const createAgentSession = () => {
  return {
    id: Date.now().toString(),
    startTime: new Date(),
    state: AgentState.INITIAL,
    messages: [],
    extractedData: {},
    metadata: {}
  };
};

// 에이전트 상태 전환
export const transitionAgentState = (currentState, action, response) => {
  const stateTransitions = {
    [AgentState.INITIAL]: {
      'describe_job': AgentState.KEYWORD_EXTRACTION,
      'tech_stack': AgentState.KEYWORD_EXTRACTION,
      'company_info': AgentState.KEYWORD_EXTRACTION
    },
    [AgentState.KEYWORD_EXTRACTION]: {
      'confirm_keywords': AgentState.TEMPLATE_SELECTION,
      'next_step': AgentState.TEMPLATE_SELECTION
    },
    [AgentState.TEMPLATE_SELECTION]: {
      'select_template': AgentState.CONTENT_GENERATION,
      'generate_new_template': AgentState.CONTENT_GENERATION
    },
    [AgentState.CONTENT_GENERATION]: {
      'review_content': AgentState.REVIEW_EDIT,
      'next_step': AgentState.REVIEW_EDIT
    },
    [AgentState.REVIEW_EDIT]: {
      'final_confirm': AgentState.FINAL_CONFIRMATION,
      'modify_content': AgentState.CONTENT_GENERATION
    },
    [AgentState.FINAL_CONFIRMATION]: {
      'register': 'completed',
      'restart': AgentState.INITIAL
    }
  };

  return stateTransitions[currentState]?.[action] || currentState;
};

// 에이전트 성능 모니터링
export const monitorAgentPerformance = (startTime, response) => {
  const endTime = Date.now();
  const responseTime = endTime - startTime;

  const performance = {
    responseTime,
    isSlow: responseTime > 5000,
    isVerySlow: responseTime > 10000,
    timestamp: new Date().toISOString()
  };

  // 성능 로깅
  if (performance.isSlow) {
    console.warn(`⚠️ 에이전트 응답이 느립니다: ${responseTime}ms`);
  }

  return performance;
};
