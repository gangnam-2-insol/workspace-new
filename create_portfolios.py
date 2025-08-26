import asyncio
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from faker import Faker

fake = Faker(['ko_KR'])

async def create_portfolios():
    """포트폴리오 데이터 생성"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        print("📁 포트폴리오 데이터 생성 시작...")

        # 포트폴리오 ID가 있는 지원자들 찾기
        applicants_with_portfolio_id = await db.applicants.find({
            "portfolio_id": {"$exists": True, "$ne": None}
        }).to_list(length=None)

        print(f"포트폴리오 ID가 있는 지원자: {len(applicants_with_portfolio_id)}명")

        # 포트폴리오 생성
        portfolios = []
        for i, applicant in enumerate(applicants_with_portfolio_id):
            try:
                # ObjectId로 변환
                portfolio_id = ObjectId(applicant['portfolio_id'])

                portfolio = {
                    "_id": portfolio_id,
                    "applicant_id": applicant["_id"],
                    "title": f"{applicant['name']}의 포트폴리오",
                    "description": generate_portfolio_description(applicant),
                    "projects": generate_projects(applicant),
                    "skills": applicant.get('skills', '').split(', '),
                    "github_url": applicant.get('github_url'),
                    "linkedin_url": applicant.get('linkedin_url'),
                    "portfolio_url": applicant.get('portfolio_url'),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                portfolios.append(portfolio)

                if (i + 1) % 10 == 0:
                    print(f"  {i+1}/{len(applicants_with_portfolio_id)} 포트폴리오 생성 완료")

            except Exception as e:
                print(f"  ❌ {applicant['name']} 포트폴리오 생성 실패: {e}")

        # 포트폴리오 DB에 삽입
        if portfolios:
            await db.portfolios.insert_many(portfolios)
            print(f"✅ {len(portfolios)}개의 포트폴리오 생성 완료")

        # 최종 현황 확인
        total_applicants = await db.applicants.count_documents({})
        applicants_with_portfolio = await db.applicants.count_documents({"portfolio_id": {"$exists": True, "$ne": None}})
        total_portfolios = await db.portfolios.count_documents({})

        print(f"\n📁 최종 포트폴리오 현황:")
        print(f"   전체 지원자 수: {total_applicants}명")
        print(f"   포트폴리오가 있는 지원자 수: {applicants_with_portfolio}명")
        print(f"   포트폴리오 컬렉션 문서 수: {total_portfolios}개")
        print(f"   포트폴리오 보유율: {applicants_with_portfolio/total_applicants*100:.1f}%")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

def generate_portfolio_description(applicant):
    """포트폴리오 설명 생성"""
    name = applicant['name']
    position = applicant.get('position', '개발자')
    experience = applicant.get('experience', '신입')

    descriptions = [
        f"{name}의 {position} 포트폴리오입니다. {experience} 경력을 바탕으로 다양한 프로젝트를 진행했습니다.",
        f"{position} 분야에서 {experience} 경력을 쌓아온 {name}의 포트폴리오입니다.",
        f"{name}의 {position} 역량을 보여주는 포트폴리오입니다. {experience} 경력을 통해 다양한 기술과 경험을 쌓았습니다."
    ]

    return random.choice(descriptions)

def generate_projects(applicant):
    """프로젝트 목록 생성"""
    position = applicant.get('position', '개발자')
    name = applicant['name']

    # 직무별 프로젝트 템플릿
    project_templates = {
        "UI/UX 디자이너": [
            {
                "name": f"{name}의 웹사이트 리디자인",
                "description": "기존 웹사이트의 사용자 경험을 개선하는 리디자인 프로젝트",
                "technologies": ["Figma", "Adobe XD", "Photoshop", "Illustrator"],
                "duration": "3개월",
                "url": f"https://behance.net/{fake.user_name()}/web-redesign"
            },
            {
                "name": f"{name}의 모바일 앱 디자인",
                "description": "사용자 중심의 모바일 앱 UI/UX 디자인 프로젝트",
                "technologies": ["Figma", "Sketch", "Principle", "InVision"],
                "duration": "4개월",
                "url": f"https://dribbble.com/{fake.user_name()}/mobile-app"
            }
        ],
        "프론트엔드 개발자": [
            {
                "name": f"{name}의 React 웹 애플리케이션",
                "description": "React와 TypeScript를 활용한 현대적인 웹 애플리케이션",
                "technologies": ["React", "TypeScript", "Tailwind CSS", "Vite"],
                "duration": "2개월",
                "url": f"https://github.com/{fake.user_name()}/react-app"
            },
            {
                "name": f"{name}의 Vue.js 프로젝트",
                "description": "Vue.js와 Vuex를 활용한 상태 관리가 포함된 웹 애플리케이션",
                "technologies": ["Vue.js", "Vuex", "Vue Router", "Axios"],
                "duration": "3개월",
                "url": f"https://github.com/{fake.user_name()}/vue-project"
            }
        ],
        "백엔드 개발자": [
            {
                "name": f"{name}의 REST API 서버",
                "description": "Node.js와 Express를 활용한 RESTful API 서버 구축",
                "technologies": ["Node.js", "Express", "MongoDB", "JWT"],
                "duration": "2개월",
                "url": f"https://github.com/{fake.user_name()}/rest-api"
            },
            {
                "name": f"{name}의 Python 웹 서비스",
                "description": "Django를 활용한 풀스택 웹 서비스 개발",
                "technologies": ["Python", "Django", "PostgreSQL", "Docker"],
                "duration": "3개월",
                "url": f"https://github.com/{fake.user_name()}/django-service"
            }
        ]
    }

    # 기본 프로젝트 템플릿
    default_projects = [
        {
            "name": f"{name}의 개인 프로젝트",
            "description": f"{position} 역량을 보여주는 개인 프로젝트",
            "technologies": ["JavaScript", "HTML", "CSS"],
            "duration": "1개월",
            "url": f"https://github.com/{fake.user_name()}/personal-project"
        }
    ]

    return project_templates.get(position, default_projects)

if __name__ == "__main__":
    asyncio.run(create_portfolios())
