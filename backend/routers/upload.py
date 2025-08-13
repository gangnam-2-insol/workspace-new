from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import os
import tempfile
import asyncio
import aiofiles
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

router = APIRouter(prefix="/api/upload", tags=["upload"])

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
    total_score: int
    recommendation: str

class DetailedAnalysisResponse(BaseModel):
    resume_analysis: ResumeAnalysis
    cover_letter_analysis: CoverLetterAnalysis
    portfolio_analysis: PortfolioAnalysis
    overall_summary: OverallSummary

# 허용된 파일 타입
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain'
}

# 파일 크기 제한 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

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
    """파일에서 텍스트 추출"""
    try:
        if file_ext == '.txt':
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        elif file_ext == '.pdf':
            # PDF 텍스트 추출 (PyPDF2 또는 pdfplumber 사용)
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                # PyPDF2가 설치되지 않은 경우 기본 텍스트 반환
                return "PDF 파일입니다. 텍스트 추출을 위해 PyPDF2를 설치해주세요."
        elif file_ext in ['.doc', '.docx']:
            # Word 문서 텍스트 추출 (python-docx 사용)
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "Word 문서입니다. 텍스트 추출을 위해 python-docx를 설치해주세요."
        else:
            return "지원하지 않는 파일 형식입니다."
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"

async def generate_summary_with_gemini(content: str, summary_type: str = "general") -> SummaryResponse:
    """Gemini API를 사용하여 요약 생성"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다.")
    
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
        
        # Gemini API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        summary = response.text.strip()
        
        # 키워드 추출을 위한 추가 요청
        keyword_prompt = f"""
        다음 요약에서 핵심 키워드 5개를 추출해주세요:
        
        {summary}
        
        키워드는 쉼표로 구분하여 나열해주세요.
        """
        
        keyword_response = await asyncio.to_thread(
            model.generate_content,
            keyword_prompt
        )
        
        keywords = [kw.strip() for kw in keyword_response.text.split(',')]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SummaryResponse(
            summary=summary,
            keywords=keywords[:5],  # 최대 5개 키워드
            confidence_score=0.85,  # 기본 신뢰도 점수
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 실패: {str(e)}")

async def generate_detailed_analysis_with_gemini(content: str, document_type: str = "resume") -> DetailedAnalysisResponse:
    """Gemini API를 사용하여 상세 분석 생성"""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다.")
    
    start_time = datetime.now()
    
    try:
        # 문서 타입에 따른 맞춤형 프롬프트 생성
        if document_type == "resume":
            analysis_prompt = f"""
[ROLE] 채용담당자로서 이력서를 분석하고 점수화하세요.

[분석 기준] 0~10점 평가, 간단한 피드백 작성

[이력서 분석 항목]
1. basic_info_completeness (기본정보 완성도)
2. job_relevance (직무 적합성)
3. experience_clarity (경력 명확성)
4. tech_stack_clarity (기술스택 명확성)
5. project_recency (프로젝트 최신성)
6. achievement_metrics (성과 지표)
7. readability (가독성)
8. typos_and_errors (오탈자)
9. update_freshness (최신성)

[출력] JSON만:
{{
  "resume_analysis": {{
    "basic_info_completeness": {{"score": 0, "feedback": ""}},
    "job_relevance": {{"score": 0, "feedback": ""}},
    "experience_clarity": {{"score": 0, "feedback": ""}},
    "tech_stack_clarity": {{"score": 0, "feedback": ""}},
    "project_recency": {{"score": 0, "feedback": ""}},
    "achievement_metrics": {{"score": 0, "feedback": ""}},
    "readability": {{"score": 0, "feedback": ""}},
    "typos_and_errors": {{"score": 0, "feedback": ""}},
    "update_freshness": {{"score": 0, "feedback": ""}}
  }},
  "cover_letter_analysis": {{}},
  "portfolio_analysis": {{}},
  "overall_summary": {{"total_score": 0, "recommendation": ""}}
}}

