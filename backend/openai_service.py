import openai
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    def __init__(self, model_name: str = "gpt-4o"):
        """
        OpenAI 서비스 초기화

        Args:
            model_name: 사용할 OpenAI 모델 이름 (기본값: gpt-4o)
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
                "당신은 HireMe 플랫폼의 전문 AI 채용 어시스턴트입니다.\n"
                "채용 담당자와 지원자 모두를 돕는 스마트한 채용 솔루션을 제공합니다.\n\n"
                
                "🎯 **핵심 역할:**\n"
                "1. 채용공고 작성 및 최적화 지원\n"
                "2. 이력서/자기소개서 분석 및 피드백\n"
                "3. 면접 질문 생성 및 평가 기준 제안\n"
                "4. 채용 프로세스 전반의 컨설팅\n\n"
                
                "📋 **채용공고 작성 가이드라인:**\n"
                "- 직무명: 구체적이고 매력적으로 (예: 'React 전문 프론트엔드 개발자')\n"
                "- 주요업무: '무엇을 + 왜 + 기대효과' 구조로 작성\n"
                "- 자격요건: 필수/우대 조건을 명확히 구분\n"
                "- 복리후생: 구체적인 혜택과 근무환경 명시\n"
                "- 지원방법: 명확한 지원 절차와 마감일 제시\n\n"
                
                "💼 **업무 설명 작성법:**\n"
                "- 개발 업무: '웹 애플리케이션 개발 → 사용자 경험 향상 → 고객 만족도 증대'\n"
                "- 분석 업무: '데이터 분석 및 인사이트 도출 → 의사결정 지원 → 비즈니스 성과 개선'\n"
                "- 기획 업무: '제품 기획 및 전략 수립 → 시장 경쟁력 강화 → 매출 증대'\n\n"
                
                "🔍 **답변 스타일:**\n"
                "- 전문적이면서도 친근한 톤\n"
                "- 실무에 바로 적용 가능한 구체적인 조언\n"
                "- 불필요한 설명 생략, 핵심만 간결하게\n"
                "- 한국 채용 시장의 트렌드와 관례 반영\n"
                "- 법적 이슈나 차별 요소는 반드시 배제\n\n"
                
                "⚡ **응답 형식:**\n"
                "- 일반 질문: 2-3문장으로 핵심만 요약\n"
                "- 채용공고: 체계적인 템플릿 구조 활용\n"
                "- 번호 항목: 각 항목마다 줄바꿈 적용\n"
                "- 이모지 활용으로 가독성 향상"
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

    async def generate_json_response(self, prompt: str) -> str:
        """
        JSON 형식 응답에 최적화된 OpenAI 응답 생성
        
        Args:
            prompt: JSON 응답을 요구하는 프롬프트
            
        Returns:
            JSON 형식의 응답 텍스트
        """
        if not self.client:
            return '{"error": "OpenAI 서비스를 사용할 수 없습니다."}'

        try:
            messages = [
                {
                    "role": "system", 
                    "content": (
                        "당신은 정확한 JSON 형식으로만 응답하는 AI입니다.\n"
                        "- 반드시 유효한 JSON 형식으로만 응답하세요\n"
                        "- 다른 설명이나 텍스트는 포함하지 마세요\n"
                        "- JSON 외부에 어떤 텍스트도 추가하지 마세요\n"
                        "- 한국어 문자열은 적절히 이스케이프 처리하세요"
                    )
                },
                {"role": "user", "content": prompt}
            ]

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,  # JSON 일관성을 위해 낮은 temperature
                max_tokens=1500,
                response_format={"type": "json_object"}  # JSON 형식 강제
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return '{"error": "응답을 생성할 수 없습니다."}'

        except Exception as e:
            print(f"[ERROR] OpenAI JSON 응답 생성 실패: {e}")
            return f'{{"error": "OpenAI 서비스 오류: {str(e)}"}}'

    async def generate_response_with_vision(self, prompt: str, images: List[Dict[str, Any]]) -> str:
        """
        Vision API를 사용하여 이미지와 텍스트를 함께 분석
        
        Args:
            prompt: 분석 요청 프롬프트
            images: base64로 인코딩된 이미지 리스트
            
        Returns:
            분석 결과 텍스트
        """
        if not self.client:
            return "OpenAI 서비스를 사용할 수 없습니다."

        try:
            # Vision API용 메시지 구성
            content = [{"type": "text", "text": prompt}]
            
            # 이미지 추가
            for image in images:
                content.append(image)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "당신은 이력서 분석 전문가입니다.\n"
                        "이미지와 텍스트를 모두 분석하여 정확한 정보를 추출해주세요.\n"
                        "JSON 형식으로 응답하되, 유효한 JSON만 반환해주세요."
                    )
                },
                {
                    "role": "user",
                    "content": content
                }
            ]

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Vision API는 gpt-4o 사용
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return '{"error": "Vision 분석 결과를 생성할 수 없습니다."}'

        except Exception as e:
            print(f"[ERROR] Vision API 응답 생성 실패: {e}")
            return f'{{"error": "Vision API 오류: {str(e)}"}}'


