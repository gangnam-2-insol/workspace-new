"""
랭그래프 Agent 전용 라우터
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid

from ..core.agent_system import AgentSystem
from ..models.agent_models import AgentOutput

router = APIRouter(tags=["langgraph"])

# Agent 시스템 인스턴스
agent_system = AgentSystem()

@router.post("/agent")
async def langgraph_agent_endpoint(request: dict):
    """랭그래프 Agent 시스템 엔드포인트"""
    try:
        user_input = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        session_id = request.get("session_id", str(uuid.uuid4()))
        
        # Agent 시스템 호출
        result = agent_system.process_request(
            user_input=user_input,
            conversation_history=conversation_history,
            session_id=session_id
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "intent": result["intent"],
            "session_id": session_id,
            "extracted_fields": result.get("extracted_fields", {}),
            "confidence": 0.9
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

