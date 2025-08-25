#!/usr/bin/env python3
"""
API 응답 상세 디버깅
"""

import json

import requests


def debug_api_response():
    print("🔍 API 응답 상세 디버깅")
    print("=" * 60)

    try:
        # API 호출
        response = requests.get('http://localhost:8000/api/applicants?limit=1')
        data = response.json()

        print(f"📊 API 응답 상태: {response.status_code}")

        if 'applicants' in data and len(data['applicants']) > 0:
            first_applicant = data['applicants'][0]
            print(f"\n📋 첫 번째 지원자 전체 필드:")
            print(json.dumps(first_applicant, indent=2, ensure_ascii=False, default=str))

            print(f"\n📋 필드 존재 여부:")
            fields_to_check = ['name', 'email', 'phone', 'position', 'skills', 'status']
            for field in fields_to_check:
                exists = field in first_applicant
                value = first_applicant.get(field, 'None')
                print(f"   - {field}: {'✅' if exists else '❌'} (값: {value})")
        else:
            print("❌ 지원자 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ API 호출 오류: {e}")

if __name__ == "__main__":
    debug_api_response()
