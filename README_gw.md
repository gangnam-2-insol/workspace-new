## HireMe 프로젝트 운영 가이드 (통합 README)

이 문서는 기존 README/README2 내용을 통합하고, 현재 작업 상태(의존성 경량화, AI 한글 이름 우선 추출, 정리 스크립트 추가)를 반영한 최신 실행/운영 지침입니다.

### 현재 상태 요약
- 백엔드: FastAPI + Uvicorn (포트 8000), MongoDB 연결 확인됨
- 프론트: 메인(3000), 관리자(3001) 정상 기동 가능 (프론트 코드는 변경하지 않음)
- AI: Groq LLM 사용(GROQ_API_KEY 필요). PDF 업로드 시 한글 이름을 AI로 최우선 추출하도록 개선됨
- 최적화: 무거운 패키지(torch/opencv/scikit-image 등) 제거, 임베딩 폴백(경량) 추가, 정리 스크립트/확장된 .gitignore 추가

---

### 1) 필수 요건
- Git, Node.js LTS(>= 18), npm
- Python 3.11 (권장)
- MongoDB Community Server (로컬 27017)
- OCR
  - Tesseract OCR (Windows 설치 후 실행 경로 필요)
  - Poppler (Windows는 bin 경로 필요)

설치 참고
- Tesseract: `https://tesseract-ocr.github.io/tessdoc/Installation.html`
- Poppler(Windows): `https://github.com/oschwartz10612/poppler-windows/releases`

---

### 2) 저장소 클론
```bash
git clone <YOUR_REPO_URL>
cd workspace
```

---

### 3) 환경 변수(.env)
환경파일 위치: `admin/backend/.env`

필수 예시
```env
# 디렉터리
DATA_DIR=data
UPLOADS_DIR=data/uploads
IMAGES_DIR=data/images
RESULTS_DIR=data/results

# OCR
OCR_LANG=kor+eng
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe   # Windows 예시
POPPLER_PATH=C:\\tools\\poppler\\Library\\bin                 # Windows 예시

# 서버
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pdf_ocr
MONGODB_COLLECTION=documents
DATABASE_NAME=hireme

# LLM (Groq 사용)
LLM_PROVIDER=groq
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=llama-3.1-70b-versatile

# (선택) OpenAI
OPENAI_MODEL=gpt-4o-mini

# CORS (필요 시)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

주의
- 백엔드는 `admin/backend/.env`만 로드합니다.
- 한글 PDF OCR은 `OCR_LANG=kor+eng` 권장입니다.

---

### 4) 백엔드 설치 및 실행
Windows (PowerShell)
```powershell
cd admin/backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
Mac/Linux (bash)
```bash
cd admin/backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

헬스 체크
```bash
curl http://localhost:8000/health
```

샘플 데이터(선택)
```powershell
cd admin/backend
python .\init_data.py
```

---

### 5) 프론트엔드 실행 (코드 변경 없음)
메인 UI (3000)
```bash
cd frontend
npm ci --no-audit --no-fund
npm start
```
관리자 UI (3001)
```bash
cd admin/frontend
npm ci --no-audit --no-fund
npm start
```

접속
- 메인: `http://localhost:3000`
- 관리자: `http://localhost:3001`
- API: `http://localhost:8000/health`

---

### 6) PDF 업로드 → OCR/색인/지원자 자동 생성
엔드포인트: `POST http://localhost:8000/api/pdf/upload`
- form-data: key=`file`, value=PDF

업로드 시 처리
- PDF→이미지 변환(Poppler)→OCR(Tesseract) & 내장텍스트 병합
- 요약/키워드(옵션) 및 임베딩(경량 폴백 제공) 생성
- `pdf_ocr.documents/pages` 저장, `hireme.applicant`/`hireme.applicants` 자동 생성

한글 이름 추출 정책 (개선)
- AI(Groq)로 한국어 이름(2~4자)을 최우선 추출
- 실패 시 정규식 기반(라벨/문서 초반) 시도
- 이메일 로컬파트로 이름을 유추하지 않고, 끝까지 없으면 “미상” 사용

---

### 7) 주요 API
- 헬스 체크: `GET /health`
- 지원자: `GET /api/applicants?skip=0&limit=20`, `GET /api/applicants/{id}`, `POST /api/applicants`, `PUT /api/applicants/{id}`
- 상태 변경: `PUT /api/applicants/{id}/status`
- 통계: `GET /api/applicants/stats/overview`
- OCR 문서를 카드 형태로: `GET /api/pdf/documents/applicants`

캐시
- 지원자 목록/통계는 서버 측 5분 캐시(캐시 키: skip/limit/status/position)
- 생성/수정/업로드 시 캐시 무효화됨

---

### 8) 경량화/최적화
- 무거운 패키지 제거: torch, scikit-image, opencv, pinecone 등 제거(필요 시 추후 복구)
- OpenCV 제거 → NumPy/Pillow 기반 전처리로 대체
- 임베딩 폴백: sentence-transformers 미설치 시 해시 기반 임베딩으로 동작
- .gitignore 확장: `node_modules`, `build`, 업로드/이미지/결과, `.venv`, `vector_db` 등 Git 제외
- 정리 스크립트: `cleanup.ps1`
  - DryRun: `powershell -ExecutionPolicy Bypass -File cleanup.ps1 -DryRun`
  - 실행: `powershell -ExecutionPolicy Bypass -File cleanup.ps1`

주의
- Pinecone 등 외부 VectorDB는 기본 비활성. 필요 시 의존성 복구 및 키 설정 후 사용

---

### 9) 자주 겪는 이슈
- PyMuPDF 빌드/호환: Python 3.11 권장
- Tesseract/Poppler 미설치: OCR 품질 저하 → 경로/설치 확인
- 포트 충돌: 8000/3000/3001 점유 시 종료 후 재시작
- MongoDB 미가동: API/목록 비노출 → 27017 가동 확인
- PowerShell 업로드 이슈: curl/Postman 사용 권장

---

### 10) 데이터/디렉터리
- 샘플/업로드: `admin/backend/data/uploads/`
- 썸네일: `admin/backend/data/images/`
- OCR 메타(JSON): `admin/backend/data/results/`

---

### 11) 변경 이력(핵심)
- Groq 기반 한글 이름 우선 추출 적용
- 백엔드 경량화(의존성/전처리/임베딩 폴백)
- 정리 스크립트 및 .gitignore 확장
- 프론트는 변경 없음

---

### 부록) 기존 COMBINED_README 통합 안내
- 기존 `COMBINED_README.md`에 흩어져 있던 실행/구성/엔드포인트/흐름 설명을 본 문서 각 절(1~11)에 재구성해 통합했습니다.
- 중복/노후 내용은 제거하고, 현 프로젝트 상태(경량화/AI 이름 추출/정리 스크립트) 기준으로 최신화했습니다.
- 필요 시 추가 상세 섹션이 요구되면 본 문서에 보강하겠습니다.

## 프로젝트 실행 가이드 (Windows/Mac/Linux)

이 문서는 다른 컴퓨터에서 본 프로젝트를 새로 실행할 때 필요한 전체 절차를 요약합니다.

### 1) 필수 요건 설치

- Git, Node.js LTS(>= 18), npm
- Python 3.11 (권장: 3.11 사용. 3.13은 PyMuPDF 빌드 이슈가 발생할 수 있음)
- MongoDB Community Server (로컬 27017 기본 포트)
- OCR 고정밀을 원할 경우
  - Tesseract OCR (Windows 설치 후 경로 필요)
  - Poppler (Windows는 bin 경로 필요)

참고 링크 (설치 안내)
- Tesseract: `https://tesseract-ocr.github.io/tessdoc/Installation.html`
- Poppler (Windows builds): `https://github.com/oschwartz10612/poppler-windows/releases`

### 2) 저장소 클론

```bash
git clone <YOUR_REPO_URL>
cd workspace
```

이 문서는 저장소 루트(여기) 기준 경로를 사용합니다.

### 3) 백엔드(.env) 설정

환경파일 위치는 `admin/backend/.env` 입니다. 아래 예시를 그대로 복사/수정해 사용하세요.

```env
# 디렉터리
DATA_DIR=data
UPLOADS_DIR=data/uploads
IMAGES_DIR=data/images
RESULTS_DIR=data/results

# OCR
OCR_LANG=kor+eng
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe   # Windows 예시 (Mac/Linux는 생략)
POPPLER_PATH=C:\\tools\\poppler\\Library\\bin                 # Windows 예시

# 서버
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pdf_ocr
MONGODB_COLLECTION=documents

# 임베딩/인덱싱
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=800
CHUNK_OVERLAP=200
MIN_CHUNK_CHARS=20
INDEX_GENERATE_SUMMARY=true
INDEX_GENERATE_KEYWORDS=true

# LLM (Groq 사용)
LLM_PROVIDER=groq
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=llama-3.1-70b-versatile

# (선택) OpenAI
OPENAI_MODEL=gpt-4o-mini

# CORS 허용 (필요 시)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

주의
- 백엔드는 `admin/backend/.env`만을 로드합니다. 다른 경로에 `.env`가 있어도 사용되지 않습니다.
- 한글 PDF OCR은 `OCR_LANG=kor+eng` 권장입니다.

### 4) 백엔드 설치 및 실행

Windows (PowerShell):
```powershell
cd admin/backend
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Mac/Linux (bash):
```bash
cd admin/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

샘플 데이터 삽입(선택):
```powershell
cd admin/backend
.\.venv\Scripts\python .\init_data.py
```

헬스 체크:
```bash
curl http://localhost:8000/health
```

### 5) 프론트엔드 실행

메인 UI (포트 3000):
```bash
cd frontend
npm ci --no-audit --no-fund
npm start
```

관리자 UI (포트 3001):
```bash
cd admin/frontend
npm ci --no-audit --no-fund
npm start
```

### 6) 동작 확인

- 메인 UI: `http://localhost:3000`
- 관리자 UI: `http://localhost:3001`
- API 헬스: `http://localhost:8000/health`
- 지원자 목록: `http://localhost:8000/api/applicants?skip=0&limit=20`

