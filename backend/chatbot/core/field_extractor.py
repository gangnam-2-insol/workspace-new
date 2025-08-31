"""
필드 추출기
"""

import re
from typing import Any, Dict, List


class FieldExtractor:
    """필드 추출기 클래스"""

    def __init__(self):
        self.field_patterns = {
            'department': [
                r'([가-힣]+)\s*(개발자|엔지니어|디자이너|마케터|영업|기획|운영|관리)',
                r'([가-힣]+)\s*(팀|부서|팀원|사원|담당자)',
                r'([가-힣]+)\s*(전문가|전문직|기술직|사무직)'
            ],
            'experience': [
                r'(\d+)\s*년\s*(이상|이하|정도|내외)?\s*(경력|경험)',
                r'(\d+)\s*년차',
                r'신입|초급|중급|고급|시니어|주니어'
            ],
            'salary': [
                r'(\d{2,4})\s*만원',
                r'(\d{2,4})\s*천원',
                r'연봉\s*(\d{2,4})\s*만원',
                r'월급\s*(\d{2,4})\s*만원'
            ],
            'headcount': [
                r'(\d+)\s*명',
                r'(\d+)\s*인',
                r'(\d+)\s*분',
                r'(\d+)\s*사람'
            ],
            'location': [
                r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)',
                r'(강남|강북|강서|강동|서초|송파|마포|용산|성동|광진|동대문|중랑|성북|노원|도봉|양천|구로|금천|영등포|동작|관악|서대문|은평|중구|종로|용산)'
            ]
        }

    def extract_fields(self, text: str) -> Dict[str, Any]:
        """텍스트에서 필드 정보 추출"""
        extracted_fields = {}

        for field_name, patterns in self.field_patterns.items():
            value = self._extract_field_value(text, patterns, field_name)
            if value:
                extracted_fields[field_name] = value

        return extracted_fields

    def _extract_field_value(self, text: str, patterns: List[str], field_name: str) -> str:
        """특정 필드의 값을 추출"""
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                if field_name == 'experience':
                    return self._process_experience(text, matches)
                elif field_name == 'salary':
                    return self._process_salary(text, matches)
                elif field_name == 'headcount':
                    return f"{matches[0]}명"
                else:
                    # 부서, 지역 등은 첫 번째 매치 사용
                    return matches[0] if isinstance(matches[0], str) else matches[0][0]

        return None

    def _process_experience(self, text: str, matches: List) -> str:
        """경력 정보 처리"""
        if '신입' in text or '초급' in text:
            return '신입'
        elif '시니어' in text or '고급' in text:
            return '시니어'
        elif '중급' in text:
            return '중급'
        elif '주니어' in text:
            return '주니어'
        else:
            # 숫자 매치가 있는 경우
            for match in matches:
                if isinstance(match, tuple) and match[0].isdigit():
                    return f"{match[0]}년"
                elif isinstance(match, str) and match.isdigit():
                    return f"{match}년"

        return None

    def _process_salary(self, text: str, matches: List) -> str:
        """급여 정보 처리"""
        for match in matches:
            if isinstance(match, tuple):
                salary = match[0]
            else:
                salary = match

            if '천원' in text:
                return f"{int(salary) * 10}만원"
            else:
                return f"{salary}만원"

        return None

    def extract_job_posting_fields(self, text: str) -> Dict[str, Any]:
        """채용공고 관련 필드 추출 (기존 agent_system의 _extract_job_posting_fields와 동일)"""
        extracted_fields = {}

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
                if len(department) >= 2:  # 2글자 이상인 경우만
                    extracted_fields['department'] = department
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
                    extracted_fields['experience'] = '신입'
                elif '시니어' in text or '고급' in text:
                    extracted_fields['experience'] = '시니어'
                elif '중급' in text:
                    extracted_fields['experience'] = '중급'
                elif '주니어' in text:
                    extracted_fields['experience'] = '주니어'
                else:
                    experience = matches[0] if isinstance(matches[0], str) else f"{matches[0][0]}년"
                    extracted_fields['experience'] = experience
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
                extracted_fields['salary'] = f"{salary}만원"
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
                extracted_fields['headcount'] = f"{matches[0]}명"
                headcount_found = True
                break

        # 인원수가 입력되지 않으면 기본값 0명으로 설정
        if not headcount_found:
            extracted_fields['headcount'] = "0명"

        # 지역 추출
        location_patterns = [
            r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)',
            r'(강남|강북|강서|강동|서초|송파|마포|용산|성동|광진|동대문|중랑|성북|노원|도봉|양천|구로|금천|영등포|동작|관악|서대문|은평|중구|종로|용산)'
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                extracted_fields['location'] = matches[0]
                break

        return extracted_fields

