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
        
        try:
            # 환경 변수에서 proxies 관련 설정 제거
            if 'HTTP_PROXY' in os.environ:
                del os.environ['HTTP_PROXY']
            if 'HTTPS_PROXY' in os.environ:
                del os.environ['HTTPS_PROXY']
            if 'http_proxy' in os.environ:
                del os.environ['http_proxy']
            if 'https_proxy' in os.environ:
                del os.environ['https_proxy']
            
            # httpx 클라이언트 설정을 명시적으로 제거
            import httpx
            self.client = OpenAI(
                api_key=api_key,
                http_client=httpx.Client(
                    timeout=httpx.Timeout(30.0),
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            )
        except Exception as e:
            print(f"[LLMService] OpenAI 클라이언트 초기화 오류: {e}")
            # 기본 설정으로 재시도
            import openai
            openai.api_key = api_key
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
        
    async def analyze_similarity_reasoning(self, 
                                         original_resume: Dict[str, Any], 
                                         similar_resume: Dict[str, Any],
                                         similarity_score: float,
                                         chunk_details: Optional[Dict] = None,
                                         document_type: str = "이력서") -> Dict[str, Any]:
        """
        두 문서 간의 유사성을 분석하고 어떤 부분이 유사한지 설명합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resume (Dict[str, Any]): 유사한 문서
            similarity_score (float): 유사도 점수
            chunk_details (Optional[Dict]): 청크별 세부 정보
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")
            
        Returns:
            Dict[str, Any]: 유사성 분석 결과
        """
        try:
            print(f"[LLMService] === 유사성 분석 시작 ===")
            print(f"[LLMService] 원본 {document_type}: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사 {document_type}: {similar_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사도 점수: {similarity_score:.3f}")
            
            # 이력서에서 주요 정보 추출
            original_info = self._extract_resume_info(original_resume)
            similar_info = self._extract_resume_info(similar_resume)
            print(f"[LLMService] {document_type} 정보 추출 완료")
            
            # 프롬프트 구성
            prompt = self._build_similarity_analysis_prompt(
                original_info, 
                similar_info, 
                similarity_score,
                chunk_details
            )
            print(f"[LLMService] 프롬프트 생성 완료 (길이: {len(prompt)})")
            
            # OpenAI API 호출
            system_prompt = f"당신은 {document_type} 유사성 분석 전문가입니다. 두 {document_type}를 비교하여 구체적으로 어떤 부분이 유사한지 간결하고 명확하게 설명해주세요."
            print(f"[LLMService] OpenAI API 호출 시작...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            print(f"[LLMService] OpenAI API 응답 수신 완료")
            analysis_result = response.choices[0].message.content
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
        
        # 청크 매칭 정보 구성
        chunk_info = ""
        if chunk_details:
            chunk_matches = []
            for key, detail in chunk_details.items():
                chunk_matches.append(f"- {detail['query_chunk']} → {detail['match_chunk']} ({detail['score']:.1%})")
            chunk_info = "\n".join(chunk_matches)
        else:
            chunk_info = "청크 매칭 정보 없음"
        
        prompt = f"""역할: 너는 유사성 판정 보조자다. 외부지식 절대 금지.
입력: 이력서 A/B의 섹션 텍스트가 주어진다.
엄격한 규칙:
- 아래 텍스트에 실제로 있는 단어만 사용
- 창작, 추측, 해석 절대 금지
- 없으면 반드시 '없음'이라고 적어라
- 4줄만 출력, 각 줄 40자 이내

## 이력서 A ({original_info['name']})
성장배경: {original_info['growth_background'][:200]}
지원동기: {original_info['motivation'][:200]}
경력사항: {original_info['career_history'][:200]}

## 이력서 B ({similar_info['name']})
성장배경: {similar_info['growth_background'][:200]}
지원동기: {similar_info['motivation'][:200]}
경력사항: {similar_info['career_history'][:200]}

출력 형식 (반드시 각 줄 사이에 공백 줄):

1) 유사부분: {{위 텍스트에서 실제 유사한 섹션만}}

2) 키워드: {{위 텍스트에 실제 나타난 단어만}}

3) 요약: {{실제 텍스트 기반으로만}}

4) 섹션키워드: 성장배경={{실제단어}}|지원동기={{실제단어}}|경력사항={{실제단어}}

**경고: 위 텍스트에 없는 단어는 절대 사용하지 마라.**"""
        
        return prompt
    
    async def analyze_plagiarism_risk(self, 
                                    original_resume: Dict[str, Any], 
                                    similar_resumes: List[Dict[str, Any]],
                                    document_type: str = "이력서") -> Dict[str, Any]:
        """
        표절 위험도를 분석합니다.
        
        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resumes (List[Dict[str, Any]]): 유사한 문서들
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")
            
        Returns:
            Dict[str, Any]: 표절 위험도 분석 결과
        """
        try:
            print(f"[LLMService] === 표절 위험도 분석 시작 ===")
            print(f"[LLMService] 원본 {document_type}: {original_resume.get('name', 'Unknown')}")
            print(f"[LLMService] 유사한 {document_type} 수: {len(similar_resumes)}")
            
            if not similar_resumes:
                print(f"[LLMService] 유사한 {document_type}가 없음 - LOW 위험도 반환")
                return {
                    "success": True,
                    "risk_level": "LOW",
                    "risk_score": 0.0,
                    "analysis": f"유사한 {document_type}가 발견되지 않았습니다.",
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
                analysis = f"매우 높은 유사도({max_similarity:.1%})의 {document_type}가 발견되었습니다. 표절 가능성이 높습니다."
                recommendations = []
            elif max_similarity >= 0.6:
                risk_level = "MEDIUM"
                risk_score = max_similarity
                analysis = f"높은 유사도({max_similarity:.1%})의 {document_type}가 발견되었습니다. 주의가 필요합니다."
                recommendations = []
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