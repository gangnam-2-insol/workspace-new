from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvaluationWeights(BaseModel):
    """평가 가중치"""
    education_weight: float = Field(description="학력 가중치", ge=0.0, le=1.0)
    experience_weight: float = Field(description="경력 가중치", ge=0.0, le=1.0)
    skills_weight: float = Field(description="기술 가중치", ge=0.0, le=1.0)
    projects_weight: float = Field(description="프로젝트 가중치", ge=0.0, le=1.0)
    growth_weight: float = Field(description="성장 가중치", ge=0.0, le=1.0)
    weight_reasoning: str = Field(description="가중치 적용 이유")

class AnalysisNotes(BaseModel):
    """분석 노트"""
    key_technologies: List[str] = Field(description="핵심 기술 스택")
    project_highlights: List[str] = Field(description="주요 프로젝트")
    performance_metrics: List[str] = Field(description="성과 지표")

class Recommendation(BaseModel):
    """개선 권장사항"""
    priority: str = Field(description="우선순위 (high, medium, low)")
    action: str = Field(description="실행할 액션")
    timeline: str = Field(description="실행 기간")
    method: str = Field(description="구체적 방법")
    expected_impact: str = Field(description="기대 효과")

class ResumeAnalysisResult(BaseModel):
    """OpenAI 기반 이력서 분석 결과 (개선된 버전)"""
    # 가중치 정보
    evaluation_weights: EvaluationWeights = Field(description="평가 가중치 정보")

    # 점수 정보
    overall_score: int = Field(description="종합 점수 (0-100)", ge=0, le=100)
    education_score: int = Field(description="학력 및 전공 점수 (0-100)", ge=0, le=100)
    experience_score: int = Field(description="경력 및 직무 경험 점수 (0-100)", ge=0, le=100)
    skills_score: int = Field(description="보유 기술 및 역량 점수 (0-100)", ge=0, le=100)
    projects_score: int = Field(description="프로젝트 및 성과 점수 (0-100)", ge=0, le=100)
    growth_score: int = Field(description="자기계발 및 성장 점수 (0-100)", ge=0, le=100)

    # 상세 분석 내용 (상황 대응형)
    education_analysis: str = Field(description="학력 및 전공에 대한 구체적 분석")
    experience_analysis: str = Field(description="경력 및 직무 경험에 대한 구체적 분석")
    skills_analysis: str = Field(description="보유 기술 및 역량에 대한 구체적 분석")
    projects_analysis: str = Field(description="프로젝트 및 성과에 대한 구체적 분석")
    growth_analysis: str = Field(description="자기계발 및 성장에 대한 구체적 분석")

    # 분석 노트
    analysis_notes: AnalysisNotes = Field(description="분석 과정에서 참고한 주요 정보")

    # 동적 강점/개선점
    strengths: List[str] = Field(description="주요 강점 리스트 (상황에 따라 개수 조절)")
    improvements: List[str] = Field(description="개선이 필요한 부분 리스트 (상황에 따라 개수 조절)")

    # 종합 피드백
    overall_feedback: str = Field(description="종합적인 피드백")

    # 실행 계획형 권장사항
    recommendations: List[Recommendation] = Field(description="구체적 실행 계획형 개선 권장사항")

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
    weights: Optional[Dict[str, int]] = Field(description="분석 가중치 설정", default=None)

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
