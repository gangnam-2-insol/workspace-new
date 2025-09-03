#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uuid

# MongoDB 연결 설정
MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "hireme"

fake = Faker(['ko_KR'])

# 실제적인 내용 생성 함수들
def generate_realistic_project_description():
    """실제적인 프로젝트 설명 생성"""
    project_templates = [
        "React와 Node.js를 활용한 풀스택 웹 애플리케이션 개발. 사용자 인증, 데이터 관리, 실시간 채팅 기능을 구현했습니다.",
        "Python Django와 PostgreSQL을 활용한 이커머스 플랫폼 구축. 결제 시스템, 재고 관리, 주문 처리 기능을 개발했습니다.",
        "Vue.js와 Spring Boot를 활용한 기업용 관리 시스템 개발. 직원 관리, 프로젝트 추적, 보고서 생성 기능을 구현했습니다.",
        "Flutter를 활용한 크로스 플랫폼 모바일 애플리케이션 개발. GPS 기반 위치 서비스와 실시간 알림 기능을 구현했습니다.",
        "Python과 TensorFlow를 활용한 머신러닝 모델 개발. 이미지 분류 및 예측 분석 시스템을 구축했습니다.",
        "AWS와 Docker를 활용한 클라우드 기반 마이크로서비스 아키텍처 구축. 자동화된 배포 및 모니터링 시스템을 개발했습니다.",
        "TypeScript와 Next.js를 활용한 SEO 최적화된 웹사이트 개발. 서버 사이드 렌더링과 정적 사이트 생성 기능을 구현했습니다.",
        "MongoDB와 Express.js를 활용한 RESTful API 서버 개발. 데이터 검증, 인증, 권한 관리 기능을 구현했습니다."
    ]
    return random.choice(project_templates)

def generate_realistic_notes():
    """실제적인 노트 생성"""
    notes_templates = [
        "기술적 역량이 우수하며 팀워크 능력도 뛰어납니다. 새로운 기술 학습에 적극적이고 문제 해결 능력이 뛰어납니다.",
        "실무 경험이 풍부하고 프로젝트 관리 능력이 우수합니다. 커뮤니케이션 스킬과 리더십을 겸비하고 있습니다.",
        "코딩 스킬과 알고리즘 이해도가 높습니다. 코드 품질과 성능 최적화에 대한 이해가 깊습니다.",
        "사용자 경험 개선에 대한 관심이 높고 디자인 감각이 뛰어납니다. 프론트엔드와 백엔드 개발 경험이 균형있습니다.",
        "데이터 분석과 머신러닝에 대한 전문성이 뛰어납니다. 비즈니스 인사이트 도출 능력이 우수합니다.",
        "DevOps와 클라우드 인프라 관리 경험이 풍부합니다. 자동화와 모니터링 시스템 구축에 능숙합니다.",
        "품질 보증과 테스트 자동화에 대한 이해가 깊습니다. 효율적인 테스트 프로세스 구축 경험이 있습니다.",
        "모바일 앱 개발 경험이 풍부하고 크로스 플랫폼 개발에 능숙합니다. 사용자 인터페이스 설계 능력이 우수합니다."
    ]
    return random.choice(notes_templates)

