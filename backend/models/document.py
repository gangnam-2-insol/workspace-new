from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

# 포트폴리오 아이템 타입
class PortfolioItemType(str, Enum):
    PROJECT = "project"
    DOC = "doc"
    SLIDE = "slide"
    CODE = "code"
    URL = "url"
    IMAGE = "image"
    VIDEO = "video"

# 아티팩트 타입
class ArtifactKind(str, Enum):
    FILE = "file"
    URL = "url"
    REPO = "repo"

# 아티팩트 모델
class Artifact(BaseModel):
    kind: ArtifactKind = Field(..., description="아티팩트 종류")
    file_id: Optional[str] = Field(None, description="파일 ID (GridFS)")
    url: Optional[str] = Field(None, description="URL")
    filename: str = Field(..., description="파일명")
    mime: Optional[str] = Field(None, description="MIME 타입")
    size: Optional[int] = Field(None, description="파일 크기")
    hash: Optional[str] = Field(None, description="파일 해시")
    preview_image: Optional[str] = Field(None, description="미리보기 이미지 URL")

# 포트폴리오 아이템 모델
class PortfolioItem(BaseModel):
    item_id: str = Field(..., description="아이템 ID")
    title: str = Field(..., description="아이템 제목")
    type: PortfolioItemType = Field(..., description="아이템 타입")
    artifacts: List[Artifact] = Field(default=[], description="아티팩트 목록")

# 기본 정보 모델
class BasicInfo(BaseModel):
    emails: List[str] = Field(default=[], description="이메일 목록")
    phones: List[str] = Field(default=[], description="전화번호 목록")
    names: List[str] = Field(default=[], description="이름 목록")
    urls: List[str] = Field(default=[], description="URL 목록")

# 파일 메타데이터 모델
class FileMetadata(BaseModel):
    filename: str = Field(..., description="파일명")
    size: int = Field(..., description="파일 크기")
    mime: str = Field(..., description="MIME 타입")
    hash: str = Field(..., description="파일 해시")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="파일 생성일시")
    modified_at: datetime = Field(default_factory=datetime.utcnow, description="파일 수정일시")

# 공통 문서 기본 클래스
class DocumentBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="OCR로 추출된 텍스트")
    summary: Optional[str] = Field(None, description="AI 요약")
    keywords: List[str] = Field(default=[], description="키워드 목록")
    document_type: str = Field(..., description="문서 타입")
    basic_info: BasicInfo = Field(default_factory=BasicInfo, description="기본 정보")
    file_metadata: FileMetadata = Field(..., description="파일 메타데이터")

# 이력서 모델 (OCR 기반)
class ResumeCreate(DocumentBase):
    pass

class ResumeDocument(DocumentBase):
    id: str = Field(alias="_id", description="이력서 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True

# 자기소개서 모델 (OCR 기반)
class CoverLetterCreate(DocumentBase):
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")

class CoverLetterDocument(CoverLetterCreate):
    id: str = Field(alias="_id", description="자기소개서 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True

# 포트폴리오 모델 (OCR 기반)
class PortfolioCreate(DocumentBase):
    items: List[PortfolioItem] = Field(default=[], description="포트폴리오 아이템들")
    analysis_score: Optional[int] = Field(None, description="분석 점수 (0-100)")
    status: str = Field(default="active", description="포트폴리오 상태")
    version: int = Field(default=1, description="버전 번호")

class PortfolioDocument(PortfolioCreate):
    id: str = Field(alias="_id", description="포트폴리오 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")
    
    @validator('analysis_score')
    def validate_analysis_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('분석 점수는 0-100 사이여야 합니다')
        return v
    
    class Config:
        populate_by_name = True
