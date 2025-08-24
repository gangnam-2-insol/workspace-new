#!/usr/bin/env python3
"""
MongoService 디버깅 스크립트
"""

import asyncio

from services.mongo_service import MongoService


async def test_mongo_service():
    print("🔍 MongoService 직접 테스트")
    print("=" * 60)

    try:
        # MongoService 인스턴스 생성
        mongo_service = MongoService()

        # get_applicants 메서드 직접 호출
        result = await mongo_service.get_applicants(skip=0, limit=3)

        print(f"📊 결과 키: {list(result.keys())}")
        print(f"📊 지원자 수: {len(result.get('applicants', []))}")

        if result.get('applicants'):
            for i, applicant in enumerate(result['applicants'], 1):
                print(f"\n📋 지원자 {i}:")
                print(f"   이름: {applicant.get('name', 'Unknown')}")
                print(f"   이메일: {applicant.get('email', 'None')}")
                print(f"   전화번호: {applicant.get('phone', 'None')}")
                print(f"   직무: {applicant.get('position', 'Unknown')}")
                print(f"   전체 필드: {list(applicant.keys())}")

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mongo_service())
