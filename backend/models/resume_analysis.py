from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeAnalysisResult(BaseModel):
    """OpenAI 기반 이력서 분석 결과"""
    overall_score: int = Field(description="종합 점수 (0-100)", ge=0, le=100)
    education_score: int = Field(description="학력 및 전공 점수 (0-100)", ge=0, le=100)
    experience_score: int = Field(description="경력 및 직무 경험 점수 (0-100)", ge=0, le=100)
    skills_score: int = Field(description="보유 기술 및 역량 점수 (0-100)", ge=0, le=100)
    projects_score: int = Field(description="프로젝트 및 성과 점수 (0-100)", ge=0, le=100)
    
    # 상세 분석 내용
    education_analysis: str = Field(description="학력 및 전공에 대한 상세 분석")
    experience_analysis: str = Field(description="경력 및 직무 경험에 대한 상세 분석")
    skills_analysis: str = Field(description="보유 기술 및 역량에 대한 상세 분석")
    projects_analysis: str = Field(description="프로젝트 및 성과에 대한 상세 분석")
    
    # 종합 피드백
    strengths: List[str] = Field(description="주요 강점 리스트")
    improvements: List[str] = Field(description="개선이 필요한 부분 리스트")
    overall_feedback: str = Field(description="종합적인 피드백")
    recommendations: List[str] = Field(description="구체적인 개선 권장사항")

class HuggingFaceAnalysisResult(BaseModel):
    """HuggingFace 기반 확장 이력서 분석 결과"""
    # 기본 4개 항목
    overall_score: int = Field(description="종합 점수 (0-100)", ge=0, le=100)
    education_score: int = Field(description="학력 및 전공 점수 (0-100)", ge=0, le=100)
    experience_score: int = Field(description="경력 및 직무 경험 점수 (0-100)", ge=0, le=100)
    skills_score: int = Field(description="보유 기술 및 역량 점수 (0-100)", ge=0, le=100)
    projects_score: int = Field(description="프로젝트 및 성과 점수 (0-100)", ge=0, le=100)
    
    # 추가 분석 결과
    grammar_score: int = Field(description="문법 및 표현 점수 (0-100)", ge=0, le=100)
    grammar_analysis: str = Field(description="문법 및 표현 분석")
    job_matching_score: int = Field(description="직무 적합성 점수 (0-100)", ge=0, le=100)
    job_matching_analysis: str = Field(description="직무 적합성 분석")
    
    # 상세 분석 및 피드백
    education_analysis: str = Field(description="학력 및 전공에 대한 상세 분석")
    experience_analysis: str = Field(description="경력 및 직무 경험에 대한 상세 분석")
    skills_analysis: str = Field(description="보유 기술 및 역량에 대한 상세 분석")
    projects_analysis: str = Field(description="프로젝트 및 성과에 대한 상세 분석")
    
    strengths: List[str] = Field(description="주요 강점 리스트")
    improvements: List[str] = Field(description="개선이 필요한 부분 리스트")
    overall_feedback: str = Field(description="종합적인 피드백")
    recommendations: List[str] = Field(description="구체적인 개선 권장사항")

class AnalysisState(BaseModel):
    """분석 상태 관리"""
    applicant_data: Dict[str, Any] = Field(description="지원자 데이터")
    current_step: str = Field(description="현재 분석 단계")
    education_analysis: Optional[Dict[str, Any]] = Field(description="학력 분석 결과")
    experience_analysis: Optional[Dict[str, Any]] = Field(description="경력 분석 결과")
    skills_analysis: Optional[Dict[str, Any]] = Field(description="기술 분석 결과")
    projects_analysis: Optional[Dict[str, Any]] = Field(description="프로젝트 분석 결과")
    growth_analysis: Optional[Dict[str, Any]] = Field(description="성장 분석 결과")
    overall_score: Optional[int] = Field(description="종합 점수")
    strengths: Optional[List[str]] = Field(description="강점 리스트")
    improvements: Optional[List[str]] = Field(description="개선점 리스트")
    recommendations: Optional[List[str]] = Field(description="권장사항 리스트")
    final_analysis: Optional[Dict[str, Any]] = Field(description="최종 분석 결과")

class ResumeAnalysisRequest(BaseModel):
    """이력서 분석 요청"""
    applicant_id: str = Field(description="지원자 ID")
    analysis_type: str = Field(description="분석 타입 (openai, huggingface, workflow)", default="openai")
    force_reanalysis: bool = Field(description="강제 재분석 여부", default=False)

class BatchAnalysisRequest(BaseModel):
    """일괄 분석 요청"""
    applicant_ids: List[str] = Field(description="지원자 ID 리스트")
    analysis_type: str = Field(description="분석 타입", default="openai")

class ResumeAnalysisResponse(BaseModel):
    """이력서 분석 응답"""
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지")
    data: Optional[Dict[str, Any]] = Field(description="분석 결과 데이터")
    analysis_id: Optional[str] = Field(description="분석 ID")
    created_at: Optional[datetime] = Field(description="생성 시간")
    processing_time: Optional[float] = Field(description="처리 시간 (초)")

class AnalysisStatusResponse(BaseModel):
    """분석 상태 응답"""
    success: bool = Field(description="성공 여부")
    message: str = Field(description="응답 메시지")
    data: Dict[str, Any] = Field(description="상태 데이터")
    total_applicants: int = Field(description="전체 지원자 수")
    analyzed_count: int = Field(description="분석 완료 수")
    pending_count: int = Field(description="대기 중인 수")
    failed_count: int = Field(description="실패한 수")
    progress_percentage: float = Field(description="진행률 (%)")
