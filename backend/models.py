from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


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

# 지원자 모델
class Applicant(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="지원자 이름")
    position: str = Field(..., description="지원 직무")
    department: str = Field(..., description="지원 부서")
    email: str = Field(..., description="이메일")
    phone: str = Field(..., description="전화번호")
    applied_date: str = Field(..., description="지원일")
    status: str = Field(default="지원", description="지원 상태")
    experience: str = Field(..., description="경력")
    skills: List[str] = Field(default=[], description="기술 스택")
    rating: float = Field(default=0.0, description="평점")
    summary: str = Field(default="", description="AI 분석 요약")
    ai_suitability: int = Field(default=0, description="AI 적합도 점수")
    ai_scores: Optional[Dict[str, Any]] = Field(default=None, description="AI 세부 점수")
    documents: Optional[Dict[str, Any]] = Field(default=None, description="제출 서류")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 사용자 모델
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., description="사용자명")
    email: str = Field(..., description="이메일")
    role: str = Field(default="user", description="사용자 역할")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 면접 모델
class Interview(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="지원자 ID")
    company: str = Field(..., description="회사명")
    position: str = Field(..., description="직무")
    date: datetime = Field(..., description="면접 일시")
    status: str = Field(default="scheduled", description="면접 상태")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 채용공고 모델
class Job(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., description="채용공고 제목")
    company: str = Field(..., description="회사명")
    location: str = Field(..., description="근무지")
    description: str = Field(..., description="직무 설명")
    requirements: List[str] = Field(default=[], description="요구사항")
    salary_range: Optional[str] = Field(default=None, description="연봉 범위")
    type: str = Field(default="full-time", description="고용 형태")
    status: str = Field(default="active", description="공고 상태")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}



# 상태 업데이트 모델
class StatusUpdate(BaseModel):
    status: str = Field(..., description="새로운 상태")

# 통계 응답 모델
class StatsResponse(BaseModel):
    total: int
    passed: int
    waiting: int
    rejected: int
