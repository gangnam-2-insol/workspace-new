#!/usr/bin/env python3
"""
OpenAI 프로바이더 테스트 스크립트

이 스크립트는 OpenAI 프로바이더의 기능을 테스트합니다.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.llm_providers.openai_provider import OpenAIProvider, OPENAI_CONFIG_EXAMPLE
from services.llm_providers.base_provider import LLMProviderFactory

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_openai_provider():
    """OpenAI 프로바이더 테스트"""
    logger.info("OpenAI 프로바이더 테스트 시작")
    
    # 환경 변수에서 API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        logger.info("테스트를 위해 환경 변수를 설정하거나 config에 직접 입력하세요.")
        return
    
    # 설정 구성
    config = OPENAI_CONFIG_EXAMPLE.copy()
    config["api_key"] = api_key
    
    try:
        # 프로바이더 생성
        logger.info("OpenAI 프로바이더 생성 중...")
        provider = OpenAIProvider(config)
        
        # 상태 확인
        logger.info(f"프로바이더 상태: {provider.is_healthy()}")
        logger.info(f"사용 가능 여부: {provider.is_available}")
        
        if not provider.is_available:
            logger.error("프로바이더가 사용 불가능합니다.")
            return
        
        # 사용 가능한 모델 조회
        logger.info("사용 가능한 모델 조회 중...")
        models = await provider.get_available_models()
        logger.info(f"사용 가능한 모델 수: {len(models)}")
        if models:
            logger.info(f"첫 5개 모델: {models[:5]}")
        
        # 간단한 프롬프트로 테스트
        test_prompt = "안녕하세요! 간단한 인사말을 한국어로 해주세요."
        logger.info(f"테스트 프롬프트: {test_prompt}")
        
        # 응답 생성
        logger.info("응답 생성 중...")
        response = await provider.generate_response(test_prompt)
        
        logger.info("=== 응답 결과 ===")
        logger.info(f"프로바이더: {response.provider}")
        logger.info(f"모델: {response.model}")
        logger.info(f"응답 시간: {response.response_time:.2f}초")
        logger.info(f"내용 길이: {len(response.content)} 문자")
        logger.info(f"내용: {response.content}")
        
        if response.metadata:
            logger.info(f"메타데이터: {response.metadata}")
        
        # 상태 확인
        health_status = await provider.health_check()
        logger.info(f"상태 확인: {health_status}")
        
        logger.info("OpenAI 프로바이더 테스트 완료!")
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_factory():
    """팩토리 테스트"""
    logger.info("LLM 프로바이더 팩토리 테스트 시작")
    
    # 등록된 프로바이더 확인
    available_providers = LLMProviderFactory.get_available_providers()
    logger.info(f"등록된 프로바이더: {available_providers}")
    
    # OpenAI 프로바이더 정보
    openai_info = LLMProviderFactory.get_provider_info("openai")
    if openai_info:
        logger.info(f"OpenAI 프로바이더 정보: {openai_info}")
    
    logger.info("팩토리 테스트 완료!")


async def main():
    """메인 함수"""
    logger.info("=== OpenAI 프로바이더 테스트 스크립트 ===")
    
    try:
        # 팩토리 테스트
        await test_factory()
        
        # OpenAI 프로바이더 테스트
        await test_openai_provider()
        
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
    
    # 메인 함수 실행
    asyncio.run(main())
