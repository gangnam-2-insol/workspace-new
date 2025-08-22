"""
모니터링 및 로깅 시스템

챗봇 운영 상태를 실시간으로 모니터링하고 로깅하는 모듈입니다.
"""

import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from threading import Lock
import smtplib

# 이메일 관련 모듈 선택적 import
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    MIMEText = None
    MIMEMultipart = None

logger = logging.getLogger(__name__)

@dataclass
class ToolExecutionLog:
    """툴 실행 로그 데이터 클래스"""
    timestamp: str
    session_id: str
    user_id: Optional[str]
    tool: str
    action: str
    status: str
    duration_ms: int
    error_message: Optional[str]
    parameters: Dict[str, Any]
    response_size: Optional[int]
    cache_hit: bool = False
    retry_count: int = 0

@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터 클래스"""
    tool: str
    action: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration_ms: float
    max_duration_ms: int
    min_duration_ms: int
    error_rate: float
    cache_hit_rate: float

class MonitoringSystem:
    """통합 모니터링 시스템"""
    
    def __init__(self, log_file: str = "logs/tool_executions.log", max_logs: int = 10000):
        """
        모니터링 시스템 초기화
        
        Args:
            log_file: 로그 파일 경로
            max_logs: 최대 로그 보관 수
        """
        self.log_file = log_file
        self.max_logs = max_logs
        
        # 로그 디렉토리 생성
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 로깅 설정
        self._setup_logging()
        
        # 메트릭 저장소
        self.metrics = defaultdict(lambda: {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "durations": deque(maxlen=1000),  # 최근 1000개 실행 시간
            "cache_hits": 0,
            "retry_counts": deque(maxlen=1000)
        })
        
        # 알림 설정
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% 이상 에러율
            "avg_duration_ms": 5000,  # 5초 이상 평균 실행 시간
            "max_duration_ms": 30000  # 30초 이상 최대 실행 시간
        }
        
        # 스레드 안전을 위한 락
        self.lock = Lock()
        
        # 알림 기록 (중복 알림 방지)
        self.alert_history = defaultdict(lambda: deque(maxlen=10))
        
        logger.info("MonitoringSystem initialized")
    
    def _setup_logging(self):
        """로깅 설정"""
        # 파일 핸들러
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 로거에 핸들러 추가
        monitoring_logger = logging.getLogger('monitoring')
        monitoring_logger.addHandler(file_handler)
        monitoring_logger.setLevel(logging.INFO)
        
        self.monitoring_logger = monitoring_logger
    
    def log_tool_execution(self, log_data: ToolExecutionLog):
        """
        툴 실행 로그 기록
        
        Args:
            log_data: 툴 실행 로그 데이터
        """
        with self.lock:
            # 로그 파일에 기록
            log_entry = asdict(log_data)
            self.monitoring_logger.info(json.dumps(log_entry, ensure_ascii=False))
            
            # 메트릭 업데이트
            key = f"{log_data.tool}.{log_data.action}"
            metrics = self.metrics[key]
            
            metrics["total_executions"] += 1
            metrics["durations"].append(log_data.duration_ms)
            
            if log_data.status == "success":
                metrics["successful_executions"] += 1
            else:
                metrics["failed_executions"] += 1
            
            if log_data.cache_hit:
                metrics["cache_hits"] += 1
            
            metrics["retry_counts"].append(log_data.retry_count)
            
            # 알림 체크
            self._check_alerts(key, log_data)
    
    def _check_alerts(self, tool_action: str, log_data: ToolExecutionLog):
        """
        알림 조건 체크
        
        Args:
            tool_action: 툴.액션 키
            log_data: 로그 데이터
        """
        metrics = self.metrics[tool_action]
        
        if metrics["total_executions"] < 10:  # 최소 10번 실행 후 알림
            return
        
        # 에러율 체크
        error_rate = metrics["failed_executions"] / metrics["total_executions"]
        if error_rate > self.alert_thresholds["error_rate"]:
            self._send_alert(
                "high_error_rate",
                f"높은 에러율 감지: {tool_action} - {error_rate:.2%}",
                {"tool_action": tool_action, "error_rate": error_rate}
            )
        
        # 평균 실행 시간 체크
        if metrics["durations"]:
            avg_duration = sum(metrics["durations"]) / len(metrics["durations"])
            if avg_duration > self.alert_thresholds["avg_duration_ms"]:
                self._send_alert(
                    "slow_execution",
                    f"느린 실행 감지: {tool_action} - 평균 {avg_duration:.0f}ms",
                    {"tool_action": tool_action, "avg_duration": avg_duration}
                )
        
        # 개별 실행 시간 체크
        if log_data.duration_ms > self.alert_thresholds["max_duration_ms"]:
            self._send_alert(
                "very_slow_execution",
                f"매우 느린 실행 감지: {tool_action} - {log_data.duration_ms}ms",
                {"tool_action": tool_action, "duration": log_data.duration_ms}
            )
    
    def _send_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """
        알림 전송
        
        Args:
            alert_type: 알림 유형
            message: 알림 메시지
            data: 알림 데이터
        """
        # 중복 알림 방지 (5분 내 같은 알림은 무시)
        now = datetime.now()
        alert_key = f"{alert_type}_{data.get('tool_action', 'unknown')}"
        
        if alert_key in self.alert_history:
            last_alert = self.alert_history[alert_key][-1]
            if (now - last_alert).total_seconds() < 300:  # 5분
                return
        
        self.alert_history[alert_key].append(now)
        
        # 로그에 알림 기록
        alert_log = {
            "timestamp": now.isoformat(),
            "alert_type": alert_type,
            "message": message,
            "data": data
        }
        
        self.monitoring_logger.warning(f"ALERT: {json.dumps(alert_log, ensure_ascii=False)}")
        
        # 실제 알림 전송 (이메일, Slack 등)
        self._send_notification(alert_type, message, data)
    
    def _send_notification(self, alert_type: str, message: str, data: Dict[str, Any]):
        """
        실제 알림 전송 (이메일, Slack 등)
        
        Args:
            alert_type: 알림 유형
            message: 알림 메시지
            data: 알림 데이터
        """
        # 이메일 알림 (환경변수 설정 필요)
        email_enabled = os.getenv("MONITORING_EMAIL_ENABLED", "false").lower() == "true"
        if email_enabled:
            self._send_email_alert(alert_type, message, data)
        
        # Slack 알림 (환경변수 설정 필요)
        slack_enabled = os.getenv("MONITORING_SLACK_ENABLED", "false").lower() == "true"
        if slack_enabled:
            self._send_slack_alert(alert_type, message, data)
    
    def _send_email_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """이메일 알림 전송"""
        if not EMAIL_AVAILABLE:
            logger.warning("Email functionality not available")
            return
            
        try:
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            alert_email = os.getenv("ALERT_EMAIL")
            
            if not all([smtp_username, smtp_password, alert_email]):
                logger.warning("Email alert configuration incomplete")
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = alert_email
            msg['Subject'] = f"챗봇 알림: {alert_type}"
            
            body = f"""
            챗봇 모니터링 알림
            
            유형: {alert_type}
            메시지: {message}
            시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            데이터: {json.dumps(data, ensure_ascii=False, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert_type}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_slack_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Slack 알림 전송"""
        try:
            import requests
            
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return
            
            payload = {
                "text": f"🚨 챗봇 알림\n\n**유형**: {alert_type}\n**메시지**: {message}\n**시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "attachments": [
                    {
                        "fields": [
                            {"title": "데이터", "value": json.dumps(data, ensure_ascii=False, indent=2), "short": False}
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent: {alert_type}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
    
    def get_performance_metrics(self, tool_action: str = None) -> Dict[str, Any]:
        """
        성능 메트릭 조회
        
        Args:
            tool_action: 특정 툴.액션 (None이면 전체)
            
        Returns:
            성능 메트릭
        """
        with self.lock:
            if tool_action:
                return self._calculate_metrics(tool_action)
            else:
                return {
                    action: self._calculate_metrics(action)
                    for action in self.metrics.keys()
                }
    
    def _calculate_metrics(self, tool_action: str) -> Dict[str, Any]:
        """특정 툴.액션의 메트릭 계산"""
        metrics = self.metrics[tool_action]
        
        if not metrics["durations"]:
            return {
                "tool_action": tool_action,
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_duration_ms": 0,
                "max_duration_ms": 0,
                "min_duration_ms": 0,
                "error_rate": 0,
                "cache_hit_rate": 0
            }
        
        durations = list(metrics["durations"])
        avg_duration = sum(durations) / len(durations)
        error_rate = metrics["failed_executions"] / metrics["total_executions"]
        cache_hit_rate = metrics["cache_hits"] / metrics["total_executions"]
        
        return {
            "tool_action": tool_action,
            "total_executions": metrics["total_executions"],
            "successful_executions": metrics["successful_executions"],
            "failed_executions": metrics["failed_executions"],
            "average_duration_ms": round(avg_duration, 2),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "error_rate": round(error_rate, 4),
            "cache_hit_rate": round(cache_hit_rate, 4)
        }
    
    def get_usage_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        사용량 통계 조회
        
        Args:
            days: 조회 기간 (일)
            
        Returns:
            사용량 통계
        """
        with self.lock:
            # 실제 구현에서는 로그 파일에서 통계 계산
            # 여기서는 메모리 데이터 기반으로 계산
            
            total_executions = sum(m["total_executions"] for m in self.metrics.values())
            total_successful = sum(m["successful_executions"] for m in self.metrics.values())
            total_failed = sum(m["failed_executions"] for m in self.metrics.values())
            
            # 인기 툴 순위
            tool_usage = {}
            for tool_action, metrics in self.metrics.items():
                tool = tool_action.split('.')[0]
                tool_usage[tool] = tool_usage.get(tool, 0) + metrics["total_executions"]
            
            popular_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "period_days": days,
                "total_executions": total_executions,
                "successful_executions": total_successful,
                "failed_executions": total_failed,
                "success_rate": round(total_successful / total_executions, 4) if total_executions > 0 else 0,
                "popular_tools": popular_tools[:5],  # 상위 5개
                "unique_tool_actions": len(self.metrics)
            }
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        최근 로그 조회
        
        Args:
            limit: 조회할 로그 수
            
        Returns:
            최근 로그 목록
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-limit:] if len(lines) > limit else lines
                
                logs = []
                for line in recent_lines:
                    try:
                        # 로그 라인에서 JSON 부분 추출
                        json_start = line.find('{')
                        if json_start != -1:
                            json_str = line[json_start:]
                            log_data = json.loads(json_str)
                            logs.append(log_data)
                    except json.JSONDecodeError:
                        continue
                
                return logs
        except FileNotFoundError:
            return []
    
    def clear_metrics(self):
        """메트릭 초기화"""
        with self.lock:
            self.metrics.clear()
            self.alert_history.clear()
            logger.info("All metrics cleared")

