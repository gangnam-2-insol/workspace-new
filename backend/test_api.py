#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_title_generation():
    """제목 생성 API를 테스트합니다."""
    
    url = "http://localhost:5000/api/pick-chatbot/generate-title"
    
    # 테스트 데이터
    test_data = {
        "form_data": {
            "department": "개발팀",
            "position": "프론트엔드 개발자",
            "mainDuties": "React, Vue.js 개발"
        },
        "content": "개발팀 프론트엔드 개발자 채용"
    }
    
    try:
        print("🔍 API 테스트 시작...")
        print(f"URL: {url}")
        print(f"데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        # POST 요청
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        print(f"\n📊 응답 상태 코드: {response.status_code}")
        print(f"📋 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 성공! 응답 데이터:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"❌ 실패! 응답 내용:")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간이 초과되었습니다.")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def test_server_status():
    """서버 상태를 확인합니다."""
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ 서버 응답: {response.status_code}")
        return True
    except:
        print("❌ 서버에 연결할 수 없습니다.")
        return False

if __name__ == "__main__":
    print("🧪 API 테스트 도구")
    print("="*50)
    
    # 서버 상태 확인
    if test_server_status():
        print("\n🔄 제목 생성 API 테스트...")
        test_title_generation()
    else:
        print("\n❌ 서버가 실행되지 않았습니다.")
        print("다음 명령어로 서버를 시작해주세요:")
        print("python main.py")
