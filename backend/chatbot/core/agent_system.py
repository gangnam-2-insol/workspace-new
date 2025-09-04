"""
기본 Agent 시스템
사용자의 요청을 분석하고 적절한 도구를 자동으로 선택하여 처리합니다.
"""

import json
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from openai_service import OpenAIService
except ImportError:
    OpenAIService = None
import os

from dotenv import load_dotenv

from .context_classifier import (
    FlexibleContextClassifier,
    classify_context,
    is_recruitment_text,
)
from .enhanced_field_extractor import enhanced_extractor
from .two_stage_classifier import two_stage_classifier

load_dotenv()

# OpenAI 설정
try:
    openai_service = OpenAIService(model_name="gpt-4o") if OpenAIService else None
except Exception as e:
    openai_service = None

@dataclass
class AgentState:
    """Agent 시스템의 상태를 관리하는 데이터 클래스"""
    user_input: str
    conversation_history: List[Dict[str, str]] = None
    intent: str = ""
    tool_result: str = ""
    final_response: str = ""
    error: str = ""

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class IntentDetectionNode:
    """사용자 의도를 파악하는 노드"""

    def __init__(self):
        self.context_classifier = FlexibleContextClassifier()

        # 강력 키워드 (LangGraph 모드에서 무시)
        self.exclude_keywords = [
            "제출", "등록", "신청", "가입", "회원가입", "로그인", "결제", "구매", "주문"
        ]

        # 채용 관련 키워드
        self.recruitment_keywords = [
            "모집", "채용", "구인", "지원", "이력서", "자기소개서", "면접", "연봉", "급여",
            "개발자", "엔지니어", "디자이너", "매니저", "기획자", "분석가", "컨설턴트",
            "React", "Python", "Java", "JavaScript", "Node.js", "Django", "Spring", "AWS", "Docker",
            "경험", "능력", "자격", "우대", "환영", "찾고", "바랍니다", "서류", "접수"
        ]

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        mode = state.get("mode", "chat")

        print(f"\n🎯 [의도 감지 시작] 모드: {mode}")
        print(f"🎯 [의도 감지] 사용자 입력: {user_input}")

        # LangGraph 모드에서 강력 키워드 무시
        if mode == "langgraph":
            print(f"🎯 [의도 감지] LangGraph 모드 - 강력 키워드 무시")

            # 2단계 분류 시스템 사용
            classification_result = two_stage_classifier.classify_text(user_input)

            if classification_result['is_recruitment']:
                intent = "recruit"
                confidence = classification_result['confidence']
                extracted_fields = classification_result['fields']
                print(f"🎯 [의도 감지] 2단계 분류 결과: 채용공고 (신뢰도: {confidence})")
            else:
                # 보강: 규칙/사전 기반 향상 추출기로 재확인
                try:
                    print(f"🔁 [보강] 의미 기반 분류가 채용이 아님 → 규칙 기반 필드 추출 시도")
                    extracted_fields_fallback = enhanced_extractor.extract_fields_enhanced(user_input)
                    # 실제 값이 있는 필드만 카운트
                    valid_fields = {k: v for k, v in extracted_fields_fallback.items()
                                  if v is not None and v != "" and v != "null"}
                    if valid_fields:
                        intent = "recruit"
                        confidence = max(classification_result.get('confidence', 0.5), 0.6)
                        extracted_fields = extracted_fields_fallback
                        print(f"🎯 [보강] 규칙 기반 추출로 채용공고 판정 (필드 {len(extracted_fields)}개)")
                    else:
                        intent = "chat"
                        confidence = 0.8
                        extracted_fields = {}
                        print(f"🎯 [의도 감지] 2단계 분류 결과: 일반 대화")
                except Exception as _e:
                    intent = "chat"
                    confidence = 0.8
                    extracted_fields = {}
                    print(f"⚠️ [보강 실패] 규칙 기반 추출 중 오류: {_e}")

        else:
            # 일반 모드에서는 기존 로직 사용
            print(f"🎯 [의도 감지] 일반 모드 - 기존 로직 사용")

            # 기존 컨텍스트 분류기 사용
            context_result = self.context_classifier.classify_context(user_input)
            context_score = context_result.total_score
            context_confidence = context_result.confidence

            print(f"🎯 [의도 감지] 컨텍스트 분류 결과: 점수={context_score}, 신뢰도={context_confidence}")

            # 의도 결정
            if context_confidence >= 0.5 and context_score >= 5:
                intent = "recruit"
                confidence = context_confidence
                print(f"🎯 [의도 감지] 컨텍스트 분류로 채용공고 판정")
            else:
                intent = "chat"
                confidence = 0.8
                print(f"🎯 [의도 감지] 일반 대화로 판정")

            extracted_fields = {}

        print(f"🎯 [의도 감지 완료] 최종 의도: {intent}, 신뢰도: {confidence}")

        return {
            "intent": intent,
            "confidence": confidence,
            "extracted_fields": extracted_fields
        }

class WebSearchNode:
    """웹 검색 도구 노드"""

    def process_search(self, search_query: str) -> str:
        try:
            # 시뮬레이션된 검색 결과 제공
            if "개발" in search_query or "프로그래밍" in search_query:
                result = """🔍 최신 개발 트렌드:

📱 프론트엔드:
• React 18의 새로운 기능 (Concurrent Features, Suspense)
• TypeScript 5.0 업데이트 및 개선사항
• Next.js 14의 App Router와 Server Components
• Vue 3의 Composition API 활용

⚙️ 백엔드:
• Node.js 20의 새로운 기능
• Python 3.12의 성능 개선
• Go 1.21의 병렬 처리 개선
• Rust의 메모리 안전성

🤖 AI/ML:
• AI 기반 코드 생성 도구 (GitHub Copilot, Cursor)
• 머신러닝 모델 최적화 기술
• 자연어 처리 발전

☁️ 클라우드/DevOps:
• Kubernetes 1.28의 새로운 기능
• Docker Desktop 개선사항
• 클라우드 네이티브 개발 패턴
• 마이크로서비스 아키텍처

💡 개발 도구:
• VS Code의 새로운 확장 기능
• Git 최신 기능과 워크플로우
• CI/CD 파이프라인 자동화"""

            elif "채용" in search_query or "구인" in search_query:
                result = """💼 2024년 IT 업계 채용 동향:

📊 시장 현황:
• IT 업계 전체적으로 안정적인 채용 시장 유지
• AI/ML 분야 인력 수요 급증
• 풀스택 개발자 선호도 증가
• 원격 근무 환경 적응력 중요성 부각

🎯 인기 직종:
• AI/ML 엔지니어 (연봉 5,000만원~8,000만원)
• 풀스택 개발자 (연봉 4,000만원~7,000만원)
• DevOps 엔지니어 (연봉 4,500만원~7,500만원)
• 데이터 엔지니어 (연봉 4,000만원~6,500만원)

💡 채용 트렌드:
• 포트폴리오 중심 평가 증가
• 기술 면접 비중 확대
• 문화적 적합성 평가 강화
• 유연한 근무 환경 제공

📈 급여 동향:
• 신입 개발자: 연봉 3,000만원~4,000만원
• 경력 3-5년: 연봉 4,000만원~6,000만원
• 경력 5년 이상: 연봉 5,000만원~8,000만원"""

            elif "기술" in search_query or "기술스택" in search_query:
                result = """🛠️ 2024년 인기 기술 스택:

🌐 프론트엔드:
• React.js (가장 인기)
• Next.js (SSR/SSG)
• Vue.js (점진적 채택)
• TypeScript (타입 안전성)

⚙️ 백엔드:
• Node.js (JavaScript 풀스택)
• Python (Django, FastAPI)
• Java (Spring Boot)
• Go (고성능 서버)

🗄️ 데이터베이스:
• PostgreSQL (관계형)
• MongoDB (NoSQL)
• Redis (캐싱)
• Elasticsearch (검색)

☁️ 클라우드:
• AWS (가장 널리 사용)
• Google Cloud Platform
• Microsoft Azure
• Kubernetes (컨테이너 오케스트레이션)

🤖 AI/ML:
• TensorFlow
• PyTorch
• OpenAI API
• Google Gemini API

📱 모바일:
• React Native
• Flutter
• Swift (iOS)
• Kotlin (Android)"""

            else:
                result = f"""🔍 검색 결과: {search_query}

📚 일반적인 정보:
• 다양한 온라인 리소스에서 관련 정보를 찾을 수 있습니다
• 전문 포럼과 커뮤니티에서 최신 정보를 확인하세요
• 공식 문서와 튜토리얼을 참고하는 것을 권장합니다

💡 추가 검색 팁:
• 구체적인 키워드를 사용하세요
• 최신 정보를 위해 날짜 필터를 활용하세요
• 신뢰할 수 있는 소스를 확인하세요"""

            return result

        except Exception as e:
            print(f"웹 검색 중 오류: {str(e)}")
            return "죄송합니다. 검색 중 오류가 발생했습니다."

class CalculatorNode:
    """계산 도구 노드"""

    def process_calculation(self, user_input: str) -> str:
        try:
            user_input = user_input.lower()

            # 수식 계산
            if any(op in user_input for op in ['+', '-', '*', '/', '=']):
                # 수식 추출
                expression = re.findall(r'[\d\+\-\*\/\(\)\.]+', user_input)
                if expression:
                    try:
                        # 안전한 수식 계산
                        expr = ''.join(expression)
                        # 위험한 함수 제거
                        expr = re.sub(r'[^0-9\+\-\*\/\(\)\.]', '', expr)
                        result = eval(expr)
                        return f"🧮 계산 결과: {expr} = {result}"
                    except:
                        return "수식 계산 중 오류가 발생했습니다."
                else:
                    return "계산할 수식을 찾을 수 없습니다."

            # 연봉 관련 계산
            elif "연봉" in user_input or "월급" in user_input:
                # 연봉에서 월급 계산
                salary_match = re.search(r'(\d+)만원', user_input)
                if salary_match:
                    annual_salary = int(salary_match.group(1))
                    monthly_salary = annual_salary / 12

                    # 4대보험 공제 (약 10%)
                    net_monthly = monthly_salary * 0.9

                    result = f"""💰 연봉 {annual_salary:,}만원의 월급 계산:

📊 기본 정보:
• 연봉: {annual_salary:,}만원
• 월급: {monthly_salary:,.0f}만원

💸 공제 후 실수령액:
• 4대보험 공제 (약 10%): {monthly_salary * 0.1:,.0f}만원
• 실수령액: {net_monthly:,.0f}만원

💡 참고사항:
• 정확한 공제액은 개인 상황에 따라 다를 수 있습니다
• 퇴직연금, 각종 수당 등이 추가될 수 있습니다
• 세금 계산은 연말정산 시 정확히 계산됩니다"""

                    return result
                else:
                    return "연봉 정보를 찾을 수 없습니다. '연봉 4000만원'과 같이 입력해주세요."

            # 퍼센트 계산
            elif "%" in user_input or "퍼센트" in user_input:
                percent_match = re.search(r'(\d+)%', user_input)
                number_match = re.search(r'(\d+)', user_input)

                if percent_match and number_match:
                    percent = int(percent_match.group(1))
                    number = int(number_match.group(1))
                    result_value = number * percent / 100

                    return f"🧮 퍼센트 계산: {number}의 {percent}% = {result_value}"
                else:
                    return "퍼센트 계산을 위한 정보가 부족합니다."

            else:
                return "계산할 수 있는 내용을 찾을 수 없습니다. 수식, 연봉, 퍼센트 등을 입력해주세요."

        except Exception as e:
            print(f"계산 중 오류: {str(e)}")
            return "죄송합니다. 계산 중 오류가 발생했습니다."

class RecruitmentNode:
    """채용공고 작성 도구 노드"""

    def process_recruitment(self, user_input: str) -> str:
        try:
            # Gemini AI를 사용하여 채용공고 내용 생성
            prompt = f"""
당신은 전문적인 채용공고 작성 전문가입니다.
사용자의 요청을 바탕으로 체계적이고 매력적인 채용공고를 작성해주세요.

사용자 요청: {user_input}

다음 형식으로 채용공고를 작성해주세요:

## 📋 채용공고

### 🏢 회사 정보
- 회사명: [추정 또는 제안]
- 위치: [지역 정보]
- 업종: [업종 정보]

### 💼 모집 직무
- 직무명: [직무명]
- 모집인원: [인원수]
- 경력요건: [경력 요구사항]

### 📝 주요업무
• [구체적인 업무 내용]
• [업무 범위]
• [담당 영역]

### 🎯 자격요건
• [필수 자격요건]
• [기술 스택]
• [경험 요구사항]

### 🌟 우대조건
• [우대사항]
• [추가 스킬]
• [관련 경험]

### 💰 복리후생
• [급여 정보]
• [복리후생]
• [근무환경]

### 📞 지원방법
• [지원 방법]
• [문의처]
• [마감일]

답변은 한국어로 작성하고, 이모지를 적절히 사용하여 가독성을 높여주세요.
"""

            if openai_service:
                try:
                    # 새로운 이벤트 루프 생성하여 사용
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(openai_service.generate_response(prompt))
                        return response
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"AI 호출 중 오류: {e}")
                    return "죄송합니다. AI 서비스 호출 중 오류가 발생했습니다."
            else:
                return "죄송합니다. AI 서비스를 사용할 수 없습니다."

        except Exception as e:
            print(f"채용공고 작성 중 오류: {str(e)}")
            return "죄송합니다. 채용공고 작성 중 오류가 발생했습니다."

class DatabaseQueryNode:
    """데이터베이스 조회 도구 노드"""

    def process_db_query(self, user_input: str) -> str:
        try:
            user_input = user_input.lower()

            # 시뮬레이션된 DB 조회 결과 제공
            if "채용공고" in user_input or "구인" in user_input:
                result = """📋 저장된 채용공고 목록:

1. 🏢 ABC테크 - 프론트엔드 개발자
   • 위치: 서울 강남구
   • 연봉: 4,000만원 ~ 6,000만원
   • 경력: 2년 이상
   • 상태: 모집중
   • 등록일: 2024-08-01

2. 🏢 XYZ소프트 - 백엔드 개발자
   • 위치: 인천 연수구
   • 연봉: 3,500만원 ~ 5,500만원
   • 경력: 1년 이상
   • 상태: 모집중
   • 등록일: 2024-07-28

3. 🏢 DEF시스템 - 풀스택 개발자
   • 위치: 부산 해운대구
   • 연봉: 4,500만원 ~ 7,000만원
   • 경력: 3년 이상
   • 상태: 모집중
   • 등록일: 2024-07-25

4. 🏢 GHI솔루션 - AI/ML 엔지니어
   • 위치: 대전 유성구
   • 연봉: 5,000만원 ~ 8,000만원
   • 경력: 2년 이상
   • 상태: 모집중
   • 등록일: 2024-07-20

5. 🏢 JKL스타트업 - DevOps 엔지니어
   • 위치: 서울 마포구
   • 연봉: 4,200만원 ~ 6,500만원
   • 경력: 1년 이상
   • 상태: 모집중
   • 등록일: 2024-07-15

📊 통계:
• 총 등록 공고: 5개
• 평균 연봉: 4,220만원
• 가장 인기 지역: 서울 (2개)
• 가장 인기 직종: 개발자 (3개)"""

            elif "이력서" in user_input or "지원자" in user_input:
                result = """📄 저장된 이력서 목록:

1. 👤 김철수 - 프론트엔드 개발자
   • 경력: 3년
   • 기술스택: React, TypeScript, Node.js
   • 지원일: 2024-08-01
   • 상태: 검토중

2. 👤 이영희 - 백엔드 개발자
   • 경력: 2년
   • 기술스택: Java, Spring, MySQL
   • 지원일: 2024-07-30
   • 상태: 검토중

3. 👤 박민수 - 풀스택 개발자
   • 경력: 4년
   • 기술스택: Python, Django, React
   • 지원일: 2024-07-28
   • 상태: 서류통과

4. 👤 정수진 - AI/ML 엔지니어
   • 경력: 2년
   • 기술스택: Python, TensorFlow, PyTorch
   • 지원일: 2024-07-25
   • 상태: 검토중

5. 👤 최동현 - DevOps 엔지니어
   • 경력: 3년
   • 기술스택: Docker, Kubernetes, AWS
   • 지원일: 2024-07-20
   • 상태: 서류통과

📊 통계:
• 총 지원자: 5명
• 평균 경력: 2.8년
• 가장 인기 기술: Python (3명)
• 서류통과율: 40%"""

            elif "면접" in user_input or "일정" in user_input:
                result = """📅 면접 일정:

1. 🗓️ 2024-08-05 (월) 14:00
   • 지원자: 김철수
   • 직종: 프론트엔드 개발자
   • 면접관: 3명
   • 장소: 1층 면접실

2. 🗓️ 2024-08-06 (화) 10:00
   • 지원자: 이영희
   • 직종: 백엔드 개발자
   • 면접관: 2명
   • 장소: 2층 면접실

3. 🗓️ 2024-08-07 (수) 15:00
   • 지원자: 박민수
   • 직종: 풀스택 개발자
   • 면접관: 3명
   • 장소: 1층 면접실

4. 🗓️ 2024-08-08 (목) 11:00
   • 지원자: 정수진
   • 직종: AI/ML 엔지니어
   • 면접관: 2명
   • 장소: 2층 면접실

📊 통계:
• 총 면접: 4건
• 평균 면접 시간: 1시간
• 면접관 수: 평균 2.5명"""

            else:
                result = f"""📋 데이터베이스 조회 결과: {user_input}

🔍 조회 가능한 데이터:
• 채용공고 목록
• 지원자 이력서
• 면접 일정
• 통계 정보

💡 구체적인 키워드를 사용해주세요:
• "채용공고 보여줘"
• "이력서 목록"
• "면접 일정" """

            return result

        except Exception as e:
            print(f"DB 조회 중 오류: {str(e)}")
            return "죄송합니다. 데이터베이스 조회 중 오류가 발생했습니다."

class FallbackNode:
    """일반 대화 처리 노드"""

    def __init__(self):
        self.system_prompt = """
당신은 친근하고 도움이 되는 AI 어시스턴트입니다.
채용 관련 질문이면 전문적인 조언을 제공하고,
일반적인 질문이면 친근하게 답변해주세요.

답변은 한국어로 하고, 이모지를 적절히 사용하여 친근하게 만들어주세요.
"""

    def process_chat(self, user_input: str) -> str:
        try:
            user_input = user_input.lower()

            # 채용 관련 질문인지 확인 (더 포괄적인 키워드 추가)
            recruitment_keywords = [
                '채용', '구인', '면접', '이력서', '연봉', '급여', '직장', '취업',
                '지원자', '신입', '경력', '직무', '업무', '근무', '근무지', '서류',
                '자기소개서', '자격증', '복리후생', '교육', '성장', '적응', '우대',
                '협의', '마감일', '문의처', '지원방법', '제출', '등록', '작성'
            ]
            is_recruitment_related = any(keyword in user_input for keyword in recruitment_keywords)

            if is_recruitment_related:
                # 채용 관련 전문적인 답변
                if "면접" in user_input:
                    result = """💼 면접 준비 가이드:

🎯 면접 전 준비사항:
• 회사 정보 철저히 조사
• 자기소개서 내용 숙지
• 포트폴리오 준비
• 적절한 복장 선택

🗣️ 면접 중 팁:
• 자신감 있게 대답
• 구체적인 경험 언급
• 질문이 명확하지 않으면 재질문
• 솔직하게 답변

📝 면접 후:
• 감사 인사 메일 발송
• 면접 내용 정리
• 개선점 파악

💡 추가 조언:
• 기술 면접은 코딩 테스트 준비
• 행동 면접은 STAR 기법 활용
• 문화적 적합성도 중요"""

                elif "이력서" in user_input:
                    result = """📄 이력서 작성 가이드:

📋 기본 구성:
• 개인정보
• 학력사항
• 경력사항
• 기술스택
• 프로젝트 경험
• 자격증/수상내역

✨ 작성 팁:
• 구체적인 성과 중심으로 작성
• 숫자와 데이터 활용
• 간결하고 명확하게
• 맞춤형 이력서 작성

🎨 디자인:
• 깔끔하고 읽기 쉽게
• 일관된 폰트 사용
• 적절한 여백
• PDF 형식 권장

💡 주의사항:
• 오타 철저히 점검
• 최신 정보로 업데이트
• 지원 직무에 맞게 수정
• 거짓 정보 금지"""

                elif "연봉" in user_input or "급여" in user_input:
                    result = """💰 연봉 협상 가이드:

📊 시장 조사:
• 동종업계 평균 연봉 확인
• 경력별 급여 수준 파악
• 지역별 차이 고려
• 회사 규모별 차이

💼 협상 전략:
• 자신의 가치 명확히 파악
• 구체적인 성과 제시
• 적절한 시기 선택
• 대안 준비

🗣️ 협상 팁:
• 자신감 있게 대화
• 구체적인 금액 제시
• 유연한 태도 유지
• 상호 이익 고려

💡 추가 고려사항:
• 복리후생 포함 여부
• 성과급/인센티브
• 연봉 인상 가능성
• 근무 환경과의 균형"""

                elif "서류" in user_input or "제출" in user_input or "지원방법" in user_input:
                    result = """📋 지원 서류 및 방법 가이드:

📄 필수 제출 서류:
• 이력서 (최신 정보로 업데이트)
• 자기소개서 (지원 동기 및 포부)
• 관련 자격증 사본
• 포트폴리오 (해당 직무의 경우)

📝 서류 작성 팁:
• 구체적인 성과 중심으로 작성
• 지원 직무와 연관성 강조
• 간결하고 명확하게
• 오타 및 문법 오류 점검

📤 제출 방법:
• 온라인 지원 시스템
• 이메일 제출
• 직접 방문 제출
• 우편 제출

💡 주의사항:
• 제출 기한 준수
• 요구사항 정확히 확인
• 백업 파일 보관
• 제출 확인 메일 확인

🤝 추가 문의사항이 있으시면 언제든 말씀해주세요!"""

                else:
                    result = """💼 채용 관련 도움말:

🎯 주요 서비스:
• 채용공고 등록 및 관리
• 이력서 분석 및 평가

• 지원자 추천

📋 채용 프로세스:
1. 채용공고 작성
2. 지원자 모집
3. 서류 전형
4. 면접 진행
5. 최종 합격자 선정

💡 효율적인 채용을 위한 팁:
• 명확한 직무 설명
• 적절한 자격 요건
• 투명한 급여 정보
• 빠른 피드백

🤝 추가 도움이 필요하시면 언제든 말씀해주세요!"""

            else:
                # 일반 대화: 하드코딩된 고정 멘트 대신 LLM으로 자연스러운 답변 생성
                try:
                    prompt = (
                        "당신은 HireMe의 한국어 AI 비서입니다.\n"
                        "사용자의 일상 대화에도 자연스럽고 간결하게 응답하세요.\n"
                        "지나친 이모지/홍보/반복 멘트(예: 추가 질문 안내)는 피하고, 질문 의도가 모호하면 한 문장으로 되물어보세요.\n"
                        f"사용자: {user_input}\n"
                        "어시스턴트:"
                    )
                    if openai_service:
                        try:
                            # 새로운 이벤트 루프 생성하여 사용
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                response = loop.run_until_complete(openai_service.generate_response(prompt))
                                result = response or "네, 알겠습니다. 더 구체적으로 말씀해 주실 수 있을까요?"
                            finally:
                                loop.close()
                        except Exception as e:
                            print(f"AI 호출 중 오류: {e}")
                            result = "네, 알겠습니다. 더 구체적으로 말씀해 주실 수 있을까요?"
                    else:
                        result = "네, 알겠습니다. 더 구체적으로 말씀해 주실 수 있을까요?"
                except Exception:
                    result = "네, 알겠습니다. 더 구체적으로 말씀해 주실 수 있을까요?"

            return result

        except Exception as e:
            print(f"대화 처리 중 오류: {str(e)}")
            return "죄송합니다. 대화 처리 중 오류가 발생했습니다."

class ResponseFormatterNode:
    """응답 포매터 노드"""

    def format_response(self, tool_result: str, intent: str, error: str = "") -> str:
        try:
            if error:
                # 오류가 있는 경우
                return f"❌ 오류가 발생했습니다: {error}\n\n💡 다시 시도해보시거나 다른 질문을 해주세요."
            else:
                # 정상적인 응답
                # 도구별 추가 메시지
                if intent == "search":
                    additional_msg = "\n\n💡 더 구체적인 정보가 필요하시면 말씀해주세요!"
                elif intent == "calc":
                    additional_msg = "\n\n🧮 다른 계산이 필요하시면 언제든 말씀해주세요!"
                elif intent == "recruit":
                    additional_msg = "\n\n📝 채용공고 수정이나 추가 요청이 있으시면 말씀해주세요!"
                elif intent == "db":
                    additional_msg = "\n\n📋 다른 데이터 조회가 필요하시면 말씀해주세요!"
                else:  # chat은 꼬리 문구를 붙이지 않음 (반복 멘트 방지)
                    additional_msg = ""

                return f"{tool_result}{additional_msg}"

        except Exception as e:
            return f"❌ 응답 포맷팅 중 오류가 발생했습니다: {str(e)}"

class AgentSystem:
    """기본 Agent 시스템"""

    def __init__(self):
        self.intent_detector = IntentDetectionNode()
        self.web_search = WebSearchNode()
        self.calculator = CalculatorNode()
        self.recruitment = RecruitmentNode()
        self.db_query = DatabaseQueryNode()
        self.fallback = FallbackNode()
        self.formatter = ResponseFormatterNode()

    def process_request(self, user_input: str, conversation_history: List[Dict[str, str]] = None, session_id: str = None, mode: str = "chat") -> Dict[str, Any]:
        """사용자 요청을 처리하고 결과를 반환합니다."""
        try:
            # 1단계: 의도 분류
            intent_result = self.intent_detector.run({"user_input": user_input, "mode": mode})
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            extracted_fields = intent_result["extracted_fields"]

            # 2단계: DOM 액션 의도 감지
            print("\n" + "="*50)
            print("🔍 [DOM 액션 감지 디버깅]")
            print("="*50)

            from langgraph_config import is_dom_action_intent

            # 입력 전처리
            text = user_input.lower()
            print(f"\n1️⃣ 입력 전처리:")
            print(f"  원본: {user_input}")
            print(f"  전처리: {text}")

            # 액션 키워드 체크
            click_words = ["클릭", "선택", "누르", "체크"]
            view_words = ["보여줘", "보기", "확인", "조회", "열람"]
            has_click = any(w in text for w in click_words)
            has_view = any(w in text for w in view_words)

            print(f"\n2️⃣ 키워드 체크:")
            print(f"  클릭 키워드: {[w for w in click_words if w in text]}")
            print(f"  보기 키워드: {[w for w in view_words if w in text]}")
            print(f"  클릭 감지: {'✅' if has_click else '❌'}")
            print(f"  보기 감지: {'✅' if has_view else '❌'}")

            # 대상 추출 시도
            print(f"\n3️⃣ 대상 추출:")
            name_match = re.search(r'([가-힣]{2,4})\s*(지원자|님|의|을|를|에게)?', text)
            doc_match = re.search(r'(자소서|이력서|포트폴리오|분석\s*결과|상세\s*정보)', text)

            target = None
            if name_match:
                target = name_match.group(1)
                print(f"  이름 패턴 매칭: ✅ -> {target}")
            else:
                print("  이름 패턴 매칭: ❌")

            if doc_match:
                target = doc_match.group(1).strip()
                print(f"  문서 패턴 매칭: ✅ -> {target}")
            else:
                print("  문서 패턴 매칭: ❌")

            # DOM 액션 판정
            is_dom_action = is_dom_action_intent(user_input)
            print(f"\n4️⃣ 최종 판정:")
            print(f"  is_dom_action_intent: {'✅' if is_dom_action else '❌'}")
            print(f"  has_click/view: {'✅' if (has_click or has_view) else '❌'}")
            print(f"  추출된 대상: {target or '없음'}")
            print("="*50 + "\n")

            # 3단계: 도구 선택 및 실행
            tool_result = ""
            error = ""

            if is_dom_action or has_click or has_view:
                # DOM 액션 처리
                print("🎯 [DOM] 액션 감지됨!")
                intent = "dom_action"
                action_type = "click" if has_click else "view" if has_view else "input"
                dom_target = (target or user_input).strip()

                # 프론트 표준 포맷(react_agent_response)으로 응답
                payload = {
                    "success": True,
                    "response": f"DOM 액션 '{action_type}'을(를) 실행합니다.",
                    "type": "react_agent_response",
                    "page_action": {
                        "action": "dom",
                        "dom_action": "click" if action_type == "click" else ("view" if action_type == "view" else "typeText"),
                        "args": {"query": dom_target}
                    }
                }
                print(f"🎯 [DOM] 응답 생성: {payload}")
                tool_result = json.dumps(payload, ensure_ascii=False)
            elif intent == "search":
                tool_result = self.web_search.process_search(user_input)
            elif intent == "calc":
                tool_result = self.calculator.process_calculation(user_input)
            elif intent == "recruit":
                tool_result = self.recruitment.process_recruitment(user_input)
            elif intent == "db":
                tool_result = self.db_query.process_db_query(user_input)
            else:  # chat
                tool_result = self.fallback.process_chat(user_input)

            # 3단계: 응답 포맷팅
            final_response = self.formatter.format_response(tool_result, intent, error)

            # 4단계: 채용공고 관련 필드 추출 보강 (채용 의도일 때만)
            if not extracted_fields and intent == "recruit":
                try:
                    fallback_fields = enhanced_extractor.extract_fields_enhanced(user_input)
                    if fallback_fields:
                        extracted_fields = fallback_fields
                except Exception:
                    pass

            return {
                "success": True,
                "response": final_response,
                "intent": intent,
                "error": error,
                "session_id": session_id,
                "extracted_fields": extracted_fields  # 추출된 필드 정보 추가
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"죄송합니다. 요청 처리 중 오류가 발생했습니다: {str(e)}",
                "intent": "error",
                "error": str(e),
                "extracted_fields": {}
            }

    def _extract_job_posting_fields(self, user_input: str) -> Dict[str, Any]:
        """향상된 필드 추출 (AI + 사전 + 규칙 결합)"""
        try:
            print(f"\n🎯 [필드 추출 시작] 사용자 입력: {user_input}")

            # 향상된 필드 추출기 사용
            extracted_fields = enhanced_extractor.extract_fields_enhanced(user_input)

            print(f"\n🎯 [필드 추출 완료] 최종 결과:")
            print(f"🎯 [필드 추출 완료] 추출된 필드 개수: {len(extracted_fields)}개")
            for key, value in extracted_fields.items():
                print(f"🎯 [필드 추출 완료] {key}: {value}")

            if not extracted_fields:
                print(f"⚠️ [필드 추출 완료] 추출된 필드가 없습니다!")

            return extracted_fields

        except Exception as e:
            print(f"❌ [필드 추출 오류] {e}")
            return {}

# 전역 Agent 시스템 인스턴스
agent_system = AgentSystem()
