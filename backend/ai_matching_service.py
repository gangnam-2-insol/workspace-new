"""
AI 기반 인재 매칭 서비스
Google의 ko-sroberta-multitask 모델을 사용한 의미적 유사도 계산
"""

# HuggingFace 모델 임시 비활성화
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AIMatchingService:
    """AI 기반 인재 매칭 서비스"""
    
    def __init__(self):
        """모델 초기화 (HuggingFace 모델 임시 비활성화)"""
        # HuggingFace 모델 임시 비활성화 - 빌드 시간 단축을 위해
        self.model = None
        logger.info("📝 HuggingFace 모델 비활성화 (기존 키워드 매칭 사용)")
        # try:
        #     # 한국어 특화 SentenceTransformer 모델 로드
        #     self.model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        #     logger.info("✅ ko-sroberta-multitask 모델 로드 완료")
        # except Exception as e:
        #     logger.error(f"❌ 모델 로드 실패: {e}")
        #     self.model = None
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간의 의미적 유사도를 계산합니다."""
        if not self.model:
            logger.warning("모델이 로드되지 않아 기본값 반환")
            return 0.5
        
        try:
            # 텍스트 임베딩 생성
            embeddings = self.model.encode([text1, text2])
            
            # 코사인 유사도 계산
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # 0-1 범위로 정규화
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"유사도 계산 오류: {e}")
            return 0.5
    
    def analyze_requirements_with_ai(self, requirements_text: str) -> Dict[str, Any]:
        """AI를 사용하여 요구사항 텍스트를 더 정교하게 분석합니다."""
        
        # 기본 키워드 기반 분석 (기존 로직 유지)
        basic_analysis = self._basic_keyword_analysis(requirements_text)
        
        # AI 기반 추가 분석
        ai_analysis = self._ai_enhanced_analysis(requirements_text)
        
        # 결과 병합
        return {
            **basic_analysis,
            'ai_embedding': ai_analysis.get('embedding'),
            'semantic_keywords': ai_analysis.get('semantic_keywords', [])
        }
    
    def _basic_keyword_analysis(self, requirements_text: str) -> Dict[str, Any]:
        """기존 키워드 기반 분석 (백업용)"""
        
        # 직무 키워드
        position_keywords = {
            '개발자': ['개발자', '프로그래머', '엔지니어', '개발', '프로그래밍'],
            '디자이너': ['디자이너', '디자인', 'UI', 'UX', '인터페이스'],
            '매니저': ['매니저', '관리자', '팀장', '리더', '관리'],
            '분석가': ['분석가', '분석', '데이터', '통계', '인사이트'],
            '마케터': ['마케터', '마케팅', '홍보', '브랜딩', '광고']
        }
        
        # 기술 키워드
        tech_keywords = ['React', 'Vue', 'Angular', 'JavaScript', 'TypeScript', 'Python', 'Java', 
                        'Node.js', 'Spring', 'Django', 'MySQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes']
        
        # 성격/능력 키워드
        ability_keywords = ['창의적', '분석적', '협업', '리더십', '커뮤니케이션', '문제해결', 
                           '적극적', '주도적', '꼼꼼', '유연']
        
        text_lower = requirements_text.lower()
        
        # 추출된 키워드들
        extracted_position = None
        for pos, keywords in position_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                extracted_position = pos
                break
        
        extracted_skills = []
        for skill in tech_keywords:
            if skill.lower() in text_lower:
                extracted_skills.append(skill)
        
        extracted_abilities = []
        for ability in ability_keywords:
            if ability in text_lower:
                extracted_abilities.append(ability)
        
        return {
            'position': extracted_position,
            'skills': extracted_skills,
            'abilities': extracted_abilities,
            'original_text': requirements_text
        }
    
    def _ai_enhanced_analysis(self, requirements_text: str) -> Dict[str, Any]:
        """AI 기반 향상된 분석"""
        if not self.model:
            return {'embedding': None, 'semantic_keywords': []}
        
        try:
            # 텍스트 임베딩 생성
            embedding = self.model.encode(requirements_text)
            
            # 의미적 키워드 추출 (향후 확장 가능)
            semantic_keywords = self._extract_semantic_keywords(requirements_text)
            
            return {
                'embedding': embedding.tolist(),  # JSON 직렬화 가능하도록 변환
                'semantic_keywords': semantic_keywords
            }
        except Exception as e:
            logger.error(f"AI 분석 오류: {e}")
            return {'embedding': None, 'semantic_keywords': []}
    
    def _extract_semantic_keywords(self, text: str) -> List[str]:
        """의미적 키워드 추출 (간단한 버전)"""
        # 향후 더 정교한 NER이나 키워드 추출 모델로 확장 가능
        keywords = []
        
        # 현재는 단순 토큰화 + 필터링
        words = re.findall(r'\b[가-힣a-zA-Z]{2,}\b', text)
        
        # 의미있는 키워드만 필터링
        meaningful_words = [word for word in words if len(word) >= 2]
        
        return meaningful_words[:10]  # 상위 10개만 반환
    
    def calculate_ai_talent_match_score(self, talent: Dict[str, Any], requirements: Dict[str, Any]) -> int:
        """AI 기반 인재 매칭 점수 계산"""
        
        if not self.model:
            # AI 모델이 없으면 기존 로직 사용
            return self._fallback_match_score(talent, requirements)
        
        try:
            # 1. 텍스트 기반 의미적 유사도 (40점)
            semantic_score = self._calculate_semantic_score(talent, requirements)
            
            # 2. 기술 스택 매칭 (30점) 
            skills_score = self._calculate_skills_score(talent, requirements)
            
            # 3. 직무 매칭 (20점)
            position_score = self._calculate_position_score(talent, requirements)
            
            # 4. 경력 점수 (10점)
            experience_score = self._calculate_experience_score(talent)
            
            # 총점 계산
            total_score = semantic_score + skills_score + position_score + experience_score
            
            # 0-100 범위로 정규화
            final_score = max(60, min(100, int(total_score)))
            
            logger.info(f"매칭 점수 계산: 의미적={semantic_score:.1f}, 기술={skills_score:.1f}, "
                       f"직무={position_score:.1f}, 경력={experience_score:.1f}, 총점={final_score}")
            
            return final_score
            
        except Exception as e:
            logger.error(f"AI 매칭 점수 계산 오류: {e}")
            return self._fallback_match_score(talent, requirements)
    
    def _calculate_semantic_score(self, talent: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """의미적 유사도 점수 계산 (40점 만점)"""
        
        talent_text = talent.get('profileText', '')
        requirements_text = requirements.get('original_text', '')
        
        if not talent_text or not requirements_text:
            return 20.0  # 기본 점수
        
        # 의미적 유사도 계산
        similarity = self.calculate_semantic_similarity(talent_text, requirements_text)
        
        # 0-40점으로 변환
        return similarity * 40.0
    
    def _calculate_skills_score(self, talent: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """기술 스택 매칭 점수 (30점 만점)"""
        
        talent_skills = [skill.lower() for skill in talent.get('skills', [])]
        req_skills = [skill.lower() for skill in requirements.get('skills', [])]
        
        if not req_skills:
            return 20.0  # 요구사항이 없으면 기본 점수
        
        # 정확한 매칭
        exact_matches = sum(1 for skill in req_skills if skill in talent_skills)
        
        # 부분 매칭 (AI 모델로 유사한 기술 찾기)
        partial_matches = 0
        for req_skill in req_skills:
            if req_skill not in talent_skills:
                for talent_skill in talent_skills:
                    similarity = self.calculate_semantic_similarity(req_skill, talent_skill)
                    if similarity > 0.7:  # 70% 이상 유사하면 부분 매칭
                        partial_matches += 0.5
                        break
        
        total_matches = exact_matches + partial_matches
        match_ratio = min(total_matches / len(req_skills), 1.0)
        
        return match_ratio * 30.0
    
    def _calculate_position_score(self, talent: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """직무 매칭 점수 (20점 만점)"""
        
        talent_position = talent.get('position', '').lower()
        req_position = requirements.get('position', '')
        
        if not req_position or not talent_position:
            return 10.0  # 기본 점수
        
        req_position_lower = req_position.lower()
        
        # 정확한 매칭
        if req_position_lower in talent_position or talent_position in req_position_lower:
            return 20.0
        
        # 의미적 유사도 기반 매칭
        similarity = self.calculate_semantic_similarity(talent_position, req_position_lower)
        return similarity * 20.0
    
    def _calculate_experience_score(self, talent: Dict[str, Any]) -> float:
        """경력 점수 (10점 만점)"""
        
        talent_exp = talent.get('experience', '0')
        exp_numbers = re.findall(r'\d+', talent_exp)
        
        if exp_numbers:
            exp_years = int(exp_numbers[0])
            return min(exp_years * 2, 10.0)
        
        return 5.0  # 기본 점수
    
    def _fallback_match_score(self, talent: Dict[str, Any], requirements: Dict[str, Any]) -> int:
        """AI 모델이 없을 때 사용하는 기본 매칭 로직"""
        base_score = 60
        
        # 기존 로직과 동일
        position_score = 0
        if requirements.get('position'):
            talent_position = talent.get('position', '').lower()
            req_position = requirements['position'].lower()
            if req_position in talent_position or talent_position in req_position:
                position_score = 30
            elif any(word in talent_position for word in req_position.split()):
                position_score = 20
        
        skills_score = 0
        talent_skills = [skill.lower() for skill in talent.get('skills', [])]
        req_skills = [skill.lower() for skill in requirements.get('skills', [])]
        if req_skills:
            matched_skills = sum(1 for skill in req_skills if any(skill in ts for ts in talent_skills))
            skills_score = min((matched_skills / len(req_skills)) * 25, 25)
        
        experience_score = 0
        talent_exp = talent.get('experience', '0')
        exp_numbers = re.findall(r'\d+', talent_exp)
        if exp_numbers:
            exp_years = int(exp_numbers[0])
            experience_score = min(exp_years * 2, 10)
        
        final_score = base_score + position_score + skills_score + experience_score
        return min(max(final_score, 60), 100)

# 전역 인스턴스
ai_matching_service = AIMatchingService()