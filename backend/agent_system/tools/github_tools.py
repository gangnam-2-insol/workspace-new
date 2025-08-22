"""
GitHub 툴 모듈

LLM 친화적인 GitHub API 툴들을 정의합니다.
명확한 메타데이터와 예시를 포함하여 LLM이 언제 어떻게 사용해야 하는지 이해할 수 있도록 합니다.
"""

import os
import requests
from typing import Dict, Any, List
from . import register_tool

# GitHub API 설정
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def _get_github_headers() -> Dict[str, str]:
    """GitHub API 요청 헤더 생성"""
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

@register_tool(
    name="get_github_user_info",
    description="GitHub 사용자의 기본 정보를 조회합니다. 사용자명을 입력하면 프로필 정보, 팔로워 수, 공개 레포지토리 수 등을 반환합니다.",
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "조회할 GitHub 사용자명"
            }
        },
        "required": ["username"]
    },
    examples=[
        "kyungho222의 GitHub 정보를 보여줘",
        "사용자 kyungho222의 프로필 정보 조회",
        "GitHub 사용자 정보: kyungho222"
    ],
    category="github"
)
def get_github_user_info(username: str) -> Dict[str, Any]:
    """GitHub 사용자 정보 조회"""
    try:
        url = f"{GITHUB_API_BASE}/users/{username}"
        response = requests.get(url, headers=_get_github_headers())
        
        if response.status_code != 200:
            return {
                "error": f"사용자를 찾을 수 없습니다: {username}",
                "status_code": response.status_code
            }
        
        user_data = response.json()
        return {
            "username": user_data["login"],
            "name": user_data.get("name", ""),
            "bio": user_data.get("bio", ""),
            "public_repos": user_data["public_repos"],
            "followers": user_data["followers"],
            "following": user_data["following"],
            "created_at": user_data["created_at"],
            "avatar_url": user_data["avatar_url"],
            "location": user_data.get("location", ""),
            "company": user_data.get("company", "")
        }
    except Exception as e:
        return {"error": f"GitHub API 호출 중 오류 발생: {str(e)}"}

@register_tool(
    name="get_github_repos",
    description="GitHub 사용자의 레포지토리 목록을 조회합니다. 사용자명을 입력하면 해당 사용자의 공개 레포지토리들을 반환합니다.",
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "조회할 GitHub 사용자명"
            },
            "limit": {
                "type": "integer",
                "description": "반환할 레포지토리 수 (기본값: 10)",
                "default": 10
            }
        },
        "required": ["username"]
    },
    examples=[
        "kyungho222의 레포지토리 목록 보여줘",
        "사용자 kyungho222의 GitHub 레포들 조회",
        "GitHub 레포지토리: kyungho222"
    ],
    category="github"
)
def get_github_repos(username: str, limit: int = 10) -> Dict[str, Any]:
    """GitHub 사용자의 레포지토리 목록 조회"""
    try:
        url = f"{GITHUB_API_BASE}/users/{username}/repos"
        params = {
            "sort": "updated",
            "per_page": min(limit, 100)  # GitHub API 최대 100개
        }
        
        response = requests.get(url, headers=_get_github_headers(), params=params)
        
        if response.status_code != 200:
            return {
                "error": f"레포지토리를 찾을 수 없습니다: {username}",
                "status_code": response.status_code
            }
        
        repos_data = response.json()
        repos = []
        
        for repo in repos_data[:limit]:
            repo_info = {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "language": repo.get("language", ""),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "updated_at": repo["updated_at"],
                "html_url": repo["html_url"]
            }
            repos.append(repo_info)
        
        return {
            "username": username,
            "total_repos": len(repos),
            "repos": repos
        }
    except Exception as e:
        return {"error": f"GitHub API 호출 중 오류 발생: {str(e)}"}

@register_tool(
    name="search_github_repos",
    description="GitHub에서 레포지토리를 검색합니다. 검색어를 입력하면 관련된 레포지토리들을 반환합니다.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "검색할 키워드나 레포지토리명"
            },
            "language": {
                "type": "string",
                "description": "프로그래밍 언어 필터 (예: python, javascript, java)"
            },
            "limit": {
                "type": "integer",
                "description": "반환할 결과 수 (기본값: 10)",
                "default": 10
            }
        },
        "required": ["query"]
    },
    examples=[
        "Python FastAPI 레포지토리 검색",
        "JavaScript React 프로젝트 찾기",
        "GitHub에서 'machine learning' 검색"
    ],
    category="github"
)
def search_github_repos(query: str, language: str = None, limit: int = 10) -> Dict[str, Any]:
    """GitHub 레포지토리 검색"""
    try:
        url = f"{GITHUB_API_BASE}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 30)  # GitHub Search API 최대 30개
        }
        
        if language:
            params["q"] += f" language:{language}"
        
        response = requests.get(url, headers=_get_github_headers(), params=params)
        
        if response.status_code != 200:
            return {
                "error": f"검색 중 오류가 발생했습니다: {query}",
                "status_code": response.status_code
            }
        
        search_data = response.json()
        repos = []
        
        for repo in search_data.get("items", [])[:limit]:
            repo_info = {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "language": repo.get("language", ""),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "owner": repo["owner"]["login"],
                "html_url": repo["html_url"],
                "created_at": repo["created_at"]
            }
            repos.append(repo_info)
        
        return {
            "query": query,
            "total_count": search_data.get("total_count", 0),
            "repos": repos
        }
    except Exception as e:
        return {"error": f"GitHub 검색 API 호출 중 오류 발생: {str(e)}"}

@register_tool(
    name="get_github_commits",
    description="GitHub 레포지토리의 최근 커밋 내역을 조회합니다. 사용자명과 레포지토리명을 입력하면 최근 커밋들을 반환합니다.",
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "레포지토리 소유자 사용자명"
            },
            "repo_name": {
                "type": "string",
                "description": "레포지토리명"
            },
            "limit": {
                "type": "integer",
                "description": "반환할 커밋 수 (기본값: 10)",
                "default": 10
            }
        },
        "required": ["username", "repo_name"]
    },
    examples=[
        "kyungho222/workspace-new의 최근 커밋 보여줘",
        "레포지토리 커밋 히스토리: kyungho222/workspace-new",
        "GitHub 커밋: kyungho222/workspace-new"
    ],
    category="github"
)
def get_github_commits(username: str, repo_name: str, limit: int = 10) -> Dict[str, Any]:
    """GitHub 레포지토리의 커밋 내역 조회"""
    try:
        url = f"{GITHUB_API_BASE}/repos/{username}/{repo_name}/commits"
        params = {
            "per_page": min(limit, 100)
        }
        
        response = requests.get(url, headers=_get_github_headers(), params=params)
        
        if response.status_code != 200:
            return {
                "error": f"커밋을 찾을 수 없습니다: {username}/{repo_name}",
                "status_code": response.status_code
            }
        
        commits_data = response.json()
        commits = []
        
        for commit in commits_data[:limit]:
            commit_info = {
                "sha": commit["sha"][:7],  # 짧은 SHA
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "html_url": commit["html_url"]
            }
            commits.append(commit_info)
        
        return {
            "repository": f"{username}/{repo_name}",
            "total_commits": len(commits),
            "commits": commits
        }
    except Exception as e:
        return {"error": f"GitHub API 호출 중 오류 발생: {str(e)}"}
