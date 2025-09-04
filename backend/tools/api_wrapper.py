"""
API 툴 래핑 모듈
기존 API들을 더 사용하기 쉽게 감싸는 래퍼 클래스들
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class APIRetryConfig:
    """API 재시도 설정"""
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

def retry_on_failure(config: APIRetryConfig = None):
    """재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_config = config or APIRetryConfig()
            last_exception = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_config.max_retries:
                        wait_time = retry_config.delay * (retry_config.backoff ** attempt)
                        logger.warning(f"API 호출 실패 (시도 {attempt + 1}/{retry_config.max_retries + 1}): {str(e)}. {wait_time}초 후 재시도...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"API 호출 최종 실패: {str(e)}")
                        raise last_exception

            raise last_exception
        return wrapper
    return decorator

class ApplicantManagementWrapper:
    """지원자 관리 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry_on_failure()
    async def create_applicant(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """지원자 생성 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/applicants/",
                json=applicant_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"지원자 생성 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure()
    async def get_applicants(self,
                           skip: int = 0,
                           limit: int = 50,
                           status: Optional[str] = None,
                           position: Optional[str] = None) -> Dict[str, Any]:
        """지원자 목록 조회 래퍼"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if position:
            params["position"] = position

        try:
            response = await self.client.get(
                f"{self.base_url}/api/applicants/",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"지원자 목록 조회 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure()
    async def update_applicant_status(self, applicant_id: str, status: str) -> Dict[str, Any]:
        """지원자 상태 업데이트 래퍼"""
        try:
            response = await self.client.put(
                f"{self.base_url}/api/applicants/{applicant_id}/status",
                json={"status": status}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"지원자 상태 업데이트 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

class ChatbotWrapper:
    """채팅봇 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry_on_failure()
    async def ai_assistant_chat(self,
                              user_input: str,
                              session_id: Optional[str] = None,
                              mode: str = "ai_assistant") -> Dict[str, Any]:
        """AI 어시스턴트 채팅 래퍼"""
        try:
            payload = {
                "user_input": user_input,
                "mode": mode
            }
            if session_id:
                payload["session_id"] = session_id

            response = await self.client.post(
                f"{self.base_url}/chatbot/ai-assistant",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"AI 어시스턴트 채팅 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure()
    async def generate_title(self,
                           job_description: str,
                           company_name: str,
                           concept: str = "일반형") -> Dict[str, Any]:
        """AI 제목 추천 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/chatbot/generate-title",
                json={
                    "job_description": job_description,
                    "company_name": company_name,
                    "concept": concept
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"제목 추천 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

class PDFOCRWrapper:
    """PDF OCR API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)  # OCR은 시간이 오래 걸림

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=2.0))
    async def upload_resume(self,
                          file_path: str,
                          name: Optional[str] = None,
                          email: Optional[str] = None,
                          phone: Optional[str] = None,
                          job_posting_id: str = None) -> Dict[str, Any]:
        """이력서 업로드 및 OCR 처리 래퍼"""
        try:
            with open(file_path, 'rb') as f:
                files = {"file": f}
                data = {}
                if name:
                    data["name"] = name
                if email:
                    data["email"] = email
                if phone:
                    data["phone"] = phone
                if job_posting_id:
                    data["job_posting_id"] = job_posting_id

                response = await self.client.post(
                    f"{self.base_url}/api/integrated-ocr/upload-resume",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            raise HTTPException(status_code=400, detail=f"파일을 찾을 수 없습니다: {file_path}")
        except httpx.HTTPStatusError as e:
            logger.error(f"이력서 업로드 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=2.0))
    async def upload_cover_letter(self,
                                file_path: str,
                                job_posting_id: str) -> Dict[str, Any]:
        """자기소개서 업로드 및 OCR 처리 래퍼"""
        try:
            with open(file_path, 'rb') as f:
                response = await self.client.post(
                    f"{self.base_url}/api/integrated-ocr/upload-cover-letter",
                    files={"file": f},
                    data={"job_posting_id": job_posting_id}
                )
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            raise HTTPException(status_code=400, detail=f"파일을 찾을 수 없습니다: {file_path}")
        except httpx.HTTPStatusError as e:
            logger.error(f"자기소개서 업로드 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

class GitHubAnalysisWrapper:
    """GitHub 분석 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)  # GitHub 분석은 시간이 오래 걸림

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=5.0))
    async def analyze_user(self,
                          username: str,
                          force_reanalysis: bool = False) -> Dict[str, Any]:
        """GitHub 사용자 분석 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/github/summary",
                json={
                    "username": username,
                    "force_reanalysis": force_reanalysis
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub 사용자 분석 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=5.0))
    async def analyze_repository(self,
                               username: str,
                               repo_name: str) -> Dict[str, Any]:
        """GitHub 저장소 분석 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/github/repo-analysis",
                json={
                    "username": username,
                    "repo_name": repo_name
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub 저장소 분석 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

class ResumeSearchWrapper:
    """이력서 검색 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry_on_failure()
    async def keyword_search(self,
                           query: str,
                           limit: int = 10) -> Dict[str, Any]:
        """키워드 검색 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/resume/search/keyword",
                json={
                    "query": query,
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"키워드 검색 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure()
    async def hybrid_search(self,
                          query: str,
                          filters: Optional[Dict[str, Any]] = None,
                          limit: int = 10) -> Dict[str, Any]:
        """하이브리드 검색 래퍼"""
        try:
            payload = {
                "query": query,
                "limit": limit
            }
            if filters:
                payload["filters"] = filters

            response = await self.client.post(
                f"{self.base_url}/api/resume/search/multi-hybrid",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"하이브리드 검색 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

class AIAnalysisWrapper:
    """AI 분석 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=3.0))
    async def analyze_resume(self,
                           applicant_id: str,
                           analyzer_type: str = "openai",
                           force_reanalysis: bool = False) -> Dict[str, Any]:
        """이력서 AI 분석 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/ai-analysis/resume/analyze",
                json={
                    "applicant_id": applicant_id,
                    "analyzer_type": analyzer_type,
                    "force_reanalysis": force_reanalysis
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"이력서 AI 분석 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @retry_on_failure(APIRetryConfig(max_retries=2, delay=3.0))
    async def batch_analyze_resumes(self,
                                  applicant_ids: List[str],
                                  analyzer_type: str = "openai") -> Dict[str, Any]:
        """일괄 이력서 분석 래퍼"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/ai-analysis/resume/batch-analyze",
                json={
                    "applicant_ids": applicant_ids,
                    "analyzer_type": analyzer_type
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"일괄 이력서 분석 실패: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# 통합 래퍼 클래스
class HireMeAPIWrapper:
    """AI 채용 관리 시스템 통합 API 래퍼"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.applicant = ApplicantManagementWrapper(base_url)
        self.chatbot = ChatbotWrapper(base_url)
        self.pdf_ocr = PDFOCRWrapper(base_url)
        self.github = GitHubAnalysisWrapper(base_url)
        self.resume_search = ResumeSearchWrapper(base_url)
        self.ai_analysis = AIAnalysisWrapper(base_url)

    async def close(self):
        """클라이언트 연결 종료"""
        await self.applicant.client.aclose()
        await self.chatbot.client.aclose()
        await self.pdf_ocr.client.aclose()
        await self.github.client.aclose()
        await self.resume_search.client.aclose()
        await self.ai_analysis.client.aclose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.close())
