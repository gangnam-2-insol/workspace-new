import requests
import json

def test_github_url_integration():
    """GitHub URL 통합 테스트"""
    try:
        print("🔍 GitHub URL 통합 테스트 시작...")

        # 1. 새로운 샘플데이터 생성
        print("📝 새로운 샘플데이터 생성 중...")
        response = requests.post(
            'http://localhost:8000/api/sample/generate-applicants',
            json={'count': 5}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 샘플데이터 생성 성공: {result['message']}")
            print(f"📊 생성된 지원자 수: {result['generated_count']}")
        else:
            print(f"❌ 샘플데이터 생성 실패: {response.status_code}")
            return

        # 2. 생성된 데이터에서 GitHub URL 확인
        print("\n🔍 생성된 데이터에서 GitHub URL 확인...")
        response = requests.get('http://localhost:8000/api/applicants?limit=10')

        if response.status_code == 200:
            data = response.json()
            applicants = data.get('applicants', [])

            github_count = 0
            total_count = len(applicants)

            print(f"\n📋 총 {total_count}명의 지원자 중 GitHub URL 보유 현황:")

            for i, applicant in enumerate(applicants[:5]):  # 처음 5명만 확인
                name = applicant.get('name', 'Unknown')
                github_url = applicant.get('github_url')

                if github_url:
                    github_count += 1
                    print(f"  ✅ {name}: {github_url}")
                else:
                    print(f"  ❌ {name}: GitHub URL 없음")

            print(f"\n📊 GitHub URL 보유율: {github_count}/{total_count} ({github_count/total_count*100:.1f}%)")

            # 3. GitHub URL 목록 확인
            print(f"\n🔗 사용된 GitHub URL 목록:")
            github_urls_used = set()
            for applicant in applicants:
                if applicant.get('github_url'):
                    github_urls_used.add(applicant['github_url'])

            for url in sorted(github_urls_used):
                print(f"  - {url}")

        else:
            print(f"❌ 데이터 조회 실패: {response.status_code}")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_github_url_integration()
