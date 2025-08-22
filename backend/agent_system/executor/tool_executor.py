"""
툴 실행기

모든 백엔드 툴을 통합 관리하고 실행하는 허브 역할을 합니다.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from agent_system.tools import GitHubTool, MongoDBTool, SearchTool
from agent_system.utils.error_handler import (
    retry_with_backoff, 
    RetryConfig, 
    create_error_response,
    is_retryable_error
)
from agent_system.utils.cache_manager import cache_manager, cache_config
from agent_system.utils.async_utils import async_executor, monitor_performance
from agent_system.utils.monitoring import log_tool_execution, monitoring_system

logger = logging.getLogger(__name__)

class ToolExecutor:
    """툴 실행기 - 모든 툴의 통합 관리자"""
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
        logger.info("ToolExecutor initialized with available tools")
    
    def _initialize_tools(self):
        """사용 가능한 툴들을 초기화"""
        try:
            # GitHub 툴 초기화
            self.tools["github"] = GitHubTool()
            logger.info("GitHub tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub tool: {e}")
        
        try:
            # MongoDB 툴 초기화
            self.tools["mongodb"] = MongoDBTool()
            logger.info("MongoDB tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB tool: {e}")
        
        try:
            # 검색 툴 초기화
            self.tools["search"] = SearchTool()
            logger.info("Search tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Search tool: {e}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """사용 가능한 툴 목록 반환"""
        tools_info = []
        for tool_name, tool in self.tools.items():
            tools_info.append({
                "name": tool_name,
                "info": tool.get_info()
            })
        return tools_info
    
    async def _execute_with_retry_async(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        비동기 재시도 로직이 포함된 툴 실행
        
        Args:
            tool_name: 실행할 툴 이름
            action: 실행할 액션
            **kwargs: 액션에 필요한 매개변수들
            
        Returns:
            표준화된 결과 딕셔너리
        """
        if tool_name not in self.tools:
            return {
                "status": "error",
                "message": f"알 수 없는 툴입니다: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        
        # 캐시에서 확인
        cached_result = cache_manager.get(tool_name, action, kwargs)
        if cached_result:
            logger.info(f"Using cached result for {tool_name}.{action}")
            
            # 캐시 히트 모니터링 로그 기록
            log_tool_execution(
                session_id=kwargs.get('session_id', 'unknown'),
                tool=tool_name,
                action=action,
                status="success",
                duration_ms=1,  # 캐시 히트는 매우 빠름
                parameters=kwargs,
                response_size=len(str(cached_result["data"])) if cached_result["data"] else 0,
                cache_hit=True,
                retry_count=0
            )
            
            return cached_result["data"]
        
        # 재시도 설정 (툴별로 다르게 설정 가능)
        retry_config = self._get_retry_config_for_tool(tool_name)
        
        @retry_with_backoff(retry_config)
        def execute_tool():
            return tool.execute(action, **kwargs)
        
        start_time = time.time()
        session_id = kwargs.get('session_id', 'unknown')
        
        try:
            # 스레드 풀에서 실행 (I/O 바운드 작업)
            result = await async_executor.run_in_thread(execute_tool)
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Tool execution completed: {tool_name}.{action}")
            
            # 성공한 결과만 캐싱
            if result.get("status") == "success":
                cache_config_obj = cache_config.get_config(tool_name)
                cache_manager.set(tool_name, action, kwargs, result, cache_config_obj.get("use_ttl", True))
                logger.info(f"Cached result for {tool_name}.{action}")
            
            # 모니터링 로그 기록
            log_tool_execution(
                session_id=session_id,
                tool=tool_name,
                action=action,
                status=result.get("status", "unknown"),
                duration_ms=duration_ms,
                parameters=kwargs,
                response_size=len(str(result)) if result else 0,
                cache_hit=False,  # 캐시 히트는 이미 위에서 처리됨
                retry_count=result.get("retry_count", 0)
            )
            
            return result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 에러 모니터링 로그 기록
            log_tool_execution(
                session_id=session_id,
                tool=tool_name,
                action=action,
                status="error",
                duration_ms=duration_ms,
                error_message=str(e),
                parameters=kwargs
            )
            
            # 에러 처리 및 복구
            return self._handle_tool_error(e, tool_name, action, kwargs)
    
    def _execute_with_retry(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        동기 재시도 로직이 포함된 툴 실행 (하위 호환성)
        
        Args:
            tool_name: 실행할 툴 이름
            action: 실행할 액션
            **kwargs: 액션에 필요한 매개변수들
            
        Returns:
            표준화된 결과 딕셔너리
        """
        # 비동기 실행을 동기적으로 래핑
        return asyncio.run(self._execute_with_retry_async(tool_name, action, **kwargs))
    
    def _get_retry_config_for_tool(self, tool_name: str) -> RetryConfig:
        """툴별 재시도 설정 반환"""
        if tool_name == "github":
            # GitHub API는 네트워크 의존적이므로 더 많은 재시도
            return RetryConfig(max_retries=3, delay=1.0, backoff_factor=2.0)
        elif tool_name == "mongodb":
            # MongoDB는 로컬 연결이므로 적은 재시도
            return RetryConfig(max_retries=2, delay=0.5, backoff_factor=1.5)
        elif tool_name == "search":
            # 검색 API는 외부 의존적이므로 중간 재시도
            return RetryConfig(max_retries=2, delay=1.0, backoff_factor=2.0)
        else:
            # 기본 설정
            return RetryConfig()
    
    def _handle_tool_error(self, error: Exception, tool_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        툴 실행 에러 처리 및 복구
        
        Args:
            error: 발생한 예외
            tool_name: 실패한 툴 이름
            action: 실패한 액션
            params: 실행 매개변수
            
        Returns:
            에러 처리 결과
        """
        logger.error(f"Tool execution failed: {tool_name}.{action} - {str(error)}")
        
        # 표준화된 에러 응답 생성
        error_response = create_error_response(error, tool_name, action, params)
        
        # 재시도 가능한 에러인지 확인
        if is_retryable_error(error):
            error_response["message"] += " 자동으로 재시도 중입니다."
        
        return error_response
    
    @monitor_performance
    async def execute_async(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        비동기 툴 실행 (에러 처리 포함)
        
        Args:
            tool_name: 실행할 툴 이름
            action: 실행할 액션
            **kwargs: 액션에 필요한 매개변수들
            
        Returns:
            표준화된 결과 딕셔너리
        """
        logger.info(f"Executing tool async: {tool_name}, action: {action}")
        
        # 재시도 로직이 포함된 실행
        result = await self._execute_with_retry_async(tool_name, action, **kwargs)
        
        # 성공한 경우 그대로 반환
        if result.get("status") == "success":
            return result
        
        # 실패한 경우 대체 툴 시도
        return await self._try_fallback_execution_async(tool_name, action, result, **kwargs)
    
    def execute(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        동기 툴 실행 (에러 처리 포함, 하위 호환성)
        
        Args:
            tool_name: 실행할 툴 이름
            action: 실행할 액션
            **kwargs: 액션에 필요한 매개변수들
            
        Returns:
            표준화된 결과 딕셔너리
        """
        # 비동기 실행을 동기적으로 래핑
        return asyncio.run(self.execute_async(tool_name, action, **kwargs))
    
    async def _try_fallback_execution_async(self, original_tool: str, action: str, error_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        비동기 대체 툴로 실행 시도
        
        Args:
            original_tool: 원래 실패한 툴
            action: 실행할 액션
            error_result: 원래 에러 결과
            **kwargs: 실행 매개변수
            
        Returns:
            대체 실행 결과 또는 원래 에러 결과
        """
        # 대체 제안이 있는지 확인
        fallback_suggestion = error_result.get("fallback_suggestion")
        if not fallback_suggestion:
            return error_result
        
        fallback_tool = fallback_suggestion.get("fallback_tool")
        fallback_action = fallback_suggestion.get("fallback_action")
        fallback_params = fallback_suggestion.get("fallback_params", {})
        
        if not fallback_tool or not fallback_action:
            return error_result
        
        logger.info(f"Trying fallback async: {fallback_tool}.{fallback_action}")
        
        try:
            # 대체 툴로 실행
            fallback_result = await self._execute_with_retry_async(fallback_tool, fallback_action, **fallback_params)
            
            if fallback_result.get("status") == "success":
                # 대체 툴 성공 시 원래 에러 정보와 함께 반환
                fallback_result["original_error"] = {
                    "tool": original_tool,
                    "action": action,
                    "message": error_result.get("message", "")
                }
                fallback_result["fallback_used"] = True
                return fallback_result
            else:
                # 대체 툴도 실패한 경우
                return error_result
                
        except Exception as e:
            logger.error(f"Fallback execution also failed: {str(e)}")
            return error_result
    
    def _try_fallback_execution(self, original_tool: str, action: str, error_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        동기 대체 툴로 실행 시도 (하위 호환성)
        
        Args:
            original_tool: 원래 실패한 툴
            action: 실행할 액션
            error_result: 원래 에러 결과
            **kwargs: 실행 매개변수
            
        Returns:
            대체 실행 결과 또는 원래 에러 결과
        """
        # 비동기 실행을 동기적으로 래핑
        return asyncio.run(self._try_fallback_execution_async(original_tool, action, error_result, **kwargs))
    
    async def execute_batch_async(self, executions: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        여러 툴을 비동기 배치로 실행 (에러 처리 포함)
        
        Args:
            executions: 실행할 툴 목록
                [
                    {"tool": "github", "action": "get_user_info", "username": "kyungho222"},
                    {"tool": "mongodb", "action": "find_documents", "collection": "users"}
                ]
            max_concurrent: 최대 동시 실행 수
                
        Returns:
            실행 결과 목록
        """
        async def execute_single(execution):
            tool_name = execution.get("tool")
            action = execution.get("action")
            params = {k: v for k, v in execution.items() if k not in ["tool", "action"]}
            
            result = await self.execute_async(tool_name, action, **params)
            return {
                "execution": execution,
                "result": result
            }
        
        # 비동기 배치 실행
        tasks = [execute_single(execution) for execution in executions]
        results = await async_executor.execute_batch(tasks, max_concurrent)
        
        return results
    
    def execute_batch(self, executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 툴을 배치로 실행 (에러 처리 포함, 하위 호환성)
        
        Args:
            executions: 실행할 툴 목록
                [
                    {"tool": "github", "action": "get_user_info", "username": "kyungho222"},
                    {"tool": "mongodb", "action": "find_documents", "collection": "users"}
                ]
                
        Returns:
            실행 결과 목록
        """
        # 비동기 실행을 동기적으로 래핑
        return asyncio.run(self.execute_batch_async(executions))
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """특정 툴의 정보 반환"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return tool.get_info()
    
    def validate_tool_action(self, tool_name: str, action: str) -> bool:
        """툴과 액션의 유효성 검증"""
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        # BaseTool의 execute 메서드가 모든 액션을 처리하므로 항상 True
        return True
    
    def get_supported_actions(self, tool_name: str) -> List[str]:
        """특정 툴이 지원하는 액션 목록 반환"""
        if tool_name == "github":
            return [
                "get_user_info",
                "get_repos", 
                "get_repo_details",
                "get_commits",
                "search_repos"
            ]
        elif tool_name == "mongodb":
            return [
                "find_documents",
                "find_one",
                "insert_document",
                "update_document", 
                "delete_document",
                "count_documents",
                "aggregate",
                "get_collections"
            ]
        elif tool_name == "search":
            return [
                "web_search",
                "news_search",
                "image_search",
                "local_search"
            ]
        else:
            return []
    
    def get_tool_status(self) -> Dict[str, Any]:
        """모든 툴의 상태 정보 반환"""
        status = {
            "total_tools": len(self.tools),
            "available_tools": list(self.tools.keys()),
            "tools_status": {}
        }
        
        for tool_name, tool in self.tools.items():
            try:
                # 간단한 연결 테스트
                if tool_name == "mongodb":
                    # MongoDB 연결 테스트
                    test_result = tool.execute("count_documents", collection="test", query={})
                    is_healthy = test_result["status"] != "error"
                elif tool_name == "github":
                    # GitHub API 연결 테스트 (빈 쿼리로 테스트)
                    is_healthy = True  # GitHub는 API 키가 없어도 기본 기능 사용 가능
                elif tool_name == "search":
                    # 검색 API 연결 테스트
                    is_healthy = tool.google_api_key is not None
                else:
                    is_healthy = True
                
                status["tools_status"][tool_name] = {
                    "healthy": is_healthy,
                    "info": tool.get_info()
                }
            except Exception as e:
                status["tools_status"][tool_name] = {
                    "healthy": False,
                    "error": str(e),
                    "info": tool.get_info()
                }
        
        return status
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 정보 반환"""
        # 실제 구현에서는 에러 로그를 분석하여 통계 제공
        return {
            "total_errors": 0,
            "errors_by_tool": {},
            "most_common_errors": [],
            "recovery_rate": 0.0
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 정보 반환"""
        return {
            "cache_stats": cache_manager.get_stats(),
            "performance_stats": performance_monitor.get_stats(),
            "tool_status": self.get_tool_status()
        }
    
    def clear_cache(self, tool_name: str = None):
        """캐시 정리"""
        cache_manager.invalidate(tool_name)
        logger.info(f"Cache cleared for {tool_name if tool_name else 'all tools'}")
    
    def reset_performance_stats(self):
        """성능 통계 초기화"""
        performance_monitor.reset()
        logger.info("Performance statistics reset")
