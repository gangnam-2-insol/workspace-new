#!/usr/bin/env python3
"""
하이브리드 모듈 연결 상태 확인
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_hybrid_status():
    """하이브리드 모듈 상태 확인"""
    print("🔍 하이브리드 모듈 연결 상태 확인")
    print("=" * 50)
    
    try:
        # 1. 모듈 파일 존재 확인
        print("1️⃣ 모듈 파일 존재 확인...")
        hybrid_dir = "modules/hybrid"
        required_files = ["__init__.py", "models.py", "services.py", "router.py"]
        
        for file in required_files:
            file_path = os.path.join(hybrid_dir, file)
            if os.path.exists(file_path):
                print(f"   ✅ {file} 존재")
            else:
                print(f"   ❌ {file} 없음")
        
        # 2. 직접 import 테스트
        print("\n2️⃣ 직접 import 테스트...")
        from modules.hybrid.router import router as hybrid_router
        print(f"   ✅ 하이브리드 라우터 import 성공")
        print(f"   📊 엔드포인트 수: {len(hybrid_router.routes)}")
        
        # 3. main.py에서 import 테스트
        print("\n3️⃣ main.py에서 import 테스트...")
        import main
        print(f"   ✅ main.py import 성공")
        print(f"   🔍 hybrid_router 변수: {main.hybrid_router is not None}")
        
        # 4. FastAPI 앱에서 라우터 확인
        print("\n4️⃣ FastAPI 앱에서 라우터 확인...")
        app = main.app
        
        # 등록된 라우터들 확인
        hybrid_routes = []
        for route in app.routes:
            if hasattr(route, 'routes'):  # APIRouter
                for sub_route in route.routes:
                    route_path = f"{route.prefix}{sub_route.path}"
                    if '/api/hybrid' in route_path:
                        hybrid_routes.append(f"{list(sub_route.methods)} {route_path}")
        
        print(f"   📊 하이브리드 라우트 수: {len(hybrid_routes)}")
        
        if hybrid_routes:
            print("   ✅ 하이브리드 라우터가 FastAPI 앱에 등록됨")
            print("   📋 등록된 엔드포인트:")
            for route in hybrid_routes[:5]:  # 처음 5개만 표시
                print(f"      - {route}")
            if len(hybrid_routes) > 5:
                print(f"      ... 외 {len(hybrid_routes) - 5}개")
        else:
            print("   ❌ 하이브리드 라우터가 FastAPI 앱에 등록되지 않음")
        
        # 5. 최종 상태 요약
        print("\n" + "=" * 50)
        print("📊 최종 상태 요약:")
        print(f"   모듈 파일: ✅ 모두 존재")
        print(f"   직접 import: ✅ 성공")
        print(f"   main.py import: ✅ 성공")
        print(f"   FastAPI 등록: {'✅ 성공' if hybrid_routes else '❌ 실패'}")
        
        if hybrid_routes:
            print("\n🎉 하이브리드 모듈이 정상적으로 연결되었습니다!")
            return True
        else:
            print("\n⚠️ 하이브리드 모듈이 FastAPI에 등록되지 않았습니다.")
            return False
            
    except Exception as e:
        print(f"\n❌ 확인 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_hybrid_status()
    sys.exit(0 if success else 1)
