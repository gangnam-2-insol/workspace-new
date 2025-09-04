"""
텍스트 처리 유틸리티
"""

import re
from typing import Any, Dict, List


class TextProcessor:
    """텍스트 처리 유틸리티 클래스"""

    @staticmethod
    def normalize_text(text: str) -> str:
        """텍스트 정규화"""
        if not text:
            return ""

        # 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())

        # 특수문자 처리
        text = re.sub(r'[^\w\s가-힣]', '', text)

        return text

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """키워드 추출"""
        if not text:
            return []

        # 기본 토큰화
        tokens = text.split()

        # 한글 키워드 추출
        korean_keywords = re.findall(r'[가-힣]+', text)

        # 영어 키워드 추출
        english_keywords = re.findall(r'\b[a-zA-Z]+\b', text)

        # 숫자 추출
        numbers = re.findall(r'\d+', text)

        # 중복 제거 및 정렬
        all_keywords = list(set(tokens + korean_keywords + english_keywords + numbers))

        return [kw for kw in all_keywords if len(kw) > 1]

    @staticmethod
    def extract_job_info(text: str) -> Dict[str, Any]:
        """채용 정보 추출"""
        extracted_info = {}

        # 부서/직무 추출
        department_patterns = [
            r'([가-힣]+)\s*(담당자|직원|사원|팀원|매니저|리더|책임자|대리|과장|차장|부장|이사|사장)',
            r'([가-힣]+)\s*(개발자|엔지니어|디자이너|마케터|영업|기획|운영|관리|분석가|컨설턴트)',
            r'([가-힣]+)\s*(전문가|전문직|기술직|사무직|서비스직|생산직)'
        ]

        for pattern in department_patterns:
            matches = re.findall(pattern, text)
            if matches:
                department = matches[0][0] if isinstance(matches[0], tuple) else matches[0]
                if len(department) >= 2:
                    extracted_info['department'] = department
                    break

        # 경력 요구사항 추출
        experience_patterns = [
            r'(\d+)\s*년\s*(이상|이하|정도|내외)?\s*(경력|경험)',
            r'(\d+)\s*년차',
            r'신입|초급|중급|고급|시니어|주니어'
        ]

        for pattern in experience_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if '신입' in text or '초급' in text:
                    extracted_info['experience'] = '신입'
                elif '시니어' in text or '고급' in text:
                    extracted_info['experience'] = '시니어'
                elif '중급' in text:
                    extracted_info['experience'] = '중급'
                elif '주니어' in text:
                    extracted_info['experience'] = '주니어'
                else:
                    experience = matches[0] if isinstance(matches[0], str) else f"{matches[0][0]}년"
                    extracted_info['experience'] = experience
                break

        # 급여 정보 추출
        salary_patterns = [
            r'(\d{2,4})\s*만원',
            r'(\d{2,4})\s*천원',
            r'(\d{2,4})\s*원',
            r'연봉\s*(\d{2,4})\s*만원',
            r'월급\s*(\d{2,4})\s*만원'
        ]

        for pattern in salary_patterns:
            matches = re.findall(pattern, text)
            if matches:
                salary = matches[0]
                if '천원' in text:
                    salary = f"{int(salary) * 10}만원"
                elif '원' in text and '만원' not in text and '천원' not in text:
                    salary = f"{int(salary) // 10000}만원"
                extracted_info['salary'] = f"{salary}만원"
                break

        # 인원 수 추출
        headcount_patterns = [
            r'(\d+)\s*명',
            r'(\d+)\s*인',
            r'(\d+)\s*분',
            r'(\d+)\s*사람'
        ]

        headcount_found = False
        for pattern in headcount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                extracted_info['headcount'] = f"{matches[0]}명"
                headcount_found = True
                break

        # 인원수가 입력되지 않으면 기본값 0명으로 설정
        if not headcount_found:
            extracted_info['headcount'] = "0명"

        # 지역 추출
        location_patterns = [
            r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)',
            r'(강남|강북|강서|강동|서초|송파|마포|용산|성동|광진|동대문|중랑|성북|노원|도봉|양천|구로|금천|영등포|동작|관악|서대문|은평|중구|종로|용산)'
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                extracted_info['location'] = matches[0]
                break

        return extracted_info

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0

        # 키워드 추출
        keywords1 = set(TextProcessor.extract_keywords(text1.lower()))
        keywords2 = set(TextProcessor.extract_keywords(text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        # Jaccard 유사도 계산
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

