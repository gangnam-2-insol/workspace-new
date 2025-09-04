"""
네이버 검색 API 서비스
실제 네이버 검색 결과를 제공하는 서비스
"""

import os
import logging
import httpx
from typing import Dict, List, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

logger = logging.getLogger(__name__)

class NaverSearchService:
    """네이버 검색 API 서비스"""

    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID") or os.getenv("Client_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET") or os.getenv("Client_Secret")
        self.base_url = "https://openapi.naver.com/v1/search"

        if not self.client_id or not self.client_secret:
            logger.warning("네이버 API 키가 설정되지 않았습니다.")
            logger.warning(f"Client ID: {self.client_id}")
            logger.warning(f"Client Secret: {self.client_secret}")

    async def search_web(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict:
        """일반 웹 검색"""
        return await self._search("web", query, display, start, sort)

    async def search_blog(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict:
        """블로그 검색"""
        return await self._search("blog", query, display, start, sort)

    async def search_news(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict:
        """뉴스 검색"""
        return await self._search("news", query, display, start, sort)

    async def search_kin(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict:
        """지식iN 검색"""
        return await self._search("kin", query, display, start, sort)

    async def _search(self, search_type: str, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict:
        """공통 검색 메서드"""
        try:
            if not self.client_id or not self.client_secret:
                return self._get_fallback_response(query, search_type)

            # URL 파라미터를 올바르게 인코딩
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            # URL 형식: /search/web?query=... 형태로 구성
            url = f"{self.base_url}/{search_type}?query={encoded_query}&display={min(display, 100)}&start={min(start, 1000)}&sort={sort}"

            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }

            logger.info(f"🔍 [네이버 검색] {search_type} 검색 시작: {query}")
            logger.info(f"🔍 [네이버 검색] URL: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                data = response.json()
                logger.info(f"✅ [네이버 검색] {search_type} 검색 완료: {data.get('total', 0)}개 결과")

                return self._format_response(data, search_type, query)

        except Exception as e:
            logger.error(f"❌ [네이버 검색] {search_type} 검색 실패: {str(e)}")
            return self._get_fallback_response(query, search_type)

    def _format_response(self, data: Dict, search_type: str, query: str) -> Dict:
        """검색 결과 포맷팅"""
        total = data.get("total", 0)
        items = data.get("items", [])

        # HTML 태그 제거
        formatted_items = []
        for item in items:
            formatted_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # HTML 태그 제거
                    import re
                    clean_value = re.sub(r'<[^>]+>', '', value)
                    formatted_item[key] = clean_value
                else:
                    formatted_item[key] = value
            formatted_items.append(formatted_item)

        return {
            "success": True,
            "message": f"🔍 '{query}'에 대한 네이버 {search_type} 검색 결과입니다:",
            "data": {
                "query": query,
                "search_type": search_type,
                "total_results": total,
                "display_count": len(formatted_items),
                "results": formatted_items,
                "source": "naver"
            }
        }

    def _get_fallback_response(self, query: str, search_type: str) -> Dict:
        """API 키가 없을 때의 대체 응답"""
        return {
            "success": False,
            "message": f"🔍 '{query}'에 대한 {search_type} 검색 결과입니다 (시뮬레이션):",
            "data": {
                "query": query,
                "search_type": search_type,
                "total_results": 2,
                "display_count": 2,
                "results": [
                    {
                        "title": f"{query} 관련 정보 1",
                        "link": "https://example1.com",
                        "description": f"{query}에 대한 상세한 정보를 제공합니다."
                    },
                    {
                        "title": f"{query} 관련 정보 2",
                        "link": "https://example2.com",
                        "description": f"{query}에 대한 추가 정보입니다."
                    }
                ],
                "source": "simulation"
            }
        }

# 싱글톤 인스턴스
naver_search_service = NaverSearchService()
