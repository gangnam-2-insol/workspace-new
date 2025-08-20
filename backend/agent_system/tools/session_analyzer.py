"""
세션 분석기

사용자의 행동 로그를 기록하고, 백엔드 연동 결과와 매칭하여 분석합니다.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from .behavior_analyzer import UserAction, ToolMapping, behavior_analyzer

logger = logging.getLogger(__name__)

@dataclass
class UserBehaviorLog:
    """사용자 행동 로그"""
    log_id: str
    session_id: str
    user_id: str
    action: UserAction
    timestamp: str
    page_context: Dict[str, Any]  # 페이지 컨텍스트 (URL, 요소 등)
    browser_info: Dict[str, Any]  # 브라우저 정보

@dataclass
class BackendExecutionLog:
    """백엔드 실행 로그"""
    execution_id: str
    session_id: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float
    timestamp: str
    success: bool

@dataclass
class SessionAnalysis:
    """세션 분석 결과"""
    session_id: str
    user_id: str
    start_time: str
    end_time: str
    total_actions: int
    total_executions: int
    matched_pairs: List[Tuple[UserBehaviorLog, BackendExecutionLog]]
    accuracy_score: float
    tool_mapping_accuracy: Dict[str, float]
    suggestions: List[str]

class SessionAnalyzer:
    """세션 분석기"""
    
    def __init__(self):
        self.user_behavior_logs: List[UserBehaviorLog] = []
        self.backend_execution_logs: List[BackendExecutionLog] = []
        self.session_analyses: Dict[str, SessionAnalysis] = {}
    
    def log_user_behavior(self, session_id: str, user_id: str, action: UserAction, 
                         page_context: Dict[str, Any] = None, browser_info: Dict[str, Any] = None) -> str:
        """사용자 행동 로그 기록"""
        log_id = f"behavior_{session_id}_{int(time.time() * 1000)}"
        
        log = UserBehaviorLog(
            log_id=log_id,
            session_id=session_id,
            user_id=user_id,
            action=action,
            timestamp=datetime.now().isoformat(),
            page_context=page_context or {},
            browser_info=browser_info or {}
        )
        
        self.user_behavior_logs.append(log)
        logger.info(f"사용자 행동 로그 기록: {log_id} - {action.content}")
        
        return log_id
    
    def log_backend_execution(self, session_id: str, tool_name: str, parameters: Dict[str, Any],
                            result: Dict[str, Any], execution_time: float, success: bool = True) -> str:
        """백엔드 실행 로그 기록"""
        execution_id = f"execution_{session_id}_{int(time.time() * 1000)}"
        
        log = BackendExecutionLog(
            execution_id=execution_id,
            session_id=session_id,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            success=success
        )
        
        self.backend_execution_logs.append(log)
        logger.info(f"백엔드 실행 로그 기록: {execution_id} - {tool_name}")
        
        return execution_id
    
    def analyze_session(self, session_id: str) -> SessionAnalysis:
        """세션 분석"""
        # 해당 세션의 사용자 행동 로그 수집
        user_logs = [log for log in self.user_behavior_logs if log.session_id == session_id]
        backend_logs = [log for log in self.backend_execution_logs if log.session_id == session_id]
        
        if not user_logs and not backend_logs:
            raise ValueError(f"세션 {session_id}에 대한 로그가 없습니다.")
        
        # 시간순으로 정렬
        user_logs.sort(key=lambda x: x.timestamp)
        backend_logs.sort(key=lambda x: x.timestamp)
        
        # 매칭 분석
        matched_pairs = self._match_behavior_with_execution(user_logs, backend_logs)
        
        # 정확도 계산
        accuracy_score = self._calculate_accuracy_score(user_logs, backend_logs, matched_pairs)
        
        # 툴별 매핑 정확도
        tool_mapping_accuracy = self._calculate_tool_mapping_accuracy(user_logs, matched_pairs)
        
        # 개선 제안
        suggestions = self._generate_suggestions(user_logs, backend_logs, matched_pairs, accuracy_score)
        
        analysis = SessionAnalysis(
            session_id=session_id,
            user_id=user_logs[0].user_id if user_logs else "unknown",
            start_time=user_logs[0].timestamp if user_logs else backend_logs[0].timestamp,
            end_time=user_logs[-1].timestamp if user_logs else backend_logs[-1].timestamp,
            total_actions=len(user_logs),
            total_executions=len(backend_logs),
            matched_pairs=matched_pairs,
            accuracy_score=accuracy_score,
            tool_mapping_accuracy=tool_mapping_accuracy,
            suggestions=suggestions
        )
        
        self.session_analyses[session_id] = analysis
        logger.info(f"세션 분석 완료: {session_id} (정확도: {accuracy_score:.1%})")
        
        return analysis
    
    def _match_behavior_with_execution(self, user_logs: List[UserBehaviorLog], 
                                     backend_logs: List[BackendExecutionLog]) -> List[Tuple[UserBehaviorLog, BackendExecutionLog]]:
        """사용자 행동과 백엔드 실행을 매칭"""
        matched_pairs = []
        
        for user_log in user_logs:
            # 사용자 행동을 툴로 매핑
            tool_mappings = behavior_analyzer.analyze_user_action(user_log.action)
            
            if not tool_mappings:
                continue
            
            best_mapping = tool_mappings[0]
            
            # 시간적으로 가까운 백엔드 실행 찾기
            best_match = None
            min_time_diff = float('inf')
            
            for backend_log in backend_logs:
                # 이미 매칭된 백엔드 로그는 제외
                if any(backend_log.execution_id == pair[1].execution_id for pair in matched_pairs):
                    continue
                
                # 툴 이름이 일치하는지 확인
                if backend_log.tool_name == best_mapping.tool_name:
                    # 시간 차이 계산
                    user_time = datetime.fromisoformat(user_log.timestamp)
                    backend_time = datetime.fromisoformat(backend_log.timestamp)
                    time_diff = abs((user_time - backend_time).total_seconds())
                    
                    # 30초 이내의 실행만 고려
                    if time_diff <= 30 and time_diff < min_time_diff:
                        min_time_diff = time_diff
                        best_match = backend_log
            
            if best_match:
                matched_pairs.append((user_log, best_match))
        
        return matched_pairs
    
    def _calculate_accuracy_score(self, user_logs: List[UserBehaviorLog], 
                                backend_logs: List[BackendExecutionLog],
                                matched_pairs: List[Tuple[UserBehaviorLog, BackendExecutionLog]]) -> float:
        """정확도 점수 계산"""
        if not user_logs or not backend_logs:
            return 0.0
        
        # 매칭된 쌍의 비율
        match_ratio = len(matched_pairs) / min(len(user_logs), len(backend_logs))
        
        # 매칭된 쌍의 신뢰도 평균
        confidence_sum = 0.0
        confidence_count = 0
        
        for user_log, backend_log in matched_pairs:
            tool_mappings = behavior_analyzer.analyze_user_action(user_log.action)
            if tool_mappings:
                confidence_sum += tool_mappings[0].confidence
                confidence_count += 1
        
        avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0.0
        
        # 최종 정확도 = 매칭 비율 * 평균 신뢰도
        accuracy = match_ratio * avg_confidence
        
        return accuracy
    
    def _calculate_tool_mapping_accuracy(self, user_logs: List[UserBehaviorLog],
                                       matched_pairs: List[Tuple[UserBehaviorLog, BackendExecutionLog]]) -> Dict[str, float]:
        """툴별 매핑 정확도 계산"""
        tool_accuracies = {}
        
        for user_log, backend_log in matched_pairs:
            tool_name = backend_log.tool_name
            
            if tool_name not in tool_accuracies:
                tool_accuracies[tool_name] = {
                    "total": 0,
                    "correct": 0,
                    "confidence_sum": 0.0
                }
            
            tool_accuracies[tool_name]["total"] += 1
            
            # 사용자 행동을 다시 분석하여 정확도 확인
            tool_mappings = behavior_analyzer.analyze_user_action(user_log.action)
            if tool_mappings and tool_mappings[0].tool_name == tool_name:
                tool_accuracies[tool_name]["correct"] += 1
                tool_accuracies[tool_name]["confidence_sum"] += tool_mappings[0].confidence
        
        # 정확도 계산
        result = {}
        for tool_name, stats in tool_accuracies.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
            avg_confidence = stats["confidence_sum"] / stats["total"] if stats["total"] > 0 else 0.0
            result[tool_name] = accuracy * avg_confidence
        
        return result
    
    def _generate_suggestions(self, user_logs: List[UserBehaviorLog],
                            backend_logs: List[BackendExecutionLog],
                            matched_pairs: List[Tuple[UserBehaviorLog, BackendExecutionLog]],
                            accuracy_score: float) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 전체 정확도 기반 제안
        if accuracy_score < 0.7:
            suggestions.append("전체 매핑 정확도가 낮습니다. 사용자 행동 패턴 분석을 개선하세요.")
        
        # 매칭되지 않은 행동들 분석
        unmatched_actions = []
        for user_log in user_logs:
            if not any(user_log.log_id == pair[0].log_id for pair in matched_pairs):
                unmatched_actions.append(user_log)
        
        if unmatched_actions:
            suggestions.append(f"{len(unmatched_actions)}개의 사용자 행동이 백엔드 실행과 매칭되지 않았습니다.")
        
        # 매칭되지 않은 백엔드 실행들 분석
        unmatched_executions = []
        for backend_log in backend_logs:
            if not any(backend_log.execution_id == pair[1].execution_id for pair in matched_pairs):
                unmatched_executions.append(backend_log)
        
        if unmatched_executions:
            suggestions.append(f"{len(unmatched_executions)}개의 백엔드 실행이 사용자 행동과 매칭되지 않았습니다.")
        
        # 툴별 개선 제안
        tool_mapping_accuracy = self._calculate_tool_mapping_accuracy(user_logs, matched_pairs)
        for tool_name, accuracy in tool_mapping_accuracy.items():
            if accuracy < 0.6:
                suggestions.append(f"{tool_name} 툴의 매핑 정확도가 낮습니다. 패턴 매칭 규칙을 개선하세요.")
        
        return suggestions
    
    def export_session_analysis(self, session_id: str, filename: str = None) -> str:
        """세션 분석 결과 내보내기"""
        if session_id not in self.session_analyses:
            self.analyze_session(session_id)
        
        analysis = self.session_analyses[session_id]
        
        # 내보낼 데이터 구성
        export_data = {
            "session_info": {
                "session_id": analysis.session_id,
                "user_id": analysis.user_id,
                "start_time": analysis.start_time,
                "end_time": analysis.end_time,
                "total_actions": analysis.total_actions,
                "total_executions": analysis.total_executions,
                "accuracy_score": analysis.accuracy_score
            },
            "matched_pairs": [
                {
                    "user_behavior": {
                        "log_id": pair[0].log_id,
                        "action": asdict(pair[0].action),
                        "timestamp": pair[0].timestamp,
                        "page_context": pair[0].page_context
                    },
                    "backend_execution": {
                        "execution_id": pair[1].execution_id,
                        "tool_name": pair[1].tool_name,
                        "parameters": pair[1].parameters,
                        "result": pair[1].result,
                        "execution_time": pair[1].execution_time,
                        "timestamp": pair[1].timestamp,
                        "success": pair[1].success
                    }
                }
                for pair in analysis.matched_pairs
            ],
            "tool_mapping_accuracy": analysis.tool_mapping_accuracy,
            "suggestions": analysis.suggestions
        }
        
        # 파일로 저장
        if filename is None:
            filename = f"session_analysis_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"세션 분석 결과 내보내기: {filename}")
        return filename
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """세션 요약 정보"""
        if session_id not in self.session_analyses:
            self.analyze_session(session_id)
        
        analysis = self.session_analyses[session_id]
        
        return {
            "session_id": session_id,
            "accuracy_score": analysis.accuracy_score,
            "total_actions": analysis.total_actions,
            "total_executions": analysis.total_executions,
            "matched_count": len(analysis.matched_pairs),
            "tool_accuracies": analysis.tool_mapping_accuracy,
            "suggestions": analysis.suggestions[:3]  # 상위 3개 제안만
        }

# 전역 세션 분석기 인스턴스
session_analyzer = SessionAnalyzer()
