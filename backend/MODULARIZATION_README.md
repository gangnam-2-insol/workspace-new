# 이력서/자소서/포트폴리오 모듈화 가이드

## 📁 모듈화된 프로젝트 구조

이 프로젝트는 이력서, 자기소개서, 포트폴리오 관련 기능들을 모듈화하여 관리하기 쉽고 확장 가능한 구조로 재구성되었습니다.

## 🏗️ 백엔드 모듈 구조

```
backend/
├── modules/
│   ├── shared/                    # 공통 모듈
│   │   ├── __init__.py
│   │   ├── models.py             # 공통 모델 (DocumentBase, AnalysisResult 등)
│   │   └── services.py           # 공통 서비스 (BaseService, FileService 등)
│   │
│   ├── resume/                   # 이력서 모듈
│   │   ├── __init__.py
│   │   ├── models.py             # 이력서 관련 모델
│   │   ├── services.py           # 이력서 서비스
│   │   └── router.py             # 이력서 API 라우터
│   │
│   ├── cover_letter/             # 자기소개서 모듈
│   │   ├── __init__.py
│   │   ├── models.py             # 자기소개서 관련 모델
│   │   ├── services.py           # 자기소개서 서비스
│   │   └── router.py             # 자기소개서 API 라우터
│   │
│   └── portfolio/                # 포트폴리오 모듈
│       ├── __init__.py
│       ├── models.py             # 포트폴리오 관련 모델
│       ├── services.py           # 포트폴리오 서비스
│       └── router.py             # 포트폴리오 API 라우터
```

## 🎨 프론트엔드 모듈 구조

```
frontend/src/
├── modules/
│   ├── shared/                   # 공통 모듈
│   │   ├── __init__.js
│   │   ├── api.js               # 공통 API 서비스
│   │   └── utils.js             # 공통 유틸리티 함수
│   │
│   ├── resume/                  # 이력서 모듈
│   │   ├── components/          # 이력서 관련 컴포넌트
│   │   ├── services/            # 이력서 API 서비스
│   │   └── utils/               # 이력서 관련 유틸리티
│   │
│   ├── cover_letter/            # 자기소개서 모듈
│   │   ├── components/          # 자기소개서 관련 컴포넌트
│   │   ├── services/            # 자기소개서 API 서비스
│   │   └── utils/               # 자기소개서 관련 유틸리티
│   │
│   └── portfolio/               # 포트폴리오 모듈
│       ├── components/          # 포트폴리오 관련 컴포넌트
│       ├── services/            # 포트폴리오 API 서비스
│       └── utils/               # 포트폴리오 관련 유틸리티
```

## 🔧 주요 모듈별 기능

### 1. 공통 모듈 (Shared)

#### 백엔드
- **models.py**: 공통 데이터 모델 정의
  - `DocumentBase`: 문서 기본 클래스
  - `AnalysisResult`: 분석 결과 모델
  - `BaseResponse`: 공통 응답 모델
  - `PaginationParams`: 페이지네이션 모델

- **services.py**: 공통 서비스 클래스
  - `BaseService`: 기본 CRUD 서비스
  - `FileService`: 파일 처리 서비스
  - `AnalysisService`: 분석 결과 관리 서비스

#### 프론트엔드
- **api.js**: 공통 API 서비스
  - HTTP 메서드 (GET, POST, PUT, DELETE)
  - 파일 업로드 기능
  - 에러 처리

- **utils.js**: 공통 유틸리티 함수
  - 날짜/파일 크기 포맷팅
  - 점수 계산 및 색상 처리
  - 로컬/세션 스토리지 관리
  - 검증 함수들

### 2. 이력서 모듈 (Resume)

#### 백엔드
- **models.py**: 이력서 관련 모델
  - `ResumeDocument`: 이력서 문서 모델
  - `ResumeAnalysis`: 이력서 분석 결과
  - `ResumeBasicInfo`: 기본 정보 모델
  - `Education`, `Experience`, `Project`: 세부 정보 모델

- **services.py**: 이력서 서비스
  - 이력서 CRUD 작업
  - 이력서 검색 및 비교
  - 통계 조회
  - 분석 결과 저장

- **router.py**: 이력서 API 엔드포인트
  - `/api/resume/upload`: 이력서 업로드
  - `/api/resume/{id}`: 이력서 조회/수정/삭제
  - `/api/resume/search`: 이력서 검색
  - `/api/resume/compare`: 이력서 비교
  - `/api/resume/statistics`: 통계 조회

