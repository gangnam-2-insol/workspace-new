import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def check_portfolio():
    """포트폴리오 데이터 현황 확인"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 전체 지원자 수
        total_applicants = await db.applicants.count_documents({})

        # 포트폴리오가 있는 지원자 수
        applicants_with_portfolio = await db.applicants.count_documents({"portfolio_id": {"$exists": True, "$ne": None}})

        # 포트폴리오 컬렉션의 총 문서 수
        total_portfolios = await db.portfolios.count_documents({})

        print(f"📁 포트폴리오 현황:")
        print(f"   전체 지원자 수: {total_applicants}명")
        print(f"   포트폴리오가 있는 지원자 수: {applicants_with_portfolio}명")
        print(f"   포트폴리오 컬렉션 문서 수: {total_portfolios}개")
        print(f"   포트폴리오 보유율: {applicants_with_portfolio/total_applicants*100:.1f}%")

        # 포트폴리오가 있는 지원자들의 이름과 직무 출력
        if applicants_with_portfolio > 0:
            print(f"\n📁 포트폴리오가 있는 지원자들:")
            applicants = await db.applicants.find({"portfolio_id": {"$exists": True, "$ne": None}}).limit(10).to_list(length=10)
            for i, applicant in enumerate(applicants):
                print(f"   {i+1}. {applicant['name']} - {applicant.get('position', 'N/A')} (ID: {applicant.get('portfolio_id', 'N/A')})")

        # 이경호 지원자 특별 확인
        kyungho = await db.applicants.find_one({"name": "이경호"})
        if kyungho:
            print(f"\n🔍 이경호 지원자 포트폴리오 정보:")
            print(f"   포트폴리오 ID: {kyungho.get('portfolio_id', 'N/A')}")
            if kyungho.get('portfolio_id'):
                try:
                    portfolio = await db.portfolios.find_one({"_id": ObjectId(kyungho['portfolio_id'])})
                    if portfolio:
                        print(f"   ✅ 포트폴리오 존재")
                        print(f"   📁 제목: {portfolio.get('title', 'N/A')}")
                        print(f"   📁 프로젝트 수: {len(portfolio.get('projects', []))}")
                    else:
                        print(f"   ❌ 포트폴리오 ID는 있지만 실제 포트폴리오가 없음")
                except Exception as e:
                    print(f"   ❌ 포트폴리오 검색 오류: {e}")
            else:
                print(f"   ❌ 포트폴리오 ID가 없음")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(check_portfolio())
