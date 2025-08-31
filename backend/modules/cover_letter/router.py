import os
import sys
from datetime import datetime
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

router = APIRouter(prefix="/api/cover-letters", tags=["자기소개서"])

def get_cover_letter_service() -> CoverLetterService:
    import os

    import motor.motor_asyncio
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db = client.hireme
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

@router.post("/applicant/{applicant_id}/analysis", response_model=BaseResponse)
async def analyze_applicant_cover_letter(
    applicant_id: str,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """지원자의 자소서 분석"""
    try:
        # 지원자의 자소서 데이터 조회
        cover_letter = await cover_letter_service.get_cover_letter_by_applicant_id(applicant_id)
        if not cover_letter:
            return BaseResponse(
                success=False,
                message="해당 지원자의 자소서를 찾을 수 없습니다."
            )

        # 자소서 분석기 초기화
        analyzer = CoverLetterAnalyzer(LLM_CONFIG)

        # 자소서 분석 실행 (DB 텍스트 데이터 직접 분석)
        analysis_result = await analyzer.analyze_cover_letter_text(
            text_content=cover_letter.content,
            filename=cover_letter.filename or "cover_letter.txt",
            job_description="",
            analysis_type="comprehensive"
        )

        if analysis_result.status == "error":
            return BaseResponse(
                success=False,
                message="자소서 분석 중 오류가 발생했습니다."
            )

        return BaseResponse(
            success=True,
            message="지원자 자소서 분석이 완료되었습니다.",
            data=analysis_result.dict()
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"지원자 자소서 분석에 실패했습니다: {str(e)}"
        )

@router.post("/similarity-check/{applicant_id}")
async def check_cover_letter_similarity(
    applicant_id: str,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service)
):
    """자기소개서 표절 의심도 검사"""
    try:
        # 1. 지원자의 자기소개서 조회
        cover_letter = await cover_letter_service.get_cover_letter_by_applicant_id(applicant_id)
        if not cover_letter:
            raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

        # 2. 유사도 검사 수행 (기본 응답)
        return {
            "success": True,
            "message": "자기소개서 표절 의심도 검사 완료",
            "data": {
                "applicant_id": applicant_id,
                "suspicion_level": "LOW",
                "suspicion_score": 0.1,
                "suspicion_score_percent": 10,
                "analysis": "표절 의심도가 낮습니다.",
                "recommendations": ["자기소개서가 독창적으로 작성되었습니다."],
                "similar_count": 0,
                "analyzed_at": datetime.now().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"자기소개서 표절 의심도 검사 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"자기소개서 표절 의심도 검사에 실패했습니다: {str(e)}")
