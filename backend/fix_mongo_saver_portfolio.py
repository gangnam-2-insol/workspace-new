from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import random

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 포트폴리오 저장 테스트 ===')

# 지원자 정보 가져오기
applicants = list(db.applicants.find({}).limit(1))

if not applicants:
    print("지원자가 없습니다.")
    client.close()
    exit()

applicant = applicants[0]
applicant_id = applicant['_id']
name = applicant['name']
position = applicant['position']
skills = applicant['skills']

print(f"테스트 지원자: {name} ({position})")

# 포트폴리오 데이터 생성 (스키마 검증을 우회하는 간단한 형태)
portfolio_data = {
    "applicant_id": str(applicant_id),
    "application_id": f"app_{applicant_id}_{random.randint(1000, 9999)}",
    "extracted_text": f"{name}의 {position} 포트폴리오입니다. {', '.join(skills)}를 활용한 다양한 프로젝트를 수행했습니다.",
    "summary": f"{name}의 {position} 포트폴리오 - 웹 애플리케이션과 모바일 앱 개발 경험",
    "keywords": skills,
    "document_type": "portfolio",
    "basic_info": {
        "emails": [f"{name.lower().replace(' ', '')}@email.com"],
        "phones": [f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"],
        "names": [name],
        "urls": [f"https://portfolio.{name.lower().replace(' ', '')}.com"]
    },
    "file_metadata": {
        "filename": f"{name}_포트폴리오.pdf",
        "size": 2048000,
        "mime": "application/pdf",
        "hash": f"hash_{name}_portfolio_{random.randint(1000, 9999)}",
        "created_at": datetime.now(),
        "modified_at": datetime.now()
    },
    "items": [
        {
            "title": f"{name} - 웹 애플리케이션 프로젝트",
            "description": "사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선한 프로젝트입니다.",
            "tech_stack": skills[:3] if len(skills) >= 3 else skills,
            "role": f"{position} 개발 및 설계",
            "duration": "6개월",
            "team_size": 5,
            "achievements": [
                "사용자 만족도 20% 향상",
                "시스템 응답 속도 30% 개선",
                "코드 품질 향상으로 유지보수성 증대"
            ],
            "artifacts": [
                {
                    "kind": "file",
                    "filename": f"{name}_프로젝트A_스크린샷.png",
                    "mime": "image/png",
                    "size": 1024000,
                    "hash": f"hash_{name}_projectA_{random.randint(1000, 9999)}"
                }
            ]
        }
    ],
    "analysis_score": random.uniform(75, 95),
    "status": "active",
    "version": 1,
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}

try:
    # 포트폴리오 저장
    result = db.portfolios.insert_one(portfolio_data)
    print(f"✅ 포트폴리오 저장 성공: {result.inserted_id}")
    
    # 저장된 포트폴리오 확인
    saved_portfolio = db.portfolios.find_one({"_id": result.inserted_id})
    print(f"저장된 포트폴리오 제목: {saved_portfolio.get('summary', '제목 없음')}")
    
except Exception as e:
    print(f"❌ 포트폴리오 저장 실패: {e}")

# 전체 포트폴리오 수 확인
portfolio_count = db.portfolios.count_documents({})
print(f"전체 포트폴리오 수: {portfolio_count}")

client.close()
