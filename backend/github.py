from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import base64
import json
import re
from typing import Optional, Dict, List, Any, Tuple
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import pickle
from collections import Counter
import math

# MongoDB 저장소 서비스와 해시 유틸리티 import
from services.github_storage_service import github_storage_service
from utils.github_hash_utils import (
    generate_file_hashes_from_github,
    compare_file_hashes,
    calculate_change_impact,
    should_trigger_full_reanalysis
)

router = APIRouter()

# 캐싱 시스템 추가
class AnalysisCache:
    """분석 결과 캐싱 시스템"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, username: str, repo_name: Optional[str] = None) -> str:
        """캐시 키 생성"""
        key_data = f"{username}:{repo_name or 'profile'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """캐시 파일 경로 반환"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    async def get_cached_analysis(self, username: str, repo_name: Optional[str] = None) -> Optional[Dict]:
        """캐시된 분석 결과 반환"""
        try:
            cache_key = self._get_cache_key(username, repo_name)
            cache_path = self._get_cache_path(cache_key)
            
            if not os.path.exists(cache_path):
                return None
            
            # 파일 수정 시간 확인 (TTL 체크)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - file_mtime > timedelta(hours=self.ttl_hours):
                os.remove(cache_path)  # 만료된 캐시 삭제
                return None
            
            # 캐시 파일 읽기
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
                print(f"캐시된 분석 결과 사용: {username}/{repo_name or 'profile'}")
                return cached_data
                
        except Exception as e:
            print(f"캐시 읽기 오류: {e}")
            return None
    
    async def cache_analysis(self, username: str, repo_name: Optional[str] = None, analysis: Dict = None):
        """분석 결과 캐싱"""
        try:
            if not analysis:
                return
                
            cache_key = self._get_cache_key(username, repo_name)
            cache_path = self._get_cache_path(cache_key)
            
            # 캐시 데이터에 타임스탬프 추가
            cache_data = {
                'analysis': analysis,
                'cached_at': datetime.now(),
                'username': username,
                'repo_name': repo_name
            }
            
            # 캐시 파일 저장
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
                
            print(f"분석 결과 캐싱 완료: {username}/{repo_name or 'profile'}")
            
        except Exception as e:
            print(f"캐시 저장 오류: {e}")

# 전역 캐시 인스턴스
analysis_cache = AnalysisCache()

# 로컬 AI 관련 함수들 제거 - GPT-4o 전용으로 변경

