#!/usr/bin/env python3
"""
실제 지원자 데이터 확인 스크립트
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def check_applicants():
    """실제 지원자 데이터 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("=== 실제 지원자 데이터 확인 ===")

        # 모든 지원자 확인
        applicants = await db.applicants.find({}).to_list(length=20)
        print(f"총 지원자 수: {len(applicants)}")

        for i, applicant in enumerate(applicants):
            print(f"\n{i+1}. 지원자 정보:")
            print(f"   - ID: {applicant['_id']}")
            print(f"   - 이름: {applicant.get('name', 'N/A')}")
            print(f"   - 이메일: {applicant.get('email', 'N/A')}")
            print(f"   - 자소서 ID: {applicant.get('cover_letter_id', 'None')}")

            # 자소서가 있는 경우 확인
            if applicant.get('cover_letter_id'):
                cover_letter = await db.cover_letters.find_one({"_id": applicant['cover_letter_id']})
                if cover_letter:
                    print(f"   - 자소서 파일명: {cover_letter.get('filename', 'N/A')}")
                    print(f"   - 자소서 내용 길이: {len(cover_letter.get('content', ''))}")
                else:
                    print(f"   - 자소서를 찾을 수 없음 (ID: {applicant['cover_letter_id']})")

        client.close()
        print("\n=== 확인 완료 ===")

    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_applicants())
