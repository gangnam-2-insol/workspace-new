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
    type: JobType = Field(default=JobType.FULL_TIME, description="고용 형태")
    salary: Optional[str] = Field(None, description="급여 조건")
    experience: Optional[str] = Field(None, description="경력 요구사항")
    education: Optional[str] = Field(None, description="학력 요구사항")
    description: Optional[str] = Field(None, description="직무 설명")
    requirements: Optional[str] = Field(None, description="자격 요건")
    benefits: Optional[str] = Field(None, description="복리후생")
    deadline: Optional[str] = Field(None, description="마감일")
    department: Optional[str] = Field(None, description="구인 부서")
    headcount: Optional[str] = Field(None, description="채용 인원")
    work_type: Optional[str] = Field(None, description="업무 내용")
    work_hours: Optional[str] = Field(None, description="근무 시간")
    contact_email: Optional[str] = Field(None, description="연락처 이메일")

    # 유사성 분석을 위한 추가 필드들
    position: Optional[str] = Field(None, description="채용 직무")
    experience_min_years: Optional[int] = Field(None, description="최소 경력 연차")
    experience_max_years: Optional[int] = Field(None, description="최대 경력 연차")
    experience_level: Optional[str] = Field(None, description="경력 수준: 신입/경력/고급")
    main_duties: Optional[str] = Field(None, description="주요 업무")
    job_keywords: List[str] = Field(default=[], description="직무 관련 키워드")
    industry: Optional[str] = Field(None, description="산업 분야")
    job_category: Optional[str] = Field(None, description="직무 카테고리")

    # 지원자 요구 항목 (MongoDB 컬렉션 구조 기반)
    required_documents: List[RequiredDocumentType] = Field(
        default=[RequiredDocumentType.RESUME],
        description="필수 제출 서류"
    )
    required_skills: List[str] = Field(
        default=[],
        description="필수 기술 스택"
    )
    preferred_skills: List[str] = Field(
        default=[],
        description="우선 기술 스택"
    )
    skill_weights: Dict[str, float] = Field(
        default={},
        description="기술별 가중치"
    )
    required_experience_years: Optional[int] = Field(
        None,
        description="필수 경력 연차"
    )
    require_portfolio_pdf: bool = Field(
        default=False,
        description="포트폴리오 PDF 제출 필수 여부"
    )
    require_github_url: bool = Field(
        default=False,
        description="GitHub URL 제출 필수 여부"
    )
    require_growth_background: bool = Field(
        default=False,
        description="성장 배경 작성 필수 여부"
    )
    require_motivation: bool = Field(
        default=False,
        description="지원 동기 작성 필수 여부"
    )
    require_career_history: bool = Field(
        default=False,
        description="경력 사항 작성 필수 여부"
    )
    max_file_size_mb: int = Field(
        default=50,
        description="최대 파일 크기 (MB)"
    )
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx"],
        description="허용된 파일 형식"
    )

    # 회사 인재상 관련 필드
    culture_requirements: List[Dict[str, Any]] = Field(
        default=[],
        description="요구되는 회사 인재상 목록"
    )
    selected_culture_id: Optional[str] = Field(
        None,
        description="선택된 회사 인재상 ID"
    )

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    type: Optional[JobType] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    deadline: Optional[str] = None
    department: Optional[str] = None
    headcount: Optional[str] = None
    work_type: Optional[str] = None
    work_hours: Optional[str] = None
    contact_email: Optional[str] = None
    required_documents: Optional[List[RequiredDocumentType]] = None
    required_skills: Optional[List[str]] = None
    require_portfolio_pdf: Optional[bool] = None
    require_github_url: Optional[bool] = None
    require_growth_background: Optional[bool] = None
    require_motivation: Optional[bool] = None
    require_career_history: Optional[bool] = None
    max_file_size_mb: Optional[int] = None
    allowed_file_types: Optional[List[str]] = None
    status: Optional[JobStatus] = None

class JobPosting(JobPostingBase):
    id: Optional[str] = Field(None)
    status: JobStatus = Field(default=JobStatus.DRAFT, description="채용공고 상태")
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
                "type": "full-time",
                "salary": "연봉 4,000만원 - 6,000만원",
                "experience": "2년 이상",
                "education": "대졸 이상",
                "description": "React, TypeScript를 활용한 웹 애플리케이션 개발",
                "requirements": "JavaScript, React 실무 경험",
                "benefits": "주말보장, 재택가능, 점심식대 지원",
                "deadline": "2024-12-31",
                "required_documents": ["resume", "cover_letter"],
                "required_skills": ["JavaScript", "React", "TypeScript"],
                "require_portfolio_pdf": True,
                "require_github_url": True,
                "require_growth_background": True,
                "require_motivation": True,
                "require_career_history": True,
                "status": "draft"
            }
        }
