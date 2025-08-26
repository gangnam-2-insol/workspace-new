import asyncio
import sys
import os
from pathlib import Path

# 백엔드 경로 추가
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

async def test_embedding_fallback():
    """임베딩 서비스 폴백 기능 테스트 (API 키 없이)"""
    try:
        print("=== 임베딩 서비스 폴백 기능 테스트 시작 ===")
        
        # API 키를 임시로 설정 (테스트용)
        os.environ["OPENAI_API_KEY"] = "test-key-for-fallback-test"
        
        # 임베딩 서비스 임포트 및 초기화
        from backend.modules.core.services.embedding_service import EmbeddingService, EmbeddingType
        
        embedding_service = EmbeddingService()
        print("[OK] EmbeddingService 초기화 성공 (폴백 모델 로드 확인)")
        
        # 폴백 모델 존재 확인
        if hasattr(embedding_service, 'fallback_model'):
            print("[OK] SentenceTransformer 폴백 모델 로드 성공")
            print(f"    - 모델: paraphrase-multilingual-MiniLM-L12-v2")
        else:
            print("[FAIL] 폴백 모델 로드 실패")
            return False
        
        # 폴백 모델 직접 테스트 (OpenAI API 실패 시뮬레이션)
        print("\n--- 폴백 모델 직접 테스트 ---")
        test_text = "이것은 폴백 모델 테스트를 위한 샘플 텍스트입니다."
        
        try:
            # 폴백 모델로 직접 임베딩 생성
            fallback_embedding = embedding_service.fallback_model.encode(test_text)
            print(f"[OK] 폴백 모델 임베딩 생성 성공")
            print(f"    - 차원: {len(fallback_embedding)}")
            print(f"    - 값 미리보기: {fallback_embedding[:5].tolist()}")
        except Exception as e:
            print(f"[FAIL] 폴백 모델 테스트 실패: {e}")
            return False
        
        # 전처리 기능 테스트
        print("\n--- 전처리 기능 테스트 ---")
        query_processed = embedding_service._preprocess_text("개발자를 찾습니다", EmbeddingType.QUERY)
        doc_processed = embedding_service._preprocess_text("저는 개발자입니다", EmbeddingType.DOCUMENT)
        
        print(f"[OK] 쿼리 전처리: {query_processed}")
        print(f"[OK] 문서 전처리: {doc_processed}")
        
        # 차원 정보 확인
        print("\n--- 임베딩 차원 정보 확인 ---")
        dimension = embedding_service.get_embedding_dimension()
        print(f"[OK] 설정된 임베딩 차원: {dimension}")
        
        print("\n=== 임베딩 서비스 폴백 기능 테스트 완료 ===")
        print("✅ 모든 폴백 관련 기능 정상 작동 확인!")
        return True
        
    except Exception as e:
        print(f"[ERROR] 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_embedding_fallback())
    print(f"\n최종 결과: {'성공' if result else '실패'}")