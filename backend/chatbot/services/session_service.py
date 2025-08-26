"""
세션 관리 서비스 클래스
"""

from typing import Dict, Any, Optional
from datetime import datetime

class SessionService:
    """세션 관리 서비스"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, page: str, mode: str = "normal") -> None:
        """새 세션 생성"""
        self.sessions[session_id] = {
            "page": page,
            "mode": mode,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "fields": {},
            "conversation_history": []
        }
        print(f"✅ 세션 생성: {session_id} (페이지: {page}, 모드: {mode})")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보 조회"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """세션 정보 업데이트"""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def update_field(self, session_id: str, field: str, value: str) -> bool:
        """세션의 필드 값 업데이트"""
        if session_id in self.sessions:
            self.sessions[session_id]["fields"][field] = value
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def get_field(self, session_id: str, field: str) -> Optional[str]:
        """세션의 필드 값 조회"""
        session = self.get_session(session_id)
        if session:
            return session.get("fields", {}).get(field)
        return None
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """세션에 메시지 추가"""
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append(message)
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def get_conversation_history(self, session_id: str) -> list:
        """세션의 대화 기록 조회"""
        session = self.get_session(session_id)
        if session:
            return session.get("conversation_history", [])
        return []
    
    def end_session(self, session_id: str) -> bool:
        """세션 종료"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"✅ 세션 종료: {session_id}")
            return True
        return False
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """비활성 세션 정리"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = session_data.get("last_activity")
            if last_activity:
                age = (now - last_activity).total_seconds() / 3600
                if age > max_age_hours:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
        
        return len(expired_sessions)

