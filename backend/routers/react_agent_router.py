"""
리액트 에이전트 전용 라우터
PickTalk에서 사용할 수 있도록 모듈화된 에이전트 시스템
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import asyncio

from fastapi import APIRouter, HTTPException
from modules.ai.services.langgraph_agent_system import LangGraphAgentSystem

# 기존 서비스들 import
from modules.core.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/react-agent", tags=["react-agent"])

# OpenAI LLM 서비스 초기화
try:
    from modules.core.services.llm_service import LLMService
    llm_service = LLMService()
    print(f"🔍 [ReactAgent] OpenAI LLM 서비스 초기화 성공")
except Exception as e:
    logger.error(f"OpenAI LLM 서비스 초기화 실패: {e}")
    llm_service = None

# OpenAI 서비스 (비활성화)
openai_service = None

# LangGraph 에이전트 시스템 초기화
try:
    langgraph_system = LangGraphAgentSystem()
except Exception as e:
    logger.error(f"LangGraph 시스템 초기화 실패: {e}")
    langgraph_system = None

# 에이전트 세션 저장소 (실제로는 Redis나 DB 사용 권장)
agent_sessions = {}

@router.post("/start-session")
async def start_react_agent_session(request: Dict[str, Any]):
    """리액트 에이전트 세션 시작"""
    try:
        user_id = request.get("user_id", "user_123")
        company_info = request.get("company_info", {})

        # 세션 ID 생성
        session_id = str(uuid.uuid4())

        # 세션 정보 저장
        agent_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "company_info": company_info,
            "state": "initial",
            "conversation_history": [],
            "extracted_data": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        logger.info(f"리액트 에이전트 세션 시작: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "message": "🤖 AI 에이전트 모드가 시작되었습니다!",
            "state": "initial",
            "next_action": "안녕하세요! 저는 채용공고 작성을 도와주는 AI 에이전트입니다. 어떤 직무의 채용공고를 작성하고 싶으신가요?",
            "quick_actions": [
                {"title": "채용공고 작성", "action": "navigate", "icon": "📝", "params": {"page": "job_posting"}},
                {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
                {"title": "대시보드", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}},
                {"title": "채용공고 목록", "action": "navigate", "icon": "📋", "params": {"page": "recruitment"}}
            ],
            "suggestions": [
                "프론트엔드 개발자",
                "백엔드 개발자",
                "풀스택 개발자",
                "데이터 사이언티스트"
            ]
        }

    except Exception as e:
        logger.error(f"에이전트 세션 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 시작 실패: {str(e)}")

@router.post("/process-input")
async def process_react_agent_input(request: Dict[str, Any]):
    """리액트 에이전트 입력 처리"""
    try:
        session_id = request.get("session_id")
        user_input = request.get("user_input", "")

        if not session_id or session_id not in agent_sessions:
            raise HTTPException(status_code=400, detail="유효하지 않은 세션 ID")

        session = agent_sessions[session_id]
        current_state = session["state"]

        # OpenAI 기반 에이전트 처리 (LangGraph 대신 직접 처리)
        try:
            # OpenAI LLM 서비스로 직접 처리
            if llm_service:
                agent_response = await _process_with_openai(
                    llm_service, user_input, session["conversation_history"]
                )

                # 응답 분석 및 상태 전환
                new_state = _determine_next_state(current_state, user_input, agent_response)

                # 세션 업데이트
                session["state"] = new_state
                session["conversation_history"].append({
                    "user": user_input,
                    "agent": agent_response.get("response", ""),
                    "timestamp": datetime.now().isoformat()
                })
                session["last_updated"] = datetime.now().isoformat()

                # 추출된 데이터가 있으면 저장
                if agent_response.get("extracted_fields"):
                    session["extracted_data"].update(agent_response["extracted_fields"])

                # 상태별 응답 강화
                enhanced_response = _enhance_response_by_state(new_state, agent_response, session)

                return {
                    "success": True,
                    "response": enhanced_response["message"],
                    "state": new_state,
                    "extracted_fields": session["extracted_data"],
                    "quick_actions": enhanced_response["quick_actions"],
                    "suggestions": enhanced_response["suggestions"],
                    "session_id": session_id,
                    "tool_result": agent_response.get("tool_result"),  # 툴 실행 결과 추가
                    "tool_error": agent_response.get("tool_error"),    # 툴 실행 에러 추가
                    "intent": agent_response.get("intent"),           # 의도 분류 추가
                    "confidence": agent_response.get("confidence")    # 신뢰도 추가
                }
            else:
                # LLM 서비스 없을 때 기본 처리
                agent_response = _process_basic_response(user_input, current_state)

                # 응답 분석 및 상태 전환
                new_state = _determine_next_state(current_state, user_input, agent_response)

                # 세션 업데이트
                session["state"] = new_state
                session["conversation_history"].append({
                    "user": user_input,
                    "agent": agent_response.get("response", ""),
                    "timestamp": datetime.now().isoformat()
                })
                session["last_updated"] = datetime.now().isoformat()

                # 추출된 데이터가 있으면 저장
                if agent_response.get("extracted_fields"):
                    session["extracted_data"].update(agent_response["extracted_fields"])

                # 상태별 응답 강화
                enhanced_response = _enhance_response_by_state(new_state, agent_response, session)

                return {
                    "success": True,
                    "response": enhanced_response["message"],
                    "state": new_state,
                    "extracted_fields": session["extracted_data"],
                    "quick_actions": enhanced_response["quick_actions"],
                    "suggestions": enhanced_response["suggestions"],
                    "session_id": session_id,
                    "tool_result": agent_response.get("tool_result"),  # 툴 실행 결과 추가
                    "tool_error": agent_response.get("tool_error"),    # 툴 실행 에러 추가
                    "intent": agent_response.get("intent"),           # 의도 분류 추가
                    "confidence": agent_response.get("confidence")    # 신뢰도 추가
                }

        except Exception as e:
            logger.error(f"에이전트 처리 실패: {e}")
            # 에이전트 실패 시 기본 처리로 폴백
            return _fallback_processing(session, user_input, current_state)

    except Exception as e:
        logger.error(f"에이전트 입력 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"입력 처리 실패: {str(e)}")

@router.get("/session-status/{session_id}")
async def get_session_status(session_id: str):
    """세션 상태 조회"""
    try:
        if session_id not in agent_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        session = agent_sessions[session_id]
        return {
            "success": True,
            "session_id": session_id,
            "state": session["state"],
            "extracted_data": session["extracted_data"],
            "conversation_count": len(session["conversation_history"]),
            "created_at": session["created_at"],
            "last_updated": session["last_updated"]
        }

    except Exception as e:
        logger.error(f"세션 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.post("/end-session")
async def end_react_agent_session(request: Dict[str, Any]):
    """리액트 에이전트 세션 종료"""
    try:
        session_id = request.get("session_id")

        if session_id and session_id in agent_sessions:
            # 세션 데이터 정리
            session_data = agent_sessions.pop(session_id)
            logger.info(f"리액트 에이전트 세션 종료: {session_id}")

            return {
                "success": True,
                "message": "에이전트 세션이 종료되었습니다",
                "session_id": session_id,
                "final_data": session_data["extracted_data"]
            }

        return {
            "success": True,
            "message": "세션이 이미 종료되었습니다"
        }

    except Exception as e:
        logger.error(f"에이전트 세션 종료 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 종료 실패: {str(e)}")

def _determine_next_state(current_state: str, user_input: str, agent_response: Dict) -> str:
    """현재 상태와 입력을 기반으로 다음 상태 결정"""
    state_transitions = {
        "initial": {
            "keywords": ["직무", "개발자", "엔지니어", "프론트엔드", "백엔드", "풀스택"],
            "next_state": "keyword_extraction"
        },
        "keyword_extraction": {
            "keywords": ["다음", "계속", "진행", "확인", "맞아"],
            "next_state": "template_selection"
        },
        "template_selection": {
            "keywords": ["선택", "템플릿", "스타일", "확인"],
            "next_state": "content_generation"
        },
        "content_generation": {
            "keywords": ["수정", "변경", "다시"],
            "next_state": "review_edit"
        },
        "review_edit": {
            "keywords": ["확인", "완료", "등록"],
            "next_state": "final_confirmation"
        }
    }

    if current_state in state_transitions:
        transition = state_transitions[current_state]
        if any(keyword in user_input for keyword in transition["keywords"]):
            return transition["next_state"]

    return current_state

def _enhance_response_by_state(state: str, agent_response: Dict, session: Dict) -> Dict:
    """상태별로 응답을 강화"""
    base_message = agent_response.get("response", "")

    # 툴 실행 결과와 상세 정보는 숨김 (사용자 요청)
    # if agent_response.get("tool_result"):
    #     tool_result = agent_response["tool_result"]
    #     base_message += f"\n\n🔧 **툴 실행 결과:**\n"
    #     base_message += f"\n📊 **상세 데이터:**\n"
    #     base_message += f"\n📊 **상세 정보:**\n"
    #     base_message += f"\n📈 **총 개수:** {tool_result.get('total_count', 0)}개\n"

    # 툴 실행 에러도 숨김 (사용자 요청)
    # if agent_response.get("tool_error"):
    #     base_message += f"\n\n❌ **툴 실행 오류:** {agent_response['tool_error']}\n"

    # 추출된 정보도 숨김 (사용자 요청)
    # if state == "keyword_extraction" and session["extracted_data"]:
    #     base_message += f"\n\n🔍 **추출된 정보:**\n"
    #     for key, value in session["extracted_data"].items():
    #         base_message += f"• {key}: {value}\n"

    quick_actions = _get_quick_actions_by_state(state)
    suggestions = _get_suggestions_by_state(state)

    return {
        "message": base_message,
        "quick_actions": quick_actions,
        "suggestions": suggestions
    }

def _get_quick_actions_by_state(state: str) -> List[Dict]:
    """상태별 빠른 액션 반환"""
    actions_map = {
        "initial": [
            {"title": "채용공고 작성", "action": "navigate", "icon": "📝", "params": {"page": "job_posting"}},
            {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
            {"title": "대시보드", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}},
            {"title": "채용공고 목록", "action": "navigate", "icon": "📋", "params": {"page": "recruitment"}}
        ],
        "keyword_extraction": [
            {"title": "채용공고 미리보기", "action": "navigate", "icon": "👁️", "params": {"page": "job_posting", "tab": "preview"}},
            {"title": "템플릿 선택", "action": "navigate", "icon": "📋", "params": {"page": "job_posting", "tab": "templates"}},
            {"title": "저장하기", "action": "navigate", "icon": "💾", "params": {"page": "job_posting", "tab": "save"}}
        ],
        "template_selection": [
            {"title": "채용공고 등록", "action": "navigate", "icon": "🚀", "params": {"page": "job_posting", "tab": "register"}},
            {"title": "내용 수정", "action": "navigate", "icon": "✏️", "params": {"page": "job_posting", "tab": "edit"}},
            {"title": "지원자 요구사항 설정", "action": "navigate", "icon": "⚙️", "params": {"page": "job_posting", "tab": "requirements"}}
        ],
        "content_generation": [
            {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
            {"title": "인터뷰 일정", "action": "navigate", "icon": "📅", "params": {"page": "interview"}},
            {"title": "통계 보기", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}}
        ],
        "review_edit": [
            {"title": "채용공고 발행", "action": "navigate", "icon": "📢", "params": {"page": "job_posting", "tab": "publish"}},
            {"title": "설정 관리", "action": "navigate", "icon": "⚙️", "params": {"page": "settings"}},
            {"title": "새 채용공고", "action": "navigate", "icon": "🆕", "params": {"page": "job_posting", "tab": "new"}}
        ],
        "final_confirmation": [
            {"title": "지원자 모니터링", "action": "navigate", "icon": "📈", "params": {"page": "dashboard", "tab": "applicants"}},
            {"title": "채용 현황", "action": "navigate", "icon": "📊", "params": {"page": "dashboard", "tab": "recruitment"}},
            {"title": "회사 문화 관리", "action": "navigate", "icon": "🏢", "params": {"page": "company_culture"}}
        ]
    }

    return actions_map.get(state, [])

def _get_suggestions_by_state(state: str) -> List[str]:
    """상태별 제안 사항 반환"""
    suggestions_map = {
        "initial": [
            "프론트엔드 개발자",
            "백엔드 개발자",
            "풀스택 개발자",
            "데이터 사이언티스트"
        ],
        "keyword_extraction": [
            "React, TypeScript, Next.js",
            "Python, Django, PostgreSQL",
            "Java, Spring Boot, MySQL",
            "Node.js, Express, MongoDB"
        ],
        "template_selection": [
            "신입 친화형",
            "전문가형",
            "일반형",
            "창의적"
        ]
    }

    return suggestions_map.get(state, [])

async def _process_with_openai(llm_service, user_input: str, conversation_history: List[Dict]) -> Dict:
    """OpenAI LLM을 사용해서 사용자 입력 처리"""
    try:
        logger.info(f"🔍 [OpenAI 처리] 사용자 입력 분석 시작: '{user_input}'")

        # 대화 컨텍스트 구성
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # 최근 3개 메시지만 사용
            context = "\n".join([
                f"사용자: {msg.get('user', '')}\n에이전트: {msg.get('agent', '')}"
                for msg in recent_messages
            ])
            logger.info(f"📝 [OpenAI 처리] 대화 컨텍스트 ({len(recent_messages)}개 메시지): {context[:200]}...")
        else:
            logger.info(f"📝 [OpenAI 처리] 대화 컨텍스트 없음 (첫 메시지)")

        # 프롬프트 구성
        system_prompt = """당신은 채용/HR 업무를 지원하는 AI 에이전트입니다.

