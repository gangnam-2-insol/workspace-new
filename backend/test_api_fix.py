import asyncio
import json

import requests
from services_mj.mongo_service import MongoService


async def test_api_fix():
    print('=== API 수정 후 테스트 ===')

    # 1. 수정된 MongoService로 직접 데이터 가져오기
    service = MongoService()
    mongo_data = await service.get_all_applicants(0, 1)

    print('1️⃣ 수정된 MongoService 결과:')
    if mongo_data['applicants']:
        applicant = mongo_data['applicants'][0]
        print(f'email 존재: {"email" in applicant}')
        print(f'phone 존재: {"phone" in applicant}')
        print(f'email 값: {applicant.get("email", "없음")}')
        print(f'phone 값: {applicant.get("phone", "없음")}')
        print(f'모든 필드: {list(applicant.keys())}')

    # 2. API 응답 시뮬레이션 (실제 라우터 로직 사용)
    # 수정된 get_mongo_service 함수와 동일한 방식으로 MongoService 생성
    import os
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    api_service = MongoService(mongo_uri)
    api_data = await api_service.get_all_applicants(skip=0, limit=1, status=None, position=None)

    print('\n2️⃣ API 라우터 시뮬레이션 결과:')
    if api_data['applicants']:
        api_applicant = api_data['applicants'][0]
        print(f'email 존재: {"email" in api_applicant}')
        print(f'phone 존재: {"phone" in api_applicant}')
        print(f'email 값: {api_applicant.get("email", "없음")}')
        print(f'phone 값: {api_applicant.get("phone", "없음")}')
        print(f'모든 필드: {list(api_applicant.keys())}')

        # 3. 타입 매칭 확인
        print('\n3️⃣ 타입 매칭 확인:')
        for key, value in api_applicant.items():
            print(f'{key}: {type(value).__name__} = {str(value)[:50]}...')

if __name__ == "__main__":
    asyncio.run(test_api_fix())
