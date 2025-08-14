import google.cloud.aiplatform as aiplatform
from typing import Dict, Any, List
import json

class AIHelper:
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self._initialize_client()
    
    def _initialize_client(self):
        aiplatform.init(project=self.api_key)
        
    async def generate_response(self, 
                              prompt: str, 
                              context: Dict[str, Any] = None, 
                              max_tokens: int = 1000,
                              temperature: float = 0.7) -> str:
        """AI 모델을 사용하여 응답을 생성합니다."""
        try:
            # 컨텍스트가 있으면 프롬프트에 추가
            full_prompt = self._build_prompt(prompt, context)
            
            # Gemini API 호출
            response = await self._call_gemini_api(
                prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다."
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """컨텍스트를 포함한 전체 프롬프트를 생성합니다."""
        if not context:
            return prompt
            
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        return f"""컨텍스트:
{context_str}

사용자 입력:
{prompt}"""
    
    async def _call_gemini_api(self,
                              prompt: str,
                              max_tokens: int = 1000,
                              temperature: float = 0.7) -> str:
        """Gemini API를 호출합니다."""
        try:
            # 실제 API 호출 구현
            # 여기에 Gemini API 호출 코드 구현
            return "API 응답 예시"
        except Exception as e:
            raise Exception(f"Gemini API 호출 실패: {e}")
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트를 분석하여 주요 정보를 추출합니다."""
        try:
            # 텍스트 분석 로직 구현
            return {
                "keywords": [],
                "sentiment": "neutral",
                "entities": []
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {}
    
    async def generate_questions(self, context: str) -> List[str]:
        """주어진 컨텍스트를 바탕으로 질문을 생성합니다."""
        try:
            # 질문 생성 로직 구현
            return ["생성된 질문 1", "생성된 질문 2"]
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []