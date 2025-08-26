import json
from datetime import datetime
from bson import ObjectId
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.services.mongo_service import MongoService

def create_chunk_analysis_applicants():
    """청크 데이터 분석을 위한 완전한 형태의 지원자 정보 5개 생성"""

    mongo_service = MongoService()

    # 지원자 데이터 정의
    applicants_data = [
        {
            "name": "김개발",
            "email": "kim.dev@example.com",
            "phone": "010-1111-2222",
            "position": "프론트엔드 개발자",
            "department": "개발팀",
            "experience": "2년",
            "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
            "growthBackground": "컴퓨터공학을 전공하며 웹 개발에 대한 깊은 관심을 키워왔습니다. 대학 시절부터 다양한 프로젝트를 통해 실무 경험을 쌓았고, 특히 사용자 경험을 중시하는 프론트엔드 개발에 매료되어 이 분야로 진로를 정했습니다.",
            "motivation": "귀사의 혁신적인 웹 서비스와 사용자 중심의 개발 문화에 매료되어 지원하게 되었습니다. 특히 모던 웹 기술을 활용한 프로젝트에 참여하고 싶어 이번 기회를 통해 귀사에 기여하고 싶습니다.",
            "careerHistory": "2022년부터 스타트업에서 프론트엔드 개발자로 근무하며 React 기반의 웹 애플리케이션을 개발했습니다. 사용자 인터페이스 개선과 성능 최적화에 중점을 두어 작업했으며, 팀 내 기술 공유 세션을 주도했습니다.",
            "analysisScore": 88,
            "analysisResult": "React와 TypeScript 기반의 프론트엔드 개발 경험이 풍부하며, 사용자 경험에 대한 이해도가 높습니다.",
            "status": "pending",
            "github_url": "https://github.com/kimdev",
            "linkedin_url": "https://linkedin.com/in/kimdev",
            "portfolio_url": "https://portfolio.kimdev.com"
        },
        {
            "name": "이백엔드",
            "email": "lee.backend@example.com",
            "phone": "010-2222-3333",
            "position": "백엔드 개발자",
            "department": "개발팀",
            "experience": "4년",
            "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Docker"],
            "growthBackground": "시스템 엔지니어링에 대한 관심으로 시작하여 백엔드 개발로 전향했습니다. 대용량 데이터 처리와 시스템 아키텍처 설계에 대한 깊은 이해를 바탕으로 안정적이고 확장 가능한 서비스를 구축하는 것을 목표로 합니다.",
            "motivation": "귀사의 대규모 사용자를 대상으로 한 서비스 운영 경험을 배우고 싶어 지원했습니다. 특히 마이크로서비스 아키텍처와 클라우드 인프라에 대한 실무 경험을 쌓고 싶습니다.",
            "careerHistory": "2019년부터 중견 IT 기업에서 백엔드 개발자로 근무하며 Java와 Spring 기반의 웹 서비스를 개발했습니다. 데이터베이스 설계와 API 개발을 주로 담당했으며, 최근에는 마이크로서비스 아키텍처 도입 프로젝트에 참여했습니다.",
            "analysisScore": 92,
            "analysisResult": "Java와 Spring 기반의 백엔드 개발 경험이 풍부하며, 시스템 설계 능력이 우수합니다.",
            "status": "pending",
            "github_url": "https://github.com/leebackend",
            "linkedin_url": "https://linkedin.com/in/leebackend",
            "portfolio_url": "https://portfolio.leebackend.com"
        },
        {
            "name": "박풀스택",
            "email": "park.fullstack@example.com",
            "phone": "010-3333-4444",
            "position": "풀스택 개발자",
            "department": "개발팀",
            "experience": "3년",
            "skills": ["JavaScript", "Node.js", "React", "MongoDB", "AWS"],
            "growthBackground": "웹 개발에 대한 전반적인 이해를 위해 프론트엔드와 백엔드를 모두 학습했습니다. JavaScript 생태계의 풍부함에 매료되어 Node.js 기반의 풀스택 개발을 전문으로 하고 있습니다.",
            "motivation": "귀사의 혁신적인 기술 스택과 빠른 개발 문화에 매료되어 지원했습니다. 특히 JavaScript 기반의 풀스택 개발 환경에서 더욱 성장하고 싶어 이번 기회를 통해 귀사에 기여하고 싶습니다.",
            "careerHistory": "2021년부터 스타트업에서 풀스택 개발자로 근무하며 JavaScript 기반의 웹 애플리케이션을 개발했습니다. 프론트엔드와 백엔드 개발을 모두 담당하며 전체 시스템을 이해하고 최적화하는 경험을 쌓았습니다.",
            "analysisScore": 85,
            "analysisResult": "JavaScript 기반의 풀스택 개발 경험이 있으며, 전체 시스템에 대한 이해도가 높습니다.",
            "status": "pending",
            "github_url": "https://github.com/parkfullstack",
            "linkedin_url": "https://linkedin.com/in/parkfullstack",
            "portfolio_url": "https://portfolio.parkfullstack.com"
        },
        {
            "name": "최데이터",
            "email": "choi.data@example.com",
            "phone": "010-4444-5555",
            "position": "데이터 엔지니어",
            "department": "데이터팀",
            "experience": "5년",
            "skills": ["Python", "Spark", "Hadoop", "Kafka", "Airflow"],
            "growthBackground": "통계학을 전공하며 데이터 분석에 대한 기초를 다졌고, 대용량 데이터 처리와 머신러닝에 대한 관심으로 데이터 엔지니어링 분야로 진입했습니다. 효율적인 데이터 파이프라인 구축과 분석을 목표로 합니다.",
            "motivation": "귀사의 대용량 데이터 처리 인프라와 데이터 기반 의사결정 문화에 매료되어 지원했습니다. 특히 실시간 데이터 처리와 머신러닝 파이프라인 구축에 대한 경험을 쌓고 싶습니다.",
            "careerHistory": "2018년부터 대기업에서 데이터 엔지니어로 근무하며 대용량 데이터 처리 시스템을 구축했습니다. ETL 파이프라인 설계와 데이터 웨어하우스 구축을 주로 담당했으며, 최근에는 실시간 데이터 처리 시스템 도입 프로젝트를 주도했습니다.",
            "analysisScore": 90,
            "analysisResult": "대용량 데이터 처리와 파이프라인 구축 경험이 풍부하며, 데이터 엔지니어링 전문성이 우수합니다.",
            "status": "pending",
            "github_url": "https://github.com/choidata",
            "linkedin_url": "https://linkedin.com/in/choidata",
            "portfolio_url": "https://portfolio.choidata.com"
        },
        {
            "name": "정AI",
            "email": "jung.ai@example.com",
            "phone": "010-5555-6666",
            "position": "AI 엔지니어",
            "department": "AI팀",
            "experience": "3년",
            "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Docker"],
            "growthBackground": "컴퓨터공학과 수학을 복수전공하며 머신러닝과 딥러닝에 대한 이론적 기초를 다졌습니다. 실제 비즈니스 문제를 해결하는 AI 모델 개발에 대한 관심으로 AI 엔지니어링 분야로 진입했습니다.",
            "motivation": "귀사의 혁신적인 AI 기술과 실제 서비스에 적용하는 경험을 배우고 싶어 지원했습니다. 특히 자연어 처리와 컴퓨터 비전 분야에서의 실무 경험을 쌓고 싶습니다.",
            "careerHistory": "2021년부터 AI 스타트업에서 AI 엔지니어로 근무하며 다양한 머신러닝 모델을 개발했습니다. 자연어 처리와 추천 시스템 개발을 주로 담당했으며, 모델 성능 최적화와 MLOps 도입에 대한 경험을 쌓았습니다.",
            "analysisScore": 87,
            "analysisResult": "머신러닝과 딥러닝 모델 개발 경험이 있으며, AI 엔지니어링 전문성이 우수합니다.",
            "status": "pending",
            "github_url": "https://github.com/jungai",
            "linkedin_url": "https://linkedin.com/in/jungai",
            "portfolio_url": "https://portfolio.jungai.com"
        }
    ]

    # 이력서 데이터 정의
    resumes_data = [
        {
            "extracted_text": """
김개발 - 프론트엔드 개발자

[개인정보]
이름: 김개발
이메일: kim.dev@example.com
전화번호: 010-1111-2222
GitHub: https://github.com/kimdev

[학력]
2020-2024 서울대학교 컴퓨터공학과 졸업

[기술스택]
프론트엔드: React, TypeScript, Next.js, Tailwind CSS
상태관리: Redux, Zustand
테스팅: Jest, React Testing Library
버전관리: Git, GitHub

[경력사항]
2022-2024 ABC 스타트업 - 프론트엔드 개발자
- React 기반 웹 애플리케이션 개발
- 사용자 인터페이스 개선 및 성능 최적화
- 팀 내 기술 공유 세션 주도

[프로젝트]
1. E-커머스 플랫폼 (2023)
- React, TypeScript, Next.js 활용
- 반응형 웹 디자인 구현
- 결제 시스템 연동

2. 관리자 대시보드 (2022)
- React, Redux 활용
- 실시간 데이터 시각화
- 차트 라이브러리 연동

[수상경력]
2023 프론트엔드 개발자 대회 우수상
2022 대학생 소프트웨어 경진대회 대상
            """,
            "summary": "2년 경력의 프론트엔드 개발자로 React와 TypeScript 기반의 웹 애플리케이션 개발 경험이 풍부합니다.",
            "keywords": ["React", "TypeScript", "Next.js", "프론트엔드", "웹개발"]
        },
        {
            "extracted_text": """
이백엔드 - 백엔드 개발자

[개인정보]
이름: 이백엔드
이메일: lee.backend@example.com
전화번호: 010-2222-3333
GitHub: https://github.com/leebackend

[학력]
2015-2019 연세대학교 컴퓨터공학과 졸업

[기술스택]
백엔드: Java, Spring Boot, Spring Security
데이터베이스: MySQL, Redis, MongoDB
인프라: Docker, AWS, Jenkins
API: RESTful API, GraphQL

[경력사항]
2019-2024 XYZ 기업 - 백엔드 개발자
- Java와 Spring 기반 웹 서비스 개발
- 데이터베이스 설계 및 최적화
- 마이크로서비스 아키텍처 도입 프로젝트 참여

[프로젝트]
1. 결제 시스템 구축 (2023)
- Spring Boot, MySQL 활용
- 결제 보안 강화 및 암호화 구현
- 트랜잭션 관리 및 롤백 처리

2. 사용자 관리 시스템 (2022)
- Spring Security, JWT 활용
- 사용자 인증 및 권한 관리
- OAuth 2.0 연동

[자격증]
AWS Solutions Architect Associate
Oracle Certified Professional Java Programmer
            """,
            "summary": "4년 경력의 백엔드 개발자로 Java와 Spring 기반의 웹 서비스 개발 경험이 풍부합니다.",
            "keywords": ["Java", "Spring Boot", "MySQL", "백엔드", "API"]
        },
        {
            "extracted_text": """
박풀스택 - 풀스택 개발자

[개인정보]
이름: 박풀스택
이메일: park.fullstack@example.com
전화번호: 010-3333-4444
GitHub: https://github.com/parkfullstack

[학력]
2018-2022 고려대학교 컴퓨터공학과 졸업

[기술스택]
프론트엔드: React, JavaScript, HTML/CSS
백엔드: Node.js, Express.js
데이터베이스: MongoDB, MySQL
클라우드: AWS, Heroku
기타: Git, Docker, Jest

[경력사항]
2021-2024 DEF 스타트업 - 풀스택 개발자
- JavaScript 기반 웹 애플리케이션 개발
- 프론트엔드와 백엔드 개발 담당
- 전체 시스템 최적화 및 성능 개선

[프로젝트]
1. 소셜 네트워킹 플랫폼 (2023)
- React, Node.js, MongoDB 활용
- 실시간 채팅 기능 구현
- 이미지 업로드 및 처리

2. 프로젝트 관리 도구 (2022)
- React, Express.js 활용
- 드래그 앤 드롭 기능 구현
- 실시간 협업 기능

[수상경력]
2023 풀스택 개발자 해커톤 우승
            """,
            "summary": "3년 경력의 풀스택 개발자로 JavaScript 기반의 웹 애플리케이션 개발 경험이 풍부합니다.",
            "keywords": ["JavaScript", "Node.js", "React", "풀스택", "웹개발"]
        },
        {
            "extracted_text": """
최데이터 - 데이터 엔지니어

[개인정보]
이름: 최데이터
이메일: choi.data@example.com
전화번호: 010-4444-5555
GitHub: https://github.com/choidata

[학력]
2014-2018 서울대학교 통계학과 졸업

[기술스택]
프로그래밍: Python, Scala, SQL
빅데이터: Spark, Hadoop, Kafka
워크플로우: Airflow, Luigi
클라우드: AWS, GCP, Azure
데이터베이스: PostgreSQL, MongoDB, Redis

[경력사항]
2018-2024 GHI 대기업 - 데이터 엔지니어
- 대용량 데이터 처리 시스템 구축
- ETL 파이프라인 설계 및 구현
- 데이터 웨어하우스 구축 및 운영

[프로젝트]
1. 실시간 데이터 처리 시스템 (2023)
- Spark Streaming, Kafka 활용
- 실시간 데이터 분석 파이프라인 구축
- 모니터링 및 알림 시스템 구현

2. 데이터 웨어하우스 구축 (2022)
- Hadoop, Hive, Airflow 활용
- 대용량 데이터 수집 및 저장 시스템
- 데이터 품질 관리 및 검증

[자격증]
AWS Big Data Specialty
Google Cloud Professional Data Engineer
            """,
            "summary": "5년 경력의 데이터 엔지니어로 대용량 데이터 처리와 파이프라인 구축 경험이 풍부합니다.",
            "keywords": ["Python", "Spark", "Hadoop", "데이터엔지니어", "빅데이터"]
        },
        {
            "extracted_text": """
정AI - AI 엔지니어

[개인정보]
이름: 정AI
이메일: jung.ai@example.com
전화번호: 010-5555-6666
GitHub: https://github.com/jungai

[학력]
2017-2021 KAIST 컴퓨터공학과 졸업 (수학 복수전공)

[기술스택]
프로그래밍: Python, R, C++
머신러닝: TensorFlow, PyTorch, Scikit-learn
딥러닝: CNN, RNN, Transformer
MLOps: Docker, Kubernetes, MLflow
클라우드: AWS, GCP

[경력사항]
2021-2024 JKL AI 스타트업 - AI 엔지니어
- 머신러닝 모델 개발 및 최적화
- 자연어 처리 및 추천 시스템 개발
- MLOps 도입 및 모델 배포 자동화

[프로젝트]
1. 감정 분석 모델 개발 (2023)
- BERT, Transformer 활용
- 한국어 자연어 처리 모델 개발
- 실시간 감정 분석 API 구축

2. 추천 시스템 구축 (2022)
- 협업 필터링, 콘텐츠 기반 필터링
- 딥러닝 기반 추천 모델 개발
- A/B 테스트 및 성능 평가

[논문]
"한국어 감정 분석을 위한 BERT 기반 모델" (2023)
"딥러닝 기반 추천 시스템 성능 비교 연구" (2022)
            """,
            "summary": "3년 경력의 AI 엔지니어로 머신러닝과 딥러닝 모델 개발 경험이 풍부합니다.",
            "keywords": ["Python", "TensorFlow", "PyTorch", "AI", "머신러닝"]
        }
    ]

    # 자기소개서 데이터 정의
    cover_letters_data = [
        {
            "extracted_text": """
지원동기
안녕하세요. 프론트엔드 개발자 김개발입니다. 귀사의 혁신적인 웹 서비스와 사용자 중심의 개발 문화에 매료되어 지원하게 되었습니다.

성장배경
컴퓨터공학을 전공하며 웹 개발에 대한 깊은 관심을 키워왔습니다. 대학 시절부터 다양한 프로젝트를 통해 실무 경험을 쌓았고, 특히 사용자 경험을 중시하는 프론트엔드 개발에 매료되어 이분야로 진로를 정했습니다.

경력사항
2022년부터 ABC 스타트업에서 프론트엔드 개발자로 근무하며 React 기반의 웹 애플리케이션을 개발했습니다. 사용자 인터페이스 개선과 성능 최적화에 중점을 두어 작업했으며, 팀 내 기술 공유 세션을 주도했습니다.

기술역량
React, TypeScript, Next.js, Tailwind CSS 등 모던 웹 기술에 대한 깊은 이해를 바탕으로 사용자 친화적인 웹 애플리케이션을 개발할 수 있습니다. 특히 성능 최적화와 접근성 개선에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 모던 웹 기술을 활용한 혁신적인 프로젝트에 참여하고 싶습니다. 사용자 경험을 최우선으로 하는 개발 문화에서 더욱 성장하여, 사용자들에게 가치 있는 서비스를 제공하는 개발자가 되고 싶습니다.
            """,
            "summary": "프론트엔드 개발에 대한 열정과 경험을 바탕으로 사용자 중심의 웹 서비스 개발에 기여하고 싶어 지원했습니다.",
            "keywords": ["프론트엔드", "React", "사용자경험", "웹개발"],
            "growthBackground": "컴퓨터공학을 전공하며 웹 개발에 대한 깊은 관심을 키워왔습니다. 대학 시절부터 다양한 프로젝트를 통해 실무 경험을 쌓았고, 특히 사용자 경험을 중시하는 프론트엔드 개발에 매료되어 이 분야로 진로를 정했습니다.",
            "motivation": "귀사의 혁신적인 웹 서비스와 사용자 중심의 개발 문화에 매료되어 지원하게 되었습니다. 특히 모던 웹 기술을 활용한 프로젝트에 참여하고 싶어 이번 기회를 통해 귀사에 기여하고 싶습니다.",
            "careerHistory": "2022년부터 ABC 스타트업에서 프론트엔드 개발자로 근무하며 React 기반의 웹 애플리케이션을 개발했습니다. 사용자 인터페이스 개선과 성능 최적화에 중점을 두어 작업했으며, 팀 내 기술 공유 세션을 주도했습니다."
        },
        {
            "extracted_text": """
지원동기
안녕하세요. 백엔드 개발자 이백엔드입니다. 귀사의 대규모 사용자를 대상으로 한 서비스 운영 경험을 배우고 싶어 지원했습니다.

성장배경
시스템 엔지니어링에 대한 관심으로 시작하여 백엔드 개발로 전향했습니다. 대용량 데이터 처리와 시스템 아키텍처 설계에 대한 깊은 이해를 바탕으로 안정적이고 확장 가능한 서비스를 구축하는 것을 목표로 합니다.

경력사항
2019년부터 XYZ 기업에서 백엔드 개발자로 근무하며 Java와 Spring 기반의 웹 서비스를 개발했습니다. 데이터베이스 설계와 API 개발을 주로 담당했으며, 최근에는 마이크로서비스 아키텍처 도입 프로젝트에 참여했습니다.

기술역량
Java, Spring Boot, MySQL, Redis 등 백엔드 기술에 대한 깊은 이해를 바탕으로 안정적이고 확장 가능한 서비스를 구축할 수 있습니다. 특히 대용량 트래픽 처리와 데이터베이스 최적화에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 마이크로서비스 아키텍처와 클라우드 인프라에 대한 실무 경험을 쌓고 싶습니다. 대규모 시스템 운영 경험을 통해 더욱 성장하여, 안정적이고 확장 가능한 서비스를 제공하는 개발자가 되고 싶습니다.
            """,
            "summary": "백엔드 개발에 대한 전문성과 시스템 설계 능력을 바탕으로 안정적이고 확장 가능한 서비스 구축에 기여하고 싶어 지원했습니다.",
            "keywords": ["백엔드", "Java", "Spring", "시스템설계"],
            "growthBackground": "시스템 엔지니어링에 대한 관심으로 시작하여 백엔드 개발로 전향했습니다. 대용량 데이터 처리와 시스템 아키텍처 설계에 대한 깊은 이해를 바탕으로 안정적이고 확장 가능한 서비스를 구축하는 것을 목표로 합니다.",
            "motivation": "귀사의 대규모 사용자를 대상으로 한 서비스 운영 경험을 배우고 싶어 지원했습니다. 특히 마이크로서비스 아키텍처와 클라우드 인프라에 대한 실무 경험을 쌓고 싶습니다.",
            "careerHistory": "2019년부터 XYZ 기업에서 백엔드 개발자로 근무하며 Java와 Spring 기반의 웹 서비스를 개발했습니다. 데이터베이스 설계와 API 개발을 주로 담당했으며, 최근에는 마이크로서비스 아키텍처 도입 프로젝트에 참여했습니다."
        },
        {
            "extracted_text": """
지원동기
안녕하세요. 풀스택 개발자 박풀스택입니다. 귀사의 혁신적인 기술 스택과 빠른 개발 문화에 매료되어 지원했습니다.

성장배경
웹 개발에 대한 전반적인 이해를 위해 프론트엔드와 백엔드를 모두 학습했습니다. JavaScript 생태계의 풍부함에 매료되어 Node.js 기반의 풀스택 개발을 전문으로 하고 있습니다.

경력사항
2021년부터 DEF 스타트업에서 풀스택 개발자로 근무하며 JavaScript 기반의 웹 애플리케이션을 개발했습니다. 프론트엔드와 백엔드 개발을 모두 담당하며 전체 시스템을 이해하고 최적화하는 경험을 쌓았습니다.

기술역량
JavaScript, Node.js, React, MongoDB 등 풀스택 기술에 대한 깊은 이해를 바탕으로 전체 시스템을 설계하고 개발할 수 있습니다. 특히 빠른 프로토타이핑과 MVP 개발에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 JavaScript 기반의 풀스택 개발 환경에서 더욱 성장하고 싶습니다. 혁신적인 기술을 활용한 빠른 개발 문화에서 더욱 성장하여, 사용자에게 가치 있는 서비스를 빠르게 제공하는 개발자가 되고 싶습니다.
            """,
            "summary": "JavaScript 기반의 풀스택 개발 경험을 바탕으로 전체 시스템을 이해하고 최적화하는 능력을 귀사에 기여하고 싶어 지원했습니다.",
            "keywords": ["풀스택", "JavaScript", "Node.js", "웹개발"],
            "growthBackground": "웹 개발에 대한 전반적인 이해를 위해 프론트엔드와 백엔드를 모두 학습했습니다. JavaScript 생태계의 풍부함에 매료되어 Node.js 기반의 풀스택 개발을 전문으로 하고 있습니다.",
            "motivation": "귀사의 혁신적인 기술 스택과 빠른 개발 문화에 매료되어 지원했습니다. 특히 JavaScript 기반의 풀스택 개발 환경에서 더욱 성장하고 싶어 이번 기회를 통해 귀사에 기여하고 싶습니다.",
            "careerHistory": "2021년부터 DEF 스타트업에서 풀스택 개발자로 근무하며 JavaScript 기반의 웹 애플리케이션을 개발했습니다. 프론트엔드와 백엔드 개발을 모두 담당하며 전체 시스템을 이해하고 최적화하는 경험을 쌓았습니다."
        },
        {
            "extracted_text": """
지원동기
안녕하세요. 데이터 엔지니어 최데이터입니다. 귀사의 대용량 데이터 처리 인프라와 데이터 기반 의사결정 문화에 매료되어 지원했습니다.

성장배경
통계학을 전공하며 데이터 분석에 대한 기초를 다졌고, 대용량 데이터 처리와 머신러닝에 대한 관심으로 데이터 엔지니어링 분야로 진입했습니다. 효율적인 데이터 파이프라인 구축과 분석을 목표로 합니다.

경력사항
2018년부터 GHI 대기업에서 데이터 엔지니어로 근무하며 대용량 데이터 처리 시스템을 구축했습니다. ETL 파이프라인 설계와 데이터 웨어하우스 구축을 주로 담당했으며, 최근에는 실시간 데이터 처리 시스템 도입 프로젝트를 주도했습니다.

기술역량
Python, Spark, Hadoop, Kafka 등 빅데이터 기술에 대한 깊은 이해를 바탕으로 대용량 데이터 처리 시스템을 구축할 수 있습니다. 특히 데이터 파이프라인 설계와 최적화에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 실시간 데이터 처리와 머신러닝 파이프라인 구축에 대한 경험을 쌓고 싶습니다. 데이터 기반 의사결정 문화에서 더욱 성장하여, 비즈니스에 가치 있는 인사이트를 제공하는 데이터 엔지니어가 되고 싶습니다.
            """,
            "summary": "대용량 데이터 처리와 파이프라인 구축 경험을 바탕으로 데이터 기반 의사결정에 기여하고 싶어 지원했습니다.",
            "keywords": ["데이터엔지니어", "빅데이터", "파이프라인", "데이터분석"],
            "growthBackground": "통계학을 전공하며 데이터 분석에 대한 기초를 다졌고, 대용량 데이터 처리와 머신러닝에 대한 관심으로 데이터 엔지니어링 분야로 진입했습니다. 효율적인 데이터 파이프라인 구축과 분석을 목표로 합니다.",
            "motivation": "귀사의 대용량 데이터 처리 인프라와 데이터 기반 의사결정 문화에 매료되어 지원했습니다. 특히 실시간 데이터 처리와 머신러닝 파이프라인 구축에 대한 경험을 쌓고 싶습니다.",
            "careerHistory": "2018년부터 GHI 대기업에서 데이터 엔지니어로 근무하며 대용량 데이터 처리 시스템을 구축했습니다. ETL 파이프라인 설계와 데이터 웨어하우스 구축을 주로 담당했으며, 최근에는 실시간 데이터 처리 시스템 도입 프로젝트를 주도했습니다."
        },
        {
            "extracted_text": """
지원동기
안녕하세요. AI 엔지니어 정AI입니다. 귀사의 혁신적인 AI 기술과 실제 서비스에 적용하는 경험을 배우고 싶어 지원했습니다.

성장배경
컴퓨터공학과 수학을 복수전공하며 머신러닝과 딥러닝에 대한 이론적 기초를 다졌습니다. 실제 비즈니스 문제를 해결하는 AI 모델 개발에 대한 관심으로 AI 엔지니어링 분야로 진입했습니다.

경력사항
2021년부터 JKL AI 스타트업에서 AI 엔지니어로 근무하며 다양한 머신러닝 모델을 개발했습니다. 자연어 처리와 추천 시스템 개발을 주로 담당했으며, 모델 성능 최적화와 MLOps 도입에 대한 경험을 쌓았습니다.

기술역량
Python, TensorFlow, PyTorch 등 AI 기술에 대한 깊은 이해를 바탕으로 다양한 머신러닝 모델을 개발할 수 있습니다. 특히 자연어 처리와 추천 시스템에 대한 경험이 풍부합니다.

입사 후 포부
귀사에서 자연어 처리와 컴퓨터 비전 분야에서의 실무 경험을 쌓고 싶습니다. 혁신적인 AI 기술을 활용한 서비스 개발에서 더욱 성장하여, 사용자에게 가치 있는 AI 서비스를 제공하는 엔지니어가 되고 싶습니다.
            """,
            "summary": "머신러닝과 딥러닝 모델 개발 경험을 바탕으로 혁신적인 AI 서비스 개발에 기여하고 싶어 지원했습니다.",
            "keywords": ["AI", "머신러닝", "딥러닝", "자연어처리"],
            "growthBackground": "컴퓨터공학과 수학을 복수전공하며 머신러닝과 딥러닝에 대한 이론적 기초를 다졌습니다. 실제 비즈니스 문제를 해결하는 AI 모델 개발에 대한 관심으로 AI 엔지니어링 분야로 진입했습니다.",
            "motivation": "귀사의 혁신적인 AI 기술과 실제 서비스에 적용하는 경험을 배우고 싶어 지원했습니다. 특히 자연어 처리와 컴퓨터 비전 분야에서의 실무 경험을 쌓고 싶습니다.",
            "careerHistory": "2021년부터 JKL AI 스타트업에서 AI 엔지니어로 근무하며 다양한 머신러닝 모델을 개발했습니다. 자연어 처리와 추천 시스템 개발을 주로 담당했으며, 모델 성능 최적화와 MLOps 도입에 대한 경험을 쌓았습니다."
        }
    ]

    try:
        # 지원자 정보 삽입
        inserted_applicants = []
        for i, applicant_data in enumerate(applicants_data):
            # 지원자 ID 생성
            applicant_id = str(ObjectId())

            # 이력서 데이터 준비
            resume_data = {
                "applicant_id": applicant_id,
                "extracted_text": resumes_data[i]["extracted_text"],
                "summary": resumes_data[i]["summary"],
                "keywords": resumes_data[i]["keywords"],
                "document_type": "resume",
                "basic_info": {
                    "emails": [applicant_data["email"]],
                    "phones": [applicant_data["phone"]],
                    "names": [applicant_data["name"]],
                    "urls": [applicant_data["github_url"]]
                },
                "file_metadata": {
                    "filename": f"{applicant_data['name']}_resume.pdf",
                    "size": 1024000,
                    "mime": "application/pdf",
                    "hash": f"resume_hash_{i}",
                    "created_at": datetime.now().isoformat(),
                    "modified_at": datetime.now().isoformat()
                },
                "created_at": datetime.now()
            }

            # 자기소개서 데이터 준비
            cover_letter_data = {
                "applicant_id": applicant_id,
                "extracted_text": cover_letters_data[i]["extracted_text"],
                "summary": cover_letters_data[i]["summary"],
                "keywords": cover_letters_data[i]["keywords"],
                "document_type": "cover_letter",
                "growthBackground": cover_letters_data[i]["growthBackground"],
                "motivation": cover_letters_data[i]["motivation"],
                "careerHistory": cover_letters_data[i]["careerHistory"],
                "basic_info": {
                    "emails": [applicant_data["email"]],
                    "phones": [applicant_data["phone"]],
                    "names": [applicant_data["name"]],
                    "urls": [applicant_data["github_url"]]
                },
                "file_metadata": {
                    "filename": f"{applicant_data['name']}_cover_letter.pdf",
                    "size": 512000,
                    "mime": "application/pdf",
                    "hash": f"cover_letter_hash_{i}",
                    "created_at": datetime.now().isoformat(),
                    "modified_at": datetime.now().isoformat()
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # 직접 MongoDB에 삽입
            resume_result = mongo_service.sync_db.resumes.insert_one(resume_data)
            resume_id = str(resume_result.inserted_id)

            cover_letter_result = mongo_service.sync_db.cover_letters.insert_one(cover_letter_data)
            cover_letter_id = str(cover_letter_result.inserted_id)

            # 지원자 데이터에 ID 연결
            applicant_data["resume_id"] = resume_id
            applicant_data["cover_letter_id"] = cover_letter_id
            applicant_data["created_at"] = datetime.now()
            applicant_data["updated_at"] = datetime.now()

                        # 지원자 삽입
            applicant_result = mongo_service.sync_db.applicants.insert_one(applicant_data)
            applicant_id_result = str(applicant_result.inserted_id)
            
            # 청크 데이터 자동 생성
            print(f"🔧 {applicant_data['name']} - 청크 데이터 생성 중...")
            
            # 이력서 청크 생성
            resume_chunks = create_resume_chunks_auto(resume_data, applicant_id_result, applicant_data["name"])
            print(f"   📄 이력서 청크 {resume_chunks}개 생성")
            
            # 자기소개서 청크 생성
            cover_letter_chunks = create_cover_letter_chunks_auto(cover_letter_data, applicant_id_result, applicant_data["name"])
            print(f"   📝 자기소개서 청크 {cover_letter_chunks}개 생성")
            
            inserted_applicants.append({
                "applicant_id": applicant_id_result,
                "name": applicant_data["name"],
                "position": applicant_data["position"],
                "resume_id": resume_id,
                "cover_letter_id": cover_letter_id,
                "resume_chunks": resume_chunks,
                "cover_letter_chunks": cover_letter_chunks
            })
            
            print(f"✅ {applicant_data['name']} ({applicant_data['position']}) - 지원자 정보 및 청크 생성 완료")
            print(f"   - 지원자 ID: {applicant_id_result}")
            print(f"   - 이력서 ID: {resume_id}")
            print(f"   - 자기소개서 ID: {cover_letter_id}")
            print()

        print(f"🎉 총 {len(inserted_applicants)}명의 지원자 정보가 성공적으로 생성되었습니다!")
        print("\n📋 생성된 지원자 목록:")
        for i, applicant in enumerate(inserted_applicants, 1):
            print(f"{i}. {applicant['name']} ({applicant['position']})")
            print(f"   지원자 ID: {applicant['applicant_id']}")
            print(f"   이력서 ID: {applicant['resume_id']}")
            print(f"   자기소개서 ID: {applicant['cover_letter_id']}")
            print()

        return inserted_applicants

    except Exception as e:
        print(f"❌ 지원자 정보 생성 중 오류 발생: {str(e)}")
        return None

def create_resume_chunks_auto(resume_data, applicant_id, applicant_name):
    """이력서 청크 자동 생성"""
    mongo_service = MongoService()
    
    text = resume_data.get("extracted_text", "")
    if not text:
        return 0
    
    # 청크 설정
    chunk_size = 500
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # 청크 문서 생성
        chunk_doc = {
            "applicant_id": applicant_id,
            "document_id": resume_data.get("applicant_id"),  # 임시로 applicant_id 사용
            "document_type": "resume",
            "chunk_index": chunk_index,
            "content": chunk_text,
            "metadata": {
                "applicant_name": applicant_name,
                "document_title": f"{applicant_name}의 이력서",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "total_chunks": len(text) // chunk_size + 1,
                "split_type": "fixed_size",
                "source": "resume_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 청크 저장
        mongo_service.sync_db.resume_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        
        if start >= len(text):
            break
    
    return len(chunks)

def create_cover_letter_chunks_auto(cover_letter_data, applicant_id, applicant_name):
    """자기소개서 청크 자동 생성"""
    mongo_service = MongoService()
    
    text = cover_letter_data.get("extracted_text", "")
    if not text:
        return 0
    
    # 청크 설정
    chunk_size = 400
    chunk_overlap = 50
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # 청크 문서 생성
        chunk_doc = {
            "applicant_id": applicant_id,
            "document_id": cover_letter_data.get("applicant_id"),  # 임시로 applicant_id 사용
            "document_type": "cover_letter",
            "chunk_index": chunk_index,
            "content": chunk_text,
            "metadata": {
                "applicant_name": applicant_name,
                "document_title": f"{applicant_name}의 자기소개서",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "total_chunks": len(text) // chunk_size + 1,
                "split_type": "fixed_size",
                "source": "cover_letter_extraction"
            },
            "created_at": datetime.now()
        }
        
        # MongoDB에 청크 저장
        mongo_service.sync_db.cover_letter_chunks.insert_one(chunk_doc)
        chunks.append(chunk_doc)
        chunk_index += 1
        
        start = end - chunk_overlap if chunk_overlap > 0 else end
        
        if start >= len(text):
            break
    
    return len(chunks)

if __name__ == "__main__":
    create_chunk_analysis_applicants()