def generate_realistic_job_description(position):
    """실제적인 채용공고 설명 생성"""
    description_templates = {
        "프론트엔드 개발자": [
            "사용자 경험을 중시하는 웹 서비스 개발을 담당합니다. React, Vue.js 등 모던 프레임워크를 활용하여 반응형 웹 애플리케이션을 개발하고, 성능 최적화 및 웹 접근성 개선에 기여합니다.",
            "대규모 웹 서비스의 프론트엔드 개발을 담당합니다. TypeScript, Next.js 등을 활용한 현대적인 웹 개발 경험을 바탕으로 사용자 친화적인 인터페이스를 구축합니다.",
            "모바일 퍼스트 접근법으로 반응형 웹사이트 및 SPA 개발을 담당합니다. 최신 웹 기술 트렌드를 반영하여 사용자 경험을 향상시키는 역할을 수행합니다."
        ],
        "백엔드 개발자": [
            "안정적이고 확장 가능한 서버 시스템 개발을 담당합니다. Java, Spring Boot, Node.js 등을 활용한 RESTful API 설계 및 데이터베이스 최적화를 수행합니다.",
            "마이크로서비스 아키텍처 기반의 백엔드 시스템 구축을 담당합니다. 대용량 트래픽 처리와 데이터베이스 성능 최적화에 중점을 두고 개발합니다.",
            "클라우드 환경에서의 서버 인프라 구축 및 관리를 담당합니다. 보안과 성능을 고려한 안정적인 백엔드 시스템을 개발합니다."
        ],
        "풀스택 개발자": [
            "웹 애플리케이션의 전체 개발 라이프사이클을 담당합니다. 프론트엔드와 백엔드 개발 경험을 바탕으로 사용자 요구사항부터 배포까지 전체 과정을 관리합니다.",
            "풀스택 개발팀에서 다양한 기술 스택을 활용한 프로젝트를 담당합니다. React, Node.js, Python, Django 등을 활용한 웹 서비스 개발을 수행합니다.",
            "독립적인 프로젝트 진행이 가능한 풀스택 개발자를 모집합니다. 사용자 요구사항 분석부터 최종 배포까지 전체 과정을 담당할 수 있는 역량을 보유해야 합니다."
        ],
        "데이터 분석가": [
            "비즈니스 데이터 분석 및 인사이트 도출을 담당합니다. Python, R, SQL을 활용한 데이터 처리 및 머신러닝 모델 개발을 수행합니다.",
            "대시보드 구축 및 데이터 시각화를 담당합니다. Tableau, Power BI 등을 활용하여 비즈니스 의사결정을 지원하는 분석 결과를 제공합니다.",
            "예측 모델링 및 통계 분석을 담당합니다. 빅데이터 처리 및 분석을 통해 비즈니스 성과 향상에 기여하는 역할을 수행합니다."
        ],
        "QA 엔지니어": [
            "웹 애플리케이션의 품질 보증 및 테스트 자동화를 담당합니다. Selenium, Cypress 등을 활용한 효율적인 테스트 프로세스를 구축합니다.",
            "사용자 관점에서의 테스트 설계 및 실행을 담당합니다. 기능 테스트, 성능 테스트, 보안 테스트를 통해 제품의 신뢰성을 향상시킵니다.",
            "지속적 통합 환경에서의 테스트 자동화를 담당합니다. CI/CD 파이프라인에 통합된 테스트 프로세스를 구축하여 개발 효율성을 높입니다."
        ]
    }
    
    templates = description_templates.get(position, [
        "해당 분야의 전문성을 바탕으로 안정적인 업무 수행을 담당합니다. 실무 경험을 바탕으로 성과를 창출할 수 있는 역량을 보유해야 합니다.",
        "관련 업무에 대한 깊은 이해를 바탕으로 다양한 프로젝트에 참여합니다. 전문성을 바탕으로 한 문제 해결 능력을 보유해야 합니다.",
        "실무 경험을 바탕으로 안정적인 업무 수행을 담당합니다. 해당 분야의 전문성을 바탕으로 성과를 창출할 수 있는 역량을 보유해야 합니다."
    ])
    
    return random.choice(templates)

def generate_realistic_school_name():
    """실제적인 학교 이름 생성"""
    school_names = [
        "서울대학교", "연세대학교", "고려대학교", "한양대학교", "성균관대학교",
        "중앙대학교", "경희대학교", "서강대학교", "동국대학교", "건국대학교",
        "홍익대학교", "숙명여자대학교", "이화여자대학교", "서울시립대학교", "국민대학교",
        "단국대학교", "아주대학교", "인하대학교", "부산대학교", "전남대학교"
    ]
    return random.choice(school_names)

def generate_realistic_major(position):
    """실제적인 전공 생성"""
    major_templates = {
        "프론트엔드 개발자": [
            "컴퓨터공학과", "소프트웨어학과", "정보통신공학과", "컴퓨터정보학과", "웹공학과"
        ],
        "백엔드 개발자": [
            "컴퓨터공학과", "소프트웨어학과", "정보통신공학과", "컴퓨터정보학과", "전자공학과"
        ],
        "풀스택 개발자": [
            "컴퓨터공학과", "소프트웨어학과", "정보통신공학과", "컴퓨터정보학과", "전자공학과"
        ],
        "데이터 분석가": [
            "통계학과", "수학과", "산업공학과", "경영학과", "컴퓨터공학과"
        ],
        "QA 엔지니어": [
            "컴퓨터공학과", "소프트웨어학과", "정보통신공학과", "컴퓨터정보학과", "전자공학과"
        ]
    }
    
    templates = major_templates.get(position, [
        "컴퓨터공학과", "소프트웨어학과", "정보통신공학과", "컴퓨터정보학과", "전자공학과"
    ])
    
    return random.choice(templates)

