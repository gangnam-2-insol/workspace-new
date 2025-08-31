"""
검증 유틸리티
"""

import re
from typing import Any, Dict, List, Optional


class ValidationUtils:
    """검증 유틸리티 클래스"""

    @staticmethod
    def validate_field_value(field: str, value: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """필드 값 검증"""
        if not value or not value.strip():
            return {
                "valid": False,
                "message": f"{field}은(는) 필수 입력 항목입니다."
            }

        # 필드별 특별 검증
        if field == "email":
            return ValidationUtils._validate_email(value)
        elif field == "phone":
            return ValidationUtils._validate_phone(value)
        elif field == "salary":
            return ValidationUtils._validate_salary(value)
        elif field == "experience":
            return ValidationUtils._validate_experience(value)
        elif field == "headcount":
            return ValidationUtils._validate_headcount(value)
        elif field == "location":
            return ValidationUtils._validate_location(value)
        else:
            return ValidationUtils._validate_general_text(value)

    @staticmethod
    def _validate_email(value: str) -> Dict[str, Any]:
        """이메일 검증"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return {"valid": True, "message": "유효한 이메일입니다."}
        else:
            return {"valid": False, "message": "올바른 이메일 형식이 아닙니다."}

    @staticmethod
    def _validate_phone(value: str) -> Dict[str, Any]:
        """전화번호 검증"""
        # 숫자만 추출
        digits = re.sub(r'\D', '', value)

        if len(digits) == 10 or len(digits) == 11:
            return {"valid": True, "message": "유효한 전화번호입니다."}
        else:
            return {"valid": False, "message": "올바른 전화번호 형식이 아닙니다."}

    @staticmethod
    def _validate_salary(value: str) -> Dict[str, Any]:
        """급여 검증"""
        # 숫자 추출
        numbers = re.findall(r'\d+', value)

        if numbers:
            salary = int(numbers[0])
            if 1000 <= salary <= 10000:  # 1000만원 ~ 1억원
                return {"valid": True, "message": "유효한 급여입니다."}
            else:
                return {"valid": False, "message": "급여는 1000만원 ~ 1억원 사이여야 합니다."}
        else:
            return {"valid": False, "message": "급여에는 숫자가 포함되어야 합니다."}

    @staticmethod
    def _validate_experience(value: str) -> Dict[str, Any]:
        """경력 검증"""
        valid_experiences = ["신입", "1-3년", "3-5년", "5-10년", "10년 이상"]

        if value in valid_experiences:
            return {"valid": True, "message": "유효한 경력입니다."}
        else:
            return {"valid": False, "message": f"경력은 다음 중 하나여야 합니다: {', '.join(valid_experiences)}"}

    @staticmethod
    def _validate_headcount(value: str) -> Dict[str, Any]:
        """인원 수 검증"""
        numbers = re.findall(r'\d+', value)

        if numbers:
            count = int(numbers[0])
            if 0 <= count <= 100:
                return {"valid": True, "message": "유효한 인원 수입니다."}
            else:
                return {"valid": False, "message": "인원 수는 0명 ~ 100명 사이여야 합니다."}
        else:
            return {"valid": False, "message": "인원 수에는 숫자가 포함되어야 합니다."}

    @staticmethod
    def _validate_location(value: str) -> Dict[str, Any]:
        """지역 검증"""
        valid_locations = [
            "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
            "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
        ]

        if value in valid_locations:
            return {"valid": True, "message": "유효한 지역입니다."}
        else:
            return {"valid": False, "message": f"지역은 다음 중 하나여야 합니다: {', '.join(valid_locations)}"}

    @staticmethod
    def _validate_general_text(value: str) -> Dict[str, Any]:
        """일반 텍스트 검증"""
        if len(value.strip()) < 2:
            return {"valid": False, "message": "최소 2글자 이상 입력해주세요."}
        elif len(value.strip()) > 1000:
            return {"valid": False, "message": "최대 1000글자까지 입력 가능합니다."}
        else:
            return {"valid": True, "message": "유효한 텍스트입니다."}

    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """폼 데이터 전체 검증"""
        errors = {}
        warnings = {}

        for field, value in form_data.items():
            validation_result = ValidationUtils.validate_field_value(field, str(value))

            if not validation_result["valid"]:
                errors[field] = validation_result["message"]
            elif "warning" in validation_result:
                warnings[field] = validation_result["message"]

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    @staticmethod
    def sanitize_input(value: str) -> str:
        """입력값 정리"""
        if not value:
            return ""

        # HTML 태그 제거
        value = re.sub(r'<[^>]+>', '', value)

        # 특수문자 처리
        value = re.sub(r'[<>"\']', '', value)

        # 공백 정리
        value = re.sub(r'\s+', ' ', value.strip())

        return value

