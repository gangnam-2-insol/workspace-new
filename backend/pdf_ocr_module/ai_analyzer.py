from __future__ import annotations

import re
from typing import Any, Dict, List
import json
import os
import asyncio

from .config import Settings

# OpenAIService는 선택적
try:
    from openai_service import OpenAIService  # async: generate_response(prompt) -> str
except ImportError:
    OpenAIService = None

# 동기식 OpenAI 클라이언트 (이벤트 루프 충돌 방지용)
try:
    from openai import OpenAI
    sync_client = OpenAI()
except ImportError:
    sync_client = None


# ========= 공통 유틸 =========

def clean_text_content(text: str) -> str:
    """텍스트를 정리하고 정규화 (OCR 품질 개선)."""
    if not text:
        return ""
    
    # 1. 불필요한 특수문자 제거 (한글, 영문, 숫자, 기본 문장부호만 유지)
    text = re.sub(r'[^\w\s\.,!?;:()\-_@#$%&*+=<>\[\]{}|\\/가-힣]', '', text)
    
    # 2. 다중 공백 정리
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 3. 과한 빈 줄 정리
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 4. 의미없는 반복 패턴 제거
    text = re.sub(r'(프로젝트에서 맡은 주요업무를 적어주세요\s*)+', '프로젝트에서 맡은 주요업무를 적어주세요', text)
    text = re.sub(r'(텍스트를 입력해주세요\s*)+', '텍스트를 입력해주세요', text)
    
    # 5. 불필요한 숫자 패턴 정리 (연도는 유지)
    text = re.sub(r'\b\d{1,2}\s*[~-]\s*\d{1,2}\s*[~-]\s*\d{4}\b', '', text)  # 날짜 범위 제거
    text = re.sub(r'\b\d{4}\s*[~-]\s*\d{4}\b', '', text)  # 연도 범위 제거
    
    # 6. 의미없는 단어들 제거
    meaningless_words = [
        '프로젝트에서 맡은 주요업무를 적어주세요',
        '텍스트를 입력해주세요',
        '사용한',
        '사이즈는',
        '행간은',
        '자간은',
        '입니다',
        '입력해주세요'
    ]
    for word in meaningless_words:
        text = re.sub(rf'\b{re.escape(word)}\b', '', text, flags=re.IGNORECASE)
    
    # 7. 연속된 공백과 줄바꿈 정리
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def extract_basic_info(text: str) -> Dict[str, Any]:
    """기본 정보 추출 (AI 우선, 규칙 기반 폴백)."""
    info = {
        "emails": [],
        "phones": [],
        "dates": [],
        "numbers": [],
        "urls": [],
        "names": [],
        "positions": [],
        "companies": [],
        "education": [],
        "skills": [],
        "addresses": [],
    }
    
    # 동기식 OpenAI 클라이언트로 AI 분석 시도
    if sync_client:
        try:
            ai_prompt = f"""다음은 OCR로 추출한 이력서 텍스트입니다. OCR 과정에서 일부 텍스트가 깨졌을 수 있으니, 가능한 정보만 추출해주세요.

텍스트:
{text}

다음 정보들을 JSON 형태로 추출해주세요:
1. 이름 (가장 가능성이 높은 하나의 이름만, 한글 이름 우선)
2. 이메일 주소 (정확한 이메일 형식)
3. 전화번호 (010-1234-5678 형식)
4. 직책/포지션 (개발자, 디자이너, 기획자 등)
5. 회사명 (미리캔버스, 미리물산 등)
6. 학력 정보 (미리대학교 시각디자인학과 등)
7. 주요 스킬/기술 (Adobe Photoshop, Illustrator 등)
8. 주소 (서울 구로구 등)

주의사항:
- OCR 오류로 인해 일부 텍스트가 깨져있을 수 있습니다
- 확실하지 않은 정보는 빈 문자열("")로 설정하세요
- 한글 이름과 회사명을 우선적으로 찾아주세요
- 기술 스킬은 Adobe 제품군, 프로그래밍 언어 등을 찾아주세요

응답은 반드시 다음과 같은 JSON 형태로만 작성해주세요:
{{
    "name": "추출된 이름",
    "email": "추출된 이메일",
    "phone": "추출된 전화번호",
    "position": "추출된 직책",
    "company": "추출된 회사명",
    "education": "추출된 학력",
    "skills": "추출된 스킬",
    "address": "추출된 주소"
}}"""

            response = sync_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 이력서 분석 AI야. 텍스트에서 정보를 정확히 추출해."},
                    {"role": "user", "content": ai_prompt}
                ],
                max_tokens=1000
            )
            
            # JSON 파싱 시도
            try:
                content = response.choices[0].message.content.strip()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    ai_data = json.loads(json_str)
                    
                    # AI 결과를 info에 매핑
                    if ai_data.get('name'):
                        info["names"] = [ai_data['name']]
                    if ai_data.get('email'):
                        info["emails"] = [ai_data['email']]
                    if ai_data.get('phone'):
                        info["phones"] = [ai_data['phone']]
                    if ai_data.get('position'):
                        info["positions"] = [ai_data['position']]
                    if ai_data.get('company'):
                        info["companies"] = [ai_data['company']]
                    if ai_data.get('education'):
                        info["education"] = [ai_data['education']]
                    if ai_data.get('skills'):
                        info["skills"] = [ai_data['skills']]
                    if ai_data.get('address'):
                        info["addresses"] = [ai_data['address']]
                    
                    print(f"AI 분석 결과: {ai_data}")
                    return info
            except Exception as e:
                print(f"AI JSON 파싱 실패: {e}")
        except Exception as e:
            print(f"AI 분석 실패: {e}")
    
    # AI 실패 시 규칙 기반 분석으로 폴백

    # 이메일
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    info["emails"] = re.findall(email_pattern, text)

    # 전화번호(간단)
    phone_pattern = r'(\+?\d[\d\s\-()]{9,})'
    info["phones"] = [p.strip() for p in re.findall(phone_pattern, text)]

    # 날짜
    date_pattern = r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}'
    info["dates"] = re.findall(date_pattern, text)

    # URL
    url_pattern = r'https?://[^\s]+'
    info["urls"] = re.findall(url_pattern, text)

    # 이름(한국어 2~4자 후보)
    name_candidates = re.findall(r'(?<![가-힣])([가-힣]{2,4})(?![가-힣])', text)
    # 과잉 추출 방지: 흔한 섹션/용어 제외
    blacklist = {"주소","전화","이메일","연락처","학력","경력","스킬","프로젝트","자격증","수상"}
    info["names"] = [n for n in set(name_candidates) if n not in blacklist]

    # 직책
    pos_pattern = r'(팀장|과장|대리|사원|부장|이사|대표|CEO|CTO|CFO|PM|PL|개발자|엔지니어|디자이너|기획자|마케터)'
    info["positions"] = list(set(re.findall(pos_pattern, text)))

    # 회사명(간단)
    comp_pattern = r'([가-힣A-Za-z0-9&\.]+)(주식회사|㈜|Corp|Inc|Ltd|LLC|회사|그룹|스튜디오|랩|연구소)'
    info["companies"] = [m[0] for m in re.findall(comp_pattern, text)]

    # 학력(간단)
    edu_pattern = r'([가-힣A-Za-z\s]+)(대학교|University|College|고등학교|High School)'
    info["education"] = [''.join(m) for m in re.findall(edu_pattern, text)]

    # 스킬(키워드 매칭)
    skill_keywords = r'(Python|Java|JavaScript|TypeScript|React|Vue|Angular|Node\.js|Django|Flask|Spring|MySQL|PostgreSQL|MongoDB|AWS|Azure|Docker|Kubernetes|Git|Linux)'
    info["skills"] = list(set(re.findall(skill_keywords, text, re.IGNORECASE)))

    # 주소(간단)
    addr_patterns = [
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣0-9]+(동|로|길)[^\n,)]*)',
        r'([가-힣]+도\s+[가-힣]+시\s+[가-힣]+구[^\n,)]*)',
    ]
    addresses = []
    for pat in addr_patterns:
        addresses += [m[0] if isinstance(m, tuple) else m for m in re.findall(pat, text)]
    info["addresses"] = list({a.strip() for a in addresses if a.strip()})

    # 정리
    for k, v in info.items():
        if isinstance(v, list):
            info[k] = sorted(list({x.strip() for x in v if str(x).strip()}), key=len, reverse=True)

    return info


