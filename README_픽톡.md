# 픽톡 (Pick Chatbot) 시스템

## 📋 개요

픽톡은 AI 기반 채용 관리 플랫폼의 지능형 챗봇 시스템으로, 사용자의 자연어 요청을 이해하고 적절한 도구를 자동으로 실행하여 채용 관리 업무를 효율적으로 처리하는 종합적인 AI 어시스턴트입니다.

## 🏗️ 시스템 구조

### 백엔드 구조

```
backend/
├── routers/
│   └── pick_chatbot.py           # 픽톡 API 엔드포인트
├── chatbot/
│   ├── core/
│   │   ├── agent_system.py       # 에이전트 시스템 핵심
│   │   ├── context_classifier.py # 컨텍스트 분류기
│   │   ├── intent_classifier.py  # 의도 분류기
│   │   ├── field_extractor.py    # 필드 추출기
│   │   ├── response_generator.py # 응답 생성기
│   │   └── suggestion_generator.py # 제안 생성기
│   ├── models/
│   │   ├── agent_models.py       # 에이전트 데이터 모델
│   │   ├── request_models.py     # 요청 모델
│   │   └── response_models.py    # 응답 모델
│   ├── services/
│   │   ├── ai_service.py         # AI 서비스
│   │   ├── field_service.py      # 필드 서비스
│   │   └── session_service.py    # 세션 관리 서비스
│   └── utils/
│       ├── field_mapper.py       # 필드 매핑 유틸리티
│       ├── text_processor.py     # 텍스트 처리 유틸리티
│       └── validation.py         # 검증 유틸리티
└── services/
    ├── llm_service.py            # LLM 서비스
    ├── openai_service.py         # OpenAI 서비스
    └── mongo_service.py          # MongoDB 서비스
```

### 프론트엔드 구조

```
frontend/src/
├── components/
│   └── NewPickChatbot.js         # 픽톡 메인 컴포넌트
├── services/
│   └── pickChatbotApi.js         # 픽톡 API 클라이언트
└── pages/
    └── Demo/
        └── ConversationalAIDemo.js # 대화형 AI 데모 페이지
```

## 🎯 주요 기능

### 1. 지능형 대화 시스템

#### 자연어 이해
- **의도 분류**: 사용자 메시지의 의도를 자동으로 분류
- **컨텍스트 인식**: 대화 맥락을 이해한 연속적인 대화 지원
- **다국어 지원**: 한국어 중심의 자연어 처리

#### 도구 자동 실행
- **GitHub 분석**: GitHub 사용자명 추출 및 포트폴리오 분석
- **페이지 네비게이션**: 시스템 내 페이지 자동 이동
- **채용공고 등록**: AI 기반 채용공고 자동 생성
- **지원자 관리**: 지원자 정보 조회 및 관리

### 2. 세션 관리

#### 대화 세션
- **세션 생성**: 고유한 대화 세션 ID 생성
- **대화 기록**: 세션별 대화 히스토리 저장
- **컨텍스트 유지**: 세션 내 대화 맥락 유지
- **세션 만료**: 자동 세션 정리 및 만료 처리

#### 상태 관리
- **사용자 상태**: 사용자의 현재 상태 및 선호도 추적
- **도구 사용 기록**: 사용된 도구 및 결과 기록
- **에러 처리**: 오류 상황에 대한 적절한 응답

### 3. AI 기반 분석

#### GitHub 포트폴리오 분석
- **사용자명 추출**: 메시지에서 GitHub 사용자명 자동 추출
- **프로필 분석**: GitHub 프로필 정보 분석
- **레포지토리 분석**: 주요 프로젝트 및 기술 스택 분석
- **활동 분석**: 커밋 패턴 및 기여도 분석

#### 채용공고 생성
- **필드 추출**: 자연어에서 채용공고 필드 자동 추출
- **제목 생성**: AI 기반 채용공고 제목 자동 생성
- **내용 완성**: 누락된 정보에 대한 스마트 제안
- **유효성 검사**: 생성된 내용의 자동 검증

