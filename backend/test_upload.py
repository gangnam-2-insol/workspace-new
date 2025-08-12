#!/usr/bin/env python3
"""
업로드 API 테스트 스크립트
"""

import requests
import tempfile
import os

def test_health_check():
    """헬스 체크 테스트"""
    try:
        response = requests.get('http://localhost:8000/api/upload/health')
        print("✅ 헬스 체크 성공:", response.json())
        return True
    except Exception as e:
        print("❌ 헬스 체크 실패:", e)
        return False

def test_text_summarization():
    """텍스트 요약 테스트"""
    try:
        data = {
            "content": "안녕하세요. 저는 3년차 백엔드 개발자입니다. Python, FastAPI, MongoDB를 주로 사용하며, 최근에는 AWS 클라우드 서비스를 활용한 프로젝트를 진행했습니다. 팀 프로젝트에서 API 설계와 데이터베이스 최적화를 담당했으며, 성능 개선을 통해 응답 속도를 30% 단축시켰습니다.",
            "summary_type": "general"
        }
        response = requests.post('http://localhost:8000/api/upload/summarize', json=data)
        print("✅ 텍스트 요약 성공:", response.json())
        return True
    except Exception as e:
        print("❌ 텍스트 요약 실패:", e)
        return False

def test_file_upload():
    """파일 업로드 및 요약 테스트"""
    try:
        # 임시 텍스트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
이력서 - 김개발

개인정보
이름: 김개발
이메일: kim.dev@email.com
연락처: 010-1234-5678
GitHub: github.com/kimdev

학력
- 서울대학교 컴퓨터공학과 졸업 (2018-2022)
- 학점: 4.2/4.5

경력
- ABC테크 (2022-현재)
  * 백엔드 개발자
  * Python, FastAPI, PostgreSQL 사용
  * API 설계 및 개발
  * 성과: 시스템 응답 속도 40% 개선

기술스택
- 프로그래밍 언어: Python, JavaScript, Java
- 프레임워크: FastAPI, Django, Spring Boot
- 데이터베이스: PostgreSQL, MongoDB, Redis
- 클라우드: AWS, Docker, Kubernetes

프로젝트
1. 이커머스 플랫폼 개발 (2023)
   - 역할: 백엔드 개발
   - 기술: Python, FastAPI, PostgreSQL
   - 성과: 월 매출 20% 증가

