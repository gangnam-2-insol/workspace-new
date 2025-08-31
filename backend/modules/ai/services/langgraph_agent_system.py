"""
LangGraph 기반 Agent 시스템
실제 LangGraph 라이브러리를 사용하여 구현된 Agent 시스템
"""

import asyncio
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from dotenv import load_dotenv
from modules.core.services.openai_service import OpenAIService

# LangGraph 관련 import
try:
    # Pydantic 버전 충돌을 피하기 위해 환경 변수 설정
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_ENDPOINT"] = ""
    os.environ["LANGCHAIN_API_KEY"] = ""

    # LangGraph import 시도
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, StateGraph
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph 라이브러리 사용 가능")
except (ImportError, TypeError, Exception) as e:
    LANGGRAPH_AVAILABLE = False
    print(f"❌ LangGraph 라이브러리 로드 실패: {e}")
    print("💡 LangGraph를 사용하지 않고 기존 시스템으로 대체합니다.")

load_dotenv()

# OpenAI 설정
try:
    openai_service = OpenAIService(model_name="gpt-4o")
except Exception as e:
    openai_service = None

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
def normalize_text(text: str) -> str:
    """텍스트 정규화"""
    # 1. 공백 정규화
    text = re.sub(r'\s+', ' ', text.strip())

    # 2. 문장 부호 정규화
    text = re.sub(r'[,.!?]+', '.', text)

    # 3. 조사 정규화
    text = re.sub(r'(으로|로)\s+(이동|가|보여)', r'\2', text)
    text = re.sub(r'(을|를)\s+(보여|열어)', r'\2', text)

    return text

def split_mixed_intent(text: str) -> tuple[str, str]:
    """혼합 의도 문장 분리"""
    # 1. 연결어 기반 분리
    connectors = [
        # 기본 연결어
        "하고", "그리고", "다음", "후에", "이후", "다음에",
        "그 다음", "그다음", "그리고 나서", "그러고 나서",

        # 동작 연결어
        "해주고", "알려주고", "설명하고", "분석하고", "보여주고",
        "확인하고", "검토하고", "평가하고", "조회하고", "찾아주고",

        # 시간 연결어
        "한 후", "한 다음", "하면서", "하고나서", "이후에",
        "다음으로", "그러고나서", "그런다음", "그리고나서",

        # 목적 연결어
        "위한", "관련", "필요한", "대한", "따른",
        "기반", "바탕", "근거", "참고"
    ]

    # 1.1 정규식 패턴 생성
    connector_pattern = "|".join(map(re.escape, connectors))
    pattern = f"(.+?)({connector_pattern})\\s+(.+)"

    if match := re.search(pattern, text):
        first_part = match.group(1).strip()
        second_part = match.group(3).strip()
        return first_part, second_part

    # 2. 문장 구조 기반 분리
    structure_patterns = [
        # 기본 구조
        r"(.+?)(?:하고|해주고|알려주고|설명하고|분석하고)\s+(.+?)(?:페이지|화면|창)(?:\s+(?:보여|열어|이동|들어가))?",
        r"(.+?)(?:방법|기준|과정|사례|팁|예시|정보|결과|피드백).*?(?:알려|설명|분석|보여).*?(?:페이지|화면|창)",
        r"(.+?)(?:준비|최적화|스케줄링|관리).*?방법.*?(?:페이지|화면|창)",
        r"(.+?)(?:위한|관련|필요한)\s+(.+?)(?:페이지|화면|창)",

        # 확장 구조
        r"(.+?)(?:확인|검토|평가|조회|찾기).*?(?:하고|후).*?(?:페이지|화면|창)",
        r"(.+?)(?:정보|데이터|내용|상태).*?(?:보고|확인).*?(?:페이지|화면|창)",
        r"(.+?)(?:작성|입력|수정|삭제).*?(?:방법|기준).*?(?:페이지|화면|창)",
        r"(.+?)(?:처리|진행|관리|설정).*?(?:절차|순서).*?(?:페이지|화면|창)",

        # 역순 구조
        r"(?:페이지|화면|창).*?(?:보여|열어|이동).*?(?:다음|후).*?(.+?)(?:알려|설명|분석)",
        r"(?:페이지|화면|창).*?(?:확인|검토).*?(?:하면서|하고).*?(.+?)(?:진행|처리)",

        # 복합 구조
        r"(.+?)(?:방법|기준|과정).*?(?:알려|설명).*?(?:다음|후).*?(?:페이지|화면|창)",
        r"(.+?)(?:정보|내용).*?(?:확인|검토).*?(?:위해|필요).*?(?:페이지|화면|창)"
    ]

    for pattern in structure_patterns:
        if match := re.search(pattern, text):
            first_part = match.group(1).strip() if len(match.groups()) >= 1 else ""
            second_part = match.group(2).strip() if len(match.groups()) >= 2 else text[match.end(1):].strip()
            if first_part and second_part:
                return first_part, second_part

    # 3. 문장 부호 기반 분리
    if "." in text or "," in text:
        parts = re.split(r'[.,]', text)
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()

    # 4. 키워드 기반 분리
    info_keywords = ["알려줘", "설명", "분석", "확인", "검토", "평가", "조회", "찾아"]
    action_keywords = ["페이지", "화면", "창", "이동", "열어", "보여", "들어가"]

    # 정보 요청이 먼저 나오는 경우
    for info_kw in info_keywords:
        if info_kw in text:
            parts = text.split(info_kw, 1)
            if len(parts) == 2:
                first_part = (parts[0] + info_kw).strip()
                second_part = parts[1].strip()
                if any(kw in second_part for kw in action_keywords):
                    return first_part, second_part

    # UI 액션이 먼저 나오는 경우
    for action_kw in action_keywords:
        if action_kw in text:
            parts = text.split(action_kw, 1)
            if len(parts) == 2:
                first_part = parts[0].strip()
                second_part = (action_kw + parts[1]).strip()
                if any(kw in first_part for kw in info_keywords):
                    return first_part, second_part

    return text, ""

