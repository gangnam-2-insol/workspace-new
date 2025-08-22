"""
챗봇 요청 모델들
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SessionStartRequest(BaseModel):
    page: str
    fields: Optional[List[Dict[str, Any]]] = []
    mode: Optional[str] = "normal"

class ChatbotRequest(BaseModel):
    session_id: Optional[str] = None  # 세션 ID는 이제 선택 사항 (Modal/AI Assistant 모드용)
    user_input: str
    # 프론트엔드에서 넘어온 대화 기록
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_field: Optional[str] = None
    current_page: Optional[str] = None  # 현재 페이지 정보 추가
    context: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = "normal"

class ConversationRequest(BaseModel):
    session_id: str
    user_input: str
    current_field: str
    filled_fields: Dict[str, Any] = {}
    mode: str = "conversational"

class GenerateQuestionsRequest(BaseModel):
    current_field: str
    filled_fields: Dict[str, Any] = {}

class FieldUpdateRequest(BaseModel):
    session_id: str
    field: str
    value: str

class SuggestionsRequest(BaseModel):
    field: str
    context: Optional[Dict[str, Any]] = {}

class ValidationRequest(BaseModel):
    field: str
    value: str
    context: Optional[Dict[str, Any]] = {}

class AutoCompleteRequest(BaseModel):
    partial_input: str
    field: str
    context: Optional[Dict[str, Any]] = {}

class RecommendationsRequest(BaseModel):
    current_field: str
    filled_fields: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = {}

