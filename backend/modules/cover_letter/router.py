from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    CoverLetterCreate, CoverLetter, CoverLetterUpdate
)
from .services import CoverLetterService
from ..shared.models import BaseResponse

router = APIRouter(prefix="/api/cover-letters", tags=["자기소개서"])

def get_cover_letter_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> CoverLetterService:
    return CoverLetterService(db)

@router.post("/", response_model=BaseResponse)
async def create_cover_letter(
    cover_letter_data: CoverLetterCreate,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 생성"""
    try:
        cover_letter_id = await cover_letter_service.create_cover_letter(cover_letter_data)
        return BaseResponse(
            success=True,
            message="자기소개서가 성공적으로 생성되었습니다.",
            data={"cover_letter_id": cover_letter_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자기소개서 생성에 실패했습니다: {str(e)}"
        )

@router.get("/{cover_letter_id}", response_model=BaseResponse)
async def get_cover_letter(
    cover_letter_id: str,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 조회"""
    try:
        cover_letter = await cover_letter_service.get_cover_letter(cover_letter_id)
        if not cover_letter:
            return BaseResponse(
                success=False,
                message="자기소개서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="자기소개서 조회 성공",
            data=cover_letter.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자기소개서 조회에 실패했습니다: {str(e)}"
        )

@router.get("/", response_model=BaseResponse)
async def get_cover_letters(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    applicant_id: Optional[str] = None,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 목록 조회"""
    try:
        skip = (page - 1) * limit
        cover_letters = await cover_letter_service.get_cover_letters(skip, limit, status, applicant_id)
        
        return BaseResponse(
            success=True,
            message="자기소개서 목록 조회 성공",
            data={
                "cover_letters": [cover_letter.dict() for cover_letter in cover_letters],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(cover_letters)
                }
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자기소개서 목록 조회에 실패했습니다: {str(e)}"
        )

@router.put("/{cover_letter_id}", response_model=BaseResponse)
async def update_cover_letter(
    cover_letter_id: str,
    update_data: CoverLetterUpdate,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 수정"""
    try:
        success = await cover_letter_service.update_cover_letter(cover_letter_id, update_data)
        if not success:
            return BaseResponse(
                success=False,
                message="자기소개서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="자기소개서가 성공적으로 수정되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자기소개서 수정에 실패했습니다: {str(e)}"
        )

@router.delete("/{cover_letter_id}", response_model=BaseResponse)
async def delete_cover_letter(
    cover_letter_id: str,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 삭제"""
    try:
        success = await cover_letter_service.delete_cover_letter(cover_letter_id)
        if not success:
            return BaseResponse(
                success=False,
                message="자기소개서를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="자기소개서가 성공적으로 삭제되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자기소개서 삭제에 실패했습니다: {str(e)}"
        )
