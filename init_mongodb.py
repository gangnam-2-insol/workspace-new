#!/usr/bin/env python3
"""
MongoDB 초기화 스크립트
"""

import pymongo
from datetime import datetime
import json

def init_mongodb():
    """MongoDB 데이터베이스 초기화"""
    
    # MongoDB 연결
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["hireme"]
    
    print("🔗 MongoDB 연결 성공!")
    
    # 기존 컬렉션 삭제 (초기화)
    collections_to_drop = ['users', 'applicants', 'resumes', 'interviews', 'cover_letters', 'portfolios', 'job_postings']
    for collection_name in collections_to_drop:
        if collection_name in db.list_collection_names():
            db[collection_name].drop()
            print(f"🗑️ {collection_name} 컬렉션 삭제 완료")
    
    # 사용자 컬렉션 생성 및 샘플 데이터
    print("👥 사용자 컬렉션 생성 중...")
    users_collection = db.create_collection('users')
    users_data = [
        {
            "username": "admin",
            "email": "admin@hireme.com",
            "role": "admin",
            "created_at": datetime.now()
        },
        {
            "username": "user1",
            "email": "user1@example.com",
            "role": "user",
            "created_at": datetime.now()
        },
        {
            "username": "user2", 
            "email": "user2@example.com",
            "role": "user",
            "created_at": datetime.now()
        }
    ]
    users_collection.insert_many(users_data)
    print(f"✅ 사용자 {len(users_data)}명 추가 완료")
    
    # 지원자 컬렉션 생성 및 샘플 데이터
    print("👤 지원자 컬렉션 생성 중...")
    applicants_collection = db.create_collection('applicants')
    applicants_data = [
        {
            "name": "김철수",
            "email": "kim.chulsoo@email.com",
            "phone": "010-1234-5678",
            "position": "프론트엔드 개발자",
            "experience": 3,
            "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "이영희",
            "email": "lee.younghee@email.com",
            "phone": "010-2345-6789",
            "position": "백엔드 개발자",
            "experience": 5,
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "name": "박민수",
            "email": "park.minsu@email.com",
            "phone": "010-3456-7890",
            "position": "UI/UX 디자이너",
            "experience": 4,
            "skills": ["Figma", "Adobe XD", "Photoshop", "Illustrator", "Sketch"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "정수진",
            "email": "jung.sujin@email.com",
            "phone": "010-4567-8901",
            "position": "데이터 분석가",
            "experience": 2,
            "skills": ["Python", "R", "SQL", "Tableau", "Power BI", "Pandas", "NumPy"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "최동현",
            "email": "choi.donghyun@email.com",
            "phone": "010-5678-9012",
            "position": "DevOps 엔지니어",
            "experience": 6,
            "skills": ["AWS", "Docker", "Kubernetes", "Jenkins", "Terraform", "Linux", "Shell Script"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    # 지원자 데이터 삽입 및 ObjectId 저장
    applicant_results = applicants_collection.insert_many(applicants_data)
    applicant_ids = applicant_results.inserted_ids
    print(f"✅ 지원자 {len(applicants_data)}명 추가 완료")
    
    # 지원자 ID 매핑 (이름으로 찾기 쉽게)
    applicant_id_map = {}
    for i, applicant in enumerate(applicants_data):
        applicant_id_map[applicant["name"]] = str(applicant_ids[i])
    
    # 이력서 컬렉션 생성 및 샘플 데이터
    print("📄 이력서 컬렉션 생성 중...")
    resumes_collection = db.create_collection('resumes')
    
    resumes_data = [
        {
            "applicant_id": applicant_id_map["김철수"],
            "extracted_text": "김철수\n프론트엔드 개발자\n연락처: 010-1234-5678\n이메일: kim.chulsoo@email.com\n\n학력\n- 서울대학교 컴퓨터공학과 졸업\n\n경력\n- ABC 회사 프론트엔드 개발자 (2021-2023)\n- XYZ 스타트업 풀스택 개발자 (2023-현재)\n\n기술스택\n- React, TypeScript, JavaScript\n- HTML, CSS, SCSS\n- Node.js, Express\n- Git, GitHub\n\n프로젝트 경험\n\n1. E-커머스 웹사이트 개발\n- React와 TypeScript를 사용한 반응형 웹사이트 구축\n- 사용자 경험 개선으로 전환율 15% 향상\n\n2. 관리자 대시보드 개발\n- 실시간 데이터 시각화 대시보드 구축\n- Chart.js와 D3.js를 활용한 인터랙티브 차트 구현\n\n자격증\n- AWS Certified Developer Associate\n- Google Analytics Individual Qualification",
            "summary": "3년간의 프론트엔드 개발 경험을 가진 김철수는 React와 TypeScript를 활용한 웹 애플리케이션 개발에 전문성을 가지고 있으며, 사용자 경험 개선을 통한 비즈니스 성과 창출에 기여한 경험이 있습니다.",
            "keywords": ["React", "TypeScript", "프론트엔드", "웹개발", "JavaScript", "사용자경험", "E-커머스", "대시보드", "시각화"],
            "document_type": "resume",
            "basic_info": {
                "emails": ["kim.chulsoo@email.com"],
                "phones": ["010-1234-5678"],
                "names": ["김철수"],
                "urls": []
            },
            "file_metadata": {
                "filename": "김철수_이력서.pdf",
                "size": 245760,
                "mime": "application/pdf",
                "hash": "abc123def456",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["이영희"],
            "extracted_text": "이영희\n백엔드 개발자\n연락처: 010-2345-6789\n이메일: lee.younghee@email.com\n\n학력\n- 연세대학교 정보산업공학과 졸업\n- 서울대학교 대학원 컴퓨터공학과 석사\n\n경력\n- DEF 회사 백엔드 개발자 (2019-2022)\n- GHI 기업 시스템 아키텍트 (2022-현재)\n\n기술스택\n- Python, Django, FastAPI\n- PostgreSQL, MySQL, Redis\n- Docker, Kubernetes\n- AWS, GCP\n- REST API, GraphQL\n- Microservices Architecture\n\n주요 프로젝트\n\n1. 대규모 E-커머스 플랫폼 백엔드 구축\n- 마이크로서비스 아키텍처 설계 및 구현\n- 초당 10만 요청 처리 가능한 시스템 구축\n- Redis를 활용한 캐싱 전략으로 응답 속도 50% 개선\n\n2. 결제 시스템 개발\n- 안전한 결제 프로세스 설계 및 구현\n- PCI DSS 준수 보안 시스템 구축\n- 모니터링 및 로깅 시스템 구축\n\n3. 데이터 파이프라인 구축\n- Apache Kafka를 활용한 실시간 데이터 처리\n- ELK 스택을 통한 로그 분석 시스템 구축\n\n자격증\n- AWS Solutions Architect Professional\n- Google Cloud Professional Cloud Architect\n- Kubernetes Administrator (CKA)",
            "summary": "5년간의 백엔드 개발 경험을 가진 이영희는 대규모 시스템 설계와 마이크로서비스 아키텍처 구현에 전문성을 가지고 있으며, 안정적이고 확장 가능한 백엔드 시스템 구축 경험이 풍부합니다.",
            "keywords": ["Python", "백엔드", "마이크로서비스", "Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis", "시스템아키텍처", "E-커머스"],
            "document_type": "resume",
            "basic_info": {
                "emails": ["lee.younghee@email.com"],
                "phones": ["010-2345-6789"],
                "names": ["이영희"],
                "urls": []
            },
            "file_metadata": {
                "filename": "이영희_이력서.pdf",
                "size": 368640,
                "mime": "application/pdf",
                "hash": "def456ghi789",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["박민수"],
            "extracted_text": "박민수\nUI/UX 디자이너\n연락처: 010-3456-7890\n이메일: park.minsu@email.com\n\n학력\n- 홍익대학교 시각디자인학과 졸업\n\n경력\n- JKL 디자인 에이전시 UI 디자이너 (2020-2022)\n- MNO 기업 UX 디자이너 (2022-현재)\n\n기술스택\n- Figma, Adobe XD, Sketch\n- Photoshop, Illustrator\n- InVision, Marvel\n- Principle, Framer\n- HTML, CSS (기본)\n\n주요 프로젝트\n\n1. 모바일 뱅킹 앱 리디자인\n- 사용자 리서치를 통한 UX 개선\n- 접근성 가이드라인 준수\n- 사용자 만족도 30% 향상\n\n2. E-커머스 웹사이트 UX 개선\n- 사용자 여정 맵 분석 및 개선\n- A/B 테스트를 통한 최적화\n- 전환율 25% 향상\n\n3. 브랜드 아이덴티티 디자인\n- 로고, CI/BI 시스템 구축\n- 브랜드 가이드라인 제작",
            "summary": "4년간의 UI/UX 디자인 경험을 가진 박민수는 사용자 중심의 디자인을 통해 비즈니스 성과를 창출하는 것에 전문성을 가지고 있으며, 다양한 디자인 도구를 활용한 프로젝트 경험이 풍부합니다.",
            "keywords": ["UI/UX", "디자인", "Figma", "사용자경험", "모바일앱", "웹사이트", "브랜딩", "사용자리서치", "A/B테스트"],
            "document_type": "resume",
            "basic_info": {
                "emails": ["park.minsu@email.com"],
                "phones": ["010-3456-7890"],
                "names": ["박민수"],
                "urls": []
            },
            "file_metadata": {
                "filename": "박민수_이력서.pdf",
                "size": 204800,
                "mime": "application/pdf",
                "hash": "ghi789jkl012",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["정수진"],
            "extracted_text": "정수진\n데이터 분석가\n연락처: 010-4567-8901\n이메일: jung.sujin@email.com\n\n학력\n- 고려대학교 통계학과 졸업\n- 서울대학교 대학원 데이터사이언스 석사\n\n경력\n- PQR 기업 데이터 분석가 (2022-현재)\n\n기술스택\n- Python, R, SQL\n- Pandas, NumPy, Scikit-learn\n- Tableau, Power BI\n- Jupyter Notebook\n- Apache Spark\n- Google Analytics\n\n주요 프로젝트\n\n1. 고객 세분화 분석\n- RFM 분석을 통한 고객 그룹 분류\n- 개인화 마케팅 전략 수립\n- 매출 20% 향상\n\n2. 예측 모델 개발\n- 머신러닝을 활용한 매출 예측 모델\n- 정확도 85% 달성\n- 비즈니스 의사결정 지원\n\n3. 대시보드 구축\n- Tableau를 활용한 실시간 대시보드\n- KPI 모니터링 시스템 구축",
            "summary": "2년간의 데이터 분석 경험을 가진 정수진은 통계학과 데이터사이언스 전공을 바탕으로 머신러닝과 데이터 시각화에 전문성을 가지고 있으며, 비즈니스 인사이트 도출을 통한 성과 창출 경험이 있습니다.",
            "keywords": ["데이터분석", "Python", "R", "SQL", "머신러닝", "Tableau", "통계학", "예측모델", "시각화", "비즈니스인사이트"],
            "document_type": "resume",
            "basic_info": {
                "emails": ["jung.sujin@email.com"],
                "phones": ["010-4567-8901"],
                "names": ["정수진"],
                "urls": []
            },
            "file_metadata": {
                "filename": "정수진_이력서.pdf",
                "size": 184320,
                "mime": "application/pdf",
                "hash": "jkl012mno345",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["최동현"],
            "extracted_text": "최동현\nDevOps 엔지니어\n연락처: 010-5678-9012\n이메일: choi.donghyun@email.com\n\n학력\n- 한양대학교 컴퓨터공학과 졸업\n\n경력\n- STU 기업 시스템 엔지니어 (2018-2022)\n- VWX 스타트업 DevOps 엔지니어 (2022-현재)\n\n기술스택\n- AWS, GCP, Azure\n- Docker, Kubernetes\n- Jenkins, GitLab CI/CD\n- Terraform, Ansible\n- Linux, Shell Script\n- Prometheus, Grafana\n- ELK Stack\n\n주요 프로젝트\n\n1. 클라우드 마이그레이션\n- 온프레미스에서 AWS로 전체 시스템 마이그레이션\n- 99.9% 가용성 달성\n- 운영 비용 40% 절감\n\n2. CI/CD 파이프라인 구축\n- Jenkins와 Docker를 활용한 자동화 파이프라인\n- 배포 시간 80% 단축\n- 롤백 시간 5분 이내\n\n3. 모니터링 시스템 구축\n- Prometheus와 Grafana를 활용한 실시간 모니터링\n- 알림 시스템 구축\n- 장애 대응 시간 50% 단축\n\n자격증\n- AWS Solutions Architect Professional\n- Kubernetes Administrator (CKA)\n- Google Cloud Professional Cloud Architect",
            "summary": "6년간의 시스템 엔지니어링과 DevOps 경험을 가진 최동현은 클라우드 인프라 구축과 CI/CD 파이프라인 구현에 전문성을 가지고 있으며, 안정적이고 확장 가능한 시스템 운영 경험이 풍부합니다.",
            "keywords": ["DevOps", "클라우드", "AWS", "Docker", "Kubernetes", "CI/CD", "Jenkins", "Terraform", "모니터링", "마이그레이션"],
            "document_type": "resume",
            "basic_info": {
                "emails": ["choi.donghyun@email.com"],
                "phones": ["010-5678-9012"],
                "names": ["최동현"],
                "urls": []
            },
            "file_metadata": {
                "filename": "최동현_이력서.pdf",
                "size": 307200,
                "mime": "application/pdf",
                "hash": "mno345pqr678",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "created_at": datetime.now()
        }
    ]
    resumes_collection.insert_many(resumes_data)
    print(f"✅ 이력서 {len(resumes_data)}개 추가 완료")
    
    # 면접 컬렉션 생성 및 샘플 데이터
    print("🤝 면접 컬렉션 생성 중...")
    interviews_collection = db.create_collection('interviews')
    interviews_data = [
        {
            "user_id": "user1",
            "company": "테크컴퍼니",
            "position": "프론트엔드 개발자",
            "date": datetime(2024, 1, 15, 10, 0, 0),
            "status": "scheduled",
            "created_at": datetime.now()
        },
        {
            "user_id": "user2",
            "company": "스타트업",
            "position": "백엔드 개발자", 
            "date": datetime(2024, 1, 20, 14, 0, 0),
            "status": "completed",
            "created_at": datetime.now()
        }
    ]
    interviews_collection.insert_many(interviews_data)
    print(f"✅ 면접 {len(interviews_data)}개 추가 완료")
    
    # 자기소개서 컬렉션 생성 및 샘플 데이터
    print("📝 자기소개서 컬렉션 생성 중...")
    cover_letters_collection = db.create_collection('cover_letters')
    cover_letters_data = [
        {
            "applicant_id": applicant_id_map["김철수"],
            "extracted_text": "React와 TypeScript에 대한 깊은 이해와 실무 경험을 바탕으로 사용자 중심의 웹 애플리케이션을 개발하고 싶습니다. ABC 회사에서 2년간 프론트엔드 개발자로 근무하며 E-커머스 웹사이트와 관리자 대시보드를 개발한 경험이 있습니다. 사용자 경험을 개선하여 전환율을 15% 향상시킨 성과를 바탕으로, 귀사의 서비스 발전에 기여하고 싶습니다.",
            "summary": "프론트엔드 개발에 대한 깊은 이해와 실무 경험을 바탕으로 사용자 중심의 웹 애플리케이션 개발에 기여하고 싶습니다.",
            "keywords": ["React", "TypeScript", "프론트엔드", "사용자경험", "E-커머스", "대시보드"],
            "document_type": "cover_letter",
            "basic_info": {
                "emails": ["kim.chulsoo@email.com"],
                "phones": ["010-1234-5678"],
                "names": ["김철수"],
                "urls": []
            },
            "file_metadata": {
                "filename": "김철수_자기소개서.pdf",
                "size": 102400,
                "mime": "application/pdf",
                "hash": "cover_001_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "growthBackground": "웹 개발에 대한 열정으로 다양한 프로젝트를 통해 성장해왔습니다.",
            "motivation": "사용자 경험을 개선하는 개발자가 되고 싶습니다.",
            "careerHistory": "ABC 회사에서 2년간 프론트엔드 개발, XYZ 스타트업에서 1년간 풀스택 개발",
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["이영희"],
            "extracted_text": "Python과 FastAPI를 활용한 효율적인 백엔드 시스템 구축 경험을 바탕으로 확장 가능한 서비스를 개발하고 싶습니다. DEF 회사에서 3년간 백엔드 개발자로 근무하며 대규모 E-커머스 플랫폼의 백엔드를 구축했습니다. 마이크로서비스 아키텍처를 설계하여 초당 10만 요청을 처리할 수 있는 시스템을 구축했으며, Redis 캐싱 전략으로 응답 속도를 50% 개선했습니다. 귀사의 기술적 도전과제를 해결하는 데 기여하고 싶습니다.",
            "summary": "백엔드 시스템 설계와 개발을 통해 안정적이고 확장 가능한 서비스를 구축하고 싶습니다.",
            "keywords": ["Python", "FastAPI", "백엔드", "마이크로서비스", "Redis", "E-커머스"],
            "document_type": "cover_letter",
            "basic_info": {
                "emails": ["lee.younghee@email.com"],
                "phones": ["010-2345-6789"],
                "names": ["이영희"],
                "urls": []
            },
            "file_metadata": {
                "filename": "이영희_자기소개서.pdf",
                "size": 122880,
                "mime": "application/pdf",
                "hash": "cover_002_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "growthBackground": "백엔드 시스템 설계와 개발을 통해 안정적인 서비스를 제공하는 것에 관심이 많습니다.",
            "motivation": "확장 가능하고 안정적인 백엔드 시스템을 구축하고 싶습니다.",
            "careerHistory": "DEF 회사에서 3년간 백엔드 개발, GHI 기업에서 2년간 시스템 아키텍트",
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["박민수"],
            "extracted_text": "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 것에 관심이 많습니다. JKL 디자인 에이전시에서 2년간 UI 디자이너로 근무하며 모바일 뱅킹 앱 리디자인 프로젝트를 진행했습니다. 사용자 리서치를 통해 UX를 개선하고 접근성 가이드라인을 준수하여 사용자 만족도를 30% 향상시켰습니다. MNO 기업에서는 E-커머스 웹사이트 UX 개선을 통해 전환율을 25% 향상시킨 경험이 있습니다. 귀사의 사용자 경험 향상에 기여하고 싶습니다.",
            "summary": "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 UI/UX 디자이너가 되고 싶습니다.",
            "keywords": ["UI/UX", "디자인", "사용자경험", "모바일앱", "웹사이트", "사용자리서치"],
            "document_type": "cover_letter",
            "basic_info": {
                "emails": ["park.minsu@email.com"],
                "phones": ["010-3456-7890"],
                "names": ["박민수"],
                "urls": []
            },
            "file_metadata": {
                "filename": "박민수_자기소개서.pdf",
                "size": 98304,
                "mime": "application/pdf",
                "hash": "cover_003_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "growthBackground": "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 것에 관심이 있습니다.",
            "motivation": "사용자 경험을 향상시키는 혁신적인 디자인을 만들고 싶습니다.",
            "careerHistory": "JKL 디자인 에이전시에서 2년간 UI 디자이너, MNO 기업에서 2년간 UX 디자이너",
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["정수진"],
            "extracted_text": "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정에 기여하는 것에 관심이 많습니다. 고려대학교 통계학과와 서울대학교 대학원 데이터사이언스를 전공하여 데이터 분석의 이론적 기반을 다졌습니다. PQR 기업에서 2년간 데이터 분석가로 근무하며 고객 세분화 분석을 통해 매출을 20% 향상시켰습니다. 머신러닝을 활용한 매출 예측 모델을 개발하여 85%의 정확도를 달성했으며, Tableau를 활용한 실시간 대시보드를 구축하여 KPI 모니터링 시스템을 운영했습니다. 귀사의 데이터 기반 의사결정을 지원하고 싶습니다.",
            "summary": "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정에 기여하는 데이터 분석가가 되고 싶습니다.",
            "keywords": ["데이터분석", "머신러닝", "Tableau", "통계학", "예측모델", "비즈니스인사이트"],
            "document_type": "cover_letter",
            "basic_info": {
                "emails": ["jung.sujin@email.com"],
                "phones": ["010-4567-8901"],
                "names": ["정수진"],
                "urls": []
            },
            "file_metadata": {
                "filename": "정수진_자기소개서.pdf",
                "size": 81920,
                "mime": "application/pdf",
                "hash": "cover_004_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "growthBackground": "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정에 기여하는 것에 관심이 있습니다.",
            "motivation": "데이터 기반의 의사결정을 지원하는 분석가가 되고 싶습니다.",
            "careerHistory": "PQR 기업에서 2년간 데이터 분석가로 근무",
            "created_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["최동현"],
            "extracted_text": "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 것에 전문성을 가지고 있습니다. STU 기업에서 4년간 시스템 엔지니어로 근무하며 온프레미스 환경에서의 시스템 운영 경험을 쌓았습니다. VWX 스타트업에서는 DevOps 엔지니어로 근무하며 온프레미스에서 AWS로의 전체 시스템 마이그레이션을 성공적으로 완료했습니다. 99.9%의 가용성을 달성하고 운영 비용을 40% 절감했으며, Jenkins와 Docker를 활용한 CI/CD 파이프라인을 구축하여 배포 시간을 80% 단축했습니다. 귀사의 안정적이고 확장 가능한 인프라 구축에 기여하고 싶습니다.",
            "summary": "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 DevOps 엔지니어가 되고 싶습니다.",
            "keywords": ["DevOps", "클라우드", "AWS", "CI/CD", "Jenkins", "Docker", "마이그레이션"],
            "document_type": "cover_letter",
            "basic_info": {
                "emails": ["choi.donghyun@email.com"],
                "phones": ["010-5678-9012"],
                "names": ["최동현"],
                "urls": []
            },
            "file_metadata": {
                "filename": "최동현_자기소개서.pdf",
                "size": 143360,
                "mime": "application/pdf",
                "hash": "cover_005_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "growthBackground": "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 것에 전문성을 가지고 있습니다.",
            "motivation": "안정적이고 확장 가능한 인프라를 구축하여 개발팀의 생산성을 향상시키고 싶습니다.",
            "careerHistory": "STU 기업에서 4년간 시스템 엔지니어, VWX 스타트업에서 2년간 DevOps 엔지니어",
            "created_at": datetime.now()
        }
    ]
    cover_letters_collection.insert_many(cover_letters_data)
    print(f"✅ 자기소개서 {len(cover_letters_data)}개 추가 완료")
    
    # 포트폴리오 컬렉션 생성 및 샘플 데이터
    print("💼 포트폴리오 컬렉션 생성 중...")
    portfolios_collection = db.create_collection('portfolios')
    portfolios_data = [
        {
            "applicant_id": applicant_id_map["김철수"],
            "extracted_text": "React와 TypeScript를 사용한 반응형 E-커머스 웹사이트입니다. 사용자 경험을 개선하여 전환율을 15% 향상시켰으며, 관리자 대시보드와 실시간 데이터 시각화 기능을 포함합니다.",
            "summary": "React와 TypeScript를 활용한 현대적인 E-커머스 웹사이트 개발 경험",
            "keywords": ["React", "TypeScript", "E-커머스", "사용자경험", "대시보드", "시각화"],
            "document_type": "portfolio",
            "basic_info": {
                "emails": ["kim.chulsoo@email.com"],
                "phones": ["010-1234-5678"],
                "names": ["김철수"],
                "urls": ["https://github.com/user1/react-ecommerce", "https://react-ecommerce-demo.com"]
            },
            "file_metadata": {
                "filename": "김철수_포트폴리오.pdf",
                "size": 512000,
                "mime": "application/pdf",
                "hash": "portfolio_001_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "items": [
                {
                    "item_id": "item_001",
                    "title": "React E-커머스 웹사이트",
                    "type": "project",
                    "artifacts": [
                        {
                            "kind": "url",
                            "url": "https://github.com/user1/react-ecommerce",
                            "filename": "react-ecommerce",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "github_hash_001"
                        },
                        {
                            "kind": "url",
                            "url": "https://react-ecommerce-demo.com",
                            "filename": "demo",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "demo_hash_001"
                        }
                    ]
                }
            ],
            "analysis_score": 85,
            "status": "active",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["이영희"],
            "extracted_text": "FastAPI와 Python을 사용한 마이크로서비스 아키텍처의 백엔드 시스템입니다. 초당 10만 요청을 처리할 수 있으며, Redis 캐싱과 ELK 스택을 활용한 모니터링 시스템을 포함합니다.",
            "summary": "FastAPI와 Python을 활용한 고성능 마이크로서비스 백엔드 시스템 개발",
            "keywords": ["Python", "FastAPI", "마이크로서비스", "Redis", "ELK", "모니터링"],
            "document_type": "portfolio",
            "basic_info": {
                "emails": ["lee.younghee@email.com"],
                "phones": ["010-2345-6789"],
                "names": ["이영희"],
                "urls": ["https://github.com/user2/fastapi-microservices", "https://api-demo.com"]
            },
            "file_metadata": {
                "filename": "이영희_포트폴리오.pdf",
                "size": 614400,
                "mime": "application/pdf",
                "hash": "portfolio_002_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "items": [
                {
                    "item_id": "item_002",
                    "title": "FastAPI 마이크로서비스 백엔드",
                    "type": "project",
                    "artifacts": [
                        {
                            "kind": "url",
                            "url": "https://github.com/user2/fastapi-microservices",
                            "filename": "fastapi-microservices",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "github_hash_002"
                        },
                        {
                            "kind": "url",
                            "url": "https://api-demo.com",
                            "filename": "demo",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "demo_hash_002"
                        }
                    ]
                }
            ],
            "analysis_score": 92,
            "status": "active",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["박민수"],
            "extracted_text": "사용자 중심의 모바일 뱅킹 앱 UI/UX 디자인 프로젝트입니다. 사용자 리서치를 통해 UX를 개선하고 접근성 가이드라인을 준수하여 사용자 만족도를 30% 향상시켰습니다.",
            "summary": "사용자 중심의 모바일 뱅킹 앱 UI/UX 디자인 프로젝트",
            "keywords": ["UI/UX", "모바일앱", "뱅킹", "사용자리서치", "접근성"],
            "document_type": "portfolio",
            "basic_info": {
                "emails": ["park.minsu@email.com"],
                "phones": ["010-3456-7890"],
                "names": ["박민수"],
                "urls": ["https://github.com/user3/banking-app-design", "https://banking-app-demo.com"]
            },
            "file_metadata": {
                "filename": "박민수_포트폴리오.pdf",
                "size": 409600,
                "mime": "application/pdf",
                "hash": "portfolio_003_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "items": [
                {
                    "item_id": "item_003",
                    "title": "모바일 뱅킹 앱 UI/UX 디자인",
                    "type": "project",
                    "artifacts": [
                        {
                            "kind": "url",
                            "url": "https://github.com/user3/banking-app-design",
                            "filename": "banking-app-design",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "github_hash_003"
                        },
                        {
                            "kind": "url",
                            "url": "https://banking-app-demo.com",
                            "filename": "demo",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "demo_hash_003"
                        }
                    ]
                }
            ],
            "analysis_score": 88,
            "status": "active",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["정수진"],
            "extracted_text": "Python과 Tableau를 활용한 데이터 분석 대시보드입니다. 고객 세분화 분석과 매출 예측 모델을 포함하며, 실시간 KPI 모니터링 시스템을 구축했습니다.",
            "summary": "Python과 Tableau를 활용한 데이터 분석 대시보드 및 예측 모델 개발",
            "keywords": ["데이터분석", "Python", "Tableau", "예측모델", "KPI", "대시보드"],
            "document_type": "portfolio",
            "basic_info": {
                "emails": ["jung.sujin@email.com"],
                "phones": ["010-4567-8901"],
                "names": ["정수진"],
                "urls": ["https://github.com/user4/data-analytics-dashboard", "https://dashboard-demo.com"]
            },
            "file_metadata": {
                "filename": "정수진_포트폴리오.pdf",
                "size": 327680,
                "mime": "application/pdf",
                "hash": "portfolio_004_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "items": [
                {
                    "item_id": "item_004",
                    "title": "데이터 분석 대시보드",
                    "type": "project",
                    "artifacts": [
                        {
                            "kind": "url",
                            "url": "https://github.com/user4/data-analytics-dashboard",
                            "filename": "data-analytics-dashboard",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "github_hash_004"
                        },
                        {
                            "kind": "url",
                            "url": "https://dashboard-demo.com",
                            "filename": "demo",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "demo_hash_004"
                        }
                    ]
                }
            ],
            "analysis_score": 78,
            "status": "active",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "applicant_id": applicant_id_map["최동현"],
            "extracted_text": "AWS와 Terraform을 활용한 클라우드 인프라 자동화 프로젝트입니다. CI/CD 파이프라인과 모니터링 시스템을 구축하여 배포 시간을 80% 단축하고 99.9%의 가용성을 달성했습니다.",
            "summary": "AWS와 Terraform을 활용한 클라우드 인프라 자동화 및 CI/CD 파이프라인 구축",
            "keywords": ["DevOps", "AWS", "Terraform", "CI/CD", "모니터링", "자동화"],
            "document_type": "portfolio",
            "basic_info": {
                "emails": ["choi.donghyun@email.com"],
                "phones": ["010-5678-9012"],
                "names": ["최동현"],
                "urls": ["https://github.com/user5/cloud-infrastructure", "https://infra-demo.com"]
            },
            "file_metadata": {
                "filename": "최동현_포트폴리오.pdf",
                "size": 737280,
                "mime": "application/pdf",
                "hash": "portfolio_005_hash",
                "created_at": datetime.now(),
                "modified_at": datetime.now()
            },
            "items": [
                {
                    "item_id": "item_005",
                    "title": "클라우드 인프라 자동화",
                    "type": "project",
                    "artifacts": [
                        {
                            "kind": "url",
                            "url": "https://github.com/user5/cloud-infrastructure",
                            "filename": "cloud-infrastructure",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "github_hash_005"
                        },
                        {
                            "kind": "url",
                            "url": "https://infra-demo.com",
                            "filename": "demo",
                            "mime": "text/html",
                            "size": 0,
                            "hash": "demo_hash_005"
                        }
                    ]
                }
            ],
            "analysis_score": 95,
            "status": "active",
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    portfolios_collection.insert_many(portfolios_data)
    print(f"✅ 포트폴리오 {len(portfolios_data)}개 추가 완료")
    
    # 채용공고 컬렉션 생성 및 샘플 데이터
    print("📋 채용공고 컬렉션 생성 중...")
    job_postings_collection = db.create_collection('job_postings')
    job_postings_data = [
        {
            "title": "프론트엔드 개발자",
            "company": "테크스타트업",
            "department": "개발팀",
            "position": "프론트엔드 개발자",
            "job_type": "정규직",
            "experience_level": "3-5년",
            "education": "대졸 이상",
            "location": "서울 강남구",
            "salary_range": "4000-6000만원",
            "description": "React와 TypeScript를 활용한 현대적인 웹 애플리케이션 개발을 담당합니다. 사용자 경험을 중시하며, 팀과의 협업을 통해 혁신적인 서비스를 만들어갑니다.",
            "requirements": [
                "React, TypeScript, JavaScript 경험 3년 이상",
                "HTML, CSS, SCSS에 대한 깊은 이해",
                "Git을 활용한 버전 관리 경험",
                "웹 표준과 접근성에 대한 이해",
                "팀 협업 및 커뮤니케이션 능력"
            ],
            "preferred_skills": [
                "Next.js, Vue.js 경험",
                "상태 관리 라이브러리 (Redux, Zustand 등) 경험",
                "테스트 자동화 경험",
                "CI/CD 파이프라인 경험",
                "모바일 반응형 웹 개발 경험"
            ],
            "benefits": [
                "유연근무제",
                "원격근무 가능",
                "성과급",
                "교육비 지원",
                "건강검진",
                "식대 지원"
            ],
            "application_deadline": datetime(2024, 12, 31),
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "백엔드 개발자",
            "company": "테크스타트업",
            "department": "개발팀",
            "position": "백엔드 개발자",
            "job_type": "정규직",
            "experience_level": "5-7년",
            "education": "대졸 이상",
            "location": "서울 강남구",
            "salary_range": "5000-8000만원",
            "description": "Python과 FastAPI를 활용한 고성능 백엔드 시스템 개발을 담당합니다. 마이크로서비스 아키텍처 설계 및 구현을 통해 확장 가능한 서비스를 구축합니다.",
            "requirements": [
                "Python, Django, FastAPI 경험 5년 이상",
                "PostgreSQL, MySQL, Redis 경험",
                "Docker, Kubernetes 경험",
                "REST API, GraphQL 설계 경험",
                "마이크로서비스 아키텍처 이해"
            ],
            "preferred_skills": [
                "AWS, GCP 클라우드 경험",
                "Apache Kafka, ELK 스택 경험",
                "CI/CD 파이프라인 구축 경험",
                "성능 최적화 경험",
                "보안 관련 지식"
            ],
            "benefits": [
                "유연근무제",
                "원격근무 가능",
                "성과급",
                "교육비 지원",
                "건강검진",
                "식대 지원"
            ],
            "application_deadline": datetime(2024, 12, 31),
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "UI/UX 디자이너",
            "company": "테크스타트업",
            "department": "디자인팀",
            "position": "UI/UX 디자이너",
            "job_type": "정규직",
            "experience_level": "3-5년",
            "education": "대졸 이상",
            "location": "서울 강남구",
            "salary_range": "3500-5500만원",
            "description": "사용자 중심의 디자인을 통해 비즈니스 가치를 창출하는 UI/UX 디자이너를 모집합니다. 사용자 리서치부터 프로토타이핑까지 전체 디자인 프로세스를 담당합니다.",
            "requirements": [
                "Figma, Adobe XD, Sketch 경험 3년 이상",
                "Photoshop, Illustrator 활용 능력",
                "사용자 리서치 및 UX 설계 경험",
                "프로토타이핑 도구 활용 능력",
                "디자인 시스템 구축 경험"
            ],
            "preferred_skills": [
                "Principle, Framer 경험",
                "A/B 테스트 설계 및 분석 경험",
                "접근성 가이드라인 이해",
                "모바일 앱 디자인 경험",
                "브랜딩 디자인 경험"
            ],
            "benefits": [
                "유연근무제",
                "원격근무 가능",
                "성과급",
                "교육비 지원",
                "건강검진",
                "식대 지원"
            ],
            "application_deadline": datetime(2024, 12, 31),
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "데이터 분석가",
            "company": "테크스타트업",
            "department": "데이터팀",
            "position": "데이터 분석가",
            "job_type": "정규직",
            "experience_level": "2-4년",
            "education": "대졸 이상",
            "location": "서울 강남구",
            "salary_range": "3000-5000만원",
            "description": "데이터를 통해 인사이트를 도출하고 비즈니스 의사결정을 지원하는 데이터 분석가를 모집합니다. 머신러닝과 데이터 시각화를 활용한 분석을 수행합니다.",
            "requirements": [
                "Python, R, SQL 경험 2년 이상",
                "Pandas, NumPy, Scikit-learn 활용 능력",
                "Tableau, Power BI 경험",
                "통계학적 지식",
                "데이터 시각화 능력"
            ],
            "preferred_skills": [
                "머신러닝 모델 개발 경험",
                "Apache Spark 경험",
                "Google Analytics 활용 능력",
                "A/B 테스트 설계 및 분석 경험",
                "비즈니스 인사이트 도출 경험"
            ],
            "benefits": [
                "유연근무제",
                "원격근무 가능",
                "성과급",
                "교육비 지원",
                "건강검진",
                "식대 지원"
            ],
            "application_deadline": datetime(2024, 12, 31),
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "DevOps 엔지니어",
            "company": "테크스타트업",
            "department": "인프라팀",
            "position": "DevOps 엔지니어",
            "job_type": "정규직",
            "experience_level": "5-7년",
            "education": "대졸 이상",
            "location": "서울 강남구",
            "salary_range": "5000-8000만원",
            "description": "클라우드 인프라와 CI/CD 파이프라인 구축을 통해 개발 생산성을 향상시키는 DevOps 엔지니어를 모집합니다. 안정적이고 확장 가능한 시스템 운영을 담당합니다.",
            "requirements": [
                "AWS, GCP, Azure 경험 5년 이상",
                "Docker, Kubernetes 경험",
                "Jenkins, GitLab CI/CD 경험",
                "Terraform, Ansible 경험",
                "Linux, Shell Script 활용 능력"
            ],
            "preferred_skills": [
                "Prometheus, Grafana 모니터링 경험",
                "ELK 스택 경험",
                "마이크로서비스 아키텍처 이해",
                "보안 관련 지식",
                "성능 최적화 경험"
            ],
            "benefits": [
                "유연근무제",
                "원격근무 가능",
                "성과급",
                "교육비 지원",
                "건강검진",
                "식대 지원"
            ],
            "application_deadline": datetime(2024, 12, 31),
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    job_postings_collection.insert_many(job_postings_data)
    print(f"✅ 채용공고 {len(job_postings_data)}개 추가 완료")
    
    # 인덱스 생성
    print("\n🔍 인덱스 생성 중...")
    
    # applicants 컬렉션 인덱스
    applicants_collection.create_index([("email", 1)], unique=True)
    applicants_collection.create_index([("created_at", -1)])
    applicants_collection.create_index([("position", 1)])
    print("✅ applicants 인덱스 생성 완료")
    
    # resumes 컬렉션 인덱스
    resumes_collection.create_index([("applicant_id", 1)])
    resumes_collection.create_index([("created_at", -1)])
    resumes_collection.create_index([("document_type", 1)])
    print("✅ resumes 인덱스 생성 완료")
    
    # cover_letters 컬렉션 인덱스
    cover_letters_collection.create_index([("applicant_id", 1)])
    cover_letters_collection.create_index([("created_at", -1)])
    cover_letters_collection.create_index([("document_type", 1)])
    print("✅ cover_letters 인덱스 생성 완료")
    
    # portfolios 컬렉션 인덱스
    portfolios_collection.create_index([("applicant_id", 1), ("version", -1)], unique=True)
    portfolios_collection.create_index([("applicant_id", 1), ("created_at", -1)])
    portfolios_collection.create_index([("document_type", 1)])
    print("✅ portfolios 인덱스 생성 완료")
    
    # job_postings 컬렉션 인덱스
    job_postings_collection.create_index([("position", 1)])
    job_postings_collection.create_index([("status", 1)])
    job_postings_collection.create_index([("created_at", -1)])
    print("✅ job_postings 인덱스 생성 완료")
    
    # 컬렉션별 데이터 개수 확인
    print("\n📊 초기화 완료된 컬렉션 현황:")
    for collection_name in collections_to_drop:
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count}개")
    
    print("\n🎉 MongoDB 초기화 완료!")
    client.close()

if __name__ == "__main__":
    try:
        init_mongodb()
    except Exception as e:
        print(f"❌ 초기화 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
