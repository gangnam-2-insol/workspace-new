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

router = APIRouter(prefix="/api/cover-letters", tags=["자기소개서"])

def get_cover_letter_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> CoverLetterService:
    return CoverLetterService(db)

@router.post("/analyze", response_model=BaseResponse)
async def analyze_cover_letter(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(""),
    analysis_type: Optional[str] = Form("comprehensive")
):
    """자소서 분석 API (기존 데이터 반환)"""
    try:
        # 파일 유효성 검사
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            return BaseResponse(
                success=False,
                message="지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 업로드 가능합니다."
            )

        # 샘플 분석 데이터 반환 (AI 분석 대신)
        sample_analysis = {
            "technical_suitability": {
                "score": 75,
                "feedback": "기본적인 기술 역량을 보유하고 있습니다.",
                "details": {
                    "score": 75,
                    "strengths": ["기본 기술 스택", "프로젝트 경험"],
                    "weaknesses": ["고급 기술 부족"]
                }
            },
            "job_understanding": {
                "score": 80,
                "feedback": "직무에 대한 기본적인 이해가 있습니다.",
                "details": {
                    "score": 80,
                    "strengths": ["직무 이해", "기본 지식"],
                    "weaknesses": ["심화 지식 부족"]
                }
            },
            "growth_potential": {
                "score": 85,
                "feedback": "성장 가능성이 높아 보입니다.",
                "details": {
                    "score": 85,
                    "strengths": ["학습 의지", "적응력"],
                    "weaknesses": ["경험 부족"]
                }
            },
            "teamwork_communication": {
                "score": 70,
                "feedback": "기본적인 협업 능력을 보유하고 있습니다.",
                "details": {
                    "score": 70,
                    "strengths": ["팀워크", "소통"],
                    "weaknesses": ["리더십 부족"]
                }
            },
            "motivation_company_fit": {
                "score": 90,
                "feedback": "회사와의 적합성이 높습니다.",
                "details": {
                    "score": 90,
                    "strengths": ["동기", "가치관"],
                    "weaknesses": ["구체적 계획 부족"]
                }
            },
            "summary": "전반적으로 우수한 자소서입니다. 기술 역량과 성장 가능성을 보여주고 있습니다.",
            "recommendations": [
                "더 구체적인 프로젝트 경험을 추가하세요",
                "기술적 깊이를 보여주는 내용을 보강하세요"
            ],
            "overall_score": 80
        }

        return BaseResponse(
            success=True,
            message="자소서 분석이 완료되었습니다. (샘플 데이터)",
            data=sample_analysis
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
    """지원자의 자소서 분석 (기존 데이터 반환)"""
    try:
        # 지원자의 자소서 데이터 조회
        cover_letter = await cover_letter_service.get_cover_letter_by_applicant_id(applicant_id)
        if not cover_letter:
            return BaseResponse(
                success=False,
                message="해당 지원자의 자소서를 찾을 수 없습니다."
            )

        # 기존 분석 결과가 있는지 확인
        analysis_results = cover_letter.get("analysis_results", [])
        
        if not analysis_results:
            return BaseResponse(
                success=False,
                message="분석 데이터가 없습니다. 먼저 분석을 수행해주세요."
            )

        # 가장 최근 분석 결과 반환
        latest_analysis = analysis_results[-1]

        return BaseResponse(
            success=True,
            message="기존 자소서 분석 결과를 반환합니다.",
            data=latest_analysis
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"자소서 분석 결과 조회에 실패했습니다: {str(e)}"
        )
