"""
메인 챗봇 라우터
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import uuid
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import traceback
import re
from openai import OpenAI
import numpy as np

from ..models.request_models import (
    SessionStartRequest, ChatbotRequest, ConversationRequest,
    GenerateQuestionsRequest, FieldUpdateRequest, SuggestionsRequest,
    ValidationRequest, AutoCompleteRequest, RecommendationsRequest
)
from ..models.response_models import (
    SessionStartResponse, ChatbotResponse, ConversationResponse
)
from ..services.ai_service import AIService
from ..services.session_service import SessionService
from ..services.field_service import FieldService
from ..utils.text_processor import TextProcessor
from ..utils.field_mapper import FieldMapper
from ..utils.validation import ValidationUtils

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# 환경 변수 로드
load_dotenv()

# 서비스 인스턴스들
ai_service = AIService()
session_service = SessionService()
field_service = FieldService()
text_processor = TextProcessor()
field_mapper = FieldMapper()
validation_utils = ValidationUtils()

# 임시 문서 데이터 (RAG용)
temporary_docs = [
    "Gemini 모델은 텍스트, 이미지 등 다양한 유형의 데이터를 처리할 수 있습니다.",
    "RAG(Retrieval-Augmented Generation)는 외부 데이터를 활용해 LLM의 답변 품질을 높이는 기술입니다.",
    "벡터 검색은 텍스트를 숫자의 배열(벡터)로 변환하고, 이 벡터 간의 유사도를 계산하여 가장 관련성이 높은 문서를 찾는 기술입니다."
]

@router.post("/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """세션 시작"""
    try:
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id, request.page, request.mode)
        
        # 첫 번째 질문 생성
        first_question = field_service.get_first_question(request.page)
        
        return SessionStartResponse(
            session_id=session_id,
            question=first_question,
            current_field="title"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-ai-assistant", response_model=SessionStartResponse)
async def start_ai_assistant(request: SessionStartRequest):
    """AI 어시스턴트 세션 시작"""
    try:
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id, request.page, "ai_assistant")
        
        return SessionStartResponse(
            session_id=session_id,
            question="안녕하세요! 채용공고 작성을 도와드리겠습니다. 어떤 정보를 입력하시겠습니까?",
            current_field="general"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    """챗봇 질문 처리"""
    try:
        # 모드에 따른 처리
        if request.mode == "ai_assistant":
            return await ai_service.handle_ai_assistant_request(request)
        elif request.mode == "modal":
            return await ai_service.handle_modal_request(request)
        else:
            return await ai_service.handle_normal_request(request)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation")
async def conversation(request: ConversationRequest):
    """대화형 챗봇 처리"""
    try:
        return await ai_service.handle_conversation_request(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions", response_model=Dict[str, Any])
async def generate_contextual_questions(request: GenerateQuestionsRequest):
    """컨텍스트 기반 질문 생성"""
    try:
        questions = field_service.generate_contextual_questions(
            request.current_field, 
            request.filled_fields
        )
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-assistant-chat", response_model=ChatbotResponse)
async def ai_assistant_chat(request: ChatbotRequest):
    """AI 어시스턴트 채팅"""
    try:
        return await ai_service.handle_ai_assistant_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions")
async def get_suggestions(request: SuggestionsRequest):
    """필드 제안사항 조회"""
    try:
        suggestions = field_service.get_field_suggestions(
            request.field, 
            request.context
        )
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_field(request: ValidationRequest):
    """필드 값 검증"""
    try:
        validation_result = validation_utils.validate_field_value(
            request.field, 
            request.value, 
            request.context
        )
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autocomplete")
async def smart_autocomplete(request: AutoCompleteRequest):
    """스마트 자동완성"""
    try:
        suggestions = field_service.get_autocomplete_suggestions(
            request.partial_input, 
            request.field, 
            request.context
        )
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations")
async def get_recommendations(request: RecommendationsRequest):
    """컨텍스트 기반 추천사항"""
    try:
        recommendations = field_service.get_contextual_recommendations(
            request.current_field, 
            request.filled_fields, 
            request.context
        )
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-field")
async def update_field_in_realtime(request: FieldUpdateRequest):
    """실시간 필드 업데이트"""
    try:
        session_service.update_field(
            request.session_id, 
            request.field, 
            request.value
        )
        return {"success": True, "message": f"{request.field} 필드가 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end")
async def end_session(request: dict):
    """세션 종료"""
    try:
        session_id = request.get("session_id")
        if session_id:
            session_service.end_session(session_id)
        return {"success": True, "message": "세션이 종료되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_endpoint(request: ChatbotRequest):
    """통합 채팅 엔드포인트"""
    try:
        # 모드에 따른 처리
        if request.mode == "langgraph":
            # 랭그래프 모드는 별도 라우터로 리다이렉트
            raise HTTPException(status_code=400, detail="랭그래프 모드는 /langgraph/agent를 사용하세요")
        
        # 일반 챗봇 처리
        return await ask_chatbot(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

