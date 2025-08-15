import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

def classify_input(user_input: str) -> Dict[str, Any]:
    """사용자 입력을 분류합니다."""
    lower_input = user_input.lower()
    
    # 필드 관련 키워드들
    field_keywords = {
        'department': ['부서', '팀', '직무', '개발', '마케팅', '영업', '디자인', '기획'],
        'headcount': ['인원', '명', '명수', '채용인원'],
        'salary': ['급여', '연봉', '월급', '봉급'],
        'location': ['위치', '근무지', '사무실', '지역'],
        'experience': ['경력', '경험', '연차'],
        'deadline': ['마감', '마감일', '기한', '지원마감']
    }
    
    # 질문 관련 키워드들
    question_keywords = ['어떻게', '방법', '알려주세요', '도움', '가르쳐', '설명']
    
    # 대화 관련 키워드들
    chat_keywords = ['안녕', '고마워', '감사', '좋아', '싫어', '그래']
    
    # 분류 로직
    for field, keywords in field_keywords.items():
        for keyword in keywords:
            if keyword in lower_input:
                return {
                    'type': 'field',
                    'category': field,
                    'value': extract_value(user_input, field),
                    'confidence': 0.8
                }
    
    # 질문인지 확인
    if any(keyword in lower_input for keyword in question_keywords):
        return {
            'type': 'question',
            'category': 'general',
            'confidence': 0.7
        }
    
    # 대화인지 확인
    if any(keyword in lower_input for keyword in chat_keywords):
        return {
            'type': 'chat',
            'category': 'casual',
            'confidence': 0.6
        }
    
    # 기본값
    return {
        'type': 'unknown',
        'category': 'general',
        'confidence': 0.3
    }

def extract_value(user_input: str, field_type: str) -> Optional[str]:
    """사용자 입력에서 값을 추출합니다."""
    if field_type == 'headcount':
        # 숫자 + 명 패턴 찾기
        match = re.search(r'(\d+)명', user_input)
        if match:
            return match.group(1)
    
    elif field_type == 'salary':
        # 급여 패턴 찾기
        match = re.search(r'(\d+[만천]?원)', user_input)
        if match:
            return match.group(1)
    
    elif field_type == 'department':
        # 부서명 추출
        departments = ['개발', '마케팅', '영업', '디자인', '기획', '인사']
        for dept in departments:
            if dept in user_input:
                return dept
    
    # 기본값: 입력된 텍스트 그대로 반환
    return user_input.strip()

def validate_session(session_id: str) -> bool:
    """세션 ID의 유효성을 검증합니다."""
    if not session_id:
        return False
    
    # 세션 ID 형식 검증 (예: uuid 형식)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(uuid_pattern, session_id):
        return True
    
    # 오프라인 세션 ID 검증
    if session_id.startswith('offline-'):
        return True
    
    return False

def format_response(message: str, response_type: str = 'text') -> Dict[str, Any]:
    """응답을 포맷팅합니다."""
    return {
        'message': message,
        'type': response_type,
        'timestamp': str(datetime.now()),
        'success': True
    }

def create_error_response(error_message: str, error_code: str = 'UNKNOWN_ERROR') -> Dict[str, Any]:
    """에러 응답을 생성합니다."""
    return {
        'message': error_message,
        'type': 'error',
        'error_code': error_code,
        'timestamp': str(datetime.now()),
        'success': False
    }

def sanitize_input(user_input: str) -> str:
    """사용자 입력을 정리합니다."""
    # HTML 태그 제거
    clean_input = re.sub(r'<[^>]+>', '', user_input)
    
    # 특수 문자 제거 (한글, 영문, 숫자, 기본 문장부호만 허용)
    clean_input = re.sub(r'[^\w\s가-힣.,!?()]', '', clean_input)
    
    # 연속된 공백 제거
    clean_input = re.sub(r'\s+', ' ', clean_input)
    
    return clean_input.strip()

def get_contextual_suggestions(current_field: str, filled_fields: Dict[str, Any]) -> List[str]:
    """컨텍스트에 맞는 제안을 생성합니다."""
    suggestions = []
    
    if current_field == 'department':
        suggestions = ['개발팀', '마케팅팀', '영업팀', '디자인팀', '기획팀']
    
    elif current_field == 'headcount':
        suggestions = ['1명', '2명', '3명', '5명', '10명']
    
    elif current_field == 'salary':
        suggestions = ['3000만원', '4000만원', '5000만원', '협의']
    
    elif current_field == 'location':
        suggestions = ['서울', '부산', '대구', '인천', '대전']
    
    return suggestions 