[문서] {content}
"""
        elif document_type == "cover_letter":
            analysis_prompt = f"""
[ROLE] 당신은 채용담당자입니다. 입력된 자기소개서를 아래 기준에 따라 분석하고 점수화해야 합니다.

[분석 기준]
- 각 항목은 0~10점으로 평가 (10점 = 매우 우수, 0점 = 전혀 충족하지 않음)
- 각 항목별로 개선이 필요한 부분을 간단히 피드백으로 작성
- 점수와 피드백은 JSON 형식으로 출력

[자기소개서 분석 기준]
1. motivation_relevance (지원 동기 직무/회사와의 연결성)
2. problem_solving_STAR (STAR 기법 적용 여부)
3. quantitative_impact (정량적 성과 언급 여부)
4. job_understanding (직무 이해도)
5. unique_experience (차별화된 경험)
6. logical_flow (논리 구조)
7. keyword_diversity (전문 용어 다양성)
8. sentence_readability (문장 가독성)
9. typos_and_errors (오탈자 여부)

[출력 형식]
아래 JSON 스키마에 맞춰 출력:
{{
  "resume_analysis": {{}},
  "cover_letter_analysis": {{
    "motivation_relevance": {{"score": 0, "feedback": ""}},
    "problem_solving_STAR": {{"score": 0, "feedback": ""}},
    "quantitative_impact": {{"score": 0, "feedback": ""}},
    "job_understanding": {{"score": 0, "feedback": ""}},
    "unique_experience": {{"score": 0, "feedback": ""}},
    "logical_flow": {{"score": 0, "feedback": ""}},
    "keyword_diversity": {{"score": 0, "feedback": ""}},
    "sentence_readability": {{"score": 0, "feedback": ""}},
    "typos_and_errors": {{"score": 0, "feedback": ""}}
  }},
  "portfolio_analysis": {{}},
  "overall_summary": {{
    "total_score": 0,
    "recommendation": ""
  }}
}}

[입력 문서]
{content}

[요구사항]
- 점수는 반드시 0~10 정수
- feedback은 간단하고 구체적으로 작성
- JSON만 출력
"""
        elif document_type == "portfolio":
            analysis_prompt = f"""
[ROLE] 당신은 채용담당자입니다. 입력된 포트폴리오를 아래 기준에 따라 분석하고 점수화해야 합니다.

[분석 기준]
- 각 항목은 0~10점으로 평가 (10점 = 매우 우수, 0점 = 전혀 충족하지 않음)
- 각 항목별로 개선이 필요한 부분을 간단히 피드백으로 작성
- 점수와 피드백은 JSON 형식으로 출력

[포트폴리오 분석 기준]
1. project_overview (프로젝트 개요 명확성)
2. tech_stack (사용 기술 스택)
3. personal_contribution (개인 기여도 명확성)
4. achievement_metrics (정량적 성과 여부)
5. visual_quality (시각 자료 품질)
6. documentation_quality (문서화 수준)
7. job_relevance (직무 관련성)
8. unique_features (독창적 기능/아이디어)
9. maintainability (유지보수성)

[출력 형식]
아래 JSON 스키마에 맞춰 출력:
{{
  "resume_analysis": {{}},
  "cover_letter_analysis": {{}},
  "portfolio_analysis": {{
    "project_overview": {{"score": 0, "feedback": ""}},
    "tech_stack": {{"score": 0, "feedback": ""}},
    "personal_contribution": {{"score": 0, "feedback": ""}},
    "achievement_metrics": {{"score": 0, "feedback": ""}},
    "visual_quality": {{"score": 0, "feedback": ""}},
    "documentation_quality": {{"score": 0, "feedback": ""}},
    "job_relevance": {{"score": 0, "feedback": ""}},
    "unique_features": {{"score": 0, "feedback": ""}},
    "maintainability": {{"score": 0, "feedback": ""}}
  }},
  "overall_summary": {{
    "total_score": 0,
    "recommendation": ""
  }}
}}