def generate_summary(text: str) -> str:
    if not text:
        return ""
    sentences = [s.strip() for s in re.split(r'[.!?]+\s*', text) if len(s.strip()) > 10]
    if not sentences:
        return text[:200] + ("..." if len(text) > 200 else "")
    if len(sentences) <= 3:
        return " ".join(sentences)
    return ". ".join([sentences[0], sentences[len(sentences)//2], sentences[-1]]) + "."


def extract_keywords(text: str) -> List[str]:
    """OCR로 뽑은 텍스트에서 키워드를 추출 (AI 우선, 규칙 기반 폴백)"""
    if not text:
        return []
    
    # 동기식 OpenAI 클라이언트 사용
    if sync_client:
        try:
            response = sync_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 OCR 분석 보조 AI야. OCR로 추출된 텍스트에서 의미있는 키워드만 추출해. 깨진 텍스트나 의미없는 단어는 제외하고, 기술 스킬, 직무, 회사명, 학력 등 중요한 정보만 키워드로 추출해."},
                    {"role": "user", "content": f"다음 OCR 텍스트에서 중요한 키워드 10개를 추출해주세요:\n\n{text}\n\n추출할 키워드 유형:\n- 기술 스킬 (Adobe Photoshop, Illustrator 등)\n- 직무 (디자이너, 개발자 등)\n- 회사명 (미리캔버스 등)\n- 학력 (미리대학교 등)\n- 자격증 (TOEIC, 컬러리스트 등)\n\n응답은 반드시 JSON 형태로만 작성해주세요:\n{{\"keywords\": [\"키워드1\", \"키워드2\", ...]}}"}
                ],
                max_tokens=300
            )
            
            # JSON 파싱 시도
            try:
                import json
                content = response.choices[0].message.content.strip()
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    data = json.loads(json_str)
                    keywords = data.get("keywords", [])
                    if keywords:
                        return keywords[:10]  # 최대 10개
            except Exception as e:
                print(f"AI 키워드 JSON 파싱 실패: {e}")
        except Exception as e:
            print(f"AI 키워드 추출 실패: {e}")
    
    # AI 실패 시 규칙 기반 키워드 추출
    bag = [
        "이력서","자기소개서","경력","학력","스킬","프로젝트","개발","데이터","AI","배포","운영",
        "resume","cv","experience","education","skills","project","development","database","server",
    ]
    found = []
    low = text.lower()
    for kw in bag:
        if (kw.isascii() and kw in low) or (not kw.isascii() and kw in text):
            found.append(kw)
    return list(dict.fromkeys(found))[:10]  # 순서 보존 중복제거


def detect_document_type(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["이력서","resume","cv","경력사항"]): return "resume"
    if any(w in t for w in ["자기소개서","cover letter","소개서"]): return "cover_letter"
    if any(w in t for w in ["보고서","report","분석","analysis"]): return "report"
    if any(w in t for w in ["계약서","contract","협약","agreement"]): return "contract"
    if any(w in t for w in ["매뉴얼","manual","가이드","guide"]): return "manual"
    return "general"


def extract_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    pats = {
        "개인정보": r"(개인정보|Personal Information|이름|Name)\s*[:\-]?\s*([^\n]+)",
        "학력": r"(학력|Education|학위|Degree)\s*[:\-]?\s*([^\n]+)",
        "경력": r"(경력|Experience|Work History|업무경험)\s*[:\-]?\s*([^\n]+)",
        "스킬": r"(스킬|Skills|기술|Technology)\s*[:\-]?\s*([^\n]+)",
        "프로젝트": r"(프로젝트|Project)\s*[:\-]?\s*([^\n]+)",
    }
    for k, pat in pats.items():
        m = re.findall(pat, text, re.IGNORECASE)
        if m:
            sections[k] = m[0][1] if isinstance(m[0], tuple) else m[0]
    return sections


def extract_entities(text: str) -> Dict[str, List[str]]:
    ents = {"organizations": [], "locations": [], "dates": [], "numbers": []}
    ents["dates"] = re.findall(r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}', text)
    ents["numbers"] = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    # 간단 추출 (영문 기관명)
    ents["organizations"] = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    return ents


def extract_structured_data(text: str) -> Dict[str, Any]:
    return {
        "document_type": detect_document_type(text),
        "sections": extract_sections(text),
        "entities": extract_entities(text),
    }


# ========= AI 경로 =========

async def analyze_with_ai(text: str, settings: Settings) -> Dict[str, Any]:
    """OpenAIService를 사용(가능하면)하고, 실패 시 규칙 기반으로 폴백."""
    try:
        if not OpenAIService:
            raise RuntimeError("OpenAIService 모듈을 찾을 수 없음")

        service = OpenAIService(model_name="gpt-4o-mini")

        basic_info_prompt = f"""다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

텍스트:
{text}

다음 정보들을 JSON 형태로 추출해주세요:
1. 이름 (가장 가능성이 높은 하나의 이름만)
2. 이메일 주소
3. 전화번호
4. 직책/포지션
5. 회사명
6. 학력 정보
7. 주요 스킬/기술
8. 주소

응답은 반드시 다음과 같은 JSON 형태로만 작성해주세요:
{{
    "name": "추출된 이름",
    "email": "추출된 이메일",
    "phone": "추출된 전화번호",
    "position": "추출된 직책",
    "company": "추출된 회사명",
    "education": "추출된 학력",
    "skills": "추출된 스킬",
    "address": "추출된 주소"
}}
만약 특정 정보를 찾을 수 없다면 해당 필드는 빈 문자열("")로 설정해주세요.
"""

        summary_prompt = f"""다음 이력서 텍스트를 간단하고 명확하게 요약해주세요:

{text}

요약은 다음을 포함해야 합니다:
- 지원자의 주요 경력과 전문 분야
- 핵심 스킬과 경험
- 학력 배경

2-3문장으로 간결하게 작성해주세요.
"""

        keywords_prompt = f"""다음 이력서 텍스트에서 중요한 키워드 10개를 추출해주세요:

{text}

추출할 키워드 유형:
- 기술 스킬 (예: Python, React, AWS)
- 직무 관련 용어 (예: 웹개발, 데이터분석, 프로젝트관리)
- 업계 관련 용어 (예: IT, 금융, 마케팅)

JSON 형태로 응답해주세요:
{{
    "keywords": ["키워드1", "키워드2", "키워드3", ...]
}}
"""

        # 동시에 호출
        basic_task = asyncio.create_task(service.generate_response(basic_info_prompt))
        summary_task = asyncio.create_task(service.generate_response(summary_prompt))
        keywords_task = asyncio.create_task(service.generate_response(keywords_prompt))

        basic_resp, summary_resp, keywords_resp = await asyncio.gather(
            basic_task, summary_task, keywords_task
        )

        # 파싱
        basic_info = {}
        try:
            s, e = basic_resp.find('{'), basic_resp.rfind('}') + 1
            if s != -1 and e > s:
                basic_info = json.loads(basic_resp[s:e])
        except Exception:
            basic_info = {}

        keywords: List[str] = []
        try:
            s, e = keywords_resp.find('{'), keywords_resp.rfind('}') + 1
            if s != -1 and e > s:
                kobj = json.loads(keywords_resp[s:e])
                keywords = kobj.get("keywords", [])
        except Exception:
            keywords = []

        return {
            "summary": summary_resp,
            "keywords": keywords,
            "structured_data": {
                "document_type": detect_document_type(text),
                "sections": extract_sections(text),
                "entities": extract_entities(text),
                "basic_info": basic_info,
            },
        }

    except Exception as e:
        # 폴백
        return {
            "summary": generate_summary(text),
            "keywords": extract_keywords(text),
            "structured_data": extract_structured_data(text),
            "error": str(e),
        }


# ========= 최상위 엔트리 =========

def analyze_text(text: str, settings: Settings) -> Dict[str, Any]:
    """텍스트를 분석하여 구조화된 정보를 추출 (완전 동기 버전)."""
    try:
        clean = clean_text_content(text)
        basic = extract_basic_info(clean)

        # 설정에 따라 AI 분석 실행 (동기식 함수들 사용)
        if getattr(settings, "index_generate_summary", True) or getattr(settings, "index_generate_keywords", True):
            # 동기식 AI 분석 함수들 사용
            summary = summarize_text(clean) if getattr(settings, "index_generate_summary", True) else ""
            keywords = extract_keywords(clean) if getattr(settings, "index_generate_keywords", True) else []
            
            # AI 분석 결과에서 더 정확한 basic_info 추출 시도
            ai_basic_info = {}
            try:
                # AI를 통한 더 정확한 정보 추출
                ai_prompt = f"""다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

텍스트:
{clean}

다음 정보들을 JSON 형태로 추출해주세요:
1. 이름 (가장 가능성이 높은 하나의 이름만, 한글 이름 우선)
2. 이메일 주소 (정확한 이메일 형식)
3. 전화번호 (010-1234-5678 형식)
4. 직책/포지션 (개발자, 디자이너, 기획자 등)

응답은 반드시 다음과 같은 JSON 형태로만 작성해주세요:
{{
    "name": "추출된 이름",
    "email": "추출된 이메일",
    "phone": "추출된 전화번호",
    "position": "추출된 직책"
}}
만약 특정 정보를 찾을 수 없다면 해당 필드는 빈 문자열("")로 설정해주세요."""

                if sync_client:
                    response = sync_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "너는 이력서 분석 AI야. 주어진 텍스트에서 개인정보를 정확히 추출해서 JSON 형태로 응답해."},
                            {"role": "user", "content": ai_prompt}
                        ],
                        max_tokens=300
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    # JSON 파싱
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        ai_basic_info = json.loads(json_match.group())
                        print(f"🤖 AI 분석 결과: {ai_basic_info}")
            except Exception as e:
                print(f"AI basic_info 추출 실패: {e}")
                ai_basic_info = {}
            
            ai = {
                "summary": summary,
                "keywords": keywords,
                "structured_data": {
                    "document_type": detect_document_type(clean),
                    "sections": extract_sections(clean),
                    "entities": extract_entities(clean),
                    "basic_info": {**basic, **ai_basic_info},  # 규칙 기반 + AI 결과 병합
                }
            }
        else:
            ai = {"summary": "", "keywords": [], "structured_data": {}}

        # 최종 결과에서 basic_info를 최상위 레벨에도 포함
        final_result = {
            "clean_text": clean,
            "basic_info": {**basic, **ai.get("structured_data", {}).get("basic_info", {})},  # 최상위 레벨
            "summary": ai.get("summary", ""),
            "keywords": ai.get("keywords", []),
            "structured_data": ai.get("structured_data", {}),
        }
        
        print(f"📊 최종 분석 결과 - basic_info: {final_result['basic_info']}")
        
        return final_result
        
    except Exception as e:
        print(f"analyze_text 오류: {e}")
        return {
            "clean_text": text,
            "basic_info": {},
            "summary": "",
            "keywords": [],
            "structured_data": {},
            "error": str(e),
        }
# --- 기존 함수 이름 호환용 래퍼들 ---

def summarize_text(text: str) -> str:
    """OCR로 뽑은 텍스트를 GPT-4o-mini로 요약 (동기식)"""
    if not text:
        return ""
    
    # 동기식 OpenAI 클라이언트 사용
    if sync_client:
        try:
            response = sync_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 OCR 분석 보조 AI야. OCR로 추출된 텍스트에서 의미있는 정보만 추출해서 간결하게 요약해. 깨진 텍스트는 무시하고 확실한 정보만 포함해."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI 요약 실패: {e}")
            # AI 실패 시 규칙 기반 요약으로 폴백
            return generate_summary(text)
    else:
        # OpenAI 클라이언트가 없으면 규칙 기반 요약
        return generate_summary(text)

def extract_fields(text: str) -> Dict[str, Any]:
    """기존 import 호환: extract_basic_info() 래핑"""
    return extract_basic_info(text)

def clean_text(text: str) -> str:
    """기존 import 호환: clean_text_content() 래핑"""
    return clean_text_content(text)
