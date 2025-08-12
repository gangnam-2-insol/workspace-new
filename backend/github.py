from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import base64
import json
from typing import Optional, Dict, List
import asyncio
from datetime import datetime, timedelta, timezone

router = APIRouter()

class GithubSummaryRequest(BaseModel):
    username: str
    repo_name: Optional[str] = None  # 특정 저장소 분석 시 사용

class GithubSummaryResponse(BaseModel):
    profileUrl: str
    profileApiUrl: str
    source: str
    summary: str
    detailed_analysis: Optional[Dict] = None

class RepositoryAnalysis(BaseModel):
    project_overview: Dict
    tech_stack: Dict
    main_features: List[str]
    file_structure: Dict
    implementation_points: List[str]
    developer_activity: Dict
    deployment_info: Optional[Dict]

GITHUB_API_BASE = 'https://api.github.com'

async def fetch_github(url: str, token: Optional[str] = None) -> Dict:
    """GitHub API 호출"""
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'admin-backend'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def fetch_github_readme(owner: str, repo: str, token: Optional[str] = None) -> Optional[Dict]:
    """리포지토리 README 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/readme', token)
        content = data.get('content', '')
        encoding = data.get('encoding', 'base64')
        
        if encoding == 'base64':
            decoded = base64.b64decode(content).decode('utf-8')
            return {
                'text': decoded,
                'path': data.get('path'),
                'html_url': data.get('html_url')
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise
    return None

def resolve_username(input_str: str) -> str:
    """사용자명 추출"""
    if not input_str:
        return ''
    
    trimmed = input_str.strip()
    
    # URL에서 사용자명 추출
    if trimmed.startswith(('http://', 'https://')):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(trimmed)
            parts = [p for p in parsed.path.split('/') if p]
            
            if parsed.hostname == 'api.github.com' and parts and parts[0] == 'users' and len(parts) > 1:
                return parts[1]
            elif parsed.hostname == 'github.com' and parts:
                return parts[0]
        except:
            pass
    
    return trimmed

def parse_github_url(url: str) -> Optional[tuple[str, Optional[str]]]:
    """GitHub URL에서 username과 repo_name 추출"""
    if not url or not url.startswith('https://github.com/'):
        return None
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split('/') if p]
        
        if len(parts) >= 2:
            username = parts[0]
            repo_name = parts[1]
            return username, repo_name
        elif len(parts) == 1:
            # 사용자 프로필 URL인 경우 (예: https://github.com/test)
            username = parts[0]
            return username, None
    except:
        pass
    
    return None

async def fetch_user_repos(username: str, token: Optional[str] = None) -> List[Dict]:
    """사용자 리포지토리 목록 가져오기"""
    data = await fetch_github(f'{GITHUB_API_BASE}/users/{username}/repos?per_page=100&sort=updated', token)
    return data or []

async def fetch_repo_languages(owner: str, repo: str, token: Optional[str] = None) -> Dict:
    """리포지토리 언어 통계 가져오기"""
    try:
        return await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/languages', token)
    except:
        return {}

async def fetch_repo_top_level_files(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """리포지토리 최상위 파일 목록 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/contents', token)
        items = data if isinstance(data, list) else []
        return [{'name': item['name'], 'type': item.get('type', 'file'), 'path': item.get('path', '')} 
                for item in items][:20]
    except:
        return []

