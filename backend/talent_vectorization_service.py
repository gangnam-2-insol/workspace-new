from typing import List, Dict, Any, Optional
from embedding_service import EmbeddingService
from vector_service import VectorService
from openai_service import OpenAIService
import json
from datetime import datetime

class TalentVectorizationService:
    def __init__(self, embedding_service: EmbeddingService, vector_service: VectorService, openai_service: OpenAIService = None):
        """
        인재추천용 벡터화 서비스 초기화
        
        Args:
            embedding_service (EmbeddingService): 임베딩 서비스
            vector_service (VectorService): 벡터 서비스
            openai_service (OpenAIService): OpenAI 서비스 (선택사항)
        """
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.openai_service = openai_service
        print("[TalentVectorizationService] 인재추천용 벡터화 서비스 초기화 완료")
        if openai_service:
            print("[TalentVectorizationService] LLM 기반 추천 이유 생성 활성화")
    
    async def vectorize_applicant_profile(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        지원자 프로필을 통합 벡터로 변환합니다.
        
        Args:
            applicant (Dict[str, Any]): 지원자 데이터
            
        Returns:
            Dict[str, Any]: 벡터화된 프로필
        """
        try:
            applicant_id = str(applicant.get("_id", ""))
            print(f"[TalentVectorizationService] === 지원자 프로필 벡터화 시작 ===")
            print(f"[TalentVectorizationService] 지원자 ID: {applicant_id}")
            print(f"[TalentVectorizationService] 지원자 이름: {applicant.get('name', 'Unknown')}")
            
            # 1. 통합 프로필 텍스트 생성
            profile_text = self._create_integrated_profile_text(applicant)
            print(f"[TalentVectorizationService] 통합 프로필 텍스트 길이: {len(profile_text)}")
            
            # 2. 구조화된 메타데이터 생성
            metadata = self._create_profile_metadata(applicant)
            
            # 3. 임베딩 생성
            embedding = await self.embedding_service.create_embedding(profile_text)
            if not embedding:
                print(f"[TalentVectorizationService] 임베딩 생성 실패: {applicant_id}")
                return None
            
            # 4. 벡터 데이터 구성
            vector_data = {
                "applicant_id": applicant_id,
                "vector": embedding,
                "metadata": metadata,
                "profile_text": profile_text,
                "created_at": datetime.now().isoformat(),
                "vector_type": "talent_profile"
            }
            
            print(f"[TalentVectorizationService] 벡터화 완료: {applicant_id}")
            return vector_data
            
        except Exception as e:
            print(f"[TalentVectorizationService] 벡터화 오류: {str(e)}")
            return None
    
    def _create_integrated_profile_text(self, applicant: Dict[str, Any]) -> str:
        """
        지원자의 모든 정보를 통합한 프로필 텍스트를 생성합니다.
        
        Args:
            applicant (Dict[str, Any]): 지원자 데이터
            
        Returns:
            str: 통합 프로필 텍스트
        """
        profile_parts = []
        
        # 기본 정보
        name = applicant.get("name", "")
        position = applicant.get("position", "")
        department = applicant.get("department", "")
        experience = applicant.get("experience", "")
        
        if name:
            profile_parts.append(f"이름: {name}")
        if position:
            profile_parts.append(f"희망직무: {position}")
        if department:
            profile_parts.append(f"희망부서: {department}")
        if experience:
            profile_parts.append(f"경력: {experience}")
        
        # 기술스택
        skills = applicant.get("skills", "")
        if skills:
            profile_parts.append(f"보유기술: {skills}")
        
        # 성장배경
        growth_background = applicant.get("growthBackground", "")
        if growth_background and len(growth_background.strip()) > 10:
            profile_parts.append(f"성장배경: {growth_background}")
        
        # 지원동기
        motivation = applicant.get("motivation", "")
        if motivation and len(motivation.strip()) > 10:
            profile_parts.append(f"지원동기: {motivation}")
        
        # 경력사항
        career_history = applicant.get("careerHistory", "")
        if career_history and len(career_history.strip()) > 10:
            profile_parts.append(f"경력사항: {career_history}")
        
        # 분석 결과 (있는 경우)
        analysis_result = applicant.get("analysisResult", "")
        if analysis_result and len(analysis_result.strip()) > 10:
            profile_parts.append(f"분석결과: {analysis_result}")
        
        return " ".join(profile_parts)
    
    def _create_profile_metadata(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        검색 및 필터링을 위한 구조화된 메타데이터를 생성합니다.
        
        Args:
            applicant (Dict[str, Any]): 지원자 데이터
            
        Returns:
            Dict[str, Any]: 메타데이터
        """
        metadata = {
            "name": applicant.get("name", ""),
            "position": applicant.get("position", ""),
            "department": applicant.get("department", ""),
            "experience": applicant.get("experience", ""),
            "status": applicant.get("status", ""),
            "analysis_score": applicant.get("analysisScore", 0),
            "created_at": applicant.get("created_at", "")
        }
        
        # 기술스택 파싱 (쉼표로 분리)
        skills = applicant.get("skills", "")
        if skills:
            skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
            metadata["skills"] = skills_list
            metadata["skills_count"] = len(skills_list)
        else:
            metadata["skills"] = []
            metadata["skills_count"] = 0
        
        # 경력 레벨 분류
        experience = applicant.get("experience", "").lower()
        if "신입" in experience or "0년" in experience:
            metadata["experience_level"] = "junior"
        elif "1년" in experience or "2년" in experience or "3년" in experience:
            metadata["experience_level"] = "mid"
        else:
            metadata["experience_level"] = "senior"
        
        # 텍스트 길이 정보
        growth_len = len(applicant.get("growthBackground", ""))
        motivation_len = len(applicant.get("motivation", ""))
        career_len = len(applicant.get("careerHistory", ""))
        
        metadata["text_completeness"] = {
            "growth_background": growth_len,
            "motivation": motivation_len,
            "career_history": career_len,
            "total": growth_len + motivation_len + career_len
        }
        
        return metadata
    
    async def store_applicant_vector(self, vector_data: Dict[str, Any]) -> bool:
        """
        지원자 벡터를 저장합니다.
        
        Args:
            vector_data (Dict[str, Any]): 벡터 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # VectorService의 save_vector 메서드 사용
            metadata = vector_data["metadata"].copy()
            metadata["chunk_type"] = "talent_profile"  # VectorService가 필터링에 사용하는 필드
            metadata["vector_type"] = "talent_profile"  # 추가 정보용
            metadata["profile_text"] = vector_data["profile_text"]
            metadata["created_at"] = vector_data["created_at"]
            
            result = await self.vector_service.save_vector(
                embedding=vector_data["vector"],
                metadata=metadata
            )
            
            if result:
                print(f"[TalentVectorizationService] 벡터 저장 완료: {vector_data['applicant_id']}")
                return True
            else:
                print(f"[TalentVectorizationService] 벡터 저장 실패: {vector_data['applicant_id']}")
                return False
                
        except Exception as e:
            print(f"[TalentVectorizationService] 벡터 저장 오류: {str(e)}")
            return False
    
    async def batch_vectorize_applicants(self, applicants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 지원자를 배치로 벡터화합니다.
        
        Args:
            applicants (List[Dict[str, Any]]): 지원자 리스트
            
        Returns:
            Dict[str, Any]: 배치 처리 결과
        """
        print(f"[TalentVectorizationService] === 배치 벡터화 시작 ===")
        print(f"[TalentVectorizationService] 처리할 지원자 수: {len(applicants)}")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for i, applicant in enumerate(applicants):
            try:
                print(f"[TalentVectorizationService] 진행률: {i+1}/{len(applicants)}")
                
                # 벡터화
                vector_data = await self.vectorize_applicant_profile(applicant)
                if not vector_data:
                    error_count += 1
                    errors.append(f"벡터화 실패: {applicant.get('name', 'Unknown')}")
                    continue
                
                # 저장
                stored = await self.store_applicant_vector(vector_data)
                if stored:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"저장 실패: {applicant.get('name', 'Unknown')}")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"처리 오류 {applicant.get('name', 'Unknown')}: {str(e)}")
        
        result = {
            "total": len(applicants),
            "success": success_count,
            "errors": error_count,
            "error_details": errors,
            "completed_at": datetime.now().isoformat()
        }
        
        print(f"[TalentVectorizationService] === 배치 벡터화 완료 ===")
        print(f"[TalentVectorizationService] 성공: {success_count}, 실패: {error_count}")
        
        return result
    
    async def recommend_similar_applicants(self, target_applicant: Dict[str, Any], limit: int = 5) -> Dict[str, Any]:
        """
        특정 지원자와 유사한 다른 지원자들을 추천합니다.
        
        Args:
            target_applicant (Dict[str, Any]): 기준이 되는 지원자
            limit (int): 추천할 지원자 수
            
        Returns:
            Dict[str, Any]: 추천 결과
        """
        try:
            target_id = str(target_applicant.get("_id", ""))
            target_name = target_applicant.get("name", "Unknown")
            
            print(f"[TalentVectorizationService] === 유사 지원자 추천 시작 ===")
            print(f"[TalentVectorizationService] 기준 지원자: {target_name} ({target_id})")
            
            # 1. 기준 지원자의 벡터 생성
            target_vector_data = await self.vectorize_applicant_profile(target_applicant)
            if not target_vector_data:
                print(f"[TalentVectorizationService] 기준 지원자 벡터화 실패")
                return {"success": False, "error": "기준 지원자 벡터화 실패"}
            
            target_embedding = target_vector_data["vector"]
            print(f"[TalentVectorizationService] 기준 지원자 벡터 생성 완료 (차원: {len(target_embedding)})")
            
            # 2. 유사한 벡터 검색 (자기 자신 제외)
            search_response = await self.vector_service.search_similar_vectors(
                query_embedding=target_embedding,
                top_k=limit + 5,  # 자기 자신과 중복 제거를 위해 더 많이 검색
                filter_type="talent_profile"  # 인재 프로필 벡터만 검색
            )
            
            search_results = search_response.get("matches", [])
            
            if not search_results:
                print(f"[TalentVectorizationService] 유사 벡터 검색 결과 없음")
                return {
                    "success": True,
                    "target_applicant": {
                        "id": target_id,
                        "name": target_name
                    },
                    "recommendations": [],
                    "message": "유사한 지원자를 찾을 수 없습니다."
                }
            
            print(f"[TalentVectorizationService] 벡터 검색 결과: {len(search_results)}개")
            
            # 3. 결과 필터링 및 가공
            recommendations = []
            for result in search_results:
                # 자기 자신 제외
                result_applicant_id = result.get("metadata", {}).get("name", "")
                if result_applicant_id == target_name:  # 이름으로 비교 (임시)
                    continue
                
                # 추천 항목 구성
                recommendation = {
                    "applicant_name": result.get("metadata", {}).get("name", "Unknown"),
                    "position": result.get("metadata", {}).get("position", ""),
                    "department": result.get("metadata", {}).get("department", ""),
                    "experience": result.get("metadata", {}).get("experience", ""),
                    "skills": result.get("metadata", {}).get("skills", []),
                    "similarity_score": round(result.get("score", 0), 4),
                    "analysis_score": result.get("metadata", {}).get("analysis_score", 0),
                    "experience_level": result.get("metadata", {}).get("experience_level", "unknown")
                }
                
                recommendations.append(recommendation)
                
                # 원하는 개수만큼 추천
                if len(recommendations) >= limit:
                    break
            
            # 4. 추천 이유 생성 (LLM 또는 규칙 기반)
            for i, rec in enumerate(recommendations):
                print(f"[TalentVectorizationService] 추천 {i+1}/{len(recommendations)} - {rec['applicant_name']} 추천 이유 생성 중")
                
                if self.openai_service:
                    print(f"[TalentVectorizationService] LLM 기반 추천 이유 생성 시도 - OpenAI 서비스 사용")
                    try:
                        rec["recommendation_reason"] = await self._generate_llm_recommendation_reason(
                            target_applicant, rec, rec["similarity_score"]
                        )
                        print(f"[TalentVectorizationService] LLM 추천 이유 생성 성공: '{rec['recommendation_reason']}'")
                    except Exception as e:
                        print(f"[TalentVectorizationService] LLM 추천 이유 생성 실패, 규칙 기반으로 대체: {e}")
                        rec["recommendation_reason"] = self._generate_simple_recommendation_reason(
                            target_applicant, rec
                        )
                        print(f"[TalentVectorizationService] 규칙 기반 추천 이유 적용: '{rec['recommendation_reason']}'")
                else:
                    print(f"[TalentVectorizationService] OpenAI 서비스 없음 - 규칙 기반 추천 이유 사용")
                    rec["recommendation_reason"] = self._generate_simple_recommendation_reason(
                        target_applicant, rec
                    )
                    print(f"[TalentVectorizationService] 규칙 기반 추천 이유: '{rec['recommendation_reason']}'")
                    
                print(f"[TalentVectorizationService] 추천 {i+1} 완료")
            
            result = {
                "success": True,
                "target_applicant": {
                    "id": target_id,
                    "name": target_name,
                    "position": target_applicant.get("position", ""),
                    "skills": target_applicant.get("skills", "").split(",") if target_applicant.get("skills") else []
                },
                "recommendations": recommendations,
                "total_found": len(recommendations),
                "search_timestamp": datetime.now().isoformat()
            }
            
            print(f"[TalentVectorizationService] 추천 완료: {len(recommendations)}명")
            print(f"[TalentVectorizationService] === 유사 지원자 추천 완료 ===")
            
            return result
            
        except Exception as e:
            print(f"[TalentVectorizationService] 추천 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "target_applicant": {
                    "id": target_applicant.get("_id", ""),
                    "name": target_applicant.get("name", "Unknown")
                },
                "recommendations": []
            }
    
    async def _generate_llm_recommendation_reason(self, target: Dict[str, Any], recommendation: Dict[str, Any], similarity_score: float) -> str:
        """
        LLM을 사용해 개인화된 추천 이유를 생성합니다.
        
        Args:
            target (Dict[str, Any]): 기준 지원자
            recommendation (Dict[str, Any]): 추천 지원자
            similarity_score (float): 유사도 점수
            
        Returns:
            str: LLM 생성 추천 이유
        """
        try:
            print(f"[TalentVectorizationService] LLM 추천 이유 생성 시작 - OpenAI 서비스 상태: {self.openai_service is not None}")
            
            # 기술스택 처리
            target_skills = target.get("skills", "")
            rec_skills = recommendation.get("skills", [])
            if isinstance(rec_skills, list):
                rec_skills_str = ", ".join(rec_skills)
            else:
                rec_skills_str = str(rec_skills)
            
            print(f"[TalentVectorizationService] 프롬프트 데이터 준비 완료")
            
            prompt = f"""다음 두 지원자가 왜 유사한지 분석하여 간결한 추천 이유를 생성해주세요.

기준 지원자:
- 이름: {target.get('name', '')}
- 직무: {target.get('position', '')}
- 경력: {target.get('experience', '')}
- 기술스택: {target_skills}

추천 지원자:
- 이름: {recommendation.get('applicant_name', '')}
- 직무: {recommendation.get('position', '')}
- 경력: {recommendation.get('experience', '')}
- 기술스택: {rec_skills_str}

유사도 점수: {similarity_score:.3f}

추천 이유를 25자 이내로 간결하게 작성해주세요. 구체적인 공통점을 중심으로 작성하되, 너무 상세하지 않게 해주세요.
예시: "React 기반 프론트엔드 경험 공통", "3년차 백엔드 개발자", "Java·Spring 공통 기술스택"
"""
            
            print(f"[TalentVectorizationService] OpenAI API 호출 시작...")
            response = await self.openai_service.generate_response(prompt)
            print(f"[TalentVectorizationService] OpenAI API 호출 완료 - 응답 길이: {len(response)}")
            
            # 응답 정제 (따옴표, 불필요한 문자 제거)
            reason = response.strip().strip('"\'').strip()
            
            # 길이 제한 (30자 초과시 자르기)
            if len(reason) > 30:
                reason = reason[:27] + "..."
            
            return reason if reason else "프로필 특성이 유사함"
            
        except Exception as e:
            print(f"[TalentVectorizationService] LLM 추천 이유 생성 오류: {e}")
            # 오류 시 규칙 기반으로 폴백
            return self._generate_simple_recommendation_reason(target, recommendation)
    
    def _generate_simple_recommendation_reason(self, target: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
        """
        간단한 추천 이유를 생성합니다.
        
        Args:
            target (Dict[str, Any]): 기준 지원자
            recommendation (Dict[str, Any]): 추천 지원자
            
        Returns:
            str: 추천 이유
        """
        reasons = []
        
        # 동일 직무
        if target.get("position") == recommendation.get("position"):
            reasons.append(f"동일한 {recommendation.get('position')} 직무")
        
        # 유사한 경력 레벨
        if target.get("experience") and recommendation.get("experience"):
            reasons.append("유사한 경력 수준")
        
        # 공통 기술스택
        target_skills = set(target.get("skills", "").split(",")) if target.get("skills") else set()
        rec_skills = set(recommendation.get("skills", []))
        common_skills = target_skills.intersection(rec_skills)
        if common_skills:
            skills_str = ", ".join(list(common_skills)[:3])  # 최대 3개만 표시
            reasons.append(f"공통 기술: {skills_str}")
        
        # 높은 유사도
        similarity = recommendation.get("similarity_score", 0)
        if similarity > 0.8:
            reasons.append("매우 높은 프로필 유사도")
        elif similarity > 0.6:
            reasons.append("높은 프로필 유사도")
        
        if not reasons:
            reasons.append("프로필 특성이 유사함")
        
        return " | ".join(reasons)