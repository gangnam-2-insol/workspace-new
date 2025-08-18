from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import traceback
import re
from openai import AsyncOpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
try:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("OpenAI 클라이언트 초기화 성공")
except Exception as e:
    print(f"OpenAI 클라이언트 초기화 실패: {e}")
    client = None

# 의도 감지 유틸리티
HARDCODED_FIELDS = {
    "UI/UX 디자인": "지원 분야: UI/UX 디자인으로 설정되었습니다.",
    "그래픽 디자인": "지원 분야: 그래픽 디자인으로 설정되었습니다.",
    "Figma 경험": "사용 툴: Figma로 등록했습니다.",
    "개발팀": "부서: 개발팀으로 설정되었습니다.",
    "마케팅팀": "부서: 마케팅팀으로 설정되었습니다.",
    "영업팀": "부서: 영업팀으로 설정되었습니다.",
    "디자인팀": "부서: 디자인팀으로 설정되었습니다.",
}

def classify_input(text: str) -> dict:
    """
    키워드 기반 1차 분류 함수
    """
    text_lower = text.lower()
    
    # 채용 관련 키워드 분류
    if any(keyword in text_lower for keyword in ["채용 인원", "몇 명", "인원수", "채용인원"]):
        return {'type': 'question', 'category': '채용 인원', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["주요 업무", "업무 내용", "담당 업무", "직무"]):
        return {'type': 'question', 'category': '주요 업무', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["근무 시간", "근무시간", "출근 시간", "퇴근 시간"]):
        return {'type': 'question', 'category': '근무 시간', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["급여", "연봉", "월급", "보수", "임금"]):
        return {'type': 'question', 'category': '급여 조건', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["근무 위치", "근무지", "사무실", "오피스"]):
        return {'type': 'question', 'category': '근무 위치', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["마감일", "지원 마감", "채용 마감", "마감"]):
        return {'type': 'question', 'category': '마감일', 'confidence': 0.8}
    
    if any(keyword in text_lower for keyword in ["이메일", "연락처", "contact", "email"]):
        return {'type': 'question', 'category': '연락처 이메일', 'confidence': 0.8}
    
    # 부서 관련 키워드
    if any(keyword in text_lower for keyword in ["개발팀", "개발", "프로그래밍", "코딩"]):
        return {'type': 'field', 'category': '부서', 'value': '개발팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["마케팅팀", "마케팅", "홍보", "광고"]):
        return {'type': 'field', 'category': '부서', 'value': '마케팅팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["영업팀", "영업", "세일즈"]):
        return {'type': 'field', 'category': '부서', 'value': '영업팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["디자인팀", "디자인", "UI/UX", "그래픽"]):
        return {'type': 'field', 'category': '부서', 'value': '디자인팀', 'confidence': 0.9}
    
    # 질문 키워드 감지
    question_keywords = ["어떻게", "왜", "무엇", "뭐", "언제", "어디", "추천", "기준", "장점", "단점", "차이", "있을까", "있나요", "어떤", "무슨", "궁금", "알려줘", "설명해줘"]
    if any(keyword in text_lower for keyword in question_keywords) or text.strip().endswith("?"):
        return {'type': 'question', 'category': 'general', 'confidence': 0.8}
    
    # 일상 대화 키워드
    chat_keywords = ["안녕", "반가워", "고마워", "감사", "좋아", "싫어", "그래", "응", "네", "아니"]
    if any(keyword in text_lower for keyword in chat_keywords):
        return {'type': 'chat', 'category': '일상대화', 'confidence': 0.7}
    
    # 기본값: 답변으로 처리
    return {'type': 'answer', 'category': 'general', 'confidence': 0.6}

# 기존 detect_intent 함수는 호환성을 위해 유지
def detect_intent(user_input: str):
    classification = classify_input(user_input)
    
    if classification['type'] == 'field':
        return "field", HARDCODED_FIELDS.get(classification['value'], f"{classification['value']}로 설정되었습니다.")
    elif classification['type'] == 'question':
        return "question", None
    else:
        return "answer", None

# 프롬프트 템플릿
PROMPT_TEMPLATE = """
너는 채용 어시스턴트야. 사용자의 답변을 분석해 의도를 파악하고, 질문인지 요청인지 구분해서 필요한 응답을 진행해.

- 사용자가 요청한 "지원 분야"는 아래와 같은 식으로 명확히 처리해줘:
  - UI/UX 디자인
  - 그래픽 디자인
  - Figma 경험 등

- 질문이면 AI답변을 생성하고, 답변이면 다음 항목을 물어봐.

지금까지의 질문 흐름에 따라 대화의 자연스러운 흐름을 유지해.

사용자 입력: {user_input}
현재 필드: {current_field}
"""

# .env 파일 로드
load_dotenv()

# --- OpenAI API 설정 추가 시작 ---
from openai import AsyncOpenAI

# 환경 변수에서 OpenAI API 키 로드
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# API 키가 없어도 기본 응답을 반환하도록 수정
if OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    print("OpenAI 클라이언트 초기화 성공")
else:
    print("Warning: OPENAI_API_KEY not found. Using fallback responses.")
    openai_client = None
# --- OpenAI API 설정 추가 끝 ---

router = APIRouter()

# 기존 세션 저장소 (normal 모드에서 이제 사용하지 않음, modal_assistant에서만 사용)
sessions = {}

# 모달 어시스턴트 세션 저장소 (기존 로직 유지를 위해 유지)
modal_sessions = {}

class SessionStartRequest(BaseModel):
    page: str
    fields: Optional[List[Dict[str, Any]]] = []
    mode: Optional[str] = "normal"

class SessionStartResponse(BaseModel):
    session_id: str
    question: str
    current_field: str

# ChatbotRequest 모델 수정: session_id를 Optional로, conversation_history 추가
class ChatbotRequest(BaseModel):
    session_id: Optional[str] = None  # 세션 ID는 이제 선택 사항 (Modal/AI Assistant 모드용)
    user_input: str
    # 프론트엔드에서 넘어온 대화 기록
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_field: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = "normal"

class ChatbotResponse(BaseModel):
    message: str
    field: Optional[str] = None
    value: Optional[str] = None
    suggestions: Optional[List[str]] = []
    confidence: Optional[float] = None

class ConversationRequest(BaseModel):
    session_id: str
    user_input: str
    current_field: str
    filled_fields: Dict[str, Any] = {}
    mode: str = "conversational"

class ConversationResponse(BaseModel):
    message: str
    is_conversation: bool = True
    suggestions: Optional[List[str]] = []
    field: Optional[str] = None
    value: Optional[str] = None

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

@router.post("/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    print("[DEBUG] /start 요청:", request)
    try:
        session_id = str(uuid.uuid4())
        if request.mode == "modal_assistant":
            if not request.fields:
                print("[ERROR] /start fields 누락")
                raise HTTPException(status_code=400, detail="모달 어시스턴트 모드에서는 fields가 필요합니다")
            modal_sessions[session_id] = {
                "page": request.page,
                "fields": request.fields,
                "current_field_index": 0,
                "filled_fields": {},
                "conversation_history": [],
                "mode": "modal_assistant"
            }
            first_field = request.fields[0]
            response = SessionStartResponse(
                session_id=session_id,
                question=f"안녕하세요! {request.page} 작성을 도와드리겠습니다. 🤖\n\n먼저 {first_field.get('label', '첫 번째 항목')}에 대해 알려주세요.",
                current_field=first_field.get('key', 'unknown')
            )
            print("[DEBUG] /start 응답:", response)
            return response
        else:
            questions = get_questions_for_page(request.page)
            sessions[session_id] = {
                "page": request.page,
                "questions": questions,
                "current_index": 0,
                "current_field": questions[0]["field"] if questions else None,
                "conversation_history": [],
                "mode": "normal"
            }
            response = SessionStartResponse(
                session_id=session_id,
                question=questions[0]["question"] if questions else "질문이 없습니다.",
                current_field=questions[0]["field"] if questions else None
            )
            print("[DEBUG] /start 응답:", response)
            return response
    except Exception as e:
        print("[ERROR] /start 예외:", e)
        traceback.print_exc()
        raise

@router.post("/start-ai-assistant", response_model=SessionStartResponse)
async def start_ai_assistant(request: SessionStartRequest):
    print("[DEBUG] /start-ai-assistant 요청:", request)
    try:
        session_id = str(uuid.uuid4())
        ai_assistant_fields = [
            {"key": "department", "label": "구인 부서", "type": "text"},
            {"key": "headcount", "label": "채용 인원", "type": "text"},
            {"key": "mainDuties", "label": "업무 내용", "type": "text"},
            {"key": "workHours", "label": "근무 시간", "type": "text"},
            {"key": "locationCity", "label": "근무 위치", "type": "text"},
            {"key": "salary", "label": "급여 조건", "type": "text"},
            {"key": "deadline", "label": "마감일", "type": "text"},
            {"key": "contactEmail", "label": "연락처 이메일", "type": "email"}
        ]
        modal_sessions[session_id] = {
            "page": request.page,
            "fields": ai_assistant_fields,
            "current_field_index": 0,
            "filled_fields": {},
            "conversation_history": [],
            "mode": "ai_assistant"
        }
        first_field = ai_assistant_fields[0]
        response = SessionStartResponse(
            session_id=session_id,
            question=f"🤖 AI 도우미를 시작하겠습니다!\n\n먼저 {first_field.get('label', '첫 번째 항목')}에 대해 알려주세요.",
            current_field=first_field.get('key', 'unknown')
        )
        print("[DEBUG] /start-ai-assistant 응답:", response)
        return response
    except Exception as e:
        print("[ERROR] /start-ai-assistant 예외:", e)
        traceback.print_exc()
        raise

@router.post("/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    print("[DEBUG] /ask 요청:", request)
    try:
        if request.mode == "normal" or not request.session_id:
            response = await handle_normal_request(request)
        elif request.mode == "modal_assistant":
            response = await handle_modal_assistant_request(request)
        else:
            print("[ERROR] /ask 알 수 없는 모드:", request.mode)
            raise HTTPException(status_code=400, detail="알 수 없는 챗봇 모드입니다.")
        print("[DEBUG] /ask 응답:", response)
        return response
    except Exception as e:
        print("[ERROR] /ask 예외:", e)
        traceback.print_exc()
        raise

@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest):
    print("[DEBUG] /conversation 요청:", request)
    try:
        response = await generate_conversational_response(
            request.user_input, 
            request.current_field, 
            request.filled_fields
        )
        result = ConversationResponse(
            message=response["message"],
            is_conversation=response.get("is_conversation", True),
            suggestions=response.get("suggestions", []),
            field=response.get("field"),
            value=response.get("value")
        )
        print("[DEBUG] /conversation 응답:", result)
        return result
    except Exception as e:
        print("[ERROR] /conversation 예외:", e)
        traceback.print_exc()
        raise

@router.post("/generate-questions", response_model=Dict[str, Any])
async def generate_contextual_questions(request: GenerateQuestionsRequest):
    """컨텍스트 기반 질문 생성"""
    print("[DEBUG] /generate-questions 요청:", request)
    try:
        questions = await generate_field_questions(
            request.current_field, 
            request.filled_fields
        )
        result = {"questions": questions}
        print("[DEBUG] /generate-questions 응답:", result)
        return result
    except Exception as e:
        print("[ERROR] /generate-questions 예외:", e)
        traceback.print_exc()
        raise

@router.post("/ai-assistant-chat", response_model=ChatbotResponse)
async def ai_assistant_chat(request: ChatbotRequest):
    """AI 도우미 채팅 처리 (session_id 필요)"""
    print("[DEBUG] /ai-assistant-chat 요청:", request)
    if not request.session_id or request.session_id not in modal_sessions:
        print("[ERROR] /ai-assistant-chat 유효하지 않은 세션:", request.session_id)
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")
    
    session = modal_sessions[request.session_id]
    current_field_index = session["current_field_index"]
    fields = session["fields"]
    
    if current_field_index >= len(fields):
        response = ChatbotResponse(
            message="🎉 모든 정보를 입력받았습니다! 채용공고 등록이 완료되었습니다."
        )
        print("[DEBUG] /ai-assistant-chat 응답:", response)
        return response
    
    current_field = fields[current_field_index]
    
    # 대화 히스토리에 사용자 입력 저장
    session["conversation_history"].append({
        "role": "user",
        "content": request.user_input,
        "field": current_field["key"]
    })
    
    # AI 응답 생성 (이 함수는 여전히 시뮬레이션된 응답을 사용합니다)
    ai_response = await generate_ai_assistant_response(request.user_input, current_field, session)
    
    # 대화 히스토리에 AI 응답 저장
    session["conversation_history"].append({
        "role": "assistant",
        "content": ai_response["message"],
        "field": current_field["key"]
    })
    
    # 필드 값이 추출된 경우
    if ai_response.get("value"):
        session["filled_fields"][current_field["key"]] = ai_response["value"]
        
        # 다음 필드로 이동
        session["current_field_index"] += 1
        
        if session["current_field_index"] < len(fields):
            next_field = fields[session["current_field_index"]]
            next_message = f"좋습니다! 이제 {next_field.get('label', '다음 항목')}에 대해 알려주세요."
            ai_response["message"] += f"\n\n{next_message}"
        else:
            ai_response["message"] += "\n\n🎉 모든 정보 입력이 완료되었습니다!"
    
    response = ChatbotResponse(
        message=ai_response["message"],
        field=current_field["key"],
        value=ai_response.get("value"),
        suggestions=ai_response.get("suggestions", []),
        confidence=ai_response.get("confidence", 0.8)
    )
    print("[DEBUG] /ai-assistant-chat 응답:", response)
    return response

async def handle_modal_assistant_request(request: ChatbotRequest):
    """모달 어시스턴트 모드 처리 (session_id 필요)"""
    print("[DEBUG] ===== handle_modal_assistant_request 시작 =====")
    print("[DEBUG] 요청 데이터:", request)
    print("[DEBUG] user_input:", request.user_input)
    print("[DEBUG] current_field:", request.current_field)
    print("[DEBUG] mode:", request.mode)
    print("[DEBUG] session_id:", request.session_id)
    if not request.session_id or request.session_id not in modal_sessions:
        print("[ERROR] /ai-assistant-chat 유효하지 않은 세션:", request.session_id)
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")
    
    session = modal_sessions[request.session_id]
    current_field_index = session["current_field_index"]
    fields = session["fields"]
    
    if current_field_index >= len(fields):
        response = ChatbotResponse(
            message="모든 정보를 입력받았습니다! 완료 버튼을 눌러주세요. 🎉"
        )
        print("[DEBUG] /ai-assistant-chat 응답:", response)
        return response
    
    current_field = fields[current_field_index]
    
    session["conversation_history"].append({
        "role": "user",
        "content": request.user_input,
        "field": current_field["key"]
    })
    
    # 변경: generate_modal_ai_response 대신 simulate_llm_response를 사용하도록 통합
    # simulate_llm_response는 이제 is_conversation 플래그를 반환할 것임
    # 이 부분은 여전히 시뮬레이션된 LLM 응답을 사용합니다.
    llm_response = await simulate_llm_response(request.user_input, current_field["key"], session)
    
    # 대화 히스토리에 LLM 응답 저장
    session["conversation_history"].append({
        "role": "assistant",
        "content": llm_response["message"],
        "field": current_field["key"] if not llm_response.get("is_conversation", False) else None # 대화형 응답은 특정 필드에 귀속되지 않을 수 있음
    })
    
    response_message = llm_response["message"]
    
    # LLM이 필드 값을 추출했다고 판단한 경우 (is_conversation이 false일 때)
    if not llm_response.get("is_conversation", True) and llm_response.get("value"):
        session["filled_fields"][current_field["key"]] = llm_response["value"]
        
        # 다음 필드로 이동
        session["current_field_index"] += 1
        
        if session["current_field_index"] < len(fields):
            next_field = fields[session["current_field_index"]]
            # LLM이 다음 질문을 생성하도록 유도하거나, 여기에서 생성
            next_message = f"\n\n다음으로 {next_field.get('label', '다음 항목')}에 대해 알려주세요."
            response_message += next_message
        else:
            response_message += "\n\n🎉 모든 정보 입력이 완료되었습니다!"
    
    response = ChatbotResponse(
        message=response_message,
        field=current_field["key"] if not llm_response.get("is_conversation", True) else None, # 대화형 응답 시 필드 값은 비워둘 수 있음
        value=llm_response.get("value"),
        suggestions=llm_response.get("suggestions", []), # LLM이 제안을 생성할 수 있다면 활용
        confidence=llm_response.get("confidence", 0.8) # LLM이 confidence를 반환할 수 있다면 활용
    )
    print("[DEBUG] ===== handle_modal_assistant_request 응답 =====")
    print("[DEBUG] 응답 메시지:", response.message)
    print("[DEBUG] 응답 필드:", response.field)
    print("[DEBUG] 응답 값:", response.value)
    print("[DEBUG] 응답 제안:", response.suggestions)
    print("[DEBUG] 응답 신뢰도:", response.confidence)
    print("[DEBUG] ===== handle_modal_assistant_request 완료 =====")
    return response

async def handle_normal_request(request: ChatbotRequest):
    """
    일반 챗봇 요청 처리 (키워드 기반 1차 분류 → LLM 호출 → 응답)
    """
    print("[DEBUG] handle_normal_request 요청:", request)
    user_input = request.user_input
    conversation_history_from_frontend = request.conversation_history

    if not user_input:
        raise HTTPException(status_code=400, detail="사용자 입력이 필요합니다.")

    try:
        # 1) 키워드 기반 1차 분류
        classification = classify_input(user_input)
        print(f"[DEBUG] 분류 결과: {classification}")
        
        # 2) 분류된 결과에 따른 처리
        if classification['type'] == 'field':
            # 필드 값으로 처리
            field_value = classification.get('value', user_input.strip())
            response = ChatbotResponse(
                message=f"{classification['category']}: {field_value}로 설정되었습니다.",
                field=None,
                value=field_value,
                suggestions=[],
                confidence=classification['confidence']
            )
            print("[DEBUG] handle_normal_request 응답 (필드):", response)
            return response
            
        elif classification['type'] == 'question':
            # 3) GPT API 호출로 답변 생성
            ai_response = await call_openai_api(user_input, conversation_history_from_frontend)
            response = ChatbotResponse(
                message=ai_response,
                field=None,
                value=None,
                suggestions=[],
                confidence=classification['confidence']
            )
            print("[DEBUG] handle_normal_request 응답 (질문):", response)
            return response
            
        elif classification['type'] == 'chat':
            # 일상 대화 처리
            response = ChatbotResponse(
                message="안녕하세요! 채용 관련 문의사항이 있으시면 언제든 말씀해 주세요.",
                field=None,
                value=None,
                suggestions=[],
                confidence=classification['confidence']
            )
            print("[DEBUG] handle_normal_request 응답 (일상대화):", response)
            return response
            
        else:
            # 답변인 경우 기본 처리 (자동 완성)
            response = ChatbotResponse(
                message=f"'{user_input}'로 입력하겠습니다. 다음 단계로 진행하겠습니다.",
                field=None,
                value=user_input.strip(),
                suggestions=[],
                confidence=classification['confidence']
            )
            print("[DEBUG] handle_normal_request 응답 (답변):", response)
            return response

    except Exception as e:
        print(f"[ERROR] handle_normal_request 예외: {e}")
        traceback.print_exc()
        response = ChatbotResponse(
            message=f"죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해 주세요. (오류: {str(e)})",
            field=None,
            value=None
        )
        print("[DEBUG] handle_normal_request 응답 (오류):", response)
        return response

# 이 아래 함수들은 현재 시뮬레이션된 응답 로직을 사용합니다.
# 만약 이 함수들도 실제 Gemini API와 연동하고 싶으시다면,
# 해당 함수 내부에 Gemini API 호출 로직을 추가해야 합니다.
async def generate_conversational_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """대화형 응답 생성"""
    print("[DEBUG] generate_conversational_response 요청:", user_input, current_field, filled_fields)
    await asyncio.sleep(0.5)
    
    question_keywords = ["어떤", "무엇", "어떻게", "왜", "언제", "어디서", "얼마나", "몇", "무슨"]
    is_question = any(keyword in user_input for keyword in question_keywords) or user_input.endswith("?")
    
    if is_question:
        response = await handle_question_response(user_input, current_field, filled_fields)
        print("[DEBUG] generate_conversational_response 응답 (질문):", response)
        return response
    else:
        response = await handle_answer_response(user_input, current_field, filled_fields)
        print("[DEBUG] generate_conversational_response 응답 (답변):", response)
        return response

async def handle_question_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """질문에 대한 응답 처리"""
    print("[DEBUG] handle_question_response 요청:", user_input, current_field, filled_fields)
    question_responses = {
        "department": {
            "개발팀": "개발팀은 주로 웹/앱 개발, 시스템 구축, 기술 지원 등을 담당합니다. 프론트엔드, 백엔드, 풀스택 개발자로 구성되어 있으며, 최신 기술 트렌드를 반영한 개발을 진행합니다.",
            "마케팅팀": "마케팅팀은 브랜드 관리, 광고 캠페인 기획, 디지털 마케팅, 콘텐츠 제작, 고객 분석 등을 담당합니다. 온라인/오프라인 마케팅 전략을 수립하고 실행합니다.",
            "영업팀": "영업팀은 신규 고객 발굴, 계약 체결, 고객 관계 관리, 매출 목표 달성 등을 담당합니다. B2B/B2C 영업, 해외 영업 등 다양한 영업 활동을 수행합니다.",
            "디자인팀": "디자인팀은 UI/UX 디자인, 브랜드 디자인, 그래픽 디자인, 웹/앱 디자인 등을 담당합니다. 사용자 경험을 최우선으로 하는 디자인을 제작합니다."
        },
        "headcount": {
            "1명": "현재 업무량과 향후 계획을 고려하여 결정하시면 됩니다. 초기에는 1명으로 시작하고, 필요에 따라 추가 채용을 고려해보세요.",
            "팀 규모": "팀 규모는 업무 특성과 회사 규모에 따라 다릅니다. 소규모 팀(3-5명)부터 대규모 팀(10명 이상)까지 다양하게 구성됩니다.",
            "신입/경력": "업무 특성에 따라 신입/경력을 구분하여 채용하는 것이 일반적입니다. 신입은 성장 잠재력, 경력자는 즉시 투입 가능한 실력을 중시합니다.",
            "계약직/정규직": "프로젝트 기반이면 계약직, 장기적 업무라면 정규직을 고려해보세요. 각각의 장단점을 비교하여 결정하시면 됩니다."
        }
    }
    
    field_responses = question_responses.get(current_field, {})
    
    for keyword, response in field_responses.items():
        if keyword in user_input:
            response_data = {
                "message": response,
                "is_conversation": True,
                "suggestions": list(field_responses.keys())
            }
            print("[DEBUG] handle_question_response 응답:", response_data)
            return response_data
    
    response_data = {
        "message": f"{current_field}에 대한 질문이군요. 더 구체적으로 어떤 부분이 궁금하신지 말씀해 주세요.",
        "is_conversation": True,
        "suggestions": list(field_responses.keys())
    }
    print("[DEBUG] handle_question_response 응답:", response_data)
    return response_data

async def handle_answer_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """답변 처리"""
    print("[DEBUG] handle_answer_response 요청:", user_input, current_field, filled_fields)
    response_data = {
        "message": f"'{user_input}'로 입력하겠습니다. 다음 질문으로 넘어가겠습니다.",
        "field": current_field,
        "value": user_input,
        "is_conversation": False
    }
    print("[DEBUG] handle_answer_response 응답:", response_data)
    return response_data

async def generate_field_questions(current_field: str, filled_fields: Dict[str, Any]) -> List[str]:
    """필드별 질문 생성"""
    print("[DEBUG] generate_field_questions 요청:", current_field, filled_fields)
    questions_map = {
        "department": [
            "개발팀은 어떤 업무를 하나요?",
            "마케팅팀은 어떤 역할인가요?",
            "영업팀의 주요 업무는?",
            "디자인팀은 어떤 일을 하나요?"
        ],
        "headcount": [
            "1명 채용하면 충분한가요?",
            "팀 규모는 어떻게 되나요?",
            "신입/경력 구분해서 채용하나요?",
            "계약직/정규직 중 어떤가요?"
        ],
        "workType": [
            "웹 개발은 어떤 기술을 사용하나요?",
            "앱 개발은 iOS/Android 둘 다인가요?",
            "디자인은 UI/UX 모두인가요?",
            "마케팅은 온라인/오프라인 모두인가요?"
        ],
        "workHours": [
            "유연근무제는 어떻게 운영되나요?",
            "재택근무 가능한가요?",
            "야근이 많은 편인가요?",
            "주말 근무가 있나요?"
        ],
        "location": [
            "원격근무는 얼마나 가능한가요?",
            "출장이 많은 편인가요?",
            "해외 지사 근무 가능한가요?",
            "지방 근무는 어떤가요?"
        ],
        "salary": [
            "연봉 협의는 언제 하나요?",
            "성과급은 어떻게 지급되나요?",
            "인센티브 제도가 있나요?",
            "연봉 인상은 언제 하나요?"
        ]
    }
    
    questions = questions_map.get(current_field, [
        "이 항목에 대해 궁금한 점이 있으신가요?",
        "더 자세한 설명이 필요하신가요?",
        "예시를 들어 설명해드릴까요?"
    ])
    print("[DEBUG] generate_field_questions 응답:", questions)
    return questions

async def generate_modal_ai_response(user_input: str, field: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """모달 어시스턴트용 AI 응답 생성 (시뮬레이션)"""
    print("[DEBUG] generate_modal_ai_response 요청:", user_input, field, session)
    field_key = field.get("key", "")
    field_label = field.get("label", "")
    
    responses = {
        "department": {
            "message": "부서 정보를 확인했습니다. 몇 명을 채용하실 예정인가요?",
            "value": user_input,
            "suggestions": ["1명", "2명", "3명", "5명", "10명"],
            "confidence": 0.8
        },
        "headcount": {
            "message": "채용 인원을 확인했습니다. 어떤 업무를 담당하게 될까요?",
            "value": user_input,
            "suggestions": ["개발", "디자인", "마케팅", "영업", "기획"],
            "confidence": 0.9
        },
        "workType": {
            "message": "업무 내용을 확인했습니다. 근무 시간은 어떻게 되나요?",
            "value": user_input,
            "suggestions": ["09:00-18:00", "10:00-19:00", "유연근무제"],
            "confidence": 0.7
        },
        "workHours": {
            "message": "근무 시간을 확인했습니다. 근무 위치는 어디인가요?",
            "value": user_input,
            "suggestions": ["서울", "부산", "대구", "인천", "대전"],
            "confidence": 0.8
        },
        "location": {
            "message": "근무 위치를 확인했습니다. 급여 조건은 어떻게 되나요?",
            "value": user_input,
            "suggestions": ["면접 후 협의", "3000만원", "4000만원", "5000만원"],
            "confidence": 0.6
        },
        "salary": {
            "message": "급여 조건을 확인했습니다. 마감일은 언제인가요?",
            "value": user_input,
            "suggestions": ["2024년 12월 31일", "2024년 11월 30일", "채용 시 마감"],
            "confidence": 0.7
        },
        "deadline": {
            "message": "마감일을 확인했습니다. 연락처 이메일을 알려주세요.",
            "value": user_input,
            "suggestions": ["hr@company.com", "recruit@company.com"],
            "confidence": 0.8
        },
        "email": {
            "message": "이메일을 확인했습니다. 모든 정보 입력이 완료되었습니다!",
            "value": user_input,
            "suggestions": [],
            "confidence": 0.9
        }
    }
    
    response_data = responses.get(field_key, {
        "message": f"{field_label} 정보를 확인했습니다. 다음 질문으로 넘어가겠습니다.",
        "value": user_input,
        "suggestions": [],
        "confidence": 0.5
    })
    print("[DEBUG] generate_modal_ai_response 응답:", response_data)
    return response_data

async def generate_ai_assistant_response(user_input: str, field: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """AI 도우미용 응답 생성 (개선된 Gemini API 사용)"""
    print("[DEBUG] ===== AI 어시스턴트 응답 생성 시작 =====")
    print("[DEBUG] 사용자 입력:", user_input)
    print("[DEBUG] 현재 필드:", field)
    print("[DEBUG] 세션 정보:", session)
    
    field_key = field.get("key", "")
    field_label = field.get("label", "")
    print(f"[DEBUG] 필드 키: {field_key}, 필드 라벨: {field_label}")
    
    # 1) 키워드 기반 1차 분류
    classification = classify_input(user_input)
    print(f"[DEBUG] 분류 결과: {classification}")
    print(f"[DEBUG] 분류 타입: {classification.get('type')}")
    print(f"[DEBUG] 분류 카테고리: {classification.get('category')}")
    print(f"[DEBUG] 분류 값: {classification.get('value')}")
    print(f"[DEBUG] 신뢰도: {classification.get('confidence')}")
    
    # 2) 분류된 결과에 따른 처리
    if classification['type'] == 'question':
        # 질문인 경우 Gemini API 호출
        try:
            ai_assistant_context = f"""
현재 채용 공고 작성 중입니다. 현재 필드: {field_label} ({field_key})

사용자 질문: {user_input}

이 질문에 대해 채용 공고 작성에 도움이 되는 실무적인 답변을 제공해주세요.
"""
            ai_response = await call_openai_api(ai_assistant_context)
            
            # 사용자 입력에서 value 추출 시도
            extracted_value = user_input.strip()
            print(f"[DEBUG] 질문 처리 - 추출된 값: {extracted_value}")
            
            return {
                "message": ai_response,
                "value": extracted_value,  # 사용자 입력을 value로 설정
                "suggestions": [],
                "confidence": classification['confidence']
            }
        except Exception as e:
            print(f"[ERROR] OpenAI API 호출 실패: {e}")
            return {
                "message": f"{field_label}에 대한 질문이군요. 구체적으로 어떤 부분이 궁금하신가요?",
                "value": None,
                "suggestions": [],
                "confidence": classification['confidence']
            }
    elif classification['type'] == 'chat':
        # 일상 대화 처리
        return {
            "message": "안녕하세요! 채용 공고 작성에 도움이 필요하시면 언제든 말씀해 주세요.",
            "value": None,
            "suggestions": [],
            "confidence": classification['confidence']
        }
    elif classification['type'] == 'field':
        # 필드 입력 처리
        field_value = classification.get('value', user_input)
        print(f"[DEBUG] 필드 입력 처리 - 추출된 값: {field_value}")
        response = {
            "message": f"'{field_value}'로 입력하겠습니다. 다음 항목으로 넘어가겠습니다.",
            "value": field_value,
            "field": field_key,  # 필드 키 추가
            "suggestions": [],
            "confidence": classification['confidence']
        }
        print(f"[DEBUG] 필드 입력 응답: {response}")
        return response
    
    # 기본 응답 (기존 로직 유지)
    responses = {
        "department": {
            "message": f"'{user_input}' 부서로 입력하겠습니다. 몇 명을 채용하실 예정인가요?",
            "value": user_input,
            "suggestions": ["1명", "2명", "3명", "5명", "10명"],
            "confidence": 0.9
        },
        "headcount": {
            "message": f"채용 인원 {user_input}명으로 입력하겠습니다. 어떤 업무를 담당하게 될까요?",
            "value": user_input,
            "suggestions": ["개발", "디자인", "마케팅", "영업", "기획"],
            "confidence": 0.8
        },
        "mainDuties": {
            "message": f"업무 내용 '{user_input}'으로 입력하겠습니다. 근무 시간은 어떻게 되나요?",
            "value": user_input,
            "suggestions": ["09:00-18:00", "10:00-19:00", "유연근무제"],
            "confidence": 0.7
        },
        "workHours": {
            "message": f"근무 시간 '{user_input}'으로 입력하겠습니다. 근무 위치는 어디인가요?",
            "value": user_input,
            "suggestions": ["서울", "부산", "대구", "인천", "대전"],
            "confidence": 0.8
        },
        "locationCity": {
            "message": f"근무 위치 '{user_input}'으로 입력하겠습니다. 급여 조건은 어떻게 되나요?",
            "value": user_input,
            "suggestions": ["면접 후 협의", "3000만원", "4000만원", "5000만원"],
            "confidence": 0.6
        },
        "salary": {
            "message": f"급여 조건 '{user_input}'으로 입력하겠습니다. 마감일은 언제인가요?",
            "value": user_input,
            "suggestions": ["2024년 12월 31일", "2024년 11월 30일", "채용 시 마감"],
            "confidence": 0.7
        },
        "deadline": {
            "message": f"마감일 '{user_input}'으로 입력하겠습니다. 연락처 이메일을 알려주세요.",
            "value": user_input,
            "suggestions": ["hr@company.com", "recruit@company.com"],
            "confidence": 0.8
        },
        "contactEmail": {
            "message": f"연락처 이메일 '{user_input}'으로 입력하겠습니다. 모든 정보 입력이 완료되었습니다!",
            "value": user_input,
            "suggestions": [],
            "confidence": 0.9
        }
    }
    
    response_data = responses.get(field_key, {
        "message": f"{field_label} 정보를 확인했습니다. 다음 질문으로 넘어가겠습니다.",
        "value": user_input,
        "field": field_key,  # 필드 키 추가
        "suggestions": [],
        "confidence": 0.5
    })
    print(f"[DEBUG] 기본 응답 데이터: {response_data}")
    print(f"[DEBUG] 응답 value: {response_data.get('value')}")
    print(f"[DEBUG] 응답 field: {response_data.get('field')}")
    print("[DEBUG] ===== AI 어시스턴트 응답 생성 완료 =====")
    return response_data

async def simulate_llm_response(user_input: str, current_field: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """
    키워드 기반 1차 분류 → LLM 호출 → 응답 처리
    """
    print("[DEBUG] ===== simulate_llm_response 시작 =====")
    print("[DEBUG] user_input:", user_input)
    print("[DEBUG] current_field:", current_field)
    print("[DEBUG] session mode:", session.get("mode"))
    
    await asyncio.sleep(0.5) # 실제 LLM API 호출 시뮬레이션

    # 현재 처리 중인 필드의 사용자 친화적인 레이블 가져오기
    current_field_label = ""
    if session.get("mode") == "modal_assistant":
        fields_config = session.get("fields", [])
        for f in fields_config:
            if f.get("key") == current_field:
                current_field_label = f.get("label", current_field)
                break
    elif session.get("mode") == "normal":
        questions_config = session.get("questions", [])
        for q in questions_config:
            if q.get("field") == current_field:
                current_field_label = q.get("question", current_field).replace("을/를 알려주세요.", "").replace("은/는 몇 명인가요?", "").strip()
                break
    
    # 1) 키워드 기반 1차 분류
    classification = classify_input(user_input)
    print(f"[DEBUG] simulate_llm_response 분류 결과: {classification}")
    print(f"[DEBUG] 분류 타입: {classification['type']}")
    print(f"[DEBUG] 분류 카테고리: {classification.get('category', 'N/A')}")
    print(f"[DEBUG] 분류 값: {classification.get('value', 'N/A')}")
    
    # 2) 분류된 결과에 따른 처리
    if classification['type'] == 'field':
        # 필드 값으로 처리
        field_value = classification.get('value', user_input.strip())
        return {
            "field": current_field,
            "value": field_value,
            "message": f"{classification['category']}: {field_value}로 설정되었습니다.",
            "is_conversation": False
        }
        
    elif classification['type'] == 'question':
        # 3) Gemini API 호출로 답변 생성 (AI 도우미 컨텍스트 포함)
        try:
            # AI 도우미용 컨텍스트 추가
            ai_assistant_context = f"""
현재 채용 공고 작성 중입니다. 현재 필드: {current_field_label} ({current_field})

사용자 질문: {user_input}

이 질문에 대해 채용 공고 작성에 도움이 되는 실무적인 답변을 제공해주세요.
"""
            ai_response = await call_openai_api(ai_assistant_context)
            return {
                "message": ai_response,
                "is_conversation": True
            }
        except Exception as e:
            print(f"[ERROR] OpenAI API 호출 실패: {e}")
            return {
                "message": f"{current_field_label}에 대한 질문이군요. 구체적으로 어떤 부분이 궁금하신가요?",
                "is_conversation": True
            }
            
    elif classification['type'] == 'chat':
        # 일상 대화 처리
        return {
            "message": "안녕하세요! 채용 관련 문의사항이 있으시면 언제든 말씀해 주세요.",
            "is_conversation": True
        }
        
    else:
        # 답변인 경우 기본 처리 (자동 완성)
        extracted_value = user_input.strip()
        
        # 기본적인 형식 검증
        if current_field == "headcount":
            import re
            match = re.search(r'(\d+)\s*명|(\d+)', user_input)
            if match:
                extracted_value = f"{match.group(1) or match.group(2)}명"
        elif current_field == "email":
            if "@" not in extracted_value:
                return {
                    "message": "이메일 형식이 올바르지 않습니다. '@'가 포함된 이메일 주소를 입력해주세요.",
                    "is_conversation": True
                }
        
        # 확인 메시지 생성
        confirmation_message = f"'{current_field_label}'에 대해 '{extracted_value}'로 입력하겠습니다."

        result = {
            "field": current_field,
            "value": extracted_value,
            "message": confirmation_message,
            "is_conversation": False
        }
        print("[DEBUG] ===== simulate_llm_response 결과 =====")
        print("[DEBUG] 최종 결과:", result)
        print("[DEBUG] ===== simulate_llm_response 완료 =====")
        return result

async def call_openai_api(prompt: str, conversation_history: List[Dict[str, Any]] = None) -> str:
    """
    OpenAI API 호출 함수
    """
    try:
        if not client:
            return "AI 서비스를 사용할 수 없습니다. 다시 시도해 주세요."
        
        # 대화 히스토리 구성
        messages = []
        if conversation_history:
            for msg in conversation_history:
                role = 'user' if msg.get('type') == 'user' else 'assistant'
                messages.append({"role": role, "content": msg.get('content', '')})
        
        # 컨텍스트가 포함된 프롬프트 생성
        context_prompt = f"""
당신은 채용 전문 어시스턴트입니다. 사용자가 채용 공고 작성이나 채용 관련 질문을 할 때 전문적이고 실용적인 답변을 제공해주세요.

**주의사항:**
- AI 모델에 대한 설명은 하지 마세요
- 채용 관련 실무적인 조언을 제공하세요
- 구체적이고 실용적인 답변을 해주세요
- 한국어로 답변해주세요
- 모든 답변은 핵심만 간단하게 요약해서 2~3줄 이내로 작성해주세요
- 불필요한 설명은 생략하고, 요점 위주로 간결하게 답변해주세요
- '주요 업무'를 작성할 때는 지원자 입장에서 직무 이해도가 높아지도록 구체적인 동사(예: 개발, 분석, 관리 등)를 사용하세요
- 각 업무는 “무엇을 한다 → 왜 한다” 구조로, 기대 성과까지 간결히 포함해서 자연스럽고 명확하게 서술하세요
- 번호가 있는 항목(1, 2, 3 등)은 각 줄마다 줄바꿈하여 출력해주세요

**특별 지시:**  
사용자가 '적용해줘', '입력해줘', '이걸로 해줘' 등의 선택적 명령어를 입력하면,  
직전 AI가 제시한 내용을 그대로 적용하는 동작으로 이해하고,  
사용자가 추가 설명을 요청하지 않는 이상 답변을 간단히 요약하며 다음 단계로 자연스럽게 넘어가세요.

**사용자 질문:** {prompt}

위 질문에 대해 채용 전문가 관점에서 답변해주세요.
"""

        messages.append({"role": "user", "content": context_prompt})
        
        # OpenAI API 호출
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[ERROR] OpenAI API 호출 실패: {e}")
        return f"AI 응답을 가져오는 데 실패했습니다. 다시 시도해 주세요. (오류: {str(e)})"

@router.post("/suggestions")
async def get_suggestions(request: SuggestionsRequest):
    """필드별 제안 가져오기"""
    print("[DEBUG] /suggestions 요청:", request)
    suggestions = get_field_suggestions(request.field, request.context)
    response = {"suggestions": suggestions}
    print("[DEBUG] /suggestions 응답:", response)
    return response

@router.post("/validate")
async def validate_field(request: ValidationRequest):
    """필드 값 검증"""
    print("[DEBUG] /validate 요청:", request)
    validation_result = validate_field_value(request.field, request.value, request.context)
    response = validation_result
    print("[DEBUG] /validate 응답:", response)
    return response

@router.post("/autocomplete")
async def smart_autocomplete(request: AutoCompleteRequest):
    """스마트 자동 완성"""
    print("[DEBUG] /autocomplete 요청:", request)
    completions = get_autocomplete_suggestions(request.partial_input, request.field, request.context)
    response = {"completions": completions}
    print("[DEBUG] /autocomplete 응답:", response)
    return response

@router.post("/recommendations")
async def get_recommendations(request: RecommendationsRequest):
    """컨텍스트 기반 추천"""
    print("[DEBUG] /recommendations 요청:", request)
    recommendations = get_contextual_recommendations(request.current_field, request.filled_fields, request.context)
    response = {"recommendations": recommendations}
    print("[DEBUG] /recommendations 응답:", response)
    return response

@router.post("/update-field")
async def update_field_in_realtime(request: FieldUpdateRequest):
    """실시간 필드 업데이트"""
    print("[DEBUG] /update-field 요청:", request)
    if request.session_id in modal_sessions:
        modal_sessions[request.session_id]["filled_fields"][request.field] = request.value
        response = {"status": "success", "message": "필드가 업데이트되었습니다."}
        print("[DEBUG] /update-field 응답:", response)
        return response
    else:
        print("[ERROR] /update-field 유효하지 않은 세션:", request.session_id)
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")

@router.post("/end")
async def end_session(request: dict):
    """세션 종료"""
    print("[DEBUG] /end 요청:", request)
    session_id = request.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    if session_id in modal_sessions:
        del modal_sessions[session_id]
    response = {"status": "success", "message": "세션이 종료되었습니다."}
    print("[DEBUG] /end 응답:", response)
    return response

def get_questions_for_page(page: str) -> List[Dict[str, Any]]:
    """페이지별 질문 목록"""
    print("[DEBUG] get_questions_for_page 요청:", page)
    questions_map = {
        "job_posting": [
            {"field": "department", "question": "구인 부서를 알려주세요."},
            {"field": "headcount", "question": "채용 인원은 몇 명인가요?"},
            {"field": "workType", "question": "어떤 업무를 담당하게 되나요?"},
            {"field": "workHours", "question": "근무 시간은 어떻게 되나요?"},
            {"field": "location", "question": "근무 위치는 어디인가요?"},
            {"field": "salary", "question": "급여 조건은 어떻게 되나요?"},
            {"field": "deadline", "question": "마감일은 언제인가요?"},
            {"field": "email", "question": "연락처 이메일을 알려주세요."}
        ]
    }
    questions = questions_map.get(page, [])
    print("[DEBUG] get_questions_for_page 응답:", questions)
    return questions

def get_field_suggestions(field: str, context: Dict[str, Any]) -> List[str]:
    """필드별 제안 목록"""
    print("[DEBUG] get_field_suggestions 요청:", field, context)
    suggestions_map = {
        "department": ["개발팀", "마케팅팀", "영업팀", "디자인팀", "기획팀"],
        "headcount": ["1명", "2명", "3명", "5명", "10명"],
        "workType": ["웹 개발", "앱 개발", "디자인", "마케팅", "영업"],
        "workHours": ["09:00-18:00", "10:00-19:00", "유연근무제"],
        "location": ["서울", "부산", "대구", "인천", "대전"],
        "salary": ["면접 후 협의", "3000만원", "4000만원", "5000만원"],
        "deadline": ["2024년 12월 31일", "2024년 11월 30일", "채용 시 마감"],
        "email": ["hr@company.com", "recruit@company.com"]
    }
    suggestions = suggestions_map.get(field, [])
    print("[DEBUG] get_field_suggestions 응답:", suggestions)
    return suggestions

def validate_field_value(field: str, value: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """필드 값 검증"""
    print("[DEBUG] validate_field_value 요청:", field, value, context)
    if field == "email" and "@" not in value:
        response = {"valid": False, "message": "올바른 이메일 형식을 입력해주세요."}
        print("[DEBUG] validate_field_value 응답 (이메일 형식 오류):", response)
        return response
    elif field == "headcount" and not any(char.isdigit() for char in value):
        response = {"valid": False, "message": "숫자를 포함한 인원 수를 입력해주세요."}
        print("[DEBUG] validate_field_value 응답 (헤드카운트 숫자 오류):", response)
        return response
    else:
        response = {"valid": True, "message": "올바른 형식입니다."}
        print("[DEBUG] validate_field_value 응답 (유효):", response)
        return response

def get_autocomplete_suggestions(partial_input: str, field: str, context: Dict[str, Any]) -> List[str]:
    """자동 완성 제안"""
    print("[DEBUG] get_autocomplete_suggestions 요청:", partial_input, field, context)
    suggestions = get_field_suggestions(field, context)
    completions = [s for s in suggestions if partial_input.lower() in s.lower()]
    print("[DEBUG] get_autocomplete_suggestions 응답:", completions)
    return completions

def get_contextual_recommendations(current_field: str, filled_fields: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
    """컨텍스트 기반 추천"""
    print("[DEBUG] get_contextual_recommendations 요청:", current_field, filled_fields, context)
    if current_field == "workType" and filled_fields.get("department") == "개발팀":
        recommendations = ["웹 개발", "앱 개발", "백엔드 개발", "프론트엔드 개발"]
    elif current_field == "salary" and filled_fields.get("workType") == "개발":
        recommendations = ["4000만원", "5000만원", "6000만원", "면접 후 협의"]
    else:
        recommendations = get_field_suggestions(current_field, context)
    print("[DEBUG] get_contextual_recommendations 응답:", recommendations)
    return recommendations

@router.post("/chat")
async def chat_endpoint(request: ChatbotRequest):
    """
    키워드 기반 1차 분류 → LLM 호출 → 응답 처리 API
    """
    print("[DEBUG] /chat 요청:", request)
    
    try:
        user_input = request.user_input
        conversation_history = request.conversation_history
        
        if not user_input:
            raise HTTPException(status_code=400, detail="사용자 입력이 필요합니다.")
        
        # 1) 키워드 기반 1차 분류
        classification = classify_input(user_input)
        print(f"[DEBUG] /chat 분류 결과: {classification}")
        
        # 2) 분류된 결과에 따른 처리
        if classification['type'] == 'field':
            # 필드 값으로 처리
            field_value = classification.get('value', user_input.strip())
            response = {
                "type": "field",
                "content": f"{classification['category']}: {field_value}로 설정되었습니다.",
                "value": field_value,
                "confidence": classification['confidence']
            }
            
        elif classification['type'] == 'question':
            # 3) OpenAI API 호출로 답변 생성
            ai_response = await call_openai_api(user_input, conversation_history)
            response = {
                "type": "answer",
                "content": ai_response,
                "confidence": classification['confidence']
            }
            
        elif classification['type'] == 'chat':
            # 일상 대화 처리
            response = {
                "type": "chat",
                "content": "안녕하세요! 채용 관련 문의사항이 있으시면 언제든 말씀해 주세요.",
                "confidence": classification['confidence']
            }
            
        else:
            # 답변인 경우 기본 처리 (자동 완성)
            response = {
                "type": "answer",
                "content": f"'{user_input}'로 입력하겠습니다. 다음 단계로 진행하겠습니다.",
                "value": user_input.strip(),
                "confidence": classification['confidence']
            }
        
        print("[DEBUG] /chat 응답:", response)
        return response
        
    except Exception as e:
        print(f"[ERROR] /chat 예외: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")