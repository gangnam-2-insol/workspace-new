import asyncio
import motor.motor_asyncio
from datetime import datetime

async def debug_applicants():
    """MongoDB의 applicants 컬렉션 데이터를 디버깅하는 함수"""
    try:
        # MongoDB 연결
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
        db = client.Hireme
        
        print("🔗 MongoDB 연결 확인 중...")
        
        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공!")
        
        # 데이터베이스 목록 확인
        databases = await client.list_database_names()
        print(f"📁 사용 가능한 데이터베이스: {databases}")
        
        # Hireme 데이터베이스의 컬렉션 목록 확인
        collections = await db.list_collection_names()
        print(f"📁 Hireme 데이터베이스의 컬렉션: {collections}")
        
        # applicants 컬렉션 확인
        applicants_count = await db.applicants.count_documents({})
        print(f"📊 applicants 컬렉션 문서 수: {applicants_count}")
        
        if applicants_count > 0:
            # 샘플 데이터 조회
            sample_applicant = await db.applicants.find_one()
            print(f"\n📄 샘플 지원자 데이터:")
            for key, value in sample_applicant.items():
                print(f"   {key}: {value}")
        else:
            print("⚠️  applicants 컬렉션에 데이터가 없습니다.")
            
            # 다른 컬렉션들 확인
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"   - {collection_name}: {count}개 문서")
                
                if count > 0:
                    sample_doc = await db[collection_name].find_one()
                    print(f"     샘플 필드: {list(sample_doc.keys())}")
                    
                    # applicants와 관련된 컬렉션인지 확인
                    if 'applicant' in str(sample_doc).lower() or 'name' in str(sample_doc).lower():
                        print(f"     ⚠️  이 컬렉션이 지원자 데이터일 수 있습니다!")
        
        client.close()
        print("\n🎉 MongoDB 데이터 확인 완료!")
        
    except Exception as e:
        print(f"❌ MongoDB 데이터 확인 실패: {e}")

if __name__ == "__main__":
    asyncio.run(debug_applicants())
