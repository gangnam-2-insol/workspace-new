from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class CoverLetterBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="추출된 텍스트")
    summary: Optional[str] = Field(None, description="요약")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    document_type: str = Field(default="cover_letter", description="문서 타입")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")

class CoverLetterCreate(CoverLetterBase):
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")

class CoverLetter(CoverLetterBase):
    id: str = Field(alias="_id", description="자기소개서 ID")
    basic_info: Optional[dict] = Field(None, description="기본 정보")
    file_metadata: Optional[dict] = Field(None, description="파일 메타데이터")
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "applicant_id": "507f1f77bcf86cd799439011",
                "extracted_text": "홍길동의 자기소개서 내용...",
                "summary": "백엔드 개발에 대한 열정과 경험",
                "keywords": ["백엔드", "개발", "열정"],
                "document_type": "cover_letter",
                "growthBackground": "학창 시절부터 프로그래밍에 관심...",
                "motivation": "귀사의 기술력에 매료되어...",
                "careerHistory": "2022년부터 스타트업에서...",
                "basic_info": {
                    "emails": ["hong@example.com"],
                    "phones": ["010-1234-5678"],
                    "names": ["홍길동"],
                    "urls": ["https://github.com/hong"]
                },
                "file_metadata": {
                    "filename": "cover_letter.pdf",
                    "size": 512000,
                    "mime": "application/pdf",
                    "hash": "def456ghi789",
                    "created_at": "2024-01-01T00:00:00Z",
                    "modified_at": "2024-01-01T00:00:00Z"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
