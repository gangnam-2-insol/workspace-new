"""
에러 처리 및 복구 유틸리티

툴 실행 실패 시 재시도, 대체 툴 제안, 사용자 친화적 에러 메시지 생성을 담당합니다.
"""

import time
import logging
from typing import Callable, Any, Dict, Optional, List
from functools import wraps

logger = logging.getLogger(__name__)

class RetryConfig:
    """재시도 설정"""
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor

def retry_with_backoff(config: RetryConfig = None):
    """
    재시도 데코레이터 (지수 백오프 적용)
    
    Args:
        config: 재시도 설정 (기본값: 3회 재시도, 1초 시작, 2배씩 증가)
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < config.max_retries:
                        # 지수 백오프 적용
                        sleep_time = config.delay * (config.backoff_factor ** attempt)
                        logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"All {config.max_retries + 1} attempts failed")
            
            # 모든 재시도 실패 시 에러 반환
            raise last_exception
        
        return wrapper
    return decorator

def create_user_friendly_error_message(error: Exception, tool_name: str, action: str) -> str:
    """
    사용자 친화적 에러 메시지 생성
    
    Args:
        error: 발생한 예외
        tool_name: 실패한 툴 이름
        action: 실패한 액션
        
    Returns:
        사용자 친화적 에러 메시지
    """
    error_str = str(error).lower()
    
    # 네트워크 관련 에러
    if any(keyword in error_str for keyword in ["connection", "timeout", "network", "unreachable"]):
        return f"네트워크 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요."
    
    # 인증 관련 에러
    if any(keyword in error_str for keyword in ["unauthorized", "forbidden", "authentication", "token"]):
        return f"인증에 문제가 있습니다. API 키를 확인해주세요."
    
    # API 제한 관련 에러
    if any(keyword in error_str for keyword in ["rate limit", "quota", "limit exceeded"]):
        return f"API 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요."
    
    # 데이터베이스 관련 에러
    if any(keyword in error_str for keyword in ["database", "mongodb", "connection refused"]):
        return f"데이터베이스 연결에 문제가 있습니다. 관리자에게 문의해주세요."
    
    # 일반적인 에러
    return f"요청을 처리하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

def get_fallback_suggestion(tool_name: str, action: str, error: Exception) -> Optional[Dict[str, Any]]:
    """
    대체 툴 제안 생성
    
    Args:
        tool_name: 실패한 툴 이름
        action: 실패한 액션
        error: 발생한 예외
        
    Returns:
        대체 툴 제안 정보 또는 None
    """
    error_str = str(error).lower()
    
    # GitHub API 실패 시 대체 제안
    if tool_name == "github":
        if "get_user_info" in action or "get_repos" in action:
            return {
                "suggestion": "GitHub 정보를 가져올 수 없습니다. 대신 웹 검색을 통해 정보를 찾아보시겠어요?",
                "fallback_tool": "search",
                "fallback_action": "web_search",
                "fallback_params": {"query": f"GitHub {action.replace('get_', '')}"}
            }
    
    # MongoDB 실패 시 대체 제안
    elif tool_name == "mongodb":
        if "find_documents" in action or "count_documents" in action:
            return {
                "suggestion": "데이터베이스에 접근할 수 없습니다. 대신 웹 검색을 통해 관련 정보를 찾아보시겠어요?",
                "fallback_tool": "search",
                "fallback_action": "web_search",
                "fallback_params": {"query": "데이터베이스 관리"}
            }
    
    # 검색 툴 실패 시 대체 제안
    elif tool_name == "search":
        return {
            "suggestion": "검색 서비스에 접근할 수 없습니다. 다른 방법으로 도움을 드릴 수 있습니다.",
            "fallback_tool": None,
            "fallback_action": None,
            "fallback_params": {}
        }
    
    return None

def is_retryable_error(error: Exception) -> bool:
    """
    재시도 가능한 에러인지 판단
    
    Args:
        error: 발생한 예외
        
    Returns:
        재시도 가능 여부
    """
    error_str = str(error).lower()
    
    # 재시도 가능한 에러들
    retryable_keywords = [
        "connection", "timeout", "network", "unreachable",
        "rate limit", "quota", "temporary", "server error",
        "gateway", "bad gateway", "service unavailable"
    ]
    
    # 재시도 불가능한 에러들
    non_retryable_keywords = [
        "unauthorized", "forbidden", "not found", "bad request",
        "invalid", "malformed", "syntax error"
    ]
    
    # 재시도 불가능한 에러가 포함되어 있으면 False
    if any(keyword in error_str for keyword in non_retryable_keywords):
        return False
    
    # 재시도 가능한 에러가 포함되어 있으면 True
    if any(keyword in error_str for keyword in retryable_keywords):
        return True
    
    # 기본적으로는 재시도 가능
    return True

def log_error_with_context(error: Exception, tool_name: str, action: str, params: Dict[str, Any]):
    """
    컨텍스트와 함께 에러 로깅
    
    Args:
        error: 발생한 예외
        tool_name: 실패한 툴 이름
        action: 실패한 액션
        params: 실행 매개변수
    """
    logger.error(
        f"Tool execution failed - Tool: {tool_name}, Action: {action}, "
        f"Params: {params}, Error: {str(error)}",
        exc_info=True
    )

def create_error_response(
    error: Exception, 
    tool_name: str, 
    action: str, 
    params: Dict[str, Any],
    include_fallback: bool = True
) -> Dict[str, Any]:
    """
    표준화된 에러 응답 생성
    
    Args:
        error: 발생한 예외
        tool_name: 실패한 툴 이름
        action: 실패한 액션
        params: 실행 매개변수
        include_fallback: 대체 제안 포함 여부
        
    Returns:
        표준화된 에러 응답
    """
    # 에러 로깅
    log_error_with_context(error, tool_name, action, params)
    
    # 사용자 친화적 메시지 생성
    user_message = create_user_friendly_error_message(error, tool_name, action)
    
    # 기본 에러 응답
    error_response = {
        "status": "error",
        "message": user_message,
        "tool_name": tool_name,
        "action": action,
        "error_type": type(error).__name__,
        "retryable": is_retryable_error(error)
    }
    
    # 대체 제안 포함
    if include_fallback:
        fallback = get_fallback_suggestion(tool_name, action, error)
        if fallback:
            error_response["fallback_suggestion"] = fallback
    
    return error_response