def detect_mixed_intent(text: str) -> tuple[bool, list[str], list[str], float]:
    """혼합 의도 감지 함수"""
    # 텍스트 정규화
    text = normalize_text(text)

    # 1. 문장 분리
    first_part, second_part = split_mixed_intent(text)

    # 2. 의도 키워드 체크
    info_keywords = [
        # 기본 질문
        "알려줘", "설명", "분석", "확인", "검토", "평가", "조회", "찾아",
        "어떻게", "왜", "뭐", "무엇", "어디", "언제", "누구", "방법",

        # 정보 요청
        "정보", "내용", "결과", "피드백", "데이터", "상태", "현황",
        "기준", "과정", "사례", "팁", "예시", "방식", "절차", "순서",

        # 분석 요청
        "분석", "평가", "검토", "확인", "조회", "찾기", "비교", "측정",
        "진단", "점검", "파악", "이해", "판단", "검사", "테스트",

        # 학습/교육
        "배우", "가르쳐", "교육", "학습", "공부", "연습", "훈련", "준비",
        "연구", "조사", "탐구", "실습", "경험", "노하우", "스킬",

        # 추가 정보 요청
        "의미", "개념", "정의", "특징", "장단점", "차이", "비교", "관계",
        "원리", "원칙", "규칙", "기법", "전략", "방안", "해결", "해결책",
        "대안", "대책", "요령", "요약", "정리", "설계", "구조", "구성",
        "흐름", "프로세스", "시스템", "메커니즘", "아키텍처", "패턴"
    ]

    action_keywords = [
        # 기본 액션
        "페이지", "화면", "창", "이동", "열어", "보여", "들어가", "접속",
        "확인", "돌아가", "닫아", "새로고침", "클릭", "선택", "입력",

        # UI 조작
        "저장", "삭제", "수정", "변경", "추가", "제거", "업데이트",
        "등록", "취소", "확인", "적용", "실행", "처리", "완료",

        # 네비게이션
        "이전", "다음", "처음", "마지막", "위", "아래", "좌", "우",
        "앞", "뒤", "메인", "홈", "대시보드", "목록", "상세",

        # 특수 액션
        "새로고침", "리로드", "초기화", "리셋", "되돌리기", "복원",
        "확대", "축소", "정렬", "필터", "검색", "출력", "다운로드",

        # 추가 UI 액션
        "보기", "뷰", "탭", "메뉴", "버튼", "링크", "폼", "입력창",
        "체크박스", "라디오", "드롭다운", "리스트", "테이블", "그리드",
        "차트", "그래프", "다이어그램", "이미지", "아이콘", "로고"
    ]

    # 3. 각 부분의 의도 분석
    first_info = any(kw in first_part for kw in info_keywords)
    first_action = any(kw in first_part for kw in action_keywords)
    second_info = any(kw in second_part for kw in info_keywords)
    second_action = any(kw in second_part for kw in action_keywords)

    # 4. 혼합 의도 판단
    if first_info and second_action:
        # 정보 요청 → UI 액션 패턴
        if any(kw in first_part for kw in ["방법", "과정", "절차", "기준", "예시"]):
            # 설명 후 관련 페이지로 이동하는 패턴
            if any(kw in second_part for kw in ["페이지", "화면", "창"]):
                return True, ["info_request", "ui_action"], [first_part, second_part], 0.95
        return True, ["info_request", "ui_action"], [first_part, second_part], 0.9
    elif first_action and second_info:
        # UI 액션 → 정보 요청 패턴
        if any(kw in first_part for kw in ["페이지", "화면", "창"]):
            # 특정 페이지에서 정보를 확인하는 패턴
            if any(kw in second_part for kw in ["확인", "검토", "분석"]):
                return True, ["ui_action", "info_request"], [first_part, second_part], 0.95
        return True, ["ui_action", "info_request"], [first_part, second_part], 0.9
    elif first_info and second_info:
        # 정보 요청 → 정보 요청 패턴
        if any(kw in second_part for kw in ["페이지", "화면", "창", "보기", "뷰"]):
            # 두 번째 부분이 UI 관련 정보를 요청하는 패턴
            return True, ["info_request", "ui_action"], [first_part, second_part], 0.85
        # 연속된 정보 요청 패턴
        if any(kw in first_part for kw in ["먼저", "우선", "처음"]):
            return True, ["info_request", "info_request"], [first_part, second_part], 0.9
        return True, ["info_request", "info_request"], [first_part, second_part], 0.8
    elif first_action and second_action:
        # UI 액션 → UI 액션 패턴
        if any(kw in first_part for kw in ["정보", "내용", "결과", "데이터"]):
            # 첫 번째 부분이 정보 관련 UI를 요청하는 패턴
            return True, ["info_request", "ui_action"], [first_part, second_part], 0.85
        # 연속된 UI 액션 패턴
        if any(kw in first_part for kw in ["먼저", "우선", "처음"]):
            return True, ["ui_action", "ui_action"], [first_part, second_part], 0.9
        return True, ["ui_action", "ui_action"], [first_part, second_part], 0.8

    # 5. 연결 패턴 감지
    connection_patterns = [
        # 기본 패턴
        r"(.+?)하고\s+(.+?)해줘",
        r"(.+?)알려주고\s+(.+?)로\s+이동",
        r"(.+?)설명하고\s+(.+?)보여줘",
        r"(.+?)분석해주고\s+(.+?)페이지",
        r"(.+?)하고\s+(.+?)페이지",
        r"(.+?)해주고\s+(.+?)화면",

        # 추가 패턴
        r"(.+?)알려주고\s+(.+?)보여줘",
        r"(.+?)설명해주고\s+(.+?)이동",
        r"(.+?)방법\s+알려주고\s+(.+?)페이지",
        r"(.+?)기준\s+설명하고\s+(.+?)화면",
        r"(.+?)정보\s+알려주고\s+(.+?)페이지",
        r"(.+?)분석하고\s+(.+?)보여줘",
        r"(.+?)결과\s+설명하고\s+(.+?)페이지",
        r"(.+?)피드백\s+해주고\s+(.+?)이동",
        r"(.+?)과정\s+설명하고\s+(.+?)보여줘",
        r"(.+?)사례\s+알려주고\s+(.+?)페이지",
        r"(.+?)방법\s+설명하고\s+(.+?)열어줘",
        r"(.+?)기준\s+알려주고\s+(.+?)이동",
        r"(.+?)팁\s+알려주고\s+(.+?)페이지"
    ]

    # 기본 반환값
    return False, [], [], 0.0