### 7) PDF 업로드 (OCR/인덱싱/지원자 자동생성)

엔드포인트: `POST http://localhost:8000/api/pdf/upload`
- form-data: key=`file`, value=PDF 파일
- 업로드 후:
  - `pdf_ocr.documents`에 문서 저장(요약/키워드 옵션 적용)
  - `hireme.applicant` 및 `hireme.applicants`에 동일 포맷으로 지원자 자동 생성
  - 프론트는 업로드 직후 목록을 재로딩하며, 추가된 카드가 즉시 표시됨

OCR 문서를 지원자 카드로 항상 노출하고 싶다면:
- 백엔드: `GET /api/pdf/documents/applicants` 제공
- 프론트: 목록 로딩 시 API 결과와 병합 (이미 반영됨)

### 8) 자주 겪는 이슈

- PyMuPDF 빌드 오류: Python 3.13 + Windows에서 Visual Studio 빌드툴 요구. Python 3.11 사용 권장
- Tesseract/Poppler 미설치: OCR 정확도가 낮아짐. Windows는 환경변수 또는 `.env` 경로 지정 필요
- 포트 충돌: 8000/3000/3001 점유 시 다른 포트 사용 또는 기존 프로세스 종료
- MongoDB 미가동: 서비스가 정상 작동하지 않음. 로컬 MongoDB가 27017에서 실행 중인지 확인

### 9) 환경 요약(필수)

- Python: 3.11
- Node.js: LTS 18 이상
- MongoDB: 6.x 이상 (로컬 27017)
- `.env` 위치: `admin/backend/.env`
- 필수 변수: `MONGODB_URI`, `OCR_LANG`, `LLM_PROVIDER`, (`GROQ_API_KEY` 또는 OpenAI/Gemini 키)

### 10) 테스트 파일/샘플 위치

- 샘플 PDF: `admin/backend/data/uploads/`
- OCR 결과 썸네일: `admin/backend/data/images/`
- OCR 메타 저장(JSON 스냅샷): `admin/backend/data/results/`

### 11) 종료/재시작 팁

- 백엔드 재시작 시 변경사항 즉시 반영(uvicorn 재실행)
- 업로드 후 목록 캐시는 자동 무효화되도록 처리됨 (즉시 반영)




---
## Appendix: Imported from README.md (20250812_184511)

# AI 채용 관리 시스템

SNOW와 NAVER 채용 사이트를 참고하여 개발한 AI 기반 채용 관리 시스템입니다.

## 🚀 프로젝트 개요

### 목적
- AI 기술을 활용한 스마트한 채용 프로세스 구축
- 이력서 분석, 면접 관리, 포트폴리오 평가 등 종합적인 채용 관리
- 직관적이고 현대적인 UI/UX 제공

### 참고 사이트
- [SNOW 채용 사이트](https://recruit.snowcorp.com/main.do)
- [NAVER 채용 사이트](https://recruit.navercorp.com/main.do)

## 🧩 현재 백엔드/AI/PDF · OCR · DB 파이프라인 요약

아래는 현재 코드 기준의 실제 동작 상태를 요약한 내용입니다. PDF 업로드 → 텍스트화 → 요약/분석 → DB 저장 흐름과 LLM(Gemini) 사용을 중점으로 정리했습니다.

- **LLM 기본값: Google Gemini**
  - 모델: `gemini-1.5-flash` (환경 변수로 변경 가능)
  - 환경변수: `GOOGLE_API_KEY`, `LLM_PROVIDER=gemini`, `GEMINI_MODEL=gemini-1.5-flash`

- **PDF 처리 경로 1: 경량 업로드/요약/분석 (Gemini)**
  - 위치: `backend/routers/upload.py`
  - 엔드포인트:
    - `POST /api/upload/file`: 파일 업로드 후 텍스트 추출 → 요약 생성
    - `POST /api/upload/analyze`: 이력서/자소서/포트폴리오 상세 분석(JSON 스키마 강제)
    - `GET /api/upload/health`: 설정/상태 확인
  - 텍스트 추출: 간단 파일별 처리(`PyPDF2`, `python-docx` 사용 시), 비동기 호출 사용
  - Gemini 호출: `generate_summary_with_gemini`, `generate_detailed_analysis_with_gemini`

- **PDF 처리 경로 2: OCR + 임베딩 + 검색 (확장 파이프라인)**
  - 위치: `backend/routers/pdf_router.py`, 모듈: `backend/pdf_ocr_module/*`
  - 엔드포인트:
    - `POST /pdf/upload`: PDF 저장 → OCR/분석 → MongoDB 저장 → (옵션) VectorDB 업서트
    - `GET /pdf/documents/applicants`: OCR 결과를 지원자 카드 형태로 반환
    - `GET /pdf/files`: 업로드 파일 목록
    - `DELETE /pdf/file/{doc_hash}`: OCR 문서/페이지/벡터 삭제
    - `GET /pdf/search?q=...&k=5`: 쿼리 임베딩 후 유사 문서 검색(Pinecone)
  - 파이프라인 개요:
    1) 저장/경로 준비 → `utils.ensure_directories`/`save_upload_file`
    2) 처리 → `pdf_ocr_module.main.process_pdf` (텍스트 정제/필드추출/요약)
    3) 저장 → MongoDB `pdf_ocr.documents`, `pdf_ocr.pages`
    4) (선택) 임베딩 계산(`embedder.py`) → VectorDB 업서트(`vector_storage.py`)
    5) 프론트 사용을 위해 `hireme.resumes`/`hireme.applicant`로 매핑 저장
  - VectorDB: Pinecone 사용. API 키 없으면 자동 비활성(오류 없이 생략)

- **일반 텍스트 추출 유틸**
  - 위치: `backend/utils/text_extractor.py`
  - 지원 포맷: `.txt`, `.pdf`(pdfplumber 또는 PyPDF2), `.docx`
  - 공통 정제 로직 포함(불필요 공백/빈 줄 정리)

- **DB 요약**
  - 드라이버: Motor/PyMongo, 기본 DB: `hireme` (`DATABASE_NAME` 변경 가능)
  - 주요 컬렉션: `applicant`, `applicants`, `resumes` (+ OCR 경로는 `pdf_ocr.documents`, `pdf_ocr.pages`)

- **프론트 연동**
  - 프록시: `frontend/package.json` → `"proxy": "http://localhost:8000"`
  - 기본 CORS: `http://localhost:3000`, `http://localhost:3001`

## 🔀 병합(Merge) 시 예상 변경점과 유의사항

- **LLM 프로바이더 선택 및 호환성**
  - 기본값이 Gemini로 설정되었습니다. 다른 프로젝트가 OpenAI를 전제로 할 경우, `.env`에서 `LLM_PROVIDER=openai`로 전환하거나 호출부를 팩토리(`LLMProviderFactory`) 기반으로 정리하세요.
  - 필요한 키 정리: `GOOGLE_API_KEY`(Gemini), `OPENAI_API_KEY`/`OPENAI_ORGANIZATION`(OpenAI), `AZURE_OPENAI_*`(Azure OpenAI)
  - 테스트 코드가 OpenAI를 가정한다면 키가 없을 때 실패할 수 있으므로, `LLM_PROVIDER`를 테스트 환경에 맞춰 지정하세요.

- **API 경로 충돌 가능성**
  - 본 프로젝트 노출 경로: ` /api/upload/*`, `/pdf/*`, `/api/chatbot/*`
  - 병합 대상에 동일/유사 경로가 있으면 프리픽스 조정이 필요합니다.
    - 예: `backend/routers/upload.py`의 `APIRouter(prefix="/api/upload")`를 환경변수 기반으로 바꾸거나 다른 프리픽스로 변경

- **PDF 처리 파이프라인의 이원화**
  - 경량 경로(`upload.py`)와 OCR+임베딩 경로(`pdf_router.py`)가 공존합니다. 병합 시 어떤 경로를 대외 공개할지 결정하고, 필요 없는 라우터는 주입을 막거나 주석 처리하세요.

- **데이터베이스 스키마 및 컬렉션**
  - 기본 DB는 `hireme`. 주요 컬렉션: `applicant`, `applicants`, `resumes` (+ OCR 경로는 `pdf_ocr.documents`, `pdf_ocr.pages`)
  - 병합 대상 프로젝트에서 다른 DB/컬렉션을 사용하면 `DATABASE_NAME`과 컬렉션 매핑을 조정해야 합니다.
  - 업로드 처리 시 두 컬렉션(`applicant`, `applicants`)에 동시 기록하는 로직이 있어, 중복 저장 정책을 사전에 합의하세요.

- **VectorDB(Pinecone) 사용 여부**
  - Pinecone 키가 없으면 자동 비활성(오류 없음). 병합 대상이 다른 벡터 스토리지를 쓴다면 해당 어댑터를 병렬 유지하거나 하나로 통합하세요.

- **의존성 및 시스템 요구사항**
  - Python: `google-generativeai`, `PyPDF2`, `pdfplumber`, `motor`, `pymongo` 등. OS 의존(선택): `Tesseract`, `Poppler` 경로 필요 시 `.env`로 설정.
  - Node(프론트): 변경 없음. 프록시(`frontend/package.json`)는 `http://localhost:8000`을 가정.

- **CORS/프록시/포트**
  - CORS 기본: `http://localhost:3000`, `http://localhost:3001`. 병합 대상 프론트 포트가 다르면 `ALLOWED_ORIGINS`를 갱신.
  - 프론트 프록시도 대상 백엔드 포트에 맞게 조정 필요.

- **.gitignore 및 산출물**
  - 가상환경/노드 모듈/캐시/백업 폴더가 커밋되지 않도록 보장하세요: `backend/.venv/`, `frontend/node_modules/`, `__pycache__/`, `*.log` 등.

