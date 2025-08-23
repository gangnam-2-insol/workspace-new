from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import tempfile
import asyncio
import aiofiles
from datetime import datetime
import sys
sys.path.append('..')  # 상위 디렉토리의 openai_service.py 사용
from openai_service import OpenAIService
from pydantic import BaseModel
import re

# .env 파일 로드 (현재 디렉토리에서)
load_dotenv('.env')

# OpenAI API 설정
try:
    openai_service = OpenAIService(model_name="gpt-4o")
    print("OpenAI 서비스 초기화 성공")
except Exception as e:
    print(f"OpenAI 서비스 초기화 실패: {e}")
    openai_service = None

router = APIRouter(tags=["upload"])

class SummaryRequest(BaseModel):
    content: str
    summary_type: str = "general"  # general, technical, experience

class SummaryResponse(BaseModel):
    summary: str
    keywords: list[str]
    confidence_score: float
    processing_time: float

# 새로운 상세 분석 모델들
class AnalysisScore(BaseModel):
    score: int  # 0-10
    feedback: str

class DocumentValidationRequest(BaseModel):
    content: str
    expected_type: str  # "이력서", "자기소개서", "포트폴리오"

class DocumentValidationResponse(BaseModel):
    is_valid: bool
    confidence: float
    reason: str
    suggested_type: str

class ResumeAnalysis(BaseModel):
    basic_info_completeness: AnalysisScore
    job_relevance: AnalysisScore
    experience_clarity: AnalysisScore
    tech_stack_clarity: AnalysisScore
    project_recency: AnalysisScore
    achievement_metrics: AnalysisScore
    readability: AnalysisScore
    typos_and_errors: AnalysisScore
    update_freshness: AnalysisScore

class CoverLetterAnalysis(BaseModel):
    motivation_relevance: AnalysisScore
    problem_solving_STAR: AnalysisScore
    quantitative_impact: AnalysisScore
    job_understanding: AnalysisScore
    unique_experience: AnalysisScore
    logical_flow: AnalysisScore
    keyword_diversity: AnalysisScore
    sentence_readability: AnalysisScore
    typos_and_errors: AnalysisScore

class PortfolioAnalysis(BaseModel):
    project_overview: AnalysisScore
    tech_stack: AnalysisScore
    personal_contribution: AnalysisScore
    achievement_metrics: AnalysisScore
    visual_quality: AnalysisScore
    documentation_quality: AnalysisScore
    job_relevance: AnalysisScore
    unique_features: AnalysisScore
    maintainability: AnalysisScore

class OverallSummary(BaseModel):
    total_score: float
    recommendation: str

class DetailedAnalysisResponse(BaseModel):
    resume_analysis: Optional[ResumeAnalysis] = None
    cover_letter_analysis: Optional[CoverLetterAnalysis] = None
    portfolio_analysis: Optional[PortfolioAnalysis] = None
    overall_summary: OverallSummary

# ===== 분석 실패 시 기본 구조 생성 유틸 =====
def _build_score(msg: str) -> Dict[str, object]:
    return {"score": 0, "feedback": msg}

def build_fallback_analysis(document_type: str) -> Dict[str, object]:
    reason = "문서에서 텍스트를 추출할 수 없어 평가하지 못했습니다. 편집 가능한 PDF/DOCX로 재업로드해주세요."
    resume = {
        "basic_info_completeness": _build_score(reason),
        "job_relevance": _build_score(reason),
        "experience_clarity": _build_score(reason),
        "tech_stack_clarity": _build_score(reason),
        "project_recency": _build_score(reason),
        "achievement_metrics": _build_score(reason),
        "readability": _build_score(reason),
        "typos_and_errors": _build_score(reason),
        "update_freshness": _build_score(reason),
    }
    cover = {
        "motivation_relevance": _build_score(reason),
        "problem_solving_STAR": _build_score(reason),
        "quantitative_impact": _build_score(reason),
        "job_understanding": _build_score(reason),
        "unique_experience": _build_score(reason),
        "logical_flow": _build_score(reason),
        "keyword_diversity": _build_score(reason),
        "sentence_readability": _build_score(reason),
        "typos_and_errors": _build_score(reason),
    }
    portfolio = {
        "project_overview": _build_score(reason),
        "tech_stack": _build_score(reason),
        "personal_contribution": _build_score(reason),
        "achievement_metrics": _build_score(reason),
        "visual_quality": _build_score(reason),
        "documentation_quality": _build_score(reason),
        "job_relevance": _build_score(reason),
        "unique_features": _build_score(reason),
        "maintainability": _build_score(reason),
    }
    return {
        "resume_analysis": resume,
        "cover_letter_analysis": cover,
        "portfolio_analysis": portfolio,
        "overall_summary": {"total_score": 0, "recommendation": reason},
    }

