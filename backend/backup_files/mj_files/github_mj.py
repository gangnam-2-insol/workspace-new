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

class GithubArchitectureRequest(BaseModel):
    owner: str
    repo: str

class GithubArchitectureResponse(BaseModel):
    owner: str
    repo: str
    topic: str
    tech_stack: List[str]
    external_libs: List[str]
    llm_models: List[str]
    architecture: str
    opened_files: List[str]
    analysis_time: float
    token_usage: Optional[Dict[str, int]] = None  # 토큰 사용량 추가

class GithubSummaryResponse(BaseModel):
    profileUrl: str
    profileApiUrl: str
    source: str
    summary: str
    detailed_analysis: Optional[Dict] = None
    # 인터랙티브 차트를 위한 원시 데이터
    language_stats: Optional[Dict[str, int]] = None
    language_total_bytes: Optional[int] = None
    original_language_stats: Optional[Dict[str, int]] = None  # 원본 언어 통계
    token_usage: Optional[Dict[str, int]] = None  # 토큰 사용량 추가

class LanguageChartResponse(BaseModel):
    language_stats: Dict[str, int]  # 언어별 통계
    total_bytes: int  # 총 바이트 수
    original_stats: Optional[Dict[str, int]] = None  # 원본 통계 (기타 분류 전)

def process_language_stats(language_stats: Dict[str, int], total_bytes: int) -> Dict[str, int]:
    """언어 통계를 처리하여 8개 이상이거나 3% 이하인 언어들을 '기타'로 분류"""
    if not language_stats:
        return language_stats

    entries = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)

    # 3% 이하인 언어들을 찾기
    small_languages = [(name, value) for name, value in entries if (value / total_bytes) * 100 <= 3]

    # 8개 이상이거나 3% 이하인 언어가 여러 개인 경우 처리
    if len(entries) > 8 or len(small_languages) > 1:
        # 3% 이하인 언어들을 제외하고 상위 언어들 선택
        significant_languages = [(name, value) for name, value in entries if (value / total_bytes) * 100 > 3]
        top_languages = significant_languages[:7]

        # 나머지 언어들을 '기타'로 분류
        others = []
        for name, value in entries:
            percentage = (value / total_bytes) * 100
            if percentage <= 3 or not any(top_name == name for top_name, _ in top_languages):
                others.append((name, value))

        # 결과 구성 - 기타를 맨 마지막에 배치
        result = {}
        for name, value in top_languages:
            result[name] = value
        if others:
            others_sum = sum(value for _, value in others)
            result['기타'] = others_sum

        return result
    else:
        # 기존 로직: 상위 7개만 표시
        return dict(entries[:7])

class RepositoryAnalysis(BaseModel):
    project_overview: Dict
    tech_stack: Dict
    main_features: List[str]
    file_structure: Dict
    implementation_points: List[str]
    developer_activity: Dict
    deployment_info: Optional[Dict]

GITHUB_API_BASE = 'https://api.github.com'

