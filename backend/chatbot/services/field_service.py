"""
필드 처리 서비스 클래스
"""

from typing import Dict, Any, List, Optional

class FieldService:
    """필드 처리 서비스"""
    
    def __init__(self):
        self.field_configs = {
            "title": {
                "name": "제목",
                "type": "text",
                "required": True,
                "suggestions": ["프론트엔드 개발자", "백엔드 개발자", "풀스택 개발자", "UI/UX 디자이너"]
            },
            "department": {
                "name": "부서",
                "type": "text",
                "required": True,
                "suggestions": ["개발팀", "디자인팀", "마케팅팀", "영업팀", "기획팀"]
            },
            "experience": {
                "name": "경력",
                "type": "select",
                "required": True,
                "suggestions": ["신입", "1-3년", "3-5년", "5-10년", "10년 이상"]
            },
            "salary": {
                "name": "급여",
                "type": "text",
                "required": False,
                "suggestions": ["3000만원", "4000만원", "5000만원", "6000만원", "협의"]
            },
            "location": {
                "name": "근무지",
                "type": "text",
                "required": True,
                "suggestions": ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
            }
        }
    
    def get_first_question(self, page: str) -> str:
        """첫 번째 질문 생성"""
        if page == "job_posting":
            return "채용공고 제목을 입력해주세요."
        elif page == "resume_analysis":
            return "이력서를 업로드해주세요."
        else:
            return "어떤 도움이 필요하신가요?"
    
    def generate_contextual_questions(self, current_field: str, filled_fields: Dict[str, Any]) -> List[str]:
        """컨텍스트 기반 질문 생성"""
        questions = []
        
        if current_field == "title":
            questions.append("채용공고 제목을 입력해주세요.")
        elif current_field == "department":
            questions.append("어떤 부서에서 채용하시나요?")
        elif current_field == "experience":
            questions.append("요구 경력은 어떻게 되나요?")
        elif current_field == "salary":
            questions.append("급여는 어떻게 되나요?")
        elif current_field == "location":
            questions.append("근무지는 어디인가요?")
        
        return questions
    
    def get_field_suggestions(self, field: str, context: Dict[str, Any] = None) -> List[str]:
        """필드 제안사항 조회"""
        field_config = self.field_configs.get(field, {})
        suggestions = field_config.get("suggestions", [])
        
        # 컨텍스트에 따른 추가 제안사항
        if context:
            if field == "department" and "title" in context:
                title = context["title"].lower()
                if "개발" in title:
                    suggestions.extend(["개발팀", "소프트웨어팀", "엔지니어링팀"])
                elif "디자인" in title:
                    suggestions.extend(["디자인팀", "UX팀", "크리에이티브팀"])
        
        return suggestions
    
    def get_autocomplete_suggestions(self, partial_input: str, field: str, context: Dict[str, Any] = None) -> List[str]:
        """자동완성 제안사항"""
        all_suggestions = self.get_field_suggestions(field, context)
        
        # 부분 입력과 일치하는 제안사항 필터링
        matching_suggestions = [
            suggestion for suggestion in all_suggestions
            if partial_input.lower() in suggestion.lower()
        ]
        
        return matching_suggestions[:5]  # 최대 5개 반환
    
    def get_contextual_recommendations(self, current_field: str, filled_fields: Dict[str, Any], context: Dict[str, Any] = None) -> List[str]:
        """컨텍스트 기반 추천사항"""
        recommendations = []
        
        if current_field == "salary":
            if "experience" in filled_fields:
                experience = filled_fields["experience"]
                if "신입" in experience:
                    recommendations.append("신입 급여는 보통 3000-3500만원 정도입니다.")
                elif "3-5년" in experience:
                    recommendations.append("3-5년 경력 급여는 보통 4000-6000만원 정도입니다.")
        
        elif current_field == "location":
            if "department" in filled_fields:
                department = filled_fields["department"]
                if "개발" in department:
                    recommendations.append("개발팀은 보통 서울 강남구나 판교에 위치합니다.")
                elif "마케팅" in department:
                    recommendations.append("마케팅팀은 보통 서울 강남구나 홍대에 위치합니다.")
        
        return recommendations
    
    def validate_field_value(self, field: str, value: str) -> Dict[str, Any]:
        """필드 값 검증"""
        field_config = self.field_configs.get(field, {})
        is_required = field_config.get("required", False)
        
        if is_required and not value.strip():
            return {
                "valid": False,
                "message": f"{field_config.get('name', field)}은(는) 필수 입력 항목입니다."
            }
        
        # 필드별 특별 검증
        if field == "salary":
            if value and not any(char.isdigit() for char in value):
                return {
                    "valid": False,
                    "message": "급여에는 숫자가 포함되어야 합니다."
                }
        
        return {
            "valid": True,
            "message": "유효한 값입니다."
        }

