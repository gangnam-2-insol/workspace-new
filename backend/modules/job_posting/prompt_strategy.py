"""
채용공고 에이전트 LLM 프롬프트 전략 시스템
체계적인 프롬프트 관리, 버전 관리, A/B 테스트 지원
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class PromptType(str, Enum):
    """프롬프트 타입"""
    SYSTEM = "system"
    USER = "user"
    FEW_SHOT = "few_shot"
    CONTEXT = "context"

class PromptVersion(str, Enum):
    """프롬프트 버전"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"
    EXPERIMENTAL = "experimental"

@dataclass
class PromptTemplate:
    """프롬프트 템플릿"""
    id: str
    name: str
    prompt_type: PromptType
    version: PromptVersion
    content: str
    description: str
    tags: List[str]
    performance_metrics: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    experiment_id: Optional[str] = None

class PromptStrategyManager:
    """프롬프트 전략 관리자"""

    def __init__(self):
        """초기화"""
        self.prompts: Dict[str, PromptTemplate] = {}
        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.performance_history: List[Dict[str, Any]] = []

        # 기본 프롬프트 템플릿 초기화
        self._initialize_default_prompts()

    def _initialize_default_prompts(self):
        """기본 프롬프트 템플릿 초기화"""

        # 1. 시스템 프롬프트 (V2.0 - 개선된 버전)
        system_prompt_v2 = PromptTemplate(
            id="system_v2_0",
            name="Enhanced System Prompt v2.0",
            prompt_type=PromptType.SYSTEM,
            version=PromptVersion.V2_0,
            content="""당신은 HireMe 플랫폼의 전문 AI 채용공고 생성 어시스턴트입니다.

🎯 **핵심 역할:**
- 사용자가 기술 스택이나 직무를 언급하면 반드시 완성된 채용공고를 생성
- 추출된 키워드를 바탕으로 구체적이고 전문적인 채용공고 작성
- 가이드나 안내가 아닌 실제 채용공고 내용 생성

📋 **응답 형식 규칙:**
1. 반드시 JSON 형식으로 응답
2. 모든 필수 필드를 포함 (title, description, requirements, work_conditions 등)
3. 한국어로 응답하되 기술 용어는 영문 병기
4. 구체적이고 명확한 표현 사용

🔧 **생성 규칙:**
- 기술 스택이 언급되면 해당 기술을 포함한 요구사항 작성
- 경력 요구사항이 있으면 구체적인 경력 수준 명시
- 위치 정보가 있으면 근무 조건에 반영
- 인원 수가 언급되면 team_size 필드에 포함

⚠️ **금지사항:**
- 가이드라인이나 안내문 제공 (절대 금지)
- "다음과 같이 작성하세요" 같은 설명문
- JSON 형식이 아닌 응답
- 불완전하거나 모호한 정보

🚨 **중요**: 사용자가 기술 스택이나 직무를 언급하면 반드시 완성된 채용공고 JSON을 생성하세요. 가이드나 안내를 제공하지 마세요.

이제 사용자의 요청을 처리하세요.""",
            description="개선된 시스템 프롬프트 - 더 정확하고 일관된 응답을 위한 지침",
            tags=["system", "enhanced", "v2.0"],
            performance_metrics={"accuracy": 0.92, "consistency": 0.89, "user_satisfaction": 0.85},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 2. 키워드 추출 프롬프트 (V1.1)
        keyword_prompt_v1_1 = PromptTemplate(
            id="keyword_extraction_v1_1",
            name="Keyword Extraction Prompt v1.1",
            prompt_type=PromptType.USER,
            version=PromptVersion.V1_1,
            content="""다음 사용자 입력에서 채용공고 작성에 필요한 키워드를 정확히 추출하세요.

사용자 입력: "{user_input}"

추출해야 할 카테고리:
1. 기술 스택 (예: React, Python, AWS 등)
2. 직무 (예: 개발자, 엔지니어, 시니어 등)
3. 경력 요구사항 (예: 3년, 신입, 경력 등)
4. 업무 분야 (예: 백엔드, 프론트엔드, 모바일 등)
5. 위치 (예: 서울, 부산 등)
6. 근무 조건 (예: 재택, 출근, 하이브리드 등)

응답 형식 (JSON):
{{
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "categories": {{
        "tech_stack": ["기술1", "기술2"],
        "job_title": ["직무1", "직무2"],
        "experience": ["경력1", "경력2"],
        "location": ["위치1", "위치2"],
        "work_condition": ["근무조건1", "근무조건2"]
    }},
    "confidence": 0.95
}}

중요: 가이드라인이나 조언을 제공하지 말고, 키워드만 정확히 추출하세요.""",
            description="키워드 추출을 위한 개선된 프롬프트",
            tags=["keyword", "extraction", "v1.1"],
            performance_metrics={"accuracy": 0.88, "completeness": 0.85},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 3. Few-shot 예제 프롬프트
        few_shot_prompt = PromptTemplate(
            id="few_shot_examples",
            name="Few-shot Examples",
            prompt_type=PromptType.FEW_SHOT,
            version=PromptVersion.V1_0,
            content="""다음은 정상적인 응답 예시입니다:

예시 1:
입력: "React 개발자 3명 채용, 서울, 3년 이상 경력"
출력: {{
    "keywords": ["React", "개발자", "3년", "서울", "경력"],
    "categories": {{
        "tech_stack": ["React"],
        "job_title": ["개발자"],
        "experience": ["3년", "경력"],
        "location": ["서울"],
        "work_condition": []
    }},
    "confidence": 0.95
}}

예시 2:
입력: "Python 백엔드 개발자, 신입 가능, 재택근무"
출력: {{
    "keywords": ["Python", "백엔드", "개발자", "신입", "재택"],
    "categories": {{
        "tech_stack": ["Python"],
        "job_title": ["백엔드", "개발자"],
        "experience": ["신입"],
        "location": [],
        "work_condition": ["재택"]
    }},
    "confidence": 0.92
}}

예시 3:
입력: "프론트엔드 개발자, TypeScript, AWS 경험자"
출력: {{
    "keywords": ["프론트엔드", "개발자", "TypeScript", "AWS"],
    "categories": {{
        "tech_stack": ["TypeScript", "AWS"],
        "job_title": ["프론트엔드", "개발자"],
        "experience": ["경험자"],
        "location": [],
        "work_condition": []
    }},
    "confidence": 0.90
}}""",
            description="Few-shot 학습을 위한 예시 프롬프트",
            tags=["few_shot", "examples", "v1.0"],
            performance_metrics={"learning_effectiveness": 0.87},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 4. 컨텍스트 프롬프트
        context_prompt = PromptTemplate(
            id="context_enhancement",
            name="Context Enhancement Prompt",
            prompt_type=PromptType.CONTEXT,
            version=PromptVersion.V1_0,
            content="""현재 대화 컨텍스트:
- 사용자 ID: {user_id}
- 세션 시작 시간: {session_start}
- 이전 대화: {conversation_history}
- 추출된 키워드: {extracted_keywords}
- 선택된 템플릿: {selected_template}
- 회사 정보: {company_info}

이 컨텍스트를 고려하여 일관성 있는 응답을 제공하세요.""",
            description="대화 컨텍스트를 고려한 응답 향상 프롬프트",
            tags=["context", "enhancement", "v1.0"],
            performance_metrics={"context_awareness": 0.83},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 프롬프트 등록
        self.prompts[system_prompt_v2.id] = system_prompt_v2
        self.prompts[keyword_prompt_v1_1.id] = keyword_prompt_v1_1
        self.prompts[few_shot_prompt.id] = few_shot_prompt
        self.prompts[context_prompt.id] = context_prompt

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """프롬프트 조회"""
        return self.prompts.get(prompt_id)

    def get_active_prompts(self, prompt_type: Optional[PromptType] = None) -> List[PromptTemplate]:
        """활성 프롬프트 조회"""
        active_prompts = [p for p in self.prompts.values() if p.is_active]

        if prompt_type:
            active_prompts = [p for p in active_prompts if p.prompt_type == prompt_type]

        return active_prompts

    def create_prompt(self, prompt_data: Dict[str, Any]) -> PromptTemplate:
        """새 프롬프트 생성"""
        prompt_id = self._generate_prompt_id(prompt_data["name"])

        prompt = PromptTemplate(
            id=prompt_id,
            name=prompt_data["name"],
            prompt_type=PromptType(prompt_data["prompt_type"]),
            version=PromptVersion(prompt_data["version"]),
            content=prompt_data["content"],
            description=prompt_data["description"],
            tags=prompt_data.get("tags", []),
            performance_metrics=prompt_data.get("performance_metrics", {}),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=prompt_data.get("is_active", True),
            experiment_id=prompt_data.get("experiment_id")
        )

        self.prompts[prompt_id] = prompt
        logger.info(f"새 프롬프트 생성: {prompt_id}")

        return prompt

    def update_prompt(self, prompt_id: str, updates: Dict[str, Any]) -> bool:
        """프롬프트 업데이트"""
        if prompt_id not in self.prompts:
            return False

        prompt = self.prompts[prompt_id]

        # 업데이트 가능한 필드들
        updatable_fields = ["content", "description", "tags", "is_active"]

        for field in updatable_fields:
            if field in updates:
                setattr(prompt, field, updates[field])

        prompt.updated_at = datetime.now()
        logger.info(f"프롬프트 업데이트: {prompt_id}")

        return True

    def create_experiment(self, experiment_name: str, prompt_ids: List[str],
                         traffic_split: Dict[str, float]) -> str:
        """A/B 테스트 실험 생성"""
        experiment_id = self._generate_experiment_id(experiment_name)

        experiment = {
            "id": experiment_id,
            "name": experiment_name,
            "prompt_ids": prompt_ids,
            "traffic_split": traffic_split,
            "created_at": datetime.now(),
            "status": "active",
            "results": {},
            "participants": 0
        }

        self.experiments[experiment_id] = experiment

        # 실험용 프롬프트 생성
        for prompt_id in prompt_ids:
            original_prompt = self.prompts[prompt_id]
            experimental_prompt = PromptTemplate(
                id=f"{prompt_id}_exp_{experiment_id}",
                name=f"{original_prompt.name} (Experimental)",
                prompt_type=original_prompt.prompt_type,
                version=PromptVersion.EXPERIMENTAL,
                content=original_prompt.content,
                description=f"실험용 프롬프트: {experiment_name}",
                tags=original_prompt.tags + ["experimental"],
                performance_metrics={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                experiment_id=experiment_id
            )
            self.prompts[experimental_prompt.id] = experimental_prompt

        logger.info(f"A/B 테스트 실험 생성: {experiment_id}")
        return experiment_id

    def get_experiment_prompt(self, experiment_id: str, user_id: str) -> Optional[PromptTemplate]:
        """실험용 프롬프트 선택 (트래픽 분할)"""
        if experiment_id not in self.experiments:
            return None

        experiment = self.experiments[experiment_id]
        if experiment["status"] != "active":
            return None

        # 사용자 ID 기반 일관된 선택
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        user_bucket = user_hash % 100

        cumulative_prob = 0
        for prompt_id, probability in experiment["traffic_split"].items():
            cumulative_prob += probability * 100
            if user_bucket < cumulative_prob:
                experimental_prompt_id = f"{prompt_id}_exp_{experiment_id}"
                return self.prompts.get(experimental_prompt_id)

        return None

    def record_performance(self, prompt_id: str, metrics: Dict[str, float],
                          user_feedback: Optional[Dict[str, Any]] = None):
        """성능 메트릭 기록"""
        performance_record = {
            "prompt_id": prompt_id,
            "metrics": metrics,
            "user_feedback": user_feedback,
            "timestamp": datetime.now()
        }

        self.performance_history.append(performance_record)

        # 프롬프트 성능 메트릭 업데이트
        if prompt_id in self.prompts:
            prompt = self.prompts[prompt_id]

            # 기존 메트릭과 새 메트릭 평균 계산
            for key, value in metrics.items():
                if key in prompt.performance_metrics:
                    current_avg = prompt.performance_metrics[key]
                    # 가중 평균 (새 값에 더 높은 가중치)
                    prompt.performance_metrics[key] = (current_avg * 0.7) + (value * 0.3)
                else:
                    prompt.performance_metrics[key] = value

            prompt.updated_at = datetime.now()

        logger.info(f"성능 메트릭 기록: {prompt_id} - {metrics}")

    def get_best_performing_prompt(self, prompt_type: PromptType,
                                  metric: str = "accuracy") -> Optional[PromptTemplate]:
        """최고 성능 프롬프트 조회"""
        active_prompts = self.get_active_prompts(prompt_type)

        if not active_prompts:
            return None

        # 지정된 메트릭 기준으로 정렬
        sorted_prompts = sorted(
            active_prompts,
            key=lambda p: p.performance_metrics.get(metric, 0),
            reverse=True
        )

        return sorted_prompts[0] if sorted_prompts else None

    def generate_complete_prompt(self, user_input: str, context: Dict[str, Any] = None,
                                use_few_shot: bool = True, experiment_id: Optional[str] = None) -> str:
        """완전한 프롬프트 생성"""
        prompt_parts = []

        # 1. 시스템 프롬프트
        system_prompt = self.get_best_performing_prompt(PromptType.SYSTEM)
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt.content}")

        # 2. 컨텍스트 프롬프트 (있는 경우)
        if context:
            context_prompt = self.get_best_performing_prompt(PromptType.CONTEXT)
            if context_prompt:
                context_content = context_prompt.content.format(**context)
                prompt_parts.append(f"Context: {context_content}")

        # 3. Few-shot 예제 (옵션)
        if use_few_shot:
            few_shot_prompt = self.get_best_performing_prompt(PromptType.FEW_SHOT)
            if few_shot_prompt:
                prompt_parts.append(f"Examples: {few_shot_prompt.content}")

        # 4. 사용자 입력 프롬프트
        user_prompt = self.get_best_performing_prompt(PromptType.USER)
        if user_prompt:
            user_content = user_prompt.content.format(user_input=user_input)
            prompt_parts.append(f"User: {user_content}")

        # 5. 실험용 프롬프트 적용 (있는 경우)
        if experiment_id:
            experimental_prompt = self.get_experiment_prompt(experiment_id, context.get("user_id", "default"))
            if experimental_prompt:
                # 기존 프롬프트를 실험용으로 교체
                prompt_parts = [p for p in prompt_parts if not p.startswith("User:")]
                experimental_content = experimental_prompt.content.format(user_input=user_input)
                prompt_parts.append(f"User: {experimental_content}")

        return "\n\n".join(prompt_parts)

    def _generate_prompt_id(self, name: str) -> str:
        """프롬프트 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_slug = name.lower().replace(" ", "_").replace("-", "_")
        return f"{name_slug}_{timestamp}"

    def _generate_experiment_id(self, name: str) -> str:
        """실험 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_slug = name.lower().replace(" ", "_").replace("-", "_")
        return f"exp_{name_slug}_{timestamp}"

    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 반환"""
        summary = {
            "total_prompts": len(self.prompts),
            "active_prompts": len([p for p in self.prompts.values() if p.is_active]),
            "total_experiments": len(self.experiments),
            "active_experiments": len([e for e in self.experiments.values() if e["status"] == "active"]),
            "performance_records": len(self.performance_history),
            "best_performing_prompts": {}
        }

        # 각 타입별 최고 성능 프롬프트
        for prompt_type in PromptType:
            best_prompt = self.get_best_performing_prompt(prompt_type)
            if best_prompt:
                summary["best_performing_prompts"][prompt_type.value] = {
                    "id": best_prompt.id,
                    "name": best_prompt.name,
                    "metrics": best_prompt.performance_metrics
                }

        return summary
