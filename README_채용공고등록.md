# 채용공고 등록 시스템

## 📋 개요

채용공고 등록 시스템은 AI 기반 채용 관리 플랫폼의 핵심 기능으로, 다양한 방식으로 채용공고를 생성하고 관리할 수 있는 종합적인 솔루션입니다.

## 🏗️ 시스템 구조

### 백엔드 구조

```
backend/
├── models/
│   └── job_posting.py          # 채용공고 데이터 모델
├── routers/
│   └── job_posting.py          # 채용공고 API 엔드포인트
└── services/
    └── mongo_service.py        # MongoDB 데이터베이스 서비스
```

### 프론트엔드 구조

```
frontend/src/pages/JobPostingRegistration/
├── JobPostingRegistration.js      # 메인 채용공고 관리 페이지
├── AIJobRegistrationPage.js       # AI 기반 채용공고 등록
├── TextBasedRegistration.js       # 텍스트 기반 등록
├── ImageBasedRegistration.js      # 이미지 기반 등록
├── LangGraphJobRegistration.js    # LangGraph 기반 등록
├── EnhancedJobRegistration.js     # 향상된 등록 기능
├── JobDetailModal.js              # 채용공고 상세 모달
├── TemplateModal.js               # 템플릿 선택 모달
└── OrganizationModal.js           # 조직 정보 모달
```

## 🎯 주요 기능

### 1. 다중 등록 방식

#### AI 기반 등록 (AIJobRegistrationPage.js)
- **자동 제목 추천**: AI가 채용 내용을 분석하여 적절한 제목 추천
- **스마트 필드 추출**: 입력된 텍스트에서 자동으로 필드 정보 추출
- **실시간 검증**: 입력 데이터의 유효성 실시간 검증

#### 텍스트 기반 등록 (TextBasedRegistration.js)
- **직접 입력**: 사용자가 직접 모든 필드 입력
- **실시간 미리보기**: 입력한 내용의 실시간 미리보기
- **유효성 검사**: 클라이언트 사이드 유효성 검사

#### 이미지 기반 등록 (ImageBasedRegistration.js)
- **OCR 처리**: 이미지에서 텍스트 추출
- **AI 분석**: 추출된 텍스트의 AI 기반 분석
- **자동 필드 매핑**: 분석 결과를 채용공고 필드에 자동 매핑

#### LangGraph 기반 등록 (LangGraphJobRegistration.js)
- **대화형 등록**: 자연어 대화를 통한 채용공고 생성
- **단계별 가이드**: AI가 단계별로 필요한 정보 요청
- **컨텍스트 인식**: 대화 맥락을 이해한 지능형 등록

### 2. 채용공고 관리 기능

#### 기본 CRUD 작업
- **생성**: 새로운 채용공고 등록
- **조회**: 채용공고 목록 및 상세 조회
- **수정**: 기존 채용공고 정보 수정
- **삭제**: 채용공고 삭제

#### 상태 관리
- **Draft**: 초안 상태
- **Published**: 발행된 상태
- **Closed**: 마감된 상태
- **Expired**: 만료된 상태

#### 통계 및 분석
- **조회수 추적**: 채용공고별 조회수 통계
- **지원자 수**: 각 공고별 지원자 수
- **북마크/공유**: 사용자 참여도 지표

## 📊 데이터 모델

### JobPostingBase 모델

```python
class JobPostingBase(BaseModel):
    # 기본 정보
    title: str                    # 채용공고 제목
    company: str                  # 회사명
    location: str                 # 근무지
    type: JobType                 # 고용 형태 (full-time, part-time, contract, internship)
    
    # 급여 및 조건
    salary: Optional[str]         # 급여 조건
    experience: Optional[str]     # 경력 요구사항
    education: Optional[str]      # 학력 요구사항
    
    # 상세 정보
    description: Optional[str]    # 직무 설명
    requirements: Optional[str]   # 자격 요건
    benefits: Optional[str]       # 복리후생
    deadline: Optional[str]       # 마감일
    
    # 추가 정보
    department: Optional[str]     # 구인 부서
    headcount: Optional[str]      # 채용 인원
    work_type: Optional[str]      # 업무 내용
    work_hours: Optional[str]     # 근무 시간
    contact_email: Optional[str]  # 연락처 이메일
    
    # 분석용 필드
    position: Optional[str]       # 채용 직무
    experience_min_years: Optional[int]  # 최소 경력 연차
    experience_max_years: Optional[int]  # 최대 경력 연차
    experience_level: Optional[str]      # 경력 수준
    main_duties: Optional[str]    # 주요 업무
    job_keywords: List[str]       # 직무 관련 키워드
    industry: Optional[str]       # 산업 분야
    job_category: Optional[str]   # 직무 카테고리
    
    # 지원자 요구 항목
    required_documents: List[RequiredDocumentType]  # 필수 제출 서류
    required_skills: List[str]    # 필수 기술 스택
    preferred_skills: List[str]   # 우선 기술 스택
    skill_weights: Dict[str, float]  # 기술별 가중치
    require_portfolio_pdf: bool   # 포트폴리오 PDF 제출 필수 여부
    require_github_url: bool      # GitHub URL 제출 필수 여부
    require_growth_background: bool  # 성장 배경 작성 필수 여부
    require_motivation: bool      # 지원 동기 작성 필수 여부
    require_career_history: bool  # 경력 사항 작성 필수 여부
    max_file_size_mb: int        # 최대 파일 크기 (MB)
    allowed_file_types: List[str] # 허용된 파일 형식
```

