import requests
import json

def test_langgraph_api():
    url = "http://localhost:8000/api/langgraph/agent"
    
    payload = {
        "message": "저희 회사는 성장 가능성이 높은 스타트업으로서, 경력 3년 이상의 백엔드 개발자를 모집하고 있습니다. 주로 Python과 Django 프레임워크를 사용하며, 대규모 트래픽 처리 경험이 있는 분을 환영합니다. 팀원들과 원활한 소통이 가능하며, 문제 해결에 적극적인 태도를 가진 인재를 찾고 있습니다. 적극적인 자기 개발 의지와 새로운 기술 습득에 열정이 있는 분을 우대합니다. 지원 시 포트폴리오와 Github 링크를 함께 제출해 주세요.",
        "conversation_history": [],
        "session_id": "test-session"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🌐 LangGraph API 테스트 시작...")
        print(f"📤 요청 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"📥 응답 상태 코드: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 성공! 응답 데이터:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 추출된 필드 확인
            if 'extracted_fields' in result:
                print(f"🔍 추출된 필드: {result['extracted_fields']}")
            else:
                print("⚠️ 추출된 필드가 없습니다.")
                
        else:
            print(f"❌ 오류! 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"💥 예외 발생: {e}")

if __name__ == "__main__":
    test_langgraph_api()