async def intent_detection_node(state: AgentState) -> AgentState:
    """의도 분류 노드"""
    try:
        user_input = state["user_input"].lower()

        # 1. 혼합 의도 감지
        is_mixed, parts = detect_mixed_intent(user_input)
        if is_mixed:
            state["intent"] = "mixed"
            state["sub_intents"] = ["info_request", "ui_action"]
            state["sub_parts"] = parts
            state["confidence"] = 0.9
            return state

        # 2. 키워드 기반 빠른 분류
        info_keywords = ["알려줘", "설명", "어떻게", "왜", "뭐", "무엇", "어디", "언제", "누구", "방법", "어떤", "어느", "가르쳐", "궁금", "분석"]
        action_keywords = ["열어줘", "이동", "보여줘", "클릭", "선택", "입력", "변경", "저장", "삭제", "추가", "페이지", "화면", "들어가"]

        # 명확한 키워드 매칭
        if any(keyword in user_input for keyword in info_keywords):
            if not any(keyword in user_input for keyword in action_keywords):
                state["intent"] = "info_request"
                state["confidence"] = 0.9
                return state

        if any(keyword in user_input for keyword in action_keywords):
            if not any(keyword in user_input for keyword in info_keywords):
                state["intent"] = "ui_action"
                state["confidence"] = 0.9
                return state

        # 2. 프론트엔드 분류 확인
        frontend_intent = state.get("frontend_intent", "")
        if frontend_intent == "page_action":
            state["intent"] = "ui_action"
            state["confidence"] = 0.9
            return state

        system_prompt = """
다음 카테고리 중 하나로 분류해주세요:

1. "info_request" - 정보 요청, 질문, 설명 요구 (예: "알려줘", "설명해줘", "어떻게", "왜")
2. "ui_action" - UI 조작, 페이지 이동 요청 (예: "열어줘", "이동해줘", "보여줘", "클릭해줘")
3. "search" - 정보 검색, 조사, 찾기 관련 요청
4. "calc" - 계산, 수식, 수치 처리 관련 요청
5. "db" - 데이터베이스 조회, 저장된 정보 검색
6. "recruit" - 채용공고 작성, 채용 관련 내용 생성
7. "chat" - 일반적인 대화

입력을 신중히 분석하여 정보 요청("info_request")과 UI 액션("ui_action")을 정확히 구분해주세요.
예시:
- "채용 트렌드 알려줘" → info_request (정보를 요구하는 질문)
- "채용 페이지 열어줘" → ui_action (UI 조작 요청)
- "개발자 채용 공고 작성해줘" → recruit (채용 관련 생성 요청)

분류 결과만 반환해주세요 (예: "info_request", "ui_action", "search", "calc", "db", "recruit", "chat")
"""

        prompt = f"{system_prompt}\n\n사용자 입력: {user_input}"
        if openai_service:
            response = await openai_service.generate_response(prompt)
            intent = response.strip().lower()
        else:
            intent = "chat"

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

async def info_handler_node(state: AgentState) -> AgentState:
    """정보 요청 처리 노드"""
    try:
        user_input = state["user_input"]

        system_prompt = """
사용자의 정보 요청에 대해 명확하고 전문적인 답변을 제공해주세요.
답변은 간단명료하게 작성하되, 핵심 정보를 포함해야 합니다.
"""

        prompt = f"{system_prompt}\n\n사용자 질문: {user_input}"
        if openai_service:
            response = await openai_service.generate_response(prompt)
        else:
            response = "죄송합니다. AI 서비스를 사용할 수 없습니다."

        state["tool_result"] = response
        state["current_node"] = "info_handler"
        return state

    except Exception as e:
        state["error"] = f"정보 처리 중 오류: {str(e)}"
        return state

def page_navigator_node(state: AgentState) -> AgentState:
    """페이지 네비게이션 노드"""
    try:
        user_input = state["user_input"]

        # 페이지 매핑 정보
        page_mapping = {
            "채용": "/recruitment",
            "이력서": "/resume",
            "면접": "/interview",
            "대시보드": "/dashboard",
            "설정": "/settings",
            "통계": "/statistics",
            "사용자": "/users",
            "포트폴리오": "/portfolio"
        }

        # 요청된 페이지 찾기
        target_page = None
        for key, value in page_mapping.items():
            if key in user_input:
                target_page = value
                break

        if target_page:
            state["tool_result"] = f"페이지 이동: {target_page}"
            state["navigation_target"] = target_page
        else:
            state["tool_result"] = "이동할 페이지를 찾을 수 없습니다."

        state["current_node"] = "page_navigator"
        return state

    except Exception as e:
        state["error"] = f"페이지 네비게이션 중 오류: {str(e)}"
        return state

def ui_controller_node(state: AgentState) -> AgentState:
    """UI 컨트롤러 노드"""
    try:
        user_input = state["user_input"]

        # UI 액션 매핑
        action_mapping = {
            "클릭": "click",
            "선택": "select",
            "입력": "input",
            "제출": "submit",
            "취소": "cancel",
            "확인": "confirm"
        }

        # 요청된 액션 찾기
        action = None
        for key, value in action_mapping.items():
            if key in user_input:
                action = value
                break

        if action:
            state["tool_result"] = f"UI 액션 실행: {action}"
            state["ui_action"] = action
        else:
            state["tool_result"] = "실행할 UI 액션을 찾을 수 없습니다."

        state["current_node"] = "ui_controller"
        return state

    except Exception as e:
        state["error"] = f"UI 컨트롤 중 오류: {str(e)}"
        return state