#### 프론트엔드
- **components/**: 이력서 관련 컴포넌트
- **services/**: 이력서 API 호출 서비스
- **utils/**: 이력서 관련 유틸리티

### 3. 자기소개서 모듈 (Cover Letter)

#### 백엔드
- **models.py**: 자기소개서 관련 모델
  - `CoverLetterDocument`: 자기소개서 문서 모델
  - `CoverLetterAnalysis`: 분석 결과 모델
  - `STARAnalysis`: STAR 분석 모델
  - `JobSuitability`: 직무 적합성 모델

- **services.py**: 자기소개서 서비스
  - 자기소개서 CRUD 작업
  - STAR 분석 처리
  - 문체 및 감정 분석
  - 개선 제안 생성

- **router.py**: 자기소개서 API 엔드포인트
  - `/api/cover-letter/upload`: 업로드
  - `/api/cover-letter/{id}`: 조회/수정/삭제
  - `/api/cover-letter/analyze`: AI 분석
  - `/api/cover-letter/compare`: 비교 분석

#### 프론트엔드
- **components/**: 자기소개서 관련 컴포넌트
- **services/**: 자기소개서 API 호출 서비스
- **utils/**: 자기소개서 관련 유틸리티

### 4. 포트폴리오 모듈 (Portfolio)

#### 백엔드
- **models.py**: 포트폴리오 관련 모델
  - `PortfolioDocument`: 포트폴리오 문서 모델
  - `PortfolioAnalysis`: 분석 결과 모델
  - `PortfolioItem`, `ProjectInfo`: 프로젝트 정보 모델
  - `GitHubIntegration`: GitHub 연동 모델

- **services.py**: 포트폴리오 서비스
  - 포트폴리오 CRUD 작업
  - GitHub 연동
  - 코드 품질 분석
  - 기술 스택 분석

- **router.py**: 포트폴리오 API 엔드포인트
  - `/api/portfolio/upload`: 업로드
  - `/api/portfolio/{id}`: 조회/수정/삭제
  - `/api/portfolio/github-sync`: GitHub 동기화
  - `/api/portfolio/analyze`: 코드 품질 분석

#### 프론트엔드
- **components/**: 포트폴리오 관련 컴포넌트
- **services/**: 포트폴리오 API 호출 서비스
- **utils/**: 포트폴리오 관련 유틸리티

## 🚀 사용 방법

### 1. 백엔드 모듈 사용

```python
# main.py에서 모듈 라우터 등록
from modules.resume.router import router as resume_router
from modules.cover_letter.router import router as cover_letter_router
from modules.portfolio.router import router as portfolio_router

app.include_router(resume_router)
app.include_router(cover_letter_router)
app.include_router(portfolio_router)
```

### 2. 프론트엔드 모듈 사용

```javascript
// 공통 API 서비스 사용
import apiService from '../modules/shared/api';

// 이력서 업로드
const uploadResume = async (file, applicantId) => {
    return await apiService.uploadFile('/api/resume/upload', file, {
        applicant_id: applicantId
    });
};

// 공통 유틸리티 사용
import { formatDate, getScoreColor } from '../modules/shared/utils';
```

## 📊 모듈별 API 엔드포인트

### 이력서 API
- `POST /api/resume/upload` - 이력서 업로드
- `GET /api/resume/{id}` - 이력서 조회
- `PUT /api/resume/{id}` - 이력서 수정
- `DELETE /api/resume/{id}` - 이력서 삭제
- `GET /api/resume/` - 이력서 목록 조회
- `POST /api/resume/search` - 이력서 검색
- `POST /api/resume/compare` - 이력서 비교
- `GET /api/resume/statistics/overview` - 통계 조회
- `POST /api/resume/{id}/analyze` - AI 분석

### 자기소개서 API
- `POST /api/cover-letter/upload` - 자기소개서 업로드
- `GET /api/cover-letter/{id}` - 자기소개서 조회
- `PUT /api/cover-letter/{id}` - 자기소개서 수정
- `DELETE /api/cover-letter/{id}` - 자기소개서 삭제
- `POST /api/cover-letter/analyze` - AI 분석
- `POST /api/cover-letter/compare` - 비교 분석

### 포트폴리오 API
- `POST /api/portfolio/upload` - 포트폴리오 업로드
- `GET /api/portfolio/{id}` - 포트폴리오 조회
- `PUT /api/portfolio/{id}` - 포트폴리오 수정
- `DELETE /api/portfolio/{id}` - 포트폴리오 삭제
- `POST /api/portfolio/github-sync` - GitHub 동기화
- `POST /api/portfolio/analyze` - 코드 품질 분석

## 🔄 모듈 확장 방법

### 1. 새로운 모듈 추가

```bash
# 백엔드 모듈 생성
mkdir backend/modules/new_module
touch backend/modules/new_module/__init__.py
touch backend/modules/new_module/models.py
touch backend/modules/new_module/services.py
touch backend/modules/new_module/router.py

# 프론트엔드 모듈 생성
mkdir frontend/src/modules/new_module
mkdir frontend/src/modules/new_module/components
mkdir frontend/src/modules/new_module/services
mkdir frontend/src/modules/new_module/utils
```

### 2. 모듈별 설정 파일

각 모듈은 자체 설정 파일을 가질 수 있습니다:

```python
# backend/modules/resume/config.py
RESUME_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": [".pdf", ".doc", ".docx", ".txt"],
    "analysis_models": ["gpt-4", "gemini-pro"]
}
```

## 🧪 테스트

각 모듈별로 독립적인 테스트를 작성할 수 있습니다:

```python
# backend/modules/resume/tests/test_models.py
# backend/modules/resume/tests/test_services.py
# backend/modules/resume/tests/test_router.py
```

## 📝 모듈화의 장점

1. **관심사 분리**: 각 모듈이 독립적인 기능을 담당
2. **재사용성**: 공통 기능을 shared 모듈로 분리
3. **확장성**: 새로운 기능 추가가 용이
4. **유지보수성**: 모듈별로 독립적인 개발 및 수정 가능
5. **테스트 용이성**: 모듈별 독립적인 테스트 작성 가능
6. **팀 협업**: 모듈별로 다른 개발자가 담당 가능

## 🔧 다음 단계

1. 각 모듈의 서비스 및 라우터 완성
2. 프론트엔드 컴포넌트 모듈화
3. 모듈별 테스트 코드 작성
4. CI/CD 파이프라인 구성
5. 모듈별 문서화 완성
