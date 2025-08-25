from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from models.applicant import Applicant, ApplicantCreate
from services.mongo_service import MongoService
from similarity_service import SimilarityService
from embedding_service import EmbeddingService
from vector_service import VectorService
import os

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# MongoDB 서비스 의존성
def get_mongo_service():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoService(mongo_uri)

# SimilarityService 의존성
def get_similarity_service():
    # 환경 변수에서 API 키 로드
    pinecone_api_key = os.getenv("PINECONE_API_KEY", "dummy-key")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
    
    embedding_service = EmbeddingService()
    vector_service = VectorService(
        api_key=pinecone_api_key,
        index_name=pinecone_index_name
    )
    return SimilarityService(embedding_service, vector_service)

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
        
        result = await mongo_service.update_applicant_status(applicant_id, new_status)
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
        stats = await mongo_service.get_applicant_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.post("/similar")
async def search_similar_applicants(
    search_criteria: Dict[str, Any],
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """유사한 지원자를 검색합니다."""
    try:
        print(f"[INFO] 유사 지원자 검색 요청 - 기준: {search_criteria}")
        
        # 검색 기준 추출
        position = search_criteria.get("position", "")
        skills = search_criteria.get("skills", "")
        experience = search_criteria.get("experience", "")
        department = search_criteria.get("department", "")
        
        # 유사도 서비스 초기화
        similarity_service = get_similarity_service()
        
        # 유사 지원자 검색 수행
        similar_applicants = await similarity_service.find_similar_applicants(
            position=position,
            skills=skills,
            experience=experience,
            department=department,
            limit=10
        )
        
        return {
            "status": "success",
            "applicants": similar_applicants,
            "search_criteria": search_criteria,
            "message": f"{len(similar_applicants)}명의 유사한 지원자를 발견했습니다."
        }
    
    except Exception as e:
        print(f"[ERROR] 유사 지원자 검색 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"유사 지원자 검색 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{applicant_id}/recommendations")
async def get_talent_recommendations(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """지원자 기반 유사 인재 추천"""
    try:
        print(f"[INFO] 유사 인재 추천 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        from bson import ObjectId
        applicant_collection = mongo_service.db.applicants
        target_applicant = await applicant_collection.find_one({"_id": ObjectId(applicant_id)})
        
        if not target_applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 2. 유사도 서비스 초기화
        similarity_service = get_similarity_service()
        
        # 3. 유사 인재 추천 수행
        result = await similarity_service.search_similar_applicants_hybrid(
            target_applicant=target_applicant,
            applicants_collection=applicant_collection,
            limit=5
        )
        
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "recommendations": result,
            "message": "유사 인재 추천 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 유사 인재 추천 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"유사 인재 추천 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{applicant_id}/cover-letter")
async def get_cover_letter(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """자소서 조회"""
    try:
        print(f"[INFO] 자소서 조회 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        applicant = mongo_service.get_applicant(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 2. 자소서 존재 확인
        if not applicant.get("cover_letter"):
            raise HTTPException(status_code=404, detail="자소서가 없습니다")
        
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "cover_letter": applicant["cover_letter"],
            "message": "자소서 조회 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"자소서 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{applicant_id}/resume")
async def get_resume(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """이력서 조회"""
    try:
        print(f"[INFO] 이력서 조회 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        applicant = mongo_service.get_applicant(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "resume": applicant,
            "message": "이력서 조회 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 이력서 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"이력서 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{applicant_id}/portfolio")
async def get_portfolio(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """포트폴리오 조회"""
    try:
        print(f"[INFO] 포트폴리오 조회 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        applicant = mongo_service.get_applicant(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 2. 포트폴리오 존재 확인
        if not applicant.get("portfolio"):
            raise HTTPException(status_code=404, detail="포트폴리오가 없습니다")
        
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "portfolio": applicant["portfolio"],
            "message": "포트폴리오 조회 완료"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 포트폴리오 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"포트폴리오 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/{applicant_id}/cover-letter")
async def check_cover_letter_plagiarism(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """자소서 표절체크 (호환성을 위한 별명 엔드포인트)"""
    try:
        print(f"[INFO] 자소서 표절체크 요청 - applicant_id: {applicant_id}")
        
        # 1. 지원자 존재 확인
        applicant = mongo_service.get_applicant(applicant_id)
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 2. 자소서 존재 확인
        if not applicant.get("cover_letter"):
            raise HTTPException(status_code=404, detail="자소서가 없습니다")
        
        # 3. 유사도 서비스 초기화
        similarity_service = get_similarity_service()
        
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
