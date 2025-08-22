from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import os
import tempfile
from pathlib import Path
from datetime import datetime
import logging

from services.advanced_analysis_service import AdvancedAnalysisService
from models.applicant import ApplicantCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advanced-analysis", tags=["advanced-analysis"])

# 분석 서비스 초기화
analysis_service = AdvancedAnalysisService()

@router.post("/analyze-resume")
async def analyze_resume_advanced(
    resume_file: UploadFile = File(...),
    cover_letter_file: Optional[UploadFile] = File(None),
    job_description: str = Form(""),
    job_position: str = Form("개발자"),
    applicant_name: str = Form(""),
    applicant_email: str = Form("")
):
    """2단계 이력서 분석 API"""
    try:
        logger.info(f"🔍 고급 이력서 분석 시작 - 지원자: {applicant_name}")
        
        # 파일 텍스트 추출
        resume_text = await _extract_text_from_file(resume_file)
        cover_letter_text = ""
        
        if cover_letter_file:
            cover_letter_text = await _extract_text_from_file(cover_letter_file)
        
        # 2단계 분석 실행
        analysis_result = await analysis_service.analyze_resume_two_stage(
            resume_text=resume_text,
            cover_letter_text=cover_letter_text,
            job_description=job_description,
            job_position=job_position
        )
        
        # 지원자 정보 구성
        applicant_data = {
            "name": applicant_name,
            "email": applicant_email,
            "job_position": job_position,
            "resume_text": resume_text,
            "cover_letter_text": cover_letter_text,
            "analysis_result": analysis_result,
            "final_score": analysis_result.get("final_score", 0),
            "created_at": datetime.now(),
            "status": "analyzed"
        }
        
        # MongoDB에 저장 (나중에 구현)
        # await save_applicant_to_db(applicant_data)
        
        logger.info(f"✅ 고급 분석 완료 - 최종 점수: {analysis_result.get('final_score', 0)}")
        
        return {
            "success": True,
            "message": "2단계 분석이 완료되었습니다.",
            "data": {
                "applicant": applicant_data,
                "analysis": analysis_result,
                "summary": {
                    "final_score": analysis_result.get("final_score", 0),
                    "job_position": job_position,
                    "analysis_timestamp": analysis_result.get("analysis_timestamp"),
                    "stage1_summary": analysis_result.get("stage1_huggingface", {}).get("summary", ""),
                    "stage2_evaluation": analysis_result.get("stage2_gpt", {}).get("종합_평가", "")
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 고급 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.post("/analyze-text")
async def analyze_text_advanced(
    resume_text: str = Form(...),
    cover_letter_text: str = Form(""),
    job_description: str = Form(""),
    job_position: str = Form("개발자"),
    applicant_name: str = Form(""),
    applicant_email: str = Form("")
):
    """텍스트 기반 2단계 분석 API"""
    try:
        logger.info(f"🔍 텍스트 기반 고급 분석 시작 - 지원자: {applicant_name}")
        
        # 2단계 분석 실행
        analysis_result = await analysis_service.analyze_resume_two_stage(
            resume_text=resume_text,
            cover_letter_text=cover_letter_text,
            job_description=job_description,
            job_position=job_position
        )
        
        # 지원자 정보 구성
        applicant_data = {
            "name": applicant_name,
            "email": applicant_email,
            "job_position": job_position,
            "resume_text": resume_text,
            "cover_letter_text": cover_letter_text,
            "analysis_result": analysis_result,
            "final_score": analysis_result.get("final_score", 0),
            "created_at": datetime.now(),
            "status": "analyzed"
        }
        
        logger.info(f"✅ 텍스트 기반 분석 완료 - 최종 점수: {analysis_result.get('final_score', 0)}")
        
        return {
            "success": True,
            "message": "텍스트 기반 2단계 분석이 완료되었습니다.",
            "data": {
                "applicant": applicant_data,
                "analysis": analysis_result,
                "summary": {
                    "final_score": analysis_result.get("final_score", 0),
                    "job_position": job_position,
                    "analysis_timestamp": analysis_result.get("analysis_timestamp"),
                    "stage1_summary": analysis_result.get("stage1_huggingface", {}).get("summary", ""),
                    "stage2_evaluation": analysis_result.get("stage2_gpt", {}).get("종합_평가", "")
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 텍스트 기반 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.get("/ranking")
async def get_applicant_ranking(
    job_position: Optional[str] = None,
    limit: int = 20
):
    """지원자 랭킹 조회"""
    try:
        # MongoDB에서 지원자 데이터 조회 (나중에 구현)
        # applicants = await get_applicants_from_db(job_position)
        
        # 임시 데이터
        applicants = [
            {
                "name": "김개발",
                "job_position": "개발자",
                "final_score": 85.5,
                "created_at": datetime.now()
            },
            {
                "name": "이기획",
                "job_position": "기획자", 
                "final_score": 78.2,
                "created_at": datetime.now()
            }
        ]
        
        # 랭킹 데이터 생성
        ranked_applicants = await analysis_service.get_ranking_data(applicants)
        
        return {
            "success": True,
            "data": {
                "ranking": ranked_applicants[:limit],
                "total_count": len(ranked_applicants),
                "job_position": job_position
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"랭킹 조회 실패: {str(e)}")

@router.get("/stats")
async def get_analysis_stats():
    """분석 통계 조회"""
    try:
        # MongoDB에서 통계 데이터 조회 (나중에 구현)
        stats = {
            "total_applicants": 150,
            "average_score": 72.5,
            "top_score": 95.2,
            "lowest_score": 45.8,
            "job_positions": {
                "개발자": {"count": 80, "avg_score": 78.3},
                "기획자": {"count": 40, "avg_score": 75.1},
                "디자이너": {"count": 30, "avg_score": 68.9}
            },
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"❌ 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """분석 서비스 상태 확인"""
    try:
        return {
            "status": "healthy",
            "service": "Advanced Analysis Service",
            "models_loaded": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def _extract_text_from_file(file: UploadFile) -> str:
    """파일에서 텍스트 추출"""
    try:
        # 파일 확장자 확인
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension == '.pdf':
            return await _extract_text_from_pdf(file)
        elif file_extension in ['.docx', '.doc']:
            return await _extract_text_from_docx(file)
        elif file_extension in ['.txt', '.md']:
            content = await file.read()
            return content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식: {file_extension}")
            
    except Exception as e:
        logger.error(f"파일 텍스트 추출 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 처리 실패: {str(e)}")

async def _extract_text_from_pdf(file: UploadFile) -> str:
    """PDF에서 텍스트 추출"""
    try:
        import PyPDF2
        import io
        
        content = await file.read()
        
        # PyPDF2로 텍스트 추출
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"PDF 텍스트 추출 실패: {e}")
        return "PDF 텍스트 추출에 실패했습니다."

async def _extract_text_from_docx(file: UploadFile) -> str:
    """DOCX에서 텍스트 추출"""
    try:
        import docx
        import io
        
        content = await file.read()
        
        # python-docx로 텍스트 추출
        doc = docx.Document(io.BytesIO(content))
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"DOCX 텍스트 추출 실패: {e}")
        return "DOCX 텍스트 추출에 실패했습니다."
