#!/usr/bin/env python3
"""
하이브리드 모듈 연결 테스트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hybrid_connection():
    """하이브리드 모듈 연결 테스트"""
    print("🔍 하이브리드 모듈 연결 테스트 시작...")
    
    try:
        # 1. 직접 import 테스트
        print("1️⃣ 직접 import 테스트...")
        from modules.hybrid.router import router as hybrid_router
        print(f"   ✅ 하이브리드 라우터 import 성공")
        print(f"   📊 등록된 엔드포인트 수: {len(hybrid_router.routes)}")
        
        # 2. main.py에서 import 테스트
        print("\n2️⃣ main.py에서 import 테스트...")
        import main
        print("   ✅ main.py import 성공")
        
        # 3. FastAPI 앱에서 라우터 확인
        print("\n3️⃣ FastAPI 앱에서 라우터 확인...")
        app = main.app
        
        # 등록된 라우터들 확인
        registered_routes = []
        for route in app.routes:
            if hasattr(route, 'routes'):  # APIRouter
                for sub_route in route.routes:
                    registered_routes.append(f"{list(sub_route.methods)} {route.prefix}{sub_route.path}")
            else:  # 직접 등록된 라우트
                registered_routes.append(f"{list(route.methods)} {route.path}")
        
        # 하이브리드 관련 라우트 찾기
        hybrid_routes = [route for route in registered_routes if '/api/hybrid' in route]
        
        print(f"   📊 전체 등록된 라우트 수: {len(registered_routes)}")
        print(f"   🔍 하이브리드 관련 라우트 수: {len(hybrid_routes)}")
        
        if hybrid_routes:
            print("   ✅ 하이브리드 라우터가 FastAPI 앱에 등록됨")
            print("   📋 등록된 하이브리드 엔드포인트:")
            for route in hybrid_routes:
                print(f"      - {route}")
        else:
            print("   ❌ 하이브리드 라우터가 FastAPI 앱에 등록되지 않음")
            
        # 4. main.py의 라우터 변수 확인
        print("\n4️⃣ main.py의 라우터 변수 확인...")
        if hasattr(main, 'hybrid_router'):
            if main.hybrid_router is not None:
                print("   ✅ hybrid_router 변수가 존재하고 None이 아님")
            else:
                print("   ⚠️ hybrid_router 변수가 None임")
        else:
            print("   ❌ hybrid_router 변수가 존재하지 않음")
            
        return len(hybrid_routes) > 0
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hybrid_connection()
    if success:
        print("\n🎉 하이브리드 모듈이 정상적으로 연결되었습니다!")
    else:
        print("\n⚠️ 하이브리드 모듈 연결에 문제가 있습니다.")
    sys.exit(0 if success else 1)
