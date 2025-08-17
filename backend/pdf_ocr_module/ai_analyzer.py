from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import json
import os
from openai import AsyncOpenAI

from .config import Settings


async def analyze_text(text: str, settings: Settings) -> Dict[str, Any]:
    """텍스트를 분석하여 구조화된 정보를 추출합니다."""
    try:
        # 기본 텍스트 정리
        clean_text = clean_text_content(text)
        
        # 기본 정보 추출
        basic_info = extract_basic_info(clean_text)
        
        # GPT-4o-mini 분석 (항상 실행)
        try:
            ai_analysis = await analyze_with_ai(clean_text, settings)
            print("GPT-4o-mini 분석 실행됨")
        except Exception as ai_error:
            print(f"GPT-4o-mini 분석 실패: {ai_error}")
            ai_analysis = {"summary": "", "keywords": [], "structured_data": {"entities": {}}}
        
        # GPT 결과가 있으면 GPT 사용, 없으면 정규식 사용
        gpt_basic_info = ai_analysis.get("structured_data", {}).get("entities", {})
        final_basic_info = gpt_basic_info if gpt_basic_info and any(gpt_basic_info.values()) else basic_info
        
        print(f"최종 사용할 basic_info: {'GPT-4o-mini' if gpt_basic_info and any(gpt_basic_info.values()) else '정규식'}")
        if gpt_basic_info and any(gpt_basic_info.values()):
            print(f"GPT-4o-mini 추출 결과: {gpt_basic_info}")
        else:
            print("GPT-4o-mini 결과가 비어있어 정규식 사용")
        
        return {
            "clean_text": clean_text,
            "basic_info": final_basic_info,
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
    
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 줄바꿈 정리
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def extract_basic_info(text: str) -> Dict[str, Any]:
    """기본 정보를 추출합니다 (정규식 기반)."""
    info = {
        "emails": [],
        "phones": [],
        "dates": [],
        "urls": [],
        "names": [],
        "positions": [],
        "companies": [],
        "education": [],
        "skills": [],
        "addresses": []
    }
    
    try:
        # 이메일 추출
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info["emails"] = re.findall(email_pattern, text)
        
        # 전화번호 추출 (다양한 형식 지원)
        phone_patterns = [
            r'\b(010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)-\d{3,4}-\d{4}\b',  # 하이픈 포함
            r'\b(010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\s\d{3,4}\s\d{4}\b',  # 공백 포함
            r'\b(010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\.\d{3,4}\.\d{4}\b',  # 점 포함
            r'\b(010|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064|070|080|090)\d{3,4}\d{4}\b',  # 구분자 없음
        ]
        
        phones = []
        for pattern in phone_patterns:
            found_phones = re.findall(pattern, text)
            phones.extend(found_phones)
        
        # 표준 형식으로 변환
        standardized_phones = []
        for phone in phones:
            # 공백, 점, 구분자 제거 후 숫자만 추출
            digits = re.sub(r'[^\d]', '', phone)
            if len(digits) >= 10:
                # 표준 형식으로 변환
                if digits.startswith('010'):
                    formatted = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
                else:
                    formatted = f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
                standardized_phones.append(formatted)
        
        info["phones"] = list(set(standardized_phones))
        
        # URL 추출
        url_pattern = r'https?://[^\s]+'
        info["urls"] = re.findall(url_pattern, text)
        
        # 이름 추출 (한국어 이름 패턴 - 더 정확하게)
        name_pattern = r'\b[가-힣]{2,3}\s*[가-힣]{1,2}\b'
        names = re.findall(name_pattern, text)
        # 의미있는 이름만 필터링 (더 엄격한 필터링)
        exclude_words = [
            '텍스트', '입력', '주세요', '사용한', '폰트', '사이즈', '행간', '자간', '리스트',
            '포토그래퍼', '구로구', '미리아파트', '기능사', '획득한', '자격증', '명칭',
            '산악하이킹', '레고수집', '최우수상', '제작참여', '프로젝트에', '주요업무를',
            '회사명', '프로젝트명', '담당업무', '대학교', '고등학교', '컬러리스트',
            '디자인컨설턴트', '디지털로', '미리캔버스', '미리대학교', '미리고등학교',
            '제작팀', '팀', '팀장', '팀원', '팀리더', '팀매니저', '팀원', '팀장', '팀리더',
            '프로젝트', '프로젝트팀', '프로젝트매니저', '프로젝트리더', '프로젝트팀장'
        ]
        info["names"] = [
            name.strip() for name in names 
            if len(name.strip()) >= 2 
            and not any(word in name for word in exclude_words)
            and not any(char.isdigit() for char in name)  # 숫자 포함 제외
            and not name.strip().endswith(('구', '로', '사', '트', '상', '를', '에', '명', '무'))
        ]
        
        # 직책 추출 (더 정확한 패턴)
        position_pattern = r'\b(사원|대리|과장|차장|부장|이사|대표|CEO|CTO|CFO|개발자|프로그래머|엔지니어|디자이너|매니저|팀장|리더|포토그래퍼|컬러리스트|디자인컨설턴트|프로젝트매니저|시스템관리자|데이터분석가|UX디자이너|UI디자이너|웹디자이너|그래픽디자이너|편집디자이너|일러스트레이터|사진작가|카피라이터|마케터|세일즈|영업|기획자|기획|연구원|연구자|교수|강사|강사|선생님|교사)\b'
        positions = re.findall(position_pattern, text)
        # 의미있는 직책만 필터링
        info["positions"] = [pos for pos in positions if len(pos.strip()) >= 2 and not any(word in pos for word in ['프로젝트에', '주요업무를', '담당업무', '적어주세요'])]
        
        # 회사명 추출 (더 정확한 패턴)
        company_pattern = r'\b[가-힣A-Za-z0-9]+(주식회사|㈜|㈐|㈑|㈒|㈓|㈔|㈕|㈖|㈗|㈘|㈙|Corp|Inc|Ltd|LLC|Co\.|회사|그룹|기업|스튜디오|랩|연구소|센터|아카데미|학교|대학교|고등학교|중학교|초등학교)\b'
        companies = re.findall(company_pattern, text)
        # 의미있는 회사명만 필터링
        exclude_company_words = ['프로젝트', '담당업무', '주요 업무', '적어주세요', '회사명', '프로젝트명', '담당업무', '주요업무를']
        info["companies"] = [company for company in companies if len(company.strip()) >= 3 and not any(word in company for word in exclude_company_words)]
        
        # 학력 추출 (더 정확한 패턴)
        education_pattern = r'\b[가-힣A-Za-z\s]+(대학교|대학|고등학교|고교|중학교|초등학교|전문대학|대학원|석사|박사|학사|전문학사|고졸|중졸|초졸)\b'
        education = re.findall(education_pattern, text)
        # 의미있는 학력만 필터링
        exclude_education_words = ['프로젝트', '담당업무', '주요 업무', '적어주세요', '학력', '학력정보', '학력사항']
        info["education"] = [edu for edu in education if len(edu.strip()) >= 4 and not any(word in edu for word in exclude_education_words)]
        
        # 기술 스킬 추출 (더 정확한 패턴)
        skill_pattern = r'\b(Python|Java|JavaScript|React|Node\.js|SQL|MongoDB|AWS|Docker|Kubernetes|Git|Linux|HTML|CSS|TypeScript|Vue\.js|Angular|Spring|Django|Flask|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Android|iOS|Photoshop|Illustrator|Figma|Sketch|컬러리스트|기능사|AutoCAD|3ds Max|Maya|Blender|Premiere Pro|After Effects|InDesign|Lightroom|Capture One|Cinema 4D|Unity|Unreal Engine|Word|Excel|PowerPoint|Access|Outlook|SharePoint|Teams|Slack|Notion|Trello|Asana|Jira|Confluence|Figma|Adobe XD|Sketch|InVision|Zeplin|Tableau|Power BI|R|MATLAB|SPSS|SAS|Stata|TensorFlow|PyTorch|Scikit-learn|Keras|OpenCV|NumPy|Pandas|Matplotlib|Seaborn|Plotly|D3\.js|Bootstrap|Tailwind CSS|Sass|Less|Webpack|Babel|ESLint|Prettier|Jest|Cypress|Selenium|Postman|Insomnia|Swagger|GraphQL|REST API|Microservices|CI/CD|Jenkins|GitLab|GitHub Actions|Terraform|Ansible|Chef|Puppet|ELK Stack|Prometheus|Grafana|Kafka|RabbitMQ|Redis|Elasticsearch|Neo4j|PostgreSQL|MySQL|Oracle|SQL Server|Firebase|Supabase|Vercel|Netlify|Heroku|AWS Lambda|Azure Functions|Google Cloud Functions|Serverless|Blockchain|Ethereum|Solidity|Bitcoin|Cryptocurrency|NFT|DeFi|Web3|Machine Learning|Deep Learning|AI|Artificial Intelligence|Data Science|Big Data|Hadoop|Spark|Kafka|Flink|Airflow|Kubernetes|Docker|Microservices|API|REST|GraphQL|SOAP|gRPC|WebSocket|Socket\.io|WebRTC|PWA|SPA|SSR|JAMstack|Headless CMS|WordPress|Drupal|Shopify|Magento|WooCommerce|Stripe|PayPal|Square|Twilio|SendGrid|Mailchimp|HubSpot|Salesforce|Zapier|IFTTT|Airtable|Notion|Coda|Linear|ClickUp|Monday\.com|Basecamp|Slack|Discord|Telegram|WhatsApp|Zoom|Microsoft Teams|Google Meet|Webex|Loom|Camtasia|OBS Studio|Audacity|GarageBand|Logic Pro|Pro Tools|Final Cut Pro|DaVinci Resolve|Avid Media Composer|Cinema 4D|Houdini|ZBrush|Substance Painter|Mari|Nuke|Houdini|RealFlow|V-Ray|Arnold|Redshift|Octane Render|Corona Renderer|Mental Ray|Maxwell Render|Lumion|Twinmotion|Enscape|V-Ray|Corona|Arnold|Redshift|Octane|Mental Ray|Maxwell|Lumion|Twinmotion|Enscape|SketchUp|Rhino|Grasshopper|Revit|AutoCAD|ArchiCAD|Vectorworks|Chief Architect|Home Designer|Sweet Home 3D|Floorplanner|RoomSketcher|Planner 5D|SketchUp|Rhino|Grasshopper|Revit|AutoCAD|ArchiCAD|Vectorworks|Chief Architect|Home Designer|Sweet Home 3D|Floorplanner|RoomSketcher|Planner 5D)\b'
        skills = re.findall(skill_pattern, text, re.IGNORECASE)
        # 의미있는 스킬만 필터링
        exclude_skill_words = ['프로젝트', '담당업무', '주요 업무', '적어주세요', '스킬', '기술', '기술스택', '기술스킬']
        info["skills"] = [skill for skill in skills if len(skill.strip()) >= 2 and not any(word in skill for word in exclude_skill_words)]
        
        # 주소 추출 (완전한 주소 패턴)
        address_patterns = [
            r'[가-힣\s]+(시|도|구|군|동|읍|면|로|길|번지)[가-힣\s\d]+(호|동|층|호수|아파트|빌라|빌딩|건물|상가|주택|단지)',
            r'[가-힣\s]+(시|도|구|군|동|읍|면|로|길|번지)[가-힣\s\d]+',
            r'[가-힣\s]+(시|도|구|군|동|읍|면|로|길|번지)',
        ]
        
        addresses = []
        for pattern in address_patterns:
            found_addresses = re.findall(pattern, text)
            addresses.extend(found_addresses)
        
        # 의미있는 주소만 필터링 (더 긴 주소 우선)
        exclude_words = ['프로젝트', '담당업무', '주요 업무', '적어주세요', '텍스트', '입력', '주세요', '주소', '주소지']
        info["addresses"] = [
            addr.strip() for addr in addresses 
            if len(addr.strip()) >= 6 
            and not any(word in addr for word in exclude_words)
        ]
        
        # 가장 긴 주소를 우선으로 정렬 (완전한 주소 우선)
        info["addresses"].sort(key=len, reverse=True)
        
        # 날짜 추출
        date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{4}\.\d{1,2}\.\d{1,2}'
        info["dates"] = re.findall(date_pattern, text)
        

        
        # 기본 정보 반환 (프론트엔드에서 배열을 기대하므로 배열 형태로 반환)
        return {
            "names": info["names"],
            "emails": info["emails"],
            "phones": info["phones"],
            "positions": info["positions"],
            "companies": info["companies"],
            "education": info["education"],
            "skills": info["skills"],
            "addresses": info["addresses"],
            "urls": info["urls"],
            "dates": info["dates"]
        }
    except Exception as e:
        return {
            "names": [],
            "emails": [],
            "phones": [],
            "positions": [],
            "companies": [],
            "education": [],
            "skills": [],
            "addresses": [],
            "urls": [],
            "dates": []
        }


def generate_simple_summary(text: str) -> str:
    """간단한 요약을 생성합니다."""
    if not text:
        return ""
    
    # 첫 200자 정도를 요약으로 사용
    summary = text[:200].strip()
    if len(text) > 200:
        summary += "..."
    
    return summary


def extract_simple_keywords(text: str) -> List[str]:
    """간단한 키워드를 추출합니다."""
    if not text:
        return []
    
    # 일반적인 기술 키워드
    tech_keywords = [
        "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "MongoDB",
        "AWS", "Docker", "Kubernetes", "Git", "Linux", "HTML", "CSS",
        "TypeScript", "Vue.js", "Angular", "Spring", "Django", "Flask"
    ]
    
    keywords = []
    for keyword in tech_keywords:
        if keyword.lower() in text.lower():
            keywords.append(keyword)
    
    return keywords[:10]  # 최대 10개만 반환


def extract_keywords(text: str) -> List[str]:
    """키워드를 추출합니다."""
    return extract_simple_keywords(text)


def summarize_text(text: str) -> str:
    """텍스트를 요약합니다."""
    return generate_simple_summary(text)


def extract_fields(text: str) -> Dict[str, Any]:
    """필드를 추출합니다."""
    return extract_basic_info(text)


def clean_text(text: str) -> str:
    """텍스트를 정리합니다."""
    return clean_text_content(text)


async def analyze_with_ai(text: str, settings: Settings) -> Dict[str, Any]:
    """OpenAI GPT-4o-mini를 사용하여 텍스트를 분석합니다."""
    try:
        # OpenAI 클라이언트 초기화
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 기본 정보 추출을 위한 프롬프트
        basic_info_prompt = f"""
다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

텍스트:
{text}

다음 정보들을 JSON 형태로 추출해주세요:
1. 이름: 가장 가능성이 높은 사람의 이름 하나만 (예: "강미리") - 템플릿 문구나 직책, 회사명, 주소 등은 제외하고 실제 사람 이름만 추출
2. 이메일: 완전한 이메일 주소 (예: "mailaddress@miricanvas.com")
3. 전화번호: 한국 표준 전화번호 형식으로 정규화 (예: "010-1234-5678", "02-1234-5678") - 공백, 점, 하이픈 등 다양한 구분자가 있어도 표준 형식으로 변환
4. 직책: 주요 직책이나 포지션 (예: "포토그래퍼", "디자이너")
5. 회사명: 주요 회사명 (예: "미리캔버스")
6. 학력: 주요 학력 정보 (예: "미리대학교 시각디자인학과")
7. 스킬: 주요 기술이나 자격 (예: "Photoshop, Illustrator, 컬러리스트 기능사")
8. 주소: 완전한 주소 정보 (예: "서울 구로구 디지털로33길 27 미리아파트 303호") - 도로명, 건물명, 호수까지 포함한 완전한 주소를 추출

중요한 규칙:
- 각 필드는 하나의 완전한 정보만 포함
- 불완전하거나 의미없는 텍스트는 제외
- 템플릿 문구나 안내 텍스트는 제외
- 숫자만 있는 정보는 제외
- 이름 필드에는 다음을 제외하고 실제 사람 이름만 추출:
  * 직책 (포토그래퍼, 컬러리스트, 디자이너 등)
  * 회사명 (미리캔버스, 미리대학교 등)
  * 주소 (구로구, 디지털로, 미리아파트 등)
  * 템플릿 문구 (프로젝트에, 주요업무를, 담당업무 등)
  * 자격증이나 수상 정보 (기능사, 최우수상 등)

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

        # 요약 생성을 위한 프롬프트
        summary_prompt = f"""
다음 이력서 텍스트를 간단하고 명확하게 요약해주세요:

{text}

요약은 다음을 포함해야 합니다:
- 지원자의 주요 경력과 전문 분야
- 핵심 스킬과 경험
- 학력 배경

2-3문장으로 간결하게 작성해주세요.
"""

        # 키워드 추출을 위한 프롬프트
        keywords_prompt = f"""
다음 이력서 텍스트에서 중요한 키워드 10개를 추출해주세요:

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

        # OpenAI API 호출
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
        basic_info_text = basic_info_response.choices[0].message.content
        summary_text = summary_response.choices[0].message.content
        keywords_text = keywords_response.choices[0].message.content
        
        # JSON 파싱 시도
        basic_info = {}
        try:
            json_start = basic_info_text.find('{')
            json_end = basic_info_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = basic_info_text[json_start:json_end]
                basic_info = json.loads(json_str)
                print(f"GPT-4o-mini 기본 정보 추출 성공: {basic_info}")
            else:
                print(f"GPT-4o-mini JSON 파싱 실패 - 응답: {basic_info_text}")
        except Exception as parse_error:
            print(f"GPT-4o-mini JSON 파싱 오류: {parse_error}")
            print(f"원본 응답: {basic_info_text}")
            basic_info = {}
        
        keywords = []
        try:
            json_start = keywords_text.find('{')
            json_end = keywords_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = keywords_text[json_start:json_end]
                keywords_data = json.loads(json_str)
                keywords = keywords_data.get('keywords', [])
        except:
            keywords = []
        
        # basic_info를 프론트엔드에서 기대하는 배열 형태로 변환
        formatted_basic_info = {
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
            "structured_data": {
                "sections": {},
                "entities": formatted_basic_info
            }
        }
        
    except Exception as e:
        print(f"OpenAI 분석 중 오류 발생: {e}")
        # 오류 발생 시 규칙 기반 분석으로 폴백
        return {
            "summary": generate_simple_summary(text),
            "keywords": extract_simple_keywords(text),
            "structured_data": {
                "sections": {},
                "entities": extract_basic_info(text)
            },
            "error": str(e)
        }



