#!/usr/bin/env python3
"""
GitHub 포트폴리오 분석 기능 테스트
"""

import asyncio
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv('backend/.env')

async def test_github_analysis():
    """GitHub 포트폴리오 분석 기능 테스트"""
    
    print("🔍 GitHub 포트폴리오 분석 기능 테스트")
    print("=" * 60)
    
    # 백엔드 서버 URL
    base_url = "http://localhost:8000"
    
    # 테스트할 GitHub 사용자들
    test_users = [
        "kyungh0222",  # 이경호 (AI 개발자)
        "torvalds",    # Linux 창시자
        "antirez",     # Redis 창시자
        "gvanrossum"   # Python 창시자
    ]
    
    print(f"📋 테스트할 GitHub 사용자: {len(test_users)}명")
    for user in test_users:
        print(f"   - {user}")
    
    # 1. 사용자 프로필 분석 테스트
    print(f"\n🔍 1. 사용자 프로필 분석 테스트")
    print("-" * 50)
    
    for username in test_users[:2]:  # 처음 2명만 테스트
        try:
            print(f"\n📊 {username} 프로필 분석 중...")
            
            # API 호출
            response = requests.post(
                f"{base_url}/github/summary",
                json={"username": username},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {username} 프로필 분석 성공!")
                
                # 결과 요약
                print(f"   📈 프로필 URL: {result.get('profileUrl', 'N/A')}")
                print(f"   📊 언어 통계: {len(result.get('language_stats', {}))}개 언어")
                print(f"   🤖 AI 분석: {len(result.get('summary', []))}개 항목")
                print(f"   💾 소스: {result.get('source', 'N/A')}")
                
                # 토큰 사용량
                token_usage = result.get('token_usage', {})
                print(f"   🔑 API 호출: GitHub {token_usage.get('github_api_calls', 0)}회, OpenAI {token_usage.get('openai_api_calls', 0)}회")
                
                # 상세 분석 결과 미리보기
                if 'summary' in result and result['summary']:
                    try:
                        summary_data = json.loads(result['summary'])
                        if isinstance(summary_data, list) and len(summary_data) > 0:
                            first_item = summary_data[0]
                            print(f"   📝 첫 번째 분석 항목:")
                            print(f"      주제: {first_item.get('주제', 'N/A')}")
                            print(f"      기술 스택: {', '.join(first_item.get('기술 스택', [])[:3])}...")
                            print(f"      주요 기능: {', '.join(first_item.get('주요 기능', [])[:2])}...")
                    except:
                        print(f"   📝 요약 데이터 파싱 실패")
                
            else:
                print(f"❌ {username} 프로필 분석 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ {username} 프로필 분석 오류: {e}")
    
    # 2. 특정 레포지토리 분석 테스트
    print(f"\n🔍 2. 특정 레포지토리 분석 테스트")
    print("-" * 50)
    
    test_repos = [
        ("kyungh0222", "insol"),  # 이경호의 주요 프로젝트
        ("torvalds", "linux"),    # Linux 커널
    ]
    
    for username, repo_name in test_repos:
        try:
            print(f"\n📊 {username}/{repo_name} 레포지토리 분석 중...")
            
            # API 호출
            response = requests.post(
                f"{base_url}/github/summary",
                json={"username": username, "repo_name": repo_name},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {username}/{repo_name} 분석 성공!")
                
                # 결과 요약
                print(f"   📈 레포지토리 URL: {result.get('profileUrl', 'N/A')}")
                print(f"   📊 언어 통계: {len(result.get('language_stats', {}))}개 언어")
                print(f"   🤖 AI 분석: {len(result.get('summary', []))}개 항목")
                
                # 상세 분석 결과
                detailed = result.get('detailed_analysis', {})
                if detailed:
                    tech_stack = detailed.get('tech_stack', {})
                    print(f"   🛠️ 기술 스택:")
                    print(f"      언어: {list(tech_stack.get('languages', {}).keys())[:3]}")
                    print(f"      프레임워크: {tech_stack.get('frameworks', [])[:3]}")
                    print(f"      빌드 도구: {tech_stack.get('build_tools', [])[:3]}")
                    
                    dependencies = detailed.get('dependencies', {})
                    print(f"   📦 의존성:")
                    print(f"      외부 라이브러리: {len(dependencies.get('external_libraries', []))}개")
                    print(f"      LLM 라이브러리: {dependencies.get('llm_libraries', [])[:3]}")
                
            else:
                print(f"❌ {username}/{repo_name} 분석 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ {username}/{repo_name} 분석 오류: {e}")
    
    # 3. 분석 상태 확인 테스트
    print(f"\n🔍 3. 분석 상태 확인 테스트")
    print("-" * 50)
    
    try:
        username = "kyungh0222"
        print(f"\n📊 {username} 분석 상태 확인 중...")
        
        response = requests.get(f"{base_url}/github/analysis-status/{username}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ {username} 분석 상태 확인 성공!")
            print(f"   📊 상태: {status.get('status', 'N/A')}")
            print(f"   ⏰ 마지막 업데이트: {status.get('last_updated', 'N/A')}")
            print(f"   📈 분석된 레포: {len(status.get('analyzed_repos', []))}개")
        else:
            print(f"❌ {username} 분석 상태 확인 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 분석 상태 확인 오류: {e}")
    
    # 4. 강제 재분석 테스트
    print(f"\n🔍 4. 강제 재분석 테스트")
    print("-" * 50)
    
    try:
        username = "kyungh0222"
        print(f"\n📊 {username} 강제 재분석 요청 중...")
        
        response = requests.post(
            f"{base_url}/github/force-reanalysis",
            json={"username": username},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {username} 강제 재분석 성공!")
            print(f"   📊 결과: {result.get('message', 'N/A')}")
        else:
            print(f"❌ {username} 강제 재분석 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 강제 재분석 오류: {e}")
    
    print(f"\n✅ GitHub 포트폴리오 분석 테스트 완료!")

def test_github_api_directly():
    """GitHub API 직접 테스트"""
    print(f"\n🔍 GitHub API 직접 테스트")
    print("-" * 50)
    
    # GitHub 토큰 확인
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    if not github_token:
        print("⚠️ GitHub 토큰이 설정되지 않았습니다.")
        print("   GITHUB_TOKEN 또는 GH_TOKEN 환경변수를 설정하세요.")
        return
    
    print(f"✅ GitHub 토큰 확인됨 (길이: {len(github_token)})")
    
    # GitHub API 직접 호출 테스트
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # 사용자 정보 조회
        username = "kyungh0222"
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API 직접 호출 성공!")
            print(f"   👤 사용자: {user_data.get('login')}")
            print(f"   📊 공개 레포: {user_data.get('public_repos')}개")
            print(f"   👥 팔로워: {user_data.get('followers')}명")
            print(f"   📅 가입일: {user_data.get('created_at')}")
        else:
            print(f"❌ GitHub API 호출 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"❌ GitHub API 직접 호출 오류: {e}")

if __name__ == "__main__":
    print("🚀 GitHub 포트폴리오 분석 기능 테스트 시작")
    print("=" * 60)
    
    # 1. GitHub API 직접 테스트
    test_github_api_directly()
    
    # 2. 백엔드 서버 테스트
    print(f"\n🔍 백엔드 서버 연결 확인...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버 연결 성공!")
            asyncio.run(test_github_analysis())
        else:
            print(f"❌ 백엔드 서버 응답 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 백엔드 서버 연결 실패: {e}")
        print("   백엔드 서버를 먼저 실행하세요: uvicorn main:app --reload --port 8000")
