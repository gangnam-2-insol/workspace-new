from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

# 지원자 상태 열거형 정의
class ApplicantStatus(str, Enum):
    PENDING = "pending"           # 지원 (기본값)
    DOCUMENT_PASS = "document_pass"    # 서류합격
    DOCUMENT_FAIL = "document_fail"    # 서류불합격
    INTERVIEW_PASS = "interview_pass"  # 면접합격
    INTERVIEW_FAIL = "interview_fail"  # 면접불합격
    FINAL_PASS = "final_pass"          # 최종합격
    FINAL_FAIL = "final_fail"          # 최종불합격
    HOLD = "hold"                      # 보류
    WITHDRAWN = "withdrawn"            # 지원취소

class ApplicantBase(BaseModel):
    name: str = Field(..., description="지원자 이름")
    email: str = Field(..., description="지원자 이메일")
    phone: Optional[str] = Field(None, description="지원자 전화번호")
    position: Optional[str] = Field(None, description="지원 직무")
    experience: Optional[int] = Field(None, description="경력 연차")
    skills: Optional[List[str]] = Field(None, description="기술 스택 목록")
    status: ApplicantStatus = Field(default=ApplicantStatus.PENDING, description="지원자 상태")

class ApplicantCreate(ApplicantBase):
    # 추가 정보 필드들
    department: Optional[str] = Field(None, description="부서")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, description="분석 점수")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    
    # 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

class ApplicantUpdate(BaseModel):
    """지원자 정보 업데이트용 모델"""
    name: Optional[str] = Field(None, description="지원자 이름")
    email: Optional[str] = Field(None, description="지원자 이메일")
    phone: Optional[str] = Field(None, description="지원자 전화번호")
    position: Optional[str] = Field(None, description="지원 직무")
    experience: Optional[int] = Field(None, description="경력 연차")
    skills: Optional[List[str]] = Field(None, description="기술 스택 목록")
    status: Optional[ApplicantStatus] = Field(None, description="지원자 상태")
    department: Optional[str] = Field(None, description="부서")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, description="분석 점수")
    analysisResult: Optional[str] = Field(None, description="분석 결과")

class ApplicantStatusUpdate(BaseModel):
    """지원자 상태 업데이트용 모델"""
    status: ApplicantStatus = Field(..., description="새로운 상태값")
    reason: Optional[str] = Field(None, description="상태 변경 사유")
    updated_by: Optional[str] = Field(None, description="상태 변경자")

class Applicant(ApplicantBase):
    id: str = Field(alias="_id", description="지원자 ID")
    department: Optional[str] = Field(None, description="부서")
    growthBackground: Optional[str] = Field(None, description="성장 배경")
    motivation: Optional[str] = Field(None, description="지원 동기")
    careerHistory: Optional[str] = Field(None, description="경력 사항")
    analysisScore: Optional[int] = Field(None, description="분석 점수")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    
    # 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")
    
    # 타임스탬프
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "email": "hong@example.com",
                "phone": "010-1234-5678",
                "position": "백엔드 개발자",
                "experience": 3,
                "skills": ["Java", "Spring Boot", "MySQL", "Redis"],
                "status": "pending",
                "department": "개발팀",
                "growthBackground": "학창 시절부터 프로그래밍에 관심...",
                "motivation": "귀사의 기술력에 매료되어...",
                "careerHistory": "2022년부터 스타트업에서...",
                "analysisScore": 85,
                "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 풍부합니다.",
                "resume_id": "507f1f77bcf86cd799439011",
                "cover_letter_id": "507f1f77bcf86cd799439012",
                "portfolio_id": "507f1f77bcf86cd799439013",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
