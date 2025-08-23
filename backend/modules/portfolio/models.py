from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from ..shared.models import PyObjectId

# 포트폴리오 상태
class PortfolioStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# 포트폴리오 모델
class Portfolio(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    applicant_id: str = Field(..., description="지원자 ID")
    title: str = Field(..., description="포트폴리오 제목")
    description: str = Field(..., description="포트폴리오 설명")
    github_url: Optional[str] = Field(None, description="GitHub URL")
    live_url: Optional[str] = Field(None, description="라이브 URL")
    technologies: List[str] = Field(default=[], description="사용 기술")
    status: PortfolioStatus = Field(default=PortfolioStatus.DRAFT, description="상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 포트폴리오 생성 모델
class PortfolioCreate(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    title: str = Field(..., description="포트폴리오 제목")
    description: str = Field(..., description="포트폴리오 설명")
    github_url: Optional[str] = Field(None, description="GitHub URL")
    live_url: Optional[str] = Field(None, description="라이브 URL")
    technologies: List[str] = Field(default=[], description="사용 기술")

# 포트폴리오 수정 모델
class PortfolioUpdate(BaseModel):
    title: Optional[str] = Field(None, description="포트폴리오 제목")
    description: Optional[str] = Field(None, description="포트폴리오 설명")
    github_url: Optional[str] = Field(None, description="GitHub URL")
    live_url: Optional[str] = Field(None, description="라이브 URL")
    technologies: Optional[List[str]] = Field(None, description="사용 기술")
    status: Optional[PortfolioStatus] = Field(None, description="상태")
