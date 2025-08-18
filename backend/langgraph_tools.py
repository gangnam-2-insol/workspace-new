"""
LangGraph 에이전트 툴 관리자
모듈화된 툴들을 중앙에서 관리하고 확장 가능한 구조로 설계
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
import os
from pathlib import Path

import importlib
try:
    _admin_guide = importlib.import_module('admin_guide')
    admin_policy = getattr(_admin_guide, 'policy', {})
except Exception:
    admin_policy = {'storage_dir': 'admin/backend/dynamic_tools', 'forbidden_patterns': []}

from langgraph_config import config as lg_config
try:
    from llm_service import LLMService  # 선택적 의존성: 없으면 LLM 경로 추론 비활성
except Exception:
    LLMService = None

class ToolManager:
    """툴 관리자 클래스"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
        self._llm = None
        self._dynamic_loaded = False
    
    def _register_default_tools(self):
        """기본 툴들 등록"""
        self.register_tool("search_jobs", self._search_jobs_tool)
        self.register_tool("analyze_resume", self._analyze_resume_tool)
        self.register_tool("create_portfolio", self._create_portfolio_tool)
        self.register_tool("submit_application", self._submit_application_tool)
        self.register_tool("get_user_info", self._get_user_info_tool)
        self.register_tool("get_interview_schedule", self._get_interview_schedule_tool)
        self.register_tool("navigate", self._navigate_tool)
        self.register_tool("create_function_tool", self._create_function_tool)
        self.register_tool("dom_action", self._dom_action_tool)
    
    def register_tool(self, tool_name: str, tool_function):
        """새로운 툴 등록"""
        self.tools[tool_name] = tool_function
    
    def get_tool(self, tool_name: str):
        """툴 가져오기"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """등록된 툴 목록 반환"""
        return list(self.tools.keys())

    def unregister_tool(self, tool_name: str) -> None:
        """툴 등록 해제"""
        if tool_name in self.tools:
            try:
                del self.tools[tool_name]
            except Exception:
                pass
    
    def execute_tool(self, tool_name: str, query: str, context: Dict[str, Any] = None) -> str:
        """툴 실행"""
        # 필요 시 동적 툴을 지연 로드하여 시작 속도 개선
        try:
            self.load_dynamic_tools()
        except Exception:
            pass
        # 관리자 모드 권한 검사 (create_function_tool, 동적 코드 관련)
        def _is_admin_mode(session_id: str) -> bool:
            try:
                mod = importlib.import_module('admin_mode')
                fn = getattr(mod, 'is_admin_mode', None)
                return bool(fn(session_id)) if callable(fn) else False
            except Exception:
                return False
        session_id = (context or {}).get("session_id", "")
        if tool_name in ("create_function_tool",) and not _is_admin_mode(session_id):
            return json.dumps({
                "success": False,
                "response": "권한이 없습니다. 관리자 모드로 전환하세요.",
                "type": "react_agent_response"
            }, ensure_ascii=False)

        # 공개 허용 툴 화이트리스트 검사 (navigate 등)
        if tool_name not in lg_config.allowed_public_tools:
            # 동적 툴인 경우 trusted 메타 확인
            meta = self._get_dynamic_tool_meta(tool_name)
            if meta is not None and meta.get('trusted', False) is True:
                pass  # 승인된 동적 툴은 허용
            else:
                # 관리자 모드가 아니면 차단
                if not _is_admin_mode(session_id):
                    return json.dumps({
                        "success": False,
                        "response": "승인된 툴이 아니어서 실행할 수 없습니다.",
                        "type": "react_agent_response"
                    }, ensure_ascii=False)

        tool = self.get_tool(tool_name)
        if tool:
            try:
                mode = (lg_config.tool_execution_mode or {}).get(tool_name, 'local')
                # 현재 구현: navigate/dom_action/search 등은 내부(local) 직접 실행
                # LLM이 필요한 경우는 도구 내부에서 자체적으로 호출(또는 context로 플래그 전달)
                # mode가 'llm'이어도, LLM 불가/에러 시 도구 내부 폴백이 적용되도록 유지
                return tool(query, context or {})
            except Exception as e:
                return f"툴 실행 중 오류가 발생했습니다: {str(e)}"
        else:
            return f"툴 '{tool_name}'을 찾을 수 없습니다."

    # LLM 헬퍼
    def _get_llm(self):
        if self._llm is None and LLMService is not None:
            try:
                self._llm = LLMService()
            except Exception:
                self._llm = None
        return self._llm

    def _resolve_route_with_llm(self, text: str) -> Optional[str]:
        """LLM을 사용해 허용 라우트 중 최적 경로를 선택. 실패 시 None 반환"""
        llm = self._get_llm()
        if llm is None:
            return None
        try:
            allowed = lg_config.allowed_routes
            # 라벨/동의어 제공해 힌트 강화
            keyword_to_path = {
                "/": ["대시보드", "홈", "메인", "home", "dashboard"],
                "/job-posting": ["채용공고", "채용", "공고", "job", "job posting", "posting"],
                "/resume": ["이력서", "이력서관리", "resume", "cv"],
                "/applicants": ["지원자", "지원자관리", "applicant", "candidate"],
                "/interview": ["면접", "면접관리", "interview"],
                "/interview-calendar": ["캘린더", "달력", "일정", "calendar"],
                "/portfolio": ["포트폴리오", "portfolio"],
                "/cover-letter": ["자소서", "cover letter"],
                "/talent": ["인재", "인재추천", "talent"],
                "/users": ["사용자", "사용자관리", "user", "users"],
                "/settings": ["설정", "세팅", "setting", "settings"]
            }

            system = (
                "너는 웹앱 내 페이지 이동을 위한 라우트 선택기다. "
                "반드시 아래 allowed_routes 중 하나만 선택하고, JSON으로만 답한다. "
                "창작/추론으로 새로운 경로를 만들지 말 것."
            )
            user_prompt = (
                f"사용자 입력: {text}\n\n"
                f"allowed_routes: {allowed}\n\n"
                f"참고 동의어: {keyword_to_path}\n\n"
                "출력 형식: {\n  \"target\": \"<allowed_routes 중 하나>\"\n}\n"
                "규칙: 정확히 하나만 고르고, 다른 말은 쓰지 말 것."
            )
            # OpenAI 호출 사용 (LLMService 내부 client)
            response = llm.client.chat.completions.create(
                model=llm.model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            text_resp = response.choices[0].message.content if response.choices else ''
            # 간단 JSON 파싱
            import json as _json
            target = None
            try:
                parsed = _json.loads(text_resp)
                target = str(parsed.get('target') or '').strip()
            except Exception:
                # 텍스트에서 첫 JSON 블록 추출 시도
                start = text_resp.find('{')
                end = text_resp.rfind('}')
                if start != -1 and end != -1 and end > start:
                    try:
                        parsed = _json.loads(text_resp[start:end+1])
                        target = str(parsed.get('target') or '').strip()
                    except Exception:
                        target = None
            if target in allowed:
                return target
        except Exception:
            return None
        return None

    # 동적 툴 저장/로드
    def _dynamic_tools_dir(self) -> str:
        # 정책 파일 기준 경로 사용
        base = os.path.join(Path.cwd(), admin_policy.get('storage_dir', 'admin/backend/dynamic_tools'))
        os.makedirs(base, exist_ok=True)
        return base

    # 인덱스 헬퍼
    def _index_paths(self):
        base = self._dynamic_tools_dir()
        return base, os.path.join(base, 'index.json')

    def _read_index(self) -> Dict[str, Any]:
        base, index_path = self._index_paths()
        if not os.path.exists(index_path):
            return {"tools": []}
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"tools": []}

    def _write_index(self, index: Dict[str, Any]) -> None:
        base, index_path = self._index_paths()
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def load_dynamic_tools(self) -> None:
        """저장소에서 동적 툴 로드"""
        if self._dynamic_loaded:
            return
        base = self._dynamic_tools_dir()
        index = self._read_index()
        for item in index.get('tools', []):
            name = item.get('name')
            file_path = os.path.join(base, f"{name}.py")
            if os.path.exists(file_path):
                func = self._load_function_from_file(file_path)
                if func:
                    self.register_tool(name, func)
        self._dynamic_loaded = True

    def _load_function_from_file(self, file_path: str):
        """파일에서 안전한 run(query, context) 함수 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            # 안전 검증
            if self._is_dangerous_code(source):
                return None

            local_env = {}
            safe_builtins = {
                'len': len, 'range': range, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
                'str': str, 'int': int, 'float': float, 'bool': bool, 'dict': dict, 'list': list,
                'enumerate': enumerate, 'zip': zip
            }
            exec(compile(source, file_path, 'exec'), {'__builtins__': safe_builtins}, local_env)
            func = local_env.get('run')
            if callable(func):
                return lambda query, context: func(query, context)
        except Exception:
            return None
        return None

    def list_dynamic_tools(self) -> List[Dict[str, Any]]:
        index = self._read_index()
        tools = []
        for t in index.get('tools', []):
            t.setdefault('trusted', False)
            tools.append(t)
        return tools

    def _get_dynamic_tool_meta(self, name: str) -> Optional[Dict[str, Any]]:
        for t in self.list_dynamic_tools():
            if t.get('name') == name:
                return t
        return None

    def create_dynamic_tool(self, name: str, code: str, description: str = "") -> bool:
        if not name or not code or self._is_dangerous_code(code):
            return False
        base = self._dynamic_tools_dir()
        file_path = os.path.join(base, f"{name}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        # update index
        index = self._read_index()
        index["tools"] = [t for t in index.get("tools", []) if t.get('name') != name]
        # 관리자 생성 시 자동 신뢰 적용 옵션은 비활성 (별도 API에서 설정)
        is_trusted = False
        index["tools"].append({"name": name, "description": description, "trusted": is_trusted})
        self._write_index(index)
        # register
        func = self._load_function_from_file(file_path)
        if func:
            self.register_tool(name, func)
            return True
        return False

    def update_dynamic_tool(self, name: str, code: str | None = None, description: str | None = None) -> bool:
        base = self._dynamic_tools_dir()
        file_path = os.path.join(base, f"{name}.py")
        if not os.path.exists(file_path):
            return False
        if code is not None:
            if self._is_dangerous_code(code):
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
        if description is not None:
            index = self._read_index()
            new_list = []
            updated = False
            for t in index.get('tools', []):
                if t.get('name') == name:
                    t['description'] = description
                    updated = True
                new_list.append(t)
            if not updated:
                new_list.append({"name": name, "description": description, "trusted": False})
            index['tools'] = new_list
            self._write_index(index)
        # re-register latest code
        func = self._load_function_from_file(file_path)
        if func:
            self.register_tool(name, func)
            return True
        return False

    def delete_dynamic_tool(self, name: str) -> bool:
        base = self._dynamic_tools_dir()
        file_path = os.path.join(base, f"{name}.py")
        exists = os.path.exists(file_path)
        if exists:
            try:
                os.remove(file_path)
            except Exception:
                return False
        # update index
        index = self._read_index()
        index['tools'] = [t for t in index.get('tools', []) if t.get('name') != name]
        self._write_index(index)
        # unregister
        self.unregister_tool(name)
        return exists

    def set_dynamic_trusted(self, name: str, trusted: bool) -> bool:
        index = self._read_index()
        changed = False
        for t in index.get('tools', []):
            if t.get('name') == name:
                t['trusted'] = bool(trusted)
                changed = True
        if changed:
            self._write_index(index)
        return changed
    
    # 기본 툴 구현들
    def _search_jobs_tool(self, query: str, context: Dict[str, Any]) -> str:
        """채용 정보 검색 툴"""
        # 실제로는 데이터베이스에서 검색
        # 여기서는 시뮬레이션된 데이터 반환
        
        # 쿼리에서 키워드 추출
        keywords = self._extract_keywords(query)
        
        # 시뮬레이션된 채용 정보
        jobs_data = [
            {
                "id": "job_001",
                "title": "Python 백엔드 개발자",
                "company": "테크스타트업",
                "location": "서울 강남구",
                "salary": "4000-6000만원",
                "skills": ["Python", "Django", "PostgreSQL"],
                "experience": "3-5년"
            },
            {
                "id": "job_002", 
                "title": "React 프론트엔드 개발자",
                "company": "IT 서비스 회사",
                "location": "서울 마포구",
                "salary": "3500-5000만원",
                "skills": ["React", "TypeScript", "Next.js"],
                "experience": "2-4년"
            },
            {
                "id": "job_003",
                "title": "AI/ML 엔지니어",
                "company": "AI 스타트업",
                "location": "서울 서초구", 
                "salary": "5000-8000만원",
                "skills": ["Python", "TensorFlow", "PyTorch"],
                "experience": "4-7년"
            }
        ]
        
        # 키워드 기반 필터링
        filtered_jobs = []
        for job in jobs_data:
            if any(keyword.lower() in job["title"].lower() or 
                   keyword.lower() in job["skills"] for keyword in keywords):
                filtered_jobs.append(job)
        
        if not filtered_jobs:
            filtered_jobs = jobs_data[:2]  # 기본 결과
        
        # 결과 포맷팅
        result = f"'{query}'에 대한 채용 정보 검색 결과:\n\n"
        for job in filtered_jobs:
            result += f"• {job['title']} ({job['company']}, {job['location']})\n"
            result += f"  - 급여: {job['salary']}\n"
            result += f"  - 필요 기술: {', '.join(job['skills'])}\n"
            result += f"  - 경력: {job['experience']}\n\n"
        
        return result
    
    def _analyze_resume_tool(self, query: str, context: Dict[str, Any]) -> str:
        """이력서 분석 툴"""
        # 시뮬레이션된 이력서 분석 결과
        
        # 분석할 텍스트 추출 (실제로는 파일 업로드나 텍스트 입력 처리)
        resume_text = query if len(query) > 10 else "Python 개발자 3년 경력, Django, React 경험"
        
        # 키워드 기반 분석
        skills = self._extract_skills_from_text(resume_text)
        experience_years = self._extract_experience_years(resume_text)
        
        # 분석 결과
        result = f"이력서 분석 결과:\n\n"
        result += f"• 주요 기술 스택: {', '.join(skills)}\n"
        result += f"• 경력 연차: {experience_years}년\n"
        result += f"• 추천 직무: {self._get_recommended_jobs(skills, experience_years)}\n"
        result += f"• 매칭도: {self._calculate_matching_score(skills, experience_years)}%\n"
        
        return result
    
    def _create_portfolio_tool(self, query: str, context: Dict[str, Any]) -> str:
        """포트폴리오 생성 툴"""
        # 시뮬레이션된 포트폴리오 생성
        
        portfolio_id = f"PORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = "포트폴리오가 성공적으로 생성되었습니다.\n\n"
        result += f"• 포트폴리오 ID: {portfolio_id}\n"
        result += f"• 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        result += f"• 상태: 활성\n"
        result += f"• 접근 URL: /portfolio/{portfolio_id}\n\n"
        result += "포트폴리오에 프로젝트와 경험을 추가하여 완성해보세요!"
        
        return result
    
    def _submit_application_tool(self, query: str, context: Dict[str, Any]) -> str:
        """지원서 제출 툴"""
        # 시뮬레이션된 지원서 제출
        
        application_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = "지원서가 성공적으로 제출되었습니다.\n\n"
        result += f"• 지원 ID: {application_id}\n"
        result += f"• 제출일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        result += f"• 상태: 검토 중\n"
        result += f"• 예상 검토 기간: 3-5일\n\n"
        result += "지원 현황은 마이페이지에서 확인할 수 있습니다."
        
        return result
    
    def _get_user_info_tool(self, query: str, context: Dict[str, Any]) -> str:
        """사용자 정보 조회 툴"""
        # 시뮬레이션된 사용자 정보
        
        user_info = {
            "name": "홍길동",
            "email": "hong@example.com",
            "phone": "010-1234-5678",
            "join_date": "2024-01-01",
            "last_login": "2024-01-15 14:30",
            "profile_complete": "85%",
            "applications_count": 3,
            "interviews_count": 1
        }
        
        result = "사용자 정보:\n\n"
        result += f"• 이름: {user_info['name']}\n"
        result += f"• 이메일: {user_info['email']}\n"
        result += f"• 전화번호: {user_info['phone']}\n"
        result += f"• 가입일: {user_info['join_date']}\n"
        result += f"• 최근 로그인: {user_info['last_login']}\n"
        result += f"• 프로필 완성도: {user_info['profile_complete']}\n"
        result += f"• 지원 횟수: {user_info['applications_count']}회\n"
        result += f"• 면접 횟수: {user_info['interviews_count']}회"
        
        return result
    
    def _get_interview_schedule_tool(self, query: str, context: Dict[str, Any]) -> str:
        """면접 일정 조회 툴"""
        # 시뮬레이션된 면접 일정
        
        interviews = [
            {
                "id": "INT_001",
                "company": "테크스타트업",
                "position": "Python 백엔드 개발자",
                "date": "2024-01-20",
                "time": "14:00",
                "type": "1차 면접",
                "location": "서울 강남구",
                "status": "예정"
            },
            {
                "id": "INT_002",
                "company": "IT 서비스 회사", 
                "position": "React 프론트엔드 개발자",
                "date": "2024-01-25",
                "time": "15:00",
                "type": "2차 면접",
                "location": "온라인 (Zoom)",
                "status": "예정"
            }
        ]
        
        result = "면접 일정:\n\n"
        for interview in interviews:
            result += f"• {interview['date']} {interview['time']} - {interview['type']}\n"
            result += f"  - 회사: {interview['company']}\n"
            result += f"  - 직무: {interview['position']}\n"
            result += f"  - 장소: {interview['location']}\n"
            result += f"  - 상태: {interview['status']}\n\n"
        
        return result

    def _navigate_tool(self, query: str, context: Dict[str, Any]) -> str:
        """페이지 이동 명령을 생성하는 툴
        입력 예: "잡 포스팅 페이지로 이동" 또는 JSON: {"target": "/job-posting"}
        출력: 프론트가 해석 가능한 구조화 JSON 문자열
        """
        target = None
        # JSON 형태 입력 시
        try:
            parsed = json.loads(query)
            if isinstance(parsed, dict) and "target" in parsed:
                target = str(parsed.get("target") or "").strip()
        except Exception:
            pass

        # 1) LLM 경로 추론 시도 (허용 라우트 중 선택)
        if not target:
            text = str(query or "").strip()
            llm_target = self._resolve_route_with_llm(text)
            if llm_target:
                target = llm_target
        # 2) 폴백 제거: 사용자가 원한 전략대로 LLM 실패 시 기본 라우트만 사용

        if not target:
            target = "/"

        # 허용 경로 화이트리스트 적용
        if target not in lg_config.allowed_routes:
            target = "/"

        payload = {
            "success": True,
            "response": f"페이지를 {target}으로 이동합니다. (navigate 툴 적용)",
            "type": "react_agent_response",
            "page_action": {
                "action": "navigate",
                "target": target
            }
        }
        return json.dumps(payload, ensure_ascii=False)

    def _dom_action_tool(self, query: str, context: Dict[str, Any]) -> str:
        """프론트가 수행할 DOM 액션 명령을 생성
        입력 예:
        {
          "action": "typeText" | "submitForm" | "check" | "selectOption" | "scrollToElement" | "scrollToBottom" | "copyText" | "pasteText" | "getText" | "exists",
          "args": { "selector": "#id", "text": "hello", "value": "opt", "query": "지원하기 버튼" }
        }
        출력: 프론트가 해석 가능한 JSON
        selector가 없고 query가 있으면 프론트는 UI 인덱스에서 자연어로 타겟을 해석한다.
        """
        try:
            payload = json.loads(query) if isinstance(query, str) else (query or {})
        except Exception:
            payload = {}
        action = str(payload.get('action') or '').strip()
        args = payload.get('args') or {}

        # 허용 액션 화이트리스트
        allowed = {
            "click": ["selector"],
            "typeText": ["selector", "text"],
            "submitForm": ["selector"],
            "check": ["selector"],
            "selectOption": ["selector", "value"],
            "scrollToElement": ["selector"],
            "scrollToBottom": [],
            "copyText": ["selector"],
            "pasteText": ["selector"],
            "getText": ["selector"],
            "exists": ["selector"],
            "dumpUI": []
        }

        if action not in allowed:
            return json.dumps({
                "success": False,
                "response": "허용되지 않은 DOM 액션입니다.",
                "type": "react_agent_response"
            }, ensure_ascii=False)

        # 필수 인자 검증 (selector는 query로 대체 가능: 프론트가 해석)
        missing = [k for k in allowed[action] if k not in args]
        if missing:
            # selector만 누락이고 query가 있으면 허용
            if not (missing == ["selector"] and isinstance(args.get('query'), str) and len(args.get('query')) > 0):
                return json.dumps({
                    "success": False,
                    "response": f"필수 인자 누락: {', '.join(missing)}",
                    "type": "react_agent_response"
                }, ensure_ascii=False)

        return json.dumps({
            "success": True,
            "response": f"DOM 액션 '{action}'을(를) 실행합니다.",
            "type": "react_agent_response",
            "page_action": {
                "action": "dom",
                "dom_action": action,
                "args": args
            }
        }, ensure_ascii=False)

    def _create_function_tool(self, query: str, context: Dict[str, Any]) -> str:
        """LLM 없이 안전 샘플로 동적 툴 생성 프로토타입
        입력(JSON 문자열 권장): {
          "name": "echo_tool",
          "description": "입력을 그대로 반환",
          "params": {"query": "str"},
          "return_type": "str",
          "requirements": "특수문자 제거 후 반환"
        }
        실제 LLM 연동은 보안 검토 후 연결
        """
        try:
            payload = json.loads(query) if isinstance(query, str) else (query or {})
        except Exception:
            payload = {}
        name = str(payload.get('name') or '').strip()
        description = str(payload.get('description') or '')
        if not name:
            return json.dumps({"success": False, "response": "name이 필요합니다."}, ensure_ascii=False)

        # 간단 샘플 함수 본문(안전한 범위)
        code = (
            "def run(query, context):\n"
            "    text = str(query)\n"
            "    # 특수문자 제거 후 반환\n"
            "    allowed = ''.join(ch for ch in text if ch.isalnum() or ch.isspace())\n"
            "    return allowed\n"
        )

        if self._is_dangerous_code(code):
            return json.dumps({"success": False, "response": "위험 코드 감지"}, ensure_ascii=False)

        # 저장
        base = self._dynamic_tools_dir()
        file_path = os.path.join(base, f"{name}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

        # 인덱스 갱신
        index_path = os.path.join(base, 'index.json')
        index = {"tools": []}
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except Exception:
                index = {"tools": []}
        # 중복 제거 후 추가
        index["tools"] = [t for t in index.get("tools", []) if t.get('name') != name]
        index["tools"].append({"name": name, "description": description})
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        # 로드 및 등록
        func = self._load_function_from_file(file_path)
        if func:
            self.register_tool(name, func)
            response = {
                "success": True,
                "response": f"함수 {name} 생성 및 등록 완료",
                "type": "react_agent_response",
                "page_action": None,
                "tool_name": name
            }
        else:
            response = {"success": False, "response": "툴 등록 실패"}

        return json.dumps(response, ensure_ascii=False)

    # 간단 금지 패턴 검사
    def _is_dangerous_code(self, source: str) -> bool:
        forbidden = admin_policy.get('forbidden_patterns', []) + [
            'fork', 'popen', 'remove(', 'rmdir(', 'unlink(', 'system('
        ]
        lowered = source.lower()
        return any(token in lowered for token in forbidden)
    
    # 유틸리티 메서드들
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        keywords = ["Python", "React", "Java", "JavaScript", "AI", "ML", "개발자", "엔지니어"]
        found_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in text.lower():
                found_keywords.append(keyword)
        
        return found_keywords if found_keywords else ["개발자"]
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """텍스트에서 기술 스택 추출"""
        skills = ["Python", "React", "Django", "JavaScript", "TypeScript", "PostgreSQL", "MongoDB"]
        found_skills = []
        
        for skill in skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return found_skills if found_skills else ["Python", "JavaScript"]
    
    def _extract_experience_years(self, text: str) -> int:
        """텍스트에서 경력 연차 추출"""
        # 정규식으로 연차 추출
        patterns = [
            r'(\d+)\s*년\s*경력',
            r'경력\s*(\d+)\s*년',
            r'(\d+)\s*년\s*경험'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return 3  # 기본값
    
    def _get_recommended_jobs(self, skills: List[str], experience: int) -> str:
        """기술과 경력에 따른 추천 직무"""
        if "Python" in skills and experience >= 3:
            return "백엔드 개발자, 풀스택 개발자"
        elif "React" in skills:
            return "프론트엔드 개발자, 웹 개발자"
        elif "AI" in skills or "ML" in skills:
            return "AI 엔지니어, 머신러닝 엔지니어"
        else:
            return "소프트웨어 개발자"
    
    def _calculate_matching_score(self, skills: List[str], experience: int) -> int:
        """매칭 점수 계산"""
        base_score = 60
        skill_bonus = len(skills) * 5
        experience_bonus = min(experience * 3, 20)
        
        return min(base_score + skill_bonus + experience_bonus, 95)

# 전역 툴 매니저 인스턴스
tool_manager = ToolManager()
