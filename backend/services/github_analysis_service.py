import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from bson import ObjectId
from pymongo import MongoClient
from models.github_analysis import GithubAnalysis, GithubAnalysisCreate

class GithubAnalysisService:
    def __init__(self, db_client: MongoClient):
        self.db = db_client
        self.collection = self.db.github_analyses
        
    def _generate_content_hash(self, analysis_data: Dict[str, Any]) -> str:
        """분석 데이터의 해시를 생성하여 변경 감지에 사용"""
        # 중요한 필드들만 선택하여 해시 생성
        key_fields = {
            'summary': analysis_data.get('summary', ''),
            'languages': analysis_data.get('languages', {}),
            'topics': analysis_data.get('topics', []),
            'total_repos': analysis_data.get('total_repos', 0),
            'total_stars': analysis_data.get('total_stars', 0),
            'total_forks': analysis_data.get('total_forks', 0),
            'main_languages': analysis_data.get('main_languages', [])
        }
        
        # 정렬된 JSON 문자열로 변환하여 일관된 해시 생성
        sorted_json = json.dumps(key_fields, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(sorted_json.encode('utf-8')).hexdigest()
    
    def _parse_github_url(self, url: str) -> Tuple[str, Optional[str]]:
        """GitHub URL을 파싱하여 사용자명과 레포지토리명 추출"""
        if not url.startswith('https://github.com/'):
            return url, None
            
        try:
            parts = url.split('github.com/')[1].split('/')
            username = parts[0]
            repo_name = parts[1] if len(parts) > 1 else None
            return username, repo_name
        except:
            return url, None
    
    def get_cached_analysis(self, applicant_id: str, github_url: str) -> Optional[GithubAnalysis]:
        """캐시된 분석 결과 조회"""
        try:
            # 지원자 ID와 GitHub URL로 기존 분석 결과 조회
            cached = self.collection.find_one({
                'applicant_id': applicant_id,
                'github_url': github_url
            })
            
            if cached:
                # ObjectId를 문자열로 변환
                if '_id' in cached and isinstance(cached['_id'], ObjectId):
                    cached['_id'] = str(cached['_id'])
                return GithubAnalysis(**cached)
            return None
        except Exception as e:
            print(f"캐시 조회 오류: {e}")
            return None
    
    def save_analysis(self, applicant_id: str, github_url: str, analysis_data: Dict[str, Any]) -> GithubAnalysis:
        """분석 결과를 저장하거나 업데이트"""
        try:
            username, repo_name = self._parse_github_url(github_url)
            analysis_type = 'repository' if repo_name else 'user'
            content_hash = self._generate_content_hash(analysis_data)
            
            # 기존 분석 결과 확인
            existing = self.collection.find_one({
                'applicant_id': applicant_id,
                'github_url': github_url
            })
            
            analysis_doc = {
                'applicant_id': applicant_id,
                'github_url': github_url,
                'analysis_type': analysis_type,
                'username': username,
                'repo_name': repo_name,
                'analysis_data': analysis_data,
                'content_hash': content_hash,
                'last_analyzed': datetime.utcnow(),
                'cache_version': '1.0',
                'total_repos': analysis_data.get('total_repos'),
                'total_stars': analysis_data.get('total_stars'),
                'total_forks': analysis_data.get('total_forks'),
                'main_languages': analysis_data.get('main_languages'),
                'updated_at': datetime.utcnow()
            }
            
            if existing:
                # 기존 문서 업데이트
                analysis_doc['created_at'] = existing.get('created_at', datetime.utcnow())
                self.collection.update_one(
                    {'_id': existing['_id']},
                    {'$set': analysis_doc}
                )
                analysis_doc['_id'] = existing['_id']
            else:
                # 새 문서 생성
                analysis_doc['created_at'] = datetime.utcnow()
                result = self.collection.insert_one(analysis_doc)
                analysis_doc['_id'] = result.inserted_id
            
            # ObjectId를 문자열로 변환
            if '_id' in analysis_doc and isinstance(analysis_doc['_id'], ObjectId):
                analysis_doc['_id'] = str(analysis_doc['_id'])
            
            return GithubAnalysis(**analysis_doc)
            
        except Exception as e:
            print(f"분석 결과 저장 오류: {e}")
            raise
    
    def check_content_changes(self, applicant_id: str, github_url: str, current_analysis: Dict[str, Any]) -> Tuple[bool, Optional[GithubAnalysis], List[str]]:
        """콘텐츠 변경 여부 확인 - 더 정교한 변경 감지"""
        try:
            cached_analysis = self.get_cached_analysis(applicant_id, github_url)
            if not cached_analysis:
                return False, None
            
            # 주요 변경 지표들 확인
            changes_detected = []
            
            # 1. 총 레포지토리 수 변경
            current_repos = current_analysis.get('total_repos', 0)
            cached_repos = cached_analysis.total_repos or 0
            if abs(current_repos - cached_repos) > 0:
                changes_detected.append(f"레포지토리 수: {cached_repos} → {current_repos}")
            
            # 2. 총 스타 수 변경 (10% 이상)
            current_stars = current_analysis.get('total_stars', 0)
            cached_stars = cached_analysis.total_stars or 0
            if cached_stars > 0 and abs(current_stars - cached_stars) / cached_stars > 0.1:
                changes_detected.append(f"스타 수: {cached_stars} → {current_stars}")
            
            # 3. 총 포크 수 변경 (10% 이상)
            current_forks = current_analysis.get('total_forks', 0)
            cached_forks = cached_analysis.total_forks or 0
            if cached_forks > 0 and abs(current_forks - cached_forks) / cached_forks > 0.1:
                changes_detected.append(f"포크 수: {cached_forks} → {current_forks}")
            
            # 4. 주요 언어 변경
            current_languages = set(current_analysis.get('main_languages', []))
            cached_languages = set(cached_analysis.main_languages or [])
            if current_languages != cached_languages:
                changes_detected.append(f"주요 언어 변경: {cached_languages} → {current_languages}")
            
            # 5. 언어 통계 변경 (20% 이상)
            current_lang_stats = current_analysis.get('language_stats', {})
            cached_lang_stats = cached_analysis.analysis_data.get('language_stats', {})
            if current_lang_stats and cached_lang_stats:
                for lang in set(current_lang_stats.keys()) | set(cached_lang_stats.keys()):
                    current_val = current_lang_stats.get(lang, 0)
                    cached_val = cached_lang_stats.get(lang, 0)
                    if cached_val > 0 and abs(current_val - cached_val) / cached_val > 0.2:
                        changes_detected.append(f"{lang} 사용량 변경: {cached_val} → {current_val}")
                        break
            
            # 6. 해시 기반 변경 감지 (백업)
            current_hash = self._generate_content_hash(current_analysis)
            cached_hash = cached_analysis.content_hash
            if current_hash != cached_hash and not changes_detected:
                changes_detected.append("콘텐츠 해시 변경")
            
            has_changes = len(changes_detected) > 0
            
            if has_changes:
                print(f"변경 감지: {', '.join(changes_detected)}")
            
            return has_changes, cached_analysis, changes_detected
            
        except Exception as e:
            print(f"콘텐츠 변경 확인 오류: {e}")
            return False, None, []
    
    def delete_analysis(self, applicant_id: str, github_url: str) -> bool:
        """분석 결과 삭제"""
        try:
            result = self.collection.delete_one({
                'applicant_id': applicant_id,
                'github_url': github_url
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"분석 결과 삭제 오류: {e}")
            return False
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[GithubAnalysis]:
        """ID로 분석 결과 조회"""
        try:
            analysis = self.collection.find_one({'_id': ObjectId(analysis_id)})
            if analysis:
                return GithubAnalysis(**analysis)
            return None
        except Exception as e:
            print(f"분석 결과 조회 오류: {e}")
            return None
