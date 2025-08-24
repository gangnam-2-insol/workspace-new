#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로젝트 전체 상태 확인 스크립트
간단한 것부터 순서대로 체크합니다.
"""

import asyncio
import os
import sys
from datetime import datetime


def check_python_environment():
    """Python 환경 확인"""
    print("🐍 Python 환경 확인:")
    print(f"  Python 버전: {sys.version}")
    print(f"  Python 경로: {sys.executable}")
    print(f"  현재 작업 디렉토리: {os.getcwd()}")
    print()

def check_imports():
    """필수 모듈 import 확인"""
    print("📦 필수 모듈 import 확인:")

    modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("motor", "motor"),
        ("openai", "openai"),
        ("pinecone", "pinecone"),
        ("pymongo", "pymongo"),
    ]

    for module_name, import_name in modules:
        try:
            __import__(import_name)
            print(f"  ✅ {module_name}")
        except ImportError:
            print(f"  ❌ {module_name} - 설치 필요")
    print()

def check_project_structure():
    """프로젝트 구조 확인"""
    print("📁 프로젝트 구조 확인:")

    required_dirs = [
        "modules",
        "modules/core/services",
        "modules/ai/services",
        "modules/data/services",
        "modules/shared",
        "modules/cover_letter",
        "modules/resume",
        "modules/portfolio",
        "modules/hybrid",
        "routers",
        "models",
        "utils"
    ]

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - 없음")
    print()

def check_main_import():
    """main.py import 확인"""
    print("🚀 main.py import 확인:")
    try:
        import sys
        sys.path.append('.')
        import main
        print("  ✅ main.py import 성공")
        print("  ✅ 모든 모듈이 정상적으로 로드됨")
    except Exception as e:
        print(f"  ❌ main.py import 실패: {e}")
    print()

def check_environment_variables():
    """환경 변수 확인"""
    print("🔧 환경 변수 확인:")

    env_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "MONGODB_URI",
        "ELASTICSEARCH_URL"
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # API 키는 보안상 일부만 표시
            if "API_KEY" in var or "SECRET" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️ {var}: 설정되지 않음")
    print()

async def check_database_connection():
    """데이터베이스 연결 확인"""
    print("🗄️ 데이터베이스 연결 확인:")

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        # MongoDB 연결 확인
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongodb_uri)

        # 연결 테스트
        await client.admin.command('ping')
        print("  ✅ MongoDB 연결 성공")

        # 데이터베이스 목록 확인
        db_list = await client.list_database_names()
        print(f"  📊 사용 가능한 데이터베이스: {len(db_list)}개")

        client.close()

    except Exception as e:
        print(f"  ❌ MongoDB 연결 실패: {e}")
    print()

def check_duplicate_files():
    """중복 파일 확인"""
    print("🔍 중복 파일 확인:")

    # _mj.py 파일들 확인
    mj_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('_mj.py'):
                mj_files.append(os.path.join(root, file))

    if mj_files:
        print(f"  ⚠️ _mj.py 파일 {len(mj_files)}개 발견:")
        for file in mj_files[:5]:  # 처음 5개만 표시
            print(f"    - {file}")
        if len(mj_files) > 5:
            print(f"    ... 및 {len(mj_files) - 5}개 더")
    else:
        print("  ✅ 중복 파일 없음")
    print()

def main():
    """메인 함수"""
    print("=" * 60)
    print("🔍 프로젝트 상태 확인 시작")
    print(f"📅 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # 1. Python 환경 확인
    check_python_environment()

    # 2. 모듈 import 확인
    check_imports()

    # 3. 프로젝트 구조 확인
    check_project_structure()

    # 4. 환경 변수 확인
    check_environment_variables()

    # 5. 중복 파일 확인
    check_duplicate_files()

    # 6. main.py import 확인
    check_main_import()

    # 7. 데이터베이스 연결 확인 (비동기)
    asyncio.run(check_database_connection())

    print("=" * 60)
    print("✅ 프로젝트 상태 확인 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()
