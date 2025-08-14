# AI 채용 관리 도우미 모듈

채용 관리 시스템에서 사용되는 AI 기반 도우미 모듈입니다. 이 모듈은 채용공고 작성, 면접 관리, 이력서 분석 등을 지원하는 AI 챗봇 기능을 제공합니다.

## 📁 완전한 폴더 구조

```
ai_modules/
├── README.md                    # 이 파일
├── frontend/
│   ├── package.json             # 프론트엔드 의존성 정의
│   └── src/
│       ├── components/          # React 컴포넌트
│       │   ├── FloatingChatbot.js      # 플로팅 AI 챗봇
│       │   └── EnhancedModalChatbot.js # 모달형 AI 챗봇
│       ├── styles/              # 스타일 관련 파일
│       │   └── ChatbotStyles.js       # 챗봇 스타일 정의
│       ├── hooks/               # React 커스텀 훅
│       │   └── useChatbot.js         # 챗봇 로직 훅
│       ├── utils/               # 유틸리티 함수
│       │   └── chatbotUtils.js       # 챗봇 유틸리티
│       └── index.js             # 진입점 (export)
│
└── backend/
    ├── config/                  # 설정 파일
    │   └── settings.py          # 환경 설정
    ├── utils/                   # 유틸리티 함수
    │   ├── __init__.py          # 패키지 초기화
    │   ├── ai_helper.py         # AI 관련 헬퍼 함수
    │   └── chatbot_utils.py     # 챗봇 유틸리티
    ├── chatbot_router.py        # FastAPI 라우터
    └── requirements.txt         # 백엔드 의존성 정의
```

## 🚀 주요 기능

### 1. 플로팅 AI 챗봇 (FloatingChatbot)
- 실시간 AI 대화 기능
- 페이지 컨텍스트 기반 응답
- 자동 추천 및 제안
- 멀티모달 입력 지원 (텍스트/이미지)
- 인라인 스타일 사용 (styled-components 의존성 없음)

### 2. 모달형 AI 챗봇 (EnhancedModalChatbot)
- AI 기반 폼 작성 도우미
- 실시간 필드 검증
- 자동 완성 제안
- 단계별 가이드
- styled-components 기반 스타일링

### 3. 백엔드 AI 서비스
- AI 세션 관리
- 문맥 기반 질문 생성
- 응답 처리 및 분석
- Gemini API 연동
- 유틸리티 함수 제공

## 💻 빠른 시작

### 1. 모듈 복사
```bash
# 프로젝트 루트 디렉토리에 모듈 복사
cp -r ai_modules/ your-project/
```

### 2. 프론트엔드 설정
```bash
# 프론트엔드 의존성 설치
cd your-project/ai_modules/frontend
npm install

# .env 파일 생성 (프로젝트 루트에)
echo "REACT_APP_API_URL=http://localhost:8000" > .env
echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> .env
echo "REACT_APP_AI_MODEL=gemini" >> .env
echo "REACT_APP_MAX_TOKENS=1000" >> .env
echo "REACT_APP_TEMPERATURE=0.7" >> .env
echo "REACT_APP_DEBUG_MODE=false" >> .env
echo "REACT_APP_AUTO_CLOSE_DELAY=3000" >> .env
```

### 3. 백엔드 설정
```bash
# 백엔드 의존성 설치
cd your-project/ai_modules/backend
pip install -r requirements.txt

# .env 파일 생성
echo "GEMINI_API_KEY=your-gemini-api-key-here" > .env
echo "MODEL_NAME=gemini-pro" >> .env
echo "MAX_TOKENS=1000" >> .env
echo "TEMPERATURE=0.7" >> .env
echo "DEBUG=false" >> .env
echo "SECRET_KEY=your-secret-key-here" >> .env
echo 'BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]' >> .env
```

## 📘 상세 사용 방법

### 프론트엔드에서 사용하기

#### 1. 플로팅 챗봇 사용
```jsx
import { FloatingChatbot } from 'ai_modules/frontend';

function App() {
  return (
    <div>
      {/* 기본 사용 */}
      <FloatingChatbot page="dashboard" />
      
      {/* 고급 사용 */}
      <FloatingChatbot 
        page="job-posting"
        onFieldUpdate={(key, value) => {
          console.log('필드 업데이트:', key, value);
        }}
        onComplete={(data) => {
          console.log('완료:', data);
        }}
        onPageAction={(action) => {
          console.log('페이지 액션:', action);
        }}
      />
    </div>
  );
}
```

#### 2. 모달형 챗봇 사용
```jsx
import { EnhancedModalChatbot } from 'ai_modules/frontend';

function JobPostingForm() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({});
  
  const fields = [
    { key: 'title', label: '채용공고 제목', type: 'text', required: true },
    { key: 'department', label: '부서', type: 'text', required: true },
    { key: 'headcount', label: '채용 인원', type: 'number', required: true },
    { key: 'description', label: '상세 설명', type: 'textarea' },
    { key: 'salary', label: '급여', type: 'text' },
    { key: 'location', label: '근무지', type: 'text' }
  ];

  const handleFieldUpdate = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleComplete = (data) => {
    console.log('폼 완료:', data);
    setIsOpen(false);
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>
        AI 도우미로 작성하기
      </button>
      
      <EnhancedModalChatbot
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        fields={fields}
        formData={formData}
        onFieldUpdate={handleFieldUpdate}
        onComplete={handleComplete}
        aiAssistant={true}
        title="AI 채용공고 작성 도우미"
      />
    </div>
  );
}
```

