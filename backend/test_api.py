#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 테스트 스크립트
"""

import requests
import json

def test_langgraph_agent():
    """랭그래프 에이전트 API 테스트"""
    
    url = "http://localhost:8000/api/langgraph/agent"
    
    # 테스트할 문장
    test_message = "저희 회사는 성장 가능성이 높은 스타트업으로서, 경력 3년 이상의 백엔드 개발자를 모집하고 있습니다. 주로 Python과 Django 프레임워크를 사용하며, 대규모 트래픽 처리 경험이 있는 분을 환영합니다. 팀원들과 원활한 소통이 가능하며, 문제 해결에 적극적인 태도를 가진 인재를 찾고 있습니다. 적극적인 자기 개발 의지와 새로운 기술 습득에 열정이 있는 분을 우대합니다. 지원 시 포트폴리오와 Github 링크를 함께 제출해 주세요."
    
    payload = {
        "message": test_message,
        "conversation_history": []
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 랭그래프 에이전트 API 테스트 시작")
        print(f"📝 테스트 메시지: {test_message[:50]}...")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 응답 성공!")
            print(f"📊 의도: {result.get('intent', 'N/A')}")
            print(f"💬 응답: {result.get('response', 'N/A')[:100]}...")
            print(f"🎯 신뢰도: {result.get('confidence', 'N/A')}")
            print(f"📋 추출된 필드: {result.get('extracted_fields', {})}")
            
            # 의도 확인
            if result.get('intent') == 'recruit':
                print("✅ SUCCESS: 올바르게 'recruit' 의도로 분류됨!")
            else:
                print(f"❌ FAIL: 예상 'recruit'이지만 '{result.get('intent')}'로 분류됨")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_langgraph_agent()
