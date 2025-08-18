from __future__ import annotations

import re
from typing import Any, Dict, List
import json
import os
from openai import AsyncOpenAI

from .config import Settings


async def analyze_text(text: str, settings: Settings) -> Dict[str, Any]:
    """텍스트를 분석하여 구조화된 정보를 추출합니다."""
    try:
        clean = clean_text_content(text)
        regex_basic = extract_basic_info(clean)

        # GPT 분석 시도(항상 시도하되 실패 시 안전 폴백)
        try:
            ai_analysis = await analyze_with_ai(clean, settings)
            print("GPT-4o-mini 분석 실행됨")
        except Exception as ai_error:
            print(f"GPT-4o-mini 분석 실패: {ai_error}")
            ai_analysis = {"summary": "", "keywords": [], "structured_data": {"entities": {}}}

        gpt_entities = ai_analysis.get("structured_data", {}).get("entities", {}) or {}
        has_gpt = any(v for v in gpt_entities.values())
        final_basic = gpt_entities if has_gpt else regex_basic

        print(f"최종 사용할 basic_info: {'GPT-4o-mini' if has_gpt else '정규식'}")
        if has_gpt:
            print(f"GPT-4o-mini 추출 결과: {gpt_entities}")
        else:
            print("GPT-4o-mini 결과가 비어있어 정규식 사용")

        return {
            "clean_text": clean,
            "basic_info": final_basic,
            "summary": ai_analysis.get("summary", ""),
            "keywords": ai_analysis.get("keywords", []),
            "structured_data": ai_analysis.get("structured_data", {})
        }
    except Exception as e:
        return {
            "clean_text": text,
            "basic_info": {},
            "summary": "",
            "keywords": [],
            "structured_data": {},
            "error": str(e)
        }


