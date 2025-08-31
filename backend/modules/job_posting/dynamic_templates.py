"""
동적 템플릿 시스템
하드코딩이 아닌 유연하고 학습 가능한 템플릿 시스템
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import random
from pymongo import MongoClient

class TemplateSource(str, Enum):
    """템플릿 소스"""
    SYSTEM = "system"          # 시스템 기본 템플릿
    USER_CREATED = "user"      # 사용자가 생성한 템플릿
    AI_GENERATED = "ai"        # AI가 생성한 템플릿
    LEARNED = "learned"        # 학습을 통해 개선된 템플릿
    COMMUNITY = "community"    # 커뮤니티에서 공유된 템플릿

class DynamicTemplate:
    """동적 템플릿 클래스"""

    def __init__(self, template_id: str, name: str, source: TemplateSource):
        self.template_id = template_id
        self.name = name
        self.source = source
        self.content = {}
        self.metadata = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "usage_count": 0,
            "success_rate": 0.0,
            "rating": 0.0,
            "tags": [],
            "version": "1.0"
        }
        self.learning_data = {
            "successful_applications": 0,
            "total_applications": 0,
            "user_feedback": [],
            "improvement_suggestions": []
        }

    def update_usage(self, success: bool = True):
        """사용 통계 업데이트"""
        self.metadata["usage_count"] += 1
        self.learning_data["total_applications"] += 1

        if success:
            self.learning_data["successful_applications"] += 1

        # 성공률 계산
        self.metadata["success_rate"] = (
            self.learning_data["successful_applications"] /
            self.learning_data["total_applications"]
        )

        self.metadata["updated_at"] = datetime.now()

    def add_feedback(self, rating: float, comment: str = ""):
        """사용자 피드백 추가"""
        self.learning_data["user_feedback"].append({
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now()
        })

        # 평균 평점 계산
        ratings = [f["rating"] for f in self.learning_data["user_feedback"]]
        self.metadata["rating"] = sum(ratings) / len(ratings)

    def suggest_improvements(self, suggestion: str):
        """개선 제안 추가"""
        self.learning_data["improvement_suggestions"].append({
            "suggestion": suggestion,
            "timestamp": datetime.now()
        })

class DynamicTemplateManager:
    """동적 템플릿 관리자"""

    def __init__(self, db_client: MongoClient):
        self.db = db_client
        self.collection = self.db.hireme.dynamic_templates
        self.cache = {}
        self.cache_expiry = timedelta(minutes=30)
        self.last_cache_update = None

    async def get_templates_by_criteria(
        self,
        level: str = None,
        job_type: str = None,
        tech_stack: List[str] = None,
        min_success_rate: float = 0.0,
        min_rating: float = 0.0
    ) -> List[DynamicTemplate]:
        """조건에 맞는 템플릿 조회"""

        # 캐시 확인
        if self._is_cache_valid():
            return self._get_from_cache(level, job_type, tech_stack, min_success_rate, min_rating)

        # DB에서 조회
        query = {}
        if level:
            query["content.level"] = level
        if job_type:
            query["content.job_type"] = job_type
        if tech_stack:
            query["content.tech_stack"] = {"$in": tech_stack}
        if min_success_rate > 0:
            query["metadata.success_rate"] = {"$gte": min_success_rate}
        if min_rating > 0:
            query["metadata.rating"] = {"$gte": min_rating}

        # 성공률과 평점으로 정렬
        cursor = self.collection.find(query).sort([
            ("metadata.success_rate", -1),
            ("metadata.rating", -1),
            ("metadata.usage_count", -1)
        ])

        templates = []
        async for doc in cursor:
            template = self._doc_to_template(doc)
            templates.append(template)

        # 캐시 업데이트
        self._update_cache(templates)

        return templates

    async def create_template(
        self,
        name: str,
        content: Dict[str, Any],
        source: TemplateSource = TemplateSource.USER_CREATED,
        tags: List[str] = None
    ) -> DynamicTemplate:
        """새 템플릿 생성"""

        template_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        template = DynamicTemplate(template_id, name, source)
        template.content = content
        if tags:
            template.metadata["tags"] = tags

        # DB에 저장
        doc = self._template_to_doc(template)
        await self.collection.insert_one(doc)

        # 캐시 무효화
        self._invalidate_cache()

        return template

    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """템플릿 업데이트"""

        update_data = {"$set": {"metadata.updated_at": datetime.now()}}

        if "content" in updates:
            update_data["$set"]["content"] = updates["content"]
        if "metadata" in updates:
            for key, value in updates["metadata"].items():
                update_data["$set"][f"metadata.{key}"] = value

        result = await self.collection.update_one(
            {"template_id": template_id},
            update_data
        )

        if result.modified_count > 0:
            self._invalidate_cache()
            return True

        return False

    async def learn_from_usage(
        self,
        template_id: str,
        success: bool,
        feedback: Dict[str, Any] = None
    ):
        """사용 결과로부터 학습"""

        template = await self.get_template_by_id(template_id)
        if not template:
            return

        template.update_usage(success)

        if feedback:
            if "rating" in feedback:
                template.add_feedback(feedback["rating"], feedback.get("comment", ""))
            if "suggestion" in feedback:
                template.suggest_improvements(feedback["suggestion"])

        # DB 업데이트
        await self.update_template(template_id, {
            "metadata": template.metadata,
            "learning_data": template.learning_data
        })

    async def generate_ai_template(
        self,
        keywords: List[str],
        requirements: Dict[str, Any],
        existing_templates: List[DynamicTemplate] = None
    ) -> DynamicTemplate:
        """AI가 새로운 템플릿 생성"""

        # 기존 템플릿 분석
        successful_patterns = []
        if existing_templates:
            for template in existing_templates:
                if template.metadata["success_rate"] > 0.7:
                    successful_patterns.append(template.content)

        # AI 프롬프트 구성
        prompt = f"""
