#!/usr/bin/env python3
"""
통합 최적화 서비스
- 모든 최적화 기능을 통합 관리
- 자동 성능 튜닝
- 동적 설정 조정
"""

import asyncio
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .background_preloader import background_preloader, register_preload_task
from .intelligent_cache_service import intelligent_cache
from .performance_monitor import monitor_performance, performance_monitor


@dataclass
class OptimizationConfig:
    """최적화 설정"""
    enable_intelligent_cache: bool = True
    enable_background_preloading: bool = True
    enable_performance_monitoring: bool = True
    auto_tuning_enabled: bool = True
    cache_memory_limit_mb: int = 500
    preload_max_concurrent: int = 2
    monitoring_interval_seconds: int = 30

class OptimizationService:
    """통합 최적화 서비스"""

    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self.is_initialized = False
        self.optimization_stats = {
            "start_time": None,
            "cache_hits": 0,
            "preloads_completed": 0,
            "performance_alerts": 0,
            "auto_tuning_adjustments": 0
        }

    async def initialize(self):
        """최적화 서비스 초기화"""
        if self.is_initialized:
            return

        print("🚀 통합 최적화 서비스 초기화 시작...")

        try:
            # 성능 모니터링 시작
            if self.config.enable_performance_monitoring:
                await performance_monitor.start()
                print("✅ 성능 모니터링 시작됨")

            # 백그라운드 프리로딩 설정
            if self.config.enable_background_preloading:
                await self._setup_background_preloading()
                await background_preloader.start()
                print("✅ 백그라운드 프리로딩 시작됨")

            # 자동 튜닝 시작
            if self.config.auto_tuning_enabled:
                asyncio.create_task(self._auto_tuning_loop())
                print("✅ 자동 튜닝 활성화됨")

            self.is_initialized = True
            self.optimization_stats["start_time"] = datetime.now()
            print("🎉 통합 최적화 서비스 초기화 완료!")

        except Exception as e:
            print(f"❌ 최적화 서비스 초기화 실패: {e}")
            raise

    async def _setup_background_preloading(self):
        """백그라운드 프리로딩 작업 설정"""
        # EmbeddingService 백업 모델 프리로딩
        register_preload_task(
            name="embedding_fallback_model",
            priority=8,
            load_function=self._load_embedding_fallback_model,
            estimated_load_time=15.0
        )

        # HuggingFace 분석기 프리로딩
        register_preload_task(
            name="huggingface_analyzer",
            priority=7,
            load_function=self._load_huggingface_analyzer,
            dependencies=["embedding_fallback_model"],
            estimated_load_time=45.0
        )

        # 자주 사용되는 모델들 프리로딩
        register_preload_task(
            name="sentence_transformer_models",
            priority=6,
            load_function=self._load_sentence_transformer_models,
            estimated_load_time=20.0
        )

    async def _load_embedding_fallback_model(self):
        """EmbeddingService 백업 모델 로딩"""
        try:
            from modules.core.services.embedding_service import EmbeddingService
            service = EmbeddingService(lazy_loading=False)
            service._load_fallback_model()
            print("✅ EmbeddingService 백업 모델 프리로딩 완료")
        except Exception as e:
            print(f"❌ EmbeddingService 백업 모델 프리로딩 실패: {e}")

    async def _load_huggingface_analyzer(self):
        """HuggingFace 분석기 로딩"""
        try:
            from modules.ai.huggingface_analyzer import HuggingFaceResumeAnalyzer
            analyzer = HuggingFaceResumeAnalyzer()
            print("✅ HuggingFace 분석기 프리로딩 완료")
        except Exception as e:
            print(f"❌ HuggingFace 분석기 프리로딩 실패: {e}")

    async def _load_sentence_transformer_models(self):
        """SentenceTransformer 모델들 로딩"""
        try:
            from sentence_transformers import SentenceTransformer

            # 자주 사용되는 모델들
            models = [
                'paraphrase-multilingual-MiniLM-L12-v2',
                'multi-qa-MiniLM-L6-cos-v1'
            ]

            for model_name in models:
                SentenceTransformer(model_name)
                print(f"✅ {model_name} 모델 로딩 완료")

        except Exception as e:
            print(f"❌ SentenceTransformer 모델 프리로딩 실패: {e}")

    async def _auto_tuning_loop(self):
        """자동 튜닝 루프"""
        while True:
            try:
                await asyncio.sleep(300)  # 5분마다 체크
                await self._perform_auto_tuning()
            except Exception as e:
                print(f"자동 튜닝 오류: {e}")
                await asyncio.sleep(600)  # 오류 시 10분 대기

    async def _perform_auto_tuning(self):
        """자동 튜닝 수행"""
        try:
            # 시스템 상태 확인
            system_health = performance_monitor.get_system_health()

            # 메모리 사용량이 높으면 캐시 정리
            if system_health.get("memory_percent", 0) > 80:
                await intelligent_cache.clear()
                print("🧹 메모리 압박으로 인한 캐시 정리")
                self.optimization_stats["auto_tuning_adjustments"] += 1

            # CPU 사용량이 높으면 프리로딩 일시 중지
            if system_health.get("cpu_percent", 0) > 90:
                await background_preloader.stop()
                await asyncio.sleep(60)  # 1분 대기
                await background_preloader.start()
                print("⏸️ CPU 사용량 높음으로 인한 프리로딩 일시 중지")
                self.optimization_stats["auto_tuning_adjustments"] += 1

            # 디스크 공간이 부족하면 캐시 크기 줄이기
            if system_health.get("disk_percent", 0) > 85:
                # 캐시 메모리 제한을 50%로 줄이기
                new_limit = self.config.cache_memory_limit_mb // 2
                intelligent_cache.max_memory_mb = new_limit
                print(f"💾 디스크 공간 부족으로 캐시 제한 조정: {new_limit}MB")
                self.optimization_stats["auto_tuning_adjustments"] += 1

        except Exception as e:
            print(f"자동 튜닝 수행 오류: {e}")

    def get_optimization_stats(self) -> Dict[str, Any]:
        """최적화 통계 반환"""
        stats = self.optimization_stats.copy()

        if self.config.enable_intelligent_cache:
            cache_stats = intelligent_cache.get_stats()
            stats["cache"] = cache_stats

        if self.config.enable_background_preloading:
            preloader_stats = background_preloader.get_stats()
            stats["preloader"] = preloader_stats

        if self.config.enable_performance_monitoring:
            system_health = performance_monitor.get_system_health()
            stats["system_health"] = system_health

        return stats

    async def optimize_for_environment(self, environment: str):
        """환경별 최적화 설정"""
        if environment == "development":
            # 개발 환경: 빠른 시작 우선
            self.config.cache_memory_limit_mb = 200
            self.config.preload_max_concurrent = 1
            self.config.monitoring_interval_seconds = 60
            print("🔧 개발 환경 최적화 설정 적용")

        elif environment == "production":
            # 프로덕션 환경: 성능 우선
            self.config.cache_memory_limit_mb = 1000
            self.config.preload_max_concurrent = 3
            self.config.monitoring_interval_seconds = 15
            print("🔧 프로덕션 환경 최적화 설정 적용")

        elif environment == "testing":
            # 테스트 환경: 최소 리소스
            self.config.cache_memory_limit_mb = 100
            self.config.preload_max_concurrent = 1
            self.config.monitoring_interval_seconds = 120
            self.config.auto_tuning_enabled = False
            print("🔧 테스트 환경 최적화 설정 적용")

    async def shutdown(self):
        """최적화 서비스 종료"""
        print("🛑 통합 최적화 서비스 종료 중...")

        try:
            if self.config.enable_background_preloading:
                await background_preloader.stop()
                print("✅ 백그라운드 프리로딩 중지됨")

            if self.config.enable_performance_monitoring:
                await performance_monitor.stop()
                print("✅ 성능 모니터링 중지됨")

            if self.config.enable_intelligent_cache:
                await intelligent_cache.close()
                print("✅ 지능형 캐시 종료됨")

            self.is_initialized = False
            print("🎉 통합 최적화 서비스 종료 완료!")

        except Exception as e:
            print(f"❌ 최적화 서비스 종료 중 오류: {e}")

# 전역 최적화 서비스 인스턴스
optimization_service = OptimizationService()

# 편의 함수들
async def initialize_optimization(environment: str = "development"):
    """최적화 서비스 초기화 편의 함수"""
    await optimization_service.optimize_for_environment(environment)
    await optimization_service.initialize()

async def shutdown_optimization():
    """최적화 서비스 종료 편의 함수"""
    await optimization_service.shutdown()

def get_optimization_stats() -> Dict[str, Any]:
    """최적화 통계 조회 편의 함수"""
    return optimization_service.get_optimization_stats()