async def fetch_repo_commits(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """리포지토리 커밋 기록 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/commits?per_page=30', token)
        return data or []
    except:
        return []

async def fetch_repo_issues(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """리포지토리 이슈 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/issues?state=all&per_page=20', token)
        return data or []
    except:
        return []

async def fetch_repo_pulls(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """리포지토리 PR 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls?state=all&per_page=20', token)
        return data or []
    except:
        return []

async def analyze_repository_structure(files: List[Dict]) -> Dict:
    """파일 구조 분석"""
    structure = {
        'main_directories': {},
        'key_files': [],
        'config_files': [],
        'documentation': []
    }
    
    for file in files:
        name = file['name']
        file_type = file['type']
        
        if file_type == 'dir':
            structure['main_directories'][name] = '디렉토리'
        else:
            if name in ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod']:
                structure['config_files'].append(name)
            elif name in ['README.md', 'CHANGELOG.md', 'LICENSE', 'CONTRIBUTING.md']:
                structure['documentation'].append(name)
            elif name in ['Dockerfile', 'docker-compose.yml', '.github', 'deploy', 'scripts']:
                structure['key_files'].append(name)
    
    return structure

async def analyze_developer_activity(commits: List[Dict], issues: List[Dict], pulls: List[Dict]) -> Dict:
    """개발자 활동 분석"""
    if not commits:
        return {'commit_frequency': '정보 없음', 'recent_activity': '정보 없음', 'collaboration': '정보 없음'}
    
    # 최근 30일 커밋 수 (timezone 정보 포함)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_commits = [c for c in commits if datetime.fromisoformat(c['commit']['author']['date'].replace('Z', '+00:00')) > thirty_days_ago]
    
    # 커밋 빈도 분석
    total_commits = len(commits)
    recent_commit_count = len(recent_commits)
    
    if recent_commit_count > 20:
        frequency = "매우 활발함"
    elif recent_commit_count > 10:
        frequency = "활발함"
    elif recent_commit_count > 5:
        frequency = "보통"
    else:
        frequency = "적음"
    
    # 협업 활동
    collaboration_score = len(pulls) + len(issues)
    if collaboration_score > 20:
        collaboration = "매우 활발한 협업"
    elif collaboration_score > 10:
        collaboration = "활발한 협업"
    elif collaboration_score > 5:
        collaboration = "일반적인 협업"
    else:
        collaboration = "개인 프로젝트"
    
    return {
        'commit_frequency': frequency,
        'recent_activity': f"최근 30일 {recent_commit_count}개 커밋",
        'total_commits': total_commits,
        'collaboration': collaboration,
        'issues_count': len(issues),
        'pulls_count': len(pulls)
    }

async def analyze_tech_stack(languages: Dict, files: List[Dict], readme_text: str) -> Dict:
    """기술 스택 분석"""
    tech_stack = {
        'languages': languages,
        'frameworks': [],
        'databases': [],
        'deployment': [],
        'testing': [],
        'other_tools': []
    }
    
    # 파일 기반 프레임워크/라이브러리 추정
    file_names = [f['name'].lower() for f in files]
    
    # 프레임워크 추정
    if any('package.json' in f for f in file_names):
        tech_stack['frameworks'].append('Node.js')
    if any('requirements.txt' in f for f in file_names):
        tech_stack['frameworks'].append('Python')
    if any('pom.xml' in f for f in file_names):
        tech_stack['frameworks'].append('Java/Maven')
    if any('build.gradle' in f for f in file_names):
        tech_stack['frameworks'].append('Java/Gradle')
    if any('cargo.toml' in f for f in file_names):
        tech_stack['frameworks'].append('Rust')
    if any('go.mod' in f for f in file_names):
        tech_stack['frameworks'].append('Go')
    
    # 데이터베이스 추정
    if any('docker-compose' in f for f in file_names):
        tech_stack['databases'].append('Docker Compose')
    if any('dockerfile' in f for f in file_names):
        tech_stack['deployment'].append('Docker')
    
    # 테스트 도구 추정
    if any('test' in f for f in file_names) or any('spec' in f for f in file_names):
        tech_stack['testing'].append('테스트 프레임워크')
    
    return tech_stack

async def extract_main_features(readme_text: str, repo_description: str) -> List[str]:
    """주요 기능 추출"""
    features = []
    
    # README에서 기능 추출 시도
    if readme_text:
        lines = readme_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('##', '###', '**', '-', '•', '*')) and any(keyword in line.lower() for keyword in ['기능', 'feature', '기능', '서비스', 'service']):
                features.append(line.replace('##', '').replace('###', '').replace('**', '').replace('-', '').replace('•', '').replace('*', '').strip())
    
    # 설명에서 기능 추출
    if repo_description:
        features.append(repo_description)
    
    return features[:5] if features else ['기능 정보 없음']

async def analyze_implementation_points(languages: Dict, files: List[Dict], readme_text: str) -> List[str]:
    """구현 포인트 분석"""
    points = []
    
    # 언어별 특징
    if 'Python' in languages:
        points.append('Python 기반 백엔드/데이터 처리')
    if 'JavaScript' in languages or 'TypeScript' in languages:
        points.append('웹 프론트엔드/백엔드')
    if 'Java' in languages:
        points.append('엔터프라이즈급 백엔드')
    if 'C++' in languages:
        points.append('성능 중심 시스템')
    if 'Go' in languages:
        points.append('고성능 서버/마이크로서비스')
    
    # 파일 구조 기반 특징
    file_names = [f['name'].lower() for f in files]
    if any('docker' in f for f in file_names):
        points.append('컨테이너화/클라우드 배포')
    if any('test' in f for f in file_names):
        points.append('테스트 주도 개발')
    if any('api' in f for f in file_names):
        points.append('API 중심 설계')
    
    return points[:5] if points else ['구현 특징 정보 없음']

async def generate_detailed_analysis(repo_data: Dict, languages: Dict, files: List[Dict], 
                                   commits: List[Dict], issues: List[Dict], pulls: List[Dict], 
                                   readme_text: str) -> Dict:
    """상세 분석 생성"""
    
    # 파일 구조 분석
    file_structure = await analyze_repository_structure(files)
    
    # 개발자 활동 분석
    developer_activity = await analyze_developer_activity(commits, issues, pulls)
    
    # 기술 스택 분석
    tech_stack = await analyze_tech_stack(languages, files, readme_text)
    
    # 주요 기능 추출
    main_features = await extract_main_features(readme_text, repo_data.get('description', ''))
    
    # 구현 포인트 분석
    implementation_points = await analyze_implementation_points(languages, files, readme_text)
    
    # 프로젝트 개요
    project_overview = {
        'name': repo_data.get('name', ''),
        'description': repo_data.get('description', '설명 없음'),
        'stars': repo_data.get('stargazers_count', 0),
        'forks': repo_data.get('forks_count', 0),
        'created_at': repo_data.get('created_at', ''),
        'updated_at': repo_data.get('updated_at', ''),
        'language': repo_data.get('language', '정보 없음')
    }
    
    # 배포 정보
    deployment_info = None
    if any('docker' in f['name'].lower() for f in files):
        deployment_info = {
            'method': 'Docker',
            'files': [f['name'] for f in files if 'docker' in f['name'].lower()]
        }
    elif any('package.json' in f['name'] for f in files):
        deployment_info = {
            'method': 'Node.js',
            'files': ['package.json']
        }
    
    return {
        'project_overview': project_overview,
        'tech_stack': tech_stack,
        'main_features': main_features,
        'file_structure': file_structure,
        'implementation_points': implementation_points,
        'developer_activity': developer_activity,
        'deployment_info': deployment_info
    }

async def generate_unified_summary(username: str, repo_name: Optional[str] = None, profile_readme: Optional[Dict] = None, repos_data: Optional[List[Dict]] = None) -> List[Dict]:
    """통합된 요약 생성 함수 - README와 레포 데이터를 모두 처리"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
    
    model = 'gemini-2.5-flash-lite'
    endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
    
    # 입력 데이터 구성
    input_data = {
        "username": username,
        "profile_url": f"https://github.com/{username}"
    }
    
    if repo_name:
        # 특정 레포지토리 분석
        input_data["analysis_type"] = "single_repo"
        input_data["repo_name"] = repo_name
        input_data["repo_data"] = repos_data[0] if repos_data else {}
    elif profile_readme and profile_readme.get('text'):
        # 프로필 README 분석
        input_data["analysis_type"] = "profile_readme"
        input_data["readme_text"] = profile_readme['text']
    elif repos_data:
        # 여러 레포지토리 분석
        input_data["analysis_type"] = "multiple_repos"
        input_data["repos"] = repos_data
    else:
        raise HTTPException(status_code=404, detail="분석할 데이터가 없습니다.")
    
    # 통합 프롬프트 구성
    if input_data["analysis_type"] == "single_repo":
        repo_data = input_data["repo_data"]
        prompt = f"""당신은 GitHub 레포지토리를 분석하여 채용 담당자가 이해하기 쉬운 형태로 요약하는 전문가입니다.

다음 레포지토리 데이터를 분석하여 '주제', '기술 스택', '주요 기능', '레포 주소', '아키텍처 구조', '외부 라이브러리', 'LLM 모델 정보'를 추출해주세요:

**레포지토리 정보**
- 이름: {repo_data.get('name', repo_name)}
- 설명: {repo_data.get('description', '설명 없음')}
- 언어: {repo_data.get('language', '정보 없음')}
- 스타: {repo_data.get('stargazers_count', 0)}, 포크: {repo_data.get('forks_count', 0)}
- URL: {repo_data.get('html_url', f'https://github.com/{username}/{repo_name}')}

**기술 스택 정보**
- 사용 언어: {repo_data.get('languages', {})}
- 프레임워크: {repo_data.get('frameworks', [])}

**주요 기능**
{repo_data.get('main_features', '기능 정보 없음')}

**파일 구조**
{repo_data.get('file_structure', '파일 구조 정보 없음')}

**개발자 활동**
{repo_data.get('developer_activity', '활동 정보 없음')}

**중요한 지침:**
- 기술 스택은 구체적인 라이브러리나 도구명 대신 카테고리별로 간단하게 표시하세요
- 예: "Naver Search MCP", "Exa Search MCP" → "MCP"
- 예: "React", "Vue.js", "Angular" → "Frontend Framework"
- 예: "MongoDB", "PostgreSQL", "MySQL" → "Database"
- 예: "Docker", "Kubernetes" → "Containerization"

- 아키텍처 구조는 전체 앱의 흐름과 주요 컴포넌트 간 관계를 설명하세요
- 외부 라이브러리는 사용된 주요 라이브러리와 API, 버전 정보를 포함하세요
- LLM 모델 정보는 사용된 LLM 종류와 호출 방식을 설명하세요

다음 JSON 형식으로 응답해주세요:
{{
  "주제": "프로젝트의 핵심 목적과 특징을 간결하게 설명",
  "기술 스택": ["언어1", "프레임워크1", "라이브러리1"],
  "주요 기능": ["기능1", "기능2", "기능3"],
  "레포 주소": "{repo_data.get('html_url', f'https://github.com/{username}/{repo_name}')}",
  "아키텍처 구조": "전체 앱의 흐름과 주요 컴포넌트 간 관계 설명",
  "외부 라이브러리": ["라이브러리1 (버전)", "API1", "라이브러리2 (버전)"],
  "LLM 모델 정보": "사용된 LLM 종류와 호출 방식 설명"
}}"""
    
    elif input_data["analysis_type"] == "profile_readme":
        readme_text = input_data["readme_text"]
        prompt = f"""당신은 GitHub 사용자 프로필 README를 분석하여 채용 담당자가 이해하기 쉬운 형태로 요약하는 전문가입니다.

다음 프로필 README 내용을 분석하여 '주제', '기술 스택', '주요 기능', '레포 주소', '아키텍처 구조', '외부 라이브러리', 'LLM 모델 정보'를 추출해주세요:

**프로필 README 내용:**
{readme_text}

**중요한 지침:**
- 기술 스택은 구체적인 라이브러리나 도구명 대신 카테고리별로 간단하게 표시하세요
- 예: "Naver Search MCP", "Exa Search MCP" → "MCP"
- 예: "React", "Vue.js", "Angular" → "Frontend Framework"
- 예: "MongoDB", "PostgreSQL", "MySQL" → "Database"
- 예: "Docker", "Kubernetes" → "Containerization"

- 아키텍처 구조는 전체 앱의 흐름과 주요 컴포넌트 간 관계를 설명하세요
- 외부 라이브러리는 사용된 주요 라이브러리와 API, 버전 정보를 포함하세요
- LLM 모델 정보는 사용된 LLM 종류와 호출 방식을 설명하세요

다음 JSON 형식으로 응답해주세요:
{{
  "주제": "사용자의 전반적인 기술적 관심사와 전문 분야를 간결하게 설명",
  "기술 스택": ["언어1", "프레임워크1", "라이브러리1"],
  "주요 기능": ["주요 프로젝트1", "주요 프로젝트2", "주요 프로젝트3"],
  "레포 주소": "{input_data['profile_url']}",
  "아키텍처 구조": "전체 앱의 흐름과 주요 컴포넌트 간 관계 설명",
  "외부 라이브러리": ["라이브러리1 (버전)", "API1", "라이브러리2 (버전)"],
  "LLM 모델 정보": "사용된 LLM 종류와 호출 방식 설명"
}}"""
    
    else:  # multiple_repos
        repos = input_data["repos"]
        repos_info = []
        for repo in repos:
            repos_info.append({
                "name": repo.get('name', ''),
                "description": repo.get('description', '설명 없음'),
                "language": repo.get('language', '정보 없음'),
                "stars": repo.get('stargazers_count', 0),
                "forks": repo.get('forks_count', 0),
                "url": repo.get('html_url', ''),
                "readme_excerpt": repo.get('readme_excerpt', '')[:500] if repo.get('readme_excerpt') else ''
            })
        
        prompt = f"""당신은 GitHub 사용자의 여러 레포지토리를 분석하여 각각을 개별적으로 요약하는 전문가입니다.

다음 {len(repos)}개의 레포지토리 데이터를 분석하여 각 레포지토리별로 '주제', '기술 스택', '주요 기능', '레포 주소', '아키텍처 구조', '외부 라이브러리', 'LLM 모델 정보'를 추출해주세요:

**레포지토리 목록:**
{json.dumps(repos_info, indent=2, ensure_ascii=False)}

**중요한 지침:**
- 기술 스택은 구체적인 라이브러리나 도구명 대신 카테고리별로 간단하게 표시하세요
- 예: "Naver Search MCP", "Exa Search MCP" → "MCP"
- 예: "React", "Vue.js", "Angular" → "Frontend Framework"
- 예: "MongoDB", "PostgreSQL", "MySQL" → "Database"
- 예: "Docker", "Kubernetes" → "Containerization"

- 아키텍처 구조는 전체 앱의 흐름과 주요 컴포넌트 간 관계를 설명하세요
- 외부 라이브러리는 사용된 주요 라이브러리와 API, 버전 정보를 포함하세요
- LLM 모델 정보는 사용된 LLM 종류와 호출 방식을 설명하세요

다음 JSON 형식으로 응답해주세요:
{{
  "repositories": [
    {{
      "name": "레포지토리명",
      "주제": "프로젝트의 핵심 목적과 특징을 간결하게 설명",
      "기술 스택": ["언어1", "프레임워크1", "라이브러리1"],
      "주요 기능": ["기능1", "기능2", "기능3"],
      "레포 주소": "https://github.com/user/repo",
      "아키텍처 구조": "전체 앱의 흐름과 주요 컴포넌트 간 관계 설명",
      "외부 라이브러리": ["라이브러리1 (버전)", "API1", "라이브러리2 (버전)"],
      "LLM 모델 정보": "사용된 LLM 종류와 호출 방식 설명"
    }},
    ...
  ]
}}

각 레포지토리를 개별적으로 분석하여 배열 형태로 제공해주세요."""
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2000
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        data = response.json()
        
        candidate = data.get('candidates', [{}])[0]
        parts = candidate.get('content', {}).get('parts', [])
        response_text = ''.join(part.get('text', '') for part in parts).strip()
        
        try:
            # JSON 응답 파싱 (마크다운 코드 블록 제거)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # ```json 제거
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]  # ``` 제거
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # 끝의 ``` 제거
            
            result = json.loads(cleaned_text.strip())
            
            # 단일 레포지토리나 프로필 README인 경우 배열 형태로 변환
            if input_data["analysis_type"] in ["single_repo", "profile_readme"]:
                if "repositories" not in result:
                    # 단일 객체를 배열로 변환
                    return [result]
                else:
                    return result["repositories"]
            else:
                # 여러 레포지토리인 경우 - 정보 부족한 항목 필터링
                repositories = result.get("repositories", [])
                filtered_repos = []
                for repo in repositories:
                    # 정보가 충분한지 확인 (기본 필드만 필수, 새로운 필드는 선택사항)
                    has_sufficient_info = (
                        repo.get('주제') and 
                        repo.get('주제') != '설명이 부족하여 주제를 특정할 수 없음' and
                        repo.get('주제') != '정보 부족으로 주제 파악 불가' and
                        repo.get('기술 스택') and 
                        len(repo.get('기술 스택', [])) > 0 and
                        repo.get('주요 기능') and 
                        len(repo.get('주요 기능', [])) > 0
                    )
                    if has_sufficient_info:
                        filtered_repos.append(repo)
                return filtered_repos
                
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 텍스트 형태로 반환
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 텍스트: {response_text}")
            return [{
                "주제": "AI 분석 결과",
                "기술 스택": ["분석 중"],
                "주요 기능": ["분석 중"],
                "레포 주소": input_data["profile_url"],
                "아키텍처 구조": "분석 중",
                "외부 라이브러리": ["분석 중"],
                "LLM 모델 정보": "분석 중",
                "raw_response": response_text
            }]

# 기존 함수들을 새로운 통합 함수로 교체
async def generate_summary_with_llm(analysis_data: Dict, repo_name: str) -> List[Dict]:
    """기존 함수를 새로운 통합 함수로 래핑"""
    username = analysis_data.get('username', 'unknown')
    repo_data = {
        'name': repo_name,
        'description': analysis_data.get('project_overview', {}).get('description', ''),
        'language': analysis_data.get('project_overview', {}).get('language', ''),
        'stargazers_count': analysis_data.get('project_overview', {}).get('stars', 0),
        'forks_count': analysis_data.get('project_overview', {}).get('forks', 0),
        'html_url': analysis_data.get('project_overview', {}).get('url', f'https://github.com/{username}/{repo_name}'),
        'languages': analysis_data.get('tech_stack', {}).get('languages', {}),
        'frameworks': analysis_data.get('tech_stack', {}).get('frameworks', []),
        'main_features': analysis_data.get('main_features', []),
        'file_structure': analysis_data.get('file_structure', {}),
        'developer_activity': analysis_data.get('developer_activity', {})
    }
    return await generate_unified_summary(username, repo_name, None, [repo_data])

async def summarize_with_llm(text: str, lines: int = 7) -> List[Dict]:
    """기존 함수를 새로운 통합 함수로 래핑"""
    # text에서 username 추출 시도 (실제로는 호출하는 곳에서 username을 전달해야 함)
    # 임시로 'unknown' 사용
    return await generate_unified_summary('unknown', None, {'text': text}, None)

@router.post("/github/summary", response_model=GithubSummaryResponse)
async def github_summary(request: GithubSummaryRequest):
    """GitHub 사용자 요약"""
    try:
        # GitHub URL이 입력된 경우 파싱
        if request.username.startswith('https://github.com/'):
            parsed = parse_github_url(request.username)
            if parsed:
                username, repo_name = parsed
                # repo_name이 None이 아닌 경우에만 request.repo_name 설정
                if repo_name and not request.repo_name:
                    request.repo_name = repo_name
            else:
                raise HTTPException(status_code=400, detail="올바른 GitHub URL 형식이 아닙니다.")
        else:
            username = resolve_username(request.username)
            if not username:
                raise HTTPException(status_code=400, detail="username이 필요합니다.")
            repo_name = request.repo_name
        
        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN') or ''
        profile_url = f"https://github.com/{username}"
        profile_api_url = f"https://api.github.com/users/{username}"
        
        # 특정 저장소 분석
        if request.repo_name:
            try:
                # 저장소 정보 가져오기
                repo_data = await fetch_github(f'{GITHUB_API_BASE}/repos/{username}/{request.repo_name}', github_token)
                
                # 병렬로 모든 데이터 수집
                languages, files, commits, issues, pulls, readme = await asyncio.gather(
                    fetch_repo_languages(username, request.repo_name, github_token),
                    fetch_repo_top_level_files(username, request.repo_name, github_token),
                    fetch_repo_commits(username, request.repo_name, github_token),
                    fetch_repo_issues(username, request.repo_name, github_token),
                    fetch_repo_pulls(username, request.repo_name, github_token),
                    fetch_github_readme(username, request.repo_name, github_token),
                    return_exceptions=True
                )
                
                # 예외 처리
                languages = languages if not isinstance(languages, Exception) else {}
                files = files if not isinstance(files, Exception) else []
                commits = commits if not isinstance(commits, Exception) else []
                issues = issues if not isinstance(issues, Exception) else []
                pulls = pulls if not isinstance(pulls, Exception) else []
                readme_text = readme['text'] if readme and not isinstance(readme, Exception) else ''
                
                # 상세 분석 생성
                detailed_analysis = await generate_detailed_analysis(
                    repo_data, languages, files, commits, issues, pulls, readme_text
                )
                
                # 통합 요약 생성
                summaries = await generate_unified_summary(username, request.repo_name, None, [detailed_analysis])
                
                return GithubSummaryResponse(
                    profileUrl=profile_url,
                    profileApiUrl=profile_api_url,
                    source=f'repo_analysis_{request.repo_name}',
                    summary=json.dumps(summaries, ensure_ascii=False),
                    detailed_analysis=detailed_analysis
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"저장소 '{request.repo_name}'을 찾을 수 없습니다.")
                raise
        
        # 프로필 README 분석
        profile_readme = await fetch_github_readme(username, username, github_token)
        if profile_readme and profile_readme['text']:
            summaries = await generate_unified_summary(username, None, profile_readme, None)
            return GithubSummaryResponse(
                profileUrl=profile_url,
                profileApiUrl=profile_api_url,
                source='profile_readme',
                summary=json.dumps(summaries, ensure_ascii=False)
            )
        
        # 리포지토리 메타데이터 분석
        repos = await fetch_user_repos(username, github_token)
        if not repos:
            raise HTTPException(status_code=404, detail="공개 리포지토리를 찾을 수 없습니다.")
        
        # 상위 5개 리포 분석
        top_repos = [r for r in repos if not r.get('fork')][:5]
        
        analyses = []
        for repo in top_repos:
            owner_login = repo.get('owner', {}).get('login', username)
            languages, top_level_files, repo_readme = await asyncio.gather(
                fetch_repo_languages(owner_login, repo['name'], github_token),
                fetch_repo_top_level_files(owner_login, repo['name'], github_token),
                fetch_github_readme(owner_login, repo['name'], github_token),
                return_exceptions=True
            )
            
            analyses.append({
                'name': repo['name'],
                'description': repo.get('description', ''),
                'html_url': repo['html_url'],
                'stargazers_count': repo.get('stargazers_count', 0),
                'forks_count': repo.get('forks_count', 0),
                'language': repo.get('language', '정보 없음'),
                'languages': languages if not isinstance(languages, Exception) else {},
                'toplevel_files': top_level_files if not isinstance(top_level_files, Exception) else [],
                'readme_excerpt': repo_readme['text'][:3000] if repo_readme and not isinstance(repo_readme, Exception) else ''
            })
        
        # 통합 요약 생성 (여러 레포지토리)
        summaries = await generate_unified_summary(username, None, None, analyses)
        
        return GithubSummaryResponse(
            profileUrl=profile_url,
            profileApiUrl=profile_api_url,
            source='repos_meta',
            summary=json.dumps(summaries, ensure_ascii=False)
        )
        
    except HTTPException:
        raise
    except Exception as error:
        import traceback
        print(f"GitHub 요약 오류: {error}")
        print(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"요약 처리 중 오류가 발생했습니다: {str(error)}")

@router.post("/github/repo-analysis", response_model=GithubSummaryResponse)
async def github_repo_analysis(request: GithubSummaryRequest):
    """GitHub 저장소 상세 분석 (새로운 엔드포인트)"""
    try:
        if not request.repo_name:
            raise HTTPException(status_code=400, detail="repo_name이 필요합니다.")
        
        username = resolve_username(request.username)
        if not username:
            raise HTTPException(status_code=400, detail="username이 필요합니다.")
        
        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN') or ''
        profile_url = f"https://github.com/{username}"
        profile_api_url = f"https://api.github.com/users/{username}"
        
        # 저장소 정보 가져오기
        repo_data = await fetch_github(f'{GITHUB_API_BASE}/repos/{username}/{request.repo_name}', github_token)
        
        # 병렬로 모든 데이터 수집
        languages, files, commits, issues, pulls, readme = await asyncio.gather(
            fetch_repo_languages(username, request.repo_name, github_token),
            fetch_repo_top_level_files(username, request.repo_name, github_token),
            fetch_repo_commits(username, request.repo_name, github_token),
            fetch_repo_issues(username, request.repo_name, github_token),
            fetch_repo_pulls(username, request.repo_name, github_token),
            fetch_github_readme(username, request.repo_name, github_token),
            return_exceptions=True
        )
        
        # 예외 처리
        languages = languages if not isinstance(languages, Exception) else {}
        files = files if not isinstance(files, Exception) else []
        commits = commits if not isinstance(commits, Exception) else []
        issues = issues if not isinstance(issues, Exception) else []
        pulls = pulls if not isinstance(pulls, Exception) else []
        readme_text = readme['text'] if readme and not isinstance(readme, Exception) else ''
        
        # 상세 분석 생성
        detailed_analysis = await generate_detailed_analysis(
            repo_data, languages, files, commits, issues, pulls, readme_text
        )
        
        # 통합 요약 생성
        summaries = await generate_unified_summary(username, request.repo_name, None, [detailed_analysis])
        
        return GithubSummaryResponse(
            profileUrl=profile_url,
            profileApiUrl=profile_api_url,
            source=f'repo_analysis_{request.repo_name}',
            summary=json.dumps(summaries, ensure_ascii=False),
            detailed_analysis=detailed_analysis
        )
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"저장소 '{request.repo_name}'을 찾을 수 없습니다.")
        raise
    except Exception as error:
        import traceback
        print(f"GitHub 저장소 분석 오류: {error}")
        print(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"저장소 분석 중 오류가 발생했습니다: {str(error)}")
 