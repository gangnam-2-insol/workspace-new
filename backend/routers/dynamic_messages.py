"""
동적 메시지 생성 API
사용자의 상황과 맥락에 따라 자연스러운 메시지를 생성합니다.
"""

import os
import sys
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ai.services.dynamic_message_generator import DynamicMessageGenerator

router = APIRouter(prefix="/api/dynamic-messages", tags=["dynamic-messages"])

class MessageContext(BaseModel):
    """메시지 생성에 필요한 컨텍스트 정보"""
    current_page: Optional[str] = ""
    current_step: Optional[str] = ""
    previous_input: Optional[Dict[str, Any]] = {}
    user_tone: Optional[str] = "friendly"
    completed_steps: Optional[list] = []
    progress: Optional[float] = 0.0
    user_input: Optional[str] = ""

class MessageResponse(BaseModel):
    """메시지 응답 모델"""
    message: str
    message_type: str
    context: Dict[str, Any]

@router.post("/generate", response_model=MessageResponse)
async def generate_contextual_message(context: MessageContext):
    """맥락에 맞는 메시지 생성"""
    try:
        message_generator = DynamicMessageGenerator()

        # 사용자 컨텍스트 정보
        user_context = {
            'current_page': context.current_page,
            'current_step': context.current_step,
            'previous_input': context.previous_input,
            'user_tone': context.user_tone,
            'completed_steps': context.completed_steps,
            'progress': context.progress
        }

        # 메시지 타입 결정
        if context.user_input:
            if "안녕" in context.user_input or "hello" in context.user_input.lower():
                message_type = "greeting"
                message = message_generator.generate_contextual_message(user_context)
            elif "감사" in context.user_input or "고마워" in context.user_input:
                message_type = "thanks"
                message = message_generator.tone_templates[context.user_tone]['thanks']
            else:
                message_type = "contextual"
                message = message_generator.generate_contextual_message(user_context)
        else:
            message_type = "contextual"
            message = message_generator.generate_contextual_message(user_context)

        # 진행 상황에 따른 격려 메시지 추가
        if context.progress > 0:
            encouragement = message_generator.generate_encouragement_message(user_context)
            message += f"\n\n{encouragement}"

        return MessageResponse(
            message=message,
            message_type=message_type,
            context=user_context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 생성 중 오류: {str(e)}")

@router.post("/follow-up", response_model=MessageResponse)
async def generate_follow_up_message(context: MessageContext):
    """후속 질문이나 안내 메시지 생성"""
    try:
        message_generator = DynamicMessageGenerator()

        user_context = {
            'current_page': context.current_page,
            'current_step': context.current_step,
            'previous_input': context.previous_input,
            'user_tone': context.user_tone,
            'completed_steps': context.completed_steps,
            'progress': context.progress
        }

        message = message_generator.generate_follow_up_message(user_context)

        return MessageResponse(
            message=message,
            message_type="follow_up",
            context=user_context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"후속 메시지 생성 중 오류: {str(e)}")

@router.post("/encouragement", response_model=MessageResponse)
async def generate_encouragement_message(context: MessageContext):
    """격려나 동기부여 메시지 생성"""
    try:
        message_generator = DynamicMessageGenerator()

        user_context = {
            'current_page': context.current_page,
            'current_step': context.current_step,
            'previous_input': context.previous_input,
            'user_tone': context.user_tone,
            'completed_steps': context.completed_steps,
            'progress': context.progress
        }

        message = message_generator.generate_encouragement_message(user_context)

        return MessageResponse(
            message=message,
            message_type="encouragement",
            context=user_context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"격려 메시지 생성 중 오류: {str(e)}")

@router.get("/templates")
async def get_message_templates():
    """사용 가능한 메시지 템플릿 조회"""
    try:
        message_generator = DynamicMessageGenerator()

        return {
            "greeting_templates": message_generator.greeting_templates,
            "context_templates": message_generator.context_templates,
            "tone_templates": message_generator.tone_templates
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 조회 중 오류: {str(e)}")
