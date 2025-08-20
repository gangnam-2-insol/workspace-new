"""
LLM 서비스 모듈

에이전트 시스템을 위한 LLM 서비스입니다.
"""

from typing import Dict, Any, Optional, List
from openai import OpenAI
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    """에이전트 시스템을 위한 LLM 서비스"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        LLM 서비스 초기화
        
        Args:
            model_name (str): 사용할 모델 이름
        """
        logger.info(f"[LLMService] === LLM 서비스 초기화 시작 ===")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("[LLMService] 경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
            raise ValueError("OPENAI_API_KEY 환경변수가 필요합니다")
        else:
            logger.info(f"[LLMService] OPENAI_API_KEY 확인됨 (길이: {len(api_key)})")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        logger.info(f"[LLMService] OpenAI 클라이언트 초기화 완료: {self.model_name}")
        logger.info(f"[LLMService] === LLM 서비스 초기화 완료 ===")
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            max_tokens: int = 1000, 
                            temperature: float = 0.7) -> str:
        """
        OpenAI Chat API를 사용하여 대화 응답을 생성합니다.
        
        Args:
            messages (List[Dict[str, str]]): 대화 메시지 리스트
            max_tokens (int): 최대 토큰 수
            temperature (float): 창의성 조절 (0.0-1.0)
            
        Returns:
            str: AI 응답 텍스트
        """
        try:
            logger.info(f"[LLMService] === 채팅 완료 시작 ===")
            logger.info(f"[LLMService] 메시지 수: {len(messages)}")
            logger.info(f"[LLMService] 모델: {self.model_name}")
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"[LLMService] AI 응답 생성 완료 (길이: {len(ai_response)})")
            logger.info(f"[LLMService] === 채팅 완료 끝 ===")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"[LLMService] === 채팅 완료 중 오류 발생 ===")
            logger.error(f"[LLMService] 오류 타입: {type(e).__name__}")
            logger.error(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            logger.error(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다."
    
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
            logger.info(f"[LLMService] === 유사성 분석 시작 ===")
            logger.info(f"[LLMService] 원본 {document_type}: {original_resume.get('name', 'Unknown')}")
            logger.info(f"[LLMService] 유사 {document_type}: {similar_resume.get('name', 'Unknown')}")
            logger.info(f"[LLMService] 유사도 점수: {similarity_score:.3f}")
            
            # 이력서에서 주요 정보 추출
            original_info = self._extract_resume_info(original_resume)
            similar_info = self._extract_resume_info(similar_resume)
            logger.info(f"[LLMService] {document_type} 정보 추출 완료")
            
            # 프롬프트 구성
            prompt = self._build_similarity_analysis_prompt(
                original_info, 
                similar_info, 
                similarity_score,
                chunk_details
            )
            logger.info(f"[LLMService] 프롬프트 생성 완료 (길이: {len(prompt)})")
            
            # OpenAI API 호출
            system_prompt = f"당신은 {document_type} 유사성 분석 전문가입니다. 두 {document_type}를 비교하여 구체적으로 어떤 부분이 유사한지 간결하고 명확하게 설명해주세요."
            logger.info(f"[LLMService] OpenAI API 호출 시작...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            logger.info(f"[LLMService] OpenAI API 응답 수신 완료")
            analysis_result = response.choices[0].message.content
            logger.info(f"[LLMService] 분석 결과 길이: {len(analysis_result) if analysis_result else 0}")
            logger.info(f"[LLMService] 분석 결과 미리보기: {analysis_result[:100] if analysis_result else 'None'}...")
            
            logger.info(f"[LLMService] === 유사성 분석 완료 ===")
            return {
                "success": True,
                "analysis": analysis_result,
                "similarity_score": similarity_score,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[LLMService] === 유사성 분석 중 오류 발생 ===")
            logger.error(f"[LLMService] 오류 타입: {type(e).__name__}")
            logger.error(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            logger.error(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
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
