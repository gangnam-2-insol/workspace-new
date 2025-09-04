import asyncio
import os
import random
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")

# 다양한 자소서 템플릿
COVER_LETTER_TEMPLATES = [
    {
        "name": "프론트엔드 개발자 김철수",
        "position": "프론트엔드 개발자",
        "content": """지원 동기:
저는 사용자 경험을 중시하는 프론트엔드 개발자로서, 직관적이고 반응형 웹 애플리케이션을 개발하는 것에 깊은 관심을 가지고 있습니다. 귀사의 혁신적인 프로젝트에 참여하여 최신 기술을 활용한 웹 솔루션을 제공하고 싶습니다.

경력 목표:
React, Vue.js, TypeScript 등 최신 프론트엔드 기술을 활용하여 사용자 친화적인 웹 애플리케이션을 개발하고, 팀 내 기술 리더로서 성장하고자 합니다.

강점 및 역량:
- React, Vue.js, Angular 등 주요 프론트엔드 프레임워크 숙련
- TypeScript를 활용한 타입 안전한 개발 경험
- CSS3, SCSS, Styled-components를 활용한 반응형 디자인 구현
- Webpack, Vite 등 모듈 번들러 활용 경험
- Git을 활용한 협업 및 버전 관리

관련 경험:
이전 회사에서 전자상거래 플랫폼의 프론트엔드 개발을 담당했습니다. React와 TypeScript를 활용하여 사용자 인터페이스를 개선하고, 성능 최적화를 통해 페이지 로딩 속도를 40% 단축시켰습니다.

주요 성과:
- 전자상거래 플랫폼 사용자 경험 개선으로 전환율 25% 향상
- 웹 성능 최적화를 통한 페이지 로딩 속도 40% 단축
- 모바일 반응형 디자인 구현으로 모바일 사용자 증가 60%

보유 기술:
JavaScript, TypeScript, React, Vue.js, Angular, HTML5, CSS3, SCSS, Styled-components, Webpack, Vite, Git, Jest, Cypress

프로젝트 경험:
1. 전자상거래 플랫폼 프론트엔드 개발 (2022-2023)
   - React, TypeScript, Redux 활용
   - 사용자 인터페이스 개선 및 성능 최적화
   - 팀 리드 역할 수행

2. 모바일 웹 애플리케이션 개발 (2021-2022)
   - Vue.js, Vuetify 활용
   - PWA 구현으로 네이티브 앱과 유사한 경험 제공

학력 사항:
- 서울대학교 컴퓨터공학과 졸업 (2018-2022)
- 웹 개발 관련 수강 과목: 웹 프로그래밍, 데이터베이스, 알고리즘

자격증:
- AWS Certified Developer - Associate
- Google Cloud Platform Associate Cloud Engineer

언어 능력:
- 한국어 (모국어)
- 영어 (TOEIC 850점)

자기소개:
저는 끊임없이 새로운 기술을 학습하고 적용하는 것을 즐기는 개발자입니다. 사용자 중심의 사고를 바탕으로 직관적이고 효율적인 웹 애플리케이션을 개발하는 것이 저의 목표입니다.

향후 계획:
귀사에서 최신 프론트엔드 기술을 활용한 혁신적인 프로젝트에 참여하여, 사용자 경험을 향상시키는 솔루션을 개발하고 싶습니다. 또한 팀 내 기술 공유와 멘토링을 통해 함께 성장하는 개발자가 되고자 합니다."""
    },
    {
        "name": "백엔드 개발자 이영희",
        "position": "백엔드 개발자",
        "content": """지원 동기:
저는 안정적이고 확장 가능한 백엔드 시스템을 구축하는 것에 열정을 가진 개발자입니다. 귀사의 대규모 사용자를 지원할 수 있는 고성능 서버 아키텍처를 설계하고 구현하고 싶습니다.

경력 목표:
Spring Boot, Django, Node.js 등 다양한 백엔드 기술을 활용하여 마이크로서비스 아키텍처를 구축하고, 클라우드 네이티브 애플리케이션 개발 전문가가 되고자 합니다.

강점 및 역량:
- Java, Python, Node.js 등 다중 언어 활용 능력
- Spring Boot, Django, Express.js 등 주요 백엔드 프레임워크 숙련
- MySQL, PostgreSQL, MongoDB 등 다양한 데이터베이스 활용 경험
- Docker, Kubernetes를 활용한 컨테이너화 및 오케스트레이션
- AWS, GCP 등 클라우드 플랫폼 활용 경험

관련 경험:
이전 회사에서 소셜 미디어 플랫폼의 백엔드 시스템을 개발했습니다. Spring Boot와 MySQL을 활용하여 사용자 인증, 게시물 관리, 댓글 시스템을 구현했으며, Redis를 활용한 캐싱으로 응답 속도를 크게 개선했습니다.

주요 성과:
- 소셜 미디어 플랫폼 API 응답 속도 60% 개선
- 데이터베이스 쿼리 최적화를 통한 서버 리소스 사용량 30% 감소
- 마이크로서비스 아키텍처 도입으로 시스템 확장성 향상

보유 기술:
Java, Python, JavaScript, Spring Boot, Django, Express.js, MySQL, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, GCP, Git, JUnit, Postman

프로젝트 경험:
1. 소셜 미디어 플랫폼 백엔드 개발 (2022-2023)
   - Spring Boot, MySQL, Redis 활용
   - RESTful API 설계 및 구현
   - 마이크로서비스 아키텍처 구축

2. 전자상거래 결제 시스템 개발 (2021-2022)
   - Django, PostgreSQL 활용
   - 결제 보안 및 암호화 구현
   - AWS 클라우드 인프라 구축

학력 사항:
- 연세대학교 컴퓨터공학과 졸업 (2017-2021)
- 백엔드 개발 관련 수강 과목: 데이터베이스, 운영체제, 네트워크 프로그래밍

자격증:
- Oracle Certified Professional Java Programmer
- AWS Certified Solutions Architect - Associate

언어 능력:
- 한국어 (모국어)
- 영어 (TOEIC 900점)

자기소개:
저는 안정성과 성능을 중시하는 백엔드 개발자입니다. 사용자에게 끊김 없는 서비스를 제공하기 위해 지속적으로 시스템을 모니터링하고 최적화하는 것을 중요하게 생각합니다.

향후 계획:
귀사에서 대규모 트래픽을 처리할 수 있는 고성능 백엔드 시스템을 구축하고, 클라우드 네이티브 기술을 활용한 혁신적인 솔루션을 개발하고 싶습니다."""
    },
    {
        "name": "데이터 사이언티스트 박민수",
        "position": "데이터 사이언티스트",
        "content": """지원 동기:
저는 데이터를 통해 비즈니스 인사이트를 도출하고 의사결정을 지원하는 것에 깊은 관심을 가지고 있습니다. 귀사의 빅데이터 플랫폼에서 머신러닝 모델을 개발하고 데이터 기반 솔루션을 제공하고 싶습니다.

경력 목표:
Python, R, SQL 등을 활용한 데이터 분석 및 머신러닝 모델 개발 전문가가 되고, 딥러닝과 AI 기술을 활용한 혁신적인 솔루션을 개발하고자 합니다.

강점 및 역량:
- Python, R, SQL 등 데이터 분석 언어 숙련
- Pandas, NumPy, Scikit-learn 등 데이터 분석 라이브러리 활용
- TensorFlow, PyTorch 등 딥러닝 프레임워크 경험
- 데이터 시각화 및 대시보드 구축 능력
- 통계적 분석 및 가설 검정 경험

관련 경험:
이전 회사에서 전자상거래 플랫폼의 고객 행동 분석을 담당했습니다. Python과 SQL을 활용하여 고객 구매 패턴을 분석하고, 추천 시스템을 개발하여 매출을 35% 증가시켰습니다.

주요 성과:
- 고객 구매 패턴 분석을 통한 추천 시스템 개발로 매출 35% 증가
- 고객 이탈 예측 모델 개발로 이탈률 20% 감소
- 실시간 데이터 대시보드 구축으로 의사결정 속도 향상

보유 기술:
Python, R, SQL, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, Matplotlib, Seaborn, Plotly, Jupyter, Git, Docker, AWS SageMaker

프로젝트 경험:
1. 전자상거래 추천 시스템 개발 (2022-2023)
   - Python, Scikit-learn, TensorFlow 활용
   - 협업 필터링 및 콘텐츠 기반 추천 알고리즘 구현
   - A/B 테스트를 통한 모델 성능 검증

2. 고객 이탈 예측 모델 개발 (2021-2022)
   - R, SQL, 머신러닝 알고리즘 활용
   - 로지스틱 회귀, 랜덤 포레스트 등 다양한 모델 비교
   - 모델 성능 최적화 및 배포

학력 사항:
- 고려대학교 통계학과 졸업 (2018-2022)
- 데이터 사이언스 관련 수강 과목: 통계학, 확률론, 머신러닝, 데이터 마이닝

자격증:
- Google Data Analytics Professional Certificate
- Microsoft Certified: Azure Data Scientist Associate

언어 능력:
- 한국어 (모국어)
- 영어 (TOEIC 920점)

자기소개:
저는 데이터를 통해 숨겨진 패턴을 발견하고 의미 있는 인사이트를 도출하는 것을 즐기는 데이터 사이언티스트입니다. 비즈니스 문제를 데이터 기반으로 해결하는 것이 저의 전문 분야입니다.

향후 계획:
귀사에서 빅데이터 플랫폼을 활용한 머신러닝 모델을 개발하고, AI 기술을 활용한 혁신적인 데이터 솔루션을 제공하고 싶습니다."""
    },
    {
        "name": "DevOps 엔지니어 정수진",
        "position": "DevOps 엔지니어",
        "content": """지원 동기:
저는 개발과 운영을 효율적으로 연결하여 빠른 배포와 안정적인 서비스를 제공하는 것에 열정을 가진 DevOps 엔지니어입니다. 귀사의 CI/CD 파이프라인을 구축하고 클라우드 인프라를 최적화하고 싶습니다.

경력 목표:
AWS, Azure, GCP 등 다양한 클라우드 플랫폼을 활용한 인프라 자동화 전문가가 되고, 마이크로서비스 아키텍처를 지원하는 DevOps 환경을 구축하고자 합니다.

강점 및 역량:
- AWS, Azure, GCP 등 주요 클라우드 플랫폼 활용 경험
- Docker, Kubernetes를 활용한 컨테이너화 및 오케스트레이션
- Jenkins, GitLab CI/CD, GitHub Actions 등 CI/CD 도구 활용
- Terraform, Ansible 등 인프라 자동화 도구 숙련
- 모니터링 및 로깅 시스템 구축 경험

관련 경험:
이전 회사에서 스타트업의 클라우드 인프라를 구축하고 CI/CD 파이프라인을 운영했습니다. AWS와 Docker를 활용하여 마이크로서비스 아키텍처를 구축하고, 배포 시간을 80% 단축시켰습니다.

주요 성과:
- CI/CD 파이프라인 구축으로 배포 시간 80% 단축
- 클라우드 비용 최적화를 통한 월 비용 25% 절감
- 모니터링 시스템 구축으로 장애 대응 시간 60% 단축

보유 기술:
AWS, Azure, GCP, Docker, Kubernetes, Jenkins, GitLab CI/CD, GitHub Actions, Terraform, Ansible, Prometheus, Grafana, ELK Stack, Linux, Git, Python, Shell Script

프로젝트 경험:
1. 클라우드 인프라 구축 및 CI/CD 파이프라인 운영 (2022-2023)
   - AWS, Docker, Kubernetes 활용
   - 마이크로서비스 아키텍처 구축
   - 자동화된 배포 파이프라인 구축

2. 모니터링 및 로깅 시스템 구축 (2021-2022)
   - Prometheus, Grafana, ELK Stack 활용
   - 실시간 모니터링 대시보드 구축
   - 알림 시스템 및 장애 대응 프로세스 수립

학력 사항:
- 한양대학교 컴퓨터공학과 졸업 (2017-2021)
- DevOps 관련 수강 과목: 운영체제, 네트워크, 클라우드 컴퓨팅

자격증:
- AWS Certified DevOps Engineer - Professional
- Kubernetes Administrator (CKA)
- Terraform Associate

언어 능력:
- 한국어 (모국어)
- 영어 (TOEIC 880점)

자기소개:
저는 개발팀과 운영팀 간의 협업을 원활하게 하고, 안정적이고 효율적인 서비스를 제공하는 것을 목표로 하는 DevOps 엔지니어입니다.

향후 계획:
귀사에서 최신 클라우드 기술을 활용한 인프라 자동화를 구현하고, 개발팀의 생산성을 향상시키는 DevOps 환경을 구축하고 싶습니다."""
    },
    {
        "name": "UI/UX 디자이너 김미영",
        "position": "UI/UX 디자이너",
        "content": """지원 동기:
저는 사용자 중심의 디자인을 통해 의미 있는 경험을 제공하는 것에 열정을 가진 UI/UX 디자이너입니다. 귀사의 제품에서 사용자 경험을 향상시키고 브랜드 가치를 높이는 디자인을 제공하고 싶습니다.

경력 목표:
사용자 리서치, 프로토타이핑, 시각적 디자인을 통합하여 직관적이고 아름다운 사용자 인터페이스를 설계하고, 디자인 시스템을 구축하여 일관된 사용자 경험을 제공하고자 합니다.

강점 및 역량:
- Figma, Sketch, Adobe Creative Suite 등 디자인 도구 숙련
- 사용자 리서치 및 사용성 테스트 경험
- 프로토타이핑 및 인터랙션 디자인 능력
- 디자인 시스템 구축 및 관리 경험
- HTML, CSS, JavaScript 기초 지식

관련 경험:
이전 회사에서 모바일 앱의 UI/UX 디자인을 담당했습니다. 사용자 리서치를 통해 사용자 니즈를 파악하고, 직관적인 인터페이스를 설계하여 앱 사용률을 45% 증가시켰습니다.

주요 성과:
- 모바일 앱 UI/UX 개선으로 사용률 45% 증가
- 디자인 시스템 구축으로 디자인 일관성 향상
- 사용자 리서치를 통한 핵심 기능 개선

보유 기술:
Figma, Sketch, Adobe XD, Photoshop, Illustrator, InVision, Principle, HTML, CSS, JavaScript, React, Vue.js

프로젝트 경험:
1. 모바일 앱 UI/UX 디자인 (2022-2023)
   - 사용자 리서치 및 페르소나 정의
   - 와이어프레임 및 프로토타입 제작
   - 사용성 테스트 및 개선

2. 웹사이트 리뉴얼 프로젝트 (2021-2022)
   - 브랜드 아이덴티티 분석
   - 반응형 웹 디자인 구현
   - 디자인 시스템 구축

학력 사항:
- 홍익대학교 디자인학부 졸업 (2018-2022)
- UI/UX 디자인 관련 수강 과목: 사용자 경험 디자인, 인터랙션 디자인, 시각 디자인

자격증:
- Google UX Design Professional Certificate
- Adobe Certified Associate - Visual Design

언어 능력:
- 한국어 (모국어)
- 영어 (TOEIC 850점)

자기소개:
저는 사용자의 니즈를 깊이 이해하고, 이를 바탕으로 직관적이고 아름다운 디자인을 만드는 것을 즐기는 UI/UX 디자이너입니다.

향후 계획:
귀사에서 사용자 중심의 디자인을 통해 제품의 사용성을 향상시키고, 브랜드 가치를 높이는 디자인 솔루션을 제공하고 싶습니다."""
    }
]

