from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import json
from pydantic import BaseModel

from services.cover_letter_analysis_service import CoverLetterAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cover-letter-analysis", tags=["자소서 분석"])

# 자소서 분석 서비스 초기화
cover_letter_service = CoverLetterAnalysisService()

class CoverLetterAnalysisRequest(BaseModel):
    """자소서 분석 요청 모델"""
    cover_letter_text: str
    job_description: Optional[str] = ""
    job_position: Optional[str] = "개발자"

class CoverLetterAnalysisResponse(BaseModel):
    """자소서 분석 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/analyze", response_model=CoverLetterAnalysisResponse)
async def analyze_cover_letter(request: CoverLetterAnalysisRequest):
    """자소서 분석 실행"""
    try:
        logger.info("🔍 자소서 분석 요청 받음")
        
        if not request.cover_letter_text.strip():
            raise HTTPException(status_code=400, detail="자소서 내용이 비어있습니다.")
        
        # 자소서 분석 실행
        analysis_result = await cover_letter_service.analyze_cover_letter(
            cover_letter_text=request.cover_letter_text,
            job_description=request.job_description
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # 평가 요약 생성
        evaluation_summary = cover_letter_service.get_evaluation_summary(
            analysis_result["cover_letter_analysis"]
        )
        
        # 응답 데이터 구성
        response_data = {
            "analysis_result": analysis_result,
            "evaluation_summary": evaluation_summary,
            "job_position": request.job_position,
            "analysis_timestamp": analysis_result["analysis_timestamp"]
        }
        
        logger.info(f"✅ 자소서 분석 완료 - 종합 점수: {analysis_result['overall_score']:.1f}/10점")
        
        return CoverLetterAnalysisResponse(
            success=True,
            message="자소서 분석이 완료되었습니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 자소서 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"자소서 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/analyze-file", response_model=CoverLetterAnalysisResponse)
async def analyze_cover_letter_file(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(""),
    job_position: Optional[str] = Form("개발자")
):
    """파일 업로드를 통한 자소서 분석"""
    try:
        logger.info(f"📁 자소서 파일 분석 요청: {file.filename}")
        
        # 파일 타입 검증
        if not file.filename.lower().endswith(('.txt', '.docx', '.pdf')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. (.txt, .docx, .pdf만 지원)")
        
        # 파일 내용 읽기
        content = await file.read()
        
        # 텍스트 추출 (간단한 구현)
        if file.filename.lower().endswith('.txt'):
            cover_letter_text = content.decode('utf-8')
        else:
            # PDF나 DOCX의 경우 간단한 텍스트 추출
            try:
                cover_letter_text = content.decode('utf-8')
            except UnicodeDecodeError:
                cover_letter_text = content.decode('utf-8', errors='ignore')
        
        if not cover_letter_text.strip():
            raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")
        
        # 자소서 분석 실행
        analysis_result = await cover_letter_service.analyze_cover_letter(
            cover_letter_text=cover_letter_text,
            job_description=job_description
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # 평가 요약 생성
        evaluation_summary = cover_letter_service.get_evaluation_summary(
            analysis_result["cover_letter_analysis"]
        )
        
        # 응답 데이터 구성
        response_data = {
            "analysis_result": analysis_result,
            "evaluation_summary": evaluation_summary,
            "job_position": job_position,
            "filename": file.filename,
            "analysis_timestamp": analysis_result["analysis_timestamp"]
        }
        
        logger.info(f"✅ 파일 자소서 분석 완료 - 종합 점수: {analysis_result['overall_score']:.1f}/10점")
        
        return CoverLetterAnalysisResponse(
            success=True,
            message="파일 자소서 분석이 완료되었습니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 파일 자소서 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 자소서 분석 중 오류가 발생했습니다: {str(e)}")

@router.get("/evaluation-items")
async def get_evaluation_items():
    """평가 항목 목록 조회"""
    try:
        return {
            "success": True,
            "evaluation_items": cover_letter_service.evaluation_items,
            "total_items": len(cover_letter_service.evaluation_items)
        }
    except Exception as e:
        logger.error(f"평가 항목 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="평가 항목 조회 중 오류가 발생했습니다.")

@router.get("/sample-analysis")
async def get_sample_analysis():
    """샘플 분석 결과 조회 (테스트용)"""
    try:
        # 샘플 자소서 텍스트
        sample_text = """
안녕하세요. 저는 3년간의 웹 개발 경험을 가진 개발자입니다.
React와 Node.js를 주로 사용하여 사용자 친화적인 웹 애플리케이션을 개발해왔습니다.
최근에는 마이크로서비스 아키텍처를 도입하여 시스템 성능을 30% 향상시킨 경험이 있습니다.
팀 프로젝트에서 프론트엔드 리드 역할을 맡아 5명의 개발자와 협업하여 프로젝트를 성공적으로 완료했습니다.
새로운 기술에 대한 학습 의지가 강하며, 현재는 TypeScript와 Docker를 학습하고 있습니다.
        """
        
        # 샘플 분석 실행
        analysis_result = await cover_letter_service.analyze_cover_letter(
            cover_letter_text=sample_text,
            job_description="웹 개발자 채용 - React, Node.js 경험자 우대"
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # 평가 요약 생성
        evaluation_summary = cover_letter_service.get_evaluation_summary(
            analysis_result["cover_letter_analysis"]
        )
        
        return {
            "success": True,
            "message": "샘플 자소서 분석 결과입니다.",
            "data": {
                "analysis_result": analysis_result,
                "evaluation_summary": evaluation_summary,
                "sample_text": sample_text
            }
        }
        
    except Exception as e:
        logger.error(f"샘플 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"샘플 분석 중 오류가 발생했습니다: {str(e)}")

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "Cover Letter Analysis Service",
        "timestamp": "2024-01-01T00:00:00Z"
    }


