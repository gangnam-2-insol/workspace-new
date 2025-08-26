#!/usr/bin/env python3
import asyncio
import json

import aiohttp


async def test_api_with_email_phone():
    """API에서 email과 phone 필드가 포함되는지 테스트"""

    try:
        # API 호출
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8000/api/applicants?skip=0&limit=1"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ API 응답 성공!")
                    print(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")

                    if data.get('applicants') and len(data['applicants']) > 0:
                        first_applicant = data['applicants'][0]
                        print(f"\n🔍 첫 번째 지원자 필드들: {list(first_applicant.keys())}")
                        print(f"🔍 email 존재: {'email' in first_applicant}")
                        print(f"🔍 phone 존재: {'phone' in first_applicant}")

                        if 'email' in first_applicant:
                            print(f"✅ email 값: {first_applicant['email']}")
                        else:
                            print("❌ email 필드 없음")

                        if 'phone' in first_applicant:
                            print(f"✅ phone 값: {first_applicant['phone']}")
                        else:
                            print("❌ phone 필드 없음")
                    else:
                        print("❌ 지원자 데이터가 없습니다.")
                else:
                    print(f"❌ API 응답 실패: {response.status}")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    print("🔍 API에서 email과 phone 필드 테스트 시작...")
    asyncio.run(test_api_with_email_phone())
