import json
import re
import random
from urllib import request as urlreq

API = "http://localhost:8000/api/langgraph-agent/chat"

GENERAL_PROMPTS = [
    "날씨가 너무 더워", "오늘 컨디션 안 좋아", "퇴근하고 뭐할까", "너무 피곤하다",
    "점심 메뉴 추천해줘", "회의 너무 길었어", "기분이 꿀꿀해", "주말에 뭐하면 좋을까",
    "커피를 너무 많이 마신 듯", "오늘은 유난히 바쁘네", "어제 잠을 잘 못 잤어",
    "산책 나갈까 고민 중", "바닷가 가고 싶다", "새로운 운동 추천해줘", "집중이 안 돼",
    "코드 리뷰가 너무 많아", "동기부여가 필요해", "오늘 일정 정리 좀 도와줘",
    "기분전환이 필요해", "책 한 권 추천해줘", "나 상처받았는데", "회사 일이 어렵네",
    "깊은 한숨만 나온다", "휴식이 필요해", "스트레스 푸는 방법 알려줘",
    "살짝 긴장돼", "약속 시간 늦겠어", "할 일이 산더미야", "도움 좀 줄래?",
    "요즘 취미가 필요해", "아침에 늦잠 잤어", "운동 루틴 추천", "식단 어떻게 짜지?",
    "생산성 올리는 팁", "멘탈 관리 팁", "집중 훈련법", "시간 관리법",
    "마감이 촉박해", "해야할 게 너무 많아", "나 좀 응원해줘", "이직 고민 중이야",
    "프로젝트가 막혔어", "아이디어가 안 떠올라", "머리가 지끈거려", "마음이 무겁다",
    "대화를 좀 하고 싶어", "잡담하자", "ㅎㅇ", "ㅂㅇ", "하하 재밌네"
]

TOOL_NAV_PROMPTS = [
    "지원자 관리 페이지로 이동해줘", "이력서 페이지 열어", "면접 캘린더로 가자",
    "채용공고 페이지로 이동", "포트폴리오 페이지로 가", "자소서 검증 페이지 열기",
    "설정 페이지로 이동해줘", "users 페이지 열어", "대시보드로 이동", "interview 페이지로 가",
]
TOOL_DOM_PROMPTS = [
    "지원자 추가 버튼 클릭해줘", "검색창에 '홍길동' 입력해줘", "필터 적용 버튼 눌러",
    "목록 새로고침 눌러줘", "지원자 상세 열기", "삭제 버튼 누르지마(테스트)",
    "UI 목록 보여줘", "현재 페이지 UI 인덱스 덤프", "스크롤 아래로", "선택 박스 옵션 변경"
]


def post_chat(text, ctx=None, sid=None):
    payload = {
        "user_input": text,
        "session_id": sid or "",
        "context": ctx or {"current_page": "/", "user_agent": "eval-script"}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlreq.Request(API, data=data, headers={"Content-Type": "application/json"})
    with urlreq.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def count_sentences(s: str) -> int:
    return len([x for x in re.split(r"[.!?\n]+", s) if x.strip()])


def looks_empathic(s: str) -> bool:
    return any(k in s for k in ["이해", "그럴 수", "도와", "괜찮", "공감", "응원", "도움"])  # 간단 규칙


def is_structured_react(s: str) -> bool:
    try:
        obj = json.loads(s)
        return isinstance(obj, dict) and obj.get("type") == "react_agent_response"
    except Exception:
        return False


def run():
    random.seed(42)
    # 50 일반 + 50 툴(네비/DOM을 가능한 범위 내에서 반복 샘플)
    general = random.sample(GENERAL_PROMPTS, min(50, len(GENERAL_PROMPTS)))
    def sample_with_replacement(lst, k):
        if not lst:
            return []
        return [random.choice(lst) for _ in range(k)]
    tools = sample_with_replacement(TOOL_NAV_PROMPTS, 25) + sample_with_replacement(TOOL_DOM_PROMPTS, 25)

    metrics = {
        "general_total": 0,
        "general_avg_sentences": 0.0,
        "general_empathy_rate": 0.0,
        "general_short_reply_rate": 0.0,
        "tool_total": 0,
        "tool_structured_rate": 0.0,
        "tool_used_rate": 0.0,
        "false_navigation": 0,
        "errors": 0,
    }
    sid = ""

    # GENERAL
    emp_hits = 0
    sent_sum = 0
    short_cnt = 0
    for q in general:
        try:
            r = post_chat(q, {"current_page": "/"}, sid)
            sid = r.get("session_id", sid)
            msg = r.get("message", "")
            n = count_sentences(msg)
            sent_sum += n
            if n <= 1:
                short_cnt += 1
            if looks_empathic(msg):
                emp_hits += 1
            metrics["general_total"] += 1
        except Exception:
            metrics["errors"] += 1

    metrics["general_avg_sentences"] = round(sent_sum / max(metrics["general_total"], 1), 2)
    metrics["general_empathy_rate"] = round(emp_hits / max(metrics["general_total"], 1), 2)
    metrics["general_short_reply_rate"] = round(short_cnt / max(metrics["general_total"], 1), 2)

    # TOOLS
    structured = 0
    tool_used = 0
    false_nav = 0
    for q in tools:
        try:
            ctx = {
                "current_page": "/",
                "is_navigation_candidate": any(k in q for k in ["이동", "가", "열어", "open", "navigate", "페이지"]),
            }
            r = post_chat(q, ctx, sid)
            sid = r.get("session_id", sid)
            msg = r.get("message", "")
            tu = r.get("tool_used")
            s_ok = is_structured_react(msg)
            structured += 1 if s_ok else 0
            tool_used += 1 if tu else 0
            if ("상세" in q or "정보" in q) and s_ok:
                try:
                    o = json.loads(msg)
                    pa = o.get("page_action") or {}
                    if pa.get("action") == "navigate":
                        false_nav += 1
                except Exception:
                    pass
            metrics["tool_total"] += 1
        except Exception:
            metrics["errors"] += 1

    metrics["tool_structured_rate"] = round(structured / max(metrics["tool_total"], 1), 2)
    metrics["tool_used_rate"] = round(tool_used / max(metrics["tool_total"], 1), 2)
    metrics["false_navigation"] = false_nav

    print("\n=== Agent Evaluation (100 runs) ===")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()


