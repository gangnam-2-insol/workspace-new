"""
메타데이터 정확성 검증 API

시연 시나리오 실행과 메타데이터 튜닝 리포트를 제공하는 API 엔드포인트들입니다.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..tools.metadata_validator import (
    get_metadata_tuning_report, 
    analyze_specific_tool,
    log_tool_execution
)
from ..tools.demo_scenarios import (
    run_demo_scenarios, 
    run_custom_scenario
)

router = APIRouter(prefix="/metadata-tuning", tags=["메타데이터 튜닝"])

class CustomScenarioRequest(BaseModel):
    """사용자 정의 시나리오 요청"""
    tool_name: str
    user_input: str
    parameters: Dict[str, Any]
    expected_success: bool = True
    expected_error: Optional[str] = None

class ToolExecutionLogRequest(BaseModel):
    """툴 실행 로그 요청"""
    tool_name: str
    user_input: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None
    execution_time: float = 0.0
    llm_confidence: Optional[float] = None

@router.get("/report")
async def get_tuning_report():
    """메타데이터 튜닝 리포트 조회"""
    try:
        report = get_metadata_tuning_report()
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 생성 실패: {str(e)}")

@router.get("/analyze/{tool_name}")
async def analyze_tool(tool_name: str):
    """특정 툴 분석"""
    try:
        analysis = analyze_specific_tool(tool_name)
        return {
            "status": "success",
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"툴 분석 실패: {str(e)}")

@router.post("/run-demo")
async def run_demo(category: Optional[str] = None):
    """시연 시나리오 실행"""
    try:
        results = run_demo_scenarios(category)
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시연 실행 실패: {str(e)}")

@router.post("/run-custom-scenario")
async def run_custom(request: CustomScenarioRequest):
    """사용자 정의 시나리오 실행"""
    try:
        result = run_custom_scenario(
            tool_name=request.tool_name,
            user_input=request.user_input,
            parameters=request.parameters,
            expected_success=request.expected_success,
            expected_error=request.expected_error
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 시나리오 실행 실패: {str(e)}")

@router.post("/log-execution")
async def log_execution(request: ToolExecutionLogRequest):
    """툴 실행 로그 기록"""
    try:
        log_tool_execution(
            tool_name=request.tool_name,
            user_input=request.user_input,
            parameters=request.parameters,
            result=request.result,
            success=request.success,
            error_message=request.error_message,
            execution_time=request.execution_time,
            llm_confidence=request.llm_confidence
        )
        return {
            "status": "success",
            "message": "실행 로그가 기록되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그 기록 실패: {str(e)}")

@router.get("/scenarios")
async def get_available_scenarios():
    """사용 가능한 시나리오 목록 조회"""
    try:
        from ..tools.demo_scenarios import demo_runner
        
        scenarios = {}
        for category, scenario_list in demo_runner.scenarios.items():
            scenarios[category] = [
                {
                    "name": scenario["name"],
                    "tool": scenario["tool"],
                    "description": scenario["description"],
                    "expected_success": scenario["expected_success"]
                }
                for scenario in scenario_list
            ]
        
        return {
            "status": "success",
            "data": scenarios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시나리오 목록 조회 실패: {str(e)}")

@router.get("/stats")
async def get_metadata_stats():
    """메타데이터 통계 조회"""
    try:
        from ..tools.metadata_validator import metadata_validator
        
        total_logs = len(metadata_validator.usage_logs)
        success_count = sum(1 for log in metadata_validator.usage_logs if log.success)
        success_rate = success_count / total_logs if total_logs > 0 else 0.0
        
        # 툴별 통계
        tool_stats = {}
        for log in metadata_validator.usage_logs:
            if log.tool_name not in tool_stats:
                tool_stats[log.tool_name] = {
                    "total_usage": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "avg_execution_time": 0.0,
                    "avg_confidence": 0.0
                }
            
            stats = tool_stats[log.tool_name]
            stats["total_usage"] += 1
            
            if log.success:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            
            stats["avg_execution_time"] += log.execution_time
            if log.llm_confidence:
                stats["avg_confidence"] += log.llm_confidence
        
        # 평균 계산
        for tool_name, stats in tool_stats.items():
            if stats["total_usage"] > 0:
                stats["avg_execution_time"] /= stats["total_usage"]
                if stats["avg_confidence"] > 0:
                    stats["avg_confidence"] /= stats["total_usage"]
        
        return {
            "status": "success",
            "data": {
                "overall": {
                    "total_logs": total_logs,
                    "success_count": success_count,
                    "success_rate": success_rate
                },
                "tool_stats": tool_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
