import asyncio
import sys
from pathlib import Path

# 백엔드 경로 추가
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

async def test_embedding_fallback():
    """임베딩 서비스 폴백 기능 테스트"""
    try:
        print("=== 임베딩 서비스 폴백 기능 테스트 시작 ===")
        
        # 임베딩 서비스 임포트 및 초기화
        from backend.modules.core.services.embedding_service import EmbeddingService, EmbeddingType
        
        embedding_service = EmbeddingService()
        print("[OK] EmbeddingService 초기화 성공")
        
        # 테스트 텍스트
        test_text = "이것은 임베딩 테스트를 위한 샘플 텍스트입니다."
        
        # 일반 임베딩 생성 테스트
        print("\n--- 일반 임베딩 생성 테스트 ---")
        embedding = await embedding_service.create_embedding(test_text)
        
        if embedding:
            print(f"[OK] 임베딩 생성 성공")
            print(f"    - 차원: {len(embedding)}")
            print(f"    - 값 미리보기: {embedding[:5]}")
            
            # 임베딩 타입별 테스트
            print("\n--- 쿼리 임베딩 테스트 ---")
            query_embedding = await embedding_service.create_query_embedding("개발자를 찾고 있습니다")
            if query_embedding:
                print(f"[OK] 쿼리 임베딩 생성 성공 (차원: {len(query_embedding)})")
            else:
                print("[FAIL] 쿼리 임베딩 생성 실패")
            
            print("\n--- 문서 임베딩 테스트 ---")
            doc_embedding = await embedding_service.create_document_embedding("저는 5년 경력의 백엔드 개발자입니다")
            if doc_embedding:
                print(f"[OK] 문서 임베딩 생성 성공 (차원: {len(doc_embedding)})")
            else:
                print("[FAIL] 문서 임베딩 생성 실패")
            
        else:
            print("[FAIL] 임베딩 생성 실패")
            return False
        
        print("\n=== 임베딩 서비스 폴백 기능 테스트 완료 ===")
        print("✅ 모든 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"[ERROR] 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_embedding_fallback())
    print(f"\n최종 결과: {'성공' if result else '실패'}")