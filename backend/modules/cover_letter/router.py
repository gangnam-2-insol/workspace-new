import os
import sys
from typing import List, Optional

import motor.motor_asyncio
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from modules.shared.models import BaseResponse

from .models import CoverLetter, CoverLetterCreate, CoverLetterUpdate
from .services import CoverLetterService

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio

from modules.core.services.cover_letter_analysis.analyzer import CoverLetterAnalyzer
from modules.core.services.llm_providers.openai_provider import OpenAIProvider

router = APIRouter(prefix="/api/cover-letter", tags=["자기소개서"])

def get_cover_letter_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> CoverLetterService:
    return CoverLetterService(db)

# LLM 설정 (실제 환경에서는 환경변수에서 가져와야 함)
LLM_CONFIG = {
    "provider": "openai",
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "model_name": "gpt-4o-mini",
    "max_tokens": 4000,
    "temperature": 0.3
}

@router.post("/analyze", response_model=BaseResponse)
async def analyze_cover_letter(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(""),
    analysis_type: Optional[str] = Form("comprehensive")
):
    """자소서 분석 API"""
    try:
        # 파일 유효성 검사
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            return BaseResponse(
                success=False,
                message="지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 업로드 가능합니다."
            )

        # 파일 내용 읽기
        file_content = await file.read()

        # 자소서 분석기 초기화
        analyzer = CoverLetterAnalyzer(LLM_CONFIG)

        # 자소서 분석 실행
        analysis_result = await analyzer.analyze_cover_letter(
            file_bytes=file_content,
            filename=file.filename,
            job_description=job_description,
            analysis_type=analysis_type
        )

        if analysis_result.status == "error":
            return BaseResponse(
                success=False,
                message="자소서 분석 중 오류가 발생했습니다."
            )

        return BaseResponse(
            success=True,
            message="자소서 분석이 완료되었습니다.",
            data=analysis_result.dict()
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자소서 분석에 실패했습니다: {str(e)}"
        )

@router.post("/analyze-existing", response_model=BaseResponse)
async def analyze_existing_cover_letter(
    cover_letter_id: str = Form(...),
    job_description: Optional[str] = Form(""),
    analysis_type: Optional[str] = Form("comprehensive")
):
    """기존 자소서 분석 API"""
    try:
        # 자소서 서비스에서 자소서 데이터 가져오기
        cover_letter_service = get_cover_letter_service()
        cover_letter = await cover_letter_service.get_cover_letter(cover_letter_id)
        
        if not cover_letter:
            return BaseResponse(
                success=False,
                message="자소서를 찾을 수 없습니다."
            )

        # 자소서 분석기 초기화
        analyzer = CoverLetterAnalyzer(LLM_CONFIG)

        # 자소서 내용을 바이트로 변환 (텍스트 기반)
        content_text = cover_letter.content or cover_letter.extracted_text or ""
        file_bytes = content_text.encode('utf-8')

        # 자소서 분석 실행
        analysis_result = await analyzer.analyze_cover_letter(
            file_bytes=file_bytes,
            filename=f"cover_letter_{cover_letter_id}.txt",
            job_description=job_description,
            analysis_type=analysis_type
        )

        if analysis_result.status == "error":
            return BaseResponse(
                success=False,
                message="자소서 분석 중 오류가 발생했습니다."
            )

        return BaseResponse(
            success=True,
            message="자소서 분석이 완료되었습니다.",
            data=analysis_result.dict()
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자소서 분석에 실패했습니다: {str(e)}"
        )

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
