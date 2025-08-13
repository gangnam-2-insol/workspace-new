"""
LangGraph 기반 Agent 시스템
실제 LangGraph 라이브러리를 사용하여 구현된 Agent 시스템
"""

import re
import json
import math
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from dataclasses import dataclass
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio

# LangGraph 관련 import
try:
    # Pydantic 버전 충돌을 피하기 위해 환경 변수 설정
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    os.environ["LANGCHAIN_API_KEY"] = ""
    
    # LangGraph import 시도
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph 라이브러리 사용 가능")
except (ImportError, TypeError, Exception) as e:
    LANGGRAPH_AVAILABLE = False
    print(f"❌ LangGraph 라이브러리 로드 실패: {e}")
    print("💡 LangGraph를 사용하지 않고 기존 시스템으로 대체합니다.")

load_dotenv()

# Gemini AI 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

# 상태 정의 (LangGraph용)
class AgentState(TypedDict):
    """LangGraph Agent 상태 정의"""
    user_input: str
    conversation_history: List[Dict[str, str]]
    intent: str
    tool_result: str
    final_response: str
    error: str
    current_node: str
    next_node: str
    metadata: Dict[str, Any]

# 노드 함수들
def intent_detection_node(state: AgentState) -> AgentState:
    """의도 분류 노드"""
    try:
        user_input = state["user_input"]
        
        system_prompt = """
다음 카테고리 중 하나로 분류해주세요:

1. "search" - 정보 검색, 조사, 찾기 관련 요청
2. "calc" - 계산, 수식, 수치 처리 관련 요청
3. "db" - 데이터베이스 조회, 저장된 정보 검색
4. "recruit" - 채용공고 작성, 채용 관련 내용 생성
5. "chat" - 일반적인 대화, 질문, 도움 요청

분류 결과만 반환해주세요 (예: "search", "calc", "db", "recruit", "chat")
"""
        
        prompt = f"{system_prompt}\n\n사용자 입력: {user_input}"
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        
        # 유효한 의도인지 확인
        valid_intents = ["search", "calc", "db", "recruit", "chat"]
        if intent not in valid_intents:
            intent = "chat"
        
        state["intent"] = intent
        state["current_node"] = "intent_detection"
        state["metadata"]["intent_detection_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 의도 분류 완료: {intent}")
        return state
        
    except Exception as e:
        state["error"] = f"의도 분류 중 오류: {str(e)}"
        state["intent"] = "chat"
        return state

def web_search_node(state: AgentState) -> AgentState:
    """웹 검색 노드"""
    try:
        user_input = state["user_input"]
        
        # 시뮬레이션된 검색 결과
        if "개발" in user_input or "프로그래밍" in user_input:
            result = """🔍 최신 개발 트렌드:

📱 프론트엔드:
• React 18의 새로운 기능 (Concurrent Features, Suspense)
• TypeScript 5.0 업데이트 및 개선사항
• Next.js 14의 App Router와 Server Components
• Vue 3의 Composition API 활용

⚙️ 백엔드:
• Node.js 20의 새로운 기능
• Python 3.12의 성능 개선
• Go 1.21의 병렬 처리 개선
• Rust의 메모리 안전성

🤖 AI/ML:
• AI 기반 코드 생성 도구 (GitHub Copilot, Cursor)
• 머신러닝 모델 최적화 기술
• 자연어 처리 발전

☁️ 클라우드/DevOps:
• Kubernetes 1.28의 새로운 기능
• Docker Compose V2 업데이트
• Terraform 1.5의 새로운 기능
• AWS Lambda의 성능 개선"""
        else:
            result = f"🔍 '{user_input}'에 대한 검색 결과를 찾았습니다.\n\n관련 정보를 제공해드리겠습니다."
        
        state["tool_result"] = result
        state["current_node"] = "web_search"
        state["metadata"]["search_query"] = user_input
        state["metadata"]["search_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 웹 검색 완료")
        return state
        
    except Exception as e:
        state["error"] = f"웹 검색 중 오류: {str(e)}"
        return state

