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

# 공통 문서 기본 클래스 (application_id 제거)
class DocumentBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="추출된 텍스트")
    summary: Optional[str] = Field(None, description="요약")
    keywords: Optional[List[str]] = Field(default=[], description="키워드")
    document_type: Optional[str] = Field(None, description="문서 타입")
    basic_info: Optional[Dict[str, Any]] = Field(default={}, description="기본 정보")
    file_metadata: Optional[Dict[str, Any]] = Field(default={}, description="파일 메타데이터")

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
    pass

class CoverLetterDocument(DocumentBase):
    id: str = Field(alias="_id", description="자기소개서 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    
    class Config:
        populate_by_name = True

# 포트폴리오 모델 (OCR 기반)
class PortfolioCreate(DocumentBase):
    items: List[PortfolioItem] = Field(..., description="포트폴리오 아이템들")
    analysis_score: Optional[float] = Field(None, description="분석 점수 (0-100)")
    status: str = Field(default="active", description="포트폴리오 상태")

class PortfolioDocument(PortfolioCreate):
    id: str = Field(alias="_id", description="포트폴리오 ID")
    version: int = Field(default=1, description="버전")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")
    
    @validator('analysis_score')
    def validate_analysis_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('분석 점수는 0-100 사이여야 합니다')
        return v
    
    class Config:
        populate_by_name = True
