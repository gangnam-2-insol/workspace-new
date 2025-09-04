#!/usr/bin/env python3
"""
자소서 lookup 디버깅 스크립트
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def debug_cover_letter_lookup():
    """자소서 lookup 디버깅"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme
        
        print("=== 자소서 lookup 디버깅 ===")
        
        # 첫 번째 지원자 확인
        applicant = await db.applicants.find_one({})
        if applicant:
            print(f"지원자: {applicant.get('name', 'N/A')}")
            print(f"지원자 _id: {applicant['_id']} (타입: {type(applicant['_id'])})")
            print(f"지원자 cover_letter_id: {applicant.get('cover_letter_id')} (타입: {type(applicant.get('cover_letter_id'))})")
            
            # cover_letter_id를 ObjectId로 변환
            cover_letter_id_str = applicant.get('cover_letter_id')
            if cover_letter_id_str:
                cover_letter_object_id = ObjectId(cover_letter_id_str)
                print(f"변환된 ObjectId: {cover_letter_object_id} (타입: {type(cover_letter_object_id)})")
                
                # 해당 자소서 직접 조회
                cover_letter = await db.cover_letters.find_one({"_id": cover_letter_object_id})
                if cover_letter:
                    print(f"자소서 _id: {cover_letter['_id']} (타입: {type(cover_letter['_id'])})")
                    print(f"자소서 applicant_id: {cover_letter.get('applicant_id')} (타입: {type(cover_letter.get('applicant_id'))})")
                    print(f"자소서 content 길이: {len(cover_letter.get('content', ''))}")
                else:
                    print("❌ 자소서를 찾을 수 없음")
        
        print("\n=== 수동 lookup 테스트 ===")
        
        # 수동으로 lookup 테스트
        test_result = await db.applicants.aggregate([
            {
                "$lookup": {
                    "from": "cover_letters",
                    "localField": "cover_letter_id",
                    "foreignField": "_id",
                    "as": "cover_letter"
                }
            },
            {
                "$project": {
                    "name": 1,
                    "cover_letter_id": 1,
                    "cover_letter_count": {"$size": "$cover_letter"},
                    "cover_letter_ids": "$cover_letter._id"
                }
            },
            {
                "$limit": 3
            }
        ]).to_list(3)
        
        for result in test_result:
            print(f"\n지원자: {result.get('name', 'N/A')}")
            print(f"  cover_letter_id: {result.get('cover_letter_id')}")
            print(f"  cover_letter_count: {result.get('cover_letter_count')}")
            print(f"  cover_letter_ids: {result.get('cover_letter_ids')}")
        
        print("\n=== ObjectId 변환 lookup 테스트 ===")
        
        # ObjectId 변환 후 lookup 테스트
        test_result2 = await db.applicants.aggregate([
            {
                "$addFields": {
                    "cover_letter_object_id": {
                        "$toObjectId": "$cover_letter_id"
                    }
                }
            },
            {
                "$lookup": {
                    "from": "cover_letters",
                    "localField": "cover_letter_object_id",
                    "foreignField": "_id",
                    "as": "cover_letter"
                }
            },
            {
                "$project": {
                    "name": 1,
                    "cover_letter_id": 1,
                    "cover_letter_object_id": 1,
                    "cover_letter_count": {"$size": "$cover_letter"}
                }
            },
            {
                "$limit": 3
            }
        ]).to_list(3)
        
        for result in test_result2:
            print(f"\n지원자: {result.get('name', 'N/A')}")
            print(f"  cover_letter_id: {result.get('cover_letter_id')}")
            print(f"  cover_letter_object_id: {result.get('cover_letter_object_id')}")
            print(f"  cover_letter_count: {result.get('cover_letter_count')}")
        
        client.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_cover_letter_lookup())
