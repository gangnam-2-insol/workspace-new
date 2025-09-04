from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from ..shared.models import PyObjectId


# 채용 타입
class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"

# 채용공고 상태
class JobStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    EXPIRED = "expired"

# 필수 제출 서류 타입
class RequiredDocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    PORTFOLIO = "portfolio"
    CERTIFICATE = "certificate"
    REFERENCE = "reference"

# 채용공고 기본 모델
class JobPostingBase(BaseModel):
    # 기본 정보
    title: str = Field(..., description="채용공고 제목")
    company: str = Field(..., description="회사명")
    location: str = Field(..., description="근무지")
    type: JobType = Field(..., description="고용 형태")

    # 급여 및 조건
    salary: Optional[str] = Field(None, description="급여 조건")
    experience: Optional[str] = Field(None, description="경력 요구사항")
    education: Optional[str] = Field(None, description="학력 요구사항")

    # 상세 정보
    description: Optional[str] = Field(None, description="직무 설명")
    requirements: Optional[str] = Field(None, description="자격 요건")
    benefits: Optional[str] = Field(None, description="복리후생")
    deadline: Optional[str] = Field(None, description="마감일")

    # 추가 정보
    department: Optional[str] = Field(None, description="구인 부서")
    headcount: Optional[str] = Field(None, description="채용 인원")
    work_type: Optional[str] = Field(None, description="업무 내용")
    work_hours: Optional[str] = Field(None, description="근무 시간")
    contact_email: Optional[str] = Field(None, description="연락처 이메일")

    # 분석용 필드
    position: Optional[str] = Field(None, description="채용 직무")
    experience_min_years: Optional[int] = Field(None, description="최소 경력 연차")
    experience_max_years: Optional[int] = Field(None, description="최대 경력 연차")
    experience_level: Optional[str] = Field(None, description="경력 수준")
    main_duties: Optional[str] = Field(None, description="주요 업무")

    # 주요업무 세분화 필드들
    core_responsibilities: Optional[str] = Field(None, description="핵심 담당업무")
    daily_tasks: Optional[str] = Field(None, description="일상 업무")
    project_tasks: Optional[str] = Field(None, description="프로젝트 업무")
    collaboration_tasks: Optional[str] = Field(None, description="협업 업무")
    technical_tasks: Optional[str] = Field(None, description="기술적 업무")
    management_tasks: Optional[str] = Field(None, description="관리 업무")

    job_keywords: List[str] = Field(default=[], description="직무 관련 키워드")
    industry: Optional[str] = Field(None, description="산업 분야")
    job_category: Optional[str] = Field(None, description="직무 카테고리")

    # 지원자 요구 항목
    required_documents: List[RequiredDocumentType] = Field(default=[], description="필수 제출 서류")
    required_skills: List[str] = Field(default=[], description="필수 기술 스택")
    preferred_skills: List[str] = Field(default=[], description="우선 기술 스택")
    skill_weights: Dict[str, float] = Field(default={}, description="기술별 가중치")
    require_portfolio_pdf: bool = Field(default=False, description="포트폴리오 PDF 제출 필수 여부")
    require_github_url: bool = Field(default=False, description="GitHub URL 제출 필수 여부")
    require_growth_background: bool = Field(default=False, description="성장 배경 작성 필수 여부")
    require_motivation: bool = Field(default=False, description="지원 동기 작성 필수 여부")
    require_career_history: bool = Field(default=False, description="경력 사항 작성 필수 여부")
    max_file_size_mb: int = Field(default=10, description="최대 파일 크기 (MB)")
    allowed_file_types: List[str] = Field(default=["pdf", "doc", "docx"], description="허용된 파일 형식")

