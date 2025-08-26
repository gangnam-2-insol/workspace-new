import asyncio
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient

async def test_api_vs_db():
    """API 응답과 DB 데이터를 비교합니다."""
    try:
        print("🔍 API 응답 vs DB 데이터 비교 시작...")
        
        # 1. API 응답 확인
        print("\n📡 API 응답 확인...")
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8000/api/applicants?skip=0&limit=5"
            async with session.get(url) as response:
                if response.status == 200:
                    api_data = await response.json()
                    print(f"✅ API 응답 성공 (상태 코드: {response.status})")
                    print(f"📊 API 응답 구조: {list(api_data.keys())}")
                    
                    if 'applicants' in api_data:
                        applicants = api_data['applicants']
                        print(f"📋 API 응답 지원자 수: {len(applicants)}")
                        
                        if applicants:
                            first_applicant = applicants[0]
                            print(f"📋 API 첫 번째 지원자 필드들: {list(first_applicant.keys())}")
                            
                            # 주요 필드 확인
                            important_fields = ['email', 'phone', 'name', 'position', 'status', 'resume_id', 'cover_letter_id']
                            for field in important_fields:
                                exists = field in first_applicant
                                value = first_applicant.get(field, 'None')
                                print(f"  - {field}: {'✅' if exists else '❌'} (값: {value})")
                else:
                    print(f"❌ API 응답 실패 (상태 코드: {response.status})")
                    error_text = await response.text()
                    print(f"❌ 오류 내용: {error_text}")
                    return
        
        # 2. DB 데이터 직접 확인
        print("\n🗄️ DB 데이터 직접 확인...")
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        db_applicants = await db.applicants.find().limit(5).to_list(5)
        print(f"📋 DB 지원자 수: {len(db_applicants)}")
        
        if db_applicants:
            first_db_applicant = db_applicants[0]
            print(f"📋 DB 첫 번째 지원자 필드들: {list(first_db_applicant.keys())}")
            
            # 주요 필드 확인
            important_fields = ['email', 'phone', 'name', 'position', 'status', 'resume_id', 'cover_letter_id']
            for field in important_fields:
                exists = field in first_db_applicant
                value = first_db_applicant.get(field, 'None')
                print(f"  - {field}: {'✅' if exists else '❌'} (값: {value})")
        
        client.close()
        
        # 3. 비교 분석
        print("\n🔍 비교 분석...")
        if 'applicants' in api_data and db_applicants:
            api_first = api_data['applicants'][0]
            db_first = db_applicants[0]
            
            print("📊 필드 일치성 확인:")
            all_fields = set(api_first.keys()) | set(db_first.keys())
            
            for field in sorted(all_fields):
                api_has = field in api_first
                db_has = field in db_first
                api_value = api_first.get(field, 'None')
                db_value = db_first.get(field, 'None')
                
                if api_has and db_has:
                    if api_value == db_value:
                        print(f"  ✅ {field}: 일치")
                    else:
                        print(f"  ⚠️ {field}: 불일치 (API: {api_value}, DB: {db_value})")
                elif api_has and not db_has:
                    print(f"  ❌ {field}: API에만 존재 (값: {api_value})")
                elif not api_has and db_has:
                    print(f"  ❌ {field}: DB에만 존재 (값: {db_value})")
        
        print("\n✅ 비교 완료")
        
    except Exception as e:
        print(f"❌ 비교 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_vs_db())
