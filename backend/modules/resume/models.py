from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from ..shared.models import PyObjectId

# 이력서 상태
class ResumeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

# 이력서 모델
class Resume(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="지원자 이름")
    position: str = Field(..., description="지원 직무")
    department: Optional[str] = Field("", description="부서")
    experience: str = Field(..., description="경력")
    skills: str = Field(..., description="기술 스택")
    growthBackground: Optional[str] = Field("", description="성장 배경")
    motivation: Optional[str] = Field("", description="지원 동기")
    careerHistory: Optional[str] = Field("", description="경력 사항")
    analysisScore: int = Field(default=0, description="분석 점수")
    analysisResult: str = Field(default="", description="분석 결과")
    status: ResumeStatus = Field(default=ResumeStatus.PENDING, description="상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 이력서 생성 모델
class ResumeCreate(BaseModel):
    name: str = Field(..., description="지원자 이름")
    position: str = Field(..., description="지원 직무")
    department: Optional[str] = Field("", description="부서")
    experience: str = Field(..., description="경력")
    skills: str = Field(..., description="기술 스택")
    growthBackground: Optional[str] = Field("", description="성장 배경")
    motivation: Optional[str] = Field("", description="지원 동기")
    careerHistory: Optional[str] = Field("", description="경력 사항")

# 이력서 수정 모델
class ResumeUpdate(BaseModel):
    name: Optional[str] = Field(None, description="지원자 이름")
    position: Optional[str] = Field(None, description="지원 직무")
    department: Optional[str] = Field(None, description="부서")
    experience: Optional[str] = Field(None, description="경력")
    skills: Optional[str] = Field(None, description="기술 스택")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, description="분석 점수")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[ResumeStatus] = Field(None, description="상태")

# 이력서 검색 모델
class ResumeSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="검색 쿼리")
    position: Optional[str] = Field(None, description="직무")
    department: Optional[str] = Field(None, description="부서")
    status: Optional[ResumeStatus] = Field(None, description="상태")
    min_score: Optional[int] = Field(None, description="최소 점수")
    max_score: Optional[int] = Field(None, description="최대 점수")
    limit: int = Field(default=10, description="검색 결과 수")
    skip: int = Field(default=0, description="건너뛸 결과 수")

# 이력서 분석 요청 모델
class ResumeAnalysisRequest(BaseModel):
    resume_id: str = Field(..., description="이력서 ID")
    analysis_type: Optional[str] = Field(default="comprehensive", description="분석 타입")

# 이력서 분석 결과 모델
class ResumeAnalysisResult(BaseModel):
    resume_id: str = Field(..., description="이력서 ID")
    overall_score: float = Field(..., description="종합 점수")
    skill_analysis: Dict[str, Any] = Field(default_factory=dict, description="기술 분석")
    experience_analysis: Dict[str, Any] = Field(default_factory=dict, description="경력 분석")
    motivation_analysis: Dict[str, Any] = Field(default_factory=dict, description="동기 분석")
    recommendations: List[str] = Field(default_factory=list, description="권장사항")
    strengths: List[str] = Field(default_factory=list, description="강점")
    weaknesses: List[str] = Field(default_factory=list, description="약점")
