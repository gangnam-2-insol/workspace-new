import requests
import json

def test_github_field():
    """GitHub URL 필드 테스트"""
    try:
        print("🔍 GitHub URL 필드 테스트 시작...")
        
        # 1. 새로운 샘플데이터 생성
        print("📝 새로운 샘플데이터 생성 중...")
        response = requests.post(
            'http://localhost:8000/api/sample/generate-applicants',
            json={'count': 3}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 샘플데이터 생성 성공: {result['message']}")
            print(f"📊 생성된 지원자 수: {result['generated_count']}")
        else:
            print(f"❌ 샘플데이터 생성 실패: {response.status_code}")
            return
        
        # 2. 생성된 데이터 확인
        print("\n🔍 생성된 데이터 확인 중...")
        response = requests.get('http://localhost:8000/api/applicants?limit=5')
        
        if response.status_code == 200:
            data = response.json()
            applicants = data.get('applicants', [])
            
            if applicants:
                latest_applicant = applicants[0]  # 최신 데이터
                print(f"📋 최신 지원자 필드:")
                for field, value in latest_applicant.items():
                    if field in ['github_url', 'linkedin_url', 'portfolio_url']:
                        print(f"  - {field}: {value}")
                    else:
                        print(f"  - {field}: {type(value).__name__}")
                
                # GitHub 관련 필드 확인
                github_fields = [field for field in latest_applicant.keys() if 'github' in field.lower()]
                if github_fields:
                    print(f"\n✅ GitHub 관련 필드 발견: {github_fields}")
                    for field in github_fields:
                        print(f"  - {field}: {latest_applicant[field]}")
                else:
                    print("\n❌ GitHub 관련 필드 없음")
            else:
                print("❌ 지원자 데이터가 없습니다.")
        else:
            print(f"❌ 데이터 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_github_field()
