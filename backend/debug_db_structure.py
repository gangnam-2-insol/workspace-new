#!/usr/bin/env python3
"""
DB 구조 디버그 스크립트
현재 DB에 저장된 실제 필드 구조를 확인
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_db_structure():
    """DB 구조 디버그"""
    try:
        # MongoDB 연결
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        print("🔍 DB 구조 디버그 시작...")
        print(f"연결 URI: {mongo_uri}")

        # 1. 지원자 컬렉션 구조 확인
        print("\n📋 지원자 컬렉션 구조:")
        sample_applicant = await db.applicants.find_one({})
        if sample_applicant:
            print("✅ 지원자 샘플 데이터 발견")
            print(f"전체 필드 목록: {list(sample_applicant.keys())}")
            
            # 주요 필드들 확인
            key_fields = ['_id', 'name', 'email', 'phone', 'position', 'status', 'job_posting_id', 'created_at', 'updated_at']
            for field in key_fields:
                if field in sample_applicant:
                    value = sample_applicant[field]
                    print(f"  - {field}: {type(value).__name__} = {value}")
                else:
                    print(f"  - {field}: ❌ 없음")
            
            # personal_info 필드 확인
            if 'personal_info' in sample_applicant:
                personal_info = sample_applicant['personal_info']
                print(f"  - personal_info: {type(personal_info).__name__} = {personal_info}")
                if isinstance(personal_info, dict):
                    print(f"    personal_info 필드들: {list(personal_info.keys())}")
            else:
                print("  - personal_info: ❌ 없음")
        else:
            print("❌ 지원자 데이터 없음")

        # 2. 채용공고 컬렉션 구조 확인
        print("\n📋 채용공고 컬렉션 구조:")
        sample_job = await db.job_postings.find_one({})
        if sample_job:
            print("✅ 채용공고 샘플 데이터 발견")
            print(f"전체 필드 목록: {list(sample_job.keys())}")
            
            key_fields = ['_id', 'title', 'company', 'position', 'status', 'created_at', 'updated_at']
            for field in key_fields:
                if field in sample_job:
                    value = sample_job[field]
                    print(f"  - {field}: {type(value).__name__} = {value}")
                else:
                    print(f"  - {field}: ❌ 없음")
        else:
            print("❌ 채용공고 데이터 없음")

        # 3. 자소서 컬렉션 구조 확인
        print("\n📋 자소서 컬렉션 구조:")
        sample_cover = await db.cover_letters.find_one({})
        if sample_cover:
            print("✅ 자소서 샘플 데이터 발견")
            print(f"전체 필드 목록: {list(sample_cover.keys())}")
            
            key_fields = ['_id', 'applicant_id', 'content', 'extracted_text', 'created_at', 'updated_at']
            for field in key_fields:
                if field in sample_cover:
                    value = sample_cover[field]
                    print(f"  - {field}: {type(value).__name__} = {value}")
                else:
                    print(f"  - {field}: ❌ 없음")
        else:
            print("❌ 자소서 데이터 없음")

        # 4. 컬렉션별 문서 수 확인
        print("\n📊 컬렉션별 문서 수:")
        collections = ['applicants', 'job_postings', 'cover_letters', 'resumes', 'portfolios']
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count}개")

        client.close()
        print("\n✅ DB 구조 디버그 완료!")

    except Exception as e:
        print(f"❌ DB 구조 디버그 실패: {e}")

if __name__ == "__main__":
    asyncio.run(debug_db_structure())
