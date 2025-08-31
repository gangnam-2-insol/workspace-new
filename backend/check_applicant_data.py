#!/usr/bin/env python3
"""
이민호 지원자 데이터 확인
"""

import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def check_applicant_data():
    """이민호 지원자 데이터 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("=== 이민호 지원자 데이터 확인 ===")

        # 이민호 지원자 ID
        applicant_id = "68b3ce182f0cf5df5e13004e"

        # 지원자 정보 확인
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            print(f"지원자를 찾을 수 없습니다: {applicant_id}")
            return

        print(f"지원자: {applicant['name']} ({applicant['email']})")
        print(f"모든 필드: {list(applicant.keys())}")

        # 자소서 관련 필드 확인
        cover_letter_fields = [
            'cover_letter_text',
            'cover_letter_extracted_text',
            'cover_letter_summary',
            'cover_letter_analysis',
            'cover_letter_id'
        ]

        for field in cover_letter_fields:
            if field in applicant:
                value = applicant[field]
                if isinstance(value, str):
                    print(f"✅ {field}: {len(value)}자")
                else:
                    print(f"✅ {field}: {type(value)} - {value}")
            else:
                print(f"❌ {field}: 없음")

        client.close()

    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_applicant_data())
