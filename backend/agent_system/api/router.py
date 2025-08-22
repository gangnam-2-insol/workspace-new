"""
에이전트 시스템 메인 라우터

에이전트 챗봇의 주요 API 엔드포인트들을 정의합니다.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["에이전트 챗봇"])

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    status: str
    message: str
    session_id: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """에이전트와 채팅"""
    try:
        # 임시 응답 (실제로는 Agent 클래스 사용)
        return ChatResponse(
            status="success",
            message=f"에이전트 응답: {request.message}",
            session_id=request.session_id or "default_session"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "에이전트 시스템이 정상 작동 중입니다."}
