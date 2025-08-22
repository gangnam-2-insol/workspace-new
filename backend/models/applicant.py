from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class ApplicantBase(BaseModel):
    name: str = Field(..., description="지원자 이름")
    email: str = Field(..., description="지원자 이메일")
    phone: Optional[str] = Field(None, description="지원자 전화번호")
    position: str = Field(..., description="지원 직무")
    experience: int = Field(..., description="경력 연차")
    skills: List[str] = Field(default=[], description="기술 스택 목록")

class ApplicantCreate(ApplicantBase):
    # 연결 필드들
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

class Applicant(ApplicantBase):
    id: str = Field(alias="_id", description="지원자 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "email": "hong@example.com",
                "phone": "010-1234-5678",
                "position": "백엔드 개발자",
                "experience": 3,
                "skills": ["Java", "Spring Boot", "MySQL"],
                "resume_id": "507f1f77bcf86cd799439011",
                "cover_letter_id": "507f1f77bcf86cd799439012",
                "portfolio_id": "507f1f77bcf86cd799439013",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
