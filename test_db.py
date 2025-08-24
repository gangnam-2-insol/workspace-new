import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient


async def test_db():
    try:
        # MongoDB 연결
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        print("🔍 데이터베이스 연결 테스트...")

        # 컬렉션별 문서 수 확인
        applicants_count = await db.applicants.count_documents({})
        cover_letters_count = await db.cover_letters.count_documents({})
        resumes_count = await db.resumes.count_documents({})
        job_postings_count = await db.job_postings.count_documents({})

        print(f"📊 지원자 수: {applicants_count}")
        print(f"📄 자소서 수: {cover_letters_count}")
        print(f"📋 이력서 수: {resumes_count}")
        print(f"💼 채용공고 수: {job_postings_count}")

        # 지원자 데이터 샘플 확인
        if applicants_count > 0:
            applicant = await db.applicants.find_one({})
            print(f"\n📝 첫 번째 지원자:")
            print(f"  - 이름: {applicant.get('name', 'N/A')}")
            print(f"  - 이메일: {applicant.get('email', 'N/A')}")
            print(f"  - cover_letter_id: {applicant.get('cover_letter_id', '없음')}")
            print(f"  - resume_id: {applicant.get('resume_id', '없음')}")
            print(f"  - job_posting_id: {applicant.get('job_posting_id', '없음')}")

        client.close()
        print("\n✅ 테스트 완료")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())

