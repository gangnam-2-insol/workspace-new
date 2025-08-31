from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from dataclasses import dataclass
from ..shared.models import PyObjectId

# 응답 모드
class ResponseMode(str, Enum):
    CHAT = "chat"
    TOOL = "tool"
    ACTION = "action"

# 의도 분류
class IntentType(str, Enum):
    GREETING = "greeting"
    GITHUB_ANALYSIS = "github_analysis"
    PAGE_NAVIGATION = "page_navigation"
    JOB_POSTING_CREATION = "job_posting_creation"
    APPLICANT_MANAGEMENT = "applicant_management"
    RESUME_UPLOAD = "resume_upload"
    RESUME_SEARCH = "resume_search"
    AI_ANALYSIS = "ai_analysis"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"

# 도구 타입
class ToolType(str, Enum):
    GITHUB_ANALYZER = "github_analyzer"
    PAGE_NAVIGATOR = "page_navigator"
    JOB_POSTING_CREATOR = "job_posting_creator"
    APPLICANT_MANAGER = "applicant_manager"
    PDF_OCR = "pdf_ocr"
    RESUME_SEARCHER = "resume_searcher"
    AI_ANALYZER = "ai_analyzer"

# 에이전트 요청 모델
@dataclass
class AgentRequest:
    """에이전트 시스템의 요청 데이터"""
    user_input: str = Field(..., description="사용자 입력 메시지")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="대화 히스토리")
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[Dict[str, Any]] = Field(None, description="추가 컨텍스트")

# 에이전트 출력 모델
@dataclass
class AgentOutput:
    """에이전트 시스템의 출력 데이터"""
    success: bool = Field(..., description="성공 여부")
    response: str = Field(..., description="응답 메시지")
    intent: str = Field(..., description="감지된 의도")
    confidence: float = Field(default=0.0, description="신뢰도")
    extracted_fields: Optional[Dict[str, Any]] = Field(None, description="추출된 필드")
    session_id: Optional[str] = Field(None, description="세션 ID")

# 채팅 메시지 모델
class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    message: str = Field(..., description="메시지 내용")
    session_id: Optional[str] = Field(None, description="세션 ID")
    timestamp: Optional[datetime] = Field(None, description="타임스탬프")

# 채팅 응답 모델
class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    mode: ResponseMode = Field(..., description="응답 모드")
    tool_used: Optional[str] = Field(None, description="사용된 도구")
    confidence: float = Field(default=0.0, description="신뢰도")
    session_id: Optional[str] = Field(None, description="세션 ID")
    quick_actions: Optional[List[Dict[str, Any]]] = Field(None, description="빠른 액션")
    error_info: Optional[Dict[str, Any]] = Field(None, description="오류 정보")

