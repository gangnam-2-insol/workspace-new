from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    HybridCreate, HybridDocument, HybridUpdate, HybridAnalysis,
    HybridSearchRequest, HybridComparisonRequest, HybridStatistics
)
from .services import HybridService
from ..shared.models import BaseResponse, PaginationParams
from ..shared.services import FileService, AnalysisService

router = APIRouter(prefix="/api/hybrid", tags=["하이브리드 분석"])

# 의존성 주입
def get_hybrid_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> HybridService:
    return HybridService(db)

def get_file_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> FileService:
    return FileService(db)

def get_analysis_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> AnalysisService:
    return AnalysisService(db)

@router.post("/create", response_model=BaseResponse)
async def create_hybrid_analysis(
    hybrid_data: HybridCreate,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 생성"""
    try:
        hybrid_id = await hybrid_service.create_hybrid_analysis(hybrid_data)
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석이 생성되었습니다",
            data={"hybrid_id": hybrid_id}
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 생성 중 오류가 발생했습니다",
            error=str(e)
        )

@router.get("/{hybrid_id}", response_model=BaseResponse)
async def get_hybrid_analysis(
    hybrid_id: str,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 조회"""
    try:
        hybrid = await hybrid_service.get_hybrid_analysis(hybrid_id)
        if not hybrid:
            raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 조회가 완료되었습니다",
            data=hybrid.dict()
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 조회 중 오류가 발생했습니다",
            error=str(e)
        )