- **마이그레이션 체크리스트**
  1) `requirements.txt`/의존성 병합 및 재설치
  2) `.env` 통합: DB, LLM 키, CORS, OCR 경로, Pinecone 키 정리
  3) 공개 라우터 결정: 경량 업로드 vs. OCR 파이프라인 선택/병행
  4) DB 컬렉션 충돌 점검 및 마이그레이션 스크립트 준비(필요 시)
  5) LLM 프로바이더 최종 결정(`LLM_PROVIDER`), 키 유효성 점검
  6) 프론트 프록시와 CORS 정합성 확인
  7) 통합 헬스체크: `/health`, `/api/upload/health` 호출로 점검

예시 환경 변수 블록:
```env
# DB
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=hireme

# LLM
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# OCR (선택)
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
POPLER_PATH=C:\\tools\\poppler-24.02.0\\Library\\bin

# VectorDB (선택)
PINECONE_API_KEY=
PINECONE_INDEX_NAME=resume-vectors
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 📋 사이트맵

### 대시보드
- [x] 전체 채용 현황 요약 (서류 접수, 면접 일정, 추천 인재 등)
- [x] 주요 알림 및 리포트 바로가기
- [x] 실시간 통계 및 차트

### 이력서 관리
- [x] 이력서 제출 현황
- [x] PDF 변환 / 다운로드
- [x] QR 코드 스캔 및 정보 조회
- [x] 서류 자동 분석 결과

### 면접 관리
- [x] 비대면 면접 예약 및 일정 관리
- [x] AI 질문 설정 / 자동 생성
- [x] 구직자 영상 응답 조회
- [x] AI 면접 분석 결과

### 포트폴리오 분석
- [x] GitHub 등 연동 관리
- [x] 자동 코드 리뷰 결과
- [x] 프로젝트별 평가 리포트

### 자소서 검증
- [x] 자소서 분석 현황
- [x] 대필 및 AI 작성 감지 결과
- [x] 자소서와 영상 답변 STT 불일치 비교

### 인재 추천
- [x] AI 유사 인재 목록
- [x] 필터 및 조건 검색
- [x] 인재 프로필 상세 조회

### 사용자 관리 및 보안
- [x] 로그인/권한 관리
- [x] 개인정보 보호 설정
- [x] 사용 로그 기록

### 설정 및 지원
- [x] 시스템 설정 (AI 모델 파라미터, 알림 설정 등)
- [x] 도움말 / FAQ
- [x] 고객 지원 문의

## ✅ 완료된 작업 (DONE)

### 1. 프로젝트 구조 설정
- [x] React 프로젝트 초기화
- [x] 필요한 패키지 설치 (react-router-dom, styled-components, framer-motion, recharts 등)
- [x] 기본 폴더 구조 생성

### 2. 레이아웃 및 네비게이션
- [x] 반응형 사이드바 네비게이션
- [x] 상단 헤더 (검색, 알림, 사용자 프로필)
- [x] 모바일 대응 (햄버거 메뉴)
- [x] SNOW/NAVER 스타일의 깔끔한 디자인

### 3. 페이지 구현
- [x] **대시보드**: 통계 카드, 차트, 최근 활동
- [x] **이력서 관리**: 이력서 리스트, AI 분석, QR 기능
- [x] **면접 관리**: 면접 일정, AI 질문, 분석 결과
- [x] **포트폴리오 분석**: GitHub 연동, 코드 리뷰
- [x] **자소서 검증**: AI 분석, 표절 검사
- [x] **인재 추천**: AI 매칭, 필터링
- [x] **사용자 관리**: 권한 관리, 보안 설정
- [x] **설정 및 지원**: 시스템 설정, FAQ

### 4. UI/UX 구현
- [x] styled-components를 활용한 모던한 스타일링
- [x] Framer Motion 애니메이션 효과
- [x] Recharts를 활용한 데이터 시각화
- [x] 반응형 디자인 (모바일/태블릿/데스크톱)
- [x] 호버 효과 및 인터랙션

### 5. 기능 구현
- [x] 라우팅 시스템 (React Router)
- [x] 검색 및 필터링 기능
- [x] 상태 관리 (React Hooks)
- [x] 샘플 데이터 및 모의 기능

## 🔄 진행 중인 작업 (IN PROGRESS)

### 1. 성능 최적화
- [ ] 코드 스플리팅 및 지연 로딩
- [ ] 이미지 최적화
- [ ] 번들 크기 최적화

### 2. 접근성 개선
- [ ] ARIA 라벨 추가
- [ ] 키보드 네비게이션
- [ ] 색상 대비 개선

## 📝 남은 작업 (TODO)

### 1. 백엔드 연동
- [ ] API 엔드포인트 설계
- [ ] 데이터베이스 스키마 설계
- [ ] 인증/인가 시스템 구현
- [ ] 파일 업로드 기능

### 2. AI 기능 구현
- [ ] 실제 AI 모델 연동
- [ ] 이력서 분석 API
- [ ] 면접 질문 생성 AI
- [ ] 포트폴리오 평가 AI
- [ ] 자소서 검증 AI

### 3. 고급 기능
- [ ] 실시간 알림 시스템
- [ ] 다국어 지원
- [ ] 다크 모드
- [ ] PWA 지원
- [ ] 오프라인 기능

### 4. 테스트 및 품질 관리
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] E2E 테스트 작성
- [ ] 성능 테스트

### 5. 배포 및 운영
- [ ] CI/CD 파이프라인 구축
- [ ] 도커 컨테이너화
- [ ] 클라우드 배포
- [ ] 모니터링 시스템

## 🛠 기술 스택

### Frontend
- **React 18.2.0** - 사용자 인터페이스 구축
- **React Router 6.3.0** - 클라이언트 사이드 라우팅
- **Styled Components 5.3.5** - CSS-in-JS 스타일링
- **Framer Motion 7.2.1** - 애니메이션 라이브러리
- **React Icons 4.4.0** - 아이콘 라이브러리
- **Recharts 2.1.8** - 데이터 시각화

### Development Tools
- **Create React App** - React 프로젝트 설정
- **ESLint** - 코드 품질 관리
- **npm** - 패키지 관리

### UI/UX
- **Noto Sans KR** - 한글 폰트
- **CSS Grid & Flexbox** - 레이아웃
- **CSS Variables** - 테마 관리
- **반응형 디자인** - 모바일 퍼스트

## 🚀 실행 방법

### 1. 프로젝트 클론
```bash
git clone [repository-url]
cd recruitment-dashboard
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 개발 서버 실행
```bash
npm start
```

