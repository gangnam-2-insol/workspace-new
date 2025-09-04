"""
채용공고 에이전트 입력 처리 및 전처리 시스템
고급 텍스트 정규화, 언어 감지, 의도 분류, 컨텍스트 추출 기능
"""

import re
import json
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InputIntent(str, Enum):
    """입력 의도 분류"""
    CREATE_POSTING = "create_posting"      # 공고 생성
    MODIFY_POSTING = "modify_posting"      # 공고 수정
    GET_GUIDE = "get_guide"               # 가이드 요청
    SEARCH_TEMPLATE = "search_template"    # 템플릿 검색
    GENERAL_QUERY = "general_query"       # 일반 질문

class LanguageType(str, Enum):
    """언어 타입"""
    KOREAN = "korean"
    ENGLISH = "english"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class InputProcessor:
    """고급 입력 처리 및 전처리 시스템"""

    def __init__(self):
        """초기화"""
        # 한국어 불용어 사전
        self.korean_stopwords = {
            '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만', '그러나',
            '따라서', '그래서', '때문', '위해', '통해', '대해', '관해', '따라', '위한',
            '은', '는', '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과',
            '의', '도', '만', '까지', '부터', '나', '이나', '든지', '라도', '마저',
            '조차', '뿐', '밖에', '처럼', '같이', '보다', '같은', '같은', '같은',
            '저희', '우리', '그것', '이것', '저것', '여기', '거기', '저기',
            '년', '월', '일', '시', '분', '초', '개', '번', '차례', '번째'
        }

        # IT 복합어 사전
        self.compound_words = {
            ('프론트', '엔드'): '프론트엔드',
            ('백', '엔드'): '백엔드',
            ('풀', '스택'): '풀스택',
            ('데이터', '베이스'): '데이터베이스',
            ('소프트', '웨어'): '소프트웨어',
            ('하드', '웨어'): '하드웨어',
            ('클라우드', '컴퓨팅'): '클라우드컴퓨팅',
            ('머신', '러닝'): '머신러닝',
            ('딥', '러닝'): '딥러닝',
            ('인공', '지능'): '인공지능',
            ('웹', '개발'): '웹개발',
            ('모바일', '앱'): '모바일앱',
            ('앱', '개발'): '앱개발',
            ('데이터', '분석'): '데이터분석',
            ('비즈니스', '분석'): '비즈니스분석',
            ('시스템', '관리'): '시스템관리',
            ('네트워크', '관리'): '네트워크관리',
            ('보안', '관리'): '보안관리',
            ('품질', '관리'): '품질관리',
            ('프로젝트', '관리'): '프로젝트관리'
        }

        # 의도 분류 키워드
        self.intent_keywords = {
            InputIntent.CREATE_POSTING: [
                '채용', '구인', '모집', '채용공고', '공고', '등록', '작성', '만들', '생성',
                'hire', 'recruit', 'post', 'create', 'write', 'make', 'generate'
            ],
            InputIntent.MODIFY_POSTING: [
                '수정', '변경', '편집', '고치', '바꾸', '업데이트', '수정해',
                'modify', 'edit', 'change', 'update', 'fix', 'revise'
            ],
            InputIntent.GET_GUIDE: [
                '가이드', '도움', '방법', '어떻게', '팁', '조언', '안내', '설명',
                'guide', 'help', 'how', 'tip', 'advice', 'explain'
            ],
            InputIntent.SEARCH_TEMPLATE: [
                '템플릿', '양식', '예시', '샘플', '찾', '검색', '추천',
                'template', 'form', 'example', 'sample', 'find', 'search', 'recommend'
            ]
        }

        # 기술 스택 사전 (대소문자, 변형 포함)
        self.tech_stack_dict = {
            # 프론트엔드
            'react': ['React', 'react', '리액트'],
            'vue': ['Vue', 'vue', '뷰'],
            'angular': ['Angular', 'angular', '앵귤러'],
            'javascript': ['JavaScript', 'javascript', 'js', '자바스크립트'],
            'typescript': ['TypeScript', 'typescript', 'ts', '타입스크립트'],
            'html': ['HTML', 'html'],
            'css': ['CSS', 'css'],
            'sass': ['Sass', 'sass', 'SCSS', 'scss'],
            'next': ['Next.js', 'next.js', 'nextjs', '넥스트'],
            'nuxt': ['Nuxt.js', 'nuxt.js', 'nuxtjs', '넉스트'],

            # 백엔드
            'python': ['Python', 'python', '파이썬'],
            'java': ['Java', 'java', '자바'],
            'spring': ['Spring', 'spring', '스프링'],
            'node': ['Node.js', 'node.js', 'nodejs', '노드'],
            'express': ['Express', 'express', '익스프레스'],
            'django': ['Django', 'django', '장고'],
            'flask': ['Flask', 'flask', '플라스크'],
            'fastapi': ['FastAPI', 'fastapi', '패스트API'],
            'go': ['Go', 'go', 'golang', '고'],
            'rust': ['Rust', 'rust', '러스트'],

            # 데이터베이스
            'mysql': ['MySQL', 'mysql'],
            'postgresql': ['PostgreSQL', 'postgresql', 'postgres'],
            'mongodb': ['MongoDB', 'mongodb', '몽고DB'],
            'redis': ['Redis', 'redis', '레디스'],

            # 클라우드/인프라
            'aws': ['AWS', 'aws', '아마존'],
            'azure': ['Azure', 'azure', '애저'],
            'gcp': ['GCP', 'gcp', '구글클라우드'],
            'docker': ['Docker', 'docker', '도커'],
            'kubernetes': ['Kubernetes', 'kubernetes', 'k8s', '쿠버네티스'],

            # 모바일
            'reactnative': ['React Native', 'react native', 'reactnative', '리액트네이티브'],
            'flutter': ['Flutter', 'flutter', '플러터'],
            'swift': ['Swift', 'swift', '스위프트'],
            'kotlin': ['Kotlin', 'kotlin', '코틀린'],
            'android': ['Android', 'android', '안드로이드'],
            'ios': ['iOS', 'ios', '아이오에스']
        }

        # 직무 사전
        self.job_dict = {
            '개발자': ['개발자', 'developer', 'dev'],
            '엔지니어': ['엔지니어', 'engineer'],
            '프로그래머': ['프로그래머', 'programmer'],
            '아키텍트': ['아키텍트', 'architect'],
            '리드': ['리드', 'lead', '팀장', '팀리드'],
            '백엔드': ['백엔드', 'backend', '백엔드개발자'],
            '프론트엔드': ['프론트엔드', 'frontend', '프론트엔드개발자'],
            '풀스택': ['풀스택', 'fullstack', '풀스택개발자'],
            '모바일': ['모바일', 'mobile', '모바일개발자'],
            '웹': ['웹', 'web', '웹개발자'],
            '시니어': ['시니어', 'senior', '고급'],
            '주니어': ['주니어', 'junior', '초급'],
            '신입': ['신입', 'newbie', '신규'],
            '인턴': ['인턴', 'intern', '인턴십']
        }

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        입력 텍스트를 종합적으로 처리

        Args:
            user_input: 사용자 입력 텍스트

        Returns:
            처리된 결과 딕셔너리
        """
        try:
            logger.info(f"입력 처리 시작: {user_input[:50]}...")

            # 1. 텍스트 정규화
            normalized_text = self._normalize_text(user_input)

            # 2. 언어 감지
            language = self._detect_language(normalized_text)

            # 3. 의도 분류
            intent = self._classify_intent(normalized_text)

            # 4. 컨텍스트 추출
            context = self._extract_context(normalized_text)

            # 5. 키워드 추출
            keywords = self._extract_keywords(normalized_text)

            result = {
                "original_input": user_input,
                "normalized_text": normalized_text,
                "language": language,
                "intent": intent,
                "context": context,
                "keywords": keywords,
                "processed_at": datetime.now().isoformat()
            }

            logger.info(f"입력 처리 완료: 의도={intent}, 언어={language}, 키워드={len(keywords)}개")
            return result

        except Exception as e:
            logger.error(f"입력 처리 중 오류: {str(e)}")
            return {
                "original_input": user_input,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        if not text:
            return ""

        # 1. 유니코드 정규화
        text = unicodedata.normalize('NFKC', text)

        # 2. 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())

        # 3. 특수문자 처리 (이메일, URL, 전화번호 보존)
        text = self._preserve_important_patterns(text)

        # 4. 복합어 처리
        text = self._process_compound_words(text)

        # 5. 불용어 제거
        text = self._remove_stopwords(text)

        return text.strip()

    def _preserve_important_patterns(self, text: str) -> str:
        """중요한 패턴 보존"""
        # 이메일 보존
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)

        # URL 보존
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)

        # 전화번호 보존
        phone_pattern = r'\d{2,3}-\d{3,4}-\d{4}'
        phones = re.findall(phone_pattern, text)

        # 임시 마커로 대체
        text = re.sub(email_pattern, 'EMAIL_PLACEHOLDER', text)
        text = re.sub(url_pattern, 'URL_PLACEHOLDER', text)
        text = re.sub(phone_pattern, 'PHONE_PLACEHOLDER', text)

        # 일반 특수문자 제거
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        # 원본 패턴 복원
        for email in emails:
            text = text.replace('EMAIL_PLACEHOLDER', email, 1)
        for url in urls:
            text = text.replace('URL_PLACEHOLDER', url, 1)
        for phone in phones:
            text = text.replace('PHONE_PLACEHOLDER', phone, 1)

        return text

    def _process_compound_words(self, text: str) -> str:
        """복합어 처리"""
        words = text.split()
        processed_words = []

        i = 0
        while i < len(words) - 1:
            current_word = words[i]
            next_word = words[i + 1]

            # 복합어 사전에서 검색
            compound_found = False
            for (word1, word2), compound in self.compound_words.items():
                if (current_word.lower() == word1.lower() and
                    next_word.lower() == word2.lower()):
                    processed_words.append(compound)
                    i += 2  # 두 단어를 건너뛰기
                    compound_found = True
                    break

            if not compound_found:
                processed_words.append(current_word)
                i += 1

        # 마지막 단어 처리
        if i < len(words):
            processed_words.append(words[i])

        return ' '.join(processed_words)

    def _remove_stopwords(self, text: str) -> str:
        """불용어 제거"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.korean_stopwords]
        return ' '.join(filtered_words)

    def _detect_language(self, text: str) -> LanguageType:
        """언어 감지"""
        if not text:
            return LanguageType.UNKNOWN

        # 한글 문자 수
        korean_chars = len(re.findall(r'[가-힣]', text))
        # 영문 문자 수
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        # 전체 문자 수
        total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))

        if total_chars == 0:
            return LanguageType.UNKNOWN

        korean_ratio = korean_chars / total_chars
        english_ratio = english_chars / total_chars

        if korean_ratio > 0.7:
            return LanguageType.KOREAN
        elif english_ratio > 0.7:
            return LanguageType.ENGLISH
        else:
            return LanguageType.MIXED

    def _classify_intent(self, text: str) -> InputIntent:
        """의도 분류"""
        text_lower = text.lower()

        # 각 의도별 점수 계산
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            intent_scores[intent] = score

        # 가장 높은 점수의 의도 반환
        if intent_scores:
            max_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[max_intent] > 0:
                return max_intent

        return InputIntent.GENERAL_QUERY

    def _extract_context(self, text: str) -> Dict[str, Any]:
        """컨텍스트 추출"""
        context = {
            "company_name": None,
            "experience_years": None,
            "location": None,
            "salary_range": None,
            "work_type": None,
            "team_size": None
        }

        # 회사명 추출 (대문자로 시작하는 명사 패턴)
        company_pattern = r'[A-Z가-힣][a-z가-힣]*\s*(?:주식회사|(주)|회사|기업|그룹|스튜디오|랩|랩스)'
        company_match = re.search(company_pattern, text)
        if company_match:
            context["company_name"] = company_match.group()

        # 경력 연수 추출
        experience_patterns = [
            r'(\d+)\s*년\s*(?:이상|이하|정도)?',
            r'(\d+)\s*years?\s*(?:of\s*)?experience',
            r'신입',
            r'경력',
            r'시니어',
            r'주니어'
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern in ['신입', '경력', '시니어', '주니어']:
                    context["experience_years"] = pattern
                else:
                    context["experience_years"] = f"{match.group(1)}년"
                break

        # 위치 추출
        locations = ["서울", "부산", "대구", "인천", "대전", "광주", "울산", "제주"]
        for location in locations:
            if location in text:
                context["location"] = location
                break

        # 급여 범위 추출
        salary_patterns = [
            r'(\d{2,3})[~-](\d{2,3})\s*만원',
            r'(\d{2,3})[~-](\d{2,3})\s*M',
            r'(\d{2,3})[~-](\d{2,3})\s*천만원'
        ]

        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                context["salary_range"] = f"{match.group(1)}-{match.group(2)}만원"
                break

        # 근무 형태 추출
        work_types = {
            "재택": ["재택", "원격", "remote", "work from home"],
            "출근": ["출근", "사무실", "office", "on-site"],
            "하이브리드": ["하이브리드", "hybrid", "혼합"]
        }

        for work_type, keywords in work_types.items():
            if any(keyword in text for keyword in keywords):
                context["work_type"] = work_type
                break

        # 팀 규모 추출
        team_patterns = [
            r'(\d+)\s*명',
            r'(\d+)\s*people',
            r'팀\s*(\d+)\s*명'
        ]

        for pattern in team_patterns:
            match = re.search(pattern, text)
            if match:
                context["team_size"] = f"{match.group(1)}명"
                break

        return context

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []

        # 기술 스택 키워드 추출
        for category, variants in self.tech_stack_dict.items():
            for variant in variants:
                if variant.lower() in text.lower():
                    keywords.append(category)
                    break

        # 직무 키워드 추출
        for category, variants in self.job_dict.items():
            for variant in variants:
                if variant.lower() in text.lower():
                    keywords.append(category)
                    break

        # 숫자 키워드 (연도, 인원 등)
        number_keywords = re.findall(r'\d+', text)
        keywords.extend(number_keywords)

        # 고유명사 추출 (대문자로 시작하는 단어)
        proper_nouns = re.findall(r'\b[A-Z가-힣][a-z가-힣]*\b', text)
        keywords.extend(proper_nouns)

        return list(set(keywords))  # 중복 제거

    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        return {
            "total_compounds": len(self.compound_words),
            "total_tech_stacks": len(self.tech_stack_dict),
            "total_jobs": len(self.job_dict),
            "total_stopwords": len(self.korean_stopwords)
        }
