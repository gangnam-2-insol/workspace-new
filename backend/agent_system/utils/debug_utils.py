"""
챗봇 디버깅 유틸리티

사용자 요청부터 LLM 분류, 행동까지 모든 과정을 상세히 추적하는 디버깅 도구
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import traceback

@dataclass
class DebugStep:
    """디버깅 단계 정보"""
    step_name: str
    timestamp: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class DebugSession:
    """디버깅 세션 정보"""
    session_id: str
    user_id: str
    start_time: str
    steps: List[DebugStep]
    total_duration_ms: float
    success: bool
    final_response: str

class ChatbotDebugger:
    """챗봇 디버깅 클래스"""
    
    def __init__(self, session_id: str, user_id: str = "unknown"):
        self.session_id = session_id
        self.user_id = user_id
        self.start_time = datetime.now()
        self.steps = []
        self.current_step = None
        
    def start_step(self, step_name: str, input_data: Dict[str, Any] = None):
        """디버깅 단계 시작"""
        self.current_step = {
            "step_name": step_name,
            "start_time": datetime.now(),
            "input_data": input_data or {}
        }
        print(f"\n🔍 [DEBUG] {step_name} 시작")
        if input_data:
            print(f"   📥 입력: {json.dumps(input_data, ensure_ascii=False, indent=2)}")
    
    def end_step(self, output_data: Dict[str, Any] = None, error: str = None, metadata: Dict[str, Any] = None):
        """디버깅 단계 종료"""
        if not self.current_step:
            return
            
        end_time = datetime.now()
        duration = (end_time - self.current_step["start_time"]).total_seconds() * 1000
        
        step = DebugStep(
            step_name=self.current_step["step_name"],
            timestamp=self.current_step["start_time"].isoformat(),
            input_data=self.current_step["input_data"],
            output_data=output_data or {},
            duration_ms=duration,
            error=error,
            metadata=metadata or {}
        )
        
        self.steps.append(step)
        
        # 콘솔 출력
        print(f"   📤 출력: {json.dumps(output_data, ensure_ascii=False, indent=2)}")
        if error:
            print(f"   ❌ 오류: {error}")
        print(f"   ⏱️  소요시간: {duration:.2f}ms")
        
        self.current_step = None
    
    def log_llm_request(self, prompt: str, model: str, temperature: float):
        """LLM 요청 로깅"""
        print(f"\n🤖 [LLM 요청]")
        print(f"   모델: {model}")
        print(f"   온도: {temperature}")
        print(f"   프롬프트: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    
    def log_llm_response(self, response: str, tokens_used: int = None):
        """LLM 응답 로깅"""
        print(f"\n🤖 [LLM 응답]")
        print(f"   응답: {response}")
        if tokens_used:
            print(f"   토큰 사용량: {tokens_used}")
    
    def log_tool_execution(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]):
        """툴 실행 로깅"""
        print(f"\n🔧 [툴 실행] {tool_name}")
        print(f"   파라미터: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
        print(f"   결과: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    def log_intent_classification(self, user_input: str, intent: str, confidence: float, reasoning: str):
        """의도 분류 로깅"""
        print(f"\n🎯 [의도 분류]")
        print(f"   사용자 입력: {user_input}")
        print(f"   분류된 의도: {intent}")
        print(f"   신뢰도: {confidence:.2%}")
        print(f"   추론 과정: {reasoning}")
    
    def log_route_decision(self, from_node: str, to_node: str, reason: str):
        """라우팅 결정 로깅"""
        print(f"\n🔄 [라우팅 결정]")
        print(f"   {from_node} → {to_node}")
        print(f"   이유: {reason}")
    
    def finish_session(self, final_response: str, success: bool = True):
        """세션 완료"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds() * 1000
        
        session = DebugSession(
            session_id=self.session_id,
            user_id=self.user_id,
            start_time=self.start_time.isoformat(),
            steps=self.steps,
            total_duration_ms=total_duration,
            success=success,
            final_response=final_response
        )
        
        print(f"\n📊 [디버깅 세션 완료]")
        print(f"   세션 ID: {self.session_id}")
        print(f"   총 소요시간: {total_duration:.2f}ms")
        print(f"   단계 수: {len(self.steps)}")
        print(f"   성공 여부: {'✅' if success else '❌'}")
        print(f"   최종 응답: {final_response}")
        
        return session
    
    def export_debug_log(self, filename: str = None) -> str:
        """디버깅 로그 내보내기"""
        if not filename:
            filename = f"debug_log_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        session = self.finish_session("", True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, ensure_ascii=False, indent=2)
        
        print(f"   📄 디버깅 로그 저장: {filename}")
        return filename

def create_debugger(session_id: str, user_id: str = "unknown") -> ChatbotDebugger:
    """디버거 생성 헬퍼 함수"""
    return ChatbotDebugger(session_id, user_id)

def log_function_call(func_name: str, args: Dict[str, Any], result: Any, error: Exception = None):
    """함수 호출 로깅 데코레이터용"""
    print(f"\n🔧 [함수 호출] {func_name}")
    print(f"   인자: {json.dumps(args, ensure_ascii=False, indent=2)}")
    if error:
        print(f"   ❌ 오류: {error}")
        print(f"   📍 스택 트레이스: {traceback.format_exc()}")
    else:
        print(f"   ✅ 결과: {result}")
