#!/usr/bin/env python3
"""
최고 점수 지원자 상세 분석 스크립트
"""

import requests
import json

def analyze_top_applicant():
    """최고 점수 지원자 상세 분석"""
    
    print("🏆 최고 점수 지원자 상세 분석")
    print("=" * 50)
    
    try:
        # 지원자 데이터 조회
        response = requests.get('http://localhost:8000/api/applicants?skip=0&limit=20')
        data = response.json()
        applicants = data.get('applicants', [])
        
        if not applicants:
            print("❌ 지원자 데이터가 없습니다.")
            return
        
        # 최고 점수 지원자 찾기
        top_applicant = max(applicants, key=lambda x: x.get('analysisScore', 0))
        
        print(f"🎯 최고 점수 지원자: {top_applicant['name']}")
        print(f"📊 AI 분석 점수: {top_applicant['analysisScore']}/100")
        print()
        
        # 기본 정보
        print("📋 기본 정보")
        print("-" * 30)
        print(f"이름: {top_applicant['name']}")
        print(f"이메일: {top_applicant['email']}")
        print(f"연락처: {top_applicant['phone']}")
        print(f"지원 직무: {top_applicant['position']}")
        print(f"부서: {top_applicant['department']}")
        print(f"경력: {top_applicant['experience']}")
        print(f"기술 스택: {top_applicant['skills']}")
        print(f"상태: {top_applicant['status']}")
        print(f"지원일: {top_applicant['created_at']}")
        
        # 채용 공고 정보
        if 'job_posting_info' in top_applicant:
            job_info = top_applicant['job_posting_info']
            print(f"\n📢 채용 공고 정보")
            print("-" * 30)
            print(f"제목: {job_info['title']}")
            print(f"회사: {job_info['company']}")
            print(f"위치: {job_info['location']}")
            print(f"상태: {job_info['status']}")
        
        # 관련 문서 ID 확인
        print(f"\n📄 관련 문서 ID")
        print("-" * 30)
        print(f"지원자 ID: {top_applicant['_id']}")
        print(f"이력서 ID: {top_applicant.get('resume_id', '없음')}")
        print(f"자기소개서 ID: {top_applicant.get('cover_letter_id', '없음')}")
        print(f"포트폴리오 ID: {top_applicant.get('portfolio_id', '없음')}")
        
        # 성장 배경, 동기, 경력 분석
        print(f"\n📈 AI 분석 결과")
        print("-" * 30)
        print(f"성장 배경: {top_applicant.get('growthBackground', 'N/A')}")
        print(f"지원 동기: {top_applicant.get('motivation', 'N/A')}")
        print(f"경력 이력: {top_applicant.get('careerHistory', 'N/A')}")
        print(f"분석 결과: {top_applicant.get('analysisResult', 'N/A')}")
        
        # 비슷한 점수대 지원자들
        print(f"\n🔍 비슷한 점수대 지원자들 (90점 이상)")
        print("-" * 30)
        
        high_score_applicants = [app for app in applicants if app.get('analysisScore', 0) >= 90]
        high_score_applicants.sort(key=lambda x: x.get('analysisScore', 0), reverse=True)
        
        for i, app in enumerate(high_score_applicants, 1):
            print(f"{i}. {app['name']} - {app['position']} - {app['analysisScore']}점")
        
        print(f"\n✅ 분석 완료!")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    analyze_top_applicant()
