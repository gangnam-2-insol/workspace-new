from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
import time
from collections import defaultdict
from datetime import datetime
import uuid

# 기존 서비스들 import
try:
    from llm_service import LLMService
except ImportError:
    try:
        from .llm_service import LLMService
    except ImportError:
        pass

try:
    from chatbot.core.agent_system import AgentSystem
except ImportError:
    try:
        from ..chatbot.core.agent_system import AgentSystem
    except ImportError:
        pass

try:
    from agent_system.executor.tool_executor import ToolExecutor
except ImportError:
    try:
        from ..agent_system.executor.tool_executor import ToolExecutor
    except ImportError:
        pass

try:
    from agent_system.utils.monitoring import monitoring_system
except ImportError:
    try:
        from ..agent_system.utils.monitoring import monitoring_system
    except ImportError:
        pass

router = APIRouter(prefix="/pick-chatbot", tags=["pick-chatbot"])

# 로깅 설정 (안전한 로깅)
logger = logging.getLogger(__name__)

# 로거 핸들러가 없으면 추가
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class SessionManager:
    def __init__(self, expiry_seconds=1800, max_history=10):
        self.sessions = defaultdict(dict)
        self.expiry_seconds = expiry_seconds
        self.max_history = max_history

    def _current_time(self):
        return int(time.time())

    def create_session(self, session_id):
        self.sessions[session_id] = {
            "history": [],
            "last_activity": self._current_time()
        }
        try:
            logger.info(f"새 세션 생성: {session_id}")
        except (ValueError, OSError):
            pass  # detached buffer 오류 무시

    def add_message(self, session_id, role, content):
        if session_id not in self.sessions:
            self.create_session(session_id)

        session = self.sessions[session_id]
        session["history"].append({"role": role, "content": content})

        # 오래된 기록은 잘라냄
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history:]

        session["last_activity"] = self._current_time()
        try:
            logger.info(f"세션 {session_id}에 메시지 추가: {role}")
        except (ValueError, OSError):
            pass  # detached buffer 오류 무시

    def get_history(self, session_id):
        if session_id in self.sessions:
            return self.sessions[session_id]["history"]
        return []

    def cleanup_sessions(self):
        now = self._current_time()
        expired = [
            sid for sid, data in self.sessions.items()
            if now - data["last_activity"] > self.expiry_seconds
        ]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            try:
                logger.info(f"만료된 세션 {len(expired)}개 정리: {expired}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시

    def get_session_info(self, session_id):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "message_count": len(session["history"]),
                "last_activity": session["last_activity"],
                "created_at": session.get("created_at", session["last_activity"])
            }
        return None

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            try:
                logger.info(f"세션 삭제: {session_id}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시
            return True
        return False

    def list_all_sessions(self):
        return [
            self.get_session_info(sid) for sid in self.sessions.keys()
        ]

# 세션 매니저 인스턴스 생성
session_manager = SessionManager(expiry_seconds=1800, max_history=10)

# 툴 실행기 인스턴스 생성
tool_executor = ToolExecutor()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    suggestions: Optional[List[str]] = None
    quick_actions: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    tool_results: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None
    page_action: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime

def get_openai_service():
    """OpenAI 서비스 인스턴스 반환"""
    return LLMService()

def get_agent_system():
    """에이전트 시스템 인스턴스 반환"""
    return AgentSystem()

def create_session_id() -> str:
    """새로운 세션 ID 생성"""
    return str(uuid.uuid4())

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """세션 ID를 가져오거나 새로 생성"""
    if not session_id:
        session_id = create_session_id()
    
    # 세션이 없으면 생성
    if session_id not in session_manager.sessions:
        session_manager.create_session(session_id)
    
    return session_id

def update_session(session_id: str, message: str, is_user: bool = True):
    """세션에 메시지 추가"""
    role = "user" if is_user else "assistant"
    session_manager.add_message(session_id, role, message)

def get_conversation_context(session_id: str) -> Dict[str, Any]:
    """대화 컨텍스트 생성 (개선된 버전)"""
    history = session_manager.get_history(session_id)
    if not history:
        return {
            "context_text": "",
            "context_summary": [],
            "recent_messages": [],
            "session_info": session_manager.get_session_info(session_id)
        }
    
    # 컨텍스트 텍스트 생성
    context_text = ""
    for msg in history:
        role = "사용자" if msg["role"] == "user" else "에이전트"
        context_text += f"{role}: {msg['content']}\n"
    
    # 최근 메시지 (최대 3개)
    recent_messages = history[-3:] if len(history) > 3 else history
    
    # 컨텍스트 요약 생성
    context_summary = []
    for msg in recent_messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            keywords = extract_context_keywords(content)
            if keywords:
                context_summary.append(f"관심사: {', '.join(keywords)}")
    
    return {
        "context_text": context_text,
        "context_summary": context_summary,
        "recent_messages": recent_messages,
        "session_info": session_manager.get_session_info(session_id)
    }

def extract_context_keywords(message: str) -> List[str]:
    """메시지에서 컨텍스트 키워드 추출"""
    keywords = []
    message_lower = message.lower()
    
    # GitHub 관련 키워드
    if any(word in message_lower for word in ["github", "깃허브", "레포", "repo", "커밋", "commit"]):
        keywords.append("GitHub")
    
    # 데이터베이스 관련 키워드
    if any(word in message_lower for word in ["데이터베이스", "db", "mongodb", "컬렉션", "collection"]):
        keywords.append("데이터베이스")
    
    # 검색 관련 키워드
    if any(word in message_lower for word in ["검색", "search", "찾기", "find"]):
        keywords.append("검색")
    
    # 채용 관련 키워드
    if any(word in message_lower for word in ["채용", "지원자", "면접", "공고", "포트폴리오", "자기소개서"]):
        keywords.append("채용관리")
    
    return keywords

async def generate_search_based_response(
    user_message: str, 
    openai_service, 
    tool_executor
) -> Optional[str]:
    """검색 결과를 바탕으로 LLM이 자연스러운 응답 생성"""
    
    # 검색 키워드 추출
    search_keywords = extract_search_keywords(user_message)
    if not search_keywords:
        return None
    
    try:
        # 웹 검색 실행
        search_result = await tool_executor.execute_async(
            "search",
            "web_search",
            query=search_keywords,
            num_results=5
        )
        
        if search_result.get("status") == "success":
            search_data = search_result.get("data", {})
            results = search_data.get("results", [])
            
            if results:
                # 검색 결과를 요약하여 LLM에게 제공
                search_summary = "\n".join([
                    f"- {result['title']}: {result['snippet']}"
                    for result in results[:3]  # 상위 3개 결과만 사용
                ])
                
                # LLM에게 검색 결과를 바탕으로 답변 생성 요청
                response_prompt = f"""
사용자가 "{user_message}"라고 질문했습니다.

웹에서 검색한 관련 정보:
{search_summary}

위의 검색 결과를 바탕으로 사용자의 질문에 대해 정확하고 도움이 되는 답변을 작성해주세요.
답변은 다음과 같은 형식으로 구성해주세요:

1. 핵심 정보 요약
2. 상세 설명 
3. 추가 도움이 될 만한 제안

답변은 친근하고 전문적인 톤으로 작성해주세요.
"""
                
                llm_response = await openai_service.chat_completion([
                    {"role": "system", "content": "당신은 웹 검색 결과를 바탕으로 정확하고 도움이 되는 답변을 제공하는 AI입니다."},
                    {"role": "user", "content": response_prompt}
                ])
                
                return llm_response
                
    except Exception as e:
        print(f"🔍 [DEBUG] 검색 기반 응답 생성 오류: {str(e)}")
        return None
    
    return None

def extract_search_keywords(message: str) -> str:
    """메시지에서 검색 키워드 추출"""
    import re
    
    # 검색 관련 키워드 패턴
    search_patterns = [
        r'검색.*?(\w+)',
        r'찾.*?(\w+)',
        r'알.*?(\w+)',
        r'(\w+).*?정보',
        r'(\w+).*?동향',
        r'(\w+).*?트렌드',
        r'최신.*?(\w+)',
    ]
    
    for pattern in search_patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    
    # 패턴이 매치되지 않으면 전체 메시지에서 핵심 단어 추출
    keywords = []
    common_words = ['검색', '찾기', '알려', '정보', '동향', '트렌드', '최신', '해서', '에서', '을', '를', '의', '가', '이', '은', '는']
    
    words = message.split()
    for word in words:
        if len(word) > 1 and word not in common_words:
            keywords.append(word)
    
    return ' '.join(keywords[:3])  # 최대 3개 키워드

async def detect_tool_usage_with_ai(
    user_message: str, 
    openai_service, 
    context_keywords: List[str] = None,
    recent_messages: List[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """AI를 사용하여 사용자 메시지에서 툴 사용 의도 감지 (컨텍스트 활용 버전)"""
    
    # 컨텍스트 정보 구성
    context_info = ""
    if context_keywords:
        context_info = f"\n이전 대화 컨텍스트: {', '.join(context_keywords)}"
    
    if recent_messages:
        recent_context = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}"
            for msg in recent_messages[-2:]  # 최근 2개 메시지만
        ])
        context_info += f"\n최근 대화:\n{recent_context}"
    
    # 개선된 AI 툴 선택 프롬프트 (컨텍스트 포함)
    tool_detection_prompt = f"""
당신은 사용자 메시지를 정확히 분석하여 적절한 툴과 액션을 선택하는 AI입니다.

사용 가능한 툴과 액션:
1. github:
   - get_user_info: GitHub 사용자 프로필 정보 조회
   - get_repos: 사용자의 레포지토리 목록 조회
   - get_commits: 레포지토리의 커밋 내역 조회
   - search_repos: GitHub에서 레포지토리 검색

2. mongodb:
   - find_documents: 데이터베이스 컬렉션에서 문서 조회
   - count_documents: 데이터베이스 컬렉션의 문서 개수 확인

3. search:
   - web_search: 일반 웹 검색
   - news_search: 뉴스 검색
   - image_search: 이미지 검색

중요한 구분 기준:
- "검색" 키워드가 있으면 search 툴 사용
- "데이터베이스", "DB", "MongoDB" 키워드가 있으면 mongodb 툴 사용
- "GitHub", "깃허브" 키워드가 있으면 github 툴 사용
- 툴이 필요하지 않으면 null 반환

{context_info}

현재 사용자 메시지: "{user_message}"

컨텍스트를 고려하여 적절한 툴을 선택해주세요. 이전 대화에서 언급된 내용이 현재 요청과 관련이 있다면 그것을 참고하세요.

JSON 형식으로만 응답해주세요:
- 툴이 필요하지 않으면: null
- 툴이 필요하면: {{"tool": "툴명", "action": "액션명", "params": {{"파라미터명": "값"}}}}

예시:
- "웹에서 AI 채용 정보 검색" → {{"tool": "search", "action": "web_search", "params": {{"query": "AI 채용 정보"}}}}
- "뉴스에서 IT 업계 동향 검색" → {{"tool": "search", "action": "news_search", "params": {{"query": "IT 업계 동향"}}}}
- "이미지에서 개발자 포트폴리오 검색" → {{"tool": "search", "action": "image_search", "params": {{"query": "개발자 포트폴리오"}}}}
- "데이터베이스에서 사용자 정보 조회" → {{"tool": "mongodb", "action": "find_documents", "params": {{"collection": "users"}}}}
- "GitHub 사용자 kyungho222 정보" → {{"tool": "github", "action": "get_user_info", "params": {{"username": "kyungho222"}}}}

JSON 응답만 해주세요:
"""

    try:
        # AI에게 툴 선택 요청
        response = await openai_service.chat_completion([
            {"role": "system", "content": "당신은 사용자 메시지를 분석하여 적절한 툴을 선택하는 AI입니다. JSON 형식으로만 응답해주세요."},
            {"role": "user", "content": tool_detection_prompt}
        ])
        
        print(f"🔍 [DEBUG] AI 툴 감지 응답: {response}")
        
        # JSON 파싱 시도
        import json
        import re
        
        # JSON 부분만 추출
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            tool_usage = json.loads(json_match.group())
            
            # 사용자명 추출이 필요한 경우
            if tool_usage and tool_usage.get("tool") == "github":
                if "username" not in tool_usage.get("params", {}) or not tool_usage["params"]["username"]:
                    username = extract_username(user_message)
                    tool_usage["params"]["username"] = username
            
            return tool_usage
        else:
            print(f"🔍 [DEBUG] AI 응답에서 JSON을 찾을 수 없음: {response}")
            return None
            
    except Exception as e:
        print(f"🔍 [DEBUG] AI 툴 감지 오류: {str(e)}")
        # AI 실패 시 기존 로직으로 폴백
        return detect_tool_usage_fallback(user_message)

