from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..shared.models import PyObjectId


# 자기소개서 상태
class CoverLetterStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"

# 자기소개서 모델
class CoverLetter(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    applicant_id: str = Field(..., description="지원자 ID")
    content: str = Field(..., description="자기소개서 내용")

    # OCR 추출 필드들
    motivation: Optional[str] = Field(None, description="지원 동기")
    career_goals: Optional[str] = Field(None, description="경력 목표")
    strengths: Optional[str] = Field(None, description="강점 및 역량")
    experience: Optional[str] = Field(None, description="관련 경험")
    achievements: Optional[str] = Field(None, description="주요 성과")
    skills: Optional[str] = Field(None, description="보유 기술")
    projects: Optional[str] = Field(None, description="프로젝트 경험")
    education: Optional[str] = Field(None, description="학력 사항")
    certifications: Optional[str] = Field(None, description="자격증")
    languages: Optional[str] = Field(None, description="언어 능력")
    personal_statement: Optional[str] = Field(None, description="자기소개")
    future_plans: Optional[str] = Field(None, description="향후 계획")

    # 메타데이터
    filename: Optional[str] = Field(None, description="파일명")
    file_size: Optional[int] = Field(None, description="파일 크기")
    extracted_text: Optional[str] = Field(None, description="OCR 추출 텍스트")

    status: CoverLetterStatus = Field(default=CoverLetterStatus.DRAFT, description="상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 자기소개서 생성 모델
class CoverLetterCreate(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    content: str = Field(..., description="자기소개서 내용")

    # OCR 추출 필드들
    motivation: Optional[str] = Field(None, description="지원 동기")
    career_goals: Optional[str] = Field(None, description="경력 목표")
    strengths: Optional[str] = Field(None, description="강점 및 역량")
    experience: Optional[str] = Field(None, description="관련 경험")
    achievements: Optional[str] = Field(None, description="주요 성과")
    skills: Optional[str] = Field(None, description="보유 기술")
    projects: Optional[str] = Field(None, description="프로젝트 경험")
    education: Optional[str] = Field(None, description="학력 사항")
    certifications: Optional[str] = Field(None, description="자격증")
    languages: Optional[str] = Field(None, description="언어 능력")
    personal_statement: Optional[str] = Field(None, description="자기소개")
    future_plans: Optional[str] = Field(None, description="향후 계획")

    # 메타데이터
    filename: Optional[str] = Field(None, description="파일명")
    file_size: Optional[int] = Field(None, description="파일 크기")
    extracted_text: Optional[str] = Field(None, description="OCR 추출 텍스트")

# 자기소개서 수정 모델
class CoverLetterUpdate(BaseModel):
    content: Optional[str] = Field(None, description="자기소개서 내용")
    status: Optional[CoverLetterStatus] = Field(None, description="상태")
