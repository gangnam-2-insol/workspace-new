from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class RankingCategory(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "coverLetter"
    PORTFOLIO = "portfolio"
    TOTAL = "total"

class ApplicantRankingBase(BaseModel):
    category: RankingCategory = Field(..., description="랭킹 카테고리")
    applicant_id: str = Field(..., description="지원자 ID")
    name: str = Field(..., description="지원자 이름")
    score: float = Field(..., description="점수")
    rank: int = Field(..., description="순위")

class ApplicantRankingCreate(ApplicantRankingBase):
    pass

class ApplicantRanking(ApplicantRankingBase):
    id: str = Field(alias="_id", description="랭킹 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "category": "resume",
                "applicant_id": "507f1f77bcf86cd799439011",
                "name": "홍길동",
                "score": 85.5,
                "rank": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
