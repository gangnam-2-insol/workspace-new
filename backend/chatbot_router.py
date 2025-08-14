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
import google.generativeai as genai
import numpy as np # numpy 라이브러리 추가
from gemini_service import GeminiService
from resume_analyzer import extract_resume_info_from_text
from agent_system import agent_system

# 고급 NLP 라이브러리 추가
try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
    okt = Okt()
    print("KoNLPy 초기화 성공")
except (ImportError, Exception) as e:
    KONLPY_AVAILABLE = False
    print(f"[WARNING] KoNLPy not available: {e}. Using basic tokenization.")

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    embedding_model_st = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Sentence Transformers 초기화 성공")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[WARNING] Sentence Transformers not available. Using keyword matching.")

# 환경 변수 로드
load_dotenv()

# AI 모델 초기화 (Gemini 메인)
gemini_service = None

# Gemini 서비스 초기화
try:
    gemini_service = GeminiService("gemini-1.5-pro")
            print("[SUCCESS] Gemini 서비스 초기화 성공 (모델: gemini-1.5-pro)")
except Exception as e:
    print(f"[ERROR] Gemini 서비스 초기화 실패: {e}")
    gemini_service = None

# 임베딩 모델 설정
embedding_model = 'models/text-embedding-004'

# ---- RAG를 위한 임시 벡터 저장 및 검색 로직 추가 시작 ----

# 임시로 사용할 문서 데이터
temporary_docs = [
    "Gemini 모델은 텍스트, 이미지 등 다양한 유형의 데이터를 처리할 수 있습니다. 멀티모달 기능을 통해 복잡한 질문에도 답변할 수 있습니다.",
    "Gemini 1.5 Pro는 1백만 토큰의 컨텍스트 윈도우를 지원하여 방대한 양의 정보를 한 번에 처리하고 이해할 수 있습니다.",
    "Gemini API는 Google AI Studio와 Google Cloud Vertex AI에서 사용할 수 있으며, 다양한 개발 환경을 지원합니다.",
    "RAG(Retrieval-Augmented Generation)는 외부 데이터를 활용해 LLM의 답변 품질을 높이는 기술입니다. 이를 통해 LLM은 학습되지 않은 최신 정보에도 답변할 수 있습니다.",
    "벡터 검색은 텍스트를 숫자의 배열(벡터)로 변환하고, 이 벡터 간의 유사도를 계산하여 가장 관련성이 높은 문서를 찾는 기술입니다.",
    "코사인 유사도(Cosine Similarity)는 두 벡터의 방향이 얼마나 일치하는지를 나타내는 지표로, 벡터 검색에서 문서 간의 유사성을 측정하는 데 널리 사용됩니다."
]

# 문서 벡터화 (초기화 시 한 번만 실행)
try:
    if gemini_service and gemini_service.client:
        temporary_embeddings = genai.embed_content(
            model=embedding_model,
            content=temporary_docs,
            task_type="RETRIEVAL_DOCUMENT"
        )['embedding']
        temporary_embeddings_np = np.array(temporary_embeddings)
        print("임시 문서 임베딩 생성 성공")
    else:
        print("Gemini 서비스가 없어 임베딩을 생성할 수 없습니다.")
        temporary_embeddings_np = None
except Exception as e:
    print(f"임시 문서 임베딩 생성 실패: {e}")
    temporary_embeddings_np = None

async def find_relevant_document(user_query: str) -> str:
    """
    사용자 입력과 가장 유사한 임시 문서를 찾아 반환합니다.
    """
    if temporary_embeddings_np is None or not temporary_docs:
        print("[WARNING] 임시 문서 또는 임베딩이 없어 RAG를 사용할 수 없습니다.")
        return ""

    try:
        if not gemini_service or not gemini_service.client:
            print("[WARNING] Gemini 서비스가 없어 RAG를 사용할 수 없습니다.")
            return ""
            
        # 사용자 질문 벡터화
        query_embedding = (await genai.embed_content_async(
            model=embedding_model,
            content=user_query,
            task_type="RETRIEVAL_QUERY"
        ))['embedding']
        
        query_embedding_np = np.array(query_embedding)
        
        # 코사인 유사도 계산
        # (A · B) / (||A|| * ||B||)
        similarities = np.dot(query_embedding_np, temporary_embeddings_np.T)
        
        # 가장 높은 유사도를 가진 문서의 인덱스 찾기
        most_similar_index = np.argmax(similarities)
        
        # 가장 유사한 문서 반환
        return temporary_docs[most_similar_index]
    except Exception as e:
        print(f"[ERROR] 유사 문서 검색 실패: {e}")
        traceback.print_exc()
        return ""

# ---- RAG를 위한 임시 벡터 저장 및 검색 로직 추가 끝 ----

# 고급 NLP 시스템 추가
def advanced_tokenization(text: str) -> List[str]:
    """
    고급 토큰화: KoNLPy 사용 또는 기본 토큰화
    """
    if KONLPY_AVAILABLE:
        try:
            # 형태소 분석으로 토큰화
            tokens = okt.morphs(text)
            # 불용어 제거
            stopwords = ['이', '가', '을', '를', '의', '에', '에서', '로', '으로', '와', '과', '도', '만', '은', '는']
            tokens = [token for token in tokens if token not in stopwords and len(token) > 1]
            return tokens
        except Exception as e:
            print(f"[ERROR] KoNLPy tokenization failed: {e}")
            return basic_tokenization(text)
    else:
        return basic_tokenization(text)

def basic_tokenization(text: str) -> List[str]:
    """
    기본 토큰화: 공백 기준 분리
    """
    # 특수문자 제거 및 소문자 변환
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = text.split()
    return [token for token in tokens if len(token) > 1]

def calculate_similarity(text1: str, text2: str) -> float:
    """
    임베딩 기반 유사도 계산
    """
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            embeddings = embedding_model_st.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"[ERROR] Embedding similarity calculation failed: {e}")
            return keyword_similarity(text1, text2)
    else:
        return keyword_similarity(text1, text2)

