#!/usr/bin/env python3
import pymongo
import json
import random
from datetime import datetime, timedelta
from bson import ObjectId

def generate_sample_applicants():
    """100개의 샘플 지원자 데이터를 생성합니다."""
    
    # 채용공고 ID 목록 로드
    with open('job_posting_ids.json', 'r', encoding='utf-8') as f:
        job_posting_ids = json.load(f)
    
    # 샘플 데이터 템플릿
    names = [
        "김민수", "이영희", "박준호", "정수진", "최동훈", "한지민", "오세훈", "임나영",
        "강태현", "윤소영", "조민기", "신예린", "배성호", "류지은", "홍준표", "문채원",
        "서민석", "안혜진", "장우진", "노수빈", "구자현", "송미래", "유정호", "전소희",
        "남궁민", "황보라", "독고준", "제갈성", "사공혜진", "선우진", "동방미", "서문호",
        "남궁수", "황보민", "독고영", "제갈준", "사공진", "선우희", "동방수", "서문영",
        "김도현", "이서연", "박지훈", "정유진", "최준영", "한소미", "오태준", "임지혜",
        "강민호", "윤채영", "조성민", "신지원", "배준수", "류혜진", "홍민기", "문서연",
        "서태호", "안지민", "장성호", "노예진", "구민수", "송지혜", "유태현", "전민영",
        "김성준", "이지은", "박민호", "정서영", "최지훈", "한예진", "오민석", "임수연",
        "강지원", "윤태호", "조혜진", "신민수", "배지은", "류성호", "홍예영", "문태준",
        "서지혜", "안민호", "장예진", "노성수", "구지은", "송태호", "유혜영", "전민석",
        "김예진", "이태호", "박지혜", "정민수", "최서영", "한성호", "오예진", "임태준",
        "강혜영", "윤민석", "조지은", "신태호"
    ]
    
    positions = [
        "프론트엔드 개발자", "백엔드 개발자", "풀스택 개발자", "모바일 개발자", 
        "데이터 사이언티스트", "DevOps 엔지니어", "QA 엔지니어", "UI/UX 디자이너",
        "프로덕트 매니저", "영업 담당자", "마케팅 전문가", "HR 담당자"
    ]
    
    skills_pool = [
        ["JavaScript", "React", "TypeScript", "HTML", "CSS"],
        ["Python", "Django", "FastAPI", "PostgreSQL", "Redis"],
        ["Java", "Spring Boot", "MySQL", "Docker", "Kubernetes"],
        ["Node.js", "Express", "MongoDB", "AWS", "Git"],
        ["Vue.js", "Nuxt.js", "Sass", "Webpack", "Jest"],
        ["React Native", "Flutter", "Swift", "Kotlin", "Firebase"],
        ["Python", "Pandas", "NumPy", "TensorFlow", "Jupyter"],
        ["AWS", "Docker", "Kubernetes", "Jenkins", "Terraform"],
        ["Selenium", "Postman", "Jest", "Cypress", "JUnit"],
        ["Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator"],
        ["Jira", "Slack", "Notion", "Analytics", "Excel"],
        ["Salesforce", "HubSpot", "Excel", "PowerPoint", "CRM"]
    ]
    
    experiences = ["신입", "1년", "2년", "3년", "4년", "5년", "6년", "7년", "8년", "9년", "10년 이상"]
    
    statuses = ["지원", "서류합격", "면접대기", "최종합격", "서류불합격", "보류"]
    
    # 이메일 도메인
    email_domains = ["gmail.com", "naver.com", "kakao.com", "hanmail.net", "outlook.com"]
    
    applicants = []
    
    for i in range(100):
        name = random.choice(names)
        position = random.choice(positions)
        skill_set = random.choice(skills_pool)
        experience = random.choice(experiences)
        status = random.choice(statuses)
        job_posting_id = random.choice(job_posting_ids)
        
        # 이메일 생성
        email_prefix = name.replace(" ", "").lower() + str(random.randint(1000, 9999))
        email = f"{email_prefix}@{random.choice(email_domains)}"
        
        # 전화번호 생성
        phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        # 생성일 (최근 30일 내)
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        applicant = {
            "_id": str(ObjectId()),
            "name": name,
            "email": email,
            "phone": phone,
            "position": position,
            "experience": experience,
            "skills": ", ".join(skill_set[:random.randint(3, 5)]),
            "status": status,
            "job_posting_id": job_posting_id,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "analysisScore": random.randint(60, 95),
            "department": random.choice(["개발팀", "디자인팀", "마케팅팀", "영업팀", "인사팀"]),
            "growthBackground": f"{name}의 성장 배경 및 학습 경험",
            "motivation": f"{position} 직무에 대한 {name}의 지원 동기",
            "careerHistory": f"{experience} 경력의 {name}의 주요 업무 경험",
            "resume_id": str(ObjectId()),
            "cover_letter_id": str(ObjectId()) if random.choice([True, False]) else None,
            "portfolio_id": str(ObjectId()) if random.choice([True, False]) else None
        }
        
        applicants.append(applicant)
    
    # JSON 파일로 저장
    with open('sample_applicants.json', 'w', encoding='utf-8') as f:
        json.dump(applicants, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(applicants)}개의 샘플 지원자 데이터가 생성되었습니다.")
    print("📁 파일 저장: sample_applicants.json")
    
    # 통계 출력
    print("\n📊 생성된 데이터 통계:")
    print(f"- 총 지원자 수: {len(applicants)}")
    
    # 직무별 분포
    position_count = {}
    for applicant in applicants:
        pos = applicant['position']
        position_count[pos] = position_count.get(pos, 0) + 1
    
    print("\n📋 직무별 분포:")
    for pos, count in sorted(position_count.items()):
        print(f"  - {pos}: {count}명")
    
    # 상태별 분포
    status_count = {}
    for applicant in applicants:
        status = applicant['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("\n📈 상태별 분포:")
    for status, count in sorted(status_count.items()):
        print(f"  - {status}: {count}명")
    
    # 채용공고별 분포
    job_count = {}
    for applicant in applicants:
        job_id = applicant['job_posting_id']
        job_count[job_id] = job_count.get(job_id, 0) + 1
    
    print(f"\n🎯 채용공고별 분포: {len(job_count)}개 공고에 골고루 분배")
    print(f"  - 평균 지원자 수: {100/len(job_count):.1f}명")
    print(f"  - 최대 지원자 수: {max(job_count.values())}명")
    print(f"  - 최소 지원자 수: {min(job_count.values())}명")
    
    return applicants

if __name__ == "__main__":
    generate_sample_applicants()
