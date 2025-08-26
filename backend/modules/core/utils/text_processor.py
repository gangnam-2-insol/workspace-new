import re
import string
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Optional

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False
    print("Warning: kiwipiepy not available, using fallback tokenizer")

class TextProcessor:
    """텍스트 전처리 유틸리티"""

    def __init__(self):
        """텍스트 프로세서 초기화"""
        self.kiwi = None
        if KIWI_AVAILABLE:
            try:
                self.kiwi = Kiwi()
            except Exception as e:
                print(f"Kiwi 초기화 실패: {e}")

        # 한국어 불용어
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

    def normalize_text(self, text: str) -> str:
        """
        텍스트 정규화

        Args:
            text: 원본 텍스트

        Returns:
            str: 정규화된 텍스트
        """
        if not text:
            return ""

        # 유니코드 정규화
        text = unicodedata.normalize('NFKC', text)

        # 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())

        # 특수문자 처리
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        return text

    def tokenize_korean(self, text: str) -> List[str]:
        """
        한국어 토큰화

        Args:
            text: 한국어 텍스트

        Returns:
            List[str]: 토큰 리스트
        """
        if not text:
            return []

        if self.kiwi:
            try:
                # Kiwi 형태소 분석기 사용
                tokens = []
                result = self.kiwi.analyze(text)

                for token, pos, start, end in result[0][0]:
                    # 명사, 동사, 형용사만 추출
                    if pos.startswith(('NNG', 'NNP', 'VV', 'VA', 'XR')):
                        tokens.append(token)

                return tokens
            except Exception as e:
                print(f"Kiwi 토큰화 실패: {e}")
                return self._fallback_tokenize(text)
        else:
            return self._fallback_tokenize(text)

    def _fallback_tokenize(self, text: str) -> List[str]:
        """
        폴백 토큰화 (Kiwi 없을 때)

        Args:
            text: 텍스트

        Returns:
            List[str]: 토큰 리스트
        """
        # 간단한 공백 기반 토큰화
        tokens = text.split()

        # 2글자 이상만 필터링
        tokens = [token for token in tokens if len(token) >= 2]

        return tokens

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        불용어 제거

        Args:
            tokens: 토큰 리스트

        Returns:
            List[str]: 불용어가 제거된 토큰 리스트
        """
        if not tokens:
            return []

        return [token for token in tokens if token not in self.korean_stopwords]

    def merge_compound_words(self, tokens: List[str]) -> List[str]:
        """
        복합어 병합

        Args:
            tokens: 토큰 리스트

        Returns:
            List[str]: 복합어가 병합된 토큰 리스트
        """
        if not tokens:
            return []

        merged_tokens = []
        i = 0

        while i < len(tokens) - 1:
            current_token = tokens[i]
            next_token = tokens[i + 1]

            # 복합어 확인
            compound_found = False
            for compound, merged in self.compound_words.items():
                if (current_token, next_token) == compound:
                    merged_tokens.append(merged)
                    i += 2  # 두 토큰을 건너뛰기
                    compound_found = True
                    break

            if not compound_found:
                merged_tokens.append(current_token)
                i += 1

        # 마지막 토큰 처리
        if i < len(tokens):
            merged_tokens.append(tokens[i])

        return merged_tokens

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        키워드 추출

        Args:
            text: 텍스트
            max_keywords: 최대 키워드 수

        Returns:
            List[str]: 키워드 리스트
        """
        if not text:
            return []

        # 텍스트 정규화
        normalized_text = self.normalize_text(text)

        # 토큰화
        tokens = self.tokenize_korean(normalized_text)

        # 불용어 제거
        tokens = self.remove_stopwords(tokens)

        # 복합어 병합
        tokens = self.merge_compound_words(tokens)

        # 빈도 계산
        token_counts = Counter(tokens)

        # 상위 키워드 반환
        return [token for token, count in token_counts.most_common(max_keywords)]

    def create_text_summary(self, text: str, max_length: int = 200) -> str:
        """
        텍스트 요약 생성

        Args:
            text: 원본 텍스트
            max_length: 최대 길이

        Returns:
            str: 요약된 텍스트
        """
        if not text:
            return ""

        # 키워드 추출
        keywords = self.extract_keywords(text, max_keywords=10)

        # 문장 분리
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 키워드가 포함된 문장 우선 선택
        keyword_sentences = []
        other_sentences = []

        for sentence in sentences:
            sentence_keywords = set(self.extract_keywords(sentence))
            if any(keyword in sentence_keywords for keyword in keywords):
                keyword_sentences.append(sentence)
            else:
                other_sentences.append(sentence)

        # 요약 생성
        summary_parts = []
        current_length = 0

        # 키워드 문장 먼저 추가
        for sentence in keyword_sentences:
            if current_length + len(sentence) <= max_length:
                summary_parts.append(sentence)
                current_length += len(sentence)
            else:
                break

        # 나머지 공간에 일반 문장 추가
        for sentence in other_sentences:
            if current_length + len(sentence) <= max_length:
                summary_parts.append(sentence)
                current_length += len(sentence)
            else:
                break

        return '. '.join(summary_parts) + '.'

    def clean_html_tags(self, text: str) -> str:
        """
        HTML 태그 제거

        Args:
            text: HTML이 포함된 텍스트

        Returns:
            str: HTML 태그가 제거된 텍스트
        """
        if not text:
            return ""

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # HTML 엔티티 디코딩
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')

        return text

    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        구조화된 데이터 추출

        Args:
            text: 텍스트

        Returns:
            Dict[str, Any]: 구조화된 데이터
        """
        if not text:
            return {}

        structured_data = {
            'keywords': self.extract_keywords(text),
            'summary': self.create_text_summary(text),
            'word_count': len(text.split()),
            'character_count': len(text),
            'sentence_count': len(re.split(r'[.!?]', text)),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
        }

        # 이메일 추출
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        structured_data['emails'] = emails

        # 전화번호 추출
        phone_pattern = r'\b\d{2,3}-\d{3,4}-\d{4}\b'
        phones = re.findall(phone_pattern, text)
        structured_data['phones'] = phones

        # URL 추출
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        structured_data['urls'] = urls

        return structured_data

    def preprocess_for_embedding(self, text: str) -> str:
        """
        임베딩을 위한 텍스트 전처리

        Args:
            text: 원본 텍스트

        Returns:
            str: 전처리된 텍스트
        """
        if not text:
            return ""

        # HTML 태그 제거
        text = self.clean_html_tags(text)

        # 텍스트 정규화
        text = self.normalize_text(text)

        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()

        return text
