from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import random

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

# 지원자 정보 가져오기
applicants = list(db.applicants.find({}))

print(f'총 {len(applicants)}명의 지원자에 대한 문서를 생성합니다...')

# 각 지원자별 문서 생성
for applicant in applicants:
    applicant_id = applicant['_id']
    name = applicant['name']
    position = applicant['position']
    experience = applicant['experience']
    skills = applicant['skills']
    
    print(f'\n=== {name} ({position}) 문서 생성 중 ===')
    
    # 1. 이력서 생성
    resume_content = f"""
# {name} - {position} 이력서

## 개인정보
- 이름: {name}
- 직무: {position}
- 경력: {experience}
- 연락처: {name.lower().replace(' ', '')}@email.com
- 전화번호: 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}

## 자기소개
{experience}년간 {position} 분야에서 다양한 프로젝트를 수행하며 사용자 중심의 솔루션을 개발해왔습니다. 
{', '.join(skills[:3])} 등 최신 기술 스택을 활용하여 효율적이고 확장 가능한 시스템을 구축하는 것을 전문으로 합니다.

## 기술 스택
{', '.join(skills)}

## 경력사항
### 최근 회사 (2022-현재)
- {position} 개발 및 유지보수
- 팀 프로젝트 리드 및 멘토링
- 성능 최적화 및 코드 리팩토링

### 이전 회사 (2020-2022)
- {position} 관련 기능 개발
- API 설계 및 구현
- 데이터베이스 설계 및 최적화

## 프로젝트 경험
### 프로젝트 A (2023)
- 기술: {', '.join(skills[:3])}
- 역할: {position} 개발
- 성과: 사용자 만족도 20% 향상

### 프로젝트 B (2022)
- 기술: {', '.join(skills[1:4])}
- 역할: {position} 담당
- 성과: 시스템 성능 30% 개선

## 교육사항
- 컴퓨터공학 학사 (2015-2019)
- 관련 자격증 보유

## 언어능력
- 한국어: 모국어
- 영어: 비즈니스 회화 가능
"""

    # 2. 자소서 생성
    cover_letter_content = f"""
# {name} 자기소개서

## 지원동기
{position} 분야에서 {experience}년간 다양한 프로젝트를 수행하며 사용자 중심의 솔루션을 개발해왔습니다. 
귀사의 혁신적인 기술과 사용자 경험에 대한 접근 방식에 깊이 공감하여 지원하게 되었습니다.

## 성장 과정
### 기술적 성장
{', '.join(skills)} 등 다양한 기술 스택을 습득하며 지속적으로 성장해왔습니다. 
특히 {skills[0] if skills else '주요 기술'}에 대한 깊은 이해를 바탕으로 효율적이고 확장 가능한 시스템을 구축하는 것을 전문으로 합니다.

### 프로젝트 경험
다양한 규모의 프로젝트를 통해 팀워크와 커뮤니케이션 능력을 기를 수 있었습니다. 
최근에는 {position} 관련 프로젝트에서 리드 역할을 수행하며 팀원들의 성장을 돕고 있습니다.

## 귀사에 기여할 수 있는 부분
1. **기술적 전문성**: {experience}년간 축적한 {position} 분야의 전문 지식
2. **문제 해결 능력**: 다양한 프로젝트를 통해 기른 분석적 사고와 해결 능력
3. **팀워크**: 협업을 통한 시너지 창출 경험
4. **지속적 학습**: 새로운 기술에 대한 빠른 적응력과 학습 의지

## 향후 계획
귀사에서 {position} 전문가로서 더욱 성장하고, 팀과 회사의 발전에 기여하고 싶습니다. 
지속적인 학습과 혁신을 통해 사용자에게 더 나은 가치를 제공하는 개발자가 되겠습니다.

## 마무리
귀사의 비전과 가치에 공감하며, 함께 성장할 수 있는 기회를 주시면 최선을 다해 기여하겠습니다.
감사합니다.

{name} 드림
"""

    # 3. 포트폴리오 생성
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

    # MongoDB에 문서 저장
    try:
        # 이력서 저장
        resume_doc = {
            "applicant_id": applicant_id,
            "content": resume_content,
            "title": f"{name} - {position} 이력서",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "file_type": "resume",
            "file_name": f"{name}_이력서.txt"
        }
        db.resumes.insert_one(resume_doc)
        print(f"✅ 이력서 생성 완료")

        # 자소서 저장
        cover_letter_doc = {
            "applicant_id": applicant_id,
            "content": cover_letter_content,
            "title": f"{name} 자기소개서",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "file_type": "cover_letter",
            "file_name": f"{name}_자기소개서.txt"
        }
        db.cover_letters.insert_one(cover_letter_doc)
        print(f"✅ 자소서 생성 완료")

        # 포트폴리오 저장
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
        print(f"❌ {name} 문서 생성 실패: {str(e)}")

# 최종 결과 확인
print(f'\n=== 문서 생성 완료 ===')
final_resumes_count = db.resumes.count_documents({})
final_cover_letters_count = db.cover_letters.count_documents({})
final_portfolios_count = db.portfolios.count_documents({})

print(f'이력서: {final_resumes_count}개')
print(f'자소서: {final_cover_letters_count}개')
print(f'포트폴리오: {final_portfolios_count}개')

client.close()