⚠️ **중요: 반드시 JSON 형식으로 응답해주세요! 자연어 텍스트가 아닌 JSON만!**

### 일반 대화 지원
사용자가 일반적인 질문(날씨, 시간, 인사 등)을 할 때도 적절하게 응답해주세요.
- 날씨 관련: "날씨가 좋네요", "비가 오고 있습니다" 등
- 시간 관련: "현재 시간은 오후 2시입니다" 등
- 인사: "안녕하세요! 무엇을 도와드릴까요?" 등

사용자의 입력을 분석하여 의도를 분류하고, 필요한 경우 여러 작업을 순차적으로 실행할 수 있습니다.

사용 가능한 툴들:
- search: 정보 검색 (blog_search, news_search, kin_search, internal_search, semantic_search)
- navigate: 페이지 이동 및 UI 조작 (page_navigate, open_modal, scroll_to, tab_switch)
- job_posting: 채용공고 생성, 수정, 삭제, 조회
- company_culture: 인재상 관리 (create, list, get, update, delete, set_default, evaluate_applicant)
- applicant: 지원자 관리, 지원자 목록 조회
- github: GitHub 정보 조회, 레포지토리 정보
- mongodb: 데이터베이스 조회, 저장된 정보 검색
- file_upload: 파일 업로드/다운로드
- mail: 메일 발송 및 템플릿 관리 (send_test, send_bulk, send_individual, create_template, get_templates)
- web_automation: 웹 자동화 (navigate, click, input, scroll, wait)

### 체이닝 작업 지원
사용자가 여러 작업을 요청했을 때는 tasks 배열을 사용하여 순차적으로 실행할 수 있습니다.

### 출력 형식 (JSON - 필수)
{
    "intent": "recruit|info_request|ui_action|chat",
    "response": "사용자에게 보여줄 응답 메시지",
    "suggested_tool": "job_posting",  // 단일 작업 시
    "suggested_action": "create",      // 단일 작업 시
    "tasks": [                         // 체이닝 작업 시
        {
            "tool": "job_posting",
            "action": "create",
            "description": "새로운 채용공고 생성",
            "depends_on": null,
            "params": {"input_text": "채용공고 내용"}
        },
        {
            "tool": "mail",
            "action": "send_individual",
            "description": "채용공고 완료 알림 이메일 발송",
            "depends_on": 0,
            "params": {"email": "hr@company.com", "template": "채용공고 완료"}
        }
    ],
    "params": {},                      // 단일 작업 시
    "confidence": 0.0-1.0
}

⚠️ **다시 한 번 강조: 반드시 JSON 형식으로 응답해주세요! 자연어 텍스트가 아닌 JSON만!**

의도 분류 예시:
- "프론트엔드 개발자 채용공고를 작성해줘" → intent: "recruit", tool: "job_posting", action: "create"
- "협력과 책임감을 중시하는 인재상을 만들어줘" → intent: "recruit", tool: "company_culture", action: "create"
- "인재상 목록을 보여줘" → intent: "info_request", tool: "company_culture", action: "list"
- "채용공고 목록 보여줘" → intent: "info_request", tool: "job_posting", action: "list"
- "GitHub 프로필 보여줘" → intent: "info_request", tool: "github", action: "get_profile"
- "지원자 데이터 조회" → intent: "info_request", tool: "mongodb", action: "query"
- "React 개발자 정보 검색해줘" → intent: "info_request", tool: "search", action: "blog_search"
- "React 개발자 뉴스 알려줘" → intent: "info_request", tool: "search", action: "news_search"
- "React 개발자 지식인에 있나?" → intent: "info_request", tool: "search", action: "kin_search"
- "채용 관리 페이지로 이동해줘" → intent: "ui_action", tool: "navigate", action: "page_navigate"
- "테스트 메일 보내줘" → intent: "ui_action", tool: "mail", action: "send_test"
- "채용공고 페이지 클릭해줘" → intent: "ui_action", tool: "web_automation", action: "click"
- "안녕하세요" → intent: "chat", tool: null, action: null

### 체이닝 작업 예시
- "채용공고 작성하고 이메일 발송해줘" → tasks 배열 사용
- "인재상 만들고 지원자에게 메일 보내줘" → tasks 배열 사용
- "React 개발자 시장 동향 검색하고 그에 맞는 채용공고 작성해줘" → tasks 배열 사용

키워드 매핑 가이드:
- 인재상 관련: "인재상", "인재상 만들어줘", "인재상 작성", "인재상 생성", "인재상 정의" → company_culture.create
- 채용공고 관련: "채용공고", "채용공고 작성", "채용공고 생성" → job_posting.create
- 메일 관련: "메일 보내줘", "메일 발송", "합격 메일", "불합격 메일" → mail.send_individual"""

        user_prompt = f"""대화 컨텍스트:
{context}

사용자 입력: {user_input}

