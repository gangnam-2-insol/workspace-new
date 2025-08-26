from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    ResumeCreate, Resume, ResumeUpdate, ResumeSearchRequest,
    ResumeAnalysisRequest, ResumeAnalysisResult
)
from .services import ResumeService
from ..shared.models import BaseResponse, PaginationParams

router = APIRouter(prefix="/api/resumes", tags=["이력서"])

def get_resume_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> ResumeService:
    return ResumeService(db)

@router.post("/", response_model=BaseResponse)
async def create_resume(
    resume_data: ResumeCreate,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 생성"""
    try:
        resume_id = await resume_service.create_resume(resume_data)
        return BaseResponse(
            success=True,
            message="이력서가 성공적으로 생성되었습니다.",
            data={"resume_id": resume_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 생성에 실패했습니다: {str(e)}"
        )

@router.get("/{resume_id}", response_model=BaseResponse)
async def get_resume(
    resume_id: str,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 조회"""
    try:
        resume = await resume_service.get_resume(resume_id)
        if not resume:
            return BaseResponse(
                success=False,
                message="이력서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="이력서 조회 성공",
            data=resume.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 조회에 실패했습니다: {str(e)}"
        )

@router.get("/", response_model=BaseResponse)
async def get_resumes(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    position: Optional[str] = None,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 목록 조회"""
    try:
        skip = (page - 1) * limit
        resumes = await resume_service.get_resumes(skip, limit, status, position)
        
        return BaseResponse(
            success=True,
            message="이력서 목록 조회 성공",
            data={
                "resumes": [resume.dict() for resume in resumes],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(resumes)
                }
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 목록 조회에 실패했습니다: {str(e)}"
        )

@router.put("/{resume_id}", response_model=BaseResponse)
async def update_resume(
    resume_id: str,
    update_data: ResumeUpdate,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 수정"""
    try:
        success = await resume_service.update_resume(resume_id, update_data)
        if not success:
            return BaseResponse(
                success=False,
                message="이력서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="이력서가 성공적으로 수정되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 수정에 실패했습니다: {str(e)}"
        )

@router.delete("/{resume_id}", response_model=BaseResponse)
async def delete_resume(
    resume_id: str,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 삭제"""
    try:
        success = await resume_service.delete_resume(resume_id)
        if not success:
            return BaseResponse(
                success=False,
                message="이력서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="이력서가 성공적으로 삭제되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 삭제에 실패했습니다: {str(e)}"
        )

@router.post("/search", response_model=BaseResponse)
async def search_resumes(
    search_request: ResumeSearchRequest,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 검색"""
    try:
        resumes = await resume_service.search_resumes(search_request)
        
        return BaseResponse(
            success=True,
            message="이력서 검색 성공",
            data={
                "resumes": [resume.dict() for resume in resumes],
                "total": len(resumes)
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 검색에 실패했습니다: {str(e)}"
        )

@router.post("/analyze", response_model=BaseResponse)
async def analyze_resume(
    analysis_request: ResumeAnalysisRequest,
    resume_service: ResumeService = Depends(get_resume_service)
):
    """이력서 분석"""
    try:
        analysis_result = await resume_service.analyze_resume(analysis_request)
        
        return BaseResponse(
            success=True,
            message="이력서 분석이 완료되었습니다.",
            data=analysis_result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이력서 분석에 실패했습니다: {str(e)}"
        )
