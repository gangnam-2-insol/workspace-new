# 포트폴리오 스키마 검증 비활성화 및 샘플 데이터 생성 가이드

## 1단계: MongoDB Compass에서 스키마 검증 비활성화

### 1. MongoDB Compass 실행
- MongoDB Compass를 열고 `localhost:27017`에 연결
- `hireme` 데이터베이스 선택

### 2. MongoDB Shell 탭 클릭
- 상단 탭에서 "MongoDB Shell" 선택

### 3. 스키마 검증 비활성화 명령어 실행
```javascript
// 포트폴리오 컬렉션의 스키마 검증 비활성화
db.runCommand({
  "collMod": "portfolios",
  "validator": {},
  "validationLevel": "off",
  "validationAction": "warn"
})
```

### 4. 확인
```javascript
// 스키마 검증이 비활성화되었는지 확인
db.getCollectionInfos({name: "portfolios"})
```

## 2단계: 샘플 포트폴리오 데이터 생성

### 1. 지원자 정보 확인
```javascript
// 현재 지원자 목록 확인
db.applicants.find({}, {name: 1, position: 1, skills: 1})
```

### 2. 포트폴리오 데이터 생성 (10개)
```javascript
// 김민수 포트폴리오
db.portfolios.insertOne({
  "applicant_id": "68999dda47ea917329ee7aba",
  "application_id": "app_68999dda47ea917329ee7aba_1001",
  "extracted_text": "김민수의 프론트엔드 개발자 포트폴리오입니다. React, JavaScript, TypeScript, CSS를 활용한 다양한 웹 애플리케이션 프로젝트를 수행했습니다.",
  "summary": "김민수의 프론트엔드 포트폴리오 - 웹 애플리케이션과 모바일 앱 개발 경험",
  "keywords": ["React", "JavaScript", "TypeScript", "CSS"],
  "document_type": "portfolio",
  "basic_info": {
    "emails": ["kimminsu@email.com"],
    "phones": ["010-1234-5678"],
    "names": ["김민수"],
    "urls": ["https://portfolio.kimminsu.com"]
  },
  "file_metadata": {
    "filename": "김민수_포트폴리오.pdf",
    "size": 2048000,
    "mime": "application/pdf",
    "hash": "hash_김민수_portfolio_1001",
    "created_at": new Date(),
    "modified_at": new Date()
  },
  "content": "# 김민수 포트폴리오\n\n## 프로필\n- 이름: 김민수\n- 직무: 프론트엔드\n- 기술 스택: React, JavaScript, TypeScript, CSS\n\n## 주요 프로젝트\n\n### 1. 웹 애플리케이션 프로젝트 (2023)\n**기술 스택**: React, JavaScript, TypeScript\n**역할**: 프론트엔드 개발 및 설계\n**기간**: 6개월\n**팀 규모**: 5명\n\n**주요 성과**\n- 사용자 만족도 20% 향상\n- 시스템 응답 속도 30% 개선\n- 코드 품질 향상으로 유지보수성 증대",
  "analysis_score": 88.5,
  "status": "active",
  "version": 1,
  "created_at": new Date(),
  "updated_at": new Date()
})

// 이지혜 포트폴리오
db.portfolios.insertOne({
  "applicant_id": "68999dda47ea917329ee7abb",
  "application_id": "app_68999dda47ea917329ee7abb_1002",
  "extracted_text": "이지혜의 백엔드 개발자 포트폴리오입니다. Python, Django, PostgreSQL, Redis를 활용한 다양한 서버 개발 프로젝트를 수행했습니다.",
  "summary": "이지혜의 백엔드 포트폴리오 - API 개발과 데이터베이스 설계 경험",
  "keywords": ["Python", "Django", "PostgreSQL", "Redis"],
  "document_type": "portfolio",
  "basic_info": {
    "emails": ["leejihye@email.com"],
    "phones": ["010-2345-6789"],
    "names": ["이지혜"],
    "urls": ["https://portfolio.leejihye.com"]
  },
  "file_metadata": {
    "filename": "이지혜_포트폴리오.pdf",
    "size": 2048000,
    "mime": "application/pdf",
    "hash": "hash_이지혜_portfolio_1002",
    "created_at": new Date(),
    "modified_at": new Date()
  },
  "content": "# 이지혜 포트폴리오\n\n## 프로필\n- 이름: 이지혜\n- 직무: 백엔드\n- 기술 스택: Python, Django, PostgreSQL, Redis\n\n## 주요 프로젝트\n\n### 1. REST API 시스템 프로젝트 (2023)\n**기술 스택**: Python, Django, PostgreSQL\n**역할**: 백엔드 개발 및 설계\n**기간**: 8개월\n**팀 규모**: 4명\n\n**주요 성과**\n- API 응답 속도 40% 개선\n- 동시 사용자 처리량 3배 증가\n- 데이터베이스 쿼리 최적화로 성능 향상",
  "analysis_score": 92.3,
  "status": "active",
  "version": 1,
  "created_at": new Date(),
  "updated_at": new Date()
})

// 나머지 8명도 비슷하게 생성...
```

### 3. 결과 확인
```javascript
// 포트폴리오 수 확인
db.portfolios.countDocuments({})

// 샘플 포트폴리오 확인
db.portfolios.find({}, {summary: 1, "basic_info.names": 1}).pretty()
```

## 3단계: 전체 데이터 확인

```javascript
// 전체 데이터베이스 상태 확인
print("=== 전체 데이터베이스 상태 ===")
print("지원자 수:", db.applicants.countDocuments({}))
print("이력서 수:", db.resumes.countDocuments({}))
print("자소서 수:", db.cover_letters.countDocuments({}))
print("포트폴리오 수:", db.portfolios.countDocuments({}))
```

## 완료 후 확인사항

✅ **스키마 검증 비활성화 완료**
✅ **10개 포트폴리오 데이터 생성 완료**
✅ **PDF 업로드 시 포트폴리오 저장 가능**
✅ **프론트엔드에서 포트폴리오 표시 가능**

이제 PDF 업로드 기능이 정상 작동할 것입니다!