def keyword_similarity(text1: str, text2: str) -> float:
    """
    키워드 기반 유사도 계산 (fallback)
    """
    tokens1 = set(advanced_tokenization(text1))
    tokens2 = set(advanced_tokenization(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    
    return intersection / union if union > 0 else 0.0

# 의도 분류 시스템
INTENT_CATEGORIES = {
    'resume_summary': '이력서 요약',
    'interview_schedule': '면접 일정',
    'job_posting': '채용공고',
    'applicant_status': '지원자 상태',
    'general_inquiry': '일반 문의',
    'field_input': '필드 입력'
}

def classify_intent_advanced(text: str, current_field: str = None) -> Dict[str, Any]:
    """
    고급 의도 분류 시스템
    """
    tokens = advanced_tokenization(text)
    
    # 의도별 키워드 매핑
    intent_keywords = {
        'resume_summary': ['이력서', '요약', '정리', 'resume', 'summary'],
        'interview_schedule': ['면접', '일정', '스케줄', 'interview', 'schedule'],
        'job_posting': ['채용', '공고', '등록', 'job', 'posting'],
        'applicant_status': ['지원자', '상태', '현황', 'applicant', 'status'],
        'field_input': ['입력', '작성', '등록', '추가', 'input', 'add']
    }
    
    # 의도 점수 계산
    intent_scores = {}
    for intent, keywords in intent_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text.lower():
                score += 1
        intent_scores[intent] = score
    
    # 가장 높은 점수의 의도 선택
    best_intent = max(intent_scores.items(), key=lambda x: x[1])
    
    return {
        'intent': best_intent[0] if best_intent[1] > 0 else 'general_inquiry',
        'confidence': best_intent[1] / len(tokens) if tokens else 0.0,
        'tokens': tokens
    }

# AI 챗봇용 대화 방식 고급 NLP 시스템
def classify_conversation_intent(text: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    AI 챗봇용 대화 의도 분류 시스템
    """
    tokens = advanced_tokenization(text)
    
    # 대화 의도별 키워드 매핑
    conversation_intents = {
        'resume_inquiry': {
            'keywords': ['이력서', 'resume', '지원자', 'applicant', '확인', '보기', '조회', '검색'],
            'responses': [
                '지원자 관리 페이지에서 이력서를 확인할 수 있습니다.',
                '지원자 목록에서 해당 지원자를 클릭하면 상세 정보를 볼 수 있어요.',
                '이력서 검색 기능을 통해 특정 조건으로 지원자를 찾을 수 있습니다.'
            ]
        },
        'interview_schedule': {
            'keywords': ['면접', 'interview', '일정', 'schedule', '관리', '등록', '확인', '보기'],
            'responses': [
                '면접 관리 페이지에서 일정을 등록하고 관리할 수 있습니다.',
                '캘린더 형태로 보기 편하게 구성되어 있어요.',
                '면접 일정을 등록하고 참석자에게 자동으로 알림을 보낼 수 있습니다.'
            ]
        },
        'job_posting_help': {
            'keywords': ['채용공고', 'job posting', '등록', '작성', '관리', '수정', '삭제'],
            'responses': [
                '채용공고 등록 페이지에서 새로운 공고를 작성할 수 있습니다.',
                'AI 도우미를 사용하면 단계별로 쉽게 채용공고를 작성할 수 있어요.',
                '기존 채용공고는 관리 페이지에서 수정하거나 삭제할 수 있습니다.'
            ]
        },
        'applicant_status': {
            'keywords': ['지원자', 'applicant', '상태', 'status', '현황', '통계', '분석'],
            'responses': [
                '지원자 현황은 대시보드에서 실시간으로 확인할 수 있습니다.',
                '지원 단계별 통계와 분석 자료를 제공하고 있어요.',
                '지원자별 진행 상황을 추적하고 관리할 수 있습니다.'
            ]
        },
        'system_help': {
            'keywords': ['도움', 'help', '사용법', '가이드', '설명', '어떻게', '방법'],
            'responses': [
                '어떤 기능에 대해 도움이 필요하신가요?',
                '채용공고 등록, 지원자 관리, 면접 관리 등 다양한 기능을 제공합니다.',
                '구체적으로 궁금한 부분을 말씀해주시면 자세히 설명드릴게요.'
            ]
        },
        'general_chat': {
            'keywords': ['안녕', 'hello', '반가워', '고마워', '감사', '좋아', '싫어', 'ㅎㅇ', '하이', 'hi', 'ㅎㅎ', 'ㅋㅋ'],
            'responses': [
                '안녕하세요! 채용 관리 시스템을 도와드릴게요.',
                '무엇을 도와드릴까요?',
                '언제든지 질문해주세요!'
            ]
        }
    }
    
    # 의도 점수 계산
    intent_scores = {}
    for intent, config in conversation_intents.items():
        score = 0
        for keyword in config['keywords']:
            if keyword in text.lower():
                score += 1
        intent_scores[intent] = score
    
    # 가장 높은 점수의 의도 선택
    best_intent = max(intent_scores.items(), key=lambda x: x[1])
    
    # 맥락 고려 (이전 대화 히스토리 활용)
    context_boost = 0
    if conversation_history:
        recent_intents = [msg.get('intent') for msg in conversation_history[-3:] if msg.get('intent')]
        if best_intent[0] in recent_intents:
            context_boost = 0.2  # 맥락 일치 시 점수 부스트
    
    final_confidence = min(1.0, (best_intent[1] / len(tokens) if tokens else 0.0) + context_boost)
    
    return {
        'intent': best_intent[0] if best_intent[1] > 0 else 'general_chat',
        'confidence': final_confidence,
        'tokens': tokens,
        'responses': conversation_intents.get(best_intent[0], {}).get('responses', []),
        'context_boost': context_boost
    }

def generate_conversation_response(intent_result: Dict[str, Any], conversation_history: List[Dict[str, Any]] = None) -> str:
    """
    대화 의도에 따른 응답 생성
    """
    intent = intent_result.get('intent', 'general_chat')
    confidence = intent_result.get('confidence', 0.0)
    responses = intent_result.get('responses', [])
    
    # 신뢰도가 낮으면 확인 질문
    if confidence < 0.3:
        return "죄송합니다. 질문을 정확히 이해하지 못했어요. 다시 말씀해주시겠어요?"
    
    # 응답 선택 (랜덤 또는 맥락 기반)
    if responses:
        import random
        selected_response = random.choice(responses)
        
        # 맥락에 따른 추가 정보 제공
        if conversation_history:
            recent_topics = [msg.get('intent') for msg in conversation_history[-2:] if msg.get('intent')]
            if len(recent_topics) > 1 and recent_topics[-1] == recent_topics[-2]:
                selected_response += "\n\n더 자세한 정보가 필요하시면 언제든 말씀해주세요!"
        
        return selected_response
    
    return "죄송합니다. 해당 질문에 대한 답변을 준비하지 못했어요."

def handle_conversation_chat(user_input: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    AI 챗봇용 대화 처리 함수
    """
    # 고급 NLP로 의도 분류
    intent_result = classify_conversation_intent(user_input, conversation_history)
    
    # 응답 생성
    response = generate_conversation_response(intent_result, conversation_history)
    
    # 대화 히스토리 업데이트
    if conversation_history is None:
        conversation_history = []
    
    conversation_history.append({
        'user_input': user_input,
        'intent': intent_result['intent'],
        'confidence': intent_result['confidence'],
        'timestamp': datetime.now()
    })
    
    return {
        'message': response,
        'intent': intent_result['intent'],
        'confidence': intent_result['confidence'],
        'conversation_history': conversation_history,
        'nlp_method': 'conversation_advanced'
    }

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
    키워드 기반 1차 분류 함수 (완전히 새로 작성)
    """
    text_lower = text.lower()
    text_length = len(text.strip())
    
    print(f"[DEBUG] ===== classify_input 시작 =====")
    print(f"[DEBUG] 입력 텍스트: {text}")
    print(f"[DEBUG] 텍스트 길이: {text_length}")
    print(f"[DEBUG] text_lower: {text_lower}")
    
    # 채용 관련 키워드 (더 포괄적) - 깨진 텍스트도 고려
    recruitment_keywords = [
        "뽑으려고", "구인", "채용", "모집", "구하다", "찾다", "채용하려고",
        "인천에서", "서울에서", "부산에서", "대구에서", "광주에서", "대전에서", "울산에서",
        "디자인팀", "개발팀", "마케팅팀", "영업팀", "기획팀", "인사팀", "웹개발자", "앱개발자", "디자이너", "마케터", "영업사원", "기획자",
        "명을", "명 뽑", "명 채용", "명 구인",
        "근무", "근무시간", "출근", "퇴근", "9 to 6", "9시", "6시", "시부터", "시까지",
        "연봉", "급여", "월급", "보수", "만원", "억원",
        "신입", "경력", "신입/경력", "경력자", "신입자", "년 이상", "년 경력",
        "주말보장", "주말 보장", "주말은",
        # 깨진 텍스트에서도 매칭될 수 있는 패턴들
        "????", "????", "????", "????", "????", "????", "????", "????", "????", "????",
        "????", "????", "????", "????", "????", "????", "????", "????", "????", "????"
    ]
    
    # 채용 관련 키워드가 포함된 경우
    matched_keywords = [keyword for keyword in recruitment_keywords if keyword in text_lower]
    print(f"[DEBUG] 매칭된 채용 키워드: {matched_keywords}")
    
    if matched_keywords:
        print(f"[DEBUG] 채용 관련 키워드 {len(matched_keywords)}개 감지 - job_posting_info 반환")
        return {'type': 'job_posting_info', 'category': '채용정보', 'confidence': 0.9}
    
    # 긴 텍스트 (20자 이상)이고 깨진 텍스트가 포함된 경우 채용 정보로 분류
    if text_length > 20 and "????" in text_lower:
        print(f"[DEBUG] 긴 텍스트 + 깨진 문자 감지 - job_posting_info 반환")
        return {'type': 'job_posting_info', 'category': '채용정보', 'confidence': 0.8}
    
    # 긴 텍스트 (30자 이상)는 대부분 채용 정보로 분류
    if text_length > 30:
        print(f"[DEBUG] 긴 텍스트 감지 ({text_length}자) - job_posting_info 반환")
        return {'type': 'job_posting_info', 'category': '채용정보', 'confidence': 0.7}
    
    # 질문 감지
    question_keywords = ["어떻게", "왜", "뭐", "무엇", "어디", "언제", "누가", "어떤", "가요", "인가요", "일까요", "?"]
    has_question = any(keyword in text_lower for keyword in question_keywords) or text.strip().endswith("?")
    
    if has_question:
        print(f"[DEBUG] 질문 감지 - question 반환")
        return {'type': 'question', 'category': 'general', 'confidence': 0.7}
    
    # 기본값: 답변으로 처리
    print(f"[DEBUG] 기본값 - answer 반환")
    return {'type': 'answer', 'category': 'general', 'confidence': 0.6}
    
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
    
    # 부서 관련 키워드 (팀 없이도 인식)
    if any(keyword in text_lower for keyword in ["개발팀", "개발", "프로그래밍", "코딩", "개발자"]):
        return {'type': 'field', 'category': '부서', 'value': '개발팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["마케팅팀", "마케팅", "홍보", "광고", "마케터"]):
        return {'type': 'field', 'category': '부서', 'value': '마케팅팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["영업팀", "영업", "세일즈", "영업사원"]):
        return {'type': 'field', 'category': '부서', 'value': '영업팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["디자인팀", "디자인", "UI/UX", "그래픽", "디자이너"]):
        return {'type': 'field', 'category': '부서', 'value': '디자인팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["기획팀", "기획", "기획자", "PM", "프로덕트"]):
        return {'type': 'field', 'category': '부서', 'value': '기획팀', 'confidence': 0.9}
    
    if any(keyword in text_lower for keyword in ["인사팀", "인사", "HR", "인사담당", "채용"]):
        return {'type': 'field', 'category': '부서', 'value': '인사팀', 'confidence': 0.9}
    
    # 일상 대화 키워드
    chat_keywords = ["안녕", "반가워", "고마워", "감사", "좋아", "싫어", "그래", "응", "네", "아니", "ㅎㅇ", "하이", "hi", "ㅎㅎ", "ㅋㅋ"]
    if any(keyword in text_lower for keyword in chat_keywords):
        return {'type': 'chat', 'category': '일상대화', 'confidence': 0.7}
    
    # 기본값: 답변으로 처리
    return {'type': 'answer', 'category': 'general', 'confidence': 0.6}

def _normalize_llm_result_to_internal_keys(parsed: dict) -> dict:
    """LLM이 반환한 컨텍스트 키(JSON)를 프런트 내부 키로 정규화"""
    if not isinstance(parsed, dict):
        return {}
    result = {}
    # job_location → locationCity
    job_location = parsed.get('job_location') or parsed.get('location')
    if job_location:
        result['locationCity'] = str(job_location).strip()
    # hiring_count → headcount (ex: "2명" 형태로 정규화)
    hiring = parsed.get('hiring_count') or parsed.get('headcount')
    if hiring:
        import re
        m = re.search(r"(\d+)", str(hiring))
        if m:
            result['headcount'] = f"{m.group(1)}명"
    # main_task → mainDuties
    main_task = parsed.get('main_task') or parsed.get('duty') or parsed.get('duties')
    if main_task:
        result['mainDuties'] = str(main_task).strip()
    # salary → salary (원문 유지)
    if parsed.get('salary'):
        result['salary'] = str(parsed['salary']).strip()
    # work_type → workType/workDays 판단
    work_type = parsed.get('work_type') or parsed.get('work_schedule') or parsed.get('work_days')
    if work_type:
        wt = str(work_type).strip()
        # "주 5일" 패턴이면 workDays로
        if '주' in wt and '일' in wt:
            result['workDays'] = wt
        else:
            result['workType'] = wt
    return result


async def extract_job_info_from_text_llm(text: str) -> dict:
    """LLM을 사용해 맥락 기반으로 항목을 구조화 추출 (가능 시)"""
    global gemini_service
    try:
        if not gemini_service or not gemini_service.client:
            return {}
        prompt = (
            "다음 채용 공고 문장에서 항목별 정보를 추출하라.\n"
            "항목: job_location, hiring_count, main_task, salary, work_type\n"
            "응답은 JSON 형식으로만 작성하라.\n"
            f"문장: \"{text}\""
        )
        response = await gemini_service.generate_response(prompt, [])
        import json
        # 응답에서 JSON만 추출 시도
        try:
            parsed = json.loads(response.strip())
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}", response)
            parsed = json.loads(m.group(0)) if m else {}
        normalized = _normalize_llm_result_to_internal_keys(parsed)
        if normalized:
            print(f"[DEBUG] LLM 맥락 추출 결과(정규화): {normalized}")
        return normalized
    except Exception as e:
        print(f"[WARN] LLM 맥락 추출 실패: {e}")
        return {}


def extract_job_info_from_text(text: str, use_llm: bool = True) -> dict:
    """
    자유 텍스트에서 채용 정보를 추출하는 함수
    JSON 키-값 쌍으로 반환하여 폼 필드와 직접 매칭
    1) LLM 컨텍스트 기반 추출(가능 시)
    2) 룰 기반 보완
    """
    text_lower = text.lower()
    extracted_data = {}
    extracted_info = []  # extracted_info 변수 초기화 추가
    
    print(f"[DEBUG] extract_job_info_from_text 시작 - 입력: {text}")
    
    # 1) LLM 컨텍스트 기반 추출 선시도
    #    - 동기 컨텍스트에서만 실행하고, 이벤트 루프가 이미 돌고 있으면 건너뜀 (런타임 충돌 방지)
    if use_llm:
        try:
            import asyncio
            try:
                asyncio.get_running_loop()
                loop_running = True
            except RuntimeError:
                loop_running = False

            if not loop_running:
                llm_result = asyncio.run(extract_job_info_from_text_llm(text))
            else:
                llm_result = {}

            if llm_result:
                extracted_data.update({
                    # 내부 키 → 한국어 라벨로도 복제 (프론트 하위 호환)
                    '인원': llm_result.get('headcount'),
                    '근무요일': llm_result.get('workDays'),
                    '연봉': llm_result.get('salary'),
                    '업무': llm_result.get('mainDuties'),
                    '지역': llm_result.get('locationCity')
                })
                # 내부 키 병행 유지 (프론트 jsonFieldMapper가 내부 키도 처리 가능)
                extracted_data.update({k: v for k, v in llm_result.items() if v})
        except Exception as e:
            print(f"[WARN] LLM 추출 단계 오류: {e}")

    # 이하: 룰 기반 보완 로직
    
    # 공통 후처리 유틸: 급여/근무형태/요일 정규화
    def normalize_salary_str(s: str) -> str:
        if not s:
            return s
        raw = str(s).strip()
        lower = raw.lower().replace(',', '').replace(' ', '')
        # 협의는 유지
        if '협의' in raw:
            return '협의'
        # M KRW → 만원 (1M KRW = 100만원)
        import re
        m_mkrw = re.search(r"(\d+(?:\.\d+)?)m\s*krw", lower)
        if m_mkrw:
            val = float(m_mkrw.group(1)) * 100
            return f"{int(round(val))}만원"
        # 원 → 만원
        m_won = re.search(r"(\d+)원$", lower)
        if m_won:
            won = int(m_won.group(1))
            return f"{int(round(won/10000))}만원"
        # 천/천만 → 만원 (4.7천 = 4700만원, 4천만 = 4000만원)
        m_thousand = re.search(r"(\d+(?:\.\d+)?)천만?", lower)
        if m_thousand:
            val = float(m_thousand.group(1)) * 1000
            return f"{int(round(val))}만원"
        # 억 → 만원 (1억 = 10000만원)
        m_eok = re.search(r"(\d+(?:\.\d+)?)억", lower)
        if m_eok:
            val = float(m_eok.group(1)) * 10000
            return f"{int(round(val))}만원"
        # 숫자+만원 패턴 보정
        m_man = re.search(r"(\d+(?:\.\d+)?)만원", lower)
        if m_man:
            val = float(m_man.group(1))
            return f"{int(round(val))}만원"
        # 최종: 원문 반환
        return raw

    def split_work_fields(s: str) -> dict:
        if not s:
            return {}
        text_s = str(s)
        import re
        res = {}
        # workDays 후보
        if re.search(r"주\s*\d+(?:\.\d+)?\s*일", text_s):
            m = re.search(r"주\s*\d+(?:\.\d+)?\s*일", text_s)
            res['workDays'] = m.group(0)
        if any(k in text_s for k in ['주중', '평일', '주말', '월~금', '월-금', '월~토', '월-토', '토일', '월화수목금']):
            # 이미 지정된 값과 다르면 우선 긴 표현 유지
            wd = '주중' if '주중' in text_s else ('평일' if '평일' in text_s else None)
            res['workDays'] = res.get('workDays') or wd or text_s
        # workType 후보
        type_keywords = ['유연근무', '탄력근무', '교대', '상근', '정규직', '계약직', '인턴', '아르바이트', '시프트', '파트타임', '풀타임', '재택', '하이브리드']
        if any(k in text_s for k in type_keywords):
            # 교대 근무/시프트 근무 등은 원문 유지
            res['workType'] = text_s
        return res

    # 부서 추출 - 더 정교한 패턴 매칭 (우선순위 고려)
    departments = [
        ("데이터분석팀", ["데이터분석팀", "데이터 분석팀", "데이터팀", "분석팀", "데이터분석", "데이터 분석"]),
        ("개발팀", ["개발팀", "개발", "프로그래밍", "코딩", "개발자", "웹개발자", "앱개발자", "백엔드", "프론트엔드", "풀스택", "프로그래머", "엔지니어", "소프트웨어", "SW"]),
        ("마케팅팀", ["마케팅팀", "마케팅", "홍보", "광고", "마케터", "브랜딩", "콘텐츠", "SNS", "소셜미디어", "디지털마케팅", "온라인마케팅"]),
        ("영업팀", ["영업팀", "영업", "세일즈", "영업사원", "고객관리", "계약", "매출", "수익", "판매", "영업관리"]),
        ("디자인팀", ["디자인팀", "디자인", "ui/ux", "그래픽", "디자이너", "웹디자인", "UI/UX", "인터페이스", "시각", "레이아웃", "브랜딩"]),
        ("기획팀", ["기획팀", "기획", "기획자", "pm", "프로덕트", "전략", "리서치", "비즈니스", "서비스기획", "제품기획", "서비스기획팀"]),
        ("인사팀", ["인사팀", "인사", "hr", "인사담당", "채용", "인사관리", "조직관리", "human resources"]),
        ("운영팀", ["운영팀", "운영", "operation", "관리", "시스템관리", "서버관리", "네트워크관리", "운영자", "관리자"]),
        ("고객지원팀", ["고객지원팀", "고객지원", "고객서비스", "CS", "customer service", "고객관리", "고객응대"]),
        ("재무팀", ["재무팀", "재무", "finance", "회계", "accounting", "재무관리", "재무담당"]),
        ("법무팀", ["법무팀", "법무", "legal", "법률", "law", "법무담당", "법무관리"]),
        ("보안팀", ["보안팀", "보안", "security", "시큐리티", "보안관리", "보안담당"])
    ]
    
    for dept_name, keywords in departments:
        if any(keyword in text_lower for keyword in keywords):
            extracted_data['부서'] = dept_name
            print(f"[DEBUG] 부서 추출됨: {dept_name}")
            break
    
    # 인원 추출 - "분"을 "명"으로 수정하여 인식
    import re
    # "2분"을 "2명"으로 수정하여 인식
    text_for_headcount = text.replace("분", "명")
    headcount_match = re.search(r'(\d+)명', text_for_headcount)
    if headcount_match:
        extracted_data['인원'] = f"{headcount_match.group(1)}명"
        print(f"[DEBUG] 인원 추출됨: {headcount_match.group(1)}명")
    
    # 지역 추출 - 더 정교한 패턴 매칭 (LLM 결과가 없을 때 보완)
    locations = {
        "서울": ["서울", "강남구", "강북구", "강동구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구", "판교", "성남", "분당", "하남", "광주시", "용인", "수원", "오산", "안산", "시흥", "안양", "의왕", "군포", "과천", "부천", "김포", "고양", "파주", "양주", "동두천", "포천", "연천", "가평", "양평", "여주", "이천", "광주시"],
        "부산": ["부산", "강서구", "금정구", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구", "기장군"],
        "대구": ["대구", "남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구"],
        "인천": ["인천", "계양구", "남구", "남동구", "동구", "부평구", "서구", "연수구", "중구", "강화군", "옹진군", "송도", "영종도", "강화", "옹진"],
        "광주": ["광주", "광산구", "남구", "동구", "북구", "서구"],
        "대전": ["대전", "대덕구", "동구", "서구", "유성구", "중구"],
        "울산": ["울산", "남구", "동구", "북구", "울주군", "중구"],
        "수원": ["수원", "장안구", "권선구", "팔달구", "영통구"],
        "창원": ["창원", "의창구", "성산구", "마산합포구", "마산회원구", "진해구"],
        "고양": ["고양", "덕양구", "일산동구", "일산서구"],
        "용인": ["용인", "처인구", "기흥구", "수지구"],
        "성남": ["성남", "수정구", "중원구", "분당구"],
        "부천": ["부천", "원미구", "소사구", "오정구"],
        "안산": ["안산", "상록구", "단원구"],
        "안양": ["안양", "만안구", "동안구"],
        "남양주": ["남양주"],
        "평택": ["평택"],
        "의정부": ["의정부"],
        "시흥": ["시흥"],
        "파주": ["파주"],
        "김포": ["김포"],
        "광명": ["광명"],
        "군포": ["군포"],
        "오산": ["오산"],
        "하남": ["하남"],
        "양평": ["양평"],
        "여주": ["여주"],
        "이천": ["이천"],
        "용인시": ["용인시"],
        "성남시": ["성남시"],
        "수원시": ["수원시"],
        "창원시": ["창원시"],
        "고양시": ["고양시"],
        "부천시": ["부천시"],
        "안산시": ["안산시"],
        "안양시": ["안양시"],
        "남양주시": ["남양주시"],
        "평택시": ["평택시"],
        "의정부시": ["의정부시"],
        "시흥시": ["시흥시"],
        "파주시": ["파주시"],
        "김포시": ["김포시"],
        "광명시": ["광명시"],
        "군포시": ["군포시"],
        "오산시": ["오산시"],
        "하남시": ["하남시"],
        "양평군": ["양평군"],
        "여주시": ["여주시"],
        "이천시": ["이천시"],
        "여수": ["여수", "여수시"],  # 여수 추가
        "전주": ["전주", "전주시"],
        "천안": ["천안", "천안시"],
        "청주": ["청주", "청주시"],
        "포항": ["포항", "포항시"],
        "춘천": ["춘천", "춘천시"],
        "강릉": ["강릉", "강릉시"],
        "경주": ["경주", "경주시"]
    }
    
    # 지역 추출 개선: 더 긴 지명부터 우선 매칭하여 '남양주' vs '양주' 등 오매칭 방지
    all_districts = []
    for _, districts in locations.items():
        all_districts.extend(districts)
    # 중복 제거 후 길이 내림차순 정렬
    all_districts = sorted(list(set(all_districts)), key=lambda s: len(s), reverse=True)
    for district in all_districts:
        if district in text:
            extracted_data['지역'] = district
            print(f"[DEBUG] 지역 추출됨: {district}")
            break
    
    # 근무시간 추출
    work_time_patterns = [
        r'(\d{1,2})시\s*출근\s*(\d{1,2})시\s*퇴근',  # 10시 출근 7시 퇴근
        r'출근\s*(\d{1,2})시\s*퇴근\s*(\d{1,2})시',  # 출근 10시 퇴근 7시
        r'출근\s*은?\s*(\d{1,2})시\s*[,·]?\s*퇴근\s*은?\s*(\d{1,2})시',  # 출근은 9시, 퇴근은 6시
        r'(\d{1,2})\s*to\s*(\d{1,2})',  # 9 to 6
        r'(\d{1,2})시\s*~\s*(\d{1,2})시',  # 9시~6시
        r'(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})',  # 9:00~18:00
        r'(\d{1,2})시\s*부터\s*(\d{1,2})시\s*까지',  # 10시부터 7시까지
        r'(\d{1,2})시\s*부터\s*(\d{1,2})시',  # 9시부터 6시
        r'근무\s*는?\s*(\d{1,2})시\s*부터\s*(\d{1,2})시',  # 근무는 9시부터 6시
        r'오전\s*(\d{1,2})시\s*부터\s*오전\s*(\d{1,2})시\s*까지',
        r'오전\s*(\d{1,2})시\s*부터\s*오후\s*(\d{1,2})시\s*까지',
        r'오전\s*(\d{1,2})시\s*부터\s*저녁\s*(\d{1,2})시\s*까지',
        r'오후\s*(\d{1,2})시\s*부터\s*오후\s*(\d{1,2})시\s*까지',
        r'오전\s*(\d{1,2})시\s*~\s*오전\s*(\d{1,2})시',
        r'오전\s*(\d{1,2})시\s*~\s*오후\s*(\d{1,2})시',
        r'오후\s*(\d{1,2})시\s*~\s*오후\s*(\d{1,2})시',
    ]
    
    for pattern in work_time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if 'to' in pattern:
                work_hours = f"{match.group(1)} to {match.group(2)}"
                extracted_data['근무시간'] = work_hours
                extracted_info.append(f"• 근무시간: {work_hours}")
                print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
            elif '오전' in pattern or '오후' in pattern or '저녁' in pattern:
                start_time = match.group(1)
                end_time = match.group(2)
                # 오전/오후/저녁 정보를 포함한 더 정확한 표현
                if '오전' in pattern and '오후' in pattern:
                    work_hours = f"오전 {start_time}시~오후 {end_time}시"
                    extracted_data['근무시간'] = work_hours
                    extracted_info.append(f"• 근무시간: {work_hours}")
                    print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
                elif '오전' in pattern and '저녁' in pattern:
                    work_hours = f"오전 {start_time}시~오후 {end_time}시"
                    extracted_data['근무시간'] = work_hours
                    extracted_info.append(f"• 근무시간: {work_hours}")
                    print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
                elif '오전' in pattern and '오전' in pattern:
                    work_hours = f"오전 {start_time}시~오전 {end_time}시"
                    extracted_data['근무시간'] = work_hours
                    extracted_info.append(f"• 근무시간: {work_hours}")
                    print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
                elif '오후' in pattern and '오후' in pattern:
                    work_hours = f"오후 {start_time}시~오후 {end_time}시"
                    extracted_data['근무시간'] = work_hours
                    extracted_info.append(f"• 근무시간: {work_hours}")
                    print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
                else:
                    work_hours = f"{start_time}시~{end_time}시"
                    extracted_data['근무시간'] = work_hours
                    extracted_info.append(f"• 근무시간: {work_hours}")
                    print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
            else:
                start_time = int(match.group(1))
                end_time = int(match.group(2))
                
                # 근무시간 통일 형식으로 변환 (일반적인 9~6은 오후로 보정)
                if start_time < 12:
                    start_format = f"오전 {start_time}시"
                else:
                    start_format = f"오후 {start_time}시"
                
                if end_time < 12:
                    # 9~6, 10~7 같은 전형적인 패턴 보정: 종료시간이 7 이하이면 오후로 간주
                    if end_time <= 8 and start_time <= 10:
                        end_format = f"오후 {end_time}시"
                    else:
                        end_format = f"오전 {end_time}시"
                else:
                    end_format = f"오후 {end_time}시"
                
                work_hours = f"{start_format} ~ {end_format}"
                extracted_data['근무시간'] = work_hours
                extracted_info.append(f"• 근무시간: {work_hours}")
                print(f"[DEBUG] 근무시간 추출됨: {work_hours}")
            break

    # 유연근무/자율출근/주간근무 인식
    if '근무시간' not in extracted_data:
        if any(k in text for k in ['유연근무', '유연 근무', '자율 출근', '자율출근', '유연 출근']):
            extracted_data['근무시간'] = '유연근무'
            print("[DEBUG] 근무시간 추출됨: 유연근무")
        elif any(k in text for k in ['주간 근무', '주간근무']):
            extracted_data['근무시간'] = '주간근무'
            print("[DEBUG] 근무시간 추출됨: 주간근무")
    
    # 근무요일 추출
    work_days_patterns = [
        r'월\s*~\s*금',  # 월~금
        r'월요일\s*부터\s*금요일',  # 월요일부터 금요일
        r'월\s*-\s*금',  # 월-금
        r'평일',  # 평일
        r'주\s*5일',  # 주5일
        r'월\s*화\s*수\s*목\s*금',  # 월화수목금
        r'월\s*화\s*수\s*목\s*금\s*토',  # 월화수목금토
        r'월\s*화\s*수\s*목\s*금\s*토\s*일'  # 월화수목금토일
    ]
    
    for pattern in work_days_patterns:
        match = re.search(pattern, text)
        if match:
            if '월~금' in pattern or '월-금' in pattern:
                extracted_data['근무요일'] = "월~금"
                print(f"[DEBUG] 근무요일 추출됨: 월~금")
            elif '평일' in pattern:
                extracted_data['근무요일'] = "평일"
                print(f"[DEBUG] 근무요일 추출됨: 평일")
            elif '주5일' in pattern:
                extracted_data['근무요일'] = "주5일"
                print(f"[DEBUG] 근무요일 추출됨: 주5일")
            else:
                extracted_data['근무요일'] = match.group(0)
                print(f"[DEBUG] 근무요일 추출됨: {match.group(0)}")
            break
    
    # 경력 추출 - 더 정교한 패턴 매칭
    experience_patterns = [
        r'신입',  # 신입
        r'경력\s*(\d+)년',  # 경력 3년
        r'경력\s*(\d+)년\s*이상',  # 경력 3년 이상
        r'(\d+)년\s*경력',  # 3년 경력
        r'경력자',  # 경력자
        r'신입자'  # 신입자
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text)
        if match:
            if '신입' in pattern:
                extracted_data['경력'] = "신입"
                print(f"[DEBUG] 경력 추출됨: 신입")
                break
            elif '경력' in pattern and match.groups():
                years = match.group(1)
                extracted_data['경력'] = f"{years}년 이상"
                print(f"[DEBUG] 경력 추출됨: {years}년 이상")
                break
            elif '경력자' in pattern:
                extracted_data['경력'] = "경력자"
                print(f"[DEBUG] 경력 추출됨: 경력자")
                break
    
    # 연봉 추출 - 더 정교한 패턴 매칭 (범위 우선 처리)
    salary_patterns = [
        r'(\d{1,3}),(\d{3})\s*~\s*(\d{1,3}),(\d{3})\s*만원?',  # 3,600~4,000만원
        r'연봉\s*(\d{1,3}),(\d{3})\s*~\s*(\d{1,3}),(\d{3})\s*만원?',
        r'(\d+)만원\s*에서\s*(\d+)만원',  # 3500만원에서 4500만원
        r'연봉\s*(\d+)만원\s*에서\s*(\d+)만원',  # 연봉 3500만원에서 4500만원
        r'(\d+)만원\s*~\s*(\d+)만원',  # 3500만원~4500만원
        r'(\d{1,3}),(\d{3})만원',  # 3,600만원
        r'연봉\s*(\d{1,3}),(\d{3})만원',  # 연봉 3,600만원
        r'(\d)\s*천만원',  # 4천만원
        r'연봉\s*(\d)\s*천만원',
        r'연봉\s*(\d+)만원',  # 연봉 2000만원
        r'(\d+)만원\s*정도',  # 2000만원 정도
        r'(\d+)만원',  # 2000만원
    ]
    
    # 콤마가 포함된 연봉 패턴 (우선 처리)
    comma_patterns = [
        r'(\d+),(\d{1,3})만원',  # 3,600만원 (천단위 구분자)
        r'연봉\s*(\d+),(\d{1,3})만원',  # 연봉 3,600만원
    ]
    
    # 연봉 파싱 함수들
    def preprocess_salary_input(s: str) -> str:
        """쉼표와 공백을 제거하여 숫자만 추출"""
        return s.replace(',', '').replace(' ', '').replace('만원', '')
    
    def is_valid_number(s: str) -> bool:
        """숫자만 포함되었는지 체크"""
        return s.isdigit()
    
    def parse_salary(s: str) -> int:
        """연봉 문자열을 숫자로 파싱"""
        s_clean = preprocess_salary_input(s)
        
        if not is_valid_number(s_clean):
            raise ValueError("숫자 형식이 아님")
        
        num = int(s_clean)
        
        if num < 10000:  # 4자리 이하면 만원 단위
            return num
        else:
            # 이미 원 단위일 수도 있음 (예: 36000000)
            return num // 10000  # 만원 단위로 변환
    
    # 연봉 추출 - 개선된 로직 (중복 정의 통합 + 천만원/콤마/범위 포함)
    salary_patterns = [
        r'(\d{1,3}),(\d{3})\s*~\s*(\d{1,3}),(\d{3})\s*만원?',  # 3,600~4,000만원
        r'연봉\s*(\d{1,3}),(\d{3})\s*~\s*(\d{1,3}),(\d{3})\s*만원?',
        r'(\d+)만원\s*에서\s*(\d+)만원',  # 3500만원에서 4500만원
        r'연봉\s*(\d+)만원\s*에서\s*(\d+)만원',  # 연봉 3500만원에서 4500만원
        r'(\d+)만원\s*~\s*(\d+)만원',  # 3500만원~4500만원
        r'(\d{1,3}),(\d{3})만원',  # 3,600만원
        r'연봉\s*(\d{1,3}),(\d{3})만원',  # 연봉 3,600만원
        r'(\d)\s*천만원',  # 4천만원
        r'연봉\s*(\d)\s*천만원',
        r'연봉\s*(\d+)만원',  # 연봉 2000만원
        r'(\d+)만원\s*(선|수준|정도|부터)',  # 2000만원 선/수준/정도/부터
        r'(\d+)만원',  # 2000만원
    ]
    
    # 협의 처리 우선
    if any(k in text for k in ['연봉 협의', '연봉은 협의', '연봉 협의입니다', '연봉은 협의입니다', '연봉 협의예요', '연봉은 협의예요', '연봉 협의임', '연봉 협의 가능', '협의']):
        extracted_data['연봉'] = '협의'
        print('[DEBUG] 연봉 추출됨: 협의')
    else:
        # "사이" 패턴 별도 처리
        사이_match = re.search(r'(\d{1,3})(?:,(\d{3}))?\s*~\s*(\d{1,3})(?:,(\d{3}))?', text)
        if 사이_match and '만원' in text:
            left = ''.join([g for g in 사이_match.groups()[:2] if g])
            right = ''.join([g for g in 사이_match.groups()[2:] if g])
            try:
                min_salary = int(left)
                max_salary = int(right)
                extracted_data['연봉'] = f"{min_salary}만원~{max_salary}만원"
                print(f"[DEBUG] 연봉 추출됨: {min_salary}만원~{max_salary}만원")
            except Exception:
                pass
        else:
            # 개선된 연봉 추출 로직
            salary_found = False
            for pattern in salary_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        if '에서' in pattern or '~' in pattern:
                            # 범위 연봉
                            if ',' in pattern:
                                # 콤마 포함 범위
                                min_salary = parse_salary(match.group(1) + match.group(2))
                                max_salary = parse_salary(match.group(3) + match.group(4))
                            else:
                                min_salary = parse_salary(match.group(1))
                                max_salary = parse_salary(match.group(2))
                            extracted_data['연봉'] = f"{min_salary}만원~{max_salary}만원"
                            print(f"[DEBUG] 연봉 추출됨: {min_salary}만원~{max_salary}만원")
                        else:
                            # 단일 연봉
                            if ',' in pattern:
                                # 천단위 구분자가 있는 경우
                                before_comma = match.group(1)
                                after_comma = match.group(2)
                                salary = parse_salary(before_comma + after_comma)
                            elif '천만원' in pattern:
                                thousands = int(match.group(1))
                                salary = thousands * 1000
                            else:
                                # 일반 연봉
                                salary = parse_salary(match.group(1))
                            extracted_data['연봉'] = f"{salary}만원"
                            print(f"[DEBUG] 연봉 추출됨: {salary}만원")
                        
                        salary_found = True
                        break
                    except ValueError as e:
                        print(f"[DEBUG] 연봉 파싱 오류: {e}")
                        continue
            
            if not salary_found:
                # 문맥 기반(만원 생략/천/선·수준·정도·부터) 보정: "연봉" 인접 숫자 인식
                ctx = re.search(r'연봉[^0-9]*(\d{1,3})(?:,(\d{3}))?(?:\s*(천))?(?:\s*만원)?(?:\s*(선|수준|정도|부터))?', text)
                if ctx:
                    try:
                        has_comma = ctx.group(2) is not None
                        has_thousand = ctx.group(3) is not None
                        if has_comma:
                            salary = parse_salary(ctx.group(1) + ctx.group(2))
                        elif has_thousand:
                            salary = int(ctx.group(1)) * 1000
                        else:
                            salary = parse_salary(ctx.group(1))
                        extracted_data['연봉'] = f"{salary}만원"
                        print(f"[DEBUG] 연봉 추출됨(문맥): {salary}만원")
                        salary_found = True
                    except ValueError:
                        pass
            
            if not salary_found:
                print(f"[DEBUG] 연봉 추출 실패")
    
    # 추가 정보 추출 (기타 항목) - 필드 매칭되지 않는 정보들
    additional_info = []
    
    # 복리후생 관련 키워드들
    welfare_keywords = [
        "주말보장", "주말 보장", "원격근무", "재택근무", "재택", "유연근무", "유연근무제", "플렉스",
        "식대지원", "교통비지원", "주차지원", "의료보험", "국민연금", "산재보험", "고용보험",
        "연차휴가", "반차", "반반차", "병가", "출산휴가", "육아휴직", "육아휴가",
        "교육지원", "자기계발", "도서구입비", "학원비", "자격증", "어학연수",
        "경조사", "상조", "장례", "결혼", "출산", "생일", "기념일",
        "동호회", "동아리", "운동", "헬스", "피트니스", "골프", "테니스",
        "회식", "워크샵", "MT", "단체행사", "기업문화", "조직문화"
    ]
    
    # 기타 항목으로 분류할 키워드들
    for keyword in welfare_keywords:
        if keyword in text:
            additional_info.append(keyword)
            print(f"[DEBUG] 기타 항목 추출됨: {keyword}")
    
    # 기타 추가 정보가 있으면 통합
    if additional_info:
        extracted_info.append(f"• 기타: {', '.join(additional_info)}")
        extracted_data['additionalInfo'] = ', '.join(additional_info)
        print(f"[DEBUG] 기타 정보 추출됨: {', '.join(additional_info)}")
    
    # 업무 내용 추출
    job_titles = {
        "프론트엔드개발": ["프론트엔드 개발자", "프론트엔드", "웹개발자", "웹 개발자", "UI개발자", "클라이언트 개발자"],
        "백엔드개발": ["백엔드 개발자", "백엔드", "서버개발자", "서버 개발자", "API 개발자", "서버 엔지니어", "백엔드 엔지니어"],
        "풀스택개발": ["풀스택 개발자", "풀스택", "전체개발", "웹서비스 개발자", "웹 서비스 개발자", "웹 프로그래머", "웹 엔지니어"],
        "앱개발": ["앱개발자", "앱 개발자", "모바일 개발자", "iOS 개발자", "안드로이드 개발자", "모바일 앱 개발자", "앱 프로그래머"],
        "AI개발": ["AI개발자", "AI 개발자", "머신러닝 개발자", "딥러닝 개발자", "인공지능 개발자"],
        "데이터분석": ["데이터분석가", "데이터 분석가", "데이터 사이언티스트", "데이터 엔지니어", "분석가", "데이터 분석"],
        "UI/UX디자인": ["UI/UX디자이너", "UI/UX 디자이너", "UX디자이너", "UI디자이너", "웹디자이너", "그래픽디자이너", "인터페이스 디자이너"],
        "마케팅": ["마케터", "마케팅 담당자", "마케팅 매니저", "디지털 마케터", "온라인 마케터", "마케팅 전문가"],
        "영업": ["영업담당자", "영업사원", "영업 매니저", "세일즈", "영업 전문가", "영업 관리자"],
        "기획": ["기획자", "기획 담당자", "PM", "프로덕트 매니저", "서비스 기획자", "제품 기획자", "비즈니스 기획자"],
        "인사": ["인사담당자", "HR", "인사 매니저", "채용 담당자", "인사 전문가", "인사 관리자"],
        "운영": ["운영담당자", "운영 매니저", "시스템 관리자", "운영 전문가", "운영 관리자"],
        "고객지원": ["고객지원", "CS", "고객서비스", "고객 응대", "고객 관리", "고객지원 담당자", "고객지원 시스템", "고객지원 시스템 담당"],
        "재무": ["재무담당자", "회계 담당자", "재무 매니저", "회계사", "재무 전문가", "재무 관리자"],
        "보안": ["보안담당자", "보안 전문가", "시큐리티", "보안 엔지니어", "보안 관리자", "보안 담당자"]
    }
    
    for job_title, keywords in job_titles.items():
        if any(keyword in text for keyword in keywords):
            extracted_data['업무'] = job_title
            print(f"[DEBUG] 업무 추출됨: {job_title}")
            break
    
    print(f"[DEBUG] 최종 추출된 정보: {extracted_data}")
    
    if not extracted_data:
        return {}
    
    return extracted_data

def classify_input_with_context(text: str, current_field: str = None) -> dict:
    """
    현재 필드 컨텍스트를 고려한 분류 함수
    """
    text_lower = text.lower()
    text_length = len(text.strip())
    
    print(f"[DEBUG] ===== classify_input_with_context 시작 =====")
    print(f"[DEBUG] 입력 텍스트: {text}")
    print(f"[DEBUG] 현재 필드: {current_field}")
    
    # 카테고리별 키워드 매핑
    field_categories = {
        'department': {
            'category': '업무부서',
            'keywords': {
                '개발': ['개발', 'dev', 'development', '프로그래밍', '코딩', '웹개발', '앱개발', '백엔드', '프론트엔드', '풀스택', '개발자', '프로그래머', '엔지니어', '소프트웨어', 'SW'],
                '마케팅': ['마케팅', 'marketing', '홍보', '광고', '브랜딩', '콘텐츠', 'SNS', '소셜미디어', '디지털마케팅', '온라인마케팅', '마케터'],
                '영업': ['영업', 'sales', '세일즈', '고객관리', '계약', '매출', '수익', '판매', '영업관리', '영업사원'],
                '디자인': ['디자인', 'design', 'UI', 'UX', '그래픽', '웹디자인', 'UI/UX', '인터페이스', '시각', '레이아웃', '브랜딩', '디자이너'],
                '기획': ['기획', 'planning', '전략', '분석', '리서치', '데이터분석', '비즈니스', '서비스기획', '제품기획', '기획자'],
                '인사': ['인사', 'HR', 'human resources', '채용', '인사담당', '인사관리', '조직관리'],
                '운영': ['운영', 'operation', '관리', '시스템관리', '서버관리', '네트워크관리', '운영자', '관리자'],
                '고객지원': ['고객지원', '고객서비스', 'CS', 'customer service', '고객관리', '고객응대'],
                '재무': ['재무', 'finance', '회계', 'accounting', '재무관리', '재무담당'],
                '법무': ['법무', 'legal', '법률', 'law', '법무담당', '법무관리'],
                '보안': ['보안', 'security', '시큐리티', '보안관리', '보안담당']
            },
            'extract_value': True
        },
        'headcount': {
            'category': '채용인원',
            'keywords': {
                '단위': ['명', '인원', '사람', '분', '명의', '인원수', '채용인원', '구인인원'],
                '숫자': ['1명', '2명', '3명', '4명', '5명', '6명', '7명', '8명', '9명', '10명', '한명', '두명', '세명', '네명', '다섯명'],
                '범위': ['1~2명', '2~3명', '3~5명', '5~10명', '10명 이상']
            },
            'extract_value': True,
            'extract_number': True
        },
        'mainDuties': {
            'category': '업무내용',
            'keywords': {
                '개발업무': ['개발', '프로그래밍', '코딩', '웹개발', '앱개발', '백엔드', '프론트엔드', '풀스택', '데이터베이스', 'API', '서버', '클라이언트'],
                '디자인업무': ['디자인', 'UI', 'UX', '그래픽', '웹디자인', 'UI/UX', '인터페이스', '시각', '레이아웃', '브랜딩'],
                '마케팅업무': ['마케팅', '홍보', '광고', '브랜딩', '콘텐츠', 'SNS', '소셜미디어', '디지털마케팅', '온라인마케팅'],
                '영업업무': ['영업', '세일즈', '고객관리', '계약', '매출', '수익', '판매', '영업관리', '고객지원'],
                '기획업무': ['기획', '전략', '분석', '리서치', '데이터분석', '비즈니스', '서비스기획', '제품기획'],
                '관리업무': ['관리', '운영', '관리자', '운영자', '시스템관리', '서버관리', '네트워크관리'],
                '일반업무': ['업무', '업무처리', '업무관리', '업무지원', '업무보조', '업무진행', '업무수행']
            },
            'extract_value': True
        },
        'workHours': {
            'category': '근무시간',
            'keywords': {
                '시간표현': ['시', '분', '시간', '오전', '오후', '아침', '저녁', '새벽', '밤'],
                '구체시간': ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'],
                '근무형태': ['유연근무', '재택근무', '원격근무', '재택', '원격', '플렉스', '탄력근무', '시차출근'],
                '시간대': ['오전9시', '오후6시', '오전10시', '오후7시', '오전8시', '오후5시'],
                '범위': ['9시~6시', '10시~7시', '8시~5시', '9시부터6시까지', '10시부터7시까지']
            },
            'extract_value': True
        },
        'workDays': {
            'category': '근무요일',
            'keywords': {
                '요일': ['월', '화', '수', '목', '금', '토', '일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'],
                '범위': ['월~금', '월~토', '월~일', '화~토', '수~일'],
                '표현': ['평일', '주말', '평일만', '주말제외', '주5일', '주6일', '주7일']
            },
            'extract_value': True
        },
        'locationCity': {
            'category': '근무위치',
            'keywords': {
                '광역시도': ['서울', '부산', '대구', '인천', '대전', '광주', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'],
                '서울구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
                '부산구': ['강서구', '금정구', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구', '기장군'],
                '경기도시': ['수원', '성남', '안양', '안산', '용인', '부천', '광명', '평택', '과천', '오산', '시흥', '군포', '의왕', '하남', '이천', '안성', '김포', '화성', '광주', '여주', '양평', '고양', '의정부', '동두천', '구리', '남양주', '파주', '양주', '포천', '연천']
            },
            'extract_value': True
        },
        'salary': {
            'category': '급여조건',
            'keywords': {
                '단위': ['만원', '원', '천원', '억원', '만', '천', '억'],
                '급여형태': ['연봉', '월급', '급여', '보수', '임금', '연봉제', '월급제', '연봉협의', '면접후협의'],
                '금액': ['3000만원', '4000만원', '5000만원', '6000만원', '7000만원', '8000만원', '9000만원', '1억원'],
                '범위': ['3000~5000만원', '4000~6000만원', '5000~7000만원', '6000~8000만원']
            },
            'extract_value': True,
            'extract_number': True
        },
        'deadline': {
            'category': '마감일',
            'keywords': {
                '시간단위': ['년', '월', '일', '주', '시간', '분'],
                '마감관련': ['마감', '마감일', '지원마감', '채용마감', '접수마감', '지원기간', '채용기간'],
                '날짜표현': ['오늘', '내일', '모레', '이번주', '다음주', '이번달', '다음달', '올해', '내년'],
                '구체날짜': ['2024년', '2025년', '12월', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월']
            },
            'extract_value': True
        },
        'contactEmail': {
            'category': '연락처',
            'keywords': {
                '이메일': ['@', '이메일', 'email', '메일', 'mail', '이메일주소', '메일주소'],
                '연락처': ['연락처', '연락', 'contact', '연락방법', '문의처', '문의'],
                '담당자': ['담당자이메일', '인사담당자이메일', '지원이메일', '문의이메일']
            },
            'extract_value': True
        },
        'experience': {
            'category': '경력요건',
            'keywords': {
                '경력구분': ['신입', '경력', '신입/경력', '경력무관', '경력상관없음'],
                '경력기간': ['1년', '2년', '3년', '4년', '5년', '6년', '7년', '8년', '9년', '10년'],
                '경력범위': ['1년이상', '2년이상', '3년이상', '4년이상', '5년이상', '1~3년', '2~4년', '3~5년', '4~6년', '5~7년']
            },
            'extract_value': True
        }
    }
    
    # 질문 키워드 감지 (가장 먼저 체크)
    question_keywords = [
        "어떻게", "왜", "무엇", "뭐", "언제", "어디", "추천", "기준", "장점", "단점", "차이", 
        "있을까", "있나요", "어떤", "무슨", "궁금", "알려줘", "설명해줘", "몇명", "몇 명", 
        "얼마나", "어느 정도", "어떤 정도", "좋을까", "될까", "할까", "인가요", "일까",
        "어때", "어떠", "어떻", "어떤가", "어떤지", "어떤지요", "어떤가요", "어떤지요",
        "어떻게", "어떡", "어떻", "어떤", "어떤지", "어떤가", "어떤지요", "어떤가요"
    ]
    
    # 질문 키워드가 포함되어 있거나 문장이 "?"로 끝나는 경우
    if any(keyword in text_lower for keyword in question_keywords) or text.strip().endswith("?"):
        matched_keywords = [kw for kw in question_keywords if kw in text_lower]
        print(f"[DEBUG] 질문으로 분류됨 - 매칭된 질문 키워드: {matched_keywords}")
        return {'type': 'question', 'category': 'general', 'confidence': 0.8}
    
    # 현재 필드에 대한 고급 NLP 기반 검토
    if current_field and current_field in field_categories:
        field_config = field_categories[current_field]
        category = field_config.get('category', 'unknown')
        print(f"[DEBUG] 필드 '{current_field}'의 카테고리 '{category}' 고급 NLP 검사 시작")
        
        # 고급 토큰화 적용
        tokens = advanced_tokenization(text)
        print(f"[DEBUG] 토큰화 결과: {tokens}")
        
        # 임베딩 기반 유사도 계산
        best_match = None
        best_similarity = 0.0
        matched_subcategories = []
        
        for subcategory, keywords in field_config['keywords'].items():
            for keyword in keywords:
                # 임베딩 기반 유사도 계산
                similarity = calculate_similarity(text, keyword)
                if similarity > best_similarity and similarity > 0.3:  # 임계값 설정
                    best_similarity = similarity
                    best_match = keyword
                    matched_subcategories = [subcategory]
        
        print(f"[DEBUG] 최고 유사도: {best_similarity} (키워드: {best_match})")
        
        if best_match:
            print(f"[DEBUG] 고급 NLP 카테고리 '{category}' 키워드 감지됨 - 맥락 검토 시작")
            # 맥락 검토: 실제 답변인지 확인
            if is_valid_answer_for_field(text, current_field):
                print(f"[DEBUG] 맥락 검토 통과 - 값 추출 시작")
                extracted_value = extract_field_value(text, current_field, field_config)
                print(f"[DEBUG] 추출된 값: {extracted_value}")
                result = {
                    'type': 'answer', 
                    'category': category, 
                    'subcategory': matched_subcategories[0] if matched_subcategories else None,
                    'value': extracted_value,
                    'confidence': best_similarity,
                    'tokens': tokens,
                    'nlp_method': 'advanced'
                }
                print(f"[DEBUG] 고급 NLP 답변으로 분류됨: {result}")
                return result
            else:
                print(f"[DEBUG] 맥락 검토 실패 - 답변으로 분류하지 않음")
        else:
            print(f"[DEBUG] 고급 NLP 카테고리 '{category}' 키워드 없음")
    
    # 기존 분류 로직 (필드별 컨텍스트가 없는 경우)
    print(f"[DEBUG] 기존 분류 로직 사용")
    result = classify_input(text)
    print(f"[DEBUG] 최종 분류 결과: {result}")
    return result

def is_valid_answer_for_field(text: str, field: str) -> bool:
    """
    해당 필드에 대한 유효한 답변인지 검토
    """
    text_lower = text.lower()
    
    print(f"[DEBUG] ===== is_valid_answer_for_field 검토 시작 =====")
    print(f"[DEBUG] 검토 텍스트: {text}")
    print(f"[DEBUG] 검토 필드: {field}")
    
    # 부정적인 표현이나 질문성 표현이 포함된 경우 제외
    negative_patterns = ['모르겠', '잘 모르', '몰라', '궁금', '어떻게', '왜', '뭐']
    negative_matches = [pattern for pattern in negative_patterns if pattern in text_lower]
    if negative_matches:
        print(f"[DEBUG] 부정적 표현 감지됨: {negative_matches} - 유효하지 않음")
        return False
    
    # 너무 짧거나 너무 긴 경우 제외
    if len(text.strip()) < 2 or len(text.strip()) > 200:
        print(f"[DEBUG] 길이 검사 실패 - 길이: {len(text.strip())} - 유효하지 않음")
        return False
    
    # 필드별 유효성 검사
    if field == 'headcount':
        # 숫자가 포함되어야 함
        import re
        numbers = re.findall(r'\d+', text)
        if not numbers:
            print(f"[DEBUG] headcount 필드 - 숫자 없음 - 유효하지 않음")
            return False
        else:
            print(f"[DEBUG] headcount 필드 - 숫자 감지됨: {numbers}")
    
    elif field == 'contactEmail':
        # 이메일 형식이어야 함
        import re
        if not re.search(r'@', text):
            print(f"[DEBUG] contactEmail 필드 - @ 없음 - 유효하지 않음")
            return False
        else:
            print(f"[DEBUG] contactEmail 필드 - @ 감지됨")
    
    print(f"[DEBUG] 모든 검토 통과 - 유효함")
    return True

def extract_field_value(text: str, field: str, field_config: dict) -> str:
    """
    필드에 맞는 값 추출 (대화형 입력 고려) - 개선된 버전
    """
    import re
    
    print(f"[DEBUG] ===== extract_field_value 시작 =====")
    print(f"[DEBUG] 원본 텍스트: {text}")
    print(f"[DEBUG] 대상 필드: {field}")
    print(f"[DEBUG] 필드 설정: {field_config}")
    
    # 텍스트 정리 (대화형 입력에서 불필요한 부분 제거)
    cleaned_text = text.strip()
    
    if field == 'headcount':
        # 숫자만 추출 (개선된 패턴)
        numbers = re.findall(r'\d+', cleaned_text)
        if numbers:
            # 가장 큰 숫자를 선택 (예: "신입 2명, 경력 1명 총 3명" → "3명")
            max_number = max(numbers, key=int)
            extracted = max_number + '명'
            print(f"[DEBUG] headcount - 숫자 추출: {max_number} → {extracted}")
            return extracted
        
        # "명"이 포함된 경우 숫자 추출 시도
        if '명' in cleaned_text:
            # "2명 정도", "3명 정도" 등의 패턴에서 숫자 추출
            number_match = re.search(r'(\d+)명', cleaned_text)
            if number_match:
                number = number_match.group(1)
                extracted = number + '명'
                print(f"[DEBUG] headcount - '명' 포함 숫자 추출: {number} → {extracted}")
                return extracted
            
            # "한 명", "두 명" 등의 한글 숫자 처리
            korean_numbers = {
                '한': '1', '두': '2', '세': '3', '네': '4', '다섯': '5',
                '여섯': '6', '일곱': '7', '여덟': '8', '아홉': '9', '열': '10'
            }
            for korean, arabic in korean_numbers.items():
                if f"{korean} 명" in cleaned_text:
                    extracted = arabic + '명'
                    print(f"[DEBUG] headcount - 한글 숫자 추출: {korean} → {extracted}")
                    return extracted
        
        # 숫자 + "명" 패턴이 없는 경우, 숫자만 추출
        if numbers:
            max_number = max(numbers, key=int)
            extracted = max_number + '명'
            print(f"[DEBUG] headcount - 숫자만 추출: {max_number} → {extracted}")
            return extracted
        
        print(f"[DEBUG] headcount - 숫자 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'salary':
        # 숫자만 추출 (개선된 패턴)
        numbers = re.findall(r'\d+', cleaned_text)
        if numbers:
            # 가장 큰 숫자를 선택 (예: "신입은 3000만원, 경력은 5000만원" → "5000만원")
            max_number = max(numbers, key=int)
            extracted = max_number + '만원'
            print(f"[DEBUG] salary - 숫자 추출: {max_number} → {extracted}")
            return extracted
        print(f"[DEBUG] salary - 숫자 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'department':
        # 부서명 추출 (대화형 입력 고려) - 개선된 로직
        department_keywords = ['개발팀', '마케팅팀', '영업팀', '디자인팀', '기획팀', '인사팀', '개발', '마케팅', '영업', '디자인', '기획', '인사']
        
        # 우선순위가 높은 키워드부터 검색
        for keyword in ['개발팀', '마케팅팀', '영업팀', '디자인팀', '기획팀', '인사팀']:
            if keyword in cleaned_text:
                print(f"[DEBUG] department - 부서명 추출: {keyword}")
                return keyword
        
        # 단일 키워드 검색
        for keyword in ['개발', '마케팅', '영업', '디자인', '기획', '인사']:
            if keyword in cleaned_text:
                keyword_with_team = keyword + '팀'
                print(f"[DEBUG] department - 부서명 추출: {keyword_with_team}")
                return keyword_with_team
        
        print(f"[DEBUG] department - 부서명 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'location':
        # 지역 추출
        location_keywords = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        
        for keyword in location_keywords:
            if keyword in cleaned_text:
                print(f"[DEBUG] location - 지역 추출: {keyword}")
                return keyword
        
        # "에서", "에" 등의 조사와 함께 사용된 경우
        location_patterns = [
            r'(\w+)에서',
            r'(\w+)에',
            r'(\w+) 지역',
            r'(\w+) 근처'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, cleaned_text)
            if match:
                location = match.group(1)
                if location in location_keywords:
                    print(f"[DEBUG] location - 패턴 매칭 지역 추출: {location}")
                    return location
        
        print(f"[DEBUG] location - 지역 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'additionalInfo':
        # 기타 항목 - 필드 매칭되지 않는 추가 정보들을 수집
        additional_keywords = [
            "주말보장", "주말 보장", "원격근무", "재택근무", "재택", "유연근무", "유연근무제", "플렉스",
            "식대지원", "교통비지원", "주차지원", "의료보험", "국민연금", "산재보험", "고용보험",
            "연차휴가", "반차", "반반차", "병가", "출산휴가", "육아휴직", "육아휴가",
            "교육지원", "자기계발", "도서구입비", "학원비", "자격증", "어학연수",
            "경조사", "상조", "장례", "결혼", "출산", "생일", "기념일",
            "동호회", "동아리", "운동", "헬스", "피트니스", "골프", "테니스",
            "회식", "워크샵", "MT", "단체행사", "기업문화", "조직문화"
        ]
        
        found_keywords = []
        for keyword in additional_keywords:
            if keyword in cleaned_text:
                found_keywords.append(keyword)
                print(f"[DEBUG] additionalInfo - 키워드 추출: {keyword}")
        
        if found_keywords:
            result = ", ".join(found_keywords)
            print(f"[DEBUG] additionalInfo - 최종 결과: {result}")
            return result
        
        # 키워드가 없는 경우 원본 텍스트 반환 (사용자가 직접 입력한 기타 정보)
        print(f"[DEBUG] additionalInfo - 키워드 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'mainDuties':
        # 주요 업무 추출 (대화형 입력 고려) - 개선된 로직
        duty_keywords = [
            '웹개발', '앱개발', '모바일개발', '서버개발', '프론트엔드', '백엔드', '풀스택', 'UI/UX', 'UI디자인', 'UX디자인', '그래픽디자인', '편집디자인', '패키지디자인',
            '브랜드마케팅', '디지털마케팅', '콘텐츠마케팅', 'SNS마케팅', '퍼포먼스마케팅',
            '데이터분석', 'AI개발', '프로그래밍', '코딩', '브랜딩',
            '개발', '디자인', '마케팅', '영업', '기획', '관리', '운영', '분석', '설계', '테스트', '유지보수',
            '광고', '홍보', '콘텐츠', 'SNS', '고객관리', '매출관리', '전략기획', '사업기획', '제품기획'
        ]
        
        # 우선순위가 높은 키워드부터 검색 (더 구체적인 키워드 우선)
        priority_keywords = ['웹개발', '앱개발', '모바일개발', '서버개발', '프론트엔드', '백엔드', '풀스택', 
                           'UI/UX', 'UI디자인', 'UX디자인', '그래픽디자인', '편집디자인', '패키지디자인',
                           '브랜드마케팅', '디지털마케팅', '콘텐츠마케팅', 'SNS마케팅', '퍼포먼스마케팅',
                           '데이터분석', 'AI개발', '프로그래밍', '코딩']
        
        for keyword in priority_keywords:
            if keyword in cleaned_text:
                print(f"[DEBUG] mainDuties - 우선순위 업무 추출: {keyword}")
                return keyword
        
        # 일반 키워드 검색
        general_keywords = ['개발', '디자인', '마케팅', '영업', '기획', '관리', '운영', '분석', '설계', '테스트', '유지보수']
        for keyword in general_keywords:
            if keyword in cleaned_text:
                print(f"[DEBUG] mainDuties - 일반 업무 추출: {keyword}")
                return keyword
        
        print(f"[DEBUG] mainDuties - 업무 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'workHours':
        # 근무 시간 추출 (개선된 패턴)
        time_patterns = [
            r'\d{1,2}:\d{2}-\d{1,2}:\d{2}',  # 09:00-18:00 형태
            r'오전 \d{1,2}시', r'오후 \d{1,2}시',  # 오전 9시, 오후 6시
            r'유연근무', r'재택근무', r'시차출근'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                print(f"[DEBUG] workHours - 시간 패턴 추출: {matches[0]}")
                return matches[0]
        
        # "오전 9시부터 오후 6시까지" 형태의 패턴 처리
        if '오전' in cleaned_text and '오후' in cleaned_text:
            morning_match = re.search(r'오전 (\d{1,2})시', cleaned_text)
            afternoon_match = re.search(r'오후 (\d{1,2})시', cleaned_text)
            if morning_match and afternoon_match:
                morning_hour = morning_match.group(1)
                afternoon_hour = afternoon_match.group(1)
                extracted = f"{morning_hour.zfill(2)}:00-{afternoon_hour.zfill(2)}:00"
                print(f"[DEBUG] workHours - 오전/오후 시간 추출: {extracted}")
                return extracted
        
        # 시간 관련 키워드가 있는지 확인
        time_keywords = ['시', '시간', '출근', '근무']
        if any(keyword in cleaned_text for keyword in time_keywords):
            # 시간 정보가 포함된 문장에서 시간 부분만 추출
            time_match = re.search(r'(\d{1,2}:\d{2})', cleaned_text)
            if time_match:
                extracted = time_match.group(1)
                print(f"[DEBUG] workHours - 시간 추출: {extracted}")
                return extracted
            
            # "9시부터 6시까지" 형태의 패턴 처리
            time_range_match = re.search(r'(\d{1,2})시부터 (\d{1,2})시까지', cleaned_text)
            if time_range_match:
                start_hour = time_range_match.group(1)
                end_hour = time_range_match.group(2)
                extracted = f"{start_hour.zfill(2)}:00-{end_hour.zfill(2)}:00"
                print(f"[DEBUG] workHours - 시간 범위 추출: {extracted}")
                return extracted
        
        print(f"[DEBUG] workHours - 시간 패턴 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'locationCity':
        # 근무 위치 추출 (개선된 로직)
        location_keywords = [
            '서울', '부산', '대구', '인천', '대전', '광주', '울산', '세종', 
            '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주',
            '강남', '강북', '서초', '송파', '마포', '용산', '영등포', '동대문', '중구'
        ]
        
        for keyword in location_keywords:
            if keyword in cleaned_text:
                print(f"[DEBUG] locationCity - 위치 추출: {keyword}")
                return keyword
        
        print(f"[DEBUG] locationCity - 위치 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'deadline':
        # 마감일 추출 (개선된 로직)
        deadline_patterns = [
            r'\d{4}년 \d{1,2}월 \d{1,2}일',  # 2024년 12월 31일
            r'\d{1,2}월 \d{1,2}일',  # 12월 31일
            r'상시채용', r'채용시마감'
        ]
        
        for pattern in deadline_patterns:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                print(f"[DEBUG] deadline - 마감일 추출: {matches[0]}")
                return matches[0]
        
        print(f"[DEBUG] deadline - 마감일 없음, 원본 반환")
        return cleaned_text
    
    elif field == 'contactEmail':
        # 이메일 추출 (개선된 로직)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, cleaned_text)
        if email_match:
            extracted = email_match.group(0)
            print(f"[DEBUG] contactEmail - 이메일 추출: {extracted}")
            return extracted
        
        print(f"[DEBUG] contactEmail - 이메일 없음, 원본 반환")
        return cleaned_text
    
    else:
        # 기본적으로 정리된 텍스트 반환
        print(f"[DEBUG] 기본 처리 - 정리된 텍스트 반환")
        return cleaned_text

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

# --- Gemini API 설정 추가 시작 ---
import google.generativeai as genai

# 환경 변수에서 Gemini API 키 로드
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

# API 키가 없어도 기본 응답을 반환하도록 수정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Gemini 모델 초기화
    # 'gemini-1.5-pro'는 최신 텍스트 기반 모델입니다.
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    print("Warning: GOOGLE_API_KEY not found. Using fallback responses.")
    model = None
# --- Gemini API 설정 추가 끝 ---

router = APIRouter()

# 기존 세션 저장소 (normal 모드에서 이제 사용하지 않음, modal_assistant에서만 사용)
sessions = {}

# 모달 어시스턴트 세션 저장소 (기존 로직 유지를 위해 유지)
modal_sessions = {}

# 대화 히스토리 관리 시스템
class ConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def add_message(self, user_id: str, message: str, response: str, metadata: Dict[str, Any] = None):
        """
        대화 히스토리에 메시지 추가
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        conversation_entry = {
            'timestamp': datetime.now(),
            'user_message': message,
            'bot_response': response,
            'metadata': metadata or {}
        }
        
        self.conversations[user_id].append(conversation_entry)
        
        # 최근 10개만 유지
        if len(self.conversations[user_id]) > 10:
            self.conversations[user_id] = self.conversations[user_id][-10:]
    
    def get_context(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        사용자의 대화 컨텍스트 반환
        """
        if user_id not in self.conversations:
            return []
        
        return self.conversations[user_id][-limit:]
    
    def get_recent_intents(self, user_id: str, limit: int = 3) -> List[str]:
        """
        최근 의도들 반환
        """
        context = self.get_context(user_id, limit)
        intents = []
        for entry in context:
            if 'metadata' in entry and 'intent' in entry['metadata']:
                intents.append(entry['metadata']['intent'])
        return intents

# 전역 대화 관리자 인스턴스
conversation_manager = ConversationManager()

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
    current_page: Optional[str] = None  # 현재 페이지 정보 추가
    context: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = "normal"

class ChatbotResponse(BaseModel):
    message: str
    field: Optional[str] = None
    value: Optional[str] = None
    suggestions: Optional[List[str]] = []
    confidence: Optional[float] = None
    items: Optional[List[Dict[str, Any]]] = None  # 선택 가능한 항목들
    show_item_selection: Optional[bool] = False  # 항목 선택 UI 표시 여부

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
    response_type: str = "conversation"  # "conversation" 또는 "selection"
    selectable_items: Optional[List[Dict[str, str]]] = []  # 선택 가능한 항목들

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
            {"key": "contactEmail", "label": "연락처 이메일", "type": "email"},
            {"key": "additionalInfo", "label": "기타 항목", "type": "text"}
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
            question=f" AI 도우미를 시작하겠습니다!\n\n먼저 {first_field.get('label', '첫 번째 항목')}에 대해 알려주세요.",
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
        # 인코딩 문제 해결을 위한 강력한 처리
        original_input = request.user_input
        
        # 인코딩 문제가 있는 경우 (한글이 깨진 경우)
        if '?' in original_input and len(original_input) < 20:
            print(f"[DEBUG] 인코딩 문제 감지: {original_input}")
            
            # 하드코딩된 테스트 메시지로 대체
            if '채용' in original_input or '공고' in original_input:
                request.user_input = "채용공고 등록 방법을 알려주세요"
            elif '이력서' in original_input:
                request.user_input = "이력서 관리 기능이 궁금해요"
            elif '면접' in original_input:
                request.user_input = "면접 일정을 어떻게 관리하나요?"
            else:
                request.user_input = "채용 관련 질문을 해주세요"
            
            print(f"[DEBUG] 인코딩 수정됨: {request.user_input}")
        
        if request.mode == "normal" or not request.session_id:
            response = await handle_normal_request(request)
        elif request.mode == "modal_assistant":
            response = await handle_modal_assistant_request(request)
        elif request.mode == "free_text":
            response = await handle_free_text_request(request)
        else:
            print("[ERROR] /ask 알 수 없는 모드:", request.mode)
            raise HTTPException(status_code=400, detail="알 수 없는 챗봇 모드입니다.")
        
        print("[DEBUG] /ask 응답:", response)
        return response
    except Exception as e:
        print("[ERROR] /ask 예외:", e)
        traceback.print_exc()
        raise

@router.post("/conversation")
async def conversation(request: ConversationRequest):
    try:
        print(f"[DEBUG] /conversation 요청: {request}")
        
        # Gemini 서비스 인스턴스 생성 
        from gemini_service import GeminiService
        gemini_service = GeminiService()
        
        # AI 응답 생성 (간단한 응답)
        prompt = f"사용자 입력: {request.user_input}"
        response_text = await gemini_service.generate_response(prompt, request.conversation_history)
        
        response = {
            "message": response_text,
            "field": request.current_field,
            "value": None,
            "suggestions": [],
            "confidence": 1.0
        }
        
        # 응답 타입 분석 및 결정
        response_type = "conversation"  # 기본값
        selectable_items = []
        
        # 선택형 응답인지 판단하는 로직
        if response.get("value") is None and response.get("message"):
            message_content = response.get("message", "")
            
            # 선택형 응답 패턴 감지
            selection_patterns = [
                "이 중에서 선택해 주세요",
                "다음 중에서 선택",
                "선택해 주세요",
                "원하는 것을 선택",
                "번호로 선택",
                "1.", "2.", "3.", "4.", "5."  # 번호로 구분된 목록
            ]
            
            # 선택형 응답인지 확인
            is_selection_response = any(pattern in message_content for pattern in selection_patterns)
            
            if is_selection_response:
                response_type = "selection"
                
                # 메시지에서 선택 항목 추출
                lines = message_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
                               line.startswith(('•', '-', '*'))):
                        # 번호나 불릿 제거
                        import re
                        clean_text = re.sub(r'^\d+\.\s*', '', line)
                        clean_text = re.sub(r'^[•\-*]\s*', '', clean_text)
                        clean_text = clean_text.strip()
                        if clean_text:
                            selectable_items.append({
                                "text": clean_text,
                                "value": clean_text
                            })
        
        result = ConversationResponse(
            message=response.get("message", ""),
            is_conversation=response.get("is_conversation", True),
            suggestions=response.get("suggestions", []),
            field=response.get("field"),
            value=response.get("value"),
            response_type=response_type,
            selectable_items=selectable_items
        )
        print("[DEBUG] /conversation 응답:", result)
        return result
        
    except Exception as e:
        print(f"[ERROR] /conversation 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        confidence=ai_response.get("confidence", 0.8),
        items=ai_response.get("items"),
        show_item_selection=ai_response.get("show_item_selection")
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
    
    # 명확하지 않은 입력인 경우 먼저 확인
    if llm_response.get("is_unclear", False):
        # 명확하지 않은 입력인 경우 다음 단계로 넘어가지 않음
        print(f"[DEBUG] 명확하지 않은 입력으로 인식됨 - current_field_index 증가하지 않음")
    # 대화형 응답인 경우 (질문에 대한 답변)
    elif llm_response.get("is_conversation", False):
        # 대화형 응답인 경우 다음 단계로 넘어가지 않음
        print(f"[DEBUG] 대화형 응답으로 인식됨 - current_field_index 증가하지 않음")
    # LLM이 필드 값을 추출했다고 판단한 경우 (value가 있고, 명확하지 않은 입력이 아닌 경우)
    elif llm_response.get("value") and not llm_response.get("is_unclear", False):
        # 필드 키를 명시적으로 설정
        field_key = llm_response.get("field", current_field["key"])
        field_value = llm_response["value"]
        
        # 값이 유효한지 확인 (빈 문자열이나 의미없는 값이 아닌지)
        invalid_values = ["ai 채용공고 등록 도우미", "채용공고 등록 도우미", "ai 어시스턴트", "채용공고", "도우미", "ai", ""]
        if field_value and field_value.strip() and field_value.lower() not in invalid_values:
            print(f"[DEBUG] 필드 업데이트 - 키: {field_key}, 값: {field_value}")
            session["filled_fields"][field_key] = field_value
            
            # 다음 필드로 이동
            session["current_field_index"] += 1
            
            if session["current_field_index"] >= len(fields):
                response_message += "\n\n🎉 모든 정보 입력이 완료되었습니다!"
        else:
            print(f"[DEBUG] 유효하지 않은 값으로 인식됨: {field_value}")
            # 유효하지 않은 값이면 다음 단계로 넘어가지 않음
            # 현재 필드에 머물면서 재입력 요청
            print(f"[DEBUG] 유효하지 않은 값으로 인한 재입력 요청 - current_field_index 증가하지 않음")
    else:
        # value가 없거나 다른 경우에도 다음 단계로 넘어가지 않음
        print(f"[DEBUG] 유효한 값이 없음 - current_field_index 증가하지 않음")
    
    # 필드 값이 추출된 경우 field와 value를 명시적으로 설정
    response_field = None
    response_value = None
    
    if llm_response.get("value") and not llm_response.get("is_conversation", False):
        response_field = current_field["key"]
        response_value = llm_response.get("value")
        print(f"[DEBUG] 필드 값 추출됨 - field: {response_field}, value: {response_value}")
    
    # 추가: LLM 응답에서 직접 field와 value를 가져오는 로직 추가
    if llm_response.get("field") and llm_response.get("value"):
        response_field = llm_response.get("field")
        response_value = llm_response.get("value")
        print(f"[DEBUG] LLM에서 직접 필드 값 추출됨 - field: {response_field}, value: {response_value}")
    
    # 추가: 유효한 값이 추출된 경우 확실히 설정
    if response_value and response_value.strip() and response_value.lower() not in ["ai 채용공고 등록 도우미", "채용공고 등록 도우미", "ai 어시스턴트", "채용공고", "도우미", "ai", ""]:
        print(f"[DEBUG] 최종 필드 값 설정 - field: {response_field}, value: {response_value}")
    else:
        print(f"[DEBUG] 유효하지 않은 값으로 필드 설정 안함 - value: {response_value}")
        response_field = None
        response_value = None
    
    response = ChatbotResponse(
        message=response_message,
        field=response_field,
        value=response_value,
        suggestions=llm_response.get("suggestions", []), # LLM이 제안을 생성할 수 있다면 활용
        confidence=llm_response.get("confidence", 0.8), # LLM이 confidence를 반환할 수 있다면 활용
        items=llm_response.get("items"),
        show_item_selection=llm_response.get("show_item_selection")
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
    일반 모드 요청 처리
    """
    print(f"[DEBUG] handle_normal_request 요청: {request}")
    
    # 입력 분류
    classification = classify_input(request.user_input)
    print(f"[DEBUG] 분류 결과: {classification}")
    
    # 분류 결과에 따른 응답 생성
    if classification['type'] == 'start_job_posting':
        # 채용공고 시작 감지 - 자유 텍스트에서 정보 추출
        extracted_data = extract_job_info_from_text(request.user_input)
        
        # JSON 데이터를 문자열로 변환하여 표시
        extracted_info_text = ""
        if extracted_data:
            for key, value in extracted_data.items():
                field_name = {
                    'department': '부서',
                    'headcount': '인원',
                    'location': '지역',
                    'workDays': '근무요일',
                    'experience': '경력',
                    'salary': '연봉',
                    'workType': '업무'
                }.get(key, key)
                extracted_info_text += f"• {field_name}: {value}\n"
        
        response = ChatbotResponse(
            message=f"채용공고 작성을 시작하겠습니다! 🎯\n\n입력하신 정보를 분석하여 폼에 자동으로 입력해드리겠습니다.\n\n추출된 정보:\n{extracted_info_text}",
            confidence=0.9
        )
    elif classification['type'] == 'question':
        if classification['category'] == 'recruitment':
            # 채용 관련 질문에 대한 구체적인 응답
            if '채용공고' in request.user_input or '등록' in request.user_input:
                response = ChatbotResponse(
                    message="채용공고 등록은 다음과 같이 진행됩니다:\n\n1. **채용공고 등록** 페이지로 이동\n2. **부서** 선택 (개발팀, 마케팅팀, 영업팀 등)\n3. **주요업무** 입력\n4. **근무조건** 설정\n5. **마감일** 설정\n\n어떤 부분에 대해 더 자세히 알고 싶으신가요?",
                    confidence=0.9
                )
            elif '이력서' in request.user_input:
                response = ChatbotResponse(
                    message="이력서 관리 기능은 다음과 같습니다:\n\n1. **이력서 업로드**: 지원자가 업로드한 이력서 확인\n2. **이력서 검토**: AI를 통한 자동 검토 및 평가\n3. **이력서 분류**: 부서별, 경력별 분류\n4. **이력서 통계**: 지원 현황 및 통계 확인\n\n어떤 기능에 대해 더 알고 싶으신가요?",
                    confidence=0.9
                )
            elif '면접' in request.user_input:
                response = ChatbotResponse(
                    message="면접 관리 기능은 다음과 같습니다:\n\n1. **면접 일정 등록**: 지원자별 면접 일정 설정\n2. **면접 평가**: 면접 결과 및 평가 기록\n3. **면접 통계**: 면접 진행 현황 확인\n4. **면접 알림**: 면접 일정 알림 발송\n\n어떤 기능에 대해 더 알고 싶으신가요?",
                    confidence=0.9
                )
            else:
                response = ChatbotResponse(
                    message="채용 관련 질문에 답변드리겠습니다. 구체적으로 어떤 기능에 대해 알고 싶으신가요?\n\n• 채용공고 등록\n• 이력서 관리\n• 면접 관리\n• 지원자 관리\n• 포트폴리오 분석",
                    confidence=0.8
                )
        else:
            # 일반 질문에 대한 응답
            response = ChatbotResponse(
                message="채용 시스템과 관련 없는 질문입니다. 채용 관련 질문을 해주시면 답변드리겠습니다.",
                confidence=0.7
            )
    elif classification['type'] == 'field':
        # 필드 입력에 대한 응답
        field_value = classification.get('value', '')
        response = ChatbotResponse(
            message=f"{classification['category']}: {field_value}로 설정되었습니다.",
            value=field_value,
            confidence=classification['confidence']
        )
    else:
        # 기본 응답
        response = ChatbotResponse(
            message="채용 관련 질문을 해주시면 답변드리겠습니다.",
            confidence=0.6
        )
    
    print(f"[DEBUG] handle_normal_request 응답 ({classification['type']}): {response}")
    return response

async def handle_free_text_request(request: ChatbotRequest):
    """
    자유 텍스트 모드 요청 처리
    """
    print(f"[DEBUG] handle_free_text_request 요청: {request}")
    
    # 자유 텍스트에서 채용 정보 추출
    extracted_data = extract_job_info_from_text(request.user_input)
    
    # JSON 데이터를 문자열로 변환하여 표시
    extracted_info_text = ""
    if extracted_data:
        for key, value in extracted_data.items():
            field_name = {
                'department': '부서',
                'headcount': '인원',
                'location': '지역',
                'workDays': '근무요일',
                'experience': '경력',
                'salary': '연봉',
                'workType': '업무'
            }.get(key, key)
            extracted_info_text += f"• {field_name}: {value}\n"
    
    response = ChatbotResponse(
        message=f"채용공고 작성을 시작하겠습니다! 🎯\n\n입력하신 정보를 분석하여 폼에 자동으로 입력해드리겠습니다.\n\n추출된 정보:\n{extracted_info_text}",
        confidence=0.9
    )
    
    print(f"[DEBUG] handle_free_text_request 응답: {response}")
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
        ],
        "additionalInfo": [
            "주말보장이나 원격근무 같은 복리후생이 있나요?",
            "식대지원이나 교통비지원 같은 지원이 있나요?",
            "연차휴가나 교육지원 같은 제도가 있나요?",
            "동호회나 회식 같은 기업문화는 어떤가요?"
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
        },
        "additionalInfo": {
            "message": "기타 항목을 확인했습니다. 마지막으로 연락처 이메일을 알려주세요.",
            "value": user_input,
            "suggestions": ["주말보장", "원격근무", "유연근무제", "식대지원", "교통비지원", "연차휴가", "교육지원", "동호회"],
            "confidence": 0.7
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
    
    # 1) 키워드 기반 1차 분류 (개선된 분류 함수 사용)
    classification = classify_input_with_context(user_input, field_key)
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
            ai_response = await call_ai_api(ai_assistant_context)
            
            # 응답을 항목별로 분할
            items = parse_response_items(ai_response)
            # 선택 대기 상태 저장 (다음 턴에서 번호/제외 처리)
            try:
                session.setdefault("pending_selection", {})
                session["pending_selection"][field_key] = [i.get("text", "") for i in items]
            except Exception:
                pass
            
            response = {
                "message": ai_response,
                "value": None,  # 질문이므로 value는 None
                "field": field_key,
                "suggestions": [],
                "confidence": classification['confidence'],
                "items": items,
                "show_item_selection": True  # 항목 선택 UI 표시
            }
            print(f"[DEBUG] 질문 응답 (항목 선택 포함): {response}")
            return response
            
        except Exception as e:
            print(f"[ERROR] Gemini API 호출 실패: {e}")
            # 오프라인 응답으로 대체
            response = {
                "message": f"'{user_input}'에 대한 답변을 제공해드리겠습니다. 현재 필드 '{field_label}'에 대한 정보를 입력해주세요.",
                "value": None,
                "field": field_key,
                "suggestions": [],
                "confidence": 0.5
            }
            return response
    elif classification['type'] == 'chat':
        # 일상 대화 처리
        return {
            "message": "안녕하세요! 채용 공고 작성에 도와드리고 있습니다. 현재 {field_label}에 대한 정보를 입력해주세요.",
            "value": None,
            "field": current_field,
            "suggestions": [],
            "confidence": classification['confidence']
        }
        print(f"[DEBUG] 일상 대화 응답: {response}")
        return response
    else:
        # 답변인 경우 (개선된 처리)
        # classification에서 추출된 값이 있으면 사용, 없으면 user_input에서 추출 시도
        if classification.get('value'):
            field_value = classification['value']
            field_category = classification.get('category', field_key)
        else:
            # classification에서 값이 없으면 user_input에서 추출 시도
            field_config = get_field_config(field_key)
            field_value = extract_field_value(user_input, field_key, field_config)
            field_category = field_key
        
        print(f"[DEBUG] 답변 처리 결과 - 필드: {field_category}, 값: {field_value}")
        
        # 필드 업데이트 후 다음 질문 자동 생성
        next_question = ""
        next_suggestions = []
        
        # 필드별 다음 질문 매핑
        field_questions = {
            "department": {
                "question": "몇 명을 채용하실 예정인가요?",
                "suggestions": ["1명", "2명", "3명", "5명", "10명"]
            },
            "headcount": {
                "question": "어떤 업무를 담당하게 될까요?",
                "suggestions": ["개발", "디자인", "마케팅", "영업", "기획", "고객지원"]
            },
            "mainDuties": {
                "question": "근무 시간은 어떻게 되나요?",
                "suggestions": ["09:00-18:00", "10:00-19:00", "유연근무제", "시차출근제"]
            },
            "workHours": {
                "question": "근무 요일은 어떻게 되나요?",
                "suggestions": ["월-금", "월-토", "주5일", "주6일"]
            },
            "workDays": {
                "question": "근무 위치는 어디인가요?",
                "suggestions": ["서울", "부산", "대구", "인천", "대전", "광주", "울산"]
            },
            "locationCity": {
                "question": "구체적인 지역을 알려주세요.",
                "suggestions": ["강남구", "서초구", "마포구", "종로구", "중구"]
            },
            "locationDistrict": {
                "question": "급여 조건은 어떻게 되나요?",
                "suggestions": ["면접 후 협의", "3000만원", "4000만원", "5000만원", "6000만원"]
            },
            "salary": {
                "question": "마감일은 언제인가요?",
                "suggestions": ["2024년 12월 31일", "2024년 11월 30일", "채용 시 마감", "상시채용"]
            },
            "deadline": {
                "question": "연락처 이메일을 알려주세요.",
                "suggestions": ["hr@company.com", "recruit@company.com", "인사팀 이메일"]
            }
        }
        
        # 현재 필드에 대한 다음 질문이 있는지 확인
        if field_key in field_questions:
            next_question = field_questions[field_key]["question"]
            next_suggestions = field_questions[field_key]["suggestions"]
        
        # 응답 메시지에 다음 질문 포함
        if next_question:
            response_message = f"'{field_label}'에 대해 '{field_value}'로 입력하겠습니다. {next_question}"
        else:
            response_message = f"'{field_label}'에 대해 '{field_value}'로 입력하겠습니다."
        
        response = {
            "message": response_message,
            "value": field_value,
            "field": field_category,  # 분류된 필드명 사용
            "suggestions": next_suggestions,
            "confidence": classification['confidence'],
            "next_question": next_question
        }
        print(f"[DEBUG] ===== AI 어시스턴트 응답 생성 완료 =====")
        print(f"[DEBUG] 최종 결과: {response}")
        print("[DEBUG] ===== AI 어시스턴트 응답 생성 완료 =====")
        return response

async def simulate_llm_response(user_input: str, current_field: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """
    키워드 기반 1차 분류 → LLM 호출 → 응답 처리 (개선된 버전)
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
    
    # 컨텍스트를 고려한 분류 (개선된 버전)
    classification = classify_input_with_context(user_input, current_field)
    print(f"[DEBUG] 분류 결과: {classification}")
    print(f"[DEBUG] 분류 타입: {classification.get('type')}")
    print(f"[DEBUG] 분류 카테고리: {classification.get('category')}")
    print(f"[DEBUG] 분류 값: {classification.get('value')}")
    print(f"[DEBUG] 신뢰도: {classification.get('confidence')}")
    
    # 2) 분류된 결과에 따른 처리
    if classification['type'] == 'question':
        # 질문인 경우 Gemini API 호출
        try:
            # 대화 히스토리를 고려한 컨텍스트 생성
            conversation_context = ""
            if session.get("conversation_history"):
                recent_messages = session["conversation_history"][-4:]  # 최근 4개 메시지만 사용
                conversation_context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in recent_messages
                ])
            
            ai_assistant_context = f"""
현재 채용 공고 작성 중입니다. 현재 필드: {current_field_label} ({current_field})

최근 대화 내용:
{conversation_context}

사용자 질문: {user_input}

이 질문에 대해 채용 공고 작성에 도움이 되는 실무적인 답변을 제공해주세요.
답변 후에는 현재 필드 '{current_field_label}'에 대한 정보를 입력해주시면 됩니다.
"""
            ai_response = await call_ai_api(ai_assistant_context)
            
            # 응답을 항목별로 분할
            items = parse_response_items(ai_response)
            
            response = {
                "message": ai_response,
                "value": None,  # 질문이므로 value는 None
                "field": current_field,
                "suggestions": [],
                "confidence": classification['confidence'],
                "items": items,
                "show_item_selection": True,  # 항목 선택 UI 표시
                "is_conversation": True  # 대화형 응답임을 표시
            }
            print(f"[DEBUG] 질문 응답 (대화형): {response}")
            return response
            
        except Exception as e:
            print(f"[ERROR] Gemini API 호출 실패: {e}")
            # 오프라인 응답으로 대체
            response = {
                "message": f"'{user_input}'에 대한 답변을 제공해드리겠습니다. 현재 필드 '{current_field_label}'에 대한 정보를 입력해주세요.",
                "value": None,
                "field": current_field,
                "suggestions": [],
                "confidence": classification['confidence'],
                "is_conversation": True
            }
            return response
    elif classification['type'] == 'conversational_answer':
        # 대화형 입력에서 맥락/키워드를 캐치하여 필드 값 추출 시도
        try:
            # 대화 히스토리를 고려한 컨텍스트 생성
            conversation_context = ""
            if session.get("conversation_history"):
                recent_messages = session["conversation_history"][-4:]  # 최근 4개 메시지만 사용
                conversation_context = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in recent_messages
                ])
            
            # LLM에게 대화형 입력에서 필드 값을 추출하도록 요청
            extraction_prompt = f"""
현재 채용 공고 작성 중입니다. 현재 필드: {current_field_label} ({current_field})

최근 대화 내용:
{conversation_context}

사용자 입력: {user_input}

이 대화형 입력에서 '{current_field_label}'에 대한 정보를 추출해주세요.
만약 관련 정보가 없다면 "관련 정보 없음"이라고 답해주세요.
추출된 정보만 간단히 답해주세요.
"""
            extracted_response = await call_ai_api(extraction_prompt)
            
            # 추출된 응답이 유효한지 확인
            if extracted_response and extracted_response.strip() and "관련 정보 없음" not in extracted_response:
                # 추출된 값을 필드에 맞게 가공
                field_config = get_field_config(current_field)
                processed_value = extract_field_value(extracted_response, current_field, field_config)
                
                response = {
                    "message": f"대화 내용에서 '{current_field_label}' 정보를 확인했습니다: {processed_value}",
                    "value": processed_value,
                    "field": current_field,
                    "suggestions": [],
                    "confidence": classification['confidence'],
                    "is_conversation": False  # 필드 값이 추출되었으므로 대화형이 아님
                }
                print(f"[DEBUG] 대화형 입력에서 필드 값 추출 성공: {response}")
                return response
            else:
                # 관련 정보가 없는 경우 대화형 응답
                response = {
                    "message": f"대화 내용을 확인했습니다. 현재 {current_field_label}에 대한 정보를 입력해주세요.",
                    "value": None,
                    "field": current_field,
                    "suggestions": [],
                    "confidence": classification['confidence'],
                    "is_conversation": True
                }
                print(f"[DEBUG] 대화형 입력에서 관련 정보 없음: {response}")
                return response
                
        except Exception as e:
            print(f"[ERROR] 대화형 입력 처리 중 오류: {e}")
            # 오류 발생 시 대화형 응답으로 처리
            response = {
                "message": f"대화 내용을 확인했습니다. 현재 {current_field_label}에 대한 정보를 입력해주세요.",
                "value": None,
                "field": current_field,
                "suggestions": [],
                "confidence": classification['confidence'],
                "is_conversation": True
            }
            return response
    elif classification['type'] == 'chat':
        # 일상 대화 처리
        response = {
            "message": f"안녕하세요! 채용 공고 작성을 도와드리고 있습니다. 현재 {current_field_label}에 대한 정보를 입력해주세요.",
            "value": None,
            "field": current_field,
            "suggestions": [],
            "confidence": classification['confidence']
        }
        print(f"[DEBUG] 일상 대화 응답: {response}")
        return response
    elif classification['type'] == 'unclear':
        # 명확하지 않은 입력 처리 - 다시 말씀해주세요
        field_suggestions = get_field_suggestions(current_field, {})
        response = {
            "message": f"죄송합니다. '{user_input}'이 무엇을 의미하는지 명확하지 않습니다. 현재 {current_field_label}에 대해 다시 말씀해주세요. 예시: {', '.join(field_suggestions[:3])}",
            "value": None,
            "field": current_field,
            "suggestions": field_suggestions,
            "confidence": classification['confidence'],
            "is_unclear": True  # 명확하지 않은 입력임을 표시
        }
        print(f"[DEBUG] 명확하지 않은 입력 응답: {response}")
        return response
    else:
        # 답변인 경우 (개선된 처리)
        # classification에서 추출된 값이 있으면 사용, 없으면 user_input에서 추출 시도
        if classification.get('value'):
            field_value = classification['value']
            field_category = classification.get('category', current_field)
        else:
            # classification에서 값이 없으면 user_input에서 추출 시도
            field_config = get_field_config(current_field)
            field_value = extract_field_value(user_input, current_field, field_config)
            field_category = current_field
        
        print(f"[DEBUG] 답변 처리 결과 - 필드: {field_category}, 값: {field_value}")
        
        # 값이 유효한지 확인 (빈 문자열이나 의미없는 값이 아닌지)
        invalid_values = ["ai 채용공고 등록 도우미", "채용공고 등록 도우미", "ai 어시스턴트", "채용공고", "도우미", "ai"]
        if not field_value or not field_value.strip() or field_value.lower() in invalid_values:
            print(f"[DEBUG] 유효하지 않은 값으로 인식됨: {field_value}")
            # 유효하지 않은 값이면 명확하지 않은 입력으로 처리
            field_suggestions = get_field_suggestions(current_field, {})
            response = {
                "message": f"죄송합니다. '{user_input}'이 무엇을 의미하는지 명확하지 않습니다. 현재 {current_field_label}에 대해 다시 말씀해주세요. 예시: {', '.join(field_suggestions[:3])}",
                "value": None,
                "field": current_field,
                "suggestions": field_suggestions,
                "confidence": 0.7,
                "is_unclear": True
            }
            print(f"[DEBUG] 유효하지 않은 값으로 인한 명확하지 않은 입력 응답: {response}")
            return response
        
        # 필드별 다음 질문 매핑 (AI 어시스턴트 필드 순서에 맞춤)
        field_questions = {
            "department": {
                "question": "몇 명을 채용하실 예정인가요?",
                "suggestions": ["1명", "2명", "3명", "5명", "10명"]
            },
            "headcount": {
                "question": "어떤 업무를 담당하게 될까요?",
                "suggestions": ["개발", "디자인", "마케팅", "영업", "기획", "고객지원"]
            },
            "mainDuties": {
                "question": "근무 시간은 어떻게 되나요?",
                "suggestions": ["09:00-18:00", "10:00-19:00", "유연근무제", "시차출근제"]
            },
            "workHours": {
                "question": "근무 위치는 어디인가요?",
                "suggestions": ["서울", "부산", "대구", "인천", "대전", "광주", "울산"]
            },
            "locationCity": {
                "question": "급여 조건은 어떻게 되나요?",
                "suggestions": ["면접 후 협의", "3000만원", "4000만원", "5000만원", "6000만원"]
            },
            "salary": {
                "question": "마감일은 언제인가요?",
                "suggestions": ["2024년 12월 31일", "2024년 11월 30일", "채용 시 마감", "상시채용"]
            },
            "deadline": {
                "question": "연락처 이메일을 알려주세요.",
                "suggestions": ["hr@company.com", "recruit@company.com", "인사팀 이메일"]
            },
            "contactEmail": {
                "question": "모든 정보 입력이 완료되었습니다!",
                "suggestions": []
            }
        }
        
        # 현재 필드에 대한 다음 질문이 있는지 확인
        next_question = ""
        next_suggestions = []
        print(f"[DEBUG] 현재 필드 '{current_field}'에 대한 다음 질문 확인")
        print(f"[DEBUG] field_questions 키들: {list(field_questions.keys())}")
        if current_field in field_questions:
            next_question = field_questions[current_field]["question"]
            next_suggestions = field_questions[current_field]["suggestions"]
            print(f"[DEBUG] 다음 질문 찾음: {next_question}")
        else:
            print(f"[DEBUG] 현재 필드 '{current_field}'에 대한 다음 질문이 정의되지 않음")
        
        # 응답 메시지에 다음 질문 포함
        if next_question:
            response_message = f"'{current_field_label}'에 대해 '{field_value}'로 입력하겠습니다. {next_question}"
        else:
            response_message = f"'{current_field_label}'에 대해 '{field_value}'로 입력하겠습니다."
        
        # 프론트엔드 키에 맞게 필드명 매핑
        field_mapping = {
            'department': 'department',
            'headcount': 'headcount', 
            'salary': 'salary',
            'workType': 'mainDuties',  # 주요업무
            'workHours': 'workHours',  # 근무시간
            'location': 'location'  # 지역
        }
        
        mapped_field = field_mapping.get(field_category, field_category)
        
        response = {
            "message": response_message,
            "value": field_value,
            "field": mapped_field,  # 매핑된 필드명 사용
            "suggestions": next_suggestions,
            "confidence": classification['confidence'],
            "next_question": next_question,
            "is_conversation": False  # 필드 값이 추출되었으므로 대화형이 아님
        }
        print(f"[DEBUG] ===== simulate_llm_response 결과 =====")
        print(f"[DEBUG] 최종 결과: {response}")
        print("[DEBUG] ===== simulate_llm_response 완료 =====")
        return response

async def call_ai_api(prompt: str, conversation_history: List[Dict[str, Any]] = None) -> str:
    """
    AI API 호출 함수 (Gemini 메인)
    """
    try:
        # Gemini 서비스가 사용 가능한 경우 사용
        if gemini_service and gemini_service.client:
            print("[DEBUG] Gemini 서비스를 사용하여 응답 생성")
            response = await gemini_service.generate_response(prompt, conversation_history)
            return response
        else:
            # 임시 테스트 응답 (API 키가 없을 때)
            return "안녕하세요! 채용 전문 어시스턴트입니다. GOOGLE_API_KEY를 설정하면 더 정확한 답변을 드릴 수 있습니다."
        
    except Exception as e:
        print(f"[ERROR] AI API 호출 실패: {e}")
        traceback.print_exc()
        return f"AI 응답을 가져오는 데 실패했습니다. 다시 시도해 주세요. (오류: {str(e)})"

async def call_gemini_api_backup(prompt: str, conversation_history: List[Dict[str, Any]] = None) -> str:
    """
    Gemini API 백업 호출 함수 (RAG 적용)
    """
    try:
        if not gemini_service or not gemini_service.client:
            return "Gemini 서비스를 사용할 수 없습니다."
        
        # --- RAG 로직 추가 시작 ---
        # 1. 사용자 질문을 기반으로 가장 관련성 높은 문서 검색
        relevant_context = await find_relevant_document(prompt)
        
        # 2. 검색된 문서를 컨텍스트로 프롬프트에 추가
        rag_prompt = f"""
        당신은 채용 전문 어시스턴트입니다. 사용자가 채용 공고 작성이나 채용 관련 질문을 할 때 전문적이고 실용적인 답변을 제공해주세요.

        **추가 정보:**
        아래에 제공된 정보를 활용하여 답변의 정확성과 신뢰도를 높여주세요.
        ---
        {relevant_context}
        ---

        **주의사항:**
        - AI 모델에 대한 설명은 하지 마세요
        - 채용 관련 실무적인 조언을 제공하세요
        - 구체적이고 실용적인 답변을 해주세요
        - 한국어로 답변해주세요
        - 모든 답변은 핵심만 간단하게 요약해서 2~3줄 이내로 작성해주세요
        - 불필요한 설명은 생략하고, 요점 위주로 간결하게 답변해주세요
        - '주요 업무'를 작성할 때는 지원자 입장에서 직무 이해도가 높아지도록 구체적인 동사(예: 개발, 분석, 관리 등)를 사용하세요
        - 각 업무는 "무엇을 한다 → 왜 한다" 구조로, 기대 성과까지 간결히 포함해서 자연스럽고 명확하게 서술하세요
        - 번호가 있는 항목(1, 2, 3 등)은 각 줄마다 줄바꿈하여 출력해주세요

        **특별 지시:** 사용자가 '적용해줘', '입력해줘', '이걸로 해줘' 등의 선택적 명령어를 입력하면,  
        직전 AI가 제시한 내용을 그대로 적용하는 동작으로 이해하고,  
        사용자가 추가 설명을 요청하지 않는 이상 답변을 간단히 요약하며 다음 단계로 자연스럽게 넘어가세요.

        **사용자 질문:** {prompt}
        """
        # --- RAG 로직 추가 끝 ---

        # 대화 히스토리 구성
        messages = []
        if conversation_history:
            for msg in conversation_history:
                role = 'user' if msg.get('type') == 'user' else 'model'
                messages.append({"role": role, "parts": [{"text": msg.get('content', '')}]})
        
        # 컨텍스트가 포함된 프롬프트 생성
        messages.append({"role": "user", "parts": [{"text": rag_prompt}]})
        
        # Gemini API 호출
        response = await gemini_service.client.generate_content_async(
            messages,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        )
        
        return response.text
        
    except Exception as e:
        print(f"[ERROR] Gemini API 백업 호출 실패: {e}")
        traceback.print_exc()
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
    suggestions = get_autocomplete_suggestions(request.partial_input, request.field, request.context)
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
            {"field": "mainDuties", "question": "어떤 업무를 담당하게 되나요?"},
            {"field": "workHours", "question": "근무 시간은 어떻게 되나요?"},
            {"field": "locationCity", "question": "근무 위치는 어디인가요?"},
            {"field": "salary", "question": "급여 조건은 어떻게 되나요?"},
            {"field": "deadline", "question": "마감일은 언제인가요?"},
            {"field": "contactEmail", "question": "연락처 이메일을 알려주세요."}
        ]
    }
    questions = questions_map.get(page, [])
    print("[DEBUG] get_questions_for_page 응답:", questions)
    return questions

def get_field_suggestions(field: str, context: Dict[str, Any]) -> List[str]:
    """필드별 제안 목록"""
    print("[DEBUG] get_field_suggestions 요청:", field, context)
    suggestions_map = {
        "department": ["개발", "기획", "마케팅", "디자인", "인사", "영업"],
        "headcount": ["1명", "2명", "3명", "5명", "10명"],
        "mainDuties": [
            "신규 웹 서비스 개발 및 기존 시스템 유지보수를 담당하여 사용자 경험을 개선하고 서비스 안정성을 확보합니다.",
            "사용자 리서치 및 제품 기획을 통해 고객 니즈를 파악하고, 데이터 기반 의사결정으로 제품 경쟁력을 향상시킵니다.",
            "브랜드 마케팅 전략 수립 및 실행을 통해 브랜드 인지도를 높이고, 타겟 고객층의 참여도를 증대시킵니다.",
            "모바일 앱 개발 및 플랫폼 최적화를 통해 사용자 편의성을 향상시키고, 앱스토어 순위 개선을 달성합니다.",
            "데이터 분석 및 인사이트 도출을 통해 비즈니스 성과를 측정하고, 마케팅 캠페인 효과를 최적화합니다."
        ],
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
    """현재 필드에 대한 컨텍스트 기반 추천사항 생성"""
    recommendations = []
    
    if current_field == "mainDuties":
        recommendations = [
            "개발 및 유지보수",
            "코드 리뷰 및 품질 관리",
            "기술 문서 작성",
            "팀 협업 및 커뮤니케이션"
        ]
    elif current_field == "requirements":
        recommendations = [
            "관련 경험 3년 이상",
            "학사 학위 이상",
            "팀워크 능력",
            "문제 해결 능력"
        ]
    
    return recommendations

def parse_response_items(response_text: str) -> List[Dict[str, Any]]:
    """LLM 응답을 항목별로 분할하여 선택 가능한 형태로 변환"""
    items = []
    
    # 줄바꿈으로 분할
    lines = response_text.strip().split('\n')
    current_item = ""
    item_counter = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 번호가 있는 항목인지 확인 (1., 2., 3. 등)
        if re.match(r'^\d+\.', line):
            # 이전 항목이 있으면 저장
            if current_item:
                items.append({
                    "id": f"item_{item_counter}",
                    "text": current_item.strip(),
                    "selected": False
                })
                item_counter += 1
            
            # 새 항목 시작
            current_item = line
        else:
            # 번호가 없는 줄은 현재 항목에 추가
            if current_item:
                current_item += " " + line
            else:
                # 첫 번째 항목인 경우
                current_item = line
    
    # 마지막 항목 저장
    if current_item:
        items.append({
            "id": f"item_{item_counter}",
            "text": current_item.strip(),
            "selected": False
        })
    
    # 항목이 없으면 전체 텍스트를 하나의 항목으로 처리
    if not items:
        items.append({
            "id": "item_1",
            "text": response_text.strip(),
            "selected": False
        })
    
    return items

@router.post("/chat")
async def chat_endpoint(request: ChatbotRequest):
    """
    키워드 기반 1차 분류 → LLM 호출 → 응답 처리 API
    """
    print("[DEBUG] /chat 요청:", request)
    
    try:
        user_input = request.user_input
        conversation_history = request.conversation_history
        mode = request.mode
        
        # 인코딩 문제 해결을 위한 디버깅
        print(f"[DEBUG] 원본 user_input: {user_input}")
        print(f"[DEBUG] user_input 길이: {len(user_input)}")
        print(f"[DEBUG] user_input 타입: {type(user_input)}")

        # 개선된 인코딩 처리
        try:
            if isinstance(user_input, bytes):
                # 바이트 문자열인 경우 UTF-8로 디코딩
                user_input = user_input.decode('utf-8', errors='replace')
            elif isinstance(user_input, str):
                # 문자열이지만 깨진 문자가 있는 경우 처리
                if '?' in user_input or '' in user_input:
                    # 깨진 문자가 있는 경우 latin1로 인코딩 후 UTF-8로 디코딩
                    try:
                        user_input = user_input.encode('latin1').decode('utf-8', errors='replace')
                    except:
                        # 실패하면 원본 유지
                        pass
        except Exception as e:
            print(f"[DEBUG] 인코딩 처리 실패: {e}")
            # 인코딩 처리 실패 시 원본 유지
        
        print(f"[DEBUG] 처리된 user_input: {user_input}")
        
        # 깨진 텍스트 감지 및 처리
        if "????" in user_input:
            print(f"[DEBUG] 깨진 텍스트 감지됨 - 길이 기반 분류 사용")
            # 깨진 텍스트의 경우 길이로 분류
            if len(user_input) > 20:
                classification = {'type': 'job_posting_info', 'category': '채용정보', 'confidence': 0.8}
            else:
                classification = {'type': 'question', 'category': 'general', 'confidence': 0.7}
        else:
            # 정상 텍스트의 경우 기존 분류 함수 사용
            classification = classify_input(user_input)
        
        if not user_input:
            raise HTTPException(status_code=400, detail="사용자 입력이 필요합니다.")
        
        # 자유 텍스트 모드 처리
        if mode == "free_text":
            print(f"[DEBUG] current_page: {request.current_page}")
            print(f"[DEBUG] request dict: {request.dict()}")
            # 페이지별 분석 함수 선택
            if request.current_page == "resume_analysis":
                extracted_data = extract_resume_info_from_text(user_input)
                page_type = "resume_analysis"
                field_names = {
                    'name': '이름',
                    'email': '이메일',
                    'phone': '전화번호',
                    'education': '학력',
                    'experience': '경력',
                    'skills': '기술스택',
                    'certificates': '자격증'
                }
            else:
                # 기본: 채용공고 분석
                extracted_data = extract_job_info_from_text(user_input)
                page_type = "job_posting"
                field_names = {
                    '부서': '부서',
                    '인원': '인원',
                    '지역': '지역',
                    '근무시간': '근무시간',
                    '근무요일': '근무요일',
                    '경력': '경력',
                    '연봉': '연봉',
                    '업무': '업무'
                }
            
            # JSON 데이터를 문자열로 변환하여 표시
            extracted_info_text = ""
            if extracted_data:
                for key, value in extracted_data.items():
                    field_name = field_names.get(key, key)
                    extracted_info_text += f"• {field_name}: {value}\n"
            
            response = {
                "type": "start_job_posting" if page_type == "job_posting" else "start_resume_analysis",
                "content": f"{'이력서 분석' if page_type == 'resume_analysis' else '채용공고 작성을'} 시작하겠습니다! 🎯\n\n입력하신 정보를 분석하여 폼에 자동으로 입력해드리겠습니다.\n\n추출된 정보:\n{extracted_info_text}",
                "extracted_data": extracted_data,  # JSON 데이터 추가
                "confidence": 0.9
            }
            print(f"[DEBUG] /chat 자유 텍스트 모드 응답 ({page_type}):", response)
            return response
        
        # AI 어시스턴트 모드 처리 추가 (랭그래프 모드가 아닌 경우에만 강력 키워드 적용)
        if mode == "ai_assistant":
            print(f"[DEBUG] AI 어시스턴트 모드 처리 시작 - 입력: {user_input}")
            # 작성 완료 요청인지 확인 (랭그래프 모드에서는 강력 키워드 적용 안함)
            completion_keywords = ['작성해줘', '만들어줘', '등록해줘', '완료', '끝']
            is_completion_request = any(keyword in user_input for keyword in completion_keywords)
            print(f"[DEBUG] AI 어시스턴트 모드 완료 요청 감지: {is_completion_request}")
            print(f"[DEBUG] AI 어시스턴트 모드 입력에서 키워드 확인: {[kw for kw in completion_keywords if kw in user_input]}")
            
            if is_completion_request:
                response = {
                    "type": "ai_assistant_completion",
                    "content": """✅ AI 어시스턴트 모드 채용공고 작성이 완료되었습니다!

🎯 AI가 도와드린 채용공고가 완성되었습니다.

📋 다음 단계:
1. 폼에서 작성된 내용을 확인해주세요
2. 필요한 경우 추가 정보를 입력해주세요  
3. "등록하기" 버튼을 클릭하여 채용공고를 등록하세요

💡 추가로 수정하거나 궁금한 점이 있으시면 언제든 말씀해주세요!

🚀 채용공고 등록이 완료되면 지원자들이 바로 확인할 수 있습니다.""",
                    "confidence": 0.95
                }
            else:
                # AI 어시스턴트 모드에서는 RAG를 활용한 전문적인 답변 제공
                ai_response = await call_ai_api(user_input, conversation_history)
                response = {
                    "type": "ai_assistant",
                    "content": ai_response,
                    "confidence": 0.95
                }
            print("[DEBUG] /chat AI 어시스턴트 모드 응답:", response)
            return response
        
        # 개별입력모드 처리 추가 (랭그래프 모드가 아닌 경우에만 강력 키워드 적용)
        if mode == "individual_input":
            print(f"[DEBUG] 개별입력모드 처리 시작 - 입력: {user_input}")
            # 개별입력모드에서는 각 필드를 하나씩 입력받는 방식
            classification = classify_input_with_context(user_input, None)
            print(f"[DEBUG] 개별입력모드 분류 결과: {classification}")
            
            # 작성 완료 요청인지 확인 (랭그래프 모드에서는 강력 키워드 적용 안함)
            completion_keywords = ['작성해줘', '만들어줘', '등록해줘', '완료', '끝']
            is_completion_request = any(keyword in user_input for keyword in completion_keywords)
            print(f"[DEBUG] 개별입력모드 완료 요청 감지: {is_completion_request}")
            print(f"[DEBUG] 개별입력모드 입력에서 키워드 확인: {[kw for kw in completion_keywords if kw in user_input]}")
            
            if is_completion_request:
                response = {
                    "type": "individual_completion",
                    "content": """✅ 개별입력모드 채용공고 작성이 완료되었습니다!

🎯 모든 필드가 입력되었습니다.

📋 다음 단계:
1. 폼에서 작성된 내용을 확인해주세요
2. 필요한 경우 추가 정보를 입력해주세요  
3. "등록하기" 버튼을 클릭하여 채용공고를 등록하세요

💡 추가로 수정하거나 궁금한 점이 있으시면 언제든 말씀해주세요!

🚀 채용공고 등록이 완료되면 지원자들이 바로 확인할 수 있습니다.""",
                    "confidence": 0.95
                }
            elif classification['type'] == 'field':
                field_value = classification.get('value', user_input.strip())
                field_category = classification.get('category', 'unknown')
                response = {
                    "type": "field",
                    "content": f"{field_category}: {field_value}로 입력하겠습니다. 다음 필드를 입력해주세요.",
                    "field": field_category,
                    "value": field_value,
                    "confidence": classification['confidence']
                }
            else:
                # 필드가 아닌 경우 질문으로 처리
                ai_response = await call_ai_api(user_input, conversation_history)
                response = {
                    "type": "question",
                    "content": ai_response,
                    "confidence": 0.8
                }
            
            print("[DEBUG] /chat 개별입력모드 응답:", response)
            return response
        
        # 자율모드 처리 비활성화 (주석 처리)
        # if mode == "autonomous":
        #     print(f"[DEBUG] 자율모드 처리 시작 - 입력: {user_input}")
        #     # 자율모드에서는 AI가 자동으로 모든 정보를 수집
        #     extracted_data = extract_job_info_from_text(user_input)
        #     print(f"[DEBUG] 자율모드 추출된 정보: {extracted_data}")

        #     # 기타 항목 추천 요청 감지 시 번호 선택 형태로 제안
        #     if ("기타" in user_input and "추천" in user_input) or ("additional" in user_input.lower() and "recommend" in user_input.lower()):
        #         print("[DEBUG] 자율모드 - 기타항목 추천 선택형 응답 생성")
        #         additional_options = [
        #             "식대/중식 제공",
        #             "최신 장비 제공(MacBook/모니터)",
        #             "교육비·도서 구입비 지원",
        #             "시차출퇴근/유연근무제",
        #             "주 2일 재택(하이브리드)",
        #             "건강검진/단체상해보험",
        #             "경조사비 및 경조휴가",
        #             "리프레시 휴가",
        #             "주간 기술공유/스터디",
        #             "회식 강요 없음"
        #         ]
        #         numbered = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(additional_options)])
        #         selection_msg = (
        #             f"다음 중 '기타 항목'에 포함할 내용을 번호로 선택해 주세요. (복수 선택 가능, 예: 1,3,5)\n\n{numbered}"
        #         )
        #         items = [{"id": f"item_{i+1}", "text": opt, "selected": False} for i, opt in enumerate(additional_options)]
        #         response = {
        #             "type": "ai_assistant",
        #             "content": selection_msg,
        #             "items": items,
        #             "show_item_selection": True,
        #             "confidence": 0.9
        #         }
        #         print("[DEBUG] /chat 자율모드 기타항목 선택 응답:", response)
        #         return response
            
        #     # JSON 데이터를 문자열로 변환
        #     extracted_info_text = ""
        #     if extracted_data:
        #         for key, value in extracted_data.items():
        #             field_name = {
        #                 '부서': '부서',
        #                 '인원': '인원',
        #                 '지역': '지역',
        #                 '근무시간': '근무시간',
        #                 '근무요일': '근무요일',
        #                 '경력': '경력',
        #                 '연봉': '연봉',
        #                 '업무': '업무'
        #             }.get(key, key)
        #             extracted_info_text += f"• {field_name}: {value}\n"
            
        #     if extracted_data and extracted_info_text:
        #         # 작성 완료 요청인지 확인
        #         completion_keywords = ['작성해줘', '만들어줘', '등록해줘', '완료', '끝']
        #         is_completion_request = any(keyword in user_input for keyword in completion_keywords)
        #         print(f"[DEBUG] 자율모드 완료 요청 감지: {is_completion_request}")
        #         print(f"[DEBUG] 자율모드 입력에서 키워드 확인: {[kw for kw in completion_keywords if kw in user_input]}")
        #         print(f"[DEBUG] 자율모드 입력 텍스트: '{user_input}'")
                
        #         if is_completion_request:
        #             print(f"[DEBUG] 자율모드 완료 응답 생성")
        #             response = {
        #                 "type": "autonomous_completion",
        #                 "content": f"""✅ 자율모드 채용공고 작성이 완료되었습니다!

        # 🎯 추출된 정보:
        # {extracted_info_text}

        # 📋 다음 단계:
        # 1. 폼에서 작성된 내용을 확인해주세요
        # 2. 필요한 경우 추가 정보를 입력해주세요  
        # 3. "등록하기" 버튼을 클릭하여 채용공고를 등록하세요

        # 💡 추가로 수정하거나 궁금한 점이 있으시면 언제든 말씀해주세요!

        # 🚀 채용공고 등록이 완료되면 지원자들이 바로 확인할 수 있습니다.""",
        #                 "confidence": 0.95
        #             }
        #         else:
        #             print(f"[DEBUG] 자율모드 일반 응답 생성")
        #             response = {
        #                 "type": "autonomous_collection",
        #                 "content": f"자율모드로 정보를 수집하겠습니다! 🚀\n\n추출된 정보:\n{extracted_info_text}\n\n추가 정보가 필요하면 말씀해주세요.",
        #                 "extracted_data": extracted_data,  # 추출된 데이터 포함
        #                 "confidence": 0.9
        #             }
        #     else:
        #         # 정보 추출이 안된 경우 AI 어시스턴트로 처리
        #         ai_response = await call_ai_api(user_input, conversation_history)
        #         response = {
        #             "type": "ai_assistant",
        #             "content": ai_response,
        #             "confidence": 0.85
        #         }
            
        #     print("[DEBUG] /chat 자율모드 응답:", response)
        #     return response
        
        # 랭그래프 모드 처리 추가 (강력 키워드 적용 안함)
        if mode == "langgraph":
            print(f"[DEBUG] 랭그래프 모드 처리 시작 - 입력: {user_input}")
            
            # 랭그래프 모드에서는 강력 키워드('제출', '등록' 등)를 일반 대화로 처리
            completion_keywords = ['작성해줘', '만들어줘', '등록해줘', '완료', '끝', '제출', '등록']
            is_completion_request = any(keyword in user_input for keyword in completion_keywords)
            
            if is_completion_request:
                # 강력 키워드가 있어도 일반 대화로 처리
                print(f"[DEBUG] 랭그래프 모드에서 강력 키워드 감지됨: {[kw for kw in completion_keywords if kw in user_input]}")
                print(f"[DEBUG] 랭그래프 모드에서는 강력 키워드를 일반 대화로 처리합니다.")
            
            try:
                # Agent 시스템을 사용하여 요청 처리
                session_id = request.session_id or str(uuid.uuid4())
                result = agent_system.process_request(
                    user_input=user_input,
                    conversation_history=conversation_history,
                    session_id=session_id
                )
                
                if result["success"]:
                    response = {
                        "type": "langgraph_response",
                        "content": result["response"],
                        "intent": result["intent"],
                        "confidence": 0.9
                    }
                else:
                    response = {
                        "type": "langgraph_error",
                        "content": "죄송합니다. 랭그래프 모드에서 오류가 발생했습니다.",
                        "confidence": 0.5
                    }
                
                print("[DEBUG] /chat 랭그래프 모드 응답:", response)
                return response
                
            except Exception as e:
                print(f"[DEBUG] 랭그래프 모드 처리 중 오류: {str(e)}")
                response = {
                    "type": "langgraph_error",
                    "content": f"랭그래프 모드 처리 중 오류가 발생했습니다: {str(e)}",
                    "confidence": 0.5
                }
                return response
        
        # 1) 키워드 기반 1차 분류 (이미 위에서 처리됨)
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
            # 3) AI API 호출로 답변 생성
            ai_response = await call_ai_api(user_input, conversation_history)
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
            
        elif classification['type'] == 'job_posting_info':
            # 채용공고 정보 처리
            extracted_data = extract_job_info_from_text(user_input)
            
            # JSON 데이터를 문자열로 변환하여 표시
            extracted_info_text = ""
            if extracted_data:
                for key, value in extracted_data.items():
                    field_name = {
                        '부서': '부서',
                        '인원': '인원',
                        '지역': '지역',
                        '근무시간': '근무시간',
                        '근무요일': '근무요일',
                        '경력': '경력',
                        '연봉': '연봉',
                        '업무': '업무'
                    }.get(key, key)
                    extracted_info_text += f"• {field_name}: {value}\n"
            
            response = {
                "type": "job_posting_info",
                "content": f"채용공고 작성을 시작하겠습니다! 🎯\n\n입력하신 정보를 분석하여 폼에 자동으로 입력해드리겠습니다.\n\n추출된 정보:\n{extracted_info_text}",
                "value": user_input.strip(),
                "confidence": classification['confidence']
            }
            
        elif classification['type'] == 'answer' and any(keyword in user_input for keyword in ['작성해줘', '만들어줘', '등록해줘', '완료', '끝']):
            # 작성 완료 요청 처리 - 다음 단계 안내
            print(f"[DEBUG] 완료 키워드 감지됨: {user_input}")
            response = {
                "type": "completion_guide",
                "content": """✅ 채용공고 작성이 완료되었습니다!

🎯 작성된 내용이 폼에 자동으로 입력되었습니다.

📋 다음 단계:
1. 폼에서 작성된 내용을 확인해주세요
2. 필요한 경우 추가 정보를 입력해주세요  
3. "등록하기" 버튼을 클릭하여 채용공고를 등록하세요

💡 추가로 수정하거나 궁금한 점이 있으시면 언제든 말씀해주세요!

🚀 채용공고 등록이 완료되면 지원자들이 바로 확인할 수 있습니다.""",
                "confidence": 0.95
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

@router.post("/test-mode-chat")
async def test_mode_chat(request: ChatbotRequest):
    """테스트중 모드 채팅 처리 - LangGraph 기반 Agent 시스템"""
    try:
        # Agent 시스템을 사용하여 요청 처리
        result = agent_system.process_request(
            user_input=request.user_input,
            conversation_history=request.conversation_history
        )
        
        if result["success"]:
            response = ChatbotResponse(
                message=result["response"],
                confidence=0.9
            )
        else:
            response = ChatbotResponse(
                message="죄송합니다. 테스트중 모드에서 오류가 발생했습니다.",
                confidence=0.5
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테스트중 모드 처리 중 오류: {str(e)}")

@router.post("/generate-title")
async def generate_title_recommendations(request: dict):
    """
    폼 데이터를 분석하여 채용공고 제목을 추천합니다.
    """
    try:
        # GeminiService를 사용한 제목 생성
        form_data = request.get('form_data', {})
        content = request.get('content', '')
        
        print(f"[DEBUG] 제목 추천 요청 - form_data: {form_data}")
        print(f"[DEBUG] 제목 추천 요청 - content: {content}")
        
        # 폼 데이터에서 주요 정보 추출
        company = form_data.get('company', '회사')
        department = form_data.get('department', '부서')
        position = form_data.get('position', '직무')
        location = form_data.get('location', form_data.get('locationCity', ''))
        experience = form_data.get('experience', '경력무관')
        headcount = form_data.get('headcount', '')
        
        # AI를 통한 제목 생성 (4가지 컨셉)
        import random
        import time
        
        # 랜덤 시드를 현재 시간으로 설정하여 매번 다른 결과 보장
        random.seed(int(time.time() * 1000) % 10000)
        
        # 창의적 표현 리스트
        creative_phrases = [
            "함께 성장할", "혁신을 이끌", "미래를 만들", "변화를 주도할", "성공을 함께할",
            "역량을 발휘할", "꿈을 실현할", "도전할", "새로운 기회를 잡을", "성과를 만들",
            "열정을 펼칠", "가능성을 실현할", "비전을 공유할", "목표를 달성할", "잠재력을 키울"
        ]
        
        professional_phrases = [
            "전문성을 갖춘", "실력있는", "경험이 풍부한", "역량있는", "숙련된",
            "전문적인", "뛰어난", "우수한", "탁월한", "최고의", "핵심", "선도적인",
            "글로벌", "혁신적인", "창의적인", "데이터 기반", "AI 전문", "디지털"
        ]
        
        # 랜덤 요소 추가
        selected_creative = random.sample(creative_phrases, 3)
        selected_professional = random.sample(professional_phrases, 3)
        variation_styles = random.sample(["채용", "모집", "구인", "영입", "선발"], 3)
        
        prompt = f"""
다음 채용공고 정보를 바탕으로 4가지 완전히 다른 컨셉의 창의적이고 독특한 채용공고 제목을 생성해주세요.
매번 새롭고 독창적인 제목을 만들어야 합니다.

채용 정보:
- 회사: {company}
- 부서/팀: {department}
- 직무/포지션: {position}
- 근무지: {location}
- 경력: {experience}
- 채용인원: {headcount}

추가 정보:
{content}

창의적 키워드 조합:
- 창의적 표현: {selected_creative}
- 전문적 표현: {selected_professional}
- 다양한 동사: {variation_styles}
- 트렌드 키워드: AI, 디지털, 스마트워크, 글로벌, 데이터기반

각 컨셉별 요구사항:
1. 첫번째 (신입친화형): 신입의 입장에서 친근하고 접근하기 쉬운 느낌
   - 성장, 배움, 시작, 동반자 등의 키워드 활용
   - 따뜻하고 격려하는 톤으로 작성
   
2. 두번째 (전문가형): 전문적이고 지적인 느낌으로 경력자 대상
   - 혁신, 리더십, 전문성, 성과 등의 키워드 활용
   - 도전적이고 임팩트 있는 톤으로 작성
   
3. 세번째 (일반형): 균형잡힌 일반적인 표현
   - 직무명과 채용을 명확히 표현
   - 간결하고 직관적인 톤으로 작성
   
4. 네번째 (일반형 변형): 세번째와 완전히 다른 표현 방식
   - 다른 동사나 명사 조합 사용
   - 약간 더 모던하거나 트렌디한 톤으로 작성

**중요**: 
- 매번 완전히 새로운 제목을 생성해야 합니다
- 똑같은 패턴이나 표현을 반복하지 마세요
- 창의적이고 독특한 조합을 만드세요
- 각 제목은 15-25자 내외로 작성해주세요

JSON 형식으로 응답해주세요:
{{
  "titles": [
    {{"concept": "신입친화형", "title": "제목1"}},
    {{"concept": "전문가형", "title": "제목2"}},
    {{"concept": "일반형", "title": "제목3"}},
    {{"concept": "일반형 변형", "title": "제목4"}}
  ]
}}
"""
        
        try:
            # GeminiService를 사용한 제목 생성
            from gemini_service import GeminiService
            gemini_service = GeminiService()
            
            # 창의성을 높인 응답 생성
            response = await gemini_service.generate_response(prompt, [])
            print(f"[DEBUG] Gemini 응답 (창의성 모드): {response}")
            
            # JSON 파싱 시도
            import json
            import re
            
            # JSON 형태의 응답 찾기
            json_match = re.search(r'\{.*"titles".*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_response = json.loads(json_str)
                titles = parsed_response.get('titles', [])
                
                # 새로운 형식 (컨셉 포함) 처리
                if titles and len(titles) >= 4 and isinstance(titles[0], dict):
                    return {"titles": titles[:4]}
                # 기존 형식 (문자열 배열) 처리
                elif titles and len(titles) >= 4:
                    # 기존 형식을 새 형식으로 변환
                    concepts = ["신입친화형", "전문가형", "일반형", "일반형 변형"]
                    formatted_titles = []
                    for i, title in enumerate(titles[:4]):
                        formatted_titles.append({
                            "concept": concepts[i] if i < len(concepts) else "일반형",
                            "title": title
                        })
                    return {"titles": formatted_titles}
            
            # JSON 파싱 실패 시 응답에서 제목 추출
            lines = response.strip().split('\n')
            titles = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('{') and not line.startswith('}') and '"' not in line:
                    # 번호나 불필요한 문자 제거
                    cleaned_line = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
                    if cleaned_line and len(cleaned_line) > 5:
                        titles.append(cleaned_line)
                        if len(titles) >= 4:
                            break
            
            if len(titles) >= 4:
                # 텍스트에서 추출한 제목들을 컨셉별로 분류
                concepts = ["신입친화형", "전문가형", "일반형", "일반형 변형"]
                formatted_titles = []
                for i, title in enumerate(titles[:4]):
                    formatted_titles.append({
                        "concept": concepts[i] if i < len(concepts) else "일반형",
                        "title": title
                    })
                return {"titles": formatted_titles}
                
        except Exception as ai_error:
            print(f"[DEBUG] AI 제목 생성 실패: {ai_error}")
        
        # AI 실패 시 기본 제목 생성 (4가지 컨셉)
        default_titles = []
        
        # 1. 신입친화형
        if position:
            default_titles.append({
                "concept": "신입친화형",
                "title": f"함께 성장할 {position} 신입을 찾습니다"
            })
        else:
            default_titles.append({
                "concept": "신입친화형", 
                "title": f"첫 커리어를 시작할 {department or '팀'} 동료 모집"
            })
        
        # 2. 전문가형
        if experience and experience != '경력무관':
            default_titles.append({
                "concept": "전문가형",
                "title": f"혁신을 리드할 {experience} {position or '전문가'} 채용"
            })
        else:
            default_titles.append({
                "concept": "전문가형",
                "title": f"전문성을 발휘할 {position or '시니어'} 인재 모집"
            })
        
        # 3. 일반형
        if company and department:
            title = f"{company} {department} {position or '직원'} 채용"
            if headcount:
                title = f"{title} ({headcount})"
            default_titles.append({
                "concept": "일반형",
                "title": title
            })
        else:
            default_titles.append({
                "concept": "일반형",
                "title": f"{department or '부서'} {position or '직무'} 모집"
            })
        
        # 4. 일반형 변형
        if location:
            default_titles.append({
                "concept": "일반형 변형",
                "title": f"{location} {department or '부서'} {position or '직무'} 구인"
            })
        else:
            default_titles.append({
                "concept": "일반형 변형", 
                "title": f"{position or '직무'} 담당자 채용공고"
            })
        
        return {"titles": default_titles}
        
    except Exception as e:
        print(f"[ERROR] 제목 추천 생성 중 오류: {e}")
        traceback.print_exc()
        
        # 오류 시에도 기본 제목들 반환 (4가지 컨셉)
        return {
            "titles": [
                {"concept": "신입친화형", "title": "함께 성장할 신입 동료를 찾습니다"},
                {"concept": "전문가형", "title": "전문성을 발휘할 인재를 모집합니다"},
                {"concept": "일반형", "title": "채용 공고"},
                {"concept": "일반형 변형", "title": "우수인재 모집"}
            ]
        }

# 기존의 복잡한 분류 함수 제거 - 새로운 범용 핸들러로 대체됨

# 기존의 복잡한 키워드 함수 제거 - 새로운 범용 핸들러로 대체됨

def get_field_config(field: str) -> dict:
    """필드별 설정 반환"""
    field_configs = {
        'department': {'extract_value': True},
        'headcount': {'extract_value': True, 'extract_number': True},
        'mainDuties': {'extract_value': True},
        'workHours': {'extract_value': True},
        'location': {'extract_value': True},
        'salary': {'extract_value': True, 'extract_number': True},
        'deadline': {'extract_value': True},
        'contactEmail': {'extract_value': True}
    }
    return field_configs.get(field, {})

def has_field_keywords(text: str, field: str) -> bool:
    """텍스트에 해당 필드의 키워드가 포함되어 있는지 확인"""
    keywords = get_field_keywords(field)
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

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
        # (특수 처리) 기타 항목 추천: 번호 선택 UI 제공
        if field_key == 'additionalInfo' or ('기타' in user_input and '추천' in user_input):
            additional_options = [
                "식대/중식 제공",
                "최신 장비 제공(MacBook/모니터)",
                "교육비·도서 구입비 지원",
                "시차출퇴근/유연근무제",
                "주 2일 재택(하이브리드)",
                "건강검진/단체상해보험",
                "경조사비 및 경조휴가",
                "리프레시 휴가",
                "주간 기술공유/스터디",
                "회식 강요 없음"
            ]
            numbered = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(additional_options)])
            selection_msg = (
                f"다음 중 '기타 항목'에 포함할 내용을 번호로 선택해 주세요. (복수 선택 가능, 예: 1,3,5)\n\n{numbered}"
            )
            items = [{"id": f"item_{i+1}", "text": opt, "selected": False} for i, opt in enumerate(additional_options)]
            return {
                "message": selection_msg,
                "value": None,
                "field": field_key,
                "suggestions": [],
                "confidence": classification['confidence'],
                "items": items,
                "show_item_selection": True
            }
        # 질문인 경우 Gemini API 호출
        try:
            ai_assistant_context = f"""
현재 채용 공고 작성 중입니다. 현재 필드: {field_label} ({field_key})

사용자 질문: {user_input}

이 질문에 대해 채용 공고 작성에 도움이 되는 실무적인 답변을 제공해주세요.
"""
            ai_response = await call_ai_api(ai_assistant_context)
            
            # 응답을 항목별로 분할
            items = parse_response_items(ai_response)
            
            response = {
                "message": ai_response,
                "value": None,  # 질문이므로 value는 None
                "field": field_key,
                "suggestions": [],
                "confidence": classification['confidence'],
                "items": items,
                "show_item_selection": True  # 항목 선택 UI 표시
            }
            print(f"[DEBUG] 질문 응답 (항목 선택 포함): {response}")
            return response
            
        except Exception as e:
            print(f"[ERROR] Gemini API 호출 실패: {e}")
            # 오프라인 응답으로 대체
            response = {
                "message": f"'{user_input}'에 대한 답변을 제공해드리겠습니다. 현재 필드 '{field_label}'에 대한 정보를 입력해주세요.",
                "value": None,
                "field": field_key,
                "suggestions": [],
                "confidence": 0.5
            }
            return response
    elif classification['type'] == 'chat':
        # 일상 대화 처리
        response = {
            "message": f"안녕하세요! 채용 공고 작성에 도와드리고 있습니다. 현재 {field_label}에 대한 정보를 입력해주세요.",
            "value": None,
            "field": field_key,
            "suggestions": [],
            "confidence": classification['confidence']
        }
        print(f"[DEBUG] 일상 대화 응답: {response}")
        return response
    else:
        # 답변인 경우 (개선된 처리)
        # (우선처리) 직전 턴에서 선택 목록을 제시했다면 번호/제외 파싱
        try:
            pending = (session.get("pending_selection") or {}).get(field_key)
        except Exception:
            pending = None
        if pending:
            import re
            numbers = re.findall(r"\d+", user_input)
            is_exclusion = any(kw in user_input for kw in ["제외", "빼고", "빼줘", "빼 ", "빼"]) or "제외하고" in user_input
            apply_rest = any(kw in user_input for kw in ["나머지", "전부", "전체", "다 ", "다해", "모두"]) or (not numbers)
            selected_texts: list[str] = []
            if apply_rest and numbers:
                exclude_idx = {int(n)-1 for n in numbers if 0 < int(n) <= len(pending)}
                for i, opt in enumerate(pending):
                    if i not in exclude_idx:
                        selected_texts.append(opt)
            elif apply_rest and not numbers:
                # "전부/전체/나머지" 등 전체 적용
                selected_texts = list(pending)
            else:
                include_idx = {int(n)-1 for n in numbers if 0 < int(n) <= len(pending)}
                if is_exclusion:
                    for i, opt in enumerate(pending):
                        if i not in include_idx:
                            selected_texts.append(opt)
                else:
                    for i in sorted(include_idx):
                        selected_texts.append(pending[i])

            # 선택 결과를 필드 값으로 변환 (멀티라인 결합)
            if selected_texts:
                joined = "\n".join([f"- {t}" for t in selected_texts]) if field_key != 'additionalInfo' else ", ".join(selected_texts)
                field_value = joined
                try:
                    # 사용 완료 후 초기화
                    if "pending_selection" in session and field_key in session["pending_selection"]:
                        del session["pending_selection"][field_key]
                except Exception:
                    pass
            else:
                # 선택이 실패하면 일반 처리로 폴백
                field_value = classification.get('value', user_input)

        # (특수 처리) 기타 항목 번호 선택 파싱
        elif field_key == 'additionalInfo':
            import re
            # 동일한 옵션 순서 유지 (질문 분기와 동일 목록)
            additional_options = [
                "식대/중식 제공",
                "최신 장비 제공(MacBook/모니터)",
                "교육비·도서 구입비 지원",
                "시차출퇴근/유연근무제",
                "주 2일 재택(하이브리드)",
                "건강검진/단체상해보험",
                "경조사비 및 경조휴가",
                "리프레시 휴가",
                "주간 기술공유/스터디",
                "회식 강요 없음"
            ]
            numbers = re.findall(r"\d+", user_input)
            text_lower = user_input.lower()
            is_exclusion = any(kw in user_input for kw in ["제외", "빼고", "빼줘", "빼 ", "빼"])
            selected = []
            if numbers:
                indices = set()
                for n in numbers:
                    idx = int(n) - 1
                    if 0 <= idx < len(additional_options):
                        indices.add(idx)
                if is_exclusion:
                    # 선택된 번호를 제외하고 나머지 모두 적용
                    for i, opt in enumerate(additional_options):
                        if i not in indices:
                            selected.append(opt)
                else:
                    for i in sorted(indices):
                        selected.append(additional_options[i])
            if selected:
                field_value = ", ".join(selected)
            else:
                # 번호가 없으면 원문을 그대로 처리하되 키워드 추출로 보정
                field_config = get_field_config(field_key)
                field_value = extract_field_value(user_input, field_key, field_config)
        else:
            field_value = classification.get('value', user_input)
        print(f"[DEBUG] 답변 처리 결과 - 필드: {field_key}, 값: {field_value}")
        
        response = {
            "message": f"'{field_label}'에 대해 '{field_value}'로 입력하겠습니다.",
            "value": field_value,
            "field": field_key,
            "suggestions": [],
            "confidence": classification['confidence']
        }
        print(f"[DEBUG] ===== AI 어시스턴트 응답 생성 완료 =====")
        print(f"[DEBUG] 최종 결과: {response}")
        print("[DEBUG] ===== AI 어시스턴트 응답 생성 완료 =====")
        return response

# 페이지별 UI 구조 정의
PAGE_CONFIGS = {
    'recruit_form': {
        'fields': [
            {'id': 'department', 'label': '부서', 'type': 'select', 'required': True, 'suggestions': ['개발팀', '마케팅팀', '영업팀', '디자인팀', '기획팀', '인사팀']},
            {'id': 'headcount', 'label': '채용 인원', 'type': 'number', 'required': True, 'suggestions': ['1명', '2명', '3명', '5명', '10명']},
            {'id': 'mainDuties', 'label': '주요 업무', 'type': 'text', 'required': True, 'suggestions': ['개발', '디자인', '마케팅', '영업', '기획', '고객지원']},
            {'id': 'workHours', 'label': '근무 시간', 'type': 'text', 'required': True, 'suggestions': ['09:00-18:00', '10:00-19:00', '유연근무제', '시차출근제']},
            {'id': 'locationCity', 'label': '근무 위치', 'type': 'text', 'required': True, 'suggestions': ['서울', '부산', '대구', '인천', '대전', '광주', '울산']},
            {'id': 'salary', 'label': '급여 조건', 'type': 'text', 'required': True, 'suggestions': ['면접 후 협의', '3000만원', '4000만원', '5000만원', '6000만원']},
            {'id': 'deadline', 'label': '마감일', 'type': 'date', 'required': True, 'suggestions': ['2024년 12월 31일', '2024년 11월 30일', '채용 시 마감', '상시채용']},
            {'id': 'contactEmail', 'label': '연락처 이메일', 'type': 'email', 'required': True, 'suggestions': ['hr@company.com', 'recruit@company.com', '인사팀 이메일']}
        ]
    }
}

async def universal_chatbot_handler(
    user_input: str, 
    page_id: str, 
    current_state: dict,
    conversation_history: list = None
) -> dict:
    """
    범용 챗봇 핸들러 - 모든 페이지에서 사용 가능
    """
    print(f"[DEBUG] ===== universal_chatbot_handler 시작 =====")
    print(f"[DEBUG] user_input: {user_input}")
    print(f"[DEBUG] page_id: {page_id}")
    print(f"[DEBUG] current_state: {current_state}")
    
    # 페이지 설정 가져오기
    page_config = PAGE_CONFIGS.get(page_id)
    if not page_config:
        return {
            'message': '지원하지 않는 페이지입니다.',
            'error': 'unsupported_page'
        }
    
    # 1. 사용자 입력 분석 (질문인지 답변인지)
    input_type = analyze_user_input(user_input)
    print(f"[DEBUG] 입력 타입: {input_type}")
    
    if input_type == 'question':
        # 사용자가 질문한 경우 - LLM으로 답변
        return await handle_user_question(user_input, page_id, current_state, conversation_history)
    
    elif input_type == 'answer':
        # 사용자가 답변한 경우 - 필드에 자동 입력
        field_id = detect_target_field(user_input, page_id, current_state)
        if field_id:
            return await auto_fill_field(user_input, field_id, page_id, current_state)
    
    # 2. 다음 질문 생성
    next_questions = await generate_page_questions(page_id, current_state)
    if next_questions:
        return {
            'message': f"{next_questions[0]['question']}",
            'target_field': next_questions[0]['field_id'],
            'remaining_fields': len(next_questions) - 1,
            'suggestions': next_questions[0].get('suggestions', [])
        }
    
    return {'message': '모든 정보가 입력되었습니다! 🎉'}

def analyze_user_input(user_input: str) -> str:
    """
    사용자 입력이 질문인지 답변인지 분석
    """
    text_lower = user_input.lower()
    
    # 질문 지표들
    question_indicators = [
        '어떻게', '왜', '무엇', '뭐', '언제', '어디', '어느', '어떤', '무슨',
        '있을까', '있나요', '인가요', '일까', '될까', '할까', '어때', '어떠',
        '?', '인가', '일까', '될까', '할까',
        '몇 명', '몇명', '얼마나', '어느 정도', '어떤 정도',
        '추천', '제안', '알려줘', '보여줘', '도와줘',
        '그럼', '그러면', '혹시', '예를 들어'
    ]
    
    # 질문으로 끝나는지 확인
    if any(indicator in text_lower for indicator in question_indicators) or user_input.strip().endswith('?'):
        return 'question'
    
    return 'answer'

async def handle_user_question(user_input: str, page_id: str, current_state: dict, conversation_history: list) -> dict:
    """
    사용자 질문에 대한 LLM 응답 처리
    """
    try:
        # 대화 히스토리 구성
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]
            context = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
                for msg in recent_messages
            ])
        
        # LLM 프롬프트 구성
        prompt = f"""
현재 채용 공고 작성 페이지에서 작업 중입니다.

최근 대화 내용:
{context}

사용자 질문: {user_input}

이 질문에 대해 채용 공고 작성에 도움이 되는 실무적인 답변을 제공해주세요.
답변은 간결하고 실용적으로 해주세요.
"""
        
        ai_response = await call_ai_api(prompt, conversation_history)
        
        return {
            'message': ai_response,
            'is_conversation': True,
            'type': 'question_response'
        }
        
    except Exception as e:
        print(f"[ERROR] LLM 호출 실패: {e}")
        return {
            'message': f"'{user_input}'에 대한 답변을 제공해드리겠습니다. 현재 페이지의 정보를 입력해주세요.",
            'is_conversation': True,
            'type': 'question_response'
        }
def detect_target_field(user_input: str, page_id: str, current_state: dict) -> str:
    """
    사용자 답변에서 대상 필드 감지
    """
    page_config = PAGE_CONFIGS.get(page_id)
    if not page_config:
        return None
    
    text_lower = user_input.lower()
    
    # 현재 상태에서 아직 입력되지 않은 필드들 찾기
    unfilled_fields = [
        field for field in page_config['fields'] 
        if field['required'] and not current_state.get(field['id'])
    ]
    
    if not unfilled_fields:
        return None
    
    # 첫 번째 미입력 필드 반환 (순서대로)
    return unfilled_fields[0]['id']

async def auto_fill_field(user_input: str, field_id: str, page_id: str, current_state: dict) -> dict:
    """
    사용자 답변을 해당 필드에 자동 입력
    """
    page_config = PAGE_CONFIGS.get(page_id)
    if not page_config:
        return {'error': 'invalid_page'}
    
    # 해당 필드 설정 찾기
    field_config = None
    for field in page_config['fields']:
        if field['id'] == field_id:
            field_config = field
            break
    
    if not field_config:
        return {'error': 'invalid_field'}
    
    # 답변 처리
    processed_value = process_answer_for_field(user_input, field_config)
    
    # 다음 질문 생성
    next_questions = await generate_page_questions(page_id, {**current_state, field_id: processed_value})
    
    if next_questions:
        return {
            'message': f"'{field_config['label']}'에 대해 '{processed_value}'로 입력하겠습니다. {next_questions[0]['question']}",
            'auto_filled': True,
            'field_id': field_id,
            'value': processed_value,
            'target_field': next_questions[0]['field_id'],
            'remaining_fields': len(next_questions) - 1,
            'suggestions': next_questions[0].get('suggestions', [])
        }
    else:
        return {
            'message': f"'{field_config['label']}'에 대해 '{processed_value}'로 입력하겠습니다. 모든 정보가 입력되었습니다! 🎉",
            'auto_filled': True,
            'field_id': field_id,
            'value': processed_value,
            'completed': True
        }

def process_answer_for_field(user_input: str, field_config: dict) -> str:
    """
    사용자 답변을 필드에 맞게 처리
    """
    # 기본적으로 사용자 입력을 그대로 사용
    processed_value = user_input.strip()
    
    # 필드 타입에 따른 추가 처리
    if field_config['type'] == 'number':
        # 숫자만 추출
        import re
        numbers = re.findall(r'\d+', processed_value)
        if numbers:
            processed_value = numbers[0]
    
    elif field_config['type'] == 'email':
        # 이메일 형식 검증
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, processed_value)
        if emails:
            processed_value = emails[0]
    
    return processed_value