# ===== 내용 기반 문서 유형 분류기 =====
def classify_document_type_by_content(text: str) -> Dict[str, object]:
    """간단한 규칙 기반으로 문서 유형(resume/cover_letter/portfolio)을 분류합니다."""
    text_lower = text.lower()

    # 한국어/영어 키워드 세트
    resume_keywords = [
        "경력", "이력", "프로젝트", "학력", "기술", "스킬", "자격증", "근무", "담당", "성과",
        "경험", "요약", "핵심역량", "phone", "email", "github", "linkedin",
        "experience", "education", "skills", "projects", "certificate"
    ]
    cover_letter_keywords = [
        "지원동기", "성장배경", "입사", "포부", "저는", "배우며", "하고자", "기여", "관심",
        "동기", "열정", "왜", "왜 우리", "motiv", "cover letter", "passion"
    ]
    portfolio_keywords = [
        "포트폴리오", "작품", "시연", "데모", "링크", "이미지", "스샷", "캡처", "레포지토리",
        "repository", "demo", "screenshot", "figma", "behance", "dribbble"
    ]

    def score_keywords(keywords: List[str]) -> float:
        score = 0.0
        for kw in keywords:
            # 단어 경계 우선, 없으면 포함 검사
            if re.search(rf"\b{re.escape(kw)}\b", text_lower) or kw in text_lower:
                score += 1.0
        # 섹션 헤더 보너스
        section_headers = ["경력", "학력", "프로젝트", "skills", "experience", "education"]
        if any(h in text for h in section_headers):
            score += 0.5
        # 연락처 패턴 보너스 (이력서 지표)
        if re.search(r"[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}", text) or re.search(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", text_lower):
            score += 0.7
        return score

    resume_score = score_keywords(resume_keywords)
    cover_letter_score = sum(1.0 for kw in cover_letter_keywords if kw in text_lower)
    portfolio_score = sum(1.0 for kw in portfolio_keywords if kw in text_lower)

    scores = {
        "resume": resume_score,
        "cover_letter": cover_letter_score,
        "portfolio": portfolio_score,
    }

    detected_type = max(scores.items(), key=lambda x: x[1])[0]
    max_score = scores[detected_type]
    # 간단한 신뢰도 정규화 (최대 10점 가정)
    confidence = min(round(max_score / 10.0, 2), 1.0)

    return {"detected_type": detected_type, "confidence": confidence, "scores": scores}

# 허용된 파일 타입
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain'
}

# 파일 크기 제한 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

def validate_file(file: UploadFile) -> bool:
    """파일 유효성 검사"""
    if not file.filename:
        return False
    
    # 파일 확장자 확인
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

async def extract_text_from_file(file_path: str, file_ext: str) -> str:
    """파일에서 텍스트 추출 (다중 백업 전략)"""
    try:
        if file_ext == '.txt':
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        elif file_ext == '.pdf':
            # 1차: PyPDF2
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        extracted = page.extract_text() or ""
                        text += extracted + ("\n" if extracted else "")
                if text.strip():
                    return text
            except Exception:
                pass
            # 2차: pdfplumber
            try:
                import pdfplumber  # type: ignore
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for p in pdf.pages:
                        extracted = p.extract_text() or ""
                        text += extracted + ("\n" if extracted else "")
                if text.strip():
                    return text
            except Exception:
                pass
            # 실패 시 빈 문자열 반환
            return ""
        elif file_ext in ['.doc', '.docx']:
            # 1차: python-docx
            try:
                from docx import Document  # type: ignore
                doc = Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs if p.text])
                if text.strip():
                    return text
            except Exception:
                pass
            # 2차: docx2txt
            try:
                import docx2txt  # type: ignore
                text = docx2txt.process(file_path) or ""
                return text
            except Exception:
                pass
            return ""
        else:
            return ""
    except Exception as e:
        return ""

