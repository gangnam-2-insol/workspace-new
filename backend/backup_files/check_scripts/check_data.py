import asyncio
import json
import os

import requests
from services.mongo_service import MongoService as MongoServiceOld
from services_mj.mongo_service import MongoService as MongoServiceMJ


async def check_data():
    print('=== MongoService 클래스 비교 ===')

    # 1. services_mj의 MongoService
    service_mj = MongoServiceMJ()
    print(f'1️⃣ services_mj MongoService URI: {service_mj.mongo_uri}')

    # 2. services의 MongoService
    service_old = MongoServiceOld()
    print(f'2️⃣ services MongoService URI: {service_old.mongo_uri}')

    # 3. 두 서비스에서 데이터 가져오기 비교
    print('\n=== 데이터 비교 ===')

    # services_mj 서비스
    data_mj = await service_mj.get_all_applicants(0, 1)
    if data_mj['applicants']:
        applicant_mj = data_mj['applicants'][0]
        print(f'services_mj - email 존재: {"email" in applicant_mj}')
        print(f'services_mj - phone 존재: {"phone" in applicant_mj}')
        if "email" in applicant_mj:
            print(f'services_mj - email 값: {applicant_mj["email"]}')
        if "phone" in applicant_mj:
            print(f'services_mj - phone 값: {applicant_mj["phone"]}')

    # services 서비스
    data_old = await service_old.get_all_applicants(0, 1)
    if data_old['applicants']:
        applicant_old = data_old['applicants'][0]
        print(f'services - email 존재: {"email" in applicant_old}')
        print(f'services - phone 존재: {"phone" in applicant_old}')
        if "email" in applicant_old:
            print(f'services - email 값: {applicant_old["email"]}')
        if "phone" in applicant_old:
            print(f'services - phone 값: {applicant_old["phone"]}')

    # 4. API 호출
    print('\n=== API 호출 결과 ===')
    try:
        response = requests.get("http://localhost:8000/api/applicants?skip=0&limit=1")
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get('applicants') and len(api_data['applicants']) > 0:
                api_applicant = api_data['applicants'][0]
                print(f'API 응답 - email 존재: {"email" in api_applicant}')
                print(f'API 응답 - phone 존재: {"phone" in api_applicant}')
        else:
            print(f'API 호출 실패: {response.status_code}')
    except Exception as e:
        print(f'API 호출 오류: {e}')

if __name__ == "__main__":
    asyncio.run(check_data())