# 전역 모니터링 시스템 인스턴스
monitoring_system = MonitoringSystem()

def log_tool_execution(
    session_id: str,
    tool: str,
    action: str,
    status: str,
    duration_ms: int,
    error_message: str = None,
    parameters: Dict[str, Any] = None,
    response_size: int = None,
    cache_hit: bool = False,
    retry_count: int = 0,
    user_id: str = None
):
    """
    툴 실행 로그 기록 헬퍼 함수
    
    Args:
        session_id: 세션 ID
        tool: 툴 이름
        action: 액션 이름
        status: 실행 상태
        duration_ms: 실행 시간 (밀리초)
        error_message: 에러 메시지
        parameters: 실행 매개변수
        response_size: 응답 크기
        cache_hit: 캐시 히트 여부
        retry_count: 재시도 횟수
        user_id: 사용자 ID
    """
    log_data = ToolExecutionLog(
        timestamp=datetime.now().isoformat(),
        session_id=session_id,
        user_id=user_id,
        tool=tool,
        action=action,
        status=status,
        duration_ms=duration_ms,
        error_message=error_message,
        parameters=parameters or {},
        response_size=response_size,
        cache_hit=cache_hit,
        retry_count=retry_count
    )
    
    monitoring_system.log_tool_execution(log_data)

def monitor_tool_execution(func):
    """
    툴 실행 모니터링 데코레이터
    
    Args:
        func: 모니터링할 함수
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        session_id = kwargs.get('session_id', 'unknown')
        tool_name = getattr(args[0], '__class__.__name__', 'UnknownTool')
        
        try:
            result = func(*args, **kwargs)
            status = result.get('status', 'unknown')
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 로그 기록
            log_tool_execution(
                session_id=session_id,
                tool=tool_name,
                action=kwargs.get('action', 'unknown'),
                status=status,
                duration_ms=duration_ms,
                parameters=kwargs,
                response_size=len(str(result)) if result else 0,
                cache_hit=result.get('cached', False),
                retry_count=result.get('retry_count', 0)
            )
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 에러 로그 기록
            log_tool_execution(
                session_id=session_id,
                tool=tool_name,
                action=kwargs.get('action', 'unknown'),
                status='error',
                duration_ms=duration_ms,
                error_message=str(e),
                parameters=kwargs
            )
            
            raise
    
    return wrapper