### JobPosting 모델 (확장)

```python
class JobPosting(JobPostingBase):
    id: Optional[str]            # 고유 식별자
    status: JobStatus            # 채용공고 상태
    applicants: int              # 지원자 수
    views: int                   # 조회수
    bookmarks: int               # 북마크 수
    shares: int                  # 공유 수
    created_at: Optional[datetime]  # 생성일시
    updated_at: Optional[datetime]  # 수정일시
```

## 🔌 API 엔드포인트

### 기본 CRUD API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/api/job-postings/` | 새로운 채용공고 생성 |
| GET | `/api/job-postings/` | 채용공고 목록 조회 |
| GET | `/api/job-postings/{job_id}` | 특정 채용공고 조회 |
| PUT | `/api/job-postings/{job_id}` | 채용공고 수정 |
| DELETE | `/api/job-postings/{job_id}` | 채용공고 삭제 |

### 상태 관리 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| PATCH | `/api/job-postings/{job_id}/publish` | 채용공고 발행 |
| PATCH | `/api/job-postings/{job_id}/close` | 채용공고 마감 |

### 통계 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/api/job-postings/stats/overview` | 채용공고 통계 조회 |

## 🎨 사용자 인터페이스

### 메인 관리 페이지 (JobPostingRegistration.js)

#### 주요 컴포넌트
- **헤더**: 제목과 새 채용공고 등록 버튼
- **등록 방식 선택**: AI, 텍스트, 이미지, LangGraph 중 선택
- **채용공고 목록**: 등록된 채용공고들의 카드 형태 표시
- **필터링**: 상태, 회사명별 필터링
- **액션 버튼**: 조회, 수정, 삭제, 발행

#### 상태 표시
- **Draft**: 회색 배경, "초안" 라벨
- **Published**: 녹색 배경, "발행됨" 라벨
- **Closed**: 빨간색 배경, "마감됨" 라벨

### AI 등록 페이지 (AIJobRegistrationPage.js)

#### AI 기능
- **제목 추천**: 입력된 내용 기반 제목 자동 생성
- **필드 자동 완성**: AI가 추천하는 필드 값 제시
- **실시간 검증**: 입력 데이터의 유효성 검사
- **스마트 제안**: 관련 기술 스택 및 키워드 제안

### 텍스트 등록 페이지 (TextBasedRegistration.js)

#### 입력 폼
- **단계별 입력**: 기본 정보 → 상세 정보 → 요구사항 순서
- **실시간 미리보기**: 입력한 내용의 실시간 미리보기
- **유효성 검사**: 필수 필드 및 형식 검증
- **자동 저장**: 임시 저장 기능

## 🔧 기술 스택

### 백엔드
- **FastAPI**: RESTful API 프레임워크
- **MongoDB**: NoSQL 데이터베이스
- **Motor**: 비동기 MongoDB 드라이버
- **Pydantic**: 데이터 검증 및 직렬화
- **Python 3.8+**: 프로그래밍 언어

### 프론트엔드
- **React**: 사용자 인터페이스 라이브러리
- **Styled Components**: CSS-in-JS 스타일링
- **Framer Motion**: 애니메이션 라이브러리
- **React Router**: 클라이언트 사이드 라우팅
- **React Icons**: 아이콘 라이브러리

### AI/ML
- **OpenAI GPT**: 자연어 처리
- **OCR**: 이미지 텍스트 추출
- **LangGraph**: 대화형 AI 프레임워크

## 🚀 설치 및 실행

### 백엔드 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export MONGODB_URI="mongodb://localhost:27017/hireme"
export OPENAI_API_KEY="your-openai-api-key"

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

### 1. AI 기반 등록

