#!/usr/bin/env python3
"""
직접 MongoDB에서 데이터 가져오기 테스트
"""

import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def test_direct_db():
    print("🔍 직접 MongoDB 연결 테스트")
    print("=" * 60)

    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme

        # 지원자 데이터 직접 조회
        applicants = await db.applicants.find().limit(3).to_list(3)

        print(f"📊 조회된 지원자 수: {len(applicants)}")

        for i, applicant in enumerate(applicants, 1):
            print(f"\n📋 지원자 {i}:")
            print(f"   이름: {applicant.get('name', 'Unknown')}")
            print(f"   이메일: {applicant.get('email', 'None')}")
            print(f"   전화번호: {applicant.get('phone', 'None')}")
            print(f"   직무: {applicant.get('position', 'Unknown')}")
            print(f"   전체 필드: {list(applicant.keys())}")

    except Exception as e:
        print(f"❌ 오류: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_direct_db())
