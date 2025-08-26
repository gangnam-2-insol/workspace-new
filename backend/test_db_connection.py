#!/usr/bin/env python3
"""
MongoDB 연결 테스트 스크립트
DB(without yc).txt 구조와 일치하는지 확인
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def test_db_connection():
    """MongoDB 연결 및 구조 테스트"""
    try:
        # MongoDB 연결
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        print("🔍 MongoDB 연결 테스트 시작...")
        print(f"연결 URI: {mongo_uri}")

        # 서버 정보 확인
        server_info = await client.admin.command('serverStatus')
        print(f"✅ MongoDB 서버 연결 성공 (버전: {server_info.get('version', 'unknown')})")

        # 컬렉션 목록 확인
        collections = await db.list_collection_names()
        print(f"📚 현재 컬렉션: {collections}")

        # 각 컬렉션의 문서 수 확인
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count}개 문서")

        # 샘플 데이터 확인 (applicants 컬렉션)
        if 'applicants' in collections:
            sample_applicant = await db.applicants.find_one({})
            if sample_applicant:
                print(f"\n📋 샘플 지원자 데이터 구조:")
                print(f"  - ID: {sample_applicant.get('_id')}")
                print(f"  - 이름: {sample_applicant.get('name')}")
                print(f"  - 이메일: {sample_applicant.get('email')}")
                print(f"  - 직무: {sample_applicant.get('position')}")
                print(f"  - 상태: {sample_applicant.get('status')}")
                print(f"  - 랭킹: {sample_applicant.get('ranks', {})}")
                print(f"  - 생성일: {sample_applicant.get('created_at')}")
                print(f"  - 수정일: {sample_applicant.get('updated_at')}")

        client.close()
        print("\n✅ DB 연결 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. Docker Compose로 MongoDB 실행:")
        print("   docker-compose up -d mongodb")
        print("2. MongoDB 서비스 상태 확인:")
        print("   docker ps")
        print("3. 환경 변수 확인:")
        print("   MONGODB_URI=mongodb://localhost:27017/hireme")
        return False

if __name__ == "__main__":
    asyncio.run(test_db_connection())