async def resume_analyzer_node(state: AgentState) -> AgentState:
    """이력서 분석 노드"""
    try:
        user_input = state["user_input"]

        system_prompt = """
이력서 분석 요청에 대해 전문적인 피드백을 제공해주세요.
다음 항목들을 중점적으로 분석해주세요:
1. 경력 및 스킬
2. 프로젝트 경험
3. 교육 및 자격
4. 개선 포인트
"""

        prompt = f"{system_prompt}\n\n분석 요청: {user_input}"
        if openai_service:
            response = await openai_service.generate_response(prompt)
        else:
            response = "죄송합니다. AI 서비스를 사용할 수 없습니다."

        state["tool_result"] = response
        state["current_node"] = "resume_analyzer"
        return state

    except Exception as e:
        state["error"] = f"이력서 분석 중 오류: {str(e)}"
        return state

def action_handler_node(state: AgentState) -> AgentState:
    """액션 핸들러 노드"""
    try:
        user_input = state["user_input"]

        # 액션 우선순위 결정
        if "페이지" in user_input or "화면" in user_input or "이동" in user_input:
            return page_navigator_node(state)
        elif "클릭" in user_input or "선택" in user_input or "입력" in user_input:
            return ui_controller_node(state)
        else:
            state["tool_result"] = "처리할 수 있는 액션을 찾을 수 없습니다."

        state["current_node"] = "action_handler"
        return state

    except Exception as e:
        state["error"] = f"액션 처리 중 오류: {str(e)}"
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

async def recruitment_node(state: AgentState) -> AgentState:
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

        if openai_service:
            result = await openai_service.generate_response(prompt)
        else:
            result = "죄송합니다. AI 서비스를 사용할 수 없습니다."

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

async def intent_revalidation_node(state: AgentState) -> AgentState:
    """의도 재검증 노드"""
    try:
        user_input = state["user_input"]
        current_intent = state.get("intent", "chat")
        confidence = state.get("confidence", 0.0)

        # 높은 신뢰도로 분류된 경우 재검증 스킵
        if confidence >= 0.9:
            state["final_intent"] = current_intent
            return state

        # 혼합 의도 감지
        info_keywords = ["알려줘", "설명", "어떻게", "왜", "뭐", "무엇", "어디", "언제", "누구", "방법"]
        action_keywords = ["열어줘", "이동", "보여줘", "클릭", "선택", "입력", "변경", "저장", "페이지", "화면"]

        has_info = any(keyword in user_input.lower() for keyword in info_keywords)
        has_action = any(keyword in user_input.lower() for keyword in action_keywords)

        if has_info and has_action:
            state["intent"] = "mixed"
            state["final_intent"] = "mixed"
            state["sub_intents"] = ["info_request", "ui_action"]
            state["confidence"] = 0.9
            return state

        system_prompt = """
사용자의 입력이 "정보 요청"인지 "UI 액션"인지 판단해주세요.

정보 요청:
- 설명이나 정보를 요구하는 질문
- "알려줘", "설명해줘", "어떻게", "왜" 등의 표현
- 지식이나 데이터를 요구하는 내용

UI 액션:
- 페이지 이동이나 UI 조작을 요청
- "열어줘", "이동해줘", "보여줘", "클릭해줘" 등의 표현
- 구체적인 페이지나 기능 조작 요청

입력: {user_input}
현재 분류: {current_intent}

"info_request" 또는 "ui_action" 중 하나로만 응답해주세요.
"""

        prompt = system_prompt.format(
            user_input=user_input,
            current_intent=current_intent
        )

        if openai_service:
            response = await openai_service.generate_response(prompt)
            revalidated_intent = response.strip().lower()
        else:
            revalidated_intent = current_intent

        if revalidated_intent in ["info_request", "ui_action"]:
            state["intent"] = revalidated_intent
            state["final_intent"] = revalidated_intent
            state["metadata"]["revalidation_time"] = datetime.now().isoformat()
            print(f"[LangGraph] 의도 재검증 완료: {current_intent} → {revalidated_intent}")
            state["confidence"] = 0.9

        return state

    except Exception as e:
        state["error"] = f"의도 재검증 중 오류: {str(e)}"
        return state

