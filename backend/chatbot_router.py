from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import asyncio
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# --- Gemini API 설정 추가 시작 ---
import google.generativeai as genai

# 환경 변수에서 Gemini API 키 로드
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

# API 키가 없어도 기본 응답을 반환하도록 수정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Gemini 모델 초기화
    # 'gemini-1.5-flash'는 텍스트 기반 모델입니다. 이미지 등을 처리하려면 다른 모델(예: 'gemini-1.5-pro')을 사용할 수 있습니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("Warning: GOOGLE_API_KEY not found. Using fallback responses.")
    model = None
# --- Gemini API 설정 추가 끝 ---

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
    session_id = str(uuid.uuid4())
    
    if request.mode == "modal_assistant":
        # 모달 어시스턴트 모드 (세션 유지)
        if not request.fields:
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
        return SessionStartResponse(
            session_id=session_id,
            question=f"안녕하세요! {request.page} 작성을 도와드리겠습니다. 🤖\n\n먼저 {first_field.get('label', '첫 번째 항목')}에 대해 알려주세요.",
            current_field=first_field.get('key', 'unknown')
        )
    else:
        # 기존 일반 모드 (여전히 세션 사용하나, /ask 엔드포인트는 이제 세션 없이 동작 가능)
        questions = get_questions_for_page(request.page)
        sessions[session_id] = {
            "page": request.page,
            "questions": questions,
            "current_index": 0,
            "current_field": questions[0]["field"] if questions else None,
            "conversation_history": [],
            "mode": "normal"
        }
        
        return SessionStartResponse(
            session_id=session_id,
            question=questions[0]["question"] if questions else "질문이 없습니다.",
            current_field=questions[0]["field"] if questions else None
        )

