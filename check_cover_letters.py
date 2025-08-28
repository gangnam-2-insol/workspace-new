import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_cover_letters():
    """자소서가 있는 지원자 수 확인"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 전체 지원자 수
        total_applicants = await db.applicants.count_documents({})

        # 자소서가 있는 지원자 수
        applicants_with_cover = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})

        # 자소서 컬렉션의 총 문서 수
        total_cover_letters = await db.cover_letters.count_documents({})

        print(f"📊 자소서 현황:")
        print(f"   전체 지원자 수: {total_applicants}명")
        print(f"   자소서가 있는 지원자 수: {applicants_with_cover}명")
        print(f"   자소서 컬렉션 문서 수: {total_cover_letters}개")
        print(f"   자소서 보유율: {applicants_with_cover/total_applicants*100:.1f}%")

        # 자소서가 있는 지원자들의 이름과 직무 출력
        if applicants_with_cover > 0:
            print(f"\n📄 자소서가 있는 지원자들:")
            applicants = await db.applicants.find({"cover_letter_id": {"$exists": True, "$ne": None}}).limit(10).to_list(length=10)
            for i, applicant in enumerate(applicants):
                print(f"   {i+1}. {applicant['name']} - {applicant.get('position', 'N/A')}")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(check_cover_letters())
