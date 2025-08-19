# 포트폴리오 수동 삽입 가이드

## MongoDB Compass 또는 mongo shell에서 실행하는 방법

### 1. MongoDB Compass 사용
1. MongoDB Compass를 열고 `localhost:27017`에 연결
2. `hireme` 데이터베이스 선택
3. `portfolios` 컬렉션 선택
4. "ADD DATA" → "Insert Document" 클릭
5. 아래 JSON 문서들을 하나씩 복사해서 삽입

### 2. mongo shell 사용
```bash
mongosh
use hireme
```

그리고 아래 명령어들을 하나씩 실행:

## 포트폴리오 문서들

### 김민수 (프론트엔드)
```javascript
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
  "items": [
    {
      "title": "김민수 - 웹 애플리케이션 프로젝트",
      "description": "사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선한 프로젝트입니다.",
      "tech_stack": ["React", "JavaScript", "TypeScript"],
      "role": "프론트엔드 개발 및 설계",
      "duration": "6개월",
      "team_size": 5,
      "achievements": [
        "사용자 만족도 20% 향상",
        "시스템 응답 속도 30% 개선",
        "코드 품질 향상으로 유지보수성 증대"
      ],
      "artifacts": [
        {
          "kind": "file",
          "filename": "김민수_프로젝트A_스크린샷.png",
          "mime": "image/png",
          "size": 1024000,
          "hash": "hash_김민수_projectA_1001"
        }
      ]
    }
  ],
  "analysis_score": 88.5,
  "status": "active",
  "version": 1,
  "created_at": new Date(),
  "updated_at": new Date()
});
```

### 이지혜 (백엔드)
```javascript
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
  "items": [
    {
      "title": "이지혜 - REST API 시스템 프로젝트",
      "description": "확장 가능한 REST API 시스템을 개발하여 대용량 트래픽을 처리할 수 있는 백엔드 아키텍처를 구축한 프로젝트입니다.",
      "tech_stack": ["Python", "Django", "PostgreSQL"],
      "role": "백엔드 개발 및 설계",
      "duration": "8개월",
      "team_size": 4,
      "achievements": [
        "API 응답 속도 40% 개선",
        "동시 사용자 처리량 3배 증가",
        "데이터베이스 쿼리 최적화로 성능 향상"
      ],
      "artifacts": [
        {
          "kind": "repo",
          "filename": "이지혜_API프로젝트_저장소",
          "url": "https://github.com/leejihye/api-project"
        }
      ]
    }
  ],
  "analysis_score": 92.3,
  "status": "active",
  "version": 1,
  "created_at": new Date(),
  "updated_at": new Date()
});
```

## 빠른 실행 명령어

모든 포트폴리오를 한 번에 생성하려면 `insert_portfolio_simple.js` 파일을 mongo shell에서 실행:

```bash
mongosh hireme < insert_portfolio_simple.js
```

또는

```bash
mongosh
load("insert_portfolio_simple.js")
```

## 확인 명령어

```javascript
// 포트폴리오 수 확인
db.portfolios.countDocuments({})

// 모든 포트폴리오 목록 확인
db.portfolios.find({}, {title: 1, "basic_info.names": 1}).pretty()
```
