#!/usr/bin/env python3
import requests
import json

def test_kyungho_applicant():
    """이경호 지원자 데이터가 API를 통해 제대로 조회되는지 테스트합니다."""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. 이메일로 특정 지원자 조회
        print("🔍 이경호 지원자 조회 테스트...")
        response = requests.get(f"{base_url}/api/applicants?email=kyunghol87@naver.com")
        
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 헤더: {response.headers}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ API 응답 성공 (상태 코드: {response.status_code})")
                print(f"📊 조회된 지원자 수: {len(data)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 오류: {e}")
                print(f"응답 내용: {response.text}")
                return
            
            print(f"데이터 타입: {type(data)}")
            print(f"데이터 길이: {len(data)}")
            
            if data and len(data) > 0:
                applicant = data[0]
                print(f"첫 번째 지원자 데이터: {applicant}")
                print("\n📋 이경호 지원자 정보:")
                print(f"이름: {applicant.get('name', 'N/A')}")
                print(f"이메일: {applicant.get('email', 'N/A')}")
                print(f"직무: {applicant.get('position', 'N/A')}")
                print(f"경력: {applicant.get('experience', 'N/A')}")
                print(f"기술스택: {applicant.get('skills', 'N/A')}")
                print(f"상태: {applicant.get('status', 'N/A')}")
                print(f"분석점수: {applicant.get('analysisScore', 'N/A')}")
                print(f"부서: {applicant.get('department', 'N/A')}")
                print(f"GitHub: {applicant.get('github_url', 'N/A')}")
                print(f"LinkedIn: {applicant.get('linkedin_url', 'N/A')}")
                print(f"포트폴리오: {applicant.get('portfolio_url', 'N/A')}")
                
                # 랭킹 정보
                ranks = applicant.get('ranks', {})
                if ranks:
                    print(f"\n🏆 랭킹 정보:")
                    print(f"  이력서: {ranks.get('resume', 'N/A')}")
                    print(f"  자기소개서: {ranks.get('coverLetter', 'N/A')}")
                    print(f"  포트폴리오: {ranks.get('portfolio', 'N/A')}")
                    print(f"  총점: {ranks.get('total', 'N/A')}")
            else:
                print("❌ 이경호 지원자를 찾을 수 없습니다.")
        else:
            print(f"❌ API 요청 실패 (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
        
        # 2. 전체 지원자 목록 조회 (최근 10개)
        print("\n🔍 전체 지원자 목록 조회 테스트...")
        response = requests.get(f"{base_url}/api/applicants?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 전체 목록 조회 성공 (상태 코드: {response.status_code})")
            print(f"📊 전체 지원자 수: {len(data)}")
            
            # 이경호가 목록에 있는지 확인
            kyungho_found = False
            for applicant in data:
                if applicant.get('email') == 'kyunghol87@naver.com':
                    kyungho_found = True
                    print(f"✅ 이경호 지원자가 목록에서 발견되었습니다!")
                    break
            
            if not kyungho_found:
                print("⚠️ 이경호 지원자가 목록에서 발견되지 않았습니다.")
            
            # 최근 지원자 5명 출력
            print(f"\n📋 최근 지원자 5명:")
            for i, applicant in enumerate(data[:5], 1):
                print(f"{i}. {applicant.get('name')} ({applicant.get('position')}) - {applicant.get('email')}")
        
        else:
            print(f"❌ 전체 목록 조회 실패 (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
        
        # 3. 지원자 통계 조회
        print("\n🔍 지원자 통계 조회 테스트...")
        response = requests.get(f"{base_url}/api/applicants/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 통계 조회 성공 (상태 코드: {response.status_code})")
            print(f"📊 통계 정보: {json.dumps(stats, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 통계 조회 실패 (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_kyungho_applicant()
