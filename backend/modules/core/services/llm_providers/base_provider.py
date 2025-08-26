"""
LLM 프로바이더 기본 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """LLM 프로바이더 기본 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "")
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.1)
        self.is_available = False
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        """프로바이더 초기화"""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> 'LLMResponse':
        """프롬프트에 대한 응답 생성"""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """프로바이더 상태 확인"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """현재 설정 반환"""
        return {
            "provider": self.__class__.__name__,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "is_available": self.is_available
        }
    
    def update_config(self, **kwargs) -> None:
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"설정 업데이트: {key} = {value}")
    
    def validate_prompt(self, prompt: str) -> bool:
        """프롬프트 유효성 검사"""
        if not prompt or len(prompt.strip()) == 0:
            return False
        
        # 토큰 수 대략적 계산 (한국어 기준)
        estimated_tokens = len(prompt) // 3
        
        if estimated_tokens > self.max_tokens:
            logger.warning(f"프롬프트가 너무 깁니다: 예상 {estimated_tokens} 토큰 (제한: {self.max_tokens})")
            return False
        
        return True
    
    async def safe_generate(self, prompt: str, **kwargs) -> Optional['LLMResponse']:
        """안전한 응답 생성 (예외 처리 포함)"""
        try:
            if not self.is_available:
                logger.error("LLM 프로바이더가 사용 불가능합니다.")
                return None
            
            if not self.validate_prompt(prompt):
                logger.error("프롬프트 유효성 검사 실패")
                return None
            
            response = await self.generate_response(prompt, **kwargs)
            
            if not response or not response.content or len(response.content.strip()) == 0:
                logger.warning("빈 응답을 받았습니다.")
                return None
            
            return response
            
        except Exception as e:
            logger.error(f"LLM 응답 생성 중 오류 발생: {str(e)}")
            return None


class LLMResponse:
    """LLM 응답 래퍼 클래스"""
    
    def __init__(self, content: str, provider: str, model: str, metadata: Optional[Dict[str, Any]] = None, 
                 start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        self.content = content
        self.provider = provider
        self.model = model
        self.metadata = metadata or {}
        self.start_time = start_time or datetime.now()
        self.end_time = end_time or datetime.now()
    
    @property
    def response_time(self) -> float:
        """응답 시간 (초)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def is_valid_json(self) -> bool:
        """응답이 유효한 JSON인지 확인"""
        import json
        try:
            json.loads(self.content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def get_json(self) -> Optional[Dict[str, Any]]:
        """JSON 응답 파싱"""
        if not self.is_valid_json():
            return None
        
        import json
        try:
            return json.loads(self.content)
        except Exception:
            return None
    
    def __str__(self) -> str:
        response_time = self.response_time
        return f"LLMResponse(provider={self.provider}, model={self.model}, content_length={len(self.content)}, response_time={response_time:.2f}s)"


class LLMProviderFactory:
    """LLM 프로바이더 팩토리"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """프로바이더 등록"""
        cls._providers[name] = provider_class
        logger.info(f"LLM 프로바이더 등록: {name}")
    
    @classmethod
    def create_provider(cls, name: str, config: Dict[str, Any]) -> Optional[LLMProvider]:
        """프로바이더 생성"""
        if name not in cls._providers:
            logger.error(f"등록되지 않은 프로바이더: {name}")
            return None
        
        try:
            provider_class = cls._providers[name]
            return provider_class(config)
        except Exception as e:
            logger.error(f"프로바이더 생성 실패: {name}, 오류: {str(e)}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> list:
        """사용 가능한 프로바이더 목록 반환"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_info(cls, name: str) -> Optional[Dict[str, Any]]:
        """프로바이더 정보 반환"""
        if name not in cls._providers:
            return None
        
        provider_class = cls._providers[name]
        return {
            "name": name,
            "class": provider_class.__name__,
            "module": provider_class.__module__
        }
