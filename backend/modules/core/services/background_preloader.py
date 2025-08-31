#!/usr/bin/env python3
"""
백그라운드 프리로딩 서비스
- 사용 패턴 분석 기반 모델 프리로딩
- 서버 시작 후 백그라운드에서 모델 로딩
- 사용량 기반 우선순위 관리
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class PreloadTask:
    """프리로드 작업 정보"""
    name: str
    priority: int  # 1-10 (높을수록 우선순위 높음)
    load_function: Callable
    dependencies: List[str] = None
    estimated_load_time: float = 0.0
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_loaded: bool = False
    load_start_time: Optional[datetime] = None

class BackgroundPreloader:
    """백그라운드 프리로더"""

    def __init__(self, max_concurrent_loads: int = 2):
        self.max_concurrent_loads = max_concurrent_loads
        self.tasks: Dict[str, PreloadTask] = {}
        self.loading_tasks: Dict[str, asyncio.Task] = {}
        self.usage_patterns = defaultdict(lambda: deque(maxlen=100))
        self.is_running = False
        self._preload_task = None

        # 통계
        self.total_preloads = 0
        self.successful_preloads = 0
        self.failed_preloads = 0
        self.cache_hits = 0

    def register_task(self, task: PreloadTask):
        """프리로드 작업 등록"""
        self.tasks[task.name] = task
        logger.info(f"프리로드 작업 등록: {task.name} (우선순위: {task.priority})")

    def record_usage(self, task_name: str):
        """사용 기록"""
        if task_name in self.tasks:
            self.tasks[task_name].last_used = datetime.now()
            self.tasks[task_name].usage_count += 1
            self.usage_patterns[task_name].append(time.time())

            # 이미 로딩된 경우 캐시 히트
            if self.tasks[task_name].is_loaded:
                self.cache_hits += 1

    def _calculate_priority_score(self, task: PreloadTask) -> float:
        """우선순위 점수 계산"""
        base_priority = task.priority

        # 사용 빈도 가중치
        usage_weight = min(task.usage_count / 10.0, 1.0)

        # 최근 사용 시간 가중치
        recency_weight = 0.0
        if task.last_used:
            hours_since_use = (datetime.now() - task.last_used).total_seconds() / 3600
            recency_weight = max(0, 1.0 - hours_since_use / 24)  # 24시간 내 사용

        # 로딩 시간 가중치 (짧을수록 높은 점수)
        load_time_weight = max(0, 1.0 - task.estimated_load_time / 60.0)  # 60초 기준

        return base_priority + usage_weight * 2 + recency_weight * 1.5 + load_time_weight * 0.5

    def _get_next_tasks(self) -> List[PreloadTask]:
        """다음 로딩할 작업들 선택"""
        # 아직 로딩되지 않은 작업들
        unloaded_tasks = [task for task in self.tasks.values() if not task.is_loaded]

        # 의존성 확인
        available_tasks = []
        for task in unloaded_tasks:
            if task.dependencies:
                dependencies_loaded = all(
                    self.tasks.get(dep, PreloadTask("", 0, lambda: None)).is_loaded
                    for dep in task.dependencies
                )
                if not dependencies_loaded:
                    continue
            available_tasks.append(task)

        # 우선순위 점수로 정렬
        available_tasks.sort(key=self._calculate_priority_score, reverse=True)

        return available_tasks[:self.max_concurrent_loads]

    async def _load_task(self, task: PreloadTask):
        """개별 작업 로딩"""
        try:
            logger.info(f"프리로딩 시작: {task.name}")
            task.load_start_time = datetime.now()

            # 비동기 함수인지 확인
            if asyncio.iscoroutinefunction(task.load_function):
                await task.load_function()
            else:
                # 동기 함수를 비동기로 실행
                await asyncio.get_event_loop().run_in_executor(None, task.load_function)

            task.is_loaded = True
            self.successful_preloads += 1
            self.total_preloads += 1

            load_time = (datetime.now() - task.load_start_time).total_seconds()
            logger.info(f"프리로딩 완료: {task.name} ({load_time:.2f}초)")

        except Exception as e:
            self.failed_preloads += 1
            self.total_preloads += 1
            logger.error(f"프리로딩 실패: {task.name} - {e}")
        finally:
            if task.name in self.loading_tasks:
                del self.loading_tasks[task.name]

    async def _preload_loop(self):
        """프리로딩 루프"""
        logger.info("백그라운드 프리로더 시작")

        while self.is_running:
            try:
                # 현재 로딩 중인 작업 수 확인
                current_loads = len(self.loading_tasks)

                if current_loads < self.max_concurrent_loads:
                    # 다음 작업들 가져오기
                    next_tasks = self._get_next_tasks()

                    for task in next_tasks:
                        if len(self.loading_tasks) >= self.max_concurrent_loads:
                            break

                        # 로딩 작업 시작
                        load_task = asyncio.create_task(self._load_task(task))
                        self.loading_tasks[task.name] = load_task

                # 10초 대기
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"프리로딩 루프 오류: {e}")
                await asyncio.sleep(30)  # 오류 시 더 긴 대기

    async def start(self):
        """프리로더 시작"""
        if not self.is_running:
            self.is_running = True
            self._preload_task = asyncio.create_task(self._preload_loop())
            logger.info("백그라운드 프리로더 시작됨")

    async def stop(self):
        """프리로더 중지"""
        if self.is_running:
            self.is_running = False

            # 진행 중인 로딩 작업들 취소
            for task in self.loading_tasks.values():
                task.cancel()

            # 메인 루프 종료 대기
            if self._preload_task:
                self._preload_task.cancel()
                try:
                    await self._preload_task
                except asyncio.CancelledError:
                    pass

            logger.info("백그라운드 프리로더 중지됨")

    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        loaded_count = sum(1 for task in self.tasks.values() if task.is_loaded)
        loading_count = len(self.loading_tasks)

        return {
            "total_tasks": len(self.tasks),
            "loaded_tasks": loaded_count,
            "loading_tasks": loading_count,
            "total_preloads": self.total_preloads,
            "successful_preloads": self.successful_preloads,
            "failed_preloads": self.failed_preloads,
            "cache_hits": self.cache_hits,
            "success_rate": (self.successful_preloads / self.total_preloads * 100) if self.total_preloads > 0 else 0,
            "is_running": self.is_running
        }

    def get_task_status(self) -> Dict[str, Dict[str, Any]]:
        """작업별 상태 반환"""
        status = {}
        for name, task in self.tasks.items():
            status[name] = {
                "is_loaded": task.is_loaded,
                "is_loading": name in self.loading_tasks,
                "priority": task.priority,
                "usage_count": task.usage_count,
                "last_used": task.last_used.isoformat() if task.last_used else None,
                "estimated_load_time": task.estimated_load_time
            }
        return status

# 전역 프리로더 인스턴스
background_preloader = BackgroundPreloader()

# 편의 함수들
def register_preload_task(name: str, priority: int, load_function: Callable,
                         dependencies: List[str] = None, estimated_load_time: float = 0.0):
    """프리로드 작업 등록 편의 함수"""
    task = PreloadTask(
        name=name,
        priority=priority,
        load_function=load_function,
        dependencies=dependencies or [],
        estimated_load_time=estimated_load_time
    )
    background_preloader.register_task(task)

def record_model_usage(model_name: str):
    """모델 사용 기록 편의 함수"""
    background_preloader.record_usage(model_name)
