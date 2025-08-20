"""
LangGraph 에이전트 설정 관리
모듈화된 에이전트 챗봇의 설정을 중앙에서 관리
"""

from typing import Dict, List, Tuple
import re
from pydantic_settings import BaseSettings

class LangGraphConfig(BaseSettings):
    """LangGraph 에이전트 설정 클래스"""
    
    # LLM 설정
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 300
    
    # 에이전트 설정
    max_conversation_history: int = 10
    session_timeout_minutes: int = 30
    max_sessions_per_user: int = 5
    enable_keyword_routing: bool = True
    # 공개적으로 허용되는 안전 툴 화이트리스트
    allowed_public_tools: List[str] = ["navigate", "dom_action"]
    # 네비게이션 허용 라우트(프론트 내부 경로)
    allowed_routes: List[str] = [
        "/",
        "/job-posting",
        "/new-posting",
        "/resume",
        "/applicants",
        "/interview",
        "/interview-calendar",
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

    # 툴 실행 모드: local | llm | auto(LLM 가능 시 LLM, 불가 시 local)
    tool_execution_mode: Dict[str, str] = {
        "navigate": "local",
        "dom_action": "local",
        "search_jobs": "local",
        "analyze_resume": "auto",
        "create_portfolio": "local",
        "submit_application": "local",
        "get_user_info": "local",
        "get_interview_schedule": "local",
        "create_function_tool": "local",
    }
    
    # 분류 설정
    tool_keywords: List[str] = [
        "검색", "찾기", "조회", "분석", "생성", "제출", "등록",
        "이력서", "채용", "지원", "포트폴리오", "면접", "사용자",
        "이동", "페이지", "navigate",
        "함수", "툴", "도구", "자동화", "생성해", "만들어"
    ]
    
    general_keywords: List[str] = [
        "안녕", "도움", "질문", "설명", "어떻게", "무엇", "왜",
        "트렌드", "동향", "추세", "현황", "통계", "분석", "현재",
        "상황", "시장", "업계", "산업"
    ]
    
    # 시스템 메시지
    system_message: str = """
당신은 HireMe AI 채용 관리 시스템의 지능형 어시스턴트입니다.
답변은 반드시 한국어로 하며, 톤은 공감적·전문적입니다.

일반 대화 규칙:
- 길이: 2~4문장
- 첫 문장: 공감 표현 1개 포함(예: 이해해요/그럴 수 있어요)
- 두 번째 이후: 관련 예시나 간단한 제안 1개 포함
- 불필요한 반복 멘트(추가 질문 안내 등) 금지

업무/정보 질문 규칙:
- 핵심 요약 1~2문장 + 불릿 3~5개
- 필요 시 다음 행동 제안 1개
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
        "search_jobs": ["채용 검색", "구인 정보", "일자리 찾기", "채용정보 조회"],  # 명확한 검색 의도만
        "analyze_resume": ["이력서", "분석", "평가"],
        "create_portfolio": ["포트폴리오", "생성", "만들기"],
        "submit_application": ["지원", "제출", "신청"],
        "get_user_info": ["사용자", "정보", "프로필"],
        "get_interview_schedule": ["면접", "일정", "스케줄"],
        "navigate": ["이동", "페이지로", "가자", "navigate"],  # 명확한 이동 의도만
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

# ===== 토큰/청크 기반의 경량 의도 판별 =====
_COMMAND_TOKENS = [
    # 일반 동사/명령형
    "해줘", "해 줘", "해라", "해주세요", "해", "줘", "주세요",
    "이동", "가자", "가 ", "열어", "열기", "보여", "보여줘", "검색", "찾아", "찾아줘",
    "분석", "분석해", "등록", "등록해", "생성", "생성해", "만들어", "만들어줘",
    "제출", "제출해", "보내", "보내줘", "조회", "확인", "확인해",
]

_TOOL_DOMAIN_TOKENS = [
    # 도메인 명사 (명령어와 함께 나오면 툴 가능성↑)
    "채용", "채용공고", "공고", "이력서", "포트폴리오", "면접", "자소서", "인재",
    "사용자", "설정", "지원서", "일정", "캘린더", "달력",
]

def _split_into_chunks(text: str) -> List[str]:
    # 문장부호/개행/접속어 기준으로 적당히 분할
    if not text:
        return []
    # 표준 문장부호 기준 1차 분할
    parts = re.split(r"[\n\r\t\.\!\?\;]+", text)
    chunks: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # 접속어 기준 소분할
        subs = re.split(r"\b(그리고|그런데|근데|또|또는|혹은)\b", p)
        # 접속어가 포함되었을 때 토막만 취합
        for s in subs:
            s = s.strip()
            if s and s not in ("그리고", "그런데", "근데", "또", "또는", "혹은"):
                chunks.append(s)
    return chunks if chunks else [text]

def quick_intent_classify(user_input: str) -> Tuple[str, float]:
    """
    토큰/청크 기반의 경량 분류기.
    반환: (intent, score) where intent in {"tool", "general"}
    규칙:
      - 명령 토큰이 존재하고 도메인 명사가 동반되면 높은 점수로 tool
      - 의문형만 있고 명령 토큰이 없으면 general 쪽 가중
    """
    text = (user_input or "").strip()
    if not text:
        return "general", 0.0

    chunks = _split_into_chunks(text)
    tool_votes = 0.0
    total = 0.0

    for ch in chunks:
        lower = ch.lower()
        has_command = any(tok in ch for tok in _COMMAND_TOKENS)
        has_domain = any(tok in ch for tok in _TOOL_DOMAIN_TOKENS)
        is_question = ("?" in ch) or ("어떻게" in ch) or ("무엇" in ch)

        score = 0.0
        if has_command and has_domain:
            score = 0.9
        elif has_command:
            score = 0.7
        elif has_domain and not is_question:
            score = 0.55
        elif is_question and any(w in lower for w in ["트렌드", "동향", "추세", "현황", "통계"]):
            score = 0.2  # 분석/통계 질문은 일반 대화 쪽으로
        else:
            score = 0.3 if is_question else 0.2

        tool_votes += score
        total += 1.0

    avg = tool_votes / max(total, 1.0)
    if avg >= 0.7:
        return "tool", avg
    elif avg <= 0.35:
        return "general", 1.0 - avg
    # 애매하면 낮은 확신으로 tool 쪽 제안 (후속 LLM 보정)
    return "tool", avg
