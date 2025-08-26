from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from services.mongo_service import MongoService
import os

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoService(mongo_uri)

@router.get("/applicant/{applicant_id}")
async def get_portfolio_by_applicant_id(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 ID로 포트폴리오를 조회합니다."""
    try:
        portfolio = mongo_service.get_portfolio_by_applicant_id(applicant_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="포트폴리오를 찾을 수 없습니다")
        return portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 조회 실패: {str(e)}")
