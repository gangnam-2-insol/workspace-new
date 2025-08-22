#!/usr/bin/env python3
"""
지원자 API 테스트 스크립트
"""

import asyncio
import pymongo
from bson import ObjectId

async def test_mongodb_connection():
    """MongoDB 연결 및 지원자 데이터 확인"""
    try:
        # MongoDB 연결
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["hireme"]
        
        print("🔗 MongoDB 연결 성공!")
        
        # 지원자 컬렉션 확인
        applicants_count = db.applicants.count_documents({})
        print(f"📊 지원자 수: {applicants_count}")
        
        # 지원자 데이터 샘플 확인
        applicants = list(db.applicants.find().limit(3))
        print(f"📋 지원자 샘플 데이터:")
        for i, applicant in enumerate(applicants):
            print(f"  {i+1}. {applicant.get('name', 'N/A')} - {applicant.get('email', 'N/A')}")
        
        # MongoService 테스트
        from services.mongo_service import MongoService
        
        mongo_service = MongoService("mongodb://localhost:27017")
        result = await mongo_service.get_applicants(skip=0, limit=5)
        
        print(f"✅ MongoService.get_applicants 결과:")
        print(f"  - 총 지원자 수: {result.get('total_count', 0)}")
        print(f"  - 반환된 지원자 수: {len(result.get('applicants', []))}")
        print(f"  - 응답 구조: {list(result.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
