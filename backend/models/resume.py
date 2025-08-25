from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class ResumeBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="추출된 텍스트")
    summary: Optional[str] = Field(None, description="요약")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    document_type: str = Field(default="resume", description="문서 타입")

class ResumeCreate(ResumeBase):
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")

class Resume(ResumeBase):
    id: str = Field(alias="_id", description="이력서 ID")
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")
    created_at: Optional[datetime] = Field(None, description="생성일시")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "applicant_id": "507f1f77bcf86cd799439011",
                "extracted_text": "홍길동의 이력서 내용...",
                "summary": "3년 경력의 백엔드 개발자",
                "keywords": ["Java", "Spring Boot", "MySQL"],
                "document_type": "resume",
                "basic_info": {
                    "emails": ["hong@example.com"],
                    "phones": ["010-1234-5678"],
                    "names": ["홍길동"],
                    "urls": ["https://github.com/hong"]
                },
                "file_metadata": {
                    "filename": "resume.pdf",
                    "size": 1024000,
                    "mime": "application/pdf",
                    "hash": "abc123def456",
                    "created_at": "2024-01-01T00:00:00Z",
                    "modified_at": "2024-01-01T00:00:00Z"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
