"""
채용공고 할당 관련 유틸리티 함수들
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random


async def get_active_job_postings(db: AsyncIOMotorClient) -> List[Dict[str, Any]]:
    """활성 채용공고 목록 조회"""
    try:
        job_postings = await db.job_postings.find({
            "status": {"$in": ["published", "active"]}
        }).to_list(length=None)

        # ObjectId를 문자열로 변환
        for job in job_postings:
            job["_id"] = str(job["_id"])

        return job_postings
    except Exception as e:
        print(f"❌ 활성 채용공고 조회 실패: {e}")
        return []


async def get_default_job_posting_id(db: AsyncIOMotorClient) -> Optional[str]:
    """기본 채용공고 ID 반환 (활성 채용공고 중 랜덤 선택)"""
    try:
        active_jobs = await get_active_job_postings(db)

        if not active_jobs:
            print("⚠️ 활성 채용공고가 없습니다.")
            return None

        # 랜덤하게 하나 선택
        selected_job = random.choice(active_jobs)
        job_id = selected_job["_id"]

        print(f"🎯 기본 채용공고 선택: {selected_job.get('title', 'Unknown')} (ID: {job_id})")
        return job_id

    except Exception as e:
        print(f"❌ 기본 채용공고 선택 실패: {e}")
        return None


async def assign_job_posting_to_applicant(
    db: AsyncIOMotorClient,
    applicant_id: str,
    job_posting_id: Optional[str] = None
) -> bool:
    """지원자에게 채용공고 할당"""
    try:
        # job_posting_id가 없으면 기본 채용공고 선택
        if not job_posting_id:
            job_posting_id = await get_default_job_posting_id(db)

        if not job_posting_id:
            print(f"❌ 지원자 {applicant_id}에게 할당할 채용공고가 없습니다.")
            return False

        # 지원자 정보 업데이트
        result = await db.applicants.update_one(
            {"_id": applicant_id},
            {
                "$set": {
                    "job_posting_id": job_posting_id,
                    "updated_at": datetime.now()
                }
            }
        )

        if result.modified_count > 0:
            print(f"✅ 지원자 {applicant_id} → 채용공고 {job_posting_id} 할당 완료")
            return True
        else:
            print(f"⚠️ 지원자 {applicant_id} 업데이트 실패 (이미 할당되었거나 존재하지 않음)")
            return False

    except Exception as e:
        print(f"❌ 지원자 채용공고 할당 실패: {e}")
        return False


async def create_default_job_posting_if_needed(db: AsyncIOMotorClient) -> Optional[str]:
    """활성 채용공고가 없으면 기본 채용공고 생성"""
    try:
        active_jobs = await get_active_job_postings(db)

        if active_jobs:
            return active_jobs[0]["_id"]  # 첫 번째 활성 채용공고 반환

        print("📝 활성 채용공고가 없어 기본 채용공고를 생성합니다...")

        # 기본 채용공고 데이터
        default_job_data = {
            "title": "기본 채용공고",
            "company": "기본 회사",
            "location": "서울",
            "type": "full-time",
            "position": "개발자",
            "department": "개발팀",
            "description": "기본 채용공고입니다. 지원자들이 자동으로 이 공고에 할당됩니다.",
            "requirements": "기본 요구사항",
            "benefits": "기본 혜택",
            "salary": "협의",
            "status": "published",
            "applicants": 0,
            "views": 0,
            "bookmarks": 0,
            "shares": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # DB에 삽입
        result = await db.job_postings.insert_one(default_job_data)
        job_id = str(result.inserted_id)

        print(f"✅ 기본 채용공고 생성 완료 (ID: {job_id})")
        return job_id

    except Exception as e:
        print(f"❌ 기본 채용공고 생성 실패: {e}")
        return None


async def ensure_applicant_has_job_posting(
    db: AsyncIOMotorClient,
    applicant_data: Dict[str, Any]
) -> Dict[str, Any]:
    """지원자 데이터에 채용공고 ID가 없으면 자동 할당"""
    try:
        # 이미 job_posting_id가 있으면 그대로 반환
        if applicant_data.get("job_posting_id"):
            return applicant_data

        # 기본 채용공고 ID 가져오기 (없으면 생성)
        job_posting_id = await get_default_job_posting_id(db)
        if not job_posting_id:
            job_posting_id = await create_default_job_posting_if_needed(db)

        if job_posting_id:
            applicant_data["job_posting_id"] = job_posting_id
            print(f"🎯 지원자에게 채용공고 자동 할당: {job_posting_id}")
        else:
            print("⚠️ 채용공고 할당 실패 - job_posting_id가 None으로 유지됩니다.")

        return applicant_data

    except Exception as e:
        print(f"❌ 지원자 채용공고 할당 확인 실패: {e}")
        return applicant_data


async def reassign_orphaned_applicants(db: AsyncIOMotorClient) -> int:
    """job_posting_id가 없는 지원자들을 활성 채용공고에 재할당"""
    try:
        print("🔄 고아 지원자 재할당 작업 시작...")

        # job_posting_id가 없는 지원자들 조회
        orphaned_applicants = await db.applicants.find({
            "$or": [
                {"job_posting_id": {"$exists": False}},
                {"job_posting_id": None},
                {"job_posting_id": ""},
                {"job_posting_id": "default_job_posting"}
            ]
        }).to_list(length=None)

        if not orphaned_applicants:
            print("ℹ️ 재할당할 고아 지원자가 없습니다.")
            return 0

        print(f"📋 재할당 대상: {len(orphaned_applicants)}명")

        # 활성 채용공고 목록
        active_jobs = await get_active_job_postings(db)
        if not active_jobs:
            print("❌ 활성 채용공고가 없습니다.")
            return 0

        job_posting_ids = [job["_id"] for job in active_jobs]

        # 라운드 로빈 방식으로 재할당
        reassigned_count = 0
        for i, applicant in enumerate(orphaned_applicants):
            target_job_posting_id = job_posting_ids[i % len(job_posting_ids)]

            success = await assign_job_posting_to_applicant(
                db,
                applicant["_id"],
                target_job_posting_id
            )

            if success:
                reassigned_count += 1

        print(f"✅ 고아 지원자 재할당 완료: {reassigned_count}/{len(orphaned_applicants)}명")
        return reassigned_count

    except Exception as e:
        print(f"❌ 고아 지원자 재할당 실패: {e}")
        return 0
