#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 테스트 스크립트
"""

import requests
import json

def test_applicants_api():
    try:
        # 지원자 API 테스트
        url = "http://localhost:8003/api/applicants/"
        print(f"🔍 API 호출 시도: {url}")
        
        response = requests.get(url)
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📡 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'applicants' in data:
                print(f"📊 지원자 수: {len(data['applicants'])}")
                for i, applicant in enumerate(data['applicants'][:3]):  # 처음 3명만 출력
                    print(f"\n--- 지원자 {i+1} ---")
                    for key, value in applicant.items():
                        print(f"{key}: {value}")
            else:
                print("❌ 'applicants' 키가 응답에 없습니다")
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_applicants_api()
