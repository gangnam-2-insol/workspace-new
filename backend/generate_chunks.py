#!/usr/bin/env python3
"""
청크 데이터 생성 스크립트
- 지원자 데이터를 청크로 분할하여 벡터 저장
- Elasticsearch에 인덱싱
"""

import asyncio

from bson import ObjectId
from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.llm_service import LLMService
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.vector_service import VectorService
from motor.motor_asyncio import AsyncIOMotorClient


async def generate_chunks():
    """청크 데이터 생성"""
    try:
        print("🚀 청크 데이터 생성 시작...")

        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme

        # 서비스 초기화
        embedding_service = EmbeddingService()
        vector_service = VectorService()
        llm_service = LLMService()
        similarity_service = SimilarityService(
            embedding_service=embedding_service,
            vector_service=vector_service,
            llm_service=llm_service
        )

        # 지원자 데이터 조회
        applicants = await db.applicants.find({}).to_list(1000)
        print(f"📊 총 {len(applicants)}명의 지원자 데이터 발견")

        success_count = 0
        error_count = 0

        for i, applicant in enumerate(applicants):
            try:
                print(f"처리 중... {i+1}/{len(applicants)}: {applicant.get('name', 'Unknown')}")

                # 지원자 정보를 벡터로 저장
                await similarity_service._store_applicant_vector_if_needed(applicant)
                success_count += 1

                # 너무 빠르게 요청하지 않도록 대기
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"❌ 오류 발생: {applicant.get('name', 'Unknown')} - {str(e)}")
                error_count += 1

        print(f"\n✅ 청크 데이터 생성 완료!")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {error_count}개")

        client.close()

    except Exception as e:
        print(f"❌ 청크 데이터 생성 실패: {str(e)}")

if __name__ == "__main__":
    asyncio.run(generate_chunks())
