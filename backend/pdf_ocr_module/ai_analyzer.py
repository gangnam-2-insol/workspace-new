from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
import json
import asyncio
import base64
from pathlib import Path

from .config import Settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from openai_service import OpenAIService
except ImportError:
    OpenAIService = None


def analyze_text(text: str, settings: Settings) -> Dict[str, Any]:
    """텍스트를 분석하여 구조화된 정보를 추출합니다."""
    try:
        # 기본 텍스트 정리
        clean_text = clean_text_content(text)
        
        # 기본 정보 추출
        basic_info = extract_basic_info(clean_text)
        
        # AI 분석 (설정에 따라)
        if settings.index_generate_summary or settings.index_generate_keywords:
            ai_analysis = analyze_with_ai(clean_text, settings)
        else:
            ai_analysis = {"summary": "", "keywords": []}
        
        return {
            "clean_text": clean_text,
            "basic_info": basic_info,
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


def analyze_text_with_vision(image_paths: List[Path], text: str, settings: Settings) -> Dict[str, Any]:
    """Vision API를 사용하여 이미지와 텍스트를 함께 분석합니다."""
    try:
        # 기본 텍스트 정리
        clean_text = clean_text_content(text)
        
        # Vision API를 사용한 분석 시도
        if settings.index_generate_summary or settings.index_generate_keywords:
            vision_analysis = analyze_with_vision(image_paths, clean_text, settings)
        else:
            vision_analysis = {"summary": "", "keywords": [], "basic_info": {}}
        
        # 기존 텍스트 기반 분석도 병행
        basic_info = extract_basic_info(clean_text)
        
        return {
            "clean_text": clean_text,
            "basic_info": basic_info,
            "summary": vision_analysis.get("summary", ""),
            "keywords": vision_analysis.get("keywords", []),
            "structured_data": vision_analysis.get("structured_data", {}),
            "vision_analysis": vision_analysis.get("vision_analysis", {})
        }
    except Exception as e:
        print(f"Vision 분석 실패, 텍스트 기반으로 폴백: {e}")
        # Vision 실패 시 기존 텍스트 기반 분석으로 폴백
        return analyze_text(text, settings)


def analyze_with_vision(image_paths: List[Path], text: str, settings: Settings) -> Dict[str, Any]:
    """GPT Vision API를 사용하여 이미지를 직접 분석합니다."""
    try:
        if not OpenAIService:
            print("OpenAI 서비스가 사용할 수 없습니다.")
            return {"summary": "", "keywords": [], "structured_data": {}}
        
        openai_service = OpenAIService(model_name="gpt-4o")
        
        # 비동기 함수를 동기적으로 실행
        async def run_vision_analysis():
            try:
                # 이미지를 base64로 인코딩
                encoded_images = []
                for image_path in image_paths:
                    if image_path.exists():
                        with open(image_path, "rb") as image_file:
                            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                            encoded_images.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            })
                
                if not encoded_images:
                    print("분석할 이미지가 없습니다.")
                    return {"summary": "", "keywords": [], "structured_data": {}}
                
                # Vision API 프롬프트
                vision_prompt = f"""
다음은 이력서 이미지와 추출된 텍스트입니다. 이미지와 텍스트를 모두 분석하여 정확한 정보를 추출해주세요.

추출된 텍스트:
{text}

이미지에서 다음 정보들을 정확히 추출해주세요:
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
    "address": "추출된 주소",
    "summary": "이력서 요약 (2-3문장)",
    "keywords": ["키워드1", "키워드2", "키워드3", ...]
}}

만약 특정 정보를 찾을 수 없다면 해당 필드는 빈 문자열("")로 설정해주세요.
이미지의 레이아웃과 시각적 정보를 활용하여 더 정확한 정보를 추출해주세요.
"""

                # Vision API 호출
                vision_response = await openai_service.generate_response_with_vision(
                    vision_prompt, 
                    encoded_images
                )
                
                # JSON 파싱 시도
                try:
                    json_start = vision_response.find('{')
                    json_end = vision_response.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = vision_response[json_start:json_end]
                        vision_data = json.loads(json_str)
                        
                        # Vision 결과를 구조화
                        basic_info = {
                            "names": [vision_data.get("name", "")] if vision_data.get("name") else [],
                            "emails": [vision_data.get("email", "")] if vision_data.get("email") else [],
                            "phones": [vision_data.get("phone", "")] if vision_data.get("phone") else [],
                            "positions": [vision_data.get("position", "")] if vision_data.get("position") else [],
                            "companies": [vision_data.get("company", "")] if vision_data.get("company") else [],
                            "education": [vision_data.get("education", "")] if vision_data.get("education") else [],
                            "skills": [vision_data.get("skills", "")] if vision_data.get("skills") else [],
                            "addresses": [vision_data.get("address", "")] if vision_data.get("address") else []
                        }
                        
                        analysis = {
                            "summary": vision_data.get("summary", ""),
                            "keywords": vision_data.get("keywords", []),
                            "basic_info": basic_info,
                            "structured_data": {
                                "document_type": "resume",
                                "vision_analysis": True,
                                "basic_info": {
                                    "name": vision_data.get("name", ""),
                                    "email": vision_data.get("email", ""),
                                    "phone": vision_data.get("phone", ""),
                                    "position": vision_data.get("position", ""),
                                    "company": vision_data.get("company", ""),
                                    "education": vision_data.get("education", ""),
                                    "skills": vision_data.get("skills", ""),
                                    "address": vision_data.get("address", "")
                                }
                            },
                            "vision_analysis": vision_data
                        }
                        
                        print(f"Vision 분석 결과: {vision_data}")
                        return analysis
                        
                except Exception as e:
                    print(f"Vision JSON 파싱 실패: {e}")
                    return {"summary": "", "keywords": [], "structured_data": {}}
                    
            except Exception as e:
                print(f"Vision 분석 실행 실패: {e}")
                return {"summary": "", "keywords": [], "structured_data": {}}
        
        # 비동기 함수 실행
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_vision_analysis())
            return result
        except Exception as e:
            print(f"Vision 비동기 실행 실패: {e}")
            return {"summary": "", "keywords": [], "structured_data": {}}
        finally:
            if 'loop' in locals():
                loop.close()
                
    except Exception as e:
        print(f"Vision 분석 중 오류 발생: {e}")
        return {"summary": "", "keywords": [], "structured_data": {}}


