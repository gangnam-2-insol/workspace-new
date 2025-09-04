#!/usr/bin/env python3
"""
DB에 저장된 샘플 데이터 분석 스크립트
"""

import requests
import json
from datetime import datetime

def analyze_sample_data():
    """샘플 데이터 분석"""
    
    print("🔍 DB에 저장된 샘플 데이터 분석")
    print("=" * 50)
    
    try:
        # 지원자 데이터 조회
        response = requests.get('http://localhost:8000/api/applicants?skip=0&limit=20')
        data = response.json()
        applicants = data.get('applicants', [])
        
        print(f"📊 총 지원자 수: {len(applicants)}")
        print()
        
        if not applicants:
            print("❌ 지원자 데이터가 없습니다.")
            return
        
        # 1. 첫 번째 지원자 상세 분석
        first_applicant = applicants[0]
        print("🎯 첫 번째 지원자 상세 분석")
        print("-" * 30)
        print(f"이름: {first_applicant['name']}")
        print(f"이메일: {first_applicant['email']}")
        print(f"연락처: {first_applicant['phone']}")
        print(f"지원 직무: {first_applicant['position']}")
        print(f"부서: {first_applicant['department']}")
        print(f"경력: {first_applicant['experience']}")
        print(f"기술 스택: {first_applicant['skills']}")
        print(f"AI 분석 점수: {first_applicant['analysisScore']}/100")
        print(f"상태: {first_applicant['status']}")
        print(f"지원일: {first_applicant['created_at']}")
        
        if 'job_posting_info' in first_applicant:
            job_info = first_applicant['job_posting_info']
            print(f"채용 공고: {job_info['title']}")
            print(f"회사: {job_info['company']}")
            print(f"위치: {job_info['location']}")
        
        print()
        
        # 2. 전체 지원자 통계
        print("📈 전체 지원자 통계")
        print("-" * 30)
        
        # 직무별 분포
        positions = {}
        departments = {}
        experience_levels = {}
        status_counts = {}
        score_ranges = {'0-50': 0, '51-70': 0, '71-85': 0, '86-100': 0}
        
        for app in applicants:
            # 직무별 카운트
            pos = app.get('position', '미지정')
            positions[pos] = positions.get(pos, 0) + 1
            
            # 부서별 카운트
            dept = app.get('department', '미지정')
            departments[dept] = departments.get(dept, 0) + 1
            
            # 경력별 카운트
            exp = app.get('experience', '미지정')
            experience_levels[exp] = experience_levels.get(exp, 0) + 1
            
            # 상태별 카운트
            status = app.get('status', '미지정')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # 점수별 카운트
            score = app.get('analysisScore', 0)
            if score <= 50:
                score_ranges['0-50'] += 1
            elif score <= 70:
                score_ranges['51-70'] += 1
            elif score <= 85:
                score_ranges['71-85'] += 1
            else:
                score_ranges['86-100'] += 1
        
        print("직무별 분포:")
        for pos, count in sorted(positions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pos}: {count}명")
        
        print("\n부서별 분포:")
        for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True):
            print(f"  {dept}: {count}명")
        
        print("\n경력별 분포:")
        for exp, count in sorted(experience_levels.items(), key=lambda x: x[1], reverse=True):
            print(f"  {exp}: {count}명")
        
        print("\n상태별 분포:")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}명")
        
        print("\nAI 분석 점수 분포:")
        for range_name, count in score_ranges.items():
            print(f"  {range_name}: {count}명")
        
        # 3. 상위 점수 지원자
        print("\n🏆 상위 점수 지원자 (Top 5)")
        print("-" * 30)
        
        top_applicants = sorted(applicants, key=lambda x: x.get('analysisScore', 0), reverse=True)[:5]
        for i, app in enumerate(top_applicants, 1):
            print(f"{i}. {app['name']} - {app['position']} - 점수: {app['analysisScore']}")
        
        # 4. 기술 스택 분석
        print("\n💻 기술 스택 분석")
        print("-" * 30)
        
        all_skills = []
        for app in applicants:
            skills = app.get('skills', '')
            if skills:
                # 쉼표로 구분된 기술들을 분리
                skill_list = [s.strip() for s in skills.split(',')]
                all_skills.extend(skill_list)
        
        skill_counts = {}
        for skill in all_skills:
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        print("가장 많이 언급된 기술:")
        for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {skill}: {count}회")
        
        print(f"\n✅ 분석 완료! 총 {len(applicants)}명의 지원자 데이터를 분석했습니다.")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    analyze_sample_data()
