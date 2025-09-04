import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def check_applicant(applicant_id):
    """특정 지원자 정보 확인"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 지원자 조회
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})

        if applicant:
            print(f"✅ 지원자 발견: {applicant['name']}")
            print(f"📧 이메일: {applicant.get('email', 'N/A')}")
            print(f"📱 전화번호: {applicant.get('phone', 'N/A')}")
            print(f"💼 직무: {applicant.get('position', 'N/A')}")
            print(f"📄 자소서 ID: {applicant.get('cover_letter_id', 'N/A')}")
            print(f"📋 이력서 ID: {applicant.get('resume_id', 'N/A')}")
            print(f"📁 포트폴리오 ID: {applicant.get('portfolio_id', 'N/A')}")
            print(f"🔗 GitHub URL: {applicant.get('github_url', 'N/A')}")
            print(f"🔗 LinkedIn URL: {applicant.get('linkedin_url', 'N/A')}")
            print(f"🔗 포트폴리오 URL: {applicant.get('portfolio_url', 'N/A')}")

            # 자소서가 있는지 확인
            if applicant.get('cover_letter_id'):
                cover_letter = await db.cover_letters.find_one({"_id": ObjectId(applicant['cover_letter_id'])})
                if cover_letter:
                    print(f"✅ 자소서 존재: {cover_letter.get('title', 'N/A')}")
                    print(f"📝 자소서 내용 길이: {len(cover_letter.get('content', ''))}자")
                else:
                    print("❌ 자소서 ID는 있지만 실제 자소서가 없음")
            else:
                print("❌ 자소서 ID가 없음")

        else:
            print(f"❌ 지원자를 찾을 수 없음: {applicant_id}")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    # 테스트할 지원자 ID
    test_id = "68ad792307c4e1b8ba8e962f"
    asyncio.run(check_applicant(test_id))
