"""
간단한 관리자 모드 유틸리티.

외부 의존성 없이 동작하도록 최소 기능만 제공합니다.

사용 방법(선택):
- 사용자 입력에 "admin:on"이 포함되면 해당 세션을 관리자 모드로 전환
- 사용자 입력에 "admin:off"가 포함되면 관리자 모드 해제

프로덕션에서는 별도의 인증/권한 시스템으로 대체하세요.
"""

from typing import Optional

_ADMIN_SESSIONS: set[str] = set()


def is_admin_mode(session_id: Optional[str]) -> bool:
    """세션이 관리자 모드인지 여부"""
    if not session_id:
        return False
    return session_id in _ADMIN_SESSIONS


def handle_admin_mode(session_id: Optional[str], user_input: str) -> Optional[str]:
    """간단한 토글 명령 처리. 처리 시 사용자에게 안내 문자열을 반환하고, 그렇지 않으면 None.

    예)
    - "admin:on"  -> 관리자 모드 활성화
    - "admin:off" -> 관리자 모드 비활성화
    """
    if not user_input:
        return None

    lowered = user_input.strip().lower()
    if lowered == "admin:on":
        if session_id:
            _ADMIN_SESSIONS.add(session_id)
        return "🔒 관리자 모드가 활성화되었습니다. (주의: 데모 모드)"
    if lowered == "admin:off":
        if session_id and session_id in _ADMIN_SESSIONS:
            _ADMIN_SESSIONS.discard(session_id)
        return "🔓 관리자 모드가 비활성화되었습니다."

    return None


