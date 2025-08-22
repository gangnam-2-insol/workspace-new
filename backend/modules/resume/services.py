from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging

from ..shared.services import BaseService
from .models import (
    Resume, ResumeCreate, ResumeUpdate, ResumeSearchRequest,
    ResumeAnalysisRequest, ResumeAnalysisResult, ResumeStatus
)

logger = logging.getLogger(__name__)

class ResumeService(BaseService):
    """이력서 서비스"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "resumes"

    async def create_resume(self, resume_data: ResumeCreate) -> str:
        """이력서 생성"""
        try:
            resume = Resume(**resume_data.dict())
            result = await self.db[self.collection].insert_one(resume.dict(by_alias=True))
            resume_id = str(result.inserted_id)
            logger.info(f"이력서 생성 완료: {resume_id}")
            return resume_id
        except Exception as e:
            logger.error(f"이력서 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 생성에 실패했습니다.")

    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """이력서 조회"""
        try:
            resume_data = await self.db[self.collection].find_one({"_id": self._get_object_id(resume_id)})
            if resume_data:
                return Resume(**resume_data)
            return None
        except Exception as e:
            logger.error(f"이력서 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 조회에 실패했습니다.")

    async def get_resumes(self, skip: int = 0, limit: int = 10, 
                         status: Optional[ResumeStatus] = None,
                         position: Optional[str] = None) -> List[Resume]:
        """이력서 목록 조회"""
        try:
            filter_query = {}
            if status:
                filter_query["status"] = status
            if position:
                filter_query["position"] = {"$regex": position, "$options": "i"}

            cursor = self.db[self.collection].find(filter_query).skip(skip).limit(limit)
            resumes = []
            async for resume_data in cursor:
                resumes.append(Resume(**resume_data))
            return resumes
        except Exception as e:
            logger.error(f"이력서 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 목록 조회에 실패했습니다.")

    async def update_resume(self, resume_id: str, update_data: ResumeUpdate) -> bool:
        """이력서 수정"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(resume_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"이력서 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 수정에 실패했습니다.")

    async def delete_resume(self, resume_id: str) -> bool:
        """이력서 삭제"""
        try:
            result = await self.db[self.collection].delete_one({"_id": self._get_object_id(resume_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"이력서 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 삭제에 실패했습니다.")

    async def search_resumes(self, search_request: ResumeSearchRequest) -> List[Resume]:
        """이력서 검색"""
        try:
            filter_query = {}
            
            if search_request.query:
                filter_query["$or"] = [
                    {"name": {"$regex": search_request.query, "$options": "i"}},
                    {"position": {"$regex": search_request.query, "$options": "i"}},
                    {"skills": {"$regex": search_request.query, "$options": "i"}}
                ]
            
            if search_request.position:
                filter_query["position"] = {"$regex": search_request.position, "$options": "i"}
            
            if search_request.department:
                filter_query["department"] = {"$regex": search_request.department, "$options": "i"}
            
            if search_request.status:
                filter_query["status"] = search_request.status
            
            if search_request.min_score is not None or search_request.max_score is not None:
                score_filter = {}
                if search_request.min_score is not None:
                    score_filter["$gte"] = search_request.min_score
                if search_request.max_score is not None:
                    score_filter["$lte"] = search_request.max_score
                filter_query["analysisScore"] = score_filter

            cursor = self.db[self.collection].find(filter_query).skip(search_request.skip).limit(search_request.limit)
            resumes = []
            async for resume_data in cursor:
                resumes.append(Resume(**resume_data))
            return resumes
        except Exception as e:
            logger.error(f"이력서 검색 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 검색에 실패했습니다.")

    async def analyze_resume(self, analysis_request: ResumeAnalysisRequest) -> ResumeAnalysisResult:
        """이력서 분석"""
        try:
            # 실제 구현에서는 AI 분석 로직 사용
            # 여기서는 더미 분석 결과 반환
            analysis_result = ResumeAnalysisResult(
                resume_id=analysis_request.resume_id,
                overall_score=85.0,
                skill_analysis={
                    "skill_match": 0.8,
                    "skill_gaps": ["React", "Docker"],
                    "recommended_skills": ["TypeScript", "AWS"]
                },
                experience_analysis={
                    "experience_level": "mid-level",
                    "relevant_experience": 3.5,
                    "project_count": 8
                },
                motivation_analysis={
                    "motivation_score": 0.9,
                    "career_alignment": 0.85
                },
                recommendations=[
                    "기술 스택을 더 다양화하세요",
                    "프로젝트 경험을 강화하세요"
                ],
                strengths=[
                    "강한 문제 해결 능력",
                    "팀워크 능력이 뛰어남"
                ],
                weaknesses=[
                    "최신 기술 스택 부족",
                    "대규모 프로젝트 경험 부족"
                ]
            )
            
            logger.info(f"이력서 분석 완료: {analysis_request.resume_id}")
            return analysis_result
        except Exception as e:
            logger.error(f"이력서 분석 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이력서 분석에 실패했습니다.")