def clean_text_content(text: str) -> str:
    """텍스트를 정리하고 정규화합니다."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def extract_basic_info(text: str) -> Dict[str, Any]:
    """기본 정보를 추출합니다 (정규식 기반)."""
    try:
        # 이메일
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)

        # 전화번호(전체 매치 유지: 비캡처 그룹 사용)
        phone_patterns = [
            r'\b(?:010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)-\d{3,4}-\d{4}\b',
            r'\b(?:010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\s\d{3,4}\s\d{4}\b',
            r'\b(?:010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\.\d{3,4}\.\d{4}\b',
            r'\b(?:010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\d{7,8}\b',
        ]
        raw_phones: List[str] = []
        for p in phone_patterns:
            raw_phones.extend(re.findall(p, text))

        standardized_phones: List[str] = []
        for ph in raw_phones:
            digits = re.sub(r'[^\d]', '', ph)
            if len(digits) >= 9:
                if digits.startswith('010') and len(digits) >= 11:
                    standardized_phones.append(f"{digits[:3]}-{digits[3:7]}-{digits[7:11]}")
                elif digits.startswith('02') and len(digits) >= 9:
                    # 서울 국번 길이가 다양하므로 보수적으로 자름
                    mid = 3 if len(digits) == 9 else 4
                    standardized_phones.append(f"{digits[:2]}-{digits[2:2+mid]}-{digits[2+mid:2+mid+4]}")
                else:
                    # 지역번호 3자리 가정
                    standardized_phones.append(f"{digits[:3]}-{digits[3:7]}-{digits[7:11]}")
        phones = sorted(set(standardized_phones))

        # URL
        urls = re.findall(r'https?://[^\s)>\]}"\']+', text)

        # 이름(한국어)
        name_pattern = r'\b[가-힣]{2,3}\s*[가-힣]{1,2}\b'
        raw_names = re.findall(name_pattern, text)
        exclude_words = {
            '텍스트','입력','주세요','사용한','폰트','사이즈','행간','자간','리스트',
            '포토그래퍼','구로구','미리아파트','기능사','획득한','자격증','명칭',
            '산악하이킹','레고수집','최우수상','제작참여','프로젝트에','주요업무를',
            '회사명','프로젝트명','담당업무','대학교','고등학교','컬러리스트',
            '디자인컨설턴트','디지털로','미리캔버스','미리대학교','미리고등학교',
            '제작팀','팀','팀장','팀원','팀리더','팀매니저','프로젝트','프로젝트팀',
            '프로젝트매니저','프로젝트리더','프로젝트팀장'
        }
        names = [
            n.strip() for n in raw_names
            if len(n.strip()) >= 2
            and not any(w in n for w in exclude_words)
            and not any(ch.isdigit() for ch in n)
            and not n.strip().endswith(('구','로','사','트','상','를','에','명','무'))
        ]

        # 직책
        position_pattern = r'\b(사원|대리|과장|차장|부장|이사|대표|CEO|CTO|CFO|개발자|프로그래머|엔지니어|디자이너|매니저|팀장|리더|포토그래퍼|컬러리스트|디자인컨설턴트|프로젝트매니저|시스템관리자|데이터분석가|UX디자이너|UI디자이너|웹디자이너|그래픽디자이너|편집디자이너|일러스트레이터|사진작가|카피라이터|마케터|세일즈|영업|기획자|기획|연구원|연구자|교수|강사|선생님|교사)\b'
        positions = [p for p in re.findall(position_pattern, text) if len(p.strip()) >= 2]

        # 회사명
        company_pattern = r'\b[가-힣A-Za-z0-9]+(?:주식회사|㈜|Corp|Inc|Ltd|LLC|Co\.|회사|그룹|기업|스튜디오|랩|연구소|센터|아카데미|학교|대학교|고등학교|중학교|초등학교)\b'
        companies = re.findall(company_pattern, text)

        # 학력
        education_pattern = r'\b[가-힣A-Za-z\s]+(?:대학교|대학|고등학교|고교|중학교|초등학교|전문대학|대학원|석사|박사|학사|전문학사|고졸|중졸|초졸)\b'
        education = re.findall(education_pattern, text)

        # 기술 스킬
        skill_pattern = r'\b(Python|Java|JavaScript|React|Node\.js|SQL|MongoDB|AWS|Docker|Kubernetes|Git|Linux|HTML|CSS|TypeScript|Vue\.js|Angular|Spring|Django|Flask|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Android|iOS|Photoshop|Illustrator|Figma|Sketch|AutoCAD|Blender|Premiere Pro|After Effects|InDesign|Tableau|Power BI|TensorFlow|PyTorch|Scikit-learn|OpenCV|NumPy|Pandas|Matplotlib|Selenium|Postman|Swagger|GraphQL|REST|gRPC|WebSocket|WebRTC|Bootstrap|Tailwind CSS|Webpack|Babel|Jest|Cypress|Redis|Elasticsearch|PostgreSQL|MySQL|Oracle|Firebase|Vercel|Netlify|Heroku|Serverless|Ethereum|Solidity|Machine Learning|Deep Learning|AI|Data Science|Big Data|Hadoop|Spark|Airflow|CI/CD|Jenkins|GitLab|GitHub Actions|Terraform|Ansible|Kafka)\b'
        skills = re.findall(skill_pattern, text, re.IGNORECASE)

        # 주소(비캡처 그룹 + 전체 매치)
        address_pattern = (
            r'(?:[가-힣A-Za-z0-9\s]+(?:시|도|구|군|동|읍|면))'
            r'(?:\s*[가-힣A-Za-z0-9\s]*?(?:로|길|번길))?'
            r'(?:\s*\d+(?:-\d+)*)?'
            r'(?:\s*[가-힣A-Za-z0-9\s]*(?:아파트|빌라|빌딩|건물|상가|주택|단지))?'
            r'(?:\s*\d+(?:호|층|동|호수))?'
        )
        raw_addresses = re.findall(address_pattern, text)
        addresses = [
            a.strip() for a in raw_addresses
            if len(a.strip()) >= 6 and not any(x in a for x in ['텍스트','입력','주소지'])
        ]
        addresses.sort(key=len, reverse=True)

        # 날짜
        dates = re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{4}\.\d{1,2}\.\d{1,2}', text)

        return {
            "names": list(dict.fromkeys(names)),
            "emails": list(dict.fromkeys(emails)),
            "phones": phones,
            "positions": list(dict.fromkeys(positions)),
            "companies": list(dict.fromkeys(companies)),
            "education": list(dict.fromkeys(education)),
            "skills": list(dict.fromkeys(skills)),
            "addresses": list(dict.fromkeys(addresses)),
            "urls": list(dict.fromkeys(urls)),
            "dates": list(dict.fromkeys(dates)),
        }
    except Exception:
        return {
            "names": [], "emails": [], "phones": [], "positions": [],
            "companies": [], "education": [], "skills": [], "addresses": [],
            "urls": [], "dates": []
        }


def generate_simple_summary(text: str) -> str:
    if not text:
        return ""
    summary = text[:200].strip()
    return summary + ("..." if len(text) > 200 else "")


def extract_simple_keywords(text: str) -> List[str]:
    if not text:
        return []
    tech_keywords = [
        "Python","Java","JavaScript","React","Node.js","SQL","MongoDB",
        "AWS","Docker","Kubernetes","Git","Linux","HTML","CSS",
        "TypeScript","Vue.js","Angular","Spring","Django","Flask"
    ]
    found = [k for k in tech_keywords if k.lower() in text.lower()]
    return found[:10]


def extract_keywords(text: str) -> List[str]:
    return extract_simple_keywords(text)


def summarize_text(text: str) -> str:
    return generate_simple_summary(text)


def extract_fields(text: str) -> Dict[str, Any]:
    return extract_basic_info(text)


def clean_text(text: str) -> str:
    return clean_text_content(text)


async def analyze_with_ai(text: str, settings: Settings) -> Dict[str, Any]:
    """OpenAI GPT-4o-mini를 사용하여 텍스트를 분석합니다."""
    try:
        api_key = getattr(settings, "openai_api_key", None) or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")
        openai_client = AsyncOpenAI(api_key=api_key)

        basic_info_prompt = f"""
