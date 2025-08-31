"""
주요업무 필드 분리 서비스
main_duties 필드의 내용을 여러 세부 필드로 분리하는 로직
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class DutiesSeparator:
    """주요업무 내용을 여러 필드로 분리하는 클래스"""

    def __init__(self):
        # 각 업무 카테고리별 키워드 패턴
        self.patterns = {
            'core_responsibilities': {
                'keywords': [
                    '핵심', '주요', '메인', '중심', '담당', '책임', '주도', '총괄',
                    '기획', '설계', '개발', '운영', '관리', '분석', '연구',
                    '전략', '방향', '정책', '의사결정'
                ],
                'patterns': [
                    r'핵심\s*업무',
                    r'주요\s*담당',
                    r'메인\s*업무',
                    r'중심\s*역할',
                    r'핵심\s*역할'
                ]
            },
            'daily_tasks': {
                'keywords': [
                    '일상', '매일', '정기', '루틴', '반복', '지속', '상시',
                    '모니터링', '점검', '확인', '업데이트', '유지보수',
                    '데이터', '보고서', '문서', '커뮤니케이션'
                ],
                'patterns': [
                    r'일상\s*업무',
                    r'매일\s*수행',
                    r'정기\s*업무',
                    r'루틴\s*업무',
                    r'반복\s*업무'
                ]
            },
            'project_tasks': {
                'keywords': [
                    '프로젝트', '과제', '개발', '구축', '구현', '제작', '생성',
                    '신규', '신설', '런칭', '출시', '배포', '개선', '최적화',
                    '기획', '설계', '아키텍처', '시스템'
                ],
                'patterns': [
                    r'프로젝트\s*수행',
                    r'신규\s*개발',
                    r'시스템\s*구축',
                    r'서비스\s*개발',
                    r'기능\s*구현'
                ]
            },
            'collaboration_tasks': {
                'keywords': [
                    '협업', '협력', '소통', '커뮤니케이션', '회의', '미팅',
                    '조율', '조정', '연계', '공유', '전달', '보고',
                    '팀', '부서', '외부', '고객', '클라이언트'
                ],
                'patterns': [
                    r'팀\s*협업',
                    r'부서\s*협력',
                    r'외부\s*소통',
                    r'고객\s*커뮤니케이션',
                    r'회의\s*참석'
                ]
            },
            'technical_tasks': {
                'keywords': [
                    '기술', '개발', '코딩', '프로그래밍', '구현', '테스트',
                    'API', '데이터베이스', '서버', '클라우드', '인프라',
                    '알고리즘', '최적화', '성능', '보안', '디버깅',
                    '프레임워크', '라이브러리', '도구', '플랫폼'
                ],
                'patterns': [
                    r'기술\s*개발',
                    r'코드\s*작성',
                    r'API\s*개발',
                    r'데이터베이스\s*설계',
                    r'시스템\s*최적화'
                ]
            },
            'management_tasks': {
                'keywords': [
                    '관리', '감독', '지휘', '리드', '매니징', '운영',
                    '계획', '일정', '스케줄', '예산', '자원', '인력',
                    '평가', '검토', '승인', '결정', '조치', '대응'
                ],
                'patterns': [
                    r'팀\s*관리',
                    r'프로젝트\s*관리',
                    r'일정\s*관리',
                    r'품질\s*관리',
                    r'리소스\s*관리'
                ]
            }
        }

    def separate_duties(self, main_duties: str) -> Dict[str, Optional[str]]:
        """
        주요업무 텍스트를 여러 카테고리로 분리

        Args:
            main_duties: 원본 주요업무 텍스트

        Returns:
            분리된 업무 카테고리별 딕셔너리
        """
        if not main_duties or not main_duties.strip():
            return self._empty_result()

        try:
            logger.info(f"주요업무 분리 시작: {main_duties[:100]}...")

            # 텍스트를 문장 단위로 분리
            sentences = self._split_into_sentences(main_duties)

            # 각 문장을 카테고리별로 분류
            categorized_sentences = self._categorize_sentences(sentences)

            # 분류된 문장들을 필드별로 조합
            result = self._combine_sentences_by_category(categorized_sentences)

            # 빈 필드들 제거 및 정리
            result = self._clean_result(result)

            logger.info(f"주요업무 분리 완료: {len([k for k, v in result.items() if v])}개 카테고리")
            return result

        except Exception as e:
            logger.error(f"주요업무 분리 중 오류: {str(e)}")
            return self._fallback_separation(main_duties)

    def separate_duties_with_smart_extraction(self, main_duties: str) -> Dict[str, Any]:
        """
        스마트 분리 및 추출: 가장 적합한 내용을 자동으로 선별

        Args:
            main_duties: 원본 주요업무 텍스트

        Returns:
            분리된 업무와 스마트 추출 결과
        """
        if not main_duties or not main_duties.strip():
            return self._empty_smart_result()

        try:
            logger.info(f"스마트 업무 분리 시작: {main_duties[:100]}...")

            # 기본 분리 수행
            separated_duties = self.separate_duties(main_duties)

            # 스마트 추출 수행
            smart_extraction = self._perform_smart_extraction(main_duties, separated_duties)

            # 결과 조합
            result = {
                'separated_duties': separated_duties,
                'smart_extraction': smart_extraction,
                'original_text': main_duties,
                'processing_info': {
                    'total_length': len(main_duties),
                    'categories_found': len([k for k, v in separated_duties.items() if v]),
                    'extraction_quality': smart_extraction['quality_score'],
                    'recommended_display': smart_extraction['recommended_content'],
                    'processing_time': datetime.now().isoformat()
                }
            }

            logger.info(f"스마트 분리 완료: 품질점수 {smart_extraction['quality_score']}")
            return result

        except Exception as e:
            logger.error(f"스마트 업무 분리 중 오류: {str(e)}")
            return self._fallback_smart_separation(main_duties)

    def _perform_smart_extraction(self, original_text: str, separated_duties: Dict[str, str]) -> Dict[str, Any]:
        """스마트 추출 로직 수행"""
        # 1. 각 카테고리별 중요도 및 품질 평가
        category_analysis = self._analyze_categories(separated_duties)

        # 2. 가장 적합한 내용 선별
        recommended_content = self._select_best_content(category_analysis, separated_duties)

        # 3. 우선순위 정렬
        priority_order = self._determine_priority_order(category_analysis)

        # 4. 품질 점수 계산
        quality_score = self._calculate_quality_score(category_analysis, original_text)

        return {
            'recommended_content': recommended_content,
            'priority_order': priority_order,
            'category_analysis': category_analysis,
            'quality_score': quality_score,
            'display_suggestions': self._generate_display_suggestions(category_analysis, separated_duties)
        }

    def _analyze_categories(self, separated_duties: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """각 카테고리의 중요도와 품질을 분석"""
        analysis = {}

        # 카테고리별 가중치 (중요도)
        category_weights = {
            'core_responsibilities': 1.0,    # 가장 중요
            'technical_tasks': 0.9,          # 기술적 업무
            'project_tasks': 0.8,            # 프로젝트 업무
            'management_tasks': 0.7,         # 관리 업무
            'collaboration_tasks': 0.6,      # 협업 업무
            'daily_tasks': 0.5               # 일상 업무
        }

        for category, content in separated_duties.items():
            if not content:
                analysis[category] = {
                    'importance_weight': category_weights.get(category, 0.5),
                    'content_length': 0,
                    'quality_score': 0,
                    'keyword_density': 0,
                    'readability': 0,
                    'final_score': 0
                }
                continue

            # 내용 길이 점수 (50-200자가 최적)
            length_score = self._calculate_length_score(len(content))

            # 키워드 밀도 점수
            keyword_density = self._calculate_keyword_density(content, category)

            # 가독성 점수
            readability = self._calculate_readability_score(content)

            # 최종 점수 계산
            final_score = (
                category_weights.get(category, 0.5) * 0.4 +  # 카테고리 중요도
                length_score * 0.2 +                          # 적절한 길이
                keyword_density * 0.2 +                       # 키워드 밀도
                readability * 0.2                             # 가독성
            )

            analysis[category] = {
                'importance_weight': category_weights.get(category, 0.5),
                'content_length': len(content),
                'quality_score': final_score,
                'keyword_density': keyword_density,
                'readability': readability,
                'final_score': final_score
            }

        return analysis

    def _select_best_content(self, category_analysis: Dict[str, Dict[str, Any]],
                           separated_duties: Dict[str, str]) -> str:
        """가장 적합한 내용을 선별"""
        # 점수가 높은 순으로 정렬
        sorted_categories = sorted(
            category_analysis.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )

        # 상위 2-3개 카테고리의 내용을 조합
        recommended_parts = []
        total_length = 0
        max_length = 300  # 최대 300자

        for category, analysis in sorted_categories:
            content = separated_duties.get(category, '')
            if content and analysis['final_score'] > 0.3:  # 임계값 이상만
                if total_length + len(content) <= max_length:
                    recommended_parts.append(content.strip())
                    total_length += len(content)
                else:
                    # 길이 제한으로 일부만 포함
                    remaining_length = max_length - total_length
                    if remaining_length > 50:  # 최소 50자는 되어야 의미있음
                        truncated = content[:remaining_length-3].strip() + '...'
                        recommended_parts.append(truncated)
                    break

        return ' '.join(recommended_parts) if recommended_parts else separated_duties.get('core_responsibilities', '')

    def _determine_priority_order(self, category_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """카테고리 우선순위 결정"""
        return sorted(
            category_analysis.keys(),
            key=lambda x: category_analysis[x]['final_score'],
            reverse=True
        )

    def _calculate_quality_score(self, category_analysis: Dict[str, Dict[str, Any]],
                               original_text: str) -> float:
        """전체 품질 점수 계산"""
        if not category_analysis:
            return 0.0

        # 카테고리별 점수의 가중 평균
        total_score = 0
        total_weight = 0

        for category, analysis in category_analysis.items():
            if analysis['final_score'] > 0:
                total_score += analysis['final_score'] * analysis['importance_weight']
                total_weight += analysis['importance_weight']

        if total_weight == 0:
            return 0.0

        base_score = total_score / total_weight

        # 원본 텍스트 길이에 따른 보정
        length_bonus = min(len(original_text) / 500, 1.0) * 0.1  # 최대 10% 보너스

        return min(base_score + length_bonus, 1.0)

    def _calculate_length_score(self, length: int) -> float:
        """적절한 길이 점수 계산 (50-200자가 최적)"""
        if length < 20:
            return 0.2
        elif length < 50:
            return 0.6
        elif length <= 200:
            return 1.0
        elif length <= 300:
            return 0.8
        else:
            return 0.5

    def _calculate_keyword_density(self, content: str, category: str) -> float:
        """키워드 밀도 점수 계산"""
        if not content:
            return 0.0

        category_config = self.patterns.get(category, {})
        keywords = category_config.get('keywords', [])

        if not keywords:
            return 0.5

        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)

        return min(keyword_matches / len(keywords), 1.0)

    def _calculate_readability_score(self, content: str) -> float:
        """가독성 점수 계산"""
        if not content:
            return 0.0

        # 문장 길이, 단어 복잡도 등을 고려한 간단한 가독성 점수
        sentences = content.count('.') + content.count('!') + content.count('?') + 1
        avg_sentence_length = len(content) / sentences

        # 적절한 문장 길이 (20-80자)
        if 20 <= avg_sentence_length <= 80:
            length_score = 1.0
        else:
            length_score = max(0.3, 1.0 - abs(avg_sentence_length - 50) / 100)

        return length_score

    def _generate_display_suggestions(self, category_analysis: Dict[str, Dict[str, Any]],
                                    separated_duties: Dict[str, str]) -> Dict[str, Any]:
        """UI 표시 제안 생성"""
        suggestions = {
            'primary_display': [],      # 기본 표시할 내용
            'secondary_display': [],    # 접을 수 있는 내용
            'hidden_content': [],       # 숨길 내용
            'display_order': []         # 표시 순서
        }

        sorted_categories = sorted(
            category_analysis.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )

        for i, (category, analysis) in enumerate(sorted_categories):
            content = separated_duties.get(category, '')
            if not content:
                continue

            category_info = {
                'category': category,
                'content': content,
                'score': analysis['final_score'],
                'length': analysis['content_length']
            }

            if analysis['final_score'] >= 0.7:
                suggestions['primary_display'].append(category_info)
            elif analysis['final_score'] >= 0.4:
                suggestions['secondary_display'].append(category_info)
            else:
                suggestions['hidden_content'].append(category_info)

            suggestions['display_order'].append(category)

        return suggestions

    def _empty_smart_result(self) -> Dict[str, Any]:
        """빈 스마트 결과 반환"""
        return {
            'separated_duties': self._empty_result(),
            'smart_extraction': {
                'recommended_content': '',
                'priority_order': [],
                'category_analysis': {},
                'quality_score': 0.0,
                'display_suggestions': {
                    'primary_display': [],
                    'secondary_display': [],
                    'hidden_content': [],
                    'display_order': []
                }
            },
            'original_text': '',
            'processing_info': {
                'total_length': 0,
                'categories_found': 0,
                'extraction_quality': 0.0,
                'recommended_display': '',
                'processing_time': datetime.now().isoformat()
            }
        }

    def _fallback_smart_separation(self, main_duties: str) -> Dict[str, Any]:
        """스마트 분리 실패 시 폴백"""
        return {
            'separated_duties': self._fallback_separation(main_duties),
            'smart_extraction': {
                'recommended_content': main_duties[:200] + '...' if len(main_duties) > 200 else main_duties,
                'priority_order': ['core_responsibilities'],
                'category_analysis': {},
                'quality_score': 0.5,
                'display_suggestions': {
                    'primary_display': [{
                        'category': 'core_responsibilities',
                        'content': main_duties,
                        'score': 0.5,
                        'length': len(main_duties)
                    }],
                    'secondary_display': [],
                    'hidden_content': [],
                    'display_order': ['core_responsibilities']
                }
            },
            'original_text': main_duties,
            'processing_info': {
                'total_length': len(main_duties),
                'categories_found': 1,
                'extraction_quality': 0.5,
                'recommended_display': main_duties[:200] + '...' if len(main_duties) > 200 else main_duties,
                'processing_time': datetime.now().isoformat()
            }
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분리"""
        # 줄바꿈, 마침표, 쉼표 등을 기준으로 분리
        sentences = []

        # 먼저 줄바꿈으로 분리
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 마침표나 특수문자로 분리
            parts = re.split(r'[.。]|(?<=[가-힣])\s*[-·•]\s*', line)

            for part in parts:
                part = part.strip()
                if len(part) > 3:  # 너무 짧은 문장은 제외
                    sentences.append(part)

        return sentences

    def _categorize_sentences(self, sentences: List[str]) -> Dict[str, List[str]]:
        """문장들을 카테고리별로 분류"""
        categorized = {
            'core_responsibilities': [],
            'daily_tasks': [],
            'project_tasks': [],
            'collaboration_tasks': [],
            'technical_tasks': [],
            'management_tasks': []
        }

        for sentence in sentences:
            # 각 카테고리별 점수 계산
            scores = {}

            for category, config in self.patterns.items():
                score = 0

                # 키워드 매칭 점수
                for keyword in config['keywords']:
                    if keyword in sentence:
                        score += 1

                # 패턴 매칭 점수 (가중치 2배)
                for pattern in config['patterns']:
                    if re.search(pattern, sentence):
                        score += 2

                scores[category] = score

            # 가장 높은 점수의 카테고리에 분류
            if max(scores.values()) > 0:
                best_category = max(scores, key=scores.get)
                categorized[best_category].append(sentence)
            else:
                # 분류되지 않은 경우 핵심업무에 포함
                categorized['core_responsibilities'].append(sentence)

        return categorized

    def _combine_sentences_by_category(self, categorized: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
        """카테고리별 문장들을 하나의 텍스트로 조합"""
        result = {}

        for category, sentences in categorized.items():
            if sentences:
                # 문장들을 자연스럽게 연결
                combined = self._join_sentences_naturally(sentences)
                result[category] = combined
            else:
                result[category] = None

        return result

    def _join_sentences_naturally(self, sentences: List[str]) -> str:
        """문장들을 자연스럽게 연결"""
        if not sentences:
            return ""

        # 중복 제거
        unique_sentences = []
        for sentence in sentences:
            if sentence not in unique_sentences:
                unique_sentences.append(sentence)

        # 마침표 추가 및 연결
        formatted_sentences = []
        for sentence in unique_sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith(('.', '다', '함', '음')):
                sentence += '.'
            formatted_sentences.append(sentence)

        return ' '.join(formatted_sentences)

    def _clean_result(self, result: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """결과 정리 및 빈 값 제거"""
        cleaned = {}

        for key, value in result.items():
            if value and value.strip():
                # 너무 짧은 내용은 제외 (3글자 미만)
                if len(value.strip()) >= 3:
                    cleaned[key] = value.strip()
                else:
                    cleaned[key] = None
            else:
                cleaned[key] = None

        return cleaned

    def _empty_result(self) -> Dict[str, Optional[str]]:
        """빈 결과 반환"""
        return {
            'core_responsibilities': None,
            'daily_tasks': None,
            'project_tasks': None,
            'collaboration_tasks': None,
            'technical_tasks': None,
            'management_tasks': None
        }

    def _fallback_separation(self, main_duties: str) -> Dict[str, Optional[str]]:
        """분리 실패 시 폴백 로직"""
        logger.warning("주요업무 분리 실패, 폴백 로직 사용")

        # 전체 내용을 핵심업무에만 할당
        return {
            'core_responsibilities': main_duties.strip() if main_duties else None,
            'daily_tasks': None,
            'project_tasks': None,
            'collaboration_tasks': None,
            'technical_tasks': None,
            'management_tasks': None
        }

    def get_separation_summary(self, separated_duties: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """분리 결과 요약 정보 제공"""
        summary = {
            'total_categories': len([v for v in separated_duties.values() if v]),
            'categories_with_content': [],
            'total_characters': 0,
            'separation_quality': 'good'
        }

        for category, content in separated_duties.items():
            if content:
                summary['categories_with_content'].append({
                    'category': category,
                    'character_count': len(content),
                    'word_count': len(content.split())
                })
                summary['total_characters'] += len(content)

        # 분리 품질 평가
        if summary['total_categories'] >= 4:
            summary['separation_quality'] = 'excellent'
        elif summary['total_categories'] >= 2:
            summary['separation_quality'] = 'good'
        else:
            summary['separation_quality'] = 'basic'

        return summary
