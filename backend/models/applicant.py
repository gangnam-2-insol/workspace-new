from datetime import datetime
from typing import Optional, Dict, Any
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from bson import ObjectId

class ApplicantBase(BaseModel):
    name: str = Field(..., description="지원자 이름")
    email: str = Field(..., description="지원자 이메일 (유니크)")
    phone: Optional[str] = Field(None, description="지원자 전화번호")

class ApplicantCreate(ApplicantBase):
    position: Optional[str] = Field(None, description="지원 직무")
    experience: Optional[Union[str, int]] = Field(None, description="경력")
    skills: Optional[Union[str, List[str]]] = Field(None, description="기술 스택")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, ge=0, le=100, description="분석 점수 (0-100)")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[str] = Field(default="pending", description="상태")
    
    # 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

class Applicant(ApplicantBase):
    id: str = Field(alias="_id", description="지원자 ID")
    position: Optional[str] = Field(None, description="지원 직무")
    experience: Optional[Union[str, int]] = Field(None, description="경력")
    skills: Optional[Union[str, List[str]]] = Field(None, description="기술 스택")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, ge=0, le=100, description="분석 점수 (0-100)")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[str] = Field(default="pending", description="상태")
    
    # 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

    # 회사 인재상 점수 필드
    culture_scores: Optional[Dict[str, Any]] = Field(
        default={},
        description="회사 인재상별 평가 점수"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")

    
    # 랭킹 정보
    ranks: Optional[dict] = Field(None, description="랭킹 정보")
    
    created_at: Optional[datetime] = Field(None, description="생성일시")
    updated_at: Optional[datetime] = Field(None, description="수정일시")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "email": "hong@example.com",
                "phone": "010-1234-5678",
                "position": "백엔드 개발자",
                "experience": "3년",
                "skills": ["Java", "Spring Boot", "MySQL"],
                "growthBackground": "학창 시절부터 프로그래밍에 관심...",
                "motivation": "귀사의 기술력에 매료되어...",
                "careerHistory": "2022년부터 스타트업에서...",
                "analysisScore": 85,
                "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 있습니다.",
                "status": "pending",
                "job_posting_id": "507f1f77bcf86cd799439011",
                "resume_id": "507f1f77bcf86cd799439012",
                "cover_letter_id": "507f1f77bcf86cd799439013",
                "portfolio_id": "507f1f77bcf86cd799439014",
                "ranks": {
                    "resume": 85,
                    "coverLetter": 78,
                    "portfolio": 82,
                    "total": 82
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
