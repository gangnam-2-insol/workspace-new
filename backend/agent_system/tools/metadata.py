"""
툴 메타데이터 정의

LLM 친화적인 툴 메타데이터를 JSON Schema 형태로 정의합니다.
가이드에 따라 구체적이고 명확한 설명을 포함합니다.
"""

from typing import Dict, Any, List

# GitHub 툴 메타데이터
GITHUB_TOOLS_METADATA = [
    {
        "name": "get_github_user_info",
        "description": "GitHub 사용자의 기본 정보를 조회하는 툴입니다. 사용자가 특정 GitHub 사용자명을 언급하거나 프로필 정보를 요청할 때 사용합니다. 입력으로 사용자명을 받아 프로필 정보, 팔로워 수, 공개 레포지토리 수 등을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "조회할 GitHub 사용자명 (예: kyungho222, microsoft, openai)"
                }
            },
            "required": ["username"]
        },
        "output": {
            "type": "object",
            "description": "GitHub 사용자 정보 객체",
            "properties": {
                "username": {"type": "string", "description": "GitHub 사용자명"},
                "name": {"type": "string", "description": "실명"},
                "bio": {"type": "string", "description": "자기소개"},
                "public_repos": {"type": "integer", "description": "공개 레포지토리 수"},
                "followers": {"type": "integer", "description": "팔로워 수"},
                "following": {"type": "integer", "description": "팔로잉 수"},
                "created_at": {"type": "string", "description": "계정 생성일"},
                "avatar_url": {"type": "string", "description": "프로필 이미지 URL"}
            }
        },
        "errors": [
            {
                "code": "USER_NOT_FOUND",
                "description": "요청한 GitHub 사용자가 존재하지 않습니다. 사용자명을 확인해주세요."
            },
            {
                "code": "RATE_LIMIT_EXCEEDED",
                "description": "GitHub API 호출 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
            },
            {
                "code": "API_UNAVAILABLE",
                "description": "GitHub API 서비스가 일시적으로 사용할 수 없습니다."
            },
            {
                "code": "INVALID_USERNAME",
                "description": "유효하지 않은 사용자명입니다. 특수문자나 공백이 포함되어 있지 않은지 확인해주세요."
            }
        ],
        "examples": [
            "kyungho222의 GitHub 정보를 보여줘",
            "사용자 kyungho222의 프로필 정보 조회",
            "GitHub 사용자 정보: kyungho222"
        ],
        "category": "github",
        "constraints": {
            "rate_limit": "GitHub API: 인증 없이 시간당 60회, 인증 시 시간당 5000회",
            "requires_auth": False,
            "error_codes": {
                "404": "사용자를 찾을 수 없습니다",
                "403": "API 접근이 제한되었습니다 (rate limit 초과 가능)",
                "500": "GitHub 서버 오류"
            }
        }
    },
    {
        "name": "get_github_repos",
        "description": "GitHub 사용자의 레포지토리 목록을 조회하는 툴입니다. 사용자가 특정 사용자의 프로젝트나 레포지토리를 요청할 때 사용합니다. 입력으로 사용자명과 선택적으로 레포지토리 수를 받아 해당 사용자의 공개 레포지토리들을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "조회할 GitHub 사용자명"
                },
                "limit": {
                    "type": "integer",
                    "description": "반환할 레포지토리 수 (기본값: 10, 최대: 100)",
                    "default": 10
                }
            },
            "required": ["username"]
        },
        "output": {
            "type": "object",
            "description": "레포지토리 목록 정보",
            "properties": {
                "username": {"type": "string", "description": "조회한 사용자명"},
                "total_repos": {"type": "integer", "description": "반환된 레포지토리 수"},
                "repos": {
                    "type": "array",
                    "description": "레포지토리 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "레포지토리명"},
                            "description": {"type": "string", "description": "설명"},
                            "language": {"type": "string", "description": "주요 언어"},
                            "stars": {"type": "integer", "description": "스타 수"},
                            "forks": {"type": "integer", "description": "포크 수"},
                            "html_url": {"type": "string", "description": "레포지토리 URL"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "USER_NOT_FOUND",
                "description": "요청한 GitHub 사용자가 존재하지 않습니다."
            },
            {
                "code": "RATE_LIMIT_EXCEEDED",
                "description": "GitHub API 호출 제한을 초과했습니다."
            },
            {
                "code": "INVALID_LIMIT",
                "description": "레포지토리 수 제한이 유효하지 않습니다. 1-100 사이의 값을 입력해주세요."
            },
            {
                "code": "NO_PUBLIC_REPOS",
                "description": "해당 사용자의 공개 레포지토리가 없습니다."
            }
        ],
        "examples": [
            "kyungho222의 레포지토리 목록 보여줘",
            "사용자 kyungho222의 GitHub 레포들 조회",
            "GitHub 레포지토리: kyungho222"
        ],
        "category": "github",
        "constraints": {
            "rate_limit": "GitHub API: 인증 없이 시간당 60회, 인증 시 시간당 5000회",
            "requires_auth": False,
            "max_limit": 100,
            "error_codes": {
                "404": "사용자를 찾을 수 없습니다",
                "403": "API 접근이 제한되었습니다",
                "500": "GitHub 서버 오류"
            }
        }
    },
    {
        "name": "search_github_repos",
        "description": "GitHub에서 레포지토리를 검색하는 툴입니다. 사용자가 특정 기술이나 프로젝트 관련 레포지토리를 찾고 싶을 때 사용합니다. 입력으로 검색어와 선택적으로 프로그래밍 언어 필터를 받아 관련된 레포지토리들을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 키워드나 레포지토리명 (예: 'Python FastAPI', 'React Todo App')"
                },
                "language": {
                    "type": "string",
                    "description": "프로그래밍 언어 필터 (예: python, javascript, java, c++)"
                },
                "limit": {
                    "type": "integer",
                    "description": "반환할 결과 수 (기본값: 10, 최대: 30)",
                    "default": 10
                }
            },
            "required": ["query"]
        },
        "output": {
            "type": "object",
            "description": "검색 결과 정보",
            "properties": {
                "query": {"type": "string", "description": "검색 쿼리"},
                "total_count": {"type": "integer", "description": "전체 검색 결과 수"},
                "repos": {
                    "type": "array",
                    "description": "검색된 레포지토리 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "레포지토리명"},
                            "full_name": {"type": "string", "description": "전체 이름 (owner/repo)"},
                            "description": {"type": "string", "description": "설명"},
                            "language": {"type": "string", "description": "주요 언어"},
                            "stars": {"type": "integer", "description": "스타 수"},
                            "forks": {"type": "integer", "description": "포크 수"},
                            "owner": {"type": "string", "description": "소유자명"},
                            "html_url": {"type": "string", "description": "레포지토리 URL"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "INVALID_SEARCH_QUERY",
                "description": "검색 쿼리가 유효하지 않습니다. 특수문자나 너무 짧은 검색어를 피해주세요."
            },
            {
                "code": "RATE_LIMIT_EXCEEDED",
                "description": "GitHub Search API 호출 제한을 초과했습니다. 인증된 요청으로 제한이 늘어납니다."
            },
            {
                "code": "NO_SEARCH_RESULTS",
                "description": "검색 조건에 맞는 레포지토리가 없습니다. 검색어를 변경해보세요."
            },
            {
                "code": "INVALID_LANGUAGE_FILTER",
                "description": "지원하지 않는 프로그래밍 언어 필터입니다."
            }
        ],
        "examples": [
            "Python FastAPI 레포지토리 검색",
            "JavaScript React 프로젝트 찾기",
            "GitHub에서 'machine learning' 검색"
        ],
        "category": "github",
        "constraints": {
            "rate_limit": "GitHub Search API: 인증 없이 시간당 10회, 인증 시 시간당 30회",
            "requires_auth": False,
            "max_limit": 30,
            "error_codes": {
                "422": "검색 쿼리가 유효하지 않습니다",
                "403": "API 접근이 제한되었습니다",
                "500": "GitHub 서버 오류"
            }
        }
    },
    {
        "name": "get_github_commits",
        "description": "GitHub 레포지토리의 최근 커밋 내역을 조회하는 툴입니다. 사용자가 특정 프로젝트의 개발 활동이나 최근 변경사항을 확인하고 싶을 때 사용합니다. 입력으로 사용자명과 레포지토리명을 받아 최근 커밋들을 반환합니다.",
        "parameters": {
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
                    "description": "반환할 커밋 수 (기본값: 10, 최대: 100)",
                    "default": 10
                }
            },
            "required": ["username", "repo_name"]
        },
        "output": {
            "type": "object",
            "description": "커밋 내역 정보",
            "properties": {
                "repository": {"type": "string", "description": "레포지토리명 (owner/repo)"},
                "total_commits": {"type": "integer", "description": "반환된 커밋 수"},
                "commits": {
                    "type": "array",
                    "description": "커밋 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sha": {"type": "string", "description": "커밋 해시 (짧은 형태)"},
                            "message": {"type": "string", "description": "커밋 메시지"},
                            "author": {"type": "string", "description": "작성자명"},
                            "date": {"type": "string", "description": "커밋 날짜"},
                            "html_url": {"type": "string", "description": "커밋 URL"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "REPOSITORY_NOT_FOUND",
                "description": "요청한 레포지토리를 찾을 수 없습니다. 사용자명과 레포지토리명을 확인해주세요."
            },
            {
                "code": "PRIVATE_REPOSITORY",
                "description": "비공개 레포지토리입니다. 접근 권한이 필요합니다."
            },
            {
                "code": "RATE_LIMIT_EXCEEDED",
                "description": "GitHub API 호출 제한을 초과했습니다."
            },
            {
                "code": "NO_COMMITS",
                "description": "해당 레포지토리에 커밋이 없습니다."
            }
        ],
        "examples": [
            "kyungho222/workspace-new의 최근 커밋 보여줘",
            "레포지토리 커밋 히스토리: kyungho222/workspace-new",
            "GitHub 커밋: kyungho222/workspace-new"
        ],
        "category": "github",
        "constraints": {
            "rate_limit": "GitHub API: 인증 없이 시간당 60회, 인증 시 시간당 5000회",
            "requires_auth": False,
            "max_limit": 100,
            "error_codes": {
                "404": "레포지토리를 찾을 수 없습니다",
                "403": "API 접근이 제한되었습니다",
                "500": "GitHub 서버 오류"
            }
        }
    }
]

