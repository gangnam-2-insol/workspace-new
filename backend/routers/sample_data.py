import io
import os
import random
from datetime import datetime
from typing import Any, Dict

import pandas as pd
from bson import ObjectId
from faker import Faker
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.vector_service import VectorService
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(tags=["샘플 데이터"])

# Faker 초기화 (한국어)
fake = Faker('ko_KR')

# MongoDB 연결 의존성
def get_database():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    return client.hireme

# 벡터 서비스 초기화
def get_vector_service():
    try:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "hireme-index")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")

        if pinecone_api_key:
            return VectorService(
                api_key=pinecone_api_key,
                index_name=pinecone_index_name,
                environment=pinecone_environment
            )
        else:
            print("⚠️ Pinecone API 키가 설정되지 않아 벡터 서비스를 사용할 수 없습니다.")
            return None
    except Exception as e:
        print(f"⚠️ 벡터 서비스 초기화 실패: {e}")
        return None

# 임베딩 서비스 초기화
def get_embedding_service():
    try:
        return EmbeddingService()
    except Exception as e:
        print(f"⚠️ 임베딩 서비스 초기화 실패: {e}")
        return None

# 벡터 저장을 위한 헬퍼 함수
async def save_to_vector_db(data: Dict[str, Any], data_type: str, vector_service: VectorService, embedding_service: EmbeddingService):
    """데이터를 벡터 데이터베이스에 저장"""
    try:
        if not vector_service or not embedding_service:
            print(f"⚠️ 벡터 서비스 또는 임베딩 서비스가 초기화되지 않아 {data_type} 벡터 저장을 건너뜁니다.")
            return False

        # 텍스트 데이터 추출
        text_content = ""
        if data_type == "applicant":
            # 지원자 데이터에서 텍스트 추출
            text_parts = [
                f"이름: {data.get('name', '')}",
                f"직무: {data.get('position', '')}",
                f"부서: {data.get('department', '')}",
                f"경력: {data.get('experience', '')}",
                f"기술: {data.get('skills', '')}",
                f"성장배경: {data.get('growthBackground', '')}",
                f"지원동기: {data.get('motivation', '')}",
                f"경력사항: {data.get('careerHistory', '')}",
                f"분석결과: {data.get('analysisResult', '')}"
            ]
            text_content = " ".join([part for part in text_parts if part.split(": ")[1]])

        elif data_type == "job_posting":
            # 채용공고 데이터에서 텍스트 추출
            text_parts = [
                f"제목: {data.get('title', '')}",
                f"회사: {data.get('company', '')}",
                f"위치: {data.get('location', '')}",
                f"부서: {data.get('department', '')}",
                f"직무: {data.get('position', '')}",
                f"급여: {data.get('salary', '')}",
                f"경력: {data.get('experience', '')}",
                f"설명: {data.get('description', '')}",
                f"요구사항: {data.get('requirements', '')}"
            ]
            text_content = " ".join([part for part in text_parts if part.split(": ")[1]])

        if not text_content.strip():
            print(f"⚠️ {data_type} 데이터에 저장할 텍스트가 없습니다.")
            return False

        # 임베딩 생성
        embedding = await embedding_service.get_embedding(text_content)
        if not embedding:
            print(f"⚠️ {data_type} 데이터의 임베딩 생성에 실패했습니다.")
            return False

        # 메타데이터 준비
        metadata = {
            "data_type": data_type,
            "data_id": str(data.get("_id", "")),
            "created_at": datetime.now().isoformat(),
            "text_content": text_content[:1000]  # 메타데이터에는 짧은 텍스트만
        }

        # 벡터 저장
        vector_id = await vector_service.save_vector(embedding, metadata)
        if vector_id:
            print(f"✅ {data_type} 벡터 저장 성공: {vector_id}")
            return True
        else:
            print(f"❌ {data_type} 벡터 저장 실패")
            return False

    except Exception as e:
        print(f"❌ {data_type} 벡터 저장 중 오류 발생: {e}")
        return False

