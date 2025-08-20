"""
GitHub API Tool

GitHub API를 통한 사용자 정보, 저장소 정보 등을 조회하는 툴
"""

import os
import requests
from typing import Dict, Any, List
from .base_tool import BaseTool

class GitHubTool(BaseTool):
    """GitHub API 연동 툴"""
    
    def __init__(self):
        super().__init__("github_tool", "GitHub API 연동 툴")
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def execute(self, action: str = "get_user_info", **kwargs) -> Dict[str, Any]:
        """GitHub API 실행"""
        print(f"🔍 [DEBUG] GitHub 툴 실행 시작 - 액션: {action}, 파라미터: {kwargs}")
        
        try:
            if action == "get_user_info":
                username = kwargs.get("username")
                print(f"🔍 [DEBUG] 사용자 정보 조회 - 사용자명: {username}")
                result = self._get_user_info(username)
                print(f"🔍 [DEBUG] 사용자 정보 조회 결과: {result}")
                return result
            elif action == "get_repos":
                username = kwargs.get("username")
                print(f"🔍 [DEBUG] 레포지토리 조회 - 사용자명: {username}")
                result = self._get_repos(username)
                print(f"🔍 [DEBUG] 레포지토리 조회 결과: {result}")
                return result
            elif action == "get_repo_details":
                username = kwargs.get("username")
                repo = kwargs.get("repo")
                print(f"🔍 [DEBUG] 레포 상세 조회 - 사용자명: {username}, 레포: {repo}")
                result = self._get_repo_details(username, repo)
                print(f"🔍 [DEBUG] 레포 상세 조회 결과: {result}")
                return result
            elif action == "get_commits":
                username = kwargs.get("username")
                repo = kwargs.get("repo")
                print(f"🔍 [DEBUG] 커밋 조회 - 사용자명: {username}, 레포: {repo}")
                result = self._get_commits(username, repo)
                print(f"🔍 [DEBUG] 커밋 조회 결과: {result}")
                return result
            elif action == "search_repos":
                query = kwargs.get("query")
                print(f"🔍 [DEBUG] 레포 검색 - 쿼리: {query}")
                result = self._search_repos(query)
                print(f"🔍 [DEBUG] 레포 검색 결과: {result}")
                return result
            else:
                print(f"🔍 [DEBUG] 지원하지 않는 액션: {action}")
                return self.create_response(False, error=f"Unknown action: {action}")
                
        except Exception as e:
            print(f"🔍 [DEBUG] GitHub 툴 예외 발생: {str(e)}")
            return self.create_response(False, error=str(e))
    
    def _get_user_info(self, username: str) -> Dict[str, Any]:
        """사용자 정보 조회"""
        if not username:
            return self.create_response(False, error="Username is required")
        
        url = f"{self.base_url}/users/{username}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return self.create_response(True, data={
                "username": data["login"],
                "name": data.get("name"),
                "bio": data.get("bio"),
                "public_repos": data["public_repos"],
                "followers": data["followers"],
                "following": data["following"],
                "created_at": data["created_at"]
            })
        else:
            return self.create_response(False, error=f"Failed to get user info: {response.status_code}")
    
    def _get_repos(self, username: str) -> Dict[str, Any]:
        """사용자의 저장소 목록 조회"""
        if not username:
            return self.create_response(False, error="Username is required")
        
        url = f"{self.base_url}/users/{username}/repos"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            repos = response.json()
            return self.create_response(True, data={
                "username": username,
                "repos": [{
                    "name": repo["name"],
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "url": repo["html_url"]
                } for repo in repos]
            })
        else:
            return self.create_response(False, error=f"Failed to get repos: {response.status_code}")
    
    def _get_repo_details(self, username: str, repo: str) -> Dict[str, Any]:
        """저장소 상세 정보 조회"""
        if not username or not repo:
            return self.create_response(False, error="Username and repo are required")
        
        url = f"{self.base_url}/repos/{username}/{repo}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return self.create_response(True, data={
                "name": data["name"],
                "description": data.get("description"),
                "language": data.get("language"),
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "issues": data["open_issues_count"],
                "url": data["html_url"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"]
            })
        else:
            return self.create_response(False, error=f"Failed to get repo details: {response.status_code}")
    
    def _get_commits(self, username: str, repo: str) -> Dict[str, Any]:
        """저장소 커밋 목록 조회"""
        if not username or not repo:
            return self.create_response(False, error="Username and repo are required")
        
        url = f"{self.base_url}/repos/{username}/{repo}/commits"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            commits = response.json()
            return self.create_response(True, data={
                "username": username,
                "repo": repo,
                "commits": [{
                    "sha": commit["sha"][:7],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"],
                    "date": commit["commit"]["author"]["date"]
                } for commit in commits[:10]]  # 최근 10개만
            })
        else:
            return self.create_response(False, error=f"Failed to get commits: {response.status_code}")
    
    def _search_repos(self, query: str) -> Dict[str, Any]:
        """저장소 검색"""
        if not query:
            return self.create_response(False, error="Query is required")
        
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc"}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return self.create_response(True, data={
                "query": query,
                "total_count": data["total_count"],
                "repos": [{
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "url": repo["html_url"]
                } for repo in data["items"][:10]]  # 상위 10개만
            })
        else:
            return self.create_response(False, error=f"Failed to search repos: {response.status_code}")

