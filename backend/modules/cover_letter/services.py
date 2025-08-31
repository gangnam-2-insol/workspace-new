import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from fastapi import HTTPException
from modules.shared.services import BaseService

from .models import CoverLetter, CoverLetterCreate, CoverLetterStatus, CoverLetterUpdate

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
            from bson import ObjectId
            cover_letter_data = await self.db[self.collection].find_one({"_id": ObjectId(cover_letter_id)})
            if cover_letter_data:
                # ObjectId를 문자열로 변환
                if "_id" in cover_letter_data:
                    cover_letter_data["_id"] = str(cover_letter_data["_id"])
                # applicant_id도 ObjectId인 경우 문자열로 변환
                if "applicant_id" in cover_letter_data and isinstance(cover_letter_data["applicant_id"], ObjectId):
                    cover_letter_data["applicant_id"] = str(cover_letter_data["applicant_id"])
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
                # ObjectId를 문자열로 변환
                if "_id" in cover_letter_data:
                    cover_letter_data["_id"] = str(cover_letter_data["_id"])
                # applicant_id도 ObjectId인 경우 문자열로 변환
                if "applicant_id" in cover_letter_data and isinstance(cover_letter_data["applicant_id"], ObjectId):
                    cover_letter_data["applicant_id"] = str(cover_letter_data["applicant_id"])
                cover_letters.append(CoverLetter(**cover_letter_data))
            return cover_letters
        except Exception as e:
            logger.error(f"자기소개서 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 목록 조회에 실패했습니다.")

    async def update_cover_letter(self, cover_letter_id: str, update_data: CoverLetterUpdate) -> bool:
        """자기소개서 수정"""
        try:
            from bson import ObjectId
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

            result = await self.db[self.collection].update_one(
                {"_id": ObjectId(cover_letter_id)},
                {"$set": update_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"자기소개서 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 수정에 실패했습니다.")

    async def delete_cover_letter(self, cover_letter_id: str) -> bool:
        """자기소개서 삭제"""
        try:
            from bson import ObjectId
            result = await self.db[self.collection].delete_one({"_id": ObjectId(cover_letter_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"자기소개서 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자기소개서 삭제에 실패했습니다.")

    async def get_cover_letter_by_applicant_id(self, applicant_id: str) -> Optional[CoverLetter]:
        """지원자 ID로 자기소개서 조회"""
        try:
            from bson import ObjectId

            # 1. 지원자 정보 조회하여 cover_letter_id 가져오기
            applicant = await self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            if not applicant:
                logger.warning(f"지원자를 찾을 수 없음: {applicant_id}")
                return None

            cover_letter_id = applicant.get("cover_letter_id")
            if not cover_letter_id:
                logger.warning(f"지원자에게 자소서 ID가 없음: {applicant_id}")
                return None

            # 2. cover_letter_id로 자소서 조회
            cover_letter_data = await self.db[self.collection].find_one({"_id": ObjectId(cover_letter_id)})
            if cover_letter_data:
                # ObjectId를 문자열로 변환
                if "_id" in cover_letter_data:
                    cover_letter_data["_id"] = str(cover_letter_data["_id"])
                # applicant_id도 ObjectId인 경우 문자열로 변환
                if "applicant_id" in cover_letter_data and isinstance(cover_letter_data["applicant_id"], ObjectId):
                    cover_letter_data["applicant_id"] = str(cover_letter_data["applicant_id"])

                # 디버깅 로그 추가
                logger.info(f"자소서 데이터 변환 후: {cover_letter_data}")

                try:
                    return CoverLetter(**cover_letter_data)
                except Exception as e:
                    logger.error(f"CoverLetter 모델 생성 실패: {str(e)}")
                    logger.error(f"자소서 데이터: {cover_letter_data}")
                    return None

            logger.warning(f"자소서를 찾을 수 없음: {cover_letter_id}")
            return None
        except Exception as e:
            logger.error(f"지원자 ID로 자기소개서 조회 실패: {str(e)}")
            return None  # HTTPException 대신 None 반환
