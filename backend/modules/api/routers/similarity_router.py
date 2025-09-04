import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...core.models.similarity_models import (
    DocumentType,
    PlagiarismAnalysis,
    SearchRequest,
    SearchResult,
    SimilarityLevel,
    SimilarityResult,
)
from ...core.services.embedding_service import EmbeddingService
from ...core.services.keyword_search_service import KeywordSearchService
from ...core.services.llm_service import LLMService
from ...core.services.similarity_service import SimilarityService
from ...core.services.vector_service import VectorService

router = APIRouter(prefix="/similarity", tags=["similarity"])

def get_similarity_service() -> SimilarityService:
    """유사도 분석 서비스 의존성 주입"""
    embedding_service = EmbeddingService()
    vector_service = VectorService()
    keyword_search_service = KeywordSearchService()
    llm_service = LLMService()

    return SimilarityService(
        embedding_service=embedding_service,
        vector_service=vector_service,
        llm_service=llm_service
    )

@router.post("/check-plagiarism/{document_id}", response_model=PlagiarismAnalysis)
async def check_plagiarism(
    document_id: str,
    document_type: DocumentType = DocumentType.COVER_LETTER,
    limit: int = Query(default=10, ge=1, le=50),
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    자소서 표절 위험도 체크

    Args:
        document_id: 문서 ID
        document_type: 문서 타입 (cover_letter, resume, portfolio)
        limit: 검색할 최대 문서 수
        similarity_service: 유사도 분석 서비스

    Returns:
        PlagiarismAnalysis: 표절 분석 결과
    """
    try:
        start_time = time.time()

        # MongoDB 컬렉션 가져오기
        from modules.core.services.mongo_service import MongoService
        mongo_service = MongoService()

        # 유사 문서 검색
        result = await similarity_service.find_similar_documents_by_chunks(
            document_id=document_id,
            collection=mongo_service.db.applicants,  # 지원자 컬렉션 사용
            document_type=document_type.value,
            limit=limit
        )

        if not result.get("success"):
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

        similar_documents = result.get("similar_documents", [])

        # LLM을 통한 표절 위험도 분석
        if similar_documents:
            plagiarism_analysis = await similarity_service.llm_service.analyze_plagiarism_suspicion(
                original_resume=None,  # 실제 구현에서는 원본 문서 주입 필요
                similar_resumes=similar_documents,
                document_type="자소서" if document_type == DocumentType.COVER_LETTER else "이력서"
            )
        else:
            plagiarism_analysis = {
                "success": True,
                "suspicion_level": SimilarityLevel.LOW,
                "suspicion_score": 0.0,
                "suspicion_score_percent": 0,
                "analysis": "유사한 문서가 발견되지 않았습니다.",
                "recommendations": [],
                "similar_count": 0,
                "analyzed_at": datetime.now().isoformat()
            }

        execution_time = time.time() - start_time

        return PlagiarismAnalysis(
            suspicion_level=SimilarityLevel(plagiarism_analysis["suspicion_level"]),
            suspicion_score=plagiarism_analysis["suspicion_score"],
            suspicion_score_percent=plagiarism_analysis["suspicion_score_percent"],
            analysis=plagiarism_analysis["analysis"],
            recommendations=plagiarism_analysis["recommendations"],
            similar_count=plagiarism_analysis["similar_count"],
            analyzed_at=datetime.fromisoformat(plagiarism_analysis["analyzed_at"])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"표절 검사 중 오류가 발생했습니다: {str(e)}")

@router.post("/search-similar", response_model=SearchResult)
async def search_similar_documents(
    request: SearchRequest,
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    유사 문서 검색

    Args:
        request: 검색 요청
        similarity_service: 유사도 분석 서비스

    Returns:
        SearchResult: 검색 결과
    """
    try:
        start_time = time.time()

        # 하이브리드 검색 수행
        if request.use_hybrid_search:
            result = await similarity_service.search_resumes_multi_hybrid(
                query=request.query,
                collection=None,  # 실제 구현에서는 컬렉션 주입 필요
                search_type=request.document_type.value,
                limit=request.limit
            )
        else:
            # 단순 벡터 검색
            result = await similarity_service._perform_vector_search(
                query=request.query,
                collection=None,
                search_type=request.document_type.value,
                limit=request.limit
            )
            result = {
                "success": True,
                "data": {
                    "query": request.query,
                    "search_method": "vector_only",
                    "weights": {"vector": 1.0, "keyword": 0.0},
                    "results": result,
                    "total": len(result),
                    "vector_count": len(result),
                    "keyword_count": 0
                }
            }

        execution_time = time.time() - start_time

        if not result.get("success"):
            raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")

        data = result["data"]

        # 결과를 SimilarityResult 모델로 변환
        similarity_results = []
        for item in data["results"]:
            similarity_result = SimilarityResult(
                document_id=str(item.get("_id", "")),
                document_name=item.get("name", ""),
                overall_similarity=item.get("similarity_score", 0.0),
                field_similarities=item.get("field_similarities", {}),
                chunk_matches=item.get("chunk_matches", 0),
                chunk_details=item.get("chunk_details", []),
                is_high_similarity=item.get("similarity_score", 0.0) > 0.7,
                is_moderate_similarity=0.4 <= item.get("similarity_score", 0.0) <= 0.7,
                is_low_similarity=item.get("similarity_score", 0.0) < 0.4,
                llm_analysis=item.get("llm_analysis"),
                analyzed_at=datetime.now()
            )
            similarity_results.append(similarity_result)

        return SearchResult(
            query=data["query"],
            search_method=data["search_method"],
            weights=data["weights"],
            results=similarity_results,
            total=data["total"],
            vector_count=data["vector_count"],
            keyword_count=data["keyword_count"],
            execution_time=execution_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@router.post("/compare-documents")
async def compare_documents(
    document1_id: str,
    document2_id: str,
    document_type: DocumentType = DocumentType.RESUME,
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    두 문서 간 유사도 비교

    Args:
        document1_id: 첫 번째 문서 ID
        document2_id: 두 번째 문서 ID
        document_type: 문서 타입
        similarity_service: 유사도 분석 서비스

    Returns:
        Dict[str, Any]: 비교 결과
    """
    try:
        # 실제 구현에서는 두 문서를 가져와서 비교
        # 여기서는 예시 응답만 반환
        similarity_score = 0.75  # 실제로는 계산된 값

        return {
            "document1_id": document1_id,
            "document2_id": document2_id,
            "document_type": document_type.value,
            "similarity_score": similarity_score,
            "similarity_level": SimilarityUtils.classify_similarity_level(similarity_score),
            "field_similarities": {
                "growthBackground": 0.8,
                "motivation": 0.7,
                "careerHistory": 0.6
            },
            "compared_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 비교 중 오류가 발생했습니다: {str(e)}")

@router.post("/batch-similarity-check")
async def batch_similarity_check(
    document_ids: List[str],
    document_type: DocumentType = DocumentType.RESUME,
    similarity_threshold: float = Query(default=0.3, ge=0.0, le=1.0),
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    배치 유사도 검사

    Args:
        document_ids: 문서 ID 리스트
        document_type: 문서 타입
        similarity_threshold: 유사도 임계값
        similarity_service: 유사도 분석 서비스

    Returns:
        Dict[str, Any]: 배치 검사 결과
    """
    try:
        results = []

        for doc_id in document_ids:
            try:
                # 각 문서에 대해 유사도 검사 수행
                result = await similarity_service.find_similar_documents_by_chunks(
                    document_id=doc_id,
                    collection=None,  # 실제 구현에서는 컬렉션 주입 필요
                    document_type=document_type.value,
                    limit=10
                )

                results.append({
                    "document_id": doc_id,
                    "success": result.get("success", False),
                    "similar_count": len(result.get("similar_documents", [])),
                    "max_similarity": max([doc.get("similarity_score", 0) for doc in result.get("similar_documents", [])], default=0),
                    "above_threshold": any(doc.get("similarity_score", 0) >= similarity_threshold for doc in result.get("similar_documents", []))
                })

            except Exception as e:
                results.append({
                    "document_id": doc_id,
                    "success": False,
                    "error": str(e),
                    "similar_count": 0,
                    "max_similarity": 0,
                    "above_threshold": False
                })

        return {
            "total_documents": len(document_ids),
            "successful_checks": len([r for r in results if r["success"]]),
            "failed_checks": len([r for r in results if not r["success"]]),
            "documents_above_threshold": len([r for r in results if r.get("above_threshold", False)]),
            "results": results,
            "processed_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 검사 중 오류가 발생했습니다: {str(e)}")

@router.get("/metrics")
async def get_similarity_metrics(
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    유사도 분석 메트릭 조회

    Args:
        similarity_service: 유사도 분석 서비스

    Returns:
        Dict[str, Any]: 메트릭 정보
    """
    try:
        # 실제 구현에서는 데이터베이스에서 통계 정보를 가져옴
        return {
            "total_documents": 1000,
            "total_embeddings": 5000,
            "average_similarity": 0.67,
            "high_similarity_count": 150,
            "medium_similarity_count": 300,
            "low_similarity_count": 550,
            "plagiarism_suspicious_count": 25,
            "last_updated": datetime.now().isoformat(),
            "search_performance": {
                "average_response_time": 0.85,
                "vector_search_success_rate": 0.98,
                "keyword_search_success_rate": 0.95,
                "hybrid_search_success_rate": 0.99
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/save-document-chunks")
async def save_document_chunks(
    document: Dict[str, Any],
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    문서 청킹 및 벡터 저장

    Args:
        document: 저장할 문서
        similarity_service: 유사도 분석 서비스

    Returns:
        Dict[str, Any]: 저장 결과
    """
    try:
        result = await similarity_service.save_resume_chunks(document)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "저장 실패"))

        return {
            "success": True,
            "document_id": str(document.get("_id", "")),
            "chunks_count": result.get("chunks_count", 0),
            "vector_ids": result.get("stored_vector_ids", []),
            "elasticsearch_indexed": result.get("elasticsearch_indexed", False),
            "saved_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 저장 중 오류가 발생했습니다: {str(e)}")

@router.delete("/delete-document/{document_id}")
async def delete_document(
    document_id: str,
    similarity_service: SimilarityService = Depends(get_similarity_service)
):
    """
    문서 및 관련 벡터 삭제

    Args:
        document_id: 삭제할 문서 ID
        similarity_service: 유사도 분석 서비스

    Returns:
        Dict[str, Any]: 삭제 결과
    """
    try:
        # 실제 구현에서는 문서와 관련된 모든 벡터를 삭제
        result = await similarity_service.delete_resume_chunks(document_id)

        return {
            "success": result.get("success", False),
            "document_id": document_id,
            "vectors_deleted": result.get("vectors_deleted", 0),
            "elasticsearch_deleted": result.get("elasticsearch_deleted", False),
            "deleted_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류가 발생했습니다: {str(e)}")
