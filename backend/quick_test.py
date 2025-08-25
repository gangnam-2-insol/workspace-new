import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def quick_test():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        count = await db.applicants.count_documents({})
        print(f"지원자 수: {count}")

        if count > 0:
            first = await db.applicants.find_one({})
            print(f"첫 번째 지원자: {first.get('personal_info', {}).get('name', 'N/A')}")

        client.close()
        print("✅ MongoDB 연결 성공")
        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(quick_test())
