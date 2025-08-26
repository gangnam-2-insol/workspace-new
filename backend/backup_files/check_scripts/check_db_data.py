import asyncio

from services_mj.mongo_service import MongoService


async def check_db_data():
    try:
        # MongoService 인스턴스 생성
        service = MongoService('mongodb://localhost:27017/hireme')

        # 지원자 데이터 가져오기
        result = await service.get_all_applicants(skip=0, limit=1)

        print("🔍 MongoService 응답:")
        print(f"전체 결과: {result}")

        if result.get('applicants') and len(result['applicants']) > 0:
            first_applicant = result['applicants'][0]
            print(f"\n🔍 첫 번째 지원자 필드들: {list(first_applicant.keys())}")
            print(f"🔍 email 존재: {'email' in first_applicant}")
            print(f"🔍 phone 존재: {'phone' in first_applicant}")

            if 'email' in first_applicant:
                print(f"🔍 email 값: {first_applicant['email']}")
            if 'phone' in first_applicant:
                print(f"🔍 phone 값: {first_applicant['phone']}")
        else:
            print("❌ 지원자 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(check_db_data())
