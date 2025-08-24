from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
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
    status: CoverLetterStatus = Field(default=CoverLetterStatus.DRAFT, description="상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 자기소개서 생성 모델
class CoverLetterCreate(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    content: str = Field(..., description="자기소개서 내용")

# 자기소개서 수정 모델
class CoverLetterUpdate(BaseModel):
    content: Optional[str] = Field(None, description="자기소개서 내용")
    status: Optional[CoverLetterStatus] = Field(None, description="상태")
