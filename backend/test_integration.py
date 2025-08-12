#!/usr/bin/env python3
"""
LLM 프로바이더 통합 테스트 스크립트

이 스크립트는 LLM 프로바이더 서비스의 통합 기능을 테스트합니다.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.llm_providers.base_provider import LLMProviderFactory
from services.llm_providers.openai_provider import OPENAI_CONFIG_EXAMPLE

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockProvider:
    """테스트용 Mock 프로바이더"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "mock-model")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.1)
        self.is_available = True
    
    async def generate_response(self, prompt: str, **kwargs):
        from services.llm_providers.base_provider import LLMResponse
        from datetime import datetime
        
        # Mock 응답 생성
        mock_content = f"Mock 응답: {prompt[:50]}..."
        
        return LLMResponse(
            content=mock_content,
            provider="mock",
            model=self.model_name,
            metadata={"mock": True, "prompt_length": len(prompt)},
            start_time=datetime.now(),
            end_time=datetime.now()
        )
    
    def is_healthy(self) -> bool:
        return self.is_available


async def test_provider_registration():
    """프로바이더 등록 테스트"""
    logger.info("=== 프로바이더 등록 테스트 ===")
    
    # Mock 프로바이더 등록
    LLMProviderFactory.register_provider("mock", MockProvider)
    
    # 등록된 프로바이더 확인
    available_providers = LLMProviderFactory.get_available_providers()
    logger.info(f"등록된 프로바이더: {available_providers}")
    
    # Mock 프로바이더 정보 확인
    mock_info = LLMProviderFactory.get_provider_info("mock")
    logger.info(f"Mock 프로바이더 정보: {mock_info}")
    
    return "mock" in available_providers


async def test_provider_creation():
    """프로바이더 생성 테스트"""
    logger.info("=== 프로바이더 생성 테스트 ===")
    
    # Mock 프로바이더 생성
    config = {
        "provider": "mock",
        "model_name": "test-model",
        "max_tokens": 500,
        "temperature": 0.5
    }
    
    provider = LLMProviderFactory.create_provider("mock", config)
    
    if provider:
        logger.info(f"프로바이더 생성 성공: {provider.__class__.__name__}")
        logger.info(f"모델명: {provider.model_name}")
        logger.info(f"상태: {provider.is_healthy()}")
        return True
    else:
        logger.error("프로바이더 생성 실패")
        return False


async def test_response_generation():
    """응답 생성 테스트"""
    logger.info("=== 응답 생성 테스트 ===")
    
    # Mock 프로바이더 생성
    config = {"provider": "mock", "model_name": "test-model"}
    provider = LLMProviderFactory.create_provider("mock", config)
    
    if not provider:
        logger.error("프로바이더 생성 실패")
        return False
    
    # 테스트 프롬프트
    test_prompts = [
        "안녕하세요!",
        "자기소개서를 분석해주세요.",
        "이력서의 장점과 개선점을 알려주세요."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"테스트 {i}: {prompt}")
        
        try:
            response = await provider.generate_response(prompt)
            
            logger.info(f"  응답: {response.content}")
            logger.info(f"  프로바이더: {response.provider}")
            logger.info(f"  모델: {response.model}")
            logger.info(f"  응답 시간: {response.response_time:.2f}초")
            
            if response.metadata:
                logger.info(f"  메타데이터: {response.metadata}")
                
        except Exception as e:
            logger.error(f"  응답 생성 실패: {str(e)}")
            return False
    
    return True


async def test_safe_generation():
    """안전한 응답 생성 테스트"""
    logger.info("=== 안전한 응답 생성 테스트 ===")
    
    config = {"provider": "mock", "model_name": "test-model"}
    provider = LLMProviderFactory.create_provider("mock", config)
    
    if not provider:
        return False
    
    # 정상 프롬프트
    response = await provider.safe_generate("정상 프롬프트")
    if response:
        logger.info(f"정상 응답: {response.content}")
    else:
        logger.error("정상 프롬프트에서 응답 생성 실패")
        return False
    
    # 빈 프롬프트 (유효성 검사 실패)
    response = await provider.safe_generate("")
    if response is None:
        logger.info("빈 프롬프트에 대한 적절한 처리 확인")
    else:
        logger.warning("빈 프롬프트에 대한 처리가 예상과 다릅니다")
    
    return True


async def test_config_validation():
    """설정 검증 테스트"""
    logger.info("=== 설정 검증 테스트 ===")
    
    config = {"provider": "mock", "model_name": "test-model"}
    provider = LLMProviderFactory.create_provider("mock", config)
    
    if not provider:
        return False
    
    # 프롬프트 유효성 검사
    valid_prompt = "유효한 프롬프트입니다."
    invalid_prompt = "x" * 10000  # 너무 긴 프롬프트
    
    # 유효한 프롬프트
    if provider.validate_prompt(valid_prompt):
        logger.info("유효한 프롬프트 검증 성공")
    else:
        logger.error("유효한 프롬프트 검증 실패")
        return False
    
    # 유효하지 않은 프롬프트
    if not provider.validate_prompt(invalid_prompt):
        logger.info("유효하지 않은 프롬프트 검증 성공")
    else:
        logger.error("유효하지 않은 프롬프트 검증 실패")
        return False
    
    return True


async def main():
    """메인 테스트 함수"""
    logger.info("=== LLM 프로바이더 통합 테스트 시작 ===")
    
    test_results = []
    
    try:
        # 각 테스트 실행
        tests = [
            ("프로바이더 등록", test_provider_registration),
            ("프로바이더 생성", test_provider_creation),
            ("응답 생성", test_response_generation),
            ("안전한 응답 생성", test_safe_generation),
            ("설정 검증", test_config_validation)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n{test_name} 테스트 실행 중...")
            try:
                result = await test_func()
                test_results.append((test_name, result))
                if result:
                    logger.info(f"✅ {test_name} 테스트 성공")
                else:
                    logger.error(f"❌ {test_name} 테스트 실패")
            except Exception as e:
                logger.error(f"❌ {test_name} 테스트 중 오류: {str(e)}")
                test_results.append((test_name, False))
        
        # 결과 요약
        logger.info("\n=== 테스트 결과 요약 ===")
        success_count = sum(1 for _, result in test_results if result)
        total_count = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 성공" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n전체 결과: {success_count}/{total_count} 성공")
        
        if success_count == total_count:
            logger.info("🎉 모든 테스트가 성공했습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")
            
    except KeyboardInterrupt:
        logger.info("테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Windows에서 asyncio 이벤트 루프 정책 설정
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 메인 테스트 실행
    asyncio.run(main())
