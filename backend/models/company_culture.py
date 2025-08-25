from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class CompanyCulture(BaseModel):
    """회사 인재상 모델"""
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="인재상 이름")
    description: str = Field(..., description="인재상 설명")
    is_active: bool = Field(True, description="활성화 여부")
    is_default: bool = Field(False, description="기본 인재상 여부")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "혁신적 사고",
                "description": "새로운 아이디어를 창출하고 문제를 창의적으로 해결하는 능력",
                "is_active": True,
                "is_default": False
            }
        }

class CompanyCultureCreate(BaseModel):
    """인재상 생성 요청 모델"""
    name: str = Field(..., description="인재상 이름")
    description: str = Field(..., description="인재상 설명")

class CompanyCultureUpdate(BaseModel):
    """인재상 수정 요청 모델"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class CompanyCultureResponse(BaseModel):
    """인재상 응답 모델"""
    id: str
    name: str
    description: str
    is_active: bool = True  # 기본값 True로 설정
    is_default: bool = False  # 기본값 False로 설정
    created_at: datetime
    updated_at: datetime

class ApplicantCultureScore(BaseModel):
    """지원자 인재상 점수 모델"""
    culture_id: str = Field(..., description="인재상 ID")
    culture_name: str = Field(..., description="인재상 이름")
    score: float = Field(..., ge=0, le=100, description="점수 (0-100)")
    criteria_scores: dict = Field(..., description="개별 기준별 점수")
    feedback: str = Field("", description="평가 피드백")
    evaluated_at: datetime = Field(default_factory=datetime.now)

class JobPostingCultureRequirement(BaseModel):
    """채용공고 인재상 요구사항 모델"""
    culture_id: str = Field(..., description="인재상 ID")
    culture_name: str = Field(..., description="인재상 이름")
    required_score: float = Field(..., ge=0, le=100, description="요구 최소 점수")
    weight: float = Field(..., ge=0, le=100, description="가중치")