def analyze_intent_parts(text: str, context: dict = None) -> tuple[str, str, float]:
    """의도 부분 분석"""
    # 1. 응답 유형 체크
    response_type, confidence = get_response_type(text, context)

    # 2. 의도 판단
    if response_type == "info_request":
        return "info_request", text, confidence
    elif response_type == "ui_action":
        return "ui_action", text, confidence
    elif response_type == "mixed":
        # 혼합 의도 감지
        is_mixed, intents, parts = detect_mixed_intent(text)
        if is_mixed:
            # 각 부분의 의도 분석
            first_type, first_conf = get_response_type(parts[0], context)
            second_type, second_conf = get_response_type(parts[1], context)

            # 혼합 의도 판단
            if intents[0] == "info_request" and intents[1] == "ui_action":
                return "mixed", text, max(first_conf, second_conf)
            elif intents[0] == "ui_action" and intents[1] == "info_request":
                return "mixed", text, max(first_conf, second_conf)
            elif "info_request" in intents:
                # 정보 요청이 포함된 경우, 문맥 확인
                if context and context.get("last_intent") == "ui_action":
                    return "ui_action", text, 0.8  # UI 액션 문맥 유지
                return "info_request", text, 0.8
            elif "ui_action" in intents:
                # UI 액션이 포함된 경우, 문맥 확인
                if context and context.get("last_intent") == "info_request":
                    return "info_request", text, 0.8  # 정보 요청 문맥 유지
                return "ui_action", text, 0.8

            # 문맥 기반 판단
            if context:
                last_intent = context.get("last_intent", "")
                last_action = context.get("last_action", "")
                last_topic = context.get("last_topic", "")

                # 이전 의도가 있는 경우
                if last_intent in ["info_request", "ui_action"]:
                    # 이전 액션이 있고 현재 입력이 관련 키워드를 포함하는 경우
                    if last_action:
                        action_keywords = ["다시", "취소", "확인", "저장", "삭제", "수정", "이전", "다음"]
                        if any(kw in text for kw in action_keywords):
                            return "ui_action", text, 0.8

                    # 이전 주제가 있고 현재 입력이 관련 키워드를 포함하는 경우
                    if last_topic:
                        topic_keywords = ["그거", "이거", "저거", "그것", "이것", "저것", "그", "이", "저"]
                        if any(kw in text for kw in topic_keywords):
                            return last_intent, text, 0.7  # 이전 의도 유지

        # 기본적으로 혼합 의도로 처리
        return "mixed", text, confidence
    elif response_type in ["confirm", "deny", "unknown"]:
        # 문맥 기반 판단
        if context:
            last_intent = context.get("last_intent", "")
            if last_intent in ["info_request", "ui_action", "mixed"]:
                return last_intent, text, confidence * 0.9  # 이전 의도 유지 (약간 낮은 신뢰도)
        return "chat", text, confidence
    elif response_type in ["laugh", "happy", "sad", "annoyed", "surprise", "confusion"]:
        # 문맥 기반 판단
        if context:
            last_intent = context.get("last_intent", "")
            if last_intent in ["info_request", "ui_action", "mixed"]:
                return last_intent, text, confidence * 0.8  # 이전 의도 유지 (더 낮은 신뢰도)
        return "chat", text, confidence
    else:
        # 문맥 기반 판단
        if context:
            last_intent = context.get("last_intent", "")
            if last_intent in ["info_request", "ui_action", "mixed"]:
                return last_intent, text, confidence * 0.7  # 이전 의도 유지 (가장 낮은 신뢰도)
        return "chat", text, confidence

async def mixed_intent_handler_node(state: AgentState) -> AgentState:
    """혼합 의도 처리 노드"""
    try:
        user_input = state["user_input"]
        context = get_conversation_context(state)

        # 1. 혼합 의도 감지
        is_mixed, intents, parts, confidence = detect_mixed_intent(user_input)
        if not is_mixed:
            state["error"] = "혼합 의도가 감지되지 않았습니다."
            return state

        # 2. 상태 초기화
        result_state = state.copy()
        result_state["sub_intents"] = intents
        result_state["sub_parts"] = parts
        result_state["confidence"] = confidence
        combined_results = []

        # 3. 순차적 처리
        for idx, (intent, part) in enumerate(zip(intents, parts)):
            # 3.1 상태 복사
            sub_state = result_state.copy()
            sub_state["intent"] = intent
            sub_state["final_intent"] = intent

            # 3.2 입력 보강
            if intent == "info_request":
                # 정보 요청 문맥 보강
                info_keywords = [
                    # 기본 질문
                    "알려줘", "설명", "분석", "확인", "검토", "평가", "조회", "찾아",
                    "어떻게", "왜", "뭐", "무엇", "어디", "언제", "누구", "방법",

                    # 정보 요청
                    "정보", "내용", "결과", "피드백", "데이터", "상태", "현황",
                    "기준", "과정", "사례", "팁", "예시", "방식", "절차", "순서",

                    # 분석 요청
                    "분석", "평가", "검토", "확인", "조회", "찾기", "비교", "측정",
                    "진단", "점검", "파악", "이해", "판단", "검사", "테스트"
                ]
                if not any(keyword in part for keyword in info_keywords):
                    part += " 알려줘"
            elif intent == "ui_action":
                # UI 액션 문맥 보강
                action_keywords = [
                    # 기본 액션
                    "열어줘", "이동", "보여줘", "들어가", "접속", "확인", "돌아가",
                    "닫아", "새로고침", "클릭", "선택", "입력", "저장", "삭제",

                    # UI 조작
                    "수정", "변경", "추가", "제거", "업데이트", "등록", "취소",
                    "확인", "적용", "실행", "처리", "완료",

                    # 네비게이션
                    "이전", "다음", "처음", "마지막", "위", "아래", "좌", "우",
                    "앞", "뒤", "메인", "홈", "대시보드", "목록", "상세"
                ]
                if not any(keyword in part for keyword in action_keywords):
                    if "페이지" in part:
                        part += " 열어줘"
                    elif "화면" in part:
                        part += " 보여줘"
                    elif "창" in part:
                        part += " 열어줘"
                    else:
                        part += " 이동"

            sub_state["user_input"] = part

            # 3.3 의도별 처리
            if intent == "info_request":
                sub_state = await info_handler_node(sub_state)
                if sub_state.get("tool_result"):
                    combined_results.append({
                        "type": "info",
                        "content": sub_state["tool_result"],
                        "metadata": {
                            "topic": sub_state.get("topic", ""),
                            "confidence": sub_state.get("confidence", 0.0),
                            "context": {
                                "last_intent": "info_request",
                                "last_confidence": sub_state.get("confidence", 0.0),
                                "last_topic": sub_state.get("topic", "")
                            }
                        }
                    })
            elif intent == "ui_action":
                sub_state = await action_handler_node(sub_state)
                if sub_state.get("tool_result"):
                    combined_results.append({
                        "type": "action",
                        "content": sub_state["tool_result"],
                        "metadata": {
                            "navigation_target": sub_state.get("navigation_target", ""),
                            "ui_action": sub_state.get("ui_action", ""),
                            "confidence": sub_state.get("confidence", 0.0),
                            "context": {
                                "last_intent": "ui_action",
                                "last_confidence": sub_state.get("confidence", 0.0),
                                "last_action": sub_state.get("ui_action", "")
                            }
                        }
                    })
                    # UI 액션의 결과를 최종 상태에 반영
                    result_state["navigation_target"] = sub_state.get("navigation_target")
                    result_state["ui_action"] = sub_state.get("ui_action")

        # 4. 결과 결합
        if combined_results:
            # 4.1 결과 정렬 (정보 요청 → UI 액션)
            combined_results.sort(key=lambda x: 0 if x["type"] == "info" else 1)

            # 4.2 순차적 응답 생성
            result_state["tool_result"] = "먼저, " + combined_results[0]["content"]
            if len(combined_results) > 1:
                result_state["tool_result"] += "\n\n그리고, " + combined_results[1]["content"]

            # 4.3 메타데이터 결합
            result_state["success"] = True
            result_state["intent"] = "mixed"  # 최종 의도를 mixed로 유지
            result_state["final_intent"] = "mixed"
            result_state["confidence"] = max(r["metadata"]["confidence"] for r in combined_results)
            result_state["sub_results"] = combined_results  # 세부 결과 저장

            # 4.4 컨텍스트 업데이트
            result_state["context"] = {
                "last_intent": "mixed",
                "last_confidence": result_state["confidence"],
                "last_topic": combined_results[0]["metadata"].get("topic", ""),
                "last_action": combined_results[-1]["metadata"].get("ui_action", "")
            }
        else:
            result_state["error"] = "혼합 의도 처리 중 결과를 생성하지 못했습니다."

        return result_state

    except Exception as e:
        state["error"] = f"혼합 의도 처리 중 오류: {str(e)}"
        return state

