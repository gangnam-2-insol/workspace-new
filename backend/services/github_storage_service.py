"""
GitHub 분석 결과를 MongoDB에 저장하고 증분 업데이트를 관리하는 서비스
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pymongo import MongoClient
from pymongo.collection import Collection
import os
import asyncio


class GitHubStorageService:
    """GitHub 분석 결과의 MongoDB 저장 및 증분 업데이트 관리"""
    
    def __init__(self, mongodb_uri: str = None, db_name: str = "hireme"):
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.db_name = db_name
        self.collection_name = "github_analyses"
        self.file_hashes_collection = "github_file_hashes"
        
    def _get_client(self) -> MongoClient:
        """MongoDB 클라이언트 생성"""
        return MongoClient(self.mongodb_uri)
    
    def _get_collections(self, client: MongoClient) -> Tuple[Collection, Collection]:
        """컬렉션 참조 반환"""
        db = client[self.db_name]
        return db[self.collection_name], db[self.file_hashes_collection]
    
    def _generate_content_hash(self, content: str) -> str:
        """콘텐츠 해시 생성"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_repo_key(self, username: str, repo_name: Optional[str] = None) -> str:
        """저장소 키 생성"""
        return f"{username}:{repo_name or 'profile'}"
    
    async def get_stored_analysis(self, username: str, repo_name: Optional[str] = None) -> Optional[Dict]:
        """저장된 분석 결과 조회"""
        client = self._get_client()
        try:
            collection, _ = self._get_collections(client)
            repo_key = self._generate_repo_key(username, repo_name)
            
            result = collection.find_one({"repo_key": repo_key})
            if result:
                # MongoDB ObjectId는 JSON 직렬화할 수 없으므로 제거
                result.pop('_id', None)
                return result
            return None
            
        finally:
            client.close()
    
    async def save_analysis(self, username: str, repo_name: Optional[str], analysis_data: Dict, 
                          file_hashes: Dict[str, str] = None) -> str:
        """분석 결과 저장"""
        client = self._get_client()
        try:
            collection, hashes_collection = self._get_collections(client)
            repo_key = self._generate_repo_key(username, repo_name)
            
            # 분석 데이터 준비
            document = {
                "repo_key": repo_key,
                "username": username,
                "repo_name": repo_name,
                "analysis_data": analysis_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_checked": datetime.utcnow()
            }
            
            # 기존 데이터가 있으면 업데이트, 없으면 생성
            result = collection.replace_one(
                {"repo_key": repo_key},
                document,
                upsert=True
            )
            
            # 파일 해시 정보 저장 (증분 업데이트용)
            if file_hashes:
                await self._save_file_hashes(hashes_collection, repo_key, file_hashes)
            
            print(f"GitHub 분석 결과 MongoDB 저장 완료: {repo_key}")
            return str(result.upserted_id or "updated")
            
        finally:
            client.close()
    
    async def _save_file_hashes(self, hashes_collection: Collection, repo_key: str, file_hashes: Dict[str, str]):
        """파일 해시 정보 저장"""
        # 기존 해시 데이터 삭제 후 새로 저장
        hashes_collection.delete_many({"repo_key": repo_key})
        
        if file_hashes:
            hash_documents = [
                {
                    "repo_key": repo_key,
                    "file_path": file_path,
                    "hash": file_hash,
                    "updated_at": datetime.utcnow()
                }
                for file_path, file_hash in file_hashes.items()
            ]
            hashes_collection.insert_many(hash_documents)
    
    async def get_stored_file_hashes(self, username: str, repo_name: Optional[str] = None) -> Dict[str, str]:
        """저장된 파일 해시 조회"""
        client = self._get_client()
        try:
            _, hashes_collection = self._get_collections(client)
            repo_key = self._generate_repo_key(username, repo_name)
            
            results = hashes_collection.find({"repo_key": repo_key})
            return {doc["file_path"]: doc["hash"] for doc in results}
            
        finally:
            client.close()
    
    async def check_if_update_needed(self, username: str, repo_name: Optional[str], 
                                   current_file_hashes: Dict[str, str]) -> Tuple[bool, List[str]]:
        """업데이트가 필요한지 확인하고 변경된 파일 목록 반환"""
        stored_hashes = await self.get_stored_file_hashes(username, repo_name)
        
        if not stored_hashes:
            # 저장된 해시가 없으면 전체 분석 필요
            return True, list(current_file_hashes.keys())
        
        changed_files = []
        
        # 변경된 파일 또는 새 파일 찾기
        for file_path, current_hash in current_file_hashes.items():
            if file_path not in stored_hashes or stored_hashes[file_path] != current_hash:
                changed_files.append(file_path)
        
        # 삭제된 파일 찾기
        for file_path in stored_hashes:
            if file_path not in current_file_hashes:
                changed_files.append(f"DELETED:{file_path}")
        
        return len(changed_files) > 0, changed_files
    
    async def get_cached_analysis_if_fresh(self, username: str, repo_name: Optional[str] = None, 
                                         max_age_hours: int = 24) -> Optional[Dict]:
        """지정된 시간보다 최근 데이터인 경우에만 캐시된 분석 결과 반환"""
        stored_analysis = await self.get_stored_analysis(username, repo_name)
        
        if not stored_analysis:
            return None
        
        last_checked = stored_analysis.get('last_checked')
        if not last_checked:
            return None
        
        # last_checked가 문자열인 경우 datetime으로 변환
        if isinstance(last_checked, str):
            last_checked = datetime.fromisoformat(last_checked.replace('Z', '+00:00'))
        
        # 시간 비교 (UTC 기준)
        if datetime.utcnow() - last_checked.replace(tzinfo=None) <= timedelta(hours=max_age_hours):
            return stored_analysis['analysis_data']
        
        return None
    
    async def update_last_checked(self, username: str, repo_name: Optional[str] = None):
        """마지막 확인 시간 업데이트"""
        client = self._get_client()
        try:
            collection, _ = self._get_collections(client)
            repo_key = self._generate_repo_key(username, repo_name)
            
            collection.update_one(
                {"repo_key": repo_key},
                {"$set": {"last_checked": datetime.utcnow()}}
            )
            
        finally:
            client.close()
    
    async def get_analysis_history(self, username: str, repo_name: Optional[str] = None, 
                                 limit: int = 10) -> List[Dict]:
        """분석 히스토리 조회 (향후 확장용)"""
        # 현재는 단순 구현, 향후 버전 히스토리 기능 추가 가능
        stored_analysis = await self.get_stored_analysis(username, repo_name)
        return [stored_analysis] if stored_analysis else []
    
    async def cleanup_old_analyses(self, days_old: int = 30):
        """오래된 분석 결과 정리"""
        client = self._get_client()
        try:
            collection, hashes_collection = self._get_collections(client)
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # 오래된 분석 결과 삭제
            analysis_result = collection.delete_many({"updated_at": {"$lt": cutoff_date}})
            
            # 오래된 파일 해시 삭제
            hash_result = hashes_collection.delete_many({"updated_at": {"$lt": cutoff_date}})
            
            print(f"정리 완료: 분석 {analysis_result.deleted_count}개, 해시 {hash_result.deleted_count}개 삭제")
            
        finally:
            client.close()


# 전역 서비스 인스턴스
github_storage_service = GitHubStorageService()
