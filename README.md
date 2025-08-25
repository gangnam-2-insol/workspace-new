# 🤖 AI 채용 관리 시스템 - 통합 가이드

## 📋 프로젝트 개요

AI 기반 채용 관리 시스템으로, 지능형 채팅봇을 통한 자연어 입력으로 채용공고 작성, 이력서 분석, 포트폴리오 분석 등을 지원합니다. **OpenAI GPT-4o**, **Agent 시스템**, **FastAPI**, **React**를 기반으로 구축된 현대적인 웹 애플리케이션입니다.

## 🚀 주요 기능

### 🎯 1. AI 채용공고 등록 도우미
- **자율모드**: AI가 단계별로 질문하며 자동 입력
- **개별모드**: 사용자가 자유롭게 입력하면 AI가 분석하여 필드 매핑
- **이미지 기반 등록**: AI가 생성한 이미지와 함께 채용공고 작성
- **🧪 테스트 자동입력**: 개발 및 테스트용 샘플 데이터 원클릭 입력

### 🧪 2. Agent 기반 시스템 (테스트중 모드)
- **의도 자동 분류**: 사용자 요청을 "search", "calc", "db", "chat" 중 하나로 자동 분류
- **도구 자동 선택**: 의도에 따라 적절한 도구(검색, 계산, DB 조회, 대화) 자동 선택
- **모듈화된 노드**: 각 도구가 독립적인 노드로 구성되어 확장성과 유지보수성 향상

### 🏷️ 3. AI 제목 추천 시스템
- **4가지 컨셉**: 신입친화형, 전문가형, 일반형, 일반형 변형
- **매번 다른 추천**: 랜덤 시드와 창의성 설정으로 다양한 제목 생성

### 💬 4. 지능형 대화 관리
- **대화 흐름 제어**: 순서가 꼬여도 🔄 처음부터 버튼으로 재시작 가능
- **세션 기반 히스토리**: 24시간 내 대화 기록 자동 복원
- **실시간 필드 업데이트**: 입력과 동시에 폼 필드 자동 반영

### 📝 5. 범용적인 JSON 매핑 시스템
- 채팅 응답을 JSON으로 처리하여 UI 필드에 자동 매핑
- 페이지별 필드 매핑 설정 지원
- 다양한 응답 형식 지원 (extracted_data, field/value, content 내 JSON)

### 📄 6. PDF OCR 및 AI 분석 시스템
- **GPT-4o Vision API**: PDF 문서 자동 텍스트 추출
- **AI 기반 정보 추출**: 이름, 이메일, 연락처, 기술스택 자동 분류
- **다중 문서 지원**: 이력서, 자기소개서, 포트폴리오 자동 감지

### 🔍 7. 고급 검색 및 유사도 분석
- **RAG 시스템**: Retrieval-Augmented Generation 기반 이력서 분석
- **청킹 기반 유사도**: 문서를 의미 단위로 분할하여 정밀한 유사도 계산
- **다중 하이브리드 검색**: 벡터 검색 + 텍스트 검색 + 키워드 검색 융합
- **BM25 키워드 검색**: 한국어 형태소 분석 기반 정확한 키워드 매칭

### 🐙 8. GitHub Test 기능
- **GitHub 프로필 분석**: 사용자 GitHub 활동 분석
- **AI 기반 아키텍처 분석**: 프로젝트 구조 및 기술 스택 자동 추출
- **인터랙티브 차트**: Recharts 기반 데이터 시각화
- **완전자율에이전트**: URL 파라미터로 자동 분석 실행

## 🏗️ 시스템 아키텍처

### 🛠️ 기술 스택
- **Frontend**: React 18, Styled Components, Framer Motion, Chart.js
- **Backend**: FastAPI, Python 3.9+
- **AI Engine**: OpenAI GPT-4o (통일)
- **Database**: MongoDB
- **Vector DB**: Pinecone
- **OCR**: Tesseract + GPT-4o Vision API

### 백엔드 구조 (포트 8000)
```
backend/
├── main.py                          # FastAPI 메인 서버
├── modules/                         # 모듈화된 기능들
│   ├── shared/                      # 공통 모듈
│   ├── resume/                      # 이력서 모듈
│   ├── cover_letter/                # 자기소개서 모듈
│   ├── portfolio/                   # 포트폴리오 모듈
│   └── hybrid/                      # 하이브리드 모듈
├── chatbot/                         # 채팅봇 시스템
├── pdf_ocr_module/                  # PDF OCR 처리
├── routers/                         # API 라우터
├── services/                        # 비즈니스 로직
└── models/                          # 데이터 모델
```

