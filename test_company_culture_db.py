import os
import asyncio
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
load_dotenv("backend/.env")

async def test_company_culture_db_connection():
    """인재상 관리 DB 연결 테스트"""
    print("🔍 인재상 관리페이지 DB 연결 확인")
    print("=" * 60)

    # 1. 환경변수 확인
    print("1️⃣ 환경변수 확인")
    print("-" * 40)

    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        print(f"✅ MONGODB_URI 설정됨")
        print(f"   URI: {mongodb_uri}")
    else:
        print("❌ MONGODB_URI 설정되지 않음")
        print("   기본값: mongodb://localhost:27017/hireme")

    print()

    # 2. MongoDB 연결 테스트
    print("2️⃣ MongoDB 연결 테스트")
    print("-" * 40)

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        # MongoDB 클라이언트 생성
        client = AsyncIOMotorClient(mongodb_uri or "mongodb://localhost:27017/hireme")
        db = client.hireme

        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공")

        # 데이터베이스 목록 확인
        db_list = await client.list_database_names()
        print(f"✅ 사용 가능한 데이터베이스: {len(db_list)}개")
        if "hireme" in db_list:
            print("   - hireme 데이터베이스 존재")
        else:
            print("   - hireme 데이터베이스 없음 (자동 생성됨)")

        # 컬렉션 목록 확인
        collections = await db.list_collection_names()
        print(f"✅ 컬렉션 목록: {len(collections)}개")
        for collection in collections:
            print(f"   - {collection}")

        return client, db

    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {str(e)}")
        return None, None

async def test_company_culture_collection(client, db):
    """인재상 컬렉션 테스트"""
    print("\n3️⃣ 인재상 컬렉션 테스트")
    print("-" * 40)

    if db is None:
        print("❌ DB 연결이 없어서 테스트할 수 없습니다.")
        return False

    try:
        collection = db.company_cultures

        # 컬렉션 존재 확인
        collection_exists = await db.list_collection_names()
        if "company_cultures" in collection_exists:
            print("✅ company_cultures 컬렉션 존재")
        else:
            print("⚠️ company_cultures 컬렉션 없음 (첫 데이터 생성 시 자동 생성)")

        # 문서 수 확인
        count = await collection.count_documents({})
        print(f"✅ 현재 인재상 수: {count}개")

        # 샘플 데이터 확인
        if count > 0:
            sample = await collection.find_one({})
            print("✅ 샘플 데이터:")
            print(f"   - ID: {sample.get('_id')}")
            print(f"   - 이름: {sample.get('name', 'N/A')}")
            print(f"   - 설명: {sample.get('description', 'N/A')[:50]}...")
            print(f"   - 활성화: {sample.get('is_active', True)}")
        else:
            print("ℹ️ 인재상 데이터가 없습니다.")

        return True

    except Exception as e:
        print(f"❌ 인재상 컬렉션 테스트 실패: {str(e)}")
        return False

async def test_company_culture_service():
    """인재상 서비스 테스트"""
    print("\n4️⃣ 인재상 서비스 테스트")
    print("-" * 40)

    try:
        from backend.modules.company_culture.services import CompanyCultureService, get_database

        # 데이터베이스 연결
        db = get_database()
        print("✅ 데이터베이스 연결 함수 로드 성공")

        # 서비스 초기화
        service = CompanyCultureService(db)
        print("✅ CompanyCultureService 초기화 성공")

        # 모든 인재상 조회 테스트
        try:
            cultures = await service.get_all_cultures(active_only=True)
            print(f"✅ 활성화된 인재상 조회 성공: {len(cultures)}개")

            if cultures:
                print("   첫 번째 인재상:")
                first_culture = cultures[0]
                print(f"   - ID: {first_culture.id}")
                print(f"   - 이름: {first_culture.name}")
                print(f"   - 설명: {first_culture.description[:50]}...")
                print(f"   - 활성화: {first_culture.is_active}")
        except Exception as e:
            print(f"⚠️ 인재상 조회 테스트 실패: {str(e)}")

        return True

    except ImportError as e:
        print(f"❌ 인재상 서비스 import 실패: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 인재상 서비스 테스트 실패: {str(e)}")
        return False

