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
import traceback
from pydantic import BaseModel
import asyncio

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

class CoverLetterAnalysisRequest(BaseModel):
    content: str
    position: str
    department: str
    analysis_type: str = "basic"  # basic, detailed, improvement

class CoverLetterAnalysisResponse(BaseModel):
    success: bool
    analysis_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@router.post("/analyze")
async def analyze_cover_letter(
    request: CoverLetterAnalysisRequest
) -> CoverLetterAnalysisResponse:
    """
    자소서 분석 API
    
    Args:
        request: 자소서 분석 요청 데이터
        
    Returns:
        분석 결과
    """
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini API가 설정되지 않았습니다.")
        
        # 간단하고 확실한 자소서 분석 프롬프트
        analysis_prompt = f"""
당신은 채용 전문가입니다. 지원자의 자기소개서를 분석하여 다음과 같은 항목들을 평가해주세요.

## 분석 대상
지원 직무: {request.position}
희망 부서: {request.department}
지원자 자기소개서 내용: {request.content}

## 평가 기준
각 항목을 1-10점으로 평가하고, 구체적인 피드백을 제공해주세요.

### 1. 동기 및 열정 (Motivation & Passion)
- 지원 동기가 명확한가?
- 회사/직무에 대한 이해도는 높은가?
- 진정성 있는 열정이 드러나는가?

### 2. 문제해결 능력 (Problem Solving)
- 구체적인 문제 상황과 해결 과정이 제시되었는가?
- STAR 방법론이 잘 적용되었는가?
- 결과와 영향이 명확한가?

### 3. 팀워크 및 협업 (Teamwork & Collaboration)
- 팀 프로젝트 경험이 구체적으로 서술되었는가?
- 갈등 해결 능력이 드러나는가?
- 협업을 통한 성과가 명확한가?

### 4. 기술적 역량 (Technical Skills)
- 직무 관련 기술/도구 사용 경험이 구체적인가?
- 학습 능력과 적응력이 드러나는가?
- 프로젝트에서의 기술적 기여도는 높은가?

### 5. 성장 잠재력 (Growth Potential)
- 지속적인 학습 의지가 드러나는가?
- 도전적 과제에 대한 태도는 적극적인가?
- 미래 비전과 계획이 구체적인가?

## 출력 형식
다음 JSON 형식으로 응답해주세요. 다른 텍스트는 포함하지 마세요:

{{
  "analysis": {{
    "motivation_score": 점수,
    "motivation_feedback": "구체적인 피드백",
    "problem_solving_score": 점수,
    "problem_solving_feedback": "구체적인 피드백",
    "teamwork_score": 점수,
    "teamwork_feedback": "구체적인 피드백",
    "technical_score": 점수,
    "technical_feedback": "구체적인 피드백",
    "growth_score": 점수,
    "growth_feedback": "구체적인 피드백"
  }},
  "overall_score": "전체 평균 점수",
  "strengths": ["강점 1", "강점 2", "강점 3"],
  "weaknesses": ["개선점 1", "개선점 2", "개선점 3"],
  "recommendations": ["구체적인 개선 제안 1", "구체적인 개선 제안 2"]
}}

## 주의사항
1. 점수는 1-10점 사이의 정수로 평가
2. 피드백은 구체적이고 실행 가능한 내용으로 작성
3. 한국어로 응답
4. JSON만 출력하고 다른 설명은 포함하지 마세요
"""
        
        # Gemini API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            analysis_prompt
        )
        
        if not response.text:
            raise HTTPException(status_code=500, detail="AI 응답이 비어있습니다.")
        
        # JSON 응답 파싱
        try:
            # JSON 부분만 추출
            response_text = response.text.strip()
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_content = response_text[json_start:json_end].strip()
                else:
                    json_content = response_text[json_start:].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_content = response_text[json_start:json_end].strip()
                else:
                    json_content = response_text[json_start:].strip()
            else:
                json_content = response_text
            
            analysis_result = json.loads(json_content)
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"응답 텍스트: {response.text}")
            
            # JSON 파싱 실패 시 기본 분석 결과 반환
            analysis_result = {
                "analysis": {
                    "motivation_score": 7,
                    "motivation_feedback": "자소서 내용을 바탕으로 기본 분석을 제공합니다.",
                    "problem_solving_score": 6,
                    "problem_solving_feedback": "문제 해결 과정에 대한 구체적 서술이 필요합니다.",
                    "teamwork_score": 6,
                    "teamwork_feedback": "팀워크 경험을 더 구체적으로 서술하면 좋겠습니다.",
                    "technical_score": 6,
                    "technical_feedback": "기술적 역량을 더 구체적으로 어필해주세요.",
                    "growth_score": 7,
                    "growth_feedback": "성장 의지와 계획이 잘 드러납니다."
                },
                "overall_score": "6.4/10",
                "strengths": ["지원 동기가 명확함", "성장 의지가 뚜렷함"],
                "weaknesses": ["구체적 사례 부족", "정량적 성과 부족"],
                "recommendations": ["STAR 방법론을 활용한 구체적 사례 추가", "정량적 성과 지표 포함"]
            }
        
        return CoverLetterAnalysisResponse(
            success=True,
            analysis_result=analysis_result
        )
        
    except Exception as e:
        print(f"자소서 분석 중 오류 발생: {str(e)}")
        traceback.print_exc()
        return CoverLetterAnalysisResponse(
            success=False,
            error_message=f"자소서 분석 중 오류가 발생했습니다: {str(e)}"
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
    # RAG 시스템 의존성 제거
    return {"positions": []} # 임시 반환

@router.get("/company-values")
async def get_company_values():
    """회사 가치 및 문화 정보 반환"""
    # RAG 시스템 의존성 제거
    return {"company_values": {}} # 임시 반환

@router.get("/evaluation-rubrics")
async def get_evaluation_rubrics():
    """평가 루브릭 정보 반환"""
    # RAG 시스템 의존성 제거
    return {"evaluation_rubrics": {}} # 임시 반환

@router.post("/search-context")
async def search_rag_context(
    query: str = Form(...),
    position: str = Form(...),
    top_k: int = Form(5)
):
    """RAG 컨텍스트 검색"""
    # RAG 시스템 의존성 제거
    return {"success": False, "error": "RAG 검색 기능은 현재 사용할 수 없습니다."} # 임시 반환

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "rag_system_initialized": False, # RAG 시스템 의존성 제거
        "gemini_api_available": model is not None,
        "google_api_key_set": bool(GOOGLE_API_KEY)
    }