def clean_text_content(text: str) -> str:
    """텍스트를 정리하고 정규화합니다."""
    if not text:
        return ""
    
    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 줄바꿈 정리
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 특수문자 정리
    text = re.sub(r'[^\w\s\.,!?;:()\-_@#$%&*+=<>\[\]{}|\\/]', '', text)
    
    return text.strip()


def clean_ocr_text(text: str) -> str:
    """OCR 텍스트를 정리하고 노이즈를 제거합니다."""
    if not text:
        return ""
    
    # OCR 노이즈 제거
    # 1. 깨진 문자 제거
    text = re.sub(r'[^\w\s\.,!?;:()\-_@#$%&*+=<>\[\]{}|\\/가-힣]', '', text)
    
    # 2. 연속된 공백 정리
    text = re.sub(r'\s+', ' ', text)
    
    # 3. 줄바꿈 정리
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # 4. 특정 OCR 오류 패턴 수정
    # 숫자와 문자의 혼동 수정
    text = re.sub(r'([0-9])[oO]([0-9])', r'\g<1>0\2', text)  # 0과 O 혼동
    text = re.sub(r'([0-9])[lL]([0-9])', r'\g<1>1\2', text)  # 1과 l 혼동
    
    # 5. 이메일 주소 정리
    text = re.sub(r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})', r'\g<1>@\g<2>.\g<3>', text)
    
    # 6. 전화번호 정리
    text = re.sub(r'(\d{2,3})\s*[-]\s*(\d{3,4})\s*[-]\s*(\d{4})', r'\g<1>-\g<2>-\g<3>', text)
    
    # 7. 불필요한 특수문자 제거 (이메일, 전화번호 제외)
    text = re.sub(r'[^\w\s\.,!?;:()\-_@#$%&*+=<>\[\]{}|\\/가-힣\-]', '', text)
    
    return text.strip()


