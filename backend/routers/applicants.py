from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from models.applicant import Applicant, ApplicantCreate
from services.mongo_service import MongoService
from similarity_service import SimilarityService
import os

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoService(mongo_uri)

@router.get("/", response_model=dict)
async def get_applicants(
    skip: int = 0,
    limit: int = 20,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 목록을 조회합니다."""
    try:
        result = await mongo_service.get_applicants(skip=skip, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

@router.post("/", response_model=Applicant)
async def create_or_get_applicant(
    applicant_data: ApplicantCreate,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 생성하거나 기존 지원자를 조회합니다."""
    try:
        result = await mongo_service.create_or_get_applicant(applicant_data.dict())
        return result["applicant"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 생성/조회 실패: {str(e)}")

@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자를 조회합니다."""
    applicant = await mongo_service.get_applicant_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
    return applicant

@router.post("/{applicant_id}/cover-letter")
async def check_cover_letter_plagiarism(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """자소서 표절체크 (호환성을 위한 별명 엔드포인트)"""
    try:
        print(f"[INFO] 자소서 표절체크 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 2. 자소서 존재 확인
        if not applicant.get("cover_letter"):
            raise HTTPException(status_code=404, detail="자소서가 없습니다")
        
        # 3. 유사도 서비스 초기화
        similarity_service = SimilarityService()
        
        # 4. 자소서 표절체크 수행
        result = similarity_service.check_coverletter_similarity(
            applicant_id=applicant_id,
            cover_letter_text=applicant["cover_letter"]
        )
        
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "plagiarism_result": result,
            "message": "자소서 표절체크 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 표절체크 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"자소서 표절체크 중 오류가 발생했습니다: {str(e)}"
        )