def calculator_node(state: AgentState) -> AgentState:
    """계산 노드"""
    try:
        user_input = state["user_input"]
        
        # 수식 계산
        if "연봉" in user_input and "월급" in user_input:
            # 연봉에서 월급 계산
            salary_match = re.search(r'(\d+)만원', user_input)
            if salary_match:
                annual_salary = int(salary_match.group(1))
                monthly_salary = annual_salary // 12
                result = f"💰 연봉 {annual_salary}만원의 월급은 약 {monthly_salary}만원입니다.\n\n(연봉 ÷ 12개월로 계산)"
            else:
                result = "💰 연봉 정보를 찾을 수 없습니다. 구체적인 금액을 알려주세요."
        else:
            result = f"🧮 '{user_input}'에 대한 계산을 수행했습니다.\n\n계산 결과를 제공해드리겠습니다."
        
        state["tool_result"] = result
        state["current_node"] = "calculator"
        state["metadata"]["calculation_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 계산 완료")
        return state
        
    except Exception as e:
        state["error"] = f"계산 중 오류: {str(e)}"
        return state

def recruitment_node(state: AgentState) -> AgentState:
    """채용공고 작성 노드"""
    try:
        user_input = state["user_input"]
        
        # Gemini AI를 사용하여 채용공고 생성
        prompt = f"""
당신은 전문적인 채용공고 작성 전문가입니다.
사용자의 요청을 바탕으로 체계적이고 매력적인 채용공고를 작성해주세요.

사용자 요청: {user_input}

다음 형식으로 채용공고를 작성해주세요:

## 📋 채용공고

### 🏢 회사 정보
- 회사명: [추정 또는 제안]
- 위치: [지역 정보]
- 업종: [업종 정보]

### 💼 모집 직무
- 직무명: [직무명]
- 모집인원: [인원수]
- 경력요건: [경력 요구사항]

### 📝 주요업무
• [구체적인 업무 내용]
• [업무 범위]
• [담당 영역]

### 🎯 자격요건
• [필수 자격요건]
• [기술 스택]
• [경험 요구사항]

### 🌟 우대조건
• [우대사항]
• [추가 스킬]
• [관련 경험]

### 💰 복리후생
• [급여 정보]
• [복리후생]
• [근무환경]

### 📞 지원방법
• [지원 방법]
• [문의처]
• [마감일]

답변은 한국어로 작성하고, 이모지를 적절히 사용하여 가독성을 높여주세요.
"""
        
        response = model.generate_content(prompt)
        result = response.text
        
        state["tool_result"] = result
        state["current_node"] = "recruitment"
        state["metadata"]["recruitment_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 채용공고 작성 완료")
        return state
        
    except Exception as e:
        state["error"] = f"채용공고 작성 중 오류: {str(e)}"
        return state

def database_query_node(state: AgentState) -> AgentState:
    """데이터베이스 조회 노드"""
    try:
        user_input = state["user_input"]
        
        # 시뮬레이션된 DB 조회 결과
        if "채용공고" in user_input or "구인" in user_input:
            result = """📋 저장된 채용공고 목록:

1. 🏢 ABC테크 - 프론트엔드 개발자
   • 위치: 서울 강남구
   • 연봉: 4,000만원 ~ 6,000만원
   • 경력: 2년 이상
   • 상태: 모집중
   • 등록일: 2024-08-01

2. 🏢 XYZ소프트 - 백엔드 개발자
   • 위치: 인천 연수구
   • 연봉: 3,500만원 ~ 5,500만원
   • 경력: 1년 이상
   • 상태: 모집중
   • 등록일: 2024-07-28

3. 🏢 DEF시스템 - 풀스택 개발자
   • 위치: 부산 해운대구
   • 연봉: 4,500만원 ~ 7,000만원
   • 경력: 3년 이상
   • 상태: 모집중
   • 등록일: 2024-07-25

4. 🏢 GHI솔루션 - AI/ML 엔지니어
   • 위치: 대전 유성구
   • 연봉: 5,000만원 ~ 8,000만원
   • 경력: 2년 이상
   • 상태: 모집중
   • 등록일: 2024-07-20

총 4개의 채용공고가 저장되어 있습니다."""
        else:
            result = f"📋 '{user_input}'에 대한 데이터베이스 조회를 수행했습니다.\n\n관련 데이터를 제공해드리겠습니다."
        
        state["tool_result"] = result
        state["current_node"] = "database_query"
        state["metadata"]["db_query_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] DB 조회 완료")
        return state
        
    except Exception as e:
        state["error"] = f"DB 조회 중 오류: {str(e)}"
        return state

