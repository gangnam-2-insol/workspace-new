"""
Base Tool Class

모든 백엔드 툴의 기본 클래스
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """모든 백엔드 툴의 기본 클래스"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """툴 실행 메서드 (하위 클래스에서 구현)"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """파라미터 검증"""
        return True
    
    def create_response(self, success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
        """표준 응답 생성"""
        if success:
            return {
                "status": "success",
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "tool": self.name
            }
        else:
            return {
                "status": "error",
                "message": error,
                "timestamp": datetime.now().isoformat(),
                "tool": self.name
            }
    
    def log_execution(self, parameters: Dict[str, Any], result: Dict[str, Any]):
        """실행 로그 기록"""
        self.logger.info(f"Tool execution: {self.name}")
        self.logger.debug(f"Parameters: {parameters}")
        self.logger.debug(f"Result: {result}")
    
    def __str__(self):
        return f"{self.name}: {self.description}"