def detect_tool_usage_fallback(user_message: str) -> Optional[Dict[str, Any]]:
    """기존 키워드 기반 툴 감지 (AI 실패 시 폴백)"""
    message_lower = user_message.lower()
    
    # GitHub 관련 의도 감지
    if any(keyword in message_lower for keyword in ["github", "깃허브", "레포", "repo", "커밋", "commit", "프로젝트", "project"]):
        if "사용자" in message_lower or "user" in message_lower or "아이디" in message_lower or "id" in message_lower:
            # GitHub 사용자 정보 조회
            return {
                "tool": "github",
                "action": "get_user_info",
                "params": {"username": extract_username(user_message)}
            }
        elif "레포" in message_lower or "repo" in message_lower:
            # GitHub 레포지토리 조회
            return {
                "tool": "github", 
                "action": "get_repos",
                "params": {"username": extract_username(user_message)}
            }
        else:
            # GitHub 키워드가 있지만 구체적인 액션이 명시되지 않은 경우, 기본적으로 사용자 정보 조회
            return {
                "tool": "github",
                "action": "get_user_info",
                "params": {"username": extract_username(user_message)}
            }
    
    # MongoDB 관련 의도 감지
    elif any(keyword in message_lower for keyword in ["데이터베이스", "db", "mongodb", "컬렉션", "collection"]):
        if "조회" in message_lower or "find" in message_lower:
            return {
                "tool": "mongodb",
                "action": "find_documents", 
                "params": {"collection": extract_collection_name(user_message)}
            }
        elif "개수" in message_lower or "count" in message_lower:
            return {
                "tool": "mongodb",
                "action": "count_documents",
                "params": {"collection": extract_collection_name(user_message)}
            }
    
    # 검색 관련 의도 감지
    elif any(keyword in message_lower for keyword in ["검색", "search", "찾기", "find"]):
        if "뉴스" in message_lower or "news" in message_lower:
            return {
                "tool": "search",
                "action": "news_search",
                "params": {"query": extract_search_query(user_message)}
            }
        elif "이미지" in message_lower or "image" in message_lower:
            return {
                "tool": "search", 
                "action": "image_search",
                "params": {"query": extract_search_query(user_message)}
            }
        else:
            return {
                "tool": "search",
                "action": "web_search", 
                "params": {"query": extract_search_query(user_message)}
            }
    
    return None