@router.post("/start-ai-assistant", response_model=SessionStartResponse)
async def start_ai_assistant(request: SessionStartRequest):
    """AI 도우미 모드 시작"""
    session_id = str(uuid.uuid4())
    
    # AI 도우미용 필드 정의
    ai_assistant_fields = [
        {"key": "department", "label": "구인 부서", "type": "text"},
        {"key": "headcount", "label": "채용 인원", "type": "text"},
        {"key": "workType", "label": "업무 내용", "type": "text"},
        {"key": "workHours", "label": "근무 시간", "type": "text"},
        {"key": "location", "label": "근무 위치", "type": "text"},
        {"key": "salary", "label": "급여 조건", "type": "text"},
        {"key": "deadline", "label": "마감일", "type": "text"},
        {"key": "email", "label": "연락처 이메일", "type": "email"}
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
    return SessionStartResponse(
        session_id=session_id,
        question=f"🤖 AI 채용공고 작성 도우미를 시작하겠습니다!\n\n먼저 {first_field.get('label', '첫 번째 항목')}에 대해 알려주세요.",
        current_field=first_field.get('key', 'unknown')
    )

@router.post("/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    # 일반 대화 모드 (session_id 없이 conversation_history로 컨텍스트 유지)
    if request.mode == "normal" or not request.session_id: # session_id가 없으면 normal 모드로 간주
        return await handle_normal_request(request)
    # 모달 어시스턴트 모드 (session_id를 통해 세션 상태 유지)
    elif request.mode == "modal_assistant":
        return await handle_modal_assistant_request(request)
    else:
        # 기타 모드 처리 (예: "ai_assistant"는 ai_assistant_chat으로 라우팅됨)
        raise HTTPException(status_code=400, detail="알 수 없는 챗봇 모드입니다.")

@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest):
    """대화형 질문-답변 처리"""
    try:
        # 대화형 응답 생성 (이 함수도 필요하다면 Gemini API 연동 고려)
        response = await generate_conversational_response(
            request.user_input, 
            request.current_field, 
            request.filled_fields
        )
        
        return ConversationResponse(
            message=response["message"],
            is_conversation=response.get("is_conversation", True),
            suggestions=response.get("suggestions", []),
            field=response.get("field"),
            value=response.get("value")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 처리 오류: {str(e)}")

@router.post("/generate-questions", response_model=Dict[str, Any])
async def generate_contextual_questions(request: GenerateQuestionsRequest):
    """컨텍스트 기반 질문 생성"""
    try:
        questions = await generate_field_questions(
            request.current_field, 
            request.filled_fields
        )
        
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 생성 오류: {str(e)}")

@router.post("/ai-assistant-chat", response_model=ChatbotResponse)
async def ai_assistant_chat(request: ChatbotRequest):
    """AI 도우미 채팅 처리 (session_id 필요)"""
    if not request.session_id or request.session_id not in modal_sessions:
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")
    
    session = modal_sessions[request.session_id]
    current_field_index = session["current_field_index"]
    fields = session["fields"]
    
    if current_field_index >= len(fields):
        return ChatbotResponse(
            message="🎉 모든 정보를 입력받았습니다! 채용공고 등록이 완료되었습니다."
        )
    
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
    
    return ChatbotResponse(
        message=ai_response["message"],
        field=current_field["key"],
        value=ai_response.get("value"),
        suggestions=ai_response.get("suggestions", []),
        confidence=ai_response.get("confidence", 0.8)
    )

async def handle_modal_assistant_request(request: ChatbotRequest):
    """모달 어시스턴트 모드 처리 (session_id 필요)"""
    if not request.session_id or request.session_id not in modal_sessions:
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")
    
    session = modal_sessions[request.session_id]
    current_field_index = session["current_field_index"]
    fields = session["fields"]
    
    if current_field_index >= len(fields):
        return ChatbotResponse(
            message="모든 정보를 입력받았습니다! 완료 버튼을 눌러주세요. 🎉"
        )
    
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
    
    return ChatbotResponse(
        message=response_message,
        field=current_field["key"] if not llm_response.get("is_conversation", True) else None, # 대화형 응답 시 필드 값은 비워둘 수 있음
        value=llm_response.get("value"),
        suggestions=llm_response.get("suggestions", []), # LLM이 제안을 생성할 수 있다면 활용
        confidence=llm_response.get("confidence", 0.8) # LLM이 confidence를 반환할 수 있다면 활용
    )

async def handle_normal_request(request: ChatbotRequest):
    """
    일반 챗봇 요청 처리 (세션 ID 없이 conversation_history로 컨텍스트 유지)
    이 부분이 실제 Gemini API와 연동됩니다.
    """
    user_input = request.user_input
    # 프론트엔드에서 넘어온 대화 기록 (type: 'user'/'bot')
    conversation_history_from_frontend = request.conversation_history

    if not user_input:
        raise HTTPException(status_code=400, detail="사용자 입력이 필요합니다.")

    try:
        # Gemini API에 전달할 대화 기록 구성
        # 프론트엔드에서 넘어온 history 형식을 Gemini API의 'role'과 'parts' 형식으로 변환
        gemini_history = []
        for msg in conversation_history_from_frontend:
            role = 'user' if msg.get('type') == 'user' else 'model' # 'bot'을 'model'로 변환
            gemini_history.append({"role": role, "parts": [{"text": msg.get('content', '')}]})
        
        # 현재 사용자 입력 추가
        full_history_for_gemini = gemini_history + [{'role': 'user', 'parts': [{'text': user_input}]}]

        # Gemini 모델 호출
        # 안전 설정을 기본으로 적용합니다. 필요에 따라 변경 가능합니다.
        # https://ai.google.dev/docs/safety_setting_gemini
        gemini_response_obj = await model.generate_content_async( # 비동기 호출로 변경
            full_history_for_gemini,
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE_SPEECH": "BLOCK_NONE",
                "SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )
        
        # 텍스트 응답 추출
        gemini_response_text = gemini_response_obj.text

        # 클라이언트에 응답 반환
        return ChatbotResponse(
            message=gemini_response_text,
            field=None,  # 일반 대화에서는 특정 필드 지정하지 않음
            value=None,  # 일반 대화에서는 특정 값 추출하지 않음
            suggestions=[], # 필요하다면 Gemini 응답에서 제안을 추출하여 제공
            confidence=1.0 # Gemini 응답이므로 높은 신뢰도
        )

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # 오류 발생 시 사용자에게 친화적인 메시지 반환
        return ChatbotResponse(
            message=f"죄송합니다. AI 응답을 가져오는 데 실패했습니다. 다시 시도해 주세요. (오류: {str(e)})",
            field=None,
            value=None
        )

# 이 아래 함수들은 현재 시뮬레이션된 응답 로직을 사용합니다.
# 만약 이 함수들도 실제 Gemini API와 연동하고 싶으시다면,
# 해당 함수 내부에 Gemini API 호출 로직을 추가해야 합니다.
async def generate_conversational_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """대화형 응답 생성"""
    await asyncio.sleep(0.5)
    
    question_keywords = ["어떤", "무엇", "어떻게", "왜", "언제", "어디서", "얼마나", "몇", "무슨"]
    is_question = any(keyword in user_input for keyword in question_keywords) or user_input.endswith("?")
    
    if is_question:
        return await handle_question_response(user_input, current_field, filled_fields)
    else:
        return await handle_answer_response(user_input, current_field, filled_fields)

async def handle_question_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """질문에 대한 응답 처리"""
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
            return {
                "message": response,
                "is_conversation": True,
                "suggestions": list(field_responses.keys())
            }
    
    return {
        "message": f"{current_field}에 대한 질문이군요. 더 구체적으로 어떤 부분이 궁금하신지 말씀해 주세요.",
        "is_conversation": True,
        "suggestions": list(field_responses.keys())
    }

async def handle_answer_response(user_input: str, current_field: str, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
    """답변 처리"""
    return {
        "message": f"'{user_input}'로 입력하겠습니다. 다음 질문으로 넘어가겠습니다.",
        "field": current_field,
        "value": user_input,
        "is_conversation": False
    }

async def generate_field_questions(current_field: str, filled_fields: Dict[str, Any]) -> List[str]:
    """필드별 질문 생성"""
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
    
    return questions_map.get(current_field, [
        "이 항목에 대해 궁금한 점이 있으신가요?",
        "더 자세한 설명이 필요하신가요?",
        "예시를 들어 설명해드릴까요?"
    ])

async def generate_modal_ai_response(user_input: str, field: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """모달 어시스턴트용 AI 응답 생성 (시뮬레이션)"""
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
    
    return responses.get(field_key, {
        "message": f"{field_label} 정보를 확인했습니다. 다음 질문으로 넘어가겠습니다.",
        "value": user_input,
        "suggestions": [],
        "confidence": 0.5
    })

async def generate_ai_assistant_response(user_input: str, field: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """AI 도우미용 응답 생성 (시뮬레이션)"""
    field_key = field.get("key", "")
    field_label = field.get("label", "")
    
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
        "workType": {
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
        "location": {
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
        "email": {
            "message": f"연락처 이메일 '{user_input}'으로 입력하겠습니다. 모든 정보 입력이 완료되었습니다!",
            "value": user_input,
            "suggestions": [],
            "confidence": 0.9
        }
    }
    
    return responses.get(field_key, {
        "message": f"{field_label} 정보를 확인했습니다. 다음 질문으로 넘어가겠습니다.",
        "value": user_input,
        "suggestions": [],
        "confidence": 0.5
    })

async def simulate_llm_response(user_input: str, current_field: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM 응답을 시뮬레이션하여 사람과 대화하는 것처럼 자연스러운 반응을 생성합니다.
    인사 담당자님의 채용공고 등록을 돕는 AI 어시스턴트 역할을 수행합니다.
    """
    await asyncio.sleep(0.5) # 실제 LLM API 호출 시뮬레이션

    # 세션에서 대화 히스토리와 현재까지 채워진 필드 정보 가져오기
    # conversation_history = session.get("conversation_history", []) # 현재 함수에서 사용하지 않음
    # filled_fields = session.get("filled_fields", {}) # 현재 함수에서 사용하지 않음

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
    
    # --- 1단계: 사용자 발화 의도 파악 ---
    # 사용자가 챗봇에게 질문을 던졌는지 판단
    question_phrases = ["어떤", "무엇", "어떻게", "왜", "언제", "어디서", "얼마나", "몇", "무슨", "궁금", "알려줘", "설명해줘", "뭐가 좋을까요", "어떤게 있나요", "어떻게 작성해야 할까요", "이름이 뭐야", "너는 누구니"]
    is_user_asking_question = any(phrase in user_input.lower() for phrase in question_phrases) or user_input.strip().endswith("?")

    # 사용자가 불확실하거나 도움을 요청하는지 판단
    uncertainty_phrases = ["음...", "글쎄요", "잘 모르겠어요", "고민 중", "생각 중", "어렵네요", "추천해줘", "도와줘", "예시", "보통 이럴때 무슨 말들을 쓸까"]
    is_user_uncertain_or_seeking_help = any(phrase in user_input.lower() for phrase in uncertainty_phrases)

    # --- 2단계: 의도에 따른 응답 생성 ---

    # 2-1. 사용자가 챗봇 자체에 대해 질문한 경우
    if any(kw in user_input.lower() for kw in ["이름이 뭐야", "너는 누구니", "봇", "ai"]):
        return {
            "message": f"안녕하세요! 저는 인사 담당자님의 채용공고 작성을 도와드리는 AI 어시스턴트입니다. 지금 {current_field_label} 정보를 입력받고 있어요. 혹시 이 부분에 대해 궁금한 점이 있으신가요, 아니면 어떤 내용을 입력할지 알려주실 수 있을까요?",
            "is_conversation": True # 대화형 응답
        }

    # 2-2. 사용자가 현재 필드에 대해 질문하거나 도움을 요청한 경우 (매우 중요)
    if is_user_asking_question or is_user_uncertain_or_seeking_help:
        # 필드별 질문 답변 및 도움말 제공
        response_map_for_questions = {
            "department": {
                "general_q": "구인 부서는 채용할 인력이 소속될 부서를 의미합니다. 예를 들어 '개발팀', '마케팅팀', '영업팀' 등이 될 수 있어요. 어떤 부서에서 인력이 필요하신가요?",
                "what_to_write": "부서명은 일반적으로 '개발팀', '기획팀', '영업팀'처럼 명확하게 작성하시면 됩니다. 특정 팀이 없다면 '경영지원팀'이나 '사업부' 등으로 기재할 수도 있고요. 어떤 부서를 채용하고 싶으신가요?",
                "example": "예시로는 '프론트엔드 개발팀', '글로벌 마케팅팀', 'B2B 영업팀' 등이 있습니다. 어떤 부서를 찾고 계신가요?",
            },
            "headcount": {
                "general_q": "채용 인원은 말 그대로 몇 명의 직원을 뽑을지 묻는 항목입니다. 1명, 2명 등으로 정확히 알려주시면 돼요. 몇 분을 채용하실 계획이신가요?",
                "what_to_write": "채용 인원은 숫자로 기재하시면 됩니다. '1명', '3명' 처럼요. 필요에 따라 '0명 (충원 완료)' 또는 'N명 (상시)'으로 표기할 수도 있습니다. 몇 명을 채용하시겠어요?",
                "example": "예시로 '1명', '2명', '3명 이상' 등이 있습니다. 몇 분을 채용하실 예정이세요?",
            },
            "workType": {
                "general_q": "주요 업무는 채용될 직원이 어떤 일을 하게 될지 구체적으로 명시하는 부분입니다. 지원자들이 자신의 역량과 맞는지 판단할 중요한 기준이 되죠. 어떤 업무를 담당할 예정인가요?",
                "what_to_write": "주요 업무는 구체적인 직무 내용을 담는 것이 좋습니다. 예를 들어 '백엔드 서비스 개발 및 운영', '신규 모바일 앱 UI/UX 디자인', '디지털 마케팅 전략 수립 및 실행'처럼요. 어떤 업무를 담당할 인력을 찾고 계신가요?",
                "example": "예시로는 'Python 기반 웹 백엔드 개발', '광고 캠페인 기획 및 성과 분석', '신규 고객사 발굴 및 계약 관리' 등이 있습니다. 어떤 주요 업무를 입력하시겠어요?",
            },
            "workHours": {
                "general_q": "근무 시간은 채용될 직원의 근무 스케줄을 나타냅니다. 보통 정규 근무 시간, 유연근무 여부, 재택근무 가능 여부 등을 기재해요. 근무 시간은 어떻게 되나요?",
                "what_to_write": "일반적으로 '주 5일, 09:00 ~ 18:00' 형태로 기재합니다. 유연근무나 재택근무가 가능하다면 '주 5일 (유연근무 가능)', '재택근무 병행 가능' 등으로 명시할 수 있어요. 희망하는 근무 시간을 알려주세요.",
                "example": "예시: '주 5일, 10:00 ~ 19:00', '주 5일 (유연근무제)', '탄력 근무제 (협의 후 결정)'. 어떻게 기재하시겠어요?",
            },
            "location": {
                "general_q": "근무 위치는 직무가 수행될 실제 장소를 의미합니다. 정확한 주소나 최소한 도시/구 단위까지 명시하는 것이 좋아요. 근무지는 어디로 등록하시겠어요?",
                "what_to_write": "근무 위치는 정확한 주소(예: '서울특별시 강남구 테헤란로 123')를 기재하거나, 최소한 '서울시 강남구', '경기도 성남시 분당구' 등으로 명확히 작성해 주세요. 만약 원격 근무가 기본이라면 '원격 근무 (전국)' 등으로 기재할 수도 있습니다. 근무 위치를 알려주시겠어요?",
                "example": "예시: '서울특별시 서초구 서초대로 123 (강남역 부근)', '판교 테크노밸리', '전국 (원격근무)'. 어디로 입력하시겠어요?",
            },
            "salary": {
                "general_q": "급여 조건은 채용될 직원의 보수와 관련된 부분입니다. 연봉, 월급, 또는 면접 후 협의 등으로 기재할 수 있어요. 급여 조건은 어떻게 되나요?",
                "what_to_write": "급여는 연봉 또는 월급으로 구체적인 액수를 기재하거나, '면접 후 협의'로 표기할 수 있습니다. 예를 들어 '연봉 3,500만원 이상', '월 250만원', '면접 후 협의' 등으로 기재할 수 있어요. 급여 조건은 어떻게 설정하시겠어요?",
                "example": "예시: '연봉 4,000만원 ~ 5,000만원', '면접 후 협의 (경력에 따라 차등)', '회사 내규에 따름'. 어떻게 작성하시겠어요?",
            },
            "deadline": {
                "general_q": "마감일은 지원서를 제출할 수 있는 최종 기한입니다. 보통 특정 날짜를 지정하거나, '채용 시 마감'으로 설정하기도 해요. 언제까지 지원을 받을 예정이신가요?",
                "what_to_write": "마감일은 'YYYY년 MM월 DD일' 형식으로 기재하거나, '채용 시 마감'이라고 명시할 수 있습니다. 예를 들어 '2025년 7월 31일' 또는 '채용 완료 시'처럼요. 언제로 마감일을 설정하시겠어요?",
                "example": "예시: '2025년 8월 15일', '별도 공지 시까지', '상시 채용'. 언제로 마감하시겠어요?",
            },
            "email": {
                "general_q": "연락처 이메일은 지원자들이 궁금한 점이 있을 때 문의할 수 있는 담당자의 이메일 주소입니다. 이메일 주소를 알려주세요.",
                "what_to_write": "지원자들에게 노출될 담당자 이메일 주소를 입력하시면 됩니다. 'recruit@company.com'과 같은 채용 전용 이메일을 사용하시는 것이 일반적입니다. 어떤 이메일 주소를 기재하시겠어요?",
                "example": "예시: 'hr@yourcompany.com', 'recruit@example.co.kr'. 이메일 주소를 알려주세요.",
            }
        }
        
        if "어떻게 작성해야 할까요" in user_input or "뭐가 좋을까요" in user_input or "어떤게 있나요" in user_input or "보통 이럴때 무슨 말들을 쓸까" in user_input:
            message = response_map_for_questions.get(current_field, {}).get("what_to_write", f"{current_field_label}을/를 어떻게 작성할지 궁금하시군요. 일반적으로 이렇게 작성합니다: (관련 예시/설명 추가). 어떤 내용을 입력하고 싶으신가요?")
        elif "예시" in user_input:
            message = response_map_for_questions.get(current_field, {}).get("example", f"{current_field_label}에 대한 예시를 찾으시는군요. 다음과 같은 예시가 있습니다: (관련 예시 추가). 어떤 내용을 입력하시겠어요?")
        else:
            message = response_map_for_questions.get(current_field, {}).get("general_q", f"{current_field_label}에 대해 궁금하신 점이 있으시군요. 어떤 부분이 더 궁금하신가요? 아니면 정보를 알려주시면 다음으로 진행할 수 있습니다. 😊")
        
        return {
            "message": message,
            "is_conversation": True
        }

    # 2-3. 사용자가 현재 필드에 대한 명확한 답변을 제공한 경우
    extracted_value = user_input.strip() 

    if current_field == "headcount":
        import re
        match = re.search(r'(\d+)\s*명|(\d+)', user_input)
        if match:
            extracted_value = f"{match.group(1) or match.group(2)}명"
        else:
            return {
                "message": f"몇 분을 채용하실지 숫자로 알려주실 수 있을까요? 예를 들어 '2명'처럼요. 😊",
                "is_conversation": True
            }
    elif current_field == "email":
        if "@" not in extracted_value:
            return {
                "message": "이메일 형식이 올바르지 않은 것 같아요. '@'가 포함된 정확한 이메일 주소를 알려주실 수 있을까요?",
                "is_conversation": True
            }
    elif current_field == "salary":
        if "만원" in extracted_value or "협의" in extracted_value or "내규" in extracted_value or "면접" in extracted_value:
            pass
        else:
            return {
                "message": "급여 조건은 '연봉 3000만원' 또는 '면접 후 협의'처럼 구체적으로 알려주시면 감사하겠습니다. 어떻게 기재하시겠어요?",
                "is_conversation": True
            }
            
    confirmation_message = ""
    if current_field == "department":
        confirmation_message = f"네, **'{extracted_value}'** 부서로 확인했습니다. 잘 알겠습니다!"
    elif current_field == "headcount":
        confirmation_message = f"**'{extracted_value}'**을/를 채용하시는군요. 알겠습니다!"
    elif current_field == "workType":
        confirmation_message = f"주요 업무는 **'{extracted_value}'**이군요. 상세하게 잘 적어주셨어요!"
    elif current_field == "workHours":
        confirmation_message = f"**'{extracted_value}'**으로 근무 시간을 확인했습니다. 좋아요!"
    elif current_field == "location":
        confirmation_message = f"근무 위치는 **'{extracted_value}'**이군요. 확인했습니다!"
    elif current_field == "salary":
        confirmation_message = f"급여 조건은 **'{extracted_value}'**으로 설정하시는군요. 알겠습니다!"
    elif current_field == "deadline":
        confirmation_message = f"마감일은 **'{extracted_value}'**이군요. 확인했습니다!"
    elif current_field == "email":
        confirmation_message = f"연락처 이메일은 **'{extracted_value}'**으로 등록해 드릴게요. 모든 정보가 입력되었습니다!"
    else:
        confirmation_message = f"**'{current_field_label}'**에 대해 **'{extracted_value}'**이라고 말씀해주셨군요. 확인했습니다!"

    return {
        "field": current_field,
        "value": extracted_value,
        "message": confirmation_message,
        "is_conversation": False
    }
    
@router.post("/suggestions")
async def get_suggestions(request: SuggestionsRequest):
    """필드별 제안 가져오기"""
    suggestions = get_field_suggestions(request.field, request.context)
    return {"suggestions": suggestions}

@router.post("/validate")
async def validate_field(request: ValidationRequest):
    """필드 값 검증"""
    validation_result = validate_field_value(request.field, request.value, request.context)
    return validation_result

@router.post("/autocomplete")
async def smart_autocomplete(request: AutoCompleteRequest):
    """스마트 자동 완성"""
    completions = get_autocomplete_suggestions(request.partial_input, request.field, request.context)
    return {"completions": completions}

@router.post("/recommendations")
async def get_recommendations(request: RecommendationsRequest):
    """컨텍스트 기반 추천"""
    recommendations = get_contextual_recommendations(request.current_field, request.filled_fields, request.context)
    return {"recommendations": recommendations}

@router.post("/update-field")
async def update_field_in_realtime(request: FieldUpdateRequest):
    """실시간 필드 업데이트"""
    if request.session_id in modal_sessions:
        modal_sessions[request.session_id]["filled_fields"][request.field] = request.value
        return {"status": "success", "message": "필드가 업데이트되었습니다."}
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")

@router.post("/end")
async def end_session(request: dict):
    """세션 종료"""
    session_id = request.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    if session_id in modal_sessions:
        del modal_sessions[session_id]
    return {"status": "success", "message": "세션이 종료되었습니다."}

def get_questions_for_page(page: str) -> List[Dict[str, Any]]:
    """페이지별 질문 목록"""
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
    return questions_map.get(page, [])

def get_field_suggestions(field: str, context: Dict[str, Any]) -> List[str]:
    """필드별 제안 목록"""
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
    return suggestions_map.get(field, [])

def validate_field_value(field: str, value: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """필드 값 검증"""
    if field == "email" and "@" not in value:
        return {"valid": False, "message": "올바른 이메일 형식을 입력해주세요."}
    elif field == "headcount" and not any(char.isdigit() for char in value):
        return {"valid": False, "message": "숫자를 포함한 인원 수를 입력해주세요."}
    else:
        return {"valid": True, "message": "올바른 형식입니다."}

def get_autocomplete_suggestions(partial_input: str, field: str, context: Dict[str, Any]) -> List[str]:
    """자동 완성 제안"""
    suggestions = get_field_suggestions(field, context)
    return [s for s in suggestions if partial_input.lower() in s.lower()]

def get_contextual_recommendations(current_field: str, filled_fields: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
    """컨텍스트 기반 추천"""
    if current_field == "workType" and filled_fields.get("department") == "개발팀":
        return ["웹 개발", "앱 개발", "백엔드 개발", "프론트엔드 개발"]
    elif current_field == "salary" and filled_fields.get("workType") == "개발":
        return ["4000만원", "5000만원", "6000만원", "면접 후 협의"]
    else:
        return get_field_suggestions(current_field, context)