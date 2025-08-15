## 에이전트 챗봇 개요

- **역할**: LangGraph 모드 기반의 에이전트형 챗봇. 사용자의 요청을 의도 분류 → 도구 선택 → 응답 생성 순으로 처리하고, 채용 관련 정보는 필드로 추출해 프런트와 연동.
- **백엔드 핵심 구성**:
  - `backend/chatbot/core/agent_system.py`: 에이전트 파이프라인(의도 감지, 도구 실행, 응답 포맷팅)
  - `backend/chatbot/core/enhanced_field_extractor.py`: 규칙/사전/AI 결합 필드 추출기
  - `backend/chatbot/routers/langgraph_router.py`: 에이전트 챗봇 HTTP API 라우터
- **프런트엔드 연동**:
  - `frontend/src/components/LangGraphChatbot.js`: `/api/langgraph-agent/health`, `/api/langgraph-agent/chat` 사용

## 엔드포인트(백엔드)

모두 FastAPI 기준이며, `backend/main.py`에서 다음과 같이 등록됩니다.
- `/api/langgraph` 및 `/api/langgraph-agent` 프리픽스에 동일 라우터 마운트

### 기본 대화
- **POST** `/api/langgraph-agent/chat`
  - 요청(JSON):
    - `user_input` 또는 `message` (string)
    - `session_id` (string, optional)
    - `conversation_history` (array, optional)
  - 응답(JSON):
    - `success` (bool), `message` (string), `mode` (string: "langgraph"), `tool_used` (string|null), `confidence` (float), `session_id` (string)

예시 요청(cURL):
```bash
curl -X POST http://localhost:8000/api/langgraph-agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "프론트엔드 개발자 채용공고 작성해줘",
    "session_id": "demo-session-1",
    "conversation_history": []
  }'
```

### 헬스체크
- **GET** `/api/langgraph-agent/health`
  - 응답(JSON): `{ status: "healthy", ... }`

### 세션 관리
- **POST** `/api/langgraph-agent/sessions/{session_id}/clear`
  - 해당 세션의 메시지 히스토리 초기화(세션은 유지)

참고: 동일 라우터가 `/api/langgraph`에도 마운트되어 있어 동일한 경로를 사용할 수 있습니다. 프런트는 `/api/langgraph-agent` 사용을 권장합니다.

## 내부 처리 흐름(요약)

1) 의도 감지(`IntentDetectionNode.run` in `agent_system.py`)
- LangGraph 모드: `two_stage_classifier` → 채용 여부 판정 실패 시 규칙/사전 기반 추출 보강
- 일반 모드: 기본 컨텍스트 분류기

2) 도구 실행 노드들
- `WebSearchNode`, `CalculatorNode`, `RecruitmentNode`, `DatabaseQueryNode`, `FallbackNode`

3) 응답 포맷팅(`ResponseFormatterNode`)

4) 필드 추출 보강(프론트 연동용)
- 의도가 chat이어도 필드가 추출되면 함께 전달하여 UI 자동입력 지원

## 채용 의도 승격 기준(중요)

의도 승격(기존: “필드 1개면 승격”) 로직이 아래처럼 **강화**되었습니다.
- 위치: `backend/chatbot/core/agent_system.py`
- 기준 함수: `IntentDetectionNode._should_promote_to_recruit(fields)`
  - **다음 중 하나**를 만족하면 `recruit`로 승격:
    - **position** 존재
    - **experience/salary/location/requirements/preferences** 중 1개 이상 존재
    - **서로 다른 필드 2개 이상** 존재
- 적용 지점: LangGraph 보강 단계, 최종 보강 단계 모두 동일 기준 적용

## 필드 추출기(기술스택 매칭 개선)

- 위치: `backend/chatbot/core/enhanced_field_extractor.py`
- 변경 사항: 기술 키워드 매칭을 **단어 경계 기반 정규식**으로 변경하여 부분 포함 오탐 제거
  - 예: `git`이 `github`에 매칭되지 않음

## 프런트엔드 연동 포인트

- `frontend/src/components/LangGraphChatbot.js`
  - 헬스체크: `GET /api/langgraph-agent/health`
  - 채팅: `POST /api/langgraph-agent/chat`
- 일부 구형 코드에서 `POST /api/langgraph-agent` 호출이 있으나, 표준은 **`/chat`** 엔드포인트 사용

## 개발/실행 포트

- **프런트엔드**: 3001, **백엔드**: 8000 (개발 서버)  
  예: `http://localhost:8000/api/langgraph-agent/chat` [[memory:6051659]]

## 에러 처리(요약)

- 예외 발생 시 `HTTP 500`과 메시지 반환
- 헬스체크는 상태 및 세션 개요 제공

## 빠른 점검 체크리스트

- [ ] `/api/langgraph-agent/health` 200 OK 확인
- [ ] `/api/langgraph-agent/chat` 기본 대화 왕복 확인
- [ ] 채용 의도 승격 기준 동작 확인(일반 텍스트 → 승격되지 않음 / 채용 텍스트 → 승격)
- [ ] `github` 같은 입력에서 `git` 오탐 미발생