async def generate_summary_with_openai(content: str, summary_type: str = "general") -> SummaryResponse:
    """OpenAI API를 사용하여 요약 생성"""
    if not openai_service:
        raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다.")
    
    start_time = datetime.now()
    
    try:
        # 요약 타입에 따른 프롬프트 설정
        prompts = {
            "general": f"""
            다음 이력서/자기소개서 내용을 간결하게 요약해주세요:
            
            {content}
            
            요약 시 다음 사항을 포함해주세요:
            1. 주요 경력 및 경험
            2. 핵심 기술 스택
            3. 주요 성과나 프로젝트
            4. 지원 직무와의 연관성
            
            요약은 200자 이내로 작성해주세요.
            """,
            "technical": f"""
            다음 내용에서 기술적 역량을 중심으로 요약해주세요:
            
            {content}
            
            다음 항목들을 포함해주세요:
            1. 프로그래밍 언어 및 프레임워크
            2. 개발 도구 및 플랫폼
            3. 프로젝트 경험
            4. 기술적 성과
            
            요약은 150자 이내로 작성해주세요.
            """,
            "experience": f"""
            다음 내용에서 경력과 경험을 중심으로 요약해주세요:
            
            {content}
            
            다음 항목들을 포함해주세요:
            1. 총 경력 기간
            2. 주요 회사 및 직무
            3. 핵심 프로젝트 경험
            4. 주요 성과 및 업적
            
            요약은 150자 이내로 작성해주세요.
            """
        }
        
        prompt = prompts.get(summary_type, prompts["general"])
        
        # OpenAI API 호출
        summary = await openai_service.generate_response(prompt)
        
        # 키워드 추출을 위한 추가 요청
        keyword_prompt = f"""
        다음 요약에서 핵심 키워드 5개를 추출해주세요:
        
        {summary}
        
        키워드는 쉼표로 구분하여 나열해주세요.
        """
        
        keyword_response = await openai_service.generate_response(keyword_prompt)
        
        keywords = [kw.strip() for kw in keyword_response.split(',')]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SummaryResponse(
            summary=summary,
            keywords=keywords[:5],  # 최대 5개 키워드
            confidence_score=0.85,  # 기본 신뢰도 점수
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 실패: {str(e)}")

@router.post("/file")
async def upload_and_summarize_file(
    file: UploadFile = File(...),
    summary_type: str = Form("general")
):
    """파일 업로드 및 요약"""
    try:
        # 파일 유효성 검사
        if not validate_file(file):
            raise HTTPException(
                status_code=400, 
                detail="지원하지 않는 파일 형식입니다. PDF, DOC, DOCX, TXT 파일만 업로드 가능합니다."
            )
        
        # 파일 크기 확인
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="파일 크기가 너무 큽니다. 최대 50MB까지 업로드 가능합니다."
            )
        
        # 임시 파일로 저장
        file_ext = os.path.splitext(file.filename.lower())[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 파일에서 텍스트 추출
            extracted_text = await extract_text_from_file(temp_file_path, file_ext)
            
            # 텍스트 추출 실패 시에도 더미 분석으로 계속 진행 (사용자 경험 개선)
            if not extracted_text or str(extracted_text).strip() == "":
                print("⚠️ 텍스트 추출 실패: 빈 내용 감지 → 더미 분석으로 계속 진행합니다.")
                extracted_text = "[EMPTY_CONTENT] 텍스트 추출 실패 (스캔 PDF/이미지 기반 문서일 수 있습니다.)"
            
            # OpenAI API로 요약 생성
            summary_result = await generate_summary_with_openai(extracted_text, summary_type)
            
            return {
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text_length": len(extracted_text),
                "summary": summary_result.summary,
                "keywords": summary_result.keywords,
                "confidence_score": summary_result.confidence_score,
                "processing_time": summary_result.processing_time,
                "summary_type": summary_type
            }
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 실패: {str(e)}")

@router.post("/summarize")
async def summarize_text(request: SummaryRequest):
    """텍스트 직접 요약"""
    try:
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="요약할 텍스트가 없습니다.")
        
        summary_result = await generate_summary_with_openai(
            request.content, 
            request.summary_type
        )
        
        return summary_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 실패: {str(e)}")

@router.get("/health")
async def upload_health_check():
    """업로드 서비스 헬스 체크"""
    return {
        "status": "healthy",
        "openai_api_configured": bool(openai_service),
        "supported_formats": list(ALLOWED_EXTENSIONS.keys()),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }