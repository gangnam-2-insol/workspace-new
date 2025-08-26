import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def check_mongo_data():
    """MongoDB 데이터 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme

        print("=== MongoDB 데이터 확인 ===")

        # 지원자 데이터 확인
        applicants_count = await db.applicants.count_documents({})
        print(f"지원자 수: {applicants_count}")

        if applicants_count > 0:
            # 첫 번째 지원자 정보 확인
            first_applicant = await db.applicants.find_one({})
            print(f"첫 번째 지원자 ID: {first_applicant['_id']}")
            print(f"이름: {first_applicant.get('name', 'N/A')}")
            print(f"직무: {first_applicant.get('position', 'N/A')}")
            print(f"성장배경 길이: {len(first_applicant.get('growthBackground', ''))}")
            print(f"지원동기 길이: {len(first_applicant.get('motivation', ''))}")
            print(f"경력사항 길이: {len(first_applicant.get('careerHistory', ''))}")

            # 유사도 체크용 지원자 ID
            test_applicant_id = str(first_applicant['_id'])
            print(f"\n테스트용 지원자 ID: {test_applicant_id}")

            return test_applicant_id

        # 이력서 데이터 확인
        resumes_count = await db.resumes.count_documents({})
        print(f"이력서 수: {resumes_count}")

        # 커버레터 데이터 확인
        cover_letters_count = await db.cover_letters.count_documents({})
        print(f"커버레터 수: {cover_letters_count}")

        # 청크 데이터 확인
        chunks_count = await db.resume_chunks.count_documents({})
        print(f"청크 수: {chunks_count}")

        client.close()

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(check_mongo_data())
