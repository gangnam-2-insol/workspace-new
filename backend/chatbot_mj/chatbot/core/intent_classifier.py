"""
의도 분류기
"""

import re
from typing import Dict, Any, List

class IntentClassifier:
    """의도 분류기 클래스"""
    
    def __init__(self):
        self.intent_patterns = {
            'recruit': [
                r'채용|구인|뽑|모집|채용공고|구인공고',
                r'개발자|엔지니어|디자이너|마케터|영업|기획',
                r'부서|팀|직무|포지션|직책',
                r'경력|연차|년차|신입|주니어|시니어',
                r'급여|연봉|월급|봉급|임금',
                r'인원|명|사람|분'
            ],
            'question': [
                r'무엇|뭐|어떤|어떻게|왜|언제|어디',
                r'질문|궁금|알고싶|궁금해',
                r'도움|도와|가르쳐|설명'
            ],
            'chat': [
                r'안녕|하이|헬로|반가워',
                r'고마워|감사|땡큐',
                r'잘가|바이|안녕히'
            ]
        }
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """텍스트의 의도를 분류"""
        text_lower = text.lower()
        
        # 각 의도별 점수 계산
        scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[intent] = score
        
        # 가장 높은 점수의 의도 선택
        if scores:
            max_intent = max(scores, key=scores.get)
            max_score = scores[max_intent]
            
            if max_score > 0:
                return {
                    'intent': max_intent,
                    'confidence': min(max_score / 5.0, 1.0),  # 최대 1.0으로 정규화
                    'scores': scores
                }
        
        # 기본값
        return {
            'intent': 'chat',
            'confidence': 0.5,
            'scores': scores
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """엔티티 추출"""
        entities = {}
        
        # 부서/직무 추출
        department_patterns = [
            r'([가-힣]+)\s*(개발자|엔지니어|디자이너|마케터|영업|기획)',
            r'([가-힣]+)\s*(팀|부서|팀원|사원)'
        ]
        
        for pattern in department_patterns:
            matches = re.findall(pattern, text)
            if matches:
                entities['department'] = matches[0][0]
                break
        
        # 경력 추출
        experience_patterns = [
            r'(\d+)\s*년\s*(경력|경험)',
            r'(\d+)\s*년차',
            r'신입|주니어|시니어'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if '신입' in text:
                    entities['experience'] = '신입'
                elif '시니어' in text:
                    entities['experience'] = '시니어'
                elif '주니어' in text:
                    entities['experience'] = '주니어'
                else:
                    entities['experience'] = f"{matches[0]}년"
                break
        
        # 급여 추출
        salary_patterns = [
            r'(\d{2,4})\s*만원',
            r'연봉\s*(\d{2,4})\s*만원'
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, text)
            if matches:
                entities['salary'] = f"{matches[0]}만원"
                break
        
        return entities

