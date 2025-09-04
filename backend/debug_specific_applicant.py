#!/usr/bin/env python3
"""
특정 지원자 디버깅
"""

import asyncio
import os

import motor.motor_asyncio
from bson import ObjectId


async def debug_specific_applicant():
    """특정 지원자 디버깅"""
    print("🔍 === 특정 지원자 디버깅 ===")

    # MongoDB 연결
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db = client.hireme

    # 테스트할 지원자 ID들
    applicant_ids = [
        "68b3ce182f0cf5df5e13004d",  # 박지민
        "68b3ce182f0cf5df5e13004f"   # 김성민
    ]

    for applicant_id in applicant_ids:
        print(f"\n=== 지원자 ID: {applicant_id} ===")

        try:
            # 1. 지원자 정보 조회
            applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
            if applicant:
                print(f"✅ 지원자 찾음: {applicant.get('name', 'Unknown')}")
                print(f"   자소서 ID: {applicant.get('cover_letter_id', 'None')}")

                # 2. 자소서 조회
                cover_letter_id = applicant.get('cover_letter_id')
                if cover_letter_id:
                    cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                    if cover_letter:
                        print(f"✅ 자소서 찾음: {cover_letter.get('filename', 'Unknown')}")
                        print(f"   내용 길이: {len(cover_letter.get('content', ''))}")
                    else:
                        print("❌ 자소서를 찾을 수 없음")
                else:
                    print("❌ 자소서 ID가 없음")
            else:
                print("❌ 지원자를 찾을 수 없음")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")

    client.close()

if __name__ == "__main__":
    asyncio.run(debug_specific_applicant())