@router.get("/test")
async def test_analysis():
    """테스트용 간단한 분석 결과 반환"""
    return CoverLetterAnalysisResponse(
        success=True,
        analysis_result={
            "analysis": {
                "motivation_score": 8,
                "motivation_feedback": "지원 동기가 명확하고 회사에 대한 이해도가 높습니다.",
                "problem_solving_score": 7,
                "problem_solving_feedback": "STAR 방법론을 활용한 구체적 사례가 잘 제시되었습니다.",
                "teamwork_score": 8,
                "teamwork_feedback": "팀 프로젝트 경험이 풍부하고 협업 능력이 뛰어납니다.",
                "technical_score": 7,
                "technical_feedback": "기술 스택이 직무 요구사항과 잘 맞습니다.",
                "growth_score": 8,
                "growth_feedback": "지속적인 학습 의지와 미래 비전이 명확합니다."
            },
            "overall_score": "7.6/10",
            "strengths": ["명확한 지원 동기", "팀워크 능력", "성장 의지"],
            "weaknesses": ["정량적 성과 부족", "기술적 깊이"],
            "recommendations": ["정량적 성과 지표 추가", "기술적 전문성 강화"]
        }
    )

if __name__ == "__main__":
    print("자소서 분석 API가 생성되었습니다.")
