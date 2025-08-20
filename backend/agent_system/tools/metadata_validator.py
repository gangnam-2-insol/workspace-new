"""
메타데이터 정확성 검증 및 튜닝 도구

실제 툴 사용 시연과 로그 분석을 통해 메타데이터의 정확성을 검증하고 개선합니다.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ToolUsageLog:
    """툴 사용 로그"""
    timestamp: str
    tool_name: str
    user_input: str
    parameters: Dict[str, Any]
    actual_result: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    llm_confidence: Optional[float] = None

@dataclass
class MetadataAccuracyReport:
    """메타데이터 정확성 리포트"""
    tool_name: str
    total_usage: int
    success_rate: float
    common_errors: List[str]
    parameter_accuracy: Dict[str, float]
    description_accuracy: float
    suggested_improvements: List[str]

class MetadataValidator:
    """메타데이터 검증 및 튜닝 도구"""
    
    def __init__(self):
        self.usage_logs: List[ToolUsageLog] = []
        self.log_file = "tool_usage_logs.json"
        self.load_logs()
    
    def log_tool_usage(self, 
                      tool_name: str, 
                      user_input: str, 
                      parameters: Dict[str, Any],
                      actual_result: Dict[str, Any],
                      success: bool,
                      error_message: Optional[str] = None,
                      execution_time: float = 0.0,
                      llm_confidence: Optional[float] = None):
        """툴 사용 로그 기록"""
        log = ToolUsageLog(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            user_input=user_input,
            parameters=parameters,
            actual_result=actual_result,
            success=success,
            error_message=error_message,
            execution_time=execution_time,
            llm_confidence=llm_confidence
        )
        
        self.usage_logs.append(log)
        self.save_logs()
        
        logger.info(f"툴 사용 로그 기록: {tool_name} - 성공: {success}")
    
    def analyze_tool_accuracy(self, tool_name: str) -> MetadataAccuracyReport:
        """특정 툴의 메타데이터 정확성 분석"""
        tool_logs = [log for log in self.usage_logs if log.tool_name == tool_name]
        
        if not tool_logs:
            return MetadataAccuracyReport(
                tool_name=tool_name,
                total_usage=0,
                success_rate=0.0,
                common_errors=[],
                parameter_accuracy={},
                description_accuracy=0.0,
                suggested_improvements=["사용 데이터가 없습니다. 더 많은 시연이 필요합니다."]
            )
        
        # 기본 통계
        total_usage = len(tool_logs)
        success_count = sum(1 for log in tool_logs if log.success)
        success_rate = success_count / total_usage if total_usage > 0 else 0.0
        
        # 에러 분석
        error_messages = [log.error_message for log in tool_logs if log.error_message]
        common_errors = self._analyze_common_errors(error_messages)
        
        # 파라미터 정확성 분석
        parameter_accuracy = self._analyze_parameter_accuracy(tool_logs)
        
        # 설명 정확성 분석
        description_accuracy = self._analyze_description_accuracy(tool_logs)
        
        # 개선 제안
        suggested_improvements = self._generate_improvement_suggestions(
            tool_logs, common_errors, parameter_accuracy, description_accuracy
        )
        
        return MetadataAccuracyReport(
            tool_name=tool_name,
            total_usage=total_usage,
            success_rate=success_rate,
            common_errors=common_errors,
            parameter_accuracy=parameter_accuracy,
            description_accuracy=description_accuracy,
            suggested_improvements=suggested_improvements
        )
    
    def _analyze_common_errors(self, error_messages: List[str]) -> List[str]:
        """일반적인 에러 패턴 분석"""
        error_counts = {}
        for error in error_messages:
            if error:
                # 에러 메시지에서 핵심 키워드 추출
                key_terms = self._extract_error_keywords(error)
                for term in key_terms:
                    error_counts[term] = error_counts.get(term, 0) + 1
        
        # 상위 5개 에러 반환
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{error}: {count}회" for error, count in sorted_errors[:5]]
    
    def _extract_error_keywords(self, error_message: str) -> List[str]:
        """에러 메시지에서 키워드 추출"""
        keywords = []
        
        # GitHub API 에러
        if "404" in error_message:
            keywords.append("NOT_FOUND")
        if "403" in error_message:
            keywords.append("RATE_LIMIT")
        if "422" in error_message:
            keywords.append("INVALID_INPUT")
        
        # MongoDB 에러
        if "connection" in error_message.lower():
            keywords.append("CONNECTION_ERROR")
        if "timeout" in error_message.lower():
            keywords.append("TIMEOUT")
        
        # 검색 API 에러
        if "api key" in error_message.lower():
            keywords.append("API_KEY_MISSING")
        if "quota" in error_message.lower():
            keywords.append("QUOTA_EXCEEDED")
        
        return keywords if keywords else ["UNKNOWN_ERROR"]
    
    def _analyze_parameter_accuracy(self, tool_logs: List[ToolUsageLog]) -> Dict[str, float]:
        """파라미터 정확성 분석"""
        if not tool_logs:
            return {}
        
        # 성공한 로그만 분석
        successful_logs = [log for log in tool_logs if log.success]
        if not successful_logs:
            return {}
        
        # 모든 파라미터 키 수집
        all_params = set()
        for log in successful_logs:
            all_params.update(log.parameters.keys())
        
        param_accuracy = {}
        for param in all_params:
            # 해당 파라미터가 사용된 횟수
            param_usage = sum(1 for log in successful_logs if param in log.parameters)
            # 전체 성공 횟수 대비 비율
            accuracy = param_usage / len(successful_logs) if successful_logs else 0.0
            param_accuracy[param] = accuracy
        
        return param_accuracy
    
    def _analyze_description_accuracy(self, tool_logs: List[ToolUsageLog]) -> float:
        """설명 정확성 분석 (LLM 신뢰도 기반)"""
        logs_with_confidence = [log for log in tool_logs if log.llm_confidence is not None]
        
        if not logs_with_confidence:
            return 0.0
        
        # LLM 신뢰도의 평균
        avg_confidence = sum(log.llm_confidence for log in logs_with_confidence) / len(logs_with_confidence)
        return avg_confidence
    
    def _generate_improvement_suggestions(self, 
                                        tool_logs: List[ToolUsageLog],
                                        common_errors: List[str],
                                        parameter_accuracy: Dict[str, float],
                                        description_accuracy: float) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 에러 기반 제안
        if common_errors:
            suggestions.append(f"에러 패턴 분석: {', '.join(common_errors[:3])}")
            
            if any("RATE_LIMIT" in error for error in common_errors):
                suggestions.append("Rate limit 제약사항을 메타데이터에 더 명확히 추가하세요")
            
            if any("NOT_FOUND" in error for error in common_errors):
                suggestions.append("존재하지 않는 리소스에 대한 에러 처리를 개선하세요")
        
        # 파라미터 기반 제안
        low_accuracy_params = [param for param, acc in parameter_accuracy.items() if acc < 0.5]
        if low_accuracy_params:
            suggestions.append(f"낮은 사용률 파라미터: {', '.join(low_accuracy_params)} - 설명을 개선하거나 필수 파라미터로 변경 고려")
        
        # 설명 정확성 기반 제안
        if description_accuracy < 0.7:
            suggestions.append("LLM 신뢰도가 낮습니다. 툴 설명을 더 구체적이고 명확하게 개선하세요")
        
        # 사용 패턴 기반 제안
        if len(tool_logs) < 10:
            suggestions.append("더 많은 사용 데이터가 필요합니다. 다양한 시나리오로 테스트하세요")
        
        return suggestions
    
    def generate_metadata_tuning_report(self) -> Dict[str, Any]:
        """전체 메타데이터 튜닝 리포트 생성"""
        all_tools = set(log.tool_name for log in self.usage_logs)
        
        reports = {}
        for tool_name in all_tools:
            reports[tool_name] = asdict(self.analyze_tool_accuracy(tool_name))
        
        # 전체 통계
        total_usage = len(self.usage_logs)
        overall_success_rate = sum(1 for log in self.usage_logs if log.success) / total_usage if total_usage > 0 else 0.0
        
        return {
            "summary": {
                "total_usage": total_usage,
                "overall_success_rate": overall_success_rate,
                "tools_analyzed": len(all_tools)
            },
            "tool_reports": reports,
            "recommendations": self._generate_overall_recommendations(reports)
        }
    
    def _generate_overall_recommendations(self, reports: Dict[str, Any]) -> List[str]:
        """전체 개선 권장사항"""
        recommendations = []
        
        # 성공률이 낮은 툴들
        low_success_tools = [
            tool for tool, report in reports.items() 
            if report["success_rate"] < 0.7
        ]
        
        if low_success_tools:
            recommendations.append(f"성공률이 낮은 툴들: {', '.join(low_success_tools)} - 에러 처리와 설명 개선 필요")
        
        # 사용량이 적은 툴들
        low_usage_tools = [
            tool for tool, report in reports.items() 
            if report["total_usage"] < 5
        ]
        
        if low_usage_tools:
            recommendations.append(f"사용량이 적은 툴들: {', '.join(low_usage_tools)} - 더 많은 테스트 필요")
        
        return recommendations
    
    def save_logs(self):
        """로그를 파일에 저장"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(log) for log in self.usage_logs], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"로그 저장 실패: {e}")
    
    def load_logs(self):
        """파일에서 로그 로드"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.usage_logs = [ToolUsageLog(**log_data) for log_data in data]
        except FileNotFoundError:
            self.usage_logs = []
        except Exception as e:
            logger.error(f"로그 로드 실패: {e}")
            self.usage_logs = []

# 전역 검증기 인스턴스
metadata_validator = MetadataValidator()

def log_tool_execution(tool_name: str, 
                      user_input: str, 
                      parameters: Dict[str, Any],
                      result: Dict[str, Any],
                      success: bool = True,
                      error_message: Optional[str] = None,
                      execution_time: float = 0.0,
                      llm_confidence: Optional[float] = None):
    """툴 실행 로그 기록 (편의 함수)"""
    metadata_validator.log_tool_usage(
        tool_name=tool_name,
        user_input=user_input,
        parameters=parameters,
        actual_result=result,
        success=success,
        error_message=error_message,
        execution_time=execution_time,
        llm_confidence=llm_confidence
    )

def get_metadata_tuning_report() -> Dict[str, Any]:
    """메타데이터 튜닝 리포트 반환"""
    return metadata_validator.generate_metadata_tuning_report()

def analyze_specific_tool(tool_name: str) -> MetadataAccuracyReport:
    """특정 툴 분석"""
    return metadata_validator.analyze_tool_accuracy(tool_name)