### 프론트엔드 구조 (포트 3001)
```
frontend/src/
├── components/                      # 공통 컴포넌트
│   ├── EnhancedModalChatbot.js     # AI 채팅 컴포넌트
│   ├── DetailedAnalysisModal.js    # 상세 분석 모달
│   └── ...
├── pages/                          # 페이지 컴포넌트
│   ├── JobPostingRegistration/     # 채용공고 등록
│   ├── ApplicantManagement/        # 지원자 관리
│   ├── ResumeManagement/           # 이력서 관리
│   ├── CoverLetterValidation/      # 자기소개서 검증
│   ├── PortfolioAnalysis/          # 포트폴리오 분석
│   ├── PDFOCRPage/                 # PDF OCR 페이지
│   └── TestGithubSummary.js        # GitHub Test 페이지
├── modules/                        # 모듈화된 프론트엔드
│   ├── shared/                     # 공통 모듈
│   └── hybrid/                     # 하이브리드 모듈
└── utils/                          # 유틸리티
```

## 🛠️ 설치 및 실행

### 1. 환경 설정
```bash
# Conda 환경 생성 및 활성화 (Windows)
conda create -n hireme python=3.11
conda activate hireme

# 또는 기존 환경 사용
conda activate hireme

# 프로젝트 클론
git clone <repository-url>
cd workspace-new
```

### 2. 환경변수 설정
```bash
# backend/env 파일 생성
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017
PINECONE_API_KEY=your_pinecone_api_key
POPPLER_PATH=C:\poppler\bin
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 3. 백엔드 서버 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (포트 8000)
cd backend
python main.py
```

### 4. 프론트엔드 실행
```bash
# 의존성 설치
cd frontend
npm install

# 개발 서버 실행 (포트 3001)
npm start
```

### 5. MongoDB 실행 (Docker)
```bash
docker run -d --name mongodb -p 27017:27017 mongo:6.0
```

## 📊 이니셜별 특이사항

### 👤 JR (Junior Developer)
- **담당 영역**: 이력서 분석 시스템, RAG 적용
- **특이사항**:
  - OpenAI GPT-4o 기반 이력서 분석 (업그레이드 완료)
  - Pinecone 벡터 DB 연동
  - 청킹 기반 유사도 분석 시스템
  - BM25 키워드 검색 엔진 구현

### 🧠 KH (Knowledge Hub)
- **담당 영역**: 컨텍스트 분류, Agent 시스템
- **특이사항**:
  - 유연한 컨텍스트 분류 시스템 (Flexible Context Classification)
  - 의도 기반 자동 분류 및 도구 선택
  - 복잡한 보너스 계산 시스템 (조합 가중치, 복잡도 보너스)
  - LangGraph 기반 Agent 워크플로우

### 💼 MJ (Management Junior)
- **담당 영역**: 지원자 관리, 문서 분류
- **특이사항**:
  - 내용 기반 문서 유형 분류 시스템
  - AI 기반 상세 문서 분석 (9개 항목 세분화)
  - 타입 불일치 경고 시스템
  - 고도화된 AI 프롬프트 엔지니어링

### 🎨 YC (Young Creator)
- **담당 영역**: UI/UX, 프론트엔드 개발
- **특이사항**:
  - 4가지 AI 모드 구현 (자율, 개별, 어시스턴트, 테스트중)
  - 실시간 필드 업데이트 및 검증
  - 창의적 제목 추천 시스템 (4가지 컨셉)
  - 모듈화된 컴포넌트 구조

### 🌐 GW (Global Worker)
- **담당 영역**: PDF OCR, AI 통합
- **특이사항**:
  - GPT-4o Vision API 기반 PDF OCR 시스템
  - Tesseract + AI 하이브리드 텍스트 추출
  - 13가지 이름 추출 패턴 시스템
  - 환경변수 최적화 및 서버 실행 자동화

## 🔧 주요 API 엔드포인트

