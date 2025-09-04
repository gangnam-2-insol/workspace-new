"""
검색 결과 상세 페이지 라우터
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from modules.core.services.naver_search_service import naver_search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search-results", tags=["search-results"])

@router.get("/")
async def get_search_results(
    query: str = Query(..., description="검색어"),
    search_type: str = Query("blog", description="검색 타입 (blog, news, kin, image)"),
    page: int = Query(1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(10, description="페이지당 결과 수 (최대 100)")
):
    """검색 결과 상세 조회"""
    try:
        logger.info(f"🔍 검색 결과 상세 조회: {query}, 타입: {search_type}, 페이지: {page}")

        # 페이지 계산
        start = (page - 1) * page_size + 1

        # 검색 실행
        if search_type == "blog":
            result = await naver_search_service.search_blog(query, display=page_size, start=start)
        elif search_type == "news":
            result = await naver_search_service.search_news(query, display=page_size, start=start)
        elif search_type == "kin":
            result = await naver_search_service.search_kin(query, display=page_size, start=start)
        elif search_type == "image":
            result = await naver_search_service.search_image(query, display=page_size, start=start)
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 검색 타입: {search_type}")

        if not result["success"]:
            raise HTTPException(status_code=500, detail="검색 실패")

        # 응답 데이터 구성
        data = result["data"]
        total_results = data["total_results"]
        current_results = data["results"]

        # 페이지네이션 정보
        total_pages = (total_results + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "success": True,
            "query": query,
            "search_type": search_type,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_results": total_results,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "start": start,
                "end": min(start + page_size - 1, total_results)
            },
            "results": current_results,
            "filters": {
                "search_type": search_type,
                "sort_options": ["sim", "date", "asc"],
                "date_range": ["all", "1d", "1w", "1m", "1y"]
            }
        }

    except Exception as e:
        logger.error(f"검색 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"검색 결과 조회 실패: {str(e)}")

@router.get("/suggestions")
async def get_search_suggestions(query: str = Query(..., description="검색어")):
    """검색어 자동완성 제안"""
    try:
        # 간단한 자동완성 로직 (실제로는 더 정교한 알고리즘 사용)
        suggestions = [
            f"{query} 개발자",
            f"{query} 강의",
            f"{query} 튜토리얼",
            f"{query} 예제",
            f"{query} 최신",
            f"{query} 2024",
            f"{query} 취업",
            f"{query} 채용"
        ]

        return {
            "success": True,
            "query": query,
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"검색 제안 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"검색 제안 생성 실패: {str(e)}")

@router.get("/trending")
async def get_trending_searches():
    """인기 검색어 목록"""
    try:
        trending = [
            "React 개발자",
            "Python 백엔드",
            "프론트엔드 취업",
            "AI 개발자",
            "데이터 사이언티스트",
            "DevOps 엔지니어",
            "풀스택 개발자",
            "모바일 앱 개발"
        ]

        return {
            "success": True,
            "trending_searches": trending
        }

    except Exception as e:
        logger.error(f"인기 검색어 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"인기 검색어 조회 실패: {str(e)}")
