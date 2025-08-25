import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def find_valid_applicant():
    """실제 데이터가 있는 지원자 찾기"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme
        
        print("=== 실제 데이터가 있는 지원자 찾기 ===")
        
        # 성장배경이 있는 지원자 찾기
        applicants_with_growth = await db.applicants.find({
            "growthBackground": {"$exists": True, "$ne": "", "$ne": None}
        }).limit(5).to_list(5)
        
        print(f"성장배경이 있는 지원자: {len(applicants_with_growth)}명")
        for i, applicant in enumerate(applicants_with_growth):
            print(f"{i+1}. ID: {applicant['_id']}")
            print(f"   이름: {applicant.get('personal_info', {}).get('name', 'N/A')}")
            print(f"   성장배경 길이: {len(applicant.get('growthBackground', ''))}")
            print(f"   지원동기 길이: {len(applicant.get('motivation', ''))}")
            print(f"   경력사항 길이: {len(applicant.get('careerHistory', ''))}")
            print()
        
        # 지원동기가 있는 지원자 찾기
        applicants_with_motivation = await db.applicants.find({
            "motivation": {"$exists": True, "$ne": "", "$ne": None}
        }).limit(5).to_list(5)
        
        print(f"지원동기가 있는 지원자: {len(applicants_with_motivation)}명")
        for i, applicant in enumerate(applicants_with_motivation):
            print(f"{i+1}. ID: {applicant['_id']}")
            print(f"   이름: {applicant.get('personal_info', {}).get('name', 'N/A')}")
            print(f"   지원동기 길이: {len(applicant.get('motivation', ''))}")
            print()
        
        # 경력사항이 있는 지원자 찾기
        applicants_with_career = await db.applicants.find({
            "careerHistory": {"$exists": True, "$ne": "", "$ne": None}
        }).limit(5).to_list(5)
        
        print(f"경력사항이 있는 지원자: {len(applicants_with_career)}명")
        for i, applicant in enumerate(applicants_with_career):
            print(f"{i+1}. ID: {applicant['_id']}")
            print(f"   이름: {applicant.get('personal_info', {}).get('name', 'N/A')}")
            print(f"   경력사항 길이: {len(applicant.get('careerHistory', ''))}")
            print()
        
        client.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(find_valid_applicant())