다음 정보를 바탕으로 새로운 채용공고 템플릿을 생성해주세요:

키워드: {keywords}
요구사항: {requirements}

성공적인 기존 템플릿 패턴:
{json.dumps(successful_patterns, ensure_ascii=False, indent=2)}

새로운 템플릿을 JSON 형태로 생성해주세요.
"""

        # LLM 호출 (실제 구현에서는 OpenAI API 사용)
        # ai_response = await openai_service.generate_response(prompt)

        # 임시로 기본 템플릿 생성
        ai_content = {
            "level": "middle",
            "job_type": "fulltime",
            "title_patterns": [f"{{company}} {keywords[0]} 개발자 채용"],
            "description_patterns": [f"열정적인 {keywords[0]} 개발자를 모집합니다."],
            "requirements": ["관련 분야 경험", "문제 해결 능력"],
            "preferred": ["프로젝트 경험", "기술 블로그 운영"]
        }

        template = await self.create_template(
            name=f"AI 생성 템플릿 - {keywords[0]}",
            content=ai_content,
            source=TemplateSource.AI_GENERATED,
            tags=keywords
        )

        return template

    async def get_template_by_id(self, template_id: str) -> Optional[DynamicTemplate]:
        """ID로 템플릿 조회"""

        doc = await self.collection.find_one({"template_id": template_id})
        if doc:
            return self._doc_to_template(doc)
        return None

    async def get_popular_templates(self, limit: int = 10) -> List[DynamicTemplate]:
        """인기 템플릿 조회"""

        cursor = self.collection.find().sort([
            ("metadata.usage_count", -1),
            ("metadata.success_rate", -1)
        ]).limit(limit)

        templates = []
        async for doc in cursor:
            templates.append(self._doc_to_template(doc))

        return templates

    async def get_recommended_templates(
        self,
        user_history: List[str],
        current_context: Dict[str, Any]
    ) -> List[DynamicTemplate]:
        """개인화된 템플릿 추천"""

        # 사용자 히스토리 기반 추천
        # 실제 구현에서는 협업 필터링이나 콘텐츠 기반 필터링 사용

        # 임시로 인기 템플릿 반환
        return await self.get_popular_templates(5)

    def _doc_to_template(self, doc: Dict) -> DynamicTemplate:
        """DB 문서를 템플릿 객체로 변환"""

        template = DynamicTemplate(
            doc["template_id"],
            doc["name"],
            TemplateSource(doc["source"])
        )
        template.content = doc["content"]
        template.metadata = doc["metadata"]
        template.learning_data = doc["learning_data"]

        return template

    def _template_to_doc(self, template: DynamicTemplate) -> Dict:
        """템플릿 객체를 DB 문서로 변환"""

        return {
            "template_id": template.template_id,
            "name": template.name,
            "source": template.source.value,
            "content": template.content,
            "metadata": template.metadata,
            "learning_data": template.learning_data
        }

    def _is_cache_valid(self) -> bool:
        """캐시 유효성 확인"""
        if not self.last_cache_update:
            return False
        return datetime.now() - self.last_cache_update < self.cache_expiry

    def _get_from_cache(self, *args) -> List[DynamicTemplate]:
        """캐시에서 조회"""
        # 실제 구현에서는 캐시 키 기반 조회
        return []

    def _update_cache(self, templates: List[DynamicTemplate]):
        """캐시 업데이트"""
        self.cache = {t.template_id: t for t in templates}
        self.last_cache_update = datetime.now()

    def _invalidate_cache(self):
        """캐시 무효화"""
        self.cache.clear()
        self.last_cache_update = None

# 전역 인스턴스
dynamic_template_manager = None

async def init_dynamic_template_manager(db_client: MongoClient):
    """동적 템플릿 매니저 초기화"""
    global dynamic_template_manager
    dynamic_template_manager = DynamicTemplateManager(db_client)

    # 기본 템플릿들이 없으면 생성
    await create_default_templates()

async def create_default_templates():
    """기본 템플릿 생성"""
    if not dynamic_template_manager:
        return

    # 기본 템플릿들 생성
    default_templates = [
        {
            "name": "신입 개발자 기본 템플릿",
            "content": {
                "level": "junior",
                "job_type": "fulltime",
                "title_patterns": ["{company} {position} 신입/경력 채용"],
                "description_patterns": ["함께 성장할 {position} 개발자를 모집합니다."],
                "requirements": ["관련 전공자 또는 관련 분야 경험"],
                "preferred": ["관련 프로젝트 경험", "Git 사용 경험"]
            },
            "tags": ["신입", "주니어", "기본"]
        },
        {
            "name": "시니어 개발자 기본 템플릿",
            "content": {
                "level": "senior",
                "job_type": "fulltime",
                "title_patterns": ["{company} {position} 시니어 개발자 채용"],
                "description_patterns": ["기술 리더십을 발휘할 {position} 시니어 개발자를 모집합니다."],
                "requirements": ["관련 분야 5년 이상 경력"],
                "preferred": ["팀 리드 경험", "기술 컨퍼런스 발표 경험"]
            },
            "tags": ["시니어", "고급", "리더십"]
        }
    ]

    for template_data in default_templates:
        await dynamic_template_manager.create_template(
            name=template_data["name"],
            content=template_data["content"],
            source=TemplateSource.SYSTEM,
            tags=template_data["tags"]
        )
