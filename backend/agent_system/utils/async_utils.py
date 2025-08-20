"""
비동기 처리 유틸리티

동시 요청 처리와 성능 최적화를 위한 비동기 처리 모듈입니다.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps
import httpx
import aiohttp

logger = logging.getLogger(__name__)

class AsyncExecutor:
    """비동기 실행 관리자"""
    
    def __init__(self, max_workers: int = 10, max_processes: int = 4):
        """
        비동기 실행기 초기화
        
        Args:
            max_workers: 스레드 풀 최대 워커 수
            max_processes: 프로세스 풀 최대 워커 수
        """
        self.max_workers = max_workers
        self.max_processes = max_processes
        
        # 스레드 풀 (I/O 바운드 작업용)
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # 프로세스 풀 (CPU 바운드 작업용)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        
        # HTTP 클라이언트 풀
        self.http_client = None
        
        logger.info(f"AsyncExecutor initialized: threads={max_workers}, processes={max_processes}")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.http_client:
            await self.http_client.aclose()
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """
        스레드 풀에서 함수 실행 (I/O 바운드 작업)
        
        Args:
            func: 실행할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            함수 실행 결과
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
    
    async def run_in_process(self, func: Callable, *args, **kwargs) -> Any:
        """
        프로세스 풀에서 함수 실행 (CPU 바운드 작업)
        
        Args:
            func: 실행할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            함수 실행 결과
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args, **kwargs)
    
    async def execute_batch(self, tasks: List[Coroutine], max_concurrent: int = 5) -> List[Any]:
        """
        여러 작업을 배치로 실행
        
        Args:
            tasks: 실행할 코루틴 목록
            max_concurrent: 최대 동시 실행 수
            
        Returns:
            실행 결과 목록
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(*[execute_with_semaphore(task) for task in tasks])
    
    async def execute_with_timeout(self, coro: Coroutine, timeout: float = 30.0) -> Any:
        """
        타임아웃과 함께 코루틴 실행
        
        Args:
            coro: 실행할 코루틴
            timeout: 타임아웃 시간 (초)
            
        Returns:
            실행 결과
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Task timed out after {timeout} seconds")
            raise

def async_retry(max_retries: int = 3, delay: float = 1.0):
    """
    비동기 함수 재시도 데코레이터
    
    Args:
        max_retries: 최대 재시도 횟수
        delay: 재시도 간격 (초)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < max_retries:
                        await asyncio.sleep(delay * (2 ** attempt))  # 지수 백오프
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator

class HTTPClient:
    """비동기 HTTP 클라이언트"""
    
    def __init__(self, timeout: float = 30.0, max_connections: int = 100):
        """
        HTTP 클라이언트 초기화
        
        Args:
            timeout: 요청 타임아웃 (초)
            max_connections: 최대 연결 수
        """
        self.timeout = timeout
        self.max_connections = max_connections
        self.session = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        connector = aiohttp.TCPConnector(limit=self.max_connections)
        self.session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    @async_retry(max_retries=3, delay=1.0)
    async def get(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        GET 요청
        
        Args:
            url: 요청 URL
            headers: 요청 헤더
            
        Returns:
            응답 데이터
        """
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    @async_retry(max_retries=3, delay=1.0)
    async def post(self, url: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        POST 요청
        
        Args:
            url: 요청 URL
            data: 요청 데이터
            headers: 요청 헤더
            
        Returns:
            응답 데이터
        """
        async with self.session.post(url, json=data, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        self.start_time = time.time()
    
    def record_request(self, success: bool, response_time: float):
        """
        요청 기록
        
        Args:
            success: 성공 여부
            response_time: 응답 시간 (초)
        """
        self.metrics["total_requests"] += 1
        self.metrics["total_response_time"] += response_time
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        # 평균 응답 시간 계산
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["total_requests"]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        uptime = time.time() - self.start_time
        success_rate = (
            self.metrics["successful_requests"] / self.metrics["total_requests"] * 100
        ) if self.metrics["total_requests"] > 0 else 0
        
        return {
            **self.metrics,
            "uptime_seconds": round(uptime, 2),
            "success_rate": round(success_rate, 2),
            "requests_per_second": round(self.metrics["total_requests"] / uptime, 2) if uptime > 0 else 0
        }
    
    def reset(self):
        """통계 초기화"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        self.start_time = time.time()

# 전역 인스턴스들
async_executor = AsyncExecutor()
performance_monitor = PerformanceMonitor()

def monitor_performance(func: Callable) -> Callable:
    """
    성능 모니터링 데코레이터
    
    Args:
        func: 모니터링할 함수
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        
        try:
            result = await func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {str(e)}")
            raise
        finally:
            response_time = time.time() - start_time
            performance_monitor.record_request(success, response_time)
    
    return wrapper
