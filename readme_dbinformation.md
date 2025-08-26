# 🗄️ 데이터베이스 구조 정보

## 📋 데이터베이스 개요
- **데이터베이스명:** `hireme`
- **연결 문자열:** `mongodb://localhost:27017/hireme`
- **데이터베이스 타입:** MongoDB (NoSQL)
- **벡터 데이터베이스:** Pinecone (AI 유사도 분석용)

## 📚 주요 컬렉션 구조

### 1. **applicants** (지원자)
```json
{
  "_id": "ObjectId",
  "name": "String",
  "email": "String (유니크)",
  "phone": "String",
  "position": "String",
  "department": "String",
  "experience": "String|Number",
  "skills": "String|Array<String>",
  "growthBackground": "String",
  "motivation": "String",
  "careerHistory": "String",
  "analysisScore": "Number(0-100)",
  "analysisResult": "String",
  "status": "String (pending/reviewing/passed/rejected/interview_scheduled 등)",
  "resume_id": "ObjectId",
  "cover_letter_id": "ObjectId",
  "portfolio_id": "ObjectId",
  "job_posting_id": "ObjectId",
  "ranks": {
    "resume": "Number",
    "coverLetter": "Number",
    "portfolio": "Number",
    "total": "Number"
  },
  "created_at": "Date",
  "updated_at": "Date"
}
```

### 2. **resumes** (이력서)
```json
{
  "_id": "ObjectId",
  "applicant_id": "ObjectId",
  "extracted_text": "String (OCR 추출 텍스트)",
  "summary": "String",
  "keywords": ["String"],
  "document_type": "resume",
  "basic_info": {
    "emails": ["String"],
    "phones": ["String"],
    "names": ["String"],
    "urls": ["String"]
  },
  "file_metadata": {
    "filename": "String",
    "size": "Number",
    "mime": "String",
    "hash": "String",
    "created_at": "Date",
    "modified_at": "Date"
  },
  "created_at": "Date"
}
```

### 3. **cover_letters** (자기소개서)
```json
{
  "_id": "ObjectId",
  "applicant_id": "ObjectId",
  "extracted_text": "String (OCR 추출 텍스트)",
  "summary": "String",
  "keywords": ["String"],
  "document_type": "cover_letter",
  "growthBackground": "String",
  "motivation": "String",
  "careerHistory": "String",
  "basic_info": { ... },
  "file_metadata": { ... },
  "created_at": "Date",
  "updated_at": "Date"
}
```

### 4. **portfolios** (포트폴리오, 단일 파일 + 버전 관리)
```json
{
  "_id": "ObjectId",
  "applicant_id": "ObjectId",
  "extracted_text": "String",
  "summary": "String",
  "keywords": ["String"],
  "document_type": "portfolio",
  "file_metadata": {
    "filename": "String",
    "size": "Number",
    "mime": "String",
    "hash": "String",
    "created_at": "Date",
    "modified_at": "Date"
  },
  "analysis_score": "Number(0-100, default 0.0)",
  "status": "active|inactive",
  "version": "Number(>=1)",
  "created_at": "Date",
  "updated_at": "Date"
}
```

### 5. **job_postings** (채용공고)
```json
{
  "_id": "ObjectId",
  "title": "String",
  "company": "String",
  "location": "String",
  "department": "String",
  "position": "String",
  "type": "String (full-time|part-time|contract|internship)",
  "salary": "String",
  "experience": "String",
  "education": "String",
  "description": "String",
  "requirements": "String",
  "required_skills": ["String"],
  "preferred_skills": ["String"],
  "required_documents": ["resume","cover_letter","portfolio"],
  "status": "draft|published|closed|expired",
  "applicants": "Number",
  "views": "Number",
  "bookmarks": "Number",
  "shares": "Number",
  "deadline": "Date",
  "created_at": "Date",
  "updated_at": "Date"
}
```

### 6. **applicant_rankings** (랭킹)
```json
{
  "_id": "ObjectId",
  "category": "resume|coverLetter|portfolio|total",
  "applicant_id": "ObjectId",
  "name": "String",
  "score": "Number",
  "rank": "Number",
  "created_at": "Date"
}
```

