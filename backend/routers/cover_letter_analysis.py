"""
자소서 분석을 위한 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import sys
import traceback
from pydantic import BaseModel

# RAG 시스템 및 프롬프트 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.vector_store import CoverLetterRAGSystem
from prompts.cover_letter_analysis import (
    COVER_LETTER_ANALYSIS_PROMPT,
    COVER_LETTER_DETAILED_PROMPT,
    IMPROVEMENT_SUGGESTION_PROMPT
)

# 환경 변수 로드
load_dotenv()

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter-analysis"])

# RAG 시스템 초기화
rag_system = CoverLetterRAGSystem()
try:
    rag_system.initialize_rag_data()
    rag_system.build_vector_index()
    print("✅ RAG 시스템이 성공적으로 초기화되었습니다.")
except Exception as e:
    print(f"⚠️ RAG 시스템 초기화 실패: {e}")
    rag_system = None

class CoverLetterAnalysisRequest(BaseModel):
    content: str
    position: str
    department: str
    analysis_type: str = "basic"  # basic, detailed, improvement

class CoverLetterAnalysisResponse(BaseModel):
    success: bool
    analysis_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    rag_context: Optional[Dict[str, Any]] = None

@router.post("/analyze")
async def analyze_cover_letter(
    content: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    analysis_type: str = Form("basic")
) -> CoverLetterAnalysisResponse:
    """
    자소서 분석 API
    
    Args:
        content: 자소서 내용
        position: 지원 직무
        department: 지원 부서
        analysis_type: 분석 유형 (basic, detailed, improvement)
        
    Returns:
        분석 결과
    """
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini API가 설정되지 않았습니다.")
        
        if not rag_system:
            raise HTTPException(status_code=500, detail="RAG 시스템이 초기화되지 않았습니다.")
        
        # RAG 컨텍스트 검색
        rag_context = rag_system.search_relevant_context(content, position)
        
        # 분석 유형에 따른 프롬프트 선택
        if analysis_type == "detailed":
            prompt = COVER_LETTER_DETAILED_PROMPT.format(
                position=position,
                content=content,
                position_specific_criteria=rag_system.get_position_specific_criteria(position),
                department_culture_fit=rag_system.get_department_culture_fit(department),
                rag_context=json.dumps(rag_context, ensure_ascii=False, indent=2)
            )
        elif analysis_type == "improvement":
            # 기본 분석 먼저 수행
            basic_prompt = COVER_LETTER_ANALYSIS_PROMPT.format(
                position=position,
                department=department,
                content=content,
                rag_context=json.dumps(rag_context, ensure_ascii=False, indent=2)
            )
            
            basic_response = await model.generate_content(basic_prompt)
            basic_analysis = basic_response.text
            
            prompt = IMPROVEMENT_SUGGESTION_PROMPT.format(
                analysis_result=basic_analysis
            )
        else:  # basic
            prompt = COVER_LETTER_ANALYSIS_PROMPT.format(
                position=position,
                department=department,
                content=content,
                rag_context=json.dumps(rag_context, ensure_ascii=False, indent=2)
            )
        
        # Gemini API로 분석 수행
        response = await model.generate_content(prompt)
        analysis_text = response.text
        
        # JSON 응답 파싱 시도
        try:
            # JSON 부분 추출
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_content = analysis_text[json_start:json_end].strip()
                analysis_result = json.loads(json_content)
            else:
                # JSON 형식이 아닌 경우 텍스트로 반환
                analysis_result = {
                    "raw_analysis": analysis_text,
                    "parsing_error": "JSON 형식으로 파싱할 수 없습니다."
                }
        except json.JSONDecodeError as e:
            analysis_result = {
                "raw_analysis": analysis_text,
                "parsing_error": f"JSON 파싱 오류: {str(e)}"
            }
        
        return CoverLetterAnalysisResponse(
            success=True,
            analysis_result=analysis_result,
            rag_context=rag_context
        )
        
    except Exception as e:
        error_msg = f"자소서 분석 중 오류가 발생했습니다: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"상세 오류: {traceback.format_exc()}")
        
        return CoverLetterAnalysisResponse(
            success=False,
            error_message=error_msg
        )

@router.post("/analyze-file")
async def analyze_cover_letter_file(
    file: UploadFile = File(...),
    position: str = Form(...),
    department: str = Form(...),
    analysis_type: str = Form("basic")
) -> CoverLetterAnalysisResponse:
    """
    파일로부터 자소서 분석 API
    
    Args:
        file: 업로드된 자소서 파일
        position: 지원 직무
        department: 지원 부서
        analysis_type: 분석 유형
        
    Returns:
        분석 결과
    """
    try:
        # 파일 내용 읽기
        content = await file.read()
        
        # 파일 인코딩 처리
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('cp949')
            except UnicodeDecodeError:
                text_content = content.decode('latin-1')
        
        # 자소서 분석 수행
        return await analyze_cover_letter(
            content=text_content,
            position=position,
            department=department,
            analysis_type=analysis_type
        )
        
    except Exception as e:
        error_msg = f"파일 분석 중 오류가 발생했습니다: {str(e)}"
        print(f"❌ {error_msg}")
        
        return CoverLetterAnalysisResponse(
            success=False,
            error_message=error_msg
        )

@router.get("/positions")
async def get_available_positions():
    """사용 가능한 직무 목록 반환"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 시스템이 초기화되지 않았습니다.")
    
    positions = []
    for job_id, job_info in rag_system.job_descriptions.items():
        positions.append({
            "id": job_id,
            "title": job_info["title"],
            "required_skills": job_info["required_skills"],
            "preferred_skills": job_info["preferred_skills"]
        })
    
    return {"positions": positions}

@router.get("/company-values")
async def get_company_values():
    """회사 가치 및 문화 정보 반환"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 시스템이 초기화되지 않았습니다.")
    
    return {"company_values": rag_system.company_values}

@router.get("/evaluation-rubrics")
async def get_evaluation_rubrics():
    """평가 루브릭 정보 반환"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 시스템이 초기화되지 않았습니다.")
    
    return {"evaluation_rubrics": rag_system.evaluation_rubrics}

@router.post("/search-context")
async def search_rag_context(
    query: str = Form(...),
    position: str = Form(...),
    top_k: int = Form(5)
):
    """RAG 컨텍스트 검색"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG 시스템이 초기화되지 않았습니다.")
    
    try:
        context = rag_system.search_relevant_context(query, position, top_k)
        return {"success": True, "context": context}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "rag_system_initialized": rag_system is not None,
        "gemini_api_available": model is not None,
        "google_api_key_set": bool(GOOGLE_API_KEY)
    }

if __name__ == "__main__":
    print("자소서 분석 API가 생성되었습니다.")
