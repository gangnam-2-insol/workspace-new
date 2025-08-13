from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Dict, List, Optional

from .config import Settings


def _normalize_unicode(text: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKC", text)


def _fix_hyphen_linebreaks(text: str) -> str:
    return re.sub(r"-\n\s*", "", text)


def _fix_spaces(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


COMMON_CONFUSIONS = [
    (r"(?<=\b)[eE](?=\b)", "c"),
    (r"\b0(?=[A-Za-z])", "O"),
    (r"\b1(?=[A-Za-z])", "l"),
]


def _apply_confusion_fixes(text: str) -> str:
    for pat, repl in COMMON_CONFUSIONS:
        text = re.sub(pat, repl, text)
    return text


def _regex_repair(text: str) -> str:
    text = re.sub(r"([\w.-]+)\s*@\s*([\w.-]+)\s*\.\s*(\w+)", r"\1@\2.\3", text)
    text = re.sub(r"(\+?82)\s*-\s*0?\s*(\d{2})\s*-\s*(\d{3,4})\s*-\s*(\d{4})", r"+82-\2-\3-\4", text)
    return text


def clean_text(text: str) -> str:
    text = _normalize_unicode(text)
    text = _fix_hyphen_linebreaks(text)
    text = _apply_confusion_fixes(text)
    text = _regex_repair(text)
    text = _fix_spaces(text)
    return text


def _simple_summary(text: str, max_chars: int = 500) -> str:
    tidy = re.sub(r"\s+", " ", text).strip()
    return tidy[:max_chars] + ("..." if len(tidy) > max_chars else "")


def _simple_keywords(text: str, top_k: int = 10) -> List[str]:
    tokens = re.findall(r"[\w가-힣]{2,}", text.lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "are",
        "you",
        "from",
        "have",
        "your",
        "대한",
        "그리고",
        "있는",
        "있는지",
        "있다",
        "하는",
        "에서",
    }
    tokens = [t for t in tokens if t not in stop]
    common = Counter(tokens).most_common(top_k)
    return [w for w, _ in common]


def _analyze_with_openai(text: str, settings: Settings) -> Dict:
    text = clean_text(text)
    try:
        from openai import OpenAI
    except Exception:  # noqa: BLE001
        return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}

    if not settings.openai_api_key:
        return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}

    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    client = OpenAI()

    prompt = (
        "다음 문서 텍스트를 한국어로 간단히 요약하고, 핵심 키워드 5~10개를 추출해 주세요. "
        "JSON 형식으로만 응답하세요: {\"summary\": string, \"keywords\": string[]}.\n\n"
        f"문서:\n{text[:6000]}"
    )

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "당신은 유능한 문서 요약 도우미입니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        # JSON 파싱 시도
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            payload = json.loads(content[start : end + 1])
            return {
                "summary": payload.get("summary") or _simple_summary(text),
                "keywords": payload.get("keywords") or _simple_keywords(text),
            }
    except Exception:  # noqa: BLE001
        pass

    return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}


def _analyze_with_groq(text: str, settings: Settings) -> Dict:
    text = clean_text(text)
    try:
        from groq import Groq
    except Exception:  # noqa: BLE001
        return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}

    if not settings.groq_api_key:
        return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}

    os.environ.setdefault("GROQ_API_KEY", settings.groq_api_key)
    client = Groq(api_key=settings.groq_api_key)

    prompt = (
        "다음 문서 텍스트를 한국어로 간단히 요약하고, 핵심 키워드 5~10개를 추출해 주세요. "
        "JSON 형식으로만 응답하세요: {\"summary\": string, \"keywords\": string[]}.\n\n"
        f"문서:\n{text[:6000]}"
    )

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": "당신은 유능한 문서 요약 도우미입니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            payload = json.loads(content[start : end + 1])
            return {
                "summary": payload.get("summary") or _simple_summary(text),
                "keywords": payload.get("keywords") or _simple_keywords(text),
            }
    except Exception:  # noqa: BLE001
        pass

    return {"summary": _simple_summary(text), "keywords": _simple_keywords(text)}


