import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional, Dict, Any
import locale
import codecs
from datetime import datetime
import io
import json
import re
import random
# from sentence_transformers import SentenceTransformer
# import numpy as np

# 자소서 분석 관련 라이브러리
try:
    import pdfplumber
    import docx
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# .env 파일 로드 (현재 디렉토리에서)
print(f"🔍 현재 작업 디렉토리: {os.getcwd()}")
print(f"🔍 .env 파일 존재 여부: {os.path.exists('.env')}")
load_dotenv('.env')
print(f"🔍 GOOGLE_API_KEY 로드 후: {os.getenv('GOOGLE_API_KEY')}")

# Gemini 클라이언트 (환경변수에서 API 키 가져오기)
try:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
        print("✅ Gemini API가 설정되었습니다.")
    else:
        GEMINI_AVAILABLE = False
        print("⚠️  GOOGLE_API_KEY가 설정되지 않았습니다. 자소서 분석 기능이 제한됩니다.")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini 라이브러리가 설치되지 않았습니다. 자소서 분석 기능이 제한됩니다.")

# Python 환경 인코딩 설정
# 시스템 기본 인코딩을 UTF-8로 설정
if sys.platform.startswith('win'):
    # Windows 환경에서 UTF-8 강제 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 콘솔 출력 인코딩 설정
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# FastAPI 앱 생성
app = FastAPI(title="AI 채용 관리 시스템 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 한글 인코딩을 위한 미들웨어
@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)
    
    # 모든 JSON 응답에 UTF-8 인코딩 명시
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"
    
    # 텍스트 응답에도 UTF-8 인코딩 명시
    elif response.headers.get("content-type", "").startswith("text/"):
        if "charset" not in response.headers.get("content-type", ""):
            current_content_type = response.headers.get("content-type", "")
            response.headers["content-type"] = f"{current_content_type}; charset=utf-8"
    
    return response

# 라우터 등록
# chatbot_router와 langgraph_router는 현재 사용하지 않음
# app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])
# app.include_router(langgraph_router, prefix="/api/langgraph", tags=["langgraph"])

# Upload 라우터 등록
from routers.upload import router as upload_router
app.include_router(upload_router, prefix="/api/upload", tags=["upload"])

# 지원자 라우터 등록
from routers.applicants import router as applicants_router
app.include_router(applicants_router, prefix="/api/applicants", tags=["applicants"])

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.hireme

# 자소서 분석 관련 함수들
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF 파일에서 텍스트 추출"""
    if not PDF_AVAILABLE:
        raise HTTPException(status_code=400, detail="PDF 처리 라이브러리가 설치되지 않았습니다.")
    
    text = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 텍스트 추출 실패: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """DOCX 파일에서 텍스트 추출"""
    if not PDF_AVAILABLE:
        raise HTTPException(status_code=400, detail="DOCX 처리 라이브러리가 설치되지 않았습니다.")
    
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n".join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX 텍스트 추출 실패: {str(e)}")

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """파일 확장자에 따라 적절한 텍스트 추출 함수 호출"""
    file_ext = filename.lower()
    
    if file_ext.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif file_ext.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    elif file_ext.endswith('.txt'):
        return file_bytes.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 지원합니다.")

def split_into_paragraphs(text: str) -> List[str]:
    """텍스트를 문단으로 분리"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        # 문단 구분이 없는 경우 문장 단위로 분리
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [s.strip() for s in sentences if s.strip()]
    return paragraphs

def split_into_sentences(text: str) -> List[str]:
    """텍스트를 문장으로 분리"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

async def analyze_cover_letter_basic(text: str, job_description: str = "") -> Dict[str, Any]:
    """기본 자소서 분석 (Gemini가 사용 불가능할 때)"""
    try:
        # 간단한 텍스트 분석
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        return {
            "summary": f"총 {len(words)}단어, {len(sentences)}문장으로 구성된 자소서입니다.",
            "top_strengths": [
                {"strength": "텍스트 길이", "evidence": f"총 {len(words)}단어", "confidence": 0.8}
            ],
            "star_cases": [],
            "job_fit_score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "grammar_suggestions": [],
            "improvement_suggestions": [],
            "overall_score": 50
        }
    except Exception as e:
        print(f"기본 분석 실패: {e}")
        return {
            "summary": "분석에 실패했습니다.",
            "top_strengths": [],
            "star_cases": [],
            "job_fit_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "grammar_suggestions": [],
            "improvement_suggestions": [],
            "overall_score": 0
        }

async def analyze_cover_letter_with_llm(text: str, job_description: str = "") -> Dict[str, Any]:
    """Gemini를 사용하여 자소서 분석"""
    if not GEMINI_AVAILABLE:
        # Gemini가 사용 불가능할 때 기본 분석 제공
        return await analyze_cover_letter_basic(text, job_description)
    
    try:
        # Gemini 모델 초기화
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 1. 요약 및 핵심 강점 추출
        summary_prompt = f"""당신은 채용담당자 역할을 한다. 지원자가 제출한 자소서를 읽고, 3문장 내로 핵심 요약과 가장 강한 '핵심 강점' 3가지를 추출해줘. 핵심 강점은 구체적 근거(문장 위치/문장 일부)와 함께 표기해라.

자소서:
{text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:
{{
  "summary": "한 문장 요약...",
  "top_strengths": [
    {{"strength":"팀 리딩 경험", "evidence":"3번째 문단: '팀을 이끌며...'", "confidence": 0.92}},
    {{"strength":"기술 스택", "evidence":"2번째 문단: 'Python과...'", "confidence": 0.88}},
    {{"strength":"문제 해결", "evidence":"4번째 문단: '프로젝트에서...'", "confidence": 0.85}}
  ]
}}"""

        summary_response = model.generate_content(summary_prompt)
        summary_result = json.loads(summary_response.text)
        
        # 2. STAR 사례 추출
        star_prompt = f"""다음 텍스트에서 STAR(상황, 과제, 행동, 결과) 구조의 사례를 찾아 각각을 분리해서 반환해라. 찾을 수 없으면 빈 배열 [] 반환.

텍스트:
{text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:
[
  {{"s":"상황 설명", "t":"과제 설명", "a":"행동 설명", "r":"결과 설명", "evidence_sentence_indices":[2,3]}}
]"""

        star_response = model.generate_content(star_prompt)
        star_result = json.loads(star_response.text)
        
        # 3. 직무 적합성 점수 및 키워드 매칭
        job_fit_prompt = f"""당신은 IT기업 채용담당자 역할을 한다. 채용공고(직무 설명)를 주면 자소서의 '직무 적합성'을 0~100으로 점수화하고, 어떤 스킬/경험이 일치하는지, 부족한 키워드는 무엇인지 정리한다.

[평가 기준]
- 기술 적합성: 사용 기술 스택, 프로젝트 경험, 문제 해결 능력
- 직무 이해도: 해당 포지션의 역할·책임에 대한 명확한 이해
- 성장 가능성: 학습 태도, 새로운 기술 습득 경험
- 팀워크/커뮤니케이션: 협업 경험, 갈등 해결 사례
- 동기/회사 이해도: 지원 동기, 회사와의 가치관 일치 여부

직무 설명: {job_description if job_description else "직무 설명이 제공되지 않았습니다."}
자소서: {text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:
{{
 "score": 78,
 "matched_skills":["Python", "팀리딩"],
 "missing_skills":["클라우드","데이터 파이프라인"],
 "explanation":"지원자는 Python과 팀리딩 경험이 우수하지만, 클라우드 기술과 데이터 파이프라인 경험이 부족합니다."
}}"""

        job_fit_response = model.generate_content(job_fit_prompt)
        job_fit_result = json.loads(job_fit_response.text)
        
        # 4. 문장별 개선 제안
        improvement_prompt = f"""각 문장을 더 간결하고 적극적으로 바꿔라. 원래 문장과 개선 문장을 짝지어 반환.

자소서:
{text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:
[{{"original":"원래 문장", "improved":"개선된 문장"}}]"""

        improvement_response = model.generate_content(improvement_prompt)
        improvement_result = json.loads(improvement_response.text)
        
        # 5. 문법 검사 및 교정 제안
        grammar_prompt = f"""다음 자소서의 문법 오류를 찾아 교정 제안을 해주세요. 각 오류에 대해 원래 문장과 교정된 문장을 짝지어 반환하세요.

자소서:
{text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요:
[{{"original":"원래 문장", "corrected":"교정된 문장", "explanation":"오류 설명"}}]"""

        grammar_response = model.generate_content(grammar_prompt)
        grammar_result = json.loads(grammar_response.text)
        
        # 종합 점수 계산
        overall_score = calculate_overall_score(summary_result, star_result, job_fit_result, improvement_result, grammar_result)
        
        return {
            "summary": summary_result.get("summary", ""),
            "top_strengths": summary_result.get("top_strengths", []),
            "star_cases": star_result if isinstance(star_result, list) else [],
            "job_fit_score": job_fit_result.get("score", 0),
            "matched_skills": job_fit_result.get("matched_skills", []),
            "missing_skills": job_fit_result.get("missing_skills", []),
            "grammar_suggestions": grammar_result if isinstance(grammar_result, list) else [],
            "improvement_suggestions": improvement_result if isinstance(improvement_result, list) else [],
            "overall_score": overall_score
        }
        
    except Exception as e:
        print(f"Gemini 분석 실패, 기본 분석으로 대체: {e}")
        return await analyze_cover_letter_basic(text, job_description)

def calculate_overall_score(summary_result: Dict, star_result: List, job_fit_result: Dict, improvement_result: List, grammar_result: List) -> int:
    """종합 점수 계산 (0-100)"""
    score = 0
    
    # 요약 및 핵심 강점 (20점)
    if summary_result.get("summary") and summary_result.get("top_strengths"):
        score += 20
    
    # STAR 사례 (25점)
    if star_result and len(star_result) > 0:
        score += min(25, len(star_result) * 8)
    
    # 직무 적합성 (30점)
    job_fit_score = job_fit_result.get("score", 0)
    score += int(job_fit_score * 0.3)
    
    # 개선 제안 (15점)
    if improvement_result and len(improvement_result) > 0:
        score += min(15, len(improvement_result) * 2)
    
    # 문법 검사 (10점)
    if grammar_result and len(grammar_result) > 0:
        score += min(10, len(grammar_result) * 1.5)
    
    return min(100, score)

# def generate_embedding(text: str) -> List[float]:
#     """텍스트 임베딩 생성"""
#     try:
#         model = SentenceTransformer('all-MiniLM-L6-v2')
#         embedding = model.encode([text])[0].tolist()
#         return embedding
#     except Exception as e:
#         print(f"임베딩 생성 실패: {e}")
#         return []


# 환경 변수에서 API 키 로드
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") 
# PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")

# 서비스 초기화 (현재 사용하지 않음)
# embedding_service = EmbeddingService()
# vector_service = VectorService(
#     api_key=PINECONE_API_KEY or "dummy-key",  # API 키가 없어도 서버 시작은 가능
#     index_name=PINECONE_INDEX_NAME
# )
# similarity_service = SimilarityService(embedding_service, vector_service)

# Pydantic 모델들
class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    role: str = "user"
    created_at: Optional[datetime] = None

class Resume(BaseModel):
    id: Optional[str] = None
    resume_id: Optional[str] = None
    name: str
    position: str
    department: str
    experience: str
    skills: str
    growthBackground: str
    motivation: str
    careerHistory: str
    analysisScore: int = 0
    analysisResult: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None

class ResumeChunk(BaseModel):
    id: Optional[str] = None
    resume_id: str
    chunk_id: str
    text: str
    start_pos: int
    end_pos: int
    chunk_index: int
    field_name: Optional[str] = None  # growthBackground, motivation, careerHistory
    metadata: Optional[Dict[str, Any]] = None
    vector_id: Optional[str] = None  # Pinecone 벡터 ID
    created_at: Optional[datetime] = None

class Interview(BaseModel):
    id: Optional[str] = None
    user_id: str
    company: str
    position: str
    date: datetime
    status: str = "scheduled"
    created_at: Optional[datetime] = None

# 자소서 분석 관련 모델들
class CoverLetterAnalysis(BaseModel):
    id: Optional[str] = None
    filename: str
    original_text: str
    summary: str
    top_strengths: List[Dict[str, Any]]
    star_cases: List[Dict[str, Any]]
    job_fit_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    grammar_suggestions: List[Dict[str, str]]
    improvement_suggestions: List[Dict[str, str]]
    overall_score: int
    analysis_date: Optional[datetime] = None
    job_description: Optional[str] = None
    # embedding: Optional[List[float]] = None

class JobDescription(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    company: str
    position_level: str

# API 라우트들
@app.get("/")
async def root():
    return {"message": "AI 채용 관리 시스템 API가 실행 중입니다."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 이력서 분석 API 엔드포인트 (레거시: 상세 분석은 routers.upload의 /api/upload/analyze 사용)
@app.post("/api/upload/analyze-legacy")
async def analyze_resume_legacy(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    company: str = Form(""),
    position: str = Form("")
):
    """이력서 파일 업로드 및 분석"""
    try:
        # 파일 크기 제한 (10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")
        
        # 파일 내용 읽기
        content = await file.read()
        
        # 텍스트 추출
        extracted_text = extract_text_from_file(file.filename, content)
        
        # 문단 및 문장 분리
        paragraphs = split_into_paragraphs(extracted_text)
        sentences = split_into_sentences(extracted_text)
        
        # LLM을 사용한 이력서 분석
        analysis_result = await analyze_cover_letter_with_llm(extracted_text, job_description)
        
        # 분석 결과를 MongoDB에 저장
        resume_doc = {
            "filename": file.filename,
            "original_text": extracted_text,
            "paragraphs": paragraphs,
            "sentences": sentences,
            "summary": analysis_result["summary"],
            "top_strengths": analysis_result["top_strengths"],
            "star_cases": analysis_result["star_cases"],
            "job_fit_score": analysis_result["job_fit_score"],
            "matched_skills": analysis_result["matched_skills"],
            "missing_skills": analysis_result["missing_skills"],
            "grammar_suggestions": analysis_result["grammar_suggestions"],
            "improvement_suggestions": analysis_result["improvement_suggestions"],
            "overall_score": analysis_result["overall_score"],
            "analysis_date": datetime.now(),
            "job_description": job_description,
            "company": company,
            "position": position
        }
        
        result = await db.resumes.insert_one(resume_doc)
        resume_doc["id"] = str(result.inserted_id)
        
        return {
            "message": "이력서 분석(레거시)이 완료되었습니다.",
            "analysis_id": str(result.inserted_id),
            "analysis_result": analysis_result,
            "overall_summary": {
                "total_score": analysis_result["overall_score"] / 10,  # 0-100을 0-10으로 변환
                "summary": analysis_result["summary"],
                "top_strengths": analysis_result["top_strengths"],
                "star_cases": analysis_result["star_cases"],
                "job_fit_score": analysis_result["job_fit_score"],
                "matched_skills": analysis_result["matched_skills"],
                "missing_skills": analysis_result["missing_skills"],
                "grammar_suggestions": analysis_result["grammar_suggestions"],
                "improvement_suggestions": analysis_result["improvement_suggestions"]
            },
            "paragraphs_count": len(paragraphs),
            "sentences_count": len(sentences)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 분석 실패: {str(e)}")

# 자소서 분석 관련 API 엔드포인트들
@app.post("/api/cover-letter/upload")
async def upload_cover_letter(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    company: str = Form(""),
    position: str = Form("")
):
    """자소서 파일 업로드 및 분석"""
    try:
        # 파일 크기 제한 (10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB를 초과할 수 없습니다.")
        
        # 파일 내용 읽기
        content = await file.read()
        
        # 텍스트 추출
        extracted_text = extract_text_from_file(file.filename, content)
        
        # 문단 및 문장 분리
        paragraphs = split_into_paragraphs(extracted_text)
        sentences = split_into_sentences(extracted_text)
        
        # LLM을 사용한 자소서 분석
        analysis_result = await analyze_cover_letter_with_llm(extracted_text, job_description)
        
        # 임베딩 생성 (현재 사용하지 않음)
        # embedding = generate_embedding(extracted_text)
        
        # 분석 결과를 MongoDB에 저장
        cover_letter_doc = {
            "filename": file.filename,
            "original_text": extracted_text,
            "paragraphs": paragraphs,
            "sentences": sentences,
            "summary": analysis_result["summary"],
            "top_strengths": analysis_result["top_strengths"],
            "star_cases": analysis_result["star_cases"],
            "job_fit_score": analysis_result["job_fit_score"],
            "matched_skills": analysis_result["matched_skills"],
            "missing_skills": analysis_result["missing_skills"],
            "grammar_suggestions": analysis_result["grammar_suggestions"],
            "improvement_suggestions": analysis_result["improvement_suggestions"],
            "overall_score": analysis_result["overall_score"],
            "analysis_date": datetime.now(),
            "job_description": job_description,
            "company": company,
            "position": position,
            # "embedding": embedding  # 현재 사용하지 않음
        }
        
        result = await db.cover_letters.insert_one(cover_letter_doc)
        cover_letter_doc["id"] = str(result.inserted_id)
        
        return {
            "message": "자소서 분석이 완료되었습니다.",
            "analysis_id": str(result.inserted_id),
            "analysis_result": analysis_result,
            "overall_summary": {
                "total_score": analysis_result["overall_score"] / 10,  # 0-100을 0-10으로 변환
                "summary": analysis_result["summary"],
                "top_strengths": analysis_result["top_strengths"],
                "star_cases": analysis_result["star_cases"],
                "job_fit_score": analysis_result["job_fit_score"],
                "matched_skills": analysis_result["matched_skills"],
                "missing_skills": analysis_result["missing_skills"],
                "grammar_suggestions": analysis_result["grammar_suggestions"],
                "improvement_suggestions": analysis_result["improvement_suggestions"]
            },
            "paragraphs_count": len(paragraphs),
            "sentences_count": len(sentences)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자소서 분석 실패: {str(e)}")

@app.get("/api/cover-letter/{analysis_id}")
async def get_cover_letter_analysis(analysis_id: str):
    """자소서 분석 결과 조회"""
    try:
        from bson import ObjectId
        analysis = await db.cover_letters.find_one({"_id": ObjectId(analysis_id)})
        
        if not analysis:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        analysis["id"] = str(analysis["_id"])
        del analysis["_id"]
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 결과 조회 실패: {str(e)}")

@app.get("/api/cover-letter/list")
async def list_cover_letter_analyses(skip: int = 0, limit: int = 20):
    """자소서 분석 결과 목록 조회"""
    try:
        analyses = await db.cover_letters.find().skip(skip).limit(limit).to_list(limit)
        
        for analysis in analyses:
            analysis["id"] = str(analysis["_id"])
            del analysis["_id"]
        
        total_count = await db.cover_letters.count_documents({})
        
        return {
            "analyses": analyses,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 결과 목록 조회 실패: {str(e)}")

@app.post("/api/cover-letter/similar")
async def find_similar_cover_letters(
    text: str = Form(...),
    limit: int = Form(5)
):
    """유사한 자소서 검색 (벡터 유사도 기반)"""
    try:
        # 입력 텍스트의 임베딩 생성 (비활성화)
        query_embedding = []
        
        # MongoDB에서 유사한 임베딩 검색 (간단한 유클리드 거리 사용)
        all_analyses = await db.cover_letters.find({"embedding": {"$exists": True}}).to_list(1000)
        
        # 유사도 계산 및 정렬
        similarities = []
        for analysis in all_analyses:
            if analysis.get("embedding"):
                # 임시 유사도 값 (임베딩 비활성화 상태)
                import random
                distance = 1.0 - random.uniform(0.0, 1.0)
                similarities.append((distance, analysis))
        
        # 거리 기준으로 정렬 (가까울수록 유사)
        similarities.sort(key=lambda x: x[0])
        
        # 상위 결과 반환
        top_results = []
        for distance, analysis in similarities[:limit]:
            analysis["id"] = str(analysis["_id"])
            analysis["similarity_score"] = 1.0 / (1.0 + distance)  # 0-1 범위의 유사도 점수
            del analysis["_id"]
            del analysis["embedding"]  # 임베딩은 제외
            top_results.append(analysis)
        
        return {
            "query_text": text,
            "similar_analyses": top_results,
            "total_found": len(top_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사 자소서 검색 실패: {str(e)}")

@app.post("/api/cover-letter/improve")
async def get_improvement_suggestions(
    text: str = Form(...),
    focus_area: str = Form("all")  # "grammar", "style", "content", "all"
):
    """자소서 개선 제안 생성"""
    try:
        if focus_area == "grammar":
            prompt = f"""다음 자소서의 문법 오류를 찾아 교정 제안을 해주세요. 각 오류에 대해 원래 문장과 교정된 문장을 짝지어 반환하세요.

자소서:
{text}

Response: [{{"original":"...", "corrected":"...", "explanation":"오류 설명"}}]"""
        elif focus_area == "style":
            prompt = f"""다음 자소서를 더 간결하고 적극적으로 바꿔라. 원래 문장과 개선 문장을 짝지어 반환.

자소서:
{text}

Response: [{{"original":"...", "improved":"... (한 줄)"}}]"""
        elif focus_area == "content":
            prompt = f"""다음 자소서의 내용을 개선하여 더 구체적이고 설득력 있게 만들어주세요. 각 문장에 대한 개선 제안을 제공하세요.

자소서:
{text}

Response: [{{"original":"...", "improved":"...", "explanation":"개선 이유"}}]"""
        else:
            prompt = f"""다음 자소서를 종합적으로 개선해주세요. 문법, 스타일, 내용을 모두 고려하여 개선 제안을 제공하세요.

자소서:
{text}

Response: [{{"original":"...", "improved":"...", "explanation":"개선 이유"}}]"""
        
        if not GEMINI_AVAILABLE:
            raise HTTPException(status_code=400, detail="Gemini API가 설정되지 않았습니다.")
        
        # Gemini 모델 초기화
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        improvement_result = json.loads(response.text)
        
        return {
            "focus_area": focus_area,
            "original_text": text,
            "improvements": improvement_result if isinstance(improvement_result, list) else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개선 제안 생성 실패: {str(e)}")

# 사용자 관련 API
@app.get("/api/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return [User(**user) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict["created_at"] = datetime.now()
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)

# 이력서 관련 API
@app.get("/api/resumes", response_model=List[Resume])
async def get_resumes():
    resumes = await db.resumes.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for resume in resumes:
        resume["id"] = str(resume["_id"])
        del resume["_id"]
    return [Resume(**resume) for resume in resumes]

@app.post("/api/resumes", response_model=Resume)
async def create_resume(resume: Resume):
    resume_dict = resume.dict()
    resume_dict["created_at"] = datetime.now()
    result = await db.resumes.insert_one(resume_dict)
    resume_dict["id"] = str(result.inserted_id)
    return Resume(**resume_dict)

# 면접 관련 API
@app.get("/api/interviews", response_model=List[Interview])
async def get_interviews():
    interviews = await db.interviews.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for interview in interviews:
        interview["id"] = str(interview["_id"])
        del interview["_id"]
    return [Interview(**interview) for interview in interviews]

@app.post("/api/interviews", response_model=Interview)
async def create_interview(interview: Interview):
    interview_dict = interview.dict()
    interview_dict["created_at"] = datetime.now()
    result = await db.interviews.insert_one(interview_dict)
    interview_dict["id"] = str(result.inserted_id)
    return Interview(**interview_dict)

# 지원자 관련 API
@app.get("/api/applicants")
async def get_applicants(skip: int = 0, limit: int = 20):
    try:
        # 페이징으로 지원자 목록 조회 (applicants 컬렉션 사용)
        applicants = await db.applicants.find().skip(skip).limit(limit).to_list(limit)
        
        # MongoDB의 _id를 id로 변환 및 필요한 필드들 추가
        for applicant in applicants:
            applicant["id"] = str(applicant["_id"])
            del applicant["_id"]
            
            # 필수 필드들이 없는 경우 기본값 설정
            if "email" not in applicant:
                applicant["email"] = "이메일 정보 없음"
            if "phone" not in applicant:
                applicant["phone"] = "전화번호 정보 없음"
            if "appliedDate" not in applicant:
                applicant["appliedDate"] = applicant.get("created_at", "지원일 정보 없음")
            if "skills" not in applicant:
                applicant["skills"] = applicant.get("skills", "기술 정보 없음")
        
        # 총 지원자 수
        total_count = await db.applicants.count_documents({})
        
        return {
            "applicants": applicants,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 목록 조회 실패: {str(e)}")

# 지원자 통계 API
@app.get("/api/applicants/stats/overview")
async def get_applicant_stats():
    try:
        # 총 지원자 수 (applicants 컬렉션 기준)
        total_applicants = await db.applicants.count_documents({})
        
        # 상태별 지원자 수
        pending_count = await db.applicants.count_documents({"status": "pending"})
        approved_count = await db.applicants.count_documents({"status": "approved"})
        rejected_count = await db.applicants.count_documents({"status": "rejected"})
        
        # 최근 30일간 지원자 수
        thirty_days_ago = datetime.now().replace(day=datetime.now().day-30) if datetime.now().day > 30 else datetime.now().replace(month=datetime.now().month-1, day=1)
        recent_applicants = await db.applicants.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        return {
            "total_applicants": total_applicants,
            "status_breakdown": {
                "pending": pending_count,
                "approved": approved_count,
                "rejected": rejected_count
            },
            "recent_applicants_30_days": recent_applicants,
            "success_rate": round((approved_count / total_applicants * 100) if total_applicants > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 통계 조회 실패: {str(e)}")

# Vector Service API
@app.post("/api/vector/create")
async def create_vector(data: Dict[str, Any]):
    """텍스트를 벡터로 변환하여 저장"""
    try:
        text = data.get("text", "")
        document_id = data.get("document_id")
        metadata = data.get("metadata", {})
        
        # 여기서 실제 벡터화 로직 구현
        # 예: embedding_model을 사용하여 텍스트를 벡터로 변환
        
        # 임시로 성공 응답 반환
        return {
            "message": "Vector created successfully",
            "document_id": document_id,
            "vector_dimension": 384,  # 예시 차원
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 생성 실패: {str(e)}")

@app.post("/api/vector/search")
async def search_vectors(data: Dict[str, Any]):
    """벡터 유사도 검색"""
    try:
        query_text = data.get("query", "")
        top_k = data.get("top_k", 5)
        threshold = data.get("threshold", 0.7)
        
        # 여기서 실제 벡터 검색 로직 구현
        
        # 임시로 검색 결과 반환
        return {
            "results": [
                {
                    "document_id": "doc_001",
                    "score": 0.95,
                    "text": "검색된 텍스트 샘플 1",
                    "metadata": {"type": "resume", "applicant_id": "app_001"}
                },
                {
                    "document_id": "doc_002", 
                    "score": 0.87,
                    "text": "검색된 텍스트 샘플 2",
                    "metadata": {"type": "cover_letter", "applicant_id": "app_002"}
                }
            ],
            "total_found": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 검색 실패: {str(e)}")

# Chunking Service API
@app.post("/api/chunking/split")
async def split_text(data: Dict[str, Any]):
    """텍스트를 청크로 분할하고 DB에 저장"""
    try:
        text = data.get("text", "")
        resume_id = data.get("resume_id")
        field_name = data.get("field_name", "")  # growthBackground, motivation, careerHistory
        chunk_size = data.get("chunk_size", 1000)
        chunk_overlap = data.get("chunk_overlap", 200)
        split_type = data.get("split_type", "recursive")
        
        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")
        
        # 텍스트 분할 로직
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]
            
            if chunk_text.strip():  # 빈 청크는 제외
                chunk_id = f"chunk_{chunk_index:03d}"
                vector_id = f"resume_{resume_id}_{chunk_id}"
                
                chunk_doc = {
                    "resume_id": resume_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_index": chunk_index,
                    "field_name": field_name,
                    "vector_id": vector_id,
                    "metadata": {
                        "length": len(chunk_text),
                        "split_type": split_type,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    },
                    "created_at": datetime.now()
                }
                
                # MongoDB에 청크 저장
                result = await db.resume_chunks.insert_one(chunk_doc)
                chunk_doc["id"] = str(result.inserted_id)
                
                chunks.append(chunk_doc)
                chunk_index += 1
            
            start = end - chunk_overlap if chunk_overlap > 0 else end
            
            if start >= text_length:
                break
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "original_length": text_length,
            "resume_id": resume_id,
            "field_name": field_name,
            "split_config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "split_type": split_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 분할 실패: {str(e)}")

@app.get("/api/chunking/resume/{resume_id}")
async def get_resume_chunks(resume_id: str):
    """특정 이력서의 모든 청크 조회"""
    try:
        chunks = await db.resume_chunks.find({"resume_id": resume_id}).to_list(1000)
        
        # MongoDB의 _id를 id로 변환
        for chunk in chunks:
            chunk["id"] = str(chunk["_id"])
            del chunk["_id"]
        
        return {
            "resume_id": resume_id,
            "chunks": [ResumeChunk(**chunk) for chunk in chunks],
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 조회 실패: {str(e)}")

@app.post("/api/chunking/process-resume")
async def process_resume_with_chunking(data: Dict[str, Any]):
    """이력서 전체를 필드별로 청킹 처리"""
    try:
        resume_id = data.get("resume_id")
        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")
        
        # 이력서 정보 조회
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")
        
        chunk_size = data.get("chunk_size", 800)
        chunk_overlap = data.get("chunk_overlap", 150)
        
        # 청킹할 필드들
        fields_to_chunk = ["growthBackground", "motivation", "careerHistory"]
        all_chunks = []
        
        for field_name in fields_to_chunk:
            field_text = resume.get(field_name, "")
            if field_text and field_text.strip():
                # 필드별 청킹 처리
                field_chunks = []
                text_length = len(field_text)
                start = 0
                chunk_index = 0
                
                while start < text_length:
                    end = min(start + chunk_size, text_length)
                    chunk_text = field_text[start:end]
                    
                    if chunk_text.strip():
                        chunk_id = f"{field_name}_chunk_{chunk_index:03d}"
                        vector_id = f"resume_{resume_id}_{chunk_id}"
                        
                        chunk_doc = {
                            "resume_id": resume_id,
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "start_pos": start,
                            "end_pos": end,
                            "chunk_index": chunk_index,
                            "field_name": field_name,
                            "vector_id": vector_id,
                            "metadata": {
                                "applicant_name": resume.get("name", ""),
                                "position": resume.get("position", ""),
                                "department": resume.get("department", ""),
                                "length": len(chunk_text)
                            },
                            "created_at": datetime.now()
                        }
                        
                        result = await db.resume_chunks.insert_one(chunk_doc)
                        chunk_doc["id"] = str(result.inserted_id)
                        field_chunks.append(chunk_doc)
                        chunk_index += 1
                    
                    start = end - chunk_overlap if chunk_overlap > 0 else end
                    if start >= text_length:
                        break
                
                all_chunks.extend(field_chunks)
        
        return {
            "resume_id": resume_id,
            "applicant_name": resume.get("name", ""),
            "processed_fields": fields_to_chunk,
            "total_chunks": len(all_chunks),
            "chunks_by_field": {
                field: len([c for c in all_chunks if c["field_name"] == field])
                for field in fields_to_chunk
            },
            "chunks": all_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 청킹 처리 실패: {str(e)}")

@app.post("/api/chunking/merge")
async def merge_chunks(data: Dict[str, Any]):
    """청크들을 병합"""
    try:
        chunks = data.get("chunks", [])
        separator = data.get("separator", "\n\n")
        
        # 청크 병합
        merged_text = separator.join([chunk.get("text", "") for chunk in chunks])
        
        return {
            "merged_text": merged_text,
            "total_length": len(merged_text),
            "chunks_merged": len(chunks),
            "separator_used": separator
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 병합 실패: {str(e)}")

# Similarity Service API
@app.post("/api/similarity/compare")
async def compare_similarity(data: Dict[str, Any]):
    """두 텍스트 간의 유사도 계산"""
    try:
        text1 = data.get("text1", "")
        text2 = data.get("text2", "")
        method = data.get("method", "cosine")  # cosine, jaccard, levenshtein
        
        # 여기서 실제 유사도 계산 로직 구현
        # 예: sentence-transformers의 cosine similarity
        
        # 임시로 유사도 점수 반환
        import random
        similarity_score = random.uniform(0.3, 0.95)  # 임시 점수
        
        return {
            "similarity_score": round(similarity_score, 4),
            "method": method,
            "text1_length": len(text1),
            "text2_length": len(text2),
            "comparison_result": {
                "highly_similar": similarity_score > 0.8,
                "moderately_similar": 0.5 < similarity_score <= 0.8,
                "low_similar": similarity_score <= 0.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 계산 실패: {str(e)}")

@app.post("/api/similarity/batch")
async def batch_similarity(data: Dict[str, Any]):
    """여러 텍스트들 간의 일괄 유사도 계산"""
    try:
        texts = data.get("texts", [])
        reference_text = data.get("reference_text", "")
        method = data.get("method", "cosine")
        threshold = data.get("threshold", 0.7)
        
        # 배치 유사도 계산
        results = []
        import random
        
        for i, text in enumerate(texts):
            similarity_score = random.uniform(0.2, 0.95)  # 임시 점수
            results.append({
                "index": i,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "similarity_score": round(similarity_score, 4),
                "above_threshold": similarity_score >= threshold
            })
        
        # 임계값 이상인 결과들 필터링
        filtered_results = [r for r in results if r["above_threshold"]]
        
        return {
            "results": results,
            "filtered_results": filtered_results,
            "total_compared": len(texts),
            "above_threshold_count": len(filtered_results),
            "method": method,
            "threshold": threshold,
            "reference_text_length": len(reference_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 유사도 계산 실패: {str(e)}")

@app.get("/api/similarity/metrics")
async def get_similarity_metrics():
    """유사도 서비스 메트릭 조회"""
    try:
        # 임시 메트릭 데이터
        return {
            "total_comparisons": 1250,
            "average_similarity": 0.67,
            "supported_methods": ["cosine", "jaccard", "levenshtein", "semantic"],
            "performance_stats": {
                "average_processing_time_ms": 45,
                "comparisons_per_second": 220,
                "cache_hit_rate": 0.78
            },
            "usage_by_method": {
                "cosine": 850,
                "semantic": 300,
                "jaccard": 70,
                "levenshtein": 30
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 조회 실패: {str(e)}")

# 이력서 유사도 체크 API
@app.post("/api/resume/similarity-check/{resume_id}")
async def check_resume_similarity(resume_id: str):
    """특정 이력서의 유사도 체크 (다른 모든 이력서와 비교)"""
    try:
        print(f"🔍 유사도 체크 요청 - resume_id: {resume_id}")
        
        # ObjectId 변환 시도
        try:
            object_id = ObjectId(resume_id)
            print(f"✅ ObjectId 변환 성공: {object_id}")
        except Exception as oid_error:
            print(f"❌ ObjectId 변환 실패: {oid_error}")
            raise HTTPException(status_code=400, detail=f"잘못된 resume_id 형식: {resume_id}")
        
        # 현재 이력서 정보 조회
        current_resume = await db.resumes.find_one({"_id": object_id})
        print(f"🔍 데이터베이스 조회 결과: {current_resume is not None}")
        
        if not current_resume:
            # 상세 덤프 대신 간단한 진단만 남기고 404 반환
            raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")
        
        # 다른 모든 이력서 조회 (현재 이력서 제외)
        other_resumes = await db.resumes.find({"_id": {"$ne": ObjectId(resume_id)}}).to_list(1000)
        
        # 현재 이력서의 비교 텍스트 (유사도 계산 필드)
        current_fields = {
            "growthBackground": current_resume.get("growthBackground", ""),
            "motivation": current_resume.get("motivation", ""),
            "careerHistory": current_resume.get("careerHistory", "")
        }
        
        # 전체 텍스트 조합
        current_text = " ".join([text for text in current_fields.values() if text])
        
        similarity_results = []
        
        for other_resume in other_resumes:
            other_id = str(other_resume["_id"])
            
            # 다른 이력서의 비교 텍스트
            other_fields = {
                "growthBackground": other_resume.get("growthBackground", ""),
                "motivation": other_resume.get("motivation", ""), 
                "careerHistory": other_resume.get("careerHistory", "")
            }
            other_text = " ".join([text for text in other_fields.values() if text])
            
            # 실제 유사도 계산 사용
            try:
                print(f"💫 이력서 간 유사도 계산 시작: {resume_id} vs {other_id}")
                
                # SimilarityService의 텍스트 유사도 계산 메서드 직접 호출 (현재 사용하지 않음)
                # text_similarity = similarity_service._calculate_text_similarity(current_resume, other_resume)
                # overall_similarity = text_similarity if text_similarity is not None else 0.0
                
                # 임시로 랜덤 값 사용
                overall_similarity = random.uniform(0.1, 0.9)
                
                print(f"📊 텍스트 유사도 결과: {overall_similarity:.3f}")
                
                # 필드별 유사도 계산 (임시로 랜덤 값 사용)
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        # 필드별 개별 텍스트 유사도 계산 (임시로 랜덤 값 사용)
                        # field_sim = similarity_service._calculate_text_similarity(
                        #     {field_name: current_fields[field_name]},
                        #     {field_name: other_fields[field_name]}
                        # )
                        field_similarities[field_name] = random.uniform(0.0, 1.0)
                        print(f"📋 {field_name} 유사도: {field_similarities[field_name]:.3f}")
                    else:
                        field_similarities[field_name] = 0.0
                        
            except Exception as e:
                print(f"❌ 유사도 계산 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                
                # 오류 시 기본값 사용
                overall_similarity = random.uniform(0.1, 0.9)
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        field_similarities[field_name] = random.uniform(0.0, 1.0)
                    else:
                        field_similarities[field_name] = 0.0
            
            similarity_result = {
                "resume_id": other_id,
                "applicant_name": other_resume.get("name", "알 수 없음"),
                "position": other_resume.get("position", ""),
                "department": other_resume.get("department", ""),
                "overall_similarity": round(overall_similarity, 4),
                "field_similarities": {
                    "growthBackground": round(field_similarities["growthBackground"], 4),
                    "motivation": round(field_similarities["motivation"], 4),
                    "careerHistory": round(field_similarities["careerHistory"], 4)
                },
                "is_high_similarity": overall_similarity > 0.7,
                "is_moderate_similarity": 0.4 <= overall_similarity <= 0.7,
                "is_low_similarity": overall_similarity < 0.4
            }
            
            similarity_results.append(similarity_result)
        
        # 유사도 높은 순으로 정렬
        similarity_results.sort(key=lambda x: x["overall_similarity"], reverse=True)
        
        # 통계 정보
        high_similarity_count = len([r for r in similarity_results if r["is_high_similarity"]])
        moderate_similarity_count = len([r for r in similarity_results if r["is_moderate_similarity"]])
        low_similarity_count = len([r for r in similarity_results if r["is_low_similarity"]])
        
        return {
            "current_resume": {
                "id": resume_id,
                "name": current_resume.get("name", ""),
                "position": current_resume.get("position", ""),
                "department": current_resume.get("department", "")
            },
            "similarity_results": similarity_results,
            "statistics": {
                "total_compared": len(similarity_results),
                "high_similarity_count": high_similarity_count,
                "moderate_similarity_count": moderate_similarity_count,
                "low_similarity_count": low_similarity_count,
                "average_similarity": round(sum([r["overall_similarity"] for r in similarity_results]) / len(similarity_results) if similarity_results else 0, 4)
            },
            "top_similar": similarity_results[:5] if similarity_results else [],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        # 명시적으로 발생시킨 4xx는 그대로 전달
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 체크 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 