async def generate_page_questions(page_id: str, current_state: dict) -> list:
    """
    페이지별 동적 질문 생성
    """
    page_config = PAGE_CONFIGS.get(page_id)
    if not page_config:
        return []
    
    questions = []
    for field in page_config['fields']:
        if field['required'] and not current_state.get(field['id']):
            questions.append({
                'field_id': field['id'],
                'question': f"{field['label']}을/를 알려주세요.",
                'type': field['type'],
                'suggestions': field.get('suggestions', [])
            })
    
    return questions

# 기존 함수들 제거하고 새로운 범용 핸들러로 교체
async def simulate_llm_response(user_input: str, current_field: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """
    기존 함수를 새로운 범용 핸들러로 교체
    """
    page_id = session.get('page_id', 'recruit_form')
    current_state = session.get('filled_fields', {})
    conversation_history = session.get('conversation_history', [])
    
    return await universal_chatbot_handler(user_input, page_id, current_state, conversation_history)

# 랭그래프 Agent API 엔드포인트
@router.post("/langgraph-agent")
async def langgraph_agent_endpoint(request: dict):
    """랭그래프 Agent 시스템 엔드포인트"""
    try:
        user_input = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        session_id = request.get("session_id", str(uuid.uuid4()))
        
        # Agent 시스템 호출
        result = agent_system.process_request(
            user_input=user_input,
            conversation_history=conversation_history,
            session_id=session_id
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "intent": result["intent"],
            "session_id": session_id,
            "extracted_fields": result.get("extracted_fields", {}),
            "confidence": 0.9
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