def extract_username(message: str) -> str:
    """메시지에서 사용자명 추출"""
    # 간단한 추출 로직 (실제로는 더 정교한 NLP 필요)
    import re
    patterns = [
        r'사용자\s*([a-zA-Z0-9_-]+)',
        r'user\s*([a-zA-Z0-9_-]+)', 
        r'([a-zA-Z0-9_-]+)\s*의\s*github',
        r'github\s*사용자\s*([a-zA-Z0-9_-]+)',
        r'아이디\s*([a-zA-Z0-9_-]+)',
        r'id\s*([a-zA-Z0-9_-]+)',
        r'([a-zA-Z0-9_-]+)\s*의\s*프로젝트',
        r'([a-zA-Z0-9_-]+)\s*프로젝트'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 기본값 (실제로는 사용자에게 확인 필요)
    return "kyungho222"

def extract_collection_name(message: str) -> str:
    """메시지에서 컬렉션명 추출"""
    import re
    patterns = [
        r'컬렉션\s*([a-zA-Z0-9_]+)',
        r'collection\s*([a-zA-Z0-9_]+)',
        r'([a-zA-Z0-9_]+)\s*컬렉션'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "users"  # 기본값

def extract_search_query(message: str) -> str:
    """메시지에서 검색 쿼리 추출"""
    # "검색" 키워드 이후의 텍스트 추출
    import re
    patterns = [
        r'검색\s*(.+)',
        r'search\s*(.+)',
        r'찾기\s*(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # 검색 키워드가 없으면 전체 메시지를 쿼리로 사용
    return message

def create_error_aware_response(tool_results: Dict[str, Any], user_message: str) -> str:
    """
    에러 정보를 포함한 사용자 친화적 응답 생성
    
    Args:
        tool_results: 툴 실행 결과
        user_message: 사용자 메시지
        
    Returns:
        사용자 친화적 응답 메시지
    """
    if not tool_results:
        return "죄송합니다. 요청을 처리하는 중 문제가 발생했습니다."
    
    result = tool_results.get("result", {})
    status = result.get("status")
    
    if status == "success":
        # 성공한 경우
        data = result.get("data", {})
        
        # 대체 툴을 사용한 경우
        if result.get("fallback_used"):
            original_error = result.get("original_error", {})
            return f"원래 요청한 방법으로는 정보를 가져올 수 없어서 다른 방법으로 찾아보았습니다. {format_tool_data(data)}"
        
        # 정상적으로 성공한 경우
        return f"요청하신 정보를 찾았습니다! {format_tool_data(data)}"
    
    elif status == "error":
        # 에러가 발생한 경우
        error_message = result.get("message", "알 수 없는 오류가 발생했습니다.")
        fallback_suggestion = result.get("fallback_suggestion")
        
        response = f"죄송합니다. {error_message}"
        
        if fallback_suggestion:
            suggestion = fallback_suggestion.get("suggestion", "")
            response += f" {suggestion}"
        
        return response
    
    return "요청을 처리하는 중 문제가 발생했습니다."

def format_tool_data(data: Dict[str, Any]) -> str:
    """툴 데이터를 사용자 친화적으로 포맷팅"""
    if not data:
        return "죄송합니다. 요청하신 정보를 찾을 수 없습니다."
    
    # GitHub 사용자 정보
    if "username" in data and "public_repos" in data:
        username = data.get("username", "알 수 없음")
        public_repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        following = data.get("following", 0)
        bio = data.get("bio", "")
        
        result = f"🎯 **{username}님의 GitHub 프로필**\n\n"
        result += f"📊 **활동 현황**\n"
        result += f"• 공개 레포지토리: {public_repos}개\n"
        result += f"• 팔로워: {followers}명\n"
        result += f"• 팔로잉: {following}명\n"
        
        if bio:
            result += f"\n💬 **자기소개**\n{bio}"
        
        return result
    
    # GitHub 레포지토리 목록
    if "repos" in data:
        repos = data["repos"]
        if repos:
            result = f"📁 **{len(repos)}개의 레포지토리 발견!**\n\n"
            
            # 주요 레포지토리 정보 추가
            top_repos = repos[:5]  # 상위 5개
            result += f"🌟 **주요 프로젝트**\n\n"
            for i, repo in enumerate(top_repos, 1):
                name = repo.get("name", "")
                language = repo.get("language", "")
                description = repo.get("description", "")
                stars = repo.get("stargazers_count", 0)
                
                result += f"{i}. **{name}**"
                # 언어 정보 제거
                # if language:
                #     result += f" ({language})"
                if stars > 0:
                    result += f" ⭐ {stars}"
                result += "\n"
                
                if description:
                    result += f"   └ {description[:80]}{'...' if len(description) > 80 else ''}\n"
                
                # 각 프로젝트 사이에 줄바꿈 추가
                result += "\n"
            
            # 기술 스택 요약 제거 (중복 방지)
            # languages = {}
            # for repo in repos:
            #     lang = repo.get("language")
            #     if lang:
            #         languages[lang] = languages.get(lang, 0) + 1
            
            # if languages:
            #     top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            #     result += f"\n💻 **기술 스택 요약**\n"
            #     lang_summary = []
            #     for lang, count in top_languages:
            #         lang_summary.append(f"{lang}({count}개)" if count > 1 else f"{lang}({count}개)")
            #     result += f"• {', '.join(lang_summary)}"
            
            return result
        else:
            return "😔 아직 레포지토리가 없네요. 첫 프로젝트를 시작해보세요!"
    
    # GitHub 커밋 정보
    if "commits" in data:
        commits = data["commits"]
        if commits:
            result = f"📝 **최근 {len(commits)}개의 커밋 활동**\n\n"
            
            # 최근 커밋 정보
            latest_commit = commits[0]
            commit_message = latest_commit.get("commit", {}).get("message", "제목 없음")
            author = latest_commit.get("commit", {}).get("author", {}).get("name", "알 수 없음")
            date = latest_commit.get("commit", {}).get("author", {}).get("date", "")
            
            result += f"🔥 **최신 커밋**\n"
            result += f"• 메시지: {commit_message}\n"
            result += f"• 작성자: {author}\n"
            
            if date:
                from datetime import datetime
                try:
                    commit_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    result += f"• 날짜: {commit_date.strftime('%Y년 %m월 %d일')}\n"
                except:
                    pass
            
            return result
        else:
            return "📅 아직 커밋 내역이 없습니다. 첫 커밋을 작성해보세요!"
    
    # MongoDB 문서
    if "documents" in data:
        count = len(data["documents"])
        if count > 0:
            return f"📋 데이터베이스에서 {count}개의 문서를 찾았습니다."
        else:
            return "📋 데이터베이스에 해당하는 문서가 없습니다."
    
    # 검색 결과
    if "results" in data:
        results = data["results"]
        if results:
            result = f"🔍 **검색 결과 {len(results)}개 발견!**\n\n"
            
            # 첫 번째 결과 정보 추가
            first_result = results[0]
            title = first_result.get("title", "제목 없음")
            snippet = first_result.get("snippet", "")[:120]  # 120자로 제한
            url = first_result.get("link", "")
            
            result += f"📌 **주요 결과**\n"
            result += f"• 제목: {title}\n"
            if snippet:
                result += f"• 요약: {snippet}...\n"
            if url:
                result += f"• 링크: {url}\n"
            
            return result
        else:
            return "🔍 검색 결과를 찾을 수 없습니다. 다른 키워드로 검색해보세요."
    
    # 기타 데이터
    return "✅ 요청하신 작업이 성공적으로 완료되었습니다!"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_help_bot(
    chat_message: ChatMessage,
    openai_service: LLMService = Depends(get_openai_service),
    agent_system: AgentSystem = Depends(get_agent_system)
):
    """
    에이전트과 대화
    """
    print(f"🔍 [DEBUG] 에이전트 호출됨 - 세션: {chat_message.session_id}, 메시지: {chat_message.message}")
    
    try:
        # 세션 정리 (만료된 세션 삭제)
        session_manager.cleanup_sessions()
        print(f"🔍 [DEBUG] 세션 정리 완료")
        
        # 세션 관리
        session_id = get_or_create_session(chat_message.session_id)
        print(f"🔍 [DEBUG] 세션 ID: {session_id}")
        
        # 사용자 메시지 저장
        update_session(session_id, chat_message.message, is_user=True)
        print(f"🔍 [DEBUG] 사용자 메시지 저장 완료")
        
        # 대화 컨텍스트 가져오기 (개선된 버전)
        conversation_context = get_conversation_context(session_id)
        print(f"🔍 [DEBUG] 대화 컨텍스트 정보: {conversation_context.get('context_summary', [])}")
        
        # 컨텍스트 기반 툴 감지 개선
        context_keywords = conversation_context.get('context_summary', [])
        recent_messages = conversation_context.get('recent_messages', [])
        
        # 검색 의도 감지 및 LLM 기반 검색 응답 시도
        search_response = None
        search_keywords = extract_search_keywords(chat_message.message)
        
        # 검색 관련 키워드가 있는 경우 LLM 기반 검색 응답 생성
        if search_keywords and any(keyword in chat_message.message.lower() for keyword in ["검색", "찾", "알려", "정보", "동향", "트렌드"]):
            print(f"🔍 [DEBUG] 검색 의도 감지됨, 키워드: {search_keywords}")
            search_response = await generate_search_based_response(
                chat_message.message, 
                openai_service, 
                tool_executor
            )
            print(f"🔍 [DEBUG] 검색 기반 응답 생성 결과: {'성공' if search_response else '실패'}")
        
        # 검색 응답이 생성되지 않은 경우에만 툴 감지 진행
        tool_usage = None
        tool_results = None
        error_info = None
        
        if not search_response:
            # AI 기반 툴 사용 의도 감지 (컨텍스트 활용)
            tool_usage = await detect_tool_usage_with_ai(
                chat_message.message, 
                openai_service, 
                context_keywords=context_keywords,
                recent_messages=recent_messages
            )
            print(f"🔍 [DEBUG] AI 기반 툴 사용 감지 결과: {tool_usage}")
        
        if tool_usage:
            print(f"🔍 [DEBUG] 툴 사용 감지됨: {tool_usage}")
            try:
                logger.info(f"툴 사용 감지: {tool_usage}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시
            try:
                print(f"🔍 [DEBUG] 툴 실행 시작 - 툴: {tool_usage['tool']}, 액션: {tool_usage['action']}, 파라미터: {tool_usage['params']}")
                
                # 비동기 툴 실행 (성능 최적화)
                result = await tool_executor.execute_async(
                    tool_usage["tool"],
                    tool_usage["action"],
                    session_id=session_id,  # 세션 ID 추가
                    **tool_usage["params"]
                )
                
                print(f"🔍 [DEBUG] 툴 실행 결과: {result}")
                
                tool_results = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "result": result
                }
                
                # 에러 정보 추출
                if result.get("status") == "error":
                    print(f"🔍 [DEBUG] 툴 실행 에러: {result.get('message')}")
                    error_info = {
                        "tool": tool_usage["tool"],
                        "action": tool_usage["action"],
                        "error_message": result.get("message"),
                        "retryable": result.get("retryable", False),
                        "fallback_suggestion": result.get("fallback_suggestion")
                    }
                else:
                    print(f"🔍 [DEBUG] 툴 실행 성공: {result.get('status')}")
                
                try:
                    logger.info(f"툴 실행 완료: {result['status']}")
                except (ValueError, OSError):
                    pass  # detached buffer 오류 무시
            except Exception as e:
                print(f"🔍 [DEBUG] 툴 실행 예외 발생: {str(e)}")
                logger.error(f"툴 실행 실패: {str(e)}")
                tool_results = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "error": str(e)
                }
                error_info = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "error_message": str(e),
                    "retryable": True
                }
        
        # 시스템 프롬프트 정의
        system_prompt = """당신은 AI 채용 관리 시스템의 에이전트입니다. 

주요 기능:
1. 채용공고 등록 및 관리
2. 지원자 관리 및 평가  
3. 면접 일정 관리
4. 포트폴리오 분석
5. 자기소개서 검증
6. 인재 추천

추가로 다음 툴들을 사용할 수 있습니다:
- GitHub API: 사용자 정보, 레포지토리, 커밋 조회
- MongoDB: 데이터베이스 문서 조회, 생성, 수정, 삭제
- 검색: 웹 검색, 뉴스 검색, 이미지 검색

사용자의 질문에 친절하고 정확하게 답변해주세요.
한국어로 답변하며, 필요시 구체적인 단계별 가이드를 제공하세요.
답변은 2-3문장으로 간결하게 작성하되, 필요한 정보는 모두 포함하세요.

툴 실행 결과가 있다면 그 결과를 바탕으로 답변해주세요.
에러가 발생한 경우에도 사용자에게 친절하게 설명해주세요.

중요: GitHub 레포지토리 분석 시 기술 스택 정보나 언어 정보를 추가로 언급하지 마세요. 
제공된 정보만 그대로 사용하세요.

절대 금지사항:
- GitHub 프로젝트 목록에서 언어 정보 (예: HTML, JavaScript, Dart) 추가 언급 금지
- 기술 스택 요약 섹션 추가 금지
- "주요 기술 스택으로는..." 같은 문장 추가 금지
- 프로젝트 이름 뒤에 언어 정보 추가 금지"""

        # 검색 기반 응답이 있는 경우 직접 반환
        if search_response:
            print(f"🔍 [DEBUG] 검색 기반 응답 사용: {search_response[:100]}...")
            response = search_response
        else:
            # AI 응답 생성
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"대화 기록:\n{conversation_context}\n\n현재 질문: {chat_message.message}"}
            ]
        
            # 툴 결과가 있으면 프롬프트에 추가
            if tool_results:
                if tool_results.get("result", {}).get("status") == "success":
                    # 툴 결과를 자연어로 변환
                    natural_language_result = format_tool_data(tool_results["result"]["data"])
                    messages.append({
                        "role": "assistant", 
                        "content": f"툴 실행 결과: {natural_language_result}"
                    })
                else:
                    # 에러가 발생한 경우 에러 정보 추가
                    error_message = create_error_aware_response(tool_results, chat_message.message)
                    messages.append({
                        "role": "assistant",
                        "content": f"툴 실행 중 오류 발생: {error_message}"
                    })
            
            print(f"🔍 [DEBUG] AI 응답 생성 시작 - 메시지 수: {len(messages)}")
            response = await openai_service.chat_completion(messages)
            print(f"🔍 [DEBUG] AI 응답 생성 완료: {response[:100]}...")
        
        # 툴 사용 시 관련 페이지로 이동하는 액션 추가
        page_action = None
        if tool_results and tool_results.get("tool"):
            tool_name = tool_results["tool"]
            action_type = tool_results.get("action", "")
            
            # 툴별 페이지 매핑
            tool_page_mapping = {
                "github": {
                    "get_user_info": {
                        "target": "/portfolio",
                        "message": "GitHub 사용자 정보를 포트폴리오 페이지에서 자세히 확인할 수 있습니다."
                    },
                    "get_repos": {
                        "target": "/portfolio", 
                        "message": "GitHub 레포지토리 정보를 포트폴리오 페이지에서 확인할 수 있습니다."
                    },
                    "get_commits": {
                        "target": "/portfolio",
                        "message": "GitHub 커밋 내역을 포트폴리오 페이지에서 확인할 수 있습니다."
                    }
                },
                "mongodb": {
                    "find_documents": {
                        "target": "/applicants",
                        "message": "데이터베이스 조회 결과를 지원자 관리 페이지에서 확인할 수 있습니다."
                    },
                    "count_documents": {
                        "target": "/dashboard",
                        "message": "데이터베이스 통계를 대시보드에서 확인할 수 있습니다."
                    }
                },
                "search": {
                    "web_search": {
                        "target": "/dashboard",
                        "message": "웹 검색 결과를 대시보드에서 종합적으로 확인할 수 있습니다."
                    },
                    "news_search": {
                        "target": "/dashboard",
                        "message": "뉴스 검색 결과를 대시보드에서 확인할 수 있습니다."
                    },
                    "image_search": {
                        "target": "/portfolio",
                        "message": "이미지 검색 결과를 포트폴리오 페이지에서 확인할 수 있습니다."
                    }
                }
            }
            
            # 툴과 액션에 따른 페이지 매핑
            if tool_name in tool_page_mapping:
                tool_config = tool_page_mapping[tool_name]
                if action_type in tool_config:
                    page_config = tool_config[action_type]
                    page_action = {
                        "action": "navigate",
                        "target": page_config["target"],
                        "message": page_config["message"]
                    }
                elif "default" in tool_config:
                    # 기본 페이지 매핑
                    page_config = tool_config["default"]
                    page_action = {
                        "action": "navigate", 
                        "target": page_config["target"],
                        "message": page_config["message"]
                    }
        
        # AI 응답 저장
        update_session(session_id, response, is_user=False)
        print(f"🔍 [DEBUG] AI 응답 저장 완료")
        
        # 추천 질문 생성
        suggestions = generate_suggestions(chat_message.message, response)
        print(f"🔍 [DEBUG] 추천 질문 생성: {suggestions}")
        
        # 빠른 액션 생성
        quick_actions = generate_quick_actions(chat_message.message, response)
        print(f"🔍 [DEBUG] 빠른 액션 생성: {quick_actions}")
        
        final_response = ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now(),
            suggestions=suggestions,
            quick_actions=quick_actions,
            confidence=0.95,
            tool_results=tool_results,
            error_info=error_info,
            page_action=page_action
        )
        
        print(f"🔍 [DEBUG] 최종 응답 생성 완료 - 세션: {session_id}")
        return final_response
        
    except Exception as e:
        print(f"🔍 [DEBUG] 에이전트 예외 발생: {str(e)}")
        logger.error(f"에이전트 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"챗봇 처리 중 오류가 발생했습니다: {str(e)}")

def generate_suggestions(user_message: str, ai_response: str) -> List[str]:
    """추천 질문 생성"""
    suggestions = [
        "채용공고를 어떻게 등록하나요?",
        "지원자 관리 기능은 어떻게 사용하나요?",
        "면접 일정을 어떻게 관리하나요?",
        "포트폴리오 분석은 어떻게 하나요?"
    ]
    
    # 사용자 메시지에 따라 관련 추천 질문 필터링
    if "채용" in user_message or "공고" in user_message:
        return [s for s in suggestions if "채용" in s or "공고" in s]
    elif "지원자" in user_message or "관리" in user_message:
        return [s for s in suggestions if "지원자" in s or "관리" in s]
    elif "면접" in user_message:
        return [s for s in suggestions if "면접" in s]
    elif "포트폴리오" in user_message or "분석" in user_message:
        return [s for s in suggestions if "포트폴리오" in s or "분석" in s]
    
    return suggestions[:3]  # 기본적으로 3개 반환

import re

def format_response_text(text: str) -> str:
    """
    한글·영어 답변을 가독성 좋게 재구성합니다.
    - 숫자 항목 뒤에 줄바꿈을 없앰
    - `**` 구문을 제거
    - 문장 끝에 두 줄 빈 줄 삽입
    - 이모지 앞에 두 줄 빈 줄 삽입
    - 불릿(•) 앞에 한 줄 빈 줄 삽입
    """
    
    if not text:
        return text

    # 1️⃣ 이모지 리스트 (섹션 구분용)
    EMOJIS = ["📋", "💡", "🎯", "🔍", "📊", "🤝", "💼", "📝", "🚀", "💻"]
    
    # 2️⃣ 숫자 항목 정규식 (숫자. 뒤에 한 칸만 남김)
    NUM_LIST_RE = re.compile(r'\b(\d+)\.\s+')
    
    # 3️⃣ 이모지 찾기
    EMOJI_RE = re.compile(r'(' + '|'.join(map(re.escape, EMOJIS)) + r')')

    # 0️⃣ 양쪽 공백 및 개행 정리
    text = text.strip()

    # 1️⃣ `**` 제거 (굵은 텍스트 표시가 필요 없으므로 없애줍니다)
    text = text.replace('**', '')

    # 2️⃣ 문장 끝(마침표·물음표·느낌표·한글 마침표) 뒤에 두 줄 빈 줄
    text = re.sub(r'([.!?。])\s+', r'\1\n\n', text)

    # 3️⃣ 불릿(•) 앞에 줄 바꿈
    text = text.replace('• ', '\n• ')

    # 4️⃣ 숫자 항목 1., 2. 앞에 줄 바꿈 **하지만** 번호 다음은 한 줄에 남김
    text = NUM_LIST_RE.sub(r'\1. ', text)     # <-- 줄바꿈 대신 공백

    # 5️⃣ 이모지 앞에 두 줄 빈 줄
    def _emoji_wrap(match):
        return f'\n\n{match.group(1)}'
    text = EMOJI_RE.sub(_emoji_wrap, text)

    # 6️⃣ 중복 빈 줄(3개 이상)을 2개로 정리
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

def generate_quick_actions(user_message: str, ai_response: str) -> List[Dict[str, Any]]:
    """빠른 액션 생성"""
    actions = [
        {
            "title": "채용공고 등록",
            "action": "navigate",
            "target": "/job-posting",
            "icon": "📝"
        },
        {
            "title": "지원자 관리",
            "action": "navigate", 
            "target": "/applicants",
            "icon": "👥"
        },
        {
            "title": "면접 관리",
            "action": "navigate",
            "target": "/interview",
            "icon": "📅"
        },
        {
            "title": "포트폴리오 분석",
            "action": "navigate",
            "target": "/portfolio",
            "icon": "📊"
        }
    ]
    
    # 사용자 메시지에 따라 관련 액션 필터링
    if "채용" in user_message or "공고" in user_message:
        return [a for a in actions if "채용" in a["title"] or "공고" in a["title"]]
    elif "지원자" in user_message:
        return [a for a in actions if "지원자" in a["title"]]
    elif "면접" in user_message:
        return [a for a in actions if "면접" in a["title"]]
    elif "포트폴리오" in user_message:
        return [a for a in actions if "포트폴리오" in a["title"]]
    
    return actions[:3]  # 기본적으로 3개 반환

@router.get("/session/{session_id}", response_model=ChatSession)
async def get_session(session_id: str):
    """세션 정보 조회"""
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    
    history = session_manager.get_history(session_id)
    
    return ChatSession(
        session_id=session_id,
        messages=history,
        created_at=datetime.fromtimestamp(session_info["created_at"]),
        last_updated=datetime.fromtimestamp(session_info["last_activity"])
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    if session_manager.delete_session(session_id):
        return {"message": "세션이 삭제되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

@router.get("/sessions")
async def list_sessions():
    """모든 세션 목록 조회"""
    # 세션 정리 후 목록 반환
    session_manager.cleanup_sessions()
    sessions = session_manager.list_all_sessions()
    
    return {
        "sessions": sessions,
        "total_count": len(sessions)
    }

@router.post("/sessions/cleanup")
async def cleanup_all_sessions():
    """모든 만료된 세션 정리"""
    before_count = len(session_manager.sessions)
    session_manager.cleanup_sessions()
    after_count = len(session_manager.sessions)
    
    return {
        "message": f"세션 정리 완료: {before_count - after_count}개 세션 삭제됨",
        "before_count": before_count,
        "after_count": after_count,
        "deleted_count": before_count - after_count
    }

@router.get("/tools/status")
async def get_tools_status():
    """툴 상태 조회"""
    return tool_executor.get_tool_status()

@router.get("/tools/available")
async def get_available_tools():
    """사용 가능한 툴 목록 조회"""
    return {
        "tools": tool_executor.get_available_tools()
    }

@router.post("/tools/execute")
async def execute_tool(tool_name: str, action: str, params: Dict[str, Any]):
    """툴 직접 실행"""
    result = tool_executor.execute(tool_name, action, **params)
    return result

@router.get("/tools/error-stats")
async def get_error_statistics():
    """에러 통계 조회"""
    return tool_executor.get_error_statistics()

@router.get("/performance/stats")
async def get_performance_statistics():
    """성능 통계 조회"""
    return tool_executor.get_performance_stats()

@router.post("/performance/cache/clear")
async def clear_cache(tool_name: str = None):
    """캐시 정리"""
    tool_executor.clear_cache(tool_name)
    return {"message": f"캐시가 정리되었습니다. (툴: {tool_name if tool_name else '전체'})"}

@router.post("/performance/stats/reset")
async def reset_performance_statistics():
    """성능 통계 초기화"""
    tool_executor.reset_performance_stats()
    return {"message": "성능 통계가 초기화되었습니다."}

# 모니터링 및 로깅 API 엔드포인트들
@router.get("/monitoring/metrics")
async def get_monitoring_metrics(tool_action: str = None):
    """모니터링 메트릭 조회"""
    metrics = monitoring_system.get_performance_metrics(tool_action)
    return {
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/monitoring/usage")
async def get_usage_statistics(days: int = 7):
    """사용량 통계 조회"""
    stats = monitoring_system.get_usage_statistics(days)
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/monitoring/logs")
async def get_recent_logs(limit: int = 100):
    """최근 로그 조회"""
    logs = monitoring_system.get_recent_logs(limit)
    return {
        "logs": logs,
        "total_count": len(logs),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/monitoring/metrics/clear")
async def clear_monitoring_metrics():
    """모니터링 메트릭 초기화"""
    monitoring_system.clear_metrics()
    return {"message": "모니터링 메트릭이 초기화되었습니다."}

@router.get("/monitoring/alerts")
async def get_alert_history():
    """알림 히스토리 조회"""
    # 실제 구현에서는 알림 히스토리를 반환
    return {
        "alerts": [],
        "message": "알림 히스토리 기능은 개발 중입니다."
    }
