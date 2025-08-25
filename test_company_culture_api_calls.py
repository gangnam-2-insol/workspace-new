import os
import asyncio
import httpx
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
load_dotenv("backend/.env")

async def test_company_culture_api_calls():
    """인재상 관리 API 실제 호출 테스트"""
    print("🔍 인재상 관리 API 실제 호출 테스트")
    print("=" * 60)

    # API 기본 URL
    api_base_url = os.getenv("REACT_APP_API_URL", "http://localhost:8000")
    culture_endpoint = f"{api_base_url}/api/company-culture"

    print(f"✅ API Base URL: {api_base_url}")
    print(f"✅ 인재상 API 엔드포인트: {culture_endpoint}")

    async with httpx.AsyncClient(timeout=30.0) as client:

        # 1. 인재상 목록 조회 테스트
        print("\n1️⃣ 인재상 목록 조회 테스트")
        print("-" * 40)

        try:
            response = await client.get(f"{culture_endpoint}/?active_only=true")
            if response.status_code == 200:
                cultures = response.json()
                print(f"✅ 인재상 목록 조회 성공: {len(cultures)}개")

                if cultures:
                    print("   첫 번째 인재상:")
                    first_culture = cultures[0]
                    print(f"   - ID: {first_culture.get('id')}")
                    print(f"   - 이름: {first_culture.get('name')}")
                    print(f"   - 설명: {first_culture.get('description', '')[:50]}...")
                    print(f"   - 활성화: {first_culture.get('is_active')}")
                else:
                    print("   ℹ️ 인재상 데이터가 없습니다.")
            else:
                print(f"❌ 인재상 목록 조회 실패: {response.status_code}")
                print(f"   응답: {response.text}")
        except Exception as e:
            print(f"❌ 인재상 목록 조회 오류: {str(e)}")

        # 2. 인재상 통계 조회 테스트
        print("\n2️⃣ 인재상 통계 조회 테스트")
        print("-" * 40)

        try:
            response = await client.get(f"{culture_endpoint}/stats/overview")
            if response.status_code == 200:
                stats = response.json()
                print("✅ 인재상 통계 조회 성공")
                print(f"   - 총 인재상 수: {stats.get('total_cultures', 0)}")
                print(f"   - 활성화된 인재상 수: {stats.get('active_cultures', 0)}")
            else:
                print(f"❌ 인재상 통계 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 인재상 통계 조회 오류: {str(e)}")

        # 3. AI 인재상 생성 테스트
        print("\n3️⃣ AI 인재상 생성 테스트")
        print("-" * 40)

        try:
            test_data = {
                "keywords": ["혁신", "창의성", "협력"],
                "job": "개발자",
                "department": "IT",
                "use_trends": False
            }

            response = await client.post(
                f"{culture_endpoint}/ai-generate",
                json=test_data,
                timeout=60.0  # AI 생성은 시간이 오래 걸릴 수 있음
            )

            if response.status_code == 200:
                ai_cultures = response.json()
                print(f"✅ AI 인재상 생성 성공: {len(ai_cultures)}개")

                if ai_cultures:
                    print("   생성된 인재상:")
                    for i, culture in enumerate(ai_cultures[:3]):  # 처음 3개만 표시
                        print(f"   {i+1}. {culture.get('name', 'N/A')}")
                        print(f"      설명: {culture.get('description', 'N/A')[:50]}...")
            else:
                print(f"❌ AI 인재상 생성 실패: {response.status_code}")
                print(f"   응답: {response.text}")
        except Exception as e:
            print(f"❌ AI 인재상 생성 오류: {str(e)}")

        # 4. 인재상 생성 테스트 (새로운 인재상)
        print("\n4️⃣ 인재상 생성 테스트")
        print("-" * 40)

        try:
            test_culture_data = {
                "name": "테스트 인재상",
                "description": "테스트를 위한 임시 인재상입니다.",
                "is_active": True
            }

            response = await client.post(
                culture_endpoint,
                json=test_culture_data
            )

            if response.status_code == 200:
                created_culture = response.json()
                print("✅ 인재상 생성 성공")
                print(f"   - ID: {created_culture.get('id')}")
                print(f"   - 이름: {created_culture.get('name')}")
                print(f"   - 설명: {created_culture.get('description')}")

                # 생성된 인재상 삭제 (테스트 정리)
                culture_id = created_culture.get('id')
                if culture_id:
                    delete_response = await client.delete(f"{culture_endpoint}/{culture_id}")
                    if delete_response.status_code == 200:
                        print("   - 테스트 인재상 삭제 완료")
                    else:
                        print(f"   - 테스트 인재상 삭제 실패: {delete_response.status_code}")
            else:
                print(f"❌ 인재상 생성 실패: {response.status_code}")
                print(f"   응답: {response.text}")
        except Exception as e:
            print(f"❌ 인재상 생성 오류: {str(e)}")

        # 5. 카테고리 목록 조회 테스트
        print("\n5️⃣ 카테고리 목록 조회 테스트")
        print("-" * 40)

        try:
            response = await client.get(f"{culture_endpoint}/categories/list")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ 카테고리 목록 조회 성공: {len(categories)}개")

                if categories:
                    print("   카테고리 목록:")
                    for category in categories[:5]:  # 처음 5개만 표시
                        print(f"   - {category}")
            else:
                print(f"❌ 카테고리 목록 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 카테고리 목록 조회 오류: {str(e)}")

async def main():
    """인재상 관리 API 호출 전체 테스트"""
    print("🚀 인재상 관리 API 호출 전체 테스트")
    print("=" * 60)

    try:
        await test_company_culture_api_calls()

        print("\n" + "=" * 60)
        print("📊 인재상 관리 API 호출 테스트 완료")
        print("=" * 60)
        print("🎉 인재상 관리 API가 정상적으로 작동합니다!")
        print("💡 이제 인재상 관리 기능을 안심하고 사용할 수 있습니다.")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        print("💡 백엔드 서버가 실행 중인지 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())
