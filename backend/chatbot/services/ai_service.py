"""
AI 서비스 클래스
"""

from __future__ import annotations

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import AsyncOpenAI

from ..models.chatbot_models import ChatbotRequest, ChatbotResponse, ConversationRequest, ConversationResponse

load_dotenv()

class AIService:
    def __init__(self):
        """AI 서비스 초기화"""
        self.openai_client = None
        self._init_openai_service()
    
    def _init_openai_service(self):
        """OpenAI 서비스 초기화"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                print("[SUCCESS] OpenAI 서비스 초기화 성공")
            else:
                print("[WARNING] OPENAI_API_KEY가 설정되지 않았습니다.")
                self.openai_client = None
        except Exception as e:
            print(f"[ERROR] OpenAI 서비스 초기화 실패: {e}")
            self.openai_client = None

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
            if not self.openai_client:
                return "AI 서비스를 사용할 수 없습니다. OPENAI_API_KEY가 설정되지 않았습니다."
            
            # 시스템 프롬프트
            system_prompt = """당신은 채용 전문 어시스턴트입니다. 
            사용자가 채용 공고 작성이나 채용 관련 질문을 할 때 전문적이고 실용적인 답변을 제공해주세요.
            
            주의사항:
            - AI 모델에 대한 설명은 하지 마세요
            - 채용 관련 실무적인 조언을 제공하세요
            - 구체적이고 실용적인 답변을 해주세요
            - 한국어로 답변해주세요
            - 모든 답변은 핵심만 간단하게 요약해서 2~3줄 이내로 작성해주세요
            - 불필요한 설명은 생략하고, 요점 위주로 간결하게 답변해주세요
            - '주요 업무'를 작성할 때는 지원자 입장에서 직무 이해도가 높아지도록 구체적인 동사(예: 개발, 분석, 관리 등)를 사용하세요
            - 각 업무는 "무엇을 한다 → 왜 한다" 구조로, 기대 성과까지 간결히 포함해서 자연스럽고 명확하게 서술하세요
            - 번호가 있는 항목(1, 2, 3 등)은 각 줄마다 줄바꿈하여 출력해주세요"""
            
            # 메시지 구성
            messages = [{"role": "system", "content": system_prompt}]
            
            # 대화 히스토리 추가
            if conversation_history:
                for msg in conversation_history[-6:]:  # 최근 3턴 (user + assistant)
                    role = 'user' if msg.get('role') == 'user' else 'assistant'
                    messages.append({"role": role, "content": msg.get('content', '')})
            
            # 현재 사용자 입력 추가
            messages.append({"role": "user", "content": prompt})
            
            # OpenAI API 호출
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "응답을 생성할 수 없습니다."
            
        except Exception as e:
            return f"AI API 호출 중 오류: {str(e)}"
    
    async def _generate_modal_response(self, request: ChatbotRequest) -> str:
        """모달 전용 응답 생성"""
        return f"모달 모드: {request.user_input}에 대한 응답입니다."
    
    async def _generate_assistant_response(self, request: ChatbotRequest) -> str:
        """AI 어시스턴트 전용 응답 생성"""
        return f"AI 어시스턴트: {request.user_input}에 대한 도움을 드리겠습니다."