# 세션 모델
class ChatSession(BaseModel):
    """채팅 세션 모델"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str = Field(..., description="세션 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="대화 히스토리")
    context: Dict[str, Any] = Field(default_factory=dict, description="세션 컨텍스트")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="마지막 활동")
    is_active: bool = Field(default=True, description="활성 상태")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# GitHub 분석 요청 모델
class GitHubAnalysisRequest(BaseModel):
    """GitHub 분석 요청 모델"""
    username: str = Field(..., description="GitHub 사용자명")
    session_id: Optional[str] = Field(None, description="세션 ID")
    analysis_type: Optional[str] = Field(default="comprehensive", description="분석 타입")

# GitHub 분석 결과 모델
class GitHubAnalysisResult(BaseModel):
    """GitHub 분석 결과 모델"""
    username: str = Field(..., description="GitHub 사용자명")
    profile_info: Dict[str, Any] = Field(default_factory=dict, description="프로필 정보")
    repositories: List[Dict[str, Any]] = Field(default_factory=list, description="레포지토리 정보")
    activity_analysis: Dict[str, Any] = Field(default_factory=dict, description="활동 분석")
    skill_analysis: Dict[str, Any] = Field(default_factory=dict, description="기술 스택 분석")
    overall_score: float = Field(default=0.0, description="종합 점수")
    recommendations: List[str] = Field(default_factory=list, description="권장사항")

# 페이지 네비게이션 요청 모델
class PageNavigationRequest(BaseModel):
    """페이지 네비게이션 요청 모델"""
    target_page: str = Field(..., description="목표 페이지")
    session_id: Optional[str] = Field(None, description="세션 ID")
    navigation_type: Optional[str] = Field(default="direct", description="네비게이션 타입")

# 페이지 네비게이션 결과 모델
class PageNavigationResult(BaseModel):
    """페이지 네비게이션 결과 모델"""
    target_page: str = Field(..., description="목표 페이지")
    navigation_success: bool = Field(..., description="네비게이션 성공 여부")
    current_url: Optional[str] = Field(None, description="현재 URL")
    page_title: Optional[str] = Field(None, description="페이지 제목")
    error_message: Optional[str] = Field(None, description="오류 메시지")

# 도구 실행 요청 모델
class ToolExecutionRequest(BaseModel):
    """도구 실행 요청 모델"""
    tool_type: ToolType = Field(..., description="도구 타입")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="도구 파라미터")
    session_id: Optional[str] = Field(None, description="세션 ID")

# 도구 실행 결과 모델
class ToolExecutionResult(BaseModel):
    """도구 실행 결과 모델"""
    tool_type: ToolType = Field(..., description="도구 타입")
    success: bool = Field(..., description="실행 성공 여부")
    result: Dict[str, Any] = Field(default_factory=dict, description="실행 결과")
    execution_time: float = Field(default=0.0, description="실행 시간")
    error_message: Optional[str] = Field(None, description="오류 메시지")

# 의도 분류 결과 모델
class IntentClassificationResult(BaseModel):
    """의도 분류 결과 모델"""
    intent: IntentType = Field(..., description="분류된 의도")
    confidence: float = Field(..., description="신뢰도")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="추출된 엔티티")
    suggested_tools: List[ToolType] = Field(default_factory=list, description="제안된 도구")

# 필드 추출 결과 모델
class FieldExtractionResult(BaseModel):
    """필드 추출 결과 모델"""
    extracted_fields: Dict[str, Any] = Field(default_factory=dict, description="추출된 필드")
    confidence: float = Field(default=0.0, description="신뢰도")
    missing_fields: List[str] = Field(default_factory=list, description="누락된 필드")
    suggestions: List[str] = Field(default_factory=list, description="제안사항")

# 빠른 액션 모델
class QuickAction(BaseModel):
    """빠른 액션 모델"""
    id: str = Field(..., description="액션 ID")
    title: str = Field(..., description="액션 제목")
    description: str = Field(..., description="액션 설명")
    icon: str = Field(..., description="아이콘")
    action_type: str = Field(..., description="액션 타입")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="액션 파라미터")

# 세션 통계 모델
class SessionStatistics(BaseModel):
    """세션 통계 모델"""
    total_sessions: int = Field(..., description="총 세션 수")
    active_sessions: int = Field(..., description="활성 세션 수")
    average_session_duration: float = Field(..., description="평균 세션 시간")
    total_messages: int = Field(..., description="총 메시지 수")
    tool_usage_stats: Dict[str, int] = Field(default_factory=dict, description="도구 사용 통계")
    intent_distribution: Dict[str, int] = Field(default_factory=dict, description="의도 분포")

# 에러 정보 모델
class ErrorInfo(BaseModel):
    """에러 정보 모델"""
    error_code: str = Field(..., description="에러 코드")
    error_message: str = Field(..., description="에러 메시지")
    error_type: str = Field(..., description="에러 타입")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="에러 발생 시간")
    context: Dict[str, Any] = Field(default_factory=dict, description="에러 컨텍스트")

# 컨텍스트 정보 모델
class ContextInfo(BaseModel):
    """컨텍스트 정보 모델"""
    current_page: Optional[str] = Field(None, description="현재 페이지")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="사용자 선호도")
    recent_actions: List[Dict[str, Any]] = Field(default_factory=list, description="최근 액션")
    session_data: Dict[str, Any] = Field(default_factory=dict, description="세션 데이터")

# 대화 히스토리 모델
class ConversationHistory(BaseModel):
    """대화 히스토리 모델"""
    session_id: str = Field(..., description="세션 ID")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="메시지 목록")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="수정일시")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
