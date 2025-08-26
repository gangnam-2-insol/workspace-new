#!/usr/bin/env python3
"""
픽톡(Pick Chatbot) 간단 테스트
"""

import json

import requests


def test_pick_chatbot():
    """픽톡 기능 테스트"""

    print("🤖 픽톡(Pick Chatbot) 간단 테스트")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # 1. 채팅 세션 시작 테스트
    print("\n🔍 1. 채팅 세션 시작 테스트")
    print("-" * 30)

    try:
        response = requests.post(
            f"{base_url}/api/pick-chatbot/chat",
            json={
                "message": "안녕하세요! 픽톡 테스트입니다.",
                "session_id": "test_session_001"
            },
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 채팅 성공!")
            print(f"응답: {data.get('response', 'N/A')[:100]}...")
            print(f"세션 ID: {data.get('session_id', 'N/A')}")
        else:
            print(f"❌ 채팅 실패: {response.status_code}")
            print(f"응답: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ 채팅 테스트 오류: {e}")

    # 2. AI 어시스턴트 채팅 테스트
    print("\n🔍 2. AI 어시스턴트 채팅 테스트")
    print("-" * 30)

    try:
        response = requests.post(
            f"{base_url}/api/pick-chatbot/ai-assistant-chat",
            json={
                "message": "AI 어시스턴트 테스트입니다.",
                "session_id": "test_session_001"
            },
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI 어시스턴트 성공!")
            print(f"응답: {data.get('response', 'N/A')[:100]}...")
        else:
            print(f"❌ AI 어시스턴트 실패: {response.status_code}")
            print(f"응답: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ AI 어시스턴트 테스트 오류: {e}")

    # 3. 제목 생성 테스트
    print("\n🔍 3. 제목 생성 테스트")
    print("-" * 30)

    try:
        response = requests.post(
            f"{base_url}/api/pick-chatbot/generate-title",
            json={
                "content": "AI 개발자 이력서입니다. Python, FastAPI, LangChain 경험이 있습니다.",
                "session_id": "test_session_001"
            },
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 제목 생성 성공!")
            print(f"제목: {data.get('title', 'N/A')}")
        else:
            print(f"❌ 제목 생성 실패: {response.status_code}")
            print(f"응답: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ 제목 생성 테스트 오류: {e}")

    print(f"\n✅ 픽톡 테스트 완료!")

if __name__ == "__main__":
    print("🚀 픽톡(Pick Chatbot) 테스트 시작")
    print("=" * 60)

    # 백엔드 서버 연결 확인
    try:
        response = requests.get(f"http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 연결 성공!")
            test_pick_chatbot()
        else:
            print(f"❌ 백엔드 서버 응답 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 백엔드 서버 연결 실패: {e}")
        print("   백엔드 서버를 먼저 실행하세요: uvicorn main:app --reload --port 8000")