## 📊 데이터 모델

### AgentRequest 모델

```python
@dataclass
class AgentRequest:
    """에이전트 시스템의 요청 데이터"""
    user_input: str                    # 사용자 입력 메시지
    conversation_history: List[Dict[str, Any]]  # 대화 히스토리
    session_id: Optional[str] = None   # 세션 ID
    context: Optional[Dict[str, Any]] = None  # 추가 컨텍스트
```

### AgentOutput 모델

```python
@dataclass
class AgentOutput:
    """에이전트 시스템의 출력 데이터"""
    success: bool                      # 성공 여부
    response: str                      # 응답 메시지
    intent: str                        # 감지된 의도
    confidence: float = 0.0            # 신뢰도
    extracted_fields: Optional[Dict[str, Any]] = None  # 추출된 필드
    session_id: Optional[str] = None   # 세션 ID
```

### ChatMessage 모델

```python
class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    message: str                       # 메시지 내용
    session_id: Optional[str] = None   # 세션 ID
    timestamp: Optional[datetime] = None  # 타임스탬프
```

### ChatResponse 모델

```python
class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool                      # 성공 여부
    message: str                       # 응답 메시지
    mode: str                          # 응답 모드 (chat/tool/action)
    tool_used: Optional[str] = None    # 사용된 도구
    confidence: float = 0.0            # 신뢰도
    session_id: Optional[str] = None   # 세션 ID
    quick_actions: Optional[List[Dict[str, Any]]] = None  # 빠른 액션
    error_info: Optional[Dict[str, Any]] = None  # 오류 정보
```

## 🔌 API 엔드포인트

### 기본 채팅 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/pick-chatbot/chat` | 픽톡과 대화 |

### 세션 관리 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/pick-chatbot/session/{session_id}` | 세션 정보 조회 |
| DELETE | `/pick-chatbot/session/{session_id}` | 세션 삭제 |

### 도구 실행 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/pick-chatbot/tools/github` | GitHub 분석 도구 |
| POST | `/pick-chatbot/tools/navigate` | 페이지 네비게이션 |
| POST | `/pick-chatbot/tools/job-posting` | 채용공고 생성 |

## 🎨 사용자 인터페이스

### 메인 챗봇 컴포넌트 (NewPickChatbot.js)

#### 주요 기능
- **플로팅 버튼**: 우하단에 고정된 챗봇 버튼
- **채팅 창**: 확장/축소 가능한 채팅 인터페이스
- **메시지 표시**: 사용자/AI 메시지 구분 표시
- **로딩 상태**: AI 처리 중 로딩 애니메이션
- **빠른 액션**: 자주 사용하는 기능의 빠른 액션 버튼

#### UI 특징
- **그라데이션 헤더**: 시각적으로 매력적인 헤더 디자인
- **메시지 버블**: 사용자/AI 메시지 구분된 버블 디자인
- **애니메이션**: 부드러운 전환 애니메이션
- **반응형**: 모바일/데스크톱 반응형 디자인

### 대화형 AI 데모 (ConversationalAIDemo.js)

#### 데모 기능
- **실시간 대화**: 실제 픽톡과의 대화 시연
- **도구 실행**: GitHub 분석, 페이지 이동 등 도구 실행
- **결과 표시**: 도구 실행 결과의 시각적 표시
- **코드 하이라이팅**: GitHub 코드의 구문 강조

## 🔧 기술 스택

### 백엔드
- **FastAPI**: RESTful API 프레임워크
- **OpenAI GPT**: 자연어 처리 및 대화 생성
- **Selenium**: 웹 자동화 및 페이지 네비게이션
- **MongoDB**: 대화 기록 및 세션 저장
- **Python 3.8+**: 프로그래밍 언어

