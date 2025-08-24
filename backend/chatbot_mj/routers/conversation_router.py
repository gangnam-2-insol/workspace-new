"""
대화 관리 라우터
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import uuid

from ..models.request_models import ConversationRequest
from ..models.response_models import ConversationResponse
from ..services.ai_service import AIService
from ..services.session_service import SessionService

router = APIRouter(prefix="/conversation", tags=["conversation"])

# 서비스 인스턴스들
ai_service = AIService()
session_service = SessionService()

@router.post("/start")
async def start_conversation(request: dict):
    """대화 세션 시작"""
    try:
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id, "conversation", "conversational")
        
        return {
            "session_id": session_id,
            "message": "대화 세션이 시작되었습니다. 무엇을 도와드릴까요?",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def conversation_chat(request: ConversationRequest):
    """대화형 채팅"""
    try:
        # 세션 확인
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # AI 서비스를 통한 응답 생성
        response = await ai_service.handle_conversation_request(request)
        
        # 세션에 메시지 추가
        session_service.add_message(request.session_id, {
            "user_input": request.user_input,
            "response": response.message,
            "timestamp": "now"
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """대화 기록 조회"""
    try:
        history = session_service.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end/{session_id}")
async def end_conversation(session_id: str):
    """대화 세션 종료"""
    try:
        success = session_service.end_session(session_id)
        if success:
            return {
                "session_id": session_id,
                "message": "대화 세션이 종료되었습니다.",
                "success": True
            }
        else:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

