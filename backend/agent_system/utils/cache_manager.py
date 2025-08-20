"""
캐시 관리 시스템

툴 실행 결과를 캐싱하여 성능을 최적화하는 모듈입니다.
"""

import time
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
from cachetools import LRUCache, TTLCache
from threading import Lock

logger = logging.getLogger(__name__)

class CacheManager:
    """통합 캐시 관리자"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        캐시 매니저 초기화
        
        Args:
            max_size: 최대 캐시 항목 수
            ttl_seconds: 캐시 유효 시간 (초)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
        # LRU 캐시 (최근 사용된 항목 우선)
        self.lru_cache = LRUCache(maxsize=max_size)
        
        # TTL 캐시 (시간 기반 만료)
        self.ttl_cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        
        # 캐시 통계
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
        # 스레드 안전을 위한 락
        self.lock = Lock()
        
        logger.info(f"CacheManager initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def _generate_cache_key(self, tool_name: str, action: str, params: Dict[str, Any]) -> str:
        """
        캐시 키 생성
        
        Args:
            tool_name: 툴 이름
            action: 액션 이름
            params: 매개변수
            
        Returns:
            고유한 캐시 키
        """
        # 매개변수를 정렬된 JSON 문자열로 변환
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        
        # 키 구성
        key_data = f"{tool_name}:{action}:{sorted_params}"
        
        # SHA256 해시로 고유 키 생성
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    def get(self, tool_name: str, action: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        캐시에서 데이터 조회
        
        Args:
            tool_name: 툴 이름
            action: 액션 이름
            params: 매개변수
            
        Returns:
            캐시된 데이터 또는 None
        """
        with self.lock:
            self.stats["total_requests"] += 1
            
            cache_key = self._generate_cache_key(tool_name, action, params)
            
            # TTL 캐시에서 먼저 확인
            if cache_key in self.ttl_cache:
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT (TTL): {tool_name}.{action}")
                return self.ttl_cache[cache_key]
            
            # LRU 캐시에서 확인
            if cache_key in self.lru_cache:
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT (LRU): {tool_name}.{action}")
                return self.lru_cache[cache_key]
            
            self.stats["misses"] += 1
            logger.debug(f"Cache MISS: {tool_name}.{action}")
            return None
    
    def set(self, tool_name: str, action: str, params: Dict[str, Any], data: Dict[str, Any], use_ttl: bool = True):
        """
        캐시에 데이터 저장
        
        Args:
            tool_name: 툴 이름
            action: 액션 이름
            params: 매개변수
            data: 저장할 데이터
            use_ttl: TTL 캐시 사용 여부
        """
        with self.lock:
            cache_key = self._generate_cache_key(tool_name, action, params)
            
            # 캐시 데이터에 메타데이터 추가
            cache_data = {
                "data": data,
                "tool_name": tool_name,
                "action": action,
                "params": params,
                "cached_at": time.time(),
                "cache_type": "ttl" if use_ttl else "lru"
            }
            
            if use_ttl:
                self.ttl_cache[cache_key] = cache_data
                logger.debug(f"Data cached (TTL): {tool_name}.{action}")
            else:
                self.lru_cache[cache_key] = cache_data
                logger.debug(f"Data cached (LRU): {tool_name}.{action}")
    
    def invalidate(self, tool_name: str = None, action: str = None):
        """
        캐시 무효화
        
        Args:
            tool_name: 특정 툴만 무효화 (None이면 전체)
            action: 특정 액션만 무효화 (None이면 전체)
        """
        with self.lock:
            if tool_name is None:
                # 전체 캐시 무효화
                self.ttl_cache.clear()
                self.lru_cache.clear()
                logger.info("All cache invalidated")
            else:
                # 특정 툴/액션 무효화
                keys_to_remove = []
                
                # TTL 캐시에서 제거할 키 찾기
                for key, value in self.ttl_cache.items():
                    if (value.get("tool_name") == tool_name and 
                        (action is None or value.get("action") == action)):
                        keys_to_remove.append(key)
                
                # LRU 캐시에서 제거할 키 찾기
                for key, value in self.lru_cache.items():
                    if (value.get("tool_name") == tool_name and 
                        (action is None or value.get("action") == action)):
                        keys_to_remove.append(key)
                
                # 키 제거
                for key in keys_to_remove:
                    self.ttl_cache.pop(key, None)
                    self.lru_cache.pop(key, None)
                
                logger.info(f"Cache invalidated for {tool_name}.{action if action else 'all'}")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        with self.lock:
            hit_rate = (self.stats["hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
            
            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "total_requests": self.stats["total_requests"],
                "hit_rate": round(hit_rate, 2),
                "ttl_cache_size": len(self.ttl_cache),
                "lru_cache_size": len(self.lru_cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds
            }
    
    def clear(self):
        """전체 캐시 삭제"""
        with self.lock:
            self.ttl_cache.clear()
            self.lru_cache.clear()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0, "total_requests": 0}
            logger.info("All cache cleared")

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager(max_size=1000, ttl_seconds=3600)

def cache_result(use_ttl: bool = True, key_prefix: str = ""):
    """
    함수 결과 캐싱 데코레이터
    
    Args:
        use_ttl: TTL 캐시 사용 여부
        key_prefix: 캐시 키 접두사
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 함수 이름과 매개변수로 캐시 키 생성
            func_name = func.__name__
            cache_key = f"{key_prefix}:{func_name}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 캐시에서 확인
            cached_result = cache_manager.get("decorator", cache_key, {"args": args, "kwargs": kwargs})
            if cached_result:
                return cached_result["data"]
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set("decorator", cache_key, {"args": args, "kwargs": kwargs}, result, use_ttl)
            
            return result
        
        return wrapper
    return decorator

def cache_tool_result(use_ttl: bool = True):
    """
    툴 실행 결과 캐싱 데코레이터
    
    Args:
        use_ttl: TTL 캐시 사용 여부
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, action: str, **kwargs):
            tool_name = getattr(self, 'name', self.__class__.__name__)
            
            # 캐시에서 확인
            cached_result = cache_manager.get(tool_name, action, kwargs)
            if cached_result:
                logger.info(f"Using cached result for {tool_name}.{action}")
                return cached_result["data"]
            
            # 툴 실행
            result = func(self, action, **kwargs)
            
            # 성공한 결과만 캐싱
            if result.get("status") == "success":
                cache_manager.set(tool_name, action, kwargs, result, use_ttl)
                logger.info(f"Cached result for {tool_name}.{action}")
            
            return result
        
        return wrapper
    return decorator

class CacheConfig:
    """캐시 설정 클래스"""
    
    def __init__(self):
        self.tool_cache_configs = {
            "github": {
                "use_ttl": True,
                "ttl_seconds": 1800,  # 30분
                "max_size": 200
            },
            "mongodb": {
                "use_ttl": False,  # MongoDB는 실시간 데이터이므로 TTL 사용 안함
                "max_size": 100
            },
            "search": {
                "use_ttl": True,
                "ttl_seconds": 3600,  # 1시간
                "max_size": 300
            }
        }
    
    def get_config(self, tool_name: str) -> Dict[str, Any]:
        """툴별 캐시 설정 반환"""
        return self.tool_cache_configs.get(tool_name, {
            "use_ttl": True,
            "ttl_seconds": 1800,
            "max_size": 100
        })

# 전역 캐시 설정 인스턴스
cache_config = CacheConfig()

