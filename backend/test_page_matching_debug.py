#!/usr/bin/env python3
import sys
import os
import json
import requests

# Add the chatbot path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot', 'chatbot'))

from core.page_matcher import PageMatcher, PageMatch

def test_page_matcher():
    """페이지 매처를 직접 테스트"""
    print("🔍 페이지 매처 테스트 시작...")
    
    page_matcher = PageMatcher()
    
    test_cases = [
        "kyungho222 포트폴리오 분석결과를 보여줘",
        "지원자 관리 확인하기",
        "면접 일정 보기",
        "채용공고 등록하기",
        "포트폴리오 분석"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 테스트 입력: {test_input}")
        result = page_matcher.match_page(test_input)
        
        if result:
            print(f"✅ 매칭 결과:")
            print(f"   - 페이지: {result.page_name}")
            print(f"   - 경로: {result.page_path}")
            print(f"   - 신뢰도: {result.confidence}")
            print(f"   - 이유: {result.reason}")
            print(f"   - 추가 데이터: {result.additional_data}")
        else:
            print("❌ 매칭 실패")

def test_agent_system_integration():
    """에이전트 시스템과의 통합 테스트"""
    print("\n🤖 에이전트 시스템 통합 테스트...")
    
    test_input = "kyungho222 포트폴리오 분석결과를 보여줘"
    
    # 백엔드 API 호출
    try:
        response = requests.post(
            "http://localhost:8000/chatbot/chat",
            json={
                "message": test_input,
                "session_id": "test_session"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API 응답 성공:")
            print(f"   - 응답 타입: {result.get('type')}")
            print(f"   - 메시지: {result.get('response')}")
            
            if result.get('type') == 'page_navigation':
                page_action = result.get('page_action', {})
                print(f"   - 페이지 액션: {page_action}")
                print(f"   - 경로: {page_action.get('path')}")
                print(f"   - 추가 데이터: {page_action.get('additional_data')}")
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 페이지 매칭 디버그 테스트 시작")
    print("=" * 50)
    
    test_page_matcher()
    test_agent_system_integration()
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")
