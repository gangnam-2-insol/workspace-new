import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

# MongoDB 연결 설정
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Hireme")

async def init_database():
    """MongoDB에 초기 데이터 삽입"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        print("MongoDB에 연결되었습니다.")
        
        # 지원자 데이터 삽입
        applicants_data = [
            {
                "id": "1",
                "name": "김철수",
                "email": "kim.chulsoo@email.com",
                "phone": "010-1234-5678",
                "position": "프론트엔드 개발자",
                "experience": "3년",
                "education": "컴퓨터공학과 졸업",
                "status": "서류합격",
                "appliedDate": "2024-01-15",
                "aiScores": {
                    "resume": 85,
                    "coverLetter": 78,
                    "portfolio": 92
                },
                "aiSuitability": 87,
                "documents": {
                    "resume": {
                        "exists": True,
                        "summary": "React, TypeScript, Next.js 경험 풍부. 3년간 프론트엔드 개발 경력. 주요 프로젝트: 이커머스 플랫폼 구축, 관리자 대시보드 개발.",
                        "keywords": ["React", "TypeScript", "Next.js", "Redux", "Tailwind CSS"],
                        "content": "상세 이력서 내용..."
                    },
                    "portfolio": {
                        "exists": True,
                        "summary": "GitHub에 15개 이상의 프로젝트 포트폴리오 보유. 반응형 웹 디자인, PWA 개발 경험.",
                        "keywords": ["GitHub", "PWA", "반응형", "UI/UX"],
                        "content": "포트폴리오 상세 내용..."
                    },
                    "coverLetter": {
                        "exists": True,
                        "summary": "개발자로서의 성장 과정과 회사에 기여할 수 있는 역량을 명확하게 표현.",
                        "keywords": ["성장", "기여", "열정", "학습"],
                        "content": "자기소개서 상세 내용..."
                    }
                },
                "interview": {
                    "scheduled": True,
                    "date": "2024-01-25",
                    "time": "14:00",
                    "type": "대면",
                    "location": "회사 면접실",
                    "status": "예정"
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": "2",
                "name": "이영희",
                "email": "lee.younghee@email.com",
                "phone": "010-2345-6789",
                "position": "백엔드 개발자",
                "experience": "5년",
                "education": "소프트웨어공학과 졸업",
                "status": "보류",
                "appliedDate": "2024-01-14",
                "aiScores": {
                    "resume": 92,
                    "coverLetter": 85,
                    "portfolio": 88
                },
                "aiSuitability": 89,
                "documents": {
                    "resume": {
                        "exists": True,
                        "summary": "Java, Spring Boot, MySQL 경험 풍부. 5년간 백엔드 개발 경력. 마이크로서비스 아키텍처 설계 경험.",
                        "keywords": ["Java", "Spring Boot", "MySQL", "Microservices", "AWS"],
                        "content": "상세 이력서 내용..."
                    },
                    "portfolio": {
                        "exists": True,
                        "summary": "대용량 트래픽 처리 시스템 구축 경험. 성능 최적화 및 모니터링 시스템 구축.",
                        "keywords": ["성능최적화", "모니터링", "대용량처리", "시스템설계"],
                        "content": "포트폴리오 상세 내용..."
                    },
                    "coverLetter": {
                        "exists": True,
                        "summary": "시스템 아키텍처 설계 능력과 팀 리더십 경험을 강조.",
                        "keywords": ["아키텍처", "리더십", "시스템설계", "팀워크"],
                        "content": "자기소개서 상세 내용..."
                    }
                },
                "interview": {
                    "scheduled": False,
                    "date": None,
                    "time": None,
                    "type": None,
                    "location": None,
                    "status": "미정"
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": "3",
                "name": "박민수",
                "email": "park.minsu@email.com",
                "phone": "010-3456-7890",
                "position": "UI/UX 디자이너",
                "experience": "4년",
                "education": "디자인학과 졸업",
                "status": "서류불합격",
                "appliedDate": "2024-01-13",
                "aiScores": {
                    "resume": 65,
                    "coverLetter": 72,
                    "portfolio": 78
                },
                "aiSuitability": 71,
                "documents": {
                    "resume": {
                        "exists": True,
                        "summary": "Figma, Adobe XD 사용 경험. 4년간 UI/UX 디자인 경력. 모바일 앱 디자인 전문.",
                        "keywords": ["Figma", "Adobe XD", "UI/UX", "모바일앱", "디자인시스템"],
                        "content": "상세 이력서 내용..."
                    },
                    "portfolio": {
                        "exists": True,
                        "summary": "다양한 모바일 앱 디자인 프로젝트 경험. 사용자 리서치 및 프로토타이핑 경험.",
                        "keywords": ["모바일앱", "프로토타이핑", "사용자리서치", "디자인시스템"],
                        "content": "포트폴리오 상세 내용..."
                    },
                    "coverLetter": {
                        "exists": True,
                        "summary": "사용자 중심의 디자인 철학과 창의적인 문제 해결 능력을 강조.",
                        "keywords": ["사용자중심", "창의성", "문제해결", "디자인철학"],
                        "content": "자기소개서 상세 내용..."
                    }
                },
                "interview": {
                    "scheduled": False,
                    "date": None,
                    "time": None,
                    "type": None,
                    "location": None,
                    "status": "미정"
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        # 기존 데이터 삭제
        await db.applicants.delete_many({})
        print("기존 지원자 데이터를 삭제했습니다.")
        
        # 새 데이터 삽입
        result = await db.applicants.insert_many(applicants_data)
        print(f"✅ {len(result.inserted_ids)}명의 지원자 데이터를 성공적으로 삽입했습니다.")
        
        # 삽입된 데이터 확인
        count = await db.applicants.count_documents({})
        print(f"📊 현재 데이터베이스에 {count}명의 지원자가 있습니다.")
        
        # 샘플 데이터 조회
        sample = await db.applicants.find_one({})
        if sample:
            print(f"📋 샘플 데이터: {sample['name']} - {sample['position']}")
        
        client.close()
        print("MongoDB 연결을 종료했습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("MongoDB 서버가 실행 중인지 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(init_database())
