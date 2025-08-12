#!/usr/bin/env python3
"""
자소서 분석 기능 테스트 스크립트
"""

import requests
import json
from typing import Dict, Any

# 테스트용 자소서 데이터
SAMPLE_COVER_LETTERS = {
    "개발자_자소서": """
안녕하세요. 저는 3년간의 웹 개발 경험을 바탕으로 귀사에 프론트엔드 개발자로 지원하게 된 김개발입니다.

저는 React와 TypeScript를 주력으로 사용하여 사용자 경험을 향상시키는 웹 애플리케이션을 개발해왔습니다. 
특히 이전 회사에서 진행한 이커머스 플랫폼 리뉴얼 프로젝트에서는 팀 리더로서 6명의 개발자와 함께 
3개월간의 개발 기간을 거쳐 매출 25% 증가를 달성했습니다.

이 프로젝트에서 저는 사용자 인터페이스 개선과 성능 최적화에 집중했습니다. 
Lighthouse 성능 점수를 45점에서 92점으로 향상시켰고, 
사용자 체류 시간을 평균 3분에서 7분으로 늘렸습니다.

또한 새로운 기술에 대한 학습에 적극적이며, 최근에는 Next.js 13의 App Router와 
Server Components를 활용한 프로젝트를 진행하여 팀원들과 함께 지식을 공유했습니다.

귀사의 혁신적인 제품 개발 문화와 사용자 중심의 서비스 철학에 깊이 공감하며, 
제가 가진 기술력과 경험을 바탕으로 귀사의 성장에 기여하고 싶습니다.
""",
    
    "디자이너_자소서": """
안녕하세요. UI/UX 디자이너로 지원한 이디자인입니다.

저는 4년간 다양한 디지털 제품의 사용자 경험을 설계해왔습니다. 
특히 모바일 앱 디자인에 전문성을 가지고 있으며, 
사용자 리서치부터 프로토타이핑, 최종 디자인까지 전 과정을 담당해왔습니다.

주요 프로젝트로는 건강 관리 앱 '헬시케어'의 UX/UI 디자인이 있습니다. 
이 프로젝트에서 저는 50명의 사용자와의 인터뷰를 통해 
사용자 니즈를 파악하고, 이를 바탕으로 직관적이고 접근성 높은 인터페이스를 설계했습니다.

결과적으로 앱 스토어 평점이 3.2점에서 4.7점으로 향상되었고, 
사용자 이탈률을 40%에서 15%로 줄였습니다.

저는 항상 사용자 중심의 사고를 바탕으로 디자인하며, 
데이터 기반의 의사결정을 통해 지속적으로 개선해나가는 것을 중요하게 생각합니다.

귀사의 창의적이고 혁신적인 제품 개발 문화에 참여하여 
사용자들에게 더 나은 경험을 제공하고 싶습니다.
""",
    
    "마케터_자소서": """
안녕하세요. 디지털 마케팅 전문가로 지원한 박마케팅입니다.

저는 5년간 B2B SaaS 기업에서 디지털 마케팅을 담당하며 
고객 확보와 브랜드 인지도 향상에 기여해왔습니다.

주요 성과로는 이전 회사에서 진행한 콘텐츠 마케팅 전략 수립과 실행이 있습니다. 
블로그, 웨비나, 소셜미디어를 활용한 콘텐츠 마케팅을 통해 
월간 웹사이트 트래픽을 15,000에서 45,000으로 증가시켰고, 
리드 생성량을 3배 향상시켰습니다.

또한 Google Ads와 Facebook Ads를 활용한 유료 광고 캠페인을 통해 
ROAS(광고 투자 수익률)를 350% 달성했으며, 
고객 획득 비용(CAC)을 30% 절감했습니다.

저는 데이터 분석을 기반으로 한 의사결정과 
A/B 테스트를 통한 지속적인 개선을 중요하게 생각합니다.

귀사의 혁신적인 제품을 더 많은 고객에게 알리고, 
성장에 기여하고 싶습니다.
"""
}

def test_cover_letter_analysis():
    """자소서 분석 API 테스트"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 자소서 분석 기능 테스트를 시작합니다...\n")
    
    # 1. 헬스 체크
    print("1️⃣ 헬스 체크...")
    try:
        response = requests.get(f"{base_url}/api/upload/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 서비스 상태: {health_data['status']}")
            print(f"✅ Gemini API 설정: {health_data['gemini_api_configured']}")
            print(f"✅ 지원 파일 형식: {health_data['supported_formats']}")
            print(f"✅ 최대 파일 크기: {health_data['max_file_size_mb']}MB\n")
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 텍스트 직접 요약 테스트
    print("2️⃣ 텍스트 직접 요약 테스트...")
    for title, content in SAMPLE_COVER_LETTERS.items():
        print(f"\n📝 {title} 분석 중...")
        
        try:
            summary_data = {
                "content": content,
                "summary_type": "general"
            }
            
            response = requests.post(
                f"{base_url}/api/upload/summarize",
                json=summary_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 요약: {result['summary'][:100]}...")
                print(f"✅ 키워드: {', '.join(result['keywords'][:5])}")
                print(f"✅ 신뢰도: {result['confidence_score']:.2f}")
                print(f"✅ 처리시간: {result['processing_time']:.2f}초")
            else:
                print(f"❌ 요약 실패: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 요약 처리 오류: {e}")
    
    print("\n🎉 자소서 분석 테스트 완료!")

def test_file_upload_analysis():
    """파일 업로드 분석 테스트 (선택사항)"""
    print("\n📁 파일 업로드 분석 테스트는 별도로 진행할 수 있습니다.")
    print("   - PDF, DOC, DOCX, TXT 파일을 /api/upload/analyze 엔드포인트로 전송")
    print("   - document_type 파라미터로 'cover_letter' 지정")

if __name__ == "__main__":
    test_cover_letter_analysis()
    test_file_upload_analysis()
