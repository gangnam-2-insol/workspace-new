#!/usr/bin/env python3
"""
CoverLetterService 디버깅
"""

import asyncio
import os

import motor.motor_asyncio
from bson import ObjectId


async def debug_cover_letter_service():
    """CoverLetterService 디버깅"""
    print("🔍 === CoverLetterService 디버깅 ===")

    # MongoDB 연결
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db = client.hireme

    # 테스트할 지원자 ID
    applicant_id = "68b3ce182f0cf5df5e13004d"  # 박지민
    print(f"지원자 ID: {applicant_id}")

    try:
        # 1. 지원자 정보 조회
        print("\n1. 지원자 정보 조회")
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if applicant:
            print(f"✅ 지원자 찾음: {applicant.get('name', 'Unknown')}")
            print(f"   자소서 ID: {applicant.get('cover_letter_id', 'None')}")
        else:
            print("❌ 지원자를 찾을 수 없음")
            return

        # 2. 자소서 컬렉션에서 지원자 ID로 검색
        print("\n2. 자소서 컬렉션에서 지원자 ID로 검색")
        cover_letter = await db.cover_letters.find_one({"applicant_id": applicant_id})
        if cover_letter:
            print(f"✅ 자소서 찾음: {cover_letter.get('filename', 'Unknown')}")
            print(f"   자소서 ID: {cover_letter['_id']}")
        else:
            print("❌ 자소서를 찾을 수 없음")

            # 3. 자소서 컬렉션의 모든 문서 확인
            print("\n3. 자소서 컬렉션의 모든 문서 확인")
            async for doc in db.cover_letters.find({}):
                print(f"   - ID: {doc['_id']}, 지원자ID: {doc.get('applicant_id', 'None')}, 파일명: {doc.get('filename', 'Unknown')}")

        # 4. cover_letter_id로 자소서 검색
        print("\n4. cover_letter_id로 자소서 검색")
        cover_letter_id = applicant.get('cover_letter_id')
        if cover_letter_id:
            cover_letter_by_id = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
            if cover_letter_by_id:
                print(f"✅ cover_letter_id로 자소서 찾음: {cover_letter_by_id.get('filename', 'Unknown')}")
                print(f"   지원자 ID: {cover_letter_by_id.get('applicant_id', 'None')}")
            else:
                print("❌ cover_letter_id로 자소서를 찾을 수 없음")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_cover_letter_service())