1. **등록 방식 선택**: "AI 등록" 버튼 클릭
2. **내용 입력**: 채용하고자 하는 직무에 대한 설명 입력
3. **AI 분석**: 시스템이 자동으로 내용 분석
4. **제목 추천**: AI가 추천하는 제목들 중 선택
5. **필드 확인**: 자동 추출된 필드 정보 확인 및 수정
6. **등록 완료**: 최종 확인 후 등록

### 2. 텍스트 기반 등록

1. **등록 방식 선택**: "텍스트 등록" 버튼 클릭
2. **기본 정보 입력**: 제목, 회사명, 근무지 등 기본 정보
3. **상세 정보 입력**: 직무 설명, 자격 요건, 복리후생 등
4. **요구사항 설정**: 필수 기술, 제출 서류, 파일 제한 등
5. **미리보기**: 입력한 내용 확인
6. **등록**: 최종 등록

### 3. 이미지 기반 등록

1. **등록 방식 선택**: "이미지 등록" 버튼 클릭
2. **이미지 업로드**: 채용공고 이미지 파일 선택
3. **OCR 처리**: 이미지에서 텍스트 자동 추출
4. **AI 분석**: 추출된 텍스트 분석 및 필드 매핑
5. **정보 확인**: 매핑된 정보 확인 및 수정
6. **등록**: 최종 등록

### 4. LangGraph 기반 등록

1. **등록 방식 선택**: "대화형 등록" 버튼 클릭
2. **자연어 입력**: "프론트엔드 개발자를 뽑고 싶어요" 등 자연어로 입력
3. **AI 질문**: AI가 필요한 정보를 단계별로 질문
4. **정보 제공**: 질문에 대한 답변 제공
5. **자동 생성**: AI가 채용공고 자동 생성
6. **확인 및 등록**: 생성된 내용 확인 후 등록

## 🔍 모니터링 및 로깅

### 로그 레벨
- **INFO**: 일반적인 작업 로그
- **WARNING**: 경고 상황
- **ERROR**: 오류 상황
- **DEBUG**: 디버깅 정보

### 주요 로그 포인트
- 채용공고 생성/수정/삭제
- AI 분석 과정
- OCR 처리 결과
- API 호출 성공/실패
- 사용자 액션 추적

## 🧪 테스트

### 백엔드 테스트

```bash
# 단위 테스트
pytest tests/test_job_posting.py

# 통합 테스트
pytest tests/test_integration.py

# API 테스트
pytest tests/test_api.py
```

### 프론트엔드 테스트

```bash
# 단위 테스트
npm test

# E2E 테스트
npm run test:e2e
```

## 🔒 보안

### 데이터 검증
- **입력 검증**: 모든 사용자 입력에 대한 검증
- **XSS 방지**: 크로스 사이트 스크립팅 방지
- **CSRF 보호**: 크로스 사이트 요청 위조 방지
- **SQL 인젝션 방지**: 파라미터화된 쿼리 사용

### 접근 제어
- **인증**: 사용자 인증 시스템
- **권한 관리**: 역할 기반 접근 제어
- **API 보안**: JWT 토큰 기반 인증

## 📈 성능 최적화

### 백엔드 최적화
- **비동기 처리**: FastAPI의 비동기 특성 활용
- **데이터베이스 인덱싱**: MongoDB 인덱스 최적화
- **캐싱**: Redis를 통한 캐싱 구현
- **페이징**: 대용량 데이터 페이징 처리

### 프론트엔드 최적화
- **코드 스플리팅**: React.lazy를 통한 지연 로딩
- **메모이제이션**: React.memo, useMemo, useCallback 활용
- **이미지 최적화**: WebP 포맷 및 압축
- **번들 최적화**: Webpack 최적화 설정

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 채용공고 등록 실패
- **원인**: 필수 필드 누락 또는 형식 오류
- **해결**: 입력 폼의 유효성 검사 메시지 확인

#### 2. AI 분석 실패
- **원인**: OpenAI API 키 오류 또는 네트워크 문제
- **해결**: API 키 설정 및 네트워크 연결 확인

#### 3. 이미지 업로드 실패
- **원인**: 파일 크기 초과 또는 지원하지 않는 형식
- **해결**: 파일 크기 및 형식 제한 확인

#### 4. 데이터베이스 연결 오류
- **원인**: MongoDB 서버 중단 또는 연결 설정 오류
- **해결**: MongoDB 서버 상태 및 연결 문자열 확인

## 📞 지원

### 개발팀 연락처
- **이메일**: dev-team@company.com
- **슬랙**: #job-posting-dev
- **깃허브**: 이슈 트래커 활용

### 문서
- **API 문서**: `/docs` 엔드포인트
- **개발 가이드**: 개발팀 위키
- **사용자 매뉴얼**: 사용자 포털

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 12월  
**담당자**: 개발팀
