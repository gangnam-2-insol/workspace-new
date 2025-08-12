import asyncio
import motor.motor_asyncio
from datetime import datetime

async def check_resumes_collection():
    """MongoDB의 resumes 컬렉션 데이터를 확인하는 함수"""
    try:
        # MongoDB 연결
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
        db = client.Hireme
        
        print("🔗 MongoDB 연결 확인 중...")
        
        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # resumes 컬렉션 확인
        resumes_count = await db.resumes.count_documents({})
        print(f"📊 resumes 컬렉션 문서 수: {resumes_count}")
        
        if resumes_count > 0:
            # 모든 이력서 데이터 조회
            resumes = await db.resumes.find().to_list(length=10)
            print(f"\n📄 이력서 데이터:")
            
            for i, resume in enumerate(resumes, 1):
                print(f"\n--- 이력서 {i} ---")
                for key, value in resume.items():
                    if key == '_id':
                        print(f"   {key}: {str(value)[:20]}...")
                    elif isinstance(value, str) and len(value) > 100:
                        print(f"   {key}: {value[:100]}...")
                    else:
                        print(f"   {key}: {value}")
        else:
            print("⚠️  resumes 컬렉션에 데이터가 없습니다.")
            
            # 다른 컬렉션들 확인
            collections = await db.list_collection_names()
            print(f"\n📁 사용 가능한 컬렉션: {collections}")
            
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"   - {collection_name}: {count}개 문서")
                
                if count > 0:
                    sample_doc = await db[collection_name].find_one()
                    print(f"     샘플 필드: {list(sample_doc.keys())}")
        
        client.close()
        print("\n🎉 MongoDB 데이터 확인 완료!")
        
    except Exception as e:
        print(f"❌ MongoDB 데이터 확인 실패: {e}")

if __name__ == "__main__":
    asyncio.run(check_resumes_collection())
