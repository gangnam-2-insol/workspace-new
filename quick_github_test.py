import json

import requests

# GitHub API 테스트 (kyungho222 계정)
username = "kyungho222"
print(f"🔍 {username} 테스트 중...")

response = requests.post(
    "http://localhost:8000/api/github/summary",
    json={"username": username},
    timeout=30
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ {username} 성공!")
    print(f"Profile URL: {data.get('profileUrl')}")
    print(f"Languages: {len(data.get('language_stats', {}))}개")

    # 상세 결과 출력
    if 'summary' in data and data['summary']:
        try:
            summary_data = json.loads(data['summary'])
            if isinstance(summary_data, list) and len(summary_data) > 0:
                print(f"\n📊 분석 결과:")
                for i, item in enumerate(summary_data[:3]):  # 처음 3개만 출력
                    print(f"  {i+1}. 주제: {item.get('주제', 'N/A')}")
                    print(f"     기술 스택: {', '.join(item.get('기술 스택', [])[:5])}")
                    print(f"     주요 기능: {', '.join(item.get('주요 기능', [])[:3])}")
        except:
            print(f"📝 요약 데이터 파싱 실패")

    # 토큰 사용량
    token_usage = data.get('token_usage', {})
    print(f"\n🔑 API 사용량:")
    print(f"  GitHub API 호출: {token_usage.get('github_api_calls', 0)}회")
    print(f"  OpenAI API 호출: {token_usage.get('openai_api_calls', 0)}회")
    print(f"  OpenAI 토큰 사용: {token_usage.get('openai_tokens_used', 0)}개")

else:
    print(f"❌ {username} 실패: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