def extract_basic_info(text: str) -> Dict[str, Any]:
    """기본 정보를 추출합니다 (OpenAI GPT 우선, 정규식 기반 폴백)."""
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
        "addresses": []
    }
    
    # 텍스트 전처리: OCR 노이즈 제거
    cleaned_text = clean_ocr_text(text)
    
    # OpenAI AI를 사용한 분석 시도
    try:
        if OpenAIService:
            openai_service = OpenAIService(model_name="gpt-4o")
            
            # 비동기 함수를 동기적으로 실행
            async def run_ai_analysis():
                try:
                    ai_prompt = f"""
다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

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

                    ai_response = await openai_service.generate_response(ai_prompt)
                    
                    # JSON 파싱 시도
                    try:
                        json_start = ai_response.find('{')
                        json_end = ai_response.rfind('}') + 1
                        if json_start != -1 and json_end != 0:
                            json_str = ai_response[json_start:json_end]
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
                    print(f"AI 분석 실행 실패: {e}")
                    
            # 비동기 함수 실행
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_ai_analysis())
                if result:
                    return result
            except Exception as e:
                print(f"비동기 실행 실패: {e}")
            finally:
                if 'loop' in locals():
                    loop.close()
            
    except Exception as e:
        print(f"AI 분석 실패, 규칙 기반으로 폴백: {e}")
    
    # AI 분석이 실패한 경우 규칙 기반 분석으로 폴백
    
    # 이메일 추출
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    info["emails"] = re.findall(email_pattern, cleaned_text)
    
    # 전화번호 추출 (더 정확한 패턴)
    phone_patterns = [
        r'\b(?:010|011|016|017|018|019)[-\s]?\d{3,4}[-\s]?\d{4}\b',  # 휴대폰
        r'\b(?:02|03[1-9]|04[1-9]|05[1-9]|06[1-9])[-\s]?\d{3,4}[-\s]?\d{4}\b',  # 지역번호
        r'\b\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}\b'  # 일반 전화번호
    ]
    
    all_phones = []
    for pattern in phone_patterns:
        phones = re.findall(pattern, cleaned_text)
        all_phones.extend(phones)
    
    # 중복 제거 및 정리
    info["phones"] = list(set([phone.strip() for phone in all_phones if len(phone.strip()) >= 10]))
    
    # 날짜 추출
    date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}'
    info["dates"] = re.findall(date_pattern, cleaned_text)
    
    # URL 추출
    url_pattern = r'https?://[^\s]+'
    info["urls"] = re.findall(url_pattern, cleaned_text)
    
    # 이름 추출 (이력서에서 가장 가능성이 높은 하나의 이름만 추출)
    name_patterns = [
        # 1. 가장 명확한 라벨 기반 이름 추출 (우선순위 최고)
        r'(?:이름|성명|Name|name)\s*[:\-]?\s*([가-힣]{2,4})',
        # 2. 개인정보 섹션에서 이름
        r'(?:개인정보|Personal Information)\s*[:\-]?\s*([가-힣]{2,4})',
        # 3. 연락처 정보에서 이름
        r'(?:연락처|Contact|contact)\s*[:\-]?\s*([가-힣]{2,4})',
        # 4. 이메일에서 추출 (한글 이름이 있는 경우)
        r'([가-힣]{2,4})@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # 5. 전화번호 앞의 이름 (이름 + 전화번호 패턴)
        r'([가-힣]{2,4})\s*[0-9]{2,3}-[0-9]{3,4}-[0-9]{4}',
        # 6. 직책 앞의 이름 (이름 + 직책 패턴)
        r'([가-힣]{2,4})\s*(?:팀장|과장|대리|사원|부장|이사|CEO|CTO|CFO)',
        # 7. 호칭과 함께 있는 이름 (이름 + 호칭 패턴)
        r'([가-힣]{2,4})\s*(?:님|씨|선생님|대표|사장)',
        # 8. 괄호 안의 이름 (이름만 있는 경우)
        r'\(([가-힣]{2,4})\)',
        # 9. RESUME 앞에 있는 이름 (새로운 패턴)
        r'([가-힣]{2,4})\s+RESUME',
        # 10. 이메일 앞에 있는 이름
        r'([가-힣]{2,4})\s+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # 11. 전화번호 앞에 있는 이름
        r'([가-힣]{2,4})\s*\+?[\d\s\-\(\)]{10,}',
        # 12. 직책과 함께 있는 이름 (이름 + 직책) - 수정
        r'(?:그래픽디자이너|디자이너|개발자|프로그래머|엔지니어|기획자|마케터|영업|인사|회계)\s*,\s*([가-힣]{2,4})',
        # 13. 문서 맨 위에 독립적으로 있는 이름 (이력서 시작 부분) - 수정
        r'^([가-힣]{2,4})\n',
        # 14. 새로운 패턴: 이메일 주소에서 이름 추출 (더 정확한 패턴)
        r'([가-힣]{2,4})[._]?[a-zA-Z0-9]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # 15. 전화번호와 이메일 사이의 이름
        r'([가-힣]{2,4})\s*[|]\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ]
    
    # 이름 추출 및 중복 제거
    all_names = []
    for i, pattern in enumerate(name_patterns):
        matches = re.findall(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
        if isinstance(matches, list):
            all_names.extend(matches)
        else:
            all_names.append(matches)
        # 디버깅 로그
        if matches:
            print(f"Pattern {i+1} found: {matches}")
    
    print(f"All names found: {all_names}")
    
    # 이름 후보들을 정리하고 가장 가능성이 높은 하나만 선택
    if all_names:
        # 빈 문자열 제거 및 정리
        clean_names = [name.strip() for name in all_names if name.strip()]
        print(f"Clean names: {clean_names}")
        
        # 중복 제거
        unique_names = list(set(clean_names))
        print(f"Unique names: {unique_names}")
        
        # 이름 유효성 검사 (한국어 이름 패턴)
        valid_names = []
        exclude_words = ['주소', '전화', '이메일', '연락처', '생년월일', '학력', '경력', '스킬', '프로젝트', '자격증', '수상', '언어', '취미', '특기', '가족', '결혼', '병역', '신장', '체중', '혈액형', '종교', '정당', '국적', '본적', '현주소', '거주지', '사는곳', '근무지', '직장', '회사', '소속', '부서', '팀', '직책', '직위', '담당', '업무', '담당업무', '담당자', '관리자', '책임자', '대표', '사장', '이사', '부장', '팀장', '과장', '대리', '사원', '주임', '계장', '선임', '수석', '선배', '후배', '동료', '상사', '부하', '직원', '근로자', '노동자', '사무직', '생산직', '기술직', '관리직', '전문직', '자유직', '프리랜서', '사업자', '개인사업자', '법인사업자', '소득세', '부가가치세', '법인세', '소득공제', '세금', '세무', '회계', '재무', '경영', '마케팅', '영업', '인사', '총무', '기획', '전략', '기술', '개발', '연구', '설계', '구현', '테스트', '배포', '운영', '유지보수', '품질', '보안', '네트워크', '서버', '클라이언트', '데이터베이스', '웹', '앱', '모바일', '클라우드', 'AI', '머신러닝', '딥러닝', '데이터', '분석', '통계', '리포트', '문서', '계약서', '매뉴얼', '가이드', '튜토리얼', '교육', '훈련', '세미나', '컨퍼런스', '워크샵', '미팅', '회의', '프레젠테이션', '발표', '강의', '멘토링', '코칭', '컨설팅', '어드바이스', '조언', '제안', '제안서', '기획서', '보고서', '결과', '성과', '실적', '업적', '수치', '지표', '목표', '계획', '전략', '방향', '비전', '미션', '가치', '문화', '환경', '조건', '요구사항', '필요사항', '우대사항', '자격요건', '지원자격', '모집요강', '채용', '구인', '구직', '이직', '퇴사', '은퇴', '정년', '연봉', '급여', '월급', '연봉', '보너스', '성과급', '수당', '복리후생', '보험', '연금', '퇴직금', '퇴직연금', '국민연금', '건강보험', '고용보험', '산재보험', '의료보험', '장기요양보험', '국민건강보험', '국민연금공단', '건강보험공단', '고용보험공단', '산재보험공단', '의료보험공단', '장기요양보험공단', '제주명조', '명조', '고딕', '바탕', '돋움', '궁서', '굴림', '맑은', '새굴림', '맑은고딕', '맑은명조', '맑은바탕', '맑은돋움', '맑은궁서', '맑은굴림', '맑은새굴림', '행간은', '행간', '자간은', '자간', '사이즈는', '사이즈', '폰트는', '폰트', '사용한', '텍스트를', '입력해주세요', '사용한', '폰트', '제주명조체', '명조체', '고딕체', '바탕체', '돋움체', '궁서체', '굴림체', '맑은체', '새굴림체', '맑은고딕체', '맑은명조체', '맑은바탕체', '맑은돋움체', '맑은궁서체', '맑은굴림체', '맑은새굴림체', '디자인팀', '개발팀', '기획팀', '마케팅팀', '영업팀', '인사팀', '회계팀', '총무팀', '기술팀', '연구팀', '품질팀', '보안팀', '운영팀', '유지보수팀', '데이터팀', 'AI팀', '클라우드팀', '웹팀', '앱팀', '모바일팀', '프론트엔드팀', '백엔드팀', '풀스택팀', 'DevOps팀', '네트워크팀', '서버팀', '데이터베이스팀', 'UI팀', 'UX팀', '그래픽팀', '시각팀', '콘텐츠팀', '편집팀', '미디어팀', '커뮤니케이션팀', '홍보팀', '브랜드팀', '전략팀', '기획팀', '분석팀', '통계팀', '리서치팀', '컨설팅팀', '교육팀', '훈련팀', '멘토링팀', '코칭팀', '어드바이스팀', '조언팀', '제안팀', '프로젝트팀', '프로덕트팀', '서비스팀', '고객팀', '지원팀', '헬프팀', '문의팀', '상담팀', '커스터머팀', '사용자팀', '유저팀', '클라이언트팀', '파트너팀', '협력팀', '제휴팀', '아웃소싱팀', '외주팀', '계약팀', '법무팀', '규정팀', '정책팀', '규정팀', '감사팀', '검토팀', '평가팀', '심사팀', '선별팀', '채용팀', '구인팀', '인재팀', '인력팀', '조직팀', '구조팀', '시스템팀', '플랫폼팀', '인프라팀', '환경팀', '설정팀', '구성팀', '배치팀', '배포팀', '릴리즈팀', '버전팀', '업데이트팀', '업그레이드팀', '마이그레이션팀', '전환팀', '이관팀', '이전팀', '복사팀', '백업팀', '복구팀', '복원팀', '재구성팀', '재구축팀', '재설계팀', '재개발팀', '재구현팀', '재테스트팀', '재배포팀', '재운영팀', '재유지보수팀', '홈페이지', '고등학교', '중학교', '초등학교', '대학교', '대학', '전문대학', '고등학교', '중학교', '초등학교', '대학교', '대학', '전문대학']
        
        for name in unique_names:
            # 2-4자 한글 이름만 허용
            if re.match(r'^[가-힣]{2,4}$', name):
                # 제외 단어가 아니면 유효한 이름으로 간주
                if name not in exclude_words:
                    valid_names.append(name)
                    print(f"Valid name found: {name}")
        
        print(f"Final valid names: {valid_names}")
        
        # 간단한 로직: 첫 번째 유효한 이름을 선택
        if valid_names:
            info["names"] = [valid_names[0]]
            print(f"Selected name: {info['names']}")
        else:
            info["names"] = []
            print("No valid names found")
    else:
        info["names"] = []
        print("No names found at all")
    
    # 직책 추출
    position_patterns = [
        r'(?:직책|직위|Position|position)\s*[:\-]?\s*([가-힣A-Za-z\s]+)',
        r'(?:담당|담당자|Manager|manager)\s*[:\-]?\s*([가-힣A-Za-z\s]+)',
        r'(?:팀장|과장|대리|사원|부장|이사|CEO|CTO|CFO|PM|PL)',
        r'(?:Senior|Junior|Lead|Principal|Staff|Associate)\s+[A-Za-z\s]+',
        r'(?:개발자|프로그래머|엔지니어|디자이너|기획자|마케터|영업|인사|회계)'
    ]
    
    for pattern in position_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if isinstance(matches, list):
            info["positions"].extend(matches)
        else:
            info["positions"].append(matches)
    
    # 회사명 추출
    company_patterns = [
        r'(?:회사|Company|company|소속|근무)\s*[:\-]?\s*([가-힣A-Za-z\s&\.]+)',
        r'([가-힣A-Za-z\s&\.]+)(?:주식회사|㈜|㈐|Corp|Inc|Ltd|LLC)',
        r'(?:재직|근무|소속)\s*[:\-]?\s*([가-힣A-Za-z\s&\.]+)'
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        info["companies"].extend(matches)
    
    # 학력 추출
    education_patterns = [
        r'(?:학력|Education|education|학위|Degree|degree)\s*[:\-]?\s*([가-힣A-Za-z\s&\.]+)',
        r'([가-힣A-Za-z\s&\.]+)(?:대학교|University|College|고등학교|High School)',
        r'(?:학사|석사|박사|Bachelor|Master|PhD|Ph\.D)',
        r'(?:전공|Major|major)\s*[:\-]?\s*([가-힣A-Za-z\s]+)'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if isinstance(matches, list):
            info["education"].extend(matches)
        else:
            info["education"].append(matches)
    
    # 스킬/기술 추출
    skill_patterns = [
        r'(?:스킬|기술|Skills|skills|기술스택|Tech Stack)\s*[:\-]?\s*([가-힣A-Za-z\s,]+)',
        r'(?:Python|Java|JavaScript|React|Vue|Angular|Node\.js|Django|Flask|Spring|MySQL|PostgreSQL|MongoDB|AWS|Azure|Docker|Kubernetes|Git|Linux|Windows|Mac|HTML|CSS|SASS|TypeScript|PHP|C\+\+|C#|Go|Rust|Swift|Kotlin|Flutter|React Native)',
        r'(?:프론트엔드|백엔드|풀스택|웹개발|앱개발|데이터분석|AI|머신러닝|딥러닝|클라우드|DevOps|보안|네트워크|데이터베이스|UI/UX|그래픽디자인|마케팅|영업|인사|회계|법무)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if isinstance(matches, list):
            info["skills"].extend(matches)
        else:
            info["skills"].append(matches)
    
    # 주소 추출
    address_patterns = [
        r'(?:주소|Address|address|거주지|사는곳)\s*[:\-]?\s*([가-힣A-Za-z\s\d\-]+)',
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+동)',
        r'([가-힣]+도\s+[가-힣]+시\s+[가-힣]+구)',
        r'([가-힣]+시\s+[가-힣]+구)'
    ]
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        info["addresses"].extend(matches)
    
    # 중복 제거 및 정리
    for key in info:
        if isinstance(info[key], list):
            # 빈 문자열 제거
            info[key] = [item.strip() for item in info[key] if item.strip()]
            # 중복 제거
            info[key] = list(set(info[key]))
            # 길이순 정렬
            info[key].sort(key=len, reverse=True)
    
    return info


def analyze_with_ai(text: str, settings: Settings) -> Dict[str, Any]:
    """AI LLM을 사용해서 텍스트를 분석합니다."""
    try:
        # OpenAI GPT를 사용한 분석
        openai_service = OpenAIService(model_name="gpt-4o") if OpenAIService else None
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 기본 정보 추출을 위한 프롬프트
            basic_info_prompt = f"""
