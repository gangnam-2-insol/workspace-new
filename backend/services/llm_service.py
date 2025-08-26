import os
import json
import logging
from typing import List, Dict, Any
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class LLMService:
    """LLM 서비스 클래스"""

    def __init__(self):
        # 기본 API 키 (기존 방식)
        self.default_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
        self.default_client = AsyncOpenAI(api_key=self.default_api_key)
        self.model = "gpt-4o"
        print(f"🔍 [LLMService] 초기화 - 기본 API 키 길이: {len(self.default_api_key) if self.default_api_key else 0}")
        print(f"🔍 [LLMService] 모델: {self.model}")

    async def generate_culture_recommendations(
        self,
        keywords: List[str],
        job: str = "",
        department: str = "",
        trends: List[str] = None
    ) -> List[Dict[str, str]]:
        """키워드 기반 인재상 추천 생성"""

        print(f"🔍 [LLMService] generate_culture_recommendations 시작")
        print(f"   - 키워드: {keywords}")
        print(f"   - 직무: {job}")
        print(f"   - 부서: {department}")
        print(f"   - 트렌드: {trends}")

        try:
            # 인재상 추천용 API 키 (env 파일에서 로드)
            from dotenv import load_dotenv
            load_dotenv()
            # fallback 제거하고 직접 환경변수만 사용
            culture_api_key = os.getenv("OPENAI_API_KEY")
            if not culture_api_key:
                raise Exception("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

            culture_client = AsyncOpenAI(api_key=culture_api_key)

            print(f"🔍 [LLMService] 인재상 추천용 API 키 길이: {len(culture_api_key) if culture_api_key else 0}")
            print(f"🔍 [LLMService] 인재상 추천용 API 키 미리보기: {culture_api_key[:20] if culture_api_key else 'None'}...")
            print(f"🔍 [LLMService] DEBUG OPENAI KEY: {culture_api_key}")
            print(f"🔍 [LLMService] 키 타입 확인: {'sk-proj-' if culture_api_key and culture_api_key.startswith('sk-proj-') else 'sk-' if culture_api_key and culture_api_key.startswith('sk-') else 'unknown'}")

            # 프롬프트 구성
            print(f"🔍 [LLMService] 프롬프트 구성 시작")
            prompt = self._build_prompt(keywords, job, department, trends)
            print(f"🔍 [LLMService] 프롬프트 구성 완료 (길이: {len(prompt)})")

            # LLM 호출
            print(f"🔍 [LLMService] OpenAI API 호출 시작")
            response = await culture_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 회사 인재상 전문가입니다. 사용자의 키워드와 직무 정보를 바탕으로 맞춤형 인재상을 추천해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            print(f"🔍 [LLMService] OpenAI API 호출 완료")

            # 응답 파싱
            content = response.choices[0].message.content
            print(f"🔍 [LLMService] 응답 내용 길이: {len(content)}")
            print(f"🔍 [LLMService] 응답 미리보기: {content[:100]}...")

            result = self._parse_response(content)
            print(f"🔍 [LLMService] 파싱된 결과: {len(result)}개")
            return result

        except Exception as e:
            print(f"❌ [LLMService] LLM 호출 실패: {str(e)}")
            import traceback
            print(f"❌ [LLMService] 스택 트레이스: {traceback.format_exc()}")
            logger.error(f"LLM 호출 실패: {str(e)}")
            # LLM 실패 시 기본 규칙 기반 추천으로 폴백
            print(f"🔍 [LLMService] 폴백으로 전환")
            return self._fallback_recommendations(keywords, job, department)

    def _build_prompt(self, keywords: List[str], job: str, department: str, trends: List[str] = None) -> str:
        """프롬프트 구성"""

        prompt_parts = [
            f"사용자 키워드: {', '.join(keywords)}",
        ]

        if job:
            prompt_parts.append(f"직무: {job}")

        if department:
            prompt_parts.append(f"부서: {department}")

        if trends:
            prompt_parts.append(f"최신 트렌드: {', '.join(trends)}")

        prompt = f"""
        다음 정보를 바탕으로 회사 인재상 5-7개를 추천해주세요:

        {chr(10).join(prompt_parts)}

        각 인재상은 다음 형식으로 JSON 배열로 응답해주세요:
        [
            {{"name": "인재상 이름", "description": "인재상에 대한 상세한 설명"}},
            ...
        ]

        인재상은 다음 기준으로 생성해주세요:
        1. 사용자 키워드를 반영한 맞춤형 인재상
        2. 직무/부서에 특화된 전문성
        3. 현대적이고 실용적인 가치관
        4. 명확하고 이해하기 쉬운 설명
        """

        return prompt

    def _parse_response(self, content: str) -> List[Dict[str, str]]:
        """LLM 응답 파싱"""
        try:
            # JSON 추출 시도
            if '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # JSON이 아닌 경우 기본 형식으로 파싱
                return self._parse_text_response(content)
        except json.JSONDecodeError:
            logger.warning("JSON 파싱 실패, 텍스트 파싱으로 폴백")
            return self._parse_text_response(content)

    def _parse_text_response(self, content: str) -> List[Dict[str, str]]:
        """텍스트 응답 파싱 (JSON이 아닌 경우)"""
        cultures = []
        lines = content.split('\n')

        current_name = ""
        current_description = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('"name"') or line.startswith('name'):
                # 이름 추출
                if ':' in line:
                    current_name = line.split(':', 1)[1].strip().strip('"').strip(',')
            elif line.startswith('"description"') or line.startswith('description'):
                # 설명 추출
                if ':' in line:
                    current_description = line.split(':', 1)[1].strip().strip('"').strip(',')

                    if current_name and current_description:
                        cultures.append({
                            "name": current_name,
                            "description": current_description
                        })
                        current_name = ""
                        current_description = ""

        return cultures

    def _fallback_recommendations(self, keywords: List[str], job: str, department: str) -> List[Dict[str, str]]:
        """LLM 실패 시 기본 규칙 기반 추천"""
        cultures = []

        # 키워드 기반 기본 추천
        keyword_mapping = {
            "책임감": {"name": "책임감과 성실성", "description": "자신의 역할과 의무를 성실히 수행하고 결과에 대한 책임을 지는 자세"},
            "협업": {"name": "효과적 협업", "description": "다양한 배경의 사람들과 협력하여 공통 목표를 달성하는 능력"},
            "문제해결": {"name": "문제 해결 능력", "description": "복잡한 문제를 체계적으로 분석하고 창의적으로 해결하는 능력"},
            "혁신": {"name": "혁신적 사고", "description": "새로운 아이디어를 창출하고 문제를 창의적으로 해결하는 능력"},
            "고객": {"name": "고객 중심 사고", "description": "고객의 니즈를 이해하고 이를 만족시키기 위해 노력하는 자세"},
            "학습": {"name": "지속적 성장", "description": "새로운 기술과 지식을 습득하여 개인과 조직의 성장을 추구하는 자세"}
        }

        for keyword in keywords:
            for key, value in keyword_mapping.items():
                if key in keyword.lower():
                    cultures.append(value)
                    break
            else:
                # 매칭되지 않는 키워드는 기본 형식으로 생성
                cultures.append({
                    "name": f"{keyword} 중심",
                    "description": f"{keyword}을(를) 중요하게 생각하고 실천하는 자세"
                })

        # 키워드가 없으면 기본 추천 제공
        if not cultures:
            default_cultures = [
                {"name": "혁신적 사고", "description": "새로운 아이디어를 창출하고 변화를 주도하는 능력"},
                {"name": "협업 정신", "description": "팀워크를 중시하고 함께 성장하는 문화"},
                {"name": "고객 중심", "description": "고객의 니즈를 최우선으로 생각하는 마인드"},
                {"name": "지속적 학습", "description": "새로운 기술과 지식을 습득하려는 의지"},
                {"name": "책임감", "description": "자신의 역할에 대한 명확한 책임 의식"}
            ]
            cultures = default_cultures

        return cultures[:7]  # 최대 7개 반환
