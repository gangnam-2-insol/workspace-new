# 🗄️ 데이터베이스 구조 분석 문서

## 📋 개요

현재 프로젝트의 MongoDB 데이터베이스 구조를 종합적으로 분석한 문서입니다. 지원자, 이력서, 자기소개서 관련 내용을 중심으로 구성되어 있습니다.

### 📊 **데이터베이스 기본 정보**
- **DB명**: `hireme`
- **연결**: `mongodb://localhost:27017/hireme`
- **주요 컬렉션**: 6개 (applicants, resumes, cover_letters, portfolios, job_postings, applicant_rankings)
- **생성일**: 2025-08-20
- **최종 업데이트**: 2025-01-26

---

## 🏗️ **핵심 컬렉션 상세 분석**

### 1️⃣ **APPLICANTS (지원자 정보)**

**컬렉션명**: `applicants`
**설명**: 지원자의 기본 정보를 저장하는 메인 컬렉션

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "name": "String",                     // 지원자 이름
  "email": "String",                    // 이메일 주소 (유니크 인덱스)
  "phone": "String",                    // 전화번호
  "position": "String",                 // 지원 직무
  "department": "String",               // 부서
  "experience": "String|Number",        // 경력 연차
  "skills": "String|Array<String>",     // 기술 스택 목록
  "growthBackground": "String",         // 성장 배경
  "motivation": "String",               // 지원 동기
  "careerHistory": "String",            // 경력 사항
  "analysisScore": "Number(0-100)",     // 분석 점수
  "analysisResult": "String",           // 분석 결과
  "status": "String"                    // 상태 (pending/reviewing/passed/rejected/interview_scheduled 등)
}
```

#### 🔗 **연결 필드**
```json
{
  "resume_id": "ObjectId",              // 이력서 ID (resumes 컬렉션 참조)
  "cover_letter_id": "ObjectId",        // 자기소개서 ID (cover_letters 컬렉션 참조)
  "portfolio_id": "ObjectId",           // 포트폴리오 ID (portfolios 컬렉션 참조)
  "job_posting_id": "ObjectId"          // 채용공고 ID (job_postings 컬렉션 참조)
}
```

#### 📊 **랭킹 정보**
```json
{
  "ranks": {
    "resume": "Number",                 // 이력서 랭킹
    "coverLetter": "Number",            // 자기소개서 랭킹
    "portfolio": "Number",              // 포트폴리오 랭킹
    "total": "Number"                   // 종합 랭킹
  }
}
```

#### 🕒 **타임스탬프**
```json
{
  "created_at": "Date",                 // 생성일시
  "updated_at": "Date"                  // 수정일시
}
```

#### 📊 **인덱스**
- `email`: 1 (유니크)
- `created_at`: -1 (최신순)
- `position`: 1
- `status`: 1
- `job_posting_id`: 1

---

### 2️⃣ **RESUMES (이력서 정보)**

**컬렉션명**: `resumes`
**설명**: OCR로 추출된 이력서 정보를 저장

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "applicant_id": "ObjectId",           // 지원자 ID (applicants 참조)
  "extracted_text": "String",           // OCR로 추출된 텍스트
  "summary": "String",                  // AI 요약
  "keywords": ["String"],               // 키워드 목록
  "document_type": "resume"             // 문서 타입
}
```

#### 📋 **기본 정보 추출**
```json
{
  "basic_info": {
    "emails": ["String"],               // 이메일 목록
    "phones": ["String"],               // 전화번호 목록
    "names": ["String"],                // 이름 목록
    "urls": ["String"]                  // URL 목록
  }
}
```

#### 📁 **파일 메타데이터**
```json
{
  "file_metadata": {
    "filename": "String",               // 파일명
    "size": "Number",                   // 파일 크기
    "mime": "String",                   // MIME 타입
    "hash": "String",                   // 파일 해시
    "created_at": "Date",               // 생성일시
    "modified_at": "Date"               // 수정일시
  }
}
```

#### 📊 **인덱스**
- `applicant_id`: 1
- `created_at`: -1
- `document_type`: 1

---

### 3️⃣ **COVER_LETTERS (자기소개서 정보)**

