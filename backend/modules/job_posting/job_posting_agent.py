"""
채용공고 에이전트 서비스
동적 템플릿 시스템과 통합된 지능형 채용공고 생성 시스템
"""

import asyncio
import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pymongo import MongoClient

from .duties_separator import DutiesSeparator
from .dynamic_templates import DynamicTemplate, DynamicTemplateManager, TemplateSource
from .job_template import JobTemplateManager


class AgentState(str, Enum):
    """에이전트 상태"""
    INITIAL = "initial"           # 초기 상태
    KEYWORD_EXTRACTION = "keyword_extraction"  # 키워드 추출
    TEMPLATE_SELECTION = "template_selection"  # 템플릿 선택
    CONTENT_GENERATION = "content_generation"  # 내용 생성
    USER_REVIEW = "user_review"   # 사용자 검토
    FINALIZATION = "finalization" # 최종화

class JobPostingAgent:
    """채용공고 에이전트"""

    def __init__(self, db_client: MongoClient, openai_service=None):
        self.db = db_client
        self.openai_service = openai_service
        self.template_manager = DynamicTemplateManager(db_client)
        self.job_template_manager = JobTemplateManager()
        self.duties_separator = DutiesSeparator()  # 주요업무 분리 서비스
        self.sessions = {}  # 세션 관리

    async def start_session(self, user_id: str, company_info: Dict[str, Any] = None) -> str:
        """새로운 세션 시작"""
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.sessions[session_id] = {
            "user_id": user_id,
            "state": AgentState.INITIAL,
            "company_info": company_info or {},
            "extracted_keywords": [],
            "selected_template": None,
            "generated_content": {},
            "user_feedback": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        return session_id

    async def process_user_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """사용자 입력 처리"""
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session = self.sessions[session_id]
        session["updated_at"] = datetime.now()

        # 현재 상태에 따른 처리
        if session["state"] == AgentState.INITIAL:
            return await self._handle_initial_input(session_id, user_input)
        elif session["state"] == AgentState.KEYWORD_EXTRACTION:
            return await self._handle_keyword_extraction(session_id, user_input)
        elif session["state"] == AgentState.TEMPLATE_SELECTION:
            return await self._handle_template_selection(session_id, user_input)
        elif session["state"] == AgentState.CONTENT_GENERATION:
            return await self._handle_content_generation(session_id, user_input)
        elif session["state"] == AgentState.USER_REVIEW:
            return await self._handle_user_review(session_id, user_input)
        elif session["state"] == AgentState.FINALIZATION:
            return await self._handle_finalization(session_id, user_input)

        return {"error": "Invalid state"}

    async def _handle_initial_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """초기 입력 처리"""
        session = self.sessions[session_id]

        # 키워드 추출
        keywords = await self._extract_keywords(user_input)
        session["extracted_keywords"] = keywords

        # 템플릿 추천
        recommended_templates = await self._get_recommended_templates(keywords, session)

        session["state"] = AgentState.TEMPLATE_SELECTION

        return {
            "state": session["state"],
            "message": f"키워드를 추출했습니다: {', '.join(keywords)}",
            "extracted_keywords": keywords,
            "recommended_templates": recommended_templates,
            "next_action": "템플릿을 선택하거나 새로운 템플릿 생성을 요청하세요."
        }

    async def _handle_template_selection(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """템플릿 선택 처리"""
        session = self.sessions[session_id]

        # 템플릿 선택 또는 새 템플릿 생성
        if "새로" in user_input or "생성" in user_input:
            # AI가 새 템플릿 생성
            template = await self._generate_new_template(session)
            session["selected_template"] = template
        else:
            # 기존 템플릿 선택 (실제로는 템플릿 ID로 선택)
            template = await self._select_existing_template(user_input, session)
            session["selected_template"] = template

        session["state"] = AgentState.CONTENT_GENERATION

        return {
            "state": session["state"],
            "message": f"템플릿을 선택했습니다: {template.name}",
            "selected_template": template.content,
            "next_action": "공고 내용을 자동으로 생성하겠습니다."
        }

    async def _handle_content_generation(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """내용 생성 처리"""
        session = self.sessions[session_id]
        template = session["selected_template"]

        # LLM을 사용하여 공고 내용 생성
        generated_content = await self._generate_job_posting_content(
            template,
            session["extracted_keywords"],
            session["company_info"]
        )

        session["generated_content"] = generated_content
        session["state"] = AgentState.USER_REVIEW

        return {
            "state": session["state"],
            "message": "공고 내용을 생성했습니다.",
            "generated_content": generated_content,
            "next_action": "생성된 내용을 확인하고 수정하세요."
        }

    async def _handle_user_review(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """사용자 검토 처리"""
        session = self.sessions[session_id]

        if "수정" in user_input or "변경" in user_input:
            # 수정 요청 처리
            modified_content = await self._apply_user_modifications(
                session["generated_content"],
                user_input
            )
            session["generated_content"] = modified_content

            return {
                "state": session["state"],
                "message": "내용을 수정했습니다.",
                "generated_content": modified_content,
                "next_action": "수정된 내용을 확인하세요."
            }
        elif "확인" in user_input or "완료" in user_input:
            # 최종 확인
            session["state"] = AgentState.FINALIZATION

            return {
                "state": session["state"],
                "message": "공고 내용이 최종 확인되었습니다.",
                "final_content": session["generated_content"],
                "next_action": "공고를 등록하시겠습니까?"
            }

        return {
            "state": session["state"],
            "message": "수정할 내용이 있으면 '수정'을, 확인되면 '확인'을 입력하세요.",
            "generated_content": session["generated_content"]
        }

    async def _handle_finalization(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """최종화 처리"""
        session = self.sessions[session_id]

        if "등록" in user_input or "확인" in user_input:
            # DB에 공고 등록
            job_posting_id = await self._save_job_posting(session)

            # 템플릿 사용 통계 업데이트
            if session["selected_template"]:
                await self.template_manager.learn_from_usage(
                    session["selected_template"].template_id,
                    success=True,
                    feedback={"rating": 5.0, "comment": "성공적으로 등록됨"}
                )

            return {
                "state": "completed",
                "message": f"공고가 성공적으로 등록되었습니다. (ID: {job_posting_id})",
                "job_posting_id": job_posting_id,
                "next_action": "새로운 공고를 작성하시겠습니까?"
            }

        return {
            "state": session["state"],
            "message": "공고를 등록하려면 '등록'을 입력하세요.",
            "final_content": session["generated_content"]
        }

    async def _extract_keywords(self, user_input: str) -> List[str]:
        """키워드 추출"""
        if self.openai_service:
            # LLM을 사용한 키워드 추출
            prompt = f"""
당신은 채용공고 에이전트입니다. 사용자의 요청에서 채용공고 작성에 필요한 키워드만 추출하세요.

사용자 입력: "{user_input}"

다음 카테고리에서 관련 키워드를 추출하세요:
1. 기술 스택 (예: React, Python, AWS 등)
2. 직무 (예: 개발자, 엔지니어, 시니어 등)
3. 경력 요구사항 (예: 3년, 신입, 경력 등)
4. 업무 분야 (예: 백엔드, 프론트엔드, 모바일 등)
5. 위치 (예: 서울, 부산 등)

JSON 형식으로 응답하세요:
{{
    "keywords": ["키워드1", "키워드2", "키워드3"]
}}

가이드라인이나 조언을 제공하지 말고, 키워드만 추출하세요.
"""
            try:
                response = await self.openai_service.generate_text(prompt)
                # JSON 파싱 시도
                import json
                result = json.loads(response)
                return result.get("keywords", [])
            except:
                pass

        # LLM 실패 시 정규식 기반 추출 (fallback)
        keywords = []

        # 기술 스택 키워드
        tech_keywords = [
            "Python", "JavaScript", "React", "Vue", "Angular", "Node.js",
            "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin",
            "Django", "Flask", "Spring", "Express", "FastAPI",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "MySQL", "PostgreSQL", "MongoDB", "Redis"
        ]

        for keyword in tech_keywords:
            if keyword.lower() in user_input.lower():
                keywords.append(keyword)

        # 직무 키워드
        job_keywords = [
            "개발자", "엔지니어", "프로그래머", "아키텍트", "리드",
            "백엔드", "프론트엔드", "풀스택", "모바일", "웹",
            "신입", "경력", "시니어", "주니어", "인턴"
        ]

        for keyword in job_keywords:
            if keyword in user_input:
                keywords.append(keyword)

        # 위치 키워드
        location_keywords = ["서울", "부산", "대구", "인천", "대전", "광주", "울산", "제주"]
        for keyword in location_keywords:
            if keyword in user_input:
                keywords.append(keyword)

        return list(set(keywords))  # 중복 제거

    async def _get_recommended_templates(self, keywords: List[str], session: Dict) -> List[DynamicTemplate]:
        """추천 템플릿 조회"""
        # 키워드 기반 템플릿 검색
        templates = await self.template_manager.get_templates_by_criteria(
            tech_stack=keywords,
            min_success_rate=0.6,
            min_rating=3.5
        )

        # 개인화 추천
        user_history = [session.get("user_id", "")]
        recommended = await self.template_manager.get_recommended_templates(
            user_history,
            {"keywords": keywords}
        )

        # 인기 템플릿
        popular = await self.template_manager.get_popular_templates(3)

        # 중복 제거하고 반환
        all_templates = templates + recommended + popular
        unique_templates = {}
        for template in all_templates:
            if template.template_id not in unique_templates:
                unique_templates[template.template_id] = template

        return list(unique_templates.values())[:5]  # 상위 5개 반환

    async def _generate_new_template(self, session: Dict) -> DynamicTemplate:
        """새 템플릿 생성"""
        keywords = session["extracted_keywords"]
        requirements = {
            "level": self._infer_job_level(keywords),
            "location": self._extract_location(keywords),
            "tech_stack": keywords
        }

        template = await self.template_manager.generate_ai_template(
            keywords=keywords,
            requirements=requirements
        )

        return template

    async def _select_existing_template(self, user_input: str, session: Dict) -> DynamicTemplate:
        """기존 템플릿 선택"""
        # 실제로는 템플릿 ID로 선택
        # 임시로 첫 번째 추천 템플릿 반환
        recommended = await self._get_recommended_templates(session["extracted_keywords"], session)
        return recommended[0] if recommended else None

    async def _generate_job_posting_content(
        self,
        template: DynamicTemplate,
        keywords: List[str],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """공고 내용 생성"""
        if self.openai_service:
            # LLM을 사용한 채용공고 생성
            prompt = f"""
당신은 채용공고 에이전트입니다. 사용자의 요청을 바탕으로 실제 채용공고를 생성하세요.

사용자 요청 키워드: {keywords}
회사 정보: {company_info}
템플릿 정보: {template.content}

다음 형식으로 채용공고를 생성하세요:
{{
    "title": "채용공고 제목",
    "description": "회사 소개 및 포지션 설명",
    "requirements": ["필수 요구사항1", "필수 요구사항2"],
    "preferred": ["우대사항1", "우대사항2"],
    "work_conditions": {{
        "location": "근무지",
        "type": "근무형태",
        "level": "직무레벨"
    }},
    "tech_stack": {keywords}
}}

가이드라인이나 조언을 제공하지 말고, 실제 채용공고 내용만 생성하세요.
"""
            try:
                response = await self.openai_service.generate_text(prompt)
                import json
                result = json.loads(response)
                result["created_at"] = datetime.now().isoformat()
                return result
            except:
                pass

        # LLM 실패 시 템플릿 기반 생성 (fallback)
        company_name = company_info.get("name", "{company}")
        position = self._extract_position(keywords)

        content = {
            "title": template.content.get("title_patterns", [f"{company_name} {position} 채용"])[0].format(
                company=company_name,
                position=position
            ),
            "description": template.content.get("description_patterns", [f"{company_name}에서 {position}를 모집합니다."])[0].format(
                company=company_name,
                position=position
            ),
            "requirements": template.content.get("requirements", ["관련 분야 경험"]),
            "preferred": template.content.get("preferred", ["프로젝트 경험"]),
            "work_conditions": {
                "location": company_info.get("location", "서울"),
                "type": template.content.get("job_type", "fulltime"),
                "level": template.content.get("level", "middle")
            },
            "tech_stack": keywords,
            "created_at": datetime.now().isoformat()
        }

        return content

    async def _apply_user_modifications(self, content: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """사용자 수정 적용"""
        # 실제로는 LLM을 사용하여 수정사항 적용
        # 임시로 키워드 기반 수정

        modified_content = content.copy()

        if "제목" in user_input:
            # 제목 수정 로직
            pass
        elif "설명" in user_input:
            # 설명 수정 로직
            pass
        elif "요구사항" in user_input:
            # 요구사항 수정 로직
            pass

        return modified_content

    async def _save_job_posting(self, session: Dict) -> str:
        """공고 DB 저장"""
        # MongoDB에 공고 저장
        collection = self.db.hireme.job_postings

        job_posting_data = {
            "user_id": session["user_id"],
            "company_info": session["company_info"],
            "content": session["generated_content"],
            "template_id": session["selected_template"].template_id if session["selected_template"] else None,
            "keywords": session["extracted_keywords"],
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = await collection.insert_one(job_posting_data)
        return str(result.inserted_id)

    def _infer_job_level(self, keywords: List[str]) -> str:
        """직무 레벨 추론"""
        if any(word in keywords for word in ["신입", "인턴"]):
            return "junior"
        elif any(word in keywords for word in ["시니어", "리드", "아키텍트"]):
            return "senior"
        else:
            return "middle"

    def _extract_location(self, keywords: List[str]) -> str:
        """위치 추출"""
        locations = ["서울", "부산", "대구", "인천", "대전", "광주", "울산", "제주"]
        for location in locations:
            if location in keywords:
                return location
        return "서울"  # 기본값

    def _extract_position(self, keywords: List[str]) -> str:
        """직무 추출"""
        positions = {
            "개발자": ["개발자", "프로그래머"],
            "엔지니어": ["엔지니어"],
            "아키텍트": ["아키텍트"],
            "리드": ["리드"]
        }

        for position, keywords_list in positions.items():
            if any(keyword in keywords for keyword in keywords_list):
                return position

        return "개발자"  # 기본값

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 상태 조회"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "state": session["state"],
            "user_id": session["user_id"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "extracted_keywords": session["extracted_keywords"],
            "has_template": session["selected_template"] is not None,
            "has_content": bool(session["generated_content"])
        }

    async def separate_main_duties(self, main_duties: str) -> Dict[str, Any]:
        """주요업무를 여러 필드로 분리하는 메소드"""
        try:
            separated_duties = self.duties_separator.separate_duties(main_duties)
            summary = self.duties_separator.get_separation_summary(separated_duties)

            return {
                "success": True,
                "original_duties": main_duties,
                "separated_duties": separated_duties,
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_duties": main_duties,
                "separated_duties": self.duties_separator._empty_result()
            }

    async def end_session(self, session_id: str):
        """세션 종료"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# 전역 인스턴스
job_posting_agent = None

async def init_job_posting_agent(db_client: MongoClient, openai_service=None):
    """채용공고 에이전트 초기화"""
    global job_posting_agent
    job_posting_agent = JobPostingAgent(db_client, openai_service)
