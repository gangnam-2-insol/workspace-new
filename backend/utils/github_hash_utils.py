"""
GitHub 저장소 파일들의 해시 생성 및 비교를 위한 유틸리티
"""

import hashlib
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import os


async def generate_file_hashes_from_github(owner: str, repo: str, token: str = None, 
                                         branch: str = "main") -> Dict[str, str]:
    """GitHub API를 통해 저장소의 모든 파일에 대한 해시를 생성"""
    
    async def fetch_tree_recursively(sha: str) -> List[Dict]:
        """GitHub API를 통해 재귀적으로 파일 트리 가져오기"""
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('tree', [])
                else:
                    print(f"파일 트리 조회 실패: {response.status}")
                    return []
    
    async def get_file_content(file_path: str) -> Optional[str]:
        """GitHub API를 통해 파일 내용 가져오기"""
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('type') == 'file' and 'content' in data:
                        import base64
                        try:
                            content = base64.b64decode(data['content']).decode('utf-8')
                            return content
                        except UnicodeDecodeError:
                            # 바이너리 파일인 경우 해시는 GitHub의 SHA를 사용
                            return f"BINARY_FILE_SHA:{data.get('sha', '')}"
                return None
    
    try:
        # 저장소의 기본 브랜치 정보 가져오기
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        async with aiohttp.ClientSession() as session:
            # 저장소 정보 조회하여 기본 브랜치 확인
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            async with session.get(repo_url, headers=headers) as response:
                if response.status == 200:
                    repo_data = await response.json()
                    default_branch = repo_data.get('default_branch', 'main')
                else:
                    default_branch = branch
            
            # 브랜치의 최신 커밋 SHA 가져오기
            branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{default_branch}"
            async with session.get(branch_url, headers=headers) as response:
                if response.status == 200:
                    branch_data = await response.json()
                    commit_sha = branch_data['commit']['sha']
                else:
                    print(f"브랜치 정보 조회 실패: {response.status}")
                    return {}
        
        # 파일 트리 가져오기
        tree_items = await fetch_tree_recursively(commit_sha)
        
        # 일반 파일들만 필터링 (디렉토리 제외)
        file_items = [item for item in tree_items if item.get('type') == 'blob']
        
        file_hashes = {}
        
        # 중요한 파일들의 내용 기반 해시 생성
        important_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.yml', '.yaml', 
                              '.toml', '.cfg', '.ini', '.txt', '.sql', '.html', '.css', '.scss', 
                              '.vue', '.php', '.rb', '.go', '.rs', '.java', '.cpp', '.c', '.h'}
        
        # 배치 처리를 위한 세마포어 (동시 요청 수 제한)
        semaphore = asyncio.Semaphore(10)
        
        async def process_file(item):
            async with semaphore:
                file_path = item['path']
                file_extension = os.path.splitext(file_path)[1].lower()
                
                if file_extension in important_extensions and item['size'] < 1024 * 1024:  # 1MB 이하
                    # 내용 기반 해시
                    content = await get_file_content(file_path)
                    if content:
                        if content.startswith("BINARY_FILE_SHA:"):
                            file_hashes[file_path] = content
                        else:
                            file_hashes[file_path] = hashlib.sha256(content.encode('utf-8')).hexdigest()
                else:
                    # GitHub SHA 사용 (바이너리 파일이나 큰 파일)
                    file_hashes[file_path] = f"GH_SHA:{item['sha']}"
        
        # 병렬로 파일 처리
        await asyncio.gather(*[process_file(item) for item in file_items])
        
        print(f"파일 해시 생성 완료: {len(file_hashes)}개 파일")
        return file_hashes
        
    except Exception as e:
        print(f"파일 해시 생성 중 오류: {e}")
        return {}


def compare_file_hashes(old_hashes: Dict[str, str], new_hashes: Dict[str, str]) -> Dict[str, List[str]]:
    """파일 해시 비교하여 변경사항 분석"""
    
    result = {
        'added': [],      # 새로 추가된 파일
        'modified': [],   # 수정된 파일
        'deleted': [],    # 삭제된 파일
        'unchanged': []   # 변경되지 않은 파일
    }
    
    # 새 파일과 수정된 파일 찾기
    for file_path, new_hash in new_hashes.items():
        if file_path not in old_hashes:
            result['added'].append(file_path)
        elif old_hashes[file_path] != new_hash:
            result['modified'].append(file_path)
        else:
            result['unchanged'].append(file_path)
    
    # 삭제된 파일 찾기
    for file_path in old_hashes:
        if file_path not in new_hashes:
            result['deleted'].append(file_path)
    
    return result


def calculate_change_impact(changes: Dict[str, List[str]]) -> Dict[str, Any]:
    """변경사항의 영향도 계산"""
    
    total_files = len(changes['added']) + len(changes['modified']) + len(changes['deleted']) + len(changes['unchanged'])
    changed_files = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
    
    if total_files == 0:
        return {'impact_level': 'none', 'change_ratio': 0.0}
    
    change_ratio = changed_files / total_files
    
    # 영향도 수준 결정
    if change_ratio == 0:
        impact_level = 'none'
    elif change_ratio < 0.1:
        impact_level = 'low'
    elif change_ratio < 0.3:
        impact_level = 'medium'
    elif change_ratio < 0.6:
        impact_level = 'high'
    else:
        impact_level = 'major'
    
    # 중요한 파일 변경 여부 확인
    important_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml', 'go.mod', 
                      'README.md', 'LICENSE', '.gitignore', 'Dockerfile', 'docker-compose.yml']
    
    important_changed = any(
        any(important_file in file_path for important_file in important_files)
        for file_path in changes['added'] + changes['modified'] + changes['deleted']
    )
    
    return {
        'impact_level': impact_level,
        'change_ratio': change_ratio,
        'total_files': total_files,
        'changed_files': changed_files,
        'important_files_changed': important_changed,
        'changes_detail': {
            'added_count': len(changes['added']),
            'modified_count': len(changes['modified']),
            'deleted_count': len(changes['deleted'])
        }
    }


def should_trigger_full_reanalysis(changes: Dict[str, List[str]], 
                                 impact_analysis: Dict[str, Any]) -> bool:
    """전체 재분석이 필요한지 판단"""
    
    # 중요한 파일이 변경된 경우
    if impact_analysis.get('important_files_changed', False):
        return True
    
    # 변경 비율이 높은 경우
    if impact_analysis.get('change_ratio', 0) > 0.5:
        return True
    
    # 새로 추가된 파일이 많은 경우
    if len(changes.get('added', [])) > 10:
        return True
    
    return False
