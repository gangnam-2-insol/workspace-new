"""
AI Analyzer
==========

텍스트를 AI로 분석하는 클래스입니다.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ..utils.config import Settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI 분석 클래스"""

    def __init__(self, settings: Settings):
        """
        AIAnalyzer 초기화

        Args:
            settings: 설정 객체
        """
        self.settings = settings
        self._setup_llm()

    def _setup_llm(self):
        """LLM 설정을 구성합니다."""
        self.llm = None

        if self.settings.llm_provider == "openai" and self.settings.openai_api_key:
            try:
                from openai import OpenAI
                self.llm = OpenAI(api_key=self.settings.openai_api_key)
                logger.info("OpenAI LLM 설정 완료")
            except ImportError:
                logger.warning("OpenAI 라이브러리가 설치되지 않았습니다.")

        elif self.settings.llm_provider == "groq" and self.settings.groq_api_key:
            try:
                from groq import Groq
                self.llm = Groq(api_key=self.settings.groq_api_key)
                logger.info("Groq LLM 설정 완료")
            except ImportError:
                logger.warning("Groq 라이브러리가 설치되지 않았습니다.")

        if not self.llm:
            logger.warning("LLM이 설정되지 않았습니다. 기본 분석만 사용 가능합니다.")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        텍스트를 AI로 분석합니다.

        Args:
            text: 분석할 텍스트

        Returns:
            분석 결과 딕셔너리
        """
        if not text.strip():
            return self._get_empty_analysis()

        try:
            # 기본 분석 (LLM 없이도 가능)
            basic_analysis = self._basic_analysis(text)

            # LLM 분석 (가능한 경우)
            if self.llm:
                llm_analysis = self._llm_analysis(text)
                basic_analysis.update(llm_analysis)

            return basic_analysis

        except Exception as e:
            logger.error(f"AI 분석 실패: {str(e)}")
            return self._get_empty_analysis()

    def _basic_analysis(self, text: str) -> Dict[str, Any]:
        """
        기본 텍스트 분석 (LLM 없이)

        Args:
            text: 분석할 텍스트

        Returns:
            기본 분석 결과
        """
        # 텍스트 통계
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # 키워드 추출 (간단한 방법)
        keywords = self._extract_keywords(text)

        # 문서 유형 추정
        document_type = self._guess_document_type(text)

        return {
            "summary": self._generate_summary(text),
            "keywords": keywords,
            "basic_info": {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "paragraph_count": len(paragraphs),
                "character_count": len(text),
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
            },
            "structured_data": {
                "document_type": document_type,
                "sections": self._extract_sections(text),
                "entities": self._extract_entities(text)
            }
        }

    def _llm_analysis(self, text: str) -> Dict[str, Any]:
        """
        LLM을 사용한 고급 분석

        Args:
            text: 분석할 텍스트

        Returns:
            LLM 분석 결과
        """
        try:
            if self.settings.llm_provider == "openai":
                return self._openai_analysis(text)
            elif self.settings.llm_provider == "groq":
                return self._groq_analysis(text)
            else:
                return {}
        except Exception as e:
            logger.error(f"LLM 분석 실패: {str(e)}")
            return {}

    def _openai_analysis(self, text: str) -> Dict[str, Any]:
        """OpenAI를 사용한 분석"""
        try:
            prompt = f"""
다음 텍스트를 분석하여 JSON 형태로 결과를 반환해주세요:

{text[:3000]}...

다음 형식으로 분석해주세요:
{{
    "summary": "텍스트 요약",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "document_type": "문서 유형",
    "main_topics": ["주제1", "주제2"],
    "sentiment": "긍정/부정/중립"
}}
"""

            response = self.llm.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            result_text = response.choices[0].message.content
            return json.loads(result_text)

        except Exception as e:
            logger.error(f"OpenAI 분석 실패: {str(e)}")
            return {}

    def _groq_analysis(self, text: str) -> Dict[str, Any]:
        """Groq를 사용한 분석"""
        try:
            prompt = f"""
다음 텍스트를 분석하여 JSON 형태로 결과를 반환해주세요:

{text[:3000]}...

