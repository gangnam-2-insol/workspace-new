from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os


class MongoService:
    """MongoDB 서비스 클래스"""
    
    def __init__(self, mongo_uri: str = None):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client.hireme
        
        # 동기 MongoDB 클라이언트도 초기화
        try:
            import pymongo
            self.sync_client = pymongo.MongoClient(self.mongo_uri)
            self.sync_db = self.sync_client.hireme
        except ImportError:
            print("pymongo가 설치되지 않았습니다. 동기 작업이 제한될 수 있습니다.")
            self.sync_client = None
            self.sync_db = None
        
    async def get_applicant_by_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 지원자 정보 조회 (비동기)"""
        try:
            if len(applicant_id) == 24:
                applicant = await self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            else:
                applicant = await self.db.applicants.find_one({"_id": applicant_id})
            return applicant
        except Exception as e:
            print(f"지원자 조회 오류: {e}")
            return None
    
    def get_applicant_by_id_sync(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 지원자 정보 조회 (동기)"""
        try:
            import asyncio
            # 이미 실행 중인 이벤트 루프가 있는지 확인
            try:
                loop = asyncio.get_running_loop()
                # 이미 실행 중인 루프가 있으면 동기적으로 처리
                return self._get_applicant_by_id_sync_impl(applicant_id)
            except RuntimeError:
                # 실행 중인 루프가 없으면 새 루프 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if len(applicant_id) == 24:
                        applicant = loop.run_until_complete(self.db.applicants.find_one({"_id": ObjectId(applicant_id)}))
                    else:
                        applicant = loop.run_until_complete(self.db.applicants.find_one({"_id": applicant_id}))
                    
                    # ObjectId를 문자열로 변환
                    if applicant and "_id" in applicant:
                        applicant["id"] = str(applicant["_id"])
                        del applicant["_id"]
                    
                    return applicant
                finally:
                    loop.close()
        except Exception as e:
            print(f"지원자 조회 오류: {e}")
            return None
    
    def _get_applicant_by_id_sync_impl(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """동기적으로 지원자 ID로 조회 (이미 실행 중인 루프가 있을 때)"""
        try:
            from bson import ObjectId
            
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            if len(applicant_id) == 24:
                applicant = self.sync_db.applicants.find_one({"_id": ObjectId(applicant_id)})
            else:
                applicant = self.sync_db.applicants.find_one({"_id": applicant_id})
            
            # ObjectId를 문자열로 변환
            if applicant and "_id" in applicant:
                applicant["id"] = str(applicant["_id"])
                del applicant["_id"]
            
            return applicant
        except Exception as e:
            print(f"동기 지원자 조회 오류: {e}")
            return None
    
    async def save_applicant(self, applicant_data: Dict[str, Any]) -> str:
        """지원자 정보 저장"""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(applicant_data, 'dict'):
                applicant_dict = applicant_data.dict()
            else:
                applicant_dict = applicant_data
            
            applicant_dict["created_at"] = datetime.now()
            result = await self.db.applicants.insert_one(applicant_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"지원자 저장 오류: {e}")
            raise
    
    async def create_or_get_applicant(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """지원자 생성 또는 기존 지원자 조회 (비동기)"""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(applicant_data, 'dict'):
                applicant_dict = applicant_data.dict()
            else:
                applicant_dict = applicant_data
            
            # 이메일로 기존 지원자 확인
            email = applicant_dict.get("email")
            if email:
                existing_applicant = await self.db.applicants.find_one({"email": email})
                if existing_applicant:
                    # 기존 지원자 반환
                    existing_applicant["id"] = str(existing_applicant["_id"])
                    del existing_applicant["_id"]
                    return {
                        "id": existing_applicant["id"],
                        "is_new": False,
                        "applicant": existing_applicant
                    }
            
            # 새 지원자 생성
            applicant_dict["created_at"] = datetime.now()
            result = await self.db.applicants.insert_one(applicant_dict)
            new_applicant_id = str(result.inserted_id)
            
            # 생성된 지원자 정보 조회
            new_applicant = await self.db.applicants.find_one({"_id": result.inserted_id})
            new_applicant["id"] = str(new_applicant["_id"])
            del new_applicant["_id"]
            
            return {
                "id": new_applicant_id,
                "is_new": True,
                "applicant": new_applicant
            }
        except Exception as e:
            print(f"지원자 생성/조회 오류: {e}")
            raise
    
    def create_or_get_applicant_sync(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """지원자 생성 또는 기존 지원자 조회 (동기)"""
        try:
            import asyncio
            # 이미 실행 중인 이벤트 루프가 있는지 확인
            try:
                loop = asyncio.get_running_loop()
                # 이미 실행 중인 루프가 있으면 동기적으로 처리
                return self._create_or_get_applicant_sync_impl(applicant_data)
            except RuntimeError:
                # 실행 중인 루프가 없으면 새 루프 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.create_or_get_applicant(applicant_data))
                finally:
                    loop.close()
        except Exception as e:
            print(f"지원자 생성/조회 오류: {e}")
            raise
    
    def _create_or_get_applicant_sync_impl(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """동기적으로 지원자 생성 또는 조회 (이미 실행 중인 루프가 있을 때)"""
        try:
            from bson import ObjectId
            
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            # Pydantic 모델을 dict로 변환
            if hasattr(applicant_data, 'dict'):
                applicant_dict = applicant_data.dict()
            else:
                applicant_dict = applicant_data
            
            # 이메일로 기존 지원자 확인
            email = applicant_dict.get("email")
            if email:
                existing_applicant = self.sync_db.applicants.find_one({"email": email})
                if existing_applicant:
                    # 기존 지원자 반환
                    existing_applicant["id"] = str(existing_applicant["_id"])
                    del existing_applicant["_id"]
                    return {
                        "id": existing_applicant["id"],
                        "is_new": False,
                        "applicant": existing_applicant
                    }
            
            # 새 지원자 생성
            applicant_dict["created_at"] = datetime.now()
            applicant_dict["updated_at"] = datetime.now()
            result = self.sync_db.applicants.insert_one(applicant_dict)
            new_applicant_id = str(result.inserted_id)
            
            # 생성된 지원자 정보 조회
            new_applicant = self.sync_db.applicants.find_one({"_id": result.inserted_id})
            new_applicant["id"] = str(new_applicant["_id"])
            del new_applicant["_id"]
            
            return {
                "id": new_applicant_id,
                "is_new": True,
                "applicant": new_applicant
            }
        except Exception as e:
            print(f"동기 지원자 생성/조회 오류: {e}")
            raise
    
    async def update_applicant(self, applicant_id: str, update_data: Dict[str, Any]) -> bool:
        """지원자 정보 업데이트"""
        try:
            if len(applicant_id) == 24:
                result = await self.db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)}, 
                    {"$set": update_data}
                )
            else:
                result = await self.db.applicants.update_one(
                    {"_id": applicant_id}, 
                    {"$set": update_data}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"지원자 업데이트 오류: {e}")
            return False
    
    async def get_applicants(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """지원자 목록 조회"""
        try:
            total_count = await self.db.applicants.count_documents({})
            applicants = await self.db.applicants.find().skip(skip).limit(limit).to_list(limit)
            
            # MongoDB의 _id를 id로 변환
            for applicant in applicants:
                applicant["id"] = str(applicant["_id"])
                del applicant["_id"]
            
            return {
                "applicants": applicants,
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count
            }
        except Exception as e:
            print(f"지원자 목록 조회 오류: {e}")
            return {
                "applicants": [],
                "total_count": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }
    
    async def delete_applicant(self, applicant_id: str) -> bool:
        """지원자 삭제"""
        try:
            if len(applicant_id) == 24:
                result = await self.db.applicants.delete_one({"_id": ObjectId(applicant_id)})
            else:
                result = await self.db.applicants.delete_one({"_id": applicant_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"지원자 삭제 오류: {e}")
            return False
    
    def update_applicant_sync(self, applicant_id: str, update_data: Dict[str, Any]) -> bool:
        """지원자 정보 업데이트 (동기)"""
        try:
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            if len(applicant_id) == 24:
                result = self.sync_db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)}, 
                    {"$set": update_data}
                )
            else:
                result = self.sync_db.applicants.update_one(
                    {"_id": applicant_id}, 
                    {"$set": update_data}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"지원자 업데이트 오류: {e}")
            return False
    
    # Document 관련 메서드들
    def create_resume(self, resume_data) -> Dict[str, Any]:
        """이력서를 생성합니다."""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(resume_data, 'dict'):
                resume_dict = resume_data.dict()
            else:
                resume_dict = resume_data
            
            # 새로운 스키마에 맞게 필드 설정
            resume_dict["created_at"] = datetime.now()
            resume_dict["document_type"] = "resume"
            
            result = self.sync_db.resumes.insert_one(resume_dict)
            resume_dict["id"] = str(result.inserted_id)
            return resume_dict
        except Exception as e:
            print(f"이력서 생성 오류: {e}")
            raise
    
    def create_cover_letter(self, cover_letter_data) -> Dict[str, Any]:
        """자기소개서를 생성합니다."""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(cover_letter_data, 'dict'):
                cover_letter_dict = cover_letter_data.dict()
            else:
                cover_letter_dict = cover_letter_data
            
            # 새로운 스키마에 맞게 필드 설정
            cover_letter_dict["created_at"] = datetime.now()
            cover_letter_dict["document_type"] = "cover_letter"
            
            result = self.sync_db.cover_letters.insert_one(cover_letter_dict)
            cover_letter_dict["id"] = str(result.inserted_id)
            return cover_letter_dict
        except Exception as e:
            print(f"자기소개서 생성 오류: {e}")
            raise
    
    def create_portfolio(self, portfolio_data) -> Dict[str, Any]:
        """포트폴리오를 생성합니다."""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(portfolio_data, 'dict'):
                portfolio_dict = portfolio_data.dict()
            else:
                portfolio_dict = portfolio_data
            
            # 새로운 스키마에 맞게 필드 설정
            portfolio_dict["created_at"] = datetime.now()
            portfolio_dict["updated_at"] = datetime.now()
            portfolio_dict["document_type"] = "portfolio"
            
            result = self.sync_db.portfolios.insert_one(portfolio_dict)
            portfolio_dict["id"] = str(result.inserted_id)
            return portfolio_dict
        except Exception as e:
            print(f"포트폴리오 생성 오류: {e}")
            raise

    def update_resume_chunks(self, resume_id: str, chunks: list) -> bool:
        """이력서에 청킹 결과를 업데이트합니다."""
        try:
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            if len(resume_id) == 24:
                result = self.sync_db.resumes.update_one(
                    {"_id": ObjectId(resume_id)}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            else:
                result = self.sync_db.resumes.update_one(
                    {"_id": resume_id}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"이력서 청킹 업데이트 오류: {e}")
            return False

    def update_cover_letter_chunks(self, cover_letter_id: str, chunks: list) -> bool:
        """자기소개서에 청킹 결과를 업데이트합니다."""
        try:
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            if len(cover_letter_id) == 24:
                result = self.sync_db.cover_letters.update_one(
                    {"_id": ObjectId(cover_letter_id)}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            else:
                result = self.sync_db.cover_letters.update_one(
                    {"_id": cover_letter_id}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"자기소개서 청킹 업데이트 오류: {e}")
            return False

    def update_portfolio_chunks(self, portfolio_id: str, chunks: list) -> bool:
        """포트폴리오에 청킹 결과를 업데이트합니다."""
        try:
            if self.sync_db is None:
                raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
            
            if len(portfolio_id) == 24:
                result = self.sync_db.portfolios.update_one(
                    {"_id": ObjectId(portfolio_id)}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            else:
                result = self.sync_db.portfolios.update_one(
                    {"_id": portfolio_id}, 
                    {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"포트폴리오 청킹 업데이트 오류: {e}")
            return False
    
    def close(self):
        """MongoDB 연결 종료"""
        if hasattr(self, 'client'):
            self.client.close()
        if hasattr(self, 'sync_client') and self.sync_client is not None:
            self.sync_client.close()
