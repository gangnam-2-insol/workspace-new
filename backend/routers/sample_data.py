from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random
from faker import Faker
import os
import pandas as pd
import io
from bson import ObjectId

router = APIRouter(prefix="/api/sample", tags=["샘플 데이터"])

# Faker 초기화 (한국어)
fake = Faker('ko_KR')

# MongoDB 연결 의존성
def get_database():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    return client.hireme

@router.post("/generate-applicants")
async def generate_sample_applicants(
    data: Dict[str, Any],
    db: AsyncIOMotorClient = Depends(get_database)
):
    """샘플 지원자 데이터 생성"""
    try:
        count = data.get('count', 50)
        
        # 기존 채용공고 ID 목록 가져오기
        job_postings = await db.job_postings.find({}, {"_id": 1}).to_list(100)
        job_posting_ids = [str(job["_id"]) for job in job_postings]
        
        # 채용공고가 없으면 오류 반환
        if not job_posting_ids:
            raise HTTPException(
                status_code=400, 
                detail="지원자를 생성하기 전에 먼저 채용공고를 생성해주세요. 지원자는 반드시 채용공고에 소속되어야 합니다."
            )
        
        # 지원자 데이터 생성
        applicants = []
        positions = ["프론트엔드 개발자", "백엔드 개발자", "UI/UX 디자이너", "프로젝트 매니저", "디지털 마케팅 전문가"]
        departments = ["개발팀", "디자인팀", "마케팅팀", "기획팀", "영업팀"]
        experiences = ["신입", "1-3년", "3-5년", "5-7년", "7년 이상"]
        statuses = ["pending", "reviewing", "interview_scheduled", "passed", "rejected"]
        
        # 지원자를 채용공고에 균등하게 분배
        for i in range(count):
            position = random.choice(positions)
            department = random.choice(departments)
            experience = random.choice(experiences)
            status = random.choice(statuses)
            
            # 기술 스킬 생성
            skills_map = {
                "프론트엔드 개발자": ["JavaScript", "React", "Vue.js", "TypeScript", "HTML", "CSS"],
                "백엔드 개발자": ["Python", "Node.js", "Java", "Spring Boot", "MySQL", "MongoDB"],
                "UI/UX 디자이너": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator"],
                "프로젝트 매니저": ["Jira", "Confluence", "Slack", "Trello", "MS Project"],
                "디지털 마케팅 전문가": ["Google Analytics", "Facebook Ads", "Google Ads", "SEO", "Content Marketing"]
            }
            
            skills = random.sample(skills_map.get(position, ["기술 스킬"]), random.randint(2, 4))
            
            # 채용공고에 균등하게 분배 (라운드 로빈 방식)
            job_posting_id = job_posting_ids[i % len(job_posting_ids)]
            
            applicant = {
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "position": position,
                "department": department,
                "experience": experience,
                "skills": ", ".join(skills),
                "growthBackground": fake.text(max_nb_chars=200),
                "motivation": fake.text(max_nb_chars=300),
                "careerHistory": fake.text(max_nb_chars=250),
                "analysisScore": random.randint(60, 95),
                "analysisResult": fake.text(max_nb_chars=200),
                "status": status,
                "job_posting_id": job_posting_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            applicants.append(applicant)
        
        # DB에 삽입
        if applicants:
            result = await db.applicants.insert_many(applicants)
            generated_count = len(result.inserted_ids)
            
            # 채용공고별 지원자 수 업데이트
            job_posting_counts = {}
            for applicant in applicants:
                job_id = applicant["job_posting_id"]
                job_posting_counts[job_id] = job_posting_counts.get(job_id, 0) + 1
            
            # 각 채용공고의 지원자 수 업데이트
            for job_id, count in job_posting_counts.items():
                await db.job_postings.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$inc": {"applicants": count}}
                )
            
            return {
                "success": True,
                "message": f"{generated_count}명의 지원자 샘플 데이터가 {len(job_posting_ids)}개 채용공고에 분배되어 생성되었습니다.",
                "generated_count": generated_count,
                "job_postings_used": len(job_posting_ids),
                "distribution": job_posting_counts
            }
        else:
            raise HTTPException(status_code=400, detail="지원자 데이터 생성에 실패했습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"샘플 지원자 생성 실패: {str(e)}")

@router.post("/generate-job-postings")
async def generate_sample_job_postings(
    data: Dict[str, Any],
    db: AsyncIOMotorClient = Depends(get_database)
):
    """샘플 채용공고 데이터 생성"""
    try:
        count = data.get('count', 10)
        
        # 채용공고 데이터 생성
        job_postings = []
        companies = ["테크스타트업", "대기업", "중소기업", "IT기업", "스타트업", "외국계기업"]
        positions = ["프론트엔드 개발자", "백엔드 개발자", "UI/UX 디자이너", "프로젝트 매니저", "디지털 마케팅 전문가"]
        departments = ["개발팀", "디자인팀", "마케팅팀", "기획팀", "영업팀"]
        locations = ["서울특별시 강남구", "서울특별시 서초구", "서울특별시 마포구", "경기도 성남시", "부산광역시 해운대구"]
        salaries = ["연봉 3,000만원 - 4,500만원", "연봉 4,000만원 - 6,000만원", "연봉 5,000만원 - 7,000만원", "연봉 6,000만원 - 8,000만원"]
        
        for i in range(count):
            company = random.choice(companies)
            position = random.choice(positions)
            department = random.choice(departments)
            location = random.choice(locations)
            salary = random.choice(salaries)
            
            job_posting = {
                "title": f"{company} {position} 채용",
                "company": company,
                "location": location,
                "department": department,
                "position": position,
                "type": "full-time",
                "salary": salary,
                "experience": random.choice(["신입", "경력", "고급"]),
                "education": "대졸 이상",
                "description": fake.text(max_nb_chars=500),
                "requirements": fake.text(max_nb_chars=300),
                "benefits": "주말보장, 재택가능, 점심식대 지원, 연차휴가",
                "deadline": "2024-12-31",
                "status": "draft",
                "applicants": 0,
                "views": 0,
                "bookmarks": 0,
                "shares": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            job_postings.append(job_posting)
        
        # DB에 삽입
        if job_postings:
            result = await db.job_postings.insert_many(job_postings)
            generated_count = len(result.inserted_ids)
            
            return {
                "success": True,
                "message": f"{generated_count}개의 채용공고 샘플 데이터가 생성되었습니다.",
                "generated_count": generated_count
            }
        else:
            raise HTTPException(status_code=400, detail="채용공고 데이터 생성에 실패했습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"샘플 채용공고 생성 실패: {str(e)}")

@router.post("/upload-excel")
async def upload_excel_file(
    file: UploadFile = File(...),
    db: AsyncIOMotorClient = Depends(get_database)
):
    """엑셀 파일 업로드 및 데이터 처리"""
    try:
        # 파일 확장자 검증
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls) 또는 CSV 파일만 업로드 가능합니다.")
        
        # 파일 크기 검증 (10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")
        
        # 파일 내용 읽기
        content = await file.read()
        
        # 파일 형식에 따라 처리
        if file.filename.endswith('.csv'):
            # CSV 파일 처리
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
        else:
            # 엑셀 파일 처리
            df = pd.read_excel(io.BytesIO(content))
        
        # 데이터 검증 및 처리
        uploaded_count = 0
        errors = []
        
        # 지원자 데이터 처리
        if 'name' in df.columns and 'email' in df.columns:
            # 지원자 데이터로 인식
            for index, row in df.iterrows():
                try:
                    applicant_data = {
                        "name": str(row.get('name', '')),
                        "email": str(row.get('email', '')),
                        "phone": str(row.get('phone', '')),
                        "position": str(row.get('position', '')),
                        "department": str(row.get('department', '')),
                        "experience": str(row.get('experience', '신입')),
                        "skills": str(row.get('skills', '')),
                        "growthBackground": str(row.get('growthBackground', '')),
                        "motivation": str(row.get('motivation', '')),
                        "careerHistory": str(row.get('careerHistory', '')),
                        "analysisScore": int(row.get('analysisScore', 0)),
                        "analysisResult": str(row.get('analysisResult', '')),
                        "status": str(row.get('status', 'pending')),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    # 필수 필드 검증
                    if not applicant_data["name"] or not applicant_data["email"]:
                        errors.append(f"행 {index + 1}: 이름과 이메일은 필수입니다.")
                        continue
                    
                    # DB에 삽입
                    await db.applicants.insert_one(applicant_data)
                    uploaded_count += 1
                    
                except Exception as e:
                    errors.append(f"행 {index + 1}: {str(e)}")
        
        # 채용공고 데이터 처리
        elif 'title' in df.columns and 'company' in df.columns:
            # 채용공고 데이터로 인식
            for index, row in df.iterrows():
                try:
                    job_posting_data = {
                        "title": str(row.get('title', '')),
                        "company": str(row.get('company', '')),
                        "location": str(row.get('location', '')),
                        "department": str(row.get('department', '')),
                        "position": str(row.get('position', '')),
                        "salary": str(row.get('salary', '')),
                        "experience": str(row.get('experience', '신입')),
                        "description": str(row.get('description', '')),
                        "requirements": str(row.get('requirements', '')),
                        "status": str(row.get('status', 'draft')),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    # 필수 필드 검증
                    if not job_posting_data["title"] or not job_posting_data["company"]:
                        errors.append(f"행 {index + 1}: 제목과 회사명은 필수입니다.")
                        continue
                    
                    # DB에 삽입
                    await db.job_postings.insert_one(job_posting_data)
                    uploaded_count += 1
                    
                except Exception as e:
                    errors.append(f"행 {index + 1}: {str(e)}")
        
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 데이터 형식입니다. 지원자 또는 채용공고 데이터 형식을 확인해주세요.")
        
        return {
            "success": True,
            "message": f"{uploaded_count}개의 데이터가 성공적으로 업로드되었습니다.",
            "uploaded_count": uploaded_count,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

@router.post("/reset-all")
async def reset_all_data(db: AsyncIOMotorClient = Depends(get_database)):
    """모든 데이터 초기화"""
    try:
        # 모든 컬렉션 삭제
        collections_to_reset = ["applicants", "job_postings", "resumes"]
        deleted_counts = {}
        
        for collection_name in collections_to_reset:
            result = await db[collection_name].delete_many({})
            deleted_counts[collection_name] = result.deleted_count
        
        return {
            "success": True,
            "message": "모든 데이터가 성공적으로 초기화되었습니다.",
            "deleted_counts": deleted_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 초기화 실패: {str(e)}")

@router.get("/stats")
async def get_sample_data_stats(db: AsyncIOMotorClient = Depends(get_database)):
    """샘플 데이터 통계 조회"""
    try:
        # 각 컬렉션의 문서 수 조회
        applicants_count = await db.applicants.count_documents({})
        job_postings_count = await db.job_postings.count_documents({})
        resumes_count = await db.resumes.count_documents({})
        
        return {
            "success": True,
            "stats": {
                "total_applicants": applicants_count,
                "total_job_postings": job_postings_count,
                "total_resumes": resumes_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
