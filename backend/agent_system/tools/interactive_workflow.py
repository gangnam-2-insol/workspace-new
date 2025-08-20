"""
인터랙티브 워크플로우 시스템

에이전트가 사용자에게 작업을 요청하고, 사용자가 수행한 과정을 로그로 기록하여 분석합니다.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .behavior_analyzer import UserAction, ToolMapping, behavior_analyzer

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """워크플로우 단계"""
    step_id: str
    agent_request: str  # 에이전트가 요청한 작업
    user_action: Optional[UserAction] = None  # 사용자가 수행한 행동
    tool_mapping: Optional[ToolMapping] = None  # 매핑된 툴
    execution_result: Optional[Dict[str, Any]] = None  # 실행 결과
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class WorkflowSession:
    """워크플로우 세션"""
    session_id: str
    user_id: str
    workflow_type: str  # "github_analysis", "mongodb_query", "search_task" 등
    steps: List[WorkflowStep]
    created_at: str
    completed_at: Optional[str] = None
    success: bool = False

class InteractiveWorkflowManager:
    """인터랙티브 워크플로우 관리자"""
    
    def __init__(self):
        self.active_sessions: Dict[str, WorkflowSession] = {}
        self.completed_sessions: List[WorkflowSession] = []
        self.workflow_templates = self._create_workflow_templates()
    
    def _create_workflow_templates(self) -> Dict[str, List[str]]:
        """워크플로우 템플릿 정의"""
        return {
            "github_analysis": [
                "GitHub 사용자 정보를 조회해주세요. 사용자명을 입력하시면 됩니다.",
                "해당 사용자의 레포지토리 목록을 확인해주세요.",
                "특정 레포지토리의 커밋 내역을 조회해주세요.",
                "레포지토리 검색을 수행해주세요. 검색어를 입력하시면 됩니다."
            ],
            "mongodb_query": [
                "MongoDB에서 사용자 컬렉션을 조회해주세요.",
                "특정 조건으로 문서를 검색해주세요.",
                "컬렉션의 전체 문서 개수를 세어주세요.",
                "새로운 문서를 추가해주세요."
            ],
            "search_task": [
                "웹에서 특정 정보를 검색해주세요.",
                "뉴스 검색을 수행해주세요.",
                "이미지 검색을 수행해주세요.",
                "검색 결과를 정리해주세요."
            ]
        }
    
    def start_workflow(self, user_id: str, workflow_type: str) -> WorkflowSession:
        """워크플로우 시작"""
        session_id = f"{workflow_type}_{user_id}_{int(time.time())}"
        
        session = WorkflowSession(
            session_id=session_id,
            user_id=user_id,
            workflow_type=workflow_type,
            steps=[],
            created_at=datetime.now().isoformat()
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"워크플로우 시작: {session_id} ({workflow_type})")
        
        return session
    
    def add_agent_request(self, session_id: str, request: str) -> WorkflowStep:
        """에이전트 요청 추가"""
        if session_id not in self.active_sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        session = self.active_sessions[session_id]
        step_id = f"step_{len(session.steps) + 1}"
        
        step = WorkflowStep(
            step_id=step_id,
            agent_request=request
        )
        
        session.steps.append(step)
        logger.info(f"에이전트 요청 추가: {session_id} - {request}")
        
        return step
    
    def record_user_action(self, session_id: str, step_id: str, action: UserAction) -> WorkflowStep:
        """사용자 행동 기록"""
        if session_id not in self.active_sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        session = self.active_sessions[session_id]
        step = self._find_step(session, step_id)
        
        if not step:
            raise ValueError(f"단계를 찾을 수 없습니다: {step_id}")
        
        # 사용자 행동 분석
        tool_mappings = behavior_analyzer.analyze_user_action(action)
        best_mapping = tool_mappings[0] if tool_mappings else None
        
        step.user_action = action
        step.tool_mapping = best_mapping
        
        logger.info(f"사용자 행동 기록: {session_id} - {action.content}")
        if best_mapping:
            logger.info(f"툴 매핑: {best_mapping.tool_name} (신뢰도: {best_mapping.confidence:.1%})")
        
        return step
    
    def record_execution_result(self, session_id: str, step_id: str, result: Dict[str, Any]) -> WorkflowStep:
        """실행 결과 기록"""
        if session_id not in self.active_sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        session = self.active_sessions[session_id]
        step = self._find_step(session, step_id)
        
        if not step:
            raise ValueError(f"단계를 찾을 수 없습니다: {step_id}")
        
        step.execution_result = result
        logger.info(f"실행 결과 기록: {session_id} - {result.get('status', 'unknown')}")
        
        return step
    
    def complete_workflow(self, session_id: str, success: bool = True) -> WorkflowSession:
        """워크플로우 완료"""
        if session_id not in self.active_sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        session = self.active_sessions[session_id]
        session.completed_at = datetime.now().isoformat()
        session.success = success
        
        # 완료된 세션을 이동
        self.completed_sessions.append(session)
        del self.active_sessions[session_id]
        
        logger.info(f"워크플로우 완료: {session_id} (성공: {success})")
        
        return session
    
    def _find_step(self, session: WorkflowSession, step_id: str) -> Optional[WorkflowStep]:
        """단계 찾기"""
        for step in session.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def analyze_workflow_accuracy(self, session_id: str) -> Dict[str, Any]:
        """워크플로우 정확도 분석"""
        session = None
        
        # 활성 세션에서 찾기
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        
        # 완료된 세션에서 찾기
        if not session:
            for completed_session in self.completed_sessions:
                if completed_session.session_id == session_id:
                    session = completed_session
                    break
        
        if not session:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        analysis = {
            "session_id": session_id,
            "workflow_type": session.workflow_type,
            "total_steps": len(session.steps),
            "completed_steps": 0,
            "successful_mappings": 0,
            "tool_accuracy": {},
            "overall_accuracy": 0.0
        }
        
        # 각 단계별 분석
        for step in session.steps:
            if step.user_action and step.tool_mapping:
                analysis["completed_steps"] += 1
                
                # 툴별 정확도 집계
                tool_name = step.tool_mapping.tool_name
                if tool_name not in analysis["tool_accuracy"]:
                    analysis["tool_accuracy"][tool_name] = {
                        "count": 0,
                        "total_confidence": 0.0,
                        "avg_confidence": 0.0
                    }
                
                tool_stats = analysis["tool_accuracy"][tool_name]
                tool_stats["count"] += 1
                tool_stats["total_confidence"] += step.tool_mapping.confidence
                tool_stats["avg_confidence"] = tool_stats["total_confidence"] / tool_stats["count"]
                
                # 성공적인 매핑으로 간주 (신뢰도 0.5 이상)
                if step.tool_mapping.confidence >= 0.5:
                    analysis["successful_mappings"] += 1
        
        # 전체 정확도 계산
        if analysis["completed_steps"] > 0:
            analysis["overall_accuracy"] = analysis["successful_mappings"] / analysis["completed_steps"]
        
        return analysis
    
    def get_workflow_suggestions(self, session_id: str) -> List[str]:
        """워크플로우 개선 제안"""
        analysis = self.analyze_workflow_accuracy(session_id)
        suggestions = []
        
        if analysis["overall_accuracy"] < 0.7:
            suggestions.append("전체 매핑 정확도가 낮습니다. 사용자 행동 패턴을 더 정확히 분석해야 합니다.")
        
        # 툴별 개선 제안
        for tool_name, stats in analysis["tool_accuracy"].items():
            if stats["avg_confidence"] < 0.6:
                suggestions.append(f"{tool_name} 툴의 매핑 정확도가 낮습니다. 패턴 매칭 규칙을 개선하세요.")
        
        if analysis["completed_steps"] < 3:
            suggestions.append("더 많은 단계를 수행하여 정확한 분석을 위해 충분한 데이터를 수집하세요.")
        
        return suggestions
    
    def export_workflow_log(self, session_id: str, filename: str = None) -> str:
        """워크플로우 로그 내보내기"""
        session = None
        
        # 활성 세션에서 찾기
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        
        # 완료된 세션에서 찾기
        if not session:
            for completed_session in self.completed_sessions:
                if completed_session.session_id == session_id:
                    session = completed_session
                    break
        
        if not session:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        # 로그 데이터 구성
        log_data = {
            "session_info": {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "workflow_type": session.workflow_type,
                "created_at": session.created_at,
                "completed_at": session.completed_at,
                "success": session.success
            },
            "steps": [
                {
                    "step_id": step.step_id,
                    "agent_request": step.agent_request,
                    "user_action": asdict(step.user_action) if step.user_action else None,
                    "tool_mapping": asdict(step.tool_mapping) if step.tool_mapping else None,
                    "execution_result": step.execution_result,
                    "timestamp": step.timestamp
                }
                for step in session.steps
            ],
            "analysis": self.analyze_workflow_accuracy(session_id),
            "suggestions": self.get_workflow_suggestions(session_id)
        }
        
        # 파일로 저장
        if filename is None:
            filename = f"workflow_log_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"워크플로우 로그 내보내기: {filename}")
        return filename

# 전역 워크플로우 관리자 인스턴스
workflow_manager = InteractiveWorkflowManager()
