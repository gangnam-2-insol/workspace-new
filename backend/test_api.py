import requests
import os

def test_api():
    """API 테스트 함수"""
    url = "http://localhost:8000/api/integrated-ocr/upload-multiple-documents"
    
    # 테스트용 데이터
    data = {
        'name': '테스트',
        'email': 'test@test.com',
        'phone': '010-1234-5678'
    }
    
    # 파일이 없어도 API 응답 확인
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()

