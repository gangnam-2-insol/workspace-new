#!/usr/bin/env python3
"""
자소서 데이터 확인 스크립트
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_cover_letter_data():
    """자소서 데이터 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme
        
        print("=== 자소서 데이터 확인 ===")
        
        # 지원자 수 확인
        applicants_count = await db.applicants.count_documents({})
        print(f"총 지원자 수: {applicants_count}")
        
        # 자소서 수 확인
        cover_letters_count = await db.cover_letters.count_documents({})
        print(f"총 자소서 수: {cover_letters_count}")
        
        # cover_letter_id가 있는 지원자 수 확인
        applicants_with_cover_letter = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})
        print(f"cover_letter_id가 있는 지원자 수: {applicants_with_cover_letter}")
        
        # 샘플 지원자 데이터 확인
        print("\n=== 샘플 지원자 데이터 ===")
        sample_applicants = await db.applicants.find({}).limit(3).to_list(3)
        for i, applicant in enumerate(sample_applicants):
            print(f"\n지원자 {i+1}:")
            print(f"  이름: {applicant.get('name', 'N/A')}")
            print(f"  이메일: {applicant.get('email', 'N/A')}")
            print(f"  cover_letter_id: {applicant.get('cover_letter_id', 'N/A')}")
            print(f"  growthBackground: {applicant.get('growthBackground', 'N/A')[:50]}...")
            print(f"  motivation: {applicant.get('motivation', 'N/A')[:50]}...")
        
        # 샘플 자소서 데이터 확인
        print("\n=== 샘플 자소서 데이터 ===")
        sample_cover_letters = await db.cover_letters.find({}).limit(3).to_list(3)
        for i, cover_letter in enumerate(sample_cover_letters):
            print(f"\n자소서 {i+1}:")
            print(f"  ID: {cover_letter.get('_id', 'N/A')}")
            print(f"  applicant_id: {cover_letter.get('applicant_id', 'N/A')}")
            print(f"  content 길이: {len(cover_letter.get('content', ''))}")
            print(f"  content 미리보기: {cover_letter.get('content', 'N/A')[:100]}...")
        
        # 자소서 분석 가능한 지원자 확인
        print("\n=== 자소서 분석 가능한 지원자 ===")
        analyzable_applicants = await db.applicants.aggregate([
            {
                "$lookup": {
                    "from": "cover_letters",
                    "localField": "cover_letter_id",
                    "foreignField": "_id",
                    "as": "cover_letter"
                }
            },
            {
                "$match": {
                    "cover_letter": {"$ne": []}
                }
            },
            {
                "$project": {
                    "name": 1,
                    "email": 1,
                    "cover_letter_id": 1,
                    "cover_letter_count": {"$size": "$cover_letter"}
                }
            }
        ]).to_list(10)
        
        print(f"자소서 분석 가능한 지원자 수: {len(analyzable_applicants)}")
        for applicant in analyzable_applicants[:3]:
            print(f"  - {applicant.get('name', 'N/A')} ({applicant.get('email', 'N/A')})")
        
        client.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_cover_letter_data())