def _extract_korean_name_ai(text: str, settings: Settings) -> Optional[str]:
    """LLM을 사용해 한국어 이름(2~4자)을 우선적으로 추출.

    - Groq(우선) 또는 OpenAI 사용 가능
    - 이메일 로컬파트 유추 금지, 호칭 제거, 여러 후보면 1개만
    - 실패 시 None 반환
    """
    cleaned = clean_text(text)[:6000]

    system_msg = "당신은 문서에서 사람 이름을 식별하는 어시스턴트입니다."
    user_msg = (
        "다음 문서에서 한국어 개인 이름(한글 2~4자)을 추출하세요.\n"
        "- 이메일 아이디나 도메인으로 이름을 유추하지 마세요.\n"
        "- 직책/호칭(님, 씨, 선생 등)은 제거하세요.\n"
        "- 여러 후보가 있으면 가장 가능성이 높은 1개만 고르세요.\n"
        "- 없다면 null을 반환하세요.\n"
        '반드시 JSON으로만 응답: {"name": string|null}\n\n'
        f"문서:\n{cleaned}"
    )

    # Groq 우선
    try:
        if settings.llm_provider.lower() == "groq" and settings.groq_api_key:
            from groq import Groq
            os.environ.setdefault("GROQ_API_KEY", settings.groq_api_key)
            client = Groq(api_key=settings.groq_api_key)
            resp = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.0,
            )
            content = (resp.choices[0].message.content or "").strip()
            i, j = content.find("{"), content.rfind("}")
            if i != -1 and j != -1:
                payload = json.loads(content[i : j + 1])
                name = payload.get("name")
                if isinstance(name, str) and re.fullmatch(r"[가-힣]{2,4}", name):
                    return name
                return None
    except Exception:
        pass

    # OpenAI 폴백
    try:
        if settings.openai_api_key:
            from openai import OpenAI
            os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
            client = OpenAI()
            resp = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.0,
            )
            content = (resp.choices[0].message.content or "").strip()
            i, j = content.find("{"), content.rfind("}")
            if i != -1 and j != -1:
                payload = json.loads(content[i : j + 1])
                name = payload.get("name")
                if isinstance(name, str) and re.fullmatch(r"[가-힣]{2,4}", name):
                    return name
                return None
    except Exception:
        pass

    return None

def analyze_text(text: str, settings: Settings) -> Dict:
    """문서를 요약하고 키워드를 추출합니다.

    OpenAI API 키가 설정되면 LLM을 사용하고, 아니면 간단한 휴리스틱을 사용합니다.
    """
    if settings.llm_provider.lower() == "groq" and settings.groq_api_key:
        return _analyze_with_groq(text, settings)
    if settings.openai_api_key:
        return _analyze_with_openai(text, settings)
    cleaned = clean_text(text)
    return {"summary": _simple_summary(cleaned), "keywords": _simple_keywords(cleaned), "clean_text": cleaned}


# 텍스트를 GPT나 LLM으로 분석: 요약, 키워드, 감정 등
def summarize_text(text: str) -> str:
    settings = Settings()
    if settings.llm_provider.lower() == "groq" and settings.groq_api_key:
        result = _analyze_with_groq(text, settings)
        return result.get("summary") or _simple_summary(text)
    if settings.openai_api_key:
        result = _analyze_with_openai(text, settings)
        return result.get("summary") or _simple_summary(text)
    return _simple_summary(clean_text(text))


def extract_keywords(text: str) -> List[str]:
    settings = Settings()
    if settings.llm_provider.lower() == "groq" and settings.groq_api_key:
        result = _analyze_with_groq(text, settings)
        return list(result.get("keywords") or _simple_keywords(text))
    if settings.openai_api_key:
        result = _analyze_with_openai(text, settings)
        return list(result.get("keywords") or _simple_keywords(text))
    return _simple_keywords(clean_text(text))


# 간단한 구조화 필드 추출기
def extract_fields(text: str) -> Dict:
    cleaned = clean_text(text)
    emails = list(dict.fromkeys(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", cleaned)))
    phones = list(
        dict.fromkeys(
            re.findall(r"(?:\+82-?\s?)?0?\d{1,2}-?\d{3,4}-?\d{4}", cleaned)
        )
    )
    # 날짜/기간 추정 (YYYY-MM / YYYY.MM / YYYY년MM월)
    periods = list(
        dict.fromkeys(
            re.findall(r"(?:19|20)\d{2}[./년\-]\s?(?:0?[1-9]|1[0-2])", cleaned)
        )
    )
    # 학교/학위 키워드 기반 단순 추출
    schools = list(dict.fromkeys(re.findall(r"[가-힣A-Za-z.&\s]{2,}(대학교|University)", cleaned)))
    degrees = list(dict.fromkeys(re.findall(r"학사|석사|박사|Bachelor|Master|PhD", cleaned, flags=re.I)))

    # 한국어 이름 추출 시도 (AI 우선)
    name: Optional[str] = None
    try:
        ai_name = _extract_korean_name_ai(cleaned, Settings())
        if ai_name:
            name = ai_name
    except Exception:
        pass
    # 1) 라벨 기반: "이름", "성명", "Name"
    m = re.search(r"(?:이름|성명|Name)\s*[:\-]?\s*([가-힣]{2,4})", cleaned, flags=re.I)
    if m:
        cand = m.group(1).strip()
        if 2 <= len(cand) <= 4:
            name = cand
    # 2) 문서 초반부 단독 한글 2~4자 라인
    if not name:
        head = "\n" + cleaned[:300]  # 앞부분만
        m2 = re.search(r"\n([가-힣]{2,4})\n", head)
        if m2:
            cand2 = m2.group(1).strip()
            if 2 <= len(cand2) <= 4:
                name = cand2
    # 3) 이메일 로컬파트가 한글일 경우
    if not name and emails:
        local = emails[0].split("@")[0]
        if re.fullmatch(r"[가-힣]{2,6}", local):
            name = local

    fields = {
        "name": name,
        "email": emails,
        "phone": phones,
        "schools": schools,
        "degrees": degrees,
        "periods": periods,
    }
    return fields



