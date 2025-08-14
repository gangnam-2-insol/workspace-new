from typing import Dict, Any, Optional, List
import google.generativeai as genai
import os
from datetime import datetime

class LLMService:
    def __init__(self):
        """
        LLM 서비스 초기화
        """
        print(f"[LLMService] === LLM 서비스 초기화 시작 ===")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(f"[LLMService] 경고: GEMINI_API_KEY 환경변수가 설정되지 않았습니다!")
        else:
            print(f"[LLMService] GEMINI_API_KEY 확인됨 (길이: {len(api_key)})")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print(f"[LLMService] Gemini 모델 초기화 완료: gemini-1.5-flash")
        print(f"[LLMService] === LLM 서비스 초기화 완료 ===")
        
    async def analyze_similarity_reasoning(self, 
                                         original_resume: Dict[str, Any], 
                                         similar_resume: Dict[str, Any],
                                         similarity_score: float,
                                         chunk_details: Optional[Dict] = None) -> Dict[str, Any]:
        """
        두 이력서 간의 유사성을 분석하고 어떤 부분이 유사한지 설명합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 이력서
            similar_resume (Dict[str, Any]): 유사한 이력서
            similarity_score (float): 유사도 점수
            chunk_details (Optional[Dict]): 청크별 세부 정보
            
        Returns:
            Dict[str, Any]: 유사성 분석 결과
        """
        try:
            print(f"[LLMService] === 유사성 분석 시작 ===")
            print(f"[LLMService] 원본 이력서: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사 이력서: {similar_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사도 점수: {similarity_score:.3f}")
            
            # 이력서에서 주요 정보 추출
            original_info = self._extract_resume_info(original_resume)
            similar_info = self._extract_resume_info(similar_resume)
            print(f"[LLMService] 이력서 정보 추출 완료")
            
            # 프롬프트 구성
            prompt = self._build_similarity_analysis_prompt(
                original_info, 
                similar_info, 
                similarity_score,
                chunk_details
            )
            print(f"[LLMService] 프롬프트 생성 완료 (길이: {len(prompt)})")
            
            # Gemini API 호출
            system_prompt = "당신은 이력서 유사성 분석 전문가입니다. 두 이력서를 비교하여 구체적으로 어떤 부분이 유사한지 간결하고 명확하게 설명해주세요."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            print(f"[LLMService] Gemini API 호출 시작...")
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.3
                )
            )
            
            print(f"[LLMService] Gemini API 응답 수신 완료")
            analysis_result = response.text
            print(f"[LLMService] 분석 결과 길이: {len(analysis_result) if analysis_result else 0}")
            print(f"[LLMService] 분석 결과 미리보기: {analysis_result[:100] if analysis_result else 'None'}...")
            
            print(f"[LLMService] === 유사성 분석 완료 ===")
            return {
                "success": True,
                "analysis": analysis_result,
                "similarity_score": similarity_score,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] === 유사성 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "유사성 분석에 실패했습니다.",
                "similarity_score": similarity_score,
                "analyzed_at": datetime.now().isoformat()
            }
    
    def _extract_resume_info(self, resume: Dict[str, Any]) -> Dict[str, str]:
        """
        이력서에서 주요 정보를 추출합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            Dict[str, str]: 추출된 정보
        """
        return {
            "name": resume.get("name", "Unknown"),
            "position": resume.get("position", ""),
            "department": resume.get("department", ""),
            "growth_background": resume.get("growthBackground", ""),
            "motivation": resume.get("motivation", ""),
            "career_history": resume.get("careerHistory", ""),
            "experience": resume.get("experience", ""),
            "skills": resume.get("skills", "")
        }
    
    def _build_similarity_analysis_prompt(self, 
                                        original_info: Dict[str, str], 
                                        similar_info: Dict[str, str],
                                        similarity_score: float,
                                        chunk_details: Optional[Dict] = None) -> str:
        """
        유사성 분석을 위한 프롬프트를 구성합니다.
        
        Args:
            original_info (Dict[str, str]): 원본 이력서 정보
            similar_info (Dict[str, str]): 유사한 이력서 정보
            similarity_score (float): 유사도 점수
            chunk_details (Optional[Dict]): 청크별 세부 정보
            
        Returns:
            str: 구성된 프롬프트
        """
        prompt = f"""
다음 두 이력서의 유사성을 분석해주세요. 유사도 점수는 {similarity_score:.1%}입니다.

**원본 이력서 A:**
- 이름: {original_info['name']}
- 지원 직무: {original_info['position']}
- 지원 부서: {original_info['department']}
- 성장배경: {original_info['growth_background'][:200]}...
- 지원동기: {original_info['motivation'][:200]}...
- 경력사항: {original_info['career_history'][:200]}...

**유사한 이력서 B:**
- 이름: {similar_info['name']}
- 지원 직무: {similar_info['position']}
- 지원 부서: {similar_info['department']}
- 성장배경: {similar_info['growth_background'][:200]}...
- 지원동기: {similar_info['motivation'][:200]}...
- 경력사항: {similar_info['career_history'][:200]}...
"""

        if chunk_details:
            prompt += f"\n**청크별 매칭 정보:**\n"
            for key, detail in chunk_details.items():
                prompt += f"- {detail['query_chunk']} → {detail['match_chunk']}: {detail['score']:.1%}\n"

        prompt += """
**분석 요청:**
1. 어떤 구체적인 부분에서 유사성이 발견되는지 설명해주세요
2. 유사한 키워드나 표현이 있다면 언급해주세요
3. 전체적인 유사성의 특징을 간결하게 요약해주세요

200자 이내로 간결하게 답변해주세요.
"""
        return prompt
    
    async def analyze_plagiarism_risk(self, 
                                    original_resume: Dict[str, Any], 
                                    similar_resumes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        표절 위험도를 분석합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 이력서
            similar_resumes (List[Dict[str, Any]]): 유사한 이력서들
            
        Returns:
            Dict[str, Any]: 표절 위험도 분석 결과
        """
        try:
            print(f"[LLMService] === 표절 위험도 분석 시작 ===")
            print(f"[LLMService] 원본 이력서: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사한 이력서 수: {len(similar_resumes)}")
            
            if not similar_resumes:
                print(f"[LLMService] 유사한 이력서가 없음 - LOW 위험도 반환")
                return {
                    "success": True,
                    "risk_level": "LOW",
                    "risk_score": 0.0,
                    "analysis": "유사한 이력서가 발견되지 않았습니다.",
                    "recommendations": []
                }
            
            # 최고 유사도 점수 확인 (API 응답 구조에 맞게 수정)
            similarities = []
            for resume in similar_resumes:
                if "similarity_score" in resume:
                    similarities.append(resume["similarity_score"])
                elif "overall_similarity" in resume:
                    similarities.append(resume["overall_similarity"])
                else:
                    print(f"[LLMService] 경고: 유사도 점수를 찾을 수 없음 - {resume.keys()}")
                    similarities.append(0.0)
            
            max_similarity = max(similarities) if similarities else 0.0
            print(f"[LLMService] 최고 유사도 점수: {max_similarity:.3f}")
            
            # 위험도 레벨 결정
            if max_similarity >= 0.8:
                risk_level = "HIGH"
                risk_score = max_similarity
                analysis = f"매우 높은 유사도({max_similarity:.1%})의 이력서가 발견되었습니다. 표절 가능성이 높습니다."
                recommendations = [
                    "이력서 내용의 독창성을 확인해주세요",
                    "유사한 표현이나 문구를 다른 방식으로 작성해주세요",
                    "개인적인 경험과 구체적인 사례를 더 추가해주세요"
                ]
            elif max_similarity >= 0.6:
                risk_level = "MEDIUM"
                risk_score = max_similarity
                analysis = f"높은 유사도({max_similarity:.1%})의 이력서가 발견되었습니다. 주의가 필요합니다."
                recommendations = [
                    "일부 내용의 독창성을 확인해주세요",
                    "개인만의 특색을 더 강조해주세요"
                ]
            else:
                risk_level = "LOW"
                risk_score = max_similarity
                analysis = f"적정 수준의 유사도({max_similarity:.1%})입니다. 표절 위험은 낮습니다."
                recommendations = []
            
            print(f"[LLMService] 위험도 결정 완료: {risk_level} (점수: {risk_score:.3f})")
            print(f"[LLMService] === 표절 위험도 분석 완료 ===")
            
            return {
                "success": True,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "analysis": analysis,
                "recommendations": recommendations,
                "similar_count": len(similar_resumes),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] === 표절 위험도 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "risk_level": "UNKNOWN",
                "risk_score": 0.0,
                "analysis": "표절 위험도 분석에 실패했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }