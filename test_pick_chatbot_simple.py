import requests
import json

# 픽톡 API 간단 테스트
print("🤖 픽톡 API 간단 테스트")
print("=" * 40)

try:
    # 1. 기본 채팅 테스트
    print("\n1. 채팅 API 테스트...")
    response = requests.post(
        "http://localhost:8000/api/pick-chatbot/chat",
        json={
            "message": "안녕하세요",
            "session_id": "test_001"
        },
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("✅ 채팅 API 성공!")
    else:
        print(f"❌ 채팅 API 실패: {response.status_code}")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n테스트 완료!")
