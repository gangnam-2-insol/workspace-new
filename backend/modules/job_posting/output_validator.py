"""
채용공고 에이전트 출력 검증 및 후처리 시스템
JSON 스키마 검증, 자동 복구, 에러 처리 기능
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ValidationStatus(str, Enum):
    """검증 상태"""
    VALID = "valid"
    INVALID = "invalid"
    PARTIALLY_VALID = "partially_valid"
    REPAIRED = "repaired"

class ErrorType(str, Enum):
    """에러 타입"""
    JSON_PARSE_ERROR = "json_parse_error"
    MISSING_FIELD = "missing_field"
    INVALID_TYPE = "invalid_type"
    INVALID_FORMAT = "invalid_format"
    EMPTY_VALUE = "empty_value"
    DUPLICATE_KEY = "duplicate_key"

@dataclass
class ValidationError:
    """검증 에러"""
    error_type: ErrorType
    field: str
    message: str
    severity: str  # "critical", "warning", "info"
    suggested_fix: Optional[str] = None

@dataclass
class ValidationResult:
    """검증 결과"""
    status: ValidationStatus
    errors: List[ValidationError]
    warnings: List[ValidationError]
    repaired_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None

class OutputValidator:
    """출력 검증 및 후처리 시스템"""

    def __init__(self):
        """초기화"""
        # 키워드 추출 결과 스키마
        self.keyword_extraction_schema = {
            "keywords": {
                "type": "array",
                "required": True,
                "items": {"type": "string"},
                "min_items": 1
            },
            "categories": {
                "type": "object",
                "required": False,
                "properties": {
                    "tech_stack": {"type": "array", "items": {"type": "string"}},
                    "job_title": {"type": "array", "items": {"type": "string"}},
                    "experience": {"type": "array", "items": {"type": "string"}},
                    "location": {"type": "array", "items": {"type": "string"}},
                    "work_condition": {"type": "array", "items": {"type": "string"}}
                }
            },
            "confidence": {
                "type": "number",
                "required": False,
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.8
            }
        }

        # 채용공고 생성 결과 스키마
        self.job_posting_schema = {
            "title": {
                "type": "string",
                "required": True,
                "min_length": 5,
                "max_length": 100
            },
            "description": {
                "type": "string",
                "required": True,
                "min_length": 20,
                "max_length": 2000
            },
            "requirements": {
                "type": "array",
                "required": True,
                "items": {"type": "string"},
                "min_items": 1
            },
            "preferred": {
                "type": "array",
                "required": False,
                "items": {"type": "string"},
                "default": []
            },
            "work_conditions": {
                "type": "object",
                "required": True,
                "properties": {
                    "location": {"type": "string", "required": True},
                    "type": {"type": "string", "required": True},
                    "level": {"type": "string", "required": True}
                }
            },
            "tech_stack": {
                "type": "array",
                "required": False,
                "items": {"type": "string"},
                "default": []
            }
        }

        # 기본값 사전
        self.default_values = {
            "keywords": [],
            "categories": {
                "tech_stack": [],
                "job_title": [],
                "experience": [],
                "location": [],
                "work_condition": []
            },
            "confidence": 0.8,
            "title": "채용공고",
            "description": "상세한 업무 내용은 면접 시 안내드립니다.",
            "requirements": ["관련 분야 경험"],
            "preferred": ["프로젝트 경험"],
            "work_conditions": {
                "location": "서울",
                "type": "fulltime",
                "level": "middle"
            },
            "tech_stack": []
        }

        # 자동 복구 규칙
        self.repair_rules = {
            "title": self._repair_title,
            "description": self._repair_description,
            "requirements": self._repair_requirements,
            "keywords": self._repair_keywords,
            "confidence": self._repair_confidence
        }

    def validate_and_repair(self, llm_response: str, schema_type: str = "keyword_extraction") -> ValidationResult:
        """
        LLM 응답을 검증하고 필요시 복구

        Args:
            llm_response: LLM 원본 응답
            schema_type: 스키마 타입 ("keyword_extraction" 또는 "job_posting")

        Returns:
            검증 및 복구 결과
        """
        try:
            logger.info(f"출력 검증 시작: {schema_type}")

            # 1. JSON 파싱 시도
            parsed_data = self._parse_json_response(llm_response)
            if not parsed_data:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    errors=[ValidationError(
                        error_type=ErrorType.JSON_PARSE_ERROR,
                        field="root",
                        message="JSON 파싱 실패",
                        severity="critical"
                    )],
                    warnings=[],
                    original_data=None
                )

            # 2. 스키마 검증
            schema = self._get_schema(schema_type)
            validation_result = self._validate_schema(parsed_data, schema)

            # 3. 자동 복구 시도
            if validation_result.status in [ValidationStatus.INVALID, ValidationStatus.PARTIALLY_VALID]:
                repaired_data = self._repair_data(parsed_data, schema, validation_result.errors)
                if repaired_data:
                    validation_result.repaired_data = repaired_data
                    validation_result.status = ValidationStatus.REPAIRED

            validation_result.original_data = parsed_data
            logger.info(f"출력 검증 완료: {validation_result.status}")

            return validation_result

        except Exception as e:
            logger.error(f"출력 검증 중 오류: {str(e)}")
            return ValidationResult(
                status=ValidationStatus.INVALID,
                errors=[ValidationError(
                    error_type=ErrorType.JSON_PARSE_ERROR,
                    field="root",
                    message=f"검증 중 오류 발생: {str(e)}",
                    severity="critical"
                )],
                warnings=[],
                original_data=None
            )

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """JSON 응답 파싱"""
        if not response or not response.strip():
            return None

        # 1. 직접 JSON 파싱 시도
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # 2. JSON 블록 추출 시도
        json_patterns = [
            r'```json\s*(.*?)\s*```',  # 마크다운 JSON 블록
            r'```\s*(.*?)\s*```',      # 일반 코드 블록
            r'\{.*\}',                 # 중괄호로 둘러싸인 JSON
            r'\[.*\]'                  # 대괄호로 둘러싸인 JSON
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # 3. 부분 JSON 복구 시도
        return self._repair_partial_json(response)

    def _repair_partial_json(self, response: str) -> Optional[Dict[str, Any]]:
        """부분적으로 깨진 JSON 복구"""
        try:
            # 일반적인 JSON 오류 패턴 수정
            repaired = response

            # 따옴표 문제 수정
            repaired = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', repaired)

            # 쉼표 문제 수정
            repaired = re.sub(r',\s*}', '}', repaired)
            repaired = re.sub(r',\s*]', ']', repaired)

            # 불필요한 문자 제거
            repaired = re.sub(r'[^\x20-\x7E\n\r\t]', '', repaired)

            return json.loads(repaired)
        except:
            return None

    def _get_schema(self, schema_type: str) -> Dict[str, Any]:
        """스키마 조회"""
        if schema_type == "keyword_extraction":
            return self.keyword_extraction_schema
        elif schema_type == "job_posting":
            return self.job_posting_schema
        else:
            raise ValueError(f"알 수 없는 스키마 타입: {schema_type}")

    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """스키마 검증"""
        errors = []
        warnings = []

        # 필수 필드 검증
        for field_name, field_schema in schema.items():
            if field_schema.get("required", False):
                if field_name not in data or data[field_name] is None:
                    errors.append(ValidationError(
                        error_type=ErrorType.MISSING_FIELD,
                        field=field_name,
                        message=f"필수 필드 '{field_name}'가 누락되었습니다",
                        severity="critical",
                        suggested_fix=f"기본값 '{self.default_values.get(field_name, '')}'을 사용하세요"
                    ))
                else:
                    # 타입 검증
                    type_error = self._validate_field_type(data[field_name], field_schema, field_name)
                    if type_error:
                        errors.append(type_error)

                    # 형식 검증
                    format_error = self._validate_field_format(data[field_name], field_schema, field_name)
                    if format_error:
                        warnings.append(format_error)

        # 선택적 필드 검증
        for field_name, field_schema in schema.items():
            if not field_schema.get("required", False) and field_name in data:
                type_error = self._validate_field_type(data[field_name], field_schema, field_name)
                if type_error:
                    warnings.append(type_error)

        # 상태 결정
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.PARTIALLY_VALID
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            status=status,
            errors=errors,
            warnings=warnings
        )

    def _validate_field_type(self, value: Any, schema: Dict[str, Any], field_name: str) -> Optional[ValidationError]:
        """필드 타입 검증"""
        expected_type = schema.get("type")

        if expected_type == "string":
            if not isinstance(value, str):
                return ValidationError(
                    error_type=ErrorType.INVALID_TYPE,
                    field=field_name,
                    message=f"'{field_name}'는 문자열이어야 합니다",
                    severity="critical",
                    suggested_fix=f"값을 문자열로 변환하세요: '{str(value)}'"
                )
        elif expected_type == "array":
            if not isinstance(value, list):
                return ValidationError(
                    error_type=ErrorType.INVALID_TYPE,
                    field=field_name,
                    message=f"'{field_name}'는 배열이어야 합니다",
                    severity="critical",
                    suggested_fix=f"값을 배열로 변환하세요: [{value}]"
                )
        elif expected_type == "object":
            if not isinstance(value, dict):
                return ValidationError(
                    error_type=ErrorType.INVALID_TYPE,
                    field=field_name,
                    message=f"'{field_name}'는 객체여야 합니다",
                    severity="critical",
                    suggested_fix=f"값을 객체로 변환하세요: {{}}"
                )
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                return ValidationError(
                    error_type=ErrorType.INVALID_TYPE,
                    field=field_name,
                    message=f"'{field_name}'는 숫자여야 합니다",
                    severity="critical",
                    suggested_fix=f"값을 숫자로 변환하세요: 0"
                )

        return None

    def _validate_field_format(self, value: Any, schema: Dict[str, Any], field_name: str) -> Optional[ValidationError]:
        """필드 형식 검증"""
        if isinstance(value, str):
            min_length = schema.get("min_length")
            max_length = schema.get("max_length")

            if min_length and len(value) < min_length:
                return ValidationError(
                    error_type=ErrorType.INVALID_FORMAT,
                    field=field_name,
                    message=f"'{field_name}'는 최소 {min_length}자 이상이어야 합니다",
                    severity="warning"
                )

            if max_length and len(value) > max_length:
                return ValidationError(
                    error_type=ErrorType.INVALID_FORMAT,
                    field=field_name,
                    message=f"'{field_name}'는 최대 {max_length}자까지 가능합니다",
                    severity="warning"
                )

        elif isinstance(value, list):
            min_items = schema.get("min_items")
            if min_items and len(value) < min_items:
                return ValidationError(
                    error_type=ErrorType.INVALID_FORMAT,
                    field=field_name,
                    message=f"'{field_name}'는 최소 {min_items}개 이상의 항목이 필요합니다",
                    severity="warning"
                )

        elif isinstance(value, (int, float)):
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")

            if minimum is not None and value < minimum:
                return ValidationError(
                    error_type=ErrorType.INVALID_FORMAT,
                    field=field_name,
                    message=f"'{field_name}'는 최소 {minimum} 이상이어야 합니다",
                    severity="warning"
                )

            if maximum is not None and value > maximum:
                return ValidationError(
                    error_type=ErrorType.INVALID_FORMAT,
                    field=field_name,
                    message=f"'{field_name}'는 최대 {maximum}까지 가능합니다",
                    severity="warning"
                )

        return None

    def _repair_data(self, data: Dict[str, Any], schema: Dict[str, Any],
                    errors: List[ValidationError]) -> Optional[Dict[str, Any]]:
        """데이터 자동 복구"""
        try:
            repaired_data = data.copy()

            for error in errors:
                if error.error_type == ErrorType.MISSING_FIELD:
                    # 필수 필드 누락 시 기본값 추가
                    field_name = error.field
                    if field_name in self.default_values:
                        repaired_data[field_name] = self.default_values[field_name]

                elif error.error_type == ErrorType.INVALID_TYPE:
                    # 타입 오류 시 변환 시도
                    field_name = error.field
                    if field_name in self.repair_rules:
                        repaired_value = self.repair_rules[field_name](repaired_data.get(field_name))
                        if repaired_value is not None:
                            repaired_data[field_name] = repaired_value

                elif error.error_type == ErrorType.EMPTY_VALUE:
                    # 빈 값 시 기본값으로 대체
                    field_name = error.field
                    if field_name in self.default_values:
                        repaired_data[field_name] = self.default_values[field_name]

            # 중복 키 제거
            repaired_data = self._remove_duplicate_keys(repaired_data)

            return repaired_data

        except Exception as e:
            logger.error(f"데이터 복구 중 오류: {str(e)}")
            return None

    def _repair_title(self, value: Any) -> Optional[str]:
        """제목 복구"""
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return " ".join(str(item) for item in value)
        return None

    def _repair_description(self, value: Any) -> Optional[str]:
        """설명 복구"""
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, list):
            return "\n".join(str(item) for item in value)
        return None

    def _repair_requirements(self, value: Any) -> Optional[List[str]]:
        """요구사항 복구"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        elif isinstance(value, str):
            # 쉼표나 줄바꿈으로 분리
            items = re.split(r'[,;\n]', value)
            return [item.strip() for item in items if item.strip()]
        return None

    def _repair_keywords(self, value: Any) -> Optional[List[str]]:
        """키워드 복구"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        elif isinstance(value, str):
            # 쉼표나 공백으로 분리
            items = re.split(r'[,\s]+', value)
            return [item.strip() for item in items if item.strip()]
        return None

    def _repair_confidence(self, value: Any) -> Optional[float]:
        """신뢰도 복구"""
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
        elif isinstance(value, str):
            try:
                confidence = float(value)
                return max(0.0, min(1.0, confidence))
            except:
                return 0.8
        return None

    def _remove_duplicate_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """중복 키 제거"""
        seen_keys = set()
        result = {}

        for key, value in data.items():
            if key not in seen_keys:
                result[key] = value
                seen_keys.add(key)

        return result

    def get_validation_summary(self) -> Dict[str, Any]:
        """검증 통계 반환"""
        return {
            "total_schemas": 2,
            "default_values": len(self.default_values),
            "repair_rules": len(self.repair_rules),
            "supported_error_types": [error_type.value for error_type in ErrorType]
        }
