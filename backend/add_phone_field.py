import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
import random

async def add_phone_field_to_existing_data():
    """기존 지원자 데이터에 phone 필드를 추가합니다."""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        print("🔍 기존 지원자 데이터에 phone 필드 추가 시작...")
        
        # 1. phone 필드가 없는 지원자 찾기
        applicants_without_phone = await db.applicants.find(
            {"phone": {"$exists": False}}
        ).to_list(None)
        
        print(f"📊 phone 필드가 없는 지원자 수: {len(applicants_without_phone)}")
        
        if not applicants_without_phone:
            print("✅ 모든 지원자에게 이미 phone 필드가 있습니다.")
            return
        
        # 2. Faker로 한국 전화번호 생성
        fake = Faker('ko_KR')
        
        # 3. 각 지원자에게 phone 필드 추가
        updated_count = 0
        for applicant in applicants_without_phone:
            # 한국 전화번호 형식으로 생성 (010-XXXX-XXXX)
            phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
            # DB 업데이트
            result = await db.applicants.update_one(
                {"_id": applicant["_id"]},
                {"$set": {"phone": phone}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"✅ {applicant.get('name', 'Unknown')} - {phone}")
        
        print(f"\n📊 총 {updated_count}명의 지원자에게 phone 필드가 추가되었습니다.")
        
        # 4. 업데이트 후 확인
        remaining_without_phone = await db.applicants.find(
            {"phone": {"$exists": False}}
        ).count_documents({})
        
        print(f"📊 아직 phone 필드가 없는 지원자 수: {remaining_without_phone}")
        
        client.close()
        print("✅ phone 필드 추가 완료")
        
    except Exception as e:
        print(f"❌ phone 필드 추가 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(add_phone_field_to_existing_data())
