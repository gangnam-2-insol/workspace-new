"""
채팅 핸들러 모듈

사용자 메시지 처리와 응답 생성을 담당합니다.
"""

import logging
from typing import Dict, Any, Optional
from .agent import Agent
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

class ChatHandler:
    """채팅 메시지 처리 핸들러"""
    
    def __init__(self, agent: Agent, session_manager: SessionManager):
        self.agent = agent
        self.session_manager = session_manager
    
    async def handle_message(self, 
                           session_id: str, 
                           user_message: str,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """사용자 메시지 처리"""
        try:
            # 세션 확인/생성
            if not self.session_manager.get_session(session_id):
                self.session_manager.create_session(session_id, user_id)
            
            # 에이전트로 메시지 처리
            response = await self.agent.process_message(session_id, user_message)
            
            # 세션에 메시지 추가
            self.session_manager.add_message(session_id, "user", user_message)
            self.session_manager.add_message(session_id, "assistant", response["message"])
            
            return {
                "status": "success",
                "message": response["message"],
                "session_id": session_id,
                "tool_used": response.get("tool_used"),
                "tool_result": response.get("tool_result")
            }
            
        except Exception as e:
            logger.error(f"메시지 처리 실패: {str(e)}")
            return {
                "status": "error",
                "message": f"메시지 처리 중 오류가 발생했습니다: {str(e)}",
                "session_id": session_id
            }
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """세션 히스토리 조회"""
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return {"status": "error", "message": "세션을 찾을 수 없습니다."}
            
            return {
                "status": "success",
                "session_id": session_id,
                "history": session["messages"],
                "created_at": session["created_at"]
            }
            
        except Exception as e:
            logger.error(f"세션 히스토리 조회 실패: {str(e)}")
            return {"status": "error", "message": f"세션 히스토리 조회 실패: {str(e)}"}
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """세션 삭제"""
        try:
            success = self.session_manager.delete_session(session_id)
            if success:
                return {"status": "success", "message": "세션이 삭제되었습니다."}
            else:
                return {"status": "error", "message": "세션을 찾을 수 없습니다."}
                
        except Exception as e:
            logger.error(f"세션 삭제 실패: {str(e)}")
            return {"status": "error", "message": f"세션 삭제 실패: {str(e)}"}
