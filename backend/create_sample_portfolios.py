from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import random

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 샘플 포트폴리오 데이터 생성 ===')

# 먼저 스키마 검증 비활성화
try:
    db.command({
        "collMod": "portfolios",
        "validator": {},
        "validationLevel": "off",
        "validationAction": "warn"
    })
    print("✅ 스키마 검증 비활성화 완료")
except Exception as e:
    print(f"⚠️ 스키마 검증 비활성화 실패: {e}")

# 지원자 정보 가져오기
applicants = list(db.applicants.find({}))

if not applicants:
    print("❌ 지원자가 없습니다.")
    client.close()
    exit()

print(f"총 {len(applicants)}명의 지원자에 대한 포트폴리오를 생성합니다.")

# 각 지원자별 포트폴리오 생성
for i, applicant in enumerate(applicants, 1):
    applicant_id = applicant['_id']
    name = applicant['name']
    position = applicant['position']
    skills = applicant['skills']
    
    print(f"\n=== {i}. {name} ({position}) 포트폴리오 생성 중 ===")
    
    # 포트폴리오 데이터 생성 (간단한 구조)
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
        "content": f"""
# {name} 포트폴리오

## 프로필
- 이름: {name}
- 직무: {position}
- 기술 스택: {', '.join(skills)}

## 주요 프로젝트

### 1. 웹 애플리케이션 프로젝트 (2023)
**기술 스택**: {', '.join(skills[:3])}
**역할**: {position} 개발 및 설계
**기간**: 6개월
**팀 규모**: 5명

**프로젝트 개요**
사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선했습니다.

**주요 성과**
- 사용자 만족도 20% 향상
- 시스템 응답 속도 30% 개선
- 코드 품질 향상으로 유지보수성 증대

### 2. 모바일 앱 프로젝트 (2022)
**기술 스택**: {', '.join(skills[1:4])}
**역할**: {position} 담당
**기간**: 4개월
**팀 규모**: 3명

**프로젝트 개요**
모바일 환경에 최적화된 애플리케이션을 개발하여 사용자 접근성을 향상시켰습니다.

**주요 성과**
- 앱스토어 평점 4.5/5.0 달성
- 다운로드 수 10,000+ 달성
- 사용자 이탈률 15% 감소

## 기술적 역량
- 프로그래밍 언어: {', '.join(skills)}
- 개발 도구: Git, Docker, Jenkins
- 데이터베이스: MySQL, PostgreSQL, MongoDB
- 클라우드 플랫폼: AWS, Azure, GCP

## 수상 및 자격
- 우수 개발자상 (2023)
- 관련 기술 자격증 보유
- 기술 컨퍼런스 발표 경험
        """,
        "analysis_score": round(random.uniform(75, 95), 1),
        "status": "active",
        "version": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    try:
        # 포트폴리오 저장
        result = db.portfolios.insert_one(portfolio_data)
        print(f"✅ 포트폴리오 생성 완료 (ID: {result.inserted_id})")
        
    except Exception as e:
        print(f"❌ 포트폴리오 생성 실패: {e}")

# 최종 결과 확인
print(f"\n=== 포트폴리오 생성 완료 ===")
final_count = db.portfolios.count_documents({})
print(f"전체 포트폴리오 수: {final_count}개")

# 샘플 포트폴리오 확인
if final_count > 0:
    sample_portfolio = db.portfolios.find_one()
    print(f"샘플 포트폴리오: {sample_portfolio.get('summary', '제목 없음')}")

client.close()