def generate_realistic_career_description(position):
    """실제적인 경력 설명 생성"""
    career_description_templates = {
        "프론트엔드 개발자": [
            "React, Vue.js 기반 웹 애플리케이션 개발 및 유지보수",
            "TypeScript, Next.js를 활용한 대규모 프로젝트 참여",
            "반응형 웹사이트 및 SPA 개발 및 성능 최적화",
            "웹 접근성 및 사용자 경험 개선 프로젝트 진행"
        ],
        "백엔드 개발자": [
            "Java, Spring Boot 기반 서버 애플리케이션 개발",
            "Node.js, Express를 활용한 RESTful API 설계 및 구현",
            "데이터베이스 설계 및 성능 최적화",
            "마이크로서비스 아키텍처 기반 시스템 구축"
        ],
        "풀스택 개발자": [
            "React, Node.js 스택을 활용한 풀스택 웹 애플리케이션 개발",
            "Vue.js, Python, FastAPI를 활용한 웹 서비스 구축",
            "TypeScript, Next.js, Prisma를 활용한 현대적인 웹 개발",
            "전체 개발 라이프사이클 관리 및 프로젝트 리딩"
        ],
        "데이터 분석가": [
            "Python, R, SQL을 활용한 데이터 분석 및 시각화",
            "머신러닝 모델 개발 및 비즈니스 인사이트 도출",
            "Tableau, Power BI를 활용한 대시보드 구축",
            "통계 분석 및 예측 모델링 프로젝트 진행"
        ],
        "QA 엔지니어": [
            "웹 애플리케이션 테스트 자동화 및 품질 보증",
            "Selenium, Cypress를 활용한 효율적인 테스트 프로세스 구축",
            "기능 테스트, 성능 테스트, 보안 테스트 수행",
            "CI/CD 파이프라인에 통합된 테스트 자동화 구축"
        ]
    }
    
    templates = career_description_templates.get(position, [
        "해당 분야 실무 업무 담당 및 프로젝트 진행",
        "관련 기술 스택을 활용한 개발 및 운영 업무",
        "팀 협업을 통한 프로젝트 성과 창출",
        "새로운 기술 학습 및 적용을 통한 업무 개선"
    ])
    
    return random.choice(templates)

# 기술 스택 목록
TECH_STACKS = [
    "Python", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Node.js", 
    "Express", "Django", "Flask", "FastAPI", "Spring Boot", "Java", "C++", "C#", 
    "Go", "Rust", "PHP", "Laravel", "Ruby", "Rails", "MySQL", "PostgreSQL", 
    "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", 
    "Jenkins", "CI/CD", "Linux", "Nginx", "Apache", "GraphQL", "REST API", 
    "Microservices", "Machine Learning", "TensorFlow", "PyTorch", "Data Science", 
    "Blockchain", "Solidity", "Unity", "Unreal Engine", "Android", "iOS", "Flutter", 
    "React Native", "Xamarin", "HTML", "CSS", "SASS", "LESS", "Bootstrap", 
    "Tailwind CSS", "Material-UI", "Ant Design", "Webpack", "Vite", "Babel", 
    "ESLint", "Prettier", "Jest", "Cypress", "Selenium", "Postman"
]

# 직무 목록
POSITIONS = [
    "프론트엔드 개발자", "백엔드 개발자", "풀스택 개발자", "모바일 개발자", 
    "데이터 사이언티스트", "머신러닝 엔지니어", "DevOps 엔지니어", "클라우드 엔지니어",
    "UI/UX 디자이너", "프로덕트 매니저", "데이터 엔지니어", "보안 엔지니어",
    "게임 개발자", "블록체인 개발자", "QA 엔지니어", "시스템 관리자"
]

# 회사 이름 목록
COMPANY_NAMES = [
    "네이버", "카카오", "라인", "쿠팡", "배달의민족", "토스", "당근마켓", 
    "야놀자", "마켓컬리", "원티드", "리디", "버킷플레이스", "직방", 
    "스타트업A", "테크컴퍼니B", "이노베이션C", "디지털솔루션D"
]

# 학력 목록
EDUCATION_LEVELS = ["고등학교 졸업", "전문대 졸업", "대학교 졸업", "석사", "박사"]

# 경력 수준
EXPERIENCE_LEVELS = ["신입", "1년차", "2년차", "3년차", "4년차", "5년차", "6년차", "7년차", "8년차", "9년차", "10년차+"]

# 지원 상태
APPLICATION_STATUSES = ["지원완료", "서류검토", "서류합격", "면접대기", "면접진행", "최종합격", "서류불합격", "면접불합격", "보류"]