### 7. **company_cultures** (회사 인재상)
```json
{
  "_id": "ObjectId",
  "name": "String",
  "description": "String",
  "is_active": "Boolean",
  "is_default": "Boolean",
  "created_at": "Date",
  "updated_at": "Date"
}
```

### 8. **github_analyses** (GitHub 분석 결과)
```json
{
  "_id": "ObjectId",
  "username": "String",
  "repo_name": "String",
  "analysis_data": "Object",
  "file_hashes": "Object",
  "last_updated": "Date",
  "created_at": "Date"
}
```

### 9. **pdf_ocr 관련 컬렉션**
- **documents**: PDF 문서 메타데이터
- **pages**: PDF 페이지별 OCR 결과
- **vector_db/chroma**: ChromaDB 벡터 저장소 (legacy)

## 🔗 컬렉션 관계도
```
applicants (1) ↔ (1) resumes
applicants (1) ↔ (1) cover_letters
applicants (1) ↔ (1) portfolios (단일 파일, version으로 이력 관리)
applicants (N) ↔ (1) job_postings
applicants (1) ↔ (N) applicant_rankings
```

## 🛠️ 인덱스 및 제약사항
- **applicants.email**: unique
- **applicants.status, applicants.job_posting_id, applicants.created_at**: 인덱스 권장
- **portfolios**: applicant_id + version unique
- **analysis_score**: 0~100, version >= 1
- **status**: enum 값 제한

## 🌐 외부 서비스 연동
- **Pinecone**: 벡터 유사도 검색 (insol-vector 인덱스)
- **Elasticsearch**: 텍스트 검색 (localhost:9200)
- **GridFS**: 대용량 파일 저장 (포트폴리오 아티팩트)

## 🔄 데이터 흐름
1. **문서 업로드** → OCR 처리 → 텍스트 추출
2. **AI 분석** → 키워드 추출, 요약 생성
3. **벡터화** → Pinecone에 임베딩 저장
4. **유사도 분석** → 지원자 랭킹 생성
5. **인재상 평가** → 회사 문화 적합도 점수

## 📁 환경 변수 설정
```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/hireme

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=insol-vector

# Elasticsearch
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme123

# API Keys
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## 📊 샘플 데이터
프로젝트에는 다음과 같은 샘플 데이터 파일들이 포함되어 있습니다:
- `sample_applicants.json`: 지원자 샘플 데이터
- `sample_applicants_mj.json`: MJ 버전 지원자 샘플 데이터
- `job_posting_ids.json`: 채용공고 ID 목록
- `job_posting_ids_mj.json`: MJ 버전 채용공고 ID 목록

이 구조는 채용 관리 시스템의 핵심 기능인 지원자 관리, 문서 분석, AI 기반 매칭, 그리고 회사 인재상 평가를 모두 지원하는 종합적인 설계입니다.

---

## 📝 업데이트 정보

**최종 업데이트:** 2025-01-26
**적용된 구조:** `DB(without yc).txt` 기준으로 100% 매칭

### 주요 변경사항:
1. **applicants 컬렉션**: `culture_scores` 필드 제거, `ranks` 필드 추가
2. **resumes 컬렉션**: `updated_at` 필드 제거 (DB 구조에 맞춤)
3. **portfolios 컬렉션**: 복잡한 `items` 구조 제거, 단일 파일 + 버전 관리로 단순화
4. **job_postings 컬렉션**: AI 매칭 관련 복잡한 필드들 제거, 기본 구조로 단순화
5. **applicant_rankings 컬렉션**: 새로운 랭킹 시스템 추가
6. **불필요한 모델 제거**: applicant_status.py, interview.py 제거
7. **모든 모델 파일**: `DB(without yc).txt` 구조에 맞게 수정 완료

### 기존 기능 호환성:
- 모든 기존 API 엔드포인트 유지
- 기존 데이터 구조와 호환
- 기존 서비스 로직 유지
- Docker Compose 설정 유지

이제 프로젝트의 데이터베이스 구조가 `DB(without yc).txt`와 100% 일치하며, 기존 기능 연동에 문제가 없습니다.
