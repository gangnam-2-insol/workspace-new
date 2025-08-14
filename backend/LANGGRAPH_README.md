# LangGraph 에이전트 챗봇

## 개요

LangGraph를 이용한 모듈화된 지능형 에이전트 챗봇입니다. 이 시스템은 재사용 가능한 구조로 설계되어 다른 프로젝트에서도 쉽게 활용할 수 있습니다.

## 주요 기능

### 🤖 지능형 대화
- Gemini LLM을 활용한 자연스러운 대화
- 컨텍스트 기반 응답 생성
- 대화 히스토리 관리

### 🛠️ 툴 기반 작업
- 채용 정보 검색
- 이력서 분석
- 포트폴리오 생성
- 지원서 제출
- 사용자 정보 조회
- 면접 일정 관리

### 🔄 모듈화된 구조
- 설정 중앙 관리
- 툴 확장 가능
- 재사용 가능한 컴포넌트

## 파일 구조

```
admin/backend/
├── langgraph_agent.py      # 메인 에이전트 클래스
├── langgraph_router.py     # FastAPI 라우터
├── langgraph_config.py     # 설정 관리
├── langgraph_tools.py      # 툴 관리자
└── LANGGRAPH_README.md     # 이 파일
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 다음을 추가:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. 서버 실행

```bash
cd admin/backend
python main.py
```

## API 엔드포인트

### 채팅
- `POST /api/langgraph-agent/chat` - 에이전트와 대화

### 세션 관리
- `GET /api/langgraph-agent/sessions` - 모든 세션 조회
- `GET /api/langgraph-agent/sessions/{session_id}/history` - 세션 히스토리 조회
- `DELETE /api/langgraph-agent/sessions/{session_id}` - 세션 삭제
- `POST /api/langgraph-agent/sessions/{session_id}/clear` - 세션 히스토리 삭제

### 시스템
- `GET /api/langgraph-agent/health` - 에이전트 상태 확인
- `GET /api/langgraph-agent/tools` - 사용 가능한 툴 목록

## 사용 예시

### 1. 기본 대화

```javascript
// 프론트엔드에서 사용
const response = await fetch('/api/langgraph-agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_input: "안녕하세요!",
    session_id: null, // 새 세션 생성
    context: { current_page: "/dashboard" }
  })
});

const data = await response.json();
console.log(data.message); // 에이전트 응답
```

### 2. 툴 사용

```javascript
// 채용 정보 검색
const response = await fetch('/api/langgraph-agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_input: "Python 개발자 채용 정보를 검색해주세요",
    session_id: "existing_session_id"
  })
});
```

## 모듈화 구조

### 1. 설정 관리 (`langgraph_config.py`)

중앙에서 모든 설정을 관리합니다:

```python
from langgraph_config import config

# LLM 설정
print(config.llm_model)  # "gemini-1.5-pro"
print(config.llm_temperature)  # 0.7

# 툴 설정
print(config.available_tools)  # ["search_jobs", "analyze_resume", ...]
```

### 2. 툴 관리 (`langgraph_tools.py`)

새로운 툴을 쉽게 추가할 수 있습니다:

```python
from langgraph_tools import tool_manager

# 새 툴 등록
def my_custom_tool(query: str, context: Dict[str, Any]) -> str:
    return f"커스텀 툴 실행: {query}"

tool_manager.register_tool("my_custom_tool", my_custom_tool)

# 툴 실행
result = tool_manager.execute_tool("my_custom_tool", "테스트 쿼리")
```

### 3. 에이전트 확장

새로운 기능을 추가하려면:

1. `langgraph_config.py`에 설정 추가
2. `langgraph_tools.py`에 툴 구현
3. `langgraph_agent.py`에서 워크플로우 수정 (필요시)

## 다른 프로젝트에서 사용하기

### 1. 파일 복사

필요한 파일들을 새 프로젝트로 복사:

```bash
cp langgraph_agent.py /path/to/new/project/
cp langgraph_router.py /path/to/new/project/
cp langgraph_config.py /path/to/new/project/
cp langgraph_tools.py /path/to/new/project/
```

### 2. 설정 수정

`langgraph_config.py`에서 프로젝트에 맞게 설정을 수정:

```python
class LangGraphConfig(BaseSettings):
    # 프로젝트별 설정으로 수정
    system_message: str = "당신은 [프로젝트명]의 AI 어시스턴트입니다..."
    
    # 새로운 툴 추가
    available_tools: List[str] = [
        "existing_tool_1",
        "existing_tool_2",
        "new_tool_1",  # 새로 추가
        "new_tool_2"   # 새로 추가
    ]
```

### 3. 툴 구현

`langgraph_tools.py`에서 새로운 툴을 구현:

```python
def _new_tool_1(self, query: str, context: Dict[str, Any]) -> str:
    """새로운 툴 1"""
    # 툴 로직 구현
    return "새로운 툴 1 실행 결과"

def _new_tool_2(self, query: str, context: Dict[str, Any]) -> str:
    """새로운 툴 2"""
    # 툴 로직 구현
    return "새로운 툴 2 실행 결과"
```

### 4. 라우터에 추가

FastAPI 앱에 라우터를 추가:

```python
from langgraph_router import router as langgraph_router

app.include_router(langgraph_router)
```

## 프론트엔드 연동

### React 컴포넌트 사용

```jsx
import LangGraphChatbot from './components/LangGraphChatbot';

function App() {
  return (
    <div>
      <h1>내 앱</h1>
      <LangGraphChatbot />
    </div>
  );
}
```

### 헤더에 아이콘 추가

```jsx
import { FiMessageCircle } from 'react-icons/fi';

function Header() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  
  return (
    <header>
      <button onClick={() => setIsChatbotOpen(!isChatbotOpen)}>
        <FiMessageCircle />
      </button>
      {isChatbotOpen && <LangGraphChatbot />}
    </header>
  );
}
```

## 트러블슈팅

### 1. LLM 초기화 실패

```
LLM 초기화 실패: GOOGLE_API_KEY not found
```

**해결방법**: `.env` 파일에 `GOOGLE_API_KEY`를 올바르게 설정하세요.

### 2. 툴 실행 오류

```
툴 실행 중 오류가 발생했습니다: [오류 메시지]
```

**해결방법**: 
1. 툴 함수의 로직을 확인
2. 필요한 의존성이 설치되어 있는지 확인
3. 입력 데이터 형식을 확인

### 3. 세션 관리 오류

```
세션을 찾을 수 없습니다
```

**해결방법**: 
1. 세션 ID가 올바른지 확인
2. 세션이 만료되었는지 확인
3. 새로운 세션을 생성

## 성능 최적화

### 1. 대화 히스토리 제한

```python
# langgraph_config.py
max_conversation_history: int = 10  # 최근 10개 메시지만 유지
```

### 2. 세션 타임아웃

```python
# langgraph_config.py
session_timeout_minutes: int = 30  # 30분 후 세션 만료
```

### 3. LLM 설정 조정

```python
# langgraph_config.py
llm_temperature: float = 0.7  # 응답 창의성 조절
llm_max_tokens: int = 1000    # 최대 토큰 수 제한
```

## 보안 고려사항

1. **API 키 보안**: 환경 변수를 통해 API 키 관리
2. **입력 검증**: 사용자 입력에 대한 적절한 검증
3. **세션 관리**: 세션 타임아웃 및 정기적인 정리
4. **에러 처리**: 민감한 정보가 노출되지 않도록 에러 메시지 관리

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
