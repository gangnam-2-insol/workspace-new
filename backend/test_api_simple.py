import requests

def test_api():
    try:
        print("🔍 API 테스트 시작...")
        response = requests.get("http://localhost:8000/api/applicants")
        print(f"📡 응답 상태: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 응답 성공: {data}")
        else:
            print(f"❌ API 응답 실패: {response.text}")
    except Exception as e:
        print(f"❌ 연결 오류: {e}")

if __name__ == "__main__":
    test_api()
