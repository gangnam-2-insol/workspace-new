#!/usr/bin/env python3
"""
EmbeddingService 디버그 스크립트
"""

import os
import sys

# 환경변수 설정
os.environ["FAST_STARTUP"] = "true"
os.environ["LAZY_LOADING_ENABLED"] = "true"
os.environ["OPENAI_API_KEY"] = "test-key"

def debug_embedding_service():
    """EmbeddingService 디버그"""
    print("🔍 EmbeddingService 디버그 시작...")

    try:
        print("1. 모듈 import 시도...")
        from modules.core.services.embedding_service import EmbeddingService
        print("✅ 모듈 import 성공")

        print("2. EmbeddingService 인스턴스 생성 시도...")
        service = EmbeddingService()
        print("✅ EmbeddingService 인스턴스 생성 성공")

        print("3. 속성 확인...")
        print(f"   - lazy_loading: {getattr(service, 'lazy_loading', 'NOT FOUND')}")
        print(f"   - fallback_model: {getattr(service, 'fallback_model', 'NOT FOUND')}")
        print(f"   - settings: {getattr(service, 'settings', 'NOT FOUND')}")

        print("4. 메서드 확인...")
        print(f"   - _load_fallback_model: {hasattr(service, '_load_fallback_model')}")

        if hasattr(service, '_load_fallback_model'):
            print("5. _load_fallback_model 메서드 호출 시도...")
            service._load_fallback_model()
            print("✅ _load_fallback_model 메서드 호출 성공")
            print(f"   - fallback_model 상태: {service.fallback_model is not None}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_embedding_service()
