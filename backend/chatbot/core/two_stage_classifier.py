"""
2단계 분류 시스템
1차: 점수 기반 필터링 (빠름, 비용 낮음)
2차: 의미 기반 재판단 (정확함, 비용 높음)
"""

import re
import json
from typing import Dict, Any, Tuple, Optional
try:
    from openai_service import OpenAIService
except ImportError:
    OpenAIService = None
import os
from dotenv import load_dotenv
from .suggestion_generator import suggestion_generator

load_dotenv()

# OpenAI 설정
try:
    openai_service = OpenAIService(model_name="gpt-4o") if OpenAIService else None
except Exception as e:
    openai_service = None

class TwoStageClassifier:
    def __init__(self):
        # 1차 점수 기반 키워드 그룹
        self.keyword_groups = {
            'recruitment_signal': {
                'keywords': ['모집', '채용', '구인', '환영', '모십니다', '참여', '공고', '지원'],
                'weight': 3,
                'max_count': 1
            },
            'submission_docs': {
                'keywords': ['이력서', '자기소개서', '포트폴리오', '제출', '서류', '면접', '접수'],
                'weight': 2,
                'max_count': 1
            },
            'qualifications': {
                'keywords': ['경험', '능력', '자격', '이해도', '관심', '적응력', '협업', '참여', '활용', '구현'],
                'weight': 1,
                'max_count': 2
            },
            'work_conditions': {
                'keywords': ['연봉', '월급', '급여', '근무지', '복리후생', '재택', '출근'],
                'weight': 1,
                'max_count': 1
            },
            'job_titles': {
                'keywords': ['개발자', '엔지니어', '디자이너', '매니저', '기획자', '분석가', '컨설턴트'],
                'weight': 2,
                'max_count': 1
            },
            'tech_stack': {
                'keywords': ['React', 'Python', 'Java', 'JavaScript', 'Node.js', 'Django', 'Spring', 'AWS', 'Docker'],
                'weight': 1,
                'max_count': 2
            }
        }
        
        # 조합 보너스 규칙
        self.combination_bonuses = [
            (['recruitment_signal', 'submission_docs'], 2),  # 모집 + 제출서류
            (['recruitment_signal', 'qualifications'], 1),   # 모집 + 자격요건
            (['job_titles', 'tech_stack'], 2),              # 직무명 + 기술스택
        ]
        
        # 복잡성 보너스 기준
        self.complexity_thresholds = {
            'length': 100,      # 100자 이상
            'sentences': 3,     # 3문장 이상
            'detail_indicators': ['경험', '능력', '우대', '환영', '찾고', '바랍니다']
        }

    def classify_text(self, text: str) -> Dict[str, Any]:
        """2단계 분류 시스템"""
        print(f"\n🔍 [2단계 분류 시작] 텍스트: {text[:100]}...")
        
        # 1차: 점수 기반 필터링
        first_stage_result = self._first_stage_scoring(text)
        print(f"🔍 [1차] 점수: {first_stage_result['score']}, 판정: {first_stage_result['decision']}")
        
        # 2차: 의미 기반 재판단 (1차가 채용으로 확정되지 않은 모든 경우)
        if first_stage_result['decision'] != 'recruitment':
            print(f"🔍 [2차] 1차 판정이 '{first_stage_result['decision']}' → 의미 기반 재분석 수행")
            second_stage_result = self._second_stage_semantic_analysis(text)
            
            final_result = {
                'is_recruitment': second_stage_result.get('is_recruitment', False),
                'confidence': second_stage_result.get('confidence', first_stage_result['confidence']),
                'fields': second_stage_result.get('fields', {}),
                'stage': 'two_stage',
                'first_stage_score': first_stage_result['score']
            }
        else:
            # 1차에서 채용으로 확정된 경우
            final_result = {
                'is_recruitment': True,
                'confidence': first_stage_result['confidence'],
                'fields': first_stage_result['fields'],
                'stage': 'first_stage',
                'first_stage_score': first_stage_result['score']
            }
            # 채용으로 확정되었으나 필드가 비어있으면 2차 의미 기반으로 보강
            if not final_result['fields']:
                print("🔍 [후보강] 채용공고로 확정되었으나 필드가 비어있음 → 2차 의미 기반 보강 실행")
                second_stage = self._second_stage_semantic_analysis(text)
                if second_stage.get('is_recruitment', False) and second_stage.get('fields'):
                    final_result['fields'] = second_stage['fields']
                    final_result['confidence'] = max(final_result['confidence'], second_stage.get('confidence', 0.5))
                    final_result['stage'] = 'first_stage+semantic_enhance'
        
        print(f"🔍 [최종] 채용공고: {final_result['is_recruitment']}, 신뢰도: {final_result['confidence']}")
        return final_result

    def _first_stage_scoring(self, text: str) -> Dict[str, Any]:
        """1차 점수 기반 필터링"""
        score = 0
        group_counts = {}
        
        # 각 키워드 그룹별 점수 계산
        for group_name, group_config in self.keyword_groups.items():
            count = 0
            for keyword in group_config['keywords']:
                if keyword.lower() in text.lower():
                    count += 1
            
            # 최대 카운트 제한
            count = min(count, group_config['max_count'])
            group_counts[group_name] = count
            
            # 점수 계산
            score += count * group_config['weight']
        
        # 조합 보너스 적용
        for groups, bonus in self.combination_bonuses:
            if all(group_counts.get(group, 0) > 0 for group in groups):
                score += bonus
                print(f"🔍 [1차] 조합 보너스 +{bonus}: {groups}")
        
        # 복잡성 보너스
        complexity_bonus = self._calculate_complexity_bonus(text)
        score += complexity_bonus
        if complexity_bonus > 0:
            print(f"🔍 [1차] 복잡성 보너스 +{complexity_bonus}")
        
        # 신뢰도 계산
        confidence = min(score / 10.0, 1.0)  # 최대 10점을 1.0으로 정규화
        
        # 판정 기준
        if score >= 5:
            decision = 'recruitment'
        elif score >= 3:
            decision = 'ambiguous'
        else:
            decision = 'general'
        
        # 기본 필드 추출 (1차에서 가능한 것만)
        basic_fields = self._extract_basic_fields(text)
        
        return {
            'score': score,
            'decision': decision,
            'confidence': confidence,
            'fields': basic_fields,
            'group_counts': group_counts
        }

    def _calculate_complexity_bonus(self, text: str) -> int:
        """복잡성 보너스 계산"""
        bonus = 0
        
        # 길이 보너스
        if len(text) >= self.complexity_thresholds['length']:
            bonus += 1
        
        # 문장 수 보너스
        sentence_count = len(re.split(r'[.!?]', text))
        if sentence_count >= self.complexity_thresholds['sentences']:
            bonus += 1
        
        # 상세 지표 보너스
        detail_count = sum(1 for indicator in self.complexity_thresholds['detail_indicators'] 
                          if indicator in text)
        if detail_count >= 2:
            bonus += 1
        
        return bonus

    def _extract_basic_fields(self, text: str) -> Dict[str, Any]:
        """1차에서 추출 가능한 기본 필드"""
        fields = {}
        
        # 직무명 추출
        job_patterns = [
            r'([가-힣]+)\s*개발자',
            r'([가-힣]+)\s*엔지니어',
            r'([가-힣]+)\s*디자이너',
            r'([가-힣]+)\s*매니저',
            r'([가-힣]+)\s*기획자',
            r'([가-힣]+)\s*분석가'
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, text)
            if match:
                fields['position'] = match.group(0)
                break
        
        # 기술스택 추출
        tech_keywords = ['React', 'Python', 'Java', 'JavaScript', 'Node.js', 'Django', 'Spring', 'AWS', 'Docker']
        tech_stack = []
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                tech_stack.append(tech)
        
        if tech_stack:
            fields['tech_stack'] = tech_stack
        
        return fields

    def _second_stage_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """2차 의미 기반 재분석 + 추천문구 생성"""
        try:
            prompt = f"""
당신은 채용공고 분석 전문가입니다. 다음 텍스트를 분석하여 채용공고인지 판단하고 정보를 추출해주세요.

텍스트: {text}

반드시 다음 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요:

{{
  "isRecruitment": true,
  "confidence": 0.9,
  "fields": {{
    "position": "백엔드 개발자",
    "tech_stack": ["Python", "Django"],
    "experience": "3년 이상",
    "requirements": ["컴퓨터 관련 학과 졸업"],
    "preferences": ["AWS 경험자 우대"],
    "salary": "연봉 4000만원",
    "location": "서울",
    "company_type": "스타트업"
  }}
}}

중요: 
- 채용공고가 아니면 isRecruitment: false, fields: {{}}로 설정
- JSON만 응답하고 다른 텍스트는 포함하지 마세요
- 정보를 찾을 수 없는 필드는 null로 설정하세요
"""

            if openai_service:
                try:
                    # 새로운 이벤트 루프 생성하여 사용
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(openai_service.generate_json_response(prompt))
                        result_text = response.strip() if response else ""
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"AI 호출 중 오류: {e}")
                    result_text = ""
            else:
                result_text = ""
            
            # JSON 파싱
            try:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    
                    fields = result.get('fields', {})
                    
                    # 추천문구 생성 (채용공고인 경우에만)
                    suggestions = {}
                    if result.get('isRecruitment', False) and fields:
                        print(f"🔍 [2차] 추천문구 생성 시작")
                        suggestions = suggestion_generator.generate_field_suggestions(fields, text)
                        print(f"🔍 [2차] 추천문구 생성 완료: {len(suggestions)}개 필드")
                    
                    return {
                        'is_recruitment': result.get('isRecruitment', False),
                        'confidence': result.get('confidence', 0.5),
                        'fields': fields,
                        'suggestions': suggestions
                    }
                else:
                    print(f"⚠️ AI 응답에서 JSON을 찾을 수 없음: {result_text}")
                    return {'is_recruitment': False, 'confidence': 0.3, 'fields': {}, 'suggestions': {}}
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ AI 응답 JSON 파싱 오류: {e}")
                return {'is_recruitment': False, 'confidence': 0.3, 'fields': {}, 'suggestions': {}}
                
        except Exception as e:
            print(f"❌ 2차 분석 오류: {e}")
            return {'is_recruitment': False, 'confidence': 0.3, 'fields': {}, 'suggestions': {}}

# 전역 인스턴스
two_stage_classifier = TwoStageClassifier()