def fallback_node(state: AgentState) -> AgentState:
    """일반 대화 처리 노드"""
    try:
        user_input = state["user_input"]
        
        # 일반적인 대화 처리
        if "안녕" in user_input or "hello" in user_input.lower():
            result = "안녕하세요! 😊 무엇을 도와드릴까요? 채용 관련 질문이나 일반적인 대화 모두 환영합니다! 💬"
        elif "도움" in user_input or "help" in user_input.lower():
            result = """🤖 AI 채용 관리 시스템 도움말:

📋 주요 기능:
• 채용공고 작성 및 관리
• 이력서 분석 및 평가
• 면접 일정 관리
• 인재 추천 및 매칭

💡 사용법:
• "채용공고 작성해줘" - AI가 채용공고를 작성해드립니다
• "최신 개발 트렌드 알려줘" - 기술 정보를 검색해드립니다
• "연봉 4000만원의 월급" - 급여 계산을 도와드립니다
• "저장된 채용공고 보여줘" - 기존 데이터를 조회해드립니다

🎯 친근한 대화:
• 자연스럽게 질문해주세요
• 구체적인 내용을 요청하면 더 정확한 답변을 드릴 수 있습니다
• 이모지도 사용 가능합니다! 😊"""
        elif "감사" in user_input or "고마워" in user_input:
            result = "천만에요! 😊 도움이 되어서 기쁩니다. 추가로 궁금한 것이 있으시면 언제든 말씀해주세요! 🙏"
        else:
            result = "안녕하세요! 😊 무엇을 도와드릴까요? 채용 관련 질문이나 일반적인 대화 모두 환영합니다! 💬"
        
        state["tool_result"] = result
        state["current_node"] = "fallback"
        state["metadata"]["chat_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 일반 대화 처리 완료")
        return state
        
    except Exception as e:
        state["error"] = f"대화 처리 중 오류: {str(e)}"
        return state

def response_formatter_node(state: AgentState) -> AgentState:
    """응답 포매터 노드"""
    try:
        tool_result = state.get("tool_result", "")
        intent = state.get("intent", "")
        error = state.get("error", "")
        
        if error:
            # 오류가 있는 경우
            final_response = f"❌ 오류가 발생했습니다: {error}\n\n💡 다시 시도해보시거나 다른 질문을 해주세요."
        else:
            # 정상적인 응답
            # 도구별 추가 메시지
            if intent == "search":
                additional_msg = "\n\n💡 더 구체적인 정보가 필요하시면 말씀해주세요!"
            elif intent == "calc":
                additional_msg = "\n\n🧮 다른 계산이 필요하시면 언제든 말씀해주세요!"
            elif intent == "recruit":
                additional_msg = "\n\n📝 채용공고 수정이나 추가 요청이 있으시면 말씀해주세요!"
            elif intent == "db":
                additional_msg = "\n\n📋 다른 데이터 조회가 필요하시면 말씀해주세요!"
            else:  # chat
                additional_msg = "\n\n💬 추가 질문이 있으시면 언제든 말씀해주세요!"
            
            final_response = f"{tool_result}{additional_msg}"
        
        state["final_response"] = final_response
        state["current_node"] = "response_formatter"
        state["metadata"]["format_time"] = datetime.now().isoformat()
        
        print(f"[LangGraph] 응답 포매팅 완료")
        return state
        
    except Exception as e:
        state["error"] = f"응답 포매팅 중 오류: {str(e)}"
        return state