@router.post("/generate-applicants")
async def generate_sample_applicants(
    data: Dict[str, Any],
    db: AsyncIOMotorClient = Depends(get_database)
):
    """샘플 지원자 데이터 생성 - 직무 매칭 보장"""
    try:
        count = data.get('count', 50)

                # 기존 채용공고 ID 목록 가져오기 (단순하게)
        job_postings = await db.job_postings.find({}, {"_id": 1, "position": 1, "title": 1}).to_list(100)

        if not job_postings:
            raise HTTPException(
                status_code=400,
                detail="지원자를 생성하기 전에 먼저 채용공고를 생성해주세요. 지원자는 반드시 채용공고에 소속되어야 합니다."
            )

        # 채용공고 ID 목록 (단순하게)
        job_posting_ids = [str(job["_id"]) for job in job_postings]
        job_posting_info = {str(job["_id"]): {"position": job.get("position", "Unknown"), "title": job.get("title", "Unknown")} for job in job_postings}

        # 지원자 데이터 생성
        applicants = []
        departments = ["개발팀", "디자인팀", "마케팅팀", "기획팀", "영업팀"]
        experiences = ["신입", "1-3년", "3-5년", "5-7년", "7년 이상"]
        statuses = ["pending", "reviewing", "interview_scheduled", "passed", "rejected"]

        # 기술 스킬 매핑
        skills_map = {
            "프론트엔드 개발자": ["JavaScript", "React", "Vue.js", "TypeScript", "HTML", "CSS", "Next.js", "Angular"],
            "백엔드 개발자": ["Python", "Node.js", "Java", "Spring Boot", "MySQL", "MongoDB", "Django", "Express.js"],
            "UI/UX 디자이너": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InVision", "Zeplin"],
            "프로젝트 매니저": ["Jira", "Confluence", "Slack", "Trello", "MS Project", "Asana", "Notion"],
            "디지털 마케팅 전문가": ["Google Analytics", "Facebook Ads", "Google Ads", "SEO", "Content Marketing", "HubSpot", "Mailchimp"],
            "DevOps 엔지니어": ["Docker", "Kubernetes", "AWS", "Azure", "Jenkins", "GitLab", "Terraform"],
            "데이터 사이언티스트": ["Python", "R", "SQL", "TensorFlow", "PyTorch", "Pandas", "NumPy"],
            "QA 엔지니어": ["Selenium", "JUnit", "TestNG", "Postman", "JMeter", "Cucumber", "Appium"],
            "모바일 개발자": ["Swift", "Kotlin", "React Native", "Flutter", "Xamarin", "Android Studio", "Xcode"],
            "풀스택 개발자": ["JavaScript", "Python", "React", "Node.js", "MongoDB", "PostgreSQL", "Docker"],
            "마케팅 전문가": ["Google Analytics", "Facebook Ads", "Google Ads", "SEO", "Content Marketing", "CRM"],
            "프로덕트 매니저": ["Jira", "Confluence", "Slack", "Figma", "Mixpanel", "Amplitude", "Notion"],
            "HR 담당자": ["Workday", "BambooHR", "Slack", "Zoom", "LinkedIn Recruiter", "ATS"],
            "영업 담당자": ["Salesforce", "HubSpot", "Pipedrive", "Slack", "Zoom", "LinkedIn Sales Navigator"]
        }

                                # 지원자를 채용공고에 랜덤 배정 (100% 매칭 보장)
        for i in range(count):
            # 랜덤으로 채용공고 선택
            selected_job_id = random.choice(job_posting_ids)
            selected_job_info = job_posting_info[selected_job_id]

            # 선택된 채용공고의 직무로 지원자 생성 (100% 매칭 보장)
            position = selected_job_info["position"]
            department = random.choice(departments)
            experience = random.choice(experiences)
            status = random.choice(statuses)

            # 해당 직무에 맞는 기술 스킬 생성
            skills = random.sample(skills_map.get(position, ["기술 스킬"]), random.randint(2, 4))

            # GitHub URL 목록 (제공된 URL들)
            github_urls = [
                "https://github.com/kyungho222/myResume",
                "https://github.com/kyungho222/hireme",
                "https://github.com/kyungho222",
                "https://github.com/rangrang-53",
                "https://github.com/gaa149",
                "https://github.com/Drew9703",
                "https://github.com/Seastar0521"
            ]

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
                "job_posting_id": selected_job_id,
                "github_url": random.choice(github_urls) if random.choice([True, False]) else None,
                "linkedin_url": f"https://linkedin.com/in/{fake.user_name()}" if random.choice([True, False]) else None,
                "portfolio_url": f"https://portfolio.example.com/{fake.user_name()}" if random.choice([True, False]) else None,
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
                "message": f"{generated_count}명의 지원자 샘플 데이터가 {len(job_posting_ids)}개 채용공고에 랜덤 배정되어 생성되었습니다.",
                "generated_count": generated_count,
                "job_postings_used": len(job_posting_ids),
                "distribution": job_posting_counts,
                "position_matching": "✅ 100% 채용공고 연동 보장"
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
    """샘플 채용공고 데이터 생성 - 다양한 직무 포함"""
    try:
        count = data.get('count', 10)

        # 다양한 직무 목록 (지원자 직무와 일치)
        positions = [
            "프론트엔드 개발자", "백엔드 개발자", "UI/UX 디자이너", "프로젝트 매니저",
            "디지털 마케팅 전문가", "DevOps 엔지니어", "데이터 사이언티스트",
            "QA 엔지니어", "모바일 개발자", "풀스택 개발자", "마케팅 전문가",
            "프로덕트 매니저", "HR 담당자", "영업 담당자"
        ]

        # 채용공고 데이터 생성
        job_postings = []
        companies = ["테크스타트업", "대기업", "중소기업", "IT기업", "스타트업", "외국계기업", "유니콘기업"]
        departments = ["개발팀", "디자인팀", "마케팅팀", "기획팀", "영업팀", "인사팀", "데이터팀"]
        locations = ["서울특별시 강남구", "서울특별시 서초구", "서울특별시 마포구", "경기도 성남시", "부산광역시 해운대구", "대구광역시 수성구"]
        salaries = ["연봉 3,000만원 - 4,500만원", "연봉 4,000만원 - 6,000만원", "연봉 5,000만원 - 7,000만원", "연봉 6,000만원 - 8,000만원", "연봉 7,000만원 - 1억원"]

        # 직무별로 균등하게 분배 (중복 제거)
        # 요청한 개수만큼 직무를 선택 (중복 없이)
        selected_positions = []
        for i in range(count):
            # 직무를 순환하면서 선택
            position = positions[i % len(positions)]
            selected_positions.append(position)

        for i in range(count):
            position = selected_positions[i]
            company = random.choice(companies)
            department = random.choice(departments)
            location = random.choice(locations)
            salary = random.choice(salaries)

            job_posting = {
                "title": f"{company} {position} 채용",
                "company": company,
                "location": location,
                "department": department,
                "position": position,  # 직무 필드 추가
                "type": "full-time",
                "salary": salary,
                "experience": random.choice(["신입", "경력", "고급"]),
                "education": "대졸 이상",
                "description": fake.text(max_nb_chars=500),
                "requirements": fake.text(max_nb_chars=300),
                "benefits": "주말보장, 재택가능, 점심식대 지원, 연차휴가",
                "deadline": "2024-12-31",
                "status": "published",  # 모든 채용공고를 활성화 상태로 통일
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

            # 생성된 직무별 통계
            position_stats = {}
            for job in job_postings:
                position = job['position']
                position_stats[position] = position_stats.get(position, 0) + 1

            return {
                "success": True,
                "message": f"{generated_count}개의 채용공고 샘플 데이터가 생성되었습니다. (다양한 직무 포함)",
                "generated_count": generated_count,
                "position_distribution": position_stats,
                "matching_ready": "✅ 지원자 직무 매칭 준비 완료"
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

@router.post("/upload-json")
async def upload_json_data(
    data: Dict[str, Any],
    db: AsyncIOMotorClient = Depends(get_database)
):
    """JSON 데이터 업로드 및 처리"""
    try:
        uploaded_count = 0
        errors = []
        vector_saved_count = 0

        # 벡터 서비스 초기화
        vector_service = get_vector_service()
        embedding_service = get_embedding_service()

        # 데이터 타입 확인
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="JSON 데이터는 객체 형태여야 합니다.")

        # 지원자 데이터 처리
        if 'applicants' in data and isinstance(data['applicants'], list):
            # 기존 채용공고 ID 목록 가져오기
            existing_job_postings = await db.job_postings.find({}, {"_id": 1}).to_list(None)
            job_posting_ids = [str(job["_id"]) for job in existing_job_postings]

            for index, applicant in enumerate(data['applicants']):
                try:
                    # 랜덤하게 채용공고 ID 할당
                    assigned_job_posting_id = None
                    if job_posting_ids:
                        import random
                        assigned_job_posting_id = random.choice(job_posting_ids)
                    else:
                        # 채용공고가 없으면 기본 채용공고 생성
                        from backend.modules.core.utils.job_posting_assignment import (
                            create_default_job_posting_if_needed,
                        )
                        assigned_job_posting_id = await create_default_job_posting_if_needed(db)

                    applicant_data = {
                        "name": str(applicant.get('name', '')),
                        "email": str(applicant.get('email', '')),
                        "phone": str(applicant.get('phone', '')),
                        "github_url": str(applicant.get('github_url', '')),
                        "position": str(applicant.get('position', '')),
                        "department": str(applicant.get('department', '')),
                        "experience": str(applicant.get('experience', '신입')),
                        "skills": str(applicant.get('skills', '')),
                        "growthBackground": str(applicant.get('growthBackground', '')),
                        "motivation": str(applicant.get('motivation', '')),
                        "careerHistory": str(applicant.get('careerHistory', '')),
                        "analysisScore": int(applicant.get('analysisScore', 0)),
                        "analysisResult": str(applicant.get('analysisResult', '')),
                        "status": str(applicant.get('status', 'pending')),
                        "job_posting_id": assigned_job_posting_id,  # 랜덤 할당된 채용공고 ID
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }

                    # 필수 필드 검증
                    if not applicant_data["name"] or not applicant_data["email"]:
                        errors.append(f"지원자 {index + 1}: 이름과 이메일은 필수입니다.")
                        continue

                    # DB에 삽입
                    result = await db.applicants.insert_one(applicant_data)
                    uploaded_count += 1

                    # 자소서 데이터가 있으면 별도로 저장
                    if result.inserted_id and applicant.get('cover_letter_id'):
                        cover_letter_data = {
                            "_id": ObjectId(applicant.get('cover_letter_id')),
                            "applicant_id": str(result.inserted_id),
                            "content": f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}",
                            "extracted_text": f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}",
                            "growthBackground": applicant.get('growthBackground', ''),
                            "motivation": applicant.get('motivation', ''),
                            "careerHistory": applicant.get('careerHistory', ''),
                            "filename": f"자소서_{applicant.get('name', '')}.txt",
                            "file_size": len(f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}"),
                            "status": "submitted",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }

                        try:
                            await db.cover_letters.insert_one(cover_letter_data)
                        except Exception as e:
                            print(f"자소서 저장 실패: {e}")

                    # 벡터 데이터베이스에 저장
                    if result.inserted_id:
                        applicant_data["_id"] = result.inserted_id
                        vector_saved = await save_to_vector_db(applicant_data, "applicant", vector_service, embedding_service)
                        if vector_saved:
                            vector_saved_count += 1

                except Exception as e:
                    errors.append(f"지원자 {index + 1}: {str(e)}")

        # 채용공고 데이터 처리
        if 'job_postings' in data and isinstance(data['job_postings'], list):
            for index, job_posting in enumerate(data['job_postings']):
                try:
                    job_posting_data = {
                        "title": str(job_posting.get('title', '')),
                        "company": str(job_posting.get('company', '')),
                        "location": str(job_posting.get('location', '')),
                        "department": str(job_posting.get('department', '')),
                        "position": str(job_posting.get('position', '')),
                        "salary": str(job_posting.get('salary', '')),
                        "experience": str(job_posting.get('experience', '신입')),
                        "description": str(job_posting.get('description', '')),
                        "requirements": str(job_posting.get('requirements', '')),
                        "status": str(job_posting.get('status', 'published')),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }

                    # 필수 필드 검증
                    if not job_posting_data["title"] or not job_posting_data["company"]:
                        errors.append(f"채용공고 {index + 1}: 제목과 회사명은 필수입니다.")
                        continue

                    # DB에 삽입
                    result = await db.job_postings.insert_one(job_posting_data)
                    uploaded_count += 1

                    # 벡터 데이터베이스에 저장
                    if result.inserted_id:
                        job_posting_data["_id"] = result.inserted_id
                        vector_saved = await save_to_vector_db(job_posting_data, "job_posting", vector_service, embedding_service)
                        if vector_saved:
                            vector_saved_count += 1

                except Exception as e:
                    errors.append(f"채용공고 {index + 1}: {str(e)}")

        # 데이터가 없는 경우
        if uploaded_count == 0 and not errors:
            raise HTTPException(status_code=400, detail="지원자(applicants) 또는 채용공고(job_postings) 데이터가 필요합니다.")

        # 응답 메시지 생성
        message = f"{uploaded_count}개의 데이터가 성공적으로 업로드되었습니다."
        if 'applicants' in data and uploaded_count > 0:
            message += f" 지원자들에게 기존 채용공고가 랜덤하게 할당되었습니다."
        if vector_saved_count > 0:
            message += f" {vector_saved_count}개의 데이터가 벡터 데이터베이스에 저장되었습니다."

        return {
            "success": True,
            "message": message,
            "uploaded_count": uploaded_count,
            "vector_saved_count": vector_saved_count,
            "errors": errors if errors else None,
            "job_posting_count": len(job_posting_ids) if 'applicants' in data else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON 데이터 업로드 실패: {str(e)}")

@router.get("/json-template")
async def get_json_template():
    """JSON 템플릿 다운로드"""
    template = {
        "applicants": [
            {
                "name": "홍길동",
                "email": "hong@example.com",
                "phone": "010-1234-5678",
                "github_url": "https://github.com/hong",
                "position": "프론트엔드 개발자",
                "department": "개발팀",
                "experience": "3년",
                "skills": "React, JavaScript, TypeScript",
                "growthBackground": "스타트업에서 프론트엔드 개발 경험",
                "motivation": "사용자 경험을 개선하는 개발자가 되고 싶습니다",
                "careerHistory": "A회사 프론트엔드 개발자 2년, B회사 웹 개발자 1년",
                "analysisScore": 85,
                "analysisResult": "우수한 프론트엔드 개발 역량을 보유",
                "status": "pending"
            },
            {
                "name": "김철수",
                "email": "kim@example.com",
                "phone": "010-9876-5432",
                "github_url": "https://github.com/kim",
                "position": "백엔드 개발자",
                "department": "개발팀",
                "experience": "5년",
                "skills": "Python, Django, PostgreSQL",
                "growthBackground": "대기업에서 백엔드 시스템 개발 경험",
                "motivation": "안정적이고 확장 가능한 시스템을 구축하고 싶습니다",
                "careerHistory": "C회사 백엔드 개발자 3년, D회사 풀스택 개발자 2년",
                "analysisScore": 92,
                "analysisResult": "뛰어난 백엔드 개발 역량과 시스템 설계 능력",
                "status": "pending"
            }
        ],
        "job_postings": [
            {
                "title": "프론트엔드 개발자 모집",
                "company": "테크스타트업",
                "location": "서울 강남구",
                "department": "개발팀",
                "position": "프론트엔드 개발자",
                "salary": "4000만원 ~ 6000만원",
                "experience": "3년 이상",
                "description": "혁신적인 웹 서비스를 개발할 프론트엔드 개발자를 모집합니다.",
                "requirements": "React, JavaScript, TypeScript 경험 필수",
                "status": "published"
            },
            {
                "title": "백엔드 개발자 모집",
                "company": "글로벌 IT기업",
                "location": "서울 서초구",
                "department": "개발팀",
                "position": "백엔드 개발자",
                "salary": "5000만원 ~ 8000만원",
                "experience": "5년 이상",
                "description": "대규모 시스템을 설계하고 개발할 백엔드 개발자를 모집합니다.",
                "requirements": "Python, Django, PostgreSQL 경험 필수",
                "status": "published"
            }
        ]
    }

    return template

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

@router.post("/generate-cover-letters")
async def generate_sample_cover_letters(
    data: Dict[str, Any],
    db: AsyncIOMotorClient = Depends(get_database)
):
    """자소서가 없는 지원자들을 위한 샘플 자소서 데이터 생성"""
    try:
        # 기존 지원자 목록 조회
        applicants = await db.applicants.find({}, {"_id": 1, "name": 1, "position": 1}).to_list(1000)

        if not applicants:
            raise HTTPException(
                status_code=400,
                detail="자소서를 생성하기 전에 먼저 지원자를 생성해주세요."
            )

        # 자소서가 없는 지원자들만 필터링
        applicants_without_cover_letters = []
        for applicant in applicants:
            existing_cover_letter = await db.cover_letters.find_one({"applicant_id": applicant["_id"]})
            if not existing_cover_letter:
                applicants_without_cover_letters.append(applicant)

        if not applicants_without_cover_letters:
            return {
                "success": True,
                "message": "모든 지원자에게 이미 자소서가 생성되어 있습니다.",
                "generated_count": 0,
                "total_applicants": len(applicants),
                "applicants_without_cover_letters": 0
            }

        # 자소서 템플릿 데이터
        cover_letter_templates = [
            {
                "motivation": "귀사의 혁신적인 기술과 사용자 중심의 서비스 철학에 깊이 공감하여 지원하게 되었습니다. 특히 귀사가 추구하는 '사용자 경험 최적화'라는 가치가 제가 지향하는 개발 철학과 일치한다고 생각합니다.",
                "career_goals": "프론트엔드 개발자로서 사용자에게 최고의 경험을 제공하는 서비스를 개발하고, 팀 내 기술 리더로 성장하여 후배 개발자들을 멘토링하는 것이 목표입니다.",
                "strengths": "React, TypeScript, Next.js 등 현대적인 프론트엔드 기술 스택에 대한 깊은 이해와 실무 경험을 보유하고 있습니다. 또한 사용자 경험을 중시하는 개발 철학과 팀워크를 중시하는 협업 능력을 강점으로 가지고 있습니다.",
                "experience": "이전 회사에서 대규모 사용자를 대상으로 하는 웹 서비스의 프론트엔드 개발을 담당했습니다. 특히 성능 최적화와 접근성 개선 프로젝트를 주도하여 페이지 로딩 속도를 40% 단축하고 웹 접근성 준수율을 95%까지 향상시켰습니다.",
                "achievements": "주요 성과로는 대규모 리팩토링 프로젝트를 성공적으로 완료하여 코드 유지보수성을 크게 향상시켰고, 신입 개발자 멘토링 프로그램을 운영하여 팀 생산성을 25% 향상시켰습니다.",
                "skills": "JavaScript, TypeScript, React, Next.js, Vue.js, HTML5, CSS3, Sass, Webpack, Jest, Git, Figma",
                "projects": "전자상거래 플랫폼 프론트엔드 개발, 모바일 웹 앱 최적화, 디자인 시스템 구축 및 운영, 마이크로프론트엔드 아키텍처 도입",
                "education": "컴퓨터공학과 학사 졸업, 웹 개발 관련 온라인 강의 수강 및 자격증 취득",
                "certifications": "AWS Certified Developer, Google Cloud Platform 자격증, React 공식 인증 과정 수료",
                "languages": "한국어(모국어), 영어(비즈니스 회화 가능), 일본어(기초)",
                "personal_statement": "끊임없이 새로운 기술을 학습하고 실무에 적용하는 것을 즐기는 개발자입니다. 사용자 중심의 사고와 팀워크를 중시하며, 항상 더 나은 솔루션을 찾기 위해 노력합니다.",
                "future_plans": "앞으로 3년 내에 프론트엔드 아키텍트로 성장하여 팀의 기술적 의사결정을 주도하고, 5년 내에는 기술 리더로서 후배 개발자들을 멘토링하며 조직의 기술 역량을 향상시키는 것이 목표입니다."
            },
            {
                "motivation": "귀사의 데이터 기반 의사결정과 AI 기술 활용에 대한 비전에 매료되어 지원하게 되었습니다. 특히 귀사가 추구하는 '데이터로 만드는 더 나은 세상'이라는 미션이 제가 추구하는 가치와 일치합니다.",
                "career_goals": "데이터 사이언티스트로서 비즈니스 문제를 데이터로 해결하고, 머신러닝 모델을 통해 실질적인 가치를 창출하는 것이 목표입니다.",
                "strengths": "Python, R, SQL 등 데이터 분석 도구에 대한 전문 지식과 머신러닝, 딥러닝 알고리즘에 대한 깊은 이해를 보유하고 있습니다. 또한 복잡한 비즈니스 문제를 데이터 관점에서 분석하고 해결하는 능력을 강점으로 가지고 있습니다.",
                "experience": "이전 회사에서 고객 행동 분석과 예측 모델링을 담당했습니다. 특히 고객 이탈 예측 모델을 개발하여 이탈률을 30% 감소시켰고, 추천 시스템을 구축하여 매출을 25% 향상시켰습니다.",
                "achievements": "주요 성과로는 대용량 데이터 처리 파이프라인을 구축하여 분석 속도를 10배 향상시켰고, A/B 테스트 프레임워크를 개발하여 의사결정 속도를 크게 개선했습니다.",
                "skills": "Python, R, SQL, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn, Apache Spark, Hadoop, Tableau, Power BI",
                "projects": "고객 이탈 예측 모델 개발, 추천 시스템 구축, 실시간 데이터 분석 대시보드 개발, 자연어 처리 모델 개발",
                "education": "통계학과 석사 졸업, 데이터 사이언스 관련 온라인 강의 수강",
                "certifications": "Google Data Analytics Professional Certificate, Microsoft Azure Data Scientist Associate",
                "languages": "한국어(모국어), 영어(유창), 중국어(기초)",
                "personal_statement": "데이터를 통해 숨겨진 인사이트를 발견하고 이를 비즈니스 가치로 전환하는 것을 즐기는 데이터 사이언티스트입니다. 지속적인 학습과 혁신을 추구하며, 팀과의 협업을 통해 더 큰 가치를 창출하고자 합니다.",
                "future_plans": "앞으로 2년 내에 시니어 데이터 사이언티스트로 성장하여 복잡한 비즈니스 문제를 해결하고, 5년 내에는 데이터 팀 리더로서 조직의 데이터 역량을 향상시키는 것이 목표입니다."
            },
            {
                "motivation": "귀사의 창의적인 디자인 철학과 사용자 중심의 제품 개발 문화에 깊이 공감하여 지원하게 되었습니다. 특히 귀사가 추구하는 '아름다움과 기능성의 조화'라는 가치가 제가 지향하는 디자인 철학과 일치합니다.",
                "career_goals": "UI/UX 디자이너로서 사용자에게 직관적이고 아름다운 경험을 제공하는 제품을 디자인하고, 디자인 시스템을 구축하여 팀의 디자인 일관성을 확보하는 것이 목표입니다.",
                "strengths": "Figma, Adobe Creative Suite 등 디자인 도구에 대한 전문 지식과 사용자 연구, 프로토타이핑, 디자인 시스템 구축에 대한 풍부한 경험을 보유하고 있습니다. 또한 사용자 중심의 사고와 시각적 커뮤니케이션 능력을 강점으로 가지고 있습니다.",
                "experience": "이전 회사에서 모바일 앱과 웹 서비스의 UI/UX 디자인을 담당했습니다. 특히 사용자 리서치를 통한 인사이트 도출과 프로토타이핑을 통한 빠른 검증을 통해 사용자 만족도를 40% 향상시켰습니다.",
                "achievements": "주요 성과로는 디자인 시스템을 구축하여 디자인 일관성을 확보하고 개발 효율성을 50% 향상시켰고, 사용자 테스트를 통한 지속적인 개선으로 앱 스토어 평점을 4.5점으로 향상시켰습니다.",
                "skills": "Figma, Adobe XD, Sketch, Photoshop, Illustrator, InVision, Zeplin, Principle, Framer, HTML/CSS 기초",
                "projects": "모바일 뱅킹 앱 UI/UX 디자인, 전자상거래 플랫폼 디자인 시스템 구축, 브랜드 아이덴티티 디자인, 사용자 리서치 및 프로토타이핑",
                "education": "시각디자인학과 학사 졸업, UI/UX 디자인 관련 온라인 강의 수강",
                "certifications": "Google UX Design Professional Certificate, Adobe Certified Associate",
                "languages": "한국어(모국어), 영어(비즈니스 회화 가능)",
                "personal_statement": "사용자의 니즈를 깊이 이해하고 이를 아름다운 디자인으로 구현하는 것을 즐기는 UI/UX 디자이너입니다. 창의적 사고와 논리적 분석을 조화롭게 활용하여 사용자에게 최고의 경험을 제공하고자 합니다.",
                "future_plans": "앞으로 3년 내에 시니어 UI/UX 디자이너로 성장하여 복잡한 제품의 디자인을 주도하고, 5년 내에는 디자인 팀 리더로서 조직의 디자인 역량을 향상시키는 것이 목표입니다."
            }
        ]

                # 자소서 데이터 생성 (자소서가 없는 지원자들만)
        cover_letters = []
        for applicant in applicants_without_cover_letters:

            # 지원자의 직무에 맞게 템플릿 선택
            position = applicant.get("position", "개발자")
            if "디자이너" in position:
                template_index = 2
            elif "데이터" in position or "분석" in position:
                template_index = 1
            else:
                template_index = 0

            selected_template = cover_letter_templates[template_index]

            # 전체 내용 생성
            full_content = f"""지원 동기:
{selected_template['motivation']}

경력 목표:
{selected_template['career_goals']}

강점 및 역량:
{selected_template['strengths']}

관련 경험:
{selected_template['experience']}

주요 성과:
{selected_template['achievements']}

보유 기술:
{selected_template['skills']}

프로젝트 경험:
{selected_template['projects']}

학력 사항:
{selected_template['education']}

자격증:
{selected_template['certifications']}

언어 능력:
{selected_template['languages']}

자기소개:
{selected_template['personal_statement']}

향후 계획:
{selected_template['future_plans']}""".strip()

            cover_letter = {
                "applicant_id": str(applicant["_id"]),
                "content": full_content,
                "motivation": selected_template['motivation'],
                "career_goals": selected_template['career_goals'],
                "strengths": selected_template['strengths'],
                "experience": selected_template['experience'],
                "achievements": selected_template['achievements'],
                "skills": selected_template['skills'],
                "projects": selected_template['projects'],
                "education": selected_template['education'],
                "certifications": selected_template['certifications'],
                "languages": selected_template['languages'],
                "personal_statement": selected_template['personal_statement'],
                "future_plans": selected_template['future_plans'],
                "filename": f"자소서_{applicant['name']}_{i+1}.pdf",
                "file_size": random.randint(50000, 200000),
                "extracted_text": full_content,
                "status": "submitted",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            cover_letters.append(cover_letter)

        # 데이터베이스에 저장
        if cover_letters:
            result = await db.cover_letters.insert_many(cover_letters)

            # 지원자 데이터에 cover_letter_id 업데이트
            for i, cover_letter in enumerate(cover_letters):
                await db.applicants.update_one(
                    {"_id": ObjectId(cover_letter["applicant_id"])},
                    {"$set": {"cover_letter_id": str(result.inserted_ids[i])}}
                )

        return {
            "success": True,
            "message": f"{len(cover_letters)}개의 자소서가 성공적으로 생성되었습니다! (자소서가 없는 지원자 {len(applicants_without_cover_letters)}명 중)",
            "generated_count": len(cover_letters),
            "total_applicants": len(applicants),
            "applicants_without_cover_letters": len(applicants_without_cover_letters)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자소서 데이터 생성 실패: {str(e)}")

@router.get("/cover-letters")
async def get_sample_cover_letters():
    """샘플 자소서 데이터 조회"""
    try:
        # 샘플 자소서 데이터
        sample_cover_letters = [
            {
                "id": 1,
                "name": "김철수",
                "position": "프론트엔드 개발자",
                "submittedDate": "2024-01-15",
                "content": """안녕하세요. 저는 소프트웨어 개발자로서 3년간의 경험을 쌓아온 김철수입니다.

기술적 역량
저는 Java, Spring Framework, React, Node.js 등 다양한 기술 스택을 보유하고 있습니다. 특히 마이크로서비스 아키텍처 설계와 클라우드 환경에서의 애플리케이션 배포에 대한 경험이 풍부합니다. 최근에는 AWS와 Docker를 활용한 CI/CD 파이프라인 구축 프로젝트를 성공적으로 완료했습니다.

직무 이해도
귀사의 혁신적인 기술 문화와 사용자 중심의 제품 개발 철학에 깊이 공감합니다. 특히 AI와 빅데이터를 활용한 새로운 서비스 개발에 대한 귀사의 비전이 저의 전문 분야와 일치한다고 생각합니다. 저는 이러한 기술을 활용하여 사용자에게 더 나은 가치를 제공하는 서비스를 개발하고 싶습니다.

성장 가능성
저는 지속적인 학습과 새로운 기술 습득에 대한 열정이 있습니다. 최근에는 머신러닝과 데이터 엔지니어링 분야에 관심을 가지고 관련 온라인 강의를 수강하고 있습니다. 또한 오픈소스 프로젝트에 기여하며 커뮤니티와 함께 성장하고 있습니다.

팀워크 및 커뮤니케이션
이전 회사에서는 5명의 개발팀에서 프로젝트 리더를 맡아 팀원들과의 원활한 소통을 통해 프로젝트를 성공적으로 완료했습니다. 다양한 배경을 가진 팀원들과의 협업을 통해 문제 해결 능력과 갈등 조정 능력을 향상시켰습니다.

지원 동기
귀사의 혁신적인 제품과 서비스가 사용자들의 삶을 어떻게 변화시키는지 지켜보며, 저도 이러한 가치 있는 일에 기여하고 싶다는 생각을 하게 되었습니다. 특히 귀사의 사용자 중심 설계 철학과 지속적인 혁신 추구가 저의 가치관과 일치합니다.

앞으로 귀사에서 더 많은 경험을 쌓으며 성장하고, 팀과 함께 사용자에게 가치 있는 서비스를 제공하는 개발자가 되고 싶습니다. 감사합니다."""
            },
            {
                "id": 2,
                "name": "이영희",
                "position": "백엔드 개발자",
                "submittedDate": "2024-01-14",
                "content": """안녕하세요. 백엔드 개발자 이영희입니다.

저는 4년간의 백엔드 개발 경험을 통해 Java, Spring Boot, MySQL, Redis 등의 기술 스택을 활용하여 다양한 웹 서비스를 개발해왔습니다. 특히 대용량 트래픽 처리와 데이터베이스 최적화에 대한 깊은 이해를 가지고 있습니다.

최근에는 마이크로서비스 아키텍처로의 전환 프로젝트를 주도하여 시스템의 확장성과 유지보수성을 크게 향상시켰습니다. 이 과정에서 Docker, Kubernetes를 활용한 컨테이너화와 CI/CD 파이프라인 구축 경험도 쌓았습니다.

귀사의 데이터 중심 의사결정과 고성능 시스템 구축에 대한 접근 방식에 깊이 공감합니다. 저의 기술적 경험과 문제 해결 능력을 바탕으로 귀사의 서비스 발전에 기여하고 싶습니다."""
            },
            {
                "id": 3,
                "name": "박민수",
                "position": "UI/UX 디자이너",
                "submittedDate": "2024-01-13",
                "content": """안녕하세요. UI/UX 디자이너 박민수입니다.

저는 사용자 중심의 디자인 철학을 바탕으로 3년간 다양한 디지털 제품의 사용자 경험을 설계해왔습니다. Figma, Sketch, Adobe Creative Suite를 활용하여 웹과 모바일 애플리케이션의 인터페이스를 디자인하고, 사용자 테스트를 통해 지속적으로 개선해왔습니다.

특히 접근성과 사용성을 고려한 디자인 시스템 구축에 대한 경험이 풍부하며, 개발팀과의 원활한 협업을 통해 아이디어를 실제 제품으로 구현하는 과정을 즐깁니다.

귀사의 혁신적인 제품과 사용자 중심의 디자인 철학에 깊이 공감하며, 저의 창의성과 기술적 이해를 바탕으로 더 나은 사용자 경험을 만들어가고 싶습니다."""
            },
            {
                "id": 4,
                "name": "최지영",
                "position": "데이터 사이언티스트",
                "submittedDate": "2024-01-12",
                "content": """안녕하세요. 데이터 사이언티스트 최지영입니다.

저는 통계학과 컴퓨터 과학을 전공하여 5년간 데이터 분석과 머신러닝 모델 개발에 종사해왔습니다. Python, R, SQL을 활용하여 대용량 데이터를 분석하고, TensorFlow, PyTorch를 사용하여 딥러닝 모델을 구축한 경험이 풍부합니다.

최근에는 추천 시스템 개발 프로젝트를 주도하여 사용자 만족도를 30% 향상시켰으며, A/B 테스트를 통한 데이터 기반 의사결정 프로세스를 구축했습니다.

귀사의 데이터 기반 비즈니스 모델과 AI 기술 활용에 대한 비전에 깊이 공감합니다. 저의 분석 능력과 머신러닝 전문성을 바탕으로 귀사의 데이터 전략 수립에 기여하고 싶습니다."""
            },
            {
                "id": 5,
                "name": "정현우",
                "position": "DevOps 엔지니어",
                "submittedDate": "2024-01-11",
                "content": """안녕하세요. DevOps 엔지니어 정현우입니다.

저는 6년간의 시스템 운영과 인프라 관리 경험을 통해 클라우드 환경에서의 안정적인 서비스 운영에 대한 전문성을 쌓아왔습니다. AWS, Azure, GCP 등 다양한 클라우드 플랫폼에서의 인프라 구축과 관리 경험이 풍부합니다.

특히 Kubernetes, Docker를 활용한 컨테이너 오케스트레이션과 Terraform, Ansible을 통한 Infrastructure as Code 구현에 대한 깊은 이해를 가지고 있습니다. 또한 모니터링 도구인 Prometheus, Grafana를 활용한 시스템 성능 모니터링과 로그 분석 경험도 보유하고 있습니다.

귀사의 클라우드 네이티브 아키텍처와 자동화된 배포 파이프라인 구축에 대한 접근 방식에 깊이 공감합니다. 저의 인프라 관리 경험과 자동화 기술을 바탕으로 귀사의 시스템 안정성과 개발 효율성 향상에 기여하고 싶습니다."""
            }
        ]

        return {
            "success": True,
            "message": "샘플 자소서 데이터를 성공적으로 조회했습니다.",
            "cover_letters": sample_cover_letters
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"샘플 자소서 데이터 조회에 실패했습니다: {str(e)}"
        }

@router.post("/create-single-applicant")
async def create_single_applicant(
    request: dict,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """개별 지원자를 생성합니다."""
    try:
        # 필수 필드 검증
        required_fields = ["name", "email"]
        for field in required_fields:
            if not request.get(field):
                raise HTTPException(
                    status_code=400,
                    detail=f"필수 필드가 누락되었습니다: {field}"
                )

        # 이메일 중복 확인
        existing_applicant = await db.applicants.find_one({"email": request["email"]})
        if existing_applicant:
            raise HTTPException(
                status_code=400,
                detail=f"이미 존재하는 이메일입니다: {request['email']}"
            )

        # 기존 채용공고 확인
        job_postings = await db.job_postings.find().to_list(1000)
        if not job_postings:
            raise HTTPException(
                status_code=400,
                detail="지원자를 생성하기 전에 먼저 채용공고를 생성해주세요."
            )

        # 랜덤 채용공고 선택
        selected_job = random.choice(job_postings)

        # 지원자 데이터 생성
        applicant_data = {
            "name": request["name"],
            "email": request["email"],
            "phone": request.get("phone", f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"),
            "position": selected_job.get("position", "개발자"),
            "experience": f"{random.randint(1, 10)}년",
            "skills": request.get("skills", "JavaScript, React, Node.js"),
            "status": random.choice(["서류합격", "면접대기", "보류", "서류불합격"]),
            "job_posting_id": str(selected_job["_id"]),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analysisScore": random.randint(60, 95),
            "department": selected_job.get("department", "개발팀"),
            "growthBackground": f"{request['name']}의 성장 배경 및 학습 경험",
            "motivation": f"{selected_job.get('position', '개발자')} 직무에 대한 {request['name']}의 지원 동기",
            "careerHistory": f"{random.randint(1, 10)}년 경력의 {request['name']}의 주요 업무 경험",
            "resume_id": str(ObjectId()),
            "cover_letter_id": str(ObjectId()),
            "portfolio_id": str(ObjectId()),
            "github_url": request.get("github_url", f"https://github.com/{request['name'].lower()}"),
            "linkedin_url": f"https://linkedin.com/in/{request['name'].lower()}",
            "portfolio_url": f"https://portfolio.example.com/{request['name'].lower()}",
            "ranks": {
                "resume": random.randint(70, 95),
                "coverLetter": random.randint(65, 90),
                "portfolio": random.randint(70, 95),
                "total": random.randint(70, 90)
            }
        }

        # MongoDB에 저장
        result = await db.applicants.insert_one(applicant_data)

        return {
            "success": True,
            "message": f"{request['name']} 지원자가 성공적으로 생성되었습니다!",
            "applicant_id": str(result.inserted_id),
            "job_posting": {
                "title": selected_job.get("title"),
                "position": selected_job.get("position"),
                "company": selected_job.get("company")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개별 지원자 생성 중 오류가 발생했습니다: {str(e)}")
