#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    url = "http://localhost:8000/api/langgraph/agent"
    
    payload = {
        "message": "저희 회사는 성장 가능성이 높은 스타트업으로서, 경력 3년 이상의 백엔드 개발자를 모집하고 있습니다. 주로 Python과 Django 프레임워크를 사용하며, 대규모 트래픽 처리 경험이 있는 분을 환영합니다. 팀원들과 원활한 소통이 가능하며, 문제 해결에 적극적인 태도를 가진 인재를 찾고 있습니다. 적극적인 자기 개발 의지와 새로운 기술 습득에 열정이 있는 분을 우대합니다. 지원 시 포트폴리오와 Github 링크를 함께 제출해 주세요.",
        "conversation_history": []
    }
    
    try:
        print("🧪 API 테스트 시작...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 응답 성공!")
            print(f"📊 의도: {result.get('intent')}")
            print(f"💬 응답: {result.get('response', '')[:100]}...")
            
            if result.get('intent') == 'recruit':
                print("🎉 SUCCESS: 올바르게 'recruit'로 분류됨!")
            else:
                print(f"❌ FAIL: 'recruit'이 아닌 '{result.get('intent')}'로 분류됨")
        else:
            print(f"❌ 오류: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    test_api()
