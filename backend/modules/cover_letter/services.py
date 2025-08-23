from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import motor.motor_asyncio
from datetime import datetime
import logging

from ..shared.services import BaseService
from .models import (
    CoverLetter, CoverLetterCreate, CoverLetterUpdate, CoverLetterStatus
)

logger = logging.getLogger(__name__)

class CoverLetterService(BaseService):
    """자기소개서 서비스"""

    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = "cover_letters"

    async def create_cover_letter(self, cover_letter_data: CoverLetterCreate) -> str:
        """자기소개서 생성"""
        try:
            cover_letter = CoverLetter(**cover_letter_data.dict())
            result = await self.db[self.collection].insert_one(cover_letter.dict(by_alias=True))
            cover_letter_id = str(result.inserted_id)
            logger.info(f"자기소개서 생성 완료: {cover_letter_id}")
            return cover_letter_id
        except Exception as e:
            logger.error(f"자기소개서 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 생성에 실패했습니다.")

    async def get_cover_letter(self, cover_letter_id: str) -> Optional[CoverLetter]:
        """자기소개서 조회"""
        try:
            cover_letter_data = await self.db[self.collection].find_one({"_id": self._get_object_id(cover_letter_id)})
            if cover_letter_data:
                return CoverLetter(**cover_letter_data)
            return None
        except Exception as e:
            logger.error(f"자기소개서 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 조회에 실패했습니다.")

    async def get_cover_letters(self, skip: int = 0, limit: int = 10, 
                               status: Optional[CoverLetterStatus] = None,
                               applicant_id: Optional[str] = None) -> List[CoverLetter]:
        """자기소개서 목록 조회"""
        try:
            filter_query = {}
            if status:
                filter_query["status"] = status
            if applicant_id:
                filter_query["applicant_id"] = applicant_id

            cursor = self.db[self.collection].find(filter_query).skip(skip).limit(limit)
            cover_letters = []
            async for cover_letter_data in cursor:
                cover_letters.append(CoverLetter(**cover_letter_data))
            return cover_letters
        except Exception as e:
            logger.error(f"자기소개서 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 목록 조회에 실패했습니다.")

    async def update_cover_letter(self, cover_letter_id: str, update_data: CoverLetterUpdate) -> bool:
        """자기소개서 수정"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            result = await self.db[self.collection].update_one(
                {"_id": self._get_object_id(cover_letter_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"자기소개서 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 수정에 실패했습니다.")

    async def delete_cover_letter(self, cover_letter_id: str) -> bool:
        """자기소개서 삭제"""
        try:
            result = await self.db[self.collection].delete_one({"_id": self._get_object_id(cover_letter_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"자기소개서 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 삭제에 실패했습니다.")
