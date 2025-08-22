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
    name: "김철수",
    email: "kim.chulsoo@email.com",
    phone: "010-1234-5678",
    position: "프론트엔드 개발자",
    department: "개발팀",
    experience: "3년",
    skills: "React, TypeScript, JavaScript, HTML, CSS",
    growthBackground: "웹 개발에 대한 열정으로 다양한 프로젝트를 통해 성장해왔습니다.",
    motivation: "사용자 경험을 개선하는 개발자가 되고 싶습니다.",
    careerHistory: "ABC 회사에서 2년간 프론트엔드 개발, XYZ 스타트업에서 1년간 풀스택 개발",
    analysisScore: 85,
    analysisResult: "프론트엔드 기술에 대한 깊은 이해와 실무 경험이 우수합니다.",
    status: "approved",
    job_posting_id: "frontend_dev_2024",
    created_at: new Date()
  },
  {
    name: "이영희",
    email: "lee.younghee@email.com",
    phone: "010-2345-6789",
    position: "백엔드 개발자",
    department: "개발팀",
    experience: "5년",
    skills: "Python, Django, FastAPI, PostgreSQL, Docker",
    growthBackground: "백엔드 시스템 설계와 개발을 통해 안정적인 서비스를 제공하는 것에 관심이 많습니다.",
    motivation: "확장 가능하고 안정적인 백엔드 시스템을 구축하고 싶습니다.",
    careerHistory: "DEF 회사에서 3년간 백엔드 개발, GHI 기업에서 2년간 시스템 아키텍트",
    analysisScore: 92,
    analysisResult: "백엔드 개발 경험이 풍부하고 시스템 설계 능력이 뛰어납니다.",
    status: "approved",
    job_posting_id: "backend_dev_2024",
    created_at: new Date()
  },
  {
    name: "박민수",
    email: "park.minsu@email.com",
    phone: "010-3456-7890",
    position: "UI/UX 디자이너",
    department: "디자인팀",
    experience: "4년",
    skills: "Figma, Adobe XD, Photoshop, Illustrator, Sketch",
    growthBackground: "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 것에 관심이 있습니다.",
    motivation: "사용자 경험을 향상시키는 혁신적인 디자인을 만들고 싶습니다.",
    careerHistory: "JKL 디자인 에이전시에서 2년간 UI 디자이너, MNO 기업에서 2년간 UX 디자이너",
    analysisScore: 88,
    analysisResult: "UI/UX 디자인 경험이 풍부하고 사용자 중심 사고가 뛰어납니다.",
    status: "pending",
    job_posting_id: "uiux_designer_2024",
    created_at: new Date()
  },
  {
    name: "정수진",
    email: "jung.sujin@email.com",
    phone: "010-4567-8901",
    position: "데이터 분석가",
    department: "데이터팀",
    experience: "2년",
    skills: "Python, R, SQL, Tableau, Power BI, Pandas, NumPy",
    growthBackground: "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정에 기여하는 것에 관심이 있습니다.",
    motivation: "데이터 기반의 의사결정을 지원하는 분석가가 되고 싶습니다.",
    careerHistory: "PQR 기업에서 2년간 데이터 분석가로 근무",
    analysisScore: 78,
    analysisResult: "데이터 분석 기본기가 탄탄하고 시각화 능력이 우수합니다.",
    status: "pending",
    job_posting_id: "data_analyst_2024",
    created_at: new Date()
  },
  {
    name: "최동현",
    email: "choi.donghyun@email.com",
    phone: "010-5678-9012",
    position: "DevOps 엔지니어",
    department: "인프라팀",
    experience: "6년",
    skills: "AWS, Docker, Kubernetes, Jenkins, Terraform, Linux, Shell Script",
    growthBackground: "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 것에 전문성을 가지고 있습니다.",
    motivation: "안정적이고 확장 가능한 인프라를 구축하여 개발팀의 생산성을 향상시키고 싶습니다.",
    careerHistory: "STU 기업에서 4년간 시스템 엔지니어, VWX 스타트업에서 2년간 DevOps 엔지니어",
    analysisScore: 95,
    analysisResult: "DevOps 경험이 매우 풍부하고 클라우드 인프라 전문성이 뛰어납니다.",
    status: "approved",
    job_posting_id: "devops_engineer_2024",
    created_at: new Date()
  }
]);

