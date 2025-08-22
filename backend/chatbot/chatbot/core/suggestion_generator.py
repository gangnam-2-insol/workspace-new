"""
필드별 추천문구 생성기
일반적으로 많이 쓰이는 필드 정보 + 기존 데이터 학습 방식
"""

import json
import re
from typing import Dict, List, Any, Tuple
try:
    from openai_service import OpenAIService
except ImportError:
    OpenAIService = None
import os
from dotenv import load_dotenv
from collections import Counter, defaultdict

load_dotenv()

# OpenAI 설정
try:
    openai_service = OpenAIService(model_name="gpt-4o") if OpenAIService else None
except Exception as e:
    print(f"OpenAI 서비스 초기화 실패: {e}")
    openai_service = None

class SuggestionGenerator:
    def __init__(self):
        # 일반적으로 많이 쓰이는 필드 정보 (업계 표준)
        self.common_field_patterns = {
            '직무명': {
                'patterns': [
                    '프론트엔드 개발자', '백엔드 개발자', '풀스택 개발자', '모바일 개발자',
                    '웹 개발자', '서버 개발자', '데이터 분석가', '데이터 사이언티스트',
                    'UI/UX 디자이너', 'DevOps 엔지니어', 'QA 엔지니어', '시스템 엔지니어',
                    '네트워크 엔지니어', '보안 엔지니어', 'AI/ML 엔지니어', '블록체인 개발자',
                    '게임 개발자', '임베디드 개발자', '클라우드 엔지니어', 'SRE 엔지니어'
                ],
                'frequency': {
                    '프론트엔드 개발자': 0.25, '백엔드 개발자': 0.22, '풀스택 개발자': 0.18,
                    '데이터 분석가': 0.12, 'UI/UX 디자이너': 0.08, 'DevOps 엔지니어': 0.06,
                    '모바일 개발자': 0.05, 'QA 엔지니어': 0.04
                }
            },
            '기술스택': {
                'patterns': {
                    '프론트엔드': ['React', 'Vue', 'Angular', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Sass', 'Webpack'],
                    '백엔드': ['Python', 'Java', 'Node.js', 'C#', 'Go', 'PHP', 'Ruby', 'Django', 'Spring', 'Express'],
                    '데이터베이스': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'Elasticsearch'],
                    '클라우드': ['AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins'],
                    '데이터': ['Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Spark', 'Hadoop']
                },
                'frequency': {
                    'React': 0.35, 'JavaScript': 0.32, 'Python': 0.28, 'Java': 0.25,
                    'Node.js': 0.20, 'TypeScript': 0.18, 'AWS': 0.15, 'Docker': 0.12,
                    'MySQL': 0.10, 'MongoDB': 0.08
                }
            },
            '경력요건': {
                'patterns': [
                    '신입', '경력 1년 이상', '경력 2년 이상', '경력 3년 이상', '경력 5년 이상',
                    '경력 7년 이상', '경력 10년 이상', '시니어', '주니어', '중급', '고급'
                ],
                'frequency': {
                    '경력 2년 이상': 0.30, '경력 3년 이상': 0.25, '신입': 0.20,
                    '경력 1년 이상': 0.15, '시니어': 0.10
                }
            },
            '자격요건': {
                'patterns': [
                    '컴퓨터 관련 학과 졸업자', '관련 분야 경력', '원활한 커뮤니케이션 능력',
                    '문제 해결 능력', '창의적 사고', '팀워크와 협업 능력', '학습 의지',
                    '책임감', '성실성', '적극성', '논리적 사고', '분석 능력'
                ],
                'frequency': {
                    '컴퓨터 관련 학과 졸업자': 0.40, '관련 분야 경력': 0.35,
                    '원활한 커뮤니케이션 능력': 0.30, '문제 해결 능력': 0.25,
                    '팀워크와 협업 능력': 0.20, '학습 의지': 0.15
                }
            },
            '우대조건': {
                'patterns': [
                    '관련 자격증 보유자', '오픈소스 프로젝트 참여 경험', '해외 출장 가능자',
                    '영어 회화 가능자', '애자일 개발 방법론 경험자', '대규모 시스템 경험',
                    '리더십 경험', '멘토링 경험', '기술 블로그 운영', '컨퍼런스 발표 경험'
                ],
                'frequency': {
                    '관련 자격증 보유자': 0.25, '오픈소스 프로젝트 참여 경험': 0.20,
                    '영어 회화 가능자': 0.18, '애자일 개발 방법론 경험자': 0.15,
                    '대규모 시스템 경험': 0.12, '해외 출장 가능자': 0.10
                }
            },
            '근무지': {
                'patterns': [
                    '서울 강남구', '서울 서초구', '서울 마포구', '서울 영등포구', '서울 송파구',
                    '경기 성남시', '경기 수원시', '경기 용인시', '경기 고양시', '경기 부천시',
                    '원격 근무', '하이브리드 근무', '재택 근무'
                ],
                'frequency': {
                    '서울 강남구': 0.35, '서울 서초구': 0.20, '원격 근무': 0.15,
                    '경기 성남시': 0.12, '서울 마포구': 0.08, '하이브리드 근무': 0.10
                }
            },
            '연봉': {
                'patterns': [
                    '면접 후 결정', '경력에 따라 협의', '업계 평균 이상', '성과에 따른 인센티브',
                    '매년 성과 평가 후 인상', '스톡옵션 제공', '성과급 지급'
                ],
                'frequency': {
                    '면접 후 결정': 0.40, '경력에 따라 협의': 0.30, '업계 평균 이상': 0.20,
                    '성과에 따른 인센티브': 0.10
                }
            }
        }
        
        # 기존 데이터 학습 결과 (실제 운영 시 DB에서 로드)
        self.learned_patterns = self._load_learned_patterns()
        
        # 필드 간 연관성 (예: 프론트엔드 개발자 + React, 백엔드 개발자 + Python)
        self.field_correlations = {
            '프론트엔드 개발자': {
                '기술스택': ['React', 'TypeScript', 'JavaScript', 'Vue', 'Angular'],
                '자격요건': ['웹 개발 경험', 'UI/UX 이해도', '반응형 웹 개발 경험'],
                '우대조건': ['모던 프레임워크 경험', '성능 최적화 경험', '크로스 브라우징 경험']
            },
            '백엔드 개발자': {
                '기술스택': ['Python', 'Java', 'Node.js', 'Spring', 'Django'],
                '자격요건': ['서버 개발 경험', '데이터베이스 설계 경험', 'API 개발 경험'],
                '우대조건': ['대규모 트래픽 처리 경험', '마이크로서비스 아키텍처 경험', '클라우드 인프라 경험']
            },
            '데이터 분석가': {
                '기술스택': ['Python', 'Pandas', 'NumPy', 'SQL', 'R'],
                '자격요건': ['통계학 지식', '데이터 분석 경험', '비즈니스 인사이트 도출 능력'],
                '우대조건': ['머신러닝 경험', '시각화 도구 경험', '대용량 데이터 처리 경험']
            }
        }

    def generate_field_suggestions(self, extracted_fields: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """추출된 필드에 대한 추천문구 생성 (일반 패턴 + 학습 데이터 + AI 결합)"""
        try:
            print(f"\n🎯 [추천문구 생성 시작] 원본 텍스트: {original_text[:100]}...")
            
            # 1단계: 일반 패턴 기반 추천
            pattern_suggestions = self._generate_pattern_suggestions(extracted_fields)
            print(f"🎯 [일반 패턴] 추천 완료: {len(pattern_suggestions)}개 필드")
            
            # 2단계: 학습 데이터 기반 추천
            learned_suggestions = self._generate_learned_suggestions(extracted_fields)
            print(f"🎯 [학습 데이터] 추천 완료: {len(learned_suggestions)}개 필드")
            
            # 3단계: AI 기반 보완 추천
            ai_suggestions = self._generate_ai_suggestions(extracted_fields, original_text)
            print(f"🎯 [AI 보완] 추천 완료: {len(ai_suggestions)}개 필드")
            
            # 4단계: 모든 추천 병합 및 순위 결정
            final_suggestions = self._merge_all_suggestions(
                pattern_suggestions, learned_suggestions, ai_suggestions
            )
            print(f"🎯 [최종 병합] 완료")
            
            return final_suggestions
            
        except Exception as e:
            print(f"❌ [추천문구 생성 오류] {e}")
            return {}

    def _generate_pattern_suggestions(self, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """일반 패턴 기반 추천"""
        suggestions = {}
        
        for field_name, field_value in extracted_fields.items():
            korean_field_name = self._get_korean_field_name(field_name)
            
            if korean_field_name in self.common_field_patterns:
                field_config = self.common_field_patterns[korean_field_name]
                
                # 빈도수 기반으로 상위 추천 선택
                sorted_patterns = sorted(
                    field_config['frequency'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # 상위 3개 추천
                top_suggestions = [pattern for pattern, freq in sorted_patterns[:3]]
                
                suggestions[korean_field_name] = {
                    'extracted': field_value,
                    'suggestions': top_suggestions,
                    'source': 'pattern'
                }
        
        return suggestions

    def _generate_learned_suggestions(self, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """학습 데이터 기반 추천"""
        suggestions = {}
        
        # 직무명이 있으면 연관성 기반 추천
        if 'position' in extracted_fields:
            position = extracted_fields['position']
            
            if position in self.field_correlations:
                correlations = self.field_correlations[position]
                
                for field_type, correlated_items in correlations.items():
                    if field_type in ['기술스택', '자격요건', '우대조건']:
                        suggestions[field_type] = {
                            'extracted': extracted_fields.get(field_type, ''),
                            'suggestions': correlated_items[:3],  # 상위 3개
                            'source': 'learned'
                        }
        
        return suggestions

    def _generate_ai_suggestions(self, extracted_fields: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """AI 기반 보완 추천"""
        try:
            # 필드별로 추천문구 생성 프롬프트 작성
            field_prompts = {}
            
            for field_name, field_value in extracted_fields.items():
                if field_name in ['position', 'tech_stack', 'experience', 'requirements', 'preferences', 'salary', 'location', 'company_type']:
                    korean_field_name = self._get_korean_field_name(field_name)
                    field_prompts[korean_field_name] = {
                        'extracted': field_value,
                        'field_name': korean_field_name
                    }
            
            # AI에게 추천문구 생성 요청
            prompt = f"""
당신은 채용공고 추천문구 생성 전문가입니다. 다음 텍스트를 바탕으로 추천 문구를 생성해주세요.

원본 텍스트: {original_text}

추출된 필드: {json.dumps(field_prompts, ensure_ascii=False, indent=2)}

반드시 다음 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요:

{{
  "직무명": {{
    "extracted": "백엔드 개발자",
    "suggestions": ["Python 백엔드 개발자", "웹 백엔드 엔지니어", "서버 개발자"]
  }},
  "자격요건": {{
    "extracted": "컴퓨터 관련 학과 졸업",
    "suggestions": ["컴퓨터공학 또는 관련 학과 졸업", "웹 개발 경험 2년 이상", "Python 개발 경험"]
  }},
  "우대조건": {{
    "extracted": "AWS 경험자 우대",
    "suggestions": ["AWS 클라우드 서비스 경험자", "Docker/Kubernetes 경험자", "팀 협업 경험자"]
  }},
  "근무지": {{
    "extracted": "서울",
    "suggestions": ["서울 강남구", "서울 및 수도권", "서울시 전체"]
  }},
  "연봉": {{
    "extracted": "4000만원",
    "suggestions": ["연봉 4000-5000만원", "경력에 따라 협의", "성과에 따른 인센티브 제공"]
  }}
}}

중요:
- JSON만 응답하고 다른 텍스트는 포함하지 마세요
- 각 필드별로 2-3개의 실용적인 추천문구를 생성하세요
- 한국어로 작성하세요
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
                    ai_suggestions = json.loads(json_str)
                    
                    # source 정보 추가
                    for field_name, field_data in ai_suggestions.items():
                        field_data['source'] = 'ai'
                    
                    return ai_suggestions
                else:
                    print(f"⚠️ AI 응답에서 JSON을 찾을 수 없음: {result_text}")
                    return {}
            except json.JSONDecodeError as e:
                print(f"⚠️ AI 응답 JSON 파싱 오류: {e}")
                return {}
                
        except Exception as e:
            print(f"❌ AI 추천문구 생성 오류: {e}")
            return {}

    def _merge_all_suggestions(self, pattern_suggestions: Dict, learned_suggestions: Dict, ai_suggestions: Dict) -> Dict[str, Any]:
        """모든 추천 병합 및 순위 결정"""
        merged_suggestions = {}
        
        # 모든 필드에 대해 추천 병합
        all_fields = set(list(pattern_suggestions.keys()) + list(learned_suggestions.keys()) + list(ai_suggestions.keys()))
        
        for field_name in all_fields:
            all_suggestions = []
            
            # 각 소스별 추천 수집
            sources = {
                'pattern': pattern_suggestions.get(field_name, {}),
                'learned': learned_suggestions.get(field_name, {}),
                'ai': ai_suggestions.get(field_name, {})
            }
            
            # 추출된 값이 있으면 첫 번째로 추가
            extracted_value = None
            for source_data in sources.values():
                if source_data.get('extracted'):
                    extracted_value = source_data['extracted']
                    break
            
            if extracted_value:
                all_suggestions.append(extracted_value)
            
            # 각 소스별 추천 추가 (중복 제거)
            for source_name, source_data in sources.items():
                if source_data.get('suggestions'):
                    for suggestion in source_data['suggestions']:
                        if suggestion not in all_suggestions:
                            all_suggestions.append(suggestion)
            
            # 최대 5개까지만 유지
            merged_suggestions[field_name] = {
                'extracted': extracted_value or '',
                'suggestions': all_suggestions[:5],
                'sources': [name for name, data in sources.items() if data.get('suggestions')]
            }
        
        return merged_suggestions

    def _load_learned_patterns(self) -> Dict[str, Any]:
        """학습된 패턴 로드 (실제 운영 시 DB에서 로드)"""
        # 실제 운영 시에는 DB에서 기존 채용공고 데이터를 분석한 결과를 로드
        return {
            'company_preferences': {
                '스타트업': {
                    '우대조건': ['적극적인 태도', '빠른 학습 능력', '다양한 업무 경험'],
                    '연봉': ['스톡옵션 제공', '성과에 따른 인센티브', '업계 평균 이상']
                },
                '대기업': {
                    '우대조건': ['관련 자격증', '대규모 프로젝트 경험', '리더십 경험'],
                    '연봉': ['경력에 따라 협의', '성과급 지급', '복리후생 우수']
                }
            },
            'position_trends': {
                '프론트엔드 개발자': {
                    'trending_skills': ['TypeScript', 'React', 'Next.js', 'Tailwind CSS'],
                    'common_requirements': ['웹 표준 이해', '반응형 웹 개발 경험', '크로스 브라우징 경험']
                }
            }
        }

    def _get_korean_field_name(self, english_field_name: str) -> str:
        """영어 필드명을 한국어로 변환"""
        field_mapping = {
            'position': '직무명',
            'tech_stack': '기술스택',
            'experience': '경력요건',
            'requirements': '자격요건',
            'preferences': '우대조건',
            'salary': '연봉',
            'location': '근무지',
            'company_type': '회사유형'
        }
        return field_mapping.get(english_field_name, english_field_name)

# 전역 인스턴스
suggestion_generator = SuggestionGenerator()
