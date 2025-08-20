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
        
    async def get_applicant_by_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """지원자 ID로 지원자 정보 조회"""
        try:
            if len(applicant_id) == 24:
                applicant = await self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            else:
                applicant = await self.db.applicants.find_one({"_id": applicant_id})
            return applicant
        except Exception as e:
            print(f"지원자 조회 오류: {e}")
            return None
    
    async def save_applicant(self, applicant_data: Dict[str, Any]) -> str:
        """지원자 정보 저장"""
        try:
            applicant_data["created_at"] = datetime.now()
            result = await self.db.applicants.insert_one(applicant_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"지원자 저장 오류: {e}")
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
    
    def close(self):
        """MongoDB 연결 종료"""
        if hasattr(self, 'client'):
            self.client.close()