다음은 이력서에서 추출한 텍스트입니다. 이 텍스트에서 다음 정보들을 정확히 추출해주세요:

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

            # OpenAI 호출
            basic_info_response = loop.run_until_complete(
                openai_service.generate_response(basic_info_prompt)
            )
            summary_response = loop.run_until_complete(
                openai_service.generate_response(summary_prompt)
            )
            keywords_response = loop.run_until_complete(
                openai_service.generate_response(keywords_prompt)
            )
            
            # JSON 파싱 시도
            basic_info = {}
            try:
                # JSON 부분만 추출
                json_start = basic_info_response.find('{')
                json_end = basic_info_response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = basic_info_response[json_start:json_end]
                    basic_info = json.loads(json_str)
            except:
                basic_info = {}
            
            keywords = []
            try:
                json_start = keywords_response.find('{')
                json_end = keywords_response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = keywords_response[json_start:json_end]
                    keywords_data = json.loads(json_str)
                    keywords = keywords_data.get('keywords', [])
            except:
                keywords = []
            
            # basic_info를 배열 형태로도 추가 (기존 코드와의 호환성을 위해)
            basic_info_array = {
                "names": [basic_info.get("name", "")] if basic_info.get("name") else [],
                "emails": [basic_info.get("email", "")] if basic_info.get("email") else [],
                "phones": [basic_info.get("phone", "")] if basic_info.get("phone") else [],
                "positions": [basic_info.get("position", "")] if basic_info.get("position") else [],
                "companies": [basic_info.get("company", "")] if basic_info.get("company") else [],
                "education": [basic_info.get("education", "")] if basic_info.get("education") else [],
                "skills": [basic_info.get("skills", "")] if basic_info.get("skills") else [],
                "addresses": [basic_info.get("address", "")] if basic_info.get("address") else []
            }
            
            analysis = {
                "summary": summary_response,
                "keywords": keywords,
                "basic_info": basic_info_array,  # 배열 형태로 추가
                "structured_data": {
                    "document_type": detect_document_type(text),
                    "sections": extract_sections(text),
                    "entities": extract_entities(text),
                    "basic_info": basic_info  # 단일 값 형태
                }
            }
            
        finally:
            loop.close()
        
        return analysis
        
    except Exception as e:
        print(f"AI 분석 중 오류 발생: {e}")
        # 오류 발생 시 규칙 기반 분석으로 폴백
        return {
            "summary": generate_summary(text),
            "keywords": extract_keywords(text),
            "structured_data": extract_structured_data(text),
            "error": str(e)
        }


