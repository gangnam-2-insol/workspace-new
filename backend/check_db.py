import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db():
    try:
        # MongoDB 연결 (소문자 데이터베이스 이름 사용)
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        # resumes 컬렉션 문서 수 확인
        count = await db.resumes.count_documents({})
        print(f'resumes 컬렉션에 {count}개의 문서가 있습니다')
        
        if count > 0:
            # 첫 3개 문서 조회
            docs = await db.resumes.find().limit(3).to_list(3)
            print('\n첫 3개 문서:')
            for i, doc in enumerate(docs):
                print(f'\n--- 문서 {i+1} ---')
                for key, value in doc.items():
                    if key == '_id':
                        print(f'{key}: {str(value)}')
                    else:
                        print(f'{key}: {value}')
        else:
            print('데이터가 없습니다. 테스트 데이터를 생성해보겠습니다.')
            
            # 테스트 데이터 생성
            test_data = {
                'name': '김개발',
                'position': '프론트엔드 개발자',
                'department': '개발팀',
                'experience': 3,
                'skills': ['JavaScript', 'React', 'Node.js'],
                'ai_score': 85.5,
                'ai_analysis': 'JavaScript와 React 경험이 풍부하며, 팀 프로젝트 경험이 있습니다.',
                'status': '신규',
                'created_at': '2024-01-15T00:00:00Z',
                'updated_at': '2024-01-15T00:00:00Z'
            }
            
            result = await db.resumes.insert_one(test_data)
            print(f'테스트 데이터가 생성되었습니다. ID: {result.inserted_id}')
        
        client.close()
        
    except Exception as e:
        print(f'오류 발생: {e}')

if __name__ == "__main__":
    asyncio.run(check_db())
