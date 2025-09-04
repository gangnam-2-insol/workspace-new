#!/usr/bin/env python3
"""
현재 지원자들에게 자소서 연결하는 스크립트
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def fix_current_applicants():
    """현재 지원자들에게 자소서 연결"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("🔧 === 현재 지원자들에게 자소서 연결 ===")

        # 1. 현재 지원자들 조회
        applicants = await db.applicants.find({}).to_list(length=10)
        print(f"총 지원자 수: {len(applicants)}")

        # 2. 사용 가능한 자소서들 조회
        cover_letters = await db.cover_letters.find({}).to_list(length=10)
        print(f"총 자소서 수: {len(cover_letters)}")

        # 3. 지원자들에게 자소서 연결
        for i, applicant in enumerate(applicants):
            if i < len(cover_letters):
                # 자소서 ID를 지원자에게 연결
                cover_letter_id = cover_letters[i]['_id']
                applicant_id = applicant['_id']

                # 지원자 업데이트
                await db.applicants.update_one(
                    {"_id": applicant_id},
                    {"$set": {"cover_letter_id": cover_letter_id}}
                )

                # 자소서에도 지원자 ID 연결
                await db.cover_letters.update_one(
                    {"_id": cover_letter_id},
                    {"$set": {"applicant_id": applicant_id}}
                )

                print(f"✅ {applicant['name']} ({applicant_id}) ← {cover_letters[i]['filename']} ({cover_letter_id})")
            else:
                print(f"⚠️  {applicant['name']} - 연결할 자소서 없음")

        # 4. 연결 결과 확인
        print("\n🔍 === 연결 결과 확인 ===")
        updated_applicants = await db.applicants.find({}).to_list(length=10)
        for app in updated_applicants:
            print(f"  - {app['name']}: 자소서ID = {app.get('cover_letter_id', 'None')}")

        client.close()
        print("✅ 자소서 연결 완료")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(fix_current_applicants())
