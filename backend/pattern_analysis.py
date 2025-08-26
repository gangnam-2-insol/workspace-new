#!/usr/bin/env python3
"""
데이터 패턴과 품질 분석 스크립트
"""

import requests
import json
from collections import defaultdict

def analyze_data_patterns():
    """데이터 패턴과 품질 분석"""
    
    print("🔍 데이터 패턴과 품질 분석")
    print("=" * 50)
    
    try:
        # 지원자 데이터 조회
        response = requests.get('http://localhost:8000/api/applicants?skip=0&limit=100')
        data = response.json()
        applicants = data.get('applicants', [])
        
        print(f"📊 분석 대상: {len(applicants)}명의 지원자")
        print()
        
        if not applicants:
            print("❌ 지원자 데이터가 없습니다.")
            return
        
        # 1. 데이터 완성도 분석
        print("📋 데이터 완성도 분석")
        print("-" * 30)
        
        required_fields = ['name', 'email', 'phone', 'position', 'department', 'experience', 'skills']
        optional_fields = ['growthBackground', 'motivation', 'careerHistory', 'analysisResult']
        
        completion_stats = {}
        for field in required_fields + optional_fields:
            completed = sum(1 for app in applicants if app.get(field) and app[field] != '')
            completion_rate = (completed / len(applicants)) * 100
            completion_stats[field] = completion_rate
            status = "✅" if completion_rate >= 90 else "⚠️" if completion_rate >= 70 else "❌"
            print(f"{status} {field}: {completion_rate:.1f}% ({completed}/{len(applicants)})")
        
        print()
        
        # 2. 기술 스택과 직무 연관성 분석
        print("💻 기술 스택과 직무 연관성 분석")
        print("-" * 30)
        
        position_skills = defaultdict(list)
        for app in applicants:
            position = app.get('position', '미지정')
            skills = app.get('skills', '')
            if skills:
                skill_list = [s.strip() for s in skills.split(',')]
                position_skills[position].extend(skill_list)
        
        for position, skills in position_skills.items():
            if skills:
                skill_counts = defaultdict(int)
                for skill in skills:
                    skill_counts[skill] += 1
                
                top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"\n{position}:")
                for skill, count in top_skills:
                    print(f"  - {skill}: {count}회")
        
        print()
        
        # 3. 점수 분포 상세 분석
        print("📊 AI 분석 점수 상세 분석")
        print("-" * 30)
        
        scores = [app.get('analysisScore', 0) for app in applicants if app.get('analysisScore') is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            print(f"평균 점수: {avg_score:.1f}")
            print(f"최저 점수: {min_score}")
            print(f"최고 점수: {max_score}")
            
            # 점수대별 분포
            score_ranges = {
                '0-50': 0, '51-60': 0, '61-70': 0, 
                '71-80': 0, '81-90': 0, '91-100': 0
            }
            
            for score in scores:
                if score <= 50:
                    score_ranges['0-50'] += 1
                elif score <= 60:
                    score_ranges['51-60'] += 1
                elif score <= 70:
                    score_ranges['61-70'] += 1
                elif score <= 80:
                    score_ranges['71-80'] += 1
                elif score <= 90:
                    score_ranges['81-90'] += 1
                else:
                    score_ranges['91-100'] += 1
            
            print("\n점수대별 분포:")
            for range_name, count in score_ranges.items():
                percentage = (count / len(scores)) * 100
                print(f"  {range_name}: {count}명 ({percentage:.1f}%)")
        
        print()
        
        # 4. 데이터 품질 이슈 분석
        print("⚠️ 데이터 품질 이슈 분석")
        print("-" * 30)
        
        issues = []
        
        # 이메일 형식 검증
        invalid_emails = []
        for app in applicants:
            email = app.get('email', '')
            if email and '@' not in email:
                invalid_emails.append(f"{app['name']}: {email}")
        
        if invalid_emails:
            issues.append(f"잘못된 이메일 형식: {len(invalid_emails)}건")
        
        # 전화번호 형식 검증
        invalid_phones = []
        for app in applicants:
            phone = app.get('phone', '')
            if phone and len(phone.replace('-', '').replace(' ', '')) < 10:
                invalid_phones.append(f"{app['name']}: {phone}")
        
        if invalid_phones:
            issues.append(f"잘못된 전화번호 형식: {len(invalid_phones)}건")
        
        # 중복 데이터 검증
        emails = [app.get('email', '') for app in applicants if app.get('email')]
        duplicate_emails = [email for email in set(emails) if emails.count(email) > 1]
        
        if duplicate_emails:
            issues.append(f"중복 이메일: {len(duplicate_emails)}건")
        
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
        else:
            print("✅ 데이터 품질 이슈가 발견되지 않았습니다.")
        
        print()
        
        # 5. 추천사항
        print("💡 데이터 품질 개선 추천사항")
        print("-" * 30)
        
        if completion_stats.get('growthBackground', 0) < 90:
            print("• 성장 배경 정보 완성도 향상 필요")
        
        if completion_stats.get('motivation', 0) < 90:
            print("• 지원 동기 정보 완성도 향상 필요")
        
        if completion_stats.get('careerHistory', 0) < 90:
            print("• 경력 이력 정보 완성도 향상 필요")
        
        if invalid_emails:
            print("• 이메일 형식 검증 로직 강화 필요")
        
        if invalid_phones:
            print("• 전화번호 형식 검증 로직 강화 필요")
        
        if duplicate_emails:
            print("• 중복 데이터 검증 로직 강화 필요")
        
        print(f"\n✅ 패턴 분석 완료!")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    analyze_data_patterns()
