from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from models.applicant import Applicant, ApplicantCreate, ApplicantUpdate, ApplicantStatusUpdate
from services.mongo_service import MongoService
from services.suitability_ranking_service import SuitabilityRankingService
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# MongoDB 서비스 의존성
def get_mongo_service():
    from main import get_database
    db = get_database()
    return MongoService(db)

def get_ranking_service():
    from main import get_database
    db = get_database()
    return SuitabilityRankingService(db)

@router.get("/")
async def get_applicants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    position: Optional[str] = None,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 목록을 조회합니다."""
    try:
        applicants = await mongo_service.get_applicants(skip, limit, search, status, position)
        return {
            "applicants": applicants,
            "total": len(applicants),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"지원자 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

@router.get("/{applicant_id}")
async def get_applicant(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """특정 지원자 정보를 조회합니다."""
    try:
        applicant = await mongo_service.get_applicant(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
        return applicant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"지원자 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 조회 실패: {str(e)}")

@router.post("/")
async def create_applicant(
    applicant: ApplicantCreate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """새로운 지원자를 생성합니다."""
    try:
        result = await mongo_service.create_applicant(applicant)
        return {"message": "지원자가 성공적으로 생성되었습니다.", "applicant_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"지원자 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 생성 실패: {str(e)}")

@router.put("/{applicant_id}")
async def update_applicant(
    applicant_id: str,
    applicant_update: ApplicantUpdate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 정보를 업데이트합니다."""
    try:
        result = await mongo_service.update_applicant(applicant_id, applicant_update)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="업데이트할 지원자를 찾을 수 없습니다.")
        return {"message": "지원자 정보가 성공적으로 업데이트되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"지원자 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 업데이트 실패: {str(e)}")

@router.put("/{applicant_id}/status")
async def update_applicant_status(
    applicant_id: str,
    status_update: ApplicantStatusUpdate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 상태를 업데이트합니다."""
    try:
        result = await mongo_service.update_applicant_status(applicant_id, status_update.status)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="상태를 업데이트할 지원자를 찾을 수 없습니다.")
        return {"message": "지원자 상태가 성공적으로 업데이트되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"지원자 상태 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 상태 업데이트 실패: {str(e)}")

@router.delete("/{applicant_id}")
async def delete_applicant(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 삭제합니다."""
    try:
        result = await mongo_service.delete_applicant(applicant_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="삭제할 지원자를 찾을 수 없습니다.")
        return {"message": "지원자가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"지원자 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 삭제 실패: {str(e)}")

@router.get("/stats/overview")
async def get_applicant_stats(
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 통계를 조회합니다."""
    try:
        stats = await mongo_service.get_applicant_stats()
        return stats
    except Exception as e:
        logger.error(f"지원자 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 통계 조회 실패: {str(e)}")

# 적합도 랭킹 관련 API
@router.post("/calculate-rankings")
async def calculate_rankings(
    ranking_service: SuitabilityRankingService = Depends(get_ranking_service)
):
    """모든 지원자의 적합도 랭킹을 계산합니다."""
    try:
        result = await ranking_service.calculate_all_rankings()
        return result
    except Exception as e:
        logger.error(f"랭킹 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"랭킹 계산 실패: {str(e)}")

@router.get("/{applicant_id}/rankings")
async def get_applicant_rankings(
    applicant_id: str,
    ranking_service: SuitabilityRankingService = Depends(get_ranking_service)
):
    """특정 지원자의 랭킹 정보를 조회합니다."""
    try:
        rankings = await ranking_service.get_applicant_rankings(applicant_id)
        return rankings
    except Exception as e:
        logger.error(f"지원자 랭킹 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지원자 랭킹 조회 실패: {str(e)}")

@router.get("/rankings/top/{category}")
async def get_top_rankings(
    category: str,
    limit: int = Query(10, ge=1, le=100),
    ranking_service: SuitabilityRankingService = Depends(get_ranking_service)
):
    """특정 카테고리의 상위 랭킹을 조회합니다."""
    try:
        if category not in ["resume", "coverLetter", "portfolio", "total"]:
            raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다.")
        
        rankings = await ranking_service.get_top_rankings(category, limit)
        return {
            "category": category,
            "rankings": rankings,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상위 랭킹 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상위 랭킹 조회 실패: {str(e)}")