# MongoDB 툴 메타데이터
MONGODB_TOOLS_METADATA = [
    {
        "name": "find_mongodb_documents",
        "description": "MongoDB 데이터베이스에서 문서를 조회하는 툴입니다. 사용자가 데이터베이스에서 특정 정보를 찾고 싶을 때 사용합니다. 입력으로 컬렉션명과 선택적으로 검색 조건을 받아 해당하는 문서들을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "조회할 컬렉션명 (예: users, applicants, jobs)"
                },
                "query": {
                    "type": "object",
                    "description": "검색 조건 (MongoDB 쿼리 형식, 예: {'age': {'$gt': 20}})"
                },
                "limit": {
                    "type": "integer",
                    "description": "반환할 문서 수 (기본값: 10)",
                    "default": 10
                }
            },
            "required": ["collection"]
        },
        "output": {
            "type": "object",
            "description": "MongoDB 조회 결과",
            "properties": {
                "collection": {"type": "string", "description": "조회한 컬렉션명"},
                "total_documents": {"type": "integer", "description": "반환된 문서 수"},
                "documents": {
                    "type": "array",
                    "description": "조회된 문서 목록",
                    "items": {"type": "object", "description": "MongoDB 문서"}
                }
            }
        },
        "errors": [
            {
                "code": "CONNECTION_ERROR",
                "description": "MongoDB 데이터베이스에 연결할 수 없습니다. 데이터베이스 서버 상태를 확인해주세요."
            },
            {
                "code": "COLLECTION_NOT_FOUND",
                "description": "요청한 컬렉션이 존재하지 않습니다. 컬렉션명을 확인해주세요."
            },
            {
                "code": "INVALID_QUERY",
                "description": "MongoDB 쿼리 형식이 유효하지 않습니다. 쿼리 구문을 확인해주세요."
            },
            {
                "code": "TIMEOUT_ERROR",
                "description": "쿼리 실행 시간이 초과되었습니다. 더 간단한 쿼리나 제한을 줄여보세요."
            },
            {
                "code": "NO_DOCUMENTS_FOUND",
                "description": "검색 조건에 맞는 문서가 없습니다."
            }
        ],
        "examples": [
            "users 컬렉션 조회",
            "지원자 데이터 찾기",
            "MongoDB에서 사용자 정보 조회"
        ],
        "category": "database",
        "constraints": {
            "requires_connection": True,
            "max_limit": 1000,
            "error_codes": {
                "connection_error": "MongoDB 연결에 실패했습니다",
                "collection_not_found": "컬렉션을 찾을 수 없습니다",
                "invalid_query": "잘못된 쿼리 형식입니다",
                "timeout": "쿼리 실행 시간이 초과되었습니다"
            }
        }
    },
    {
        "name": "count_mongodb_documents",
        "description": "MongoDB 데이터베이스에서 문서 개수를 세는 툴입니다. 사용자가 특정 조건에 맞는 데이터의 개수를 알고 싶을 때 사용합니다. 입력으로 컬렉션명과 선택적으로 검색 조건을 받아 문서 개수를 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "description": "개수를 셀 컬렉션명"
                },
                "query": {
                    "type": "object",
                    "description": "검색 조건 (MongoDB 쿼리 형식)"
                }
            },
            "required": ["collection"]
        },
        "output": {
            "type": "object",
            "description": "문서 개수 정보",
            "properties": {
                "collection": {"type": "string", "description": "조회한 컬렉션명"},
                "count": {"type": "integer", "description": "문서 개수"},
                "query_applied": {"type": "object", "description": "적용된 검색 조건"}
            }
        },
        "errors": [
            {
                "code": "CONNECTION_ERROR",
                "description": "MongoDB 데이터베이스에 연결할 수 없습니다."
            },
            {
                "code": "COLLECTION_NOT_FOUND",
                "description": "요청한 컬렉션이 존재하지 않습니다."
            },
            {
                "code": "INVALID_QUERY",
                "description": "MongoDB 쿼리 형식이 유효하지 않습니다."
            },
            {
                "code": "TIMEOUT_ERROR",
                "description": "카운트 쿼리 실행 시간이 초과되었습니다."
            }
        ],
        "examples": [
            "users 컬렉션 개수 조회",
            "지원자 수 세기",
            "MongoDB 문서 개수 확인"
        ],
        "category": "database",
        "constraints": {
            "requires_connection": True,
            "error_codes": {
                "connection_error": "MongoDB 연결에 실패했습니다",
                "collection_not_found": "컬렉션을 찾을 수 없습니다",
                "invalid_query": "잘못된 쿼리 형식입니다",
                "timeout": "쿼리 실행 시간이 초과되었습니다"
            }
        }
    }
]

