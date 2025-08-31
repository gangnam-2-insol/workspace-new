#!/usr/bin/env python3
"""
데이터베이스 연결 및 자소서 데이터 확인 스크립트
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def check_database():
    """데이터베이스 상태 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("=== 데이터베이스 연결 확인 ===")

        # 지원자 컬렉션 확인
        print("\n=== 지원자 컬렉션 ===")
        applicants_count = await db.applicants.count_documents({})
        print(f"총 지원자 수: {applicants_count}")

        # 이민호 지원자 정보 확인
        applicant = await db.applicants.find_one({"_id": "68b3ce182f0cf5df5e13004e"})
        if applicant:
            print(f"이민호 지원자 정보:")
            print(f"  - ID: {applicant['_id']}")
            print(f"  - 이름: {applicant['name']}")
            print(f"  - 자소서 ID: {applicant.get('cover_letter_id', 'None')}")
            print(f"  - 이메일: {applicant.get('email', 'N/A')}")
        else:
            print("이민호 지원자를 찾을 수 없습니다.")

        # 자소서 컬렉션 확인
        print("\n=== 자소서 컬렉션 ===")
        cover_letters_count = await db.cover_letters.count_documents({})
        print(f"총 자소서 수: {cover_letters_count}")

        # 모든 자소서 확인
        cover_letters = await db.cover_letters.find({}).to_list(length=10)
        for i, cl in enumerate(cover_letters):
            print(f"  {i+1}. ID: {cl['_id']}, 파일명: {cl.get('filename', 'N/A')}, 내용 길이: {len(cl.get('content', ''))}")

        # 이민호의 자소서 찾기
        if applicant and applicant.get('cover_letter_id'):
            cover_letter = await db.cover_letters.find_one({"_id": applicant['cover_letter_id']})
            if cover_letter:
                print(f"\n=== 이민호의 자소서 ===")
                print(f"  - ID: {cover_letter['_id']}")
                print(f"  - 파일명: {cover_letter.get('filename', 'N/A')}")
                print(f"  - 내용 길이: {len(cover_letter.get('content', ''))}")
                print(f"  - 내용 미리보기: {cover_letter.get('content', '')[:100]}...")
            else:
                print(f"\n이민호의 자소서를 찾을 수 없습니다. (ID: {applicant['cover_letter_id']})")

        client.close()
        print("\n=== 데이터베이스 연결 종료 ===")

    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_database())