def get_conversation_context(state: AgentState) -> dict:
    """대화 컨텍스트 가져오기"""
    history = state.get("conversation_history", [])
    if not history:
        return {}

    last_state = history[-1]
    return {
        "last_intent": last_state.get("intent", ""),
        "last_action": last_state.get("action", ""),
        "last_page": last_state.get("page", ""),
        "last_topic": last_state.get("topic", "")
    }

def get_intent_keywords(text: str) -> tuple[bool, bool]:
    """의도 관련 키워드 체크"""
    # 1. 정보 요청 키워드
    info_keywords = [
        "알려줘", "설명", "어떻게", "왜", "뭐", "무엇", "어디", "언제", "누구", "방법",
        "어떤", "어느", "가르쳐", "궁금", "분석", "평가", "확인", "찾아", "검색"
    ]

    # 2. UI 액션 키워드
    action_keywords = [
        "열어줘", "이동", "보여줘", "클릭", "선택", "입력", "변경", "저장", "삭제", "추가",
        "페이지", "화면", "창", "들어가", "접속", "확인", "돌아가", "닫아", "새로고침"
    ]

    has_info = any(keyword in text for keyword in info_keywords)
    has_action = any(keyword in text for keyword in action_keywords)

    return has_info, has_action

def get_response_type(text: str, context: dict = None) -> tuple[str, float]:
    """응답 유형 판단"""
    # 1. 기본 응답
    simple_responses = {
        # 긍정
        "네": "confirm", "응": "confirm", "어": "confirm", "그래": "confirm",
        "ㅇㅇ": "confirm", "좋아": "confirm", "알겠어": "confirm", "괜찮아": "confirm",
        "yes": "confirm", "ok": "confirm", "y": "confirm", "ㅇ": "confirm",

        # 부정
        "아니": "deny", "ㄴㄴ": "deny", "싫어": "deny", "no": "deny", "n": "deny",
        "ㄴ": "deny", "아뇨": "deny", "아니오": "deny",

        # 모름/불확실
        "모르겠어": "unknown", "글쎄": "unknown", "잘모르겠어": "unknown",
        "maybe": "unknown", "아마도": "unknown", "글쎄요": "unknown"
    }

    # 2. 감정 표현
    emotion_responses = {
        # 긍정적
        "ㅋㅋ": "laugh", "ㅎㅎ": "laugh", "^^": "happy", "😊": "happy",
        "ㅋ": "laugh", "ㅎ": "laugh", "😄": "laugh", "😆": "laugh",
        "ㅋㅋㅋ": "laugh", "ㅎㅎㅎ": "laugh", "ㅋㅋㅋㅋ": "laugh", "ㅎㅎㅎㅎ": "laugh",

        # 부정적
        "ㅠㅠ": "sad", "ㅜㅜ": "sad", "ㅡㅡ": "annoyed", "😢": "sad",
        "ㅠ": "sad", "ㅜ": "sad", "😭": "sad", "😤": "annoyed",
        "ㅠㅠㅠ": "sad", "ㅜㅜㅜ": "sad", "ㅠㅠㅠㅠ": "sad", "ㅜㅜㅜㅜ": "sad",

        # 놀람/혼란
        "헐": "surprise", "와": "surprise", "오": "surprise", "아": "surprise",
        "엥": "confusion", "헉": "surprise", "😮": "surprise", "😲": "surprise",
        "헐~": "surprise", "와~": "surprise", "오~": "surprise", "아~": "surprise"
    }

    # 3. 단순 긍정/부정
    confirmation_responses = {
        # 긍정
        "좋습니다": "confirm", "알겠습니다": "confirm", "그렇습니다": "confirm",
        "맞습니다": "confirm", "동의합니다": "confirm", "네맞아요": "confirm",
        "좋아요": "confirm", "알겠어요": "confirm", "그래요": "confirm",

        # 부정
        "싫습니다": "deny", "아닙니다": "deny", "그렇지않습니다": "deny",
        "아니요": "deny", "반대합니다": "deny", "아니에요": "deny",
        "싫어요": "deny", "아니예요": "deny", "그렇지않아요": "deny",

        # 모름/불확실
        "모르겠습니다": "unknown", "잘모르겠습니다": "unknown",
        "글쎄요": "unknown", "애매합니다": "unknown",
        "모르겠어요": "unknown", "잘모르겠어요": "unknown"
    }

    text = text.strip().lower()

    # 1. 빈 입력 체크
    if not text:
        if context and context.get("last_intent"):
            return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
        return "empty", 1.0

    # 2. 정규식 패턴
    if re.match(r'^[ㄱ-ㅎㅏ-ㅣ]+$', text):  # 자음/모음만
        if context and context.get("last_intent"):
            # 자음/모음이 긍정/부정을 나타내는 경우
            if text in ["ㅇ", "ㄴ"]:
                response_type = "confirm" if text == "ㅇ" else "deny"
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.8  # 이전 의도 유지 (높은 신뢰도)
                return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
            return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
        return "incomplete", 1.0

    if re.match(r'^[!?.]+$', text):  # 문장부호만
        if "?" in text:  # 물음표는 정보 요청일 가능성이 높음
            if context and context.get("last_intent") == "info_request":
                return "info_request", 0.8  # 이전 정보 요청 의도 유지
            return "info_request", 0.7
        elif "!" in text:  # 느낌표는 UI 액션일 가능성이 높음
            if context and context.get("last_intent") == "ui_action":
                return "ui_action", 0.8  # 이전 UI 액션 의도 유지
            return "ui_action", 0.7
        return "punctuation", 1.0

    if re.match(r'^[ㅋㅎㅠㅜ]+$', text):  # 이모티콘
        if context and context.get("last_intent"):
            # 이모티콘이 긍정/부정을 나타내는 경우
            if text.startswith("ㅋ") or text.startswith("ㅎ"):
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.8  # 이전 의도 유지 (높은 신뢰도)
                return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
            elif text.startswith("ㅠ") or text.startswith("ㅜ"):
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
                return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
            return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
        return "emotion", 1.0

    if re.match(r'^\d+$', text):  # 숫자만
        if context:
            if context.get("last_intent") == "calc":
                return "calc", 0.9  # 계산 의도 유지 (높은 신뢰도)
            elif context.get("last_intent") in ["info_request", "ui_action"]:
                # 숫자가 선택이나 입력을 나타내는 경우
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.8  # 이전 의도 유지 (높은 신뢰도)
                return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
        return "number", 1.0

    if re.match(r'^[!@#$%^&*()_+=\-\[\]{}|\\:;"\'<>,.?/~`]+$', text):  # 특수문자만
        if context and context.get("last_intent"):
            # 특수문자가 긍정/부정을 나타내는 경우
            if text in ["!", "?", ".."]:
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
                return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
            return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
        return "special", 1.0

    # 3. 혼합 의도 체크
    is_mixed, intents, parts, confidence = detect_mixed_intent(text)
    if is_mixed:
        return "mixed", confidence

    # 4. 의도 키워드 체크
    has_info, has_action = get_intent_keywords(text)
    if has_info and has_action:
        return "mixed", 0.8
    elif has_info:
        return "info_request", 0.9
    elif has_action:
        return "ui_action", 0.9

    # 5. 단순 응답 체크
    if text in simple_responses:
        response_type = simple_responses[text]
        # 이전 의도가 있는 경우
        if context and context.get("last_intent"):
            last_intent = context["last_intent"]
            if response_type in ["confirm", "deny"]:
                # 이전 의도의 신뢰도 체크
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return last_intent, 0.8  # 이전 의도 유지 (높은 신뢰도)
                return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
        return response_type, 1.0

    if text in emotion_responses:
        response_type = emotion_responses[text]
        # 이전 의도가 있는 경우
        if context and context.get("last_intent"):
            last_intent = context["last_intent"]
            if response_type in ["laugh", "happy", "sad", "annoyed", "surprise", "confusion"]:
                # 이전 의도의 신뢰도 체크
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
                return last_intent, 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
        return response_type, 1.0

    if text in confirmation_responses:
        response_type = confirmation_responses[text]
        # 이전 의도가 있는 경우
        if context and context.get("last_intent"):
            last_intent = context["last_intent"]
            if response_type in ["confirm", "deny", "unknown"]:
                # 이전 의도의 신뢰도 체크
                last_confidence = context.get("last_confidence", 0.0)
                if last_confidence >= 0.8:
                    return last_intent, 0.8  # 이전 의도 유지 (높은 신뢰도)
                return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
        return response_type, 1.0

    # 6. 문맥 기반 체크
    if context:
        last_intent = context.get("last_intent", "")
        last_action = context.get("last_action", "")
        last_topic = context.get("last_topic", "")
        last_confidence = context.get("last_confidence", 0.0)

        # 이전 의도가 있고 현재 입력이 짧은 경우
        if last_intent and len(text) <= 2:
            # 짧은 입력이 긍정/부정을 나타내는 경우
            if text in ["응", "어", "네", "아니"]:
                if last_confidence >= 0.8:
                    return last_intent, 0.8  # 이전 의도 유지 (높은 신뢰도)
                return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
            elif text in ["ㅇ", "ㄴ"]:
                if last_confidence >= 0.8:
                    return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
                return last_intent, 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
            return last_intent, 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)

        # 이전 액션이 있고 현재 입력이 관련 키워드를 포함하는 경우
        if last_action:
            action_keywords = [
                # 기본 액션
                "다시", "취소", "확인", "저장", "삭제", "수정", "이전", "다음",

                # UI 조작
                "실행", "적용", "처리", "완료", "중단", "재시작", "새로고침",

                # 네비게이션
                "뒤로", "앞으로", "처음으로", "마지막으로", "위로", "아래로",

                # 특수 액션
                "되돌리기", "복원", "초기화", "리셋", "업데이트", "동기화",

                # 추가 액션
                "선택", "입력", "클릭", "체크", "해제", "닫기", "열기",
                "추가", "제거", "변경", "이동", "보기", "숨기기", "표시"
            ]
            if any(kw in text for kw in action_keywords):
                return "ui_action", 0.8

        # 이전 주제가 있고 현재 입력이 관련 키워드를 포함하는 경우
        if last_topic:
            topic_keywords = [
                # 지시대명사
                "그거", "이거", "저거", "그것", "이것", "저것", "그", "이", "저",

                # 연결어
                "그래서", "그러면", "그렇다면", "그럼", "그리고", "그런데",
                "그러니까", "그래도", "그러다가", "그러고", "그리하여",

                # 지시부사
                "거기", "여기", "저기", "그곳", "이곳", "저곳",
                "그쪽", "이쪽", "저쪽", "그리", "이리", "저리",

                # 시간 관련
                "그때", "이때", "저때", "그동안", "이제", "아까",
                "방금", "조금전", "이전", "다음", "이후", "그후"
            ]
            if any(kw in text for kw in topic_keywords):
                if last_confidence >= 0.8:
                    return last_intent, 0.7  # 이전 의도 유지 (낮은 신뢰도)
                return last_intent, 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)

    # 7. 짧은 입력 체크
    if len(text) <= 2:
        if context and context.get("last_intent"):
            # 짧은 입력이 긍정/부정을 나타내는 경우
            if text in ["응", "어", "네", "아니"]:
                if last_confidence >= 0.8:
                    return context["last_intent"], 0.8  # 이전 의도 유지 (높은 신뢰도)
                return context["last_intent"], 0.7  # 이전 의도 유지 (낮은 신뢰도)
            return context["last_intent"], 0.6  # 이전 의도 유지 (매우 낮은 신뢰도)
        return "short", 1.0

    return "unknown", 0.5

