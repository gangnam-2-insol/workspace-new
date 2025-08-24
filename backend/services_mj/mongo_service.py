import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


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

            # MongoDB의 _id를 문자열로 변환 (id 필드 추가)
            for applicant in applicants:
                applicant["id"] = str(applicant["_id"])
                # _id도 문자열로 변환하여 유지
                applicant["_id"] = str(applicant["_id"])

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

    async def get_all_applicants(self, skip: int = 0, limit: int = 50, status: str = None, position: str = None):
        """모든 지원자 목록을 조회합니다 (필터링 포함)"""
        try:
            # 필터 조건 구성
            filter_query = {}
            if status:
                filter_query["status"] = status
            if position:
                filter_query["position"] = position

            total_count = await self.db.applicants.count_documents(filter_query)
            applicants = await self.db.applicants.find(filter_query).skip(skip).limit(limit).to_list(limit)

            # MongoDB의 _id를 문자열로 변환
            for applicant in applicants:
                applicant["id"] = str(applicant["_id"])
                applicant["_id"] = str(applicant["_id"])
                # ObjectId 필드들을 문자열로 변환
                if "resume_id" in applicant and applicant["resume_id"]:
                    applicant["resume_id"] = str(applicant["resume_id"])
                if "cover_letter_id" in applicant and applicant["cover_letter_id"]:
                    applicant["cover_letter_id"] = str(applicant["cover_letter_id"])
                if "portfolio_id" in applicant and applicant["portfolio_id"]:
                    applicant["portfolio_id"] = str(applicant["portfolio_id"])
                if "job_posting_id" in applicant and applicant["job_posting_id"]:
                    applicant["job_posting_id"] = str(applicant["job_posting_id"])
                # datetime 필드들을 ISO 문자열로 변환
                if "created_at" in applicant and applicant["created_at"]:
                    applicant["created_at"] = applicant["created_at"].isoformat()
                if "updated_at" in applicant and applicant["updated_at"]:
                    applicant["updated_at"] = applicant["updated_at"].isoformat()

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

    async def get_applicant_stats(self):
        """지원자 통계를 조회합니다"""
        try:
            total_applicants = await self.db.applicants.count_documents({})

            # 상태별 지원자 수 (샘플 데이터의 실제 상태값 사용 - application_status 필드)
            pending_count = await self.db.applicants.count_documents({"application_status": "보류"})
            approved_count = await self.db.applicants.count_documents({"application_status": {"$in": ["서류합격", "최종합격"]}})
            rejected_count = await self.db.applicants.count_documents({"application_status": {"$in": ["서류불합격", "면접불합격"]}})
            waiting_count = await self.db.applicants.count_documents({"application_status": {"$in": ["지원완료", "서류검토", "면접대기", "면접진행"]}})

            # 최근 30일간 지원자 수
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_applicants = await self.db.applicants.count_documents({"created_at": {"$gte": thirty_days_ago}})

            return {
                "total_applicants": total_applicants,
                "status_breakdown": {
                    "pending": pending_count,
                    "approved": approved_count,
                    "rejected": rejected_count,
                    "waiting": waiting_count
                },
                "recent_applicants_30_days": recent_applicants,
                "success_rate": round((approved_count / total_applicants * 100) if total_applicants > 0 else 0, 2)
            }
        except Exception as e:
            print(f"지원자 통계 조회 오류: {e}")
            return {
                "total_applicants": 0,
                "status_breakdown": {"pending": 0, "approved": 0, "rejected": 0, "waiting": 0},
                "recent_applicants_30_days": 0,
                "success_rate": 0
            }

    async def update_applicant_status(self, applicant_id: str, new_status: str):
        """지원자 상태를 업데이트합니다"""
        try:
            if len(applicant_id) == 24:
                result = await self.db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)},
                    {"$set": {"application_status": new_status, "updated_at": datetime.now()}}
                )
            else:
                result = await self.db.applicants.update_one(
                    {"_id": applicant_id},
                    {"$set": {"application_status": new_status, "updated_at": datetime.now()}}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"지원자 상태 업데이트 오류: {e}")
            return False

    def close(self):
        """MongoDB 연결 종료"""
        if hasattr(self, 'client'):
            self.client.close()