async def clear_collections():
    """기존 데이터 삭제"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("🗑️ 기존 데이터 삭제 중...")
    
    # 기존 컬렉션 삭제
    await db.job_postings.delete_many({})
    await db.applicants.delete_many({})
    
    print("✅ 기존 데이터 삭제 완료")
    
    return client, db

def generate_job_posting():
    """채용공고 생성"""
    company = random.choice(COMPANY_NAMES)
    position = random.choice(POSITIONS)
    
    # 해당 직무에 맞는 기술 스택 선택
    relevant_techs = []
    if "프론트엔드" in position:
        relevant_techs = ["JavaScript", "TypeScript", "React", "Vue.js", "Angular", "HTML", "CSS", "SASS"]
    elif "백엔드" in position:
        relevant_techs = ["Python", "Java", "Node.js", "Spring Boot", "Django", "Flask", "MySQL", "PostgreSQL", "MongoDB"]
    elif "풀스택" in position:
        relevant_techs = ["JavaScript", "TypeScript", "React", "Node.js", "Python", "Django", "MySQL", "MongoDB"]
    elif "모바일" in position:
        relevant_techs = ["Android", "iOS", "Flutter", "React Native", "Java", "Swift", "Kotlin"]
    elif "데이터" in position:
        relevant_techs = ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Data Science", "SQL", "R"]
    elif "DevOps" in position or "클라우드" in position:
        relevant_techs = ["Docker", "Kubernetes", "AWS", "Azure", "Jenkins", "CI/CD", "Linux"]
    else:
        relevant_techs = random.sample(TECH_STACKS, random.randint(3, 8))
    
    required_skills = random.sample(relevant_techs, min(len(relevant_techs), random.randint(3, 6)))
    preferred_skills = random.sample([tech for tech in relevant_techs if tech not in required_skills], 
                                   min(len(relevant_techs) - len(required_skills), random.randint(2, 4)))
    
    # 급여 범위 설정
    base_salary = random.randint(3000, 8000) * 10000  # 3천만원 ~ 8천만원
    salary_range = f"{base_salary//10000}만원 ~ {(base_salary + random.randint(500, 2000) * 10000)//10000}만원"
    
    return {
        "_id": ObjectId(),
        "title": f"{company} {position} 채용",
        "company": company,
        "position": position,
        "department": random.choice(["개발팀", "기술팀", "IT팀", "서비스팀", "플랫폼팀", "인프라팀"]),
        "employment_type": random.choice(["정규직", "계약직", "인턴"]),
        "experience_level": random.choice(["신입", "경력 1~3년", "경력 3~5년", "경력 5년+", "경력무관"]),
        "location": random.choice(["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종", "원격근무"]),
        "salary_range": salary_range,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "description": generate_realistic_job_description(position),
        "benefits": [
            "4대보험 완비",
            "연차 자유 사용",
            "교육비 지원",
            "도서 구입비 지원",
            "건강검진비 지원",
            "야근식대 제공",
            "자유로운 근무 환경",
            "최신 장비 제공"
        ],
        "application_deadline": datetime.now() + timedelta(days=random.randint(7, 60)),
        "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
        "updated_at": datetime.now(),
        "status": "active",
        "views": random.randint(50, 1000),
        "applications_count": 0  # 나중에 지원자 수로 업데이트
    }

def generate_applicant(job_posting_ids):
    """지원자 생성"""
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    
    # 랜덤하게 채용공고 선택
    job_posting_id = random.choice(job_posting_ids)
    
    # 나이와 경력 생성
    age = random.randint(22, 45)
    experience_years = max(0, age - 22 - random.randint(0, 4))
    
    # 기술 스택 생성
    skills = random.sample(TECH_STACKS, random.randint(3, 12))
    
    # 학력 정보
    education = {
        "level": random.choice(EDUCATION_LEVELS),
        "school": generate_realistic_school_name(),
        "major": generate_realistic_major(position),
        "graduation_year": random.randint(2015, 2023)
    }
    
    # 경력 정보
    career_history = []
    if experience_years > 0:
        for i in range(random.randint(1, min(3, experience_years))):
            career_history.append({
                "company": random.choice(COMPANY_NAMES),
                "position": position,
                "duration": f"{random.randint(1, 36)}개월",
                "description": generate_realistic_career_description(position)
            })
    
    # 포트폴리오 프로젝트
    projects = []
    for i in range(random.randint(1, 4)):
        projects.append({
            "name": f"프로젝트 {i+1}",
            "description": generate_realistic_project_description(),
            "tech_stack": random.sample(skills, min(len(skills), random.randint(2, 5))),
            "url": fake.url() if random.choice([True, False]) else None,
            "github_url": f"https://github.com/{fake.user_name()}/{fake.word()}" if random.choice([True, False]) else None
        })
    
    # 점수 생성 (실제로는 AI가 분석해서 생성)
    scores = {
        "resume_score": random.randint(60, 100),
        "cover_letter_score": random.randint(60, 100),
        "portfolio_score": random.randint(60, 100),
        "skill_match_score": random.randint(50, 100),
        "experience_score": min(100, experience_years * 10 + random.randint(0, 20)),
        "overall_score": 0
    }
    scores["overall_score"] = sum(scores.values()) // len(scores)
    
    return {
        "_id": ObjectId(),
        "job_posting_id": job_posting_id,
        "personal_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "age": age,
            "gender": random.choice(["남성", "여성"]),
            "address": fake.address()
        },
        "education": education,
        "career_history": career_history,
        "experience_years": experience_years,
        "skills": skills,
        "projects": projects,
        "desired_position": random.choice(POSITIONS),
        "desired_salary": random.randint(3000, 7000) * 10000,
        "application_status": random.choice(APPLICATION_STATUSES),
        "application_date": datetime.now() - timedelta(days=random.randint(1, 30)),
        "resume_url": f"https://storage.example.com/resumes/{uuid.uuid4()}.pdf",
        "cover_letter_url": f"https://storage.example.com/covers/{uuid.uuid4()}.pdf",
        "portfolio_url": f"https://portfolio.example.com/{fake.user_name()}" if random.choice([True, False]) else None,
        "github_url": f"https://github.com/{fake.user_name()}" if random.choice([True, False]) else None,
        "linkedin_url": f"https://linkedin.com/in/{fake.user_name()}" if random.choice([True, False]) else None,
        "scores": scores,
                    "notes": generate_realistic_notes() if random.choice([True, False]) else "",
        "interview_date": None,
        "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
        "updated_at": datetime.now()
    }

async def generate_sample_data():
    """샘플 데이터 생성"""
    client, db = await clear_collections()
    
    try:
        print("📝 채용공고 생성 중...")
        
        # 1. 채용공고 7개 생성
        job_postings = []
        for i in range(7):
            job_posting = generate_job_posting()
            job_postings.append(job_posting)
            print(f"   {i+1}/7: {job_posting['company']} - {job_posting['position']}")
        
        # 채용공고 DB에 삽입
        await db.job_postings.insert_many(job_postings)
        job_posting_ids = [jp["_id"] for jp in job_postings]
        
        print("✅ 채용공고 생성 완료")
        print(f"📊 지원자 300명 생성 중...")
        
        # 2. 지원자 300명 생성
        applicants = []
        for i in range(300):
            applicant = generate_applicant(job_posting_ids)
            applicants.append(applicant)
            
            if (i + 1) % 50 == 0:
                print(f"   {i+1}/300 완료...")
        
        # 지원자 DB에 삽입
        await db.applicants.insert_many(applicants)
        
        print("✅ 지원자 생성 완료")
        
        # 3. 채용공고별 지원자 수 업데이트
        print("📈 채용공고별 지원자 수 업데이트 중...")
        for job_posting_id in job_posting_ids:
            count = await db.applicants.count_documents({"job_posting_id": job_posting_id})
            await db.job_postings.update_one(
                {"_id": job_posting_id},
                {"$set": {"applications_count": count}}
            )
        
        print("✅ 업데이트 완료")
        
        # 4. 통계 출력
        print("\n📊 생성된 데이터 통계:")
        print(f"   채용공고: {await db.job_postings.count_documents({})}개")
        print(f"   지원자: {await db.applicants.count_documents({})}명")
        
        print("\n📋 채용공고별 지원자 수:")
        async for job_posting in db.job_postings.find():
            count = await db.applicants.count_documents({"job_posting_id": job_posting["_id"]})
            print(f"   {job_posting['company']} - {job_posting['position']}: {count}명")
        
        print("\n🎯 지원 상태별 통계:")
        for status in APPLICATION_STATUSES:
            count = await db.applicants.count_documents({"application_status": status})
            if count > 0:
                print(f"   {status}: {count}명")
        
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 DB 샘플 데이터 재생성 시작...")
    asyncio.run(generate_sample_data())
    print("🎉 DB 샘플 데이터 재생성 완료!")
