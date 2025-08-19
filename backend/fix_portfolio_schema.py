from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import random

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 포트폴리오 문서 생성 (스키마 수정) ===')

# 지원자 정보 가져오기
applicants = list(db.applicants.find({}))

print(f'총 {len(applicants)}명의 지원자에 대한 포트폴리오를 생성합니다...')

# 각 지원자별 포트폴리오 생성
for applicant in applicants:
    applicant_id = applicant['_id']
    name = applicant['name']
    position = applicant['position']
    experience = applicant['experience']
    skills = applicant['skills']
    
    print(f'\n=== {name} ({position}) 포트폴리오 생성 중 ===')
    
    # application_id 생성 (샘플용)
    application_id = ObjectId()
    
    # 포트폴리오 내용 생성
    portfolio_content = f"""
# {name} 포트폴리오

## 프로필
- 이름: {name}
- 직무: {position}
- 경력: {experience}
- 기술 스택: {', '.join(skills)}

## 주요 프로젝트

### 1. 프로젝트 A - 웹 애플리케이션 (2023)
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

**기술적 도전과 해결**
- 대용량 데이터 처리 최적화
- 반응형 디자인 구현
- 보안 강화 및 인증 시스템 구축

### 2. 프로젝트 B - 모바일 앱 (2022)
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

### 3. 프로젝트 C - 데이터 분석 시스템 (2021)
**기술 스택**: {', '.join(skills[2:5]) if len(skills) >= 5 else ', '.join(skills)}
**역할**: {position} 개발
**기간**: 8개월
**팀 규모**: 7명

**프로젝트 개요**
대용량 데이터를 실시간으로 분석하고 시각화하는 시스템을 구축했습니다.

**주요 성과**
- 데이터 처리 속도 50% 향상
- 실시간 대시보드 구축
- 비즈니스 인사이트 제공으로 의사결정 지원

## 기술적 역량

### 프로그래밍 언어
{', '.join(skills)}

### 개발 도구
- Git, Docker, Jenkins
- VS Code, IntelliJ IDEA
- Postman, Swagger

### 데이터베이스
- MySQL, PostgreSQL, MongoDB
- Redis, Elasticsearch

### 클라우드 플랫폼
- AWS, Azure, GCP
- Kubernetes, Docker

## 수상 및 자격
- 우수 개발자상 (2023)
- 관련 기술 자격증 보유
- 기술 컨퍼런스 발표 경험

## 연락처
- 이메일: {name.lower().replace(' ', '')}@email.com
- 전화: 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}
- GitHub: github.com/{name.lower().replace(' ', '')}
- LinkedIn: linkedin.com/in/{name.lower().replace(' ', '')}
"""

    # MongoDB에 포트폴리오 저장 (간단한 스키마)
    try:
        portfolio_doc = {
            "applicant_id": applicant_id,
            "content": portfolio_content,
            "title": f"{name} 포트폴리오",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "file_type": "portfolio",
            "file_name": f"{name}_포트폴리오.txt"
        }
        db.portfolios.insert_one(portfolio_doc)
        print(f"✅ 포트폴리오 생성 완료")

    except Exception as e:
        print(f"❌ {name} 포트폴리오 생성 실패: {str(e)}")

# 최종 결과 확인
print(f'\n=== 포트폴리오 생성 완료 ===')
final_portfolios_count = db.portfolios.count_documents({})
print(f'포트폴리오: {final_portfolios_count}개')

client.close()