**컬렉션명**: `cover_letters`
**설명**: OCR로 추출된 자기소개서 정보를 저장

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "applicant_id": "ObjectId",           // 지원자 ID (applicants 참조)
  "extracted_text": "String",           // OCR로 추출된 텍스트
  "summary": "String",                  // AI 요약
  "keywords": ["String"],               // 키워드 목록
  "document_type": "cover_letter"       // 문서 타입
}
```

#### 🆕 **새로 추가된 필드 (2025-08-20)**
```json
{
  "growthBackground": "String",         // 성장 배경
  "motivation": "String",               // 지원 동기
  "careerHistory": "String"             // 경력 사항
}
```

#### 📋 **기본 정보 및 파일 메타데이터**
```json
{
  "basic_info": { ... },                // 기본 정보 (resumes와 동일 구조)
  "file_metadata": { ... }              // 파일 메타데이터 (resumes와 동일 구조)
}
```

#### 📊 **인덱스**
- `applicant_id`: 1
- `created_at`: -1
- `document_type`: 1

---

### 4️⃣ **PORTFOLIOS (포트폴리오 정보)**

**컬렉션명**: `portfolios`
**설명**: OCR로 추출된 포트폴리오 정보를 저장 (버전 관리)

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "applicant_id": "ObjectId",           // 지원자 ID (applicants 참조)
  "extracted_text": "String",           // OCR로 추출된 텍스트
  "summary": "String",                  // AI 요약
  "keywords": ["String"],               // 키워드 목록
  "document_type": "portfolio"          // 문서 타입
}
```

#### 📁 **포트폴리오 전용 필드**
```json
{
  "analysis_score": "Number(0-100)",    // 분석 점수 (기본값 0.0)
  "status": "active|inactive",          // 포트폴리오 상태
  "version": "Number(>=1)"              // 버전 번호 (버전 관리)
}
```

#### 📊 **인덱스**
- `applicant_id`: 1, `version`: -1 (유니크)
- `applicant_id`: 1, `created_at`: -1
- `document_type`: 1

---

### 5️⃣ **JOB_POSTINGS (채용공고 정보)**