다음 형식으로 분석해주세요:
{{
    "summary": "텍스트 요약",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "document_type": "문서 유형",
    "main_topics": ["주제1", "주제2"],
    "sentiment": "긍정/부정/중립"
}}
"""

            response = self.llm.chat.completions.create(
                model=self.settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            result_text = response.choices[0].message.content
            return json.loads(result_text)

        except Exception as e:
            logger.error(f"Groq 분석 실패: {str(e)}")
            return {}

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출 (간단한 방법)"""
        # 한국어 키워드 패턴
        korean_keywords = re.findall(r'[가-힣]{2,}', text)

        # 영어 키워드 패턴
        english_keywords = re.findall(r'\b[a-zA-Z]{3,}\b', text)

        # 빈도수 계산
        from collections import Counter
        all_keywords = korean_keywords + english_keywords

        # 불용어 제거
        stop_words = {'이', '그', '저', '것', '수', '등', '및', '또는', '그리고', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_keywords = [word for word in all_keywords if word.lower() not in stop_words]

        # 상위 10개 키워드 반환
        counter = Counter(filtered_keywords)
        return [word for word, count in counter.most_common(10)]

    def _guess_document_type(self, text: str) -> str:
        """문서 유형 추정"""
        text_lower = text.lower()

        # 이력서 관련 키워드
        resume_keywords = ['이력서', '경력', '학력', '경험', '스킬', '자격증', '수상', '프로젝트', 'resume', 'experience', 'education', 'skills']
        if any(keyword in text_lower for keyword in resume_keywords):
            return "이력서"

        # 자기소개서 관련 키워드
        cover_letter_keywords = ['자기소개서', '지원동기', '입사동기', 'cover letter', 'motivation', 'introduction']
        if any(keyword in text_lower for keyword in cover_letter_keywords):
            return "자기소개서"

        # 포트폴리오 관련 키워드
        portfolio_keywords = ['포트폴리오', '작품', '프로젝트', 'portfolio', 'project', 'work']
        if any(keyword in text_lower for keyword in portfolio_keywords):
            return "포트폴리오"

        # 일반 문서
        return "일반문서"

    def _generate_summary(self, text: str) -> str:
        """텍스트 요약 생성"""
        # 간단한 요약 (첫 200자)
        summary = text[:200].strip()
        if len(text) > 200:
            summary += "..."
        return summary

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """섹션 추출"""
        sections = {}

        # 일반적인 섹션 패턴
        section_patterns = {
            '개인정보': r'(이름|성명|주소|연락처|전화|이메일)',
            '학력': r'(학력|교육|학교|대학|졸업)',
            '경력': r'(경력|경험|직장|회사|근무)',
            '스킬': r'(스킬|기술|능력|언어|프로그램)',
            '프로젝트': r'(프로젝트|작업|개발|구현)',
            '자격증': r'(자격증|자격|인증|수료)',
            '수상': r'(수상|상|장려상|우수상)'
        }

        lines = text.split('\n')
        current_section = '기타'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 섹션 헤더 확인
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    current_section = section_name
                    break

            # 섹션에 내용 추가
            if current_section not in sections:
                sections[current_section] = ""
            sections[current_section] += line + "\n"

        return sections

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """엔티티 추출"""
        entities = {
            'names': [],
            'emails': [],
            'phones': [],
            'companies': [],
            'schools': []
        }

        # 이메일 추출
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)

        # 전화번호 추출
        phone_pattern = r'(\d{2,3}-\d{3,4}-\d{4}|\d{10,11})'
        entities['phones'] = re.findall(phone_pattern, text)

        # 회사명 추출 (간단한 패턴)
        company_pattern = r'([가-힣a-zA-Z]+(주식회사|㈜|㈐|회사|Corp|Inc|Ltd))'
        entities['companies'] = [match[0] for match in re.findall(company_pattern, text)]

        return entities

    def _get_empty_analysis(self) -> Dict[str, Any]:
        """빈 분석 결과 반환"""
        return {
            "summary": "",
            "keywords": [],
            "basic_info": {
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "character_count": 0,
                "average_word_length": 0
            },
            "structured_data": {
                "document_type": "알 수 없음",
                "sections": {},
                "entities": {
                    'names': [],
                    'emails': [],
                    'phones': [],
                    'companies': [],
                    'schools': []
                }
            }
        }
