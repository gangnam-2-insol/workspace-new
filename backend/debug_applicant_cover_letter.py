#!/usr/bin/env python3
"""
특정 지원자의 자소서 정보 디버그 스크립트
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_applicant_cover_letter(applicant_id: str):
    """특정 지원자의 자소서 정보 디버그"""
    try:
        # MongoDB 연결
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        print(f"🔍 지원자 자소서 디버그 시작...")
        print(f"지원자 ID: {applicant_id}")
        print(f"연결 URI: {mongo_uri}")

        # 1. 지원자 정보 조회
        print("\n📋 지원자 정보:")
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if applicant:
            print("✅ 지원자 발견")
            print(f"  - 이름: {applicant.get('name', 'N/A')}")
            print(f"  - 이메일: {applicant.get('email', 'N/A')}")
            print(f"  - 직무: {applicant.get('position', 'N/A')}")
            print(f"  - 상태: {applicant.get('status', 'N/A')}")
            print(f"  - cover_letter_id: {applicant.get('cover_letter_id', 'N/A')}")

            # cover_letter_id가 있는지 확인
            cover_letter_id = applicant.get('cover_letter_id')
            if cover_letter_id:
                print(f"  - cover_letter_id 타입: {type(cover_letter_id)}")
                print(f"  - cover_letter_id 값: {cover_letter_id}")

                # 2. 자소서 정보 조회
                print("\n📋 자소서 정보:")
                try:
                    cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                    if cover_letter:
                        print("✅ 자소서 발견")
                        print(f"  - 자소서 ID: {str(cover_letter['_id'])}")
                        print(f"  - 지원자 ID: {cover_letter.get('applicant_id', 'N/A')}")
                        print(f"  - 내용 길이: {len(cover_letter.get('content', ''))} 문자")
                        print(f"  - 추출 텍스트 길이: {len(cover_letter.get('extracted_text', ''))} 문자")
                        print(f"  - 상태: {cover_letter.get('status', 'N/A')}")
                        print(f"  - 생성일: {cover_letter.get('created_at', 'N/A')}")
                    else:
                        print("❌ 자소서를 찾을 수 없음")
                        print(f"  - 검색한 ID: {cover_letter_id}")

                        # 전체 자소서 목록 확인
                        all_cover_letters = await db.cover_letters.find({}).to_list(10)
                        print(f"  - 전체 자소서 수: {len(all_cover_letters)}")
                        if all_cover_letters:
                            print("  - 최근 자소서들:")
                            for i, cl in enumerate(all_cover_letters[:3]):
                                print(f"    {i+1}. ID: {str(cl['_id'])}, applicant_id: {cl.get('applicant_id', 'N/A')}")

                except Exception as e:
                    print(f"❌ 자소서 조회 오류: {e}")
            else:
                print("❌ cover_letter_id가 없음")

                # 해당 지원자와 연결된 자소서가 있는지 확인
                print("\n🔍 해당 지원자와 연결된 자소서 검색:")
                cover_letters = await db.cover_letters.find({"applicant_id": applicant_id}).to_list(10)
                if cover_letters:
                    print(f"✅ {len(cover_letters)}개의 자소서 발견")
                    for i, cl in enumerate(cover_letters):
                        print(f"  {i+1}. ID: {str(cl['_id'])}, 상태: {cl.get('status', 'N/A')}")
                else:
                    print("❌ 연결된 자소서 없음")
        else:
            print("❌ 지원자를 찾을 수 없음")

        # 3. 전체 통계
        print("\n📊 전체 통계:")
        total_applicants = await db.applicants.count_documents({})
        total_cover_letters = await db.cover_letters.count_documents({})
        applicants_with_cover_letters = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})

        print(f"  - 전체 지원자: {total_applicants}명")
        print(f"  - 전체 자소서: {total_cover_letters}개")
        print(f"  - 자소서가 있는 지원자: {applicants_with_cover_letters}명")

        client.close()
        print("\n✅ 디버그 완료!")

    except Exception as e:
        print(f"❌ 디버그 실패: {e}")

if __name__ == "__main__":
    # 로그에서 보인 지원자 ID 사용
    applicant_id = "68ad2c2e5efcd127f4d1a1e2"
    asyncio.run(debug_applicant_cover_letter(applicant_id))