### 프론트엔드
- **React**: 사용자 인터페이스 라이브러리
- **Styled Components**: CSS-in-JS 스타일링
- **Framer Motion**: 애니메이션 라이브러리
- **React Icons**: 아이콘 라이브러리
- **SessionStorage**: 클라이언트 사이드 세션 저장

### AI/ML
- **OpenAI GPT-4**: 고급 자연어 처리
- **컨텍스트 분류기**: 사용자 의도 분류
- **필드 추출기**: 구조화된 데이터 추출
- **응답 생성기**: 자연스러운 응답 생성

## 🚀 설치 및 실행

### 백엔드 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY="your-openai-api-key"
export MONGODB_URI="mongodb://localhost:27017/hireme"
export FRONTEND_URL="http://localhost:3001"

# Selenium WebDriver 설치 (Chrome)
# ChromeDriver는 시스템에 맞는 버전 설치 필요

# 서버 실행
python main.py
```

### 프론트엔드 설정

```bash
# 의존성 설치
npm install

# 환경 변수 설정
REACT_APP_API_URL=http://localhost:8000

# 개발 서버 실행
npm start
```

## 📝 사용법

### 1. 기본 대화

1. **챗봇 시작**: 우하단 픽톡 버튼 클릭
2. **메시지 입력**: 자연어로 질문이나 요청 입력
3. **AI 응답**: 픽톡이 적절한 응답 제공
4. **대화 지속**: 연속적인 대화 가능

### 2. GitHub 분석

1. **사용자명 제공**: "john_doe의 GitHub 분석해줘" 입력
2. **자동 추출**: 픽톡이 사용자명 자동 추출
3. **프로필 분석**: GitHub 프로필 정보 분석
4. **결과 표시**: 분석 결과를 구조화된 형태로 표시

### 3. 페이지 네비게이션

1. **페이지 요청**: "채용공고 등록 페이지로 이동해줘" 입력
2. **자동 이동**: 픽톡이 해당 페이지로 자동 이동
3. **상태 확인**: 이동 완료 후 확인 메시지

### 4. 채용공고 생성

1. **채용 요청**: "프론트엔드 개발자를 뽑고 싶어요" 입력
2. **정보 수집**: 픽톡이 필요한 정보 질문
3. **자동 생성**: AI가 채용공고 자동 생성
4. **확인 및 저장**: 생성된 내용 확인 후 저장

## 🔍 모니터링 및 로깅

### 로그 레벨
- **INFO**: 일반적인 대화 및 도구 실행 로그
- **WARNING**: 경고 상황 (도구 실행 실패 등)
- **ERROR**: 오류 상황 (API 오류, 네트워크 오류 등)
- **DEBUG**: 디버깅 정보 (의도 분류, 필드 추출 과정 등)

### 주요 로그 포인트
- 사용자 메시지 수신
- 의도 분류 결과
- 도구 실행 시작/완료
- AI 응답 생성
- 세션 생성/만료
- 오류 발생 및 처리

### 성능 모니터링
- **응답 시간**: 메시지 처리 시간 측정
- **도구 실행 시간**: 각 도구별 실행 시간
- **AI 호출 횟수**: OpenAI API 호출 통계
- **세션 수**: 동시 활성 세션 수

## 🧪 테스트

### 백엔드 테스트

```bash
# 단위 테스트
pytest tests/test_agent_system.py
pytest tests/test_context_classifier.py
pytest tests/test_field_extractor.py

# 통합 테스트
pytest tests/test_pick_chatbot_integration.py

# API 테스트
pytest tests/test_pick_chatbot_api.py
```

### 프론트엔드 테스트

```bash
# 단위 테스트
npm test -- --testPathPattern=NewPickChatbot

# 컴포넌트 테스트
npm test -- --testPathPattern=pickChatbotApi

# E2E 테스트
npm run test:e2e -- --spec="cypress/integration/pick-chatbot.spec.js"
```

### AI 모델 테스트

```bash
# 의도 분류 테스트
python -m pytest tests/test_intent_classification.py

