import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def debug_applicant_structure():
    """지원자 데이터 구조 디버깅"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme
        
        print("=== 지원자 데이터 구조 디버깅 ===")
        
        # 첫 번째 지원자 가져오기
        first_applicant = await db.applicants.find_one({})
        
        if first_applicant:
            print("첫 번째 지원자 전체 구조:")
            print(json.dumps(first_applicant, indent=2, default=str))
            
            print("\n=== 필드별 상세 분석 ===")
            for key, value in first_applicant.items():
                if key == '_id':
                    print(f"{key}: {value} (타입: {type(value)})")
                elif isinstance(value, dict):
                    print(f"{key}: {type(value)} - 키들: {list(value.keys())}")
                elif isinstance(value, list):
                    print(f"{key}: {type(value)} - 길이: {len(value)}")
                else:
                    print(f"{key}: {value} (타입: {type(value)})")
        else:
            print("지원자 데이터가 없습니다.")
        
        client.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(debug_applicant_structure())

