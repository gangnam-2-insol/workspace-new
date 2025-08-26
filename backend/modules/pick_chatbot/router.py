from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
import motor.motor_asyncio
from .models import (
    ChatMessage, ChatResponse, GitHubAnalysisRequest, GitHubAnalysisResult,
    PageNavigationRequest, PageNavigationResult, ToolExecutionRequest,
    ToolExecutionResult, SessionStatistics
)
from .services import PickChatbotService
from ..shared.models import BaseResponse

router = APIRouter(prefix="/api/pick-chatbot", tags=["픽톡"])

def get_pick_chatbot_service(db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()) -> PickChatbotService:
    return PickChatbotService(db)

@router.post("/chat", response_model=BaseResponse)
async def chat_with_pick_chatbot(
    chat_message: ChatMessage,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """픽톡과 대화"""
    try:
        response = await pick_service.process_chat_message(chat_message)
        
        return BaseResponse(
            success=response.success,
            message=response.message,
            data={
                "mode": response.mode,
                "tool_used": response.tool_used,
                "confidence": response.confidence,
                "session_id": response.session_id,
                "quick_actions": response.quick_actions,
                "error_info": response.error_info
            }
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채팅 처리에 실패했습니다: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=BaseResponse)
async def get_session(
    session_id: str,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """세션 정보 조회"""
    try:
        session = await pick_service.get_session(session_id)
        if not session:
            return BaseResponse(
                success=False,
                message="세션을 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="세션 조회 성공",
            data=session.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"세션 조회에 실패했습니다: {str(e)}"
        )

@router.delete("/session/{session_id}", response_model=BaseResponse)
async def delete_session(
    session_id: str,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """세션 삭제"""
    try:
        success = await pick_service.delete_session(session_id)
        if not success:
            return BaseResponse(
                success=False,
                message="세션을 찾을 수 없습니다."
            )
        
        return BaseResponse(
            success=True,
            message="세션이 성공적으로 삭제되었습니다."
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"세션 삭제에 실패했습니다: {str(e)}"
        )

@router.post("/tools/github", response_model=BaseResponse)
async def analyze_github(
    request: GitHubAnalysisRequest,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """GitHub 분석 도구"""
    try:
        result = await pick_service.analyze_github(request)
        
        return BaseResponse(
            success=True,
            message="GitHub 분석이 완료되었습니다.",
            data=result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"GitHub 분석에 실패했습니다: {str(e)}"
        )

@router.post("/tools/navigate", response_model=BaseResponse)
async def navigate_page(
    request: PageNavigationRequest,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """페이지 네비게이션 도구"""
    try:
        result = await pick_service.navigate_page(request)
        
        return BaseResponse(
            success=True,
            message="페이지 네비게이션이 완료되었습니다.",
            data=result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"페이지 네비게이션에 실패했습니다: {str(e)}"
        )

@router.post("/tools/execute", response_model=BaseResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """도구 실행"""
    try:
        result = await pick_service.execute_tool(request)
        
        return BaseResponse(
            success=result.success,
            message="도구 실행이 완료되었습니다." if result.success else f"도구 실행에 실패했습니다: {result.error_message}",
            data=result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"도구 실행에 실패했습니다: {str(e)}"
        )

@router.get("/statistics", response_model=BaseResponse)
async def get_session_statistics(
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """세션 통계 조회"""
    try:
        statistics = await pick_service.get_session_statistics()
        
        return BaseResponse(
            success=True,
            message="세션 통계 조회 성공",
            data=statistics.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"세션 통계 조회에 실패했습니다: {str(e)}"
        )

@router.post("/tools/job-posting", response_model=BaseResponse)
async def create_job_posting_via_chatbot(
    request: dict,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """채팅을 통한 채용공고 생성"""
    try:
        # 채용공고 생성 요청을 도구 실행으로 처리
        tool_request = ToolExecutionRequest(
            tool_type="job_posting_creator",
            parameters=request
        )
        
        result = await pick_service.execute_tool(tool_request)
        
        return BaseResponse(
            success=result.success,
            message="채용공고 생성이 완료되었습니다." if result.success else f"채용공고 생성에 실패했습니다: {result.error_message}",
            data=result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"채용공고 생성에 실패했습니다: {str(e)}"
        )

@router.get("/health", response_model=BaseResponse)
async def health_check():
    """픽톡 서비스 상태 확인"""
    return BaseResponse(
        success=True,
        message="픽톡 서비스가 정상적으로 동작 중입니다.",
        data={
            "status": "healthy",
            "service": "pick-chatbot",
            "version": "1.0.0"
        }
    )

@router.post("/tools/analyze-intent", response_model=BaseResponse)
async def analyze_intent(
    message: str,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """의도 분석 (개발용)"""
    try:
        # 의도 분류 로직 직접 호출
        intent_result = await pick_service._classify_intent(message)
        
        return BaseResponse(
            success=True,
            message="의도 분석이 완료되었습니다.",
            data=intent_result.dict()
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"의도 분석에 실패했습니다: {str(e)}"
        )

@router.post("/tools/extract-fields", response_model=BaseResponse)
async def extract_fields(
    message: str,
    pick_service: PickChatbotService = Depends(get_pick_chatbot_service)
):
    """필드 추출 (개발용)"""
    try:
        # GitHub 사용자명 추출 예시
        username = pick_service._extract_github_username(message)
        target_page = pick_service._extract_target_page(message)
        
        extracted_fields = {
            "github_username": username,
            "target_page": target_page,
            "message": message
        }
        
        return BaseResponse(
            success=True,
            message="필드 추출이 완료되었습니다.",
            data=extracted_fields
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"필드 추출에 실패했습니다: {str(e)}"
        )
