#!/usr/bin/env python3
import requests
import json

def simple_test():
    """간단한 이경호 지원자 테스트"""
    
    try:
        # 이메일로 이경호 지원자 조회
        url = "http://localhost:8000/api/applicants?email=kyunghol87@naver.com"
        print(f"🔍 API 요청: {url}")
        
        response = requests.get(url)
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 데이터 조회 성공! 조회된 지원자 수: {len(data)}")
            
            if data and len(data) > 0:
                applicant = data[0]
                print(f"\n📋 이경호 지원자 정보:")
                print(f"이름: {applicant.get('name', 'N/A')}")
                print(f"이메일: {applicant.get('email', 'N/A')}")
                print(f"직무: {applicant.get('position', 'N/A')}")
                print(f"상태: {applicant.get('status', 'N/A')}")
                print(f"분석점수: {applicant.get('analysisScore', 'N/A')}")
                print("✅ 이경호 지원자 데이터가 성공적으로 생성되었습니다!")
                
                # 이경호인지 확인
                if applicant.get('email') == 'kyunghol87@naver.com':
                    print("🎉 정확히 이경호 지원자 데이터입니다!")
                else:
                    print(f"⚠️ 다른 지원자 데이터입니다: {applicant.get('email')}")
            else:
                print("❌ 이경호 지원자를 찾을 수 없습니다.")
        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    else:
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    simple_test()
