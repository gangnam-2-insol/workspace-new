import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId

async def check_db_data():
    """DB 데이터 구조와 내용을 확인합니다."""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        print("🔍 MongoDB 데이터 확인 시작...")
        
        # 1. 지원자 컬렉션 확인
        applicants_count = await db.applicants.count_documents({})
        print(f"📊 총 지원자 수: {applicants_count}")
        
        if applicants_count > 0:
            # 샘플 데이터 확인
            sample_applicant = await db.applicants.find_one()
            print(f"📋 샘플 지원자 필드들: {list(sample_applicant.keys())}")
            
            # 주요 필드 확인
            important_fields = ['email', 'phone', 'name', 'position', 'status', 'resume_id', 'cover_letter_id']
            for field in important_fields:
                exists = field in sample_applicant
                value = sample_applicant.get(field, 'None')
                print(f"  - {field}: {'✅' if exists else '❌'} (값: {value})")
            
            # ObjectId 필드 확인
            if '_id' in sample_applicant:
                print(f"  - _id 타입: {type(sample_applicant['_id'])}")
            
            # 최근 5개 지원자 확인
            print("\n📋 최근 5개 지원자:")
            recent_applicants = await db.applicants.find().limit(5).to_list(5)
            for i, applicant in enumerate(recent_applicants, 1):
                name = applicant.get('name', 'Unknown')
                email = applicant.get('email', 'No email')
                status = applicant.get('status', 'No status')
                print(f"  {i}. {name} - {email} - {status}")
        
        # 2. 자소서 컬렉션 확인
        cover_letters_count = await db.cover_letters.count_documents({})
        print(f"\n📄 총 자소서 수: {cover_letters_count}")
        
        if cover_letters_count > 0:
            sample_cover_letter = await db.cover_letters.find_one()
            print(f"📋 샘플 자소서 필드들: {list(sample_cover_letter.keys())}")
        
        # 3. 이력서 컬렉션 확인
        resumes_count = await db.resumes.count_documents({})
        print(f"\n📝 총 이력서 수: {resumes_count}")
        
        if resumes_count > 0:
            sample_resume = await db.resumes.find_one()
            print(f"📋 샘플 이력서 필드들: {list(sample_resume.keys())}")
        
        client.close()
        print("\n✅ DB 데이터 확인 완료")
        
    except Exception as e:
        print(f"❌ DB 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(check_db_data())
