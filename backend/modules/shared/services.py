from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class BaseService:
    """공통 서비스 기본 클래스"""
    
    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        self.db = db
    
    def _get_object_id(self, id_str: str):
        """문자열 ID를 ObjectId로 변환"""
        try:
            return ObjectId(id_str)
        except Exception:
            return id_str
    
    async def get_by_id(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """ID로 문서 조회"""
        try:
            document = await self.db[collection].find_one({"_id": document_id})
            return document
        except Exception as e:
            logger.error(f"문서 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 조회 중 오류가 발생했습니다")
    
    async def get_list(self, collection: str, filters: Optional[Dict[str, Any]] = None, 
                      skip: int = 0, limit: int = 10, sort_by: str = "created_at", 
                      sort_order: int = -1) -> List[Dict[str, Any]]:
        """문서 목록 조회"""
        try:
            query = filters or {}
            cursor = self.db[collection].find(query)
            cursor = cursor.sort(sort_by, sort_order).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"문서 목록 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 목록 조회 중 오류가 발생했습니다")
    
    async def create(self, collection: str, data: Dict[str, Any]) -> str:
        """문서 생성"""
        try:
            data["created_at"] = datetime.utcnow()
            result = await self.db[collection].insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"문서 생성 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 생성 중 오류가 발생했습니다")
    
    async def update(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """문서 업데이트"""
        try:
            data["updated_at"] = datetime.utcnow()
            result = await self.db[collection].update_one(
                {"_id": document_id}, {"$set": data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"문서 업데이트 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 업데이트 중 오류가 발생했습니다")
    
    async def delete(self, collection: str, document_id: str) -> bool:
        """문서 삭제"""
        try:
            result = await self.db[collection].delete_one({"_id": document_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"문서 삭제 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 삭제 중 오류가 발생했습니다")
    
    async def count(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """문서 개수 조회"""
        try:
            query = filters or {}
            count = await self.db[collection].count_documents(query)
            return count
        except Exception as e:
            logger.error(f"문서 개수 조회 실패: {e}")
            raise HTTPException(status_code=500, detail="문서 개수 조회 중 오류가 발생했습니다")

class FileService(BaseService):
    """파일 관련 공통 서비스"""
    
    async def save_file_metadata(self, filename: str, file_size: int, 
                                file_type: str, metadata: Dict[str, Any]) -> str:
        """파일 메타데이터 저장"""
        file_data = {
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type,
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        return await self.create("files", file_data)
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 메타데이터 조회"""
        return await self.get_by_id("files", file_id)

class AnalysisService(BaseService):
    """분석 관련 공통 서비스"""
    
    async def save_analysis_result(self, document_id: str, analysis_result: Dict[str, Any], 
                                 document_type: str) -> str:
        """분석 결과 저장"""
        analysis_data = {
            "document_id": document_id,
            "document_type": document_type,
            "analysis_result": analysis_result,
            "created_at": datetime.utcnow()
        }
        return await self.create("analysis_results", analysis_data)
    
    async def get_analysis_result(self, document_id: str) -> Optional[Dict[str, Any]]:
        """분석 결과 조회"""
        return await self.get_by_id("analysis_results", document_id)
    
    async def get_analysis_history(self, document_id: str) -> List[Dict[str, Any]]:
        """분석 히스토리 조회"""
        return await self.get_list("analysis_results", {"document_id": document_id})
