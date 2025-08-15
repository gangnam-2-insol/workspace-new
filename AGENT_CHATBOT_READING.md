## 에이전트 챗봇 리딩 문서

이 문서는 프로젝트 내 에이전트 챗봇 기능의 구성 파일 목록과 동작 방식을 한눈에 이해할 수 있도록 정리한 가이드입니다.

### 개요
- **역할**: LangGraph 기반 에이전트가 사용자 입력을 분류하고, 일반 대화 또는 툴 실행(네비게이션/DOM 액션 등)을 수행해 결과를 반환합니다.
- **구성**: 프런트엔드의 챗 UI 컴포넌트 → 백엔드 FastAPI 라우터 → LangGraph 에이전트(LLM/툴 매니저/세션 관리).

---

### 관련 파일 목록

- **백엔드**
  - `backend/main.py`: FastAPI 앱 초기화 및 라우터 포함(챗봇/에이전트).
  - `backend/langgraph_router.py`: LangGraph 에이전트 전용 REST API 라우터(prefix: `/api/langgraph-agent`).
  - `backend/langgraph_agent.py`: LangGraph 에이전트 핵심 구현(StateGraph, LLM, 툴 실행, 세션 관리).
  - `backend/langgraph_config.py`: 에이전트 설정, 허용 경로, 의도/행동 유틸.
  - `backend/langgraph_tools.py`: `tool_manager` 제공. 네비게이션/DOM 등 툴 실행 및 동적 툴 로드.
  - `backend/services/llm_providers/*`: LLM 프로바이더 공통/오픈AI 등(참고용).
  - `backend/chatbot_router.py`: 일반 챗봇(Gemini 등) 라우터(`/api/chatbot`).
  - `backend/chatbot/routers/langgraph_router.py`: 별도(내부 AgentSystem 샘플) 라우터. 현재 메인 앱에는 미포함.

- **프런트엔드**
  - `frontend/src/components/LangGraphChatbot.js`: LangGraph 에이전트용 플로팅 챗봇(UI/전송/DOM 액션 처리).
  - `frontend/src/chatbot/components/FloatingChatbot/index.js`: 페이지 유도/자동화 중심의 플로팅 챗봇(일반 챗봇 + 일부 에이전트 연동).
  - `frontend/src/chatbot/services/langgraphApi.js`: LangGraph 전용 API 서비스(레거시 경로 사용 주의, 아래 참고).
  - `frontend/src/chatbot/services/chatbotApi.js`: 일반 챗봇 API 래퍼(백엔드 `/api/chatbot`).

---

### 프런트엔드 동작 방식

- **`LangGraphChatbot.js`**
  - 전송 시 우선 로컬 DOM 액션 시도(키워드로 클릭/네비게이션 해석) 후, 실패 시 백엔드 호출.
  - REST 호출: `POST /api/langgraph-agent/chat` 로 `user_input`, `session_id`, `context` 전달.
  - 응답이 `react_agent_response` JSON 형태라면 페이지 이동(`navigate`) 또는 DOM 액션(`dom`)을 수행.
  - 세션 관리: 최초 응답의 `session_id`를 보관하여 이후 요청에 재사용.
  - 상태 확인: `GET /api/langgraph-agent/health` 로 에이전트 상태 점검.

- **`FloatingChatbot/index.js`**
  - 메뉴/페이지 키워드 매칭 → `onPageAction` 콜백 또는 `navigate` 호출로 페이지 이동 유도.
  - UI 스캔 및 간단 임베딩을 이용한 RAG 스타일 요소 매칭으로 버튼 클릭 등 자동화 시도.
  - 일반 대화/질의는 기본적으로 백엔드 일반 챗봇 `POST {REACT_APP_API_URL}/api/chatbot/chat` 사용.
  - LangGraph 연동 경로로 `POST /api/langgraph-agent` 호출 코드가 있으나, 현재 백엔드는 `/api/langgraph-agent/chat` 만 제공(주의사항 참조).

---

### 백엔드 동작 방식

