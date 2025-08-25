#!/usr/bin/env python3
import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def test_applicants():
    """지원자 API 테스트"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme

        print("=== 지원자 API 테스트 ===")

        # 지원자 수 확인
        count = await db.applicants.count_documents({})
        print(f"총 지원자 수: {count}")

        # 첫 3명만 조회
        applicants = await db.applicants.find({}).limit(3).to_list(3)

        for i, applicant in enumerate(applicants):
            print(f"\n--- 지원자 {i+1} ---")
            print(f"ID: {applicant['_id']}")
            print(f"personal_info: {applicant.get('personal_info', 'N/A')}")
            print(f"desired_position: {applicant.get('desired_position', 'N/A')}")
            print(f"application_status: {applicant.get('application_status', 'N/A')}")
            print(f"필드들: {list(applicant.keys())}")

        client.close()
        return True

    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_applicants())

    
    base_url = "http://localhost:8000"
    
    print("🧪 지원자 API 테스트 시작...")
    
    # 1. 지원자 목록 조회 테스트
    try:
        print("\n1️⃣ 지원자 목록 조회 테스트")
        response = requests.get(f"{base_url}/api/applicants?limit=5")
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공! 지원자 수: {len(data.get('applicants', []))}명")
            
            # 첫 번째 지원자 정보 출력
            if data.get('applicants'):
                first_applicant = data['applicants'][0]
                print(f"   📋 첫 번째 지원자: {first_applicant.get('name', 'N/A')} ({first_applicant.get('position', 'N/A')})")
                print(f"   📧 이메일: {first_applicant.get('email', 'N/A')}")
                print(f"   📋 상태: {first_applicant.get('status', 'N/A')}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패: 백엔드 서버가 실행 중인지 확인하세요")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 2. 통계 조회 테스트
    try:
        print("\n2️⃣ 지원자 통계 조회 테스트")
        response = requests.get(f"{base_url}/api/applicants/stats/overview")
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 성공!")
            print(f"   📊 총 지원자: {stats.get('total_applicants', 0)}명")
            print(f"   📈 승인: {stats.get('approved_count', 0)}명")
            print(f"   ⏳ 대기: {stats.get('pending_count', 0)}명")
            print(f"   ❌ 거절: {stats.get('rejected_count', 0)}명")
        else:
            print(f"   ❌ 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 3. 서버 상태 확인
    try:
        print("\n3️⃣ 서버 상태 확인")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   서버 응답: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ 서버 연결 실패")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

if __name__ == "__main__":
    test_applicants_api()
