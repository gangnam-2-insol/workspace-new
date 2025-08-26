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


# STAR 분석 결과 모델
class STARAnalysis(BaseModel):
    situation: str = Field(..., description="상황")
    task: str = Field(..., description="과제")
    action: str = Field(..., description="행동")
    result: str = Field(..., description="결과")
    evidence_sentence_indices: List[int] = Field(default=[], description="증거 문장 인덱스")
    confidence: float = Field(default=0.0, description="신뢰도")


# 핵심 강점 모델
class TopStrength(BaseModel):
    strength: str = Field(..., description="강점 내용")
    evidence: str = Field(..., description="증거 문장")
    confidence: float = Field(default=0.0, description="신뢰도")


# 직무 적합성 분석 모델
class JobSuitability(BaseModel):
    score: int = Field(..., description="적합성 점수 (0-100)")
    matched_skills: List[str] = Field(default=[], description="매칭된 스킬")
    missing_skills: List[str] = Field(default=[], description="부족한 스킬")
    explanation: str = Field(default="", description="점수 근거 설명")


# 문장 개선 제안 모델
class SentenceImprovement(BaseModel):
    original: str = Field(..., description="원본 문장")
    improved: str = Field(..., description="개선된 문장")
    improvement_type: str = Field(default="", description="개선 유형 (문법/간결성/적극성)")


# 평가 루브릭 점수 모델
class EvaluationRubric(BaseModel):
    job_relevance: float = Field(default=0.0, description="직무 연관성 (0-10)")
    problem_solving: float = Field(default=0.0, description="문제 해결 능력 (0-10)")
    impact: float = Field(default=0.0, description="임팩트 (0-10)")
    clarity: float = Field(default=0.0, description="명료성 (0-10)")
    professionalism: float = Field(default=0.0, description="전문성 (0-10)")
    grammar: float = Field(default=0.0, description="문법 및 맞춤법 (0-10)")
    keyword_coverage: float = Field(default=0.0, description="키워드 커버리지 (0-10)")
    overall_score: float = Field(default=0.0, description="종합 점수 (0-10)")


# 자소서 분석 결과 모델
class CoverLetterAnalysis(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    filename: str = Field(..., description="파일명")
    original_text: str = Field(..., description="원본 텍스트")
    job_description: Optional[str] = Field(default="", description="직무 설명")
    
    # 분석 결과
    summary: str = Field(default="", description="요약")
    top_strengths: List[TopStrength] = Field(default=[], description="핵심 강점")
    star_cases: List[STARAnalysis] = Field(default=[], description="STAR 사례")
    job_suitability: Optional[JobSuitability] = Field(default=None, description="직무 적합성")
    sentence_improvements: List[SentenceImprovement] = Field(default=[], description="문장 개선 제안")
    evaluation_rubric: Optional[EvaluationRubric] = Field(default=None, description="평가 루브릭")
    
    # 메타데이터
    file_size: int = Field(default=0, description="파일 크기")
    file_type: str = Field(default="", description="파일 타입")
    processing_time: float = Field(default=0.0, description="처리 시간 (초)")
    llm_model_used: str = Field(default="", description="사용된 LLM 모델")
    
    # 벡터 검색용
    embedding: Optional[List[float]] = Field(default=None, description="텍스트 임베딩")
    
    # 상태 및 시간
    status: str = Field(default="processing", description="처리 상태")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 자소서 업로드 요청 모델
class CoverLetterUploadRequest(BaseModel):
    job_description: Optional[str] = Field(default="", description="직무 설명")
    analysis_type: str = Field(default="full", description="분석 유형 (full/summary/star/suitability)")


# 자소서 분석 응답 모델
class CoverLetterAnalysisResponse(BaseModel):
    id: str = Field(..., description="분석 ID")
    status: str = Field(..., description="처리 상태")
    analysis: Optional[CoverLetterAnalysis] = Field(default=None, description="분석 결과")
    message: str = Field(default="", description="응답 메시지")


# 자소서 검색 요청 모델
class CoverLetterSearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(default=10, description="검색 결과 수")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="필터 조건")


# 자소서 비교 요청 모델
class CoverLetterComparisonRequest(BaseModel):
    cover_letter_ids: List[str] = Field(..., description="비교할 자소서 ID 목록")
    comparison_type: str = Field(default="strengths", description="비교 유형")
