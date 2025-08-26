#!/usr/bin/env python3
"""
모든 지원자 벡터에 text 필드를 추가하는 업데이트 스크립트
"""
import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from modules.core.services.mongo_service import MongoService
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.vector_service import VectorService

async def update_all_applicant_vectors():
    """모든 지원자 벡터에 text 필드 추가"""
    print("=== 지원자 벡터 text 필드 업데이트 시작 ===")
    
    # MongoDB 연결
    mongo_service = MongoService()
    applicants_collection = mongo_service.db.applicants
    
    # 서비스들 초기화
    embedding_service = EmbeddingService()
    vector_service = VectorService()
    similarity_service = SimilarityService(embedding_service, vector_service)
    
    # 모든 지원자 조회
    applicants = await applicants_collection.find({}).to_list(1000)
    print(f"총 {len(applicants)}명의 지원자 벡터 업데이트 예정")
    
    success_count = 0
    for i, applicant in enumerate(applicants, 1):
        try:
            print(f"\n[{i}/{len(applicants)}] 처리 중: {applicant.get('name', 'Unknown')}")
            
            # 각 지원자 벡터 업데이트 (text 필드 추가)
            result = await similarity_service._store_applicant_vector_if_needed(applicant)
            if result:
                success_count += 1
                print(f"  OK 성공")
            else:
                print(f"  FAIL 실패")
                
        except Exception as e:
            print(f"  ERROR 오류: {e}")
    
    print(f"\n=== 업데이트 완료 ===")
    print(f"성공: {success_count}/{len(applicants)}")

if __name__ == "__main__":
    asyncio.run(update_all_applicant_vectors())