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
        "description": f"""
{company}에서 {position}를 모집합니다.

[주요 업무]
- {position} 관련 개발 및 운영 업무
- 서비스 기획부터 개발, 배포까지 전 과정 참여
- 코드 리뷰 및 기술 문서 작성
- 팀원들과의 협업을 통한 프로젝트 진행

[자격 요건]
- {random.choice(EDUCATION_LEVELS)} 이상
- 관련 분야 경험자 우대
- 새로운 기술에 대한 학습 의지

[우대 사항]
- 관련 프로젝트 경험
- 오픈소스 기여 경험
- 팀 리딩 경험
        """.strip(),
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
        "school": fake.company() + " 대학교",
        "major": random.choice(["컴퓨터공학과", "소프트웨어학과", "전자공학과", "정보통신학과", "산업공학과", "경영학과"]),
        "graduation_year": random.randint(2015, 2023)
    }
    
    # 경력 정보
    career_history = []
    if experience_years > 0:
        for i in range(random.randint(1, min(3, experience_years))):
            career_history.append({
                "company": random.choice(COMPANY_NAMES),
                "position": random.choice(POSITIONS),
                "duration": f"{random.randint(1, 36)}개월",
                "description": f"{random.choice(POSITIONS)} 업무 담당"
            })
    
    # 포트폴리오 프로젝트
    projects = []
    for i in range(random.randint(1, 4)):
        projects.append({
            "name": f"프로젝트 {i+1}",
            "description": fake.text(max_nb_chars=200),
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
        "notes": fake.text(max_nb_chars=300) if random.choice([True, False]) else "",
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
