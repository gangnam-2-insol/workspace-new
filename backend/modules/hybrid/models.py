from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from ..shared.models import DocumentBase, PyObjectId

# 하이브리드 분석 타입
class HybridAnalysisType(str, Enum):
    COMPREHENSIVE = "comprehensive"  # 종합 분석
    COMPARATIVE = "comparative"      # 비교 분석
    INTEGRATED = "integrated"        # 통합 분석
    CROSS_REFERENCE = "cross_reference"  # 교차 참조

# 통합 문서 타입
class IntegratedDocumentType(str, Enum):
    RESUME_ONLY = "resume_only"
    COVER_LETTER_ONLY = "cover_letter_only"
    PORTFOLIO_ONLY = "portfolio_only"
    RESUME_COVER_LETTER = "resume_cover_letter"
    RESUME_PORTFOLIO = "resume_portfolio"
    COVER_LETTER_PORTFOLIO = "cover_letter_portfolio"
    ALL_DOCUMENTS = "all_documents"

# 통합 분석 결과 모델
class HybridAnalysis(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    applicant_id: str = Field(..., description="지원자 ID")
    analysis_type: HybridAnalysisType = Field(..., description="분석 타입")
    integrated_document_type: IntegratedDocumentType = Field(..., description="통합 문서 타입")
    
    # 문서 ID들
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")
    
    # 종합 분석 점수
    overall_score: float = Field(..., description="종합 점수 (0-100)")
    consistency_score: float = Field(..., description="일관성 점수 (0-100)")
    completeness_score: float = Field(..., description="완성도 점수 (0-100)")
    coherence_score: float = Field(..., description="논리성 점수 (0-100)")
    
    # 분석 결과
    summary: str = Field(..., description="종합 분석 요약")
    strengths: List[str] = Field(default=[], description="종합 강점")
    weaknesses: List[str] = Field(default=[], description="종합 개선점")
    recommendations: List[str] = Field(default=[], description="종합 권장사항")
    
    # 문서별 분석 결과
    resume_analysis: Optional[Dict[str, Any]] = Field(default=None, description="이력서 분석 결과")
    cover_letter_analysis: Optional[Dict[str, Any]] = Field(default=None, description="자기소개서 분석 결과")
    portfolio_analysis: Optional[Dict[str, Any]] = Field(default=None, description="포트폴리오 분석 결과")
    
    # 교차 참조 분석
    cross_references: Dict[str, Any] = Field(default={}, description="교차 참조 분석")
    contradictions: List[str] = Field(default=[], description="모순점 목록")
    reinforcements: List[str] = Field(default=[], description="강화점 목록")
    
    # 메타데이터
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="분석 일시")
    model_used: Optional[str] = Field(None, description="사용된 AI 모델")
    confidence: float = Field(default=0.0, description="신뢰도 (0-1)")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 하이브리드 생성 모델
class HybridCreate(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    analysis_type: HybridAnalysisType = Field(default=HybridAnalysisType.COMPREHENSIVE, description="분석 타입")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")

# 하이브리드 문서 모델
class HybridDocument(HybridCreate):
    id: str = Field(alias="_id", description="하이브리드 분석 ID")
    analysis_results: Optional[List[HybridAnalysis]] = Field(default=[], description="분석 결과 목록")
    status: str = Field(default="active", description="상태")
    version: int = Field(default=1, description="버전")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")
    
    class Config:
        populate_by_name = True

# 하이브리드 업데이트 모델
class HybridUpdate(BaseModel):
    analysis_type: Optional[HybridAnalysisType] = Field(None, description="분석 타입")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    status: Optional[str] = Field(None, description="상태")

# 하이브리드 검색 요청 모델
class HybridSearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    analysis_type: Optional[HybridAnalysisType] = Field(None, description="분석 타입")
    integrated_document_type: Optional[IntegratedDocumentType] = Field(None, description="통합 문서 타입")
    min_score: Optional[float] = Field(None, description="최소 점수")
    limit: int = Field(default=10, description="검색 결과 수")

# 하이브리드 비교 요청 모델
class HybridComparisonRequest(BaseModel):
    hybrid_ids: List[str] = Field(..., description="비교할 하이브리드 분석 ID 목록")
    comparison_type: str = Field(default="overall", description="비교 유형 (overall/consistency/completeness)")

# 하이브리드 통계 모델
class HybridStatistics(BaseModel):
    total_analyses: int = Field(..., description="총 분석 수")
    average_overall_score: float = Field(..., description="평균 종합 점수")
    analysis_type_distribution: Dict[str, int] = Field(default={}, description="분석 타입 분포")
    document_type_distribution: Dict[str, int] = Field(default={}, description="문서 타입 분포")
    score_distribution: Dict[str, int] = Field(default={}, description="점수 분포")

# 교차 참조 분석 모델
class CrossReferenceAnalysis(BaseModel):
    field_name: str = Field(..., description="필드명")
    resume_value: Optional[str] = Field(None, description="이력서 값")
    cover_letter_value: Optional[str] = Field(None, description="자기소개서 값")
    portfolio_value: Optional[str] = Field(None, description="포트폴리오 값")
    consistency_score: float = Field(..., description="일관성 점수 (0-100)")
    notes: Optional[str] = Field(None, description="참고사항")

# 통합 평가 모델
class IntegratedEvaluation(BaseModel):
    technical_competency: float = Field(default=0.0, description="기술 역량 (0-100)")
    communication_skills: float = Field(default=0.0, description="의사소통 능력 (0-100)")
    problem_solving: float = Field(default=0.0, description="문제 해결 능력 (0-100)")
    teamwork: float = Field(default=0.0, description="팀워크 (0-100)")
    leadership: float = Field(default=0.0, description="리더십 (0-100)")
    adaptability: float = Field(default=0.0, description="적응력 (0-100)")
    overall_fit: float = Field(default=0.0, description="전체 적합도 (0-100)")
    evaluation_notes: List[str] = Field(default=[], description="평가 노트")
