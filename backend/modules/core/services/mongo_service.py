import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


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
        """지원자 ID로 지원자 정보 조회"""
        try:
            if len(applicant_id) == 24:
                applicant = await self.db.applicants.find_one({"_id": ObjectId(applicant_id)})
            else:
                applicant = await self.db.applicants.find_one({"_id": applicant_id})

            if applicant:
                # MongoDB의 _id를 문자열로 변환
                applicant["id"] = str(applicant["_id"])
                applicant["_id"] = str(applicant["_id"])

                # 이메일과 전화번호 필드가 없으면 기본값 설정
                if "email" not in applicant:
                    applicant["email"] = "이메일 없음"
                if "phone" not in applicant:
                    applicant["phone"] = "전화번호 없음"

                # 채용공고 정보 가져오기 (job_posting_id가 있는 경우)
                if applicant.get("job_posting_id"):
                    try:
                        job_posting = await self.db.job_postings.find_one({"_id": ObjectId(applicant["job_posting_id"])})
                        if job_posting:
                            applicant["job_posting_info"] = {
                                "id": str(job_posting["_id"]),
                                "title": job_posting.get("title", "제목 없음"),
                                "company": job_posting.get("company", "회사명 없음"),
                                "location": job_posting.get("location", "근무지 없음"),
                                "status": job_posting.get("status", "draft")
                            }
                    except Exception as e:
                        print(f"채용공고 정보 가져오기 실패 (ID: {applicant['job_posting_id']}): {e}")

                # 자소서 내용 가져오기 (cover_letter_id가 있는 경우)
                if applicant.get("cover_letter_id"):
                    try:
                        cover_letter = await self.db.cover_letters.find_one({"_id": ObjectId(applicant["cover_letter_id"])})
                        if cover_letter:
                            applicant["cover_letter_content"] = cover_letter.get("content", cover_letter.get("extracted_text", "자소서 내용을 불러올 수 없습니다."))
                    except Exception as e:
                        print(f"자소서 내용 가져오기 실패 (ID: {applicant['cover_letter_id']}): {e}")

                # 이력서 내용 가져오기 (resume_id가 있는 경우)
                if applicant.get("resume_id"):
                    try:
                        resume = await self.db.resumes.find_one({"_id": ObjectId(applicant["resume_id"])})
                        if resume:
                            applicant["resume_content"] = resume.get("content", resume.get("extracted_text", "이력서 내용을 불러올 수 없습니다."))
                    except Exception as e:
                        print(f"이력서 내용 가져오기 실패 (ID: {applicant['resume_id']}): {e}")

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

    async def get_applicants(self, skip: int = 0, limit: int = 20, status: str = None, position: str = None) -> Dict[str, Any]:
        """지원자 목록 조회 (필터링 포함)"""
        try:
            # 필터 조건 구성
            filter_query = {}
            if status:
                filter_query["status"] = status
            if position:
                filter_query["position"] = position

            total_count = await self.db.applicants.count_documents(filter_query)
            applicants = await self.db.applicants.find(filter_query).skip(skip).limit(limit).to_list(limit)

            # MongoDB의 _id를 문자열로 변환 (id 필드 추가)
            for applicant in applicants:
                applicant["id"] = str(applicant["_id"])
                # _id도 문자열로 변환하여 유지
                applicant["_id"] = str(applicant["_id"])

                # 이메일과 전화번호 필드가 없으면 기본값 설정
                if "email" not in applicant:
                    applicant["email"] = "이메일 없음"
                if "phone" not in applicant:
                    applicant["phone"] = "전화번호 없음"

                # 채용공고 정보 가져오기 (job_posting_id가 있는 경우)
                if applicant.get("job_posting_id"):
                    try:
                        job_posting = await self.db.job_postings.find_one({"_id": ObjectId(applicant["job_posting_id"])})
                        if job_posting:
                            applicant["job_posting_info"] = {
                                "id": str(job_posting["_id"]),
                                "title": job_posting.get("title", "제목 없음"),
                                "company": job_posting.get("company", "회사명 없음"),
                                "location": job_posting.get("location", "근무지 없음"),
                                "status": job_posting.get("status", "draft")
                            }
                    except Exception as e:
                        print(f"채용공고 정보 가져오기 실패 (ID: {applicant['job_posting_id']}): {e}")

                # 자소서 내용 가져오기 (cover_letter_id가 있는 경우)
                if applicant.get("cover_letter_id"):
                    try:
                        cover_letter = await self.db.cover_letters.find_one({"_id": ObjectId(applicant["cover_letter_id"])})
                        if cover_letter:
                            applicant["cover_letter_content"] = cover_letter.get("content", cover_letter.get("extracted_text", "자소서 내용을 불러올 수 없습니다."))
                    except Exception as e:
                        print(f"자소서 내용 가져오기 실패 (ID: {applicant['cover_letter_id']}): {e}")

                # 이력서 내용 가져오기 (resume_id가 있는 경우)
                if applicant.get("resume_id"):
                    try:
                        resume = await self.db.resumes.find_one({"_id": ObjectId(applicant["resume_id"])})
                        if resume:
                            applicant["resume_content"] = resume.get("content", resume.get("extracted_text", "이력서 내용을 불러올 수 없습니다."))
                    except Exception as e:
                        print(f"이력서 내용 가져오기 실패 (ID: {applicant['resume_id']}): {e}")

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

    async def update_applicant_status(self, applicant_id: str, new_status: str) -> bool:
        """지원자 상태 업데이트"""
        try:
            if len(applicant_id) == 24:
                result = await self.db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)},
                    {"$set": {"status": new_status, "updated_at": datetime.now()}}
                )
            else:
                result = await self.db.applicants.update_one(
                    {"_id": applicant_id},
                    {"$set": {"status": new_status, "updated_at": datetime.now()}}
                )
            return result.modified_count > 0
        except Exception as e:
            print(f"지원자 상태 업데이트 오류: {e}")
            return False

    async def get_applicant_stats(self) -> Dict[str, Any]:
        """지원자 통계 조회"""
        try:
            # 전체 지원자 수
            total_count = await self.db.applicants.count_documents({})

            # 상태별 지원자 수
            status_stats = await self.db.applicants.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]).to_list(None)

            # 직무별 지원자 수
            position_stats = await self.db.applicants.aggregate([
                {"$group": {"_id": "$position", "count": {"$sum": 1}}}
            ]).to_list(None)

            # 최근 지원자 수 (7일)
            recent_count = await self.db.applicants.count_documents({
                "created_at": {"$gte": datetime.now() - timedelta(days=7)}
            })

            # 상태 분포를 세분화하여 계산
            status_distribution = {item["_id"]: item["count"] for item in status_stats if item["_id"]}

            # 서류합격과 최종합격을 구분
            document_passed = 0
            final_passed = 0

            # 기존 상태값들을 새로운 분류로 매핑
            if 'passed' in status_distribution:
                document_passed += status_distribution['passed']
            if 'document_passed' in status_distribution:
                document_passed += status_distribution['document_passed']
            if 'approved' in status_distribution:
                final_passed += status_distribution['approved']
            if 'final_passed' in status_distribution:
                final_passed += status_distribution['final_passed']
            if 'interview_scheduled' in status_distribution:
                final_passed += status_distribution['interview_scheduled']

            # 검토중 상태 통합
            pending = (status_distribution.get('pending', 0) +
                      status_distribution.get('reviewing', 0) +
                      status_distribution.get('None', 0))

            # 불합격 상태 통합
            rejected = (status_distribution.get('rejected', 0) +
                       status_distribution.get('failed', 0))

            return {
                "total_applicants": total_count,
                "status_distribution": {
                    **status_distribution,
                    "document_passed": document_passed,
                    "final_passed": final_passed,
                    "pending": pending,
                    "rejected": rejected
                },
                "position_distribution": {item["_id"]: item["count"] for item in position_stats if item["_id"]},
                "recent_applicants": recent_count,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"지원자 통계 조회 오류: {e}")
            return {
                "total_applicants": 0,
                "status_distribution": {
                    "document_passed": 0,
                    "final_passed": 0,
                    "pending": 0,
                    "rejected": 0
                },
                "position_distribution": {},
                "recent_applicants": 0,
                "last_updated": datetime.now().isoformat()
            }

    # Document 관련 메서드들
    def create_resume(self, resume_data) -> Dict[str, Any]:
        """이력서를 생성합니다."""
        try:
            # Pydantic 모델을 dict로 변환
            if hasattr(resume_data, 'dict'):
                resume_dict = resume_data.dict()
            else:
                resume_dict = resume_data

            resume_dict["created_at"] = datetime.now()
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

            cover_letter_dict["created_at"] = datetime.now()
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

            portfolio_dict["created_at"] = datetime.now()
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
