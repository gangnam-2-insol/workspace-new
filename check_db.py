import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def check_applicants():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        # 총 지원자 수 확인
        count = await db.applicants.count_documents({})
        print(f'총 지원자 수: {count}')
        
        if count > 0:
            # 샘플 지원자 확인
            sample = await db.applicants.find_one()
            print(f'샘플 지원자 ID: {sample["_id"]}')
            print(f'샘플 지원자 이름: {sample.get("name", "N/A")}')
            print(f'샘플 지원자 직무: {sample.get("position", "N/A")}')
            
            # 처음 5명의 지원자 ID 출력
            print('\n처음 5명의 지원자 ID:')
            cursor = db.applicants.find().limit(5)
            async for doc in cursor:
                print(f'- {doc["_id"]} ({doc.get("name", "N/A")})')
        else:
            print('데이터베이스에 지원자가 없습니다.')
            
        client.close()
        
    except Exception as e:
        print(f'오류 발생: {e}')

if __name__ == "__main__":
    asyncio.run(check_applicants())
