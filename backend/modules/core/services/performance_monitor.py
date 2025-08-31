#!/usr/bin/env python3
"""
성능 모니터링 서비스
- 실시간 성능 메트릭 수집
- 메모리 사용량 모니터링
- 응답 시간 추적
- 알림 시스템
"""

import asyncio
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """성능 메트릭 데이터"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AlertRule:
    """알림 규칙"""
    name: str
    metric_name: str
    threshold: float
    operator: str  # '>', '<', '>=', '<=', '=='
    duration_seconds: int = 60  # 지속 시간
    enabled: bool = True

class PerformanceMonitor:
    """성능 모니터링 서비스"""

    def __init__(self, max_metrics_per_type: int = 1000):
        self.max_metrics_per_type = max_metrics_per_type
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.is_monitoring = False
        self._monitor_task = None
        self._alert_check_task = None

        # 시스템 메트릭 수집 간격
        self.system_metrics_interval = 30  # 30초
        self.application_metrics_interval = 10  # 10초

        # 기본 알림 규칙 설정
        self._setup_default_alerts()

    def _setup_default_alerts(self):
        """기본 알림 규칙 설정"""
        default_rules = [
            AlertRule("high_cpu", "system.cpu_percent", 80.0, ">", 60),
            AlertRule("high_memory", "system.memory_percent", 85.0, ">", 60),
            AlertRule("high_disk", "system.disk_percent", 90.0, ">", 60),
            AlertRule("slow_response", "application.response_time", 5.0, ">", 30),
            AlertRule("high_error_rate", "application.error_rate", 10.0, ">", 60),
        ]

        for rule in default_rules:
            self.add_alert_rule(rule)

    def add_metric(self, metric_name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """메트릭 추가"""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.metrics[metric_name].append(metric)

    def add_alert_rule(self, rule: AlertRule):
        """알림 규칙 추가"""
        self.alert_rules.append(rule)
        logger.info(f"알림 규칙 추가: {rule.name} ({rule.metric_name} {rule.operator} {rule.threshold})")

    def remove_alert_rule(self, rule_name: str):
        """알림 규칙 제거"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]

    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric("system.cpu_percent", cpu_percent, "%")

            # 메모리 사용률
            memory = psutil.virtual_memory()
            self.add_metric("system.memory_percent", memory.percent, "%")
            self.add_metric("system.memory_used_mb", memory.used / 1024 / 1024, "MB")
            self.add_metric("system.memory_available_mb", memory.available / 1024 / 1024, "MB")

            # 디스크 사용률
            disk = psutil.disk_usage('/')
            self.add_metric("system.disk_percent", (disk.used / disk.total) * 100, "%")
            self.add_metric("system.disk_used_gb", disk.used / 1024 / 1024 / 1024, "GB")
            self.add_metric("system.disk_free_gb", disk.free / 1024 / 1024 / 1024, "GB")

            # 네트워크 I/O
            net_io = psutil.net_io_counters()
            self.add_metric("system.network_bytes_sent", net_io.bytes_sent, "bytes")
            self.add_metric("system.network_bytes_recv", net_io.bytes_recv, "bytes")

            # 프로세스 정보
            process = psutil.Process()
            self.add_metric("application.process_memory_mb", process.memory_info().rss / 1024 / 1024, "MB")
            self.add_metric("application.process_cpu_percent", process.cpu_percent(), "%")
            self.add_metric("application.process_threads", process.num_threads(), "count")

        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")

    def _check_alerts(self):
        """알림 규칙 확인"""
        current_time = datetime.now()

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # 최근 메트릭 값들 확인
            recent_metrics = list(self.metrics[rule.metric_name])
            if not recent_metrics:
                continue

            # 지정된 시간 동안의 메트릭들 필터링
            cutoff_time = current_time - timedelta(seconds=rule.duration_seconds)
            relevant_metrics = [
                m for m in recent_metrics
                if m.timestamp >= cutoff_time
            ]

            if not relevant_metrics:
                continue

            # 평균값 계산
            avg_value = sum(m.value for m in relevant_metrics) / len(relevant_metrics)

            # 알림 조건 확인
            alert_triggered = False
            if rule.operator == '>':
                alert_triggered = avg_value > rule.threshold
            elif rule.operator == '<':
                alert_triggered = avg_value < rule.threshold
            elif rule.operator == '>=':
                alert_triggered = avg_value >= rule.threshold
            elif rule.operator == '<=':
                alert_triggered = avg_value <= rule.threshold
            elif rule.operator == '==':
                alert_triggered = abs(avg_value - rule.threshold) < 0.01

            if alert_triggered:
                if rule.name not in self.active_alerts:
                    self.active_alerts[rule.name] = current_time
                    self._send_alert(rule, avg_value, relevant_metrics)
            else:
                if rule.name in self.active_alerts:
                    del self.active_alerts[rule.name]
                    self._send_alert_resolved(rule, avg_value)

    def _send_alert(self, rule: AlertRule, current_value: float, metrics: List[PerformanceMetric]):
        """알림 전송"""
        alert_message = (
            f"🚨 성능 알림: {rule.name}\n"
            f"메트릭: {rule.metric_name}\n"
            f"현재값: {current_value:.2f}{metrics[0].unit if metrics else ''}\n"
            f"임계값: {rule.threshold}{metrics[0].unit if metrics else ''}\n"
            f"조건: {rule.operator}\n"
            f"시간: {datetime.now().isoformat()}"
        )

        logger.warning(alert_message)
        print(f"\n{alert_message}\n")

    def _send_alert_resolved(self, rule: AlertRule, current_value: float):
        """알림 해결 메시지 전송"""
        resolved_message = (
            f"✅ 알림 해결: {rule.name}\n"
            f"메트릭: {rule.metric_name}\n"
            f"현재값: {current_value:.2f}\n"
            f"시간: {datetime.now().isoformat()}"
        )

        logger.info(resolved_message)
        print(f"\n{resolved_message}\n")

    async def _monitor_loop(self):
        """모니터링 루프"""
        logger.info("성능 모니터링 시작")
        last_system_metrics = 0
        last_app_metrics = 0

        while self.is_monitoring:
            try:
                current_time = time.time()

                # 시스템 메트릭 수집
                if current_time - last_system_metrics >= self.system_metrics_interval:
                    self._collect_system_metrics()
                    last_system_metrics = current_time

                # 애플리케이션 메트릭 수집 (기본적인 것들)
                if current_time - last_app_metrics >= self.application_metrics_interval:
                    # 활성 스레드 수
                    self.add_metric("application.active_threads", threading.active_count(), "count")

                    # 이벤트 루프 상태
                    try:
                        loop = asyncio.get_running_loop()
                        self.add_metric("application.event_loop_running", 1, "boolean")
                    except:
                        self.add_metric("application.event_loop_running", 0, "boolean")

                    last_app_metrics = current_time

                await asyncio.sleep(5)  # 5초마다 체크

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                await asyncio.sleep(30)

    async def _alert_check_loop(self):
        """알림 확인 루프"""
        while self.is_monitoring:
            try:
                self._check_alerts()
                await asyncio.sleep(30)  # 30초마다 알림 확인
            except Exception as e:
                logger.error(f"알림 확인 루프 오류: {e}")
                await asyncio.sleep(60)

    async def start(self):
        """모니터링 시작"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            self._alert_check_task = asyncio.create_task(self._alert_check_loop())
            logger.info("성능 모니터링 서비스 시작됨")

    async def stop(self):
        """모니터링 중지"""
        if self.is_monitoring:
            self.is_monitoring = False

            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            if self._alert_check_task:
                self._alert_check_task.cancel()
                try:
                    await self._alert_check_task
                except asyncio.CancelledError:
                    pass

            logger.info("성능 모니터링 서비스 중지됨")

    def get_metrics_summary(self, metric_name: str, hours: int = 1) -> Dict[str, Any]:
        """메트릭 요약 정보 반환"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics[metric_name]
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return {"error": "데이터 없음"}

        values = [m.value for m in recent_metrics]

        return {
            "metric_name": metric_name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "time_range": f"{hours}시간",
            "unit": recent_metrics[0].unit if recent_metrics else ""
        }

    def get_system_health(self) -> Dict[str, Any]:
        """시스템 상태 요약"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "active_alerts": len(self.active_alerts),
                "monitoring_status": "active" if self.is_monitoring else "inactive"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """모든 메트릭 반환"""
        result = {}
        for metric_name, metrics in self.metrics.items():
            result[metric_name] = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "value": m.value,
                    "unit": m.unit,
                    "tags": m.tags
                }
                for m in metrics
            ]
        return result

# 전역 모니터 인스턴스
performance_monitor = PerformanceMonitor()

# 데코레이터
def monitor_performance(metric_name: str, unit: str = ""):
    """함수 성능 모니터링 데코레이터"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.add_metric(
                    f"{metric_name}.execution_time",
                    execution_time,
                    "seconds"
                )
                performance_monitor.add_metric(
                    f"{metric_name}.success_count",
                    1,
                    "count"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.add_metric(
                    f"{metric_name}.execution_time",
                    execution_time,
                    "seconds"
                )
                performance_monitor.add_metric(
                    f"{metric_name}.error_count",
                    1,
                    "count"
                )
                raise
        return wrapper
    return decorator