[입력 문서]
{content}

[요구사항]
- 점수는 반드시 0~10 정수
- feedback은 간단하고 구체적으로 작성
- JSON만 출력
"""
        else:
            # 기본 프롬프트 (기존과 동일)
            analysis_prompt = f"""
[ROLE] 당신은 채용담당자입니다. 입력된 문서({document_type})를 아래 기준에 따라 분석하고 점수화해야 합니다.

[분석 기준]
- 각 항목은 0~10점으로 평가 (10점 = 매우 우수, 0점 = 전혀 충족하지 않음)
- 각 항목별로 개선이 필요한 부분을 간단히 피드백으로 작성
- 점수와 피드백은 JSON 형식으로 출력

[이력서 분석 기준]
1. basic_info_completeness (이름, 연락처, 이메일, GitHub/LinkedIn 여부)
2. job_relevance (직무 적합성)
3. experience_clarity (경력 설명 명확성)
4. tech_stack_clarity (기술 스택 명확성)
5. project_recency (프로젝트 최신성)
6. achievement_metrics (정량적 성과 지표 여부)
7. readability (가독성)
8. typos_and_errors (오탈자 여부)
9. update_freshness (최신 수정 여부)

[자기소개서 분석 기준]
1. motivation_relevance (지원 동기 직무/회사와의 연결성)
2. problem_solving_STAR (STAR 기법 적용 여부)
3. quantitative_impact (정량적 성과 언급 여부)
4. job_understanding (직무 이해도)
5. unique_experience (차별화된 경험)
6. logical_flow (논리 구조)
7. keyword_diversity (전문 용어 다양성)
8. sentence_readability (문장 가독성)
9. typos_and_errors (오탈자 여부)

[포트폴리오 분석 기준]
1. project_overview (프로젝트 개요 명확성)
2. tech_stack (사용 기술 스택)
3. personal_contribution (개인 기여도 명확성)
4. achievement_metrics (정량적 성과 여부)
5. visual_quality (시각 자료 품질)
6. documentation_quality (문서화 수준)
7. job_relevance (직무 관련성)
8. unique_features (독창적 기능/아이디어)
9. maintainability (유지보수성)

[출력 형식]
아래 JSON 스키마에 맞춰 출력:
{{
  "resume_analysis": {{
    "basic_info_completeness": {{"score": 0, "feedback": ""}},
    "job_relevance": {{"score": 0, "feedback": ""}},
    "experience_clarity": {{"score": 0, "feedback": ""}},
    "tech_stack_clarity": {{"score": 0, "feedback": ""}},
    "project_recency": {{"score": 0, "feedback": ""}},
    "achievement_metrics": {{"score": 0, "feedback": ""}},
    "readability": {{"score": 0, "feedback": ""}},
    "typos_and_errors": {{"score": 0, "feedback": ""}},
    "update_freshness": {{"score": 0, "feedback": ""}}
  }},
  "cover_letter_analysis": {{
    "motivation_relevance": {{"score": 0, "feedback": ""}},
    "problem_solving_STAR": {{"score": 0, "feedback": ""}},
    "quantitative_impact": {{"score": 0, "feedback": ""}},
    "job_understanding": {{"score": 0, "feedback": ""}},
    "unique_experience": {{"score": 0, "feedback": ""}},
    "logical_flow": {{"score": 0, "feedback": ""}},
    "keyword_diversity": {{"score": 0, "feedback": ""}},
    "sentence_readability": {{"score": 0, "feedback": ""}},
    "typos_and_errors": {{"score": 0, "feedback": ""}}
  }},
  "portfolio_analysis": {{
    "project_overview": {{"score": 0, "feedback": ""}},
    "tech_stack": {{"score": 0, "feedback": ""}},
    "personal_contribution": {{"score": 0, "feedback": ""}},
    "achievement_metrics": {{"score": 0, "feedback": ""}},
    "visual_quality": {{"score": 0, "feedback": ""}},
    "documentation_quality": {{"score": 0, "feedback": ""}},
    "job_relevance": {{"score": 0, "feedback": ""}},
    "unique_features": {{"score": 0, "feedback": ""}},
    "maintainability": {{"score": 0, "feedback": ""}}
  }},
  "overall_summary": {{
    "total_score": 0,
    "recommendation": ""
  }}
}}