### 채용공고 관리
- `POST /api/chatbot/ai-assistant` - AI 어시스턴트 대화
- `POST /api/chatbot/generate-title` - AI 제목 추천
- `POST /api/chatbot/test-mode-chat` - Agent 기반 테스트 모드

### 지원자 관리
- `GET /api/applicants/` - 지원자 목록 조회
- `POST /api/applicants/` - 새 지원자 생성
- `PUT /api/applicants/{id}/status` - 지원자 상태 변경

### 문서 처리
- `POST /api/upload/analyze` - 문서 업로드 및 AI 분석
- `POST /api/pdf-ocr/upload-pdf` - PDF OCR 처리
- `POST /api/resume/similarity-check/{id}` - 이력서 유사도 분석

### 검색 및 분석
- `POST /api/resume/search/keyword` - BM25 키워드 검색
- `POST /api/resume/search/multi-hybrid` - 다중 하이브리드 검색
- `POST /api/vector/search` - 벡터 유사도 검색

### GitHub Test
- `POST /api/github/analyze` - GitHub 프로필 분석
- `GET /api/github/health` - GitHub API 상태 확인

## 🎯 핵심 장점

1. **🚀 고도화된 AI**: OpenAI GPT-4o 모델로 정확한 자연어 이해
2. **⚡ 실시간 처리**: 입력과 동시에 폼 필드 자동 반영
3. **🎨 창의적 제목**: 매번 다른 4가지 컨셉의 제목 추천
4. **🔄 안정적 대화**: 순서가 꼬여도 쉽게 재시작 가능
5. **🧪 개발 친화적**: 테스트 자동입력으로 빠른 개발/테스트
6. **📱 반응형 UI**: 모바일과 데스크톱 모두 최적화
7. **🔒 세션 관리**: 24시간 대화 기록 보존 및 복원
8. **⚙️ 모듈화**: 컴포넌트 기반으로 쉬운 확장과 유지보수

## 🛠️ 설치 및 실행

### 1. 백엔드 서버 실행 (포트 8000)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. 프론트엔드 실행 (포트 3001)
```bash
cd frontend
npm install
npm start
```

### 3. MongoDB 실행 (Docker)
```bash
docker run -d --name mongodb -p 27017:27017 mongo:6.0
```

## 📊 이니셜별 특이사항

### 👤 **JR** (Junior Developer)
- **담당**: 이력서 분석 시스템, RAG 적용
- **특이사항**: OpenAI GPT-4o 기반 이력서 분석, Pinecone 벡터 DB 연동, 청킹 기반 유사도 분석, BM25 키워드 검색 엔진

### 🧠 **KH** (Knowledge Hub)
- **담당**: 컨텍스트 분류, Agent 시스템
- **특이사항**: 유연한 컨텍스트 분류 시스템, 의도 기반 자동 분류, 복잡한 보너스 계산 시스템, LangGraph 기반 Agent 워크플로우

### 💼 **MJ** (Management Junior)
- **담당**: 지원자 관리, 문서 분류
- **특이사항**: 내용 기반 문서 유형 분류, AI 기반 상세 문서 분석, 타입 불일치 경고 시스템, 고도화된 AI 프롬프트 엔지니어링

### 🎨 **YC** (Young Creator)
- **담당**: UI/UX, 프론트엔드 개발
- **특이사항**: 4가지 AI 모드 구현, 실시간 필드 업데이트, 창의적 제목 추천 시스템, 모듈화된 컴포넌트 구조

### 🌐 **GW** (Global Worker)
- **담당**: PDF OCR, AI 통합
- **특이사항**: GPT-4o Vision API 기반 PDF OCR, Tesseract + AI 하이브리드 텍스트 추출, 13가지 이름 추출 패턴, 환경변수 최적화

## 📈 성능 지표

- **AI 분석 정확도**: 95% 이상 (이름 추출), 98% 이상 (연락처)
- **처리 속도**: 1페이지 PDF 2-3초, AI 분석 3-5초
- **유사도 검색**: 1-2초, 제목 추천 2-3초

## 🎯 실행 후 접속
- **프론트엔드**: http://localhost:3001
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

---

**마지막 업데이트**: 2025년 1월 15일 | **버전**: v3.0 | **메인테이너**: AI Development Team
**주요 개발자**: JR (이력서), KH (Agent), MJ (관리), YC (UI), GW (OCR)
