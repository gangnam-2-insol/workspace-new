"""
챗봇 응답 모델들
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SessionStartResponse(BaseModel):
    session_id: str
    question: str
    current_field: str

class ChatbotResponse(BaseModel):
    message: str
    field: Optional[str] = None
    value: Optional[str] = None
    suggestions: Optional[List[str]] = []
    confidence: Optional[float] = None
    items: Optional[List[Dict[str, Any]]] = None  # 선택 가능한 항목들
    show_item_selection: Optional[bool] = False  # 항목 선택 UI 표시 여부

class ConversationResponse(BaseModel):
    message: str
    is_conversation: bool = True
    suggestions: Optional[List[str]] = []
    field: Optional[str] = None
    value: Optional[str] = None
    response_type: str = "conversation"  # "conversation" 또는 "selection"
    selectable_items: Optional[List[Dict[str, str]]] = []  # 선택 가능한 항목들