### 4. 브라우저에서 확인
- http://localhost:3000 접속

## 📁 프로젝트 구조

```
src/
├── components/
│   └── Layout/
│       └── Layout.js          # 메인 레이아웃 컴포넌트
├── pages/
│   ├── Dashboard/
│   │   └── Dashboard.js       # 대시보드 페이지
│   ├── ResumeManagement/
│   │   └── ResumeManagement.js # 이력서 관리 페이지
│   ├── InterviewManagement/
│   │   └── InterviewManagement.js # 면접 관리 페이지
│   ├── PortfolioAnalysis/
│   │   └── PortfolioAnalysis.js # 포트폴리오 분석 페이지
│   ├── CoverLetterValidation/
│   │   └── CoverLetterValidation.js # 자소서 검증 페이지
│   ├── TalentRecommendation/
│   │   └── TalentRecommendation.js # 인재 추천 페이지
│   ├── UserManagement/
│   │   └── UserManagement.js   # 사용자 관리 페이지
│   └── Settings/
│       └── Settings.js        # 설정 및 지원 페이지
├── App.js                     # 메인 앱 컴포넌트
├── index.js                   # 진입점
└── index.css                  # 전역 스타일
```

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: #00c851 (초록색)
- **Secondary**: #007bff (파란색)
- **Accent**: #ff6b35 (주황색)
- **Background**: #f8f9fa (연한 회색)
- **Text**: #333 (진한 회색)

### 타이포그래피
- **Font Family**: Noto Sans KR
- **Font Weights**: 300, 400, 500, 700
- **Line Height**: 1.6

### 컴포넌트
- **Border Radius**: 8px
- **Shadow**: 0 2px 4px rgba(0,0,0,0.1)
- **Transition**: all 0.3s ease

## 📊 주요 기능

### 1. 대시보드
- 실시간 채용 현황 통계
- 지원자 추이 차트
- 채용 현황 파이 차트
- 최근 활동 목록

### 2. 이력서 관리
- 이력서 목록 및 검색
- AI 분석 결과 표시
- PDF 다운로드
- QR 코드 생성/스캔

### 3. 면접 관리
- 면접 일정 관리
- AI 질문 자동 생성
- 면접 분석 결과
- 영상 응답 조회

### 4. 포트폴리오 분석
- GitHub 프로젝트 연동
- 코드 품질 분석
- 기술 스택 평가
- 프로젝트별 리포트

### 5. 자소서 검증
- AI 자소서 분석
- 표절 검사
- 문법 및 일관성 검사
- 개선 사항 제안

### 6. 인재 추천
- AI 기반 인재 매칭
- 필터링 및 검색
- 상세 프로필 조회
- 연락 기능

## 🔧 개발 환경 설정

### 필수 요구사항
- Node.js 16.0.0 이상
- npm 8.0.0 이상

### 권장 개발 도구
- VS Code
- React Developer Tools
- Redux DevTools (향후 추가 예정)

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**마지막 업데이트**: 2024년 1월
**버전**: 1.0.0
**상태**: 개발 중 (Development) 


---
## Appendix: Selected from README2.md (filtered) (20250812_184511)

# AI 채용 관리 시스템 - 진행사항 및 문제점 정리

## 📋 프로젝트 개요

SNOW와 NAVER 채용 사이트를 참고하여 개발한 AI 기반 채용 관리 시스템입니다.

### 🎯 목표
- AI 기술을 활용한 스마트한 채용 프로세스 구축
- 이력서 분석, 면접 관리, 포트폴리오 평가 등 종합적인 채용 관리
- 직관적이고 현대적인 UI/UX 제공

## ✅ 완료된 작업 (DONE)

