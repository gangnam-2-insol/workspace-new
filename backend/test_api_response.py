#!/usr/bin/env python3
"""
API 응답 테스트 스크립트
"""

import requests


def test_api_response():
    print("🔍 지원자 관리 페이지 연동 확인")
    print("=" * 60)

    try:
        # API 호출
        response = requests.get('http://localhost:8000/api/applicants?limit=5')
        data = response.json()

        print(f"📊 API 응답 상태: {response.status_code}")
        print(f"📊 응답 데이터 키: {list(data.keys())}")

        if 'applicants' in data:
            applicants = data['applicants']
            print(f"📊 지원자 수: {len(applicants)}명")

            print(f"\n📋 지원자 5명 이메일/전화번호 확인:")
            for i, app in enumerate(applicants[:5], 1):
                name = app.get('name', 'Unknown')
                email = app.get('email', '없음')
                phone = app.get('phone', '없음')
                position = app.get('position', 'Unknown')

                print(f"{i}. {name}")
                print(f"   직무: {position}")
                print(f"   이메일: {email}")
                print(f"   전화번호: {phone}")
                print(f"   연동 상태: {'✅' if email != '없음' and phone != '없음' else '❌'}")
                print()
        else:
            print("❌ 'applicants' 키가 응답에 없습니다.")

    except Exception as e:
        print(f"❌ API 호출 오류: {e}")

if __name__ == "__main__":
    test_api_response()
