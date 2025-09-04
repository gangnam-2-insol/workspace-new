from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    EXPIRED = "expired"

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"

class RequiredDocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    PORTFOLIO = "portfolio"

class JobPostingBase(BaseModel):
    title: str = Field(..., description="채용공고 제목")
    company: str = Field(..., description="회사명")
    location: str = Field(..., description="근무지")
    department: Optional[str] = Field(None, description="구인 부서")
    position: Optional[str] = Field(None, description="채용 직무")
    type: JobType = Field(default=JobType.FULL_TIME, description="고용 형태")
    salary: Optional[str] = Field(None, description="급여 조건")
    experience: Optional[str] = Field(None, description="경력 요구사항")
    education: Optional[str] = Field(None, description="학력 요구사항")
    description: Optional[str] = Field(None, description="직무 설명")
    requirements: Optional[str] = Field(None, description="자격 요건")
    required_skills: List[str] = Field(default=[], description="필수 기술 스택")
    preferred_skills: List[str] = Field(default=[], description="우선 기술 스택")
    required_documents: List[RequiredDocumentType] = Field(
        default=[RequiredDocumentType.RESUME],
        description="필수 제출 서류"
    )
    deadline: Optional[str] = Field(None, description="마감일")

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    type: Optional[JobType] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    required_documents: Optional[List[RequiredDocumentType]] = None
    deadline: Optional[str] = None
    status: Optional[JobStatus] = None

class JobPosting(JobPostingBase):
    id: Optional[str] = Field(None)
    status: JobStatus = Field(default=JobStatus.PUBLISHED, description="채용공고 상태")
    applicants: int = Field(default=0, description="지원자 수")
    views: int = Field(default=0, description="조회수")
    bookmarks: int = Field(default=0, description="북마크 수")
    shares: int = Field(default=0, description="공유 수")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "프론트엔드 개발자",
                "company": "테크스타트업",
                "location": "서울특별시 강남구",
                "department": "개발팀",
                "position": "프론트엔드 개발자",
                "type": "full-time",
                "salary": "연봉 4,000만원 - 6,000만원",
                "experience": "2년 이상",
                "education": "대졸 이상",
                "description": "React, TypeScript를 활용한 웹 애플리케이션 개발",
                "requirements": "JavaScript, React 실무 경험",
                "required_skills": ["JavaScript", "React", "TypeScript"],
                "preferred_skills": ["Next.js", "Redux"],
                "required_documents": ["resume", "cover_letter", "portfolio"],
                "deadline": "2024-12-31",
                "status": "draft"
            }
        }
