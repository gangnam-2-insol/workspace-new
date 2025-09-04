#!/usr/bin/env python3
"""
이민호 지원자 자소서 데이터 수정
"""

import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def fix_cover_letter_data():
    """이민호 지원자 자소서 데이터 수정"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("=== 이민호 지원자 자소서 데이터 수정 ===")

        # 이민호 지원자 ID
        applicant_id = "68b3ce182f0cf5df5e13004e"

        # 지원자 정보 확인
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            print(f"지원자를 찾을 수 없습니다: {applicant_id}")
            return

        print(f"지원자: {applicant['name']} ({applicant['email']})")
        print(f"자소서 ID: {applicant.get('cover_letter_id')}")

        # 자소서 정보 확인
        if applicant.get('cover_letter_id'):
            cover_letter = await db.cover_letters.find_one({"_id": applicant['cover_letter_id']})
            if cover_letter:
                print(f"자소서 파일명: {cover_letter.get('filename')}")
                print(f"자소서 내용 길이: {len(cover_letter.get('content', ''))}")

                # 자소서 텍스트를 지원자 데이터에 추가
                cover_letter_text = cover_letter.get('content', '')
                if cover_letter_text:
                    await db.applicants.update_one(
                        {"_id": ObjectId(applicant_id)},
                        {"$set": {
                            "cover_letter_text": cover_letter_text,
                            "cover_letter_extracted_text": cover_letter_text
                        }}
                    )
                    print("✅ 자소서 텍스트를 지원자 데이터에 추가했습니다.")
                else:
                    print("❌ 자소서 내용이 비어있습니다.")
            else:
                print("❌ 자소서를 찾을 수 없습니다.")
        else:
            print("❌ 자소서 ID가 없습니다.")

        client.close()

    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_cover_letter_data())
