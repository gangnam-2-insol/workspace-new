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

// 지원자 컬렉션 생성 및 샘플 데이터
db.createCollection('applicants');
db.applicants.insertMany([
  {
    id: "1",
    name: "김철수",
    email: "kim.chulsoo@email.com",
    phone: "010-1234-5678",
    position: "프론트엔드 개발자",
    experience: "3년",
    education: "컴퓨터공학과 졸업",
    status: "서류합격",
    appliedDate: "2024-01-15",
    aiScores: {
      resume: 85,
      coverLetter: 78,
      portfolio: 92
    },
    aiSuitability: 87,
    documents: {
      resume: {
        exists: true,
        summary: "React, TypeScript, Next.js 경험 풍부. 3년간 프론트엔드 개발 경력. 주요 프로젝트: 이커머스 플랫폼 구축, 관리자 대시보드 개발.",
        keywords: ["React", "TypeScript", "Next.js", "Redux", "Tailwind CSS"],
        content: "상세 이력서 내용..."
      },
      portfolio: {
        exists: true,
        summary: "GitHub에 15개 이상의 프로젝트 포트폴리오 보유. 반응형 웹 디자인, PWA 개발 경험.",
        keywords: ["GitHub", "PWA", "반응형", "UI/UX"],
        content: "포트폴리오 상세 내용..."
      },
      coverLetter: {
        exists: true,
        summary: "개발자로서의 성장 과정과 회사에 기여할 수 있는 역량을 명확하게 표현.",
        keywords: ["성장", "기여", "열정", "학습"],
        content: "자기소개서 상세 내용..."
      }
    },
    interview: {
      scheduled: true,
      date: "2024-01-25",
      time: "14:00",
      type: "대면",
      location: "회사 면접실",
      status: "예정"
    },
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    id: "2",
    name: "이영희",
    email: "lee.younghee@email.com",
    phone: "010-2345-6789",
    position: "백엔드 개발자",
    experience: "5년",
    education: "소프트웨어공학과 졸업",
    status: "보류",
    appliedDate: "2024-01-14",
    aiScores: {
      resume: 92,
      coverLetter: 85,
      portfolio: 88
    },
    aiSuitability: 89,
    documents: {
      resume: {
        exists: true,
        summary: "Java, Spring Boot, MySQL 경험 풍부. 5년간 백엔드 개발 경력. 마이크로서비스 아키텍처 설계 경험.",
        keywords: ["Java", "Spring Boot", "MySQL", "Microservices", "AWS"],
        content: "상세 이력서 내용..."
      },
      portfolio: {
        exists: true,
        summary: "대용량 트래픽 처리 시스템 구축 경험. 성능 최적화 및 모니터링 시스템 구축.",
        keywords: ["성능최적화", "모니터링", "대용량처리", "시스템설계"],
        content: "포트폴리오 상세 내용..."
      },
      coverLetter: {
        exists: true,
        summary: "시스템 아키텍처 설계 능력과 팀 리더십 경험을 강조.",
        keywords: ["아키텍처", "리더십", "시스템설계", "팀워크"],
        content: "자기소개서 상세 내용..."
      }
    },
    interview: {
      scheduled: false,
      date: null,
      time: null,
      type: null,
      location: null,
      status: "미정"
    },
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    id: "3",
    name: "박민수",
    email: "park.minsu@email.com",
    phone: "010-3456-7890",
    position: "UI/UX 디자이너",
    experience: "4년",
    education: "디자인학과 졸업",
    status: "서류불합격",
    appliedDate: "2024-01-13",
    aiScores: {
      resume: 65,
      coverLetter: 72,
      portfolio: 78
    },
    aiSuitability: 71,
    documents: {
      resume: {
        exists: true,
        summary: "Figma, Adobe XD 사용 경험. 4년간 UI/UX 디자인 경력. 모바일 앱 디자인 전문.",
        keywords: ["Figma", "Adobe XD", "UI/UX", "모바일앱", "디자인시스템"],
        content: "상세 이력서 내용..."
      },
      portfolio: {
        exists: true,
        summary: "다양한 모바일 앱 디자인 프로젝트 경험. 사용자 리서치 및 프로토타이핑 경험.",
        keywords: ["모바일앱", "프로토타이핑", "사용자리서치", "디자인시스템"],
        content: "포트폴리오 상세 내용..."
      },
      coverLetter: {
        exists: true,
        summary: "사용자 중심의 디자인 철학과 창의적인 문제 해결 능력을 강조.",
        keywords: ["사용자중심", "창의성", "문제해결", "디자인철학"],
        content: "자기소개서 상세 내용..."
      }
    },
    interview: {
      scheduled: false,
      date: null,
      time: null,
      type: null,
      location: null,
      status: "미정"
    },
    created_at: new Date(),
    updated_at: new Date()
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