async def fetch_github_tree(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """GitHub 레포지토리의 전체 파일 트리를 가져오기"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1', token)
        return data.get('tree', [])
    except Exception as e:
        print(f"파일 트리 가져오기 실패: {e}")
        return []

async def fetch_github_file_content(owner: str, repo: str, file_path: str, token: Optional[str] = None) -> Optional[str]:
    """GitHub 파일 내용 가져오기"""
    try:
        # 파일 정보 먼저 조회하여 크기 확인
        file_info = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{file_path}', token)

        # 파일 크기 제한 (1MB)
        file_size = file_info.get('size', 0)
        if file_size > 1024 * 1024:  # 1MB
            print(f"파일이 너무 큽니다: {file_path} ({file_size} bytes)")
            return None

        # 바이너리 파일 확장자 제외
        binary_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.tflite', '.task', '.model', '.pkl', '.h5', '.pb']
        if any(file_path.lower().endswith(ext) for ext in binary_extensions):
            print(f"바이너리 파일 제외: {file_path}")
            return None

        content = file_info.get('content', '')
        encoding = file_info.get('encoding', 'base64')

        if encoding == 'base64':
            try:
                decoded = base64.b64decode(content).decode('utf-8')
                return decoded
            except UnicodeDecodeError:
                print(f"파일 인코딩 오류: {file_path}")
                return None
        else:
            return content

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"파일을 찾을 수 없음: {file_path}")
            return None
        elif e.response.status_code == 403:
            print(f"파일 접근 권한 없음: {file_path}")
            return None
        else:
            print(f"파일 조회 오류 ({file_path}): {e.response.status_code}")
            return None
    except Exception as e:
        print(f"파일 처리 오류 ({file_path}): {e}")
        return None

async def call_openai_for_planning(file_tree: List[Dict], opened_files: Dict[str, str], token: Optional[str] = None) -> Dict:
    """OpenAI API를 사용하여 다음 액션 계획"""
    global openai_api_calls, openai_tokens_used

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다.")

    # Groq API 사용 (sk-proj-로 시작하는 키)
    if api_key.startswith('sk-proj-'):
        endpoint = "https://api.groq.com/openai/v1/chat/completions"
    else:
        endpoint = "https://api.openai.com/v1/chat/completions"

    # 파일 트리 정보 요약
    file_summary = []
    for file_info in file_tree[:50]:  # 최대 50개 파일만 전송
        file_summary.append({
            'name': file_info.get('path', ''),
            'type': file_info.get('type', ''),
            'size': file_info.get('size', 0)
        })

    # 열린 파일 정보 요약
    opened_summary = []
    for file_path, content in list(opened_files.items())[:5]:  # 최대 5개 파일만 전송
        opened_summary.append({
            'path': file_path,
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        })

    prompt = f"""GitHub 레포지토리 분석을 위한 Planner-Executor 루프입니다.

현재 상황:
- 파일 트리: {len(file_tree)}개 파일
- 열린 파일: {len(opened_files)}개
- 열린 파일 목록: {list(opened_files.keys())}

파일 트리 (상위 50개):
{json.dumps(file_summary, ensure_ascii=False, indent=2)}

열린 파일 내용 (상위 5개):
{json.dumps(opened_summary, ensure_ascii=False, indent=2)}

다음 중 하나의 액션을 선택하세요:

1. 더 많은 파일을 열어야 하는 경우:
{{
  "action": "open",
  "files": ["파일명1", "파일명2", "파일명3"],
  "reason": "이 파일들을 열어야 하는 이유"
}}

2. 충분한 정보가 모여서 최종 분석 결과를 제공하는 경우:
{{
  "action": "answer",
  "result": {{
    "topic": "프로젝트의 핵심 주제와 목적",
    "tech_stack": ["주요 기술 스택 목록"],
    "external_libs": ["외부 라이브러리 목록"],
    "llm_models": ["LLM 관련 라이브러리 목록"],
    "architecture": "전체 아키텍처 구조 설명"
  }}
}}

중요한 지침:
- 항상 JSON 형식으로만 응답하세요
- 파일을 열 때는 가장 중요한 파일부터 선택하세요 (README, package.json, requirements.txt, 주요 설정 파일 등)
- 한 번에 최대 3개 파일까지만 요청하세요
- 충분한 정보가 모이면 "answer" 액션으로 최종 결과를 제공하세요
- LLM 관련 라이브러리는 openai, anthropic, langchain, transformers 등 AI/ML 관련 라이브러리를 포함하세요"""

    payload = {
                    "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    # 타임아웃을 90초로 증가
    async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as client:
        try:
            openai_api_calls += 1
            response = await client.post(endpoint, json=payload, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            })
            response.raise_for_status()
            data = response.json()

            # 토큰 사용량 기록
            if 'usage' in data:
                openai_tokens_used += data['usage'].get('total_tokens', 0)

            response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

            try:
                # JSON 응답 파싱
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError as e:
                print(f"OpenAI 응답 JSON 파싱 실패: {e}")
                print(f"응답 텍스트: {response_text}")
                # 기본 응답 반환
                return {
                    "action": "open",
                    "files": ["README.md"],
                    "reason": "JSON 파싱 실패로 기본 파일 요청"
                }
        except httpx.TimeoutException:
            print("OpenAI API 타임아웃 발생")
            return {
                "action": "answer",
                "result": {
                    "topic": "분석 시간 초과",
                    "tech_stack": [],
                    "external_libs": [],
                    "llm_models": [],
                    "architecture": "분석 시간 초과로 인해 완전한 분석을 제공할 수 없습니다."
                }
            }
        except Exception as e:
            print(f"OpenAI API 호출 오류: {e}")
            return {
                "action": "answer",
                "result": {
                    "topic": "분석 오류",
                    "tech_stack": [],
                    "external_libs": [],
                    "llm_models": [],
                    "architecture": f"분석 중 오류가 발생했습니다: {str(e)}"
                }
            }

async def analyze_repository_architecture(owner: str, repo: str, token: Optional[str] = None) -> GithubArchitectureResponse:
    """Planner-Executor 루프를 사용하여 레포지토리 아키텍처 분석"""
    start_time = datetime.now()

    # 아키텍처 분석 전에 토큰 사용량 초기화
    reset_token_usage()

    try:
        # 1. 파일 트리 가져오기
        print(f"1단계: 파일 트리 수집 중... ({owner}/{repo})")
        file_tree = await fetch_github_tree(owner, repo, token)
        if not file_tree:
            raise HTTPException(status_code=404, detail="파일 트리를 가져올 수 없습니다.")

        print(f"총 {len(file_tree)}개 파일 발견")

        # 2. Planner-Executor 루프 시작
        opened_files = {}
        max_iterations = 6  # 최대 반복 횟수를 6번으로 줄임
        max_analysis_time = 300  # 최대 분석 시간을 5분으로 제한
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            current_time = (datetime.now() - start_time).total_seconds()

            # 분석 시간 제한 확인
            if current_time > max_analysis_time:
                print(f"분석 시간 제한 도달: {current_time:.2f}초")
                break

            print(f"반복 {iteration}: AI 분석 중... (경과 시간: {current_time:.2f}초)")

            # OpenAI에 현재 상황 전달하고 다음 액션 요청
            try:
                ai_response = await call_openai_for_planning(file_tree, opened_files, token)
            except Exception as e:
                print(f"AI 분석 중 오류: {e}")
                break

            if ai_response.get('action') == 'answer':
                # 최종 답변 생성
                result = ai_response.get('result', {})
                analysis_time = (datetime.now() - start_time).total_seconds()

                return GithubArchitectureResponse(
                    owner=owner,
                    repo=repo,
                    topic=result.get('topic', '분석 완료'),
                    tech_stack=result.get('tech_stack', []),
                    external_libs=result.get('external_libs', []),
                    llm_models=result.get('llm_models', []),
                    architecture=result.get('architecture', '분석 완료'),
                    opened_files=list(opened_files.keys()),
                    analysis_time=analysis_time,
                    token_usage=get_token_usage()
                )

            elif ai_response.get('action') == 'open':
                # 파일 열기 요청
                files_to_open = ai_response.get('files', [])
                reason = ai_response.get('reason', '')
                print(f"파일 열기 요청: {files_to_open} (이유: {reason})")

                # 요청된 파일들 열기 (최대 3개씩만 처리)
                opened_count = 0
                for file_path in files_to_open[:3]:
                    if file_path not in opened_files and opened_count < 3:
                        try:
                            content = await fetch_github_file_content(owner, repo, file_path, token)
                            if content:
                                opened_files[file_path] = content
                                opened_count += 1
                                print(f"파일 열기 성공: {file_path}")
                            else:
                                print(f"파일 열기 실패: {file_path}")
                        except Exception as e:
                            print(f"파일 열기 오류 ({file_path}): {e}")

                print(f"현재 열린 파일 수: {len(opened_files)}")

                # 충분한 파일이 열렸으면 분석 완료로 간주
                if len(opened_files) >= 15:
                    print("충분한 파일이 열려서 분석을 완료합니다.")
                    break
            else:
                print(f"알 수 없는 AI 응답: {ai_response}")
                break

        # 최대 반복 횟수 도달 또는 시간 초과 시 기본 결과 반환
        analysis_time = (datetime.now() - start_time).total_seconds()
        print(f"분석 완료 (반복 {iteration}회, 시간 {analysis_time:.2f}초)")

        return GithubArchitectureResponse(
            owner=owner,
            repo=repo,
            topic="분석 완료 (제한 시간 내)",
            tech_stack=[],
            external_libs=[],
            llm_models=[],
            architecture="분석 완료",
            opened_files=list(opened_files.keys()),
            analysis_time=analysis_time,
            token_usage=get_token_usage()
        )

    except Exception as e:
        analysis_time = (datetime.now() - start_time).total_seconds()
        print(f"아키텍처 분석 중 오류: {e}")
        return GithubArchitectureResponse(
            owner=owner,
            repo=repo,
            topic=f"분석 오류: {str(e)}",
            tech_stack=[],
            external_libs=[],
            llm_models=[],
            architecture="분석 실패",
            opened_files=[],
            analysis_time=analysis_time,
            token_usage=get_token_usage()
        )

# 토큰 사용량 추적을 위한 전역 변수
github_api_calls = 0
openai_api_calls = 0
openai_tokens_used = 0

def reset_token_usage():
    """토큰 사용량 초기화"""
    global github_api_calls, openai_api_calls, openai_tokens_used
    github_api_calls = 0
    openai_api_calls = 0
    openai_tokens_used = 0

def get_token_usage():
    """현재 토큰 사용량 반환"""
    global github_api_calls, openai_api_calls, openai_tokens_used
    return {
        "github_api_calls": github_api_calls,
        "openai_api_calls": openai_api_calls,
        "openai_tokens_used": openai_tokens_used
    }

async def fetch_github(url: str, token: Optional[str] = None) -> Dict:
    """GitHub API 호출"""
    global github_api_calls
    github_api_calls += 1

    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'admin-backend'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    # 타임아웃을 60초로 증가
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            print(f"GitHub API 타임아웃: {url}")
            raise HTTPException(status_code=408, detail="GitHub API 요청이 시간 초과되었습니다.")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise HTTPException(status_code=403, detail="GitHub API 호출 제한에 도달했습니다. 잠시 후 다시 시도해주세요.")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="요청한 리소스를 찾을 수 없습니다.")
            else:
                raise HTTPException(status_code=e.response.status_code, detail=f"GitHub API 오류: {e.response.status_code}")

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
    """사용자명 추출 - parse_github_url과 일관된 로직 사용"""
    if not input_str:
        return ''

    trimmed = input_str.strip()

    # GitHub URL인 경우 parse_github_url 함수 사용
    if trimmed.startswith('https://github.com/'):
        parsed = parse_github_url(trimmed)
        if parsed:
            return parsed[0]  # username 반환

    # 다른 URL 형식 처리
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
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/users/{username}/repos?per_page=100&sort=updated', token)
        return data or []
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"사용자 '{username}'을 찾을 수 없습니다.")
            raise HTTPException(status_code=404, detail=f"GitHub 사용자 '{username}'을 찾을 수 없습니다.")
        elif e.response.status_code == 403:
            print(f"사용자 '{username}'의 리포지토리에 접근 권한이 없습니다.")
            raise HTTPException(status_code=403, detail="GitHub API 호출 제한에 도달했습니다. 잠시 후 다시 시도해주세요.")
        else:
            print(f"사용자 '{username}'의 리포지토리 조회 중 오류: {e.response.status_code}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GitHub API 오류: {e.response.status_code}")
    except Exception as e:
        print(f"사용자 '{username}'의 리포지토리 조회 중 예외: {e}")
        raise HTTPException(status_code=500, detail=f"리포지토리 조회 중 오류가 발생했습니다: {str(e)}")

async def fetch_repo_languages(owner: str, repo: str, token: Optional[str] = None) -> Dict:
    """리포지토리 언어 통계 가져오기"""
    try:
        return await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/languages', token)
    except:
        return {}

# 핵심파일 우선순위 정의
CORE_FILES_PRIORITY = {
    # 의존성 및 설정 파일 (최우선)
    'high': [
        'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'requirements.txt', 'Pipfile', 'poetry.lock', 'pyproject.toml',
        'pom.xml', 'build.gradle', 'gradle.properties',
        'Cargo.toml', 'Cargo.lock',
        'go.mod', 'go.sum',
        'Gemfile', 'Gemfile.lock',
        'composer.json', 'composer.lock',
        'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        'kubernetes.yml', 'k8s.yml', 'helm-chart.yaml',
        '.env.example', '.env.sample', 'config.yml', 'config.yaml'
    ],
    # 문서 및 설명 파일
    'medium': [
        'readme.md', 'readme.txt', 'readme.rst', 'readme.markdown',
        'readme', 'readme.txt', 'readme.rst', 'readme.markdown',
        'README.md', 'README.txt', 'README.rst', 'README.markdown',
        'README', 'README.txt', 'README.rst', 'README.markdown',
        'docs/', 'documentation/', 'doc/',
        'changelog.md', 'changelog.txt', 'history.md', 'history.txt',
        'license', 'license.txt', 'license.md', 'licence', 'licence.txt', 'licence.md',
        'LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENCE', 'LICENCE.txt', 'LICENCE.md'
    ],
    # 프레임워크 및 빌드 설정 파일
    'normal': [
        'webpack.config.js', 'webpack.config.ts', 'vite.config.js', 'vite.config.ts',
        'rollup.config.js', 'parcel.config.js', 'esbuild.config.js',
        'next.config.js', 'next.config.ts', 'nuxt.config.js', 'nuxt.config.ts',
        'angular.json', 'angular-cli.json', 'vue.config.js', 'vue.config.ts',
        'tsconfig.json', 'tsconfig.ts', 'jsconfig.json', 'jsconfig.js',
        'babel.config.js', 'babel.config.json', '.babelrc', '.babelrc.js',
        'eslint.config.js', 'eslint.config.ts', '.eslintrc', '.eslintrc.js', '.eslintrc.json',
        'prettier.config.js', 'prettier.config.ts', '.prettierrc', '.prettierrc.js', '.prettierrc.json',
        'jest.config.js', 'jest.config.ts', 'vitest.config.js', 'vitest.config.ts',
        'karma.conf.js', 'mocha.opts', '.mocharc.js', '.mocharc.json',
        'pytest.ini', 'tox.ini', 'setup.cfg', 'setup.py',
        'Makefile', 'makefile', 'Rakefile', 'rakefile',
        'Procfile', 'procfile', 'heroku.yml', 'app.json',
        'vercel.json', 'netlify.toml', 'firebase.json', 'firebase.rules',
        'tailwind.config.js', 'tailwind.config.ts', 'postcss.config.js', 'postcss.config.ts',
        'sass.config.js', 'less.config.js', 'stylus.config.js'
    ]
}

async def fetch_repo_core_files(owner: str, repo: str, token: Optional[str] = None) -> Dict[str, List[Dict]]:
    """핵심파일 우선순위에 따라 레포지토리 파일들을 선별 조회"""
    try:
        # 최상위 디렉토리 파일 목록 가져오기
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/contents', token)
        if not isinstance(data, list):
            return {'high': [], 'medium': [], 'normal': [], 'other': []}

        # 파일들을 우선순위별로 분류
        categorized_files = {'high': [], 'medium': [], 'normal': [], 'other': []}

        for item in data:
            if item.get('type') != 'file':
                continue

            filename = item['name'].lower()
            file_info = {
                'name': item['name'],
                'path': item.get('path', ''),
                'size': item.get('size', 0),
                'url': item.get('download_url', ''),
                'sha': item.get('sha', '')
            }

            # 우선순위별 분류
            if filename in [f.lower() for f in CORE_FILES_PRIORITY['high']]:
                categorized_files['high'].append(file_info)
            elif filename in [f.lower() for f in CORE_FILES_PRIORITY['medium']]:
                categorized_files['medium'].append(file_info)
            elif filename in [f.lower() for f in CORE_FILES_PRIORITY['normal']]:
                categorized_files['normal'].append(file_info)
            else:
                categorized_files['other'].append(file_info)

        # 각 우선순위별로 상위 파일들만 선택 (성능 최적화)
        result = {
            'high': categorized_files['high'][:15],  # 의존성 파일은 최대 15개
            'medium': categorized_files['medium'][:10],  # 문서 파일은 최대 10개
            'normal': categorized_files['normal'][:20],  # 설정 파일은 최대 20개
            'other': categorized_files['other'][:10]  # 기타 파일은 최대 10개
        }

        return result

    except Exception as e:
        print(f"핵심파일 조회 중 오류: {e}")
        return {'high': [], 'medium': [], 'normal': [], 'other': []}

async def fetch_repo_top_level_files(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """리포지토리 최상위 파일 목록 가져오기 (기존 호환성 유지)"""
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/contents', token)
        items = data if isinstance(data, list) else []
        return [{'name': item['name'], 'type': item.get('type', 'file'), 'path': item.get('path', '')}
                for item in items][:20]
    except:
        return []

async def fetch_repo_file(owner: str, repo: str, path: str, token: Optional[str] = None) -> Optional[str]:
    """특정 경로의 파일 원문 가져오기 (base64 디코딩 포함)
    - 최상위 파일 위주로 사용 (package.json, requirements.txt 등)
    """
    try:
        data = await fetch_github(f'{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}', token)
        content = data.get('content', '')
        encoding = data.get('encoding', 'base64')
        if encoding == 'base64' and content:
            return base64.b64decode(content).decode('utf-8', errors='ignore')
        return None
    except Exception:
        return None

async def analyze_core_files_content(owner: str, repo: str, core_files: Dict[str, List[Dict]], token: Optional[str] = None) -> Dict:
    """핵심파일들의 내용을 분석하여 프로젝트 정보 추출"""
    analysis_result = {
        'dependencies': {},
        'frameworks': [],
        'build_tools': [],
        'deployment_configs': [],
        'documentation': {},
        'project_structure': {}
    }

    # 의존성 파일 분석 (high priority)
    for file_info in core_files.get('high', []):
        file_content = await fetch_repo_file(owner, repo, file_info['path'], token)
        if not file_content:
            continue

        filename = file_info['name'].lower()

        # package.json 분석
        if filename == 'package.json':
            try:
                import json
                pkg_data = json.loads(file_content)
                analysis_result['dependencies']['npm'] = {
                    'dependencies': pkg_data.get('dependencies', {}),
                    'devDependencies': pkg_data.get('devDependencies', {}),
                    'scripts': pkg_data.get('scripts', {}),
                    'engines': pkg_data.get('engines', {})
                }

                # 프레임워크 감지
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                if 'react' in deps:
                    analysis_result['frameworks'].append('React')
                if 'vue' in deps:
                    analysis_result['frameworks'].append('Vue.js')
                if 'angular' in deps:
                    analysis_result['frameworks'].append('Angular')
                if 'next' in deps:
                    analysis_result['frameworks'].append('Next.js')
                if 'nuxt' in deps:
                    analysis_result['frameworks'].append('Nuxt.js')
                if 'express' in deps:
                    analysis_result['frameworks'].append('Express.js')
                if 'fastify' in deps:
                    analysis_result['frameworks'].append('Fastify')

            except json.JSONDecodeError:
                pass

        # requirements.txt 분석
        elif filename == 'requirements.txt':
            dependencies = []
            for line in file_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 버전 정보 제거하여 패키지명만 추출
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                    dependencies.append(package_name.strip())

            analysis_result['dependencies']['pip'] = dependencies

            # Python 프레임워크 감지
            if 'django' in dependencies:
                analysis_result['frameworks'].append('Django')
            if 'flask' in dependencies:
                analysis_result['frameworks'].append('Flask')
            if 'fastapi' in dependencies:
                analysis_result['frameworks'].append('FastAPI')
            if 'streamlit' in dependencies:
                analysis_result['frameworks'].append('Streamlit')

        # Docker 파일 분석
        elif filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            analysis_result['deployment_configs'].append({
                'type': 'Docker',
                'file': filename,
                'content_preview': file_content[:500] + '...' if len(file_content) > 500 else file_content
            })

        # 기타 설정 파일들
        elif filename in ['pom.xml', 'build.gradle']:
            analysis_result['build_tools'].append('Maven' if filename == 'pom.xml' else 'Gradle')
        elif filename in ['cargo.toml', 'go.mod']:
            analysis_result['build_tools'].append('Cargo' if filename == 'cargo.toml' else 'Go Modules')

    # 문서 파일 분석 (medium priority)
    for file_info in core_files.get('medium', []):
        file_content = await fetch_repo_file(owner, repo, file_info['path'], token)
        if not file_content:
            continue

        filename = file_info['name'].lower()

        if 'readme' in filename:
            analysis_result['documentation']['readme'] = {
                'file': file_info['name'],
                'content_preview': file_content[:1000] + '...' if len(file_content) > 1000 else file_content
            }
        elif 'license' in filename or 'licence' in filename:
            analysis_result['documentation']['license'] = {
                'file': file_info['name'],
                'type': 'License file'
            }
        elif 'changelog' in filename or 'history' in filename:
            analysis_result['documentation']['changelog'] = {
                'file': file_info['name'],
                'content_preview': file_content[:500] + '...' if len(file_content) > 500 else file_content
            }

    # 설정 파일 분석 (normal priority)
    for file_info in core_files.get('normal', []):
        filename = file_info['name'].lower()

        # 프레임워크 설정 파일 감지
        if 'next.config' in filename:
            analysis_result['frameworks'].append('Next.js')
        elif 'nuxt.config' in filename:
            analysis_result['frameworks'].append('Nuxt.js')
        elif 'vue.config' in filename:
            analysis_result['frameworks'].append('Vue.js')
        elif 'angular.json' in filename:
            analysis_result['frameworks'].append('Angular')
        elif 'webpack.config' in filename:
            analysis_result['build_tools'].append('Webpack')
        elif 'vite.config' in filename:
            analysis_result['build_tools'].append('Vite')
        elif 'tsconfig' in filename:
            analysis_result['build_tools'].append('TypeScript')

    # 중복 제거
    analysis_result['frameworks'] = list(set(analysis_result['frameworks']))
    analysis_result['build_tools'] = list(set(analysis_result['build_tools']))

    return analysis_result

def _parse_dependencies_from_package_json(content: str) -> List[str]:
    try:
        import json as _json
        data = _json.loads(content)
        deps = []
        for key in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
            if isinstance(data.get(key), dict):
                deps.extend(list(data[key].keys()))
        return list(sorted(set(deps)))
    except Exception:
        return []

def _parse_dependencies_from_requirements(content: str) -> List[str]:
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # 패키지명만 추출 (버전 제약 제거)
        name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('>')[0].split('<')[0].strip()
        if name:
            deps.append(name)
    return list(sorted(set(deps)))

async def collect_dependency_hints(owner: str, repo: str, token: Optional[str]) -> Dict[str, List[str]]:
    """핵심파일 선별 조회를 통해 외부 라이브러리 및 LLM 관련 힌트를 수집한다."""
    hints: Dict[str, List[str]] = {
        'external_libraries': [],
        'llm_hints': [],
        'frameworks': [],
        'build_tools': [],
        'deployment_configs': []
    }

    try:
        # 핵심파일 선별 조회
        core_files = await fetch_repo_core_files(owner, repo, token)

        # 핵심파일 내용 분석
        analysis_result = await analyze_core_files_content(owner, repo, core_files, token)

        # 의존성 정보 수집
        if 'npm' in analysis_result['dependencies']:
            npm_deps = analysis_result['dependencies']['npm']
            deps = {**npm_deps.get('dependencies', {}), **npm_deps.get('devDependencies', {})}
            hints['external_libraries'].extend(list(deps.keys()))

        if 'pip' in analysis_result['dependencies']:
            hints['external_libraries'].extend(analysis_result['dependencies']['pip'])

        # 프레임워크 및 빌드 도구 정보
        hints['frameworks'] = analysis_result['frameworks']
        hints['build_tools'] = analysis_result['build_tools']
        hints['deployment_configs'] = [config['type'] for config in analysis_result['deployment_configs']]

        # LLM 라이브러리 키워드 매핑
        llm_keywords = [
            'openai', 'google-generativeai', 'google.generativeai', 'vertexai',
            'anthropic', 'langchain', 'llama-index', 'transformers', 'cohere',
            'groq', 'mcp', 'claude', 'gpt', 'llama', 'gemini', 'palm'
        ]

        for lib in list(hints['external_libraries']):
            lower = lib.lower()
            if any(k in lower for k in llm_keywords):
                hints['llm_hints'].append(lib)

        # 중복 제거
        hints['external_libraries'] = list(sorted(set(hints['external_libraries'])))
        hints['llm_hints'] = list(sorted(set(hints['llm_hints'])))
        hints['frameworks'] = list(sorted(set(hints['frameworks'])))
        hints['build_tools'] = list(sorted(set(hints['build_tools'])))
        hints['deployment_configs'] = list(sorted(set(hints['deployment_configs'])))

    except Exception as e:
        print(f"핵심파일 분석 중 오류: {e}")
        # 기존 방식으로 fallback
        top_level_files = await fetch_repo_top_level_files(owner, repo, token)
        file_names = [f.get('name', '').lower() for f in (top_level_files or [])]

        # package.json
        if 'package.json' in file_names:
            content = await fetch_repo_file(owner, repo, 'package.json', token)
            pkgs = _parse_dependencies_from_package_json(content or '') if content else []
            if pkgs:
                hints['external_libraries'].extend(pkgs)

        # requirements.txt
        if 'requirements.txt' in file_names:
            content = await fetch_repo_file(owner, repo, 'requirements.txt', token)
            reqs = _parse_dependencies_from_requirements(content or '') if content else []
            if reqs:
                hints['external_libraries'].extend(reqs)

        # LLM 라이브러리 키워드 매핑
        llm_keywords = ['openai', 'google-generativeai', 'google.generativeai', 'vertexai', 'anthropic', 'langchain', 'llama-index', 'transformers', 'cohere', 'groq', 'mcp']
        for lib in list(hints['external_libraries']):
            lower = lib.lower()
            if any(k in lower for k in llm_keywords):
                hints['llm_hints'].append(lib)

        # 중복 제거
        hints['external_libraries'] = list(sorted(set(hints['external_libraries'])))
        hints['llm_hints'] = list(sorted(set(hints['llm_hints'])))

    return hints

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
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

    # Groq API 사용 (sk-proj-로 시작하는 키)
    if api_key.startswith('sk-proj-'):
        model = 'llama-3.1-70b-versatile'
        endpoint = 'https://api.groq.com/openai/v1/chat/completions'
    else:
        model = 'gpt-4o'
        endpoint = 'https://api.openai.com/v1/chat/completions'

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
        - 상단 파일 목록: {repo_data.get('toplevel_files', [])}

**주요 기능**
{repo_data.get('main_features', '기능 정보 없음')}

**파일 구조**
{repo_data.get('file_structure', '파일 구조 정보 없음')}

**개발자 활동**
{repo_data.get('developer_activity', '활동 정보 없음')}

        **중요한 지침:**
        - 기술 스택은 카테고리로 요약하되, 외부 라이브러리/LLM 항목은 구체 명칭으로 작성하세요.
        - README 정보가 부실하거나 모호하면 다음 힌트를 참고하여 보완하세요:
          - toplevel_files: 프레임워크/배포 방식 추정
          - external_libraries_hint: 의존성 파일에서 수집된 라이브러리 후보
          - llm_hints: LLM 관련 라이브러리 후보
        - 외부 라이브러리는 위 힌트를 활용해 구체적인 라이브러리명/서비스명을 기입하세요.
        - LLM 모델 정보는 라이브러리/플랫폼과 호출 방식을 근거와 함께 요약하세요.

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
                "readme_excerpt": repo.get('readme_excerpt', '')[:500] if repo.get('readme_excerpt') else '',
                "toplevel_files": repo.get('toplevel_files', []),
                "external_libraries_hint": repo.get('external_libraries_hint', []),
                "llm_hints": repo.get('llm_hints', [])
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
        - README 정보가 부실하거나 모호하면 다음 힌트를 참고하여 보완하세요:
          - toplevel_files: 상단 파일 목록으로 프레임워크/배포 방식을 유추
          - external_libraries_hint: package.json/requirements.txt에서 수집한 의존성 후보
          - llm_hints: LLM 관련 라이브러리 후보 (예: openai, google-generativeai, langchain 등)
        - 외부 라이브러리는 위 힌트를 활용해 구체적인 라이브러리명/서비스명으로 작성하세요
        - LLM 모델 정보는 라이브러리/플랫폼과 호출 방식을 근거와 함께 요약하세요

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
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(endpoint, json=payload, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        })
        response.raise_for_status()
        data = response.json()

        response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

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



async def generate_user_language_chart(username: str, token: Optional[str] = None) -> LanguageChartResponse:
    """사용자의 모든 레포지토리 언어 통계를 수집"""
    try:
        # 사용자의 모든 레포지토리 가져오기
        repos = await fetch_user_repos(username, token)
        if not repos:
            raise HTTPException(status_code=404, detail="공개 리포지토리를 찾을 수 없습니다.")

        # 모든 레포지토리의 언어 통계 수집
        all_languages = {}
        total_bytes = 0

        # 상위 10개 레포지토리만 분석 (성능 최적화)
        top_repos = [r for r in repos if not r.get('fork')][:10]

        for repo in top_repos:
            owner_login = repo.get('owner', {}).get('login', username)
            try:
                repo_languages = await fetch_repo_languages(owner_login, repo['name'], token)
                for lang, bytes_count in repo_languages.items():
                    all_languages[lang] = all_languages.get(lang, 0) + bytes_count
                    total_bytes += bytes_count
            except Exception as e:
                print(f"레포지토리 {repo['name']} 언어 통계 수집 실패: {e}")
                continue

        if not all_languages:
            raise HTTPException(status_code=404, detail="언어 통계를 찾을 수 없습니다.")

        # 언어 통계 처리
        processed_languages = process_language_stats(all_languages, total_bytes)

        return LanguageChartResponse(
            language_stats=processed_languages,
            total_bytes=total_bytes,
            original_stats=all_languages
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"언어 통계 수집 중 오류가 발생했습니다: {str(e)}")

async def generate_repo_language_chart(username: str, repo_name: str, token: Optional[str] = None) -> LanguageChartResponse:
    """특정 레포지토리의 언어 통계를 수집"""
    try:
        # 레포지토리 언어 통계 가져오기
        languages = await fetch_repo_languages(username, repo_name, token)

        if not languages:
            raise HTTPException(status_code=404, detail="언어 통계를 찾을 수 없습니다.")

        total_bytes = sum(languages.values())

        # 언어 통계 처리
        processed_languages = process_language_stats(languages, total_bytes)

        return LanguageChartResponse(
            language_stats=processed_languages,
            total_bytes=total_bytes,
            original_stats=languages
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"언어 통계 수집 중 오류가 발생했습니다: {str(e)}")

@router.post("/github/summary", response_model=GithubSummaryResponse)
async def github_summary(request: GithubSummaryRequest):
    """GitHub 사용자 요약"""
    # 토큰 사용량 초기화
    reset_token_usage()

    try:
        print(f"=== GitHub 검색 요청 시작 ===")
        print(f"원본 입력: {request.username}")
        print(f"원본 repo_name: {request.repo_name}")

        # 통일된 파싱 로직: URL과 유저이름 모두 동일한 방식으로 처리
        username = None
        repo_name = request.repo_name

        if request.username.startswith('https://github.com/'):
            # GitHub URL 파싱
            parsed = parse_github_url(request.username)
            if parsed:
                username, extracted_repo_name = parsed
                print(f"URL 파싱 결과 - username: {username}, extracted_repo_name: {extracted_repo_name}")
                # extracted_repo_name이 None이 아닌 경우에만 repo_name 설정
                if extracted_repo_name and not request.repo_name:
                    repo_name = extracted_repo_name
                    print(f"repo_name 설정됨: {repo_name}")
            else:
                raise HTTPException(status_code=400, detail="올바른 GitHub URL 형식이 아닙니다.")
        else:
            # 일반 유저이름 파싱
            username = resolve_username(request.username)
            if not username:
                raise HTTPException(status_code=400, detail="username이 필요합니다.")
            print(f"유저이름 파싱 결과 - username: {username}, repo_name: {repo_name}")

        # 최종 검증: username이 동일한지 확인
        print(f"최종 검증 - username: {username}, repo_name: {repo_name}")

        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN') or ''
        profile_url = f"https://github.com/{username}"
        profile_api_url = f"https://api.github.com/users/{username}"

        print(f"최종 처리 - username: {username}, repo_name: {repo_name}")

        # 언어 통계 데이터 생성
        language_stats: Dict[str, int] = {}
        language_total_bytes: int = 0
        try:
            if repo_name:
                # 특정 레포지토리 언어 통계
                chart_response = await generate_repo_language_chart(username, repo_name, github_token)
                language_stats = chart_response.language_stats
                language_total_bytes = chart_response.total_bytes
            else:
                # 사용자 전체 언어 통계
                chart_response = await generate_user_language_chart(username, github_token)
                language_stats = chart_response.language_stats
                language_total_bytes = chart_response.total_bytes
        except Exception as e:
            print(f"언어 통계 수집 실패: {e}")
            language_stats = {}
            language_total_bytes = 0

        # 통일된 검색 로직: 항상 동일한 우선순위로 분석 수행
        # 1. 특정 저장소가 지정된 경우에도 '전체 레포 분석 파이프라인'을 재사용하여 일관된 결과 생성
        if repo_name:
            print(f"1단계: 특정 저장소 분석(멀티 파이프라인 재사용) - {username}/{repo_name}")
            try:
                # 전체 레포 목록에서 대상 레포 탐색 후, 다중 레포 분석 입력 형식으로 단일 레포 분석
                print("특정 저장소 분석 전: 전체 레포 목록 조회")
                repos_list = await fetch_user_repos(username, github_token)
                if not repos_list:
                    raise HTTPException(status_code=404, detail="공개 리포지토리를 찾을 수 없습니다.")

                target_repo_meta = None
                target_repo_name_lower = repo_name.lower()
                for r in repos_list:
                    name = r.get('name', '')
                    full_name = r.get('full_name', '')
                    if name.lower() == target_repo_name_lower or full_name.lower().endswith(f"/{target_repo_name_lower}"):
                        target_repo_meta = r
                        break

                if not target_repo_meta:
                    raise HTTPException(status_code=404, detail=f"저장소 '{repo_name}'을 찾을 수 없습니다.")

                owner_login = target_repo_meta.get('owner', {}).get('login', username)

                # 다중 레포 분석 경로에서 사용하던 입력 데이터 수집(README 발췌 포함)
                languages, top_level_files, repo_readme = await asyncio.gather(
                    fetch_repo_languages(owner_login, repo_name, github_token),
                    fetch_repo_top_level_files(owner_login, repo_name, github_token),
                    fetch_github_readme(owner_login, repo_name, github_token),
                    return_exceptions=True
                )

                # README가 부실한 경우를 대비해 의존성 힌트 수집 (핵심파일 선별 조회 방식)
                dep_hints = await collect_dependency_hints(owner_login, repo_name, github_token)

                analysis_item = {
                    'name': target_repo_meta.get('name', repo_name),
                    'description': target_repo_meta.get('description', ''),
                    'html_url': target_repo_meta.get('html_url', f'https://github.com/{username}/{repo_name}'),
                    'stargazers_count': target_repo_meta.get('stargazers_count', 0),
                    'forks_count': target_repo_meta.get('forks_count', 0),
                    'language': target_repo_meta.get('language', '정보 없음'),
                    'languages': languages if not isinstance(languages, Exception) else {},
                    'toplevel_files': top_level_files if not isinstance(top_level_files, Exception) else [],
                    'readme_excerpt': (repo_readme['text'][:3000] if (repo_readme and not isinstance(repo_readme, Exception) and repo_readme.get('text')) else ''),
                    'external_libraries_hint': dep_hints.get('external_libraries', []),
                    'llm_hints': dep_hints.get('llm_hints', []),
                    'frameworks': dep_hints.get('frameworks', []),
                    'build_tools': dep_hints.get('build_tools', []),
                    'deployment_configs': dep_hints.get('deployment_configs', [])
                }

                # 아키텍처 분석 실행
                arch_result = await analyze_repository_architecture(owner_login, repo_name, github_token)

                # 아키텍처 분석 결과를 기존 분석 결과에 통합
                if arch_result:
                    analysis_item.update({
                        'architecture_topic': arch_result.topic,
                        'architecture_tech_stack': arch_result.tech_stack,
                        'architecture_external_libs': arch_result.external_libs,
                        'architecture_llm_models': arch_result.llm_models,
                        'architecture_structure': arch_result.architecture,
                        'architecture_opened_files': arch_result.opened_files,
                        'architecture_analysis_time': arch_result.analysis_time
                    })

                # 멀티 레포 분석 프롬프트를 사용하되, 대상 레포만 전달하여 동일한 추출 품질 확보
                summaries = await generate_unified_summary(username, None, None, [analysis_item])

                # detailed_analysis에 핵심파일 분석 결과와 아키텍처 분석 결과 포함
                detailed_analysis = {
                    'tech_stack': {
                        'languages': languages if not isinstance(languages, Exception) else {},
                        'frameworks': dep_hints.get('frameworks', []),
                        'build_tools': dep_hints.get('build_tools', []),
                        'deployment_configs': dep_hints.get('deployment_configs', [])
                    },
                    'dependencies': {
                        'external_libraries': dep_hints.get('external_libraries', []),
                        'llm_libraries': dep_hints.get('llm_hints', [])
                    },
                    'architecture_analysis': {
                        'total_repos_analyzed': 1,
                        'architecture_results': [
                            {
                                'owner': arch_result.owner,
                                'repo': arch_result.repo,
                                'topic': arch_result.topic,
                                'tech_stack': arch_result.tech_stack,
                                'external_libs': arch_result.external_libs,
                                'llm_models': arch_result.llm_models,
                                'architecture': arch_result.architecture,
                                'opened_files': arch_result.opened_files,
                                'analysis_time': arch_result.analysis_time
                            }
                        ] if arch_result else []
                    }
                }

                return GithubSummaryResponse(
                    profileUrl=profile_url,
                    profileApiUrl=profile_api_url,
                    source=f'repos_meta_filtered_{repo_name}',
                    summary=json.dumps(summaries, ensure_ascii=False),
                    detailed_analysis=detailed_analysis,
                    language_stats=language_stats,
                    language_total_bytes=language_total_bytes,
                    original_language_stats=chart_response.original_stats,
                    token_usage=get_token_usage()
                )

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"저장소 '{repo_name}'을 찾을 수 없습니다.")
                raise

        # 2. 프로필 README 분석 (저장소가 지정되지 않은 경우)
        print(f"2단계: 프로필 README 분석 시도 - {username}")
        try:
            profile_readme = await fetch_github_readme(username, username, github_token)
            if profile_readme and profile_readme.get('text'):
                print(f"프로필 README 발견 - 분석 진행")
                summaries = await generate_unified_summary(username, None, profile_readme, None)
                return GithubSummaryResponse(
                    profileUrl=profile_url,
                    profileApiUrl=profile_api_url,
                    source='profile_readme',
                    summary=json.dumps(summaries, ensure_ascii=False),
                    language_stats=language_stats,
                    language_total_bytes=language_total_bytes,
                    original_language_stats=chart_response.original_stats,
                    token_usage=get_token_usage()
                )
            else:
                print(f"프로필 README가 없습니다 - 리포지토리 메타데이터 분석으로 진행")
        except Exception as e:
            print(f"프로필 README 분석 중 오류: {e} - 리포지토리 메타데이터 분석으로 진행")

        # 3. 리포지토리 메타데이터 분석 (프로필 README가 없는 경우)
        print(f"3단계: 리포지토리 메타데이터 분석 - {username}")
        try:
            repos = await fetch_user_repos(username, github_token)
            if not repos:
                raise HTTPException(status_code=404, detail="공개 리포지토리를 찾을 수 없습니다.")

            print(f"발견된 리포지토리 수: {len(repos)}")
            # 상위 5개 리포 분석
            top_repos = [r for r in repos if not r.get('fork')][:5]
            print(f"분석할 상위 리포지토리 수: {len(top_repos)}")

            if not top_repos:
                # 포크된 리포지토리만 있는 경우 포크된 리포지토리도 포함
                top_repos = repos[:5]
                print(f"포크된 리포지토리 포함하여 분석: {len(top_repos)}개")

            analyses = []
            architecture_results = []  # 아키텍처 분석 결과 저장

            for repo in top_repos:
                owner_login = repo.get('owner', {}).get('login', username)

                # 기존 메타데이터 분석과 아키텍처 분석을 병렬로 실행
                languages, repo_readme, dep_hints, arch_result = await asyncio.gather(
                    fetch_repo_languages(owner_login, repo['name'], github_token),
                    fetch_github_readme(owner_login, repo['name'], github_token),
                    collect_dependency_hints(owner_login, repo['name'], github_token),
                    analyze_repository_architecture(owner_login, repo['name'], github_token),
                    return_exceptions=True
                )

                # 기존 메타데이터 분석 결과
                analysis_item = {
                    'name': repo['name'],
                    'description': repo.get('description', ''),
                    'html_url': repo['html_url'],
                    'stargazers_count': repo.get('stargazers_count', 0),
                    'forks_count': repo.get('forks_count', 0),
                    'language': repo.get('language', '정보 없음'),
                    'languages': languages if not isinstance(languages, Exception) else {},
                    'readme_excerpt': repo_readme['text'][:3000] if repo_readme and not isinstance(repo_readme, Exception) else '',
                    'external_libraries_hint': dep_hints.get('external_libraries', []) if not isinstance(dep_hints, Exception) else [],
                    'llm_hints': dep_hints.get('llm_hints', []) if not isinstance(dep_hints, Exception) else [],
                    'frameworks': dep_hints.get('frameworks', []) if not isinstance(dep_hints, Exception) else [],
                    'build_tools': dep_hints.get('build_tools', []) if not isinstance(dep_hints, Exception) else [],
                    'deployment_configs': dep_hints.get('deployment_configs', []) if not isinstance(dep_hints, Exception) else []
                }

                # 아키텍처 분석 결과가 성공적으로 완료된 경우 추가 정보 통합
                if not isinstance(arch_result, Exception) and arch_result:
                    analysis_item.update({
                        'architecture_topic': arch_result.topic,
                        'architecture_tech_stack': arch_result.tech_stack,
                        'architecture_external_libs': arch_result.external_libs,
                        'architecture_llm_models': arch_result.llm_models,
                        'architecture_structure': arch_result.architecture,
                        'architecture_opened_files': arch_result.opened_files,
                        'architecture_analysis_time': arch_result.analysis_time
                    })
                    architecture_results.append(arch_result)

                analyses.append(analysis_item)

            # 통합 요약 생성 (여러 레포지토리)
            summaries = await generate_unified_summary(username, None, None, analyses)

            # 전체 분석 결과에서 프레임워크, 빌드 도구, 배포 설정 정보 수집
            all_frameworks = []
            all_build_tools = []
            all_deployment_configs = []
            all_external_libraries = []
            all_llm_libraries = []

            for analysis in analyses:
                if 'frameworks' in analysis:
                    all_frameworks.extend(analysis.get('frameworks', []))
                if 'build_tools' in analysis:
                    all_build_tools.extend(analysis.get('build_tools', []))
                if 'deployment_configs' in analysis:
                    all_deployment_configs.extend(analysis.get('deployment_configs', []))
                if 'external_libraries_hint' in analysis:
                    all_external_libraries.extend(analysis.get('external_libraries_hint', []))
                if 'llm_hints' in analysis:
                    all_llm_libraries.extend(analysis.get('llm_hints', []))

            # 중복 제거
            all_frameworks = list(set(all_frameworks))
            all_build_tools = list(set(all_build_tools))
            all_deployment_configs = list(set(all_deployment_configs))
            all_external_libraries = list(set(all_external_libraries))
            all_llm_libraries = list(set(all_llm_libraries))

            # detailed_analysis에 핵심파일 분석 결과와 아키텍처 분석 결과 포함
            detailed_analysis = {
                'tech_stack': {
                    'languages': language_stats,
                    'frameworks': all_frameworks,
                    'build_tools': all_build_tools,
                    'deployment_configs': all_deployment_configs
                },
                'dependencies': {
                    'external_libraries': all_external_libraries,
                    'llm_libraries': all_llm_libraries
                },
                'architecture_analysis': {
                    'total_repos_analyzed': len(architecture_results),
                    'architecture_results': [
                        {
                            'owner': arch.owner,
                            'repo': arch.repo,
                            'topic': arch.topic,
                            'tech_stack': arch.tech_stack,
                            'external_libs': arch.external_libs,
                            'llm_models': arch.llm_models,
                            'architecture': arch.architecture,
                            'opened_files': arch.opened_files,
                            'analysis_time': arch.analysis_time
                        } for arch in architecture_results
                    ]
                }
            }

            return GithubSummaryResponse(
                profileUrl=profile_url,
                profileApiUrl=profile_api_url,
                source='repos_meta',
                summary=json.dumps(summaries, ensure_ascii=False),
                detailed_analysis=detailed_analysis,
                language_stats=language_stats,
                language_total_bytes=language_total_bytes,
                original_language_stats=chart_response.original_stats,
                token_usage=get_token_usage()
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"리포지토리 메타데이터 분석 중 오류: {e}")
            raise HTTPException(status_code=500, detail=f"리포지토리 분석 중 오류가 발생했습니다: {str(e)}")

    except HTTPException:
        raise
    except httpx.ReadTimeout:
        print("GitHub API 요청 타임아웃 발생")
        raise HTTPException(status_code=408, detail="요청이 시간 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except httpx.ConnectTimeout:
        print("GitHub API 연결 타임아웃 발생")
        raise HTTPException(status_code=408, detail="연결이 시간 초과되었습니다. 네트워크 상태를 확인해주세요.")
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

        # 전체 레포 목록에서 대상 레포 탐색 후 분석
        repos_list = await fetch_user_repos(username, github_token)
        if not repos_list:
            raise HTTPException(status_code=404, detail="공개 리포지토리를 찾을 수 없습니다.")

        target_repo_meta = None
        target_repo_name_lower = request.repo_name.lower()
        for r in repos_list:
            name = r.get('name', '')
            full_name = r.get('full_name', '')
            if name.lower() == target_repo_name_lower or full_name.lower().endswith(f"/{target_repo_name_lower}"):
                target_repo_meta = r
                break

        if not target_repo_meta:
            raise HTTPException(status_code=404, detail=f"저장소 '{request.repo_name}'을 찾을 수 없습니다.")

        owner_login = target_repo_meta.get('owner', {}).get('login', username)
        repo_data = target_repo_meta

        # 병렬로 모든 데이터 수집 (owner_login 기준)
        languages, files, commits, issues, pulls, readme = await asyncio.gather(
            fetch_repo_languages(owner_login, request.repo_name, github_token),
            fetch_repo_top_level_files(owner_login, request.repo_name, github_token),
            fetch_repo_commits(owner_login, request.repo_name, github_token),
            fetch_repo_issues(owner_login, request.repo_name, github_token),
            fetch_repo_pulls(owner_login, request.repo_name, github_token),
            fetch_github_readme(owner_login, request.repo_name, github_token),
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

        # 언어 통계 데이터 생성 (repo 전용)
        try:
            chart_response = await generate_repo_language_chart(owner_login, request.repo_name, github_token)
            language_stats = chart_response.language_stats
            language_total_bytes = chart_response.total_bytes
        except Exception:
            language_stats = languages or {}
            language_total_bytes = sum((languages or {}).values()) if languages else 0

        return GithubSummaryResponse(
            profileUrl=profile_url,
            profileApiUrl=profile_api_url,
            source=f'repo_analysis_{request.repo_name}',
            summary=json.dumps(summaries, ensure_ascii=False),
            language_stats=language_stats,
            language_total_bytes=language_total_bytes,
            original_language_stats=chart_response.original_stats,
            token_usage=None
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"저장소 '{request.repo_name}'을 찾을 수 없습니다.")
        raise
    except httpx.ReadTimeout:
        print("GitHub API 요청 타임아웃 발생")
        raise HTTPException(status_code=408, detail="요청이 시간 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except httpx.ConnectTimeout:
        print("GitHub API 연결 타임아웃 발생")
        raise HTTPException(status_code=408, detail="연결이 시간 초과되었습니다. 네트워크 상태를 확인해주세요.")
    except Exception as error:
        import traceback
        print(f"GitHub 저장소 분석 오류: {error}")
        print(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"저장소 분석 중 오류가 발생했습니다: {str(error)}")

@router.post("/github/architecture", response_model=GithubArchitectureResponse)
async def github_architecture_analysis(request: GithubArchitectureRequest):
    """GitHub 레포지토리 아키텍처 분석 (Planner-Executor 루프)"""
    try:
        print(f"=== 아키텍처 분석 시작 ===")
        print(f"분석 대상: {request.owner}/{request.repo}")

        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN') or ''

        # Planner-Executor 루프를 사용한 아키텍처 분석
        result = await analyze_repository_architecture(request.owner, request.repo, github_token)

        print(f"=== 아키텍처 분석 완료 ===")
        print(f"분석 시간: {result.analysis_time:.2f}초")
        print(f"열린 파일 수: {len(result.opened_files)}")
        print(f"주제: {result.topic}")
        print(f"기술 스택: {result.tech_stack}")
        print(f"외부 라이브러리: {result.external_libs}")
        print(f"LLM 모델: {result.llm_models}")

        return result

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"레포지토리 '{request.owner}/{request.repo}'을 찾을 수 없습니다.")
        elif e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="비공개 레포지토리입니다. 접근 권한이 필요합니다.")
        raise
    except httpx.ReadTimeout:
        print("GitHub API 요청 타임아웃 발생")
        raise HTTPException(status_code=408, detail="요청이 시간 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except httpx.ConnectTimeout:
        print("GitHub API 연결 타임아웃 발생")
        raise HTTPException(status_code=408, detail="연결이 시간 초과되었습니다. 네트워크 상태를 확인해주세요.")
    except Exception as error:
        import traceback
        print(f"아키텍처 분석 오류: {error}")
        print(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"아키텍처 분석 중 오류가 발생했습니다: {str(error)}")
