import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def create_kyungho_cover_letter():
    """이경호 지원자에게 자소서 생성"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 이경호 지원자 찾기
        kyungho = await db.applicants.find_one({"name": "이경호"})

        if not kyungho:
            print("❌ 이경호 지원자를 찾을 수 없습니다")
            return

        print(f"✅ 이경호 지원자 발견: {kyungho['name']}")

        # 새로운 자소서 생성
        cover_letter = {
            "_id": ObjectId(),
            "applicant_id": kyungho["_id"],
            "title": "이경호의 자기소개서",
            "content": """
안녕하세요, 이경호입니다.

UI/UX 디자이너 직무에 지원하게 되어 기쁩니다. 저는 사용자 중심의 디자인을 통해 더 나은 사용자 경험을 제공하고자 합니다.

## 지원 동기
UI/UX 디자이너 직무에 지원하게 된 이유는 사용자들의 니즈를 파악하고 이를 아름다운 인터페이스로 구현하는 것에 대한 열정 때문입니다.

## 경력 및 프로젝트
다양한 웹사이트와 모바일 앱 디자인 프로젝트를 진행했습니다. 사용자 리서치부터 와이어프레임, 프로토타입 제작까지 전체 디자인 프로세스를 경험했습니다.

## 기술 스택
Figma, Adobe XD, Sketch, Photoshop, Illustrator 등 디자인 도구에 능숙하며, HTML/CSS 기초 지식도 보유하고 있습니다.

## 성장 계획
앞으로 더 많은 사용자 리서치와 데이터 분석을 통해 데이터 기반의 디자인을 구현하고, 새로운 디자인 트렌드와 기술을 습득하여 더 나은 사용자 경험을 제공하고 싶습니다.

귀사의 UI/UX 디자이너 직무에서 제 역량을 발휘하여 회사 발전에 기여하고 싶습니다.

감사합니다.
이경호 드림
""",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # 자소서 DB에 삽입
        await db.cover_letters.insert_one(cover_letter)

        # 지원자 정보에 자소서 ID 업데이트
        await db.applicants.update_one(
            {"_id": kyungho["_id"]},
            {"$set": {"cover_letter_id": str(cover_letter["_id"])}}
        )

        print(f"✅ 이경호 자소서 생성 완료 (ID: {cover_letter['_id']})")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(create_kyungho_cover_letter())
