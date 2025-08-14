"""
LangGraph 기반 모듈화된 에이전트 챗봇
재사용 가능한 구조로 설계되어 다른 프로젝트에서도 활용 가능
"""

import os
import json
from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 로컬 모듈 imports
from langgraph_config import (
    config,
    get_tool_by_keywords,
    is_tool_request,
    get_tool_description,
    is_navigate_intent,
)
from langgraph_config import is_dom_action_intent, is_ui_dump_intent
from langgraph_tools import tool_manager
from admin_mode import handle_admin_mode, is_admin_mode

# 환경 변수 로드
load_dotenv()

# 상태 정의
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    current_tool: Optional[str]
    tool_input: Optional[str]
    tool_output: Optional[str]
    user_input: str
    context: Dict[str, Any]
    session_id: str
    mode: str  # 'general' or 'tool'
    confidence: float
    next_action: Optional[str]
    llm_intent: Optional[str]
    llm_target: Optional[str]

class LangGraphAgent:
    """모듈화된 LangGraph 에이전트 클래스"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.graph = self._build_graph()
        self.sessions = {}
        # 서버 기동 시 동적 툴 로드
        try:
            tool_manager.load_dynamic_tools()
        except Exception as e:
            print(f"동적 툴 로드 실패: {e}")
        
    def _initialize_llm(self):
        """LLM 초기화"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            return ChatGoogleGenerativeAI(
                model=config.llm_model,
                google_api_key=api_key,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens
            )
        except Exception as e:
            print(f"LLM 초기화 실패: {e}")
            return None
    
    def _build_graph(self):
        """LangGraph 워크플로우 구축"""
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("classify_input", self._classify_input)
        workflow.add_node("general_conversation", self._general_conversation)
        workflow.add_node("tool_execution", self._tool_execution)
        workflow.add_node("response_generation", self._response_generation)
        
        # START에서 classify_input으로
        workflow.add_edge(START, "classify_input")
        
        # 조건부 라우팅
        workflow.add_conditional_edges(
            "classify_input",
            self._route_after_classification,
            {
                "general": "general_conversation",
                "tool": "tool_execution"
            }
        )
        
        # 일반 대화와 툴 실행에서 응답 생성으로
        workflow.add_edge("general_conversation", "response_generation")
        workflow.add_edge("tool_execution", "response_generation")
        
        # 응답 생성에서 END로
        workflow.add_edge("response_generation", END)
        
        return workflow.compile()
    
    def _classify_input(self, state: AgentState) -> AgentState:
        """사용자 입력 분류"""
        user_input = state["user_input"]
        
        # LLM 기반 의도 분류 시도
        intent, target = self._classify_with_llm(user_input)
        state["llm_intent"] = intent
        state["llm_target"] = target

        # 사용자가 클릭/열기 등 DOM 액션을 명시했다면 네비게이션 예측을 상쇄하고 DOM 액션을 우선시한다.
        if is_dom_action_intent(user_input):
            state["mode"] = "tool"
            state["next_action"] = "tool"
            state["llm_intent"] = "dom_action"
            return state
        # 사용자가 UI 덤프를 요청하면 dom_action으로 덤프 명령을 생성하도록 우선시
        if is_ui_dump_intent(user_input):
            state["mode"] = "tool"
            state["next_action"] = "tool"
            state["llm_intent"] = "dom_action"
            state["llm_target"] = "dumpUI"
            return state

        if intent == "navigate":
            state["mode"] = "tool"
            state["next_action"] = "tool"
        elif intent == "tool":
            state["mode"] = "tool"
            state["next_action"] = "tool"
        else:
            # LLM이 general로 분류했더라도 이동 의도가 뚜렷하면 navigate로 보정
            if is_navigate_intent(user_input):
                state["mode"] = "tool"
                state["next_action"] = "tool"
                state["llm_intent"] = "navigate"
                # target 미추출 시 도구에서 자연어 매핑 처리
            elif is_dom_action_intent(user_input):
                state["mode"] = "tool"
                state["next_action"] = "tool"
                state["llm_intent"] = "dom_action"
            else:
                state["mode"] = "general"
                state["next_action"] = "general"
        
        return state
    
    def _route_after_classification(self, state: AgentState) -> str:
        """분류 후 라우팅 결정"""
        return state["next_action"]
    
    def _general_conversation(self, state: AgentState) -> AgentState:
        """일반 대화 처리"""
        try:
            if not self.llm:
                state["messages"].append({
                    "role": "assistant",
                    "content": "죄송합니다. AI 서비스를 사용할 수 없습니다.",
                    "timestamp": datetime.now().isoformat()
                })
                return state
            
            # 대화 히스토리 구성
            messages = []
            for msg in state["messages"][-5:]:  # 최근 5개 메시지만 사용
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # 시스템 메시지 추가
            system_message = SystemMessage(content=config.system_message)
            
            messages.insert(0, system_message)
            messages.append(HumanMessage(content=state["user_input"]))
            
            # LLM 응답 생성
            response = self.llm.invoke(messages)
            
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            state["messages"].append({
                "role": "assistant",
                "content": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    def _tool_execution(self, state: AgentState) -> AgentState:
        """툴 실행"""
        try:
            # 툴 매니저를 사용하여 적절한 툴 선택 (LLM 의도 우선)
            selected_tool = None
            if state.get("llm_intent") == "navigate":
                selected_tool = "navigate"
            elif state.get("llm_intent") == "dom_action":
                selected_tool = "dom_action"
            if not selected_tool:
                selected_tool = get_tool_by_keywords(state["user_input"])
            
            if selected_tool:
                # 툴 매니저를 통해 툴 실행
                # context에 session_id 주입(권한 검사용)
                context_with_session = dict(state["context"] or {})
                context_with_session.setdefault("session_id", state["session_id"])
                # 관리자 모드에서 생성되는 툴은 자동 신뢰 옵션 부여 가능
                if selected_tool == 'create_function_tool' and is_admin_mode(state['session_id']):
                    context_with_session['auto_trust_new_tool'] = True

                query_payload = state["user_input"]
                if selected_tool == "navigate" and state.get("llm_target"):
                    query_payload = json.dumps({"target": state["llm_target"]}, ensure_ascii=False)
                # 자연어 클릭 지시를 dom_action으로 매핑 (셀렉터는 프론트의 UI 인덱서가 해석)
                if selected_tool == "dom_action":
                    if state.get("llm_target") == "dumpUI":
                        query_payload = json.dumps({
                            "action": "dumpUI",
                            "args": { }
                        }, ensure_ascii=False)
                    else:
                        query_payload = json.dumps({
                            "action": "click",
                            "args": { "query": state["user_input"] }
                        }, ensure_ascii=False)

                tool_result = tool_manager.execute_tool(
                    selected_tool,
                    query_payload,
                    context_with_session,
                )

                # navigate 등의 구조화 응답(JSON 문자열)인 경우 파싱 시도
                try:
                    parsed = json.loads(tool_result)
                    # 구조화된 응답을 그대로 반환 메시지에 반영할 수 있도록 저장
                    state["tool_output"] = parsed
                except Exception:
                    state["tool_output"] = tool_result

                state["current_tool"] = selected_tool
            else:
                state["tool_output"] = "죄송합니다. 요청하신 기능을 찾을 수 없습니다."
            
        except Exception as e:
            state["tool_output"] = f"툴 실행 중 오류가 발생했습니다: {str(e)}"
        
        return state
    
    def _response_generation(self, state: AgentState) -> AgentState:
        """최종 응답 생성"""
        try:
            if state["mode"] == "tool" and state["tool_output"]:
                # 툴 실행 결과를 자연스러운 응답으로 변환
                tool_output = state["tool_output"]
                # navigate 등 구조화 응답 처리
                if isinstance(tool_output, dict) and tool_output.get("type") == "react_agent_response":
                    response_content = json.dumps(tool_output, ensure_ascii=False)
                else:
                    response_content = self._format_tool_response(
                        str(tool_output),
                        state["current_tool"],
                    )
            else:
                # 일반 대화의 경우 마지막 메시지 사용
                response_content = state["messages"][-1]["content"]
            
            # 최종 응답 저장
            state["messages"].append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            state["messages"].append({
                "role": "assistant",
                "content": f"응답 생성 중 오류가 발생했습니다: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    def _format_tool_response(self, tool_output: str, tool_name: str) -> str:
        """툴 실행 결과를 자연스러운 응답으로 포맷팅"""
        description = get_tool_description(tool_name)
        return f"{description}\n\n{tool_output}"

    def _classify_with_llm(self, user_input: str) -> (str, Optional[str]):
        """LLM을 사용하여 의도를 분류하고 타겟 경로를 추출합니다.
        반환: (intent, target) where intent in {navigate, tool, general}
        """
        try:
            if not self.llm:
                if is_navigate_intent(user_input):
                    return "navigate", None
                if is_tool_request(user_input):
                    return "tool", None
                return "general", None

            allowed_routes = "\n".join(config.allowed_routes)
            system = SystemMessage(content=(
                "당신은 사용자의 요청을 의도(navigate|tool|general)로 분류하고, navigate일 때 target 경로를 추출하는 분류기입니다.\n"
                "반드시 JSON만 출력하세요. 예: {\"intent\":\"navigate\", \"target\":\"/resume\"}.\n"
                "target는 아래 허용 경로 중 하나여야 합니다. 허용 경로 이외면 null 또는 공백으로 두세요.\n"
                f"허용 경로:\n{allowed_routes}\n"
            ))
            human = HumanMessage(content=f"사용자 입력: {user_input}")
            resp = self.llm.invoke([system, human])
            content = resp.content if isinstance(resp.content, str) else str(resp.content)
            data = json.loads(content)
            intent = str(data.get("intent", "general")).lower()
            target = data.get("target")
            if intent == "navigate" and target not in config.allowed_routes:
                target = None
            if intent not in ("navigate", "tool"):
                intent = "general"
            return intent, target
        except Exception:
            return "general", None
    

    
    async def process_message(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """메시지 처리 메인 함수"""
        try:
            # 관리자 모드 트리거 우선 처리
            admin_reply = handle_admin_mode(session_id, user_input)
            if admin_reply is not None:
                # 세션이 없더라도 응답 반환을 위해 세션 보장
                if session_id not in self.sessions:
                    self.sessions[session_id] = {
                        "messages": [],
                        "created_at": datetime.now(),
                        "last_activity": datetime.now()
                    }
                self.sessions[session_id]["messages"].append({
                    "role": "assistant",
                    "content": admin_reply,
                    "timestamp": datetime.now().isoformat()
                })
                # 프론트 표시용 이벤트 힌트(옵션): 시스템 메시지 브로드캐스트는 프런트에서 커스텀 이벤트로 처리 가능
                return {
                    "success": True,
                    "message": admin_reply,
                    "mode": "general",
                    "tool_used": None,
                    "confidence": 1.0,
                    "session_id": session_id
                }
            # 세션 초기화 또는 가져오기
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "messages": [],
                    "created_at": datetime.now(),
                    "last_activity": datetime.now()
                }
            
            session = self.sessions[session_id]
            
            # 상태 초기화
            state = AgentState(
                messages=session["messages"].copy(),
                current_tool=None,
                tool_input=None,
                tool_output=None,
                user_input=user_input,
                context=context or {},
                session_id=session_id,
                mode="general",
                confidence=0.8,
                next_action=None
            )
            
            # 사용자 메시지 추가
            state["messages"].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # 그래프 실행
            final_state = await self.graph.ainvoke(state)
            
            # 세션 업데이트
            session["messages"] = final_state["messages"]
            session["last_activity"] = datetime.now()
            
            # 응답 반환
            return {
                "success": True,
                "message": final_state["messages"][-1]["content"],
                "mode": final_state["mode"],
                "tool_used": final_state.get("current_tool"),
                "confidence": final_state["confidence"],
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"오류가 발생했습니다: {str(e)}",
                "error": str(e)
            }
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 히스토리 조회"""
        if session_id in self.sessions:
            return self.sessions[session_id]["messages"]
        return []
    
    def clear_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# 전역 에이전트 인스턴스
agent = LangGraphAgent()