# 필드 추출 테스트
python -m pytest tests/test_field_extraction.py

# 응답 생성 테스트
python -m pytest tests/test_response_generation.py
```

## 🔒 보안

### 데이터 보호
- **개인정보 보호**: GitHub 사용자 정보의 안전한 처리
- **세션 보안**: 세션 ID의 암호화 및 안전한 관리
- **API 보안**: OpenAI API 키의 안전한 관리
- **입력 검증**: 모든 사용자 입력의 검증 및 필터링

### 접근 제어
- **세션 기반 인증**: 세션별 접근 제어
- **도구 실행 권한**: 도구별 실행 권한 관리
- **API 제한**: OpenAI API 호출 제한 및 모니터링

## 📈 성능 최적화

### 백엔드 최적화
- **비동기 처리**: FastAPI의 비동기 특성 활용
- **캐싱**: 자주 사용되는 응답의 캐싱
- **배치 처리**: 여러 도구의 배치 실행
- **연결 풀링**: 데이터베이스 연결 풀링

### 프론트엔드 최적화
- **메시지 가상화**: 대량 메시지의 가상 스크롤
- **이미지 지연 로딩**: 이미지의 지연 로딩
- **메모이제이션**: 컴포넌트 및 함수 메모이제이션
- **번들 최적화**: 코드 스플리팅 및 트리 쉐이킹

### AI 모델 최적화
- **프롬프트 최적화**: 효율적인 프롬프트 설계
- **응답 캐싱**: 유사한 질문에 대한 응답 캐싱
- **모델 선택**: 작업에 적합한 모델 선택
- **배치 처리**: 여러 요청의 배치 처리

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 챗봇 응답 없음
- **원인**: OpenAI API 키 오류 또는 네트워크 문제
- **해결**: API 키 설정 및 네트워크 연결 확인

#### 2. GitHub 분석 실패
- **원인**: 사용자명 추출 실패 또는 GitHub API 오류
- **해결**: 사용자명 명확히 입력 및 GitHub 접근 확인

#### 3. 페이지 이동 실패
- **원인**: Selenium WebDriver 오류 또는 페이지 로딩 실패
- **해결**: ChromeDriver 버전 확인 및 페이지 URL 확인

#### 4. 세션 오류
- **원인**: 세션 만료 또는 데이터베이스 연결 오류
- **해결**: 새 세션 생성 및 데이터베이스 연결 확인

#### 5. 메모리 부족
- **원인**: 대화 기록 누적 또는 이미지 처리 과부하
- **해결**: 세션 정리 및 메모리 사용량 모니터링

### 디버깅 도구

#### 로그 분석
```bash
# 실시간 로그 모니터링
tail -f logs/pick_chatbot.log

# 오류 로그 필터링
grep "ERROR" logs/pick_chatbot.log

# 성능 로그 분석
grep "response_time" logs/pick_chatbot.log
```

#### API 테스트
```bash
# 챗봇 API 테스트
curl -X POST "http://localhost:8000/pick-chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요", "session_id": "test-session"}'
```

#### 브라우저 개발자 도구
- **Network 탭**: API 호출 모니터링
- **Console 탭**: JavaScript 오류 확인
- **Application 탭**: SessionStorage 상태 확인

## 📞 지원

### 개발팀 연락처
- **이메일**: ai-team@company.com
- **슬랙**: #pick-chatbot-dev
- **깃허브**: 이슈 트래커 활용

### 문서
- **API 문서**: `/docs` 엔드포인트
- **개발 가이드**: 개발팀 위키
- **사용자 매뉴얼**: 사용자 포털

### 커뮤니티
- **개발자 포럼**: 기술적 질문 및 토론
- **사용자 그룹**: 사용자 피드백 및 제안
- **기여 가이드**: 오픈소스 기여 방법

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 12월  
**담당자**: AI 개발팀
