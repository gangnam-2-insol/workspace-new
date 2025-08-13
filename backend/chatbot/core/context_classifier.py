import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContextScore:
    """맥락 점수 결과"""
    total_score: float
    category_scores: Dict[str, float]
    confidence: float
    is_recruitment: bool
    details: Dict[str, Any]

class FlexibleContextClassifier:
    """유연한 맥락 분류기 - 의미적 유사성과 문맥 분석 기반"""
    
    def __init__(self):
        # 핵심 개념 그룹 (의미적 유사성 기반)
        self.concept_groups = {
            "recruitment_intent": {
                "primary": ["지원", "모집", "채용", "구인", "환영", "참여", "공고", "뽑다", "선발", "찾고", "모집합니다", "찾고 있습니다"],
                "secondary": ["구하다", "찾다", "모시다", "초대", "제안", "권유", "전문가를", "담당자를", "개발자를", "디자이너를", "마케터를", "기획자를", "운영자를", "분석가를", "보안을", "영업을", "인사를", "품질을"],
                "weight": 3.0
            },
            "application_process": {
                "primary": ["이력서", "자기소개서", "포트폴리오", "제출", "서류", "면접", "접수", "지원서"],
                "secondary": ["제출하다", "접수하다", "보내다", "올리다", "첨부", "첨부파일", "필수", "필수 조건", "우대", "경험이 있으시면", "능력이 필요", "자격증", "보유자"],
                "weight": 2.0
            },
            "qualification_requirements": {
                "primary": ["경험", "자격증", "학위", "경력", "신입", "능력", "기술", "역량"],
                "secondary": ["필요하다", "요구하다", "가져야", "갖춰야", "중요하다"],
                "weight": 1.0
            },
            "work_conditions": {
                "primary": ["연봉", "월급", "시급", "급여", "근무지", "복리후생", "재택", "출근"],
                "secondary": ["지급", "제공", "지원", "환경", "조건", "혜택"],
                "weight": 1.0
            },
            "attitude_qualities": {
                "primary": ["책임감", "성실", "배우려는", "긍정적", "적극적", "열정", "도전"],
                "secondary": ["마인드", "자세", "태도", "정신", "의지", "열의"],
                "weight": 1.0
            },
            "computer_skills": {
                "primary": ["컴퓨터", "PC", "프로그램", "소프트웨어", "기술", "스킬"],
                "secondary": ["활용", "사용", "조작", "다룰", "할 수", "능숙"],
                "weight": 1.0
            }
        }
        
        # 문맥 강화 패턴
        self.context_patterns = {
            "recruitment_structure": [
                r"([가-힣]+)\s*(지원자|모집|채용|구인)",
                r"([가-힣]+)\s*(환영합니다|모십니다|찾고 있습니다)",
                r"([가-힣]+)\s*(전문가|담당자)\s*(을|를)\s*(찾고|모집)",
                r"(제출\s*서류|지원\s*방법|접수\s*기간)",
                r"(연봉|급여|근무조건)\s*(은|는)\s*([가-힣]+)",
                r"(근무지|근무장소)\s*(은|는)\s*([가-힣]+)"
            ],
            "qualification_structure": [
                r"([가-힣]+)\s*(능력|기술|경험|자격)\s*(을|를)\s*([가-힣]+)",
                r"([가-힣]+)\s*(필요|요구|중요|우대)",
                r"([가-힣]+)\s*(경험이|능력이)\s*(필요|우대)",
                r"(신입|경력)\s*(지원자|사원|직원)",
                r"([가-힣]+)\s*(등|및)\s*([가-힣]+)\s*(활용|사용)\s*(경험이|능력이)"
            ]
        }
        
        # 문장 길이 및 복잡성 가중치
        self.complexity_weights = {
            "length_threshold": 50,  # 50자 이상
            "sentence_count_threshold": 2,  # 2문장 이상
            "detail_bonus": 0.5  # 상세한 내용 보너스
        }
    
    def calculate_semantic_similarity(self, text: str, concept_group: Dict) -> float:
        """의미적 유사성 계산"""
        text_lower = text.lower()
        score = 0.0
        
        # 1차 키워드 매칭 (높은 가중치)
        for keyword in concept_group["primary"]:
            if keyword in text_lower:
                score += 1.0
                # 연속된 키워드 보너스
                if len([k for k in concept_group["primary"] if k in text_lower]) > 1:
                    score += 0.3
        
        # 2차 키워드 매칭 (낮은 가중치)
        for keyword in concept_group["secondary"]:
            if keyword in text_lower:
                score += 0.5
        
        # 문맥 패턴 매칭
        context_bonus = self._check_context_patterns(text, concept_group)
        score += context_bonus
        
        return score * concept_group["weight"]
    
    def _check_context_patterns(self, text: str, concept_group: Dict) -> float:
        """문맥 패턴 확인"""
        bonus = 0.0
        
        # 채용 의도 관련 패턴
        if "recruitment_intent" in str(concept_group):
            for pattern in self.context_patterns["recruitment_structure"]:
                if re.search(pattern, text):
                    bonus += 0.5
        
        # 자격 요건 관련 패턴
        if "qualification_requirements" in str(concept_group):
            for pattern in self.context_patterns["qualification_structure"]:
                if re.search(pattern, text):
                    bonus += 0.3
        
        return bonus
    
    def calculate_complexity_bonus(self, text: str) -> float:
        """문장 복잡성 보너스 계산"""
        bonus = 0.0
        
        # 길이 보너스
        if len(text) >= self.complexity_weights["length_threshold"]:
            bonus += self.complexity_weights["detail_bonus"]
        
        # 문장 수 보너스
        sentence_count = len(re.split(r'[.!?]+', text))
        if sentence_count >= self.complexity_weights["sentence_count_threshold"]:
            bonus += 0.3
        
        # 상세한 설명 보너스
        detail_indicators = ["구체적으로", "상세히", "자세히", "예를 들어", "특히", "또한", "그리고"]
        detail_count = sum(1 for indicator in detail_indicators if indicator in text)
        bonus += detail_count * 0.2
        
        return bonus
    
    def classify_context(self, text: str) -> ContextScore:
        """맥락 분류 (외부 인터페이스용)"""
        return self.analyze_recruitment_context(text)
    
    def analyze_recruitment_context(self, text: str) -> ContextScore:
        """채용 맥락 분석"""
        logger.info(f"🔍 맥락 분석 시작: {text[:50]}...")
        
        category_scores = {}
        total_score = 0.0
        
        # 각 개념 그룹별 점수 계산
        for category, group in self.concept_groups.items():
            score = self.calculate_semantic_similarity(text, group)
            category_scores[category] = score
            total_score += score
            logger.info(f"📊 {category}: {score:.2f}점")
        
        # 복잡성 보너스
        complexity_bonus = self.calculate_complexity_bonus(text)
        total_score += complexity_bonus
        category_scores["complexity_bonus"] = complexity_bonus
        
        # 조합 가중치 적용
        combination_bonus = self._calculate_combination_bonus(category_scores)
        total_score += combination_bonus
        category_scores["combination_bonus"] = combination_bonus
        
        # 최종 점수 조정
        final_score = self._adjust_final_score(total_score, category_scores)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(category_scores, text)
        
        # 채용 여부 판정
        is_recruitment = final_score >= 5.0
        
        # 상세 정보
        details = {
            "text_length": len(text),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "key_indicators": self._extract_key_indicators(text),
            "score_breakdown": category_scores.copy()
        }
        
        result = ContextScore(
            total_score=final_score,
            category_scores=category_scores,
            confidence=confidence,
            is_recruitment=is_recruitment,
            details=details
        )
        
        logger.info(f"🎯 최종 결과: {final_score:.2f}점 (채용: {is_recruitment}, 신뢰도: {confidence:.2f})")
        
        return result
    
    def _calculate_combination_bonus(self, category_scores: Dict[str, float]) -> float:
        """조합 가중치 계산"""
        bonus = 0.0
        
        # 지원 의도 + 제출 절차 조합 (강한 채용 신호)
        if (category_scores.get("recruitment_intent", 0) > 0 and 
            category_scores.get("application_process", 0) > 0):
            bonus += 2.0
        
        # 지원 의도 + 자격 요건 조합
        if (category_scores.get("recruitment_intent", 0) > 0 and 
            category_scores.get("qualification_requirements", 0) > 0):
            bonus += 1.0
        
        # 지원 의도 + 근무 조건 조합
        if (category_scores.get("recruitment_intent", 0) > 0 and 
            category_scores.get("work_conditions", 0) > 0):
            bonus += 1.0
        
        # 지원 의도가 없으면 페널티
        if category_scores.get("recruitment_intent", 0) == 0:
            bonus -= 2.0
        
        return bonus
    
    def _adjust_final_score(self, total_score: float, category_scores: Dict[str, float]) -> float:
        """최종 점수 조정"""
        adjusted_score = total_score
        
        # 너무 짧은 문장 페널티
        if total_score < 3.0 and category_scores.get("complexity_bonus", 0) < 0.5:
            adjusted_score *= 0.8
        
        # 너무 높은 점수 정규화
        if adjusted_score > 15.0:
            adjusted_score = 15.0
        
        return adjusted_score
    
    def _calculate_confidence(self, category_scores: Dict[str, float], text: str) -> float:
        """신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도
        
        # 점수 기반 신뢰도
        total_score = sum(category_scores.values())
        if total_score >= 8.0:
            confidence += 0.3
        elif total_score >= 5.0:
            confidence += 0.2
        elif total_score >= 3.0:
            confidence += 0.1
        
        # 문장 길이 기반 신뢰도
        if len(text) >= 100:
            confidence += 0.1
        elif len(text) >= 50:
            confidence += 0.05
        
        # 키워드 다양성 기반 신뢰도
        non_zero_categories = sum(1 for score in category_scores.values() if score > 0)
        if non_zero_categories >= 3:
            confidence += 0.1
        elif non_zero_categories >= 2:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _extract_key_indicators(self, text: str) -> List[str]:
        """주요 지표 추출"""
        indicators = []
        
        for category, group in self.concept_groups.items():
            for keyword in group["primary"]:
                if keyword in text.lower():
                    indicators.append(f"{category}: {keyword}")
        
        return indicators[:5]  # 상위 5개만 반환

# 전역 인스턴스
context_classifier = FlexibleContextClassifier()

def classify_context(text: str) -> ContextScore:
    """맥락 분류 함수 (외부 인터페이스)"""
    return context_classifier.analyze_recruitment_context(text)

def is_recruitment_text(text: str, threshold: float = 5.0) -> Tuple[bool, float, Dict[str, Any]]:
    """채용 텍스트 여부 판별 (간단한 인터페이스)"""
    result = classify_context(text)
    return result.is_recruitment, result.total_score, result.details
