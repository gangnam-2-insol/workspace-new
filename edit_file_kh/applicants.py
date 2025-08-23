from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from models.applicant import Applicant, ApplicantCreate
from services.mongo_service import MongoService
import os

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoService(mongo_uri)

@router.post("/", response_model=Applicant)
async def create_or_get_applicant(
    applicant_data: ApplicantCreate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 생성하거나 기존 지원자를 조회합니다."""
    try:
        applicant = mongo_service.create_or_get_applicant(applicant_data)
        return applicant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 생성/조회 실패: {str(e)}")

@router.get("/")
async def get_all_applicants(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(50, ge=1, le=1000, description="가져올 개수"),
    status: Optional[str] = Query(None, description="상태 필터"),
    position: Optional[str] = Query(None, description="직무 필터"),
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """모든 지원자 목록을 조회합니다."""
    try:
        result = await mongo_service.get_all_applicants(skip=skip, limit=limit, status=status, position=position)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 조회합니다."""
    applicant = mongo_service.get_applicant(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
    return applicant

@router.put("/{applicant_id}/status")
async def update_applicant_status(
    applicant_id: str,
    status_data: dict,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 상태를 업데이트합니다."""
    try:
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="상태 값이 필요합니다")
        
        result = mongo_service.update_applicant_status(applicant_id, new_status)
        if not result:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        return {"message": "상태가 성공적으로 업데이트되었습니다", "status": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 업데이트 실패: {str(e)}")

@router.get("/stats/overview")
async def get_applicant_stats(
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 통계를 조회합니다."""
    try:
        stats = mongo_service.get_applicant_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
