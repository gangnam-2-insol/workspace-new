import asyncio
import motor.motor_asyncio

async def test_mongodb():
    try:
        print("🔗 MongoDB 연결 테스트 시작...")
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
        
        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 목록 확인
        databases = await client.list_database_names()
        print(f"📁 사용 가능한 데이터베이스: {databases}")
        
        # Hireme 데이터베이스 확인
        if 'Hireme' in databases:
            db = client.Hireme
            collections = await db.list_collection_names()
            print(f"📁 Hireme 데이터베이스의 컬렉션: {collections}")
            
            # applicants 컬렉션 확인
            if 'applicants' in collections:
                count = await db.applicants.count_documents({})
                print(f"📊 applicants 컬렉션 문서 수: {count}")
                
                if count > 0:
                    sample = await db.applicants.find_one()
                    print(f"📄 샘플 데이터: {sample}")
            else:
                print("⚠️ applicants 컬렉션이 없습니다.")
        else:
            print("⚠️ Hireme 데이터베이스가 없습니다.")
            
        client.close()
        print("🎉 MongoDB 테스트 완료!")
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongodb())
