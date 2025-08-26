// MongoDB 초기화 스크립트
db = db.getSiblingDB('hireme');

// 사용자 컬렉션 생성 및 샘플 데이터
db.createCollection('users');
db.users.insertMany([
  {
    username: "admin",
    email: "admin@hireme.com",
    role: "admin",
    created_at: new Date()
  },
  {
    username: "user1",
    email: "user1@example.com",
    role: "user",
    created_at: new Date()
  },
  {
    username: "user2", 
    email: "user2@example.com",
    role: "user",
    created_at: new Date()
  }
]);

// 이력서 컬렉션 생성 및 샘플 데이터
db.createCollection('resumes');
db.resumes.insertMany([
  {
    user_id: "user1",
    title: "프론트엔드 개발자 이력서",
    content: "React, TypeScript, Node.js 경험...",
    status: "pending",
    created_at: new Date()
  },
  {
    user_id: "user2",
    title: "백엔드 개발자 이력서", 
    content: "Python, FastAPI, MongoDB 경험...",
    status: "approved",
    created_at: new Date()
  }
]);

// 면접 컬렉션 생성 및 샘플 데이터
db.createCollection('interviews');
db.interviews.insertMany([
  {
    user_id: "user1",
    company: "테크컴퍼니",
    position: "프론트엔드 개발자",
    date: new Date("2024-01-15T10:00:00Z"),
    status: "scheduled",
    created_at: new Date()
  },
  {
    user_id: "user2",
    company: "스타트업",
    position: "백엔드 개발자", 
    date: new Date("2024-01-20T14:00:00Z"),
    status: "completed",
    created_at: new Date()
  }
]);

// 포트폴리오 컬렉션 생성 및 샘플 데이터
db.createCollection('portfolios');
db.portfolios.insertMany([
  {
    user_id: "user1",
    title: "React 프로젝트",
    description: "React와 TypeScript를 사용한 웹 애플리케이션",
    github_url: "https://github.com/user1/react-project",
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user2",
    title: "FastAPI 백엔드",
    description: "FastAPI와 MongoDB를 사용한 REST API",
    github_url: "https://github.com/user2/fastapi-project",
    status: "active", 
    created_at: new Date()
  }
]);

print("MongoDB 초기화 완료!"); 