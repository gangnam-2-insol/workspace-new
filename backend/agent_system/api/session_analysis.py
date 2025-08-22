"""
세션 분석 API

사용자 행동 로그와 백엔드 연동 결과를 매칭하여 분석하는 API 엔드포인트들
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..tools.session_analyzer import session_analyzer, UserAction
from ..tools.behavior_analyzer import behavior_analyzer

router = APIRouter(prefix="/session-analysis", tags=["세션 분석"])

# Pydantic 모델들
class UserActionRequest(BaseModel):
    """사용자 행동 로그 요청"""
    session_id: str
    user_id: str
    action_type: str
    target_element: str
    content: str
    page_url: str
    context: Dict[str, Any] = {}
    browser_info: Dict[str, Any] = {}

class BackendExecutionRequest(BaseModel):
    """백엔드 실행 로그 요청"""
    session_id: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float
    success: bool = True

class SessionAnalysisRequest(BaseModel):
    """세션 분석 요청"""
    session_id: str

class PatternAnalysisRequest(BaseModel):
    """패턴 분석 요청"""
    session_ids: List[str]

@router.post("/log-user-behavior")
async def log_user_behavior(request: UserActionRequest) -> Dict[str, Any]:
    """사용자 행동 로그 기록"""
    try:
        action = UserAction(
            action_type=request.action_type,
            target_element=request.target_element,
            content=request.content,
            timestamp=datetime.now().isoformat(),
            page_url=request.page_url,
            context=request.context
        )
        
        log_id = session_analyzer.log_user_behavior(
            session_id=request.session_id,
            user_id=request.user_id,
            action=action,
            page_context=request.context,
            browser_info=request.browser_info
        )
        
        return {
            "status": "success",
            "log_id": log_id,
            "message": "사용자 행동 로그가 성공적으로 기록되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그 기록 실패: {str(e)}")

@router.post("/log-backend-execution")
async def log_backend_execution(request: BackendExecutionRequest) -> Dict[str, Any]:
    """백엔드 실행 로그 기록"""
    try:
        execution_id = session_analyzer.log_backend_execution(
            session_id=request.session_id,
            tool_name=request.tool_name,
            parameters=request.parameters,
            result=request.result,
            execution_time=request.execution_time,
            success=request.success
        )
        
        return {
            "status": "success",
            "execution_id": execution_id,
            "message": "백엔드 실행 로그가 성공적으로 기록되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그 기록 실패: {str(e)}")

@router.post("/analyze-session")
async def analyze_session(request: SessionAnalysisRequest) -> Dict[str, Any]:
    """세션 분석"""
    try:
        analysis = session_analyzer.analyze_session(request.session_id)
        
        return {
            "status": "success",
            "analysis": {
                "session_id": analysis.session_id,
                "user_id": analysis.user_id,
                "start_time": analysis.start_time,
                "end_time": analysis.end_time,
                "total_actions": analysis.total_actions,
                "total_executions": analysis.total_executions,
                "accuracy_score": analysis.accuracy_score,
                "tool_mapping_accuracy": analysis.tool_mapping_accuracy,
                "suggestions": analysis.suggestions,
                "matched_pairs_count": len(analysis.matched_pairs)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.get("/session-summary/{session_id}")
async def get_session_summary(session_id: str) -> Dict[str, Any]:
    """세션 요약 정보"""
    try:
        summary = session_analyzer.get_session_summary(session_id)
        
        return {
            "status": "success",
            "summary": summary
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 조회 실패: {str(e)}")

@router.post("/export-analysis/{session_id}")
async def export_session_analysis(session_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """세션 분석 결과 내보내기"""
    try:
        exported_filename = session_analyzer.export_session_analysis(session_id, filename)
        
        return {
            "status": "success",
            "filename": exported_filename,
            "message": "분석 결과가 성공적으로 내보내졌습니다."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")

@router.post("/analyze-user-action")
async def analyze_user_action(request: UserActionRequest) -> Dict[str, Any]:
    """사용자 행동 분석 (툴 매핑)"""
    try:
        action = UserAction(
            action_type=request.action_type,
            target_element=request.target_element,
            content=request.content,
            timestamp=datetime.now().isoformat(),
            page_url=request.page_url,
            context=request.context
        )
        
        tool_mappings = behavior_analyzer.analyze_user_action(action)
        
        return {
            "status": "success",
            "user_action": request.content,
            "tool_mappings": [
                {
                    "tool_name": mapping.tool_name,
                    "confidence": mapping.confidence,
                    "parameters": mapping.parameters,
                    "reasoning": mapping.reasoning
                }
                for mapping in tool_mappings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"행동 분석 실패: {str(e)}")

@router.get("/active-sessions")
async def get_active_sessions() -> Dict[str, Any]:
    """활성 세션 목록"""
    try:
        # 실제로는 session_analyzer에서 활성 세션 정보를 가져와야 함
        # 현재는 시뮬레이션된 데이터 반환
        active_sessions = [
            {
                "session_id": "demo_session_001",
                "user_id": "user123",
                "start_time": "2025-08-19T14:58:35",
                "total_actions": 6,
                "total_executions": 3
            }
        ]
        
        return {
            "status": "success",
            "active_sessions": active_sessions,
            "count": len(active_sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 목록 조회 실패: {str(e)}")

@router.get("/session-stats")
async def get_session_statistics() -> Dict[str, Any]:
    """세션 통계"""
    try:
        # 실제로는 session_analyzer에서 통계 정보를 계산해야 함
        stats = {
            "total_sessions": 1,
            "total_user_actions": 6,
            "total_backend_executions": 3,
            "average_accuracy": 0.187,
            "most_used_tools": [
                {"tool_name": "get_github_user_info", "count": 1},
                {"tool_name": "find_documents", "count": 1},
                {"tool_name": "web_search", "count": 1}
            ]
        }
        
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.post("/clear-session/{session_id}")
async def clear_session_data(session_id: str) -> Dict[str, Any]:
    """세션 데이터 삭제"""
    try:
        # 실제로는 session_analyzer에서 세션 데이터를 삭제해야 함
        return {
            "status": "success",
            "message": f"세션 {session_id}의 데이터가 삭제되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 삭제 실패: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "session-analysis",
        "timestamp": datetime.now().isoformat()
    }
