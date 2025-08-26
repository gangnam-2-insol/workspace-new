import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from ..core.models.similarity_models import (
    DocumentType,
    PlagiarismAnalysis,
    SimilarityResult,
)
from ..core.services.embedding_service import EmbeddingService
from ..core.services.llm_service import LLMService
from ..core.services.similarity_service import SimilarityService
from ..core.services.vector_service import VectorService


class TestSimilarityService:
    """유사도 서비스 테스트 클래스"""

    @pytest.fixture
    def mock_embedding_service(self):
        """Mock 임베딩 서비스"""
        service = Mock(spec=EmbeddingService)
        service.create_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return service

    @pytest.fixture
    def mock_vector_service(self):
        """Mock 벡터 서비스"""
        service = Mock(spec=VectorService)
        service.save_chunk_vectors = AsyncMock(return_value=["vec_1", "vec_2"])
        service.search_similar_chunks = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM 서비스"""
        service = Mock(spec=LLMService)
        service.analyze_plagiarism_suspicion = AsyncMock(return_value={
            "success": True,
            "suspicion_level": "LOW",
            "suspicion_score": 0.1,
            "suspicion_score_percent": 10,
            "analysis": "테스트 분석",
            "recommendations": ["테스트 권장사항"],
            "similar_count": 0,
            "analyzed_at": "2024-01-01T00:00:00"
        })
        return service

    @pytest.fixture
    def similarity_service(self, mock_embedding_service, mock_vector_service, mock_llm_service):
        """유사도 서비스 인스턴스"""
        return SimilarityService(
            embedding_service=mock_embedding_service,
            vector_service=mock_vector_service,
            llm_service=mock_llm_service
        )

    @pytest.fixture
    def sample_resume(self):
        """테스트용 이력서 데이터"""
        return {
            "_id": "test_resume_id",
            "name": "테스트 지원자",
            "position": "백엔드 개발자",
            "department": "개발팀",
            "growthBackground": "성장 배경 테스트 내용입니다.",
            "motivation": "지원 동기 테스트 내용입니다.",
            "careerHistory": "경력 사항 테스트 내용입니다.",
            "skills": "Python, FastAPI, MongoDB",
            "experience": "3년"
        }

    @pytest.fixture
    def sample_collection(self):
        """Mock MongoDB 컬렉션"""
        collection = Mock()
        collection.find = Mock()
        collection.find_one = Mock()
        return collection

    @pytest.mark.asyncio
    async def test_save_resume_chunks_success(self, similarity_service, sample_resume):
        """이력서 청킹 및 저장 성공 테스트"""
        result = await similarity_service.save_resume_chunks(sample_resume)

        assert result["success"] is True
        assert "chunks_count" in result
        assert "stored_vector_ids" in result

    @pytest.mark.asyncio
    async def test_save_resume_chunks_empty_resume(self, similarity_service):
        """빈 이력서 처리 테스트"""
        empty_resume = {"_id": "empty_id"}

        result = await similarity_service.save_resume_chunks(empty_resume)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_find_similar_documents_by_chunks(self, similarity_service, sample_collection):
        """청킹 기반 유사 문서 검색 테스트"""
        # Mock 검색 결과
        mock_similar_docs = [
            {
                "_id": "similar_1",
                "name": "유사 지원자 1",
                "similarity_score": 0.8,
                "chunk_matches": 3
            },
            {
                "_id": "similar_2",
                "name": "유사 지원자 2",
                "similarity_score": 0.6,
                "chunk_matches": 2
            }
        ]

        similarity_service.vector_service.search_similar_chunks = AsyncMock(
            return_value=mock_similar_docs
        )

        result = await similarity_service.find_similar_documents_by_chunks(
            document_id="test_id",
            collection=sample_collection,
            document_type="resume",
            limit=5
        )

        assert result["success"] is True
        assert "similar_documents" in result
        assert len(result["similar_documents"]) == 2

    @pytest.mark.asyncio
    async def test_calculate_text_similarity(self, similarity_service):
        """텍스트 유사도 계산 테스트"""
        text1 = "Python 개발자입니다."
        text2 = "Python 프로그래머입니다."

        similarity = similarity_service._calculate_text_similarity(
            {"content": text1},
            {"content": text2}
        )

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_plagiarism_suspicion(self, similarity_service, mock_llm_service):
        """표절 의심도 분석 테스트"""
        similar_documents = [
            {
                "similarity_score": 0.85,
                "name": "유사 문서 1"
            },
            {
                "similarity_score": 0.75,
                "name": "유사 문서 2"
            }
        ]

        result = await similarity_service.llm_service.analyze_plagiarism_suspicion(
            original_resume={"name": "원본 문서"},
            similar_resumes=similar_documents,
            document_type="자소서"
        )

        assert result["success"] is True
        assert "suspicion_level" in result
        assert "suspicion_score" in result
        assert "analysis" in result

    @pytest.mark.asyncio
    async def test_search_resumes_multi_hybrid(self, similarity_service, sample_collection):
        """다중 하이브리드 검색 테스트"""
        # Mock 검색 결과
        mock_vector_results = [
            {"_id": "vec_1", "similarity_score": 0.8},
            {"_id": "vec_2", "similarity_score": 0.7}
        ]

        mock_keyword_results = [
            {"_id": "kw_1", "bm25_score": 0.9},
            {"_id": "kw_2", "bm25_score": 0.6}
        ]

        similarity_service._perform_vector_search = AsyncMock(
            return_value=mock_vector_results
        )
        similarity_service._perform_keyword_search = AsyncMock(
            return_value=mock_keyword_results
        )

        result = await similarity_service.search_resumes_multi_hybrid(
            query="Python 개발자",
            collection=sample_collection,
            search_type="resume",
            limit=10
        )

        assert result["success"] is True
        assert "data" in result
        assert "results" in result["data"]

    def test_similarity_threshold_configuration(self, similarity_service):
        """유사도 임계값 설정 테스트"""
        assert similarity_service.similarity_threshold == 0.3
        assert similarity_service.field_thresholds["growthBackground"] == 0.2
        assert similarity_service.field_thresholds["motivation"] == 0.2
        assert similarity_service.field_thresholds["careerHistory"] == 0.2

    def test_search_weights_configuration(self, similarity_service):
        """검색 가중치 설정 테스트"""
        assert similarity_service.search_weights["vector"] == 0.5
        assert similarity_service.search_weights["keyword"] == 0.5
        assert sum(similarity_service.search_weights.values()) == 1.0

    @pytest.mark.asyncio
    async def test_delete_resume_chunks(self, similarity_service):
        """이력서 청킹 삭제 테스트"""
        # Mock 삭제 결과
        similarity_service.vector_service.delete_chunk_vectors = AsyncMock(
            return_value={"success": True, "deleted_count": 5}
        )
        similarity_service.keyword_search_service.delete_document = AsyncMock(
            return_value={"success": True}
        )

        result = await similarity_service.delete_resume_chunks("test_resume_id")

        assert result["success"] is True
        assert "vectors_deleted" in result
        assert "elasticsearch_deleted" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, similarity_service, sample_resume):
        """에러 처리 테스트"""
        # Mock 에러 발생
        similarity_service.vector_service.save_chunk_vectors = AsyncMock(
            side_effect=Exception("벡터 저장 실패")
        )

        result = await similarity_service.save_resume_chunks(sample_resume)

        assert result["success"] is False
        assert "error" in result


class TestSimilarityModels:
    """유사도 모델 테스트 클래스"""

    def test_similarity_result_model(self):
        """SimilarityResult 모델 테스트"""
        result = SimilarityResult(
            document_id="test_id",
            document_name="테스트 문서",
            overall_similarity=0.75,
            field_similarities={"growthBackground": 0.8, "motivation": 0.7},
            chunk_matches=3,
            is_high_similarity=True,
            is_moderate_similarity=False,
            is_low_similarity=False
        )

        assert result.document_id == "test_id"
        assert result.overall_similarity == 0.75
        assert result.is_high_similarity is True

    def test_plagiarism_analysis_model(self):
        """PlagiarismAnalysis 모델 테스트"""
        analysis = PlagiarismAnalysis(
            suspicion_level="MEDIUM",
            suspicion_score=0.65,
            suspicion_score_percent=65,
            analysis="테스트 분석",
            recommendations=["권장사항 1", "권장사항 2"],
            similar_count=3
        )

        assert analysis.suspicion_level == "MEDIUM"
        assert analysis.suspicion_score == 0.65
        assert analysis.suspicion_score_percent == 65
        assert len(analysis.recommendations) == 2

    def test_document_type_enum(self):
        """DocumentType 열거형 테스트"""
        assert DocumentType.RESUME == "resume"
        assert DocumentType.COVER_LETTER == "cover_letter"
        assert DocumentType.PORTFOLIO == "portfolio"


if __name__ == "__main__":
    pytest.main([__file__])
