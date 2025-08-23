#!/usr/bin/env python3
"""
프로젝트 최초 실행 시 샘플 데이터 자동 생성 스크립트
- 지원자 데이터 200개 자동 생성
- 채용공고 데이터 자동 생성 (없는 경우)
- 작업 완료 후 자동 삭제
"""

import os
import sys
import json
import random
import requests
import time
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
from bson import ObjectId

# Faker 초기화 (한국어)
fake = Faker('ko_KR')

# MongoDB 연결
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'hireme'

# Flask 서버 URL
FLASK_URL = 'http://localhost:8000'

def check_database_connection():
    """데이터베이스 연결 확인"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # 연결 테스트
        db.command('ping')
        print("✅ MongoDB 연결 성공")
        return db
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

def check_flask_server():
    """Flask 서버 실행 확인"""
    try:
        response = requests.get(f"{FLASK_URL}/api/applicants", timeout=5)
        if response.status_code == 200:
            print("✅ Flask 서버 연결 성공")
            return True
        else:
            print(f"❌ Flask 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask 서버 연결 실패: {e}")
        return False

def check_existing_data(db):
    """기존 데이터 확인"""
    try:
        # 지원자 데이터 확인
        applicants_count = db.applicants.count_documents({})
        job_postings_count = db.job_postings.count_documents({})
        
        print(f"📊 현재 DB 상태:")
        print(f"   - 지원자: {applicants_count}명")
        print(f"   - 채용공고: {job_postings_count}개")
        
        return applicants_count, job_postings_count
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")
        return 0, 0

def generate_job_postings():
    """채용공고 샘플 데이터 생성"""
    job_postings = [
        {
            "title": "함께 성장할 개발팀 신입을 찾습니다",
            "company": "테크스타트업",
            "location": "서울특별시 강남구",
            "department": "개발팀",
            "position": "프론트엔드 개발자",
            "type": "full-time",
            "salary": "연봉 3,500만원 - 4,500만원",
            "experience": "경력",
            "education": "대졸 이상",
            "description": "React, TypeScript를 활용한 웹 애플리케이션 개발",
            "requirements": "JavaScript, React 실무 경험",
            "benefits": "주말보장, 재택가능, 점심식대 지원",
            "deadline": "2024-12-31",
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "전문성을 발휘할 개발팀 인재 모집",
            "company": "테크스타트업",
            "location": "서울특별시 강남구",
            "department": "개발팀",
            "position": "백엔드 개발자",
            "type": "full-time",
            "salary": "연봉 4,000만원 - 6,000만원",
            "experience": "경력",
            "education": "대졸 이상",
            "description": "Node.js, Python을 활용한 서버 개발",
            "requirements": "Node.js, Python 실무 경험",
            "benefits": "주말보장, 재택가능, 점심식대 지원",
            "deadline": "2024-12-31",
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "디자인팀 UI/UX 디자이너 채용",
            "company": "테크스타트업",
            "location": "서울특별시 강남구",
            "department": "디자인팀",
            "position": "UI/UX 디자이너",
            "type": "full-time",
            "salary": "연봉 3,500만원 - 5,000만원",
            "experience": "경력",
            "education": "대졸 이상",
            "description": "사용자 경험을 고려한 UI/UX 디자인",
            "requirements": "Figma, Adobe XD 실무 경험",
            "benefits": "주말보장, 재택가능, 점심식대 지원",
            "deadline": "2024-12-31",
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "혁신을 이끌 마케팅팀를 찾습니다",
            "company": "테크스타트업",
            "location": "서울특별시 강남구",
            "department": "마케팅팀",
            "position": "디지털 마케팅 전문가",
            "type": "full-time",
            "salary": "연봉 3,500만원 - 5,000만원",
            "experience": "경력",
            "education": "대졸 이상",
            "description": "디지털 마케팅 전략 수립 및 실행",
            "requirements": "Google Ads, Facebook Ads 실무 경험",
            "benefits": "주말보장, 재택가능, 점심식대 지원",
            "deadline": "2024-12-31",
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "전문성을 발휘할 기획팀 인재 모집",
            "company": "테크스타트업",
            "location": "서울특별시 강남구",
            "department": "기획팀",
            "position": "프로젝트 매니저",
            "type": "full-time",
            "salary": "연봉 4,500만원 - 6,500만원",
            "experience": "고급",
            "education": "대졸 이상",
            "description": "프로젝트 기획 및 관리",
            "requirements": "프로젝트 관리 경험",
            "benefits": "주말보장, 재택가능, 점심식대 지원",
            "deadline": "2024-12-31",
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    return job_postings

def generate_applicant_data(job_posting_id):
    """지원자 데이터 한 개 생성"""
    # 직무별 기술 스택
    position_skills_map = {
        "프론트엔드 개발자": ["React", "Vue.js", "JavaScript", "TypeScript", "HTML", "CSS", "Webpack", "Next.js"],
        "백엔드 개발자": ["Node.js", "Python", "Java", "Spring Boot", "MySQL", "PostgreSQL", "MongoDB", "Redis"],
        "UI/UX 디자이너": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "Principle"],
        "디지털 마케팅 전문가": ["Google Ads", "Facebook Ads", "GA4", "GTM", "SEO", "SEM"],
        "프로젝트 매니저": ["Jira", "Notion", "Slack", "애자일", "스크럼", "PMP"]
    }
    
    # 기본 정보
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    
    # 직무 정보 (채용공고에서 가져올 예정)
    position = "프론트엔드 개발자"  # 기본값
    department = "개발팀"  # 기본값
    
    # 경력 및 기술
    experience_options = ["신입", "1-3년", "3-5년", "5-7년", "7-10년", "10년 이상"]
    experience = random.choice(experience_options)
    
    available_skills = position_skills_map.get(position, ["기타"])
    num_skills = random.randint(3, min(6, len(available_skills)))
    skills = random.sample(available_skills, num_skills)
    skills_str = ", ".join(skills)
    
    # 텍스트 필드들
    growth_background = fake.text(max_nb_chars=200)
    motivation = fake.text(max_nb_chars=200)
    career_history = fake.text(max_nb_chars=200)
    
    # 분석 관련
    analysis_score = random.randint(60, 95)
    analysis_result = f"{position} 포지션에 적합한 {', '.join(skills[:3])} 기술을 보유하고 있습니다."
    
    # 상태
    status_options = ["pending", "reviewing", "interview_scheduled", "passed", "rejected"]
    status = random.choice(status_options)
    
    # 생성 일시 (최근 30일 내)
    created_at = datetime.now() - timedelta(days=random.randint(0, 30))
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "position": position,
        "department": department,
        "experience": experience,
        "skills": skills_str,
        "growthBackground": growth_background,
        "motivation": motivation,
        "careerHistory": career_history,
        "analysisScore": analysis_score,
        "analysisResult": analysis_result,
        "status": status,
        "job_posting_id": job_posting_id,
        "created_at": created_at
    }

def insert_job_postings(db):
    """채용공고 데이터 삽입"""
    try:
        existing_count = db.job_postings.count_documents({})
        if existing_count > 0:
            print(f"📋 채용공고가 이미 {existing_count}개 존재합니다. 건너뜁니다.")
            return list(db.job_postings.find())
        
        job_postings = generate_job_postings()
        result = db.job_postings.insert_many(job_postings)
        print(f"✅ 채용공고 {len(result.inserted_ids)}개 생성 완료")
        
        # 생성된 채용공고 반환
        return list(db.job_postings.find())
    except Exception as e:
        print(f"❌ 채용공고 생성 실패: {e}")
        return []

def insert_applicants_via_api(job_posting_ids, target_count=200):
    """API를 통해 지원자 데이터 삽입"""
    try:
        print(f"👥 {target_count}명의 지원자 데이터 생성 시작...")
        
        success_count = 0
        fail_count = 0
        batch_size = 10
        
        for i in range(0, target_count, batch_size):
            batch_count = min(batch_size, target_count - i)
            print(f"📦 배치 {i//batch_size + 1} 처리 중... ({i+1}-{i+batch_count})")
            
            for j in range(batch_count):
                try:
                    # 랜덤하게 채용공고 선택
                    job_posting_id = random.choice(job_posting_ids)
                    
                    # 지원자 데이터 생성
                    applicant_data = generate_applicant_data(str(job_posting_id))
                    
                    # API 호출
                    response = requests.post(
                        f"{FLASK_URL}/api/applicants",
                        json=applicant_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        success_count += 1
                    else:
                        fail_count += 1
                        print(f"  ❌ {i+j+1}: API 응답 오류 {response.status_code}")
                        
                except Exception as e:
                    fail_count += 1
                    print(f"  ❌ {i+j+1}: {str(e)}")
                
                # 요청 간 간격
                time.sleep(0.1)
            
            # 배치 간 간격
            time.sleep(1)
            print(f"배치 완료: 성공 {success_count}, 실패 {fail_count}")
        
        print(f"\n✅ 지원자 데이터 생성 완료:")
        print(f"   - 성공: {success_count}명")
        print(f"   - 실패: {fail_count}명")
        print(f"   - 총 처리: {target_count}명")
        
        return success_count
        
    except Exception as e:
        print(f"❌ 지원자 데이터 생성 실패: {e}")
        return 0

def verify_data(db):
    """생성된 데이터 검증"""
    try:
        applicants_count = db.applicants.count_documents({})
        job_postings_count = db.job_postings.count_documents({})
        
        print(f"\n🔍 데이터 검증 결과:")
        print(f"   - 지원자: {applicants_count}명")
        print(f"   - 채용공고: {job_postings_count}개")
        
        if applicants_count >= 200 and job_postings_count >= 5:
            print("✅ 샘플 데이터 생성이 성공적으로 완료되었습니다!")
            return True
        else:
            print("⚠️ 샘플 데이터 생성이 완전하지 않습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 데이터 검증 실패: {e}")
        return False

def cleanup_script():
    """스크립트 자동 삭제"""
    try:
        script_path = os.path.abspath(__file__)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"🗑️ 스크립트 자동 삭제 완료: {script_path}")
    except Exception as e:
        print(f"⚠️ 스크립트 삭제 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 프로젝트 샘플 데이터 자동 생성 시작!")
    print("=" * 50)
    
    # 1. 데이터베이스 연결 확인
    db = check_database_connection()
    if db is None:
        print("❌ 데이터베이스 연결 실패로 종료합니다.")
        return False
    
    # 2. Flask 서버 확인
    if not check_flask_server():
        print("❌ Flask 서버 연결 실패로 종료합니다.")
        return False
    
    # 3. 기존 데이터 확인
    existing_applicants, existing_job_postings = check_existing_data(db)
    
    # 4. 충분한 데이터가 있으면 스크립트 삭제 후 종료
    if existing_applicants >= 200 and existing_job_postings >= 5:
        print("✅ 충분한 샘플 데이터가 이미 존재합니다.")
        print("🎉 프로젝트가 준비되었습니다!")
        print("🗑️ 초기화 스크립트를 자동으로 삭제합니다...")
        cleanup_script()
        return True
    
    # 5. 채용공고 데이터 생성
    job_postings = insert_job_postings(db)
    if len(job_postings) == 0:
        print("❌ 채용공고 생성 실패로 종료합니다.")
        return False
    
    # 6. 지원자 데이터 생성
    job_posting_ids = [str(job['_id']) for job in job_postings]
    target_applicants = max(0, 200 - existing_applicants)
    
    if target_applicants > 0:
        success_count = insert_applicants_via_api(job_posting_ids, target_applicants)
        if success_count == 0:
            print("❌ 지원자 데이터 생성 실패로 종료합니다.")
            return False
    else:
        print("✅ 충분한 지원자 데이터가 이미 존재합니다.")
    
    # 7. 데이터 검증
    if verify_data(db):
        print("\n🎉 프로젝트 샘플 데이터 생성이 완료되었습니다!")
        print("이제 지원자 관리 시스템을 사용할 수 있습니다.")
        
        # 8. 스크립트 자동 삭제
        cleanup_script()
        return True
    else:
        print("❌ 데이터 검증 실패")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")
            sys.exit(0)
        else:
            print("\n❌ 작업 중 오류가 발생했습니다.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)