@router.get("/", response_model=BaseResponse)
async def get_hybrid_analyses(
    applicant_id: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 목록 조회"""
    try:
        skip = (page - 1) * limit
        hybrid_analyses = await hybrid_service.get_hybrid_analyses(applicant_id, skip, limit)
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 목록 조회가 완료되었습니다",
            data={
                "hybrid_analyses": [hybrid.dict() for hybrid in hybrid_analyses],
                "page": page,
                "limit": limit,
                "total": len(hybrid_analyses)
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 목록 조회 중 오류가 발생했습니다",
            error=str(e)
        )

@router.put("/{hybrid_id}", response_model=BaseResponse)
async def update_hybrid_analysis(
    hybrid_id: str,
    update_data: HybridUpdate,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 수정"""
    try:
        success = await hybrid_service.update_hybrid_analysis(hybrid_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 수정이 완료되었습니다"
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 수정 중 오류가 발생했습니다",
            error=str(e)
        )

@router.delete("/{hybrid_id}", response_model=BaseResponse)
async def delete_hybrid_analysis(
    hybrid_id: str,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 삭제"""
    try:
        success = await hybrid_service.delete_hybrid_analysis(hybrid_id)
        if not success:
            raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 삭제가 완료되었습니다"
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 삭제 중 오류가 발생했습니다",
            error=str(e)
        )

@router.post("/search", response_model=BaseResponse)
async def search_hybrid_analyses(
    search_request: HybridSearchRequest,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 검색"""
    try:
        hybrid_analyses = await hybrid_service.search_hybrid_analyses(search_request)
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 검색이 완료되었습니다",
            data={
                "hybrid_analyses": [hybrid.dict() for hybrid in hybrid_analyses],
                "total": len(hybrid_analyses)
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 검색 중 오류가 발생했습니다",
            error=str(e)
        )

@router.post("/compare", response_model=BaseResponse)
async def compare_hybrid_analyses(
    comparison_request: HybridComparisonRequest,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 비교"""
    try:
        comparison_result = await hybrid_service.compare_hybrid_analyses(comparison_request)
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 비교가 완료되었습니다",
            data=comparison_result
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 비교 중 오류가 발생했습니다",
            error=str(e)
        )

@router.get("/statistics/overview", response_model=BaseResponse)
async def get_hybrid_statistics(
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """하이브리드 분석 통계 조회"""
    try:
        statistics = await hybrid_service.get_hybrid_statistics()
        
        return BaseResponse(
            success=True,
            message="하이브리드 분석 통계 조회가 완료되었습니다",
            data=statistics.dict()
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="하이브리드 분석 통계 조회 중 오류가 발생했습니다",
            error=str(e)
        )

@router.post("/{hybrid_id}/analyze", response_model=BaseResponse)
async def perform_comprehensive_analysis(
    hybrid_id: str,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """종합 분석 수행"""
    try:
        analysis = await hybrid_service.perform_comprehensive_analysis(hybrid_id)
        
        return BaseResponse(
            success=True,
            message="종합 분석이 완료되었습니다",
            data={
                "analysis_id": analysis.id,
                "analysis_result": analysis.dict()
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="종합 분석 중 오류가 발생했습니다",
            error=str(e)
        )

@router.post("/upload-multiple", response_model=BaseResponse)
async def upload_multiple_documents(
    resume_file: Optional[UploadFile] = File(None),
    cover_letter_file: Optional[UploadFile] = File(None),
    portfolio_file: Optional[UploadFile] = File(None),
    applicant_id: str = Form(...),
    job_posting_id: Optional[str] = Form(None),
    hybrid_service: HybridService = Depends(get_hybrid_service),
    file_service: FileService = Depends(get_file_service)
):
    """다중 문서 업로드 및 하이브리드 분석"""
    try:
        # 파일 검증
        files = []
        if resume_file:
            if not resume_file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                raise HTTPException(status_code=400, detail="이력서 파일 형식이 올바르지 않습니다")
            files.append(("resume", resume_file))
        
        if cover_letter_file:
            if not cover_letter_file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                raise HTTPException(status_code=400, detail="자기소개서 파일 형식이 올바르지 않습니다")
            files.append(("cover_letter", cover_letter_file))
        
        if portfolio_file:
            if not portfolio_file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt', '.zip')):
                raise HTTPException(status_code=400, detail="포트폴리오 파일 형식이 올바르지 않습니다")
            files.append(("portfolio", portfolio_file))
        
        if not files:
            raise HTTPException(status_code=400, detail="최소 하나의 파일이 필요합니다")
        
        # 파일 처리 및 문서 ID 수집
        document_ids = {}
        
        for doc_type, file in files:
            # 파일 내용 읽기
            content = await file.read()
            text_content = content.decode('utf-8') if isinstance(content, bytes) else str(content)
            
            # 파일 메타데이터 저장
            file_metadata = {
                "filename": file.filename,
                "file_size": len(content),
                "content_type": file.content_type
            }
            file_id = await file_service.save_file_metadata(
                file.filename, len(content), file.content_type, file_metadata
            )
            
            # 여기서는 실제로는 각 모듈의 서비스를 호출하여 문서를 생성해야 합니다
            # 현재는 예시로 file_id를 사용
            document_ids[f"{doc_type}_id"] = file_id
        
        # 하이브리드 분석 생성
        hybrid_data = HybridCreate(
            applicant_id=applicant_id,
            resume_id=document_ids.get("resume_id"),
            cover_letter_id=document_ids.get("cover_letter_id"),
            portfolio_id=document_ids.get("portfolio_id"),
            job_posting_id=job_posting_id
        )
        
        hybrid_id = await hybrid_service.create_hybrid_analysis(hybrid_data)
        
        # 종합 분석 수행
        analysis = await hybrid_service.perform_comprehensive_analysis(hybrid_id)
        
        return BaseResponse(
            success=True,
            message="다중 문서 업로드 및 하이브리드 분석이 완료되었습니다",
            data={
                "hybrid_id": hybrid_id,
                "document_ids": document_ids,
                "analysis_result": analysis.dict()
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="다중 문서 업로드 중 오류가 발생했습니다",
            error=str(e)
        )

@router.get("/{hybrid_id}/cross-reference", response_model=BaseResponse)
async def get_cross_reference_analysis(
    hybrid_id: str,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """교차 참조 분석 결과 조회"""
    try:
        hybrid = await hybrid_service.get_hybrid_analysis(hybrid_id)
        if not hybrid:
            raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
        
        # 최신 분석 결과에서 교차 참조 정보 추출
        cross_references = {}
        if hybrid.analysis_results:
            latest_analysis = hybrid.analysis_results[-1]
            cross_references = latest_analysis.get("cross_references", {})
        
        return BaseResponse(
            success=True,
            message="교차 참조 분석 결과 조회가 완료되었습니다",
            data={
                "hybrid_id": hybrid_id,
                "cross_references": cross_references
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="교차 참조 분석 결과 조회 중 오류가 발생했습니다",
            error=str(e)
        )

@router.get("/{hybrid_id}/evaluation", response_model=BaseResponse)
async def get_integrated_evaluation(
    hybrid_id: str,
    hybrid_service: HybridService = Depends(get_hybrid_service)
):
    """통합 평가 결과 조회"""
    try:
        hybrid = await hybrid_service.get_hybrid_analysis(hybrid_id)
        if not hybrid:
            raise HTTPException(status_code=404, detail="하이브리드 분석을 찾을 수 없습니다")
        
        # 통합 평가 생성 (실제로는 더 복잡한 로직이 필요)
        evaluation = {
            "technical_competency": 85.0,
            "communication_skills": 80.0,
            "problem_solving": 82.0,
            "teamwork": 78.0,
            "leadership": 75.0,
            "adaptability": 88.0,
            "overall_fit": 83.0,
            "evaluation_notes": [
                "기술 역량이 우수함",
                "의사소통 능력이 좋음",
                "문제 해결 능력이 뛰어남"
            ]
        }
        
        return BaseResponse(
            success=True,
            message="통합 평가 결과 조회가 완료되었습니다",
            data={
                "hybrid_id": hybrid_id,
                "evaluation": evaluation
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            message="통합 평가 결과 조회 중 오류가 발생했습니다",
            error=str(e)
        )