### 백엔드에서 사용하기

#### 1. FastAPI 앱에 통합
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_modules.backend.chatbot_router import router as chatbot_router
from ai_modules.backend.config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 챗봇 라우터 추가
app.include_router(chatbot_router, prefix="/api/chatbot")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. AI 헬퍼 직접 사용
```python
from ai_modules.backend.utils.ai_helper import AIHelper
from ai_modules.backend.config.settings import settings

# AI 헬퍼 초기화
ai_helper = AIHelper(
    api_key=settings.GEMINI_API_KEY,
    model_name=settings.MODEL_NAME
)

# 응답 생성
async def generate_ai_response(prompt: str, context: dict = None):
    response = await ai_helper.generate_response(
        prompt=prompt,
        context=context,
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE
    )
    return response
```

## ⚙️ 환경 변수 설정

### 프론트엔드 (.env)
```env
# API 설정
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# AI 설정
REACT_APP_AI_MODEL=gemini
REACT_APP_MAX_TOKENS=1000
REACT_APP_TEMPERATURE=0.7

# 기타 설정
REACT_APP_DEBUG_MODE=false
REACT_APP_AUTO_CLOSE_DELAY=3000
```

### 백엔드 (.env)
```env
# AI 설정
GEMINI_API_KEY=your-gemini-api-key-here
MODEL_NAME=gemini-pro
MAX_TOKENS=1000
TEMPERATURE=0.7

# 서버 설정
DEBUG=false
SECRET_KEY=your-secret-key-here

# CORS 설정
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

## 🔧 커스터마이징

### 1. 스타일 커스터마이징
```jsx
// ChatbotStyles.js 파일을 복사하여 수정
import { ChatContainer, ChatButton } from 'ai_modules/frontend/src/styles/ChatbotStyles';
import styled from 'styled-components';

export const CustomChatContainer = styled(ChatContainer)`
  // 커스텀 스타일 추가
  background-color: #your-color;
  border-radius: 20px;
`;
```

### 2. AI 로직 커스터마이징
```python
# ai_helper.py 파일을 복사하여 수정
from ai_modules.backend.utils.ai_helper import AIHelper

class CustomAIHelper(AIHelper):
    async def generate_response(self, prompt, context=None):
        # 커스텀 로직 구현
        custom_prompt = self._build_custom_prompt(prompt, context)
        return await self._call_custom_api(custom_prompt)
```

### 3. 유틸리티 함수 확장
```javascript
// chatbotUtils.js에 새로운 함수 추가
export const customKeywordExtractor = (text) => {
  // 커스텀 키워드 추출 로직
  return extractKeywords(text).filter(keyword => 
    keyword.length > 2
  );
};
```

## 🔒 보안 고려사항

### 1. API 키 관리
- Gemini API 키는 반드시 환경 변수로 관리
- 프론트엔드에 API 키 노출 금지
- 프로덕션 환경에서는 키 로테이션 고려

### 2. CORS 설정
- 프로덕션 환경에서는 허용된 도메인만 설정
- `BACKEND_CORS_ORIGINS` 설정 필수
- 개발/프로덕션 환경별 설정 분리

### 3. 입력 검증
- 모든 사용자 입력에 대한 검증 필수
- XSS 공격 방지를 위한 입력 정리
- SQL 인젝션 방지 (백엔드)

### 4. 웹소켓 보안
- 인증된 사용자만 접근 가능하도록 설정
- 메시지 암호화 고려
- 연결 상태 모니터링

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 모듈을 찾을 수 없음
```bash
# 의존성 재설치
cd ai_modules/frontend && npm install
cd ai_modules/backend && pip install -r requirements.txt
```

#### 2. API 연결 실패
```bash
# 백엔드 서버 실행 확인
cd ai_modules/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 스타일이 적용되지 않음
```jsx
// styled-components 설치 확인
npm install styled-components

// 또는 인라인 스타일 사용
<div style={{ backgroundColor: '#667eea' }}>
```

#### 4. 환경 변수 문제
```bash
# .env 파일이 올바른 위치에 있는지 확인
# 프로젝트 루트에 .env 파일 생성
touch .env

# 환경 변수 설정
echo "REACT_APP_API_URL=http://localhost:8000" >> .env
echo "GEMINI_API_KEY=your-api-key" >> .env
```

#### 5. 백엔드 서버 시작 실패
```bash
# 필요한 패키지 설치 확인
pip install fastapi uvicorn python-dotenv

# 서버 시작
cd ai_modules/backend
python -m uvicorn chatbot_router:app --reload --host 0.0.0.0 --port 8000
```

## ✅ 설치 확인 체크리스트

### 프론트엔드
- [ ] ai_modules/frontend 폴더가 프로젝트에 복사됨
- [ ] npm install 실행 완료
- [ ] .env 파일 생성 및 환경 변수 설정
- [ ] 컴포넌트 import 테스트

### 백엔드
- [ ] ai_modules/backend 폴더가 프로젝트에 복사됨
- [ ] pip install -r requirements.txt 실행 완료
- [ ] .env 파일 생성 및 API 키 설정
- [ ] FastAPI 서버 시작 테스트

### 통합 테스트
- [ ] 프론트엔드에서 챗봇 컴포넌트 렌더링
- [ ] 백엔드 API 연결 테스트
- [ ] AI 응답 기능 테스트
- [ ] 스타일 적용 확인

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.