def is_simple_response(text: str, context: dict = None) -> bool:
    """단순 응답인지 확인"""
    response_type = get_response_type(text)

    # 1. 명확한 의도가 있는 경우
    if response_type in ["info_request", "ui_action", "mixed"]:
        return False

    # 2. 컨텍스트 기반 처리
    if context:
        last_intent = context.get("last_intent", "")
        if last_intent:
            # 이전 의도가 있는 경우, 단순 응답/감정 표현은 유효한 응답으로 처리
            if response_type in ["simple_confirm", "formal_confirm", "emotion"]:
                return False

    # 3. 기타 케이스
    return response_type in [
        "empty", "incomplete", "punctuation", "number",
        "special", "short", "unknown"
    ]

def is_valid_input(text: str) -> bool:
    """유효한 입력인지 확인"""
    # 1. 빈 입력 체크
    if not text or text.isspace():
        return False

    # 2. 특수문자/이모지만 있는 경우 체크
    text_clean = re.sub(r'[^\w\s]', '', text)
    if not text_clean:
        return False

    # 3. 한글 자음/모음만 있는 경우 체크
    if all(c in 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ' for c in text):
        return False

    return True

def route_by_intent(state: AgentState) -> str:
    """의도에 따른 라우팅 함수"""
    try:
        # 최종 의도 확인
        intent = state.get("final_intent", state.get("intent", "chat"))
        confidence = state.get("confidence", 0.0)
        user_input = state.get("user_input", "").strip()

        # 1. 입력 유효성 검사
        if not is_valid_input(user_input):
            return "fallback"

        # 2. 단순 응답 처리
        if is_simple_response(user_input):
            # 이전 대화 컨텍스트 확인
            prev_intent = state.get("conversation_history", [{}])[-1].get("intent", "")
            if prev_intent:
                return prev_intent  # 이전 의도 유지
            return "fallback"

        # 3. 신뢰도 체크
        if confidence < 0.5:
            return "fallback"

        # 혼합 의도 처리
        if intent == "mixed":
            return "mixed_intent_handler"

        # 일반 의도 처리
        routing_map = {
            "info_request": "info_handler",
            "ui_action": "action_handler",
            "search": "web_search",
            "calc": "calculator",
            "recruit": "recruitment",
            "db": "database_query",
            "chat": "fallback"
        }

        next_node = routing_map.get(intent, "fallback")
        print(f"[LangGraph] 라우팅: {intent} → {next_node}")
        return next_node

    except Exception as e:
        print(f"[LangGraph] 라우팅 오류: {str(e)}")
        return "fallback"

def create_langgraph_workflow():
    """LangGraph 워크플로우 생성"""
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph 라이브러리가 설치되지 않았습니다.")

    # 워크플로우 그래프 생성
    workflow = StateGraph(AgentState)

    # 1. 의도 분류 및 검증 노드
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("intent_revalidation", intent_revalidation_node)
    workflow.add_node("mixed_intent_handler", mixed_intent_handler_node)

    # 2. 정보 처리 노드
    workflow.add_node("info_handler", info_handler_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("calculator", calculator_node)
    workflow.add_node("database_query", database_query_node)

    # 3. UI 액션 노드
    workflow.add_node("action_handler", action_handler_node)
    workflow.add_node("page_navigator", page_navigator_node)
    workflow.add_node("ui_controller", ui_controller_node)

    # 4. 도메인 특화 노드
    workflow.add_node("recruitment", recruitment_node)
    workflow.add_node("resume_analyzer", resume_analyzer_node)

    # 5. 유틸리티 노드
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("response_formatter", response_formatter_node)

    # 기본 플로우: 의도 분류 → 재검증 → 처리 → 응답 포매팅
    workflow.add_edge("intent_detection", "intent_revalidation")

    # 재검증 노드에서 조건부 라우팅
    workflow.add_conditional_edges(
        "intent_revalidation",
        route_by_intent,
        {
            # 정보 요청 플로우
            "info_request": "info_handler",
            "search": "web_search",
            "calc": "calculator",
            "db": "database_query",

            # UI 액션 플로우
            "ui_action": "action_handler",
            "page_action": "page_navigator",
            "ui_control": "ui_controller",

            # 혼합 의도 플로우
            "mixed": "mixed_intent_handler",

            # 도메인 특화 플로우
            "recruit": "recruitment",
            "resume": "resume_analyzer",

            # 폴백
            "fallback": "fallback"
        }
    )

    # 처리 노드에서 응답 포매터로 연결
    for node in [
        "info_handler", "web_search", "calculator", "database_query",
        "action_handler", "page_navigator", "ui_controller",
        "recruitment", "resume_analyzer", "mixed_intent_handler",
        "fallback"
    ]:
        workflow.add_edge(node, "response_formatter")

    # 응답 포매터에서 종료
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
