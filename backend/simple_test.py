#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
"""

import requests
import json

def test_langgraph_api():
    """LangGraph API를 테스트합니다."""
    
    base_url = "http://localhost:8000"
    endpoint = "/api/langgraph/agent"
    
    test_data = {
        "message": "채용공고 작성해줘. 마케팅 담당자 2명 뽑고 싶어요, 연봉 3500만원",
        "conversation_history": [],
        "session_id": "test123"
    }
    
    print("🧪 LangGraph API 테스트 시작")
    print(f"엔드포인트: {endpoint}")
    print(f"입력: {test_data['message']}")
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 응답 성공!")
            print(f"Intent: {data.get('intent', 'N/A')}")
            print(f"Extracted Fields: {data.get('extracted_fields', {})}")
            print(f"Response: {data.get('response', 'N/A')[:200]}...")
        else:
            print(f"❌ 오류: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
    
    print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_langgraph_api()
