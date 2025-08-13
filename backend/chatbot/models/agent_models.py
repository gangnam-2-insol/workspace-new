"""
Agent 관련 모델들
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class AgentOutput:
    """Agent 시스템의 출력 데이터"""
    success: bool
    response: str
    intent: str
    confidence: float = 0.0
    extracted_fields: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@dataclass
class AgentRequest:
    """Agent 시스템의 요청 데이터"""
    user_input: str
    conversation_history: List[Dict[str, Any]]
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