# 검색 툴 메타데이터
SEARCH_TOOLS_METADATA = [
    {
        "name": "web_search",
        "description": "웹에서 정보를 검색하는 툴입니다. 사용자가 최신 정보나 특정 주제에 대한 정보를 요청할 때 사용합니다. 입력으로 검색어를 받아 관련된 웹 검색 결과를 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 키워드나 질문 (예: 'Python FastAPI 튜토리얼', '최신 AI 기술 동향')"
                },
                "num_results": {
                    "type": "integer",
                    "description": "반환할 결과 수 (기본값: 10, 최대: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        },
        "output": {
            "type": "object",
            "description": "웹 검색 결과",
            "properties": {
                "query": {"type": "string", "description": "검색 쿼리"},
                "total_results": {"type": "integer", "description": "전체 검색 결과 수"},
                "results": {
                    "type": "array",
                    "description": "검색 결과 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "페이지 제목"},
                            "snippet": {"type": "string", "description": "페이지 요약"},
                            "url": {"type": "string", "description": "페이지 URL"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "API_KEY_MISSING",
                "description": "Google Search API 키가 설정되지 않았습니다. API 키를 확인해주세요."
            },
            {
                "code": "QUOTA_EXCEEDED",
                "description": "Google Search API 할당량을 초과했습니다. 일일 사용량을 확인해주세요."
            },
            {
                "code": "INVALID_QUERY",
                "description": "검색어가 유효하지 않습니다. 너무 짧거나 특수문자가 포함된 검색어를 피해주세요."
            },
            {
                "code": "NO_RESULTS",
                "description": "검색 조건에 맞는 결과가 없습니다. 검색어를 변경해보세요."
            },
            {
                "code": "SEARCH_SERVICE_UNAVAILABLE",
                "description": "검색 서비스가 일시적으로 사용할 수 없습니다."
            }
        ],
        "examples": [
            "Python FastAPI 검색",
            "웹에서 최신 기술 정보 찾기",
            "검색: AI 채용 시스템"
        ],
        "category": "search",
        "constraints": {
            "requires_api_key": True,
            "max_results": 10,
            "error_codes": {
                "api_key_missing": "Google API 키가 필요합니다",
                "quota_exceeded": "API 할당량을 초과했습니다",
                "invalid_query": "검색어가 유효하지 않습니다",
                "no_results": "검색 결과가 없습니다"
            }
        }
    },
    {
        "name": "news_search",
        "description": "뉴스 기사를 검색하는 툴입니다. 사용자가 최신 뉴스나 특정 주제의 뉴스를 요청할 때 사용합니다. 입력으로 검색어를 받아 관련된 뉴스 기사들을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 뉴스 키워드 (예: 'AI 기술', '채용 시장 동향')"
                },
                "num_results": {
                    "type": "integer",
                    "description": "반환할 결과 수 (기본값: 10, 최대: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        },
        "output": {
            "type": "object",
            "description": "뉴스 검색 결과",
            "properties": {
                "query": {"type": "string", "description": "검색 쿼리"},
                "total_results": {"type": "integer", "description": "전체 검색 결과 수"},
                "results": {
                    "type": "array",
                    "description": "뉴스 기사 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "기사 제목"},
                            "snippet": {"type": "string", "description": "기사 요약"},
                            "url": {"type": "string", "description": "기사 URL"},
                            "source": {"type": "string", "description": "뉴스 출처"},
                            "published_date": {"type": "string", "description": "발행일"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "API_KEY_MISSING",
                "description": "Google News API 키가 설정되지 않았습니다."
            },
            {
                "code": "QUOTA_EXCEEDED",
                "description": "Google News API 할당량을 초과했습니다."
            },
            {
                "code": "INVALID_QUERY",
                "description": "뉴스 검색어가 유효하지 않습니다."
            },
            {
                "code": "NO_NEWS_RESULTS",
                "description": "검색 조건에 맞는 뉴스 기사가 없습니다."
            },
            {
                "code": "NEWS_SERVICE_UNAVAILABLE",
                "description": "뉴스 검색 서비스가 일시적으로 사용할 수 없습니다."
            }
        ],
        "examples": [
            "AI 기술 뉴스 검색",
            "최신 채용 시장 뉴스",
            "뉴스: IT 업계 동향"
        ],
        "category": "search",
        "constraints": {
            "requires_api_key": True,
            "max_results": 10,
            "error_codes": {
                "api_key_missing": "Google API 키가 필요합니다",
                "quota_exceeded": "API 할당량을 초과했습니다",
                "invalid_query": "검색어가 유효하지 않습니다",
                "no_results": "뉴스 검색 결과가 없습니다"
            }
        }
    },
    {
        "name": "image_search",
        "description": "이미지를 검색하는 툴입니다. 사용자가 특정 이미지나 시각적 자료를 요청할 때 사용합니다. 입력으로 검색어를 받아 관련된 이미지들을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 이미지 키워드 (예: '회사 로고', '프로젝트 구조도')"
                },
                "num_results": {
                    "type": "integer",
                    "description": "반환할 결과 수 (기본값: 10, 최대: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        },
        "output": {
            "type": "object",
            "description": "이미지 검색 결과",
            "properties": {
                "query": {"type": "string", "description": "검색 쿼리"},
                "total_results": {"type": "integer", "description": "전체 검색 결과 수"},
                "results": {
                    "type": "array",
                    "description": "이미지 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "이미지 제목"},
                            "url": {"type": "string", "description": "이미지 URL"},
                            "thumbnail": {"type": "string", "description": "썸네일 URL"},
                            "context": {"type": "string", "description": "이미지 컨텍스트"}
                        }
                    }
                }
            }
        },
        "errors": [
            {
                "code": "API_KEY_MISSING",
                "description": "Google Image Search API 키가 설정되지 않았습니다."
            },
            {
                "code": "QUOTA_EXCEEDED",
                "description": "Google Image Search API 할당량을 초과했습니다."
            },
            {
                "code": "INVALID_QUERY",
                "description": "이미지 검색어가 유효하지 않습니다."
            },
            {
                "code": "NO_IMAGE_RESULTS",
                "description": "검색 조건에 맞는 이미지가 없습니다."
            },
            {
                "code": "IMAGE_SERVICE_UNAVAILABLE",
                "description": "이미지 검색 서비스가 일시적으로 사용할 수 없습니다."
            }
        ],
        "examples": [
            "회사 로고 이미지 검색",
            "프로젝트 구조도 찾기",
            "이미지: AI 시스템 아키텍처"
        ],
        "category": "search",
        "constraints": {
            "requires_api_key": True,
            "max_results": 10,
            "error_codes": {
                "api_key_missing": "Google API 키가 필요합니다",
                "quota_exceeded": "API 할당량을 초과했습니다",
                "invalid_query": "검색어가 유효하지 않습니다",
                "no_results": "이미지 검색 결과가 없습니다"
            }
        }
    }
]

# 모든 툴 메타데이터 통합
ALL_TOOLS_METADATA = (
    GITHUB_TOOLS_METADATA + 
    MONGODB_TOOLS_METADATA + 
    SEARCH_TOOLS_METADATA
)

def get_tool_metadata_by_name(name: str) -> Dict[str, Any]:
    """툴 이름으로 메타데이터 조회"""
    for tool in ALL_TOOLS_METADATA:
        if tool["name"] == name:
            return tool
    return None

def get_tools_by_category(category: str) -> List[Dict[str, Any]]:
    """카테고리별 툴 메타데이터 조회"""
    return [tool for tool in ALL_TOOLS_METADATA if tool["category"] == category]

def get_all_tool_names() -> List[str]:
    """모든 툴 이름 반환"""
    return [tool["name"] for tool in ALL_TOOLS_METADATA]

def get_tool_descriptions_for_llm() -> List[str]:
    """LLM 프롬프트용 툴 설명 반환"""
    descriptions = []
    for tool in ALL_TOOLS_METADATA:
        desc = f"- {tool['name']}: {tool['description']}"
        if tool.get('examples'):
            desc += f" (예시: {', '.join(tool['examples'][:2])})"
        descriptions.append(desc)
    return descriptions

def get_function_calling_schemas() -> List[Dict[str, Any]]:
    """OpenAI Function Calling을 위한 스키마 반환"""
    schemas = []
    for tool in ALL_TOOLS_METADATA:
        schema = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        }
        schemas.append(schema)
    return schemas

def get_tool_constraints_summary() -> Dict[str, List[str]]:
    """툴별 제약사항 요약 반환"""
    constraints = {}
    for tool in ALL_TOOLS_METADATA:
        category = tool["category"]
        if category not in constraints:
            constraints[category] = []
        
        tool_constraints = tool.get("constraints", {})
        if tool_constraints:
            constraint_summary = f"{tool['name']}: "
            if tool_constraints.get("requires_auth"):
                constraint_summary += "인증 필요, "
            if tool_constraints.get("requires_connection"):
                constraint_summary += "DB 연결 필요, "
            if tool_constraints.get("requires_api_key"):
                constraint_summary += "API 키 필요, "
            if tool_constraints.get("rate_limit"):
                constraint_summary += f"제한: {tool_constraints['rate_limit']}"
            
            constraints[category].append(constraint_summary.rstrip(", "))
    
    return constraints

def get_tool_errors_summary() -> Dict[str, List[str]]:
    """툴별 에러 정보 요약 반환"""
    errors = {}
    for tool in ALL_TOOLS_METADATA:
        category = tool["category"]
        if category not in errors:
            errors[category] = []
        
        tool_errors = tool.get("errors", [])
        if tool_errors:
            error_summary = f"{tool['name']}: "
            error_codes = [error["code"] for error in tool_errors[:3]]  # 상위 3개 에러만
            error_summary += ", ".join(error_codes)
            errors[category].append(error_summary)
    
    return errors
