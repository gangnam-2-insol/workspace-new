"""
Google Gemini API LLM 프로바이더

`google-generativeai` SDK를 사용하여 Gemini 모델을 호출합니다.
비동기 컨텍스트에서 동작하도록 동기 SDK 호출을 스레드로 위임합니다.
"""

from __future__ import annotations

import os
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_provider import LLMProvider, LLMResponse, LLMProviderFactory


logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini API 프로바이더"""

    def __init__(self, config: Dict[str, Any]):
        self.api_key: Optional[str] = None
        self.model_name: str = config.get("model_name", "gemini-1.5-flash")
        self._model: Optional[Any] = None
        self.request_timeout: float = config.get("request_timeout", 30.0)
        super().__init__(config)

    def _initialize(self) -> None:
        """Gemini 클라이언트 초기화"""
        if not GEMINI_AVAILABLE:
            logger.error("google-generativeai 라이브러리가 설치되지 않았습니다.")
            self.is_available = False
            return

        self.api_key = self.config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("Gemini API 키(GOOGLE_API_KEY)가 설정되지 않았습니다.")
            self.is_available = False
            return

        try:
            genai.configure(api_key=self.api_key)
            # 모델 핸들 준비 (SDK는 동기 방식)
            self._model = genai.GenerativeModel(self.model_name)
            # 간단한 연결 확인: 모델 명만으로는 오류가 나지 않으므로 키 유효성은 첫 호출 시 확인됨
            self.is_available = True
            logger.info("Gemini 프로바이더 초기화 완료")
        except Exception as e:
            logger.error(f"Gemini 초기화 실패: {e}")
            self.is_available = False

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Gemini API를 사용한 응답 생성"""
        if not self.is_available or self._model is None:
            raise RuntimeError("Gemini 프로바이더가 초기화되지 않았습니다.")

        start_time = datetime.now()

        # messages 지원: system_message, messages(list[dict{role,content}]) 처리
        system_message: str = kwargs.get(
            "system_message",
            "You are a helpful HR assistant specializing in resume and cover letter analysis.",
        )

        # Gemini는 role/parts 형식을 사용. 간단화를 위해 하나의 합쳐진 텍스트 프롬프트로 전달
        full_prompt = f"""[SYSTEM]\n{system_message}\n\n[USER]\n{prompt}"""

        try:
            # google-generativeai는 동기 API이므로 스레드로 위임
            response = await asyncio.to_thread(self._model.generate_content, full_prompt)
            content_text = getattr(response, "text", "") or ""

            metadata: Dict[str, Any] = {
                "model": self.model_name,
                "finish_reason": getattr(getattr(response, "prompt_feedback", None), "block_reason", None),
            }

            return LLMResponse(
                content=content_text,
                provider="Gemini",
                model=self.model_name,
                metadata=metadata,
                start_time=start_time,
                end_time=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Gemini API 호출 실패: {e}")
            raise

    def is_healthy(self) -> bool:
        return self.is_available and self._model is not None

    async def health_check(self) -> Dict[str, Any]:  # optional helper
        return {
            "provider": "Gemini",
            "is_available": self.is_available,
            "model": self.model_name,
        }


# 팩토리에 등록
if GEMINI_AVAILABLE:
    LLMProviderFactory.register_provider("gemini", GeminiProvider)
    logger.info("Gemini 프로바이더가 등록되었습니다.")
else:
    logger.warning("google-generativeai가 설치되지 않아 Gemini 프로바이더를 사용할 수 없습니다.")


