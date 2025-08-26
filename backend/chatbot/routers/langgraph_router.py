"""
랭그래프 Agent 전용 라우터
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid

from ..core.agent_system import AgentSystem
from ..core.enhanced_field_extractor import enhanced_extractor
import re
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
        mode = request.get("mode", "langgraph")
        
        # Agent 시스템 호출
        result = agent_system.process_request(
            user_input=user_input,
            conversation_history=conversation_history,
            session_id=session_id,
            mode=mode
        )
        # 백업: 추출 필드가 비어있으면 규칙 기반 추출 보강
        try:
            if not result.get("extracted_fields"):
                fallback_fields = enhanced_extractor.extract_fields_enhanced(user_input)
                if fallback_fields:
                    result["extracted_fields"] = fallback_fields
                    result["intent"] = "recruit"
                if not result.get("extracted_fields"):
                    simple_fields = {}
                    try:
                        m = re.search(r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)", user_input)
                        if m:
                            simple_fields['location'] = m.group(1)
                        m = re.search(r"(\d+)\s*명", user_input)
                        if m:
                            simple_fields['headcount'] = f"{m.group(1)}명"
                        m = re.search(r"(\d{2,4})\s*만원", user_input)
                        if m:
                            simple_fields['salary'] = f"{m.group(1)}만원"
                        if '신입' in user_input:
                            simple_fields['experience'] = '신입'
                        elif '시니어' in user_input:
                            simple_fields['experience'] = '시니어'
                        elif '경력' in user_input:
                            simple_fields['experience'] = '경력'
                        m = re.search(r"([가-힣A-Za-z]+)\s*(담당자|매니저|전문가)", user_input)
                        if m:
                            simple_fields['position'] = f"{m.group(1)} {m.group(2)}".strip()
                    except Exception:
                        simple_fields = {}
                    if simple_fields:
                        result['extracted_fields'] = simple_fields
                        result['intent'] = 'recruit'
        except Exception:
            pass
        
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

@router.get("/health")
async def langgraph_health() -> Dict[str, Any]:
    """LangGraph Agent 헬스체크"""
    return {"status": "healthy"}

@router.post("/chat")
async def langgraph_chat_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """프론트엔드 호환용 Chat 엔드포인트 (/api/langgraph-agent/chat 기대 형태)

    허용 페이로드:
    - { user_input: string, session_id?: string, conversation_history?: list }
    - { message: string, session_id?: string, conversation_history?: list }
    """
    try:
        user_input = payload.get("user_input") or payload.get("message") or ""
        conversation_history = payload.get("conversation_history", [])
        session_id = payload.get("session_id", str(uuid.uuid4()))

        result = agent_system.process_request(
            user_input=user_input,
            conversation_history=conversation_history,
            session_id=session_id,
            mode="langgraph",
        )

        # 프론트엔드(LangGraphChatbot) 기대 응답 구조 맞춤
        return {
            "success": result.get("success", True),
            "message": result.get("response", ""),
            "mode": "langgraph",
            "tool_used": result.get("tool_used"),
            "confidence": result.get("confidence", 0.9),
            "session_id": session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

