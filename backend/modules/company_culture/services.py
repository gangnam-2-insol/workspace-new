import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, Depends
from bson import ObjectId

from models.company_culture import (
    CompanyCulture, CompanyCultureCreate, CompanyCultureUpdate,
    CompanyCultureResponse, ApplicantCultureScore, JobPostingCultureRequirement
)

logger = logging.getLogger(__name__)

def get_database():
    """데이터베이스 연결 의존성"""
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    return client.hireme

class CompanyCultureService:
    """회사 인재상 서비스"""

    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = "company_cultures"

    async def create_culture(self, culture_data: CompanyCultureCreate) -> CompanyCultureResponse:
        """인재상 생성"""
        try:
            culture_dict = culture_data.dict()
            culture_dict["created_at"] = datetime.now()
            culture_dict["updated_at"] = datetime.now()

            # 첫 번째 인재상인지 확인
            existing_count = await self.db[self.collection].count_documents({})
            if existing_count == 0:
                culture_dict["is_default"] = True
            else:
                culture_dict["is_default"] = False

            result = await self.db[self.collection].insert_one(culture_dict)

            # 생성된 문서 조회
            created_culture = await self.db[self.collection].find_one({"_id": result.inserted_id})
            return CompanyCultureResponse(
                id=str(created_culture["_id"]),
                name=created_culture["name"],
                description=created_culture["description"],
                is_active=created_culture.get("is_active", True),
                is_default=created_culture.get("is_default", False),
                created_at=created_culture["created_at"],
                updated_at=created_culture["updated_at"]
            )

        except Exception as e:
            logger.error(f"인재상 생성 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 생성에 실패했습니다.")

    async def get_all_cultures(self) -> List[CompanyCultureResponse]:
        """모든 인재상 조회"""
        try:
            cursor = self.db[self.collection].find({}).sort("created_at", -1)
            cultures = await cursor.to_list(None)

            return [
                CompanyCultureResponse(
                    id=str(culture["_id"]),
                    name=culture["name"],
                    description=culture["description"],
                    is_active=True,  # 모든 인재상은 활성 상태
                    is_default=culture.get("is_default", False),
                    created_at=culture["created_at"],
                    updated_at=culture["updated_at"]
                )
                for culture in cultures
            ]
        except Exception as e:
            logger.error(f"인재상 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 조회에 실패했습니다.")

    async def get_culture_by_id(self, culture_id: str) -> CompanyCultureResponse:
        """ID로 인재상 조회"""
        try:
            culture = await self.db[self.collection].find_one({"_id": ObjectId(culture_id)})
            if not culture:
                raise HTTPException(status_code=404, detail="인재상을 찾을 수 없습니다.")

            return CompanyCultureResponse(
                id=str(culture["_id"]),
                name=culture["name"],
                description=culture["description"],
                is_active=culture.get("is_active", True),
                is_default=culture.get("is_default", False),
                created_at=culture["created_at"],
                updated_at=culture["updated_at"]
            )
        except Exception as e:
            logger.error(f"인재상 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 조회에 실패했습니다.")

    async def get_default_culture(self) -> Optional[CompanyCultureResponse]:
        """기본 인재상 조회"""
        try:
            culture = await self.db[self.collection].find_one({
                "is_default": True
            })

            if not culture:
                return None

            return CompanyCultureResponse(
                id=str(culture["_id"]),
                name=culture["name"],
                description=culture["description"],
                is_active=True,  # 모든 인재상은 활성 상태
                is_default=culture.get("is_default", False),
                created_at=culture["created_at"],
                updated_at=culture["updated_at"]
            )
        except Exception as e:
            logger.error(f"기본 인재상 조회 실패: {str(e)}")
            return None

    async def set_default_culture(self, culture_id: str) -> CompanyCultureResponse:
        """기본 인재상 설정"""
        try:
            # 기존 기본 인재상 해제
            await self.db[self.collection].update_many(
                {"is_default": True},
                {"$set": {"is_default": False, "updated_at": datetime.now()}}
            )

            # 새로운 기본 인재상 설정
            result = await self.db[self.collection].update_one(
                {"_id": ObjectId(culture_id)},
                {"$set": {"is_default": True, "updated_at": datetime.now()}}
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="인재상을 찾을 수 없습니다.")

            # 업데이트된 문서 조회
            updated_culture = await self.db[self.collection].find_one({"_id": ObjectId(culture_id)})
            return CompanyCultureResponse(
                id=str(updated_culture["_id"]),
                name=updated_culture["name"],
                description=updated_culture["description"],
                is_active=updated_culture.get("is_active", True),
                is_default=updated_culture.get("is_default", False),
                created_at=updated_culture["created_at"],
                updated_at=updated_culture["updated_at"]
            )

        except Exception as e:
            logger.error(f"기본 인재상 설정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="기본 인재상 설정에 실패했습니다.")

    async def update_culture(self, culture_id: str, update_data: CompanyCultureUpdate) -> CompanyCultureResponse:
        """인재상 수정"""
        try:
            # 기존 인재상 조회
            existing_culture = await self.db[self.collection].find_one({"_id": ObjectId(culture_id)})
            if not existing_culture:
                raise HTTPException(status_code=404, detail="인재상을 찾을 수 없습니다.")

            # 업데이트 데이터 준비
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.now()

            # is_default가 True로 설정되는 경우, 다른 모든 인재상의 is_default를 False로 설정
            if update_dict.get("is_default", False):
                await self.db[self.collection].update_many(
                    {"_id": {"$ne": ObjectId(culture_id)}},
                    {"$set": {"is_default": False, "updated_at": datetime.now()}}
                )

            await self.db[self.collection].update_one(
                {"_id": ObjectId(culture_id)},
                {"$set": update_dict}
            )

            # 업데이트된 문서 조회
            updated_culture = await self.db[self.collection].find_one({"_id": ObjectId(culture_id)})
            return CompanyCultureResponse(
                id=str(updated_culture["_id"]),
                name=updated_culture["name"],
                description=updated_culture["description"],
                is_active=updated_culture.get("is_active", True),
                is_default=updated_culture.get("is_default", False),
                created_at=updated_culture["created_at"],
                updated_at=updated_culture["updated_at"]
            )

        except Exception as e:
            logger.error(f"인재상 수정 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 수정에 실패했습니다.")

    async def delete_culture(self, culture_id: str) -> bool:
        """인재상 삭제 (실제 삭제)"""
        try:
            # 삭제하려는 인재상이 기본 인재상인지 확인
            culture = await self.db[self.collection].find_one({"_id": ObjectId(culture_id)})
            if not culture:
                raise HTTPException(status_code=404, detail="인재상을 찾을 수 없습니다.")

            if culture.get("is_default", False):
                raise HTTPException(status_code=400, detail="기본 인재상은 삭제할 수 없습니다. 다른 인재상을 기본으로 설정한 후 삭제해주세요.")

            result = await self.db[self.collection].delete_one(
                {"_id": ObjectId(culture_id)}
            )

            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="인재상을 찾을 수 없습니다.")

            return True
        except Exception as e:
            logger.error(f"인재상 삭제 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 삭제에 실패했습니다.")

    async def get_cultures_by_category(self, category: str) -> List[CompanyCultureResponse]:
        """카테고리별 인재상 조회 (더 이상 사용되지 않음)"""
        try:
            cursor = self.db[self.collection].find({}).sort("created_at", -1)

            cultures = await cursor.to_list(None)
            return [
                CompanyCultureResponse(
                    id=str(culture["_id"]),
                    name=culture["name"],
                    description=culture["description"],
                    is_active=True,  # 모든 인재상은 활성 상태
                    is_default=culture.get("is_default", False),
                    created_at=culture["created_at"],
                    updated_at=culture["updated_at"]
                )
                for culture in cultures
            ]
        except Exception as e:
            logger.error(f"인재상 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 조회에 실패했습니다.")

    async def evaluate_applicant_culture(self, applicant_id: str, culture_id: str,
                                       resume_text: str, cover_letter_text: str = "") -> ApplicantCultureScore:
        """지원자 인재상 평가"""
        try:
            # 인재상 정보 조회
            culture = await self.get_culture_by_id(culture_id)

            # 간단한 키워드 기반 평가 (실제로는 AI 분석 필요)
            score = await self._calculate_culture_score(
                culture, resume_text, cover_letter_text
            )

            return ApplicantCultureScore(
                culture_id=culture_id,
                culture_name=culture.name,
                score=score["total_score"],
                criteria_scores=score["criteria_scores"],
                feedback=score["feedback"]
            )

        except Exception as e:
            logger.error(f"지원자 인재상 평가 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="인재상 평가에 실패했습니다.")

    async def _calculate_culture_score(self, culture: CompanyCultureResponse,
                                     resume_text: str, cover_letter_text: str) -> Dict[str, Any]:
        """인재상 점수 계산 (키워드 기반)"""
        # 실제 구현에서는 AI 분석을 사용해야 함
        import random

        # 간단한 랜덤 점수 생성 (실제로는 더 정교한 분석 필요)
        score = random.randint(60, 95)

        feedback = f"{culture.name}에 대한 평가가 완료되었습니다. 점수: {score}점"

        return {
            "total_score": score,
            "criteria_scores": {"overall": score},
            "feedback": feedback
        }