def generate_summary(text: str) -> str:
    """텍스트 요약을 생성합니다."""
    if not text:
        return ""
    
    # 간단한 요약 로직
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if len(sentences) <= 3:
        return text[:200] + "..." if len(text) > 200 else text
    
    # 첫 번째, 중간, 마지막 문장 선택
    summary_sentences = []
    if sentences:
        summary_sentences.append(sentences[0])
    if len(sentences) > 2:
        summary_sentences.append(sentences[len(sentences)//2])
    if len(sentences) > 1:
        summary_sentences.append(sentences[-1])
    
    return ". ".join(summary_sentences) + "."


def extract_keywords(text: str) -> List[str]:
    """키워드를 추출합니다."""
    if not text:
        return []
    
    # 한국어 키워드 패턴
    korean_keywords = [
        "이력서", "자기소개서", "경력", "학력", "스킬", "기술", "프로젝트", "업무", "담당",
        "개발", "프로그래밍", "소프트웨어", "웹", "앱", "데이터베이스", "서버", "클라이언트",
        "프론트엔드", "백엔드", "풀스택", "AI", "머신러닝", "딥러닝", "데이터", "분석",
        "관리", "운영", "설계", "구현", "테스트", "배포", "유지보수", "최적화",
        "성능", "보안", "품질", "문서", "리포트", "계획", "전략", "분석", "연구"
    ]
    
    # 영어 키워드 패턴
    english_keywords = [
        "resume", "cv", "experience", "education", "skills", "project", "work", "job",
        "development", "programming", "software", "web", "app", "database", "server",
        "frontend", "backend", "fullstack", "ai", "machine learning", "data", "analysis",
        "management", "operation", "design", "implementation", "test", "deploy", "maintenance",
        "performance", "security", "quality", "document", "report", "plan", "strategy"
    ]
    
    found_keywords = []
    
    # 한국어 키워드 검색
    for keyword in korean_keywords:
        if keyword in text:
            found_keywords.append(keyword)
    
    # 영어 키워드 검색 (대소문자 구분 없이)
    text_lower = text.lower()
    for keyword in english_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    # 중복 제거하고 상위 10개만 반환
    unique_keywords = list(set(found_keywords))
    return unique_keywords[:10]


def extract_structured_data(text: str) -> Dict[str, Any]:
    """구조화된 데이터를 추출합니다."""
    structured_data = {
        "document_type": detect_document_type(text),
        "sections": extract_sections(text),
        "entities": extract_entities(text)
    }
    
    return structured_data


def detect_document_type(text: str) -> str:
    """문서 유형을 감지합니다."""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["이력서", "resume", "cv", "경력사항"]):
        return "resume"
    elif any(word in text_lower for word in ["자기소개서", "cover letter", "소개서"]):
        return "cover_letter"
    elif any(word in text_lower for word in ["보고서", "report", "분석", "analysis"]):
        return "report"
    elif any(word in text_lower for word in ["계약서", "contract", "협약", "agreement"]):
        return "contract"
    elif any(word in text_lower for word in ["매뉴얼", "manual", "가이드", "guide"]):
        return "manual"
    else:
        return "general"


def extract_sections(text: str) -> Dict[str, str]:
    """문서의 섹션들을 추출합니다."""
    sections = {}
    
    # 일반적인 섹션 제목들
    section_patterns = {
        "개인정보": r"(개인정보|Personal Information|이름|Name)[:\s]*([^\n]+)",
        "학력": r"(학력|Education|학위|Degree)[:\s]*([^\n]+)",
        "경력": r"(경력|Experience|Work History|업무경험)[:\s]*([^\n]+)",
        "스킬": r"(스킬|Skills|기술|Technology)[:\s]*([^\n]+)",
        "프로젝트": r"(프로젝트|Project|프로젝트 경험)[:\s]*([^\n]+)",
        "자격증": r"(자격증|Certification|License)[:\s]*([^\n]+)",
        "수상": r"(수상|Award|상|Prize)[:\s]*([^\n]+)",
        "언어": r"(언어|Language|외국어)[:\s]*([^\n]+)"
    }
    
    for section_name, pattern in section_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            sections[section_name] = matches[0][1] if isinstance(matches[0], tuple) else matches[0]
    
    return sections


def extract_entities(text: str) -> Dict[str, List[str]]:
    """엔티티를 추출합니다."""
    entities = {
        "organizations": [],
        "locations": [],
        "dates": [],
        "numbers": []
    }
    
    # 조직명 추출 (대문자로 시작하는 연속된 단어들)
    org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    entities["organizations"] = re.findall(org_pattern, text)
    
    # 날짜 추출
    date_pattern = r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}'
    entities["dates"] = re.findall(date_pattern, text)
    
    # 숫자 추출
    number_pattern = r'\b\d+(?:\.\d+)?\b'
    entities["numbers"] = re.findall(number_pattern, text)
    
    return entities


def extract_fields(text: str) -> Dict[str, Any]:
    """기존 함수와의 호환성을 위한 래퍼 함수."""
    return extract_basic_info(text)


def summarize_text(text: str) -> str:
    """기존 함수와의 호환성을 위한 래퍼 함수."""
    return generate_summary(text)


def clean_text(text: str) -> str:
    """기존 함수와의 호환성을 위한 래퍼 함수."""
    return clean_text_content(text)



