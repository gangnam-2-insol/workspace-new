from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime
from bson import ObjectId
import os

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")

async def insert_test_data():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.hireme
    
    # 기존 데이터 삭제
    await db.resumes.delete_many({})
    print("기존 데이터를 삭제했습니다.")
    
    # 테스트 데이터
    test_applicants = [
        {
            "resume_id": ObjectId(),
            "name": "김민수",
            "position": "프론트엔드",
            "department": "개발",
            "experience": "3-5년",
            "skills": "React, JavaScript, TypeScript, CSS",
            "growthBackground": "4",
            "motivation": "4",
            "careerHistory": "4",
            "analysisScore": 85,
            "analysisResult": "우수한 프론트엔드 개발자로 React와 TypeScript에 대한 깊은 이해를 보여줍니다.",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "이지혜",
            "position": "백엔드",
            "department": "개발",
            "experience": "1-3년",
            "skills": "Python, Django, PostgreSQL, Redis",
            "growthBackground": "3",
            "motivation": "4",
            "careerHistory": "3",
            "analysisScore": 75,
            "analysisResult": "Python과 Django에 대한 실무 경험이 있는 백엔드 개발자입니다.",
            "status": "approved",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "박준영",
            "position": "풀스택",
            "department": "개발",
            "experience": "5-10년",
            "skills": "Java, Spring, React, MySQL, Docker",
            "growthBackground": "5",
            "motivation": "5",
            "careerHistory": "5",
            "analysisScore": 92,
            "analysisResult": "풀스택 개발 경험이 풍부하고 팀 리딩 경험도 있는 시니어 개발자입니다.",
            "status": "approved",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "최유진",
            "position": "데이터 분석가",
            "department": "데이터",
            "experience": "1-3년",
            "skills": "Python, Pandas, SQL, Tableau, R",
            "growthBackground": "3",
            "motivation": "4",
            "careerHistory": "2",
            "analysisScore": 68,
            "analysisResult": "데이터 분석 도구에 대한 기본기가 탄탄한 주니어 분석가입니다.",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "정태현",
            "position": "DevOps 엔지니어",
            "department": "인프라",
            "experience": "3-5년",
            "skills": "AWS, Kubernetes, Docker, Jenkins, Terraform",
            "growthBackground": "4",
            "motivation": "3",
            "careerHistory": "4",
            "analysisScore": 80,
            "analysisResult": "클라우드 인프라와 CI/CD에 대한 실무 경험이 풍부합니다.",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "한소영",
            "position": "UI/UX 디자이너",
            "department": "디자인",
            "experience": "1-3년",
            "skills": "Figma, Adobe XD, Sketch, Photoshop, Illustrator",
            "growthBackground": "3",
            "motivation": "5",
            "careerHistory": "2",
            "analysisScore": 72,
            "analysisResult": "사용자 경험에 대한 이해가 높고 디자인 도구 활용 능력이 우수합니다.",
            "status": "rejected",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "서동훈",
            "position": "백엔드",
            "department": "개발",
            "experience": "신입",
            "skills": "Node.js, Express, MongoDB, JavaScript",
            "growthBackground": "2",
            "motivation": "4",
            "careerHistory": "1",
            "analysisScore": 55,
            "analysisResult": "기본기는 있으나 실무 경험이 부족합니다. 성장 가능성은 높습니다.",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "윤아린",
            "position": "프론트엔드",
            "department": "개발",
            "experience": "1-3년",
            "skills": "Vue.js, JavaScript, HTML, CSS, Vuex",
            "growthBackground": "3",
            "motivation": "3",
            "careerHistory": "3",
            "analysisScore": 70,
            "analysisResult": "Vue.js 프레임워크에 대한 이해도가 높고 실무 적응력이 좋습니다.",
            "status": "approved",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "강민호",
            "position": "프로덕트 매니저",
            "department": "기획",
            "experience": "3-5년",
            "skills": "기획, 데이터 분석, SQL, Jira, Confluence",
            "growthBackground": "4",
            "motivation": "4",
            "careerHistory": "4",
            "analysisScore": 78,
            "analysisResult": "제품 기획과 데이터 기반 의사결정 경험이 풍부합니다.",
            "status": "pending",
            "created_at": datetime.now()
        },
        {
            "resume_id": ObjectId(),
            "name": "박주랑",
            "position": "백엔드",
            "department": "개발",
            "experience": "1-3년",
            "skills": "Java, Spring Boot, MySQL, Redis, JPA",
            "growthBackground": "2",
            "motivation": "2",
            "careerHistory": "3",
            "analysisScore": 65,
            "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 있습니다.",
            "status": "pending",
            "created_at": datetime.now()
        }
    ]
    
    # 데이터 삽입
    result = await db.resumes.insert_many(test_applicants)
    print(f"{len(result.inserted_ids)}명의 지원자 데이터가 성공적으로 삽입되었습니다.")
    
    # 삽입된 데이터 확인
    count = await db.resumes.count_documents({})
    print(f"현재 DB에 총 {count}명의 지원자가 있습니다.")
    
    # 몇 개 샘플 데이터 출력
    sample_data = await db.resumes.find().limit(3).to_list(3)
    print("\n샘플 데이터:")
    for applicant in sample_data:
        print(f"- {applicant['name']} ({applicant['position']}) - {applicant['status']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(insert_test_data())