"""
AI 서비스 클래스
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
try:
    from openai_service import OpenAIService
except ImportError:
    OpenAIService = None

from ..models.request_models import ChatbotRequest, ConversationRequest
from ..models.response_models import ChatbotResponse, ConversationResponse

load_dotenv()

class AIService:
    """AI 관련 서비스 클래스"""
    
    def __init__(self):
        self.openai_service = None
        self._init_openai_service()
    
    def _init_openai_service(self):
        """OpenAI 서비스 초기화"""
        try:
            if OpenAIService:
                self.openai_service = OpenAIService(model_name="gpt-3.5-turbo")
                print("[SUCCESS] OpenAI 서비스 초기화 성공")
            else:
                print("[ERROR] OpenAI 서비스를 사용할 수 없습니다")
                self.openai_service = None
        except Exception as e:
            print(f"[ERROR] OpenAI 서비스 초기화 실패: {e}")
            self.openai_service = None
    
    async def handle_ai_assistant_request(self, request: ChatbotRequest) -> ChatbotResponse:
        """AI 어시스턴트 요청 처리"""
        try:
            # AI API 호출
            ai_response = await self._call_ai_api(request.user_input, request.conversation_history)
            
            return ChatbotResponse(
                message=ai_response,
                confidence=0.9
            )
        except Exception as e:
            return ChatbotResponse(
                message=f"AI 처리 중 오류가 발생했습니다: {str(e)}",
                confidence=0.5
            )
    
    async def handle_modal_request(self, request: ChatbotRequest) -> ChatbotResponse:
        """모달 요청 처리"""
        try:
            # 모달 전용 AI 응답 생성
            modal_response = await self._generate_modal_response(request)
            
            return ChatbotResponse(
                message=modal_response,
                confidence=0.8
            )
        except Exception as e:
            return ChatbotResponse(
                message=f"모달 처리 중 오류가 발생했습니다: {str(e)}",
                confidence=0.5
            )
    
    async def handle_normal_request(self, request: ChatbotRequest) -> ChatbotResponse:
        """일반 요청 처리"""
        try:
            # 기본 AI 응답 생성
            normal_response = await self._call_ai_api(request.user_input, request.conversation_history)
            
            return ChatbotResponse(
                message=normal_response,
                confidence=0.7
            )
        except Exception as e:
            return ChatbotResponse(
                message=f"일반 처리 중 오류가 발생했습니다: {str(e)}",
                confidence=0.5
            )
    
    async def handle_conversation_request(self, request: ConversationRequest) -> ConversationResponse:
        """대화 요청 처리"""
        try:
            # 대화형 AI 응답 생성
            conversation_response = await self._call_ai_api(request.user_input, [])
            
            return ConversationResponse(
                message=conversation_response,
                is_conversation=True
            )
        except Exception as e:
            return ConversationResponse(
                message=f"대화 처리 중 오류가 발생했습니다: {str(e)}",
                is_conversation=True
            )
    
    async def handle_ai_assistant_chat(self, request: ChatbotRequest) -> ChatbotResponse:
        """AI 어시스턴트 채팅 처리"""
        try:
            # AI 어시스턴트 전용 응답 생성
            assistant_response = await self._generate_assistant_response(request)
            
            return ChatbotResponse(
                message=assistant_response,
                confidence=0.9
            )
        except Exception as e:
            return ChatbotResponse(
                message=f"AI 어시스턴트 처리 중 오류가 발생했습니다: {str(e)}",
                confidence=0.5
            )
    
    async def _call_ai_api(self, prompt: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """AI API 호출"""
        try:
            if self.openai_service:
                response = await self.openai_service.generate_response(prompt)
                return response
            else:
                return "AI 서비스를 사용할 수 없습니다. 기본 응답을 제공합니다."
        except Exception as e:
            return f"AI API 호출 중 오류: {str(e)}"
    
    async def _generate_modal_response(self, request: ChatbotRequest) -> str:
        """모달 전용 응답 생성"""
        return f"모달 모드: {request.user_input}에 대한 응답입니다."
    
    async def _generate_assistant_response(self, request: ChatbotRequest) -> str:
        """AI 어시스턴트 전용 응답 생성"""
        return f"AI 어시스턴트: {request.user_input}에 대한 도움을 드리겠습니다."

