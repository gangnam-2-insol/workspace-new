import asyncio
import json
from datetime import datetime

from bson import ObjectId
from services_mj.mongo_service import MongoService


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

async def test_json_serialization():
    print('=== JSON 직렬화 테스트 ===')

    service = MongoService()
    data = await service.get_all_applicants(0, 1)

    if data['applicants']:
        applicant = data['applicants'][0]
        print('1️⃣ 원본 데이터 타입:')
        print(f'created_at 타입: {type(applicant.get("created_at"))}')
        print(f'created_at 값: {applicant.get("created_at")}')

        # JSON 직렬화 테스트
        try:
            print('\n2️⃣ 기본 JSON 직렬화:')
            json_str = json.dumps(applicant, ensure_ascii=False)
            print('✅ 성공')
        except TypeError as e:
            print(f'❌ 실패: {e}')

            print('\n3️⃣ 커스텀 인코더로 JSON 직렬화:')
            json_str = json.dumps(applicant, cls=DateTimeEncoder, ensure_ascii=False)
            print('✅ 성공')

            # 직렬화된 데이터 확인
            parsed_data = json.loads(json_str)
            print(f'직렬화된 created_at: {parsed_data.get("created_at")}')
            print(f'email 존재: {"email" in parsed_data}')
            print(f'phone 존재: {"phone" in parsed_data}')

if __name__ == "__main__":
    asyncio.run(test_json_serialization())
