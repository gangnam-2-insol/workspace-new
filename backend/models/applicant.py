from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field


class ApplicantBase(BaseModel):
    name: str = Field(..., description="지원자 이름")
    email: str = Field(..., description="지원자 이메일 (유니크)")
    phone: Optional[str] = Field(None, description="지원자 전화번호")

class ApplicantCreate(ApplicantBase):
    # ===== 이력서 (Resume) 필드들 =====
    # 기본 정보
    position: Optional[str] = Field(None, description="지원 직무")
    department: Optional[str] = Field(None, description="부서")

    # 경력 정보
    experience: Optional[Union[str, int]] = Field(None, description="경력")

    # 기술 스택
    skills: Optional[Union[str, List[str]]] = Field(None, description="기술 스택")

    # 경력 사항
    careerHistory: Optional[str] = Field(None, description="경력 사항")

    # ===== 자소서 (Cover Letter) 필드들 =====
    # 성장 배경
    growthBackground: Optional[str] = Field(None, description="성장 배경")

    # 지원 동기
    motivation: Optional[str] = Field(None, description="지원 동기")

    # ===== 공통 필드들 =====
    analysisScore: Optional[int] = Field(None, ge=0, le=100, description="분석 점수 (0-100)")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[str] = Field(default="pending", description="상태")

    # 직접 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

    # 소셜 미디어 및 포트폴리오 URL
    github_url: Optional[str] = Field(None, description="GitHub 프로필 URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn 프로필 URL")
    portfolio_url: Optional[str] = Field(None, description="포트폴리오 URL")

class Applicant(ApplicantBase):
    id: str = Field(alias="_id", description="지원자 ID")

    # ===== 이력서 (Resume) 필드들 =====
    # 기본 정보
    position: Optional[str] = Field(None, description="지원 직무")
    department: Optional[str] = Field(None, description="부서")

    # 경력 정보
    experience: Optional[Union[str, int]] = Field(None, description="경력")

    # 기술 스택
    skills: Optional[Union[str, List[str]]] = Field(None, description="기술 스택")

    # 경력 사항
    careerHistory: Optional[str] = Field(None, description="경력 사항")

    # ===== 자소서 (Cover Letter) 필드들 =====
    # 성장 배경
    growthBackground: Optional[str] = Field(None, description="성장 배경")

    # 지원 동기
    motivation: Optional[str] = Field(None, description="지원 동기")

    # ===== 공통 필드들 =====
    analysisScore: Optional[int] = Field(None, ge=0, le=100, description="분석 점수 (0-100)")
    analysisResult: Optional[str] = Field(None, description="분석 결과")
    status: Optional[str] = Field(default="pending", description="상태")

    # 직접 연결 필드들
    job_posting_id: Optional[str] = Field(None, description="채용공고 ID")
    resume_id: Optional[str] = Field(None, description="이력서 ID")
    cover_letter_id: Optional[str] = Field(None, description="자기소개서 ID")
    portfolio_id: Optional[str] = Field(None, description="포트폴리오 ID")

    # 소셜 미디어 및 포트폴리오 URL
    github_url: Optional[str] = Field(None, description="GitHub 프로필 URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn 프로필 URL")
    portfolio_url: Optional[str] = Field(None, description="포트폴리오 URL")

    # 랭킹 정보
    ranks: Optional[Dict[str, int]] = Field(
        default={},
        description="랭킹 정보 (resume, coverLetter, portfolio, total)"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "email": "hong@example.com",
                "phone": "010-1234-5678",
                # 이력서 필드들
                "position": "백엔드 개발자",
                "experience": "3년",
                "skills": ["Java", "Spring Boot", "MySQL"],
                "careerHistory": "2022년부터 스타트업에서...",
                # 자소서 필드들
                "growthBackground": "학창 시절부터 프로그래밍에 관심...",
                "motivation": "귀사의 기술력에 매료되어...",
                "analysisScore": 85,
                "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 있습니다.",
                "status": "pending",
                "job_posting_id": "507f1f77bcf86cd799439011",
                "resume_id": "507f1f77bcf86cd799439012",
                "cover_letter_id": "507f1f77bcf86cd799439013",
                "portfolio_id": "507f1f77bcf86cd799439014",
                "github_url": "https://github.com/kyungho222",
                "linkedin_url": "https://linkedin.com/in/honggildong",
                "portfolio_url": "https://portfolio.example.com/honggildong",
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