[입력 문서]
{content}

[요구사항]
- 점수는 반드시 0~10 정수
- feedback은 간단하고 구체적으로 작성
- JSON만 출력
"""
        
        # Gemini API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            analysis_prompt
        )
        
        # 응답 검증
        if not response or not response.text or response.text.strip() == "":
            raise HTTPException(status_code=500, detail="Gemini API에서 빈 응답을 받았습니다.")
        
        response_text = response.text.strip()
        print(f"Gemini API 응답: {response_text[:200]}...")  # 디버깅용 로그
        
        # Markdown 코드 블록 제거 (정규식 사용으로 속도 향상)
        import re
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text, flags=re.MULTILINE)
        response_text = response_text.strip()
        print(f"정리된 응답: {response_text[:200]}...")  # 디버깅용 로그
        
        # JSON 파싱 (최적화)
        import json
        try:
            analysis_result = json.loads(response_text)
            
            # 응답 구조 검증 (빠른 검증)
            if not isinstance(analysis_result, dict):
                raise ValueError("응답이 딕셔너리 형식이 아닙니다.")
            
            # 문서 타입별로만 필요한 키 확인 (속도 향상)
            if document_type == "resume":
                if "resume_analysis" not in analysis_result:
                    raise ValueError("이력서 분석 결과가 응답에 없습니다.")
            elif document_type == "cover_letter":
                if "cover_letter_analysis" not in analysis_result:
                    raise ValueError("자기소개서 분석 결과가 응답에 없습니다.")
            elif document_type == "portfolio":
                if "portfolio_analysis" not in analysis_result:
                    raise ValueError("포트폴리오 분석 결과가 응답에 없습니다.")
            
            if "overall_summary" not in analysis_result:
                raise ValueError("전체 요약이 응답에 없습니다.")
            
            # 전체 점수 계산 (문서 타입별로만 계산하여 속도 향상)
            total_score = 0
            count = 0
            
            if document_type == "resume" and "resume_analysis" in analysis_result:
                for value in analysis_result["resume_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            elif document_type == "cover_letter" and "cover_letter_analysis" in analysis_result:
                for value in analysis_result["cover_letter_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            elif document_type == "portfolio" and "portfolio_analysis" in analysis_result:
                for value in analysis_result["portfolio_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            
            # 평균 점수 계산 (소수점 포함)
            if count > 0:
                average_score = round(total_score / count, 1)
            else:
                average_score = 0
            
            # 추천사항 생성
            if document_type == "resume":
                if average_score >= 8:
                    recommendation = "전반적으로 우수한 이력서입니다. 현재 상태를 유지하세요."
                elif average_score >= 6:
                    recommendation = "양호한 수준이지만 몇 가지 개선점이 있습니다. 피드백을 참고하여 수정하세요."
                else:
                    recommendation = "전반적인 개선이 필요합니다. 각 항목별 피드백을 참고하여 체계적으로 수정하세요."
            elif document_type == "cover_letter":
                if average_score >= 8:
                    recommendation = "매우 우수한 자기소개서입니다. 현재 상태를 유지하세요."
                elif average_score >= 6:
                    recommendation = "양호한 수준이지만 몇 가지 개선점이 있습니다. 피드백을 참고하여 수정하세요."
                else:
                    recommendation = "전반적인 개선이 필요합니다. 각 항목별 피드백을 참고하여 체계적으로 수정하세요."
            elif document_type == "portfolio":
                if average_score >= 8:
                    recommendation = "매우 우수한 포트폴리오입니다. 현재 상태를 유지하세요."
                elif average_score >= 6:
                    recommendation = "양호한 수준이지만 몇 가지 개선점이 있습니다. 피드백을 참고하여 수정하세요."
                else:
                    recommendation = "전반적인 개선이 필요합니다. 각 항목별 피드백을 참고하여 체계적으로 수정하세요."
            else:
                recommendation = "문서 분석이 완료되었습니다."
            
            analysis_result["overall_summary"]["total_score"] = average_score
            analysis_result["overall_summary"]["recommendation"] = recommendation
            
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"분석 처리 완료: {processing_time:.2f}초")
            
            return DetailedAnalysisResponse(**analysis_result)
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용: {response_text}")
            raise HTTPException(status_code=500, detail=f"분석 결과 파싱 실패: {str(e)}")
        except ValueError as e:
            print(f"응답 구조 오류: {e}")
            print(f"응답 내용: {response_text}")
            raise HTTPException(status_code=500, detail=f"분석 결과 구조 오류: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상세 분석 생성 실패: {str(e)}")

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
                detail="파일 크기가 너무 큽니다. 최대 10MB까지 업로드 가능합니다."
            )
        
        # 임시 파일로 저장
        file_ext = os.path.splitext(file.filename.lower())[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 파일에서 텍스트 추출
            extracted_text = await extract_text_from_file(temp_file_path, file_ext)
            
            if not extracted_text or extracted_text.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="파일에서 텍스트를 추출할 수 없습니다."
                )
            
            # Gemini API로 요약 생성
            summary_result = await generate_summary_with_gemini(extracted_text, summary_type)
            
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

@router.post("/analyze")
async def analyze_documents(
    file: UploadFile = File(...),
    document_type: str = Form("resume")  # resume, cover_letter, portfolio
):
    """파일 업로드 및 상세 분석"""
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
                detail="파일 크기가 너무 큽니다. 최대 10MB까지 업로드 가능합니다."
            )
        
        # 임시 파일로 저장
        file_ext = os.path.splitext(file.filename.lower())[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 파일에서 텍스트 추출
            extracted_text = await extract_text_from_file(temp_file_path, file_ext)
            
            if not extracted_text or extracted_text.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="파일에서 텍스트를 추출할 수 없습니다."
                )
            
            # Gemini API로 상세 분석 생성
            analysis_result = await generate_detailed_analysis_with_gemini(extracted_text, document_type)
            
            # 문서 타입에 따라 해당하는 분석 결과만 반환
            if document_type == "resume":
                return {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text_length": len(extracted_text),
                    "document_type": document_type,
                    "analysis_result": {
                        "resume_analysis": analysis_result.resume_analysis,
                        "overall_summary": analysis_result.overall_summary
                    }
                }
            elif document_type == "cover_letter":
                return {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text_length": len(extracted_text),
                    "document_type": document_type,
                    "analysis_result": {
                        "cover_letter_analysis": analysis_result.cover_letter_analysis,
                        "overall_summary": analysis_result.overall_summary
                    }
                }
            elif document_type == "portfolio":
                return {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text_length": len(extracted_text),
                    "document_type": document_type,
                    "analysis_result": {
                        "portfolio_analysis": analysis_result.portfolio_analysis,
                        "overall_summary": analysis_result.overall_summary
                    }
                }
            else:
                # 기본값: 전체 결과 반환
                return {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text_length": len(extracted_text),
                    "document_type": document_type,
                    "analysis_result": analysis_result.dict()
                }
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 분석 실패: {str(e)}")

@router.post("/summarize")
async def summarize_text(request: SummaryRequest):
    """텍스트 직접 요약"""
    try:
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="요약할 텍스트가 없습니다.")
        
        summary_result = await generate_summary_with_gemini(
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
        "gemini_api_configured": bool(GOOGLE_API_KEY),
        "supported_formats": list(ALLOWED_EXTENSIONS.keys()),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }
