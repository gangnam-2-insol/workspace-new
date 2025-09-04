"""
동적 메시지 생성기
사용자의 상황과 맥락에 따라 자연스러운 메시지를 생성합니다.
"""

import random
from datetime import datetime
from typing import Any, Dict, List, Optional


class DynamicMessageGenerator:
    """동적 메시지 생성기 클래스"""

    def __init__(self):
        # 기본 인사말 템플릿
        self.greeting_templates = [
            "안녕하세요! 오늘은 어떤 도움이 필요하신가요? 😊",
            "반갑습니다! 무엇을 도와드릴까요? ✨",
            "안녕하세요! 어떤 일을 진행하고 계신가요? 🚀",
            "반갑습니다! 오늘은 어떤 작업을 도와드릴까요? 💫"
        ]

        # 맥락별 메시지 템플릿
        self.context_templates = {
            "job_posting": {
                "title": [
                    "좋은 제목이네요! 이제 어떤 부서에서 일하게 될지 알려주세요 😊",
                    "멋진 포지션이에요! 부서는 어디로 생각하고 계신가요? 🎯",
                    "제목이 명확하네요! 다음으로 부서를 선택해주세요 ✨"
                ],
                "department": [
                    "개발팀이시군요! 경력은 어느 정도로 찾고 계신가요? 🚀",
                    "좋은 부서예요! 지원자 경력은 어떻게 생각하고 계신가요? 💼",
                    "개발팀이네요! 경력 요건을 알려주세요 🎯"
                ],
                "experience": [
                    "3년 경력이시군요! 급여는 어떻게 생각하고 계신가요? 💰",
                    "적절한 경력이에요! 급여 범위는 어느 정도로 생각하고 계신가요? 💵",
                    "좋은 경력이네요! 이제 급여 조건을 정해보세요 💎"
                ],
                "salary": [
                    "근무지는 어디로 생각하고 계시나요? 서울, 부산 등 지역을 알려주세요 🌍",
                    "급여가 명확하네요! 근무지는 어디인가요? 🏢",
                    "좋은 조건이에요! 마지막으로 근무지를 알려주세요 📍"
                ],
                "location": [
                    "완벽해요! 채용공고가 완성되었습니다. 수정할 부분이 있으시거나 바로 등록하시겠어요? ✨",
                    "훌륭해요! 모든 정보가 입력되었습니다. 검토 후 등록하시겠어요? 🎉",
                    "완성되었어요! 채용공고를 등록하시겠어요? 🚀"
                ]
            },
            "resume_analysis": {
                "upload": [
                    "이력서를 업로드해주세요! 분석해드리겠습니다 📄",
                    "이력서 파일을 선택해주세요. 상세한 분석을 제공해드릴게요 📋",
                    "이력서를 올려주시면 전문적으로 분석해드리겠습니다 🔍"
                ],
                "analyzing": [
                    "이력서를 분석하고 있어요! 잠시만 기다려주세요 ⏳",
                    "분석 중입니다. 곧 결과를 보여드릴게요 🔍",
                    "이력서를 꼼꼼히 살펴보고 있어요. 조금만 기다려주세요 📊"
                ],
                "complete": [
                    "분석이 완료되었어요! 결과를 확인해보세요 📊",
                    "이력서 분석이 끝났습니다. 어떤 부분이 궁금하신가요? 💡",
                    "분석 결과가 나왔어요! 추가로 궁금한 점이 있으시면 말씀해주세요 ✨"
                ]
            },
            "applicant_management": {
                "list": [
                    "지원자 목록을 보여드릴게요! 어떤 기준으로 정렬하시겠어요? 👥",
                    "지원자들을 확인해보세요. 필터링이나 검색이 필요하시면 말씀해주세요 🔍",
                    "지원자 목록입니다. 특정 조건으로 찾고 계신가요? 📋"
                ],
                "evaluation": [
                    "지원자 평가를 진행하시는군요! 어떤 기준으로 평가하시겠어요? ⭐",
                    "평가 작업을 도와드릴게요. 평가 기준을 설정해주세요 📊",
                    "지원자 평가를 시작해보세요! 어떤 항목부터 시작할까요? 🎯"
                ]
            }
        }

        # 감정/톤별 응답
        self.tone_templates = {
            "formal": {
                "greeting": "안녕하세요. 무엇을 도와드릴까요?",
                "thanks": "도움이 되어 기쁩니다. 추가 문의사항이 있으시면 언제든 말씀해주세요."
            },
            "casual": {
                "greeting": "안녕! 뭐 도와줄까? 😊",
                "thanks": "도움이 되었다니 다행이야! 또 궁금한 게 있으면 언제든 말해줘 ✨"
            },
            "friendly": {
                "greeting": "안녕하세요! 오늘은 어떤 도움이 필요하신가요? 😊",
                "thanks": "도움이 되어서 기뻐요! 추가로 궁금한 점이 있으시면 언제든 말씀해주세요 💫"
            }
        }

    def generate_contextual_message(self, context: Dict[str, Any]) -> str:
        """맥락에 맞는 메시지 생성"""
        try:
            current_page = context.get('current_page', '')
            current_step = context.get('current_step', '')
            previous_input = context.get('previous_input', {})
            user_tone = context.get('user_tone', 'friendly')

            # 특정 페이지의 특정 단계에 대한 메시지
            if current_page in self.context_templates and current_step in self.context_templates[current_page]:
                templates = self.context_templates[current_page][current_step]
                message = random.choice(templates)

                # 이전 입력 내용을 반영한 개인화
                if previous_input:
                    message = self._personalize_message(message, previous_input)

                return message

            # 기본 인사말
            return self._get_greeting_by_tone(user_tone)

        except Exception as e:
            return "안녕하세요! 무엇을 도와드릴까요? 😊"

    def _personalize_message(self, message: str, previous_input: Dict[str, Any]) -> str:
        """이전 입력 내용을 반영한 개인화된 메시지 생성"""
        try:
            # 부서별 맞춤 메시지
            if 'department' in previous_input:
                dept = previous_input['department']
                if '개발' in dept:
                    message = message.replace('부서', '개발팀')
                elif '디자인' in dept:
                    message = message.replace('부서', '디자인팀')
                elif '마케팅' in dept:
                    message = message.replace('부서', '마케팅팀')

            # 경력별 맞춤 메시지
            if 'experience' in previous_input:
                exp = previous_input['experience']
                if '신입' in exp:
                    message = message.replace('경력', '신입 지원자')
                elif '3-5년' in exp:
                    message = message.replace('경력', '중급 개발자')
                elif '5년 이상' in exp:
                    message = message.replace('경력', '시니어 개발자')

            return message

        except Exception:
            return message

    def _get_greeting_by_tone(self, tone: str) -> str:
        """톤에 맞는 인사말 반환"""
        if tone in self.tone_templates:
            return self.tone_templates[tone]['greeting']
        return random.choice(self.greeting_templates)

    def generate_follow_up_message(self, context: Dict[str, Any]) -> str:
        """후속 질문이나 안내 메시지 생성"""
        try:
            current_page = context.get('current_page', '')
            completed_steps = context.get('completed_steps', [])

            if current_page == 'job_posting':
                if len(completed_steps) == 1:
                    return "다음 단계로 넘어가볼까요? 부서를 선택해주세요 🚀"
                elif len(completed_steps) == 2:
                    return "잘 진행되고 있어요! 이제 경력 요건을 정해보세요 💼"
                elif len(completed_steps) == 3:
                    return "거의 다 왔어요! 급여 조건을 입력해주세요 💰"
                elif len(completed_steps) == 4:
                    return "마지막 단계예요! 근무지를 알려주세요 🌍"

            return "다음 단계를 진행해보시겠어요? 😊"

        except Exception:
            return "추가로 도움이 필요한 부분이 있으시면 말씀해주세요! 💫"

    def generate_encouragement_message(self, context: Dict[str, Any]) -> str:
        """격려나 동기부여 메시지 생성"""
        try:
            current_page = context.get('current_page', '')
            progress = context.get('progress', 0)

            if progress >= 0.8:
                return "거의 다 완성되었어요! 마지막 한 걸음이에요 🎯"
            elif progress >= 0.6:
                return "잘 진행되고 있어요! 조금만 더 힘내세요 💪"
            elif progress >= 0.4:
                return "반쯤 왔어요! 계속 진행해보세요 🚀"
            elif progress >= 0.2:
                return "좋은 시작이에요! 차근차근 진행해보세요 ✨"
            else:
                return "시작이 반이에요! 차근차근 진행해보세요 🌟"

        except Exception:
            return "잘 하고 있어요! 계속 진행해보세요 💫"