- **라우터(`backend/langgraph_router.py`)**
  - `POST /api/langgraph-agent/chat`: 세션 ID 생성·재사용 → 에이전트 `process_message` 호출 → 결과를 `success/message/mode/tool_used/confidence/timestamp`로 반환.
  - 세션 관리: `GET /api/langgraph-agent/sessions`, `GET /api/langgraph-agent/sessions/{id}/history`, `POST /api/langgraph-agent/sessions/{id}/clear`, `DELETE /api/langgraph-agent/sessions/{id}`.
  - 헬스체크: `GET /api/langgraph-agent/health`.

- **에이전트(`backend/langgraph_agent.py`)**
  - LLM: `ChatGoogleGenerativeAI` 사용. 환경변수 `GOOGLE_API_KEY` 필요.
  - 워크플로우(StateGraph):
    1) `classify_input`에서 의도 분류(navigate/tool/general) 및 타깃 추출.
    2) 분기 후 일반 대화(`general_conversation`) 또는 툴 실행(`tool_execution`).
    3) `response_generation`에서 최종 응답 메시지 생성(툴 결과는 자연어/JSON 가공).
  - 툴 실행: `tool_manager.execute_tool` 호출. 네비게이션/DOM 액션은 구조화 응답을 생성할 수 있으며, 프런트는 이를 파싱해 동작.
  - 세션: `self.sessions`에 히스토리/타임스탬프 보관. 히스토리 일부를 LLM 컨텍스트로 사용.
  - 관리자 모드: `admin_mode` 연계. 세션별 토글/명령 처리 후 즉시 응답.

---

### 주요 엔드포인트 요약

- 에이전트(LangGraph)
  - `POST /api/langgraph-agent/chat`
  - `GET /api/langgraph-agent/health`
  - `GET /api/langgraph-agent/sessions`
  - `GET /api/langgraph-agent/sessions/{session_id}/history`
  - `POST /api/langgraph-agent/sessions/{session_id}/clear`
  - `DELETE /api/langgraph-agent/sessions/{session_id}`

- 일반 챗봇(키워드 분류 → Gemini 응답 등)
  - `POST /api/chatbot/chat`

---

### 데이터 포맷(페이지 액션)

- 에이전트가 페이지 액션을 유도할 때, 다음과 같은 구조화 메시지를 반환할 수 있습니다.
```json
{
  "type": "react_agent_response",
  "response": "이동합니다.",
  "page_action": {
    "action": "navigate",
    "target": "/resume"
  }
}
```
- 프런트는 해당 JSON을 감지해 `navigate` 또는 `dom` 액션을 수행합니다.

---

### 환경/설정

- 포트: 프런트 3001, 백엔드 8000(기억 정보 기준). 프런트 서비스는 기본 `http://localhost:8000`을 가정하며 `REACT_APP_API_URL`로 재정의 가능.
- LLM: `GOOGLE_API_KEY` 필요. 모델/파라미터는 `backend/langgraph_config.py`에서 관리.

---

### 주의사항 및 권장 변경

- `FloatingChatbot/index.js`에 존재하는 `POST /api/langgraph-agent` 호출은 현재 백엔드 라우터에 존재하지 않습니다. 실제 동작 엔드포인트는 `POST /api/langgraph-agent/chat` 입니다.
  - 옵션 A: 프런트 호출 경로를 `'/api/langgraph-agent/chat'`로 변경.
  - 옵션 B: 백엔드에 `POST /api/langgraph-agent` 엔드포인트를 추가해 호환성 유지.

---

### 빠른 점검 체크리스트

- 프런트에서 에이전트 사용: `frontend/src/components/LangGraphChatbot.js`가 렌더되고 있는지 확인.
- 백엔드 가동: `backend/main.py` 실행 후 `/api/langgraph-agent/health`가 healthy 인지 확인.
- LLM 키: `GOOGLE_API_KEY` 설정 확인.
- 페이지 액션: 에이전트 응답에 `react_agent_response`가 포함될 때 프런트에서 네비게이션/DOM 액션이 정상 동작하는지 확인.