# 채용공고 모델 (확장)
class JobPosting(JobPostingBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    status: JobStatus = Field(default=JobStatus.PUBLISHED, description="채용공고 상태")
    applicants: int = Field(default=0, description="지원자 수")
    views: int = Field(default=0, description="조회수")
    bookmarks: int = Field(default=0, description="북마크 수")
    shares: int = Field(default=0, description="공유 수")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# 채용공고 생성 모델
class JobPostingCreate(JobPostingBase):
    pass

# 채용공고 수정 모델
class JobPostingUpdate(BaseModel):
    title: Optional[str] = Field(None, description="채용공고 제목")
    company: Optional[str] = Field(None, description="회사명")
    location: Optional[str] = Field(None, description="근무지")
    type: Optional[JobType] = Field(None, description="고용 형태")
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
    position: Optional[str] = Field(None, description="채용 직무")
    experience_min_years: Optional[int] = Field(None, description="최소 경력 연차")
    experience_max_years: Optional[int] = Field(None, description="최대 경력 연차")
    experience_level: Optional[str] = Field(None, description="경력 수준")
    main_duties: Optional[str] = Field(None, description="주요 업무")

    # 주요업무 세분화 필드들
    core_responsibilities: Optional[str] = Field(None, description="핵심 담당업무")
    daily_tasks: Optional[str] = Field(None, description="일상 업무")
    project_tasks: Optional[str] = Field(None, description="프로젝트 업무")
    collaboration_tasks: Optional[str] = Field(None, description="협업 업무")
    technical_tasks: Optional[str] = Field(None, description="기술적 업무")
    management_tasks: Optional[str] = Field(None, description="관리 업무")

    job_keywords: Optional[List[str]] = Field(None, description="직무 관련 키워드")
    industry: Optional[str] = Field(None, description="산업 분야")
    job_category: Optional[str] = Field(None, description="직무 카테고리")
    required_documents: Optional[List[RequiredDocumentType]] = Field(None, description="필수 제출 서류")
    required_skills: Optional[List[str]] = Field(None, description="필수 기술 스택")
    preferred_skills: Optional[List[str]] = Field(None, description="우선 기술 스택")
    skill_weights: Optional[Dict[str, float]] = Field(None, description="기술별 가중치")
    require_portfolio_pdf: Optional[bool] = Field(None, description="포트폴리오 PDF 제출 필수 여부")
    require_github_url: Optional[bool] = Field(None, description="GitHub URL 제출 필수 여부")
    require_growth_background: Optional[bool] = Field(None, description="성장 배경 작성 필수 여부")
    require_motivation: Optional[bool] = Field(None, description="지원 동기 작성 필수 여부")
    require_career_history: Optional[bool] = Field(None, description="경력 사항 작성 필수 여부")
    max_file_size_mb: Optional[int] = Field(None, description="최대 파일 크기 (MB)")
    allowed_file_types: Optional[List[str]] = Field(None, description="허용된 파일 형식")
    status: Optional[JobStatus] = Field(None, description="채용공고 상태")

# 채용공고 검색 모델
class JobPostingSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="검색 쿼리")
    company: Optional[str] = Field(None, description="회사명")
    location: Optional[str] = Field(None, description="근무지")
    type: Optional[JobType] = Field(None, description="고용 형태")
    status: Optional[JobStatus] = Field(None, description="상태")
    required_skills: Optional[List[str]] = Field(None, description="필수 기술")
    industry: Optional[str] = Field(None, description="산업 분야")
    min_experience: Optional[int] = Field(None, description="최소 경력")
    max_experience: Optional[int] = Field(None, description="최대 경력")
    limit: int = Field(default=10, description="검색 결과 수")
    skip: int = Field(default=0, description="건너뛸 결과 수")

# 채용공고 통계 모델
class JobPostingStatistics(BaseModel):
    total_jobs: int = Field(..., description="총 채용공고 수")
    published_jobs: int = Field(..., description="발행된 채용공고 수")
    draft_jobs: int = Field(..., description="초안 채용공고 수")
    closed_jobs: int = Field(..., description="마감된 채용공고 수")
    total_applicants: int = Field(..., description="총 지원자 수")
    total_views: int = Field(..., description="총 조회수")
    average_applicants_per_job: float = Field(..., description="채용공고당 평균 지원자 수")
    job_type_distribution: Dict[str, int] = Field(default={}, description="고용 형태별 분포")
    industry_distribution: Dict[str, int] = Field(default={}, description="산업별 분포")
    top_companies: List[Dict[str, Any]] = Field(default=[], description="상위 회사")

# AI 기반 채용공고 생성 요청 모델
class AIJobPostingRequest(BaseModel):
    description: str = Field(..., description="채용하고자 하는 직무에 대한 설명")
    company: Optional[str] = Field(None, description="회사명")
    location: Optional[str] = Field(None, description="근무지")
    type: Optional[JobType] = Field(None, description="고용 형태")
    additional_requirements: Optional[str] = Field(None, description="추가 요구사항")

# 이미지 기반 채용공고 생성 요청 모델
class ImageJobPostingRequest(BaseModel):
    image_file: str = Field(..., description="이미지 파일 (base64 인코딩)")
    company: Optional[str] = Field(None, description="회사명")
    additional_info: Optional[str] = Field(None, description="추가 정보")

# LangGraph 기반 채용공고 생성 요청 모델
class LangGraphJobPostingRequest(BaseModel):
    user_input: str = Field(..., description="사용자 자연어 입력")
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[Dict[str, Any]] = Field(None, description="추가 컨텍스트")

# 채용공고 템플릿 모델
class JobPostingTemplate(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="템플릿 이름")
    description: str = Field(..., description="템플릿 설명")
    category: str = Field(..., description="템플릿 카테고리")
    template_data: JobPostingBase = Field(..., description="템플릿 데이터")
    is_public: bool = Field(default=True, description="공개 여부")
    created_by: Optional[str] = Field(None, description="생성자")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
