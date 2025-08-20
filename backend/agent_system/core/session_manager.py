"""
세션 관리 모듈

사용자 대화 세션을 관리하는 클래스입니다.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SessionManager:
    """사용자 대화 세션을 관리하는 클래스"""
    
    def __init__(self, expiry_seconds=1800, max_history=10):
        """
        세션 매니저 초기화
        
        Args:
            expiry_seconds (int): 세션 만료 시간 (초)
            max_history (int): 최대 대화 기록 수
        """
        self.sessions = defaultdict(dict)
        self.expiry_seconds = expiry_seconds
        self.max_history = max_history
        logger.info(f"SessionManager 초기화 완료 (만료: {expiry_seconds}초, 최대기록: {max_history}개)")

    def _current_time(self) -> int:
        """현재 시간을 Unix timestamp로 반환"""
        return int(time.time())

    def create_session(self, session_id: str) -> None:
        """
        새로운 세션 생성
        
        Args:
            session_id (str): 세션 ID
        """
        self.sessions[session_id] = {
            "history": [],
            "last_activity": self._current_time(),
            "created_at": self._current_time()
        }
        logger.info(f"새 세션 생성: {session_id}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        세션에 메시지 추가
        
        Args:
            session_id (str): 세션 ID
            role (str): 메시지 역할 (user/assistant)
            content (str): 메시지 내용
        """
        if session_id not in self.sessions:
            self.create_session(session_id)

        session = self.sessions[session_id]
        session["history"].append({"role": role, "content": content})

        # 오래된 기록은 잘라냄
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history:]

        session["last_activity"] = self._current_time()
        logger.info(f"세션 {session_id}에 메시지 추가: {role}")

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        세션의 대화 기록 반환
        
        Args:
            session_id (str): 세션 ID
            
        Returns:
            List[Dict[str, str]]: 대화 기록 리스트
        """
        if session_id in self.sessions:
            return self.sessions[session_id]["history"]
        return []

    def cleanup_sessions(self) -> None:
        """만료된 세션들을 정리"""
        now = self._current_time()
        expired = [
            sid for sid, data in self.sessions.items()
            if now - data["last_activity"] > self.expiry_seconds
        ]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.info(f"만료된 세션 {len(expired)}개 정리: {expired}")

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        세션 정보 반환
        
        Args:
            session_id (str): 세션 ID
            
        Returns:
            Optional[Dict[str, Any]]: 세션 정보 또는 None
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "message_count": len(session["history"]),
                "last_activity": session["last_activity"],
                "created_at": session.get("created_at", session["last_activity"])
            }
        return None

    def delete_session(self, session_id: str) -> bool:
        """
        세션 삭제
        
        Args:
            session_id (str): 세션 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"세션 삭제: {session_id}")
            return True
        return False

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """
        모든 세션 정보 반환
        
        Returns:
            List[Dict[str, Any]]: 모든 세션 정보 리스트
        """
        return [
            self.get_session_info(sid) for sid in self.sessions.keys()
        ]

    def get_active_sessions_count(self) -> int:
        """
        활성 세션 수 반환
        
        Returns:
            int: 활성 세션 수
        """
        return len(self.sessions)

    def is_session_valid(self, session_id: str) -> bool:
        """
        세션이 유효한지 확인
        
        Args:
            session_id (str): 세션 ID
            
        Returns:
            bool: 세션 유효성
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        now = self._current_time()
        return (now - session["last_activity"]) <= self.expiry_seconds
