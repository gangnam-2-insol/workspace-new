import openai
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        OpenAI 서비스 초기화

        Args:
            model_name: 사용할 OpenAI 모델 이름 (기본값: gpt-4o-mini)
        """
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")

        try:
            if not self.api_key:
                raise Exception("OPENAI_API_KEY가 설정되지 않았습니다.")

            openai.api_key = self.api_key
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            print(f"[SUCCESS] OpenAI 서비스 초기화 성공 (모델: {model_name})")
        except Exception as e:
            print(f"[ERROR] OpenAI 서비스 초기화 실패: {e}")
            print("[INFO] OPENAI_API_KEY가 올바르게 설정되었는지 확인하세요")
            self.client = None

    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        OpenAI 모델을 사용하여 응답 생성

        Args:
            prompt: 사용자 입력 프롬프트
            conversation_history: 대화 히스토리 (role/content 형식)

        Returns:
            생성된 응답 텍스트
        """
        if not self.client:
            return "OpenAI 서비스를 사용할 수 없습니다. OPENAI_API_KEY가 올바르게 설정되었는지 확인해주세요."

        try:
            messages: List[Dict[str, str]] = []

            system_prompt = (
                "당신은 채용 전문 어시스턴트입니다. "
                "사용자가 채용 공고 작성이나 채용 관련 질문을 할 때 전문적이고 실용적인 답변을 제공해주세요.\n\n"
                "주의사항:\n"
                "- AI 모델에 대한 설명은 하지 마세요\n"
                "- 채용 관련 실무적인 조언을 제공하세요\n"
                "- 구체적이고 실용적인 답변을 해주세요\n"
                "- 한국어로 답변해주세요\n"
                "- 모든 답변은 핵심만 간단하게 요약해서 2~3줄 이내로 작성해주세요\n"
                "- 불필요한 설명은 생략하고, 요점 위주로 간결하게 답변해주세요\n"
                "- '주요 업무'를 작성할 때는 지원자 입장에서 직무 이해도가 높아지도록 구체적인 동사(예: 개발, 분석, 관리 등)를 사용하세요\n"
                "- 각 업무는 \"무엇을 한다 → 왜 한다\" 구조로, 기대 성과까지 간결히 포함하세요\n"
                "- 번호가 있는 항목(1, 2, 3 등)은 각 줄마다 줄바꿈하여 출력해주세요"
            )
            messages.append({"role": "system", "content": system_prompt})

            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=0.8,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "응답을 생성할 수 없습니다."

        except Exception as e:
            print(f"[ERROR] OpenAI 응답 생성 실패: {e}")
            return f"OpenAI 서비스 오류가 발생했습니다: {str(e)}"


