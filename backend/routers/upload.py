from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
import tempfile
import asyncio
import aiofiles
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel
import re

# .env 파일 로드 (현재 디렉토리에서)
print(f"🔍 upload.py 현재 작업 디렉토리: {os.getcwd()}")
print(f"🔍 upload.py .env 파일 존재 여부: {os.path.exists('.env')}")
load_dotenv('.env')
print(f"🔍 upload.py GOOGLE_API_KEY 로드 후: {os.getenv('GOOGLE_API_KEY')}")

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

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
        # 통합 분석 프롬프트 - 직무별 맞춤형 분석 및 적합률 계산
        analysis_prompt = f"""
[ROLE] 당신은 직무별 채용 전문가입니다. 업로드된 이력서와 자기소개서를 직무별 중요사항과 필수 역량에 맞춰 평가하고, 적합률을 계산하여 상세한 피드백을 제공하세요.

[절대 규칙]
- 반드시 JSON 형식만 출력하세요
- JSON 외의 텍스트, 메모, 설명은 절대 포함하지 마세요
- "**Note:**", "참고:", "예시:" 등의 텍스트는 절대 포함하지 마세요
- JSON 응답 후 아무것도 추가하지 마세요

[중요: 실제 문서 내용 기반 분석]
- 반드시 제공된 문서 내용만을 기반으로 분석하세요
- 문서에 없는 내용을 추측하거나 가정하지 마세요
- 문서에 명시되지 않은 정보에 대해 점수를 매기지 마세요
- 실제 문서 내용을 구체적으로 인용하여 피드백을 작성하세요

[이력서 분석 시 가이드: 형식적 답변 금지]
- 각 항목의 피드백은 반드시 실제 이력서 텍스트에서 인용구(따옴표)로 최소 1개 이상 포함하세요
- 인용구 바로 뒤에 개선 제안을 한 문장으로 제시하세요
- "형식적인 일반 조언"은 금지합니다. 문서의 구체 표현, 수치, 기술명, 기간 등만을 근거로 하세요
- 정량 지표(숫자, %, 기간, 규모)가 없다면 "정량 지표 부재"를 명시하고, 무엇을 채워야 할지 구체적으로 제안하세요

[직무별 중요사항 및 필수 역량 평가 기준]

## ① 개발자 / 엔지니어
**중요 사항:**
- JD에 명시된 프로그래밍 언어, 프레임워크, 협업 툴 등 기술 스택과 툴의 일치 여부 확인
- 프로젝트 경험은 단순 나열이 아닌, STAR 기법 기반 구조 + 수치 성과 포함

**필수 역량:**
- AI 도구 활용 능력 (예: 코드 리뷰 자동화, 테스트 자동화 등)
- 지속적인 업스킬링 학습력, 문제 해결력, 효율 개선 경험

## ② 데이터 / AI 분석가
**중요 사항:**
- Python, SQL, Tableau, Power BI 같은 데이터 분석 툴 및 언어 키워드 반영
- 분석 결과와 영향(예: 매출 증가, 고객 만족도 향상 등) 명시

**필수 역량:**
- 데이터 기반 의사결정 능력, AI 활용 능력
- 협업 도구 활용 경험 (예: 클라우드, 협업 플랫폼 등), 원격 협업 능력

## ③ 기획 / 프로덕트 매니저 (PM)
**중요 사항:**
- JD에서 요구하는 프로세스 관리, 프로젝트 목표 달성 경험, 성과 지표 (KPI) 연결
- 협업 능력과 갈등 해결 경험 강조

**필수 역량:**
- 커뮤니케이션 능력 + 전략적 사고 + 조직 적합성
- STAR 방식으로 문제 상황 → 해결 과정 → 결과 전달, 수치 포함

## ④ 프로젝트 매니저 / 운영 직무
**중요 사항:**
- PM 경험이나 일정 관리, 예산 관리, 리소스 조율 등 JD 관련 경험 요약
- 면접 질문 설계 시, "최근 담당 프로젝트의 가장 큰 도전과 극복 사례" 같은 질문 예상

**필수 역량:**
- 일정 준수율, 품질 관리, 협업 조율력 등 수치 기반 성과 활용
- AI 도구를 통한 일정 관리나 업무 자동화 경험

## ⑤ HR / 채용 담당자
**중요 사항:**
- "3년 이상 채용/HR 담당 경력" 같은 필수 요건 여부
- ATS, MS Office, 데이터 기반 채용 경험 등의 도구 역량

**필수 역량:**
- 체계적인 평가 기준 설정 능력 (Google식 GCA, RRKE, 리더십 등)
- JD 기반 체계적 프로세스 설계 및 실행 경험

[직무별 평가 기준 - 0-10점]
- 0-2점: 해당 항목이 전혀 충족되지 않음 (심각한 문제)
- 3-4점: 매우 부족함 (대폭 개선 필요)
- 5-6점: 보통 수준, 개선 여지가 있음 (중간 수준)
- 7-8점: 양호함, 일부 개선점 있음 (좋은 수준)
- 9-10점: 매우 우수함, 모범 사례 수준 (완벽함)

[직무별 적합률 계산 가중치]
**개발자/엔지니어:**
- 기술 스택 일치도: 40%
- 프로젝트 경험 (STAR + 수치): 30%
- AI 도구 활용 능력: 20%
- 학습력/문제해결력: 10%

**데이터/AI 분석가:**
- 데이터 분석 도구 역량: 35%
- AI 활용 능력: 25%
- 분석 결과/영향 수치: 25%
- 협업 도구 경험: 15%

**기획/PM:**
- 프로세스 관리 경험: 30%
- KPI 달성 성과: 25%
- 협업/갈등해결 능력: 25%
- 전략적 사고: 20%

**프로젝트 매니저/운영:**
- PM 경험/일정관리: 35%
- 수치 기반 성과: 30%
- 리소스 조율 능력: 25%
- AI 도구 활용: 10%

**HR/채용 담당자:**
- 필수 요건 충족도: 40%
- 도구 역량: 25%
- 평가 기준 설정: 20%
- 프로세스 설계: 15%

[이력서 분석 항목 - 직무별 맞춤형]
1. basic_info_completeness: 
   - 필수 정보: 이름, 연락처, 직무 관련 필수 요건 충족 여부
   - 학력 정보: 전공분야, 관련 수업/프로젝트, 직무 관련 자격증
   - 경력 기간: 각 회사별 재직기간, 직무명, 담당 업무 영역
   - 추가 정보: 직무 관련 포트폴리오, 인증서, 수상 경험

2. job_relevance: 
   - 지원 직무와 보유 역량의 직접적 연관성
   - JD 요구사항과 실제 보유 역량의 일치 정도
   - 관련 프로젝트 경험: 지원 직무와 직접 관련된 프로젝트의 규모, 기간, 역할, 성과
   - 업계 경험: 해당 분야에서의 경력 기간과 전문성 수준

3. experience_clarity: 
   - 각 경험의 역할과 책임: 구체적인 직무명, 담당 업무, 팀 내 위치
   - 경험 기간: 시작일-종료일, 단계별 참여 기간
   - 경험 규모: 프로젝트 규모, 예산, 인원, 복잡도 등 구체적 수치
   - 팀 구성: 본인 역할, 팀원 수, 협업 방식, 보고 체계
   - 업무 성과: 구체적인 결과물, 개선 효과, 비즈니스 임팩트

4. tech_stack_clarity: 
   - 직무별 필수 기술/도구: 각 직무에서 요구하는 핵심 기술과 도구
   - 기술/도구 버전: 구체적인 버전 정보와 활용 경험
   - 최신 기술 트렌드: 최근 2-3년 내 출시된 기술의 활용 여부
   - 기술/도구의 다양성: 다양한 영역에서의 활용 경험
   - 기술/도구 깊이: 각 기술/도구에 대한 숙련도, 인증서, 프로젝트 적용 경험

5. project_recency: 
   - 최근 2-3년 내 경험의 비중: 전체 경력 대비 최신 경험의 비율
   - 경험의 규모: 대형, 중형, 소형 구분
   - 경험의 복잡성: 기술적/업무적 난이도, 비즈니스 로직의 복잡성
   - 최신 방법론 적용: 최신 업무 방법론, 도구, 프로세스 활용
   - 경험 성공률: 완료된 경험의 비율, 고객 만족도, 예산/일정 준수율

6. achievement_metrics: 
   - 정량적 성과 지표: 직무별 핵심 성과 지표
   - 구체적인 수치와 데이터: 정확한 수치와 개선 효과
   - 성과의 영향력: 비즈니스에 미친 구체적 영향
   - 비교 데이터: 이전 대비 개선율, 목표 달성률
   - 지속적 개선: 성과 지표의 지속적 모니터링과 개선 노력

7. readability: 
   - 정보의 논리적 배치: 직무별 적절한 정보 구성
   - 가독성: 명확하고 이해하기 쉬운 정보 전달
   - 시각적 요소: 적절한 시각적 요소 활용
   - 일관성: 용어 사용, 형식의 통일성
   - 핵심 정보 강조: 중요한 내용의 적절한 배치와 강조

8. typos_and_errors: 
   - 맞춤법과 문법: 한글 맞춤법, 영어 문법, 전문 용어의 정확성
   - 용어 사용의 정확성: 업계 표준 용어, 회사 내부 용어의 일관된 사용
   - 일관된 문체와 톤앤매너: 존댓말/반말의 일관성, 공식적/비공식적 톤의 적절한 선택
   - 전문성과 신뢰성: 오타나 문법 오류가 없는 깔끔한 문서, 전문가다운 신뢰감
   - 검토 상태: 최종 검토 완료 여부, 수정 이력 관리

9. update_freshness: 
   - 정보의 최신성: 최근 업데이트 여부, 현재 상태와의 일치성
   - 경험과 역량의 최신성: 최신 트렌드 반영, 현재 사용 중인 기술/방법론
   - 업데이트 주기: 정기적인 정보 갱신, 변화 시 즉시 반영
   - 관리 상태: 문서 관리의 체계성, 버전 관리
   - 현실성: 과장되지 않은 정확한 정보, 검증 가능한 사실 기반 기술

[자기소개서 분석 항목 - 직무별 맞춤형]
1. motivation_relevance: 
   - 지원 동기의 명확성: "왜 이 회사인가?", "왜 이 직무인가?"에 대한 명확한 답변
   - 진정성: 개인적 경험과 연결된 진심 어린 동기
   - 회사/직무와의 구체적 연결성: 회사 비전, 제품, 서비스, 문화와의 직접적 연관성
   - 개인적 경험과 지원 동기의 연관성: 과거 경험, 학습, 성장 과정이 지원 동기로 연결되는 논리적 흐름
   - 미래 계획과의 연관성: 지원 동기가 개인의 장기적 커리어 목표와 어떻게 연결되는지

2. problem_solving_STAR: 
   - STAR 기법 적용의 완성도: 상황(Situation)-과제(Task)-행동(Action)-결과(Result)의 모든 요소 포함
   - 구체적인 사례: 실제 발생한 문제 상황, 해결해야 할 과제의 명확한 정의
   - 해결 과정: 문제 분석, 대안 검토, 선택한 해결책의 구체적 실행 과정
   - 문제 해결 능력의 입증: 창의적 사고, 논리적 분석, 실행력, 결과 도출 능력
   - 학습과 성장: 문제 해결 과정에서 얻은 교훈, 개선점, 향후 적용 방안

3. quantitative_impact: 
   - 정량적 성과와 영향력: 구체적인 수치와 데이터를 통한 성과 입증
   - 수치화된 결과: 직무별 핵심 성과 지표
   - 개선 효과: 이전 대비 개선율, 목표 달성률, 예상 효과 대비 실제 결과
   - 비즈니스 임팩트: 회사에 미친 구체적 영향
   - 지속적 성과: 일회성이 아닌 지속적인 개선 효과와 장기적 가치 창출

4. job_understanding: 
   - 직무에 대한 깊은 이해: 해당 직무의 핵심 책임, 요구되는 역량, 업무 프로세스에 대한 정확한 인식
   - 업계 트렌드와 동향: 최신 동향, 시장 변화, 경쟁사 동향에 대한 파악
   - 직무 요구사항의 정확한 인식: 회사가 요구하는 구체적인 역량, 경험, 자격 요건 이해
   - 업무 환경과 문화: 해당 직무의 업무 환경, 팀 문화, 협업 방식에 대한 이해
   - 성장 가능성: 직무에서의 학습 기회, 커리어 발전 경로, 전문성 향상 방안

5. unique_experience: 
   - 차별화된 경험: 다른 지원자와 구별되는 독특한 경험, 특별한 프로젝트, 특수한 상황
   - 개인만의 특별한 스토리: 개인의 성장 과정, 도전과 극복, 실패와 학습의 구체적 사례
   - 경쟁력 있는 차별점: 직무별 전문성, 업계 경험, 인증서, 수상 경력 등 객관적 우수성
   - 창의적 문제 해결: 기존 방식과 다른 혁신적 접근법, 창의적 아이디어의 실제 적용
   - 국제적 경험: 해외 연수, 글로벌 프로젝트, 다국적 팀 협업 등 국제적 역량

6. logical_flow: 
   - 논리적 구조와 흐름: 도입-전개-결론의 명확한 구조, 각 문단의 논리적 연결
   - 각 문단 간의 연결성: 문단 간 자연스러운 전환, 핵심 메시지의 일관성
   - 전개 방식: 시간순, 중요도순, 인과관계순 등 적절한 전개 방식 선택
   - 결론으로의 자연스러운 흐름: 각 문단이 최종 결론으로 연결되는 논리적 흐름
   - 핵심 메시지의 강조: 중요한 내용의 적절한 배치와 강조, 독자의 이해도 향상

7. keyword_diversity: 
   - 전문 용어와 키워드: 해당 직무/업계에서 사용되는 전문 용어의 적절한 활용
   - 업계 표준 용어: 표준화된 용어, 약어, 기술 명세서의 정확한 사용
   - 기술적 깊이와 전문성: 직무별 세부사항, 방법론, 도구에 대한 깊이 있는 설명
   - 트렌드 키워드: 최신 업계 트렌드, 핫 이슈, 신기술 관련 키워드 활용
   - 용어의 일관성: 동일한 개념에 대해 일관된 용어 사용, 혼동을 주지 않는 명확한 표현

8. sentence_readability: 
   - 문장력과 가독성: 명확하고 이해하기 쉬운 문장 구성, 적절한 문장 길이
   - 명확하고 간결한 표현: 불필요한 수식어 제거, 핵심 내용의 명확한 전달
   - 적절한 문장 길이: 너무 길거나 짧지 않은 적절한 문장 길이, 읽기 편한 구성
   - 문체의 일관성: 공식적이면서도 친근한 문체, 일관된 톤앤매너 유지
   - 문법적 정확성: 맞춤법, 문법, 문장 구조의 정확성, 자연스러운 한국어 표현

9. typos_and_errors: 
   - 맞춤법과 문법: 한글 맞춤법, 영어 문법, 전문 용어의 정확성
   - 용어 사용의 정확성: 업계 표준 용어, 회사 내부 용어의 일관된 사용
   - 일관된 문체와 톤앤매너: 존댓말/반말의 일관성, 공식적/비공식적 톤의 적절한 선택
   - 전문성과 신뢰성: 오타나 문법 오류가 없는 깔끔한 문서, 전문가다운 신뢰감
   - 검토 상태: 최종 검토 완료 여부, 수정 이력 관리

[피드백 작성 가이드 - 직무별 맞춤형]
- 각 항목에 대해 반드시 실제 문서에서 발견된 구체적인 내용을 인용하세요
- 문서에 없는 내용을 추측하거나 가정하지 마세요
- 실제 문서 내용을 바탕으로 한 구체적 예시를 포함하세요
- 실무에서 바로 적용 가능한 개선 방안을 제시하세요
- 점수에 따른 명확한 근거와 이유를 설명하세요
- 긍정적 피드백과 개선 제안의 균형을 유지하세요

[출력 형식 강화]
- 모든 feedback은 다음 형식을 준수합니다:
  "인용: <문서에서 발췌한 구체 문장>" → "개선: <해당 문장을 바탕으로 한 구체 개선 제안>"

[구체적 피드백 강제 요구사항 - 반드시 준수]
절대적으로 금지할 것:
❌ "~가 부족합니다", "~가 미흡합니다", "~가 불충분합니다" 등 추상적이고 모호한 표현
❌ "~를 추가하세요", "~를 보완하세요" 등 일반적인 조언
❌ "~가 좋습니다", "~가 우수합니다" 등 구체적 근거 없는 칭찬
❌ 문서에 없는 내용을 추측하거나 가정하는 피드백

반드시 포함해야 할 것:
✅ 실제 문서에서 발견된 구체적인 내용 인용 (예: "React 경험이 기술되어 있지만")
✅ 구체적인 개선 방안 제시 (예: "React 18.2 버전과 함께 TypeScript 적용 경험을 추가하세요")
✅ 정량적 지표나 구체적 예시 포함 (예: "사용자 수 10만명 증가, 페이지 로딩 속도 3초→1초 단축")
✅ 실무에서 바로 적용 가능한 구체적 행동 지침

[AI 분석 강제 지시사항]
당신은 반드시 다음 단계를 따라야 합니다:

1단계: 제공된 문서 내용을 한 글자씩 꼼꼼히 읽고 분석하세요
2단계: 각 항목에서 발견된 구체적인 내용을 정확히 인용하세요
3단계: 구체적인 개선 방안을 제시하세요 (구체적 기술명, 버전, 프로젝트 예시 포함)
4단계: 정량적 지표나 구체적 수치를 포함하세요
5단계: 문서에 없는 내용은 절대 추측하거나 가정하지 마세요

만약 위 단계를 따르지 않으면 분석을 처음부터 다시 시작하세요.

[분석 결과 검증 기준]
각 피드백이 다음 기준을 만족하는지 확인:
1. 실제 문서 내용을 구체적으로 인용했는가?
2. 구체적인 개선 방안을 제시했는가?
3. 정량적 지표나 구체적 예시를 포함했는가?
4. 지원자가 바로 실행할 수 있는 행동 지침인가?
5. 추상적이고 모호한 표현을 사용하지 않았는가?
6. 문서에 없는 내용을 추측하지 않았는가?

위 기준을 만족하지 않으면 피드백을 다시 작성하세요.

[최종 강제 지시사항]
⚠️ 경고: 만약 당신이 추상적이고 모호한 피드백을 생성하거나, 문서에 없는 내용을 추측한다면, 이는 완전히 실패한 분석입니다.

✅ 성공적인 분석의 예시:
"React 경험이 기술되어 있지만 구체적인 버전(React 16? 18?)과 활용 프로젝트가 명시되지 않았습니다. '2023년 사용자 관리 시스템 구축 시 React 18.2 + TypeScript 5.0 조합으로 타입 안정성을 확보하고, Next.js 14를 활용한 SSR 구현 경험을 추가하세요.'"

❌ 실패한 분석의 예시:
"기술 스택이 부족합니다", "기술을 보완하세요", "기술 경험이 미흡합니다", "React 경험이 있을 것으로 예상됩니다"

당신은 반드시 성공적인 분석 예시 수준의 구체적이고 실용적인 피드백을 생성해야 합니다. 
추상적이고 모호한 피드백을 생성하거나 문서에 없는 내용을 추측하면 분석을 처음부터 다시 시작하세요.

[출력] JSON만:
{{
  "resume_analysis": {{
    "basic_info_completeness": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "job_relevance": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "experience_clarity": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "tech_stack_clarity": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "project_recency": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "achievement_metrics": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "readability": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "typos_and_errors": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "update_freshness": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}}
  }},
  "cover_letter_analysis": {{
    "motivation_relevance": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "problem_solving_STAR": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "quantitative_impact": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "job_understanding": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "unique_experience": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "logical_flow": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "keyword_diversity": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "sentence_readability": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "typos_and_errors": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}}
  }},
  "portfolio_analysis": {{
    "project_overview": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "tech_stack": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "personal_contribution": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "achievement_metrics": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "visual_quality": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "documentation_quality": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "job_relevance": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "unique_features": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}},
    "maintainability": {{"score": [0-10], "feedback": "구체적이고 실용적인 피드백"}}
  }},
  "overall_summary": {{
    "total_score": 0,
    "job_fit_score": 0,
    "recommendation": "전체적인 개선 방향과 우선순위를 제시하는 구체적이고 실용적인 조언"
  }},
  "job_specific_analysis": {{
    "job_category": "직무 분류 (개발자/데이터분석가/기획PM/프로젝트매니저/HR)",
    "key_requirements_match": "JD 핵심 요구사항 일치도 (%)",
    "essential_competencies": "필수 역량 충족도 (%)",
    "overall_job_fit": "전체 직무 적합도 (%)",
    "strengths": ["직무별 강점 리스트"],
    "improvement_areas": ["직무별 개선 영역 리스트"],
    "priority_recommendations": ["우선순위별 개선 제안"]
  }}
}}

[분석할 문서 내용]
{content}

[최종 분석 지시사항]
위 내용을 바탕으로 직무별 맞춤형 분석을 수행하고, 각 직무별 중요사항과 필수 역량을 기준으로 적합률을 계산하여 JSON으로만 출력하세요.

⚠️ 중요: 
1. 직무별 중요사항과 필수 역량을 우선적으로 분석하세요.
2. 각 분석 항목마다 반드시 구체적이고 실용적인 피드백을 생성하세요.
3. 평가 속성을 세분화하여 각 항목의 세부 요소를 상세하게 분석하세요.
4. 직무별 적합률을 정확하게 계산하세요.
5. 반드시 제공된 문서 내용만을 기반으로 분석하고, 문서에 없는 내용은 추측하지 마세요.

❌ 절대 추상적이고 모호한 표현을 사용하지 마세요.
✅ 반드시 실제 문서 내용을 인용하고, 구체적인 개선 방안을 제시하세요.

JSON 외의 텍스트는 절대 포함하지 마세요.
"""
        # 모든 문서 타입에 대해 통합 분석 수행
        
        # Gemini API 호출 (JSON 강제)
        json_model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={
                'response_mime_type': 'application/json'
            }
        )
        response = await asyncio.to_thread(
            json_model.generate_content,
            analysis_prompt
        )
        
        # 응답 검증
        if not response or not response.text or response.text.strip() == "":
            raise HTTPException(status_code=500, detail="Gemini API에서 빈 응답을 받았습니다.")
        
        # 일부 드라이버는 .text가 없을 수 있어 안전 접근
        response_text = getattr(response, 'text', '')
        if hasattr(response, 'candidates') and not response_text:
            try:
                # application/json로 내려오면 first candidate의 content를 합성
                parts = []
                for c in response.candidates or []:
                    for p in getattr(c, 'content', {}).get('parts', []):
                        parts.append(str(getattr(p, 'text', '')))
                response_text = ''.join(parts).strip()
            except Exception:
                response_text = ''
        response_text = (response_text or '').strip()
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
            
            # 응답 구조 검증 및 보정
            if not isinstance(analysis_result, dict):
                raise ValueError("응답이 딕셔너리 형식이 아닙니다.")

                # 키 정규화/보정 함수들
            def make_score(obj):
                    if not isinstance(obj, dict):
                        return {"score": 0, "feedback": ""}
                    return {
                        "score": int(obj.get("score", 0)) if isinstance(obj.get("score", 0), (int, float)) else 0,
                        "feedback": str(obj.get("feedback", ""))
                    }

            # 필수 overall_summary 보정
            if "overall_summary" not in analysis_result:
                analysis_result["overall_summary"] = {"total_score": 0, "recommendation": ""}

            # 이력서 섹션 보정 (skill_stack_clarity -> tech_stack_clarity 매핑 포함)
            if isinstance(analysis_result.get("resume_analysis"), dict):
                resume_raw = analysis_result["resume_analysis"]
                if "tech_stack_clarity" not in resume_raw and "skill_stack_clarity" in resume_raw:
                    resume_raw["tech_stack_clarity"] = resume_raw.pop("skill_stack_clarity")
                expected_resume = [
                    "basic_info_completeness","job_relevance","experience_clarity","tech_stack_clarity",
                    "project_recency","achievement_metrics","readability","typos_and_errors","update_freshness"
                ]
                analysis_result["resume_analysis"] = {k: make_score(resume_raw.get(k, {})) for k in expected_resume}
            elif analysis_result.get("resume_analysis") is None:
                analysis_result["resume_analysis"] = None

            # 자소서 섹션 보정
            if isinstance(analysis_result.get("cover_letter_analysis"), dict):
                cover_raw = analysis_result["cover_letter_analysis"]
                expected_cover = [
                    "motivation_relevance","problem_solving_STAR","quantitative_impact","job_understanding",
                    "unique_experience","logical_flow","keyword_diversity","sentence_readability","typos_and_errors"
                ]
                analysis_result["cover_letter_analysis"] = {k: make_score(cover_raw.get(k, {})) for k in expected_cover}
            elif analysis_result.get("cover_letter_analysis") is None:
                analysis_result["cover_letter_analysis"] = None

            # 포트폴리오 섹션 보정
            if isinstance(analysis_result.get("portfolio_analysis"), dict):
                port_raw = analysis_result["portfolio_analysis"]
                expected_port = [
                    "project_overview","tech_stack","personal_contribution","achievement_metrics","visual_quality",
                    "documentation_quality","job_relevance","unique_features","maintainability"
                ]
                analysis_result["portfolio_analysis"] = {k: make_score(port_raw.get(k, {})) for k in expected_port}
            elif analysis_result.get("portfolio_analysis") is None:
                analysis_result["portfolio_analysis"] = None
            
            # 전체 점수 계산 (모든 섹션의 평균)
            total_score = 0
            count = 0
            
            # 이력서 분석 점수
            if "resume_analysis" in analysis_result:
                for value in analysis_result["resume_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            
            # 자기소개서 분석 점수
            if "cover_letter_analysis" in analysis_result:
                for value in analysis_result["cover_letter_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            
            # 포트폴리오 분석 점수
            if "portfolio_analysis" in analysis_result:
                for value in analysis_result["portfolio_analysis"].values():
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
            
            if document_type == "resume" and "resume_analysis" in analysis_result:
                print(f"🔍 이력서 분석 항목: {list(analysis_result['resume_analysis'].keys())}")
                for key, value in analysis_result["resume_analysis"].items():
                    print(f"🔍 {key}: {value}")
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
                        print(f"🔍 {key} 점수: {value['score']}")
            elif document_type == "cover_letter" and "cover_letter_analysis" in analysis_result:
                print(f"🔍 자기소개서 분석 항목: {list(analysis_result['cover_letter_analysis'].keys())}")
                for key, value in analysis_result["cover_letter_analysis"].items():
                    print(f"🔍 {key}: {value}")
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
                        print(f"🔍 {key} 점수: {value['score']}")
            elif document_type == "portfolio" and "portfolio_analysis" in analysis_result:
                print(f"🔍 포트폴리오 분석 항목: {list(analysis_result['portfolio_analysis'].keys())}")
                for key, value in analysis_result["portfolio_analysis"].items():
                    print(f"🔍 {key}: {value}")
                    if isinstance(value, dict) and "score" in value:
                        total_score += value["score"]
                        count += 1
                        print(f"🔍 {key} 점수: {value['score']}")
            
            print(f"🔍 총 점수: {total_score}, 항목 수: {count}")
            
            # 평균 점수 계산 (정수로 변환)
            if count > 0:
                average_score = int(round(total_score / count))
            else:
                average_score = 0
            
            # 추천사항 생성 (통합 분석 기준)
            if average_score >= 8:
                recommendation = "전반적으로 우수한 문서입니다. 현재 상태를 유지하세요."
            elif average_score >= 6:
                recommendation = "양호한 수준이지만 몇 가지 개선점이 있습니다. 피드백을 참고하여 수정하세요."
            else:
                recommendation = "전반적인 개선이 필요합니다. 각 항목별 피드백을 참고하여 체계적으로 수정하세요."

            
            analysis_result["overall_summary"]["total_score"] = average_score
            analysis_result["overall_summary"]["recommendation"] = recommendation
            
            # 문서 타입에 따라 누락된 필드에 기본값 제공
            if document_type == "resume" and "resume_analysis" not in analysis_result:
                # 이력서 분석 결과가 없는 경우 기본값 생성
                analysis_result["resume_analysis"] = {
                    "basic_info_completeness": {"score": 0, "feedback": "분석 실패"},
                    "job_relevance": {"score": 0, "feedback": "분석 실패"},
                    "experience_clarity": {"score": 0, "feedback": "분석 실패"},
                    "tech_stack_clarity": {"score": 0, "feedback": "분석 실패"},
                    "project_recency": {"score": 0, "feedback": "분석 실패"},
                    "achievement_metrics": {"score": 0, "feedback": "분석 실패"},
                    "readability": {"score": 0, "feedback": "분석 실패"},
                    "typos_and_errors": {"score": 0, "feedback": "분석 실패"},
                    "update_freshness": {"score": 0, "feedback": "분석 실패"}
                }
            
            if document_type == "cover_letter" and "cover_letter_analysis" not in analysis_result:
                # 자기소개서 분석 결과가 없는 경우 기본값 생성
                analysis_result["cover_letter_analysis"] = {
                    "motivation_relevance": {"score": 0, "feedback": "분석 실패"},
                    "problem_solving_STAR": {"score": 0, "feedback": "분석 실패"},
                    "quantitative_impact": {"score": 0, "feedback": "분석 실패"},
                    "job_understanding": {"score": 0, "feedback": "분석 실패"},
                    "unique_experience": {"score": 0, "feedback": "분석 실패"},
                    "logical_flow": {"score": 0, "feedback": "분석 실패"},
                    "keyword_diversity": {"score": 0, "feedback": "분석 실패"},
                    "sentence_readability": {"score": 0, "feedback": "분석 실패"},
                    "typos_and_errors": {"score": 0, "feedback": "분석 실패"}
                }
            
            if document_type == "portfolio" and "portfolio_analysis" not in analysis_result:
                # 포트폴리오 분석 결과가 없는 경우 기본값 생성
                analysis_result["portfolio_analysis"] = {
                    "project_overview": {"score": 0, "feedback": "분석 실패"},
                    "tech_stack": {"score": 0, "feedback": "분석 실패"},
                    "personal_contribution": {"score": 0, "feedback": "분석 실패"},
                    "achievement_metrics": {"score": 0, "feedback": "분석 실패"},
                    "visual_quality": {"score": 0, "feedback": "분석 실패"},
                    "documentation_quality": {"score": 0, "feedback": "분석 실패"},
                    "job_relevance": {"score": 0, "feedback": "분석 실패"},
                    "unique_features": {"score": 0, "feedback": "분석 실패"},
                    "maintainability": {"score": 0, "feedback": "분석 실패"}
                }
            
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
            
            # 텍스트 추출 실패 시에도 더미 분석으로 계속 진행 (사용자 경험 개선)
            if not extracted_text or str(extracted_text).strip() == "":
                print("⚠️ 텍스트 추출 실패: 빈 내용 감지 → 더미 분석으로 계속 진행합니다.")
                extracted_text = "[EMPTY_CONTENT] 텍스트 추출 실패 (스캔 PDF/이미지 기반 문서일 수 있습니다.)"
            
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
    document_type: str = Form("resume"),  # resume, cover_letter, portfolio
    applicant_name: str = Form(""),  # 지원자 이름
    position: str = Form(""),  # 희망 직무
    department: str = Form("")  # 희망 부서
):
    # 프론트엔드에서 보내는 한글 문서 타입을 영문으로 변환
    document_type_mapping = {
        "이력서": "resume",
        "자기소개서": "cover_letter", 
        "포트폴리오": "portfolio"
    }
    
    # 한글로 들어온 경우 영문으로 변환
    if document_type in document_type_mapping:
        document_type = document_type_mapping[document_type]
    
    print(f"🔍 변환된 문서 타입: {document_type}")
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
                # 스캔 PDF 등 추출 불가 → 기본 구조로 결과 제공 (400 대신 200)
                fallback = build_fallback_analysis(document_type)
                return {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text_length": 0,
                    "document_type": "통합 분석",
                    "analysis_result": fallback,
                    "detected_type": None,
                    "detected_confidence": 0,
                    "wrong_placement": False,
                    "placement_message": "텍스트 추출 불가 문서로 기본 안내 결과 제공"
                }
            
            # 내용 기반 문서 타입 분류 수행
            classification = classify_document_type_by_content(extracted_text)

            # Gemini API로 상세 분석 생성
            analysis_result = await generate_detailed_analysis_with_gemini(extracted_text, document_type)
            
            # 업로드된 의도(document_type)와 실제 감지 타입이 다르면 경고 포함
            wrong_placement = False
            placement_message = ""
            detected_type = classification.get("detected_type")
            if detected_type and detected_type != document_type:
                wrong_placement = True
                placement_message = f"이 문서는 '{detected_type}'로 감지되었습니다. 현재 영역('{document_type}')에 올바르지 않습니다. 옳지 않은 자리에 놓였습니다."

            # 모든 분석 결과를 통합하여 반환
            return {
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text_length": len(extracted_text),
                "document_type": "통합 분석",
                "analysis_result": analysis_result.dict(),
                "detected_type": detected_type,
                "detected_confidence": classification.get("confidence"),
                "wrong_placement": wrong_placement,
                "placement_message": placement_message
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

@router.post("/validate-document-type")
async def validate_document_type(request: DocumentValidationRequest):
    """문서 내용을 분석하여 선택된 문서 타입과 일치하는지 검증"""
    try:
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="검증할 문서 내용이 없습니다.")
        
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다.")
        
        # 문서 타입 검증을 위한 프롬프트 생성
        validation_prompt = f"""
        다음 문서 내용을 분석하여 이것이 "{request.expected_type}"인지 판단해주세요.
        
        문서 내용:
        {request.content[:2000]}  # 내용이 너무 길면 앞부분만 사용
        
        다음 기준으로 판단해주세요:
        
        이력서의 경우:
        - 개인 정보 (이름, 연락처, 생년월일 등)
        - 학력 정보
        - 경력 정보 (회사명, 직무, 기간)
        - 기술 스택
        - 자격증
        - 프로젝트 경험
        
        자기소개서의 경우:
        - 지원 동기
        - 성장 과정
        - 지원 직무에 대한 이해
        - 본인의 강점과 약점
        - 입사 후 포부
        
        포트폴리오의 경우:
        - 프로젝트 개요
        - 사용 기술
        - 구현 과정
        - 결과물
        - GitHub 링크 등
        
        응답 형식:
        - 유효성: true/false
        - 신뢰도: 0.0-1.0 (소수점)
        - 판단 이유: 간단한 설명
        - 제안 타입: 실제 문서 타입 (이력서/자기소개서/포트폴리오)
        
        JSON 형태로 응답해주세요.
        """
        
        # Gemini API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            validation_prompt
        )
        
        response_text = response.text.strip()
        
        # JSON 응답 파싱 시도
        try:
            # JSON 부분만 추출
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                import json
                parsed_response = json.loads(json_str)
                
                return DocumentValidationResponse(
                    is_valid=parsed_response.get('유효성', False),
                    confidence=parsed_response.get('신뢰도', 0.0),
                    reason=parsed_response.get('판단 이유', '분석 실패'),
                    suggested_type=parsed_response.get('제안 타입', '알 수 없음')
                )
        except (json.JSONDecodeError, KeyError):
            pass
        
        # JSON 파싱 실패 시 텍스트 분석으로 대체
        response_lower = response_text.lower()
        
        # 간단한 키워드 기반 분석
        resume_keywords = ['이력서', 'resume', 'cv', '경력', '학력', '자격증', '프로젝트']
        cover_letter_keywords = ['자기소개서', '자소서', 'cover letter', '지원동기', '성장과정', '포부']
        portfolio_keywords = ['포트폴리오', 'portfolio', '프로젝트', 'github', '구현']
        
        expected_lower = request.expected_type.lower()
        
        if '이력서' in expected_lower:
            relevant_keywords = resume_keywords
            conflicting_keywords = cover_letter_keywords + portfolio_keywords
        elif '자기소개서' in expected_lower:
            relevant_keywords = cover_letter_keywords
            conflicting_keywords = resume_keywords + portfolio_keywords
        elif '포트폴리오' in expected_lower:
            relevant_keywords = portfolio_keywords
            conflicting_keywords = resume_keywords + cover_letter_keywords
        else:
            relevant_keywords = []
            conflicting_keywords = []
        
        # 키워드 기반 유효성 판단
        has_relevant = any(keyword in response_lower for keyword in relevant_keywords)
        has_conflicting = any(keyword in response_lower for keyword in conflicting_keywords)
        
        if has_conflicting:
            is_valid = False
            confidence = 0.8
            reason = f"문서 내용이 {request.expected_type}와 맞지 않습니다."
            suggested_type = "알 수 없음"
        elif has_relevant:
            is_valid = True
            confidence = 0.7
            reason = f"문서 내용이 {request.expected_type}와 일치합니다."
            suggested_type = request.expected_type
        else:
            is_valid = False
            confidence = 0.6
            reason = f"문서 내용을 분석할 수 없습니다."
            suggested_type = "알 수 없음"
        
        return DocumentValidationResponse(
            is_valid=is_valid,
            confidence=confidence,
            reason=reason,
            suggested_type=suggested_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 타입 검증 실패: {str(e)}")

@router.post("/validate-uploaded-file")
async def validate_uploaded_file(
    file: UploadFile = File(...),
    expected_type: str = Form(...)
):
    """업로드된 파일을 분석하여 선택된 문서 타입과 일치하는지 검증"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")
        
        # 파일 유효성 검사
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        # 파일 크기 확인
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="파일 크기가 너무 큽니다. 최대 10MB까지 지원합니다.")
        
        # 파일 확장자 확인
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        # 임시 파일 생성
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
            
            # 문서 타입 검증
            validation_result = await validate_document_type_internal(extracted_text, expected_type)
            
            return {
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text_length": len(extracted_text),
                "expected_type": expected_type,
                "validation_result": validation_result.dict()
            }
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 검증 실패: {str(e)}")

async def validate_document_type_internal(content: str, expected_type: str) -> DocumentValidationResponse:
    """내부적으로 문서 타입을 검증하는 함수"""
    # if not GOOGLE_API_KEY:
    #     raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다.")
    
    # 문서 타입 검증을 위한 프롬프트 생성
    validation_prompt = f"""
    다음 문서 내용을 분석하여 이것이 "{expected_type}"인지 판단해주세요.
    
    문서 내용:
    {content[:2000]}  # 내용이 너무 길면 앞부분만 사용
    
    다음 기준으로 판단해주세요:
    
    이력서의 경우:
    - 개인 정보 (이름, 연락처, 생년월일 등)
    - 학력 정보
    - 경력 정보 (회사명, 직무, 기간)
    - 기술 스택
    - 자격증
    - 프로젝트 경험
    
    자기소개서의 경우:
    - 지원 동기
    - 성장 과정
    - 지원 직무에 대한 이해
    - 본인의 강점과 약점
    - 입사 후 포부
    
    포트폴리오의 경우:
    - 프로젝트 개요
    - 사용 기술
    - 구현 과정
    - 결과물
    - GitHub 링크 등
    
    응답 형식:
    - 유효성: true/false
    - 신뢰도: 0.0-1.0 (소수점)
    - 판단 이유: 간단한 설명
    - 제안 타입: 실제 문서 타입 (이력서/자기소개서/포트폴리오)
    
    JSON 형태로 응답해주세요.
    """
    
    # Gemini API 호출
    response = await asyncio.to_thread(
        model.generate_content,
        validation_prompt
    )
    
    response_text = response.text.strip()
    
    # JSON 응답 파싱 시도
    try:
        # JSON 부분만 추출
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            json_str = response_text[json_start:json_end]
            import json
            parsed_response = json.loads(json_str)
            
            return DocumentValidationResponse(
                is_valid=parsed_response.get('유효성', False),
                confidence=parsed_response.get('신뢰도', 0.0),
                reason=parsed_response.get('판단 이유', '분석 실패'),
                suggested_type=parsed_response.get('제안 타입', '알 수 없음')
            )
    except (json.JSONDecodeError, KeyError):
        pass
    
    # JSON 파싱 실패 시 텍스트 분석으로 대체
    response_lower = response_text.lower()
    
    # 간단한 키워드 기반 분석
    resume_keywords = ['이력서', 'resume', 'cv', '경력', '학력', '자격증', '프로젝트']
    cover_letter_keywords = ['자기소개서', '자소서', 'cover letter', '지원동기', '성장과정', '포부']
    portfolio_keywords = ['포트폴리오', 'portfolio', '프로젝트', 'github', '구현']
    
    expected_lower = expected_type.lower()
    
    if '이력서' in expected_lower:
        relevant_keywords = resume_keywords
        conflicting_keywords = cover_letter_keywords + portfolio_keywords
    elif '자기소개서' in expected_lower:
        relevant_keywords = cover_letter_keywords
        conflicting_keywords = resume_keywords + portfolio_keywords
    elif '포트폴리오' in expected_lower:
        relevant_keywords = portfolio_keywords
        conflicting_keywords = resume_keywords + cover_letter_keywords
    else:
        relevant_keywords = []
        conflicting_keywords = []
    
    # 키워드 기반 유효성 판단
    has_relevant = any(keyword in response_lower for keyword in relevant_keywords)
    has_conflicting = any(keyword in response_lower for keyword in conflicting_keywords)
    
    if has_conflicting:
        is_valid = False
        confidence = 0.8
        reason = f"문서 내용이 {expected_type}와 맞지 않습니다."
        suggested_type = "알 수 없음"
    elif has_relevant:
        is_valid = True
        confidence = 0.7
        reason = f"문서 내용이 {expected_type}와 일치합니다."
        suggested_type = expected_type
    else:
        is_valid = False
        confidence = 0.6
        reason = f"문서 내용을 분석할 수 없습니다."
        suggested_type = "알 수 없음"
    
    return DocumentValidationResponse(
        is_valid=is_valid,
        confidence=confidence,
        reason=reason,
        suggested_type=suggested_type
    )

@router.get("/health")
async def upload_health_check():
    """업로드 서비스 헬스 체크"""
    return {
        "status": "healthy",
        "gemini_api_configured": bool(GOOGLE_API_KEY),
        "supported_formats": list(ALLOWED_EXTENSIONS.keys()),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }
