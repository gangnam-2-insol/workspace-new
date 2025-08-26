from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging
import json
import base64
from PIL import Image
import io
import re

from ..shared.services import BaseService
from .models import (
    JobPosting, JobPostingCreate, JobPostingUpdate, JobPostingSearchRequest,
    JobPostingStatistics, AIJobPostingRequest, ImageJobPostingRequest,
    LangGraphJobPostingRequest, JobPostingTemplate, JobStatus, JobType
)

logger = logging.getLogger(__name__)

class JobPostingService(BaseService):
    """채용공고 서비스"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "job_postings"
        self.templates_collection = "job_posting_templates"

    async def create_job_posting(self, job_data: JobPostingCreate) -> str:
        """채용공고 생성"""
        try:
            job_posting = JobPosting(**job_data.dict())
            result = await self.db[self.collection].insert_one(job_posting.dict(by_alias=True))
            job_id = str(result.inserted_id)
            logger.info(f"채용공고 생성 완료: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"채용공고 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 생성에 실패했습니다.")

    async def get_job_posting(self, job_id: str) -> Optional[JobPosting]:
        """채용공고 조회"""
        try:
            job_data = await self.db[self.collection].find_one({"_id": self._get_object_id(job_id)})
            if job_data:
                return JobPosting(**job_data)
            return None
        except Exception as e:
            logger.error(f"채용공고 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 조회에 실패했습니다.")

    async def get_job_postings(self, skip: int = 0, limit: int = 10, 
                             status: Optional[JobStatus] = None,
                             company: Optional[str] = None) -> List[JobPosting]:
        """채용공고 목록 조회"""
        try:
            filter_query = {}
            if status:
                filter_query["status"] = status
            if company:
                filter_query["company"] = {"$regex": company, "$options": "i"}

            cursor = self.db[self.collection].find(filter_query).skip(skip).limit(limit)
            job_postings = []
            async for job_data in cursor:
                job_postings.append(JobPosting(**job_data))
            return job_postings
        except Exception as e:
            logger.error(f"채용공고 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 목록 조회에 실패했습니다.")

    async def update_job_posting(self, job_id: str, update_data: JobPostingUpdate) -> bool:
        """채용공고 수정"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(job_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"채용공고 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 수정에 실패했습니다.")

    async def delete_job_posting(self, job_id: str) -> bool:
        """채용공고 삭제"""
        try:
            result = await self.db[self.collection].delete_one({"_id": self._get_object_id(job_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"채용공고 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 삭제에 실패했습니다.")

    async def publish_job_posting(self, job_id: str) -> bool:
        """채용공고 발행"""
        try:
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(job_id)},
                {"$set": {"status": JobStatus.PUBLISHED, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"채용공고 발행 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 발행에 실패했습니다.")

    async def close_job_posting(self, job_id: str) -> bool:
        """채용공고 마감"""
        try:
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(job_id)},
                {"$set": {"status": JobStatus.CLOSED, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"채용공고 마감 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 마감에 실패했습니다.")

    async def increment_views(self, job_id: str) -> bool:
        """조회수 증가"""
        try:
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(job_id)},
                {"$inc": {"views": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"조회수 증가 실패: {str(e)}")
            return False

    async def search_job_postings(self, search_request: JobPostingSearchRequest) -> List[JobPosting]:
        """채용공고 검색"""
        try:
            filter_query = {}
            
            if search_request.query:
                filter_query["$or"] = [
                    {"title": {"$regex": search_request.query, "$options": "i"}},
                    {"description": {"$regex": search_request.query, "$options": "i"}},
                    {"requirements": {"$regex": search_request.query, "$options": "i"}}
                ]
            
            if search_request.company:
                filter_query["company"] = {"$regex": search_request.company, "$options": "i"}
            
            if search_request.location:
                filter_query["location"] = {"$regex": search_request.location, "$options": "i"}
            
            if search_request.type:
                filter_query["type"] = search_request.type
            
            if search_request.status:
                filter_query["status"] = search_request.status
            
            if search_request.required_skills:
                filter_query["required_skills"] = {"$in": search_request.required_skills}
            
            if search_request.industry:
                filter_query["industry"] = {"$regex": search_request.industry, "$options": "i"}
            
            if search_request.min_experience is not None or search_request.max_experience is not None:
                experience_filter = {}
                if search_request.min_experience is not None:
                    experience_filter["$gte"] = search_request.min_experience
                if search_request.max_experience is not None:
                    experience_filter["$lte"] = search_request.max_experience
                filter_query["experience_min_years"] = experience_filter

            cursor = self.db[self.collection].find(filter_query).skip(search_request.skip).limit(search_request.limit)
            job_postings = []
            async for job_data in cursor:
                job_postings.append(JobPosting(**job_data))
            return job_postings
        except Exception as e:
            logger.error(f"채용공고 검색 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 검색에 실패했습니다.")

    async def get_job_posting_statistics(self) -> JobPostingStatistics:
        """채용공고 통계 조회"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_jobs": {"$sum": 1},
                        "total_applicants": {"$sum": "$applicants"},
                        "total_views": {"$sum": "$views"},
                        "published_jobs": {
                            "$sum": {"$cond": [{"$eq": ["$status", JobStatus.PUBLISHED]}, 1, 0]}
                        },
                        "draft_jobs": {
                            "$sum": {"$cond": [{"$eq": ["$status", JobStatus.DRAFT]}, 1, 0]}
                        },
                        "closed_jobs": {
                            "$sum": {"$cond": [{"$eq": ["$status", JobStatus.CLOSED]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await self.db[self.collection].aggregate(pipeline).to_list(1)
            if result:
                stats = result[0]
                average_applicants = stats["total_applicants"] / stats["total_jobs"] if stats["total_jobs"] > 0 else 0
                
                # 고용 형태별 분포
                type_pipeline = [
                    {"$group": {"_id": "$type", "count": {"$sum": 1}}}
                ]
                type_distribution = {}
                type_results = await self.db[self.collection].aggregate(type_pipeline).to_list(None)
                for type_result in type_results:
                    type_distribution[type_result["_id"]] = type_result["count"]
                
                # 산업별 분포
                industry_pipeline = [
                    {"$group": {"_id": "$industry", "count": {"$sum": 1}}}
                ]
                industry_distribution = {}
                industry_results = await self.db[self.collection].aggregate(industry_pipeline).to_list(None)
                for industry_result in industry_results:
                    if industry_result["_id"]:
                        industry_distribution[industry_result["_id"]] = industry_result["count"]
                
                # 상위 회사
                company_pipeline = [
                    {"$group": {"_id": "$company", "count": {"$sum": 1}, "total_applicants": {"$sum": "$applicants"}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                top_companies = await self.db[self.collection].aggregate(company_pipeline).to_list(None)
                
                return JobPostingStatistics(
                    total_jobs=stats["total_jobs"],
                    published_jobs=stats["published_jobs"],
                    draft_jobs=stats["draft_jobs"],
                    closed_jobs=stats["closed_jobs"],
                    total_applicants=stats["total_applicants"],
                    total_views=stats["total_views"],
                    average_applicants_per_job=average_applicants,
                    job_type_distribution=type_distribution,
                    industry_distribution=industry_distribution,
                    top_companies=top_companies
                )
            
            return JobPostingStatistics(
                total_jobs=0, published_jobs=0, draft_jobs=0, closed_jobs=0,
                total_applicants=0, total_views=0, average_applicants_per_job=0.0
            )
        except Exception as e:
            logger.error(f"채용공고 통계 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 통계 조회에 실패했습니다.")

    async def create_ai_job_posting(self, ai_request: AIJobPostingRequest) -> JobPosting:
        """AI 기반 채용공고 생성"""
        try:
            # AI 분석을 통한 채용공고 생성 로직
            # 실제 구현에서는 OpenAI API 등을 사용하여 분석
            job_data = await self._analyze_job_description(ai_request.description)
            
            # 기본 정보 설정
            job_data["company"] = ai_request.company or "미정"
            job_data["location"] = "미정"
            job_data["type"] = ai_request.type or JobType.FULL_TIME
            
            # 추가 요구사항이 있으면 병합
            if ai_request.additional_requirements:
                job_data["requirements"] = f"{job_data.get('requirements', '')}\n\n추가 요구사항:\n{ai_request.additional_requirements}"
            
            job_posting = JobPosting(**job_data)
            result = await self.db[self.collection].insert_one(job_posting.dict(by_alias=True))
            job_posting.id = result.inserted_id
            
            logger.info(f"AI 기반 채용공고 생성 완료: {job_posting.id}")
            return job_posting
        except Exception as e:
            logger.error(f"AI 기반 채용공고 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="AI 기반 채용공고 생성에 실패했습니다.")

    async def create_image_job_posting(self, image_request: ImageJobPostingRequest) -> JobPosting:
        """이미지 기반 채용공고 생성"""
        try:
            # OCR을 통한 텍스트 추출
            extracted_text = await self._extract_text_from_image(image_request.image_file)
            
            # AI 분석을 통한 채용공고 생성
            job_data = await self._analyze_job_description(extracted_text)
            
            # 추가 정보 병합
            if image_request.additional_info:
                job_data["description"] = f"{job_data.get('description', '')}\n\n추가 정보:\n{image_request.additional_info}"
            
            job_data["company"] = image_request.company or "미정"
            job_data["location"] = "미정"
            job_data["type"] = JobType.FULL_TIME
            
            job_posting = JobPosting(**job_data)
            result = await self.db[self.collection].insert_one(job_posting.dict(by_alias=True))
            job_posting.id = result.inserted_id
            
            logger.info(f"이미지 기반 채용공고 생성 완료: {job_posting.id}")
            return job_posting
        except Exception as e:
            logger.error(f"이미지 기반 채용공고 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="이미지 기반 채용공고 생성에 실패했습니다.")

    async def create_langgraph_job_posting(self, langgraph_request: LangGraphJobPostingRequest) -> JobPosting:
        """LangGraph 기반 채용공고 생성"""
        try:
            # LangGraph를 통한 대화형 채용공고 생성
            job_data = await self._process_langgraph_request(langgraph_request)
            
            job_posting = JobPosting(**job_data)
            result = await self.db[self.collection].insert_one(job_posting.dict(by_alias=True))
            job_posting.id = result.inserted_id
            
            logger.info(f"LangGraph 기반 채용공고 생성 완료: {job_posting.id}")
            return job_posting
        except Exception as e:
            logger.error(f"LangGraph 기반 채용공고 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="LangGraph 기반 채용공고 생성에 실패했습니다.")

    async def get_job_posting_templates(self, category: Optional[str] = None) -> List[JobPostingTemplate]:
        """채용공고 템플릿 조회"""
        try:
            filter_query = {"is_public": True}
            if category:
                filter_query["category"] = category
            
            cursor = self.db[self.templates_collection].find(filter_query)
            templates = []
            async for template_data in cursor:
                templates.append(JobPostingTemplate(**template_data))
            return templates
        except Exception as e:
            logger.error(f"채용공고 템플릿 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 템플릿 조회에 실패했습니다.")

    async def create_job_posting_template(self, template_data: JobPostingTemplate) -> str:
        """채용공고 템플릿 생성"""
        try:
            result = await self.db[self.templates_collection].insert_one(template_data.dict(by_alias=True))
            template_id = str(result.inserted_id)
            logger.info(f"채용공고 템플릿 생성 완료: {template_id}")
            return template_id
        except Exception as e:
            logger.error(f"채용공고 템플릿 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="채용공고 템플릿 생성에 실패했습니다.")

    async def _analyze_job_description(self, description: str) -> Dict[str, Any]:
        """직무 설명 분석"""
        # 실제 구현에서는 OpenAI API 등을 사용하여 분석
        # 여기서는 간단한 키워드 추출 로직
        job_data = {
            "title": "새로운 채용공고",
            "description": description,
            "requirements": "상세한 자격 요건은 면접 시 논의",
            "job_keywords": [],
            "required_skills": [],
            "preferred_skills": []
        }
        
        # 간단한 키워드 추출
        keywords = re.findall(r'\b(?:Python|JavaScript|React|Node\.js|Java|C\+\+|AWS|Docker|Kubernetes|Git|SQL|MongoDB|Redis|Elasticsearch|Machine Learning|AI|Data Science|Frontend|Backend|Full Stack|DevOps|UI/UX|Mobile|iOS|Android)\b', description, re.IGNORECASE)
        job_data["job_keywords"] = list(set(keywords))
        job_data["required_skills"] = keywords[:5]  # 상위 5개를 필수 기술로
        job_data["preferred_skills"] = keywords[5:10]  # 나머지를 우선 기술로
        
        return job_data

    async def _extract_text_from_image(self, image_base64: str) -> str:
        """이미지에서 텍스트 추출 (OCR)"""
        try:
            # base64 디코딩
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # 실제 구현에서는 OCR 라이브러리 사용
            # 여기서는 더미 텍스트 반환
            return "이미지에서 추출된 텍스트입니다. 실제 OCR 구현이 필요합니다."
        except Exception as e:
            logger.error(f"이미지 텍스트 추출 실패: {str(e)}")
            return ""

    async def _process_langgraph_request(self, request: LangGraphJobPostingRequest) -> Dict[str, Any]:
        """LangGraph 요청 처리"""
        # 실제 구현에서는 LangGraph 에이전트 사용
        # 여기서는 기본 데이터 반환
        return {
            "title": "LangGraph로 생성된 채용공고",
            "description": request.user_input,
            "company": "미정",
            "location": "미정",
            "type": JobType.FULL_TIME,
            "requirements": "LangGraph를 통한 상세 요구사항 분석 필요",
            "job_keywords": [],
            "required_skills": [],
            "preferred_skills": []
        }