2. 실시간 채팅 시스템 (2022)
   - 역할: 전체 개발
   - 기술: Node.js, Socket.io, MongoDB
   - 성과: 동시 접속자 1000명 지원
            """)
            temp_file_path = f.name

        # 파일 업로드 테스트
        with open(temp_file_path, 'rb') as f:
            files = {'file': f}
            data = {'summary_type': 'general'}
            response = requests.post('http://localhost:8000/api/upload/file', files=files, data=data)
            
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        print("✅ 파일 업로드 성공:", response.json())
        return True
    except Exception as e:
        print("❌ 파일 업로드 실패:", e)
        return False

def test_detailed_analysis():
    """상세 분석 테스트"""
    try:
        # 임시 텍스트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
이력서 - 김개발

개인정보
이름: 김개발
이메일: kim.dev@email.com
연락처: 010-1234-5678
GitHub: github.com/kimdev
LinkedIn: linkedin.com/in/kimdev

학력
- 서울대학교 컴퓨터공학과 졸업 (2018-2022)
- 학점: 4.2/4.5

경력
- ABC테크 (2022-현재)
  * 백엔드 개발자
  * Python, FastAPI, PostgreSQL 사용
  * API 설계 및 개발
  * 성과: 시스템 응답 속도 40% 개선, 월 매출 20% 증가

기술스택
- 프로그래밍 언어: Python, JavaScript, Java
- 프레임워크: FastAPI, Django, Spring Boot
- 데이터베이스: PostgreSQL, MongoDB, Redis
- 클라우드: AWS, Docker, Kubernetes

프로젝트
1. 이커머스 플랫폼 개발 (2023)
   - 역할: 백엔드 개발
   - 기술: Python, FastAPI, PostgreSQL
   - 성과: 월 매출 20% 증가, API 응답 속도 30% 개선

2. 실시간 채팅 시스템 (2022)
   - 역할: 전체 개발
   - 기술: Node.js, Socket.io, MongoDB
   - 성과: 동시 접속자 1000명 지원

자기소개서

지원 동기
ABC테크의 혁신적인 기술 문화와 사용자 중심의 서비스 개발 철학에 깊이 공감하여 지원하게 되었습니다. 특히 AI 기술을 활용한 개인화 서비스 개발 분야에서 제가 가진 경험과 기술을 발휘할 수 있을 것이라 확신합니다.

문제 해결 사례
이전 회사에서 레거시 시스템으로 인한 성능 문제가 발생했을 때, STAR 기법을 활용하여 문제를 해결했습니다. Situation: API 응답 속도가 평균 3초로 사용자 불만이 증가. Task: 2개월 내 응답 속도를 1초 이하로 개선. Action: 데이터베이스 쿼리 최적화, 캐싱 시스템 도입, API 구조 개선. Result: 응답 속도 67% 개선, 사용자 만족도 25% 향상.

기술적 성과
- 시스템 성능 개선: API 응답 속도 40% 단축
- 비즈니스 성과: 월 매출 20% 증가
- 사용자 경험: 사용자 만족도 25% 향상

포트폴리오

프로젝트 1: 이커머스 플랫폼
- 기간: 2023.01-2023.06 (6개월)
- 팀 규모: 5명 (백엔드 2명, 프론트엔드 2명, 디자이너 1명)
- 역할: 백엔드 개발 및 API 설계
- 기술 스택: Python, FastAPI, PostgreSQL, Redis, AWS
- 주요 기능: 상품 관리, 주문 처리, 결제 시스템, 사용자 인증
- 성과: 월 매출 20% 증가, API 응답 속도 30% 개선
- 개인 기여도: 백엔드 전체 개발 (50%)

프로젝트 2: 실시간 채팅 시스템
- 기간: 2022.07-2022.12 (6개월)
- 팀 규모: 3명 (풀스택 2명, 디자이너 1명)
- 역할: 전체 개발 및 배포
- 기술 스택: Node.js, Socket.io, MongoDB, AWS
- 주요 기능: 실시간 메시징, 파일 공유, 그룹 채팅
- 성과: 동시 접속자 1000명 지원, 메시지 전송 지연 0.1초 이하
- 개인 기여도: 전체 개발 (80%)

문서화 및 유지보수
- 모든 프로젝트에 상세한 README 작성
- API 문서 자동 생성 시스템 구축
- Git을 활용한 버전 관리 및 협업
- Docker 컨테이너화로 배포 자동화
            """)
            temp_file_path = f.name

        # 상세 분석 테스트
        with open(temp_file_path, 'rb') as f:
            files = {'file': f}
            data = {'document_type': 'resume'}
            response = requests.post('http://localhost:8000/api/upload/analyze', files=files, data=data)
            
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        print("✅ 상세 분석 성공:", response.json())
        return True
    except Exception as e:
        print("❌ 상세 분석 실패:", e)
        return False

def main():
    """모든 테스트 실행"""
    print("🚀 업로드 API 테스트 시작\n")
    
    tests = [
        ("헬스 체크", test_health_check),
        ("텍스트 요약", test_text_summarization),
        ("파일 업로드", test_file_upload),
        ("상세 분석", test_detailed_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name} 테스트 중...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name} {'성공' if success else '실패'}\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}\n")
            results.append((test_name, False))
    
    # 결과 요약
    print("📊 테스트 결과 요약:")
    print("=" * 50)
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    print(f"\n전체: {success_count}/{total_count} 테스트 성공")

if __name__ == "__main__":
    main()
