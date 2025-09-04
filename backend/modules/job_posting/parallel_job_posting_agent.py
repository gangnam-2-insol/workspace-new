"""
병렬 채용공고 생성 에이전트
메인: 채용공고 생성 / 백그라운드: 내부 DB 검색
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .duties_separator import DutiesSeparator

logger = logging.getLogger(__name__)

class ParallelJobPostingAgent:
    """병렬 채용공고 생성 에이전트"""

    def __init__(self, openai_service=None, tool_executor=None):
        """초기화"""
        self.openai_service = openai_service
        self.tool_executor = tool_executor
        self.duties_separator = DutiesSeparator()  # 주요업무 분리기

        # 기술 스택 키워드
        self.tech_keywords = {
            "react": ["react", "리액트"],
            "react_native": ["react native", "reactnative", "리액트네이티브"],
            "python": ["python", "파이썬"],
            "java": ["java", "자바"],
            "javascript": ["javascript", "js", "자바스크립트"],
            "typescript": ["typescript", "ts", "타입스크립트"],
            "node": ["node", "nodejs", "node.js", "노드"],
            "aws": ["aws", "아마존"],
            "docker": ["docker", "도커"],
            "kubernetes": ["kubernetes", "k8s", "쿠버네티스"],
            "frontend": ["프론트엔드", "frontend", "front-end"],
            "backend": ["백엔드", "backend", "back-end"],
            "fullstack": ["풀스택", "fullstack", "full-stack"],
            "django": ["django", "장고"],
            "angular": ["angular", "angularjs", "앵귤러"],
            "unity": ["unity", "유니티"],
            "mobile": ["모바일", "mobile", "앱"],
            "web": ["웹", "web"],
            "devops": ["데브옵스", "devops", "dev-ops"]
        }

        # 직무 키워드 (확장)
        self.job_keywords = [
            "개발자", "엔지니어", "프로그래머", "아키텍트", "리드",
            "신입", "시니어", "주니어", "인턴", "CTO", "테크리드", "테크 리드"
        ]

        # 위치 키워드
        self.location_keywords = ["서울", "부산", "대구", "인천", "대전", "광주", "울산", "제주", "강남구", "종로구", "마포구"]

        # 의도분류 결과 저장용 변수
        self.last_intent_tool = ""
        self.last_intent_action = ""

    async def process_job_posting_request(self, user_message: str, session_id: str = None) -> Dict[str, Any]:
        """채용공고 요청 처리 - 실제 채용공고 생성 및 미리보기"""
        import time
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"🤖 [JOB-AGENT DEBUG] 채용공고 에이전트 처리 시작")
        print(f"📝 세션 ID: {session_id}")
        print(f"💬 사용자 메시지: '{user_message}'")
        print(f"🕐 처리 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        logger.info(f"채용공고 요청 처리 시작: {user_message[:50]}...")

        # 의도 분류
        intent_start = time.time()
        is_job_posting = self._is_job_posting_intent(user_message)
        intent_time = time.time() - intent_start
        print(f"🎯 [의도 분류] 결과: {is_job_posting} (소요시간: {intent_time:.3f}초)")

        if not is_job_posting:
            print(f"❌ [의도 분류] 채용공고 생성 요청이 아닙니다. 일반 응답 반환")
            return {
                "type": "general_response",
                "message": "채용공고 생성 요청이 아닙니다.",
                "job_posting": None,
                "candidate_recommendations": None
            }

        # 채용공고 생성 및 백그라운드 검색
        try:
            print(f"🚀 [채용공고 처리] 채팅창 응답 + 페이지 이동 모드 실행")
            # 메인 작업: 실제 채용공고 생성 (채팅창에 표시용)
            job_posting_task = self._generate_job_posting_with_preview(user_message)
            # 백그라운드 작업: 내부 DB 검색
            background_task = self._search_internal_candidates(user_message, session_id)

            # 두 작업을 병렬로 실행
            job_posting_result, candidate_search_result = await asyncio.gather(
                job_posting_task,
                background_task,
                return_exceptions=True
            )

            # 결과 처리 - 채팅창 응답 + 페이지 이동 액션 추가
            return self._combine_job_posting_results_with_navigation(job_posting_result, candidate_search_result)

        except Exception as e:
            logger.error(f"처리 중 오류: {str(e)}")
            return {
                "type": "error",
                "message": "처리 중 오류가 발생했습니다.",
                "error": str(e)
            }

    def _combine_job_posting_results_with_navigation(self, job_posting_result: Dict[str, Any],
                                                   candidate_result: Dict[str, Any]) -> Dict[str, Any]:
        """채용공고 결과 결합 - 채팅창 응답 + 페이지 이동 액션 추가"""

        print(f"🔄 [결과 결합] 채팅창 응답 + 페이지 이동 액션 생성")

        # 메인 결과 (채용공고 생성)
        if isinstance(job_posting_result, Exception):
            print(f"❌ [결과 결합] 채용공고 생성 실패: {str(job_posting_result)}")
            return {
                "type": "error",
                "message": f"채용공고 생성 실패: {str(job_posting_result)}"
            }

        if job_posting_result.get("status") != "success":
            print(f"❌ [결과 결합] 채용공고 생성 상태 오류: {job_posting_result.get('message', '알 수 없는 오류')}")
            return {
                "type": "error",
                "message": job_posting_result.get("message", "채용공고 생성 실패")
            }

        job_posting = job_posting_result["job_posting"]
        extracted_data = job_posting_result.get("extracted_data", {})

        print(f"✅ [결과 결합] 채용공고 생성 성공: {job_posting.get('title', 'N/A')}")

        # 기본 응답 구성 (기존과 동일)
        from datetime import datetime

        result = {
            "status": "success",  # ✅ 누락된 status 필드 추가
            "type": "job_posting_preview",
            "message": "채용공고를 생성했습니다. 검토 후 등록하시겠습니까?",
            "job_posting": job_posting,
            "original_message": job_posting_result.get("original_message", ""),
            "candidate_recommendations": None,
            "background_status": "🔍 조건에 맞는 지원자 검색 중...",
            "timestamp": datetime.now(),  # ✅ timestamp 필드 추가
            "preview_actions": {
                "register": "등록하기",
                "edit": "수정하기",
                "cancel": "취소"
            },
            # 🎯 핵심: 페이지 이동 액션 추가
            "page_action": {
                "action": "navigate",
                "path": "/ai-job-registration",
                            "auto_fill_data": {
                "title": job_posting.get('title', ''),
                "position": job_posting.get('position', ''),
                "location": job_posting.get('location', '서울'),
                "tech_stack": job_posting.get('tech_stack', []),
                "experience_level": job_posting.get('experience_level', '경력무관'),
                "team_size": job_posting.get('team_size', 1),
                "remote_work": job_posting.get('remote_work', False),
                "employment_type": job_posting.get('employment_type', '정규직'),
                "department": job_posting.get('department', '개발팀'),
                "salary": self._format_salary_for_ui(job_posting.get('salary')),  # 급여 필드 추가
                "working_hours": job_posting.get('working_hours', '09:00-18:00'),  # 근무 시간 추가
                "contact_email": job_posting.get('contact_email', ''),  # 연락처 이메일 추가
                "description": job_posting.get('description', ''),
                "requirements": job_posting.get('requirements', []),
                "preferred_qualifications": job_posting.get('preferred_qualifications', []),
                "benefits": job_posting.get('benefits', [])
            },
                "message": "🤖 AI 채용공고 등록 페이지로 이동하여 추출된 정보를 확인하고 등록하세요."
            }
        }

        print(f"📝 [결과 결합] 페이지 이동 액션 추가: {result['page_action']['path']}")
        print(f"🎯 [결과 결합] 자동 입력 데이터 개수: {len(result['page_action']['auto_fill_data'])}개")

        # 백그라운드 결과 (지원자 추천) 처리
        if (not isinstance(candidate_result, Exception) and
            candidate_result.get("status") == "success" and
            candidate_result.get("candidates")):

            candidates = candidate_result["candidates"]
            if candidates:
                result["candidate_recommendations"] = {
                    "count": len(candidates),
                    "candidates": candidates[:3],  # 최대 3명만 표시
                    "message": "💡 혹시 이런 지원자는 어떠세요?"
                }
                result["background_status"] = "✅ 지원자 검색 완료"
                print(f"👥 [결과 결합] 지원자 추천 추가: {len(candidates)}명")
            else:
                result["background_status"] = "📭 조건에 맞는 지원자를 찾지 못했습니다"
                print(f"📭 [결과 결합] 지원자 없음")
        elif isinstance(candidate_result, Exception):
            result["background_status"] = "⚠️ 지원자 검색 중 오류 발생"
            logger.error(f"지원자 검색 오류: {str(candidate_result)}")
        else:
            # 검색 결과 없음 - 조용히 처리
            result["background_status"] = "🔍 검색 완료 (결과 없음)"
            logger.info("지원자 검색 결과 없음")

        logger.info(f"최종 응답 완성: 타입={result['type']}, 페이지액션={bool(result.get('page_action'))}")
        return result

    def _is_job_posting_intent(self, message: str) -> bool:
        """채용공고 생성 의도 판단 - LLM 기반으로 단순화"""
        logger.debug(f"의도 분류 분석: '{message}'")

        # LLM 기반 의도 분류 (기존 복잡한 로직 대체)
        try:
            # 간단한 키워드 체크만 유지 (빠른 필터링용)
            basic_keywords = ["채용", "모집", "구인", "뽑", "구하", "개발자", "엔지니어"]
            has_basic_keywords = any(keyword in message for keyword in basic_keywords)

            if not has_basic_keywords:
                logger.debug("기본 키워드 없음 - False 반환")
                return False

            # LLM에게 의도 분류 요청
            return self._classify_intent_with_llm(message)

        except Exception as e:
            logger.warning(f"LLM 기반 분류 실패, 기본 로직으로 폴백: {e}")
            return self._fallback_intent_classification(message)

    def _classify_intent_with_llm(self, message: str) -> bool:
        """LLM을 사용한 의도 분류"""
        try:
            # LLM에게 JSON 형식으로 의도 분류 요청 (툴 정보 포함)
            prompt = f"""
