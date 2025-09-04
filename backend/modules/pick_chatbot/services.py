from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging
import time
import uuid
import re
from collections import defaultdict

from ..shared.services import BaseService
from .models import (
    ChatSession, ChatMessage, ChatResponse, AgentRequest, AgentOutput,
    GitHubAnalysisRequest, GitHubAnalysisResult, PageNavigationRequest,
    PageNavigationResult, ToolExecutionRequest, ToolExecutionResult,
    IntentClassificationResult, FieldExtractionResult, SessionStatistics,
    ResponseMode, IntentType, ToolType
)

logger = logging.getLogger(__name__)

class PickChatbotService(BaseService):
    """픽톡 서비스"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "chat_sessions"
        self.sessions = defaultdict(dict)
        self.expiry_seconds = 1800  # 30분
        self.max_history = 10

    async def process_chat_message(self, chat_message: ChatMessage) -> ChatResponse:
        """채팅 메시지 처리"""
        try:
            # 세션 관리
            session_id = chat_message.session_id or self._generate_session_id()
            await self._manage_session(session_id, "user", chat_message.message)

            # 의도 분류
            intent_result = await self._classify_intent(chat_message.message)

            # 도구 실행 여부 결정
            if intent_result.intent in [
                IntentType.GITHUB_ANALYSIS,
                IntentType.PAGE_NAVIGATION,
                IntentType.JOB_POSTING_CREATION,
                IntentType.APPLICANT_MANAGEMENT,
                IntentType.RESUME_UPLOAD,
                IntentType.RESUME_SEARCH,
                IntentType.AI_ANALYSIS
            ]:
                tool_result = await self._execute_tool(intent_result, chat_message.message)
                response = await self._generate_tool_response(tool_result, intent_result)
            else:
                response = await self._generate_chat_response(chat_message.message, intent_result)

            # 세션 업데이트
            await self._manage_session(session_id, "assistant", response.message)

            return ChatResponse(
                success=True,
                message=response.message,
                mode=response.mode,
                tool_used=response.tool_used,
                confidence=intent_result.confidence,
                session_id=session_id,
                quick_actions=response.quick_actions
            )
        except Exception as e:
            logger.error(f"채팅 메시지 처리 실패: {str(e)}")
            return ChatResponse(
                success=False,
                message="죄송합니다. 처리 중 오류가 발생했습니다.",
                mode=ResponseMode.CHAT,
                error_info={"error": str(e)}
            )

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 조회"""
        try:
            session_data = await self.db[self.collection].find_one({"session_id": session_id})
            if session_data:
                return ChatSession(**session_data)
            return None
        except Exception as e:
            logger.error(f"세션 조회 실패: {str(e)}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        try:
            result = await self.db[self.collection].delete_one({"session_id": session_id})
            if session_id in self.sessions:
                del self.sessions[session_id]
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"세션 삭제 실패: {str(e)}")
            return False

    async def create_job_posting(self, message: str) -> Dict[str, Any]:
        """채용공고 생성"""
        try:
            # 채용공고 에이전트 초기화 및 호출
            from modules.job_posting.job_posting_agent import JobPostingAgent
            from modules.job_posting.dynamic_templates import DynamicTemplateManager

            # MongoDB 클라이언트 가져오기
            client = self.db.client
            template_manager = DynamicTemplateManager(client)
            agent = JobPostingAgent(client, template_manager)

            # 세션 시작
            session_id = await agent.start_session("pick_chatbot_user")

            # 사용자 입력 처리
            response = await agent.process_user_input(session_id, message)

            # 세션 종료
            await agent.end_session(session_id)

            return {
                "success": True,
                "response": response,
                "message": "채용공고 생성이 완료되었습니다."
            }

        except Exception as e:
            logger.error(f"채용공고 생성 실패: {str(e)}")
            return {
                "success": False,
                "message": f"채용공고 생성 중 오류가 발생했습니다: {str(e)}"
            }

    async def manage_applicants(self, message: str) -> Dict[str, Any]:
        """지원자 관리"""
        try:
            from tools.api_wrapper import ApplicantManagementWrapper

            wrapper = ApplicantManagementWrapper()

            # 메시지에서 지원자 관리 작업 추출
            if "목록" in message or "조회" in message:
                result = await wrapper.get_applicants()
            elif "생성" in message or "추가" in message:
                # 기본 지원자 데이터 (실제로는 사용자 입력에서 추출해야 함)
                applicant_data = {
                    "name": "새 지원자",
                    "email": "new@example.com",
                    "position": "개발자"
                }
                result = await wrapper.create_applicant(applicant_data)
            else:
                result = await wrapper.get_applicants()

            return {
                "success": True,
                "response": result,
                "message": "지원자 관리 작업이 완료되었습니다."
            }

        except Exception as e:
            logger.error(f"지원자 관리 실패: {str(e)}")
            return {
                "success": False,
                "message": f"지원자 관리 중 오류가 발생했습니다: {str(e)}"
            }

    async def upload_resume(self, message: str) -> Dict[str, Any]:
        """이력서 업로드"""
        try:
            from tools.api_wrapper import PDFOCRWrapper

            wrapper = PDFOCRWrapper()

            # 메시지에서 파일 경로 추출 (실제로는 파일 업로드 처리)
            # 여기서는 더미 파일 경로 사용
            file_path = "sample_resume.pdf"

            result = await wrapper.upload_resume(
                file_path=file_path,
                name="지원자",
                email="applicant@example.com"
            )

            return {
                "success": True,
                "response": result,
                "message": "이력서 업로드가 완료되었습니다."
            }

        except Exception as e:
            logger.error(f"이력서 업로드 실패: {str(e)}")
            return {
                "success": False,
                "message": f"이력서 업로드 중 오류가 발생했습니다: {str(e)}"
            }

    async def search_resumes(self, message: str) -> Dict[str, Any]:
        """이력서 검색"""
        try:
            from tools.api_wrapper import ResumeSearchWrapper

            wrapper = ResumeSearchWrapper()

            # 메시지에서 검색어 추출
            search_query = message.replace("검색", "").replace("찾기", "").strip()
            if not search_query:
                search_query = "개발자"

            result = await wrapper.keyword_search(search_query)

            return {
                "success": True,
                "response": result,
                "message": f"'{search_query}' 검색 결과입니다."
            }

        except Exception as e:
            logger.error(f"이력서 검색 실패: {str(e)}")
            return {
                "success": False,
                "message": f"이력서 검색 중 오류가 발생했습니다: {str(e)}"
            }

    async def analyze_with_ai(self, message: str) -> Dict[str, Any]:
        """AI 분석"""
        try:
            from tools.api_wrapper import AIAnalysisWrapper

            wrapper = AIAnalysisWrapper()

            # 메시지에서 분석할 지원자 ID 추출 (실제로는 사용자 입력에서 추출)
            applicant_id = "sample_applicant_id"

            result = await wrapper.analyze_resume(applicant_id)

            return {
                "success": True,
                "response": result,
                "message": "AI 분석이 완료되었습니다."
            }

        except Exception as e:
            logger.error(f"AI 분석 실패: {str(e)}")
            return {
                "success": False,
                "message": f"AI 분석 중 오류가 발생했습니다: {str(e)}"
            }

    async def analyze_github(self, request: GitHubAnalysisRequest) -> GitHubAnalysisResult:
        """GitHub 분석"""
        import time
        start_time = time.time()

        logger.info(f"🔍 [GitHub 분석 서비스] 시작 - 사용자: {request.username}")

        try:
            # GitHub 사용자명 추출
            extract_start = time.time()
            username = self._extract_github_username(request.username)
            if not username:
                raise ValueError("GitHub 사용자명을 찾을 수 없습니다.")
            extract_time = time.time() - extract_start
            logger.info(f"📝 [사용자명 추출] 완료: {username} (소요시간: {extract_time:.3f}초)")

            # GitHub API 호출 (실제 구현에서는 GitHub API 사용)
            profile_start = time.time()
            profile_info = await self._get_github_profile(username)
            profile_time = time.time() - profile_start
            logger.info(f"👤 [프로필 조회] 완료 (소요시간: {profile_time:.3f}초)")

            repos_start = time.time()
            repositories = await self._get_github_repositories(username)
            repos_time = time.time() - repos_start
            logger.info(f"📚 [레포지토리 조회] 완료: {len(repositories)}개 (소요시간: {repos_time:.3f}초)")

            activity_start = time.time()
            activity_analysis = await self._analyze_github_activity(username)
            activity_time = time.time() - activity_start
            logger.info(f"📈 [활동 분석] 완료 (소요시간: {activity_time:.3f}초)")

            skills_start = time.time()
            skill_analysis = await self._analyze_github_skills(repositories)
            skills_time = time.time() - skills_start
            logger.info(f"🔧 [기술 분석] 완료 (소요시간: {skills_time:.3f}초)")

            # 종합 점수 계산
            score_start = time.time()
            overall_score = self._calculate_overall_score(profile_info, repositories, activity_analysis, skill_analysis)
            score_time = time.time() - score_start
            logger.info(f"📊 [점수 계산] 완료: {overall_score:.2f}/10 (소요시간: {score_time:.3f}초)")

            # 권장사항 생성
            rec_start = time.time()
            recommendations = self._generate_recommendations(profile_info, repositories, activity_analysis, skill_analysis)
            rec_time = time.time() - rec_start
            logger.info(f"💡 [권장사항 생성] 완료: {len(recommendations)}개 (소요시간: {rec_time:.3f}초)")

            total_time = time.time() - start_time
            logger.info(f"🎉 [GitHub 분석 전체 완료] 총 소요시간: {total_time:.3f}초")

            return GitHubAnalysisResult(
                username=username,
                profile_info=profile_info,
                repositories=repositories,
                activity_analysis=activity_analysis,
                skill_analysis=skill_analysis,
                overall_score=overall_score,
                recommendations=recommendations
            )
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ [GitHub 분석 실패] 소요시간: {error_time:.3f}초, 오류: {str(e)}")

            # 상세 오류 정보 로깅
            logger.error(f"🔍 [오류 상세]:")
            logger.error(f"    📝 사용자명: {request.username}")
            logger.error(f"    🔍 오류 타입: {type(e).__name__}")
            logger.error(f"    📄 오류 메시지: {str(e)}")

            raise HTTPException(status_code=500, detail=f"GitHub 분석에 실패했습니다: {str(e)}")

    async def navigate_page(self, request: PageNavigationRequest) -> PageNavigationResult:
        """페이지 네비게이션"""
        try:
            # 페이지 매핑
            page_mapping = {
                "채용공고 등록": "/job-posting-registration",
                "지원자 관리": "/applicant-management",
                "대시보드": "/dashboard",
                "포트폴리오 분석": "/portfolio-analysis",

            }

            target_url = page_mapping.get(request.target_page)
            if not target_url:
                return PageNavigationResult(
                    target_page=request.target_page,
                    navigation_success=False,
                    error_message="해당 페이지를 찾을 수 없습니다."
                )

            return PageNavigationResult(
                target_page=request.target_page,
                navigation_success=True,
                current_url=target_url,
                page_title=request.target_page
            )
        except Exception as e:
            logger.error(f"페이지 네비게이션 실패: {str(e)}")
            return PageNavigationResult(
                target_page=request.target_page,
                navigation_success=False,
                error_message=str(e)
            )

    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """도구 실행"""
        try:
            start_time = time.time()

            if request.tool_type == ToolType.GITHUB_ANALYZER:
                result = await self._execute_github_analyzer(request.parameters)
            elif request.tool_type == ToolType.PAGE_NAVIGATOR:
                result = await self._execute_page_navigator(request.parameters)
            elif request.tool_type == ToolType.JOB_POSTING_CREATOR:
                result = await self._execute_job_posting_creator(request.parameters)
            else:
                raise ValueError(f"지원하지 않는 도구 타입: {request.tool_type}")

            execution_time = time.time() - start_time

            return ToolExecutionResult(
                tool_type=request.tool_type,
                success=True,
                result=result,
                execution_time=execution_time
            )
        except Exception as e:
            logger.error(f"도구 실행 실패: {str(e)}")
            return ToolExecutionResult(
                tool_type=request.tool_type,
                success=False,
                error_message=str(e)
            )

    async def get_session_statistics(self) -> SessionStatistics:
        """세션 통계 조회"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_sessions": {"$sum": 1},
                        "active_sessions": {"$sum": {"$cond": ["$is_active", 1, 0]}},
                        "total_messages": {"$sum": {"$size": "$history"}}
                    }
                }
            ]

            result = await self.db[self.collection].aggregate(pipeline).to_list(1)
            if result:
                stats = result[0]
                return SessionStatistics(
                    total_sessions=stats["total_sessions"],
                    active_sessions=stats["active_sessions"],
                    average_session_duration=0.0,  # 실제 구현에서는 계산 필요
                    total_messages=stats["total_messages"],
                    tool_usage_stats={},
                    intent_distribution={}
                )

            return SessionStatistics(
                total_sessions=0, active_sessions=0, average_session_duration=0.0,
                total_messages=0
            )
        except Exception as e:
            logger.error(f"세션 통계 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="세션 통계 조회에 실패했습니다.")

    async def _manage_session(self, session_id: str, role: str, content: str):
        """세션 관리"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "last_activity": int(time.time())
            }

        session = self.sessions[session_id]
        session["history"].append({"role": role, "content": content})

        # 오래된 기록 제거
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history:]

        session["last_activity"] = int(time.time())

    async def _classify_intent(self, message: str) -> IntentClassificationResult:
        """의도 분류"""
        # 간단한 키워드 기반 분류 (실제 구현에서는 AI 모델 사용)
        message_lower = message.lower()

        if any(word in message_lower for word in ["안녕", "hello", "hi"]):
            return IntentClassificationResult(
                intent=IntentType.GREETING,
                confidence=0.9,
                extracted_entities={},
                suggested_tools=[]
            )
        elif any(word in message_lower for word in ["github", "깃허브", "깃헙"]):
            return IntentClassificationResult(
                intent=IntentType.GITHUB_ANALYSIS,
                confidence=0.8,
                extracted_entities={"platform": "github"},
                suggested_tools=[ToolType.GITHUB_ANALYZER]
            )
        elif any(word in message_lower for word in ["이동", "페이지", "페이지로"]):
            return IntentClassificationResult(
                intent=IntentType.PAGE_NAVIGATION,
                confidence=0.7,
                extracted_entities={},
                suggested_tools=[ToolType.PAGE_NAVIGATOR]
            )
        elif any(word in message_lower for word in ["채용공고", "채용", "공고"]):
            return IntentClassificationResult(
                intent=IntentType.JOB_POSTING_CREATION,
                confidence=0.8,
                extracted_entities={},
                suggested_tools=[ToolType.JOB_POSTING_CREATOR]
            )
        elif any(word in message_lower for word in ["지원자", "지원", "applicant"]):
            return IntentClassificationResult(
                intent=IntentType.APPLICANT_MANAGEMENT,
                confidence=0.8,
                extracted_entities={},
                suggested_tools=[ToolType.APPLICANT_MANAGER]
            )
        elif any(word in message_lower for word in ["이력서", "resume", "업로드", "ocr"]):
            return IntentClassificationResult(
                intent=IntentType.RESUME_UPLOAD,
                confidence=0.8,
                extracted_entities={},
                suggested_tools=[ToolType.PDF_OCR]
            )
        elif any(word in message_lower for word in ["검색", "search", "찾기"]):
            return IntentClassificationResult(
                intent=IntentType.RESUME_SEARCH,
                confidence=0.8,
                extracted_entities={},
                suggested_tools=[ToolType.RESUME_SEARCHER]
            )
        elif any(word in message_lower for word in ["분석", "analyze", "ai 분석"]):
            return IntentClassificationResult(
                intent=IntentType.AI_ANALYSIS,
                confidence=0.8,
                extracted_entities={},
                suggested_tools=[ToolType.AI_ANALYZER]
            )
        else:
            return IntentClassificationResult(
                intent=IntentType.GENERAL_QUESTION,
                confidence=0.5,
                extracted_entities={},
                suggested_tools=[]
            )

    async def _execute_tool(self, intent_result: IntentClassificationResult, message: str) -> Dict[str, Any]:
        """도구 실행"""
        if intent_result.intent == IntentType.GITHUB_ANALYSIS:
            username = self._extract_github_username(message)
            if username:
                return await self.analyze_github(GitHubAnalysisRequest(username=username))
        elif intent_result.intent == IntentType.PAGE_NAVIGATION:
            target_page = self._extract_target_page(message)
            if target_page:
                return await self.navigate_page(PageNavigationRequest(target_page=target_page))
        elif intent_result.intent == IntentType.JOB_POSTING_CREATION:
            # 채용공고 생성 처리
            return await self.create_job_posting(message)
        elif intent_result.intent == IntentType.APPLICANT_MANAGEMENT:
            # 지원자 관리 처리
            return await self.manage_applicants(message)
        elif intent_result.intent == IntentType.RESUME_UPLOAD:
            # 이력서 업로드 처리
            return await self.upload_resume(message)
        elif intent_result.intent == IntentType.RESUME_SEARCH:
            # 이력서 검색 처리
            return await self.search_resumes(message)
        elif intent_result.intent == IntentType.AI_ANALYSIS:
            # AI 분석 처리
            return await self.analyze_with_ai(message)

        return {"message": "도구 실행에 실패했습니다."}

    async def _generate_tool_response(self, tool_result: Dict[str, Any], intent_result: IntentClassificationResult) -> ChatResponse:
        """도구 응답 생성"""
        if intent_result.intent == IntentType.GITHUB_ANALYSIS:
            if isinstance(tool_result, GitHubAnalysisResult):
                message = f"GitHub 분석 결과:\n\n"
                message += f"사용자: {tool_result.username}\n"
                message += f"종합 점수: {tool_result.overall_score:.1f}/100\n"
                message += f"레포지토리 수: {len(tool_result.repositories)}\n"
                if tool_result.recommendations:
                    message += f"\n권장사항:\n" + "\n".join(f"- {rec}" for rec in tool_result.recommendations[:3])

                return ChatResponse(
                    success=True,
                    message=message,
                    mode=ResponseMode.TOOL,
                    tool_used="github_analyzer",
                    confidence=intent_result.confidence
                )
        elif intent_result.intent == IntentType.PAGE_NAVIGATION:
            if isinstance(tool_result, PageNavigationResult):
                if tool_result.navigation_success:
                    message = f"'{tool_result.target_page}' 페이지로 이동했습니다."
                else:
                    message = f"페이지 이동에 실패했습니다: {tool_result.error_message}"

                return ChatResponse(
                    success=True,
                    message=message,
                    mode=ResponseMode.ACTION,
                    tool_used="page_navigator",
                    confidence=intent_result.confidence
                )
        elif intent_result.intent == IntentType.JOB_POSTING_CREATION:
            # 채용공고 생성 응답 처리
            if tool_result.get("success"):
                job_response = tool_result.get("response", {})

                # 채용공고 에이전트 응답을 사용자 친화적으로 변환
                if job_response.get("state") == "template_selection":
                    message = f"채용공고 작성을 도와드리겠습니다!\n\n"
                    message += f"추출된 키워드: {', '.join(job_response.get('extracted_keywords', []))}\n\n"
                    message += f"다음 단계: {job_response.get('next_action', '')}"

                    # 빠른 액션 추가
                    quick_actions = [
                        {"title": "채용공고 등록", "action": "navigate", "target": "/job-posting", "icon": "📝"},
                        {"title": "템플릿 선택", "action": "chat", "message": "템플릿을 선택해주세요", "icon": "📋"}
                    ]
                else:
                    message = job_response.get("message", "채용공고 생성이 완료되었습니다.")
                    quick_actions = []

                return ChatResponse(
                    success=True,
                    message=message,
                    mode=ResponseMode.TOOL,
                    tool_used="job_posting_creator",
                    confidence=intent_result.confidence,
                    quick_actions=quick_actions
                )
            else:
                return ChatResponse(
                    success=False,
                    message=tool_result.get("message", "채용공고 생성에 실패했습니다."),
                    mode=ResponseMode.TOOL,
                    confidence=intent_result.confidence
                )

        return ChatResponse(
            success=True,
            message="도구 실행이 완료되었습니다.",
            mode=ResponseMode.TOOL,
            confidence=intent_result.confidence
        )

    async def _generate_chat_response(self, message: str, intent_result: IntentClassificationResult) -> ChatResponse:
        """일반 채팅 응답 생성"""
        if intent_result.intent == IntentType.GREETING:
            response_message = "안녕하세요! 픽톡입니다. 무엇을 도와드릴까요?"
        else:
            response_message = "죄송합니다. 더 구체적으로 말씀해 주시면 도움을 드릴 수 있습니다."

        return ChatResponse(
            success=True,
            message=response_message,
            mode=ResponseMode.CHAT,
            confidence=intent_result.confidence
        )

    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        return str(uuid.uuid4())

    def _extract_github_username(self, message: str) -> Optional[str]:
        """GitHub 사용자명 추출"""
        # GitHub URL 패턴 매칭
        github_pattern = r'github\.com/([a-zA-Z0-9_-]+)'
        match = re.search(github_pattern, message)
        if match:
            return match.group(1)

        # 사용자명 직접 추출
        username_pattern = r'@([a-zA-Z0-9_-]+)'
        match = re.search(username_pattern, message)
        if match:
            return match.group(1)

        return None

    def _extract_target_page(self, message: str) -> Optional[str]:
        """목표 페이지 추출"""
        page_keywords = {
            "채용공고": "채용공고 등록",
            "지원자": "지원자 관리",
            "대시보드": "대시보드",
            "포트폴리오": "포트폴리오 분석",

        }

        for keyword, page in page_keywords.items():
            if keyword in message:
                return page

        return None

    async def _get_github_profile(self, username: str) -> Dict[str, Any]:
        """GitHub 프로필 정보 조회 (더미 데이터)"""
        return {
            "username": username,
            "name": f"{username}",
            "bio": "개발자",
            "followers": 100,
            "following": 50,
            "public_repos": 20,
            "created_at": "2020-01-01"
        }

    async def _get_github_repositories(self, username: str) -> List[Dict[str, Any]]:
        """GitHub 레포지토리 정보 조회 (더미 데이터)"""
        return [
            {
                "name": "project-1",
                "description": "첫 번째 프로젝트",
                "language": "Python",
                "stars": 10,
                "forks": 5,
                "updated_at": "2024-01-01"
            },
            {
                "name": "project-2",
                "description": "두 번째 프로젝트",
                "language": "JavaScript",
                "stars": 15,
                "forks": 8,
                "updated_at": "2024-01-15"
            }
        ]

    async def _analyze_github_activity(self, username: str) -> Dict[str, Any]:
        """GitHub 활동 분석 (더미 데이터)"""
        return {
            "commit_frequency": "높음",
            "contribution_streak": 30,
            "recent_activity": "활발함",
            "collaboration_score": 8.5
        }

    async def _analyze_github_skills(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """GitHub 기술 스택 분석"""
        languages = {}
        for repo in repositories:
            lang = repo.get("language", "Unknown")
            languages[lang] = languages.get(lang, 0) + 1

        return {
            "languages": languages,
            "primary_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown",
            "diversity_score": len(languages) / 10.0
        }

    def _calculate_overall_score(self, profile: Dict[str, Any], repos: List[Dict[str, Any]],
                               activity: Dict[str, Any], skills: Dict[str, Any]) -> float:
        """종합 점수 계산"""
        score = 0.0

        # 프로필 점수 (20점)
        score += min(profile.get("followers", 0) / 100, 10)
        score += min(profile.get("public_repos", 0) / 20, 10)

        # 레포지토리 점수 (40점)
        score += min(len(repos) * 2, 20)
        total_stars = sum(repo.get("stars", 0) for repo in repos)
        score += min(total_stars / 10, 20)

        # 활동 점수 (20점)
        score += min(activity.get("contribution_streak", 0) / 3, 20)

        # 기술 다양성 점수 (20점)
        score += skills.get("diversity_score", 0) * 20

        return min(score, 100.0)

    def _generate_recommendations(self, profile: Dict[str, Any], repos: List[Dict[str, Any]],
                                activity: Dict[str, Any], skills: Dict[str, Any]) -> List[str]:
        """권장사항 생성"""
        recommendations = []

        if profile.get("followers", 0) < 50:
            recommendations.append("GitHub 활동을 더 활발히 하여 팔로워를 늘려보세요.")

        if len(repos) < 5:
            recommendations.append("더 많은 프로젝트를 공개하여 포트폴리오를 확장해보세요.")

        if skills.get("diversity_score", 0) < 0.3:
            recommendations.append("다양한 프로그래밍 언어를 사용해보세요.")

        if not recommendations:
            recommendations.append("훌륭한 GitHub 프로필입니다! 계속해서 활동을 이어가세요.")

        return recommendations

    async def _execute_github_analyzer(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub 분석기 실행"""
        username = parameters.get("username")
        if not username:
            raise ValueError("GitHub 사용자명이 필요합니다.")

        result = await self.analyze_github(GitHubAnalysisRequest(username=username))
        return result.dict()

    async def _execute_page_navigator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """페이지 네비게이터 실행"""
        target_page = parameters.get("target_page")
        if not target_page:
            raise ValueError("목표 페이지가 필요합니다.")

        result = await self.navigate_page(PageNavigationRequest(target_page=target_page))
        return result.dict()

    async def _execute_job_posting_creator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """채용공고 생성기 실행"""
        # 실제 구현에서는 채용공고 생성 로직 호출
        return {
            "message": "채용공고 생성 기능은 준비 중입니다.",
            "status": "pending"
        }
