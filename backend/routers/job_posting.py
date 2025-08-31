import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate, JobStatus
from modules.job_posting.duties_separator import DutiesSeparator
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/job-postings", tags=["job-postings"])

# MongoDB 연결 의존성
def get_database():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    return client.hireme

@router.post("/", response_model=JobPosting)
async def create_job_posting(
    job_posting: JobPostingCreate,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """새로운 채용공고를 생성합니다."""
    import time
    start_time = time.time()

    print(f"\n📝 [채용공고 생성] API 호출 시작 ================================")
    print(f"🕐 시작 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 입력 데이터 분석
        job_data = job_posting.dict()

        print(f"📊 [입력 데이터 분석]:")
        print(f"    📋 총 필드 수: {len(job_data)}개")
        print(f"    📝 제목: {job_data.get('title', 'N/A')}")
        print(f"    🏢 부서: {job_data.get('department', 'N/A')}")
        print(f"    💼 직무: {job_data.get('position', 'N/A')}")
        print(f"    👥 모집인원: {job_data.get('headcount', 'N/A')}")
        print(f"    💰 급여: {job_data.get('salary', 'N/A')}")
        print(f"    📍 위치: {job_data.get('location', 'N/A')}")
        print(f"    📧 연락처: {job_data.get('contact_email', 'N/A')}")
        print(f"    📅 마감일: {job_data.get('deadline', 'N/A')}")

        # 주요업무 분석
        main_duties = job_data.get('main_duties', '')
        if main_duties:
            print(f"    📋 주요업무 길이: {len(main_duties)}자")
            print(f"    📋 주요업무 미리보기: {main_duties[:100]}...")

        # 분리된 업무 필드 확인
        separated_fields = ['core_responsibilities', 'daily_tasks', 'project_tasks',
                          'collaboration_tasks', 'technical_tasks', 'management_tasks']
        separated_count = sum(1 for field in separated_fields if job_data.get(field))
        print(f"    🔄 분리된 업무 필드: {separated_count}/{len(separated_fields)}개")

        if separated_count > 0:
            print(f"    📋 분리된 필드 상세:")
            for field in separated_fields:
                if job_data.get(field):
                    content = job_data[field]
                    print(f"      - {field}: {len(content)}자")

        # 데이터 보강
        job_data["created_at"] = datetime.now()
        job_data["updated_at"] = datetime.now()
        job_data["status"] = JobStatus.PUBLISHED  # 모든 채용공고를 활성화 상태로 통일
        job_data["applicants"] = 0
        job_data["views"] = 0
        job_data["bookmarks"] = 0
        job_data["shares"] = 0

        print(f"📊 [데이터 보강] 완료 - 메타데이터 추가")
        print(f"    📝 상태: {job_data['status']}")
        print(f"    🕐 생성일: {job_data['created_at']}")

        # DB 삽입
        insert_start = time.time()
        result = await db.job_postings.insert_one(job_data)
        insert_time = time.time() - insert_start

        job_data["id"] = str(result.inserted_id)

        print(f"💾 [DB 삽입] 완료:")
        print(f"    ⏱️ 소요시간: {insert_time:.3f}초")
        print(f"    🆔 생성된 ID: {job_data['id']}")
        print(f"    📊 최종 데이터 크기: {len(str(job_data))}자")

        total_time = time.time() - start_time
        print(f"🎉 [채용공고 생성 완료] 총 소요시간: {total_time:.3f}초")
        print(f"================================================\n")

        return JobPosting(**job_data)

    except Exception as e:
        error_time = time.time() - start_time

        print(f"❌ [채용공고 생성 실패] ================================")
        print(f"⏱️ 실패까지 소요시간: {error_time:.3f}초")
        print(f"🔍 오류 타입: {type(e).__name__}")
        print(f"📄 오류 메시지: {str(e)}")

        # 입력 데이터 오류 분석
        if hasattr(job_posting, 'dict'):
            try:
                data_analysis = job_posting.dict()
                print(f"📊 [오류 발생시 입력 데이터]:")
                print(f"    📝 제목: {data_analysis.get('title', 'N/A')}")
                print(f"    🏢 부서: {data_analysis.get('department', 'N/A')}")
                print(f"    📊 데이터 크기: {len(str(data_analysis))}자")
            except:
                print(f"📊 [입력 데이터] 분석 불가")

        # 스택 트레이스 출력
        import traceback
        print(f"📊 스택 트레이스:")
        traceback.print_exc()
        print(f"================================================\n")

        raise HTTPException(status_code=500, detail=f"채용공고 생성 실패: {str(e)}")

@router.get("/", response_model=List[JobPosting])
async def get_job_postings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[JobStatus] = Query(None),
    company: Optional[str] = Query(None),
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고 목록을 조회합니다."""
    try:
        # 필터 조건 구성
        filter_query = {}
        if status:
            filter_query["status"] = status
        if company:
            filter_query["company"] = {"$regex": company, "$options": "i"}

        # 총 개수 조회
        total_count = await db.job_postings.count_documents(filter_query)

        # 페이징으로 데이터 조회
        cursor = db.job_postings.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        job_postings = await cursor.to_list(length=limit)

        # ObjectId를 문자열로 변환하고 필드 매핑
        result_jobs = []
        for job in job_postings:
            # _id를 id로 변환
            job["id"] = str(job["_id"])
            del job["_id"]

            # 필수 필드가 없는 경우 기본값 설정
            if "title" not in job or not job["title"]:
                job["title"] = "제목 없음"
            if "company" not in job or not job["company"]:
                job["company"] = "회사명 없음"
            if "location" not in job or not job["location"]:
                job["location"] = "근무지 없음"
            if "type" not in job or not job["type"]:
                # 픽톡 데이터의 employment_type을 type으로 매핑
                if job.get("employment_type"):
                    job["type"] = job["employment_type"]
                elif job.get("work_type"):
                    job["type"] = job["work_type"]
                else:
                    job["type"] = "full-time"  # 기본값

            # type 필드 값 정규화 (한국어 → 영어)
            if "type" in job:
                type_mapping = {
                    "정규직": "full-time",
                    "계약직": "contract",
                    "파트타임": "part-time",
                    "인턴": "internship"
                }
                if job["type"] in type_mapping:
                    job["type"] = type_mapping[job["type"]]

            # status 값 정규화
            if "status" in job:
                status_value = job["status"]
                if status_value == "active":
                    job["status"] = "published"
                elif status_value not in ["draft", "published", "closed", "expired"]:
                    job["status"] = "draft"

            # salary 필드 처리 (딕셔너리를 문자열로 변환)
            if "salary" in job and isinstance(job["salary"], dict):
                salary_dict = job["salary"]
                if "min" in salary_dict and "max" in salary_dict:
                    min_salary = salary_dict["min"]
                    max_salary = salary_dict["max"]
                    currency = salary_dict.get("currency", "KRW")
                    job["salary"] = f"{min_salary:,}~{max_salary:,} {currency}"
                else:
                    job["salary"] = str(salary_dict)
            elif "salary" in job and not isinstance(job["salary"], str):
                job["salary"] = str(job["salary"])

            # benefits 필드 처리 (리스트를 문자열로 변환)
            if "benefits" in job and isinstance(job["benefits"], list):
                job["benefits"] = ", ".join(job["benefits"])

            # requirements 필드 처리 (리스트를 문자열로 변환)
            if "requirements" in job and isinstance(job["requirements"], list):
                job["requirements"] = ", ".join(job["requirements"])

            # required_skills 필드 처리 (문자열을 리스트로 변환)
            if "required_skills" in job and isinstance(job["required_skills"], str):
                job["required_skills"] = [skill.strip() for skill in job["required_skills"].split(",") if skill.strip()]
            elif "required_skills" not in job:
                job["required_skills"] = []

            # preferred_skills 필드 처리
            if "preferred_skills" in job and isinstance(job["preferred_skills"], str):
                job["preferred_skills"] = [skill.strip() for skill in job["preferred_skills"].split(",") if skill.strip()]
            elif "preferred_skills" not in job:
                job["preferred_skills"] = []

            # job_keywords 필드 처리
            if "job_keywords" not in job:
                job["job_keywords"] = []

            # required_documents 필드 처리
            if "required_documents" not in job:
                job["required_documents"] = ["resume"]

            # skill_weights 필드 처리
            if "skill_weights" not in job:
                job["skill_weights"] = {}

            # culture_requirements 필드 처리
            if "culture_requirements" not in job:
                job["culture_requirements"] = []

            try:
                result_jobs.append(JobPosting(**job))
            except Exception as validation_error:
                print(f"Validation error for job {job.get('id', 'unknown')}: {validation_error}")
                # 유효하지 않은 데이터는 건너뛰기
                continue

        return result_jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 목록 조회 실패: {str(e)}")

@router.get("/{job_id}", response_model=JobPosting)
async def get_job_posting(
    job_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """특정 채용공고를 조회합니다."""
    try:
        # 조회수 증가
        await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {"$inc": {"views": 1}}
        )

        job_posting = await db.job_postings.find_one({"_id": ObjectId(job_id)})
        if not job_posting:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        job_posting["id"] = str(job_posting["_id"])
        del job_posting["_id"]

        return JobPosting(**job_posting)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 조회 실패: {str(e)}")

@router.put("/{job_id}", response_model=JobPosting)
async def update_job_posting(
    job_id: str,
    job_update: JobPostingUpdate,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고를 수정합니다."""
    try:
        update_data = job_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now()

        result = await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        # 업데이트된 데이터 조회
        updated_job = await db.job_postings.find_one({"_id": ObjectId(job_id)})
        updated_job["id"] = str(updated_job["_id"])
        del updated_job["_id"]

        return JobPosting(**updated_job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 수정 실패: {str(e)}")

@router.delete("/{job_id}")
async def delete_job_posting(
    job_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고를 삭제합니다."""
    try:
        result = await db.job_postings.delete_one({"_id": ObjectId(job_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        return {"message": "채용공고가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 삭제 실패: {str(e)}")

@router.patch("/{job_id}/publish")
async def publish_job_posting(
    job_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고를 발행합니다."""
    try:
        result = await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": JobStatus.PUBLISHED,
                    "updated_at": datetime.now()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        return {"message": "채용공고가 성공적으로 발행되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 발행 실패: {str(e)}")

@router.patch("/{job_id}/close")
async def close_job_posting(
    job_id: str,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고를 마감합니다."""
    try:
        result = await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": JobStatus.CLOSED,
                    "updated_at": datetime.now()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        return {"message": "채용공고가 성공적으로 마감되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채용공고 마감 실패: {str(e)}")

@router.get("/stats/overview")
async def get_job_posting_stats(
    db: AsyncIOMotorClient = Depends(get_database)
):
    """채용공고 통계를 조회합니다."""
    try:
        # 전체 통계
        total_jobs = await db.job_postings.count_documents({})
        draft_jobs = await db.job_postings.count_documents({"status": JobStatus.DRAFT})
        published_jobs = await db.job_postings.count_documents({"status": JobStatus.PUBLISHED})
        closed_jobs = await db.job_postings.count_documents({"status": JobStatus.CLOSED})

        # 총 조회수, 지원자 수
        stats = await db.job_postings.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total_views": {"$sum": "$views"},
                    "total_applicants": {"$sum": "$applicants"},
                    "total_bookmarks": {"$sum": "$bookmarks"},
                    "total_shares": {"$sum": "$shares"}
                }
            }
        ]).to_list(1)

        stats_data = stats[0] if stats else {
            "total_views": 0,
            "total_applicants": 0,
            "total_bookmarks": 0,
            "total_shares": 0
        }

        return {
            "total_jobs": total_jobs,
            "draft_jobs": draft_jobs,
            "published_jobs": published_jobs,
            "closed_jobs": closed_jobs,
            "total_views": stats_data["total_views"],
            "total_applicants": stats_data["total_applicants"],
            "total_bookmarks": stats_data["total_bookmarks"],
            "total_shares": stats_data["total_shares"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.post("/separate-duties")
async def separate_main_duties(request_data: dict):
    """주요업무 텍스트를 여러 필드로 분리합니다."""
    try:
        main_duties = request_data.get("main_duties", "")

        if not main_duties or not main_duties.strip():
            raise HTTPException(status_code=400, detail="주요업무 내용이 필요합니다.")

        # 주요업무 분리 서비스 사용
        duties_separator = DutiesSeparator()
        separated_duties = duties_separator.separate_duties(main_duties)
        summary = duties_separator.get_separation_summary(separated_duties)

        return {
            "success": True,
            "original_duties": main_duties,
            "separated_duties": separated_duties,
            "summary": summary,
            "message": f"{summary['total_categories']}개 카테고리로 분리되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주요업무 분리 실패: {str(e)}")

@router.post("/{job_id}/apply-separated-duties")
async def apply_separated_duties(
    job_id: str,
    separated_duties: dict,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """분리된 주요업무를 채용공고에 적용합니다."""
    try:
        # 분리된 업무 데이터 검증
        valid_fields = [
            'core_responsibilities', 'daily_tasks', 'project_tasks',
            'collaboration_tasks', 'technical_tasks', 'management_tasks'
        ]

        update_data = {}
        for field in valid_fields:
            if field in separated_duties and separated_duties[field]:
                update_data[field] = separated_duties[field]

        update_data["updated_at"] = datetime.now()

        # DB 업데이트
        result = await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="채용공고를 찾을 수 없습니다")

        # 업데이트된 데이터 조회
        updated_job = await db.job_postings.find_one({"_id": ObjectId(job_id)})
        updated_job["id"] = str(updated_job["_id"])
        del updated_job["_id"]

        return {
            "success": True,
            "message": "분리된 주요업무가 성공적으로 적용되었습니다.",
            "updated_fields": list(update_data.keys()),
            "job_posting": updated_job
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분리된 업무 적용 실패: {str(e)}")

@router.post("/separate-duties-smart")
async def separate_main_duties_smart(request_data: dict):
    """스마트 주요업무 분리 및 추출 (가장 적합한 내용 자동 선별)"""
    import time
    start_time = time.time()

    print(f"\n🤖 [스마트 분리] API 호출 시작")

    try:
        main_duties = request_data.get("main_duties", "")

        if not main_duties or not main_duties.strip():
            raise HTTPException(status_code=400, detail="주요업무 내용이 필요합니다.")

        print(f"📝 원본 텍스트: {main_duties[:100]}...")
        print(f"📏 텍스트 길이: {len(main_duties)}자")

        # 스마트 분리 수행
        duties_separator = DutiesSeparator()
        smart_result = duties_separator.separate_duties_with_smart_extraction(main_duties)

        processing_time = time.time() - start_time

        print(f"✅ [스마트 분리] 완료 (소요시간: {processing_time:.3f}초)")
        print(f"📊 [분리 결과] 품질점수: {smart_result['smart_extraction']['quality_score']:.2f}")
        print(f"🎯 [추천 내용] 길이: {len(smart_result['smart_extraction']['recommended_content'])}자")

        # 응답 데이터 구성
        response_data = {
            "success": True,
            "original_duties": main_duties,
            "separated_duties": smart_result['separated_duties'],
            "smart_extraction": smart_result['smart_extraction'],
            "processing_info": smart_result['processing_info'],
            "summary": {
                "total_categories": smart_result['processing_info']['categories_found'],
                "original_length": smart_result['processing_info']['total_length'],
                "extraction_quality": smart_result['smart_extraction']['quality_score'],
                "recommended_length": len(smart_result['smart_extraction']['recommended_content']),
                "processing_time": processing_time,
                "primary_categories": len(smart_result['smart_extraction']['display_suggestions']['primary_display']),
                "secondary_categories": len(smart_result['smart_extraction']['display_suggestions']['secondary_display'])
            },
            "message": f"스마트 분리 완료 (품질점수: {smart_result['smart_extraction']['quality_score']:.1f})"
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)

        print(f"❌ [스마트 분리] 실패 (소요시간: {processing_time:.3f}초)")
        print(f"📄 오류: {error_msg}")

        raise HTTPException(status_code=500, detail=f"스마트 분리 실패: {error_msg}")


@router.post("/extract-fields")
async def extract_job_fields(
    request: dict
):
    """사용자 입력에서 산업 분야와 직무 카테고리를 추출합니다."""
    try:
        user_input = request.get("input_text", "")
        if not user_input:
            raise HTTPException(status_code=400, detail="입력 텍스트가 필요합니다.")

        # 기존 필드들 (부서, 직무, 업무내용 등)
        department = request.get("department", "")
        position = request.get("position", "")
        main_duties = request.get("main_duties", "")

        # 전체 텍스트 결합
        combined_text = f"{department} {position} {main_duties} {user_input}".strip()

        # 산업 분야 추출
        industry = extract_industry_field(combined_text)

        # 직무 카테고리 추출
        job_category = extract_job_category(combined_text)

        return {
            "success": True,
            "extracted_fields": {
                "industry": industry,
                "job_category": job_category
            },
            "confidence_scores": {
                "industry": calculate_confidence_score(combined_text, industry, "industry"),
                "job_category": calculate_confidence_score(combined_text, job_category, "job_category")
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분야 추출 실패: {str(e)}")


def extract_industry_field(text: str) -> str:
    """텍스트에서 산업 분야를 추출합니다."""
    text_lower = text.lower()

    # 산업 분야 키워드 매핑
    industry_keywords = {
        "IT/소프트웨어": [
            "개발", "프로그래밍", "소프트웨어", "웹", "앱", "시스템", "서버", "데이터베이스",
            "프론트엔드", "백엔드", "풀스택", "모바일", "웹개발", "앱개발", "시스템개발",
            "python", "java", "javascript", "react", "vue", "angular", "node.js", "spring",
            "django", "flask", "aws", "azure", "docker", "kubernetes", "ai", "머신러닝",
            "딥러닝", "데이터사이언스", "빅데이터", "클라우드", "devops", "it", "기술"
        ],
        "금융/보험": [
            "금융", "은행", "보험", "증권", "투자", "자산관리", "펀드", "대출", "신용",
            "핀테크", "페이", "결제", "송금", "카드", "finance", "banking", "insurance"
        ],
        "제조업": [
            "제조", "생산", "공장", "제품", "품질관리", "생산관리", "제조업", "공정",
            "설비", "기계", "자동차", "전자", "화학", "manufacturing", "production"
        ],
        "유통/서비스": [
            "유통", "서비스", "판매", "마케팅", "영업", "고객서비스", "cs", "상품기획",
            "브랜드", "온라인쇼핑", "이커머스", "retail", "commerce", "sales", "marketing"
        ],
        "미디어/엔터테인먼트": [
            "미디어", "방송", "콘텐츠", "게임", "엔터테인먼트", "영상", "음악", "디자인",
            "광고", "크리에이티브", "media", "entertainment", "content", "game", "creative"
        ],
        "의료/바이오": [
            "의료", "병원", "바이오", "제약", "헬스케어", "의학", "간호", "치료",
            "건강", "medical", "healthcare", "bio", "pharma", "health"
        ],
        "교육": [
            "교육", "학교", "강의", "교사", "선생님", "교수", "학습", "교육기관",
            "education", "teaching", "school", "university", "learning"
        ]
    }

    # 각 분야별 점수 계산
    field_scores = {}
    for industry, keywords in industry_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        field_scores[industry] = score

    # 가장 높은 점수를 가진 분야 반환
    if field_scores:
        best_industry = max(field_scores, key=field_scores.get)
        if field_scores[best_industry] > 0:
            return best_industry

    # 추출 실패 시 기본값: IT/소프트웨어
    return "IT/소프트웨어"


def extract_job_category(text: str) -> str:
    """텍스트에서 직무 카테고리를 추출합니다."""
    text_lower = text.lower()

    # 직무 카테고리 키워드 매핑
    category_keywords = {
        "개발": [
            "개발", "프로그래밍", "코딩", "개발자", "프로그래머", "엔지니어", "시스템",
            "소프트웨어", "웹", "앱", "모바일", "프론트엔드", "백엔드", "풀스택",
            "developer", "programmer", "engineer", "programming", "coding", "development"
        ],
        "기획": [
            "기획", "전략", "pm", "기획자", "프로덕트", "서비스기획", "사업기획",
            "product", "planning", "strategy", "manager", "planner"
        ],
        "디자인": [
            "디자인", "디자이너", "ui", "ux", "그래픽", "웹디자인", "앱디자인",
            "시각디자인", "design", "designer", "graphic", "visual"
        ],
        "마케팅": [
            "마케팅", "광고", "홍보", "브랜드", "퍼포먼스", "디지털마케팅", "sns",
            "marketing", "advertising", "promotion", "brand", "digital"
        ],
        "영업": [
            "영업", "세일즈", "판매", "고객", "b2b", "b2c", "sales", "selling"
        ],
        "운영": [
            "운영", "관리", "cs", "고객서비스", "품질관리", "생산관리", "운영관리",
            "operation", "management", "service", "quality"
        ],
        "인사": [
            "인사", "hr", "채용", "교육", "조직", "인력", "human", "resource", "recruiting"
        ]
    }

    # 각 카테고리별 점수 계산
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        category_scores[category] = score

    # 가장 높은 점수를 가진 카테고리 반환
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category

    # 추출 실패 시 기본값: 개발
    return "개발"


def calculate_confidence_score(text: str, extracted_field: str, field_type: str) -> float:
    """추출된 필드의 신뢰도 점수를 계산합니다."""
    # 기본값인 경우 낮은 신뢰도 반환
    if (field_type == "industry" and extracted_field == "IT/소프트웨어") or \
       (field_type == "job_category" and extracted_field == "개발"):
        # 텍스트에 관련 키워드가 있는지 확인
        text_lower = text.lower()
        if field_type == "industry":
            it_keywords = ["개발", "프로그래밍", "소프트웨어", "웹", "앱", "시스템", "it"]
            if any(keyword in text_lower for keyword in it_keywords):
                return 0.7  # 키워드가 있으면 높은 신뢰도
            else:
                return 0.4  # 기본값이지만 키워드가 없으면 낮은 신뢰도
        else:  # job_category
            dev_keywords = ["개발", "프로그래밍", "코딩", "개발자", "프로그래머", "엔지니어"]
            if any(keyword in text_lower for keyword in dev_keywords):
                return 0.7  # 키워드가 있으면 높은 신뢰도
            else:
                return 0.4  # 기본값이지만 키워드가 없으면 낮은 신뢰도

    text_lower = text.lower()

    # 필드별 키워드 수 계산
    if field_type == "industry":
        industry_keywords = {
            "IT/소프트웨어": [
                "개발", "프로그래밍", "소프트웨어", "웹", "앱", "시스템", "서버",
                "python", "java", "javascript", "react", "vue", "ai", "머신러닝"
            ],
            "금융/보험": ["금융", "은행", "보험", "증권", "투자", "핀테크", "페이"],
            "제조업": ["제조", "생산", "공장", "제품", "품질관리", "생산관리"],
            "유통/서비스": ["유통", "서비스", "판매", "마케팅", "영업", "이커머스"],
            "미디어/엔터테인먼트": ["미디어", "방송", "콘텐츠", "게임", "광고", "크리에이티브"],
            "의료/바이오": ["의료", "병원", "바이오", "제약", "헬스케어"],
            "교육": ["교육", "학교", "강의", "교사", "선생님"]
        }
        keywords = industry_keywords.get(extracted_field, [])
    else:  # job_category
        category_keywords = {
            "개발": ["개발", "프로그래밍", "코딩", "개발자", "프로그래머", "엔지니어"],
            "기획": ["기획", "전략", "pm", "기획자", "프로덕트", "서비스기획"],
            "디자인": ["디자인", "디자이너", "ui", "ux", "그래픽", "웹디자인"],
            "마케팅": ["마케팅", "광고", "홍보", "브랜드", "퍼포먼스"],
            "영업": ["영업", "세일즈", "판매", "고객", "b2b"],
            "운영": ["운영", "관리", "cs", "고객서비스", "품질관리"],
            "인사": ["인사", "hr", "채용", "교육", "조직"]
        }
        keywords = category_keywords.get(extracted_field, [])

    # 매칭된 키워드 수 계산
    matched_keywords = sum(1 for keyword in keywords if keyword in text_lower)

    # 신뢰도 점수 계산 (0.5 ~ 1.0)
    if matched_keywords == 0:
        return 0.5
    elif matched_keywords <= 2:
        return 0.6 + (matched_keywords * 0.1)
    else:
        return min(0.9, 0.6 + (matched_keywords * 0.05))
