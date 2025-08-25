from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    JobPostingCreate, JobPosting, JobPostingUpdate, JobPostingSearchRequest,
    JobPostingStatistics, AIJobPostingRequest, ImageJobPostingRequest,
    LangGraphJobPostingRequest, JobPostingTemplate, JobStatus
)
from .services import JobPostingService
from ..shared.models import BaseResponse, PaginationParams
import base64

router = APIRouter(prefix="/api/job-posting-module", tags=["채용공고"])

def get_job_posting_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> JobPostingService:
    return JobPostingService(db)

@router.post("/", response_model=BaseResponse)
async def create_job_posting(
    job_data: JobPostingCreate,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 생성"""
    try:
        job_id = await job_service.create_job_posting(job_data)
        return BaseResponse(
            success=True,
            message="채용공고가 성공적으로 생성되었습니다.",
            data={"job_id": job_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 생성에 실패했습니다: {str(e)}"
        )

@router.get("/{job_id}", response_model=BaseResponse)
async def get_job_posting(
    job_id: str,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 조회"""
    try:
        job_posting = await job_service.get_job_posting(job_id)
        if not job_posting:
            return BaseResponse(
                success=False,
                message="채용공고를 찾을 수 없습니다."
            )
        
        # 조회수 증가
        await job_service.increment_views(job_id)
        
        return BaseResponse(
            success=True,
            message="채용공고 조회 성공",
            data=job_posting.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 조회에 실패했습니다: {str(e)}"
        )

@router.get("/", response_model=BaseResponse)
async def get_job_postings(
    page: int = 1,
    limit: int = 10,
    status: Optional[JobStatus] = None,
    company: Optional[str] = None,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 목록 조회"""
    try:
        skip = (page - 1) * limit
        job_postings = await job_service.get_job_postings(skip, limit, status, company)
        
        return BaseResponse(
            success=True,
            message="채용공고 목록 조회 성공",
            data={
                "job_postings": [job.dict() for job in job_postings],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(job_postings)
                }
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 목록 조회에 실패했습니다: {str(e)}"
        )

@router.put("/{job_id}", response_model=BaseResponse)
async def update_job_posting(
    job_id: str,
    update_data: JobPostingUpdate,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 수정"""
    try:
        success = await job_service.update_job_posting(job_id, update_data)
        if not success:
            return BaseResponse(
                success=False,
                message="채용공고를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="채용공고가 성공적으로 수정되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 수정에 실패했습니다: {str(e)}"
        )

@router.delete("/{job_id}", response_model=BaseResponse)
async def delete_job_posting(
    job_id: str,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 삭제"""
    try:
        success = await job_service.delete_job_posting(job_id)
        if not success:
            return BaseResponse(
                success=False,
                message="채용공고를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="채용공고가 성공적으로 삭제되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 삭제에 실패했습니다: {str(e)}"
        )

@router.patch("/{job_id}/publish", response_model=BaseResponse)
async def publish_job_posting(
    job_id: str,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 발행"""
    try:
        success = await job_service.publish_job_posting(job_id)
        if not success:
            return BaseResponse(
                success=False,
                message="채용공고를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="채용공고가 성공적으로 발행되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 발행에 실패했습니다: {str(e)}"
        )

@router.patch("/{job_id}/close", response_model=BaseResponse)
async def close_job_posting(
    job_id: str,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 마감"""
    try:
        success = await job_service.close_job_posting(job_id)
        if not success:
            return BaseResponse(
                success=False,
                message="채용공고를 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="채용공고가 성공적으로 마감되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 마감에 실패했습니다: {str(e)}"
        )

@router.post("/search", response_model=BaseResponse)
async def search_job_postings(
    search_request: JobPostingSearchRequest,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 검색"""
    try:
        job_postings = await job_service.search_job_postings(search_request)
        
        return BaseResponse(
            success=True,
            message="채용공고 검색 성공",
            data={
                "job_postings": [job.dict() for job in job_postings],
                "total": len(job_postings)
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 검색에 실패했습니다: {str(e)}"
        )

@router.get("/stats/overview", response_model=BaseResponse)
async def get_job_posting_statistics(
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 통계 조회"""
    try:
        statistics = await job_service.get_job_posting_statistics()
        
        return BaseResponse(
            success=True,
            message="채용공고 통계 조회 성공",
            data=statistics.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 통계 조회에 실패했습니다: {str(e)}"
        )

@router.post("/ai/create", response_model=BaseResponse)
async def create_ai_job_posting(
    ai_request: AIJobPostingRequest,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """AI 기반 채용공고 생성"""
    try:
        job_posting = await job_service.create_ai_job_posting(ai_request)
        
        return BaseResponse(
            success=True,
            message="AI 기반 채용공고가 성공적으로 생성되었습니다.",
            data=job_posting.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"AI 기반 채용공고 생성에 실패했습니다: {str(e)}"
        )

@router.post("/image/create", response_model=BaseResponse)
async def create_image_job_posting(
    image_request: ImageJobPostingRequest,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """이미지 기반 채용공고 생성"""
    try:
        job_posting = await job_service.create_image_job_posting(image_request)
        
        return BaseResponse(
            success=True,
            message="이미지 기반 채용공고가 성공적으로 생성되었습니다.",
            data=job_posting.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이미지 기반 채용공고 생성에 실패했습니다: {str(e)}"
        )

@router.post("/langgraph/create", response_model=BaseResponse)
async def create_langgraph_job_posting(
    langgraph_request: LangGraphJobPostingRequest,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """LangGraph 기반 채용공고 생성"""
    try:
        job_posting = await job_service.create_langgraph_job_posting(langgraph_request)
        
        return BaseResponse(
            success=True,
            message="LangGraph 기반 채용공고가 성공적으로 생성되었습니다.",
            data=job_posting.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"LangGraph 기반 채용공고 생성에 실패했습니다: {str(e)}"
        )

@router.get("/templates", response_model=BaseResponse)
async def get_job_posting_templates(
    category: Optional[str] = None,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 템플릿 조회"""
    try:
        templates = await job_service.get_job_posting_templates(category)
        
        return BaseResponse(
            success=True,
            message="채용공고 템플릿 조회 성공",
            data=[template.dict() for template in templates]
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 템플릿 조회에 실패했습니다: {str(e)}"
        )

@router.post("/templates", response_model=BaseResponse)
async def create_job_posting_template(
    template_data: JobPostingTemplate,
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """채용공고 템플릿 생성"""
    try:
        template_id = await job_service.create_job_posting_template(template_data)
        
        return BaseResponse(
            success=True,
            message="채용공고 템플릿이 성공적으로 생성되었습니다.",
            data={"template_id": template_id}
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 템플릿 생성에 실패했습니다: {str(e)}"
        )

@router.post("/upload-image", response_model=BaseResponse)
async def upload_job_posting_image(
    image_file: UploadFile = File(...),
    company: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None),
    job_service: JobPostingService = Depends(get_job_posting_service)
):
    """이미지 업로드를 통한 채용공고 생성"""
    try:
        # 이미지 파일을 base64로 인코딩
        image_content = await image_file.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        image_request = ImageJobPostingRequest(
            image_file=image_base64,
            company=company,
            additional_info=additional_info
        )
        
        job_posting = await job_service.create_image_job_posting(image_request)
        
        return BaseResponse(
            success=True,
            message="이미지 업로드를 통한 채용공고가 성공적으로 생성되었습니다.",
            data=job_posting.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"이미지 업로드를 통한 채용공고 생성에 실패했습니다: {str(e)}"
        )
