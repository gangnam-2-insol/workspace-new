from typing import Dict, Any, Optional, List
from openai import OpenAI
import os
from datetime import datetime

class LLMService:
    def __init__(self):
        """
        LLM 서비스 초기화
        """
        print(f"[LLMService] === LLM 서비스 초기화 시작 ===")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"[LLMService] 경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
        else:
            print(f"[LLMService] OPENAI_API_KEY 확인됨 (길이: {len(api_key)})")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = 'gpt-4o'
        print(f"[LLMService] OpenAI 클라이언트 초기화 완료: {self.model_name}")
        print(f"[LLMService] === LLM 서비스 초기화 완료 ===")
    
    async def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        OpenAI Chat Completion API를 사용하여 대화 응답을 생성합니다.
        
        Args:
            messages (List[Dict[str, str]]): 대화 메시지 리스트
            max_tokens (int): 최대 토큰 수
            temperature (float): 창의성 조절 (0.0 ~ 1.0)
            
        Returns:
            str: AI 응답 텍스트
        """
        try:
            print(f"[LLMService] === Chat Completion 시작 ===")
            print(f"[LLMService] 메시지 수: {len(messages)}")
            print(f"[LLMService] 모델: {self.model_name}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result = response.choices[0].message.content
            print(f"[LLMService] 응답 생성 완료 (길이: {len(result) if result else 0})")
            print(f"[LLMService] === Chat Completion 완료 ===")
            
            return result
            
        except Exception as e:
            print(f"[LLMService] === Chat Completion 오류 ===")
            print(f"[LLMService] 오류: {str(e)}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    async def analyze_plagiarism_suspicion(self, 
                                    original_resume: Dict[str, Any], 
                                    similar_resumes: List[Dict[str, Any]],
                                    document_type: str = "자소서") -> Dict[str, Any]:
        """
        표절 의심도를 분석합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resumes (List[Dict[str, Any]]): 유사한 문서들
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")
            
        Returns:
            Dict[str, Any]: 표절 의심도 분석 결과
        """
        try:
            print(f"[LLMService] === 표절 의심도 분석 시작 ===")
            
            # 자소서의 경우 applicant_id로 지원자 이름을 조회해야 함
            if document_type == "자소서":
                original_name = original_resume.get('basic_info_names') or original_resume.get('name')
                if not original_name:
                    # applicant_id가 있으면 해당 지원자의 이름을 표시
                    applicant_id = original_resume.get('applicant_id')
                    if applicant_id:
                        original_name = f"지원자ID_{applicant_id}"
                    else:
                        original_name = "Unknown"
            else:
                original_name = original_resume.get('name', 'Unknown')
            print(f"[LLMService] 원본 {document_type}: {original_name}")
            print(f"[LLMService] 유사한 {document_type} 수: {len(similar_resumes)}")
            
            if not similar_resumes:
                print(f"[LLMService] 유사한 {document_type}가 없음 - LOW 의심도 반환")
                return {
                    "success": True,
                    "suspicion_level": "LOW",
                    "suspicion_score": 0.0,
                    "suspicion_score_percent": 0,
                    "analysis": f"유사한 {document_type}가 발견되지 않았습니다. 표절 의심도가 낮습니다.",
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
            
            # 의심도 레벨 결정
            if max_similarity >= 0.8:
                suspicion_level = "HIGH"
            elif max_similarity >= 0.6:
                suspicion_level = "MEDIUM"
            else:
                suspicion_level = "LOW"
            
            suspicion_score = max_similarity
            
            # LLM을 사용하여 상세한 분석 생성
            analysis = await self._generate_plagiarism_analysis(
                max_similarity, suspicion_level, len(similar_resumes), document_type, similar_resumes
            )
            
            recommendations = []
            
            print(f"[LLMService] 의심도 결정 완료: {suspicion_level} (점수: {suspicion_score:.3f})")
            print(f"[LLMService] === 표절 의심도 분석 완료 ===")
            
            return {
                "success": True,
                "suspicion_level": suspicion_level,
                "suspicion_score": suspicion_score,
                "suspicion_score_percent": int(suspicion_score * 100),
                "analysis": analysis,
                "recommendations": recommendations,
                "similar_count": len(similar_resumes),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] === 표절 의심도 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "suspicion_level": "UNKNOWN",
                "suspicion_score": 0.0,
                "suspicion_score_percent": 0,
                "analysis": "표절 의심도 분석에 실패했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }

    async def analyze_similar_applicants(self, target_applicant: Dict[str, Any], 
                                       similar_applicants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        유사 지원자들에 대한 LLM 분석 수행
        
        Args:
            target_applicant (Dict): 기준 지원자 정보
            similar_applicants (List[Dict]): 유사한 지원자들 정보
            
        Returns:
            Dict: LLM 분석 결과
        """
        try:
            print(f"[LLMService] === 유사 지원자 LLM 분석 시작 ===")
            print(f"[LLMService] 기준 지원자: {target_applicant.get('name', 'N/A')}")
            print(f"[LLMService] 유사 지원자 수: {len(similar_applicants)}")
            
            if not similar_applicants:
                return {
                    "success": False,
                    "message": "분석할 유사 지원자가 없습니다."
                }
            
            # LLM 프롬프트 구성
            prompt = self._create_similar_applicants_analysis_prompt(target_applicant, similar_applicants)
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "당신은 인재 채용 전문가입니다. 반드시 요청된 정확한 형식을 따라 응답해주세요. 특히 '### 3. 각 유사 지원자별 상세 분석' 섹션에서 각 지원자마다 🔍 핵심 공통점, 💡 주요 특징, ⭐ 추천 이유, 🎯 유사성 요인을 모두 포함해야 합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 더 일관된 응답을 위해 낮춤
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            print(f"[LLMService] LLM 분석 완료")
            print(f"[LLMService] === LLM 분석 결과 ===")
            print(analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text)
            print(f"[LLMService] === LLM 분석 결과 끝 ===")
            
            return {
                "success": True,
                "analysis": analysis_text,
                "target_applicant": target_applicant,
                "similar_count": len(similar_applicants),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[LLMService] 유사 지원자 분석 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "유사 지원자 분석 중 오류가 발생했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }

    def _create_similar_applicants_analysis_prompt(self, target_applicant: Dict[str, Any], 
                                                 similar_applicants: List[Dict[str, Any]]) -> str:
        """유사 지원자 분석용 프롬프트 생성"""
        
        # 기준 지원자 정보
        prompt = f"""다음 기준 지원자와 유사한 지원자들을 찾았습니다. 왜 유사한지 분석해주세요.

**기준 지원자:**
- 이름: {target_applicant.get('name', 'N/A')}
- 지원직무: {target_applicant.get('position', 'N/A')}
- 경력: {target_applicant.get('experience', 'N/A')}
- 기술스택: {target_applicant.get('skills', 'N/A')}
- 부서: {target_applicant.get('department', 'N/A')}

**유사한 지원자들:**
"""
        
        # 유사 지원자들 정보
        for applicant in similar_applicants:
            prompt += f"""
{applicant['rank']}순위. {applicant.get('name', 'N/A')}
- 지원직무: {applicant.get('position', 'N/A')}
- 경력: {applicant.get('experience', 'N/A')}
- 기술스택: {applicant.get('skills', 'N/A')}
- 부서: {applicant.get('department', 'N/A')}
- 유사도 점수: {applicant.get('final_score', 0):.3f} (벡터: {applicant.get('vector_score', 0):.3f}, 키워드: {applicant.get('keyword_score', 0):.3f})
"""
        
        prompt += """

**중요: 반드시 아래 정확한 형식을 따라 응답해주세요.**

### 1. 기준 지원자와 각 유사 지원자 간의 공통점

### 2. 유사성에 가장 큰 영향을 미친 특성 분석

### 3. 각 유사 지원자별 상세 분석

- **[지원자명]**
  - 🔍 **핵심 공통점**: [기준 지원자와의 주요 공통점 1줄]
  - 💡 **주요 특징**: [핵심 역량이나 경력 요약 1줄]  
  - ⭐ **추천 이유**: [구체적인 추천 근거]
  - 🎯 **유사성 요인**: [유사성에 가장 큰 영향을 미친 특성]

**필수 준수사항:**
1. 반드시 "### 3. 각 유사 지원자별 상세 분석" 섹션을 포함하세요
2. 각 지원자마다 🔍, 💡, ⭐, 🎯 네 가지 항목을 모두 작성하세요
3. 지원자 이름은 **[지원자명]** 형식으로 작성하세요
4. 위 형식을 정확히 따르지 않으면 시스템에서 파싱이 실패합니다
"""
        
        return prompt

    async def _generate_plagiarism_analysis(self, 
                                          similarity_score: float, 
                                          suspicion_level: str, 
                                          similar_count: int, 
                                          document_type: str,
                                          similar_documents: List[Dict[str, Any]]) -> str:
        """
        LLM을 사용하여 표절 의심도 분석 결과를 생성합니다.
        
        Args:
            similarity_score (float): 최고 유사도 점수 (0.0 ~ 1.0)
            suspicion_level (str): 위험도 레벨 (HIGH/MEDIUM/LOW)
            similar_count (int): 유사한 문서 개수
            document_type (str): 문서 타입
            similar_documents (List[Dict]): 유사한 문서들의 상세 정보
            
        Returns:
            str: LLM이 생성한 상세 분석 텍스트
        """
        try:
            print(f"[LLMService] LLM 기반 표절 의심도 분석 시작...")
            
            # 유사도 점수들을 수집
            similarity_details = []
            for doc in similar_documents[:3]:  # 상위 3개만 분석에 포함
                score = doc.get("similarity_score", doc.get("overall_similarity", 0.0))
                name = doc.get("basic_info_names", doc.get("name", "Unknown"))
                similarity_details.append(f"- {name}: {score:.1%} 유사도")
            
            similarity_details_text = "\n".join(similarity_details)
            
            # LLM 프롬프트 구성
            prompt = f"""다음 정보를 바탕으로 {document_type} 표절 의심도를 분석해주세요:

[역할]  
당신은 자기소개서의 의미 기반 유사성을 평가하는 검토 보조자입니다.  
기준 자소서의 일부 문장에서 의미 중복이 감지된 경우, 표현 구조나 흐름 중심으로 평가를 제공합니다.

[입력 데이터]  
- 기준 자소서 문장 중 유사도가 높은 문장 1~2개  
- 각 문장에 대한 유사도 레벨 (HIGH / MEDIUM / LOW)  
- 각 문장에 대해 유사 판단된 이유 (표현 구조, 흐름, 키워드 등)

[작성 목표]  
- 유사도 수치나 유사 자소서 개수는 **말하지 마세요**  
- 기준 자소서 내 **유사 문장**과 그에 대한 **유사 이유**만 간결하게 제시  
- 마지막 줄에는 중립적 LLM 평가 문장을 넣으세요 ("검토 권장" 등)

[출력 예시]

“‘고객 중심 사고를 바탕으로 문제를 해결했습니다.’ 문장은 표현 구조와 핵심 단어가 반복되어 HIGH 등급의 유사성이 관측되었습니다.  
또한 ‘협업을 통해 어려움을 극복하며 성장했습니다.’ 문장도 유사한 흐름으로 구성되어 MEDIUM 등급으로 분류되었습니다.  
일부 문장에서 의미적 중복이 나타나므로, 표절 여부에 대한 검토가 권장됩니다.”


"""

            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 문서 표절 분석 전문가입니다. 임베딩 유사도 점수를 바탕으로 정확하고 전문적인 표절 의심도 분석을 제공해주세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 일관성 있는 분석을 위해 낮은 temperature 사용
                max_tokens=200
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 3줄 제한 처리
            lines = analysis_text.split('\n')
            if len(lines) > 3:
                analysis_text = '\n'.join(lines[:3])
                print(f"[LLMService] LLM 응답이 {len(lines)}줄이므로 3줄로 제한됨")
            
            print(f"[LLMService] LLM 기반 표절 분석 완료 (길이: {len(analysis_text)})")
            
            return analysis_text
            
        except Exception as e:
            print(f"[LLMService] LLM 기반 분석 생성 실패: {str(e)}")
            # 폴백: 기본 규칙 기반 분석
            if suspicion_level == "HIGH":
                return f"매우 높은 유사도({similarity_score:.1%})의 {document_type}가 {similar_count}개 발견되었습니다. 표절 의심도가 높아 추가 검토가 필요합니다."
            elif suspicion_level == "MEDIUM":
                return f"높은 유사도({similarity_score:.1%})의 {document_type}가 {similar_count}개 발견되었습니다. 표절 의심도가 보통 수준이므로 주의가 필요합니다."
            else:
                return f"적정 수준의 유사도({similarity_score:.1%})입니다. 유사한 {document_type} {similar_count}개가 발견되었으나 표절 의심도가 낮습니다."