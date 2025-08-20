"""
OpenAI API LLM 프로바이더

이 모듈은 OpenAI API를 사용하여 LLM 서비스를 제공합니다.
Azure OpenAI와 OpenAI API 모두 지원합니다.
"""

import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

try:
    import openai
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai 라이브러리가 설치되지 않았습니다.")

from .base_provider import LLMProvider, LLMResponse, LLMProviderFactory

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API 프로바이더
    
    OpenAI API와 Azure OpenAI를 모두 지원하는 프로바이더입니다.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = None
        self.client = None
        self.base_url = None
        self.api_version = None
        self.use_azure = False
        self.organization = None
        self.max_retries = 3
        self.timeout = 60.0
        self.request_timeout = 30.0
        super().__init__(config)
    
    def _initialize(self) -> None:
        """OpenAI 클라이언트 초기화"""
        try:
            # 필수 설정 검증
            if not self._validate_config():
                return
            
            # 클라이언트 설정 구성
            client_config = self._build_client_config()
            
            # 클라이언트 생성
            self.client = AsyncOpenAI(**client_config)
            
            # 연결 테스트
            self._test_connection()
            
        except Exception as e:
            logger.error(f"OpenAI 초기화 실패: {str(e)}")
            self.is_available = False
    
    def _validate_config(self) -> bool:
        """설정 유효성 검증"""
        # API 키 검증
        self.api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API 키가 설정되지 않았습니다.")
            self.is_available = False
            return False
        
        # Azure OpenAI 설정 검증
        self.use_azure = self.config.get("use_azure", False)
        if self.use_azure:
            self.base_url = self.config.get("base_url") or os.getenv("AZURE_OPENAI_ENDPOINT")
            if not self.base_url:
                logger.error("Azure OpenAI 사용 시 base_url이 필요합니다.")
                self.is_available = False
                return False
            
            # Azure API 키 사용
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if azure_api_key:
                self.api_key = azure_api_key
            
            self.api_version = self.config.get("api_version", "2024-02-15-preview")
            logger.info(f"Azure OpenAI 설정: {self.base_url}")
        
        # 기타 설정
        self.organization = self.config.get("organization") or os.getenv("OPENAI_ORGANIZATION")
        self.max_retries = self.config.get("max_retries", 3)
        self.timeout = self.config.get("timeout", 60.0)
        self.request_timeout = self.config.get("request_timeout", 30.0)
        
        return True
    
    def _build_client_config(self) -> Dict[str, Any]:
        """클라이언트 설정 구성"""
        client_config = {
            "api_key": self.api_key,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
        
        if self.organization:
            client_config["organization"] = self.organization
        
        if self.use_azure and self.base_url:
            client_config["base_url"] = self.base_url
            client_config["api_version"] = self.api_version
        
        return client_config
    
    def _test_connection(self) -> None:
        """연결 테스트"""
        try:
            # 간단한 모델 목록 조회로 연결 테스트
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def test():
                try:
                    models = await self.client.models.list()
                    available_models = [model.id for model in models.data]
                    logger.info(f"OpenAI 연결 성공. 사용 가능한 모델: {len(available_models)}개")
                    logger.debug(f"사용 가능한 모델: {available_models[:5]}...")
                    self.is_available = True
                except Exception as e:
                    logger.error(f"OpenAI 연결 테스트 실패: {str(e)}")
                    self.is_available = False
            
            loop.run_until_complete(test())
            loop.close()
            
        except Exception as e:
            logger.error(f"연결 테스트 중 오류: {str(e)}")
            self.is_available = False
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """OpenAI API를 사용한 응답 생성"""
        if not self.is_available or not self.client:
            raise RuntimeError("OpenAI 프로바이더가 초기화되지 않았습니다.")
        
        start_time = datetime.now()
        
        try:
            # 요청 파라미터 설정
            request_params = self._build_request_params(prompt, **kwargs)
            
            # 응답 생성
            response = await self.client.chat.completions.create(**request_params)
            
            # 응답 처리
            result = self._process_response(response, start_time)
            logger.info(f"OpenAI 응답 생성 완료: {len(result.content)} 문자")
            return result
                
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {str(e)}")
            raise
    
    def _build_request_params(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """요청 파라미터 구성"""
        # 시스템 메시지 설정
        system_message = kwargs.get("system_message", "You are a helpful HR assistant.")
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        # 사용자 정의 메시지가 있으면 추가
        if "messages" in kwargs:
            messages = kwargs["messages"]
        
        request_params = {
            "model": kwargs.get("model", self.model_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "timeout": kwargs.get("timeout", self.request_timeout)
        }
        
        # 선택적 파라미터 추가
        if "stream" in kwargs:
            request_params["stream"] = kwargs["stream"]
        
        if "stop" in kwargs:
            request_params["stop"] = kwargs["stop"]
        
        return request_params
    
    def _process_response(self, response: ChatCompletion, start_time: datetime) -> LLMResponse:
        """API 응답 처리"""
        if not response.choices or len(response.choices) == 0:
            raise ValueError("OpenAI API에서 빈 응답을 받았습니다.")
        
        choice = response.choices[0]
        content = choice.message.content or ""
        
        # 사용량 정보 추출
        usage_info = {}
        if response.usage:
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        # 메타데이터 구성
        metadata = {
            "model": response.model,
            "finish_reason": choice.finish_reason,
            "usage": usage_info,
            "response_id": response.id,
            "created": response.created
        }
        
        return LLMResponse(
            content=content,
            provider="OpenAI",
            model=response.model,
            metadata=metadata,
            start_time=start_time,
            end_time=datetime.now()
        )
    
    async def generate_streaming_response(self, prompt: str, **kwargs):
        """스트리밍 응답 생성"""
        if not self.is_available or not self.client:
            raise RuntimeError("OpenAI 프로바이더가 초기화되지 않았습니다.")
        
        try:
            request_params = self._build_request_params(prompt, **kwargs)
            request_params["stream"] = True
            
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"OpenAI 스트리밍 응답 생성 실패: {str(e)}")
            raise
    
    def is_healthy(self) -> bool:
        """프로바이더 상태 확인"""
        return self.is_available and self.client is not None
    
    async def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회"""
        if not self.is_available or not self.client:
            return []
        
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"모델 목록 조회 실패: {str(e)}")
            return []
    
    def get_usage_info(self) -> Dict[str, Any]:
        """사용량 정보 반환"""
        return {
            "provider": "OpenAI",
            "model": self.model_name,
            "base_url": self.base_url,
            "is_azure": self.use_azure,
            "api_version": self.api_version,
            "organization": self.organization,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """상세한 상태 확인"""
        health_status = {
            "provider": "OpenAI",
            "is_available": self.is_available,
            "is_healthy": self.is_healthy(),
            "client_initialized": self.client is not None,
            "config": {
                "use_azure": self.use_azure,
                "base_url": self.base_url,
                "api_version": self.api_version,
                "organization": self.organization
            }
        }
        
        if self.is_available and self.client:
            try:
                models = await self.client.models.list()
                health_status["available_models_count"] = len(models.data)
                health_status["connection_status"] = "healthy"
            except Exception as e:
                health_status["connection_status"] = "error"
                health_status["error"] = str(e)
        
        return health_status


# OpenAI 프로바이더 등록
if OPENAI_AVAILABLE:
    LLMProviderFactory.register_provider("openai", OpenAIProvider)
    logger.info("OpenAI 프로바이더가 등록되었습니다.")
else:
    logger.warning("OpenAI 라이브러리가 설치되지 않아 OpenAI 프로바이더를 사용할 수 없습니다.")


# 설정 예시
OPENAI_CONFIG_EXAMPLE = {
    "provider": "openai",
    "api_key": "your-api-key-here",
                "model_name": "gpt-4o",
    "max_tokens": 4000,
    "temperature": 0.1,
    "max_retries": 3,
    "timeout": 60.0,
    "request_timeout": 30.0,
    "use_azure": False,  # Azure OpenAI 사용 시 True
    "base_url": None,    # Azure OpenAI 엔드포인트
    "api_version": "2024-02-15-preview",
    "organization": None,  # OpenAI 조직 ID (선택사항)
    "system_message": "You are a helpful HR assistant specializing in resume and cover letter analysis."
}

# Azure OpenAI 설정 예시
AZURE_OPENAI_CONFIG_EXAMPLE = {
    "provider": "openai",
    "api_key": "your-azure-api-key-here",
    "model_name": "gpt-4",
    "max_tokens": 4000,
    "temperature": 0.1,
    "max_retries": 3,
    "timeout": 60.0,
    "request_timeout": 30.0,
    "use_azure": True,
    "base_url": "https://your-resource.openai.azure.com/",
    "api_version": "2024-02-15-preview",
    "system_message": "You are a helpful HR assistant specializing in resume and cover letter analysis."
}
