import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")

async def add_test_data():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.hireme
    
    # 테스트 이력서 데이터
    test_resumes = [
        {
            "user_id": "user1",
            "title": "프론트엔드 개발자 이력서",
            "content": "React, Vue.js, TypeScript 경험자",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "user_id": "user2", 
            "title": "백엔드 개발자 이력서",
            "content": "Python, FastAPI, MongoDB 경험자",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "user_id": "user3",
            "title": "풀스택 개발자 이력서", 
            "content": "JavaScript, Node.js, React, Python 경험자",
            "status": "approved",
            "created_at": datetime.now()
        }
    ]
    
    try:
        # 기존 데이터 삭제
        await db.resumes.delete_many({})
        print("기존 데이터 삭제 완료")
        
        # 새 테스트 데이터 추가
        result = await db.resumes.insert_many(test_resumes)
        print(f"테스트 데이터 {len(result.inserted_ids)}개 추가 완료")
        
        # 추가된 데이터 확인
        all_resumes = await db.resumes.find().to_list(1000)
        print(f"현재 총 {len(all_resumes)}개의 이력서가 있습니다:")
        
        for resume in all_resumes:
            print(f"- ID: {resume['_id']}, 제목: {resume['title']}, 상태: {resume['status']}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_test_data())