### 1. 프로젝트 구조 설정
- [x] **프론트엔드**: React 18.2.0 기반 프로젝트 초기화
- [x] **백엔드**: FastAPI 기반 백엔드 서버 구축
- [x] **데이터베이스**: MongoDB 연동 설정
- [x] **Docker**: 프론트엔드/백엔드 컨테이너화

### 2. 프론트엔드 구현
- [x] **레이아웃**: 반응형 사이드바 네비게이션
- [x] **페이지 구현**:
  - 대시보드 (Dashboard.js)
  - 지원자 관리 (ApplicantManagement.js)
  - 면접 관리 (InterviewManagement/)
  - 채용공고 등록 (JobPostingRegistration/)
  - 사용자 관리 (UserManagement.js)
  - 설정 (Settings.js)
- [x] **UI/UX**: styled-components, Framer Motion 애니메이션
- [x] **차트**: Recharts를 활용한 데이터 시각화

### 3. 백엔드 구현
- [x] **API 엔드포인트**:
  - 지원자 관리 (/api/applicants)
  - 사용자 관리 (/api/users)
  - 파일 업로드 (/api/upload)
  - 챗봇 (/api/chatbot)
- [x] **데이터베이스**: MongoDB 연동 (motor 라이브러리)
- [x] **AI 서비스**: Google Generative AI 연동
- [x] **파일 처리**: PDF, DOCX 파일 파싱

### 4. AI 기능 구현
- [x] **챗봇**: Google Generative AI 기반 채용 상담 챗봇
- [x] **이력서 분석**: PDF/DOCX 파일 자동 파싱
- [x] **인재 매칭**: 키워드 기반 매칭 알고리즘
- [x] **면접 관리**: AI 기반 면접 일정 및 질문 관리

## ⚠️ 발생한 문제점 및 해결방법

### 1. 백엔드 빌드 시간 문제

**문제**: HuggingFace 모델 로딩으로 인한 Docker 빌드 시간 지연
```
# requirements.txt에서 문제가 되는 라이브러리들
sentence-transformers==2.2.2
scikit-learn==1.3.2
numpy==1.24.3
```

**해결방법**:
- HuggingFace 모델을 임시로 비활성화
- 키워드 기반 매칭으로 대체
- `ai_matching_service.py`에서 모델 로딩 부분 주석 처리

```python
# HuggingFace 모델 임시 비활성화 - 빌드 시간 단축을 위해
self.model = None
logger.info("📝 HuggingFace 모델 비활성화 (기존 키워드 매칭 사용)")
```

### 2. 프론트엔드 라우팅 문제

**문제**: React Router 설정으로 인한 페이지 접근 오류
- 개발 환경에서 새로고침 시 404 오류
- 프로덕션 빌드 시 라우팅 문제

**해결방법**:
- `package.json`에 `homepage` 설정 추가
- `proxy` 설정으로 백엔드 API 연동
```json
{
  "homepage": "http://localhost:3001",
  "proxy": "http://localhost:8000"
}
```

### 3. CORS 설정 문제

**문제**: 프론트엔드와 백엔드 간 CORS 오류
```
Access to fetch at 'http://localhost:8000/api/applicants' from origin 'http://localhost:3001' has been blocked by CORS policy
```

**해결방법**:
- FastAPI에 CORS 미들웨어 추가
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. 파일 업로드 크기 제한

**문제**: 대용량 파일 업로드 시 메모리 부족 오류
```
413 Payload Too Large
```

**해결방법**:
- FastAPI에서 파일 크기 제한 설정
- 청크 단위 파일 처리 구현
- 임시 파일 저장 후 처리

### 5. MongoDB 연결 문제

**문제**: 데이터베이스 연결 실패
```
Connection refused to MongoDB
```

**해결방법**:
- 연결 문자열 검증
- 네트워크 설정 확인
- 연결 풀 설정 최적화

## 🔄 진행 중인 작업 (IN PROGRESS)

### 1. AI 모델 최적화
- [ ] HuggingFace 모델 경량화
- [ ] 모델 캐싱 구현
- [ ] 배치 처리 최적화

### 2. 성능 개선
- [ ] 프론트엔드 코드 스플리팅
- [ ] 이미지 최적화
- [ ] API 응답 시간 개선

### 3. 보안 강화
- [ ] JWT 토큰 인증
- [ ] API 요청 제한
- [ ] 입력 데이터 검증

## 📝 남은 작업 (TODO)

### 1. 고급 AI 기능
- [ ] 실제 HuggingFace 모델 재활성화
- [ ] 이력서 자동 분석
- [ ] 면접 질문 자동 생성
- [ ] 포트폴리오 평가 AI

### 2. 실시간 기능
- [ ] WebSocket 연동
- [ ] 실시간 알림
- [ ] 실시간 채팅

### 3. 테스트 및 배포
- [ ] 단위 테스트 작성
- [ ] E2E 테스트
- [ ] CI/CD 파이프라인
- [ ] 클라우드 배포

## 🛠 기술 스택

