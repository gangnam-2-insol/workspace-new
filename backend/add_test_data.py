import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def add_test_data():
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        # 기존 데이터 확인
        count = await db.resumes.count_documents({})
        print(f'현재 resumes 컬렉션에 {count}개의 문서가 있습니다')
        
        # 추가 테스트 데이터
        additional_data = [
            {
                'name': '최수진',
                'position': '데이터 사이언티스트',
                'department': 'AI팀',
                'experience': '3-5년',
                'skills': ['Python', 'TensorFlow', 'Pandas', 'SQL'],
                'growthBackground': 5,
                'motivation': 4,
                'careerHistory': 4,
                'analysisScore': 88,
                'analysisResult': '머신러닝과 데이터 분석에 대한 깊은 이해를 보여주며, 실무 프로젝트 경험이 풍부합니다.',
                'status': 'approved',
                'created_at': datetime.now()
            },
            {
                'name': '정현우',
                'position': 'DevOps 엔지니어',
                'department': '인프라팀',
                'experience': '5-10년',
                'skills': ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Jenkins'],
                'growthBackground': 5,
                'motivation': 5,
                'careerHistory': 5,
                'analysisScore': 95,
                'analysisResult': '클라우드 인프라와 CI/CD 파이프라인 구축 경험이 뛰어나며, 팀 리딩 능력도 우수합니다.',
                'status': 'approved',
                'created_at': datetime.now()
            },
            {
                'name': '한소영',
                'position': 'UX/UI 디자이너',
                'department': '디자인팀',
                'experience': '1-3년',
                'skills': ['Figma', 'Adobe XD', 'Sketch', '프로토타이핑'],
                'growthBackground': 4,
                'motivation': 4,
                'careerHistory': 3,
                'analysisScore': 78,
                'analysisResult': '사용자 중심의 디자인 사고를 가지고 있으며, 프로토타이핑 도구 활용 능력이 좋습니다.',
                'status': 'pending',
                'created_at': datetime.now()
            },
            {
                'name': '송민호',
                'position': '보안 엔지니어',
                'department': '보안팀',
                'experience': '3-5년',
                'skills': ['네트워크 보안', '침입 탐지', '보안 정책', '취약점 분석'],
                'growthBackground': 4,
                'motivation': 4,
                'careerHistory': 4,
                'analysisScore': 82,
                'analysisResult': '보안 인프라 구축과 모니터링 시스템 운영 경험이 있으며, 보안 사고 대응 능력이 우수합니다.',
                'status': 'pending',
                'created_at': datetime.now()
            }
        ]
        
        # 데이터 추가
        for data in additional_data:
            result = await db.resumes.insert_one(data)
            print(f'테스트 데이터 추가됨: {data["name"]} - ID: {result.inserted_id}')
        
        # 최종 문서 수 확인
        final_count = await db.resumes.count_documents({})
        print(f'\n최종 resumes 컬렉션에 {final_count}개의 문서가 있습니다')
        
        client.close()
        
    except Exception as e:
        print(f'오류 발생: {e}')

if __name__ == "__main__":
    asyncio.run(add_test_data())
