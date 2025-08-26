from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

# 공통 ObjectId 처리
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

# 문서 타입 열거형
class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    PORTFOLIO = "portfolio"

# 공통 문서 기본 클래스
class DocumentBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    extracted_text: str = Field(..., description="추출된 텍스트")
    summary: Optional[str] = Field(None, description="요약")
    keywords: Optional[List[str]] = Field(default=[], description="키워드")
    document_type: Optional[DocumentType] = Field(None, description="문서 타입")
    basic_info: Optional[Dict[str, Any]] = Field(default={}, description="기본 정보")
    file_metadata: Optional[Dict[str, Any]] = Field(default={}, description="파일 메타데이터")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")

# 공통 분석 결과 모델
class AnalysisResult(BaseModel):
    score: float = Field(..., description="분석 점수 (0-100)")
    summary: str = Field(..., description="분석 요약")
    strengths: List[str] = Field(default=[], description="강점 목록")
    weaknesses: List[str] = Field(default=[], description="개선점 목록")
    recommendations: List[str] = Field(default=[], description="권장사항 목록")
    confidence: float = Field(default=0.0, description="신뢰도 (0-1)")

# 공통 파일 업로드 응답 모델
class FileUploadResponse(BaseModel):
    success: bool = Field(..., description="업로드 성공 여부")
    message: str = Field(..., description="응답 메시지")
    file_id: Optional[str] = Field(None, description="파일 ID")
    filename: Optional[str] = Field(None, description="파일명")
    file_size: Optional[int] = Field(None, description="파일 크기")
    analysis_result: Optional[AnalysisResult] = Field(None, description="분석 결과")

# 공통 검색 요청 모델
class SearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(default=10, description="검색 결과 수")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="필터 조건")
    document_type: Optional[DocumentType] = Field(None, description="문서 타입")

# 공통 페이지네이션 모델
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=10, ge=1, le=100, description="페이지당 항목 수")
    sort_by: Optional[str] = Field(default="created_at", description="정렬 기준")
    sort_order: Optional[str] = Field(default="desc", description="정렬 순서 (asc/desc)")

# 공통 응답 모델
class BaseResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    error: Optional[str] = Field(None, description="에러 메시지")
