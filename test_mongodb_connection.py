import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def test_mongodb_connection():
    try:
        # MongoDB 연결
        mongo_uri = "mongodb://localhost:27017/hireme"
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme
        
        print("🔍 MongoDB 연결 테스트 시작...")
        
        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 목록 확인
        db_list = await client.list_database_names()
        print(f"📊 사용 가능한 데이터베이스: {db_list}")
        
        # hireme 데이터베이스의 컬렉션 확인
        collections = await db.list_collection_names()
        print(f"📁 hireme 데이터베이스 컬렉션: {collections}")
        
        # applicants 컬렉션 데이터 확인
        if 'applicants' in collections:
            applicants_count = await db.applicants.count_documents({})
            print(f"👥 applicants 컬렉션 문서 수: {applicants_count}")
            
            if applicants_count > 0:
                # 첫 번째 문서 확인
                first_applicant = await db.applicants.find_one()
                print(f"📄 첫 번째 지원자 문서 키: {list(first_applicant.keys())}")
        
        # job_postings 컬렉션 데이터 확인
        if 'job_postings' in collections:
            job_postings_count = await db.job_postings.count_documents({})
            print(f"💼 job_postings 컬렉션 문서 수: {job_postings_count}")
            
            if job_postings_count > 0:
                # 첫 번째 문서 확인
                first_job = await db.job_postings.find_one()
                print(f"📄 첫 번째 채용공고 문서 키: {list(first_job.keys())}")
        
        client.close()
        print("✅ MongoDB 연결 테스트 완료!")
        
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
