#!/usr/bin/env python3
"""
지능형 캐싱 서비스
- 사용 패턴 기반 자동 캐시 관리
- 메모리 사용량 최적화
- 캐시 히트율 향상
"""

import asyncio
import gc
import hashlib
import json
import time
import weakref
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


class IntelligentCacheService:
    """지능형 캐싱 서비스"""

    def __init__(self, max_memory_mb: int = 500, ttl_hours: int = 24):
        self.max_memory_mb = max_memory_mb
        self.ttl_hours = ttl_hours

        # 캐시 저장소 (LRU 방식)
        self.cache = OrderedDict()
        self.access_times = {}
        self.access_counts = defaultdict(int)
        self.cache_sizes = {}

        # 통계
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

        # 백그라운드 정리 작업
        self._cleanup_task = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """백그라운드 정리 작업 시작"""
        if self._cleanup_task is None or self._cleanup_task.done():
            try:
                # 현재 실행 중인 이벤트 루프 확인
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
            except RuntimeError:
                # 이벤트 루프가 없으면 백그라운드에서 실행
                import threading
                def run_cleanup():
                    try:
                        asyncio.run(self._periodic_cleanup())
                    except Exception as e:
                        print(f"백그라운드 캐시 정리 오류: {e}")

                cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
                cleanup_thread.start()

    async def _periodic_cleanup(self):
        """주기적 캐시 정리"""
        while True:
            try:
                await asyncio.sleep(300)  # 5분마다 정리
                await self._cleanup_expired()
                await self._cleanup_memory_pressure()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"캐시 정리 중 오류: {e}")

    async def _cleanup_expired(self):
        """만료된 캐시 정리"""
        current_time = time.time()
        expired_keys = []

        for key, (data, timestamp) in self.cache.items():
            if current_time - timestamp > self.ttl_hours * 3600:
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_from_cache(key)
            self.eviction_count += 1

    async def _cleanup_memory_pressure(self):
        """메모리 압박 시 캐시 정리"""
        current_memory = self._estimate_memory_usage()
        if current_memory > self.max_memory_mb * 1024 * 1024:
            # 가장 오래된 20% 제거
            keys_to_remove = list(self.cache.keys())[:len(self.cache) // 5]
            for key in keys_to_remove:
                self._remove_from_cache(key)
                self.eviction_count += 1

    def _estimate_memory_usage(self) -> int:
        """메모리 사용량 추정 (바이트)"""
        total_size = 0
        for key, (data, _) in self.cache.items():
            try:
                size = len(json.dumps(data, default=str).encode('utf-8'))
                total_size += size
            except:
                total_size += 1024  # 추정값
        return total_size

    def _remove_from_cache(self, key: str):
        """캐시에서 항목 제거"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
        if key in self.cache_sizes:
            del self.cache_sizes[key]

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        key = self._generate_cache_key(prefix, *args, **kwargs)

        if key in self.cache:
            data, timestamp = self.cache[key]

            # TTL 체크
            if time.time() - timestamp > self.ttl_hours * 3600:
                self._remove_from_cache(key)
                self.miss_count += 1
                return None

            # LRU 업데이트
            self.cache.move_to_end(key)
            self.access_times[key] = time.time()
            self.access_counts[key] += 1
            self.hit_count += 1

            return data

        self.miss_count += 1
        return None

    async def set(self, prefix: str, data: Any, *args, **kwargs):
        """캐시에 데이터 저장"""
        key = self._generate_cache_key(prefix, *args, **kwargs)
        timestamp = time.time()

        # 기존 항목이 있으면 제거
        if key in self.cache:
            self._remove_from_cache(key)

        # 새 항목 추가
        self.cache[key] = (data, timestamp)
        self.access_times[key] = timestamp
        self.access_counts[key] = 1

        # 크기 추정
        try:
            size = len(json.dumps(data, default=str).encode('utf-8'))
            self.cache_sizes[key] = size
        except:
            self.cache_sizes[key] = 1024

    async def invalidate(self, prefix: str, *args, **kwargs):
        """캐시 무효화"""
        key = self._generate_cache_key(prefix, *args, **kwargs)
        if key in self.cache:
            self._remove_from_cache(key)

    async def invalidate_pattern(self, pattern: str):
        """패턴으로 캐시 무효화"""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        for key in keys_to_remove:
            self._remove_from_cache(key)

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_size": len(self.cache),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
            "eviction_count": self.eviction_count,
            "memory_usage_mb": self._estimate_memory_usage() / (1024 * 1024),
            "max_memory_mb": self.max_memory_mb,
            "ttl_hours": self.ttl_hours
        }

    async def clear(self):
        """전체 캐시 클리어"""
        self.cache.clear()
        self.access_times.clear()
        self.access_counts.clear()
        self.cache_sizes.clear()
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0

    async def close(self):
        """캐시 서비스 종료"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.clear()

# 전역 캐시 인스턴스
intelligent_cache = IntelligentCacheService()

# 데코레이터
def cache_result(prefix: str, ttl_hours: int = 24):
    """함수 결과 캐싱 데코레이터"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성 (함수명 + 인자)
            cache_key_args = (func.__name__,) + args
            cache_key_kwargs = kwargs

            # 캐시에서 조회
            cached_result = await intelligent_cache.get(
                prefix, *cache_key_args, **cache_key_kwargs
            )

            if cached_result is not None:
                return cached_result

            # 함수 실행
            result = await func(*args, **kwargs)

            # 결과 캐싱
            await intelligent_cache.set(
                prefix, result, *cache_key_args, **cache_key_kwargs
            )

            return result
        return wrapper
    return decorator
