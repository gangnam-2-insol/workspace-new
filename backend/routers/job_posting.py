from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os

from models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate, JobStatus

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
    try:
        job_data = job_posting.dict()
        job_data["created_at"] = datetime.now()
        job_data["updated_at"] = datetime.now()
        job_data["status"] = JobStatus.DRAFT
        job_data["applicants"] = 0
        job_data["views"] = 0
        job_data["bookmarks"] = 0
        job_data["shares"] = 0
        
        result = await db.job_postings.insert_one(job_data)
        job_data["id"] = str(result.inserted_id)
        
        return JobPosting(**job_data)
    except Exception as e:
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
            
            # status 값 정규화
            if "status" in job:
                status_value = job["status"]
                if status_value == "active":
                    job["status"] = "published"
                elif status_value not in ["draft", "published", "closed", "expired"]:
                    job["status"] = "draft"
            
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