def route_by_intent(state: AgentState) -> str:
    """의도에 따른 라우팅 함수"""
    intent = state.get("intent", "chat")
    
    routing_map = {
        "search": "web_search",
        "calc": "calculator", 
        "recruit": "recruitment",
        "db": "database_query",
        "chat": "fallback"
    }
    
    return routing_map.get(intent, "fallback")

def create_langgraph_workflow():
    """LangGraph 워크플로우 생성"""
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph 라이브러리가 설치되지 않았습니다.")
    
    # 워크플로우 그래프 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("calculator", calculator_node)
    workflow.add_node("recruitment", recruitment_node)
    workflow.add_node("database_query", database_query_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("response_formatter", response_formatter_node)
    
    # 조건부 엣지 정의 (의도 분류 후 라우팅)
    workflow.add_conditional_edges(
        "intent_detection",
        route_by_intent,
        {
            "web_search": "web_search",
            "calculator": "calculator",
            "recruitment": "recruitment",
            "database_query": "database_query",
            "fallback": "fallback"
        }
    )
    
    # 모든 도구 노드에서 포매터로 연결
    workflow.add_edge("web_search", "response_formatter")
    workflow.add_edge("calculator", "response_formatter")
    workflow.add_edge("recruitment", "response_formatter")
    workflow.add_edge("database_query", "response_formatter")
    workflow.add_edge("fallback", "response_formatter")
    
    # 포매터에서 종료
    workflow.add_edge("response_formatter", END)
    
    # 시작점 설정
    workflow.set_entry_point("intent_detection")
    
    return workflow.compile()

class LangGraphAgentSystem:
    """LangGraph 기반 Agent 시스템"""
    
    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph 라이브러리가 설치되지 않았습니다.")
        
        self.workflow = create_langgraph_workflow()
        print("✅ LangGraph Agent 시스템 초기화 완료")
    
    async def process_request(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """사용자 요청을 처리하고 결과를 반환합니다."""
        try:
            # 초기 상태 설정
            initial_state = AgentState(
                user_input=user_input,
                conversation_history=conversation_history or [],
                intent="",
                tool_result="",
                final_response="",
                error="",
                current_node="",
                next_node="",
                metadata={}
            )
            
            # 워크플로우 실행
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "response": result.get("final_response", ""),
                "intent": result.get("intent", ""),
                "error": result.get("error", ""),
                "metadata": result.get("metadata", {}),
                "workflow_trace": result.get("current_node", "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"죄송합니다. 요청 처리 중 오류가 발생했습니다: {str(e)}",
                "intent": "error",
                "error": str(e),
                "metadata": {},
                "workflow_trace": "error"
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """워크플로우 정보 반환"""
        return {
            "nodes": ["intent_detection", "web_search", "calculator", "recruitment", "database_query", "fallback", "response_formatter"],
            "edges": {
                "intent_detection": ["web_search", "calculator", "recruitment", "database_query", "fallback"],
                "web_search": ["response_formatter"],
                "calculator": ["response_formatter"],
                "recruitment": ["response_formatter"],
                "database_query": ["response_formatter"],
                "fallback": ["response_formatter"],
                "response_formatter": ["END"]
            },
            "entry_point": "intent_detection",
            "exit_point": "response_formatter"
        }

# 전역 LangGraph Agent 시스템 인스턴스
langgraph_agent_system = None

def initialize_langgraph_system():
    """LangGraph 시스템 초기화"""
    global langgraph_agent_system
    try:
        if LANGGRAPH_AVAILABLE:
            langgraph_agent_system = LangGraphAgentSystem()
            print("✅ LangGraph Agent 시스템 초기화 성공")
            return True
        else:
            print("❌ LangGraph 라이브러리가 설치되지 않아 초기화할 수 없습니다.")
            return False
    except Exception as e:
        print(f"❌ LangGraph 시스템 초기화 실패: {e}")
        return False

# 시스템 초기화
initialize_langgraph_system()
