"""
메타데이터 정확성 검증을 위한 시연 시나리오

실제 사용자가 할 수 있는 다양한 시나리오를 통해 메타데이터의 정확성을 검증합니다.
"""

from typing import Dict, Any, List, Tuple
from .metadata_validator import log_tool_execution
import time
import random

class DemoScenarioRunner:
    """시연 시나리오 실행기"""
    
    def __init__(self):
        self.scenarios = self._create_scenarios()
    
    def _create_scenarios(self) -> Dict[str, List[Dict[str, Any]]]:
        """시연 시나리오 생성"""
        return {
            "github_tools": [
                # 성공 시나리오
                {
                    "name": "유효한 GitHub 사용자 정보 조회",
                    "tool": "get_github_user_info",
                    "user_input": "kyungho222의 GitHub 정보를 보여줘",
                    "parameters": {"username": "kyungho222"},
                    "expected_success": True,
                    "description": "존재하는 GitHub 사용자의 정보 조회"
                },
                {
                    "name": "레포지토리 목록 조회 (제한 포함)",
                    "tool": "get_github_repos",
                    "user_input": "kyungho222의 최근 5개 레포지토리 보여줘",
                    "parameters": {"username": "kyungho222", "limit": 5},
                    "expected_success": True,
                    "description": "레포지토리 수 제한과 함께 조회"
                },
                {
                    "name": "GitHub 레포지토리 검색",
                    "tool": "search_github_repos",
                    "user_input": "Python FastAPI 프로젝트 찾기",
                    "parameters": {"query": "Python FastAPI", "language": "python"},
                    "expected_success": True,
                    "description": "언어 필터와 함께 레포지토리 검색"
                },
                {
                    "name": "커밋 내역 조회",
                    "tool": "get_github_commits",
                    "user_input": "kyungho222/workspace-new의 최근 커밋 보여줘",
                    "parameters": {"username": "kyungho222", "repo_name": "workspace-new"},
                    "expected_success": True,
                    "description": "특정 레포지토리의 커밋 내역 조회"
                },
                
                # 에러 시나리오
                {
                    "name": "존재하지 않는 사용자 조회",
                    "tool": "get_github_user_info",
                    "user_input": "존재하지않는사용자123의 GitHub 정보를 보여줘",
                    "parameters": {"username": "존재하지않는사용자123"},
                    "expected_success": False,
                    "expected_error": "NOT_FOUND",
                    "description": "존재하지 않는 GitHub 사용자 조회"
                },
                {
                    "name": "잘못된 레포지토리명",
                    "tool": "get_github_commits",
                    "user_input": "kyungho222/존재하지않는레포의 커밋 보여줘",
                    "parameters": {"username": "kyungho222", "repo_name": "존재하지않는레포"},
                    "expected_success": False,
                    "expected_error": "NOT_FOUND",
                    "description": "존재하지 않는 레포지토리 조회"
                },
                {
                    "name": "Rate Limit 초과 시뮬레이션",
                    "tool": "get_github_user_info",
                    "user_input": "Rate limit 테스트",
                    "parameters": {"username": "test_user"},
                    "expected_success": False,
                    "expected_error": "RATE_LIMIT",
                    "description": "API 호출 제한 초과 상황"
                }
            ],
            
            "mongodb_tools": [
                # 성공 시나리오
                {
                    "name": "사용자 컬렉션 조회",
                    "tool": "find_mongodb_documents",
                    "user_input": "users 컬렉션에서 모든 사용자 정보 조회",
                    "parameters": {"collection": "users"},
                    "expected_success": True,
                    "description": "기본 컬렉션 조회"
                },
                {
                    "name": "조건부 문서 조회",
                    "tool": "find_mongodb_documents",
                    "user_input": "나이가 25세 이상인 사용자 찾기",
                    "parameters": {
                        "collection": "users",
                        "query": {"age": {"$gte": 25}},
                        "limit": 10
                    },
                    "expected_success": True,
                    "description": "MongoDB 쿼리 조건과 함께 조회"
                },
                {
                    "name": "문서 개수 세기",
                    "tool": "count_mongodb_documents",
                    "user_input": "전체 사용자 수 세기",
                    "parameters": {"collection": "users"},
                    "expected_success": True,
                    "description": "컬렉션의 전체 문서 개수 조회"
                },
                
                # 에러 시나리오
                {
                    "name": "존재하지 않는 컬렉션",
                    "tool": "find_mongodb_documents",
                    "user_input": "존재하지않는컬렉션 조회",
                    "parameters": {"collection": "존재하지않는컬렉션"},
                    "expected_success": False,
                    "expected_error": "COLLECTION_NOT_FOUND",
                    "description": "존재하지 않는 컬렉션 조회"
                },
                {
                    "name": "잘못된 쿼리 형식",
                    "tool": "find_mongodb_documents",
                    "user_input": "잘못된 쿼리로 조회",
                    "parameters": {
                        "collection": "users",
                        "query": "잘못된 쿼리 문자열"
                    },
                    "expected_success": False,
                    "expected_error": "INVALID_QUERY",
                    "description": "유효하지 않은 MongoDB 쿼리"
                },
                {
                    "name": "연결 오류 시뮬레이션",
                    "tool": "find_mongodb_documents",
                    "user_input": "DB 연결 테스트",
                    "parameters": {"collection": "users"},
                    "expected_success": False,
                    "expected_error": "CONNECTION_ERROR",
                    "description": "MongoDB 연결 실패 상황"
                }
            ],
            
            "search_tools": [
                # 성공 시나리오
                {
                    "name": "웹 검색",
                    "tool": "web_search",
                    "user_input": "Python FastAPI 튜토리얼 검색",
                    "parameters": {"query": "Python FastAPI 튜토리얼"},
                    "expected_success": True,
                    "description": "일반적인 웹 검색"
                },
                {
                    "name": "뉴스 검색",
                    "tool": "news_search",
                    "user_input": "AI 기술 관련 뉴스 검색",
                    "parameters": {"query": "AI 기술", "num_results": 5},
                    "expected_success": True,
                    "description": "뉴스 기사 검색"
                },
                {
                    "name": "이미지 검색",
                    "tool": "image_search",
                    "user_input": "회사 로고 이미지 검색",
                    "parameters": {"query": "회사 로고"},
                    "expected_success": True,
                    "description": "이미지 검색"
                },
                
                # 에러 시나리오
                {
                    "name": "API 키 누락",
                    "tool": "web_search",
                    "user_input": "API 키 없이 검색",
                    "parameters": {"query": "테스트 검색"},
                    "expected_success": False,
                    "expected_error": "API_KEY_MISSING",
                    "description": "Google API 키가 설정되지 않은 상황"
                },
                {
                    "name": "할당량 초과",
                    "tool": "news_search",
                    "user_input": "할당량 초과 테스트",
                    "parameters": {"query": "테스트 뉴스"},
                    "expected_success": False,
                    "expected_error": "QUOTA_EXCEEDED",
                    "description": "API 할당량 초과 상황"
                },
                {
                    "name": "검색 결과 없음",
                    "tool": "web_search",
                    "user_input": "매우 특이한 검색어",
                    "parameters": {"query": "매우특이하고존재하지않을검색어12345"},
                    "expected_success": False,
                    "expected_error": "NO_RESULTS",
                    "description": "검색 결과가 없는 상황"
                }
            ]
        }
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """모든 시나리오 실행"""
        results = {
            "total_scenarios": 0,
            "successful_scenarios": 0,
            "failed_scenarios": 0,
            "tool_results": {}
        }
        
        for category, scenarios in self.scenarios.items():
            category_results = {
                "total": len(scenarios),
                "successful": 0,
                "failed": 0,
                "scenarios": []
            }
            
            for scenario in scenarios:
                result = self._run_single_scenario(scenario)
                category_results["scenarios"].append(result)
                
                if result["actual_success"]:
                    category_results["successful"] += 1
                else:
                    category_results["failed"] += 1
                
                results["total_scenarios"] += 1
                if result["actual_success"]:
                    results["successful_scenarios"] += 1
                else:
                    results["failed_scenarios"] += 1
            
            results["tool_results"][category] = category_results
        
        return results
    
    def run_category_scenarios(self, category: str) -> Dict[str, Any]:
        """특정 카테고리의 시나리오만 실행"""
        if category not in self.scenarios:
            return {"error": f"카테고리 '{category}'를 찾을 수 없습니다."}
        
        scenarios = self.scenarios[category]
        results = {
            "category": category,
            "total": len(scenarios),
            "successful": 0,
            "failed": 0,
            "scenarios": []
        }
        
        for scenario in scenarios:
            result = self._run_single_scenario(scenario)
            results["scenarios"].append(result)
            
            if result["actual_success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def _run_single_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """단일 시나리오 실행"""
        tool_name = scenario["tool"]
        user_input = scenario["user_input"]
        parameters = scenario["parameters"]
        expected_success = scenario["expected_success"]
        
        # 시뮬레이션된 실행 시간
        execution_time = random.uniform(0.1, 2.0)
        
        # 시뮬레이션된 결과 생성
        if expected_success:
            # 성공 시나리오
            result = self._generate_success_result(tool_name, parameters)
            success = True
            error_message = None
            llm_confidence = random.uniform(0.8, 1.0)  # 높은 신뢰도
        else:
            # 실패 시나리오
            expected_error = scenario.get("expected_error", "UNKNOWN_ERROR")
            result = self._generate_error_result(tool_name, expected_error)
            success = False
            error_message = self._get_error_message(expected_error)
            llm_confidence = random.uniform(0.3, 0.7)  # 낮은 신뢰도
        
        # 로그 기록
        log_tool_execution(
            tool_name=tool_name,
            user_input=user_input,
            parameters=parameters,
            result=result,
            success=success,
            error_message=error_message,
            execution_time=execution_time,
            llm_confidence=llm_confidence
        )
        
        return {
            "scenario_name": scenario["name"],
            "tool": tool_name,
            "user_input": user_input,
            "parameters": parameters,
            "expected_success": expected_success,
            "actual_success": success,
            "result": result,
            "execution_time": execution_time,
            "llm_confidence": llm_confidence,
            "description": scenario["description"]
        }
    
    def _generate_success_result(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """성공 결과 생성"""
        if tool_name == "get_github_user_info":
            return {
                "username": parameters.get("username", "test_user"),
                "name": "테스트 사용자",
                "bio": "테스트용 사용자입니다.",
                "public_repos": 15,
                "followers": 42,
                "following": 23,
                "created_at": "2020-01-01T00:00:00Z",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        elif tool_name == "get_github_repos":
            return {
                "username": parameters.get("username", "test_user"),
                "total_repos": 3,
                "repos": [
                    {
                        "name": "test-repo-1",
                        "description": "테스트 레포지토리 1",
                        "language": "Python",
                        "stars": 10,
                        "forks": 5,
                        "html_url": "https://github.com/test_user/test-repo-1"
                    }
                ]
            }
        elif tool_name == "find_mongodb_documents":
            return {
                "collection": parameters.get("collection", "users"),
                "total_documents": 2,
                "documents": [
                    {"_id": "1", "name": "사용자1", "age": 25},
                    {"_id": "2", "name": "사용자2", "age": 30}
                ]
            }
        elif tool_name == "web_search":
            return {
                "query": parameters.get("query", "테스트 검색"),
                "total_results": 5,
                "results": [
                    {
                        "title": "테스트 검색 결과 1",
                        "snippet": "테스트 검색 결과의 요약입니다.",
                        "url": "https://example.com/result1"
                    }
                ]
            }
        else:
            return {"status": "success", "data": "테스트 결과"}
    
    def _generate_error_result(self, tool_name: str, error_type: str) -> Dict[str, Any]:
        """에러 결과 생성"""
        return {
            "status": "error",
            "error_type": error_type,
            "message": self._get_error_message(error_type)
        }
    
    def _get_error_message(self, error_type: str) -> str:
        """에러 메시지 생성"""
        error_messages = {
            "NOT_FOUND": "요청한 리소스를 찾을 수 없습니다.",
            "RATE_LIMIT": "API 호출 제한을 초과했습니다.",
            "COLLECTION_NOT_FOUND": "요청한 컬렉션을 찾을 수 없습니다.",
            "INVALID_QUERY": "잘못된 쿼리 형식입니다.",
            "CONNECTION_ERROR": "데이터베이스 연결에 실패했습니다.",
            "API_KEY_MISSING": "API 키가 설정되지 않았습니다.",
            "QUOTA_EXCEEDED": "API 할당량을 초과했습니다.",
            "NO_RESULTS": "검색 결과가 없습니다.",
            "UNKNOWN_ERROR": "알 수 없는 오류가 발생했습니다."
        }
        return error_messages.get(error_type, "알 수 없는 오류")
    
    def generate_custom_scenario(self, 
                               tool_name: str, 
                               user_input: str, 
                               parameters: Dict[str, Any],
                               expected_success: bool = True,
                               expected_error: str = None) -> Dict[str, Any]:
        """사용자 정의 시나리오 생성"""
        scenario = {
            "name": f"사용자 정의 시나리오 - {tool_name}",
            "tool": tool_name,
            "user_input": user_input,
            "parameters": parameters,
            "expected_success": expected_success,
            "description": "사용자가 정의한 시나리오"
        }
        
        if expected_error:
            scenario["expected_error"] = expected_error
        
        return self._run_single_scenario(scenario)

# 전역 시나리오 실행기 인스턴스
demo_runner = DemoScenarioRunner()

def run_demo_scenarios(category: str = None) -> Dict[str, Any]:
    """시연 시나리오 실행"""
    if category:
        return demo_runner.run_category_scenarios(category)
    else:
        return demo_runner.run_all_scenarios()

def run_custom_scenario(tool_name: str, 
                       user_input: str, 
                       parameters: Dict[str, Any],
                       expected_success: bool = True,
                       expected_error: str = None) -> Dict[str, Any]:
    """사용자 정의 시나리오 실행"""
    return demo_runner.generate_custom_scenario(
        tool_name, user_input, parameters, expected_success, expected_error
    )