async def create_cover_letter_samples():
    """청킹 테스트를 위한 다양한 자소서 샘플 생성"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.hireme

        print("✅ MongoDB 연결 성공")

        # 기존 자소서 데이터 삭제 (선택사항)
        delete_existing = input("기존 자소서 데이터를 삭제하시겠습니까? (y/N): ").lower()
        if delete_existing == 'y':
            await db.cover_letters.delete_many({})
            print("🗑️ 기존 자소서 데이터 삭제 완료")

        # 지원자 조회
        applicants = await db.applicants.find({}).to_list(100)
        print(f"📋 지원자 수: {len(applicants)}")

        if not applicants:
            print("❌ 지원자가 없습니다. 먼저 지원자 샘플 데이터를 생성해주세요.")
            return

        # 자소서 생성
        cover_letters = []
        for i, template in enumerate(COVER_LETTER_TEMPLATES):
            # 지원자 선택 (순환)
            applicant = applicants[i % len(applicants)]

            cover_letter = {
                "applicant_id": str(applicant["_id"]),
                "content": template["content"],
                "extracted_text": template["content"],  # 청킹을 위해 extracted_text 필드 추가
                "filename": f"자소서_{template['name']}.pdf",
                "file_size": random.randint(50000, 200000),
                "status": "submitted",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            cover_letters.append(cover_letter)
            print(f"📝 자소서 생성: {template['name']} ({template['position']})")

        # 데이터베이스에 저장
        if cover_letters:
            result = await db.cover_letters.insert_many(cover_letters)
            print(f"💾 {len(cover_letters)}개의 자소서 저장 완료")

            # 지원자 데이터에 cover_letter_id 업데이트
            for i, cover_letter in enumerate(cover_letters):
                await db.applicants.update_one(
                    {"_id": ObjectId(cover_letter["applicant_id"])},
                    {"$set": {"cover_letter_id": str(result.inserted_ids[i])}}
                )

            print("✅ 지원자 데이터 업데이트 완료")

        # 생성된 자소서 목록 출력
        print("\n📋 생성된 자소서 목록:")
        for i, template in enumerate(COVER_LETTER_TEMPLATES):
            print(f"  {i+1}. {template['name']} - {template['position']}")

        client.close()
        return {
            "success": True,
            "message": f"{len(cover_letters)}개의 자소서 샘플이 성공적으로 생성되었습니다!",
            "generated_count": len(cover_letters)
        }

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {
            "success": False,
            "message": f"자소서 샘플 생성 실패: {str(e)}"
        }

if __name__ == "__main__":
    result = asyncio.run(create_cover_letter_samples())
    print(f"\n🎯 결과: {result['message']}")
