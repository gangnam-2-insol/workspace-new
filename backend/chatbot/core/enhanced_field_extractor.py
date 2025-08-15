"""
향상된 필드 추출기
AI 추론 + 사전 매칭 + 규칙 기반 결합 방식
"""

import re
import json
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini AI 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

class EnhancedFieldExtractor:
    def __init__(self):
        # 기술스택 사전 (대소문자, 변형 포함)
        self.tech_dictionary = {
            # 프론트엔드
            'react': ['React', 'react', 'React.js', '리액트', 'reactjs'],
            'vue': ['Vue', 'vue', 'Vue.js', '뷰', 'vuejs'],
            'angular': ['Angular', 'angular', '앵귤러'],
            'typescript': ['TypeScript', 'typescript', '타입스크립트', 'TS'],
            'javascript': ['JavaScript', 'javascript', '자바스크립트', 'JS'],
            'html': ['HTML', 'html'],
            'css': ['CSS', 'css'],
            'sass': ['Sass', 'sass', 'SCSS', 'scss'],
            'less': ['Less', 'less'],
            'webpack': ['Webpack', 'webpack'],
            'babel': ['Babel', 'babel'],
            'eslint': ['ESLint', 'eslint'],
            'redux': ['Redux', 'redux'],
            'vuex': ['Vuex', 'vuex'],
            'mobx': ['MobX', 'mobx'],
            
            # 백엔드
            'python': ['Python', 'python', '파이썬'],
            'java': ['Java', 'java', '자바'],
            'node.js': ['Node.js', 'node.js', 'NodeJS', 'nodejs', '노드'],
            'django': ['Django', 'django'],
            'spring': ['Spring', 'spring', '스프링'],
            'express': ['Express', 'express'],
            'flask': ['Flask', 'flask'],
            'fastapi': ['FastAPI', 'fastapi'],
            
            # 데이터베이스
            'mysql': ['MySQL', 'mysql'],
            'postgresql': ['PostgreSQL', 'postgresql', 'Postgres', 'postgres'],
            'mongodb': ['MongoDB', 'mongodb'],
            'redis': ['Redis', 'redis'],
            
            # 클라우드/인프라
            'aws': ['AWS', 'aws', 'Amazon Web Services'],
            'gcp': ['GCP', 'gcp', 'Google Cloud Platform'],
            'azure': ['Azure', 'azure'],
            'docker': ['Docker', 'docker'],
            'kubernetes': ['Kubernetes', 'kubernetes', 'k8s'],
            
            # 기타
            'git': ['Git', 'git'],
            'jenkins': ['Jenkins', 'jenkins'],
            'jira': ['Jira', 'jira'],
            'slack': ['Slack', 'slack']
        }
        
        # 직무명 사전
        self.job_dictionary = {
            '프론트엔드 개발자': ['프론트엔드 개발자', 'Frontend Developer', '웹 개발자', 'UI 개발자'],
            '백엔드 개발자': ['백엔드 개발자', 'Backend Developer', '서버 개발자', 'API 개발자'],
            '풀스택 개발자': ['풀스택 개발자', 'Full Stack Developer', 'Full-Stack Developer'],
            '모바일 개발자': ['모바일 개발자', 'Mobile Developer', 'iOS 개발자', 'Android 개발자'],
            '데이터 분석가': ['데이터 분석가', 'Data Analyst', '데이터 사이언티스트', 'Data Scientist'],
            'DevOps 엔지니어': ['DevOps 엔지니어', 'DevOps Engineer', '인프라 엔지니어'],
            'UI/UX 디자이너': ['UI/UX 디자이너', 'UI Designer', 'UX Designer', '디자이너'],
            '마케팅 매니저': ['마케팅 매니저', 'Marketing Manager', '마케터'],
            '영업 매니저': ['영업 매니저', 'Sales Manager', '영업사원'],
            '기획자': ['기획자', 'Planner', '전략 기획자', '서비스 기획자'],
            '운영 매니저': ['운영 매니저', 'Operation Manager', '운영자']
        }
        
        # 우대조건 키워드
        self.preference_keywords = [
            '우대', '경험', '능력', '자격', '이해도', '관심', '적응력', '협업', '참여', 
            '활용', '구현', '선호', '가능', '바람직', '좋음', '더욱 좋음'
        ]
        
        # 자격요건 키워드
        self.requirement_keywords = [
            '필수', '요구', '필요', '기본', '기본적', '최소', '최소한'
        ]

    def extract_fields_enhanced(self, user_input: str) -> Dict[str, Any]:
        """향상된 필드 추출 (AI + 사전 + 규칙 결합)
        실패 시에도 규칙 기반 결과는 반드시 반환"""
        print(f"\n🔍 [향상된 필드 추출 시작] 사용자 입력: {user_input}")
        
        # 1단계: 규칙 기반 초기 추출 (항상 수행)
        initial_fields = {}
        try:
            initial_fields = self._rule_based_extraction(user_input)
        except Exception as e:
            print(f"⚠️ [규칙 기반 추출 오류] {e}")
            initial_fields = {}
        print(f"🔍 [1단계] 규칙 기반 추출 결과: {initial_fields}")
        
        # 2단계: AI 기반 보완 추출 (실패해도 규칙 결과 유지)
        ai_fields: Dict[str, Any] = {}
        try:
            ai_fields = self._ai_based_extraction(user_input)
            print(f"🔍 [2단계] AI 기반 추출 결과: {ai_fields}")
        except Exception as e:
            print(f"⚠️ [AI 기반 추출 오류] {e}")
            ai_fields = {}
        
        # 3단계: 결과 병합 및 정리
        try:
            final_fields = self._merge_and_clean_fields(initial_fields, ai_fields)
        except Exception as e:
            print(f"⚠️ [병합 단계 오류] {e}")
            final_fields = initial_fields
        
        print(f"🔍 [3단계] 최종 병합 결과: {final_fields}")
        return final_fields

    def _rule_based_extraction(self, user_input: str) -> Dict[str, Any]:
        """규칙 기반 초기 추출"""
        fields = {}
        
        # 1. 직무명 추출 (사전 매칭)
        for job_title, variations in self.job_dictionary.items():
            for variation in variations:
                if variation.lower() in user_input.lower():
                    fields['position'] = job_title
                    break
            if 'position' in fields:
                break
        
        # 1-1. 일반 직무 패턴 (담당자/매니저 등)
        try:
            position_match = re.search(r'([가-힣A-Za-z]+)\s*(담당자|매니저|전문가)', user_input)
            if position_match:
                # 예: 마케팅 담당자, 운영 매니저
                fields['position'] = f"{position_match.group(1)} {position_match.group(2)}".strip()
        except Exception:
            pass

        # 2. 기술스택 추출 (사전 매칭)
        tech_stack = []
        for tech_name, variations in self.tech_dictionary.items():
            for variation in variations:
                if variation.lower() in user_input.lower():
                    tech_stack.append(tech_name.title())  # 첫 글자 대문자로
                    break
        
        if tech_stack:
            fields['tech_stack'] = list(set(tech_stack))  # 중복 제거
        
        # 3. 경력 요구사항 추출
        experience_patterns = [
            r'경력\s*(\d+)\s*년\s*(이상|이하|정도|내외)?',
            r'(\d+)\s*년\s*(이상|이하|정도|내외)?\s*경력',
            r'(\d+)\s*년\s*(이상|이하|정도|내외)?\s*경험',
            r'경험이\s*(\d+)\s*년\s*(이상|이하|정도|내외)?',
            r'(\d+)\s*년차'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, user_input)
            if match:
                years = match.group(1)
                fields['experience'] = f"{years}년"
                break
        
        # 4. 급여 정보 추출
        salary_patterns = [
            r'(\d{2,4})\s*만원',
            r'연봉\s*(\d{2,4})\s*만원',
            r'월급\s*(\d{2,4})\s*만원'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, user_input)
            if match:
                salary = match.group(1)
                fields['salary'] = f"{salary}만원"
                break
        
        if '면접 후 결정' in user_input or '협의 가능' in user_input:
            fields['salary'] = '면접 후 결정'
        
        # 5. 근무지 추출
        location_keywords = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        for location in location_keywords:
            if location in user_input:
                fields['location'] = location
                break

        # 6. 인원수 추출 (예: 1명, 2명)
        try:
            m = re.search(r'(\d+)\s*명', user_input)
            if m:
                fields['headcount'] = f"{m.group(1)}명"
        except Exception:
            pass

        # 7. 경력 키워드 추출 (신입/경력/시니어 등)
        if '신입' in user_input:
            fields.setdefault('experience', '신입')
        elif '시니어' in user_input:
            fields.setdefault('experience', '시니어')
        elif '경력' in user_input:
            fields.setdefault('experience', '경력')
        
        return fields

    def _ai_based_extraction(self, user_input: str) -> Dict[str, Any]:
        """AI 기반 보완 추출"""
        try:
            prompt = f"""
다음 채용공고 텍스트에서 채용 관련 정보를 JSON 형태로 추출해주세요.

텍스트: {user_input}

다음 필드들을 추출해주세요:
- position: 직무명 (예: 프론트엔드 개발자, 백엔드 개발자)
- tech_stack: 기술스택 배열 (예: ["React", "TypeScript", "JavaScript"])
- experience: 경력 요구사항 (예: "2년", "신입", "시니어")
- requirements: 자격요건 배열 (예: ["웹 개발 경험", "커뮤니케이션 능력"])
- preferences: 우대조건 배열 (예: ["애자일 경험", "팀 협업 능력"])
- salary: 급여 정보 (예: "면접 후 결정", "3000만원")
- location: 근무지 (예: "서울", "부산")
- company_type: 회사 유형 (예: "스타트업", "대기업")

추출할 수 없는 필드는 null로 설정하고, JSON 형식으로만 응답해주세요.
"""

            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 파싱
            try:
                # JSON 블록 추출
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    ai_fields = json.loads(json_str)
                    return ai_fields
                else:
                    print(f"⚠️ AI 응답에서 JSON을 찾을 수 없음: {result_text}")
                    return {}
            except json.JSONDecodeError as e:
                print(f"⚠️ AI 응답 JSON 파싱 오류: {e}")
                return {}
                
        except Exception as e:
            print(f"❌ AI 기반 추출 오류: {e}")
            return {}

    def _merge_and_clean_fields(self, rule_fields: Dict[str, Any], ai_fields: Dict[str, Any]) -> Dict[str, Any]:
        """결과 병합 및 정리"""
        merged_fields = {}
        
        # 규칙 기반 결과를 기본으로 사용
        merged_fields.update(rule_fields)
        
        # AI 결과로 보완
        for key, ai_value in ai_fields.items():
            if ai_value is not None and ai_value != "":
                if key not in merged_fields or merged_fields[key] is None:
                    merged_fields[key] = ai_value
                elif isinstance(ai_value, list) and isinstance(merged_fields[key], list):
                    # 리스트인 경우 병합
                    merged_fields[key] = list(set(merged_fields[key] + ai_value))
                elif isinstance(ai_value, list) and not isinstance(merged_fields[key], list):
                    # AI가 리스트로 추출했는데 규칙은 단일값인 경우
                    merged_fields[key] = ai_value
        
        # 필드 정리
        cleaned_fields = {}
        for key, value in merged_fields.items():
            if value is not None and value != "":
                if isinstance(value, list) and len(value) == 0:
                    continue
                cleaned_fields[key] = value
        
        return cleaned_fields

# 전역 인스턴스
enhanced_extractor = EnhancedFieldExtractor()