// 이력서 컬렉션 생성 및 샘플 데이터
db.createCollection('resumes');
db.resumes.insertMany([
  {
    doc_id: "resume_001",
    doc_hash: "abc123def456",
    file_name: "김철수_이력서.pdf",
    num_pages: 2,
    preview: ["thumb_kim_chulsoo_resume_page0001.png", "thumb_kim_chulsoo_resume_page0002.png"],
    pages: [
      {
        page: 1,
        clean_text: "김철수\n프론트엔드 개발자\n연락처: 010-1234-5678\n이메일: kim.chulsoo@email.com\n\n학력\n- 서울대학교 컴퓨터공학과 졸업\n\n경력\n- ABC 회사 프론트엔드 개발자 (2021-2023)\n- XYZ 스타트업 풀스택 개발자 (2023-현재)\n\n기술스택\n- React, TypeScript, JavaScript\n- HTML, CSS, SCSS\n- Node.js, Express\n- Git, GitHub",
        quality_score: 0.95,
        trace: { attempts: [] }
      },
      {
        page: 2,
        clean_text: "프로젝트 경험\n\n1. E-커머스 웹사이트 개발\n- React와 TypeScript를 사용한 반응형 웹사이트 구축\n- 사용자 경험 개선으로 전환율 15% 향상\n\n2. 관리자 대시보드 개발\n- 실시간 데이터 시각화 대시보드 구축\n- Chart.js와 D3.js를 활용한 인터랙티브 차트 구현\n\n자격증\n- AWS Certified Developer Associate\n- Google Analytics Individual Qualification",
        quality_score: 0.92,
        trace: { attempts: [] }
      }
    ],
    text: "김철수\n프론트엔드 개발자\n연락처: 010-1234-5678\n이메일: kim.chulsoo@email.com\n\n학력\n- 서울대학교 컴퓨터공학과 졸업\n\n경력\n- ABC 회사 프론트엔드 개발자 (2021-2023)\n- XYZ 스타트업 풀스택 개발자 (2023-현재)\n\n기술스택\n- React, TypeScript, JavaScript\n- HTML, CSS, SCSS\n- Node.js, Express\n- Git, GitHub\n\n프로젝트 경험\n\n1. E-커머스 웹사이트 개발\n- React와 TypeScript를 사용한 반응형 웹사이트 구축\n- 사용자 경험 개선으로 전환율 15% 향상\n\n2. 관리자 대시보드 개발\n- 실시간 데이터 시각화 대시보드 구축\n- Chart.js와 D3.js를 활용한 인터랙티브 차트 구현\n\n자격증\n- AWS Certified Developer Associate\n- Google Analytics Individual Qualification",
    fields: {
      names: ["김철수"],
      emails: ["kim.chulsoo@email.com"],
      phones: ["010-1234-5678"],
      positions: ["프론트엔드 개발자"],
      companies: [],
      education: ["서울대학교 컴퓨터공학과"],
      skills: ["React", "TypeScript", "JavaScript", "HTML", "CSS", "SCSS", "Node.js", "Express", "Git", "GitHub", "Chart.js", "D3.js"],
      addresses: []
    },
    summary: "3년간의 프론트엔드 개발 경험을 가진 김철수는 React와 TypeScript를 활용한 웹 애플리케이션 개발에 전문성을 가지고 있으며, 사용자 경험 개선을 통한 비즈니스 성과 창출에 기여한 경험이 있습니다.",
    keywords: ["React", "TypeScript", "프론트엔드", "웹개발", "JavaScript", "사용자경험", "E-커머스", "대시보드", "시각화"],
    created_at: new Date()
  },
  {
    doc_id: "resume_002",
    doc_hash: "def456ghi789",
    file_name: "이영희_이력서.pdf",
    num_pages: 3,
    preview: ["thumb_lee_younghee_resume_page0001.png", "thumb_lee_younghee_resume_page0002.png", "thumb_lee_younghee_resume_page0003.png"],
    pages: [
      {
        page: 1,
        clean_text: "이영희\n백엔드 개발자\n연락처: 010-2345-6789\n이메일: lee.younghee@email.com\n\n학력\n- 연세대학교 정보산업공학과 졸업\n- 서울대학교 대학원 컴퓨터공학과 석사\n\n경력\n- DEF 회사 백엔드 개발자 (2019-2022)\n- GHI 기업 시스템 아키텍트 (2022-현재)",
        quality_score: 0.98,
        trace: { attempts: [] }
      },
      {
        page: 2,
        clean_text: "기술스택\n- Python, Django, FastAPI\n- PostgreSQL, MySQL, Redis\n- Docker, Kubernetes\n- AWS, GCP\n- REST API, GraphQL\n- Microservices Architecture\n\n주요 프로젝트\n\n1. 대규모 E-커머스 플랫폼 백엔드 구축\n- 마이크로서비스 아키텍처 설계 및 구현\n- 초당 10만 요청 처리 가능한 시스템 구축\n- Redis를 활용한 캐싱 전략으로 응답 속도 50% 개선",
        quality_score: 0.96,
        trace: { attempts: [] }
      },
      {
        page: 3,
        clean_text: "2. 결제 시스템 개발\n- 안전한 결제 프로세스 설계 및 구현\n- PCI DSS 준수 보안 시스템 구축\n- 모니터링 및 로깅 시스템 구축\n\n3. 데이터 파이프라인 구축\n- Apache Kafka를 활용한 실시간 데이터 처리\n- ELK 스택을 통한 로그 분석 시스템 구축\n\n자격증\n- AWS Solutions Architect Professional\n- Google Cloud Professional Cloud Architect\n- Kubernetes Administrator (CKA)",
        quality_score: 0.94,
        trace: { attempts: [] }
      }
    ],
    text: "이영희\n백엔드 개발자\n연락처: 010-2345-6789\n이메일: lee.younghee@email.com\n\n학력\n- 연세대학교 정보산업공학과 졸업\n- 서울대학교 대학원 컴퓨터공학과 석사\n\n경력\n- DEF 회사 백엔드 개발자 (2019-2022)\n- GHI 기업 시스템 아키텍트 (2022-현재)\n\n기술스택\n- Python, Django, FastAPI\n- PostgreSQL, MySQL, Redis\n- Docker, Kubernetes\n- AWS, GCP\n- REST API, GraphQL\n- Microservices Architecture\n\n주요 프로젝트\n\n1. 대규모 E-커머스 플랫폼 백엔드 구축\n- 마이크로서비스 아키텍처 설계 및 구현\n- 초당 10만 요청 처리 가능한 시스템 구축\n- Redis를 활용한 캐싱 전략으로 응답 속도 50% 개선\n\n2. 결제 시스템 개발\n- 안전한 결제 프로세스 설계 및 구현\n- PCI DSS 준수 보안 시스템 구축\n- 모니터링 및 로깅 시스템 구축\n\n3. 데이터 파이프라인 구축\n- Apache Kafka를 활용한 실시간 데이터 처리\n- ELK 스택을 통한 로그 분석 시스템 구축\n\n자격증\n- AWS Solutions Architect Professional\n- Google Cloud Professional Cloud Architect\n- Kubernetes Administrator (CKA)",
    fields: {
      names: ["이영희"],
      emails: ["lee.younghee@email.com"],
      phones: ["010-2345-6789"],
      positions: ["백엔드 개발자", "시스템 아키텍트"],
      companies: ["DEF 회사", "GHI 기업"],
      education: ["연세대학교 정보산업공학과", "서울대학교 대학원 컴퓨터공학과"],
      skills: ["Python", "Django", "FastAPI", "PostgreSQL", "MySQL", "Redis", "Docker", "Kubernetes", "AWS", "GCP", "REST API", "GraphQL", "Microservices", "Apache Kafka", "ELK 스택"],
      addresses: []
    },
    summary: "5년간의 백엔드 개발 경험을 가진 이영희는 대규모 시스템 설계와 마이크로서비스 아키텍처 구현에 전문성을 가지고 있으며, 안정적이고 확장 가능한 백엔드 시스템 구축 경험이 풍부합니다.",
    keywords: ["Python", "백엔드", "마이크로서비스", "Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis", "시스템아키텍처", "E-커머스"],
    created_at: new Date()
  },
  {
    doc_id: "resume_003",
    doc_hash: "ghi789jkl012",
    file_name: "박민수_이력서.pdf",
    num_pages: 2,
    preview: ["thumb_park_minsu_resume_page0001.png", "thumb_park_minsu_resume_page0002.png"],
    pages: [
      {
        page: 1,
        clean_text: "박민수\nUI/UX 디자이너\n연락처: 010-3456-7890\n이메일: park.minsu@email.com\n\n학력\n- 홍익대학교 시각디자인학과 졸업\n\n경력\n- JKL 디자인 에이전시 UI 디자이너 (2020-2022)\n- MNO 기업 UX 디자이너 (2022-현재)",
        quality_score: 0.93,
        trace: { attempts: [] }
      },
      {
        page: 2,
        clean_text: "기술스택\n- Figma, Adobe XD, Sketch\n- Photoshop, Illustrator\n- InVision, Marvel\n- Principle, Framer\n- HTML, CSS (기본)\n\n주요 프로젝트\n\n1. 모바일 뱅킹 앱 리디자인\n- 사용자 리서치를 통한 UX 개선\n- 접근성 가이드라인 준수\n- 사용자 만족도 30% 향상\n\n2. E-커머스 웹사이트 UX 개선\n- 사용자 여정 맵 분석 및 개선\n- A/B 테스트를 통한 최적화\n- 전환율 25% 향상\n\n3. 브랜드 아이덴티티 디자인\n- 로고, CI/BI 시스템 구축\n- 브랜드 가이드라인 제작",
        quality_score: 0.91,
        trace: { attempts: [] }
      }
    ],
    text: "박민수\nUI/UX 디자이너\n연락처: 010-3456-7890\n이메일: park.minsu@email.com\n\n학력\n- 홍익대학교 시각디자인학과 졸업\n\n경력\n- JKL 디자인 에이전시 UI 디자이너 (2020-2022)\n- MNO 기업 UX 디자이너 (2022-현재)\n\n기술스택\n- Figma, Adobe XD, Sketch\n- Photoshop, Illustrator\n- InVision, Marvel\n- Principle, Framer\n- HTML, CSS (기본)\n\n주요 프로젝트\n\n1. 모바일 뱅킹 앱 리디자인\n- 사용자 리서치를 통한 UX 개선\n- 접근성 가이드라인 준수\n- 사용자 만족도 30% 향상\n\n2. E-커머스 웹사이트 UX 개선\n- 사용자 여정 맵 분석 및 개선\n- A/B 테스트를 통한 최적화\n- 전환율 25% 향상\n\n3. 브랜드 아이덴티티 디자인\n- 로고, CI/BI 시스템 구축\n- 브랜드 가이드라인 제작",
    fields: {
      names: ["박민수"],
      emails: ["park.minsu@email.com"],
      phones: ["010-3456-7890"],
      positions: ["UI/UX 디자이너"],
      companies: ["JKL 디자인 에이전시", "MNO 기업"],
      education: ["홍익대학교 시각디자인학과"],
      skills: ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InVision", "Marvel", "Principle", "Framer", "HTML", "CSS"],
      addresses: []
    },
    summary: "4년간의 UI/UX 디자인 경험을 가진 박민수는 사용자 중심의 디자인을 통해 비즈니스 성과를 창출하는 것에 전문성을 가지고 있으며, 다양한 디자인 도구를 활용한 프로젝트 경험이 풍부합니다.",
    keywords: ["UI/UX", "디자인", "Figma", "사용자경험", "모바일앱", "웹사이트", "브랜딩", "사용자리서치", "A/B테스트"],
    created_at: new Date()
  },
  {
    doc_id: "resume_004",
    doc_hash: "jkl012mno345",
    file_name: "정수진_이력서.pdf",
    num_pages: 2,
    preview: ["thumb_jung_sujin_resume_page0001.png", "thumb_jung_sujin_resume_page0002.png"],
    pages: [
      {
        page: 1,
        clean_text: "정수진\n데이터 분석가\n연락처: 010-4567-8901\n이메일: jung.sujin@email.com\n\n학력\n- 고려대학교 통계학과 졸업\n- 서울대학교 대학원 데이터사이언스 석사\n\n경력\n- PQR 기업 데이터 분석가 (2022-현재)",
        quality_score: 0.89,
        trace: { attempts: [] }
      },
      {
        page: 2,
        clean_text: "기술스택\n- Python, R, SQL\n- Pandas, NumPy, Scikit-learn\n- Tableau, Power BI\n- Jupyter Notebook\n- Apache Spark\n- Google Analytics\n\n주요 프로젝트\n\n1. 고객 세분화 분석\n- RFM 분석을 통한 고객 그룹 분류\n- 개인화 마케팅 전략 수립\n- 매출 20% 향상\n\n2. 예측 모델 개발\n- 머신러닝을 활용한 매출 예측 모델\n- 정확도 85% 달성\n- 비즈니스 의사결정 지원\n\n3. 대시보드 구축\n- Tableau를 활용한 실시간 대시보드\n- KPI 모니터링 시스템 구축",
        quality_score: 0.87,
        trace: { attempts: [] }
      }
    ],
    text: "정수진\n데이터 분석가\n연락처: 010-4567-8901\n이메일: jung.sujin@email.com\n\n학력\n- 고려대학교 통계학과 졸업\n- 서울대학교 대학원 데이터사이언스 석사\n\n경력\n- PQR 기업 데이터 분석가 (2022-현재)\n\n기술스택\n- Python, R, SQL\n- Pandas, NumPy, Scikit-learn\n- Tableau, Power BI\n- Jupyter Notebook\n- Apache Spark\n- Google Analytics\n\n주요 프로젝트\n\n1. 고객 세분화 분석\n- RFM 분석을 통한 고객 그룹 분류\n- 개인화 마케팅 전략 수립\n- 매출 20% 향상\n\n2. 예측 모델 개발\n- 머신러닝을 활용한 매출 예측 모델\n- 정확도 85% 달성\n- 비즈니스 의사결정 지원\n\n3. 대시보드 구축\n- Tableau를 활용한 실시간 대시보드\n- KPI 모니터링 시스템 구축",
    fields: {
      names: ["정수진"],
      emails: ["jung.sujin@email.com"],
      phones: ["010-4567-8901"],
      positions: ["데이터 분석가"],
      companies: ["PQR 기업"],
      education: ["고려대학교 통계학과", "서울대학교 대학원 데이터사이언스"],
      skills: ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "Tableau", "Power BI", "Jupyter Notebook", "Apache Spark", "Google Analytics"],
      addresses: []
    },
    summary: "2년간의 데이터 분석 경험을 가진 정수진은 통계학과 데이터사이언스 전공을 바탕으로 머신러닝과 데이터 시각화에 전문성을 가지고 있으며, 비즈니스 인사이트 도출을 통한 성과 창출 경험이 있습니다.",
    keywords: ["데이터분석", "Python", "R", "SQL", "머신러닝", "Tableau", "통계학", "예측모델", "시각화", "비즈니스인사이트"],
    created_at: new Date()
  },
  {
    doc_id: "resume_005",
    doc_hash: "mno345pqr678",
    file_name: "최동현_이력서.pdf",
    num_pages: 3,
    preview: ["thumb_choi_donghyun_resume_page0001.png", "thumb_choi_donghyun_resume_page0002.png", "thumb_choi_donghyun_resume_page0003.png"],
    pages: [
      {
        page: 1,
        clean_text: "최동현\nDevOps 엔지니어\n연락처: 010-5678-9012\n이메일: choi.donghyun@email.com\n\n학력\n- 한양대학교 컴퓨터공학과 졸업\n\n경력\n- STU 기업 시스템 엔지니어 (2018-2022)\n- VWX 스타트업 DevOps 엔지니어 (2022-현재)",
        quality_score: 0.97,
        trace: { attempts: [] }
      },
      {
        page: 2,
        clean_text: "기술스택\n- AWS, GCP, Azure\n- Docker, Kubernetes\n- Jenkins, GitLab CI/CD\n- Terraform, Ansible\n- Linux, Shell Script\n- Prometheus, Grafana\n- ELK Stack\n\n주요 프로젝트\n\n1. 클라우드 마이그레이션\n- 온프레미스에서 AWS로 전체 시스템 마이그레이션\n- 99.9% 가용성 달성\n- 운영 비용 40% 절감",
        quality_score: 0.95,
        trace: { attempts: [] }
      },
      {
        page: 3,
        clean_text: "2. CI/CD 파이프라인 구축\n- Jenkins와 Docker를 활용한 자동화 파이프라인\n- 배포 시간 80% 단축\n- 롤백 시간 5분 이내\n\n3. 모니터링 시스템 구축\n- Prometheus와 Grafana를 활용한 실시간 모니터링\n- 알림 시스템 구축\n- 장애 대응 시간 50% 단축\n\n자격증\n- AWS Solutions Architect Professional\n- Kubernetes Administrator (CKA)\n- Google Cloud Professional Cloud Architect",
        quality_score: 0.93,
        trace: { attempts: [] }
      }
    ],
    text: "최동현\nDevOps 엔지니어\n연락처: 010-5678-9012\n이메일: choi.donghyun@email.com\n\n학력\n- 한양대학교 컴퓨터공학과 졸업\n\n경력\n- STU 기업 시스템 엔지니어 (2018-2022)\n- VWX 스타트업 DevOps 엔지니어 (2022-현재)\n\n기술스택\n- AWS, GCP, Azure\n- Docker, Kubernetes\n- Jenkins, GitLab CI/CD\n- Terraform, Ansible\n- Linux, Shell Script\n- Prometheus, Grafana\n- ELK Stack\n\n주요 프로젝트\n\n1. 클라우드 마이그레이션\n- 온프레미스에서 AWS로 전체 시스템 마이그레이션\n- 99.9% 가용성 달성\n- 운영 비용 40% 절감\n\n2. CI/CD 파이프라인 구축\n- Jenkins와 Docker를 활용한 자동화 파이프라인\n- 배포 시간 80% 단축\n- 롤백 시간 5분 이내\n\n3. 모니터링 시스템 구축\n- Prometheus와 Grafana를 활용한 실시간 모니터링\n- 알림 시스템 구축\n- 장애 대응 시간 50% 단축\n\n자격증\n- AWS Solutions Architect Professional\n- Kubernetes Administrator (CKA)\n- Google Cloud Professional Cloud Architect",
    fields: {
      names: ["최동현"],
      emails: ["choi.donghyun@email.com"],
      phones: ["010-5678-9012"],
      positions: ["DevOps 엔지니어"],
      companies: ["STU 기업", "VWX 스타트업"],
      education: ["한양대학교 컴퓨터공학과"],
      skills: ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "Jenkins", "GitLab CI/CD", "Terraform", "Ansible", "Linux", "Shell Script", "Prometheus", "Grafana", "ELK Stack"],
      addresses: []
    },
    summary: "6년간의 시스템 엔지니어링과 DevOps 경험을 가진 최동현은 클라우드 인프라 구축과 CI/CD 파이프라인 구현에 전문성을 가지고 있으며, 안정적이고 확장 가능한 시스템 운영 경험이 풍부합니다.",
    keywords: ["DevOps", "클라우드", "AWS", "Docker", "Kubernetes", "CI/CD", "Jenkins", "Terraform", "모니터링", "마이그레이션"],
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

// 자기소개서 컬렉션 생성 및 샘플 데이터
db.createCollection('cover_letters');
db.cover_letters.insertMany([
  {
    user_id: "user1",
    title: "프론트엔드 개발자 자기소개서",
    content: "React와 TypeScript에 대한 깊은 이해와 실무 경험을 바탕으로 사용자 중심의 웹 애플리케이션을 개발하고 싶습니다. ABC 회사에서 2년간 프론트엔드 개발자로 근무하며 E-커머스 웹사이트와 관리자 대시보드를 개발한 경험이 있습니다. 사용자 경험을 개선하여 전환율을 15% 향상시킨 성과를 바탕으로, 귀사의 서비스 발전에 기여하고 싶습니다.",
    job_posting_id: "frontend_dev_2024",
    status: "pending",
    created_at: new Date()
  },
  {
    user_id: "user2",
    title: "백엔드 개발자 자기소개서",
    content: "Python과 FastAPI를 활용한 효율적인 백엔드 시스템 구축 경험을 바탕으로 확장 가능한 서비스를 개발하고 싶습니다. DEF 회사에서 3년간 백엔드 개발자로 근무하며 대규모 E-커머스 플랫폼의 백엔드를 구축했습니다. 마이크로서비스 아키텍처를 설계하여 초당 10만 요청을 처리할 수 있는 시스템을 구축했으며, Redis 캐싱 전략으로 응답 속도를 50% 개선했습니다. 귀사의 기술적 도전과제를 해결하는 데 기여하고 싶습니다.",
    job_posting_id: "backend_dev_2024",
    status: "approved",
    created_at: new Date()
  },
  {
    user_id: "user3",
    title: "UI/UX 디자이너 자기소개서",
    content: "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 것에 관심이 많습니다. JKL 디자인 에이전시에서 2년간 UI 디자이너로 근무하며 모바일 뱅킹 앱 리디자인 프로젝트를 진행했습니다. 사용자 리서치를 통해 UX를 개선하고 접근성 가이드라인을 준수하여 사용자 만족도를 30% 향상시켰습니다. MNO 기업에서는 E-커머스 웹사이트 UX 개선을 통해 전환율을 25% 향상시킨 경험이 있습니다. 귀사의 사용자 경험 향상에 기여하고 싶습니다.",
    job_posting_id: "uiux_designer_2024",
    status: "pending",
    created_at: new Date()
  },
  {
    user_id: "user4",
    title: "데이터 분석가 자기소개서",
    content: "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정에 기여하는 것에 관심이 많습니다. 고려대학교 통계학과와 서울대학교 대학원 데이터사이언스를 전공하여 데이터 분석의 이론적 기반을 다졌습니다. PQR 기업에서 2년간 데이터 분석가로 근무하며 고객 세분화 분석을 통해 매출을 20% 향상시켰습니다. 머신러닝을 활용한 매출 예측 모델을 개발하여 85%의 정확도를 달성했으며, Tableau를 활용한 실시간 대시보드를 구축하여 KPI 모니터링 시스템을 운영했습니다. 귀사의 데이터 기반 의사결정을 지원하고 싶습니다.",
    job_posting_id: "data_analyst_2024",
    status: "pending",
    created_at: new Date()
  },
  {
    user_id: "user5",
    title: "DevOps 엔지니어 자기소개서",
    content: "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 것에 전문성을 가지고 있습니다. STU 기업에서 4년간 시스템 엔지니어로 근무하며 온프레미스 환경에서의 시스템 운영 경험을 쌓았습니다. VWX 스타트업에서는 DevOps 엔지니어로 근무하며 온프레미스에서 AWS로의 전체 시스템 마이그레이션을 성공적으로 완료했습니다. 99.9%의 가용성을 달성하고 운영 비용을 40% 절감했으며, Jenkins와 Docker를 활용한 CI/CD 파이프라인을 구축하여 배포 시간을 80% 단축했습니다. 귀사의 안정적이고 확장 가능한 인프라 구축에 기여하고 싶습니다.",
    job_posting_id: "devops_engineer_2024",
    status: "approved",
    created_at: new Date()
  }
]);

// 포트폴리오 컬렉션 생성 및 샘플 데이터
db.createCollection('portfolios');
db.portfolios.insertMany([
  {
    user_id: "user1",
    title: "React E-커머스 웹사이트",
    description: "React와 TypeScript를 사용한 반응형 E-커머스 웹사이트입니다. 사용자 경험을 개선하여 전환율을 15% 향상시켰으며, 관리자 대시보드와 실시간 데이터 시각화 기능을 포함합니다.",
    github_url: "https://github.com/user1/react-ecommerce",
    demo_url: "https://react-ecommerce-demo.com",
    technologies: ["React", "TypeScript", "Node.js", "Express", "MongoDB", "Chart.js"],
    features: ["반응형 디자인", "실시간 재고 관리", "결제 시스템 연동", "관리자 대시보드", "데이터 시각화"],
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user2",
    title: "FastAPI 마이크로서비스 백엔드",
    description: "FastAPI와 Python을 사용한 마이크로서비스 아키텍처의 백엔드 시스템입니다. 초당 10만 요청을 처리할 수 있으며, Redis 캐싱과 ELK 스택을 활용한 모니터링 시스템을 포함합니다.",
    github_url: "https://github.com/user2/fastapi-microservices",
    demo_url: "https://api-demo.com",
    technologies: ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes", "Apache Kafka"],
    features: ["마이크로서비스 아키텍처", "Redis 캐싱", "실시간 데이터 처리", "모니터링 시스템", "자동 스케일링"],
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user3",
    title: "모바일 뱅킹 앱 UI/UX 디자인",
    description: "사용자 중심의 모바일 뱅킹 앱 UI/UX 디자인 프로젝트입니다. 사용자 리서치를 통해 UX를 개선하고 접근성 가이드라인을 준수하여 사용자 만족도를 30% 향상시켰습니다.",
    github_url: "https://github.com/user3/banking-app-design",
    demo_url: "https://banking-app-demo.com",
    technologies: ["Figma", "Adobe XD", "Principle", "InVision"],
    features: ["사용자 리서치", "UX 개선", "접근성 준수", "프로토타이핑", "A/B 테스트"],
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user4",
    title: "데이터 분석 대시보드",
    description: "Python과 Tableau를 활용한 데이터 분석 대시보드입니다. 고객 세분화 분석과 매출 예측 모델을 포함하며, 실시간 KPI 모니터링 시스템을 구축했습니다.",
    github_url: "https://github.com/user4/data-analytics-dashboard",
    demo_url: "https://dashboard-demo.com",
    technologies: ["Python", "Pandas", "NumPy", "Scikit-learn", "Tableau", "SQL"],
    features: ["고객 세분화", "매출 예측", "실시간 대시보드", "KPI 모니터링", "데이터 시각화"],
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user5",
    title: "클라우드 인프라 자동화",
    description: "AWS와 Terraform을 활용한 클라우드 인프라 자동화 프로젝트입니다. CI/CD 파이프라인과 모니터링 시스템을 구축하여 배포 시간을 80% 단축하고 99.9%의 가용성을 달성했습니다.",
    github_url: "https://github.com/user5/cloud-infrastructure",
    demo_url: "https://infra-demo.com",
    technologies: ["AWS", "Terraform", "Docker", "Kubernetes", "Jenkins", "Prometheus", "Grafana"],
    features: ["인프라 자동화", "CI/CD 파이프라인", "모니터링 시스템", "자동 스케일링", "장애 복구"],
    status: "active",
    created_at: new Date()
  }
]);

print("MongoDB 초기화 완료!"); 