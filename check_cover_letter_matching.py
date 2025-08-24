import asyncio
import os

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def check_cover_letter_matching():
    # MongoDB 연결
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.hireme

    print("🔍 자소서-지원자 매칭 상태 및 유사도 기능 연동 확인 중...")

    # 1. 자소서 데이터 확인
    print("\n📄 자소서 데이터 확인:")
    cover_letters_count = await db.cover_letters.count_documents({})
    print(f"총 자소서 수: {cover_letters_count}")

    if cover_letters_count > 0:
        cover_letters = await db.cover_letters.find({}).limit(3).to_list(3)
        for i, cover_letter in enumerate(cover_letters):
            print(f"\n자소서 {i+1}:")
            print(f"  - ID: {cover_letter.get('_id')}")
            print(f"  - applicant_id: {cover_letter.get('applicant_id', '없음')}")
            print(f"  - filename: {cover_letter.get('filename', 'N/A')}")
            print(f"  - content 길이: {len(cover_letter.get('content', ''))}")
            print(f"  - motivation 길이: {len(cover_letter.get('motivation', ''))}")
            print(f"  - status: {cover_letter.get('status', 'N/A')}")

    # 2. 지원자 데이터 확인
    print("\n👥 지원자 데이터 확인:")
    applicants_count = await db.applicants.count_documents({})
    print(f"총 지원자 수: {applicants_count}")

    if applicants_count > 0:
        applicants = await db.applicants.find({}).limit(3).to_list(3)
        for i, applicant in enumerate(applicants):
            print(f"\n지원자 {i+1}:")
            print(f"  - ID: {applicant.get('_id')}")
            print(f"  - 이름: {applicant.get('name', 'N/A')}")
            print(f"  - 직무: {applicant.get('position', 'N/A')}")
            print(f"  - cover_letter_id: {applicant.get('cover_letter_id', '없음')}")

    # 3. 매칭 상태 확인
    print("\n🔗 매칭 상태 확인:")

    # 자소서가 있는 지원자 수
    applicants_with_cover_letter = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})
    print(f"자소서가 매칭된 지원자 수: {applicants_with_cover_letter}")

    # 자소서가 없는 지원자 수
    applicants_without_cover_letter = await db.applicants.count_documents({"cover_letter_id": {"$exists": False}})
    print(f"자소서가 없는 지원자 수: {applicants_without_cover_letter}")

    # 4. 유사도 기능 연동 테스트
    print("\n🔍 유사도 기능 연동 테스트:")

    # 자소서가 있는 지원자 중 하나를 선택해서 유사도 체크 가능한지 확인
    applicant_with_cover_letter = await db.applicants.find_one({"cover_letter_id": {"$exists": True, "$ne": None}})

    if applicant_with_cover_letter:
        applicant_id = str(applicant_with_cover_letter.get('_id'))
        cover_letter_id = applicant_with_cover_letter.get('cover_letter_id')

        print(f"✅ 테스트 지원자: {applicant_with_cover_letter.get('name')} (ID: {applicant_id})")
        print(f"✅ 자소서 ID: {cover_letter_id}")

        # 자소서 내용 확인
        cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
        if cover_letter:
            content_length = len(cover_letter.get('content', ''))
            print(f"✅ 자소서 내용 길이: {content_length} 문자")

            if content_length > 0:
                print("✅ 유사도 기능 연동 가능: 자소서 내용이 존재함")
                print(f"   API 호출 예시: POST /api/coverletter/similarity-check/{applicant_id}")
            else:
                print("❌ 유사도 기능 연동 불가: 자소서 내용이 비어있음")
        else:
            print("❌ 유사도 기능 연동 불가: 자소서를 찾을 수 없음")
    else:
        print("❌ 유사도 기능 연동 불가: 자소서가 매칭된 지원자가 없음")

    # 5. 샘플 데이터 생성 필요성 확인
    print("\n📊 샘플 데이터 생성 필요성:")
    if applicants_with_cover_letter == 0:
        print("❌ 자소서가 매칭된 지원자가 없습니다.")
        print("   → '샘플 데이터 관리' 페이지에서 자소서 데이터를 생성해주세요.")
    elif applicants_with_cover_letter < 10:
        print(f"⚠️ 자소서가 매칭된 지원자가 {applicants_with_cover_letter}명으로 적습니다.")
        print("   → 더 많은 샘플 데이터를 생성하는 것을 권장합니다.")
    else:
        print(f"✅ 자소서가 매칭된 지원자가 {applicants_with_cover_letter}명으로 충분합니다.")

    client.close()
    print("\n✅ 매칭 상태 및 연동 확인 완료")

if __name__ == "__main__":
    asyncio.run(check_cover_letter_matching())
