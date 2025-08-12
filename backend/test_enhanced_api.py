"""
향상된 필드 추출기가 통합된 API 테스트
"""

import requests
import json

def test_enhanced_api():
    """향상된 필드 추출기가 통합된 API 테스트"""
    
    # 테스트 케이스
    test_text = "프론트엔드 개발자 모집 공고입니다. React와 Typescript를 활용한 웹 애플리케이션 개발 경험이 2년 이상인 분을 우대하며, 사용자 경험(UX) 개선에 관심이 많고 세심한 UI 구현 능력을 갖춘 분을 찾고 있습니다. 애자일(Agile) 개발 환경에 적응력이 좋고, 팀 내 협업 및 코드 리뷰에 적극적으로 참여할 수 있는 분이면 더욱 좋습니다. 자바스크립트 라이브러리 및 최신 트렌드에 대한 이해도가 높은 지원자를 환영합니다."
    
    url = "http://localhost:8000/api/langgraph/agent"
    
    payload = {
        "message": test_text,
        "mode": "langgraph"
    }
    
    print("🚀 향상된 필드 추출기 API 테스트 시작")
    print(f"📝 테스트 텍스트: {test_text}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API 응답 성공!")
            print(f"🎯 의도: {result.get('intent', 'N/A')}")
            print(f"💬 응답: {result.get('response', 'N/A')}")
            
            # 추출된 필드 확인
            if 'extracted_fields' in result:
                extracted_fields = result['extracted_fields']
                print(f"\n📊 추출된 필드 ({len(extracted_fields)}개):")
                for key, value in extracted_fields.items():
                    print(f"   {key}: {value}")
            else:
                print("\n⚠️ 추출된 필드가 없습니다.")
                
        else:
            print(f"❌ API 오류: {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

if __name__ == "__main__":
    test_enhanced_api()