**컬렉션명**: `job_postings`
**설명**: 채용공고 정보를 저장

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "title": "String",                    // 공고 제목
  "company": "String",                  // 회사명
  "location": "String",                 // 근무지
  "department": "String",               // 부서
  "position": "String",                 // 직무
  "type": "String",                     // 고용 형태 (full-time|part-time|contract|internship)
  "salary": "String",                   // 급여
  "experience": "String",               // 경력 요구사항
  "education": "String",                // 학력 요구사항
  "description": "String",              // 업무 설명
  "requirements": "String",             // 자격 요건
  "required_skills": ["String"],        // 필수 기술
  "preferred_skills": ["String"],       // 우대 기술
  "required_documents": ["String"],     // 필수 제출 서류
  "status": "String",                   // 상태 (draft|published|closed|expired)
  "applicants": "Number",               // 지원자 수
  "views": "Number",                    // 조회수
  "bookmarks": "Number",                // 북마크 수
  "shares": "Number",                   // 공유 수
  "deadline": "Date",                   // 마감일
  "created_at": "Date",                 // 생성일시
  "updated_at": "Date"                  // 수정일시
}
```

---

### 6️⃣ **APPLICANT_RANKINGS (랭킹 정보)**

**컬렉션명**: `applicant_rankings`
**설명**: 지원자별 랭킹 정보를 저장

#### 🔑 **주요 필드**
```json
{
  "_id": "ObjectId",                    // 기본 키
  "category": "String",                 // 카테고리 (resume|coverLetter|portfolio|total)
  "applicant_id": "ObjectId",           // 지원자 ID
  "name": "String",                     // 지원자 이름
  "score": "Number",                    // 점수
  "rank": "Number",                     // 순위
  "created_at": "Date"                  // 생성일시
}
```

---

## 🔗 **컬렉션 간 관계도**

### 📊 **관계 구조**
```
applicants (1) ←→ (1) resumes
applicants (1) ←→ (1) cover_letters
applicants (1) ←→ (1) portfolios (버전 관리)
applicants (N) ←→ (1) job_postings
applicants (1) ←→ (N) applicant_rankings
```

### 📝 **관계 상세**
- **1:1 관계**: 지원자 ↔ 이력서, 지원자 ↔ 자기소개서
- **1:1 관계 (버전 관리)**: 지원자 ↔ 포트폴리오 (version 필드로 이력 관리)
- **N:1 관계**: 여러 지원자 ↔ 하나의 채용공고
- **1:N 관계**: 한 지원자 ↔ 여러 랭킹 기록

### 📋 **참조 방식**
- **직접 참조**: `applicant_id`, `job_posting_id` 등
- **ID 참조**: `resume_id`, `cover_letter_id`, `portfolio_id`
- **버전 관리**: `portfolios` 컬렉션의 `version` 필드

---

## 🛠️ **인덱스 및 제약사항**

### 🔒 **유니크 인덱스**
- `applicants.email`: 유니크
- `portfolios`: `applicant_id` + `version` 유니크

### 📊 **일반 인덱스**
- `applicants.created_at`: -1 (최신순)
- `applicants.position`: 1
- `applicants.status`: 1
- `applicants.job_posting_id`: 1
- `resumes.applicant_id`: 1
- `cover_letters.applicant_id`: 1
- `portfolios.applicant_id`: 1

### 🔒 **데이터 제약**
- `analysis_score`: 0-100 범위
- `version`: 1 이상
- `status`: enum 값 제한
- `document_type`: 고정값 ("resume", "cover_letter", "portfolio")

---

## 📈 **주요 특징 및 장점**

### ✅ **구조적 장점**
1. **명확한 분리**: 지원자, 이력서, 자기소개서, 포트폴리오가 독립적 컬렉션
2. **버전 관리**: 포트폴리오의 버전 관리로 이력 추적 가능
3. **OCR 통합**: 모든 문서에 OCR 추출 텍스트 저장
4. **AI 분석**: 요약, 키워드, 점수 등 AI 분석 결과 저장
5. **랭킹 시스템**: 지원자별 상세 랭킹 정보 관리

### ✅ **확장성**
- 새로운 문서 타입 추가 용이
- AI 분석 필드 확장 가능
- 랭킹 시스템 확장 가능
- 새로운 분석 지표 추가 가능

### ✅ **데이터 무결성**
- 참조 무결성 보장
- 스키마 검증 규칙 적용
- 중복 업로드 방지 (`file_hash` 활용)
- 유니크 인덱스로 중복 데이터 방지

---

## 🔄 **최근 업데이트 사항**

### 🆕 **2025-08-20 업데이트**
- `cover_letters` 컬렉션에 3개 필드 추가:
  - `growthBackground`: 성장 배경
  - `motivation`: 지원 동기
  - `careerHistory`: 경력 사항
- `portfolios` 컬렉션 버전 관리 개선
- `application_id` 필드 제거 (스키마 단순화)
- 파일 크기 제한 50MB로 증가

### 🔄 **스키마 변경**
- `portfolios.application_id`: 필수 → 선택사항
- `portfolios.analysis_score`: 기본값 0.0 설정
- 인덱스 최적화 및 중복 키 에러 해결

---

## ⚠️ **주의사항**

### 🔒 **중요 사항**
- `applicant_id`는 모든 문서 컬렉션에서 필수
- `portfolios`는 버전 관리로 중복 방지
- `file_hash`는 문서 중복 업로드 방지
- 이메일은 지원자 식별의 주요 키
- 스키마 검증으로 데이터 무결성 보장

### 📝 **개발 시 고려사항**
- **버전 관리**: `portfolios` 컬렉션
- **참조 무결성**: ID 기반 연결
- **인덱스 최적화**: 쿼리 성능 향상
- **스키마 검증**: 데이터 품질 보장
- **확장성**: 새로운 필드 추가 용이

---

## 🧪 **테스트 및 검증**

### ✅ **검증 완료 사항**
- `DB(without yc).txt` 구조와 100% 일치 확인
- 기존 기능 호환성 유지
- API 엔드포인트 모든 기능 유지
- 데이터 구조 기존 데이터와 호환

### 🔧 **테스트 방법**
1. **DB 연결 테스트**: `python test_db_connection.py`
2. **Docker Compose 실행**: `docker-compose up -d mongodb`
3. **기존 기능 테스트**: `python quick_test.py`

---

## 📚 **관련 문서**

- [MongoDB 컬렉션 구조 상세](./mongodb_collection_structure.txt)
- [DB 구조 검증 문서](./DB_STRUCTURE_VERIFICATION.md)
- [이력서 통합 계획](./RESUME_INTEGRATION_PLAN.md)

---

**문서 생성일**: 2025-01-26
**최종 업데이트**: 2025-01-26
**상태**: 검증 완료 ✅