다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

텍스트:
{text}

다음 정보들을 JSON 형태로 추출해주세요:
1. 이름
2. 이메일
3. 전화번호(한국 표준형식)
4. 직책
5. 회사명
6. 학력
7. 스킬
8. 주소(가능하면 도로명/건물/호수 포함)

응답은 반드시 다음 JSON만 출력:
{{
    "name": "…",
    "email": "…",
    "phone": "…",
    "position": "…",
    "company": "…",
    "education": "…",
    "skills": "…",
    "address": "…"
}}
없으면 빈 문자열("").
"""

        summary_prompt = f"""
다음 이력서 텍스트를 2-3문장으로 간결하게 요약해주세요:
{text}
"""

        keywords_prompt = f"""
다음 이력서 텍스트에서 중요한 키워드 10개를 JSON으로 추출:
텍스트:
{text}
응답:
{{"keywords": ["..."]}}
"""

        # OpenAI 호출
        basic_info_response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": basic_info_prompt}],
            max_tokens=500
        )
        summary_response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=300
        )
        keywords_response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": keywords_prompt}],
            max_tokens=300
        )

        # 응답 파싱
        basic_info_text = basic_info_response.choices[0].message.content or ""
        summary_text = (summary_response.choices[0].message.content or "").strip()
        keywords_text = keywords_response.choices[0].message.content or ""

        basic_info: Dict[str, Any] = {}
        try:
            j0, j1 = basic_info_text.find('{'), basic_info_text.rfind('}') + 1
            if j0 != -1 and j1 > j0:
                basic_info = json.loads(basic_info_text[j0:j1])
                print(f"GPT-4o-mini 기본 정보 추출 성공: {basic_info}")
            else:
                print(f"GPT-4o-mini JSON 파싱 실패 - 응답: {basic_info_text}")
        except Exception as parse_err:
            print(f"GPT-4o-mini JSON 파싱 오류: {parse_err}")
            print(f"원본 응답: {basic_info_text}")
            basic_info = {}

        keywords: List[str] = []
        try:
            k0, k1 = keywords_text.find('{'), keywords_text.rfind('}') + 1
            if k0 != -1 and k1 > k0:
                kw = json.loads(keywords_text[k0:k1])
                keywords = kw.get("keywords", [])
        except Exception:
            keywords = []

        # 배열 형태로 변환
        entities = {
            "names": [basic_info.get("name", "")] if basic_info.get("name") else [],
            "emails": [basic_info.get("email", "")] if basic_info.get("email") else [],
            "phones": [basic_info.get("phone", "")] if basic_info.get("phone") else [],
            "positions": [basic_info.get("position", "")] if basic_info.get("position") else [],
            "companies": [basic_info.get("company", "")] if basic_info.get("company") else [],
            "education": [basic_info.get("education", "")] if basic_info.get("education") else [],
            "skills": [basic_info.get("skills", "")] if basic_info.get("skills") else [],
            "addresses": [basic_info.get("address", "")] if basic_info.get("address") else [],
            "urls": [],
            "dates": []
        }

        return {
            "summary": summary_text,
            "keywords": keywords,
            "structured_data": {"sections": {}, "entities": entities}
        }

    except Exception as e:
        print(f"OpenAI 분석 중 오류 발생: {e}")
        return {
            "summary": generate_simple_summary(text),
            "keywords": extract_simple_keywords(text),
            "structured_data": {"sections": {}, "entities": extract_basic_info(text)},
            "error": str(e)
        }
