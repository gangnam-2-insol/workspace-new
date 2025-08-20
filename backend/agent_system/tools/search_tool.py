"""
Search Tool

Google Custom Search API를 통한 웹 검색 툴
"""

import os
import requests
from typing import Dict, Any, List
from .base_tool import BaseTool

class SearchTool(BaseTool):
    """Google Custom Search API 연동 툴"""
    
    def __init__(self):
        super().__init__("search_tool", "Google Custom Search API 연동 툴")
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """검색 실행"""
        action = parameters.get("action", "web_search")
        
        try:
            if action == "web_search":
                return self._web_search(
                    parameters.get("query"),
                    parameters.get("num_results", 10)
                )
            elif action == "news_search":
                return self._news_search(
                    parameters.get("query"),
                    parameters.get("num_results", 10)
                )
            elif action == "image_search":
                return self._image_search(
                    parameters.get("query"),
                    parameters.get("num_results", 10)
                )
            elif action == "local_search":
                return self._local_search(
                    parameters.get("query"),
                    parameters.get("location"),
                    parameters.get("num_results", 10)
                )
            else:
                return self.create_response(False, error=f"Unknown action: {action}")
                
        except Exception as e:
            return self.create_response(False, error=str(e))
    
    def _web_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """웹 검색"""
        if not query:
            return self.create_response(False, error="Query is required")
        
        if not self.api_key or not self.search_engine_id:
            return self.create_response(False, error="Google Search API credentials not configured")
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10)  # Google API 최대 10개
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "display_link": item.get("displayLink", "")
                    })
                
                return self.create_response(True, data={
                    "query": query,
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get("totalResults", 0),
                    "search_time": data.get("searchInformation", {}).get("searchTime", 0)
                })
            else:
                return self.create_response(False, error=f"Search API error: {response.status_code}")
                
        except requests.RequestException as e:
            return self.create_response(False, error=f"Request error: {str(e)}")
    
    def _news_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """뉴스 검색"""
        if not query:
            return self.create_response(False, error="Query is required")
        
        if not self.api_key or not self.search_engine_id:
            return self.create_response(False, error="Google Search API credentials not configured")
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10),
                "searchType": "news"
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", "")
                    })
                
                return self.create_response(True, data={
                    "query": query,
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get("totalResults", 0)
                })
            else:
                return self.create_response(False, error=f"News search API error: {response.status_code}")
                
        except requests.RequestException as e:
            return self.create_response(False, error=f"Request error: {str(e)}")
    
    def _image_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """이미지 검색"""
        if not query:
            return self.create_response(False, error="Query is required")
        
        if not self.api_key or not self.search_engine_id:
            return self.create_response(False, error="Google Search API credentials not configured")
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10),
                "searchType": "image"
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "image_url": item.get("image", {}).get("thumbnailLink", ""),
                        "context": item.get("image", {}).get("contextLink", "")
                    })
                
                return self.create_response(True, data={
                    "query": query,
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get("totalResults", 0)
                })
            else:
                return self.create_response(False, error=f"Image search API error: {response.status_code}")
                
        except requests.RequestException as e:
            return self.create_response(False, error=f"Request error: {str(e)}")
    
    def _local_search(self, query: str, location: str = None, num_results: int = 10) -> Dict[str, Any]:
        """지역 검색"""
        if not query:
            return self.create_response(False, error="Query is required")
        
        if not self.api_key or not self.search_engine_id:
            return self.create_response(False, error="Google Search API credentials not configured")
        
        try:
            # 지역 정보가 있으면 쿼리에 추가
            search_query = query
            if location:
                search_query = f"{query} {location}"
            
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": search_query,
                "num": min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "display_link": item.get("displayLink", "")
                    })
                
                return self.create_response(True, data={
                    "query": query,
                    "location": location,
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get("totalResults", 0)
                })
            else:
                return self.create_response(False, error=f"Local search API error: {response.status_code}")
                
        except requests.RequestException as e:
            return self.create_response(False, error=f"Request error: {str(e)}")

