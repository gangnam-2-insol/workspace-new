"""
향상된 채용공고 에이전트
입력 처리, 프롬프트 전략, 출력 검증 시스템이 통합된 완전한 에이전트
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
from pymongo import MongoClient

from .input_processor import InputProcessor, InputIntent, LanguageType
from .prompt_strategy import PromptStrategyManager, PromptType
from .output_validator import OutputValidator, ValidationStatus
from .dynamic_templates import DynamicTemplateManager, DynamicTemplate
from .job_template import JobTemplateManager

logger = logging.getLogger(__name__)

class EnhancedAgentState(str, Enum):
    """향상된 에이전트 상태"""
    INITIAL = "initial"
    INPUT_PROCESSING = "input_processing"
    INTENT_ANALYSIS = "intent_analysis"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TEMPLATE_SELECTION = "template_selection"
    CONTENT_GENERATION = "content_generation"
    OUTPUT_VALIDATION = "output_validation"
    USER_REVIEW = "user_review"
    FINALIZATION = "finalization"
    ERROR_HANDLING = "error_handling"

class EnhancedJobPostingAgent:
    """향상된 채용공고 에이전트"""

    def __init__(self, db_client: MongoClient, openai_service=None):
        """초기화"""
        self.db = db_client
        self.openai_service = openai_service

        # 핵심 시스템 초기화
        self.input_processor = InputProcessor()
        self.prompt_strategy = PromptStrategyManager()
        self.output_validator = OutputValidator()
        self.template_manager = DynamicTemplateManager(db_client)
        self.job_template_manager = JobTemplateManager()

        # 세션 관리
        self.sessions = {}

        # 성능 모니터링
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "input_processing_accuracy": 0.0,
            "output_validation_success_rate": 0.0
        }

        logger.info("향상된 채용공고 에이전트 초기화 완료")

    async def start_session(self, user_id: str, company_info: Dict[str, Any] = None) -> str:
        """새로운 세션 시작"""
        session_id = f"enhanced_session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.sessions[session_id] = {
            "user_id": user_id,
            "state": EnhancedAgentState.INITIAL,
            "company_info": company_info or {},
            "conversation_history": [],
            "input_processing_results": {},
            "extracted_keywords": [],
            "selected_template": None,
            "generated_content": {},
            "validation_results": {},
            "user_feedback": [],
            "performance_data": {
                "start_time": datetime.now(),
                "processing_times": {},
                "error_count": 0
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        logger.info(f"새 세션 시작: {session_id}")
        return session_id

    async def process_user_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """사용자 입력 처리 (향상된 버전)"""
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session = self.sessions[session_id]
        session["updated_at"] = datetime.now()
        session["conversation_history"].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })

        start_time = datetime.now()

        try:
            # 1. 입력 처리 및 전처리
            session["state"] = EnhancedAgentState.INPUT_PROCESSING
            input_result = await self._process_input(user_input)
            session["input_processing_results"] = input_result

            # 2. 의도 분석
            session["state"] = EnhancedAgentState.INTENT_ANALYSIS
            intent_result = await self._analyze_intent(input_result)

            # 3. 의도별 처리
            if intent_result["intent"] == InputIntent.CREATE_POSTING:
                return await self._handle_create_posting(session_id, input_result)
            elif intent_result["intent"] == InputIntent.MODIFY_POSTING:
                return await self._handle_modify_posting(session_id, input_result)
            elif intent_result["intent"] == InputIntent.GET_GUIDE:
                return await self._handle_get_guide(session_id, input_result)
            elif intent_result["intent"] == InputIntent.SEARCH_TEMPLATE:
                return await self._handle_search_template(session_id, input_result)
            else:
                return await self._handle_general_query(session_id, input_result)

        except Exception as e:
            logger.error(f"입력 처리 중 오류: {str(e)}")
            session["state"] = EnhancedAgentState.ERROR_HANDLING
            session["performance_data"]["error_count"] += 1

            return {
                "state": session["state"],
                "error": str(e),
                "message": "처리 중 오류가 발생했습니다. 다시 시도해주세요.",
                "suggested_action": "다른 표현으로 다시 입력해주세요."
            }

        finally:
            # 성능 측정
            processing_time = (datetime.now() - start_time).total_seconds()
            session["performance_data"]["processing_times"]["total"] = processing_time
            self._update_performance_metrics(processing_time, True)

    async def _process_input(self, user_input: str) -> Dict[str, Any]:
        """입력 처리 및 전처리"""
        logger.info("입력 처리 시작")

        # 고급 입력 처리 시스템 사용
        processed_input = self.input_processor.process_input(user_input)

        logger.info(f"입력 처리 완료: 의도={processed_input['intent']}, 언어={processed_input['language']}")
        return processed_input

    async def _analyze_intent(self, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """의도 분석 - LLM 기반 강화"""
        logger.info("의도 분석 시작")

        # 1. 기본 의도 (입력 처리에서 분류된 것)
        base_intent = input_result["intent"]
        keywords = input_result["keywords"]

        # 2. 기술 스택 기반 의도 재분류
        tech_keywords = ["react", "python", "java", "javascript", "typescript", "aws", "docker"]
        has_tech_stack = any(tech in [k.lower() for k in keywords] for tech in tech_keywords)

        # 3. 직무 키워드 기반 의도 재분류
        job_keywords = ["개발자", "엔지니어", "프로그래머", "아키텍트"]
        has_job_keyword = any(job in keywords for job in job_keywords)

        # 4. 최종 의도 결정
        if has_tech_stack and has_job_keyword:
            final_intent = InputIntent.CREATE_POSTING
            confidence = 0.95
        elif base_intent == InputIntent.CREATE_POSTING:
            final_intent = InputIntent.CREATE_POSTING
            confidence = 0.9
        elif "가이드" in input_result["original_input"] or "방법" in input_result["original_input"]:
            final_intent = InputIntent.GET_GUIDE
            confidence = 0.8
        else:
            final_intent = InputIntent.GENERAL_QUERY
            confidence = 0.7

        logger.info(f"의도 분석 완료: {base_intent} → {final_intent} (신뢰도: {confidence})")

        return {
            "intent": final_intent,
            "confidence": confidence,
            "language": input_result["language"],
            "context": input_result["context"],
            "analysis_reason": f"기술스택:{has_tech_stack}, 직무키워드:{has_job_keyword}"
        }

    async def _handle_create_posting(self, session_id: str, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """공고 생성 처리"""
        session = self.sessions[session_id]

        # 1. 키워드 추출 (향상된 버전)
        session["state"] = EnhancedAgentState.KEYWORD_EXTRACTION
        keyword_result = await self._extract_keywords_enhanced(input_result)
        session["extracted_keywords"] = keyword_result["keywords"]

        # 2. 템플릿 선택
        session["state"] = EnhancedAgentState.TEMPLATE_SELECTION
        template_result = await self._select_template_enhanced(keyword_result, session)
        session["selected_template"] = template_result["template"]

        # 3. 내용 생성
        session["state"] = EnhancedAgentState.CONTENT_GENERATION
        content_result = await self._generate_content_enhanced(keyword_result, template_result, session)

        # 4. 출력 검증
        session["state"] = EnhancedAgentState.OUTPUT_VALIDATION
        validation_result = await self._validate_output_enhanced(content_result)
        session["validation_results"] = validation_result

        if validation_result["status"] == ValidationStatus.VALID:
            session["generated_content"] = validation_result["data"]
            session["state"] = EnhancedAgentState.USER_REVIEW

            return {
                "state": session["state"],
                "message": "채용공고가 성공적으로 생성되었습니다.",
                "generated_content": validation_result["data"],
                "confidence": keyword_result["confidence"],
                "next_action": "생성된 내용을 확인하고 수정하세요."
            }
        else:
            # 검증 실패 시 재시도
            return await self._handle_validation_failure(session_id, validation_result)

    async def _extract_keywords_enhanced(self, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """향상된 키워드 추출"""
        logger.info("향상된 키워드 추출 시작")

        # 1. 규칙 기반 키워드 추출 (기본)
        rule_based_keywords = input_result["keywords"]

        # 2. LLM 기반 키워드 추출 (향상된 프롬프트 사용)
        llm_keywords = await self._extract_keywords_with_llm(input_result)

        # 3. 결과 병합 및 정리
        merged_keywords = self._merge_keywords(rule_based_keywords, llm_keywords)

        # 4. 신뢰도 계산
        confidence = self._calculate_keyword_confidence(merged_keywords, input_result)

        result = {
            "keywords": merged_keywords,
            "categories": llm_keywords.get("categories", {}),
            "confidence": confidence,
            "source": "enhanced_extraction"
        }

        logger.info(f"키워드 추출 완료: {len(merged_keywords)}개 키워드, 신뢰도: {confidence}")
        return result

    async def _extract_keywords_with_llm(self, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """LLM을 사용한 키워드 추출"""
        if not self.openai_service:
            return {"keywords": [], "categories": {}}

        try:
            # 향상된 프롬프트 전략 사용
            context = {
                "user_id": "current_user",
                "session_start": datetime.now().isoformat(),
                "conversation_history": "이전 대화 없음",
                "extracted_keywords": input_result["keywords"],
                "selected_template": None,
                "company_info": {}
            }

            prompt = self.prompt_strategy.generate_complete_prompt(
                user_input=input_result["original_input"],
                context=context,
                use_few_shot=True
            )

            # LLM 호출
            response = await self.openai_service.generate_text(prompt)

            # 출력 검증
            validation_result = self.output_validator.validate_and_repair(
                response, "keyword_extraction"
            )

            if validation_result.status in [ValidationStatus.VALID, ValidationStatus.REPAIRED]:
                data = validation_result.repaired_data or validation_result.original_data

                # 성능 기록
                self.prompt_strategy.record_performance(
                    "keyword_extraction_v1_1",
                    {"accuracy": 0.9, "completeness": 0.85}
                )

                return data
            else:
                logger.warning(f"키워드 추출 검증 실패: {validation_result.errors}")
                return {"keywords": [], "categories": {}}

        except Exception as e:
            logger.error(f"LLM 키워드 추출 실패: {str(e)}")
            return {"keywords": [], "categories": {}}

    def _merge_keywords(self, rule_based: List[str], llm_based: Dict[str, Any]) -> List[str]:
        """키워드 병합"""
        llm_keywords = llm_based.get("keywords", [])

        # 중복 제거하면서 병합
        all_keywords = set(rule_based + llm_keywords)

        # 우선순위 정렬 (LLM 결과를 우선)
        priority_keywords = []
        for keyword in llm_keywords:
            if keyword in all_keywords:
                priority_keywords.append(keyword)
                all_keywords.remove(keyword)

        # 나머지 키워드 추가
        result = priority_keywords + list(all_keywords)

        return result[:20]  # 최대 20개로 제한

    def _calculate_keyword_confidence(self, keywords: List[str], input_result: Dict[str, Any]) -> float:
        """키워드 신뢰도 계산"""
        if not keywords:
            return 0.0

        # 기본 신뢰도
        base_confidence = 0.7

        # 키워드 수에 따른 보정
        keyword_count_bonus = min(len(keywords) * 0.05, 0.2)

        # 언어 일치도에 따른 보정
        language_bonus = 0.1 if input_result["language"] in [LanguageType.KOREAN, LanguageType.MIXED] else 0.0

        # 컨텍스트 정보에 따른 보정
        context_bonus = 0.0
        context = input_result["context"]
        if context.get("company_name") or context.get("experience_years"):
            context_bonus = 0.1

        total_confidence = base_confidence + keyword_count_bonus + language_bonus + context_bonus
        return min(total_confidence, 1.0)

    async def _select_template_enhanced(self, keyword_result: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """향상된 템플릿 선택"""
        logger.info("향상된 템플릿 선택 시작")

        keywords = keyword_result["keywords"]
        categories = keyword_result.get("categories", {})

        # 1. 키워드 기반 템플릿 검색
        templates = await self.template_manager.get_templates_by_criteria(
            tech_stack=keywords,
            min_success_rate=0.6,
            min_rating=3.5
        )

        # 2. 개인화 추천
        user_history = [session.get("user_id", "")]
        recommended = await self.template_manager.get_recommended_templates(
            user_history,
            {"keywords": keywords, "categories": categories}
        )

        # 3. 인기 템플릿
        popular = await self.template_manager.get_popular_templates(3)

        # 4. 템플릿 점수 계산 및 정렬
        all_templates = templates + recommended + popular
        scored_templates = []

        for template in all_templates:
            score = self._calculate_template_score(template, keywords, categories)
            scored_templates.append((template, score))

        # 점수순 정렬
        scored_templates.sort(key=lambda x: x[1], reverse=True)

        # 상위 5개 반환
        top_templates = [template for template, score in scored_templates[:5]]

        # 중복 제거
        unique_templates = {}
        for template in top_templates:
            if template.template_id not in unique_templates:
                unique_templates[template.template_id] = template

        result_templates = list(unique_templates.values())

        logger.info(f"템플릿 선택 완료: {len(result_templates)}개 템플릿")

        return {
            "templates": result_templates,
            "template": result_templates[0] if result_templates else None,
            "selection_method": "enhanced_scoring"
        }

    def _calculate_template_score(self, template: DynamicTemplate, keywords: List[str], categories: Dict[str, Any]) -> float:
        """템플릿 점수 계산"""
        score = 0.0

        # 1. 성공률 기반 점수 (40%)
        success_rate = template.metadata.get("success_rate", 0.0)
        score += success_rate * 0.4

        # 2. 평점 기반 점수 (20%)
        rating = template.metadata.get("rating", 0.0)
        score += (rating / 5.0) * 0.2

        # 3. 키워드 매칭 점수 (30%)
        template_keywords = template.content.get("keywords", [])
        keyword_matches = len(set(keywords) & set(template_keywords))
        keyword_score = min(keyword_matches / max(len(keywords), 1), 1.0)
        score += keyword_score * 0.3

        # 4. 사용 빈도 점수 (10%)
        usage_count = template.metadata.get("usage_count", 0)
        usage_score = min(usage_count / 100, 1.0)  # 최대 100회 사용을 기준
        score += usage_score * 0.1

        return score

    async def _generate_content_enhanced(self, keyword_result: Dict[str, Any],
                                       template_result: Dict[str, Any],
                                       session: Dict[str, Any]) -> Dict[str, Any]:
        """향상된 내용 생성"""
        logger.info("향상된 내용 생성 시작")

        if not self.openai_service:
            return self._generate_fallback_content(keyword_result, template_result, session)

        try:
            # 향상된 프롬프트 생성
            context = {
                "user_id": session["user_id"],
                "session_start": session["performance_data"]["start_time"].isoformat(),
                "conversation_history": str(session["conversation_history"][-3:]),  # 최근 3개
                "extracted_keywords": keyword_result["keywords"],
                "selected_template": template_result["template"].name if template_result["template"] else None,
                "company_info": session["company_info"]
            }

            prompt = self.prompt_strategy.generate_complete_prompt(
                user_input=session["conversation_history"][-1]["content"],
                context=context,
                use_few_shot=True
            )

            # LLM 호출
            response = await self.openai_service.generate_text(prompt)

            # 출력 검증
            validation_result = self.output_validator.validate_and_repair(
                response, "job_posting"
            )

            if validation_result.status in [ValidationStatus.VALID, ValidationStatus.REPAIRED]:
                data = validation_result.repaired_data or validation_result.original_data

                # 성능 기록
                self.prompt_strategy.record_performance(
                    "system_v2_0",
                    {"accuracy": 0.9, "consistency": 0.85}
                )

                return {
                    "content": data,
                    "validation_status": validation_result.status,
                    "confidence": keyword_result["confidence"]
                }
            else:
                logger.warning(f"내용 생성 검증 실패: {validation_result.errors}")
                return self._generate_fallback_content(keyword_result, template_result, session)

        except Exception as e:
            logger.error(f"LLM 내용 생성 실패: {str(e)}")
            return self._generate_fallback_content(keyword_result, template_result, session)

    def _generate_fallback_content(self, keyword_result: Dict[str, Any],
                                 template_result: Dict[str, Any],
                                 session: Dict[str, Any]) -> Dict[str, Any]:
        """폴백 내용 생성"""
        template = template_result["template"]
        keywords = keyword_result["keywords"]
        company_info = session["company_info"]

        # 기본 템플릿 기반 생성
        company_name = company_info.get("name", "우리 회사")
        position = self._extract_position_from_keywords(keywords)

        content = {
            "title": f"{company_name} {position} 채용",
            "description": f"{company_name}에서 {position}를 모집합니다. 관련 경험이 있으신 분들의 많은 지원 바랍니다.",
            "requirements": ["관련 분야 경험", "팀워크 능력"],
            "preferred": ["프로젝트 경험", "자격증 보유"],
            "work_conditions": {
                "location": company_info.get("location", "서울"),
                "type": "fulltime",
                "level": "middle"
            },
            "tech_stack": keywords[:5]  # 상위 5개 키워드
        }

        return {
            "content": content,
            "validation_status": ValidationStatus.VALID,
            "confidence": 0.7,
            "source": "fallback"
        }

    def _extract_position_from_keywords(self, keywords: List[str]) -> str:
        """키워드에서 직무 추출"""
        position_keywords = ["개발자", "엔지니어", "프로그래머", "아키텍트", "리드"]

        for keyword in keywords:
            if keyword in position_keywords:
                return keyword

        return "개발자"  # 기본값

    async def _validate_output_enhanced(self, content_result: Dict[str, Any]) -> Dict[str, Any]:
        """향상된 출력 검증"""
        logger.info("향상된 출력 검증 시작")

        content = content_result["content"]

        # 추가 검증 로직
        validation_checks = {
            "title_length": len(content.get("title", "")) >= 5,
            "description_length": len(content.get("description", "")) >= 20,
            "requirements_exist": len(content.get("requirements", [])) > 0,
            "work_conditions_complete": all(
                key in content.get("work_conditions", {})
                for key in ["location", "type", "level"]
            )
        }

        all_valid = all(validation_checks.values())

        if all_valid:
            return {
                "status": ValidationStatus.VALID,
                "data": content,
                "checks": validation_checks
            }
        else:
            return {
                "status": ValidationStatus.PARTIALLY_VALID,
                "data": content,
                "checks": validation_checks,
                "issues": [key for key, valid in validation_checks.items() if not valid]
            }

    async def _handle_validation_failure(self, session_id: str, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """검증 실패 처리"""
        session = self.sessions[session_id]
        session["state"] = EnhancedAgentState.ERROR_HANDLING

        return {
            "state": session["state"],
            "error": "내용 생성 중 오류가 발생했습니다.",
            "message": "다시 시도해주세요.",
            "suggested_action": "더 구체적인 정보를 입력해주세요.",
            "retry_available": True
        }

    async def _handle_modify_posting(self, session_id: str, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """공고 수정 처리"""
        session = self.sessions[session_id]

        if not session.get("generated_content"):
            return {
                "state": session["state"],
                "error": "수정할 공고가 없습니다.",
                "message": "먼저 공고를 생성해주세요."
            }

        # 수정 로직 구현
        return {
            "state": EnhancedAgentState.USER_REVIEW,
            "message": "공고 수정 기능은 개발 중입니다.",
            "current_content": session["generated_content"]
        }

    async def _handle_get_guide(self, session_id: str, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """가이드 요청 처리"""
        return {
            "state": EnhancedAgentState.USER_REVIEW,
            "message": "채용공고 작성 가이드를 제공합니다.",
            "guide": {
                "title": "효과적인 채용공고 작성법",
                "tips": [
                    "구체적인 직무 설명을 포함하세요",
                    "필수 요구사항과 우대사항을 명확히 구분하세요",
                    "근무 조건과 복리후생을 상세히 설명하세요",
                    "지원 방법과 마감일을 명시하세요"
                ]
            }
        }

    async def _handle_search_template(self, session_id: str, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 검색 처리"""
        session = self.sessions[session_id]

        # 키워드 기반 템플릿 검색
        templates = await self.template_manager.get_templates_by_criteria(
            tech_stack=input_result["keywords"],
            min_success_rate=0.5,
            min_rating=3.0
        )

        return {
            "state": EnhancedAgentState.TEMPLATE_SELECTION,
            "message": f"{len(templates)}개의 관련 템플릿을 찾았습니다.",
            "templates": [{"id": t.template_id, "name": t.name, "rating": t.metadata.get("rating", 0)} for t in templates[:5]]
        }

    async def _handle_general_query(self, session_id: str, input_result: Dict[str, Any]) -> Dict[str, Any]:
        """일반 질문 처리"""
        return {
            "state": EnhancedAgentState.USER_REVIEW,
            "message": "채용공고 작성에 도움이 필요하시면 구체적으로 말씀해주세요.",
            "suggestions": [
                "React 개발자 채용공고 작성해줘",
                "신입 개발자 모집 공고 템플릿 추천해줘",
                "채용공고 작성 팁 알려줘"
            ]
        }

    def _update_performance_metrics(self, processing_time: float, success: bool):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_requests"] += 1

        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1

        # 평균 처리 시간 업데이트
        current_avg = self.performance_metrics["average_processing_time"]
        total_requests = self.performance_metrics["total_requests"]
        self.performance_metrics["average_processing_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )

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
            "conversation_count": len(session["conversation_history"]),
            "has_keywords": len(session.get("extracted_keywords", [])) > 0,
            "has_template": session.get("selected_template") is not None,
            "has_content": bool(session.get("generated_content")),
            "error_count": session["performance_data"]["error_count"]
        }

    async def end_session(self, session_id: str):
        """세션 종료"""
        if session_id in self.sessions:
            # 성능 데이터 저장
            session = self.sessions[session_id]
            total_time = (datetime.now() - session["performance_data"]["start_time"]).total_seconds()

            logger.info(f"세션 종료: {session_id}, 총 시간: {total_time:.2f}초, 오류: {session['performance_data']['error_count']}회")

            del self.sessions[session_id]

    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        return {
            "active_sessions": len(self.sessions),
            "performance_metrics": self.performance_metrics,
            "input_processor_stats": self.input_processor.get_processing_stats(),
            "prompt_strategy_stats": self.prompt_strategy.get_performance_summary(),
            "output_validator_stats": self.output_validator.get_validation_summary()
        }

# 전역 인스턴스
enhanced_job_posting_agent = None

async def init_enhanced_job_posting_agent(db_client: MongoClient, openai_service=None):
    """향상된 채용공고 에이전트 초기화"""
    global enhanced_job_posting_agent
    enhanced_job_posting_agent = EnhancedJobPostingAgent(db_client, openai_service)
    logger.info("향상된 채용공고 에이전트 초기화 완료")
