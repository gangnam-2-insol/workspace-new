"""
LangGraph 에이전트 설정 관리
모듈화된 에이전트 챗봇의 설정을 중앙에서 관리
"""

from typing import Dict, List
from pydantic_settings import BaseSettings

class LangGraphConfig(BaseSettings):
    """LangGraph 에이전트 설정 클래스"""
    
    # LLM 설정
    llm_model: str = "gemini-1.5-pro"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # 에이전트 설정
    max_conversation_history: int = 10
    session_timeout_minutes: int = 30
    max_sessions_per_user: int = 5
    enable_keyword_routing: bool = False
    # 공개적으로 허용되는 안전 툴 화이트리스트
    allowed_public_tools: List[str] = ["navigate", "dom_action"]
    # 네비게이션 허용 라우트(프론트 내부 경로)
    allowed_routes: List[str] = [
        "/",
        "/job-posting",
        "/new-posting",
        "/resume",
        "/interview",
        "/portfolio",
        "/cover-letter",
        "/talent",
        "/users",
        "/settings",
    ]
    trash_retention_days: int = 30
    
    # 툴 설정
    enable_tools: bool = True
    available_tools: List[str] = [
        "search_jobs",
        "analyze_resume", 
        "create_portfolio",
        "submit_application",
        "get_user_info",
        "get_interview_schedule",
        "navigate",
        "create_function_tool"
    ]
    
    # 분류 설정
    tool_keywords: List[str] = [
        "검색", "찾기", "조회", "분석", "생성", "제출", "등록",
        "이력서", "채용", "지원", "포트폴리오", "면접", "사용자",
        "이동", "페이지", "navigate",
        "함수", "툴", "도구", "자동화", "생성해", "만들어"
    ]
    
    general_keywords: List[str] = [
        "안녕", "도움", "질문", "설명", "어떻게", "무엇", "왜"
    ]
    
    # 시스템 메시지
    system_message: str = """
당신은 HireMe AI 채용 관리 시스템의 지능형 어시스턴트입니다.
사용자와 자연스럽고 친근하게 대화하며, 채용 관련 질문에 대해 도움을 제공합니다.
답변은 한국어로 제공하고, 전문적이면서도 이해하기 쉽게 설명해주세요.
"""
    
    # 툴 설명
    tool_descriptions: Dict[str, str] = {
        "search_jobs": "채용 정보 검색 결과입니다:",
        "analyze_resume": "이력서 분석 결과입니다:",
        "create_portfolio": "포트폴리오 생성 결과입니다:",
        "submit_application": "지원서 제출 결과입니다:",
        "get_user_info": "사용자 정보입니다:",
        "get_interview_schedule": "면접 일정 정보입니다:",
        "navigate": "페이지 이동 명령입니다:",
        "create_function_tool": "동적 함수(툴) 생성 결과입니다:"
    }
    
    # 툴 키워드 매핑
    tool_keyword_mapping: Dict[str, List[str]] = {
        "search_jobs": ["채용", "구인", "검색", "일자리"],
        "analyze_resume": ["이력서", "분석", "평가"],
        "create_portfolio": ["포트폴리오", "생성", "만들기"],
        "submit_application": ["지원", "제출", "신청"],
        "get_user_info": ["사용자", "정보", "프로필"],
        "get_interview_schedule": ["면접", "일정", "스케줄"],
        "navigate": ["이동", "페이지", "가자", "가", "navigate"],
        "create_function_tool": ["함수 생성", "툴 생성", "도구 생성", "create function", "새 툴", "동적 툴"]
    }
    
    class Config:
        env_prefix = "LANGGRAPH_"

# 전역 설정 인스턴스
config = LangGraphConfig()

def get_tool_by_keywords(user_input: str) -> str:
    """키워드 기반으로 적절한 툴 선택"""
    if not config.enable_keyword_routing:
        return None
    user_input_lower = user_input.lower()
    for tool_name, keywords in config.tool_keyword_mapping.items():
        if any(keyword in user_input_lower for keyword in keywords):
            return tool_name
    return None

def is_tool_request(user_input: str) -> bool:
    """사용자 입력이 툴 사용 요청인지 판단"""
    if not config.enable_keyword_routing:
        return False
    user_input_lower = user_input.lower()
    return any(keyword in user_input_lower for keyword in config.tool_keywords)

def is_general_conversation(user_input: str) -> bool:
    """사용자 입력이 일반 대화인지 판단"""
    user_input_lower = user_input.lower()
    return any(keyword in user_input_lower for keyword in config.general_keywords)

def get_tool_description(tool_name: str) -> str:
    """툴 설명 반환"""
    return config.tool_descriptions.get(tool_name, "요청하신 정보입니다:")

def is_navigate_intent(user_input: str) -> bool:
    """네비게이션 의도 감지: 명시적 이동 동사 위주로만 판단"""
    text = (user_input or "").lower()
    verbs = ["이동", "가자", "가", "열어", "열어줘", "로 가", "페이지로"]
    return any(v in text for v in verbs)

def is_dom_action_intent(user_input: str) -> bool:
    """DOM 액션(클릭/입력/선택 등) 의도 감지"""
    text = (user_input or "").lower()
    click_words = ["클릭", "눌러", "누르", "선택", "체크", "열기", "열어", "탭", "버튼", "삭제", "제거", "지워", "delete", "remove"]
    type_words = ["입력", "타이핑", "써", "적어", "붙여넣"]
    return any(w in text for w in click_words + type_words)

def is_ui_dump_intent(user_input: str) -> bool:
    """현재 페이지의 UI 구조(요소 목록) 출력 의도 감지"""
    text = (user_input or "").lower()
    keywords = [
        "ui 구조", "ui구조", "ui 맵", "ui map", "ui 인덱스", "ui index",
        "요소 목록", "엘리먼트 목록", "element list", "컴포넌트 목록",
        "목록 보여줘", "리스트 보여줘", "보여줘", "추출 가능한 ui", "ui 추출"
    ]
    # 너무 광범위한 '보여줘' 단어는 'ui'/'목록' 등과 결합된 경우만 허용
    if "보여줘" in text and not ("ui" in text or "목록" in text or "리스트" in text or "요소" in text):
        return False
    return any(k in text for k in keywords)

def validate_tool_name(tool_name: str) -> bool:
    """툴 이름 유효성 검사"""
    return tool_name in config.available_tools
