"""
향상된 필드 추출기 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.core.enhanced_field_extractor import enhanced_extractor

def test_enhanced_extractor():
    """향상된 필드 추출기 테스트"""
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "프론트엔드 개발자 모집 (기술스택 중심)",
            "text": "프론트엔드 개발자 모집 공고입니다. React와 Typescript를 활용한 웹 애플리케이션 개발 경험이 2년 이상인 분을 우대하며, 사용자 경험(UX) 개선에 관심이 많고 세심한 UI 구현 능력을 갖춘 분을 찾고 있습니다. 애자일(Agile) 개발 환경에 적응력이 좋고, 팀 내 협업 및 코드 리뷰에 적극적으로 참여할 수 있는 분이면 더욱 좋습니다. 자바스크립트 라이브러리 및 최신 트렌드에 대한 이해도가 높은 지원자를 환영합니다."
        },
        {
            "name": "백엔드 개발자 모집 (경력 중심)",
            "text": "저희 회사는 성장 가능성이 높은 스타트업으로서, 경력 3년 이상의 백엔드 개발자를 모집하고 있습니다. 주로 Python과 Django 프레임워크를 사용하며, 대규모 트래픽 처리 경험이 있는 분을 환영합니다. 팀원들과 원활한 소통이 가능하며, 문제 해결에 적극적인 태도를 가진 인재를 찾고 있습니다. 적극적인 자기 개발 의지와 새로운 기술 습득에 열정이 있는 분을 우대합니다. 지원 시 포트폴리오와 Github 링크를 함께 제출해 주세요."
        },
        {
            "name": "풀스택 개발자 모집 (제출서류 포함)",
            "text": "풀스택 개발자를 모집합니다. React, Node.js, MongoDB를 사용한 프로젝트 경험이 있는 분을 우대합니다. 신입 및 경력 지원자 모두 환영하며, 기본적인 컴퓨터 활용 능력과 긍정적인 마인드를 갖춘 분을 찾고 있습니다. 연봉은 경력과 역량에 따라 협의 후 결정되며, 근무지는 서울 강남구입니다. 제출 서류로는 이력서, 자기소개서, 관련 자격증 사본이 필요합니다."
        },
        {
            "name": "데이터 분석가 모집 (AI/ML 중심)",
            "text": "데이터 분석가를 모집합니다. Python, Pandas, NumPy를 활용한 데이터 분석 경험이 1년 이상인 분을 우대합니다. 머신러닝과 딥러닝에 대한 이해도가 높고, TensorFlow나 PyTorch 사용 경험이 있는 분이면 더욱 좋습니다. 통계적 사고와 비즈니스 인사이트 도출 능력을 갖춘 분을 찾고 있습니다."
        },
        {
            "name": "DevOps 엔지니어 모집 (인프라 중심)",
            "text": "DevOps 엔지니어를 모집합니다. AWS, Docker, Kubernetes 사용 경험이 있는 분을 우대합니다. CI/CD 파이프라인 구축 및 운영 경험이 2년 이상인 분을 찾고 있습니다. 인프라 자동화와 모니터링 시스템 구축에 관심이 많은 분이면 더욱 좋습니다. Git, Jenkins, Ansible 사용 경험이 있는 분을 환영합니다."
        }
    ]
    
    print("🚀 향상된 필드 추출기 테스트 시작\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 테스트 케이스 {i}: {test_case['name']}")
        print(f"📝 입력 텍스트: {test_case['text']}")
        print("-" * 80)
        
        # 향상된 필드 추출 실행
        result = enhanced_extractor.extract_fields_enhanced(test_case['text'])
        
        print(f"✅ 추출 결과:")
        for key, value in result.items():
            print(f"   {key}: {value}")
        
        print(f"📊 추출된 필드 수: {len(result)}개")
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_enhanced_extractor()
