"""
LangGraph 에이전트 챗봇 API 라우터
모듈화된 에이전트 챗봇의 REST API 엔드포인트 제공
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from datetime import datetime
import traceback

from langgraph_agent import agent
from admin_mode import is_admin_mode
from langgraph_tools import tool_manager
from database import database
from langgraph_config import config as lg_config

router = APIRouter(prefix="/api/langgraph-agent", tags=["LangGraph Agent"])

# Pydantic 모델들
class AgentChatRequest(BaseModel):
    user_input: str = Field(..., description="사용자 입력 메시지")
    session_id: Optional[str] = Field(None, description="세션 ID (없으면 새로 생성)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 컨텍스트 정보")

class AgentChatResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    mode: str
    tool_used: Optional[str] = None
    confidence: float
    timestamp: str

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    last_activity: str

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: str
    last_activity: str

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(request: AgentChatRequest):
    """
    LangGraph 에이전트와 대화
    """
    try:
        # 세션 ID 생성 또는 사용
        session_id = request.session_id or str(uuid.uuid4())
        
        # 에이전트에 메시지 전달
        result = await agent.process_message(
            session_id=session_id,
            user_input=request.user_input,
            context=request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return AgentChatResponse(
            success=True,
            message=result["message"],
            session_id=session_id,
            mode=result["mode"],
            tool_used=result.get("tool_used"),
            confidence=result["confidence"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"[ERROR] /chat 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"챗봇 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/sessions", response_model=List[SessionInfo])
async def get_all_sessions():
    """
    모든 활성 세션 목록 조회
    """
    try:
        sessions = []
        for session_id, session_data in agent.sessions.items():
            sessions.append(SessionInfo(
                session_id=session_id,
                message_count=len(session_data["messages"]),
                created_at=session_data["created_at"].isoformat(),
                last_activity=session_data["last_activity"].isoformat()
            ))
        
        return sessions
        
    except Exception as e:
        print(f"[ERROR] /sessions 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"세션 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    특정 세션의 대화 히스토리 조회
    """
    try:
        messages = agent.get_session_history(session_id)
        
        if not messages and session_id not in agent.sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
        
        session_data = agent.sessions.get(session_id, {})
        
        return SessionHistoryResponse(
            session_id=session_id,
            messages=messages,
            created_at=session_data.get("created_at", datetime.now()).isoformat(),
            last_activity=session_data.get("last_activity", datetime.now()).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] /sessions/{session_id}/history 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"세션 히스토리 조회 중 오류가 발생했습니다: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    세션 삭제
    """
    try:
        success = agent.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
        
        return {"success": True, "message": "세션이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] /sessions/{session_id} DELETE 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"세션 삭제 중 오류가 발생했습니다: {str(e)}")

@router.post("/sessions/{session_id}/clear")
async def clear_session_history(session_id: str):
    """
    세션 히스토리만 삭제 (세션은 유지)
    """
    try:
        if session_id not in agent.sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
        
        agent.sessions[session_id]["messages"] = []
        agent.sessions[session_id]["last_activity"] = datetime.now()
        
        return {"success": True, "message": "세션 히스토리가 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] /sessions/{session_id}/clear 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"세션 히스토리 삭제 중 오류가 발생했습니다: {str(e)}")

@router.get("/health")
async def health_check():
    """
    에이전트 상태 확인
    """
    try:
        return {
            "status": "healthy",
            "agent_initialized": agent.llm is not None,
            "active_sessions": len(agent.sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/tools")
async def get_available_tools():
    """
    사용 가능한 툴 목록 조회
    """
    try:
        tools = [
            {
                "name": "search_jobs",
                "description": "채용 정보 검색",
                "keywords": ["채용", "구인", "검색", "일자리"]
            },
            {
                "name": "analyze_resume",
                "description": "이력서 분석",
                "keywords": ["이력서", "분석", "평가"]
            },
            {
                "name": "create_portfolio",
                "description": "포트폴리오 생성",
                "keywords": ["포트폴리오", "생성", "만들기"]
            },
            {
                "name": "submit_application",
                "description": "지원서 제출",
                "keywords": ["지원", "제출", "신청"]
            },
            {
                "name": "get_user_info",
                "description": "사용자 정보 조회",
                "keywords": ["사용자", "정보", "프로필"]
            },
            {
                "name": "get_interview_schedule",
                "description": "면접 일정 조회",
                "keywords": ["면접", "일정", "스케줄"]
            }
        ]
        
        return {"tools": tools}
        
    except Exception as e:
        print(f"[ERROR] /tools 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"툴 목록 조회 중 오류가 발생했습니다: {str(e)}")


# 관리자 모드에서만 접근 가능한 툴 CRUD API
class ToolItem(BaseModel):
    name: str
    description: Optional[str] = ""
    code: Optional[str] = None
    trusted: Optional[bool] = None


def _require_admin(session_id: str):
    if not is_admin_mode(session_id):
        raise HTTPException(status_code=403, detail="권한이 없습니다. 관리자 모드로 전환하세요.")


@router.get("/admin/tools")
async def admin_list_tools(session_id: str):
    _require_admin(session_id)
    return {
        "registered": tool_manager.list_tools(),
        "dynamic": tool_manager.list_dynamic_tools(),
    }


@router.post("/admin/tools")
async def admin_create_tool(session_id: str, item: ToolItem):
    _require_admin(session_id)
    if not item.name or not item.code:
        raise HTTPException(status_code=400, detail="name, code는 필수입니다.")
    ok = tool_manager.create_dynamic_tool(item.name, item.code, item.description or "")
    if not ok:
        raise HTTPException(status_code=400, detail="툴 생성 실패")
    # 신뢰 플래그 설정
    if item.trusted is not None:
        tool_manager.set_dynamic_trusted(item.name, bool(item.trusted))
    return {"success": True}


@router.put("/admin/tools/{name}")
async def admin_update_tool(session_id: str, name: str, item: ToolItem):
    _require_admin(session_id)
    ok = tool_manager.update_dynamic_tool(name, code=item.code, description=item.description)
    if not ok:
        raise HTTPException(status_code=400, detail="툴 업데이트 실패")
    if item.trusted is not None:
        tool_manager.set_dynamic_trusted(name, bool(item.trusted))
    return {"success": True}


@router.delete("/admin/tools/{name}")
async def admin_delete_tool(session_id: str, name: str):
    _require_admin(session_id)
    # 휴지통 보관: 파일/메타를 MongoDB에 저장 후 실제 삭제
    try:
        base_dir = tool_manager._dynamic_tools_dir()
        file_path = os.path.join(base_dir, f"{name}.py")
        meta = None
        try:
            meta = tool_manager._get_dynamic_tool_meta(name)
        except Exception:
            meta = None

        code_text = None
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_text = f.read()
            except Exception:
                code_text = None

        # MongoDB에 저장
        coll = database.get_collection('tool_trash')
        if coll is not None:
            from datetime import datetime, timedelta
            doc = {
                "name": name,
                "description": (meta or {}).get("description"),
                "trusted": (meta or {}).get("trusted", False),
                "code": code_text,
                "deleted_at": datetime.utcnow(),
                "retention_days": lg_config.trash_retention_days,
                "source": "filesystem"
            }
            try:
                await coll.create_index("deleted_at", expireAfterSeconds=int(lg_config.trash_retention_days) * 86400)
            except Exception:
                pass
            try:
                await coll.insert_one(doc)
            except Exception:
                pass

        # 실제 파일/인덱스 삭제
        ok = tool_manager.delete_dynamic_tool(name)
    except Exception:
        ok = False
    if not ok:
        raise HTTPException(status_code=404, detail="툴을 찾을 수 없거나 삭제 실패")
    return {"success": True}
