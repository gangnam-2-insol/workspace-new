"""
응답 생성기
"""

from typing import Dict, Any, List

class ResponseGenerator:
    """응답 생성기 클래스"""
    
    def __init__(self):
        self.response_templates = {
            'recruit': {
                'success': [
                    "채용 정보를 성공적으로 추출했습니다! 🎯",
                    "채용공고 작성을 도와드리겠습니다! 📝",
                    "입력하신 정보를 분석하여 폼에 자동으로 입력해드리겠습니다! ✨"
                ],
                'partial': [
                    "일부 정보를 추출했습니다. 추가 정보를 입력해주세요.",
                    "더 자세한 정보를 알려주시면 더 정확하게 도와드릴 수 있습니다."
                ]
            },
            'question': {
                'general': [
                    "채용 관련 질문에 답변드리겠습니다! 🤔",
                    "궁금한 점이 있으시면 언제든 말씀해주세요! 💬"
                ]
            },
            'chat': {
                'greeting': [
                    "안녕하세요! 채용공고 작성을 도와드리겠습니다! 👋",
                    "반갑습니다! 어떤 도움이 필요하신가요? 😊"
                ],
                'thanks': [
                    "도움이 되어서 기쁩니다! 😊",
                    "감사합니다! 더 필요한 것이 있으시면 언제든 말씀해주세요! 🙏"
                ]
            }
        }
    
    def generate_response(self, intent: str, extracted_fields: Dict[str, Any] = None, confidence: float = 0.0) -> str:
        """의도에 따른 응답 생성"""
        if intent == 'recruit':
            return self._generate_recruit_response(extracted_fields, confidence)
        elif intent == 'question':
            return self._generate_question_response()
        elif intent == 'chat':
            return self._generate_chat_response()
        else:
            return "안녕하세요! 채용공고 작성을 도와드리겠습니다! 👋"
    
    def _generate_recruit_response(self, extracted_fields: Dict[str, Any], confidence: float) -> str:
        """채용 관련 응답 생성"""
        if not extracted_fields:
            return "채용 관련 정보를 입력해주세요. 예: '프론트엔드 개발자 2명 뽑아요. 3년 경력, 연봉 4000만원'"
        
        # 추출된 정보 요약
        field_summary = []
        if extracted_fields.get('department'):
            field_summary.append(f"• 부서: {extracted_fields['department']}")
        if extracted_fields.get('experience'):
            field_summary.append(f"• 경력: {extracted_fields['experience']}")
        if extracted_fields.get('salary'):
            field_summary.append(f"• 급여: {extracted_fields['salary']}")
        if extracted_fields.get('headcount'):
            field_summary.append(f"• 인원: {extracted_fields['headcount']}")
        if extracted_fields.get('location'):
            field_summary.append(f"• 지역: {extracted_fields['location']}")
        
        if field_summary:
            summary_text = "\n".join(field_summary)
            
            if confidence > 0.7:
                template = self.response_templates['recruit']['success'][0]
                return f"{template}\n\n추출된 정보:\n{summary_text}\n\n이 정보가 채용공고 폼에 자동으로 입력됩니다!"
            else:
                template = self.response_templates['recruit']['partial'][0]
                return f"{template}\n\n현재 추출된 정보:\n{summary_text}\n\n더 자세한 정보를 입력해주세요."
        else:
            return "채용 관련 정보를 더 구체적으로 입력해주세요."
    
    def _generate_question_response(self) -> str:
        """질문 관련 응답 생성"""
        import random
        templates = self.response_templates['question']['general']
        return random.choice(templates)
    
    def _generate_chat_response(self) -> str:
        """일반 대화 응답 생성"""
        import random
        templates = self.response_templates['chat']['greeting']
        return random.choice(templates)
    
    def generate_error_response(self, error_type: str = "general") -> str:
        """오류 응답 생성"""
        error_messages = {
            "general": "죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해주세요.",
            "network": "네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해주세요.",
            "timeout": "요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
            "validation": "입력하신 정보를 확인해주세요.",
            "api": "API 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요."
        }
        
        return error_messages.get(error_type, error_messages["general"])
    
    def generate_help_response(self) -> str:
        """도움말 응답 생성"""
        return """채용공고 작성을 도와드리겠습니다! 📝

다음과 같은 정보를 입력해주세요:
• 부서/직무 (예: 프론트엔드 개발자, 마케팅 담당자)
• 경력 요구사항 (예: 3년 경력, 신입 가능)
• 급여 정보 (예: 연봉 4000만원)
• 인원 수 (예: 2명)
• 근무 지역 (예: 서울 강남구)

예시: "프론트엔드 개발자 2명 뽑아요. React 경험 필수, 3년 경력, 연봉 4000만원, 서울 강남구"

어떤 정보를 입력하시겠습니까?"""

