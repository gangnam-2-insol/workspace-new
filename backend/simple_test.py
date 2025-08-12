#!/usr/bin/env python3
"""
간단한 자소서 분석 API 테스트
"""

import requests
import json

def test_health():
    """헬스 체크 테스트"""
    print("🏥 헬스 체크 테스트...")
    try:
        response = requests.get("http://localhost:8000/api/upload/health")
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 서비스 상태: {data['status']}")
            print(f"✅ Gemini API 설정: {data['gemini_api_configured']}")
            print(f"✅ 지원 파일 형식: {data['supported_formats']}")
            print(f"✅ 최대 파일 크기: {data['max_file_size_mb']}MB")
            return True
        else:
            print(f"❌ 헬스 체크 실패: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def test_simple_summary():
    """간단한 텍스트 요약 테스트"""
    print("\n📝 간단한 텍스트 요약 테스트...")
    
    test_text = "안녕하세요. 저는 3년간의 웹 개발 경험을 바탕으로 귀사에 프론트엔드 개발자로 지원하게 된 김개발입니다."
    
    try:
        data = {
            "content": test_text,
            "summary_type": "general"
        }
        
        response = requests.post(
            "http://localhost:8000/api/upload/summarize",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 요약: {result['summary']}")
            print(f"✅ 키워드: {result['keywords']}")
            print(f"✅ 신뢰도: {result['confidence_score']}")
            return True
        else:
            print(f"❌ 요약 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 요약 처리 오류: {e}")
        return False

def test_cover_letter_analysis():
    """자소서 분석 테스트"""
    print("\n📄 자소서 분석 테스트...")
    
    cover_letter = """
안녕하세요. 저는 3년간의 웹 개발 경험을 바탕으로 귀사에 프론트엔드 개발자로 지원하게 된 김개발입니다.

저는 React와 TypeScript를 주력으로 사용하여 사용자 경험을 향상시키는 웹 애플리케이션을 개발해왔습니다. 
특히 이전 회사에서 진행한 이커머스 플랫폼 리뉴얼 프로젝트에서는 팀 리더로서 6명의 개발자와 함께 
3개월간의 개발 기간을 거쳐 매출 25% 증가를 달성했습니다.

이 프로젝트에서 저는 사용자 인터페이스 개선과 성능 최적화에 집중했습니다. 
Lighthouse 성능 점수를 45점에서 92점으로 향상시켰고, 
사용자 체류 시간을 평균 3분에서 7분으로 늘렸습니다.
"""
    
    try:
        data = {
            "content": cover_letter,
            "summary_type": "general"
        }
        
        response = requests.post(
            "http://localhost:8000/api/upload/summarize",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 요약: {result['summary'][:100]}...")
            print(f"✅ 키워드: {', '.join(result['keywords'][:5])}")
            print(f"✅ 신뢰도: {result['confidence_score']}")
            return True
        else:
            print(f"❌ 분석 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 분석 처리 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 자소서 분석 API 테스트 시작...\n")
    
    # 1. 헬스 체크
    health_ok = test_health()
    
    if health_ok:
        # 2. 간단한 요약 테스트
        summary_ok = test_simple_summary()
        
        # 3. 자소서 분석 테스트
        analysis_ok = test_cover_letter_analysis()
        
        print(f"\n📊 테스트 결과 요약:")
        print(f"헬스 체크: {'✅' if health_ok else '❌'}")
        print(f"간단 요약: {'✅' if summary_ok else '❌'}")
        print(f"자소서 분석: {'✅' if analysis_ok else '❌'}")
        
        if all([health_ok, summary_ok, analysis_ok]):
            print("\n🎉 모든 테스트가 성공했습니다!")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    else:
        print("\n❌ 서버 연결에 실패했습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
