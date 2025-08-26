import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_database_structure():
    """데이터베이스 구조 확인"""
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.hireme
    
    try:
        print("🔍 데이터베이스 구조 확인 중...")
        
        # 지원자 컬렉션 확인 (최신 데이터)
        sample_applicant = await db.applicants.find_one(sort=[("created_at", -1)])
        if sample_applicant:
            print("\n📋 APPLICANTS 컬렉션 필드 (최신 데이터):")
            for field in sorted(sample_applicant.keys()):
                field_type = type(sample_applicant[field]).__name__
                field_value = sample_applicant[field]
                if field in ['github_url', 'linkedin_url', 'portfolio_url']:
                    print(f"  - {field}: {field_type} = {field_value}")
                else:
                    print(f"  - {field}: {field_type}")
            
            # GitHub 관련 필드 확인
            github_fields = [field for field in sample_applicant.keys() if 'github' in field.lower()]
            if github_fields:
                print(f"\n✅ GitHub 관련 필드 발견: {github_fields}")
                for field in github_fields:
                    print(f"  - {field}: {sample_applicant[field]}")
            else:
                print("\n❌ GitHub 관련 필드 없음")
        else:
            print("❌ 지원자 데이터가 없습니다.")
        
        # 채용공고 컬렉션 확인
        sample_job = await db.job_postings.find_one()
        if sample_job:
            print("\n📋 JOB_POSTINGS 컬렉션 필드:")
            for field in sorted(sample_job.keys()):
                field_type = type(sample_job[field]).__name__
                print(f"  - {field}: {field_type}")
        else:
            print("❌ 채용공고 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_database_structure())
