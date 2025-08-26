import asyncio

from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.llm_service import LLMService
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.vector_service import VectorService


async def test_similarity():
    try:
        print("🚀 유사도 기능 테스트 시작...")

        # 서비스 초기화
        embedding_service = EmbeddingService()
        vector_service = VectorService()
        llm_service = LLMService()
        similarity_service = SimilarityService(
            embedding_service=embedding_service,
            vector_service=vector_service,
            llm_service=llm_service
        )

        print("✅ 서비스 초기화 완료")

        # 간단한 검색 테스트
        result = await similarity_service.search_resumes_multi_hybrid(
            query="개발자",
            collection=None,
            search_type="resume",
            limit=3
        )

        print(f"검색 결과: {result}")
        print("✅ 유사도 검색 성공")
        return True

    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_similarity())