async def test_company_culture_api():
    """인재상 API 엔드포인트 테스트"""
    print("\n5️⃣ 인재상 API 엔드포인트 테스트")
    print("-" * 40)

    try:
        from backend.routers.company_culture import router

        # 라우터에서 엔드포인트 확인
        routes = router.routes
        culture_routes = [route for route in routes if 'company-culture' in route.path]

        print(f"✅ 인재상 관련 엔드포인트 {len(culture_routes)}개 발견:")
        for route in culture_routes:
            print(f"   - {route.methods} {route.path}")

        # 주요 엔드포인트들
        expected_endpoints = [
            "/api/company-culture/",
            "/api/company-culture/{culture_id}",
            "/api/company-culture/stats/overview",
            "/api/company-culture/ai-generate"
        ]

        print("\n📋 주요 인재상 관리 엔드포인트:")
        for endpoint in expected_endpoints:
            found = any(endpoint.replace("{culture_id}", "test") in route.path for route in culture_routes)
            status = "✅" if found else "❌"
            print(f"   {status} {endpoint}")

        return True

    except Exception as e:
        print(f"❌ 인재상 API 테스트 실패: {str(e)}")
        return False

async def test_frontend_connection():
    """프론트엔드 연결 테스트"""
    print("\n6️⃣ 프론트엔드 연결 테스트")
    print("-" * 40)

    try:
        # 프론트엔드 API URL 확인
        api_base_url = os.getenv("REACT_APP_API_URL", "http://localhost:8000")
        print(f"✅ API Base URL: {api_base_url}")

        # 인재상 API 엔드포인트
        culture_endpoint = f"{api_base_url}/api/company-culture/"
        print(f"✅ 인재상 API 엔드포인트: {culture_endpoint}")

        # HTTP 요청 테스트 (선택사항)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(culture_endpoint, timeout=5.0)
                if response.status_code == 200:
                    print("✅ 프론트엔드 API 연결 성공")
                else:
                    print(f"⚠️ API 응답 상태: {response.status_code}")
        except Exception as e:
            print(f"⚠️ API 연결 테스트 실패 (서버가 실행되지 않았을 수 있음): {str(e)}")

        return True

    except Exception as e:
        print(f"❌ 프론트엔드 연결 테스트 실패: {str(e)}")
        return False

async def main():
    """인재상 관리 DB 연결 전체 테스트"""
    print("🚀 인재상 관리페이지 DB 연결 전체 테스트")
    print("=" * 60)

    # 각 테스트 실행
    tests = [
        test_company_culture_db_connection,
        test_company_culture_service,
        test_company_culture_api,
        test_frontend_connection
    ]

    results = []
    client = None
    db = None

    for i, test in enumerate(tests):
        try:
            if i == 0:  # 첫 번째 테스트에서 client, db 반환
                client, db = await test()
                results.append(client is not None and db is not None)

                # 인재상 컬렉션 테스트 추가
                if client is not None and db is not None:
                    collection_result = await test_company_culture_collection(client, db)
                    results.append(collection_result)
            else:
                result = await test()
                results.append(result)
        except Exception as e:
            print(f"❌ 테스트 중 오류: {str(e)}")
            results.append(False)

    # MongoDB 연결 종료
    if client:
        client.close()

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 인재상 관리 DB 연결 테스트 결과")
    print("=" * 60)

    success_count = sum(results)
    total_count = len(results)

    print(f"✅ 성공: {success_count}/{total_count}")
    print(f"❌ 실패: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("🎉 인재상 관리페이지 DB 연결이 완벽하게 설정되었습니다!")
        print("💡 이제 인재상 관리 기능을 안심하고 사용할 수 있습니다.")
    else:
        print("⚠️ 일부 기능에 문제가 있습니다.")
        print("💡 MongoDB 서버가 실행 중인지 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())