### Frontend
- **React 18.2.0** - 사용자 인터페이스
- **React Router 6.3.0** - 클라이언트 라우팅
- **Styled Components 5.3.5** - CSS-in-JS
- **Framer Motion 7.2.1** - 애니메이션
- **Recharts 2.1.8** - 데이터 시각화
- **Axios 0.27.2** - HTTP 클라이언트

### Backend
- **FastAPI 0.104.1** - 웹 프레임워크
- **Uvicorn 0.24.0** - ASGI 서버
- **Motor 3.3.2** - MongoDB 비동기 드라이버
- **Google Generative AI 0.3.2** - AI 서비스
- **PyPDF2 3.0.1** - PDF 처리
- **Python-docx 1.1.0** - DOCX 처리

### Database
- **MongoDB** - NoSQL 데이터베이스

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 멀티 컨테이너 관리

## 🚀 실행 방법

### 1. 전체 시스템 실행 (Docker)
```bash
```

### 2. 개별 실행

#### 백엔드 실행
```bash
pip install -r requirements.txt
python main.py
```

#### 프론트엔드 실행
```bash
npm install
npm start
```

### 3. 접속 URL
- **프론트엔드**: http://localhost:3001
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 📁 프로젝트 구조

```
├── backend/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── ai_matching_service.py  # AI 매칭 서비스
│   ├── chatbot_router.py       # 챗봇 API
│   ├── database.py             # DB 연결
│   ├── models.py               # 데이터 모델
│   ├── requirements.txt        # Python 의존성
│   ├── Dockerfile              # 백엔드 컨테이너
│   └── routers/
│       ├── applicants.py       # 지원자 관리 API
│       ├── users.py            # 사용자 관리 API
│       └── upload.py           # 파일 업로드 API
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard/      # 대시보드
│   │   │   ├── ApplicantManagement.js
│   │   │   ├── InterviewManagement/
│   │   │   ├── JobPostingRegistration/
│   │   │   ├── UserManagement.js
│   │   │   └── Settings.js
│   │   ├── components/         # 재사용 컴포넌트
│   │   └── services/           # API 서비스
│   ├── package.json
│   └── Dockerfile              # 프론트엔드 컨테이너
```

## 🔧 개발 환경 설정

### 필수 요구사항
- **Node.js**: 16.0.0 이상
- **Python**: 3.8 이상
- **Docker**: 20.0 이상
- **MongoDB**: 5.0 이상

### 권장 개발 도구
- **VS Code** - 통합 개발 환경
- **Postman** - API 테스트
- **MongoDB Compass** - 데이터베이스 관리

## 📊 주요 기능 상세

### 1. 지원자 관리
- 이력서 업로드 및 파싱
- AI 기반 자동 분석
- 지원자 정보 관리
- 검색 및 필터링

### 2. 면접 관리
- 면접 일정 관리
- AI 질문 생성
- 면접 결과 기록
- 영상 면접 지원

### 3. 채용공고 관리
- 채용공고 등록/수정
- 템플릿 기반 등록
- 이미지 기반 등록
- 조직 정보 관리

### 4. AI 챗봇
- Google Generative AI 연동
- 채용 상담 자동 응답
- 문의사항 처리
- 실시간 대화

## 🐛 알려진 이슈

### 1. 성능 이슈
- **문제**: 대용량 파일 업로드 시 메모리 사용량 증가
- **상태**: 모니터링 중
- **해결 예정**: 스트리밍 업로드 구현

### 2. 보안 이슈
- **문제**: JWT 토큰 인증 미구현
- **상태**: 개발 중
- **해결 예정**: 다음 버전에서 구현

### 3. 호환성 이슈
- **문제**: 일부 브라우저에서 애니메이션 성능 저하
- **상태**: 조사 중
- **해결 예정**: 폴백 애니메이션 구현

## 📈 성능 지표

### 현재 성능
- **API 응답 시간**: 평균 200ms
- **페이지 로딩 시간**: 평균 1.2초
- **메모리 사용량**: 백엔드 512MB, 프론트엔드 256MB

### 목표 성능
- **API 응답 시간**: 평균 100ms 이하
- **페이지 로딩 시간**: 평균 800ms 이하
- **메모리 사용량**: 백엔드 256MB, 프론트엔드 128MB

## 🔄 버전 관리

### 현재 버전: 1.0.0
- 기본 기능 구현 완료
- AI 챗봇 연동
- 파일 업로드 기능

### 다음 버전: 1.1.0 (예정)
- JWT 인증 구현
- 실시간 알림
- 성능 최적화

### 향후 계획: 2.0.0
- 고급 AI 기능
- 모바일 앱
- 다국어 지원

## 📞 지원 및 문의

### 개발팀 연락처
- **프로젝트 관리자**: [이메일]
- **프론트엔드 개발자**: [이메일]
- **백엔드 개발자**: [이메일]

### 이슈 리포트
- GitHub Issues를 통한 버그 리포트
- 기능 요청 및 개선 제안 환영

---

**마지막 업데이트**: 2024년 1월
**문서 버전**: 2.0.0
**상태**: 개발 중 (Development)
