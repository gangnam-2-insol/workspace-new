import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_portfolio():
    """포트폴리오 ID 디버깅"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 이경호 지원자 찾기
        kyungho = await db.applicants.find_one({"name": "이경호"})

        if not kyungho:
            print("❌ 이경호 지원자를 찾을 수 없습니다")
            return

        print(f"✅ 이경호 지원자 발견: {kyungho['name']}")
        print(f"📁 포트폴리오 ID (문자열): {kyungho.get('portfolio_id', 'N/A')}")
        print(f"📁 포트폴리오 ID 타입: {type(kyungho.get('portfolio_id'))}")

        if kyungho.get('portfolio_id'):
            try:
                # ObjectId로 변환 시도
                portfolio_object_id = ObjectId(kyungho['portfolio_id'])
                print(f"📁 변환된 ObjectId: {portfolio_object_id}")

                # 포트폴리오 검색
                portfolio = await db.portfolios.find_one({"_id": portfolio_object_id})
                if portfolio:
                    print("✅ 포트폴리오 발견!")
                    print(f"   제목: {portfolio.get('title', 'N/A')}")
                    print(f"   프로젝트 수: {len(portfolio.get('projects', []))}")
                else:
                    print("❌ 포트폴리오를 찾을 수 없습니다")

                    # 포트폴리오 컬렉션의 모든 문서 확인
                    all_portfolios = await db.portfolios.find({}).to_list(length=5)
                    print(f"📁 포트폴리오 컬렉션의 처음 5개 문서:")
                    for i, p in enumerate(all_portfolios):
                        print(f"   {i+1}. ID: {p['_id']}, 제목: {p.get('title', 'N/A')}")

            except Exception as e:
                print(f"❌ ObjectId 변환 실패: {e}")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(debug_portfolio())
