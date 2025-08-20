"""
에이전트 시스템

LLM 친화적인 에이전트 시스템입니다.
Function Calling을 지원하여 LLM이 적절한 툴을 선택하고 실행할 수 있도록 합니다.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from ..tools import tool_registry
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)

class Agent:
    """LLM 친화적인 에이전트"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        사용자 메시지를 처리하고 적절한 툴을 실행합니다.
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            
        Returns:
            처리 결과
        """
        try:
            # 1. 툴 사용 의도 분석
            tool_intent = await self._analyze_tool_intent(message)
            
            if tool_intent:
                # 2. 툴 실행
                tool_result = await self._execute_tool(tool_intent)
                
                # 3. 결과를 바탕으로 응답 생성
                response = await self._generate_response_with_tool_result(
                    message, tool_result, session_id
                )
            else:
                # 4. 일반적인 대화 응답 생성
                response = await self._generate_general_response(message, session_id)
            
            return {
                "status": "success",
                "response": response,
                "tool_used": tool_intent.get("tool_name") if tool_intent else None,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"에이전트 처리 중 오류: {str(e)}")
            return {
                "status": "error",
                "response": "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
                "error": str(e)
            }
    
    async def _analyze_tool_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """
        사용자 메시지에서 툴 사용 의도를 분석합니다.
        Function Calling을 사용하여 LLM이 적절한 툴을 선택하도록 합니다.
        """
        try:
            # 사용 가능한 툴들의 Function Calling 스키마
            function_schemas = tool_registry.get_function_schemas()
            
            if not function_schemas:
                return None
            
            # LLM에게 툴 선택 요청
            system_prompt = """당신은 사용자의 요청을 분석하여 적절한 툴을 선택하는 에이전트입니다.

사용 가능한 툴들:
{}

사용자의 요청을 분석하여 가장 적절한 툴을 선택하고 필요한 매개변수를 추출하세요.
툴이 필요하지 않은 경우 null을 반환하세요.""".format(
                "\n".join(tool_registry.get_tool_descriptions())
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"사용자 요청: {message}"}
            ]
            
            # Function Calling을 사용하여 툴 선택
            response = await self.llm_service.chat_completion_with_functions(
                messages=messages,
                functions=function_schemas,
                function_call="auto"
            )
            
            # Function Calling 결과 파싱
            if response.get("function_call"):
                function_call = response["function_call"]
                tool_name = function_call["name"]
                arguments = json.loads(function_call["arguments"])
                
                return {
                    "tool_name": tool_name,
                    "parameters": arguments
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"툴 의도 분석 중 오류: {str(e)}")
            return None
    
    async def _execute_tool(self, tool_intent: Dict[str, Any]) -> Dict[str, Any]:
        """선택된 툴을 실행합니다."""
        try:
            tool_name = tool_intent["tool_name"]
            parameters = tool_intent["parameters"]
            
            # 툴 조회
            tool = tool_registry.get_tool(tool_name)
            if not tool:
                return {
                    "status": "error",
                    "message": f"알 수 없는 툴입니다: {tool_name}"
                }
            
            # 툴 실행
            result = tool.execute(**parameters)
            
            return {
                "status": "success",
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"툴 실행 중 오류: {str(e)}")
            return {
                "status": "error",
                "message": f"툴 실행 중 오류가 발생했습니다: {str(e)}"
            }
    
    async def _generate_response_with_tool_result(self, 
                                                message: str, 
                                                tool_result: Dict[str, Any],
                                                session_id: str = None) -> str:
        """툴 실행 결과를 바탕으로 응답을 생성합니다."""
        try:
            if tool_result["status"] == "success":
                # 성공한 경우
                tool_data = tool_result["result"]["data"]
                tool_name = tool_result["tool_name"]
                
                system_prompt = f"""당신은 AI 채용 관리 시스템의 도움말 챗봇입니다.

사용자가 요청한 정보를 툴을 통해 성공적으로 가져왔습니다.
툴 실행 결과를 바탕으로 사용자에게 친절하고 유용한 답변을 제공하세요.

툴: {tool_name}
결과: {json.dumps(tool_data, ensure_ascii=False, indent=2)}

답변은 한국어로 작성하고, 2-3문장으로 간결하게 작성하되 필요한 정보는 모두 포함하세요."""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"사용자 요청: {message}"}
                ]
                
                response = await self.llm_service.chat_completion(messages)
                return response
                
            else:
                # 실패한 경우
                error_message = tool_result.get("message", "알 수 없는 오류가 발생했습니다.")
                
                system_prompt = f"""당신은 AI 채용 관리 시스템의 도움말 챗봇입니다.

사용자가 요청한 작업을 수행하려고 했지만 오류가 발생했습니다.
사용자에게 친절하게 오류 상황을 설명하고 대안을 제시하세요.

오류: {error_message}

사용자에게 죄송하다고 말하고, 다른 방법을 제안하거나 도움을 요청하도록 안내하세요."""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"사용자 요청: {message}"}
                ]
                
                response = await self.llm_service.chat_completion(messages)
                return response
                
        except Exception as e:
            self.logger.error(f"응답 생성 중 오류: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    async def _generate_general_response(self, message: str, session_id: str = None) -> str:
        """일반적인 대화 응답을 생성합니다."""
        try:
            system_prompt = """당신은 AI 채용 관리 시스템의 도움말 챗봇입니다.

주요 기능:
1. 채용공고 등록 및 관리
2. 지원자 관리 및 평가  
3. 면접 일정 관리
4. 포트폴리오 분석
5. 자기소개서 검증
6. 인재 추천

사용자의 질문에 친절하고 정확하게 답변해주세요.
한국어로 답변하며, 필요시 구체적인 단계별 가이드를 제공하세요.
답변은 2-3문장으로 간결하게 작성하되, 필요한 정보는 모두 포함하세요."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = await self.llm_service.chat_completion(messages)
            return response
            
        except Exception as e:
            self.logger.error(f"일반 응답 생성 중 오류: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """사용 가능한 툴 목록을 반환합니다."""
        tools = []
        for tool in tool_registry.get_all_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "examples": tool.examples
            })
        return tools
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Function Calling을 위한 툴 스키마를 반환합니다."""
        return tool_registry.get_function_schemas()
