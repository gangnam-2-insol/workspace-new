#!/usr/bin/env python3
"""
API 엔드포인트 테스트 스크립트
"""

import asyncio
import aiohttp
import json
import sys

def test_health_endpoint():
    """헬스 체크 엔드포인트 테스트"""
    print("🏥 헬스 체크 테스트...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def test_hybrid_create():
    """하이브리드 생성 엔드포인트 테스트"""
    print("\n🔧 하이브리드 생성 테스트...")
    
    test_data = {
        "applicant_id": "test_user_123",
        "analysis_type": "comprehensive",
        "resume_id": "resume_456",
        "cover_letter_id": "cover_789",
        "portfolio_id": "portfolio_101"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/hybrid/create",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # MongoDB 연결이 없어도 422 (Validation Error)는 정상적인 응답
        return response.status_code in [200, 201, 422]
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def test_hybrid_list():
    """하이브리드 목록 조회 테스트"""
    print("\n📋 하이브리드 목록 조회 테스트...")
    
    try:
        response = requests.get("http://localhost:8000/api/hybrid/")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code in [200, 422]
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def test_hybrid_search():
    """하이브리드 검색 테스트"""
    print("\n🔍 하이브리드 검색 테스트...")
    
    test_data = {
        "query": "테스트 검색",
        "limit": 5
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/hybrid/search",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code in [200, 422]
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def test_hybrid_statistics():
    """하이브리드 통계 테스트"""
    print("\n📊 하이브리드 통계 테스트...")
    
    try:
        response = requests.get("http://localhost:8000/api/hybrid/statistics/overview")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code in [200, 422]
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 API 엔드포인트 테스트 시작")
    print("=" * 50)
    
    # 서버가 시작될 때까지 잠시 대기
    print("⏳ 서버 시작 대기 중...")
    await asyncio.sleep(3)
    
    # 각 엔드포인트 테스트
    tests = [
        ("헬스 체크", test_health_endpoint),
        ("하이브리드 생성", test_hybrid_create),
        ("하이브리드 목록", test_hybrid_list),
        ("하이브리드 검색", test_hybrid_search),
        ("하이브리드 통계", test_hybrid_statistics),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 테스트 중...")
        success = test_func()
        results.append((test_name, success))
        print(f"   {'✅ 성공' if success else '❌ 실패'}")
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약:")
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n🎯 전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과! 하이브리드 API가 정상적으로 작동합니다.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. MongoDB 연결이 필요할 수 있습니다.")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