# 정적 코드 분석 시스템
class StaticCodeAnalyzer:
    """정적 코드 분석을 통한 품질 평가"""
    
    def __init__(self):
        self.quality_metrics = {}
    
    async def analyze_code_quality(self, owner: str, repo: str, token: str) -> Dict:
        """정적 코드 분석을 통한 품질 평가"""
        try:
            # 파일 구조 분석
            file_structure = await self._analyze_file_structure(owner, repo, token)
            
            # 코드 복잡도 분석
            complexity_metrics = await self._analyze_complexity(owner, repo, token)
            
            # 테스트 커버리지 추정
            test_coverage = await self._estimate_test_coverage(owner, repo, token)
            
            # 보안 취약점 스캔
            security_issues = await self._scan_security_vulnerabilities(owner, repo, token)
            
            return {
                'code_quality': {
                    'complexity': complexity_metrics.get('overall_complexity', 'medium'),
                    'maintainability': self._calculate_maintainability_score(file_structure, complexity_metrics),
                    'test_coverage': test_coverage,
                    'code_smells': complexity_metrics.get('code_smells', 0),
                    'security_issues': len(security_issues),
                    'file_structure_score': self._calculate_structure_score(file_structure)
                },
                'file_structure': file_structure,
                'complexity_metrics': complexity_metrics,
                'security_issues': security_issues
            }
        except Exception as e:
            print(f"정적 코드 분석 오류: {e}")
            return {'code_quality': {'error': str(e)}}
    
    async def _analyze_file_structure(self, owner: str, repo: str, token: str) -> Dict:
        """파일 구조 분석"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            
            structure = {
                'total_files': len(tree),
                'directories': {},
                'file_types': {},
                'config_files': [],
                'test_files': [],
                'documentation_files': []
            }
            
            for item in tree:
                path = item.get('path', '')
                name = item.get('name', '')
                
                # 파일 타입 분류
                if '.' in name:
                    ext = name.split('.')[-1].lower()
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
                # 디렉토리 분석
                if item.get('type') == 'tree':
                    dir_name = path.split('/')[-1]
                    structure['directories'][dir_name] = structure['directories'].get(dir_name, 0) + 1
                
                # 특수 파일 분류
                if any(keyword in name.lower() for keyword in ['test', 'spec', 'specs']):
                    structure['test_files'].append(path)
                elif any(keyword in name.lower() for keyword in ['readme', 'docs', 'documentation']):
                    structure['documentation_files'].append(path)
                elif any(keyword in name.lower() for keyword in ['config', 'settings', '.env']):
                    structure['config_files'].append(path)
            
            return structure
        except Exception as e:
            print(f"파일 구조 분석 오류: {e}")
            return {}
    
    async def _analyze_complexity(self, owner: str, repo: str, token: str) -> Dict:
        """코드 복잡도 분석"""
        try:
            # 주요 소스 파일들 분석
            source_files = await self._get_source_files(owner, repo, token)
            
            complexity_metrics = {
                'overall_complexity': 'low',
                'code_smells': 0,
                'long_functions': 0,
                'deep_nesting': 0,
                'duplicate_code': 0
            }
            
            total_lines = 0
            total_functions = 0
            
            for file_path in source_files[:10]:  # 상위 10개 파일만 분석
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_metrics = self._analyze_file_complexity(content, file_path)
                        total_lines += file_metrics.get('lines', 0)
                        total_functions += file_metrics.get('functions', 0)
                        complexity_metrics['code_smells'] += file_metrics.get('smells', 0)
                        complexity_metrics['long_functions'] += file_metrics.get('long_functions', 0)
                        complexity_metrics['deep_nesting'] += file_metrics.get('deep_nesting', 0)
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            # 전체 복잡도 계산
            if total_lines > 0:
                avg_complexity = complexity_metrics['code_smells'] / total_lines
                if avg_complexity > 0.1:
                    complexity_metrics['overall_complexity'] = 'high'
                elif avg_complexity > 0.05:
                    complexity_metrics['overall_complexity'] = 'medium'
                else:
                    complexity_metrics['overall_complexity'] = 'low'
            
            return complexity_metrics
        except Exception as e:
            print(f"복잡도 분석 오류: {e}")
            return {'overall_complexity': 'unknown'}
    
    async def _get_source_files(self, owner: str, repo: str, token: str) -> List[str]:
        """소스 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            source_extensions = ['.js', '.ts', '.py', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']
            
            source_files = []
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if any(path.endswith(ext) for ext in source_extensions):
                        source_files.append(path)
            
            return source_files
        except Exception as e:
            print(f"소스 파일 목록 가져오기 오류: {e}")
            return []
    
    def _analyze_file_complexity(self, content: str, file_path: str) -> Dict:
        """개별 파일 복잡도 분석"""
        lines = content.split('\n')
        
        metrics = {
            'lines': len(lines),
            'functions': 0,
            'smells': 0,
            'long_functions': 0,
            'deep_nesting': 0
        }
        
        # 간단한 복잡도 분석
        for line in lines:
            line = line.strip()
            
            # 함수 정의 감지
            if any(keyword in line for keyword in ['function ', 'def ', 'class ', 'async def ']):
                metrics['functions'] += 1
            
            # 긴 함수 감지 (20줄 이상)
            if len(line) > 100:
                metrics['smells'] += 1
            
            # 깊은 중첩 감지
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 8:
                metrics['deep_nesting'] += 1
        
        return metrics
    
    async def _estimate_test_coverage(self, owner: str, repo: str, token: str) -> int:
        """테스트 커버리지 추정"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            
            test_files = 0
            source_files = 0
            
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if any(keyword in path.lower() for keyword in ['test', 'spec', 'specs']):
                        test_files += 1
                    elif any(path.endswith(ext) for ext in ['.js', '.ts', '.py', '.java']):
                        source_files += 1
            
            if source_files > 0:
                return min(100, int((test_files / source_files) * 100))
            return 0
        except Exception as e:
            print(f"테스트 커버리지 추정 오류: {e}")
            return 0
    
    async def _scan_security_vulnerabilities(self, owner: str, repo: str, token: str) -> List[Dict]:
        """보안 취약점 스캔"""
        try:
            # 주요 설정 파일들 확인
            config_files = ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 'Dockerfile']
            vulnerabilities = []
            
            for config_file in config_files:
                try:
                    content = await fetch_github_file_content(owner, repo, config_file, token)
                    if content:
                        file_vulns = self._scan_file_vulnerabilities(content, config_file)
                        vulnerabilities.extend(file_vulns)
                except Exception as file_error:
                    # 파일이 존재하지 않거나 접근할 수 없는 경우 무시
                    continue
            
            return vulnerabilities
        except Exception as e:
            print(f"보안 취약점 스캔 오류: {e}")
            return []
    
    def _scan_file_vulnerabilities(self, content: str, filename: str) -> List[Dict]:
        """파일별 보안 취약점 스캔"""
        vulnerabilities = []
        
        # 하드코딩된 비밀번호/키 감지
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'hardcoded_credentials',
                    'severity': 'high',
                    'file': filename,
                    'description': '하드코딩된 비밀번호 또는 API 키 발견'
                })
        
        return vulnerabilities
    
    def _calculate_maintainability_score(self, file_structure: Dict, complexity_metrics: Dict) -> str:
        """유지보수성 점수 계산"""
        score = 100
        
        # 파일 구조 점수
        if file_structure.get('total_files', 0) > 1000:
            score -= 20
        elif file_structure.get('total_files', 0) > 500:
            score -= 10
        
        # 복잡도 점수
        if complexity_metrics.get('overall_complexity') == 'high':
            score -= 30
        elif complexity_metrics.get('overall_complexity') == 'medium':
            score -= 15
        
        # 테스트 파일 점수
        test_ratio = len(file_structure.get('test_files', [])) / max(1, file_structure.get('total_files', 1))
        if test_ratio < 0.1:
            score -= 20
        elif test_ratio < 0.2:
            score -= 10
        
        if score >= 80:
            return 'high'
        elif score >= 60:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_structure_score(self, file_structure: Dict) -> int:
        """파일 구조 점수 계산"""
        score = 100
        
        # 문서화 점수
        doc_files = len(file_structure.get('documentation_files', []))
        if doc_files == 0:
            score -= 20
        elif doc_files < 3:
            score -= 10
        
        # 설정 파일 점수
        config_files = len(file_structure.get('config_files', []))
        if config_files == 0:
            score -= 10
        
        return max(0, score)

# 실제 사용 패턴 분석 시스템 (현재 사용되지 않음)
class UsagePatternAnalyzer:
    """실제 코드에서 라이브러리 사용 패턴 분석"""
    
    def __init__(self):
        self.import_patterns = {
            'javascript': [
                r'import\s+.*?from\s+["\']([^"\']+)["\']',
                r'require\s*\(\s*["\']([^"\']+)["\']\s*\)',
                r'import\s+["\']([^"\']+)["\']'
            ],
            'python': [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
            ],
            'java': [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*);',
                r'import\s+static\s+([a-zA-Z_][a-zA-Z0-9_.]*);'
            ]
        }
    
    async def analyze_actual_usage(self, owner: str, repo: str, token: str) -> Dict:
        """실제 코드에서 라이브러리 사용 패턴 분석"""
        try:
            # 소스 파일들 가져오기
            source_files = await self._get_source_files(owner, repo, token)
            
            usage_analysis = {
                'actual_imports': {},
                'unused_dependencies': [],
                'import_frequency': {},
                'framework_usage': {},
                'api_usage': {}
            }
            
            # 각 파일별 import 분석
            for file_path in source_files[:20]:  # 상위 20개 파일만 분석
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_usage = self._analyze_file_imports(content, file_path)
                        
                        # 실제 import 수집
                        for lang, imports in file_usage.items():
                            if lang not in usage_analysis['actual_imports']:
                                usage_analysis['actual_imports'][lang] = []
                            usage_analysis['actual_imports'][lang].extend(imports)
                            
                            # 사용 빈도 계산
                            for imp in imports:
                                usage_analysis['import_frequency'][imp] = usage_analysis['import_frequency'].get(imp, 0) + 1
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            # 중복 제거
            for lang in usage_analysis['actual_imports']:
                usage_analysis['actual_imports'][lang] = list(set(usage_analysis['actual_imports'][lang]))
            
            # 프레임워크 사용 패턴 분석
            usage_analysis['framework_usage'] = self._analyze_framework_usage(usage_analysis['actual_imports'])
            
            # API 사용 패턴 분석
            usage_analysis['api_usage'] = self._analyze_api_usage(usage_analysis['actual_imports'])
            
            return usage_analysis
            
        except Exception as e:
            print(f"실제 사용 패턴 분석 오류: {e}")
            return {}
    
    async def _get_source_files(self, owner: str, repo: str, token: str) -> List[str]:
        """소스 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            
            source_files = []
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if any(path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c']):
                        source_files.append(path)
            
            return source_files
        except Exception as e:
            print(f"소스 파일 목록 가져오기 오류: {e}")
            return []
    
    def _analyze_file_imports(self, content: str, file_path: str) -> Dict:
        """파일별 import 분석"""
        imports = {
            'javascript': [],
            'python': [],
            'java': []
        }
        
        # 파일 확장자로 언어 판단
        if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            lang = 'javascript'
        elif file_path.endswith('.py'):
            lang = 'python'
        elif file_path.endswith('.java'):
            lang = 'java'
        else:
            return imports
        
        # 언어별 import 패턴 매칭
        patterns = self.import_patterns.get(lang, [])
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    imports[lang].extend(match)
                else:
                    imports[lang].append(match)
        
        return imports
    
    def _analyze_framework_usage(self, actual_imports: Dict) -> Dict:
        """프레임워크 사용 패턴 분석"""
        framework_usage = {}
        
        # JavaScript/TypeScript 프레임워크
        js_imports = actual_imports.get('javascript', [])
        if any('react' in imp.lower() for imp in js_imports):
            framework_usage['react'] = True
        if any('vue' in imp.lower() for imp in js_imports):
            framework_usage['vue'] = True
        if any('angular' in imp.lower() for imp in js_imports):
            framework_usage['angular'] = True
        if any('express' in imp.lower() for imp in js_imports):
            framework_usage['express'] = True
        
        # Python 프레임워크
        py_imports = actual_imports.get('python', [])
        if any('django' in imp.lower() for imp in py_imports):
            framework_usage['django'] = True
        if any('flask' in imp.lower() for imp in py_imports):
            framework_usage['flask'] = True
        if any('fastapi' in imp.lower() for imp in py_imports):
            framework_usage['fastapi'] = True
        
        return framework_usage
    
    def _analyze_api_usage(self, actual_imports: Dict) -> Dict:
        """API 사용 패턴 분석"""
        api_usage = {}
        
        all_imports = []
        for imports in actual_imports.values():
            all_imports.extend(imports)
        
        # API 관련 라이브러리 감지
        api_keywords = {
            'http': 'HTTP 클라이언트',
            'axios': 'Axios HTTP 클라이언트',
            'fetch': 'Fetch API',
            'requests': 'Python Requests',
            'urllib': 'Python urllib',
            'socket': '소켓 통신',
            'websocket': 'WebSocket',
            'grpc': 'gRPC',
            'graphql': 'GraphQL'
        }
        
        for keyword, description in api_keywords.items():
            if any(keyword in imp.lower() for imp in all_imports):
                api_usage[keyword] = description
        
        return api_usage

# 플러그인 시스템 (현재 사용되지 않음)
class AnalysisPlugin:
    """분석 플러그인 기본 클래스"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
    
    async def analyze(self, owner: str, repo: str, token: str, repo_data: Dict) -> Dict:
        """플러그인별 분석 로직"""
        raise NotImplementedError
    
    def can_handle(self, repo_data: Dict) -> bool:
        """이 플러그인이 해당 레포지토리를 처리할 수 있는지 확인"""
        raise NotImplementedError

class ReactPlugin(AnalysisPlugin):
    """React 프로젝트 특화 분석"""
    
    def __init__(self):
        super().__init__("React", priority=10)
    
    def can_handle(self, repo_data: Dict) -> bool:
        frameworks = repo_data.get('frameworks', [])
        return 'React' in frameworks or any('react' in f.lower() for f in frameworks)
    
    async def analyze(self, owner: str, repo: str, token: str, repo_data: Dict) -> Dict:
        try:
            # React 특화 분석
            hooks_usage = await self._analyze_hooks_usage(owner, repo, token)
            component_structure = await self._analyze_component_structure(owner, repo, token)
            
            return {
                'react_analysis': {
                    'hooks_usage': hooks_usage,
                    'component_structure': component_structure,
                    'state_management': self._detect_state_management(repo_data),
                    'routing': self._detect_routing(repo_data)
                }
            }
        except Exception as e:
            print(f"React 플러그인 분석 오류: {e}")
            return {}
    
    async def _analyze_hooks_usage(self, owner: str, repo: str, token: str) -> Dict:
        """React Hooks 사용 패턴 분석"""
        hooks = ['useState', 'useEffect', 'useContext', 'useReducer', 'useCallback', 'useMemo']
        usage = {}
        
        try:
            source_files = await self._get_react_files(owner, repo, token)
            for file_path in source_files[:10]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        for hook in hooks:
                            if hook in content:
                                usage[hook] = usage.get(hook, 0) + 1
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
        except Exception as e:
            print(f"Hooks 분석 오류: {e}")
        
        return usage
    
    async def _analyze_component_structure(self, owner: str, repo: str, token: str) -> Dict:
        """컴포넌트 구조 분석"""
        try:
            source_files = await self._get_react_files(owner, repo, token)
            
            structure = {
                'functional_components': 0,
                'class_components': 0,
                'custom_hooks': 0
            }
            
            for file_path in source_files[:10]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        if 'function ' in content or 'const ' in content:
                            structure['functional_components'] += 1
                        if 'class ' in content and 'extends' in content:
                            structure['class_components'] += 1
                        if 'use' in content and 'function' in content:
                            structure['custom_hooks'] += 1
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return structure
        except Exception as e:
            print(f"컴포넌트 구조 분석 오류: {e}")
            return {}
    
    async def _get_react_files(self, owner: str, repo: str, token: str) -> List[str]:
        """React 관련 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            react_files = []
            
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if path.endswith(('.jsx', '.tsx', '.js', '.ts')):
                        react_files.append(path)
            
            return react_files
        except Exception as e:
            print(f"React 파일 목록 가져오기 오류: {e}")
            return []
    
    def _detect_state_management(self, repo_data: Dict) -> str:
        """상태 관리 라이브러리 감지"""
        external_libs = repo_data.get('external_libraries_hint', [])
        
        if any('redux' in lib.lower() for lib in external_libs):
            return 'Redux'
        elif any('zustand' in lib.lower() for lib in external_libs):
            return 'Zustand'
        elif any('recoil' in lib.lower() for lib in external_libs):
            return 'Recoil'
        elif any('jotai' in lib.lower() for lib in external_libs):
            return 'Jotai'
        else:
            return 'useState/useContext'
    
    def _detect_routing(self, repo_data: Dict) -> str:
        """라우팅 라이브러리 감지"""
        external_libs = repo_data.get('external_libraries_hint', [])
        
        if any('react-router' in lib.lower() for lib in external_libs):
            return 'React Router'
        elif any('next' in lib.lower() for lib in external_libs):
            return 'Next.js Router'
        else:
            return '기본 라우팅'

class PythonPlugin(AnalysisPlugin):
    """Python 프로젝트 특화 분석"""
    
    def __init__(self):
        super().__init__("Python", priority=10)
    
    def can_handle(self, repo_data: Dict) -> bool:
        language = repo_data.get('language', '')
        return language.lower() == 'python'
    
    async def analyze(self, owner: str, repo: str, token: str, repo_data: Dict) -> Dict:
        try:
            # Python 특화 분석
            async_usage = await self._analyze_async_usage(owner, repo, token)
            framework_analysis = self._analyze_framework(repo_data)
            
            return {
                'python_analysis': {
                    'async_usage': async_usage,
                    'framework_analysis': framework_analysis,
                    'package_management': self._detect_package_manager(repo_data)
                }
            }
        except Exception as e:
            print(f"Python 플러그인 분석 오류: {e}")
            return {}
    
    async def _analyze_async_usage(self, owner: str, repo: str, token: str) -> Dict:
        """비동기 사용 패턴 분석"""
        try:
            source_files = await self._get_python_files(owner, repo, token)
            
            async_metrics = {
                'async_functions': 0,
                'await_usage': 0,
                'asyncio_imports': 0
            }
            
            for file_path in source_files[:10]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        if 'async def' in content:
                            async_metrics['async_functions'] += 1
                        if 'await ' in content:
                            async_metrics['await_usage'] += 1
                        if 'import asyncio' in content:
                            async_metrics['asyncio_imports'] += 1
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return async_metrics
        except Exception as e:
            print(f"비동기 사용 분석 오류: {e}")
            return {}
    
    async def _get_python_files(self, owner: str, repo: str, token: str) -> List[str]:
        """Python 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            python_files = []
            
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if path.endswith('.py'):
                        python_files.append(path)
            
            return python_files
        except Exception as e:
            print(f"Python 파일 목록 가져오기 오류: {e}")
            return []
    
    def _analyze_framework(self, repo_data: Dict) -> Dict:
        """프레임워크 분석"""
        frameworks = repo_data.get('frameworks', [])
        
        analysis = {
            'web_framework': None,
            'has_orm': False,
            'has_api': False
        }
        
        if 'Django' in frameworks:
            analysis['web_framework'] = 'Django'
            analysis['has_orm'] = True
        elif 'Flask' in frameworks:
            analysis['web_framework'] = 'Flask'
        elif 'FastAPI' in frameworks:
            analysis['web_framework'] = 'FastAPI'
            analysis['has_api'] = True
        
        return analysis
    
    def _detect_package_manager(self, repo_data: Dict) -> str:
        """패키지 관리자 감지"""
        toplevel_files = repo_data.get('toplevel_files', [])
        
        if 'requirements.txt' in toplevel_files:
            return 'pip'
        elif 'pyproject.toml' in toplevel_files:
            return 'poetry'
        elif 'Pipfile' in toplevel_files:
            return 'pipenv'
        else:
            return 'unknown'

# 플러그인 매니저
class PluginManager:
    """분석 플러그인 관리자"""
    
    def __init__(self):
        self.plugins = []
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """기본 플러그인 등록"""
        self.register_plugin(ReactPlugin())
        self.register_plugin(PythonPlugin())
    
    def register_plugin(self, plugin: AnalysisPlugin):
        """플러그인 등록"""
        self.plugins.append(plugin)
        # 우선순위별 정렬
        self.plugins.sort(key=lambda x: x.priority, reverse=True)
    
    async def analyze_with_plugins(self, owner: str, repo: str, token: str, repo_data: Dict) -> Dict:
        """플러그인을 사용한 분석"""
        plugin_results = {}
        
        for plugin in self.plugins:
            try:
                if plugin.can_handle(repo_data):
                    result = await plugin.analyze(owner, repo, token, repo_data)
                    if result:
                        plugin_results[plugin.name] = result
            except Exception as e:
                print(f"플러그인 {plugin.name} 분석 오류: {e}")
        
        return plugin_results

# 의존성 그래프 분석 시스템 (현재 사용되지 않음)
class DependencyGraphAnalyzer:
    """의존성 그래프 분석을 통한 복잡한 관계 파악"""
    
    def __init__(self):
        self.dependency_patterns = {
            'javascript': {
                'import': r'import\s+.*?from\s+["\']([^"\']+)["\']',
                'require': r'require\s*\(\s*["\']([^"\']+)["\']\s*\)',
                'export': r'export\s+.*?from\s+["\']([^"\']+)["\']'
            },
            'python': {
                'import': r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                'from_import': r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                'relative_import': r'from\s+\.([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            },
            'java': {
                'import': r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*);',
                'package': r'package\s+([a-zA-Z_][a-zA-Z0-9_.]*);'
            }
        }
    
    async def analyze_dependency_graph(self, owner: str, repo: str, token: str) -> Dict:
        """의존성 그래프 분석"""
        try:
            # 파일 구조 분석
            file_structure = await self._analyze_file_structure(owner, repo, token)
            
            # 의존성 관계 분석
            dependencies = await self._analyze_dependencies(owner, repo, token)
            
            # 순환 의존성 검사
            circular_deps = self._detect_circular_dependencies(dependencies)
            
            # 의존성 복잡도 계산
            complexity_metrics = self._calculate_dependency_complexity(dependencies)
            
            # 모듈 간 결합도 분석
            coupling_analysis = self._analyze_module_coupling(dependencies)
            
            return {
                'dependency_graph': {
                    'nodes': list(dependencies.keys()),
                    'edges': self._extract_edges(dependencies),
                    'circular_dependencies': circular_deps,
                    'complexity_metrics': complexity_metrics,
                    'coupling_analysis': coupling_analysis
                },
                'file_structure': file_structure,
                'dependencies': dependencies
            }
        except Exception as e:
            print(f"의존성 그래프 분석 오류: {e}")
            return {}
    
    async def _analyze_file_structure(self, owner: str, repo: str, token: str) -> Dict:
        """파일 구조 분석"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            
            structure = {
                'files': [],
                'directories': [],
                'modules': {},
                'entry_points': []
            }
            
            for item in tree:
                path = item.get('path', '')
                name = item.get('name', '')
                
                if item.get('type') == 'blob':
                    structure['files'].append(path)
                    
                    # 모듈 식별
                    module_name = self._extract_module_name(path)
                    if module_name:
                        structure['modules'][module_name] = path
                    
                    # 진입점 식별
                    if self._is_entry_point(name):
                        structure['entry_points'].append(path)
                
                elif item.get('type') == 'tree':
                    structure['directories'].append(path)
            
            return structure
        except Exception as e:
            print(f"파일 구조 분석 오류: {e}")
            return {}
    
    async def _analyze_dependencies(self, owner: str, repo: str, token: str) -> Dict:
        """의존성 관계 분석"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            dependencies = {}
            
            for file_path in source_files[:30]:  # 상위 30개 파일만 분석
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_deps = self._extract_file_dependencies(content, file_path)
                        if file_deps:
                            dependencies[file_path] = file_deps
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return dependencies
        except Exception as e:
            print(f"의존성 분석 오류: {e}")
            return {}
    
    async def _get_source_files(self, owner: str, repo: str, token: str) -> List[str]:
        """소스 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            source_files = []
            
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if any(path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java']):
                        source_files.append(path)
            
            return source_files
        except Exception as e:
            print(f"소스 파일 목록 가져오기 오류: {e}")
            return []
    
    def _extract_file_dependencies(self, content: str, file_path: str) -> List[str]:
        """파일별 의존성 추출"""
        dependencies = []
        
        # 파일 확장자로 언어 판단
        if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            lang = 'javascript'
        elif file_path.endswith('.py'):
            lang = 'python'
        elif file_path.endswith('.java'):
            lang = 'java'
        else:
            return dependencies
        
        patterns = self.dependency_patterns.get(lang, {})
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    dependencies.extend(match)
                else:
                    dependencies.append(match)
        
        return list(set(dependencies))  # 중복 제거
    
    def _extract_module_name(self, file_path: str) -> Optional[str]:
        """파일 경로에서 모듈명 추출"""
        if not file_path:
            return None
        
        # 파일명에서 확장자 제거
        name = os.path.basename(file_path)
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # 특수 파일 제외
        if name in ['index', 'main', '__init__']:
            return None
        
        return name
    
    def _is_entry_point(self, filename: str) -> bool:
        """진입점 파일인지 확인"""
        entry_points = ['index.js', 'main.js', 'app.js', 'main.py', 'app.py', 'Main.java']
        return filename in entry_points
    
    def _detect_circular_dependencies(self, dependencies: Dict) -> List[List[str]]:
        """순환 의존성 검사"""
        try:
            # 그래프 생성
            graph = {}
            for file_path, deps in dependencies.items():
                graph[file_path] = []
                for dep in deps:
                    # 의존성을 파일 경로로 변환 시도
                    dep_file = self._resolve_dependency_to_file(dep, dependencies.keys())
                    if dep_file:
                        graph[file_path].append(dep_file)
            
            # DFS로 순환 의존성 검사
            visited = set()
            rec_stack = set()
            circular_deps = []
            
            def dfs(node, path):
                if node in rec_stack:
                    # 순환 발견
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    circular_deps.append(cycle)
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    dfs(neighbor, path + [node])
                
                rec_stack.remove(node)
            
            for node in graph:
                if node not in visited:
                    dfs(node, [])
            
            return circular_deps
        except Exception as e:
            print(f"순환 의존성 검사 오류: {e}")
            return []
    
    def _resolve_dependency_to_file(self, dep: str, files: List[str]) -> Optional[str]:
        """의존성을 파일 경로로 해석"""
        # 간단한 매칭 로직
        for file_path in files:
            if dep in file_path or dep in os.path.basename(file_path):
                return file_path
        return None
    
    def _calculate_dependency_complexity(self, dependencies: Dict) -> Dict:
        """의존성 복잡도 계산"""
        if not dependencies:
            return {}
        
        total_files = len(dependencies)
        total_deps = sum(len(deps) for deps in dependencies.values())
        
        # 평균 의존성 수
        avg_deps = total_deps / total_files if total_files > 0 else 0
        
        # 최대 의존성 수
        max_deps = max(len(deps) for deps in dependencies.values()) if dependencies else 0
        
        # 복잡도 등급
        if avg_deps > 10:
            complexity_level = 'high'
        elif avg_deps > 5:
            complexity_level = 'medium'
        else:
            complexity_level = 'low'
        
        return {
            'total_files': total_files,
            'total_dependencies': total_deps,
            'average_dependencies': round(avg_deps, 2),
            'max_dependencies': max_deps,
            'complexity_level': complexity_level
        }
    
    def _analyze_module_coupling(self, dependencies: Dict) -> Dict:
        """모듈 간 결합도 분석"""
        coupling_metrics = {
            'high_coupling_modules': [],
            'low_coupling_modules': [],
            'coupling_scores': {}
        }
        
        for file_path, deps in dependencies.items():
            coupling_score = len(deps)
            coupling_metrics['coupling_scores'][file_path] = coupling_score
            
            if coupling_score > 5:
                coupling_metrics['high_coupling_modules'].append(file_path)
            elif coupling_score <= 2:
                coupling_metrics['low_coupling_modules'].append(file_path)
        
        return coupling_metrics
    
    def _extract_edges(self, dependencies: Dict) -> List[Dict]:
        """의존성 그래프의 엣지 추출"""
        edges = []
        for source, deps in dependencies.items():
            for dep in deps:
                edges.append({
                    'source': source,
                    'target': dep,
                    'type': 'dependency'
                })
        return edges

# 성능 메트릭 분석 시스템 (현재 사용되지 않음)
class PerformanceMetricsAnalyzer:
    """성능 메트릭 분석을 통한 실제 성능 평가"""
    
    def __init__(self):
        self.performance_patterns = {
            'javascript': {
                'async_operations': [
                    r'async\s+function',
                    r'await\s+',
                    r'Promise\.',
                    r'setTimeout\(',
                    r'setInterval\('
                ],
                'memory_usage': [
                    r'new\s+Array\(',
                    r'new\s+Object\(',
                    r'JSON\.parse\(',
                    r'JSON\.stringify\('
                ],
                'dom_operations': [
                    r'document\.',
                    r'getElementById\(',
                    r'querySelector\(',
                    r'addEventListener\('
                ]
            },
            'python': {
                'async_operations': [
                    r'async\s+def',
                    r'await\s+',
                    r'asyncio\.',
                    r'threading\.',
                    r'multiprocessing\.'
                ],
                'memory_usage': [
                    r'list\(\)',
                    r'dict\(\)',
                    r'open\(',
                    r'with\s+open\('
                ],
                'io_operations': [
                    r'requests\.',
                    r'urllib\.',
                    r'socket\.',
                    r'subprocess\.'
                ]
            }
        }
    
    async def analyze_performance_metrics(self, owner: str, repo: str, token: str) -> Dict:
        """성능 메트릭 분석"""
        try:
            # 코드 성능 패턴 분석
            performance_patterns = await self._analyze_performance_patterns(owner, repo, token)
            
            # 파일 크기 및 복잡도 분석
            file_metrics = await self._analyze_file_metrics(owner, repo, token)
            
            # 알고리즘 복잡도 추정
            algorithm_complexity = await self._analyze_algorithm_complexity(owner, repo, token)
            
            # 메모리 사용 패턴 분석
            memory_patterns = await self._analyze_memory_patterns(owner, repo, token)
            
            # 네트워크/IO 패턴 분석
            io_patterns = await self._analyze_io_patterns(owner, repo, token)
            
            return {
                'performance_metrics': {
                    'overall_score': self._calculate_performance_score(performance_patterns, file_metrics),
                    'performance_patterns': performance_patterns,
                    'file_metrics': file_metrics,
                    'algorithm_complexity': algorithm_complexity,
                    'memory_patterns': memory_patterns,
                    'io_patterns': io_patterns
                }
            }
        except Exception as e:
            print(f"성능 메트릭 분석 오류: {e}")
            return {}
    
    async def _analyze_performance_patterns(self, owner: str, repo: str, token: str) -> Dict:
        """성능 패턴 분석"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            patterns = {
                'async_operations': 0,
                'memory_operations': 0,
                'dom_operations': 0,
                'io_operations': 0,
                'performance_issues': []
            }
            
            for file_path in source_files[:20]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_patterns = self._analyze_file_performance_patterns(content, file_path)
                        
                        patterns['async_operations'] += file_patterns.get('async_operations', 0)
                        patterns['memory_operations'] += file_patterns.get('memory_operations', 0)
                        patterns['dom_operations'] += file_patterns.get('dom_operations', 0)
                        patterns['io_operations'] += file_patterns.get('io_operations', 0)
                        patterns['performance_issues'].extend(file_patterns.get('performance_issues', []))
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return patterns
        except Exception as e:
            print(f"성능 패턴 분석 오류: {e}")
            return {}
    
    async def _get_source_files(self, owner: str, repo: str, token: str) -> List[str]:
        """소스 파일 목록 가져오기"""
        try:
            tree = await fetch_github_tree(owner, repo, token)
            source_files = []
            
            for item in tree:
                if item.get('type') == 'blob':
                    path = item.get('path', '')
                    if any(path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java']):
                        source_files.append(path)
            
            return source_files
        except Exception as e:
            print(f"소스 파일 목록 가져오기 오류: {e}")
            return []
    
    def _analyze_file_performance_patterns(self, content: str, file_path: str) -> Dict:
        """파일별 성능 패턴 분석"""
        patterns = {
            'async_operations': 0,
            'memory_operations': 0,
            'dom_operations': 0,
            'io_operations': 0,
            'performance_issues': []
        }
        
        # 파일 확장자로 언어 판단
        if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            lang = 'javascript'
        elif file_path.endswith('.py'):
            lang = 'python'
        else:
            return patterns
        
        lang_patterns = self.performance_patterns.get(lang, {})
        
        for pattern_type, pattern_list in lang_patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, content, re.MULTILINE)
                if pattern_type == 'async_operations':
                    patterns['async_operations'] += len(matches)
                elif pattern_type == 'memory_usage':
                    patterns['memory_operations'] += len(matches)
                elif pattern_type == 'dom_operations':
                    patterns['dom_operations'] += len(matches)
                elif pattern_type == 'io_operations':
                    patterns['io_operations'] += len(matches)
        
        # 성능 이슈 감지
        performance_issues = self._detect_performance_issues(content, file_path)
        patterns['performance_issues'] = performance_issues
        
        return patterns
    
    def _detect_performance_issues(self, content: str, file_path: str) -> List[Dict]:
        """성능 이슈 감지"""
        issues = []
        
        # N+1 쿼리 패턴
        if re.search(r'for.*in.*\n.*query|select', content, re.IGNORECASE):
            issues.append({
                'type': 'n_plus_one_query',
                'severity': 'high',
                'description': 'N+1 쿼리 패턴 감지'
            })
        
        # 무한 루프 가능성
        if re.search(r'while\s*\(\s*true\s*\)|for\s*\(\s*;\s*;\s*\)', content):
            issues.append({
                'type': 'infinite_loop_risk',
                'severity': 'medium',
                'description': '무한 루프 위험 감지'
            })
        
        # 메모리 누수 패턴
        if re.search(r'setInterval|setTimeout.*function', content):
            issues.append({
                'type': 'memory_leak_risk',
                'severity': 'medium',
                'description': '메모리 누수 위험 감지'
            })
        
        return issues
    
    async def _analyze_file_metrics(self, owner: str, repo: str, token: str) -> Dict:
        """파일 크기 및 복잡도 분석"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            
            metrics = {
                'total_files': len(source_files),
                'total_lines': 0,
                'average_file_size': 0,
                'large_files': [],
                'complex_files': []
            }
            
            file_sizes = []
            
            for file_path in source_files:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        lines = len(content.split('\n'))
                        file_sizes.append(lines)
                        metrics['total_lines'] += lines
                        
                        # 큰 파일 감지 (1000줄 이상)
                        if lines > 1000:
                            metrics['large_files'].append({
                                'file': file_path,
                                'lines': lines
                            })
                        
                        # 복잡한 파일 감지 (함수 수가 많은 파일)
                        complexity = self._calculate_file_complexity(content)
                        if complexity > 20:
                            metrics['complex_files'].append({
                                'file': file_path,
                                'complexity': complexity
                            })
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            if file_sizes:
                metrics['average_file_size'] = sum(file_sizes) / len(file_sizes)
            
            return metrics
        except Exception as e:
            print(f"파일 메트릭 분석 오류: {e}")
            return {}
    
    def _calculate_file_complexity(self, content: str) -> int:
        """파일 복잡도 계산"""
        complexity = 0
        
        # 함수 수 계산
        function_patterns = [
            r'function\s+\w+\s*\(',
            r'def\s+\w+\s*\(',
            r'async\s+function\s+\w+\s*\(',
            r'async\s+def\s+\w+\s*\(',
            r'const\s+\w+\s*=\s*\([^)]*\)\s*=>',
            r'let\s+\w+\s*=\s*\([^)]*\)\s*=>'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            complexity += len(matches)
        
        return complexity
    
    async def _analyze_algorithm_complexity(self, owner: str, repo: str, token: str) -> Dict:
        """알고리즘 복잡도 추정"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            
            complexity_analysis = {
                'nested_loops': 0,
                'recursive_functions': 0,
                'sorting_operations': 0,
                'search_operations': 0,
                'complexity_estimates': []
            }
            
            for file_path in source_files[:10]:  # 상위 10개 파일만 분석
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_complexity = self._analyze_file_algorithm_complexity(content, file_path)
                        
                        complexity_analysis['nested_loops'] += file_complexity.get('nested_loops', 0)
                        complexity_analysis['recursive_functions'] += file_complexity.get('recursive_functions', 0)
                        complexity_analysis['sorting_operations'] += file_complexity.get('sorting_operations', 0)
                        complexity_analysis['search_operations'] += file_complexity.get('search_operations', 0)
                        complexity_analysis['complexity_estimates'].extend(file_complexity.get('estimates', []))
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return complexity_analysis
        except Exception as e:
            print(f"알고리즘 복잡도 분석 오류: {e}")
            return {}
    
    def _analyze_file_algorithm_complexity(self, content: str, file_path: str) -> Dict:
        """파일별 알고리즘 복잡도 분석"""
        analysis = {
            'nested_loops': 0,
            'recursive_functions': 0,
            'sorting_operations': 0,
            'search_operations': 0,
            'estimates': []
        }
        
        lines = content.split('\n')
        
        # 중첩 루프 감지
        loop_depth = 0
        for line in lines:
            if re.search(r'\bfor\b|\bwhile\b', line):
                loop_depth += 1
            elif re.search(r'^\s*}', line):  # 루프 종료
                if loop_depth > 1:
                    analysis['nested_loops'] += 1
                loop_depth = max(0, loop_depth - 1)
        
        # 재귀 함수 감지
        recursive_patterns = [
            r'function\s+(\w+).*\1',  # 함수가 자신을 호출
            r'def\s+(\w+).*\1'
        ]
        
        for pattern in recursive_patterns:
            if re.search(pattern, content, re.MULTILINE):
                analysis['recursive_functions'] += 1
        
        # 정렬 및 검색 작업 감지
        sorting_keywords = ['sort', 'sorted', 'orderBy', 'sortBy']
        search_keywords = ['find', 'search', 'indexOf', 'includes', 'filter']
        
        for keyword in sorting_keywords:
            if keyword in content:
                analysis['sorting_operations'] += 1
        
        for keyword in search_keywords:
            if keyword in content:
                analysis['search_operations'] += 1
        
        # 복잡도 추정
        if analysis['nested_loops'] > 5:
            analysis['estimates'].append('O(n²) 이상의 복잡도 가능성')
        if analysis['recursive_functions'] > 2:
            analysis['estimates'].append('재귀 함수로 인한 스택 오버플로우 위험')
        
        return analysis
    
    async def _analyze_memory_patterns(self, owner: str, repo: str, token: str) -> Dict:
        """메모리 사용 패턴 분석"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            
            memory_patterns = {
                'memory_allocation': 0,
                'memory_deallocation': 0,
                'large_data_structures': 0,
                'memory_issues': []
            }
            
            for file_path in source_files[:15]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_memory = self._analyze_file_memory_patterns(content, file_path)
                        
                        memory_patterns['memory_allocation'] += file_memory.get('allocation', 0)
                        memory_patterns['memory_deallocation'] += file_memory.get('deallocation', 0)
                        memory_patterns['large_data_structures'] += file_memory.get('large_structures', 0)
                        memory_patterns['memory_issues'].extend(file_memory.get('issues', []))
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return memory_patterns
        except Exception as e:
            print(f"메모리 패턴 분석 오류: {e}")
            return {}
    
    def _analyze_file_memory_patterns(self, content: str, file_path: str) -> Dict:
        """파일별 메모리 패턴 분석"""
        patterns = {
            'allocation': 0,
            'deallocation': 0,
            'large_structures': 0,
            'issues': []
        }
        
        # 메모리 할당 패턴
        allocation_patterns = [
            r'new\s+\w+\(',
            r'Array\(',
            r'Object\(',
            r'\[\]',
            r'\{\}'
        ]
        
        for pattern in allocation_patterns:
            matches = re.findall(pattern, content)
            patterns['allocation'] += len(matches)
        
        # 큰 데이터 구조 감지
        if re.search(r'Array\(\d{3,}\)|\[\s*\d{3,}\s*\]', content):
            patterns['large_structures'] += 1
            patterns['issues'].append('큰 배열 할당 감지')
        
        # 메모리 누수 패턴
        if re.search(r'setInterval|setTimeout.*function', content):
            patterns['issues'].append('타이머 기반 메모리 누수 위험')
        
        return patterns
    
    async def _analyze_io_patterns(self, owner: str, repo: str, token: str) -> Dict:
        """네트워크/IO 패턴 분석"""
        try:
            source_files = await self._get_source_files(owner, repo, token)
            
            io_patterns = {
                'network_requests': 0,
                'file_operations': 0,
                'database_queries': 0,
                'io_issues': []
            }
            
            for file_path in source_files[:15]:
                try:
                    content = await fetch_github_file_content(owner, repo, file_path, token)
                    if content:
                        file_io = self._analyze_file_io_patterns(content, file_path)
                        
                        io_patterns['network_requests'] += file_io.get('network', 0)
                        io_patterns['file_operations'] += file_io.get('file', 0)
                        io_patterns['database_queries'] += file_io.get('database', 0)
                        io_patterns['io_issues'].extend(file_io.get('issues', []))
                except Exception as e:
                    # 파일 처리 중 오류 발생 시 무시하고 계속 진행
                    continue
            
            return io_patterns
        except Exception as e:
            print(f"IO 패턴 분석 오류: {e}")
            return {}
    
    def _analyze_file_io_patterns(self, content: str, file_path: str) -> Dict:
        """파일별 IO 패턴 분석"""
        patterns = {
            'network': 0,
            'file': 0,
            'database': 0,
            'issues': []
        }
        
        # 네트워크 요청 패턴
        network_patterns = [
            r'fetch\(',
            r'axios\.',
            r'XMLHttpRequest',
            r'requests\.',
            r'urllib\.'
        ]
        
        for pattern in network_patterns:
            matches = re.findall(pattern, content)
            patterns['network'] += len(matches)
        
        # 파일 작업 패턴
        file_patterns = [
            r'open\(',
            r'readFile',
            r'writeFile',
            r'fs\.'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            patterns['file'] += len(matches)
        
        # 데이터베이스 쿼리 패턴
        db_patterns = [
            r'SELECT|INSERT|UPDATE|DELETE',
            r'query\(',
            r'execute\(',
            r'find\(',
            r'save\('
        ]
        
        for pattern in db_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            patterns['database'] += len(matches)
        
        # IO 이슈 감지
        if patterns['network'] > 10:
            patterns['issues'].append('과도한 네트워크 요청')
        if patterns['database'] > 20:
            patterns['issues'].append('과도한 데이터베이스 쿼리')
        
        return patterns
    
    def _calculate_performance_score(self, performance_patterns: Dict, file_metrics: Dict) -> int:
        """전체 성능 점수 계산"""
        score = 100
        
        # 성능 이슈에 따른 점수 감점
        performance_issues = performance_patterns.get('performance_issues', [])
        for issue in performance_issues:
            if issue.get('severity') == 'high':
                score -= 10
            elif issue.get('severity') == 'medium':
                score -= 5
        
        # 파일 크기에 따른 점수 감점
        avg_file_size = file_metrics.get('average_file_size', 0)
        if avg_file_size > 500:
            score -= 10
        elif avg_file_size > 300:
            score -= 5
        
        # 복잡한 파일에 따른 점수 감점
        complex_files = file_metrics.get('complex_files', [])
        if len(complex_files) > 5:
            score -= 10
        elif len(complex_files) > 2:
            score -= 5
        
        return max(0, score)

# 전역 인스턴스들 (필요한 것만 유지)
analysis_cache = AnalysisCache()

class GithubSummaryRequest(BaseModel):
    username: str
    repo_name: Optional[str] = None  # 특정 저장소 분석 시 사용



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
    """언어 통계를 처리하여 정확한 비율로 분류 (정확도 개선)"""
    if not language_stats:
        return language_stats
    
    entries = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    
    # 정확한 비율 계산
    language_percentages = {}
    for name, value in entries:
        percentage = (value / total_bytes) * 100
        language_percentages[name] = percentage
    
    # 2% 이하인 언어들을 찾기 (더 엄격한 기준)
    small_languages = [(name, value) for name, value in entries if language_percentages[name] <= 2]
    
    # 7개 이상이거나 2% 이하인 언어가 여러 개인 경우 처리 (더 엄격한 기준)
    if len(entries) > 7 or len(small_languages) > 1:
        # 2% 이상인 언어들을 선택
        significant_languages = [(name, value) for name, value in entries if language_percentages[name] > 2]
        top_languages = significant_languages[:6]  # 상위 6개로 제한
        
        # 나머지 언어들을 '기타'로 분류
        others = []
        for name, value in entries:
            percentage = language_percentages[name]
            if percentage <= 2 or not any(top_name == name for top_name, _ in top_languages):
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
        # 기존 로직: 상위 6개만 표시
        return dict(entries[:6])

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
            # 404 오류는 정상적인 상황이므로 로그 출력하지 않음
            return None
        elif e.response.status_code == 403:
            print(f"파일 접근 권한 없음: {file_path}")
            return None
        else:
            print(f"파일 조회 오류 ({file_path}): {e.response.status_code}")
            return None
    except Exception as e:
        # 모든 파일 처리 오류를 조용히 무시
        return None















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
        import traceback
        traceback.print_exc()
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
        
        # package.json 분석 (정확도 개선)
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
                
                # 정확한 프레임워크 감지 (오탐 방지)
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                
                # React 생태계 (정확한 매칭)
                if 'react' in deps and 'react-dom' in deps:
                    analysis_result['frameworks'].append('React')
                if 'next' in deps:
                    analysis_result['frameworks'].append('Next.js')
                if 'gatsby' in deps:
                    analysis_result['frameworks'].append('Gatsby')
                
                # Vue 생태계 (정확한 매칭)
                if 'vue' in deps:
                    analysis_result['frameworks'].append('Vue.js')
                if 'nuxt' in deps:
                    analysis_result['frameworks'].append('Nuxt.js')
                
                # Angular (정확한 매칭)
                if 'angular' in deps or '@angular/core' in deps:
                    analysis_result['frameworks'].append('Angular')
                
                # Node.js 백엔드 (정확한 매칭)
                if 'express' in deps:
                    analysis_result['frameworks'].append('Express.js')
                if 'fastify' in deps:
                    analysis_result['frameworks'].append('Fastify')
                if 'koa' in deps:
                    analysis_result['frameworks'].append('Koa.js')
                if 'nest' in deps or '@nestjs/core' in deps:
                    analysis_result['frameworks'].append('NestJS')
                
                # 빌드 도구 (정확한 매칭)
                if 'webpack' in deps:
                    analysis_result['build_tools'].append('Webpack')
                if 'vite' in deps:
                    analysis_result['build_tools'].append('Vite')
                if 'rollup' in deps:
                    analysis_result['build_tools'].append('Rollup')
                if 'parcel' in deps:
                    analysis_result['build_tools'].append('Parcel')
                
                # 의존성 관리자 추가
                if deps:  # dependencies나 devDependencies가 있으면
                    if 'dependency_managers' not in analysis_result:
                        analysis_result['dependency_managers'] = []
                    analysis_result['dependency_managers'].append('npm')
                    
            except json.JSONDecodeError:
                pass
                
        # requirements.txt 분석 (정확도 개선)
        elif filename == 'requirements.txt':
            dependencies = []
            for line in file_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 버전 정보 제거하여 패키지명만 추출
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                    dependencies.append(package_name.strip())
            
            analysis_result['dependencies']['pip'] = dependencies
            
            # 정확한 Python 프레임워크 감지 (오탐 방지)
            if 'django' in dependencies:
                analysis_result['frameworks'].append('Django')
            if 'flask' in dependencies:
                analysis_result['frameworks'].append('Flask')
            if 'fastapi' in dependencies:
                analysis_result['frameworks'].append('FastAPI')
            if 'streamlit' in dependencies:
                analysis_result['frameworks'].append('Streamlit')
            if 'tornado' in dependencies:
                analysis_result['frameworks'].append('Tornado')
            if 'aiohttp' in dependencies:
                analysis_result['frameworks'].append('aiohttp')
            
            # Python 빌드 도구 감지
            if 'uvicorn' in dependencies:
                analysis_result['build_tools'].append('Uvicorn')
            if 'gunicorn' in dependencies:
                analysis_result['build_tools'].append('Gunicorn')
            
            # 데이터베이스 감지
            if 'motor' in dependencies or 'pymongo' in dependencies:
                if 'databases' not in analysis_result:
                    analysis_result['databases'] = []
                analysis_result['databases'].append('MongoDB')
            if 'psycopg2' in dependencies or 'asyncpg' in dependencies:
                if 'databases' not in analysis_result:
                    analysis_result['databases'] = []
                analysis_result['databases'].append('PostgreSQL')
            if 'mysql-connector-python' in dependencies or 'pymysql' in dependencies:
                if 'databases' not in analysis_result:
                    analysis_result['databases'] = []
                analysis_result['databases'].append('MySQL')
            if 'redis' in dependencies:
                if 'databases' not in analysis_result:
                    analysis_result['databases'] = []
                analysis_result['databases'].append('Redis')
            
            # Python 의존성 관리자 추가
            if dependencies:  # requirements.txt가 있으면
                if 'dependency_managers' not in analysis_result:
                    analysis_result['dependency_managers'] = []
                analysis_result['dependency_managers'].append('pip')
                
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
    
    # 중복 제거 및 정확도 검증
    analysis_result['frameworks'] = list(set(analysis_result['frameworks']))
    analysis_result['build_tools'] = list(set(analysis_result['build_tools']))
    
    # 프레임워크 정확도 검증 (상호 배타적 프레임워크 처리)
    frameworks = analysis_result['frameworks']
    if 'Next.js' in frameworks and 'React' not in frameworks:
        frameworks.append('React')  # Next.js는 React 기반
    if 'Nuxt.js' in frameworks and 'Vue.js' not in frameworks:
        frameworks.append('Vue.js')  # Nuxt.js는 Vue 기반
    if 'Gatsby' in frameworks and 'React' not in frameworks:
        frameworks.append('React')  # Gatsby는 React 기반
    
    analysis_result['frameworks'] = list(set(frameworks))
    
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
    """향상된 의존성 분석을 통해 외부 라이브러리 및 LLM 관련 힌트를 수집한다."""
    hints: Dict[str, List[str]] = {
        'external_libraries': [],
        'llm_hints': [],
        'frameworks': [],
        'build_tools': [],
        'deployment_configs': []
    }

    try:
        # 1단계: 핵심파일 선별 조회 및 분석
        core_files = await fetch_repo_core_files(owner, repo, token)
        analysis_result = await analyze_core_files_content(owner, repo, core_files, token)
        
        # 2단계: 향상된 의존성 정보 수집
        await _collect_enhanced_dependencies(owner, repo, analysis_result, hints, token)
        
        # 3단계: 향상된 LLM 라이브러리 감지
        await _detect_enhanced_llm_libraries(hints)
        
        # 4단계: 추가 파일 스캔 (fallback)
        await _scan_additional_files(owner, repo, hints, token)
        
        # 5단계: 중복 제거 및 정렬
        _cleanup_and_sort_hints(hints)

    except Exception as e:
        print(f"향상된 의존성 분석 중 오류: {e}")
        # 강화된 fallback 로직
        await _enhanced_fallback_analysis(owner, repo, hints, token)

    return hints

async def _collect_enhanced_dependencies(owner: str, repo: str, analysis_result: Dict, hints: Dict[str, List[str]], token: Optional[str]):
    """향상된 의존성 정보 수집"""
    
    # 분석 결과에서 직접 추출된 정보를 hints에 복사
    if 'frameworks' in analysis_result:
        hints['frameworks'].extend(analysis_result['frameworks'])
    
    if 'build_tools' in analysis_result:
        hints['build_tools'].extend(analysis_result['build_tools'])
    
    if 'dependency_managers' in analysis_result:
        if 'dependency_managers' not in hints:
            hints['dependency_managers'] = []
        hints['dependency_managers'].extend(analysis_result['dependency_managers'])
    
    if 'databases' in analysis_result:
        if 'databases' not in hints:
            hints['databases'] = []
        hints['databases'].extend(analysis_result['databases'])
    
    if 'deployment_configs' in analysis_result:
        hints['deployment_configs'].extend(analysis_result['deployment_configs'])
    
    # NPM 의존성 수집
    if 'dependencies' in analysis_result and 'npm' in analysis_result['dependencies']:
            npm_deps = analysis_result['dependencies']['npm']
            deps = {**npm_deps.get('dependencies', {}), **npm_deps.get('devDependencies', {}), 
                **npm_deps.get('peerDependencies', {}), **npm_deps.get('optionalDependencies', {})}
            hints['external_libraries'].extend(list(deps.keys()))
            
    # Python 의존성 수집
    if 'dependencies' in analysis_result and 'pip' in analysis_result['dependencies']:
            hints['external_libraries'].extend(analysis_result['dependencies']['pip'])
        
    # Go 의존성 수집
    go_mod_content = await fetch_repo_file(owner, repo, 'go.mod', token)
    if go_mod_content:
        go_deps = _parse_go_dependencies(go_mod_content)
        hints['external_libraries'].extend(go_deps)
    
    # Rust 의존성 수집
    cargo_content = await fetch_repo_file(owner, repo, 'Cargo.toml', token)
    if cargo_content:
        rust_deps = _parse_cargo_dependencies(cargo_content)
        hints['external_libraries'].extend(rust_deps)
    
    # Java 의존성 수집
    pom_content = await fetch_repo_file(owner, repo, 'pom.xml', token)
    if pom_content:
        maven_deps = _parse_maven_dependencies(pom_content)
        hints['external_libraries'].extend(maven_deps)
        
async def _detect_enhanced_llm_libraries(hints: Dict[str, List[str]]):
    """향상된 LLM 라이브러리 감지 (정확도 개선)"""
    
    # 정확한 LLM 라이브러리 매핑 (오탐 방지)
    llm_library_patterns = {
        # OpenAI 생태계 (정확한 매칭)
        'openai': ['openai', 'gpt-4', 'gpt-3.5', 'gpt-3', 'dall-e', 'whisper', 'tiktoken', 'openai-python'],
        # Google AI 생태계 (정확한 매칭)
        'google_ai': ['google-generativeai', 'google.generativeai', 'vertexai', 'gemini', 'palm', 'tensorflow', 'tensorflow-hub'],
        # Anthropic 생태계 (정확한 매칭)
        'anthropic': ['anthropic', 'claude', 'claude-3', 'claude-2', 'claude-instant'],
        # LangChain 생태계 (정확한 매칭)
        'langchain': ['langchain', 'langchain-js', 'langchain-python', 'langchain-community', 'langchain-core'],
        # LlamaIndex 생태계 (정확한 매칭)
        'llamaindex': ['llama-index', 'llamaindex', 'llama-index-core', 'llama-index-llms'],
        # Hugging Face (정확한 매칭)
        'huggingface': ['transformers', 'huggingface-hub', 'datasets', 'tokenizers', 'accelerate', 'diffusers'],
        # 기타 LLM 라이브러리 (정확한 매칭)
        'others': ['cohere', 'groq', 'mcp', 'llama', 'mistral', 'falcon', 't5', 'bert', 'roberta', 'gpt2', 'gpt-j'],
        # 벡터 데이터베이스 (정확한 매칭)
        'vector_db': ['pinecone', 'weaviate', 'qdrant', 'chromadb', 'faiss', 'milvus', 'elasticsearch'],
        # 프롬프트 엔지니어링 (정확한 매칭)
        'prompting': ['promptify', 'promptlayer', 'promptfoo', 'langfuse', 'promptflow'],
        # RAG 관련 (정확한 매칭)
        'rag': ['haystack', 'sentence-transformers', 'all-minilm-l6-v2', 'all-mpnet-base-v2'],
        # 멀티모달 (정확한 매칭)
        'multimodal': ['clip', 'blip', 'llava', 'instructblip', 'cogvlm', 'qwen-vl']
    }
    
    # 제외할 키워드 (오탐 방지)
    exclude_keywords = ['ai', 'ml', 'nlp', 'llm', 'gpt', 'claude', 'gemini', 'openai', 'anthropic', 'google']
    
    detected_llm_libs = []
    
    for lib in hints['external_libraries']:
        lib_lower = lib.lower()
        
        # 정확한 매칭만 허용 (오탐 방지)
        is_llm_lib = False
        for category, patterns in llm_library_patterns.items():
            for pattern in patterns:
                if pattern == lib_lower or lib_lower.startswith(pattern + '-') or lib_lower.endswith('-' + pattern):
                    detected_llm_libs.append(lib)
                    is_llm_lib = True
                    break
            if is_llm_lib:
                break
        
        # 추가 검증: 일반적인 키워드만으로는 포함하지 않음
        if not is_llm_lib:
            # 매우 구체적인 패턴만 허용
            specific_patterns = [
                'openai-', 'anthropic-', 'google-ai', 'langchain-', 'llamaindex-',
                'transformers', 'huggingface', 'cohere-', 'groq-', 'mistral-',
                'google-generativeai', 'google.generativeai'  # Gemini 특화
            ]
            for pattern in specific_patterns:
                if pattern in lib_lower:
                    detected_llm_libs.append(lib)
                    break
    
    # Gemini 관련 라이브러리 특별 처리 (강화)
    for lib in hints['external_libraries']:
        if 'google-generativeai' in lib.lower() or 'google.generativeai' in lib.lower():
            detected_llm_libs.append('google-generativeai')
            detected_llm_libs.append('gemini')
            break
    
    # LLM 라이브러리에서도 Gemini 확인
    if 'llm_libraries' in hints:
        for lib in hints['llm_libraries']:
            if 'gemini' in lib.lower() or 'google-generativeai' in lib.lower():
                detected_llm_libs.append('gemini')
                break
    
    hints['llm_hints'] = list(set(detected_llm_libs))

async def _scan_additional_files(owner: str, repo: str, hints: Dict[str, List[str]], token: Optional[str]):
    """추가 파일 스캔으로 의존성 정보 보완 (강화)"""
    
    # 1. 의존성 파일 스캔
    additional_files = [
        'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'poetry.lock', 'Pipfile', 'Pipfile.lock', 'pyproject.toml',
        'go.sum', 'Cargo.lock', 'composer.json', 'composer.lock',
        'Gemfile', 'Gemfile.lock', 'Podfile', 'Podfile.lock'
    ]
    
    for filename in additional_files:
        content = await fetch_repo_file(owner, repo, filename, token)
        if content:
            if filename in ['package-lock.json', 'yarn.lock']:
                npm_deps = _parse_lockfile_dependencies(content)
                hints['external_libraries'].extend(npm_deps)
            elif filename in ['poetry.lock', 'Pipfile', 'pyproject.toml']:
                python_deps = _parse_python_dependencies(content, filename)
                hints['external_libraries'].extend(python_deps)
    
    # 2. README에서 라이브러리 정보 추출
    readme_content = await fetch_repo_file(owner, repo, 'README.md', token)
    if readme_content:
        await _extract_libraries_from_readme(readme_content, hints)
    
    # 3. 실제 코드 파일에서 import/require 문 분석
    await _analyze_code_imports(owner, repo, hints, token)
    
    # 4. LLM 관련 키워드 검색 강화
    await _search_llm_patterns(owner, repo, hints, token)

async def _enhanced_fallback_analysis(owner: str, repo: str, hints: Dict[str, List[str]], token: Optional[str]):
    """강화된 fallback 분석"""
    
    # 1. 최상위 파일 스캔
    top_level_files = await fetch_repo_top_level_files(owner, repo, token)
    file_names = [f.get('name', '').lower() for f in (top_level_files or [])]
        
    # 2. 주요 의존성 파일 분석
    dependency_files = {
        'package.json': _parse_dependencies_from_package_json,
        'requirements.txt': _parse_dependencies_from_requirements,
        'go.mod': _parse_go_dependencies,
        'Cargo.toml': _parse_cargo_dependencies,
        'pom.xml': _parse_maven_dependencies
    }
    
    for filename, parser_func in dependency_files.items():
        if filename in file_names:
            content = await fetch_repo_file(owner, repo, filename, token)
            if content:
                deps = parser_func(content)
                hints['external_libraries'].extend(deps)
    
    # 3. LLM 라이브러리 재감지
    await _detect_enhanced_llm_libraries(hints)
    
    # 4. 정리
    _cleanup_and_sort_hints(hints)

async def _extract_libraries_from_readme(content: str, hints: Dict[str, List[str]]):
    """README에서 라이브러리 정보 추출"""
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        
        # 설치 명령어에서 패키지명 추출
        if 'npm install' in line_lower or 'yarn add' in line_lower:
            # 패키지명 추출 로직
            packages = re.findall(r'(?:npm install|yarn add)\s+([^\s]+)', line)
            hints['external_libraries'].extend(packages)
        
        # pip install 명령어에서 패키지명 추출
        elif 'pip install' in line_lower:
            packages = re.findall(r'pip install\s+([^\s]+)', line)
            hints['external_libraries'].extend(packages)

async def _analyze_code_imports(owner: str, repo: str, hints: Dict[str, List[str]], token: Optional[str]):
    """실제 코드 파일에서 import/require 문 분석"""
    try:
        # 파일 트리 가져오기
        tree = await fetch_github_tree(owner, repo, token)
        
        # 주요 코드 파일들 분석
        code_files = []
        for item in tree:
            if item.get('type') == 'blob':
                path = item.get('path', '')
                if any(path.endswith(ext) for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c']):
                    code_files.append(path)
        
        # 상위 20개 파일만 분석 (성능 고려)
        for file_path in code_files[:20]:
            try:
                content = await fetch_github_file_content(owner, repo, file_path, token)
                if content:
                    # JavaScript/TypeScript import 분석
                    if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        js_imports = _extract_js_imports(content)
                        hints['external_libraries'].extend(js_imports)
                    
                    # Python import 분석
                    elif file_path.endswith('.py'):
                        py_imports = _extract_py_imports(content)
                        hints['external_libraries'].extend(py_imports)
                    
                    # Java import 분석
                    elif file_path.endswith('.java'):
                        java_imports = _extract_java_imports(content)
                        hints['external_libraries'].extend(java_imports)
                        
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"코드 import 분석 오류: {e}")

async def _search_llm_patterns(owner: str, repo: str, hints: Dict[str, List[str]], token: Optional[str]):
    """LLM 관련 패턴 검색 강화"""
    try:
        # 파일 트리 가져오기
        tree = await fetch_github_tree(owner, repo, token)
        
        # 모든 텍스트 파일에서 LLM 관련 키워드 검색
        for item in tree:
            if item.get('type') == 'blob':
                path = item.get('path', '')
                if any(path.endswith(ext) for ext in ['.md', '.txt', '.js', '.ts', '.jsx', '.tsx', '.py', '.json', '.env', '.env.example']):
                    try:
                        content = await fetch_github_file_content(owner, repo, path, token)
                        if content:
                            # 일반 LLM 패턴 검색
                            llm_patterns = _find_llm_patterns(content)
                            if llm_patterns:
                                hints['llm_hints'].extend(llm_patterns)
                            
                            # Gemini 특화 패턴 검색
                            gemini_patterns = _find_gemini_specific_patterns(content)
                            if gemini_patterns:
                                hints['llm_hints'].extend(gemini_patterns)
                                
                    except Exception as e:
                        continue
                        
    except Exception as e:
        print(f"LLM 패턴 검색 오류: {e}")

def _extract_js_imports(content: str) -> List[str]:
    """JavaScript/TypeScript import 문에서 라이브러리 추출"""
    imports = []
    
    # ES6 import 문
    import_patterns = [
        r'import\s+.*?from\s+["\']([^"\']+)["\']',
        r'import\s+["\']([^"\']+)["\']',
        r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        imports.extend(matches)
    
    return list(set(imports))

def _extract_py_imports(content: str) -> List[str]:
    """Python import 문에서 라이브러리 추출"""
    imports = []
    
    # Python import 문
    import_patterns = [
        r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        imports.extend(matches)
    
    return list(set(imports))

def _extract_java_imports(content: str) -> List[str]:
    """Java import 문에서 라이브러리 추출"""
    imports = []
    
    # Java import 문
    import_patterns = [
        r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*);'
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, content)
        imports.extend(matches)
    
    return list(set(imports))

def _find_llm_patterns(content: str) -> List[str]:
    """LLM 관련 패턴 검색 (강화)"""
    llm_patterns = []
    
    # LLM 관련 키워드 패턴 (확장)
    llm_keywords = [
        # OpenAI 생태계
        'openai', 'gpt', 'gpt-4', 'gpt-3.5', 'dall-e', 'whisper', 'tiktoken',
        # Anthropic 생태계
        'claude', 'claude-3', 'claude-2', 'anthropic',
        # Google AI 생태계 (강화)
        'gemini', 'palm', 'vertexai', 'google-generativeai', 'google.generativeai', 'generativeai',
        'google-ai', 'googleai', 'genai', 'google_genai',
        # LangChain 생태계
        'langchain', 'langchain-js', 'langchain-python', 'langchain-community',
        # LlamaIndex 생태계
        'llamaindex', 'llama-index',
        # Hugging Face
        'transformers', 'huggingface', 'huggingface-hub', 'datasets', 'tokenizers',
        # 기타 LLM 라이브러리
        'cohere', 'groq', 'mistral', 'falcon', 't5', 'bert', 'roberta', 'gpt2',
        # 벡터 데이터베이스
        'pinecone', 'weaviate', 'qdrant', 'chromadb', 'faiss', 'milvus',
        # 프롬프트 엔지니어링
        'prompt', 'completion', 'chat', 'llm', 'ai', 'ml', 'nlp',
        # API 관련
        'api_key', 'api_key', 'endpoint', 'client', 'model', 'response'
    ]
    
    content_lower = content.lower()
    for keyword in llm_keywords:
        if keyword in content_lower:
            # 키워드 주변 컨텍스트 분석
            context = _extract_context(content, keyword)
            if _is_llm_related_context(context):
                llm_patterns.append(keyword)
    
    # 추가: 코드 패턴 검색 (강화)
    code_patterns = [
        r'openai\s*\.\s*',  # openai.
        r'claude\s*\.\s*',  # claude.
        r'gemini\s*\.\s*',  # gemini.
        r'langchain\s*\.\s*',  # langchain.
        r'from\s+openai\s+import',  # from openai import
        r'from\s+anthropic\s+import',  # from anthropic import
        r'from\s+google\s+import\s+generativeai',  # from google import generativeai
        r'import\s+google\.generativeai',  # import google.generativeai
        r'import\s+generativeai',  # import generativeai
        r'import\s+openai',  # import openai
        r'import\s+anthropic',  # import anthropic
        r'new\s+OpenAI',  # new OpenAI
        r'new\s+Anthropic',  # new Anthropic
        r'genai\s*\.\s*',  # genai.
        r'google\.generativeai\s*\.\s*',  # google.generativeai.
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            # 패턴에서 라이브러리명 추출
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                lib_name = pattern.split(r'\s*\.\s*')[0] if r'\s*\.\s*' in pattern else pattern.split(r'\s+import')[0].split(r'from\s+')[-1]
                if lib_name not in llm_patterns:
                    llm_patterns.append(lib_name)
    
    return list(set(llm_patterns))

def _find_gemini_specific_patterns(content: str) -> List[str]:
    """Gemini 특화 패턴 검색 (강화)"""
    gemini_patterns = []
    content_lower = content.lower()
    
    # Gemini 관련 특화 패턴들 (확장)
    gemini_specific_patterns = [
        r'google\.generativeai\.GenerativeModel',
        r'genai\.GenerativeModel',
        r'generativeai\.GenerativeModel',
        r'gemini-pro',
        r'gemini-pro-vision',
        r'gemini-1\.5',
        r'gemini-2\.0',
        r'gemini-flash',
        r'GOOGLE_API_KEY',
        r'GEMINI_API_KEY',
        r'GOOGLE_GENERATIVE_AI_API_KEY',
        r'genai\.configure',
        r'generativeai\.configure',
        r'google\.generativeai\.configure',
        r'genai\.generate_content',
        r'generativeai\.generate_content',
        r'google\.generativeai\.generate_content',
        r'google-generativeai',
        r'import\s+google\.generativeai',
        r'from\s+google\.generativeai'
    ]
    
    # 패턴 매칭
    for pattern in gemini_specific_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            gemini_patterns.append('gemini')
            break
    
    # 직접적인 키워드 검색 추가
    if 'gemini' in content_lower:
        gemini_patterns.append('gemini')
    
    if 'google.generativeai' in content_lower or 'google-generativeai' in content_lower:
        gemini_patterns.append('gemini')
    
    if 'genai' in content_lower and ('import' in content_lower or 'configure' in content_lower):
        gemini_patterns.append('gemini')
    
    return list(set(gemini_patterns))

def _extract_context(content: str, keyword: str, context_size: int = 50) -> str:
    """키워드 주변 컨텍스트 추출"""
    try:
        index = content.lower().find(keyword.lower())
        if index != -1:
            start = max(0, index - context_size)
            end = min(len(content), index + len(keyword) + context_size)
            return content[start:end]
    except:
        pass
    return ""

def _is_llm_related_context(context: str) -> bool:
    """컨텍스트가 LLM 관련인지 판단 (강화)"""
    llm_indicators = [
        'api', 'model', 'token', 'response', 'request', 'client', 'config',
        'key', 'secret', 'endpoint', 'url', 'service', 'library', 'package',
        'generate', 'completion', 'chat', 'prompt', 'text', 'content',
        'gemini', 'openai', 'anthropic', 'claude', 'gpt', 'llm', 'ai'
    ]
    
    context_lower = context.lower()
    return any(indicator in context_lower for indicator in llm_indicators)

def _cleanup_and_sort_hints(hints: Dict[str, List[str]]):
    """힌트 정리 및 정렬 (정확도 개선)"""
    for key in hints:
        if isinstance(hints[key], list):
            # 중복 제거 및 정렬 (정확도 개선)
            cleaned_list = []
            seen = set()
            
            for item in hints[key]:
                # 딕셔너리인 경우 문자열로 변환
                if isinstance(item, dict):
                    if 'name' in item:
                        item_str = str(item['name'])
                    elif 'type' in item:
                        item_str = str(item['type'])
                    else:
                        item_str = str(item)
                else:
                    item_str = str(item)
                
                # 정규화된 이름으로 중복 체크
                normalized = item_str.lower().replace('-', '').replace('_', '')
                if normalized not in seen:
                    seen.add(normalized)
                    cleaned_list.append(item_str)
            
            # 알파벳 순으로 정렬
            hints[key] = sorted(cleaned_list)

def _parse_go_dependencies(content: str) -> List[str]:
    """Go 모듈 의존성 파싱 (정확도 개선)"""
    deps = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('require ') and '(' in line and ')' in line:
            # require (github.com/example/package v1.2.3)
            parts = line.split('(')[1].split(')')[0].strip()
            for part in parts.split('\n'):
                part = part.strip()
                if part and not part.startswith('//'):
                    module = part.split()[0]
                    # 정확한 모듈명만 추출 (버전 정보 제거)
                    if '/' in module:
                        deps.append(module)
    return deps

def _parse_cargo_dependencies(content: str) -> List[str]:
    """Rust Cargo 의존성 파싱 (정확도 개선)"""
    deps = []
    lines = content.split('\n')
    in_dependencies = False
    
    for line in lines:
        line = line.strip()
        if line == '[dependencies]':
            in_dependencies = True
            continue
        elif line.startswith('[') and line.endswith(']'):
            in_dependencies = False
            continue
        
        if in_dependencies and line and not line.startswith('#'):
            if '=' in line:
                package = line.split('=')[0].strip()
                # 정확한 패키지명만 추출 (버전 정보 제거)
                if package and not package.startswith('{'):
                    deps.append(package)
    
    return deps

def _parse_maven_dependencies(content: str) -> List[str]:
    """Maven 의존성 파싱"""
    deps = []
    import re
    
    # groupId:artifactId 패턴 찾기
    pattern = r'<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>'
    matches = re.findall(pattern, content)
    
    for group_id, artifact_id in matches:
        deps.append(f"{group_id}:{artifact_id}")
    
    return deps

def _parse_lockfile_dependencies(content: str) -> List[str]:
    """NPM lockfile 의존성 파싱"""
    deps = []
    try:
        import json
        data = json.loads(content)
        if 'dependencies' in data:
            deps.extend(list(data['dependencies'].keys()))
    except:
        pass
    return deps

def _parse_python_dependencies(content: str, filename: str) -> List[str]:
    """Python 의존성 파일 파싱"""
    deps = []
    
    if filename == 'pyproject.toml':
        # TOML 파싱 (간단한 버전)
        lines = content.split('\n')
        in_dependencies = False
        for line in lines:
            line = line.strip()
            if line == '[tool.poetry.dependencies]' or line == '[project.dependencies]':
                in_dependencies = True
                continue
            elif line.startswith('[') and line.endswith(']'):
                in_dependencies = False
                continue
            
            if in_dependencies and line and not line.startswith('#'):
                if '=' in line:
                    package = line.split('=')[0].strip()
                    deps.append(package)
    
    elif filename == 'Pipfile':
        # Pipfile 파싱
        lines = content.split('\n')
        in_packages = False
        for line in lines:
            line = line.strip()
            if line == '[packages]':
                in_packages = True
                continue
            elif line.startswith('[') and line.endswith(']'):
                in_packages = False
                continue
            
            if in_packages and line and not line.startswith('#'):
                if '=' in line:
                    package = line.split('=')[0].strip().strip('"').strip("'")
                    deps.append(package)
    
    return deps

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
    """통합된 요약 생성 함수 - GPT-4o 최적화"""
    
    # OpenAI API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API 키가 설정되지 않았습니다.")
    
    model = 'gpt-4o'  # GPT-4o로 업그레이드
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
    
    # GPT-4o 최적화 프롬프트 구성 - 정확도 향상
    if input_data["analysis_type"] == "single_repo":
        repo_data = input_data["repo_data"]
        prompt = f"""당신은 GitHub 레포지토리를 분석하여 채용 담당자가 이해하기 쉬운 형태로 요약하는 전문가입니다. GPT-4o의 강력한 분석 능력을 활용하여 실제 레포지토리 내용과 정확히 일치하는 분석을 제공해주세요.

**중요**: 제공된 데이터만을 기반으로 분석하고, 추측이나 일반적인 내용을 포함하지 마세요. 실제 파일 구조, 언어 사용량, 기술 스택을 정확히 반영해주세요.

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
- 외부 라이브러리 힌트: {repo_data.get('external_libraries_hint', [])}
- LLM 관련 힌트: {repo_data.get('llm_hints', [])}

**파일 구조 및 메타데이터**
- 파일 구조: {repo_data.get('file_structure', '파일 구조 정보 없음')}
- 개발자 활동: {repo_data.get('developer_activity', '활동 정보 없음')}
- 빌드 도구: {repo_data.get('build_tools', [])}
- 배포 설정: {repo_data.get('deployment_configs', [])}

**GPT-4o 정확도 향상 분석 지침 (강화):**
1. **주제 분석**: 
   - 실제 파일명, 폴더명, README 내용을 기반으로 정확한 프로젝트 목적 파악
   - 추측하지 말고 제공된 데이터만으로 분석
   - 일반적인 설명이 아닌 구체적인 프로젝트 특징만 언급
2. **기술 스택 분석**: 
   - 실제 언어 사용량 비율을 정확히 반영 (백분율 기반)
   - 프레임워크는 실제 발견된 것만 포함 (오탐 방지)
   - 라이브러리는 실제 의존성 파일에서 확인된 것만 포함
   - 버전 정보가 있다면 정확히 표시
3. **주요 기능 추출**: 
   - 실제 파일 구조와 코드 패턴을 기반으로 구현된 기능만 식별
   - README나 코드에서 명시적으로 확인된 기능만 포함
   - 추측이 아닌 실제 구현된 기능만 분석
4. **아키텍처 구조 분석**:
   - 실제 폴더 구조와 파일 배치를 기반으로 아키텍처 패턴 분석
   - 추측이 아닌 실제 구조를 반영
   - 구체적인 아키텍처 패턴명 사용 (MVC, MVVM, Microservices 등)
5. **외부 라이브러리 분석**:
   - 실제 package.json, requirements.txt 등에서 확인된 라이브러리만 포함
   - 버전 정보가 있다면 정확히 표시
   - 오탐 방지를 위해 정확한 라이브러리명만 사용
6. **LLM 모델 정보**:
   - 실제 코드에서 LLM 관련 라이브러리나 API 호출이 확인된 경우만 포함
   - 추측하지 말고 실제 사용된 것만 분석
   - 구체적인 모델명이나 API 종류 명시

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
        prompt = f"""당신은 GitHub 사용자 프로필 README를 분석하여 채용 담당자가 이해하기 쉬운 형태로 요약하는 전문가입니다. GPT-4o의 강력한 분석 능력을 활용하여 실제 프로필 내용과 정확히 일치하는 분석을 제공해주세요.

**중요**: 제공된 README 내용만을 기반으로 분석하고, 추측이나 일반적인 내용을 포함하지 마세요. 실제 언급된 기술, 프로젝트, 경험만을 정확히 반영해주세요.

다음 프로필 README 내용을 분석하여 '주제', '기술 스택', '주요 기능', '레포 주소', '아키텍처 구조', '외부 라이브러리', 'LLM 모델 정보'를 추출해주세요:

**프로필 README 내용:**
{readme_text}

**GPT-4o 정확도 향상 분석 지침:**
1. **주제 분석**: 
   - 실제 README에서 언급된 기술적 관심사와 전문 분야만 파악
   - 추측하지 말고 명시적으로 언급된 내용만 분석
   - 실제 프로젝트와 성과를 중심으로 전문성 평가

2. **기술 스택 분석**:
   - 실제 README에서 언급된 기술들만 카테고리별로 분류
   - 추측하지 말고 명시적으로 언급된 기술만 포함
   - 기술 간의 실제 연관성만 분석

3. **주요 기능/프로젝트 추출**:
   - 실제 README에서 언급된 프로젝트만 식별
   - 추측하지 말고 명시적으로 언급된 프로젝트만 포함
   - 실제 언급된 기술적 난이도와 복잡성만 평가

4. **아키텍처 구조 분석**:
   - 실제 README에서 언급된 아키텍처 패턴만 분석
   - 추측하지 말고 명시적으로 언급된 구조만 포함
   - 실제 언급된 확장성과 유지보수성만 평가

5. **외부 라이브러리 및 도구**:
   - 실제 README에서 언급된 라이브러리, 프레임워크, 도구만 분석
   - 추측하지 말고 명시적으로 언급된 것만 포함
   - 실제 언급된 클라우드 서비스, API, 개발 도구만 분석

6. **LLM 모델 정보**:
   - 실제 README에서 언급된 AI/ML 관련 프로젝트나 기술만 분석
   - 추측하지 말고 명시적으로 언급된 LLM 관련 경험만 포함

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
        
        prompt = f"""당신은 GitHub 사용자의 여러 레포지토리를 분석하여 각각을 개별적으로 요약하는 전문가입니다. GPT-4o의 강력한 분석 능력을 활용하여 실제 레포지토리 내용과 정확히 일치하는 분석을 제공해주세요.

**중요**: 제공된 데이터만을 기반으로 분석하고, 추측이나 일반적인 내용을 포함하지 마세요. 각 레포지토리의 실제 파일 구조, 언어, 기술 스택을 정확히 반영해주세요.

다음 {len(repos)}개의 레포지토리 데이터를 분석하여 각 레포지토리별로 '주제', '기술 스택', '주요 기능', '레포 주소', '아키텍처 구조', '외부 라이브러리', 'LLM 모델 정보'를 추출해주세요:

**레포지토리 목록:**
{json.dumps(repos_info, indent=2, ensure_ascii=False)}

**GPT-4o 정확도 향상 분석 지침:**
1. **개별 레포지토리 분석**:
   - 실제 파일명, 폴더명, README 내용을 기반으로 정확한 프로젝트 목적 파악
   - 추측하지 말고 제공된 데이터만으로 분석
   - 각 레포지토리의 고유한 특징과 목적 파악

2. **기술 스택 분석**:
   - 실제 언어 사용량 비율을 정확히 반영
   - 프레임워크는 실제 발견된 것만 포함
   - 라이브러리는 실제 의존성 파일에서 확인된 것만 포함

3. **주요 기능 추출**:
   - 실제 파일 구조와 코드 패턴을 기반으로 구현된 기능만 식별
   - README나 코드에서 명시적으로 확인된 기능만 포함
   - 추측이 아닌 실제 구현된 기능만 분석

4. **아키텍처 구조 분석**:
   - 실제 폴더 구조와 파일 배치를 기반으로 아키텍처 패턴 분석
   - 추측이 아닌 실제 구조를 반영
   - 각 프로젝트의 실제 아키텍처 패턴 식별

5. **외부 라이브러리 분석**:
   - 실제 package.json, requirements.txt 등에서 확인된 라이브러리만 포함
   - 버전 정보가 있다면 정확히 표시
   - 추측하지 말고 실제 사용된 것만 분석

6. **LLM 모델 정보**:
   - 실제 코드에서 LLM 관련 라이브러리나 API 호출이 확인된 경우만 포함
   - 추측하지 말고 실제 사용된 것만 분석

7. **포트폴리오 관점 분석**:
   - 전체 레포지토리 간의 실제 기술적 일관성과 다양성 평가
   - 제공된 데이터를 기반으로 한 정확한 기술적 역량 평가

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
                "role": "system",
                "content": "당신은 GitHub 레포지토리 분석 전문가입니다. GPT-4o의 강력한 분석 능력을 활용하여 실제 레포지토리 내용과 정확히 일치하는 분석을 제공해주세요. 제공된 데이터만을 기반으로 분석하고 추측하지 마세요. 항상 JSON 형식으로 응답해주세요."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.05,  # 최고 정확도를 위해 매우 낮은 temperature
        "max_tokens": 10000,  # 더 상세한 분석을 위해 토큰 수 증가
        "response_format": {"type": "json_object"}  # JSON 응답 강제
    }
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:  # GPT-4o는 더 긴 응답 시간 필요
        response = await client.post(endpoint, json=payload, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        })
        response.raise_for_status()
        data = response.json()
        
        # 토큰 사용량 추적
        global openai_api_calls, openai_tokens_used
        openai_api_calls += 1
        if 'usage' in data:
            usage = data['usage']
            openai_tokens_used += usage.get('total_tokens', 0)
            print(f"[TOKEN USAGE] API 호출: {openai_api_calls}, 총 토큰: {openai_tokens_used}")
        
        response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        try:
            # GPT-4o의 response_format: json_object를 사용하므로 직접 파싱 가능
            result = json.loads(response_text.strip())
            
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
    """GitHub 사용자 요약 - 캐싱 및 에러 처리 강화"""
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
        
        # MongoDB에서 기존 분석 결과 확인 및 증분 업데이트 로직
        print(f"MongoDB에서 기존 분석 확인: {username}/{repo_name or 'profile'}")
        
        # 1. 저장된 분석이 최근 것인지 확인 (24시간 이내)
        cached_result = await github_storage_service.get_cached_analysis_if_fresh(username, repo_name, max_age_hours=24)
        
        if cached_result and repo_name:
            # 2. 저장소가 지정된 경우, 파일 변경 사항 확인
            try:
                print(f"파일 변경사항 확인 중: {username}/{repo_name}")
                current_file_hashes = await generate_file_hashes_from_github(username, repo_name, github_token)
                
                if current_file_hashes:
                    update_needed, changed_files = await github_storage_service.check_if_update_needed(
                        username, repo_name, current_file_hashes
                    )
                    
                    if not update_needed:
                        print(f"변경사항 없음 - 캐시된 결과 반환: {username}/{repo_name}")
                        await github_storage_service.update_last_checked(username, repo_name)
                        return cached_result
                    else:
                        print(f"변경된 파일 {len(changed_files)}개 감지 - 재분석 진행")
                        # 변경 영향도 분석
                        stored_hashes = await github_storage_service.get_stored_file_hashes(username, repo_name)
                        changes = compare_file_hashes(stored_hashes, current_file_hashes)
                        impact = calculate_change_impact(changes)
                        
                        if not should_trigger_full_reanalysis(changes, impact):
                            print(f"변경사항이 미미함 - 캐시된 결과 반환 (영향도: {impact['impact_level']})")
                            await github_storage_service.update_last_checked(username, repo_name)
                            return cached_result
                        else:
                            print(f"중요한 변경사항 감지 - 전체 재분석 필요 (영향도: {impact['impact_level']})")
                            
            except Exception as e:
                print(f"파일 변경사항 확인 중 오류: {e} - 기존 캐시 사용")
                if cached_result:
                    return cached_result
        elif cached_result:
            # 프로필 분석인 경우 (repo_name이 없음) 캐시된 결과 반환
            print(f"프로필 분석 캐시된 결과 반환: {username}")
            return cached_result
        
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


                
                # 멀티 레포 분석 프롬프트를 사용하되, 대상 레포만 전달하여 동일한 추출 품질 확보
                summaries = await generate_unified_summary(username, None, None, [analysis_item])

                # detailed_analysis 구성 (고급 분석 제거)
                detailed_analysis = {
                    'tech_stack': {
                        'languages': languages if not isinstance(languages, Exception) else {},
                        'frameworks': dep_hints.get('frameworks', []),
                        'build_tools': dep_hints.get('build_tools', []),
                        'dependency_managers': dep_hints.get('dependency_managers', []),
                        'databases': dep_hints.get('databases', []),
                        'deployment_configs': dep_hints.get('deployment_configs', [])
                    },
                    'dependencies': {
                        'external_libraries': dep_hints.get('external_libraries', []),
                        'llm_libraries': dep_hints.get('llm_hints', [])
                    }
                }
                
                result = GithubSummaryResponse(
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
                
                # MongoDB에 분석 결과 저장 (파일 해시 포함)
                try:
                    current_file_hashes = await generate_file_hashes_from_github(username, repo_name, github_token)
                    await github_storage_service.save_analysis(
                        username, repo_name, result.dict(), current_file_hashes
                    )
                    print(f"MongoDB 저장 완료: {username}/{repo_name}")
                except Exception as e:
                    print(f"MongoDB 저장 중 오류: {e}")
                    # 기존 파일 캐시 시스템도 유지 (백업용)
                    await analysis_cache.cache_analysis(username, repo_name, result.dict())
                
                return result

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
                result = GithubSummaryResponse(
                    profileUrl=profile_url,
                    profileApiUrl=profile_api_url,
                    source='profile_readme',
                    summary=json.dumps(summaries, ensure_ascii=False),
                    language_stats=language_stats,
                    language_total_bytes=language_total_bytes,
                    original_language_stats=chart_response.original_stats,
                    token_usage=get_token_usage()
                )
                
                # MongoDB에 프로필 분석 결과 저장
                try:
                    await github_storage_service.save_analysis(username, None, result.dict())
                    print(f"MongoDB 프로필 저장 완료: {username}")
                except Exception as e:
                    print(f"MongoDB 프로필 저장 중 오류: {e}")
                    # 기존 파일 캐시 시스템도 유지 (백업용)
                    await analysis_cache.cache_analysis(username, None, result.dict())
                
                return result
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
            
            # 자격 판정 먼저 실행
            try:
                qualification_result = await repo_qualification.qualify_repositories(repos, github_token)
                print(f"자격 판정 결과: {len(qualification_result.get('qualified', []))}개 통과, {len(qualification_result.get('hidden', []))}개 제외")
            except Exception as e:
                print(f"자격 판정 실패: {e}")
                qualification_result = {
                    'qualified': [],
                    'hidden': [],
                    'reasons': {}
                }
            
            # 자격판정 통과한 레포지토리 우선 사용, 없으면 기존 필터링 사용
            qualified_repos = qualification_result.get('qualified', [])
            if qualified_repos:
                top_repos = qualified_repos[:4]  # 최대 4개
                print(f"자격판정 통과 레포지토리 {len(top_repos)}개 분석")
            else:
                # 자격판정 통과한 것이 없으면 기존 필터링 사용
                top_repos = await filter_relevant_repositories(repos, max_repos=4)
                print(f"기존 필터링으로 분석할 레포지토리 수: {len(top_repos)}")
            
            if not top_repos:
                # 필터링 결과가 없는 경우 기존 방식으로 폴백 (4개로 증가)
                top_repos = [r for r in repos if not r.get('fork')][:4]
                if not top_repos:
                    top_repos = repos[:4]
                print(f"필터링 실패로 폴백하여 분석: {len(top_repos)}개")
            
            analyses = []

            
            for repo in top_repos:
                owner_login = repo.get('owner', {}).get('login', username)
                
                # 기존 메타데이터 분석 실행
                languages, repo_readme, dep_hints = await asyncio.gather(
                    fetch_repo_languages(owner_login, repo['name'], github_token),
                    fetch_github_readme(owner_login, repo['name'], github_token),
                    collect_dependency_hints(owner_login, repo['name'], github_token),
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
                

                
                analyses.append(analysis_item)
            
            # 통합 요약 생성 (여러 레포지토리) - 정확도 향상
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
            
            # detailed_analysis에 기술 스택 및 자격 판정 결과 포함 (고급 분석 제거)
            print(f"자격 판정 결과 전달: {qualification_result}")
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
                'qualification_results': qualification_result
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
        
        # MongoDB에서 기존 분석 결과 확인 및 증분 업데이트 로직
        print(f"repo-analysis MongoDB에서 기존 분석 확인: {username}/{request.repo_name}")
        
        # 저장된 분석이 최근 것인지 확인 (24시간 이내)
        cached_result = await github_storage_service.get_cached_analysis_if_fresh(username, request.repo_name, max_age_hours=24)
        
        if cached_result:
            # 파일 변경 사항 확인
            try:
                print(f"파일 변경사항 확인 중: {username}/{request.repo_name}")
                current_file_hashes = await generate_file_hashes_from_github(username, request.repo_name, github_token)
                
                if current_file_hashes:
                    update_needed, changed_files = await github_storage_service.check_if_update_needed(
                        username, request.repo_name, current_file_hashes
                    )
                    
                    if not update_needed:
                        print(f"변경사항 없음 - 캐시된 결과 반환: {username}/{request.repo_name}")
                        await github_storage_service.update_last_checked(username, request.repo_name)
                        return GithubSummaryResponse(**cached_result)
                    else:
                        print(f"변경된 파일 {len(changed_files)}개 감지 - 재분석 진행")
                        # 변경 영향도 분석
                        stored_hashes = await github_storage_service.get_stored_file_hashes(username, request.repo_name)
                        changes = compare_file_hashes(stored_hashes, current_file_hashes)
                        impact = calculate_change_impact(changes)
                        
                        if not should_trigger_full_reanalysis(changes, impact):
                            print(f"변경사항이 미미함 - 캐시된 결과 반환 (영향도: {impact['impact_level']})")
                            await github_storage_service.update_last_checked(username, request.repo_name)
                            return GithubSummaryResponse(**cached_result)
                        else:
                            print(f"중요한 변경사항 감지 - 전체 재분석 필요 (영향도: {impact['impact_level']})")
                            
            except Exception as e:
                print(f"파일 변경사항 확인 중 오류: {e} - 기존 캐시 사용")
                if cached_result:
                    return GithubSummaryResponse(**cached_result)
        
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

        result = GithubSummaryResponse(
            profileUrl=profile_url,
            profileApiUrl=profile_api_url,
            source=f'repo_analysis_{request.repo_name}',
            summary=json.dumps(summaries, ensure_ascii=False),
            language_stats=language_stats,
            language_total_bytes=language_total_bytes,
            original_language_stats=chart_response.original_stats,
            token_usage=None
        )
        
        # MongoDB에 분석 결과 저장 (파일 해시 포함)
        try:
            current_file_hashes = await generate_file_hashes_from_github(username, request.repo_name, github_token)
            await github_storage_service.save_analysis(
                username, request.repo_name, result.dict(), current_file_hashes
            )
            print(f"repo-analysis MongoDB 저장 완료: {username}/{request.repo_name}")
        except Exception as e:
            print(f"repo-analysis MongoDB 저장 중 오류: {e}")
        
        return result
        
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


@router.get("/github/analysis-status/{username}")
async def get_analysis_status(username: str, repo_name: Optional[str] = None):
    """분석 상태 및 히스토리 조회"""
    try:
        stored_analysis = await github_storage_service.get_stored_analysis(username, repo_name)
        
        if not stored_analysis:
            return {
                "status": "not_found",
                "message": "저장된 분석 결과가 없습니다."
            }
        
        return {
            "status": "found",
            "last_analyzed": stored_analysis.get('created_at'),
            "last_checked": stored_analysis.get('last_checked'),
            "repo_key": stored_analysis.get('repo_key'),
            "has_file_hashes": bool(await github_storage_service.get_stored_file_hashes(username, repo_name))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 상태 조회 중 오류: {str(e)}")


@router.post("/github/force-reanalysis")
async def force_reanalysis(request: GithubSummaryRequest):
    """강제 재분석 (캐시 무시)"""
    try:
        # 기존 분석 데이터 삭제
        client = github_storage_service._get_client()
        try:
            collection, hashes_collection = github_storage_service._get_collections(client)
            username = resolve_username(request.username)
            repo_key = github_storage_service._generate_repo_key(username, request.repo_name)
            
            collection.delete_one({"repo_key": repo_key})
            hashes_collection.delete_many({"repo_key": repo_key})
            
            print(f"기존 분석 데이터 삭제 완료: {repo_key}")
            
        finally:
            client.close()
        
        # 새로운 분석 실행
        if request.repo_name:
            return await github_repo_analysis(request)
        else:
            return await github_summary(request)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강제 재분석 중 오류: {str(e)}")


@router.post("/github/cleanup-old-analyses")
async def cleanup_old_analyses(days_old: int = 30):
    """오래된 분석 결과 정리"""
    try:
        await github_storage_service.cleanup_old_analyses(days_old)
        return {"status": "success", "message": f"{days_old}일 이상 된 분석 결과를 정리했습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정리 중 오류: {str(e)}")


@router.get("/github/file-changes/{username}/{repo_name}")
async def get_file_changes(username: str, repo_name: str):
    """파일 변경사항 확인"""
    try:
        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN') or ''
        
        # 현재 파일 해시 생성
        current_file_hashes = await generate_file_hashes_from_github(username, repo_name, github_token)
        
        if not current_file_hashes:
            return {"status": "error", "message": "파일 해시를 생성할 수 없습니다."}
        
        # 저장된 해시와 비교
        update_needed, changed_files = await github_storage_service.check_if_update_needed(
            username, repo_name, current_file_hashes
        )
        
        if not update_needed:
            return {
                "status": "no_changes",
                "message": "변경된 파일이 없습니다.",
                "total_files": len(current_file_hashes)
            }
        
        # 변경사항 분석
        stored_hashes = await github_storage_service.get_stored_file_hashes(username, repo_name)
        changes = compare_file_hashes(stored_hashes, current_file_hashes)
        impact = calculate_change_impact(changes)
        
        return {
            "status": "changes_detected",
            "changes": changes,
            "impact": impact,
            "should_reanalyze": should_trigger_full_reanalysis(changes, impact),
            "total_files": len(current_file_hashes),
            "changed_files_count": len(changed_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 변경사항 확인 중 오류: {str(e)}")





# 레포지토리 자격 판정 및 점수화 시스템
class RepositoryQualificationSystem:
    """레포지토리 자격 판정 및 점수화 시스템"""
    
    def __init__(self):
        # 샘플 키워드 (강한 제외 신호)
        self.sample_keywords = ['sample', 'demo', 'tutorial', 'study', 'practice', 'playground', 'test']
        
        # 빌드/실행 신호 파일들
        self.build_signals = [
            'package.json', 'requirements.txt', 'go.mod', 'cargo.toml', 'pom.xml', 'build.gradle',
            'Dockerfile', 'docker-compose.yml', '.github/workflows', 'Makefile', 'CMakeLists.txt',
            'setup.py', 'pyproject.toml', 'composer.json', 'Gemfile', 'Podfile', 'pubspec.yaml'
        ]
        
        # 매니페스트 파일들
        self.manifest_files = [
            'package.json', 'requirements.txt', 'go.mod', 'cargo.toml', 'pom.xml', 'build.gradle',
            'setup.py', 'pyproject.toml', 'composer.json', 'Gemfile', 'Podfile', 'pubspec.yaml'
        ]
        
        # 테스트 관련 파일들
        self.test_files = [
            'test', 'tests', 'spec', 'specs', '__tests__', 'test_', 'spec_',
            'jest.config', 'pytest.ini', 'tox.ini', '.coveragerc', 'coverage'
        ]
        
        # CI/CD 관련 파일들
        self.ci_files = [
            '.github/workflows', '.gitlab-ci.yml', '.travis.yml', '.circleci',
            'Jenkinsfile', 'azure-pipelines.yml', '.drone.yml', 'appveyor.yml'
        ]
        
        # 인프라 관련 파일들
        self.infra_files = [
            'Dockerfile', 'docker-compose.yml', 'kubernetes', 'k8s', 'helm',
            'terraform', 'ansible', 'puppet', 'chef', 'cloudformation'
        ]

    async def qualify_repositories(self, repos: List[Dict], token: Optional[str] = None) -> Dict:
        """레포지토리 자격 판정 및 점수화"""
        if not repos:
            return {'qualified': [], 'hidden': [], 'reasons': {}}
        
        qualified_repos = []
        hidden_repos = []
        reasons = {}
        
        for repo in repos:
            qualification_result = await self._qualify_single_repo(repo, token)
            
            if qualification_result['qualified']:
                qualified_repos.append({
                    **repo,
                    '_score': qualification_result['score'],
                    '_score_breakdown': qualification_result['score_breakdown']
                })
            else:
                hidden_repos.append({
                    **repo,
                    '_exclusion_reason': qualification_result['exclusion_reason']
                })
                reasons[repo.get('name', '')] = qualification_result['exclusion_reason']
        
        # 점수 순으로 정렬
        qualified_repos.sort(key=lambda x: x.get('_score', 0), reverse=True)
        
        return {
            'qualified': qualified_repos,
            'hidden': hidden_repos,
            'reasons': reasons
        }

    async def _qualify_single_repo(self, repo: Dict, token: Optional[str] = None) -> Dict:
        """단일 레포지토리 자격 판정"""
        repo_name = repo.get('name', '').lower()
        description = (repo.get('description') or '').lower()
        
        # 1. 자격 판정 (하드 필터)
        
        # 1-1. 코드 존재 여부 확인
        code_ratio, code_loc = await self._check_code_existence(repo, token)
        if code_ratio < 0.2 and code_loc < 200:
            return {
                'qualified': False,
                'exclusion_reason': 'docs-only',
                'score': 0,
                'score_breakdown': {}
            }
        
        # 1-2. 빌드/실행 신호 확인
        has_build_signal = await self._check_build_signals(repo, token)
        if not has_build_signal:
            return {
                'qualified': False,
                'exclusion_reason': 'no-build-signal',
                'score': 0,
                'score_breakdown': {}
            }
        
        # 1-3. 최근성 확인 (12개월 이내)
        is_recent = self._check_recency(repo)
        if not is_recent:
            return {
                'qualified': False,
                'exclusion_reason': 'stale(>12m)',
                'score': 0,
                'score_breakdown': {}
            }
        
        # 1-4. archived 확인
        if repo.get('archived', False):
            return {
                'qualified': False,
                'exclusion_reason': 'archived',
                'score': 0,
                'score_breakdown': {}
            }
        
        # 1-5. 의미 있는 기여 없는 fork 확인
        if repo.get('fork', False):
            meaningful_fork = await self._check_meaningful_fork(repo, token)
            if not meaningful_fork:
                return {
                    'qualified': False,
                    'exclusion_reason': 'meaningless-fork',
                    'score': 0,
                    'score_breakdown': {}
                }
        
        # 1-6. 샘플 키워드 + 코드 LOC < 1000 확인
        has_sample_keyword = any(keyword in repo_name or keyword in description for keyword in self.sample_keywords)
        if has_sample_keyword and code_loc < 1000:
            return {
                'qualified': False,
                'exclusion_reason': 'tutorial',
                'score': 0,
                'score_breakdown': {}
            }
        
        # 2. 점수화 (랭킹)
        score_breakdown = await self._calculate_score(repo, token)
        total_score = sum(score_breakdown.values())
        
        return {
            'qualified': True,
            'score': total_score,
            'score_breakdown': score_breakdown,
            'exclusion_reason': None
        }

    async def _check_code_existence(self, repo: Dict, token: Optional[str] = None) -> Tuple[float, int]:
        """코드 존재 여부 확인 (코드 비율 ≥ 20% 또는 코드 LOC ≥ 200)"""
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 언어 통계 가져오기
            languages = await fetch_repo_languages(owner, repo_name, token)
            if not languages:
                return 0.0, 0
            
            total_bytes = sum(languages.values())
            code_bytes = sum(bytes for lang, bytes in languages.items() 
                           if lang.lower() not in ['markdown', 'text', 'html', 'css'])
            
            code_ratio = code_bytes / total_bytes if total_bytes > 0 else 0.0
            
            # LOC 추정 (1KB ≈ 50 LOC)
            code_loc = int(code_bytes / 1024 * 50)
            
            return code_ratio, code_loc
            
        except Exception as e:
            print(f"코드 존재 확인 오류: {e}")
            return 0.0, 0

    async def _check_build_signals(self, repo: Dict, token: Optional[str] = None) -> bool:
        """빌드/실행 신호 확인"""
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 최상위 파일 목록 가져오기
            files = await fetch_repo_top_level_files(owner, repo_name, token)
            file_names = [f['name'].lower() for f in files]
            
            # 빌드 신호 파일 확인
            for signal in self.build_signals:
                if any(signal in fname for fname in file_names):
                    return True
            
            # 추가 신호 확인: 소스 코드 파일 존재
            source_extensions = ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']
            has_source_files = any(any(ext in fname for ext in source_extensions) for fname in file_names)
            
            # README 파일 존재 확인
            has_readme = any('readme' in fname for fname in file_names)
            
            # 소스 파일이 있고 README가 있으면 빌드 신호로 간주
            if has_source_files and has_readme:
                return True
            
            return False
            
        except Exception as e:
            print(f"빌드 신호 확인 오류: {e}")
            return False

    def _check_recency(self, repo: Dict) -> bool:
        """최근성 확인 (12개월 이내)"""
        try:
            pushed_at = repo.get('pushed_at') or repo.get('updated_at')
            if not pushed_at:
                return False
            
            push_time = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_diff = (now - push_time).days
            
            return days_diff <= 365  # 12개월 이내
            
        except Exception as e:
            print(f"최근성 확인 오류: {e}")
            return False

    async def _check_meaningful_fork(self, repo: Dict, token: Optional[str] = None) -> bool:
        """의미 있는 기여 없는 fork 확인"""
        try:
            # 스타 수가 원본보다 많거나, 최근 커밋이 있으면 의미 있는 fork
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            
            # 스타나 포크가 있으면 의미 있는 fork로 간주
            if stars > 0 or forks > 0:
                return True
            
            # 최근 업데이트 확인
            if self._check_recency(repo):
                return True
            
            return False
            
        except Exception as e:
            print(f"의미 있는 fork 확인 오류: {e}")
            return False

    async def _calculate_score(self, repo: Dict, token: Optional[str] = None) -> Dict[str, float]:
        """점수화 (총점 100 기준)"""
        score_breakdown = {
            'maturity': 0,      # 성숙도 (30점)
            'activity': 0,      # 활동성·커뮤니티 (25점)
            'code_scale': 0,    # 코드 규모·구조 (20점)
            'deployment': 0,    # 배포 흔적 (15점)
            'impact': 0         # 영향도 (10점)
        }
        
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 1. 성숙도 (30점)
            score_breakdown['maturity'] = await self._calculate_maturity_score(repo, token)
            
            # 2. 활동성·커뮤니티 (25점)
            score_breakdown['activity'] = self._calculate_activity_score(repo)
            
            # 3. 코드 규모·구조 (20점)
            score_breakdown['code_scale'] = await self._calculate_code_scale_score(repo, token)
            
            # 4. 배포 흔적 (15점)
            score_breakdown['deployment'] = await self._calculate_deployment_score(repo, token)
            
            # 5. 영향도 (10점)
            score_breakdown['impact'] = self._calculate_impact_score(repo)
            
        except Exception as e:
            print(f"점수 계산 오류: {e}")
        
        return score_breakdown

    async def _calculate_maturity_score(self, repo: Dict, token: Optional[str] = None) -> float:
        """성숙도 점수 계산 (30점)"""
        score = 0
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 파일 목록 가져오기
            files = await fetch_repo_top_level_files(owner, repo_name, token)
            file_names = [f['name'].lower() for f in files]
            
            # 매니페스트 파일 (6점)
            has_manifest = any(any(manifest in fname for fname in file_names) 
                             for manifest in self.manifest_files)
            if has_manifest:
                score += 6
            
            # 테스트 파일 (6점)
            has_test = any(any(test in fname for fname in file_names) 
                          for test in self.test_files)
            if has_test:
                score += 6
            
            # CI/CD 파일 (6점)
            has_ci = any(any(ci in fname for fname in file_names) 
                        for ci in self.ci_files)
            if has_ci:
                score += 6
            
            # 릴리스 정보 (6점)
            releases = repo.get('releases_count', 0)
            if releases > 0:
                score += min(releases * 2, 6)
            
            # 인프라 파일 (6점)
            has_infra = any(any(infra in fname for fname in file_names) 
                           for infra in self.infra_files)
            if has_infra:
                score += 6
            
        except Exception as e:
            print(f"성숙도 점수 계산 오류: {e}")
        
        return min(score, 30)

    def _calculate_activity_score(self, repo: Dict) -> float:
        """활동성·커뮤니티 점수 계산 (25점)"""
        score = 0
        
        # Star 수 (로그 스케일, 10점)
        stars = repo.get('stargazers_count', 0)
        if stars > 0:
            score += min(math.log(stars + 1) * 2, 10)
        
        # Fork 수 (로그 스케일, 8점)
        forks = repo.get('forks_count', 0)
        if forks > 0:
            score += min(math.log(forks + 1) * 1.5, 8)
        
        # 최근 업데이트 (7점)
        pushed_at = repo.get('pushed_at') or repo.get('updated_at')
        if pushed_at:
            try:
                push_time = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                days_diff = (now - push_time).days
                
                if days_diff <= 30:
                    score += 7
                elif days_diff <= 90:
                    score += 5
                elif days_diff <= 180:
                    score += 3
                elif days_diff <= 365:
                    score += 1
            except:
                pass
        
        return min(score, 25)

    async def _calculate_code_scale_score(self, repo: Dict, token: Optional[str] = None) -> float:
        """코드 규모·구조 점수 계산 (20점)"""
        score = 0
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 언어 통계 가져오기
            languages = await fetch_repo_languages(owner, repo_name, token)
            if languages:
                total_bytes = sum(languages.values())
                code_bytes = sum(bytes for lang, bytes in languages.items() 
                               if lang.lower() not in ['markdown', 'text', 'html', 'css'])
                
                # LOC 기반 점수 (10점)
                loc = int(code_bytes / 1024 * 50)
                if loc >= 10000:
                    score += 10
                elif loc >= 5000:
                    score += 8
                elif loc >= 2000:
                    score += 6
                elif loc >= 1000:
                    score += 4
                elif loc >= 500:
                    score += 2
            
            # 모듈 구조 점수 (10점)
            files = await fetch_repo_top_level_files(owner, repo_name, token)
            file_names = [f['name'].lower() for f in files]
            
            # 주요 디렉토리 구조 확인
            has_src = any('src' in fname for fname in file_names)
            has_lib = any('lib' in fname for fname in file_names)
            has_app = any('app' in fname for fname in file_names)
            has_components = any('components' in fname for fname in file_names)
            has_utils = any('utils' in fname for fname in file_names)
            
            structure_score = sum([has_src, has_lib, has_app, has_components, has_utils])
            score += min(structure_score * 2, 10)
            
        except Exception as e:
            print(f"코드 규모 점수 계산 오류: {e}")
        
        return min(score, 20)

    async def _calculate_deployment_score(self, repo: Dict, token: Optional[str] = None) -> float:
        """배포 흔적 점수 계산 (15점)"""
        score = 0
        try:
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            
            # 파일 목록 가져오기
            files = await fetch_repo_top_level_files(owner, repo_name, token)
            file_names = [f['name'].lower() for f in files]
            
            # Docker 관련 (5점)
            has_docker = any('docker' in fname for fname in file_names)
            if has_docker:
                score += 5
            
            # K8s 관련 (3점)
            has_k8s = any('kubernetes' in fname or 'k8s' in fname for fname in file_names)
            if has_k8s:
                score += 3
            
            # IaC 관련 (3점)
            has_iac = any('terraform' in fname or 'ansible' in fname or 'puppet' in fname for fname in file_names)
            if has_iac:
                score += 3
            
            # README 품질 (4점)
            readme = await fetch_github_readme(owner, repo_name, token)
            if readme and readme.get('text'):
                readme_text = readme['text']
                # README 길이와 구조로 품질 평가
                if len(readme_text) > 1000:
                    score += 2
                if '##' in readme_text:  # 섹션 구조
                    score += 1
                if '```' in readme_text:  # 코드 예제
                    score += 1
            
        except Exception as e:
            print(f"배포 점수 계산 오류: {e}")
        
        return min(score, 15)

    def _calculate_impact_score(self, repo: Dict) -> float:
        """영향도 점수 계산 (10점)"""
        score = 0
        
        # 외부 참조 (5점)
        # GitHub에서 외부 참조를 직접 확인하기 어려우므로 간접 지표 사용
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        
        if stars > 100:
            score += 3
        elif stars > 50:
            score += 2
        elif stars > 10:
            score += 1
        
        if forks > 50:
            score += 2
        elif forks > 20:
            score += 1
        
        # 레지스트리 배포 (5점)
        # package.json, setup.py 등이 있으면 배포 가능성으로 간주
        description = (repo.get('description') or '').lower()
        if any(keyword in description for keyword in ['npm', 'pypi', 'crates', 'maven', 'nuget']):
            score += 5
        elif 'package' in description or 'library' in description:
            score += 3
        
        return min(score, 10)

# 전역 인스턴스
repo_qualification = RepositoryQualificationSystem()

async def filter_relevant_repositories(repos, max_repos=5):
    """
    새로운 자격 판정 및 점수화 시스템을 사용한 레포지토리 필터링
    
    자격 판정 (하드 필터):
    - 코드 존재: 코드 비율 ≥ 20% 또는 코드 LOC ≥ 200
    - 빌드/실행 신호: package.json/requirements.txt/go.mod/Dockerfile 등 하나 이상
    - 최근성: pushed_at 12개월 이내
    - 제외: archived=true, 의미 있는 기여 없는 fork
    - 샘플 키워드 강함 & 코드 LOC < 1000 → 제외
    
    점수화 (랭킹):
    - 성숙도(30): 매니페스트/테스트/CI/릴리스/인프라
    - 활동성·커뮤니티(25): 최근 커밋·이슈/PR·Star/Fork(로그 스케일)
    - 코드 규모·구조(20): LOC·모듈 구조
    - 배포 흔적(15): Docker/K8s/IaC·README 품질
    - 영향도(10): 외부 참조·레지스트리 배포
    """
    if not repos:
        return []
    
    # 자격 판정 실행
    try:
        result = await repo_qualification.qualify_repositories(repos)
        
        qualified_repos = result['qualified']
        hidden_repos = result['hidden']
        reasons = result['reasons']
        
        # 최소 임계치 35점 이상만 선택
        threshold_repos = [repo for repo in qualified_repos if repo.get('_score', 0) >= 35]
        
        # 동률 처리: 점수순 → 최근 커밋 → 최신 릴리스 → Star
        def sort_key(repo):
            score = repo.get('_score', 0)
            pushed_at = repo.get('pushed_at') or repo.get('updated_at', '')
            releases = repo.get('releases_count', 0)
            stars = repo.get('stargazers_count', 0)
            
            # 날짜를 숫자로 변환 (최신일수록 큰 값)
            try:
                if pushed_at:
                    push_time = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                    date_score = push_time.timestamp()
                else:
                    date_score = 0
            except:
                date_score = 0
            
            return (score, date_score, releases, stars)
        
        # 정렬 후 상위 4~5개 선택
        threshold_repos.sort(key=sort_key, reverse=True)
        selected_repos = threshold_repos[:max_repos]
        
        # 임계치 미달 레포는 숨김으로 이동
        below_threshold = [repo for repo in qualified_repos if repo.get('_score', 0) < 35]
        for repo in below_threshold:
            repo['_exclusion_reason'] = 'below-threshold'
            hidden_repos.append(repo)
            reasons[repo.get('name', '')] = 'below-threshold'
        
        # 핵심 배지 정보 추가
        for repo in selected_repos:
            repo['_hidden_count'] = len(hidden_repos)
            repo['_hidden_reasons'] = reasons
            
            # 핵심 배지 생성
            badges = []
            
            # Stars 배지
            stars = repo.get('stargazers_count', 0)
            if stars > 0:
                badges.append(f"⭐ {stars}")
            
            # Recent commits 배지
            pushed_at = repo.get('pushed_at') or repo.get('updated_at', '')
            if pushed_at:
                try:
                    push_time = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    days_diff = (now - push_time).days
                    
                    if days_diff <= 7:
                        badges.append("🟢 Recent")
                    elif days_diff <= 30:
                        badges.append("🟡 Active")
                    elif days_diff <= 90:
                        badges.append("🟠 Recent")
                except:
                    pass
            
            # Releases 배지
            releases = repo.get('releases_count', 0)
            if releases > 0:
                badges.append(f"📦 {releases}")
            
            # CI/Docker 배지 (기존 분석 결과에서 확인)
            score_breakdown = repo.get('_score_breakdown', {})
            if score_breakdown.get('maturity', 0) >= 6:  # CI/CD 파일이 있으면 성숙도 점수에서 확인
                badges.append("🔄 CI")
            if score_breakdown.get('deployment', 0) >= 5:  # Docker 관련 점수에서 확인
                badges.append("🐳 Docker")
            
            repo['_badges'] = badges
        
        print(f"자격 판정 결과: {len(repos)}개 중 {len(qualified_repos)}개 자격 통과, {len(selected_repos)}개 선택")
        print(f"숨김 레포: {len(hidden_repos)}개")
        for reason, count in Counter(reasons.values()).items():
            print(f"  - {reason}: {count}개")
        
        return selected_repos
        
    except Exception as e:
        print(f"자격 판정 중 오류: {e}")
        # 오류 발생 시 기존 방식으로 폴백
        return _fallback_filter(repos, max_repos)

def _fallback_filter(repos, max_repos=5):
    """기존 필터링 방식 (폴백용)"""
    if not repos:
        return []
    
    # 제외할 키워드 (개인용, 테스트용, 학습용 등)
    exclude_keywords = [
        'test', 'demo', 'example', 'sample', 'tutorial', 'learning', 'study',
        'practice', 'playground', 'temp', 'tmp', 'backup', 'old', 'archive',
        'deprecated', 'personal', 'notes', 'blog', 'website', 'portfolio',
        'resume', 'cv', 'profile', 'homepage'
    ]
    
    filtered_repos = []
    
    for repo in repos:
        repo_name = (repo.get('name') or '').lower()
        description = (repo.get('description') or '').lower()
        
        # 제외 키워드 체크
        should_exclude = False
        for keyword in exclude_keywords:
            if keyword in repo_name or keyword in description:
                should_exclude = True
                break
        
        if should_exclude:
            continue
        
        # 기본 스코어 계산
        score = 0
        score += repo.get('stargazers_count', 0)
        score += repo.get('forks_count', 0) * 0.5
        
        if repo.get('description'):
            score += 5
        
        if not repo.get('fork', False):
            score += 10
        
        if score >= 5:
            repo['_score'] = score
            filtered_repos.append(repo)
    
    filtered_repos.sort(key=lambda x: x.get('_score', 0), reverse=True)
    return filtered_repos[:max_repos]
 