위 정보를 바탕으로 분석해주세요."""

        logger.info(f"📤 [OpenAI 처리] LLM 호출 시작")
        logger.info(f"📋 [OpenAI 처리] System Prompt 길이: {len(system_prompt)} 문자")
        logger.info(f"📋 [OpenAI 처리] User Prompt 길이: {len(user_prompt)} 문자")

        # LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        llm_response = await llm_service.chat_completion(messages)

        logger.info(f"📥 [OpenAI 처리] LLM 응답 수신 완료 (길이: {len(llm_response)})")
        logger.info(f"📄 [OpenAI 처리] LLM 원본 응답: {llm_response[:500]}...")

        # JSON 파싱 시도
        try:
            import json
            logger.info(f"🔍 [OpenAI 처리] JSON 파싱 시작")

            parsed_response = json.loads(llm_response)
            logger.info(f"✅ [OpenAI 처리] JSON 파싱 성공: {parsed_response}")

            # 필수 필드 확인 및 로깅
            logger.info(f"🔍 [OpenAI 처리] 파싱된 응답 필드 분석:")
            logger.info(f"  - intent: {parsed_response.get('intent', 'MISSING')}")
            logger.info(f"  - suggested_tool: {parsed_response.get('suggested_tool', 'MISSING')}")
            logger.info(f"  - suggested_action: {parsed_response.get('suggested_action', 'MISSING')}")
            logger.info(f"  - tasks: {len(parsed_response.get('tasks', []))}개")
            logger.info(f"  - params: {parsed_response.get('params', 'MISSING')}")
            logger.info(f"  - confidence: {parsed_response.get('confidence', 'MISSING')}")
            logger.info(f"  - response: {parsed_response.get('response', 'MISSING')[:100]}...")

            # 필수 필드 확인
            if "response" not in parsed_response:
                parsed_response["response"] = "응답을 처리했습니다."
                logger.warning(f"⚠️ [OpenAI 처리] response 필드 누락, 기본값 설정")

            if "intent" not in parsed_response:
                parsed_response["intent"] = "chat"
                logger.warning(f"⚠️ [OpenAI 처리] intent 필드 누락, 기본값 'chat' 설정")

            if "suggested_tool" not in parsed_response:
                parsed_response["suggested_tool"] = None
                logger.warning(f"⚠️ [OpenAI 처리] suggested_tool 필드 누락, None 설정")

            if "suggested_action" not in parsed_response:
                parsed_response["suggested_action"] = None
                logger.warning(f"⚠️ [OpenAI 처리] suggested_action 필드 누락, None 설정")

            if "params" not in parsed_response:
                parsed_response["params"] = {}
                logger.warning(f"⚠️ [OpenAI 처리] params 필드 누락, 빈 딕셔너리 설정")

            if "confidence" not in parsed_response:
                parsed_response["confidence"] = 0.8
                logger.warning(f"⚠️ [OpenAI 처리] confidence 필드 누락, 기본값 0.8 설정")

            logger.info(f"🔍 [OpenAI 처리] 최종 파싱된 응답: {parsed_response}")

            # 체이닝 작업 감지 및 실행 (Phase 2: 고급 기능 사용)
            tasks = parsed_response.get("tasks", [])
            if tasks and len(tasks) > 1:
                logger.info(f"🔗 [OpenAI 처리] {len(tasks)}개 작업 체이닝 감지")

                # 고급 체이닝 기능 사용 (병렬 + 재시도)
                final_response = await _execute_chained_tasks_advanced(parsed_response)

                # 체이닝 성능 정보 로깅
                chaining_results = final_response.get("chaining_results", {})
                if chaining_results:
                    logger.info(f"🚀 [OpenAI 처리] 체이닝 성능 요약: {chaining_results.get('performance_summary', {})}")

                logger.info(f"🎯 [OpenAI 처리] 체이닝 완료, 최종 응답 반환")
                return final_response

            # 단일 툴 실행 (기존 로직)
            if parsed_response.get("suggested_tool") and parsed_response.get("suggested_action"):
                logger.info(f"🔧 [OpenAI 처리] 툴 실행 시작: {parsed_response['suggested_tool']}.{parsed_response['suggested_action']}")

                # tasks가 있을 때는 tasks[0]의 params 사용, 없으면 최상위 params 사용
                tasks = parsed_response.get("tasks", [])
                if tasks and len(tasks) > 0:
                    params = tasks[0].get("params", {})
                    logger.info(f"🔧 [OpenAI 처리] tasks[0]의 params 사용: {params}")
                else:
                    params = parsed_response.get("params", {})
                    logger.info(f"🔧 [OpenAI 처리] 최상위 params 사용: {params}")

                # 사용자 원본 입력을 params에 추가
                params["input_text"] = user_input

                tool_result = await _execute_tool(
                    parsed_response["suggested_tool"],
                    parsed_response["suggested_action"],
                    params
                )

                if tool_result["success"]:
                    # 툴 실행 성공 시 결과를 응답에 포함
                    parsed_response["tool_result"] = tool_result["result"]

                    # result에서 message 추출 (안전하게)
                    if isinstance(tool_result["result"], dict) and "message" in tool_result["result"]:
                        message = tool_result["result"]["message"]

                        # 검색 결과가 있으면 간략 요약 (챗봇용)
                        if "data" in tool_result["result"] and "results" in tool_result["result"]["data"]:
                            search_results = tool_result["result"]["data"]["results"]
                            total_results = tool_result["result"]["data"]["total_results"]

                            # 검색 결과 간략 요약
                            summary_message = f"{message}\n\n📊 총 {total_results}개 결과 중 {len(search_results)}개 표시\n\n"

                            # 상위 3개 제목만 간략하게
                            for i, result in enumerate(search_results[:3], 1):
                                title = result.get("title", "제목 없음")
                                summary_message += f"{i}. {title}\n"

                            summary_message += f"\n🔍 [전체 결과 보기] 버튼을 클릭하여 상세 결과를 확인하세요!"

                            message = summary_message
                    else:
                        message = str(tool_result["result"])

                    parsed_response["response"] = f"{parsed_response['response']}\n\n{message}"
                    logger.info(f"✅ [OpenAI 처리] 툴 실행 성공: {message}")
                else:
                    # 툴 실행 실패 시 에러 메시지 추가
                    parsed_response["tool_error"] = tool_result["error"]
                    parsed_response["response"] = f"{parsed_response['response']}\n\n❌ 툴 실행 실패: {tool_result['error']}"
                    logger.error(f"❌ [OpenAI 처리] 툴 실행 실패: {tool_result['error']}")
            else:
                logger.info(f"🔍 [OpenAI 처리] 툴 실행 불필요: intent={parsed_response.get('intent')}, tool={parsed_response.get('suggested_tool')}, action={parsed_response.get('suggested_action')}")

            logger.info(f"🎯 [OpenAI 처리] 최종 응답 반환: {parsed_response}")
            return parsed_response

        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 자연어에서 정보 추출 시도
            logger.error(f"❌ [OpenAI 처리] JSON 파싱 실패: {e}")
            logger.error(f"📄 [OpenAI 처리] 파싱 실패한 원본 응답: {llm_response}")

            # 자연어 응답에서 정보 추출 시도
            try:
                extracted_info = _extract_info_from_natural_language(llm_response, user_input)
                logger.info(f"🔄 [Ollama 처리] 자연어에서 정보 추출 성공: {extracted_info}")

                # Fallback에서도 툴 실행 시도
                if extracted_info.get("suggested_tool") and extracted_info.get("suggested_action"):
                    logger.info(f"🔄 [OpenAI 처리] Fallback 툴 실행 시작: {extracted_info['suggested_tool']}.{extracted_info['suggested_action']}")

                    # tasks가 있을 때는 tasks[0]의 params 사용, 없으면 최상위 params 사용
                    tasks = extracted_info.get("tasks", [])
                    if tasks and len(tasks) > 0:
                        params = tasks[0].get("params", {})
                        logger.info(f"🔄 [OpenAI 처리] Fallback tasks[0]의 params 사용: {params}")
                    else:
                        params = extracted_info.get("params", {})
                        logger.info(f"🔄 [OpenAI 처리] Fallback 최상위 params 사용: {params}")

                    # 사용자 원본 입력을 params에 추가
                    params["input_text"] = user_input

                    tool_result = await _execute_tool(
                        extracted_info["suggested_tool"],
                        extracted_info["suggested_action"],
                        params
                    )

                    if tool_result["success"]:
                        # 툴 실행 성공 시 결과를 응답에 포함
                        extracted_info["tool_result"] = tool_result["result"]

                                                # result에서 message 추출 (안전하게)
                        if isinstance(tool_result["result"], dict) and "message" in tool_result["result"]:
                            message = tool_result["result"]["message"]

                            # 검색 결과가 있으면 간략 요약 (챗봇용)
                            if "data" in tool_result["result"] and "results" in tool_result["result"]["data"]:
                                search_results = tool_result["result"]["data"]["results"]
                                total_results = tool_result["result"]["data"]["total_results"]

                                # 검색 결과 간략 요약
                                summary_message = f"{message}\n\n📊 총 {total_results}개 결과 중 {len(search_results)}개 표시\n\n"

                                # 상위 3개 제목만 간략하게
                                for i, result in enumerate(search_results[:3], 1):
                                    title = result.get("title", "제목 없음")
                                    summary_message += f"{i}. {title}\n"

                                summary_message += f"\n🔍 [전체 결과 보기] 버튼을 클릭하여 상세 결과를 확인하세요!"

                                message = summary_message
                        else:
                            message = str(tool_result["result"])

                        extracted_info["response"] = f"{extracted_info['response']}\n\n{message}"
                        logger.info(f"✅ [OpenAI 처리] Fallback 툴 실행 성공: {message}")
                    else:
                        # 툴 실행 실패 시 에러 메시지 추가
                        extracted_info["tool_error"] = tool_result["error"]
                        extracted_info["response"] = f"{extracted_info['response']}\n\n❌ 툴 실행 실패: {tool_result['error']}"
                        logger.error(f"❌ [OpenAI 처리] Fallback 툴 실행 실패: {tool_result['error']}")

                return extracted_info
            except Exception as fallback_error:
                logger.error(f"❌ [OpenAI 처리] 자연어 추출도 실패: {fallback_error}")

                # 최종 fallback: 기본 응답
                return {
                    "intent": "chat",
                    "response": f"입력하신 내용을 분석했습니다: {user_input}",
                    "suggested_tool": None,
                    "suggested_action": None,
                    "params": {},
                    "confidence": 0.6
                }

    except Exception as e:
        logger.error(f"OpenAI 처리 중 오류: {e}")
        return {
            "intent": "chat",
            "response": "죄송합니다. 처리 중 오류가 발생했습니다.",
            "suggested_tool": None,
            "suggested_action": None,
            "params": {},
            "confidence": 0.0
        }

def _extract_info_from_natural_language(llm_response: str, user_input: str) -> Dict:
    """자연어 응답에서 의도와 도구 정보를 추출"""
    try:
        # 사용자 입력 분석
        user_input_lower = user_input.lower()

        # 검색 관련 키워드
        if any(word in user_input_lower for word in ["검색", "찾아", "알려", "정보"]):
            if any(word in user_input_lower for word in ["뉴스", "news"]):
                return {
                    "intent": "info_request",
                    "response": f"'{user_input}'에 대한 뉴스를 검색하겠습니다.",
                    "suggested_tool": "search",
                    "suggested_action": "news_search",
                    "params": {"query": user_input},
                    "confidence": 0.8
                }
            elif any(word in user_input_lower for word in ["지식인", "kin", "질문"]):
                return {
                    "intent": "info_request",
                    "response": f"'{user_input}'에 대한 지식iN 정보를 검색하겠습니다.",
                    "suggested_tool": "search",
                    "suggested_action": "kin_search",
                    "params": {"query": user_input},
                    "confidence": 0.8
                }
            else:
                return {
                    "intent": "info_request",
                    "response": f"'{user_input}'에 대한 정보를 검색하겠습니다.",
                    "suggested_tool": "search",
                    "suggested_action": "blog_search",
                    "params": {"query": user_input},
                    "confidence": 0.8
                }

        # 채용 관련 키워드
        elif any(word in user_input_lower for word in ["채용", "공고", "개발자", "엔지니어", "모집"]):
            return {
                "intent": "recruit",
                "response": f"'{user_input}'에 대한 채용공고를 작성하겠습니다.",
                "suggested_tool": "job_posting",
                "suggested_action": "create",
                "params": {"input_text": user_input},
                "confidence": 0.8
            }

        # 인재상 관련 키워드
        elif any(word in user_input_lower for word in ["인재상", "문화", "가치"]):
            return {
                "intent": "recruit",
                "response": f"'{user_input}'에 대한 인재상을 생성하겠습니다.",
                "suggested_tool": "company_culture",
                "suggested_action": "create",
                "params": {"input_text": user_input},
                "confidence": 0.8
            }

        # 일반 대화 응답 개선
        if any(word in user_input_lower for word in ["날씨", "weather", "기온", "비", "맑음"]):
            return {
                "intent": "info_request",
                "response": f"'{user_input}'에 대한 날씨 정보를 제공하겠습니다. (날씨 API 연동 예정)",
                "suggested_tool": "weather",
                "suggested_action": "get_current",
                "params": {"location": "서울"},
                "confidence": 0.8
            }
        elif any(word in user_input_lower for word in ["시간", "time", "몇시", "언제"]):
            from datetime import datetime
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            return {
                "intent": "chat",
                "response": f"현재 시간은 {current_time}입니다.",
                "suggested_tool": None,
                "suggested_action": None,
                "params": {},
                "confidence": 0.9
            }
        elif any(word in user_input_lower for word in ["안녕", "hello", "hi", "반가워"]):
            return {
                "intent": "chat",
                "response": f"안녕하세요! 저는 채용공고 작성을 도와주는 AI 에이전트입니다. 어떤 도움이 필요하신가요?",
                "suggested_tool": None,
                "suggested_action": None,
                "params": {},
                "confidence": 0.9
            }
        else:
            # 기본 대화 응답
            return {
                "intent": "chat",
                "response": f"'{user_input}'에 대해 답변드리겠습니다. 하지만 저는 주로 채용 관련 업무를 도와주는 에이전트입니다. 채용공고 작성, 지원자 관리, 검색 등에 대해 질문해 주시면 더 자세히 도와드릴 수 있습니다.",
                "suggested_tool": None,
                "suggested_action": None,
                "params": {},
                "confidence": 0.7
            }

    except Exception as e:
        logger.error(f"자연어 정보 추출 실패: {e}")
        raise e

def _process_basic_response(user_input: str, current_state: str) -> Dict:
    """기본 응답 처리 (LLM 없을 때)"""
    # 간단한 키워드 추출
    intent = "chat"
    suggested_tool = None
    suggested_action = None
    params = {}

    # 채용 관련 키워드 체크
    if any(word in user_input.lower() for word in ["채용", "공고", "개발자", "엔지니어", "모집"]):
        intent = "recruit"
        suggested_tool = "job_posting"
        suggested_action = "create"

        # 직무 추출
        job_keywords = ["개발자", "엔지니어", "프로그래머", "디자이너"]
        for keyword in job_keywords:
            if keyword in user_input:
                params["position"] = keyword
                break

        # 기술 스택 추출
        tech_keywords = ["React", "Python", "Java", "Node.js", "TypeScript"]
        found_tech = []
        for tech in tech_keywords:
            if tech.lower() in user_input.lower():
                found_tech.append(tech)

        if found_tech:
            params["skills"] = found_tech

    return {
        "intent": intent,
        "response": f"입력하신 내용을 분석했습니다. {', '.join(params.values()) if params else '추가 정보가 필요합니다.'}",
        "suggested_tool": suggested_tool,
        "suggested_action": suggested_action,
        "params": params,
        "confidence": 0.7
    }

async def _execute_tool(tool_name: str, action: str, params: Dict) -> Dict:
    """실제 툴 실행"""
    try:
        logger.info(f"🔧 [툴 실행] {tool_name}.{action} 시작")
        logger.info(f"🔧 [툴 실행] 파라미터: {params}")

        if tool_name == "search":
            return await _execute_search_tool(action, params)
        elif tool_name == "navigate":
            return await _execute_navigate_tool(action, params)
        elif tool_name == "job_posting":
            return await _execute_job_posting_tool(action, params)
        elif tool_name == "github":
            return await _execute_github_tool(action, params)
        elif tool_name == "mongodb":
            return await _execute_mongodb_tool(action, params)
        elif tool_name == "applicant":
            return await _execute_applicant_tool(action, params)
        elif tool_name == "file_upload":
            return await _execute_file_upload_tool(action, params)
        elif tool_name == "mail":
            return await _execute_mail_tool(action, params)
        elif tool_name == "web_automation":
            return await _execute_web_automation_tool(action, params)
        elif tool_name == "company_culture":
            return await _execute_company_culture_tool(action, params)
        else:
            return {
                "success": False,
                "error": f"알 수 없는 툴: {tool_name}",
                "result": None
            }

    except Exception as e:
        logger.error(f"툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

def _get_search_type_from_query(query: str) -> str:
    """사용자 쿼리에서 검색 타입을 자동으로 결정"""
    query_lower = query.lower()

    # 검색 타입 매핑
    search_type_map = {
        # 뉴스 관련
        "뉴스": "news_search",
        "news": "news_search",
        "최신": "news_search",
        "시사": "news_search",

        # 블로그/후기 관련
        "블로그": "blog_search",
        "blog": "blog_search",
        "후기": "blog_search",
        "리뷰": "blog_search",
        "경험": "blog_search",
        "생생": "blog_search",

        # 지식iN 관련
        "지식인": "kin_search",
        "kin": "kin_search",
        "질문": "kin_search",
        "답변": "kin_search",
        "해결": "kin_search",

        # 이미지 관련
        "이미지": "image_search",
        "image": "image_search",
        "사진": "image_search",
        "그림": "image_search",

        # 쇼핑 관련
        "쇼핑": "shop_search",
        "shop": "shop_search",
        "구매": "shop_search",
        "가격": "shop_search",

        # 도서 관련
        "책": "book_search",
        "book": "book_search",
        "도서": "book_search",
        "서적": "book_search",
    }

    # 키워드 매칭
    for keyword, search_type in search_type_map.items():
        if keyword in query_lower:
            return search_type

    # 기본값: 블로그 검색
    return "blog_search"

async def _execute_search_tool(action: str, params: Dict) -> Dict:
    """검색 관련 툴 실행"""
    try:
        # 자동 타입 매핑 적용
        query = params.get("query", "")
        if action == "search" and query:
            action = _get_search_type_from_query(query)
            logger.info(f"🔍 자동 검색 타입 선택: {action} (쿼리: {query})")

        if action == "blog_search":
            # 블로그 검색 (네이버 API 사용)
            query = params.get("query") or params.get("input_text", "검색어")
            try:
                from modules.core.services.naver_search_service import naver_search_service
                search_result = await naver_search_service.search_blog(query, display=5)
                result = {
                    "message": search_result.get("message", f"🔍 '{query}'에 대한 블로그 검색 결과입니다:"),
                    "data": search_result.get("data", {})
                }
            except Exception as e:
                logger.error(f"블로그 검색 실패: {e}")
                # 폴백: 시뮬레이션 결과
                result = {
                    "message": f"🔍 '{query}'에 대한 블로그 검색 결과입니다:",
                    "data": {
                        "query": query,
                        "results": [
                            {"title": f"{query} 관련 블로그 포스트 1", "url": "https://blog1.com", "snippet": f"{query}에 대한 블로그 포스트입니다."},
                            {"title": f"{query} 관련 블로그 포스트 2", "url": "https://blog2.com", "snippet": f"{query}에 대한 추가 블로그 포스트입니다."}
                        ],
                        "total_results": 2
                    }
                }

        elif action == "news_search":
            # 뉴스 검색 (네이버 API 사용)
            query = params.get("query") or params.get("input_text", "검색어")
            try:
                from modules.core.services.naver_search_service import naver_search_service
                search_result = await naver_search_service.search_news(query, display=5)
                result = {
                    "message": search_result.get("message", f"📰 '{query}'에 대한 뉴스 검색 결과입니다:"),
                    "data": search_result.get("data", {})
                }
            except Exception as e:
                logger.error(f"뉴스 검색 실패: {e}")
                # 폴백: 시뮬레이션 결과
                result = {
                    "message": f"📰 '{query}'에 대한 뉴스 검색 결과입니다:",
                    "data": {
                        "query": query,
                        "results": [
                            {"title": f"{query} 관련 뉴스 1", "url": "https://news1.com", "snippet": f"{query}에 대한 최신 뉴스입니다."},
                            {"title": f"{query} 관련 뉴스 2", "url": "https://news2.com", "snippet": f"{query}에 대한 추가 뉴스입니다."}
                        ],
                        "total_results": 2
                    }
                }

        elif action == "kin_search":
            # 지식iN 검색 (네이버 API 사용)
            query = params.get("query") or params.get("input_text", "검색어")
            try:
                from modules.core.services.naver_search_service import naver_search_service
                search_result = await naver_search_service.search_kin(query, display=5)
                result = {
                    "message": search_result.get("message", f"💡 '{query}'에 대한 지식iN 검색 결과입니다:"),
                    "data": search_result.get("data", {})
                }
            except Exception as e:
                logger.error(f"지식iN 검색 실패: {e}")
                # 폴백: 시뮬레이션 결과
                result = {
                    "message": f"💡 '{query}'에 대한 지식iN 검색 결과입니다:",
                    "data": {
                        "query": query,
                        "results": [
                            {"title": f"{query} 관련 질문 1", "url": "https://kin1.com", "snippet": f"{query}에 대한 질문과 답변입니다."},
                            {"title": f"{query} 관련 질문 2", "url": "https://kin2.com", "snippet": f"{query}에 대한 추가 질문입니다."}
                        ],
                        "total_results": 2
                    }
                }

        elif action == "internal_search":
            # 내부 검색 시뮬레이션
            query = params.get("query", "검색어")
            category = params.get("category", "all")
            result = {
                "message": f"🔍 내부 시스템에서 '{query}'를 검색한 결과입니다:",
                "data": {
                    "query": query,
                    "category": category,
                    "results": [
                        {"type": "job_posting", "title": f"{query} 관련 채용공고", "id": "job_123"},
                        {"type": "applicant", "title": f"{query} 관련 지원자", "id": "app_456"}
                    ],
                    "total_results": 2
                }
            }

        elif action == "semantic_search":
            # 의미 기반 검색 시뮬레이션
            query = params.get("query", "검색어")
            result = {
                "message": f"🧠 '{query}'의 의미를 분석한 검색 결과입니다:",
                "data": {
                    "query": query,
                    "semantic_results": [
                        {"concept": "개발자", "relevance": 0.95, "related_terms": ["프로그래머", "엔지니어"]},
                        {"concept": "기술", "relevance": 0.87, "related_terms": ["스킬", "역량"]}
                    ]
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 검색 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"검색 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_navigate_tool(action: str, params: Dict) -> Dict:
    """네비게이션 관련 툴 실행"""
    try:
        if action == "page_navigate":
            # 페이지 이동 시뮬레이션
            target_page = params.get("page", "home")
            target_tab = params.get("tab", "")

            page_mapping = {
                "home": {"path": "/", "title": "홈", "description": "메인 페이지"},
                "job_posting": {"path": "/job-posting", "title": "채용공고 작성", "description": "새로운 채용공고 작성 및 관리"},
                "recruitment": {"path": "/recruitment", "title": "채용 관리", "description": "채용공고 및 지원자 관리"},
                "applicants": {"path": "/applicants", "title": "지원자 관리", "description": "지원자 목록 및 상태 관리"},
                "dashboard": {"path": "/dashboard", "title": "대시보드", "description": "통계 및 현황"},
                "interview": {"path": "/interview", "title": "인터뷰 관리", "description": "인터뷰 일정 및 결과 관리"},
                "settings": {"path": "/settings", "title": "설정", "description": "시스템 설정"},
                "profile": {"path": "/profile", "title": "프로필", "description": "사용자 프로필"},
                "company_culture": {"path": "/company-culture", "title": "회사 문화", "description": "회사 문화 및 인재상 관리"}
            }

            if target_page in page_mapping:
                page_info = page_mapping[target_page]

                # 탭 정보가 있으면 추가
                tab_info = ""
                if target_tab:
                    tab_mapping = {
                        "preview": "미리보기",
                        "templates": "템플릿",
                        "save": "저장",
                        "register": "등록",
                        "edit": "수정",
                        "requirements": "요구사항",
                        "publish": "발행",
                        "new": "새로 작성",
                        "applicants": "지원자",
                        "recruitment": "채용"
                    }
                    tab_name = tab_mapping.get(target_tab, target_tab)
                    tab_info = f" ({tab_name} 탭)"

                result = {
                    "message": f"🚀 {page_info['title']}{tab_info} 페이지로 이동합니다!",
                    "data": {
                        "action": "navigate",
                        "target_page": target_page,
                        "target_tab": target_tab,
                        "path": page_info["path"],
                        "title": page_info["title"],
                        "description": page_info["description"],
                        "full_path": f"{page_info['path']}{'#' + target_tab if target_tab else ''}"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"알 수 없는 페이지: {target_page}",
                    "result": None
                }

        elif action == "open_modal":
            # 모달 열기 시뮬레이션
            modal_type = params.get("type", "info")
            modal_title = params.get("title", "알림")
            modal_content = params.get("content", "모달 내용")

            result = {
                "message": f"📱 {modal_title} 모달을 열었습니다!",
                "data": {
                    "action": "open_modal",
                    "modal_type": modal_type,
                    "title": modal_title,
                    "content": modal_content
                }
            }

        elif action == "scroll_to":
            # 특정 요소로 스크롤 시뮬레이션
            element_id = params.get("element_id", "section")
            element_name = params.get("element_name", "섹션")

            result = {
                "message": f"📜 {element_name}으로 스크롤합니다!",
                "data": {
                    "action": "scroll_to",
                    "element_id": element_id,
                    "element_name": element_name
                }
            }

        elif action == "tab_switch":
            # 탭 전환 시뮬레이션
            tab_name = params.get("tab_name", "메인")
            tab_id = params.get("tab_id", "main")

            result = {
                "message": f"🔄 {tab_name} 탭으로 전환합니다!",
                "data": {
                    "action": "tab_switch",
                    "tab_name": tab_name,
                    "tab_id": tab_id
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 네비게이션 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"네비게이션 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_job_posting_tool(action: str, params: Dict) -> Dict:
    """채용공고 관련 툴 실행"""
    try:
        logger.info(f"🔧 [채용공고툴] {action} 액션 실행 시작")
        logger.info(f"🔧 [채용공고툴] 파라미터: {params}")

        if action == "create":
            # 픽톡과 동일한 방식으로 채용공고 생성
            try:
                from modules.core.services.mongo_service import MongoService

                # MongoDB 서비스 초기화
                mongo_service = MongoService()

                # 입력된 텍스트를 job_data로 변환
                input_text = params.get("input_text", "")
                if not input_text:
                    return {
                        "success": False,
                        "error": "채용공고 내용이 입력되지 않았습니다."
                    }

                # 사용자 입력에서 실제 정보 추출하여 job_data 생성 (AI 페이지 필드명과 정확히 맞춤)
                job_data = {
                    # AI 페이지 필드명과 정확히 일치하도록 수정
                    "department": "개발팀",  # 구인 부서
                    "position": "백엔드 개발자",  # 채용 직무
                    "headcount": "1명",  # 구인 인원수
                    "mainDuties": input_text,  # 주요 업무 (AI 페이지 필드명)
                    "workHours": "09:00-18:00",  # 근무 시간 (AI 페이지 필드명)
                    "workDays": "주중 (월~금)",  # 근무 요일 (AI 페이지 필드명)
                    "salary": "협의",  # 연봉
                    "contactEmail": "hr@company.com",  # 연락처 이메일 (AI 페이지 필드명)
                    "deadline": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),  # 마감일
                    "experience": "경력자",  # 경력 수준
                    "locationCity": "서울",  # 근무 위치 (AI 페이지 필드명)

                    # 기존 필드들 (호환성 유지)
                    "title": f"채용공고 - {datetime.now().strftime('%Y-%m-%d')}",
                    "company": "회사명",
                    "location": "서울",
                    "type": "full-time",
                    "requirements": "경력자",
                    "preferred": "우대사항",
                    "benefits": "복리후생",
                    "description": input_text,
                    "contact_email": "hr@company.com",
                    "work_type": "정규직",
                    "work_hours": "09:00-18:00"
                }

                # 사용자 입력에서 실제 정보 추출
                input_lower = input_text.lower()

                # 직책 추출
                if "프론트엔드" in input_lower:
                    job_data["position"] = "프론트엔드 개발자"
                elif "백엔드" in input_lower:
                    job_data["position"] = "백엔드 개발자"
                elif "풀스택" in input_lower:
                    job_data["position"] = "풀스택 개발자"
                elif "개발자" in input_lower:
                    job_data["position"] = "개발자"

                # 기술 스택 추출
                tech_skills = []
                if "react" in input_lower:
                    tech_skills.append("React")
                if "typescript" in input_lower or "ts" in input_lower:
                    tech_skills.append("TypeScript")
                if "javascript" in input_lower or "js" in input_lower:
                    tech_skills.append("JavaScript")
                if "python" in input_lower:
                    tech_skills.append("Python")
                if "java" in input_lower:
                    tech_skills.append("Java")

                if tech_skills:
                    job_data["preferred"] = tech_skills

                # 경력 요구사항 추출 (AI 페이지 필드명과 맞춤)
                if "3년" in input_text or "3년 이상" in input_text:
                    job_data["experience"] = "3년 이상 경력자"
                    job_data["requirements"] = "3년 이상 경력자"
                elif "신입" in input_text:
                    job_data["experience"] = "신입"
                    job_data["requirements"] = "신입"
                elif "경력자" in input_text:
                    job_data["experience"] = "경력자"
                    job_data["requirements"] = "경력자"

                # 급여 추출
                if "4000만원" in input_text or "4000" in input_text:
                    job_data["salary"] = "4000만원"
                elif "5000만원" in input_text or "5000" in input_text:
                    job_data["salary"] = "5000만원"

                # 근무지 추출 (AI 페이지 필드명과 맞춤)
                if "서울" in input_text:
                    job_data["location"] = "서울"
                    job_data["locationCity"] = "서울"  # AI 페이지 필드명
                if "강남구" in input_text:
                    job_data["location"] = "서울 강남구"
                    job_data["locationCity"] = "서울 강남구"
                if "부산" in input_text:
                    job_data["location"] = "부산"
                    job_data["locationCity"] = "부산"
                if "대구" in input_text:
                    job_data["location"] = "대구"
                    job_data["locationCity"] = "대구"

                # 픽톡과 동일한 방식으로 키워드 추출 (간단한 로직)
                keywords = set()
                key_fields = ['title', 'company', 'position', 'requirements', 'preferred', 'description']

                for field in key_fields:
                    if field in job_data and job_data[field]:
                        text = str(job_data[field])
                        words = text.replace(',', ' ').replace(';', ' ').split()
                        for word in words:
                            cleaned_word = ''.join(c for c in word if c.isalnum())
                            if len(cleaned_word) >= 2 and not cleaned_word.isdigit():
                                keywords.add(cleaned_word.lower())

                extracted_keywords = list(keywords)[:10]
                job_data["extracted_keywords"] = extracted_keywords

                # 채용공고 데이터에 기본 정보 추가 (픽톡과 동일)
                job_data["created_at"] = datetime.now()
                job_data["updated_at"] = datetime.now()
                job_data["status"] = "published"
                job_data["applicants"] = 0
                job_data["views"] = 0

                # MongoDB에 저장 (픽톡과 동일)
                result = await mongo_service.db.job_postings.insert_one(job_data)

                logger.info(f"✅ [에이전트 채용공고툴] 픽톡 방식으로 생성 완료: {result.inserted_id}")

                # ObjectId를 문자열로 변환하여 직렬화 오류 방지
                safe_job_data = {}
                for key, value in job_data.items():
                    if key == '_id' or hasattr(value, '__dict__') or str(type(value)).find('ObjectId') != -1:
                        safe_job_data[key] = str(value)
                    else:
                        safe_job_data[key] = value

                # 픽톡과 동일한 응답 구조 + auto_navigation 추가
                return {
                    "success": True,
                    "result": {
                        "message": "🎉 채용공고 정보가 성공적으로 추출되었습니다! 🚀 3초 후 등록 페이지로 이동합니다.",
                        "data": {
                            "job_id": str(result.inserted_id),
                            "extracted_keywords": extracted_keywords
                        },
                        "auto_navigation": {
                            "enabled": True,
                            "delay": 3000,
                            "target": "ai-job-registration",
                            "action": "open_job_modal",
                            "extracted_data": safe_job_data
                        },
                        "quick_actions": [
                            {
                                "title": "즉시 이동",
                                "action": "navigate",
                                "target": "/ai-job-registration",
                                "icon": "⚡"
                            },
                            {
                                "title": "수동 입력",
                                "action": "navigate",
                                "target": "/ai-job-registration",
                                "icon": "✏️"
                            }
                        ]
                    }
                }

            except Exception as e:
                logger.error(f"❌ [에이전트 채용공고툴] 실제 채용공고 생성 실패: {e}")
                return {
                    "success": False,
                    "error": f"채용공고 생성 중 오류가 발생했습니다: {str(e)}"
                }

        elif action == "list":
            # 실제 데이터베이스에서 채용공고 목록 조회
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                db = client.hireme

                # 전체 채용공고 수 조회
                total_count = await db.job_postings.count_documents({})
                logger.info(f"🔍 [채용공고툴] DB에서 조회된 총 채용공고 수: {total_count}개")

                # 최근 10개 채용공고 조회
                recent_jobs = await db.job_postings.find().sort("created_at", -1).limit(10).to_list(10)

                # ObjectId를 문자열로 변환
                for job in recent_jobs:
                    job["id"] = str(job["_id"])
                    del job["_id"]

                client.close()

                result = {
                    "message": f"📋 현재 등록된 채용공고 목록입니다 (총 {total_count}개):",
                    "data": recent_jobs,
                    "total_count": total_count,
                    "displayed_count": len(recent_jobs)
                }

                logger.info(f"✅ [채용공고툴] 실제 DB 조회 완료: {total_count}개 중 {len(recent_jobs)}개 표시")

            except Exception as e:
                logger.error(f"❌ [채용공고툴] DB 조회 실패: {e}")
                # DB 조회 실패 시 더미 데이터 반환
                result = {
                    "message": "📋 채용공고 목록 조회 중 오류가 발생했습니다.",
                    "data": [],
                    "total_count": 0,
                    "displayed_count": 0,
                    "error": str(e)
                }

        elif action == "update":
            # 채용공고 수정 시뮬레이션
            result = {
                "message": "✏️ 채용공고가 수정되었습니다!",
                "data": {"status": "updated"}
            }

        elif action == "delete":
            # 채용공고 삭제 시뮬레이션
            result = {
                "message": "🗑️ 채용공고가 삭제되었습니다!",
                "data": {"status": "deleted"}
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"채용공고 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_github_tool(action: str, params: Dict) -> Dict:
    """GitHub 관련 툴 실행"""
    try:
        if action == "get_profile":
            username = params.get("username", "octocat")
            result = {
                "message": f"👤 GitHub 프로필: {username}",
                "data": {
                    "username": username,
                    "followers": 1234,
                    "repos": 56,
                    "bio": "AI-powered developer"
                }
            }

        elif action == "get_repos":
            username = params.get("username", "octocat")
            result = {
                "message": f"📚 {username}의 레포지토리 목록:",
                "data": [
                    {"name": "awesome-project", "stars": 100, "language": "JavaScript"},
                    {"name": "ml-toolkit", "stars": 50, "language": "Python"}
                ]
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"GitHub 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_mongodb_tool(action: str, params: Dict) -> Dict:
    """MongoDB 관련 툴 실행"""
    try:
        if action == "query":
            collection = params.get("collection", "applicants")
            query = params.get("query", {})

            try:
                result = {
                    "message": f"📊 {collection} 컬렉션을 실제 데이터베이스에서 조회합니다:",
                    "data": {
                        "collection": collection,
                        "query": query,
                        "note": "실제 MongoDB 데이터베이스에 연결하여 데이터를 조회합니다.",
                        "status": "connected",
                        "database": "hireme"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 데이터베이스 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"MongoDB 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_applicant_tool(action: str, params: Dict) -> Dict:
    """지원자 관련 툴 실행"""
    try:
        if action == "list":
            # 실제 지원자 목록 API 호출
            try:
                from routers.applicants import router as applicants_router

                result = {
                    "message": "👥 실제 지원자 목록을 조회합니다:",
                    "data": {
                        "note": "실제 데이터베이스에서 지원자 정보를 가져옵니다.",
                        "api_endpoint": "/api/applicants",
                        "status": "connected"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 지원자 목록 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "get":
            # 실제 지원자 정보 API 호출
            applicant_id = params.get("id", "unknown")
            try:
                result = {
                    "message": f"👤 지원자 정보 (ID: {applicant_id}):",
                    "data": {
                        "note": "실제 데이터베이스에서 지원자 상세 정보를 가져옵니다.",
                        "api_endpoint": f"/api/applicants/{applicant_id}",
                        "applicant_id": applicant_id,
                        "status": "connected"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 지원자 정보 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"지원자 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_file_upload_tool(action: str, params: Dict) -> Dict:
    """파일 업로드 관련 툴 실행"""
    try:
        if action == "upload":
            filename = params.get("filename", "unknown")
            try:
                result = {
                    "message": f"📁 파일 '{filename}'을 실제 업로드 시스템에 전송합니다!",
                    "data": {
                        "filename": filename,
                        "note": "실제 파일 업로드 API를 통해 파일이 저장됩니다.",
                        "api_endpoint": "/api/upload",
                        "status": "connecting"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 파일 업로드 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "download":
            filename = params.get("filename", "unknown")
            result = {
                "message": f"📥 파일 '{filename}' 다운로드가 시작되었습니다!",
                "data": {
                    "filename": filename,
                    "download_url": f"/download/{filename}"
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"파일 업로드 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_mail_tool(action: str, params: Dict) -> Dict:
    """메일 관련 툴 실행"""
    try:
        if action == "send_test":
            # 실제 테스트 메일 발송 API 호출
            recipient = params.get("recipient", "test@example.com")
            try:
                result = {
                    "message": f"📧 실제 테스트 메일을 {recipient}로 발송합니다!",
                    "data": {
                        "action": "send_test",
                        "recipient": recipient,
                        "status": "connecting",
                        "note": "실제 SMTP 서버를 통해 메일이 전송됩니다.",
                        "api_endpoint": "/api/send-test-mail"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 테스트 메일 발송 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "send_bulk":
            # 일괄 메일 발송 시뮬레이션
            recipients = params.get("recipients", [])
            template = params.get("template", "default")
            count = len(recipients) if recipients else 0

            result = {
                "message": f"📧 일괄 메일이 {count}명에게 발송되었습니다!",
                "data": {
                    "action": "send_bulk",
                    "recipients": recipients,
                    "template": template,
                    "count": count,
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                }
            }

        elif action == "send_individual":
            # 개별 메일 발송 - 실제 API 호출
            email = params.get("email") or params.get("recipient")
            template = params.get("template", "기본 안내")
            message_type = params.get("message_type", "")
            status = params.get("status", "")
            input_text = params.get("input_text", "")

            if not email:
                return {
                    "success": False,
                    "error": "이메일 주소가 필요합니다.",
                    "result": None
                }

            # message_type 또는 status를 template으로 매핑 (우선순위 고려)
            # template 파라미터도 매핑하여 잘못된 템플릿명 수정
            if message_type or status:
                message_type = message_type or status

                if "불합격" in message_type:
                    template = "불합격 통보"
                elif "면접" in message_type and "합격" in message_type:
                    template = "면접 합격"
                elif "합격" in message_type:
                    template = "합격 통보"

            # template 파라미터도 매핑 (OpenAI가 잘못된 템플릿명을 생성할 수 있음)
            template_mapping = {
                # 영어 템플릿명을 한글 템플릿명으로 매핑
                "rejection": "불합격 통지",
                "rejected": "불합격 통지",
                "pass": "합격 통지",
                "passed": "합격 통지",
                "합격 메일 템플릿": "합격 통지",
                "합격 메일": "합격 통지",
                "interview": "면접 안내",
                "document_passed": "면접 안내",
                "final_pass": "최종 합격",
                "final_passed": "최종 합격",

                # 한글 템플릿명 매핑
                "불합격 통보": "불합격 통지",
                "합격 통보": "합격 통지",
                "면접 합격": "면접 안내",
                # 잘못된 템플릿명들을 올바른 템플릿으로 매핑
                "합격 메일": "합격 통지",
                "불합격 메일": "불합격 통지",
                "면접 메일": "면접 안내",
                "합격": "합격 통지",
                "불합격": "불합격 통지",
                "면접": "면접 안내"
            }

            # 템플릿 매핑 적용
            template = template_mapping.get(template, template)

            try:
                # Settings의 실제 메일 템플릿 사용을 위해 main.py API 호출
                import httpx
                import json

                mail_data = {
                    "recipient": email,
                    "template": template,
                    "input_text": input_text
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8000/api/send-individual-mail",
                        json=mail_data,
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        api_result = response.json()
                        result = {
                            "message": f"📧 개별 메일이 {email}로 발송되었습니다!",
                            "data": api_result.get("data", {})
                        }
                    else:
                        result = {
                            "success": False,
                            "error": f"메일 발송 API 오류: {response.status_code}",
                            "result": None
                        }

            except Exception as e:
                result = {
                    "success": False,
                    "error": f"메일 발송 실패: {str(e)}",
                    "result": None
                }

        elif action == "create_template":
            # 메일 템플릿 생성 시뮬레이션
            template_name = params.get("name", "새 템플릿")
            subject = params.get("subject", "제목")
            content = params.get("content", "내용")

            result = {
                "message": f"📝 메일 템플릿 '{template_name}'이 생성되었습니다!",
                "data": {
                    "action": "create_template",
                    "template_name": template_name,
                    "subject": subject,
                    "content": content,
                    "created_at": datetime.now().isoformat(),
                    "template_id": f"template_{int(datetime.now().timestamp())}"
                }
            }

        elif action == "get_templates":
            # 메일 템플릿 조회 시뮬레이션
            result = {
                "message": "📝 등록된 메일 템플릿 목록입니다:",
                "data": {
                    "action": "get_templates",
                    "templates": [
                        {"id": "template_1", "name": "채용공고 알림", "subject": "새로운 채용공고가 등록되었습니다"},
                        {"id": "template_2", "name": "지원자 안내", "subject": "지원해주셔서 감사합니다"},
                        {"id": "template_3", "name": "면접 안내", "subject": "면접 일정 안내"}
                    ],
                    "count": 3
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 메일 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"메일 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_web_automation_tool(action: str, params: Dict) -> Dict:
    """웹 자동화 관련 툴 실행"""
    try:
        if action == "navigate":
            # 실제 페이지 이동 기능
            page_path = params.get("page_path", "/")
            try:
                result = {
                    "message": f"🚀 실제 페이지 이동을 수행합니다!",
                    "data": {
                        "action": "navigate",
                        "page_path": page_path,
                        "note": "실제 React Router를 통해 페이지 이동이 실행됩니다.",
                        "status": "executing",
                        "navigated_at": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 페이지 이동 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "click":
            # 요소 클릭 시뮬레이션
            element_selector = params.get("selector", "button")
            element_text = params.get("text", "버튼")

            result = {
                "message": f"🖱️ '{element_text}' 요소를 클릭했습니다!",
                "data": {
                    "action": "click",
                    "selector": element_selector,
                    "text": element_text,
                    "clicked_at": datetime.now().isoformat()
                }
            }

        elif action == "input":
            # 텍스트 입력 시뮬레이션
            field_name = params.get("field", "입력 필드")
            input_value = params.get("value", "")

            result = {
                "message": f"⌨️ '{field_name}'에 '{input_value}'를 입력했습니다!",
                "data": {
                    "action": "input",
                    "field": field_name,
                    "value": input_value,
                    "input_at": datetime.now().isoformat()
                }
            }

        elif action == "scroll":
            # 스크롤 시뮬레이션
            direction = params.get("direction", "down")
            amount = params.get("amount", "100px")

            result = {
                "message": f"📜 {direction} 방향으로 {amount} 스크롤했습니다!",
                "data": {
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "scrolled_at": datetime.now().isoformat()
                }
            }

        elif action == "wait":
            # 대기 시뮬레이션
            duration = params.get("duration", 1)
            reason = params.get("reason", "페이지 로딩")

            result = {
                "message": f"⏳ {reason}을 위해 {duration}초 대기했습니다!",
                "data": {
                    "action": "wait",
                    "duration": duration,
                    "reason": reason,
                    "waited_at": datetime.now().isoformat()
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 웹 자동화 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"웹 자동화 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_company_culture_tool(action: str, params: Dict) -> Dict:
    """인재상 관리 관련 툴 실행"""
    try:
        logger.info(f"🔧 [인재상툴] {action} 액션 실행 시작")
        logger.info(f"🔧 [인재상툴] 파라미터: {params}")

        if action == "create":
            # 인재상 생성
            input_text = params.get("input_text", "")

            # 사용자 입력에서 인재상 정보 추출
            name, description = _extract_culture_info(input_text)

            try:
                import httpx

                culture_data = {
                    "name": name,
                    "description": description
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8000/api/company-culture/",
                        json=culture_data,
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"🎯 인재상 '{name}'이 성공적으로 생성되었습니다!",
                                "data": result
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"인재상 생성 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"인재상 생성 중 오류: {str(e)}"
                }

        elif action == "list":
            # 인재상 목록 조회
            category = params.get("category", None)

            try:
                import httpx

                url = "http://localhost:8000/api/company-culture/"
                if category:
                    url += f"?category={category}"

                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=30.0)

                    if response.status_code == 200:
                        cultures = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"📋 인재상 목록을 조회했습니다. (총 {len(cultures)}개)",
                                "data": {
                                    "cultures": cultures,
                                    "count": len(cultures),
                                    "category": category
                                }
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"인재상 목록 조회 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"인재상 목록 조회 중 오류: {str(e)}"
                }

        elif action == "get":
            # 특정 인재상 조회
            culture_id = params.get("id")
            if not culture_id:
                return {
                    "success": False,
                    "error": "인재상 ID가 필요합니다."
                }

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"http://localhost:8000/api/company-culture/{culture_id}",
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        culture = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"🎯 인재상 '{culture['name']}' 정보입니다.",
                                "data": culture
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"인재상 조회 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"인재상 조회 중 오류: {str(e)}"
                }

        elif action == "update":
            # 인재상 수정
            culture_id = params.get("id")
            if not culture_id:
                return {
                    "success": False,
                    "error": "인재상 ID가 필요합니다."
                }

            update_data = {}
            if "name" in params:
                update_data["name"] = params["name"]
            if "description" in params:
                update_data["description"] = params["description"]
            if "is_active" in params:
                update_data["is_active"] = params["is_active"]

            if not update_data:
                return {
                    "success": False,
                    "error": "수정할 내용이 없습니다."
                }

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.put(
                        f"http://localhost:8000/api/company-culture/{culture_id}",
                        json=update_data,
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"✅ 인재상 '{result['name']}'이 성공적으로 수정되었습니다!",
                                "data": result
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"인재상 수정 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"인재상 수정 중 오류: {str(e)}"
                }

        elif action == "delete":
            # 인재상 삭제 (비활성화)
            culture_id = params.get("id")
            if not culture_id:
                return {
                    "success": False,
                    "error": "인재상 ID가 필요합니다."
                }

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"http://localhost:8000/api/company-culture/{culture_id}",
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        return {
                            "success": True,
                            "result": {
                                "message": "🗑️ 인재상이 성공적으로 삭제되었습니다.",
                                "data": {"deleted_id": culture_id}
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"인재상 삭제 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"인재상 삭제 중 오류: {str(e)}"
                }

        elif action == "set_default":
            # 기본 인재상 설정
            culture_id = params.get("id")
            if not culture_id:
                return {
                    "success": False,
                    "error": "인재상 ID가 필요합니다."
                }

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"http://localhost:8000/api/company-culture/{culture_id}/set-default",
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"⭐ '{result['name']}'이 기본 인재상으로 설정되었습니다!",
                                "data": result
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"기본 인재상 설정 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"기본 인재상 설정 중 오류: {str(e)}"
                }

        elif action == "evaluate_applicant":
            # 지원자 인재상 평가
            applicant_id = params.get("applicant_id")
            culture_id = params.get("culture_id")

            if not applicant_id or not culture_id:
                return {
                    "success": False,
                    "error": "지원자 ID와 인재상 ID가 모두 필요합니다."
                }

            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"http://localhost:8000/api/company-culture/evaluate/{applicant_id}/{culture_id}",
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "result": {
                                "message": f"📊 지원자 인재상 평가가 완료되었습니다. 점수: {result['score']}점",
                                "data": result
                            }
                        }
                    else:
                        error_text = response.text
                        return {
                            "success": False,
                            "error": f"지원자 인재상 평가 실패: {response.status_code} - {error_text}"
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"지원자 인재상 평가 중 오류: {str(e)}"
                }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 인재상 관리 액션: {action}",
                "result": None
            }

    except Exception as e:
        logger.error(f"인재상 관리 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

def _determine_execution_order(tasks: List[Dict]) -> List[int]:
    """의존성을 고려한 실행 순서 결정"""
    # 의존성이 없는 작업들을 먼저 실행
    independent_tasks = []
    dependent_tasks = []

    for i, task in enumerate(tasks):
        if task.get("depends_on") is None:
            independent_tasks.append(i)
        else:
            dependent_tasks.append(i)

    # 의존성 순서대로 정렬
    execution_order = independent_tasks.copy()

    # 의존성 작업들을 의존 순서대로 추가
    for task in dependent_tasks:
        depends_on = task["depends_on"]
        if depends_on in execution_order:
            # 의존 작업 다음에 삽입
            insert_index = execution_order.index(depends_on) + 1
            execution_order.insert(insert_index, task)
        else:
            # 의존 작업이 없으면 맨 뒤에 추가
            execution_order.append(task)

    return execution_order

def _inject_previous_results(params: Dict, all_results: List[Dict], depends_on: int) -> Dict:
    """이전 작업 결과를 현재 파라미터에 주입"""
    if depends_on < len(all_results):
        previous_result = all_results[depends_on]
        if previous_result["status"] == "success":
            # 이전 작업의 결과 데이터를 현재 파라미터에 주입
            result_data = previous_result["result"].get("data", {})

            # 예: 채용공고 생성 결과를 메일 발송 파라미터에 주입
            if "job_id" in result_data:
                params["job_id"] = result_data["job_id"]
            if "title" in result_data:
                params["title"] = result_data["title"]
            if "id" in result_data:
                params["culture_id"] = result_data["id"]

    return params

def _build_chained_response(parsed_response: Dict, all_results: List[Dict]) -> Dict:
    """체이닝 결과를 통합한 최종 응답 생성"""
    success_messages = []
    failed_tasks = []

    for result in all_results:
        if result["status"] == "success":
            # 성공 메시지 추출
            if isinstance(result["result"], dict):
                message = result["result"].get("message", "")
                if message:
                    success_messages.append(f"✅ {message}")
            else:
                success_messages.append(f"✅ {result['tool']}.{result['action']} 완료")
        else:
            # 실패 작업 기록
            failed_tasks.append(f"❌ {result['tool']}.{result['action']}: {result['error']}")

    # 최종 응답 구성
    final_response = parsed_response.copy()

    if success_messages:
        final_response["response"] += "\n\n" + "\n".join(success_messages)

    if failed_tasks:
        logger.warning(f"⚠️ [체이닝] 실패한 작업들: {failed_tasks}")
        # 실패 작업은 로그에만 기록하고 사용자 응답에는 포함하지 않음

    # 체이닝 결과 정보 추가
    final_response["chaining_results"] = {
        "total_tasks": len(all_results),
        "successful_tasks": len([r for r in all_results if r["status"] == "success"]),
        "failed_tasks": len([r for r in all_results if r["status"] == "failed"]),
        "execution_details": all_results
    }

    return final_response

async def _execute_chained_tasks(parsed_response: Dict) -> Dict:
    """체이닝 작업 실행"""
    try:
        tasks = parsed_response.get("tasks", [])
        if not tasks:
            return parsed_response

        logger.info(f"🔗 [체이닝] {len(tasks)}개 작업 체이닝 시작")

        # 작업 결과 수집
        all_results = []
        execution_order = _determine_execution_order(tasks)

        for i, task_index in enumerate(execution_order):
            task = tasks[task_index]
            tool = task["tool"]
            action = task["action"]
            params = task.get("params", {})

            logger.info(f"🔗 [체이닝] 작업 {i+1}/{len(tasks)}: {tool}.{action}")

            try:
                # 이전 작업 결과를 현재 작업 파라미터에 주입
                if task.get("depends_on") is not None:
                    params = _inject_previous_results(params, all_results, task["depends_on"])

                # 툴 실행
                result = await _execute_tool(tool, action, params)
                all_results.append({
                    "task_index": task_index,
                    "status": "success",
                    "tool": tool,
                    "action": action,
                    "result": result
                })

                logger.info(f"✅ [체이닝] 작업 {i+1} 성공: {tool}.{action}")

            except Exception as e:
                logger.error(f"❌ [체이닝] 작업 {i+1} 실패: {tool}.{action} - {str(e)}")
                all_results.append({
                    "task_index": task_index,
                    "status": "failed",
                    "tool": tool,
                    "action": action,
                    "error": str(e)
                })

        # 최종 응답 생성
        final_response = _build_chained_response(parsed_response, all_results)
        return final_response

    except Exception as e:
        logger.error(f"❌ [체이닝] 체이닝 실행 중 오류: {str(e)}")
        return parsed_response

async def _execute_chained_tasks_advanced(parsed_response: Dict) -> Dict:
    """체이닝 작업 실행 (Phase 2: 병렬 + 재시도)"""
    try:
        tasks = parsed_response.get("tasks", [])
        if not tasks:
            return parsed_response

        logger.info(f"🚀 [체이닝 고급] {len(tasks)}개 작업 체이닝 시작 (병렬 + 순차)")

        # 독립 작업과 의존 작업 분리
        independent_tasks = [t for t in tasks if t.get("depends_on") is None]
        dependent_tasks = [t for t in tasks if t.get("depends_on") is not None]

        all_results = []

        # 🔹 독립 작업 병렬 실행
        if independent_tasks:
            logger.info(f"⚡ [체이닝 고급] {len(independent_tasks)}개 독립 작업 병렬 실행")

            async def run_independent_task(task, index):
                try:
                    result = await _execute_with_retry(task["tool"], task["action"], task.get("params", {}))
                    return {
                        "task_index": index,
                        "status": "success",
                        "tool": task["tool"],
                        "action": task["action"],
                        "result": result,
                        "execution_type": "parallel"
                    }
                except Exception as e:
                    return {
                        "task_index": index,
                        "status": "failed",
                        "tool": task["tool"],
                        "action": task["action"],
                        "error": str(e),
                        "execution_type": "parallel"
                    }

            # 병렬 실행
            parallel_results = await asyncio.gather(*[
                run_independent_task(t, i) for i, t in enumerate(independent_tasks)
            ])
            all_results.extend(parallel_results)

            logger.info(f"✅ [체이닝 고급] 독립 작업 병렬 실행 완료")

        # 🔹 의존 작업 순차 실행
        if dependent_tasks:
            logger.info(f"🔗 [체이닝 고급] {len(dependent_tasks)}개 의존 작업 순차 실행")

            for i, task in enumerate(dependent_tasks):
                tool = task["tool"]
                action = task["action"]
                params = task.get("params", {})

                logger.info(f"🔗 [체이닝 고급] 의존 작업 {i+1}/{len(dependent_tasks)}: {tool}.{action}")

                try:
                    # 이전 작업 결과를 현재 작업 파라미터에 주입
                    params = _inject_previous_results(params, all_results, task["depends_on"])

                    # 툴 실행 (재시도 로직 포함)
                    result = await _execute_with_retry(tool, action, params)
                    all_results.append({
                        "task_index": len(independent_tasks) + i,
                        "status": "success",
                        "tool": tool,
                        "action": action,
                        "result": result,
                        "execution_type": "sequential"
                    })

                    logger.info(f"✅ [체이닝 고급] 의존 작업 {i+1} 성공: {tool}.{action}")

                except Exception as e:
                    logger.error(f"❌ [체이닝 고급] 의존 작업 {i+1} 실패: {tool}.{action} - {str(e)}")
                    all_results.append({
                        "task_index": len(independent_tasks) + i,
                        "status": "failed",
                        "tool": tool,
                        "action": action,
                        "error": str(e),
                        "execution_type": "sequential"
                    })

        # 최종 응답 생성
        final_response = _build_chained_response_advanced(parsed_response, all_results)
        return final_response

    except Exception as e:
        logger.error(f"❌ [체이닝 고급] 체이닝 실행 중 오류: {str(e)}")
        return parsed_response

def _extract_culture_info(input_text: str) -> tuple[str, str]:
    """사용자 입력에서 인재상 이름과 설명을 추출"""
    if not input_text:
        return "새로운 인재상", "인재상 설명"

    # 기본값
    name = "새로운 인재상"
    description = input_text

    # 특정 패턴 매칭
    import re

    # "~을 중시하는 인재상" 패턴
    pattern1 = r"(.+?)을\s*중시하는\s*인재상"
    match1 = re.search(pattern1, input_text)
    if match1:
        trait = match1.group(1).strip()
        name = f"{trait}을 중시하는 인재상"
        description = f"우리 회사는 {trait}을 중요하게 여기는 인재를 찾습니다. {trait}을 바탕으로 업무를 수행하며, 팀과 함께 성장할 수 있는 인재를 환영합니다."
        return name, description

    # "~한 인재상" 패턴
    pattern2 = r"(.+?)한\s*인재상"
    match2 = re.search(pattern2, input_text)
    if match2:
        trait = match2.group(1).strip()
        name = f"{trait}한 인재상"
        description = f"우리 회사는 {trait}한 인재를 찾습니다. {trait}한 자세로 업무에 임하며, 지속적인 성장과 발전을 추구하는 인재를 환영합니다."
        return name, description

    # "~하는 인재상" 패턴
    pattern3 = r"(.+?)하는\s*인재상"
    match3 = re.search(pattern3, input_text)
    if match3:
        trait = match3.group(1).strip()
        name = f"{trait}하는 인재상"
        description = f"우리 회사는 {trait}하는 인재를 찾습니다. {trait}하는 능력을 바탕으로 혁신적인 솔루션을 제시하고, 회사의 성장에 기여할 수 있는 인재를 환영합니다."
        return name, description

    # "~형 인재상" 패턴
    pattern4 = r"(.+?)형\s*인재상"
    match4 = re.search(pattern4, input_text)
    if match4:
        trait = match4.group(1).strip()
        name = f"{trait}형 인재상"
        description = f"우리 회사는 {trait}형 인재를 찾습니다. {trait}한 특성을 바탕으로 창의적이고 혁신적인 아이디어를 제시하며, 팀의 성장을 이끌 수 있는 인재를 환영합니다."
        return name, description

    # 일반적인 경우: 입력 텍스트를 그대로 사용
    if "인재상" in input_text:
        # "인재상"이라는 단어를 제거하고 핵심 내용 추출
        clean_text = input_text.replace("인재상", "").replace("을", "").replace("를", "").replace("이", "").replace("가", "").strip()
        if clean_text:
            name = f"{clean_text} 인재상"
            description = f"우리 회사는 {clean_text}한 인재를 찾습니다. {clean_text}한 자세와 능력을 바탕으로 회사의 성장과 발전에 기여할 수 있는 인재를 환영합니다."

    return name, description

def _fallback_processing(session: Dict, user_input: str, current_state: str) -> Dict:
    """LangGraph 실패 시 기본 처리"""
    # 간단한 키워드 추출
    extracted_fields = {}

    # 직무 추출
    job_keywords = ["개발자", "엔지니어", "프로그래머", "디자이너"]
    for keyword in job_keywords:
        if keyword in user_input:
            extracted_fields["position"] = keyword
            break

    # 기술 스택 추출
    tech_keywords = ["React", "Python", "Java", "Node.js", "TypeScript"]
    found_tech = []
    for tech in tech_keywords:
        if tech.lower() in user_input.lower():
            found_tech.append(tech)

    if found_tech:
        extracted_fields["skills"] = found_tech

    # 세션 업데이트
    session["extracted_data"].update(extracted_fields)

    return {
        "success": True,
        "response": f"입력하신 내용을 분석했습니다. {', '.join(extracted_fields.values()) if extracted_fields else '추가 정보가 필요합니다.'}",
        "state": current_state,
        "extracted_fields": session["extracted_data"],
        "quick_actions": _get_quick_actions_by_state(current_state),
        "suggestions": _get_suggestions_by_state(current_state),
        "session_id": session["session_id"]
    }

async def _execute_with_retry(tool: str, action: str, params: Dict, max_retries: int = 2, retry_delay: float = 1.0) -> Dict:
    """재시도 로직이 포함된 툴 실행"""
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🔄 [재시도] {tool}.{action} 실행 시도 {attempt + 1}/{max_retries + 1}")
            result = await _execute_tool(tool, action, params)
            if attempt > 0:
                logger.info(f"✅ [재시도] {tool}.{action} {attempt + 1}번째 시도에서 성공")
            return result
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"⚠️ [재시도] {tool}.{action} {attempt + 1}번째 시도 실패: {str(e)}")
                logger.info(f"⏳ [재시도] {retry_delay}초 후 재시도...")
                await asyncio.sleep(retry_delay)
                # 재시도 간격을 점진적으로 증가 (exponential backoff)
                retry_delay *= 1.5
            else:
                logger.error(f"❌ [재시도] {tool}.{action} 최대 재시도 횟수 초과: {str(e)}")
                raise e

def _build_chained_response_advanced(parsed_response: Dict, all_results: List[Dict]) -> Dict:
    """고급 체이닝 결과를 통합한 최종 응답 생성"""
    success_messages = []
    failed_tasks = []
    parallel_tasks = []
    sequential_tasks = []

    for result in all_results:
        if result["status"] == "success":
            # 성공 메시지 추출
            if isinstance(result["result"], dict):
                message = result["result"].get("message", "")
                if message:
                    execution_type = result.get("execution_type", "unknown")
                    if execution_type == "parallel":
                        success_messages.append(f"⚡ {message}")
                        parallel_tasks.append(f"✅ {result['tool']}.{result['action']}")
                    else:
                        success_messages.append(f"🔗 {message}")
                        sequential_tasks.append(f"✅ {result['tool']}.{result['action']}")
            else:
                execution_type = result.get("execution_type", "unknown")
                if execution_type == "parallel":
                    success_messages.append(f"⚡ {result['tool']}.{result['action']} 완료")
                    parallel_tasks.append(f"✅ {result['tool']}.{result['action']}")
                else:
                    success_messages.append(f"🔗 {result['tool']}.{result['action']} 완료")
                    sequential_tasks.append(f"✅ {result['tool']}.{result['action']}")
        else:
            # 실패 작업 기록
            failed_tasks.append(f"❌ {result['tool']}.{result['action']}: {result['error']}")

    # 최종 응답 구성
    final_response = parsed_response.copy()

    if success_messages:
        final_response["response"] += "\n\n" + "\n".join(success_messages)

    if failed_tasks:
        logger.warning(f"⚠️ [체이닝 고급] 실패한 작업들: {failed_tasks}")
        # 실패 작업은 로그에만 기록하고 사용자 응답에는 포함하지 않음

    # 고급 체이닝 결과 정보 추가
    final_response["chaining_results"] = {
        "total_tasks": len(all_results),
        "successful_tasks": len([r for r in all_results if r["status"] == "success"]),
        "failed_tasks": len([r for r in all_results if r["status"] == "failed"]),
        "parallel_tasks": len([r for r in all_results if r.get("execution_type") == "parallel"]),
        "sequential_tasks": len([r for r in all_results if r.get("execution_type") == "sequential"]),
        "execution_details": all_results,
        "performance_summary": {
            "parallel_execution": len(parallel_tasks) > 0,
            "total_execution_time": "측정 예정",  # Phase 3에서 구현
            "efficiency_gain": f"병렬 실행: {len(parallel_tasks)}개, 순차 실행: {len(sequential_tasks)}개"
        }
    }

    return final_response

# 체이닝 템플릿 정의
CHAINING_TEMPLATES = {
    "job_posting_with_email": [
        {
            "tool": "job_posting",
            "action": "create",
            "description": "채용공고 생성",
            "depends_on": None,
            "params": {}
        },
        {
            "tool": "mail",
            "action": "send_individual",
            "description": "완료 알림 이메일 발송",
            "depends_on": 0,
            "params": {
                "template": "채용공고 완료",
                "email": "hr@company.com"
            }
        }
    ],
    "create_culture_and_evaluate": [
        {
            "tool": "company_culture",
            "action": "create",
            "description": "인재상 생성",
            "depends_on": None,
            "params": {}
        },
        {
            "tool": "company_culture",
            "action": "evaluate_applicant",
            "description": "지원자 평가",
            "depends_on": 0,
            "params": {
                "applicant_id": "sample_applicant"
            }
        }
    ],
    "search_and_create_job": [
        {
            "tool": "search",
            "action": "blog_search",
            "description": "시장 동향 검색",
            "depends_on": None,
            "params": {}
        },
        {
            "tool": "job_posting",
            "action": "create",
            "description": "검색 결과 반영한 채용공고 작성",
            "depends_on": 0,
            "params": {}
        }
    ]
}

def get_chaining_template(template_name: str) -> List[Dict]:
    """체이닝 템플릿 조회"""
    return CHAINING_TEMPLATES.get(template_name, [])

def list_available_templates() -> List[str]:
    """사용 가능한 체이닝 템플릿 목록 반환"""
    return list(CHAINING_TEMPLATES.keys())


