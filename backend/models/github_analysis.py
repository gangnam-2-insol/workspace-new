from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId

class GithubAnalysisBase(BaseModel):
    applicant_id: str = Field(..., description="지원자 ID")
    github_url: str = Field(..., description="분석된 GitHub URL")
    analysis_type: str = Field(..., description="분석 타입 (user/repository)")
    username: Optional[str] = Field(None, description="GitHub 사용자명")
    repo_name: Optional[str] = Field(None, description="레포지토리명 (repository 분석인 경우)")
    
    # 분석 결과 데이터
    analysis_data: Dict[str, Any] = Field(..., description="GitHub 분석 결과")
    
    # 캐시 관리
    last_analyzed: datetime = Field(default_factory=datetime.utcnow, description="마지막 분석 시간")
    cache_version: str = Field(default="1.0", description="캐시 버전")
    
    # 차이점 감지용 해시
    content_hash: str = Field(..., description="콘텐츠 해시 (변경 감지용)")
    
    # 메타데이터
    total_repos: Optional[int] = Field(None, description="총 레포지토리 수 (user 분석인 경우)")
    total_stars: Optional[int] = Field(None, description="총 스타 수 (user 분석인 경우)")
    total_forks: Optional[int] = Field(None, description="총 포크 수 (user 분석인 경우)")
    main_languages: Optional[List[str]] = Field(None, description="주요 프로그래밍 언어")

class GithubAnalysisCreate(GithubAnalysisBase):
    pass

class GithubAnalysis(GithubAnalysisBase):
    id: str = Field(alias="_id", description="분석 결과 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_string(cls, v):
        """ObjectId를 문자열로 변환"""
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "applicant_id": "507f1f77bcf86cd799439011",
                "github_url": "https://github.com/gaa149/mini_project",
                "analysis_type": "repository",
                "username": "gaa149",
                "repo_name": "mini_project",
                "analysis_data": {
                    "summary": "이 프로젝트는 미니 프로젝트입니다...",
                    "languages": {"JavaScript": 60, "Python": 40},
                    "topics": ["web", "api", "javascript"],
                    "readme_content": "프로젝트 설명...",
                    "commit_history": [...],
                    "contributors": [...]
                },
                "content_hash": "abc123def456",
                "total_repos": 15,
                "total_stars": 25,
                "total_forks": 5,
                "main_languages": ["JavaScript", "Python"],
                "last_analyzed": "2024-01-01T00:00:00Z",
                "cache_version": "1.0",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
