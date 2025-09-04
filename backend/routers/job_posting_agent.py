"""
채용공고 에이전트 API 라우터
동적 템플릿 시스템과 통합된 채용공고 생성 API
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

from modules.job_posting.job_posting_agent import job_posting_agent, AgentState
from modules.core.services.mongo_service import MongoService

router = APIRouter(prefix="/api/job-posting-agent", tags=["Job Posting Agent"])

# Pydantic 모델들
class StartSessionRequest(BaseModel):
    user_id: str
    company_info: Optional[Dict[str, Any]] = None

class ProcessInputRequest(BaseModel):
    session_id: str
    user_input: str

class SessionStatusResponse(BaseModel):
    session_id: str
    state: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    extracted_keywords: List[str]
    has_template: bool
    has_content: bool

class AgentResponse(BaseModel):
    state: str
    message: str
    next_action: Optional[str] = None
    extracted_keywords: Optional[List[str]] = None
    recommended_templates: Optional[List[Dict[str, Any]]] = None
    selected_template: Optional[Dict[str, Any]] = None
    generated_content: Optional[Dict[str, Any]] = None
    final_content: Optional[Dict[str, Any]] = None
    job_posting_id: Optional[str] = None

@router.post("/start-session", response_model=Dict[str, str])
async def start_session(request: StartSessionRequest):
    """새로운 채용공고 작성 세션 시작"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        session_id = await job_posting_agent.start_session(
            user_id=request.user_id,
            company_info=request.company_info
        )

        return {
            "session_id": session_id,
            "message": "채용공고 작성 세션이 시작되었습니다.",
            "next_action": "채용하고 싶은 직무나 기술 스택을 알려주세요."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/process-input", response_model=AgentResponse)
async def process_user_input(request: ProcessInputRequest):
    """사용자 입력 처리"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        response = await job_posting_agent.process_user_input(
            session_id=request.session_id,
            user_input=request.user_input
        )

        return AgentResponse(**response)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid session: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")

@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """세션 상태 조회"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        status = await job_posting_agent.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")

@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """세션 종료"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        await job_posting_agent.end_session(session_id)

        return {
            "message": "세션이 종료되었습니다.",
            "session_id": session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.get("/templates/recommended")
async def get_recommended_templates(
    user_id: str,
    keywords: Optional[str] = None,
    limit: int = 5
):
    """추천 템플릿 조회"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        keyword_list = keywords.split(",") if keywords else []

        templates = await job_posting_agent.template_manager.get_recommended_templates(
            user_history=[user_id],
            current_context={"keywords": keyword_list}
        )

        # 템플릿 정보 변환
        template_data = []
        for template in templates[:limit]:
            template_data.append({
                "template_id": template.template_id,
                "name": template.name,
                "source": template.source.value,
                "content": template.content,
                "metadata": {
                    "usage_count": template.metadata["usage_count"],
                    "success_rate": template.metadata["success_rate"],
                    "rating": template.metadata["rating"],
                    "tags": template.metadata["tags"]
                }
            })

        return {
            "templates": template_data,
            "count": len(template_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommended templates: {str(e)}")

@router.get("/templates/popular")
async def get_popular_templates(limit: int = 10):
    """인기 템플릿 조회"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        templates = await job_posting_agent.template_manager.get_popular_templates(limit)

        # 템플릿 정보 변환
        template_data = []
        for template in templates:
            template_data.append({
                "template_id": template.template_id,
                "name": template.name,
                "source": template.source.value,
                "content": template.content,
                "metadata": {
                    "usage_count": template.metadata["usage_count"],
                    "success_rate": template.metadata["success_rate"],
                    "rating": template.metadata["rating"],
                    "tags": template.metadata["tags"]
                }
            })

        return {
            "templates": template_data,
            "count": len(template_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular templates: {str(e)}")

@router.post("/templates/generate")
async def generate_ai_template(
    keywords: List[str],
    requirements: Dict[str, Any]
):
    """AI 템플릿 생성"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        template = await job_posting_agent.template_manager.generate_ai_template(
            keywords=keywords,
            requirements=requirements
        )

        return {
            "template_id": template.template_id,
            "name": template.name,
            "source": template.source.value,
            "content": template.content,
            "metadata": {
                "usage_count": template.metadata["usage_count"],
                "success_rate": template.metadata["success_rate"],
                "rating": template.metadata["rating"],
                "tags": template.metadata["tags"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI template: {str(e)}")

@router.post("/templates/{template_id}/feedback")
async def submit_template_feedback(
    template_id: str,
    success: bool,
    rating: Optional[float] = None,
    comment: Optional[str] = None
):
    """템플릿 사용 피드백 제출"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        feedback = {}
        if rating is not None:
            feedback["rating"] = rating
        if comment:
            feedback["comment"] = comment

        await job_posting_agent.template_manager.learn_from_usage(
            template_id=template_id,
            success=success,
            feedback=feedback if feedback else None
        )

        return {
            "message": "피드백이 성공적으로 제출되었습니다.",
            "template_id": template_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.get("/job-postings")
async def get_user_job_postings(user_id: str, limit: int = 20):
    """사용자의 채용공고 목록 조회"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        collection = job_posting_agent.db.job_postings

        # 사용자의 공고 조회
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)

        job_postings = []
        async for doc in cursor:
            job_postings.append({
                "id": str(doc["_id"]),
                "title": doc["content"]["title"],
                "company_info": doc["company_info"],
                "status": doc["status"],
                "created_at": doc["created_at"],
                "updated_at": doc["updated_at"]
            })

        return {
            "job_postings": job_postings,
            "count": len(job_postings)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job postings: {str(e)}")

@router.get("/job-postings/{job_posting_id}")
async def get_job_posting_detail(job_posting_id: str):
    """채용공고 상세 조회"""
    try:
        if not job_posting_agent:
            raise HTTPException(status_code=500, detail="Job posting agent not initialized")

        from bson import ObjectId

        collection = job_posting_agent.db.job_postings
        doc = await collection.find_one({"_id": ObjectId(job_posting_id)})

        if not doc:
            raise HTTPException(status_code=404, detail="Job posting not found")

        return {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "company_info": doc["company_info"],
            "content": doc["content"],
            "template_id": doc["template_id"],
            "keywords": doc["keywords"],
            "status": doc["status"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job posting: {str(e)}")

# 에이전트 초기화 엔드포인트
@router.post("/init")
async def initialize_agent():
    """에이전트 초기화 (개발용)"""
    try:
        from ..modules.job_posting.job_posting_agent import init_job_posting_agent
        from ..modules.job_posting.dynamic_templates import init_dynamic_template_manager

        mongo_client = get_mongo_client()

        # 동적 템플릿 매니저 초기화
        await init_dynamic_template_manager(mongo_client)

        # 채용공고 에이전트 초기화
        await init_job_posting_agent(mongo_client)

        return {
            "message": "Job posting agent initialized successfully",
            "status": "ready"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
