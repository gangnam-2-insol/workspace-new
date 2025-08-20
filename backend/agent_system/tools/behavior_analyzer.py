"""
사용자 행동 분석기

실제 사용자의 행동을 분석하여 어떤 툴 작업에 해당하는지 매핑합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class UserAction:
    """사용자 행동 정의"""
    action_type: str  # "click", "type", "scroll", "hover" 등
    target_element: str  # "button", "input", "link" 등
    content: str  # 실제 입력 내용이나 클릭한 요소
    timestamp: str
    page_url: str
    context: Dict[str, Any]  # 추가 컨텍스트 정보

@dataclass
class ToolMapping:
    """툴 매핑 결과"""
    tool_name: str
    confidence: float  # 0.0 ~ 1.0
    parameters: Dict[str, Any]
    reasoning: str  # 왜 이 툴로 매핑했는지 설명

class BehaviorAnalyzer:
    """사용자 행동 분석기"""
    
    def __init__(self):
        self.action_patterns = self._create_action_patterns()
        self.tool_keywords = self._create_tool_keywords()
    
    def _create_action_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """행동 패턴 정의"""
        return {
            "github_tools": [
                {
                    "pattern": r"GitHub|github|깃허브|깃헙",
                    "weight": 0.8,
                    "tool_mappings": {
                        "get_github_user_info": {"confidence": 0.7, "param_extractor": "extract_username"},
                        "get_github_repos": {"confidence": 0.6, "param_extractor": "extract_username"},
                        "search_github_repos": {"confidence": 0.5, "param_extractor": "extract_search_query"}
                    }
                },
                {
                    "pattern": r"사용자|user|프로필|profile",
                    "weight": 0.6,
                    "tool_mappings": {
                        "get_github_user_info": {"confidence": 0.8, "param_extractor": "extract_username"}
                    }
                },
                {
                    "pattern": r"레포|repo|repository|저장소",
                    "weight": 0.7,
                    "tool_mappings": {
                        "get_github_repos": {"confidence": 0.8, "param_extractor": "extract_username"},
                        "search_github_repos": {"confidence": 0.6, "param_extractor": "extract_search_query"}
                    }
                },
                {
                    "pattern": r"커밋|commit|변경|history",
                    "weight": 0.6,
                    "tool_mappings": {
                        "get_github_commits": {"confidence": 0.8, "param_extractor": "extract_repo_info"}
                    }
                }
            ],
            "mongodb_tools": [
                {
                    "pattern": r"데이터|data|DB|database|컬렉션|collection",
                    "weight": 0.7,
                    "tool_mappings": {
                        "find_mongodb_documents": {"confidence": 0.7, "param_extractor": "extract_collection_query"},
                        "count_mongodb_documents": {"confidence": 0.6, "param_extractor": "extract_collection"}
                    }
                },
                {
                    "pattern": r"사용자|user|회원|member",
                    "weight": 0.6,
                    "tool_mappings": {
                        "find_mongodb_documents": {"confidence": 0.8, "param_extractor": "extract_user_query"}
                    }
                }
            ],
            "search_tools": [
                {
                    "pattern": r"검색|search|찾기|find",
                    "weight": 0.8,
                    "tool_mappings": {
                        "web_search": {"confidence": 0.8, "param_extractor": "extract_search_query"},
                        "news_search": {"confidence": 0.6, "param_extractor": "extract_search_query"},
                        "image_search": {"confidence": 0.5, "param_extractor": "extract_search_query"}
                    }
                },
                {
                    "pattern": r"뉴스|news|기사|article",
                    "weight": 0.7,
                    "tool_mappings": {
                        "news_search": {"confidence": 0.9, "param_extractor": "extract_search_query"}
                    }
                },
                {
                    "pattern": r"이미지|image|사진|picture|로고|logo",
                    "weight": 0.7,
                    "tool_mappings": {
                        "image_search": {"confidence": 0.9, "param_extractor": "extract_search_query"}
                    }
                }
            ]
        }
    
    def _create_tool_keywords(self) -> Dict[str, List[str]]:
        """툴별 키워드 정의"""
        return {
            "get_github_user_info": ["사용자", "프로필", "정보", "user", "profile", "info"],
            "get_github_repos": ["레포", "저장소", "repository", "repo", "프로젝트"],
            "search_github_repos": ["검색", "찾기", "search", "find", "레포 검색"],
            "get_github_commits": ["커밋", "변경", "history", "commit", "로그"],
            "find_mongodb_documents": ["조회", "찾기", "검색", "find", "query"],
            "count_mongodb_documents": ["개수", "수", "count", "총", "전체"],
            "web_search": ["웹 검색", "검색", "search", "찾기"],
            "news_search": ["뉴스", "기사", "news", "article"],
            "image_search": ["이미지", "사진", "image", "picture"]
        }
    
    def analyze_user_action(self, action: UserAction) -> List[ToolMapping]:
        """사용자 행동을 분석하여 툴 매핑"""
        mappings = []
        
        # 1. 텍스트 내용 분석
        text_content = action.content.lower()
        
        # 2. 각 툴 카테고리별로 패턴 매칭
        for category, patterns in self.action_patterns.items():
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], text_content, re.IGNORECASE):
                    # 패턴이 매칭되면 해당 툴들에 매핑
                    for tool_name, tool_info in pattern_info["tool_mappings"].items():
                        # 파라미터 추출
                        params = self._extract_parameters(tool_name, text_content, action)
                        
                        # 신뢰도 계산
                        confidence = tool_info["confidence"] * pattern_info["weight"]
                        
                        # 추론 과정 설명
                        reasoning = f"'{text_content}'에서 '{pattern_info['pattern']}' 패턴이 감지되어 {tool_name} 툴로 매핑"
                        
                        mappings.append(ToolMapping(
                            tool_name=tool_name,
                            confidence=confidence,
                            parameters=params,
                            reasoning=reasoning
                        ))
        
        # 3. 키워드 기반 추가 매핑
        keyword_mappings = self._analyze_keywords(text_content)
        mappings.extend(keyword_mappings)
        
        # 4. 신뢰도 순으로 정렬
        mappings.sort(key=lambda x: x.confidence, reverse=True)
        
        return mappings
    
    def _extract_parameters(self, tool_name: str, text: str, action: UserAction) -> Dict[str, Any]:
        """툴별 파라미터 추출"""
        params = {}
        
        if tool_name == "get_github_user_info":
            # GitHub 사용자명 추출
            username_match = re.search(r'@?([a-zA-Z0-9_-]+)', text)
            if username_match:
                params["username"] = username_match.group(1)
        
        elif tool_name == "get_github_repos":
            # GitHub 사용자명 추출
            username_match = re.search(r'@?([a-zA-Z0-9_-]+)', text)
            if username_match:
                params["username"] = username_match.group(1)
                # 레포 개수 제한 추출
                limit_match = re.search(r'(\d+)개?', text)
                if limit_match:
                    params["limit"] = int(limit_match.group(1))
        
        elif tool_name == "search_github_repos":
            # 검색어 추출
            search_match = re.search(r'["\']([^"\']+)["\']', text)
            if search_match:
                params["query"] = search_match.group(1)
            else:
                # 따옴표가 없으면 전체 텍스트를 검색어로
                params["query"] = text.strip()
        
        elif tool_name == "get_github_commits":
            # 레포 정보 추출 (username/repo 형식)
            repo_match = re.search(r'([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)', text)
            if repo_match:
                params["username"] = repo_match.group(1)
                params["repo_name"] = repo_match.group(2)
        
        elif tool_name in ["find_mongodb_documents", "count_mongodb_documents"]:
            # 컬렉션명 추출
            collection_match = re.search(r'(users?|posts?|comments?)', text, re.IGNORECASE)
            if collection_match:
                params["collection"] = collection_match.group(1)
        
        elif tool_name in ["web_search", "news_search", "image_search"]:
            # 검색어 추출
            search_match = re.search(r'["\']([^"\']+)["\']', text)
            if search_match:
                params["query"] = search_match.group(1)
            else:
                params["query"] = text.strip()
        
        return params
    
    def _analyze_keywords(self, text: str) -> List[ToolMapping]:
        """키워드 기반 툴 매핑"""
        mappings = []
        
        for tool_name, keywords in self.tool_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    # 키워드가 포함된 경우 해당 툴로 매핑
                    params = self._extract_parameters(tool_name, text, UserAction("", "", text, "", "", {}))
                    
                    mappings.append(ToolMapping(
                        tool_name=tool_name,
                        confidence=0.5,  # 키워드 매칭은 낮은 신뢰도
                        parameters=params,
                        reasoning=f"키워드 '{keyword}'가 감지되어 {tool_name} 툴로 매핑"
                    ))
                    break  # 한 툴에 대해 하나의 키워드만 매칭
        
        return mappings
    
    def get_action_summary(self, actions: List[UserAction]) -> Dict[str, Any]:
        """사용자 행동 요약"""
        summary = {
            "total_actions": len(actions),
            "action_types": {},
            "tool_mappings": {},
            "most_likely_tool": None,
            "confidence_score": 0.0
        }
        
        # 액션 타입별 통계
        for action in actions:
            action_type = action.action_type
            summary["action_types"][action_type] = summary["action_types"].get(action_type, 0) + 1
        
        # 툴 매핑 통계
        all_mappings = []
        for action in actions:
            mappings = self.analyze_user_action(action)
            all_mappings.extend(mappings)
        
        # 툴별 신뢰도 집계
        tool_scores = {}
        for mapping in all_mappings:
            if mapping.tool_name not in tool_scores:
                tool_scores[mapping.tool_name] = []
            tool_scores[mapping.tool_name].append(mapping.confidence)
        
        # 평균 신뢰도 계산
        for tool_name, scores in tool_scores.items():
            avg_confidence = sum(scores) / len(scores)
            summary["tool_mappings"][tool_name] = {
                "count": len(scores),
                "avg_confidence": avg_confidence,
                "max_confidence": max(scores)
            }
        
        # 가장 가능성 높은 툴 찾기
        if tool_scores:
            best_tool = max(tool_scores.keys(), key=lambda x: max(tool_scores[x]))
            summary["most_likely_tool"] = best_tool
            summary["confidence_score"] = max(tool_scores[best_tool])
        
        return summary

# 전역 분석기 인스턴스
behavior_analyzer = BehaviorAnalyzer()