사용자 메시지가 채용공고 생성을 요청하는 것인지 판단해주세요.

메시지: "{message}"

**예시:**
- "프론트엔드 개발자 채용공고를 작성해줘" → true
- "채용 공고를 새로 등록하고 싶어" → true
- "개발자 뽑고 있어요" → true
- "백엔드 엔지니어 모집해요" → true
- "이번 주 날씨 어때?" → false
- "지원자 목록 보여줘" → false
- "안녕하세요" → false

**판단 기준:**
1. 직무 + 채용 관련 키워드 조합 → true
2. "채용공고", "작성해줘", "생성", "등록" 등 액션 키워드 → true
3. "개발자", "엔지니어", "프로그래머" + "모집", "뽑", "구인" → true
4. 일반 대화, 다른 기능 요청 → false

사용 가능한 툴들:
- job_posting: 채용공고 생성, 수정, 삭제, 조회
- applicant: 지원자 관리
- github: GitHub 정보 조회
- mongodb: 데이터베이스 조회

다음 JSON 형식으로 응답해주세요:
{{
    "is_job_posting_intent": true/false,
    "confidence": 0.0-1.0,
    "reason": "판단 근거",
    "suggested_tool": "job_posting",
    "suggested_action": "create"
}}

사용자가 채용공고 생성을 요청하면 true, 아니면 false를 반환하세요.
reason에는 판단 근거를 구체적으로 작성해주세요.
"""

            # LLM 서비스 호출 (비동기 처리)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                from modules.core.services.llm_service import LLMService
                llm_service = LLMService()

                # 간단한 응답 생성 (실제로는 LLM 호출)
                response = loop.run_until_complete(
                    llm_service.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=100,
                        temperature=0.1
                    )
                )

                print(f"🔍 [의도분류] LLM 응답: {response}")

                # JSON 파싱 시도 (안전화 강화)
                import json
                try:
                    if "{" in response and "}" in response:
                        start = response.find("{")
                        end = response.rfind("}") + 1
                        json_str = response[start:end]

                        # JSON 유효성 검사
                        result = json.loads(json_str)

                        # 필수 필드 검증
                        if "is_job_posting_intent" not in result:
                            print(f"🔍 [의도분류] JSON에 필수 필드 없음, 폴백 사용")
                            return self._fallback_intent_classification(message)

                        is_intent = result.get("is_job_posting_intent", False)
                        confidence = result.get("confidence", 0.0)
                        suggested_tool = result.get("suggested_tool", "")
                        suggested_action = result.get("suggested_action", "")
                        reason = result.get("reason", "")

                        print(f"🔍 [의도분류] LLM 결과: {is_intent} (신뢰도: {confidence})")
                        print(f"🔍 [의도분류] 제안 툴: {suggested_tool}, 액션: {suggested_action}")
                        print(f"🔍 [의도분류] 판단 근거: {reason}")

                        # 툴 정보를 인스턴스 변수에 저장
                        self.last_intent_tool = suggested_tool
                        self.last_intent_action = suggested_action

                        # 신뢰도가 낮으면 폴백 로직 사용
                        if confidence < 0.5:
                            print(f"🔍 [의도분류] 신뢰도 낮음 ({confidence}), 폴백 사용")
                            return self._fallback_intent_classification(message)

                        return is_intent
                    else:
                        print(f"🔍 [의도분류] JSON 형식 없음, 폴백 사용")
                        return self._fallback_intent_classification(message)

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"🔍 [의도분류] JSON 파싱 오류: {e}, 폴백 사용")
                    return self._fallback_intent_classification(message)

            finally:
                loop.close()

        except Exception as e:
            print(f"🔍 [의도분류] LLM 분류 오류: {e}")
            return self._fallback_intent_classification(message)

    def _fallback_intent_classification(self, message: str) -> bool:
        """LLM 실패 시 사용할 기본 의도 분류 (강화된 로직)"""
        print(f"🔍 [의도분류] 폴백 로직 사용")

        message_lower = message.lower()

        # 1단계: 액션 키워드 체크 (가장 강력한 신호)
        action_keywords = ["채용공고", "작성해줘", "생성", "등록", "만들어줘", "작성", "생성해줘"]
        has_action = any(keyword in message for keyword in action_keywords)

        if has_action:
            print(f"🔍 [의도분류] 액션 키워드 감지: {[k for k in action_keywords if k in message]}")
            return True

        # 2단계: 직무 + 채용 키워드 조합 체크
        job_keywords = ["개발자", "엔지니어", "프로그래머", "디자이너", "기획자", "마케터"]
        recruitment_keywords = ["채용", "모집", "구인", "뽑", "구하", "모집해", "뽑아"]

        has_job = any(keyword in message for keyword in job_keywords)
        has_recruitment = any(keyword in message for keyword in recruitment_keywords)

        if has_job and has_recruitment:
            print(f"🔍 [의도분류] 직무+채용 키워드 조합 감지: 직무={has_job}, 채용={has_recruitment}")
            return True

        # 3단계: 구체적인 채용 표현 체크
        specific_patterns = [
            "뽑고 있어", "모집 중", "구하고 있어", "채용 중",
            "개발자 뽑", "엔지니어 모집", "프로그래머 구해"
        ]

        for pattern in specific_patterns:
            if pattern in message_lower:
                print(f"🔍 [의도분류] 구체적 패턴 감지: {pattern}")
                return True

        print(f"🔍 [의도분류] 폴백 로직: False 반환")
        return False

    # 기존 복잡한 의도분류 로직 주석처리
    """
    def _is_job_posting_intent_old(self, message: str) -> bool:
        # 기존 복잡한 의도분류 로직 (주석처리)
        message_lower = message.lower()

        print(f"🔍 [의도분류] 메시지 분석: '{message}'")

        # 기술 스택 + 직무 키워드 체크 (하드코딩 방식)
        has_tech_hardcoded = any(
            any(variant in message_lower for variant in variants)
            for variants in self.tech_keywords.values()
        )
        has_job_hardcoded = any(job in message for job in self.job_keywords)

        # 동적 기술 스택 감지 (더 유연한 방식)
        tech_patterns = [
            r'\b(?:python|java|javascript|typescript|go|golang|react|vue|angular|node|spring|django|flask|express|mysql|postgresql|mongodb|redis|docker|kubernetes|aws|azure|gcp)\b',
            r'\b(?:프론트엔드|백엔드|풀스택|모바일|웹|앱|서버|데이터베이스|클라우드)\b',
            r'\b(?:개발|프로그래밍|코딩|구현|설계|아키텍처)\b'
        ]

        import re
        has_tech_dynamic = any(re.search(pattern, message_lower) for pattern in tech_patterns)

        # 직무 관련 동적 감지
        job_patterns = [
            r'\b(?:개발자|엔지니어|프로그래머|아키텍트|데이터사이언티스트|데이터분석가|기획자|디자이너)\b',
            r'\b(?:시니어|주니어|리드|매니저|팀장|책임자)\b',
            r'\b(?:경력|신입|주니어|시니어)\s*\d*\s*년'
        ]

        has_job_dynamic = any(re.search(pattern, message) for pattern in job_patterns)

        # 통합 결과 (하드코딩 또는 동적 감지 중 하나라도 True면 True)
        has_tech = has_tech_hardcoded or has_tech_dynamic
        has_job = has_job_hardcoded or has_job_dynamic

        # 채용 관련 키워드 체크 (기본 키워드)
        basic_hiring_keywords = ["채용", "모집", "구인", "뽑", "구하"]
        has_basic_hiring = any(keyword in message for keyword in basic_hiring_keywords)

        # 채용공고 맥락 키워드 체크 (더 정확한 맥락 파악)
        job_posting_context_patterns = [
            "공고를 등록", "공고 등록", "채용공고 등록", "채용 공고 등록",
            "공고를 작성", "공고 작성", "채용공고 작성", "채용 공고 작성",
            "공고를 만들어", "공고 만들", "채용공고 만들", "채용 공고 만들",
            "공고를 생성", "공고 생성", "채용공고 생성", "채용 공고 생성",
            "채용공고", "채용 공고", "구인공고", "구인 공고", "모집공고", "모집 공고"
        ]
        has_job_posting_context = any(pattern in message for pattern in job_posting_context_patterns)

        # 기본 채용 키워드 또는 채용공고 맥락 키워드가 있으면 True
        has_hiring = has_basic_hiring or has_job_posting_context

        print(f"🔍 [의도분류] 분석 결과:")
        print(f"    기술스택(하드코딩): {has_tech_hardcoded}")
        print(f"    기술스택(동적): {has_tech_dynamic}")
        print(f"    기술스택(통합): {has_tech}")
        print(f"    직무키워드(하드코딩): {has_job_hardcoded}")
        print(f"    직무키워드(동적): {has_job_dynamic}")
        print(f"    직무키워드(통합): {has_job}")
        print(f"    기본채용키워드: {has_basic_hiring}")
        print(f"    채용공고맥락: {has_job_posting_context}")
        print(f"    채용키워드(통합): {has_hiring}")

        # 가이드 요청 제외 (기준 완화)
        # 명확한 가이드 요청만 제외하고, 애매한 경우는 채용공고로 분류
        strong_guide_patterns = [
            "작성 방법", "어떻게 작성", "방법을 알려", "가이드를", "도움이", "설명해",
            "작성법", "쓰는 법", "만드는 방법", "작성 팁", "어떻게 써야", "뭘 써야"
        ]
        is_strong_guide = any(pattern in message for pattern in strong_guide_patterns)

        # 질문 형태의 가이드 요청 (물음표 + 가이드 키워드)
        guide_question_keywords = ["방법", "어떻게", "가이드", "안내", "설명"]
        is_guide_question = "?" in message and any(keyword in message for keyword in guide_question_keywords)

        # 강력한 가이드 요청이거나 명확한 가이드 질문인 경우만 제외
        if is_strong_guide or is_guide_question:
            return False

        # 채용 의도 판단 (더 포용적으로 변경)
        # 1. 기술스택 + 직무
        # 2. 채용키워드 + 기술스택
        # 3. 채용키워드 + 직무 (새로 추가)
        # 4. 개발자 + 채용관련 동사 (새로 추가)

        hiring_verbs = ["뽑", "구하", "모집", "채용", "구인", "찾", "필요"]
        has_hiring_verb = any(verb in message for verb in hiring_verbs)

        print(f"    채용동사: {has_hiring_verb}")

        # 최종 판단
        result = (
            (has_tech and has_job) or           # 기술스택 + 직무
            (has_hiring and has_tech) or        # 채용키워드 + 기술스택
            (has_hiring and has_job) or         # 채용키워드 + 직무
            (has_job and has_hiring_verb)       # 직무 + 채용동사
        )

        print(f"🔍 [의도분류] 최종 결과: {result}")
        return result
    """

    async def _generate_job_posting_with_preview(self, message: str) -> Dict[str, Any]:
        """실제 채용공고 생성 (미리보기용)"""
        logger.info("채용공고 생성 시작")

        try:
            # 키워드 추출
            extracted_data = self._extract_job_info(message)

            # LLM을 사용한 완전한 채용공고 생성
            if self.openai_service:
                job_posting = await self._generate_complete_job_posting(message, extracted_data)
            else:
                # LLM 없을 때 기본 템플릿 사용
                job_posting = self._create_default_job_posting(extracted_data)

            logger.info("채용공고 생성 완료")
            return {
                "status": "success",
                "job_posting": job_posting,
                "extracted_data": extracted_data,
                "original_message": message
            }

        except Exception as e:
            logger.error(f"채용공고 생성 실패: {str(e)}")
            return {
                "status": "error",
                "message": f"채용공고 생성 실패: {str(e)}"
            }

    async def _generate_complete_job_posting(self, message: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM을 사용한 완전한 채용공고 생성"""
        system_prompt = """당신은 전문 채용공고 작성 전문가입니다.

주어진 정보를 바탕으로 완전한 채용공고를 JSON 형식으로 생성하세요.

응답 형식:
{
  "title": "구체적인 채용공고 제목",
  "company_name": "회사명 (알 수 없으면 '스타트업' 또는 '성장기업')",
  "department": "부서명",
  "position": "직무명",
  "employment_type": "정규직",
  "experience_level": "신입/경력 구분",
  "location": "근무지",
  "salary": {
    "min": 최소급여(숫자, 천단위 쉼표 없이),
    "max": 최대급여(숫자, 천단위 쉼표 없이),
    "currency": "KRW"
  },
  "description": "회사 소개 및 일반적인 업무 개요 (예: 우리 회사는 성장기업이며, 백엔드 개발 업무를 담당하게 됩니다)",
  "requirements": [
    "필수 요구사항1",
    "필수 요구사항2"
  ],
  "preferred_qualifications": [
    "우대사항1",
    "우대사항2"
  ],
  "benefits": [
    "복리후생1",
    "복리후생2"
  ],
  "work_conditions": {
    "location": "구체적 근무지",
    "remote": true/false,
    "working_hours": "근무시간"
  },
  "tech_stack": ["기술1", "기술2"],
  "team_size": 숫자,
  "application_deadline": "2024-12-31",
  "contact_info": {
    "email": "contact@company.com",
    "phone": "02-1234-5678"
  }
}

**중요 규칙:**
- description: 회사 소개와 일반적인 업무 개요만 작성. 구체적인 기술명, 경력 요구사항, 스킬은 절대 언급하지 말 것
- requirements: 필수 요구사항만 배열로 작성 (구체적인 기술, 경력, 스킬 포함)
- preferred_qualifications: 우대사항만 배열로 작성
- benefits: 복리후생/혜택만 배열로 작성

**절대 금지:** description에 기술명(Node.js, JavaScript 등), 경력(5년 이상 등), 구체적 업무(API 개발, 데이터베이스 설계 등) 언급 금지

**올바른 예시:**
- description: "우리 회사는 혁신적인 서비스를 제공하는 성장기업입니다. 개발팀에서 백엔드 개발 업무를 담당하게 됩니다."
- requirements: ["Node.js 개발 경력 5년 이상", "데이터베이스 설계 경험"]

**잘못된 예시:**
- description: "Node.js를 활용한 백엔드 개발자를 찾습니다. 5년 이상의 경력과 데이터베이스 설계 경험이 필요합니다."

반드시 완전한 JSON만 응답하세요."""

        user_prompt = f"""
다음 요청을 바탕으로 채용공고를 생성하세요:

사용자 요청: {message}

추출된 정보:
- 기술 스택: {extracted_data.get('tech_stack', [])}
- 직무: {extracted_data.get('job_title', '')}
- 위치: {extracted_data.get('location', '')}
- 경력: {extracted_data.get('experience', '')}
- 인원: {extracted_data.get('team_size', '')}명
- 재택근무: {extracted_data.get('remote', False)}

완전한 채용공고 JSON을 생성하세요.
"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.openai_service.chat_completion(messages)
            job_posting = self._parse_json_response(response)

            if job_posting:
                # 추출된 데이터로 보완
                if not job_posting.get('tech_stack'):
                    job_posting['tech_stack'] = extracted_data.get('tech_stack', [])
                if not job_posting.get('team_size'):
                    job_posting['team_size'] = extracted_data.get('team_size', 1)

                # ✅ description을 고정된 깔끔한 회사 소개로 교체
                try:
                    job_posting['description'] = "우리 회사는 혁신적인 서비스를 제공하는 성장기업입니다. 개발팀에서 함께 성장할 동료를 찾고 있습니다."
                    logger.info("description을 고정값으로 교체 완료")
                except Exception as e:
                    logger.error(f"description 교체 중 오류: {e}")

                return job_posting
            else:
                # JSON 파싱 실패 시 기본 템플릿 사용
                return self._create_default_job_posting(extracted_data)

        except Exception as e:
            logger.error(f"LLM 채용공고 생성 실패: {str(e)}")
            return self._create_default_job_posting(extracted_data)

    def _create_default_job_posting(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 채용공고 템플릿"""
        tech_stack = extracted_data.get('tech_stack', [])
        job_title = extracted_data.get('job_title', '개발자')
        location = extracted_data.get('location', '서울')

        title = f"{' '.join(tech_stack[:2])} {job_title} 채용" if tech_stack else f"{job_title} 채용"

        # 급여 정보 설정
        salary_info = extracted_data.get('salary', '협의')
        if salary_info != '협의' and salary_info:
            # 급여가 "5000만원" 형식인 경우 숫자 추출
            import re
            salary_match = re.search(r'(\d+)만원', str(salary_info))
            if salary_match:
                salary_amount = int(salary_match.group(1))
                salary_dict = {
                    "min": salary_amount,
                    "max": salary_amount,
                    "currency": "KRW"
                }
            else:
                # 기본값
                salary_dict = {
                    "min": 3000,
                    "max": 6000,
                    "currency": "KRW"
                }
        else:
            # 기본값
            salary_dict = {
                "min": 3000,
                "max": 6000,
                "currency": "KRW"
            }

        return {
            "title": title,
            "company_name": "성장기업",
            "department": "개발팀",
            "position": job_title,
            "employment_type": "정규직",
            "experience_level": extracted_data.get('experience', '경력무관'),
            "location": location,
            "salary": salary_dict,
            "working_hours": "09:00-18:00",  # 근무 시간 기본값
            "contact_email": "",  # 연락처 이메일 빈 값
            "description": "우리 회사는 혁신적인 서비스를 제공하는 성장기업입니다. 개발팀에서 함께 성장할 동료를 찾고 있습니다.",
            "requirements": tech_stack[:3] if tech_stack else ["개발 경험"],
            "preferred_qualifications": ["팀워크", "커뮤니케이션 능력"],
            "benefits": ["재택근무 가능", "유연근무제", "교육비 지원"],
            "work_conditions": {
                "location": location,
                "remote": extracted_data.get('remote', False),
                "working_hours": "09:00-18:00"
            },
            "tech_stack": tech_stack,
            "team_size": extracted_data.get('team_size', 2),
            "application_deadline": "2024-12-31",
            "contact_info": {
                "email": "recruit@company.com",
                "phone": "02-1234-5678"
            }
        }

    async def _extract_job_info_enhanced(self, message: str) -> Dict[str, Any]:
        """향상된 채용공고 정보 추출"""
        logger.info("향상된 정보 추출 시작")

        try:
            # 기본 정보 추출
            extracted_data = self._extract_job_info(message)

            # LLM을 사용한 추가 정보 추출 (옵션)
            if self.openai_service:
                enhanced_data = await self._enhance_extraction_with_llm(message, extracted_data)
                extracted_data.update(enhanced_data)

            logger.info("정보 추출 완료")
            return {
                "status": "success",
                "extracted_data": extracted_data,
                "original_message": message
            }

        except Exception as e:
            logger.error(f"정보 추출 실패: {str(e)}")
            return {
                "status": "error",
                "message": f"정보 추출 실패: {str(e)}"
            }

    async def _enhance_extraction_with_llm(self, message: str, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM을 사용한 정보 추출 강화"""
        system_prompt = """당신은 채용공고 정보 추출 전문가입니다.

사용자의 메시지에서 다음 정보를 추출하여 JSON으로 응답하세요:
{
  "company_name": "회사명",
  "department": "부서명",
  "position_level": "junior/middle/senior",
  "employment_type": "정규직/계약직/인턴",
  "salary_min": 최소급여(숫자),
  "salary_max": 최대급여(숫자),
  "benefits": ["복리후생1", "복리후생2"],
  "deadline": "마감일",
  "interview_process": ["면접절차1", "면접절차2"]
}

정보가 없으면 null을 사용하세요."""

        user_prompt = f"""
다음 메시지에서 채용공고 정보를 추출하세요:

메시지: {message}

기본 추출 정보:
- 기술 스택: {base_data['tech_stack']}
- 직무: {base_data['job_title']}
- 위치: {base_data['location']}
- 경력: {base_data['experience']}

추가 정보를 JSON 형태로 추출하세요.
"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.openai_service.chat_completion(messages)
            enhanced_data = self._parse_json_response(response)

            return enhanced_data if enhanced_data else {}

        except Exception as e:
            logger.error(f"LLM 정보 추출 강화 실패: {str(e)}")
            return {}

    async def _generate_job_posting(self, message: str) -> Dict[str, Any]:
        """메인 작업: 채용공고 생성"""
        logger.info("채용공고 생성 시작")

        try:
            # 키워드 추출
            extracted_data = self._extract_job_info(message)

            # LLM을 사용한 채용공고 생성
            if self.openai_service:
                logger.info("openai_service 있음 - LLM 사용")
                job_posting = await self._generate_with_llm(message, extracted_data)
            else:
                logger.info("openai_service 없음 - fallback 사용")
                job_posting = self._generate_fallback(extracted_data)

            logger.info("채용공고 생성 완료")
            return {
                "status": "success",
                "job_posting": job_posting,
                "extracted_data": extracted_data
            }

        except Exception as e:
            logger.error(f"채용공고 생성 실패: {str(e)}")
            return {
                "status": "error",
                "message": f"채용공고 생성 실패: {str(e)}"
            }

    async def _search_internal_candidates(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """백그라운드 작업: 내부 DB 검색"""
        logger.info("내부 지원자 검색 시작 (백그라운드)")

        try:
            if not self.tool_executor:
                return {"status": "no_tool", "candidates": []}

            # 검색 조건 추출
            search_params = self._build_search_params(message)

            # MongoDB 검색 실행
            result = await self.tool_executor.execute_async(
                "mongodb",
                "find_documents",
                session_id=session_id,
                **search_params
            )

            if result.get("status") == "success":
                candidates = result.get("data", {}).get("documents", [])
                logger.info(f"내부 지원자 검색 완료: {len(candidates)}명 발견")
                return {
                    "status": "success",
                    "candidates": candidates,
                    "search_params": search_params
                }
            else:
                logger.info("내부 지원자 검색 결과 없음")
                return {"status": "no_results", "candidates": []}

        except Exception as e:
            logger.error(f"내부 지원자 검색 실패: {str(e)}")
            return {"status": "error", "message": str(e), "candidates": []}

    def _extract_job_info(self, message: str) -> Dict[str, Any]:
        """채용공고 정보 추출"""
        # 먼저 pick_chatbot의 extract_job_posting_info 함수 사용
        from backend.routers.pick_chatbot import extract_job_posting_info
        detailed_info = extract_job_posting_info(message)

        extracted = {
            "tech_stack": [],
            "job_title": "개발자",
            "location": "서울",
            "experience": detailed_info.get('experience'),
            "team_size": detailed_info.get('headcount', 0),  # 기본값 0명
            "headcount": detailed_info.get('headcount', 0),  # headcount 필드도 추가
            "remote": False,
            "salary": detailed_info.get('salary')
        }

        # 기술 스택 추출
        for tech, variants in self.tech_keywords.items():
            if any(variant in message.lower() for variant in variants):
                extracted["tech_stack"].append(tech)

        # 직무 추출
        for job in self.job_keywords:
            if job in message:
                extracted["job_title"] = job
                break

        # 위치 추출
        for location in self.location_keywords:
            if location in message:
                extracted["location"] = location
                break

        # 경력 추출
        experience_patterns = [
            r'(\d+)\s*년\s*(?:이상|이하|정도)?',
            r'신입',
            r'경력',
            r'시니어',
            r'주니어'
        ]
        for pattern in experience_patterns:
            match = re.search(pattern, message)
            if match:
                if pattern in ['신입', '경력', '시니어', '주니어']:
                    extracted["experience"] = pattern
                else:
                    extracted["experience"] = f"{match.group(1)}년"
                break

        # 팀 규모 추출
        team_match = re.search(r'(\d+)\s*명', message)
        if team_match:
            extracted["team_size"] = int(team_match.group(1))

        # 재택근무 체크
        remote_keywords = ["재택", "원격", "remote", "하이브리드"]
        extracted["remote"] = any(keyword in message for keyword in remote_keywords)

        return extracted

    def _format_salary_for_ui(self, salary_info):
        """급여 정보를 UI에 맞는 형식으로 변환"""
        if not salary_info:
            return "협의"

        if isinstance(salary_info, dict):
            # 딕셔너리 형태인 경우 (예: {"min": 5000, "max": 5000})
            min_salary = salary_info.get('min', 0)
            max_salary = salary_info.get('max', 0)

            # 원 단위를 만원 단위로 변환
            if min_salary > 10000:
                min_display = min_salary // 10000
                max_display = max_salary // 10000
            else:
                min_display = min_salary
                max_display = max_salary

            if min_display == max_display:
                return str(min_display)  # "5000" (만원 단위는 UI에서 자동 추가)
            else:
                return f"{min_display}~{max_display}"  # "3000~6000"

        elif isinstance(salary_info, str):
            # 문자열인 경우 (예: "5000만원", "협의")
            if "만원" in salary_info:
                # "5000만원" → "5000"으로 변환
                import re
                match = re.search(r'(\d+)만원', salary_info)
                if match:
                    return match.group(1)
            return salary_info

        return "협의"

    def _use_simple_company_description(self, job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """간단하고 깔끔한 회사 소개만 사용"""

        # 아예 고정된 깔끔한 회사 소개 사용
        job_posting['description'] = "우리 회사는 혁신적인 서비스를 제공하는 성장기업입니다. 개발팀에서 함께 성장할 동료를 찾고 있습니다."

        logger.info("고정된 깔끔한 회사 소개 사용")

        return job_posting

    async def _generate_with_llm(self, message: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM을 사용한 채용공고 생성"""

        system_prompt = """당신은 전문 채용공고 생성 AI입니다.

주어진 조건을 바탕으로 완성된 채용공고를 JSON 형태로 생성하세요.

반드시 다음 형식으로 응답하세요:
{
  "title": "제목",
  "description": "회사 소개와 일반적 업무 개요 (구체적 기술/경력/업무 내용 금지)",
  "main_duties": "구체적인 담당업무 내용 (기술명, 업무 세부사항 포함 가능)",
  "requirements": ["필수 요구사항1", "필수 요구사항2"],
  "preferred": ["우대사항1", "우대사항2"],
  "work_conditions": {
    "location": "위치",
    "type": "fulltime/parttime",
    "level": "junior/middle/senior",
    "remote": true/false
  },
  "tech_stack": ["기술1", "기술2"],
  "team_size": 숫자 또는 null,
  "salary_range": "급여 범위 (쉼표 없는 숫자만)" 또는 null
}

절대 가이드나 설명을 제공하지 말고, 오직 JSON 형태의 채용공고만 생성하세요."""

        user_prompt = f"""
다음 조건으로 채용공고를 생성해주세요:

사용자 요청: {message}

추출된 정보:
- 기술 스택: {extracted_data['tech_stack']}
- 직무: {extracted_data['job_title']}
- 위치: {extracted_data['location']}
- 경력: {extracted_data['experience']}
- 팀 규모: {extracted_data['team_size']}
- 재택근무: {extracted_data['remote']}

완성된 채용공고 JSON을 생성하세요.
"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = await self.openai_service.chat_completion(messages)

            # JSON 파싱 시도
            job_posting = self._parse_json_response(response)

            if job_posting:
                # ✅ 간단하고 깔끔한 회사 소개만 사용
                job_posting = self._use_simple_company_description(job_posting)
                return job_posting
            else:
                # JSON 파싱 실패 시 폴백
                return self._generate_fallback(extracted_data)

        except Exception as e:
            logger.error(f"LLM 채용공고 생성 실패: {str(e)}")
            return self._generate_fallback(extracted_data)

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """JSON 응답 파싱"""
        try:
            # 직접 JSON 파싱 시도
            return json.loads(response.strip())
        except:
            pass

        # JSON 블록 추출 시도
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except:
                    continue

        return None

    def _generate_fallback(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """폴백 채용공고 생성"""
        tech_stack = extracted_data["tech_stack"]
        job_title = extracted_data["job_title"]
        location = extracted_data["location"]

        # 기본 제목 생성
        if tech_stack:
            title = f"{'/'.join(tech_stack).title()} {job_title} 채용"
        else:
            title = f"{job_title} 채용"

        if extracted_data["team_size"]:
            title += f" ({extracted_data['team_size']}명)"

        # 고정된 깔끔한 회사 소개 사용
        description = "우리 회사는 혁신적인 서비스를 제공하는 성장기업입니다. 개발팀에서 함께 성장할 동료를 찾고 있습니다."

        # 요구사항 생성
        requirements = [f"{job_title} 경험"]
        if tech_stack:
            requirements.append(f"{'/'.join(tech_stack)} 숙련자")
        if extracted_data["experience"]:
            requirements.append(f"{extracted_data['experience']} 경력")

        return {
            "title": title,
            "description": description,
            "requirements": requirements,
            "preferred": ["프로젝트 경험", "팀워크 능력", "의사소통 능력"],
            "work_conditions": {
                "location": location,
                "type": "fulltime",
                "level": "middle",
                "remote": extracted_data["remote"]
            },
            "tech_stack": tech_stack,
            "team_size": extracted_data["team_size"],
            "salary_range": None
        }

    def _build_search_params(self, message: str) -> Dict[str, Any]:
        """MongoDB 검색 파라미터 구성"""
        extracted = self._extract_job_info(message)

        # 검색 쿼리 구성
        query = {}

        # 기술 스택 조건
        if extracted["tech_stack"]:
            query["skills"] = {"$in": extracted["tech_stack"]}

        # 위치 조건
        if extracted["location"] != "서울":  # 기본값이 아닌 경우만
            query["location"] = {"$regex": extracted["location"], "$options": "i"}

        # 경력 조건
        if extracted["experience"] and extracted["experience"].endswith("년"):
            try:
                years = int(extracted["experience"].replace("년", ""))
                query["experience_years"] = {"$gte": years}
            except:
                pass

        return {
            "collection": "applicants",  # 지원자 컬렉션
            "query": query,
            "limit": 5  # 최대 5명
        }

    def _combine_job_posting_results(self, job_posting_result: Dict[str, Any],
                                    candidate_result: Dict[str, Any]) -> Dict[str, Any]:
        """채용공고 생성 결과 결합"""

        # 메인 결과 (채용공고 생성)
        if isinstance(job_posting_result, Exception):
            return {
                "type": "error",
                "message": f"채용공고 생성 실패: {str(job_posting_result)}"
            }

        if job_posting_result.get("status") != "success":
            return {
                "type": "error",
                "message": job_posting_result.get("message", "채용공고 생성 실패")
            }

        job_posting = job_posting_result["job_posting"]

        result = {
            "type": "job_posting_preview",
            "message": "채용공고를 생성했습니다. 검토 후 등록하시겠습니까?",
            "job_posting": job_posting,
            "original_message": job_posting_result["original_message"],
            "candidate_recommendations": None,
            "background_status": "🔍 조건에 맞는 지원자 검색 중...",
            "preview_actions": {
                "confirm": {
                    "label": "등록하기",
                    "action": "register_job_posting",
                    "style": "primary"
                },
                "modify": {
                    "label": "수정하기",
                    "action": "modify_job_posting",
                    "style": "secondary"
                },
                "cancel": {
                    "label": "취소",
                    "action": "cancel_job_posting",
                    "style": "outline"
                }
            }
        }

        # 백그라운드 결과 (지원자 추천) 처리
        if (not isinstance(candidate_result, Exception) and
            candidate_result.get("status") == "success" and
            candidate_result.get("candidates")):

            candidates = candidate_result["candidates"]
            if candidates:
                result["candidate_recommendations"] = {
                    "count": len(candidates),
                    "candidates": candidates[:3],  # 최대 3명만 표시
                    "message": "💡 혹시 이런 지원자는 어떠세요?"
                }
                result["background_status"] = "✅ 지원자 검색 완료"
            else:
                result["background_status"] = "📭 조건에 맞는 지원자를 찾지 못했습니다"
        elif isinstance(candidate_result, Exception):
            result["background_status"] = "⚠️ 지원자 검색 중 오류 발생"
        else:
            # 검색 결과 없음 - 조용히 처리
            result["background_status"] = "🔍 검색 완료 (결과 없음)"

        return result

    async def register_job_posting(self, job_posting_data: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """채용공고를 PICK-TALK 직접 등록 API를 통해 등록"""
        logger.info("PICK-TALK 직접 등록 시작")
        print(f"🚀 [PICK-TALK 직접 등록] register_job_posting 호출됨")
        print(f"    📝 job_posting_data: {job_posting_data}")
        print(f"    🔧 tool_executor: {self.tool_executor}")

        try:
            import httpx

            # PICK-TALK 직접 등록 API 호출
            direct_registration_url = "http://localhost:8000/pick-chatbot/direct-register"
            debug_url = "http://localhost:8000/pick-chatbot/debug"

            print(f"🌐 [API 호출] PICK-TALK 직접 등록 API: {direct_registration_url}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"🔍 [DEBUG] 전달할 데이터 구조:")
                print(f"    데이터 타입: {type(job_posting_data)}")
                print(f"    데이터 내용: {job_posting_data}")

                # 먼저 디버그 API로 데이터 확인
                try:
                    debug_response = await client.post(
                        debug_url,
                        json=job_posting_data
                    )
                    print(f"🔍 [DEBUG API] 응답: {debug_response.status_code}")
                    if debug_response.status_code == 200:
                        debug_result = debug_response.json()
                        print(f"🔍 [DEBUG API] 결과: {debug_result}")
                except Exception as debug_e:
                    print(f"🔍 [DEBUG API] 오류: {debug_e}")

                # 실제 등록 API 호출
                response = await client.post(
                    direct_registration_url,
                    json=job_posting_data
                )

                print(f"📡 [API 응답] 상태 코드: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ [등록 성공] 응답: {result}")

                    if result.get("success"):
                        return {
                            "status": "success",
                            "job_posting_id": result.get("job_posting_id"),
                            "message": result.get("message", "채용공고가 성공적으로 등록되었습니다!")
                        }
                    else:
                        return {
                            "status": "error",
                            "message": result.get("message", "채용공고 등록에 실패했습니다.")
                        }
                else:
                    print(f"❌ [API 오류] HTTP {response.status_code}: {response.text}")
                    return {
                        "status": "error",
                        "message": f"등록 API 호출 실패: HTTP {response.status_code}"
                    }

        except httpx.RequestError as e:
            logger.error(f"PICK-TALK 직접 등록 API 호출 실패: {str(e)}")
            print(f"🌐 [네트워크 오류] API 호출 실패: {str(e)}")
            return {
                "status": "error",
                "message": f"등록 API 호출 중 네트워크 오류가 발생했습니다: {str(e)}"
            }
        except Exception as e:
            logger.error(f"PICK-TALK 직접 등록 실패: {str(e)}")
            print(f"💥 [예외 발생] {str(e)}")
            import traceback
            print(f"🔍 [스택 트레이스]: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": f"채용공고 등록 실패: {str(e)}"
            }

# 전역 인스턴스
parallel_agent = None

def get_parallel_agent(openai_service=None, tool_executor=None):
    """병렬 에이전트 인스턴스 반환"""
    global parallel_agent
    if parallel_agent is None:
        parallel_agent = ParallelJobPostingAgent(openai_service, tool_executor)
    return parallel_agent
