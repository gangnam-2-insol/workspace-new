import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def create_kyungho_portfolio():
    """이경호 지원자의 포트폴리오 생성"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 이경호 지원자 찾기
        kyungho = await db.applicants.find_one({"name": "이경호"})

        if not kyungho:
            print("❌ 이경호 지원자를 찾을 수 없습니다")
            return

        print(f"✅ 이경호 지원자 발견: {kyungho['name']}")
        print(f"📁 포트폴리오 ID: {kyungho.get('portfolio_id', 'N/A')}")

        # 포트폴리오가 이미 존재하는지 확인
        if kyungho.get('portfolio_id'):
            existing_portfolio = await db.portfolios.find_one({"_id": ObjectId(kyungho['portfolio_id'])})
            if existing_portfolio:
                print("✅ 포트폴리오가 이미 존재합니다")
                return

        # 새로운 포트폴리오 생성
        portfolio = {
            "_id": ObjectId(kyungho['portfolio_id']) if kyungho.get('portfolio_id') else ObjectId(),
            "applicant_id": kyungho["_id"],
            "title": "이경호의 UI/UX 디자인 포트폴리오",
            "description": "UI/UX 디자이너로서의 역량을 보여주는 포트폴리오입니다. 사용자 중심의 디자인을 통해 더 나은 사용자 경험을 제공하고자 합니다.",
            "projects": [
                {
                    "name": "이경호의 웹사이트 리디자인",
                    "description": "기존 웹사이트의 사용자 경험을 개선하는 리디자인 프로젝트",
                    "technologies": ["Figma", "Adobe XD", "Photoshop", "Illustrator"],
                    "duration": "3개월",
                    "url": "https://behance.net/kyungho/web-redesign"
                },
                {
                    "name": "이경호의 모바일 앱 디자인",
                    "description": "사용자 중심의 모바일 앱 UI/UX 디자인 프로젝트",
                    "technologies": ["Figma", "Sketch", "Principle", "InVision"],
                    "duration": "4개월",
                    "url": "https://dribbble.com/kyungho/mobile-app"
                },
                {
                    "name": "이경호의 대시보드 디자인",
                    "description": "데이터 시각화를 위한 관리자 대시보드 UI/UX 디자인",
                    "technologies": ["Figma", "Adobe XD", "Chart.js", "Material Design"],
                    "duration": "2개월",
                    "url": "https://figma.com/kyungho/dashboard"
                }
            ],
            "skills": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "Principle", "InVision", "HTML", "CSS"],
            "github_url": "https://github.com/kyungho222",
            "linkedin_url": "https://linkedin.com/in/이경호",
            "portfolio_url": "https://portfolio.example.com/이경호",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # 포트폴리오 DB에 삽입
        await db.portfolios.insert_one(portfolio)

        # 지원자 정보에 포트폴리오 ID 업데이트 (필요한 경우)
        if not kyungho.get('portfolio_id'):
            await db.applicants.update_one(
                {"_id": kyungho["_id"]},
                {"$set": {"portfolio_id": str(portfolio["_id"])}}
            )

        print(f"✅ 이경호 포트폴리오 생성 완료 (ID: {portfolio['_id']})")
        print(f"📁 프로젝트 수: {len(portfolio['projects'])}개")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(create_kyungho_portfolio())
