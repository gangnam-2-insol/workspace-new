#!/usr/bin/env python3
"""
지원자 생성 로직 디버깅 스크립트
"""

import pymongo
from bson import ObjectId


def debug_applicant_generation():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 지원자 생성 로직 디버깅")
    print("=" * 60)

    # 1. 기존 채용공고 정보 가져오기
    job_postings = list(db.job_postings.find({}, {"_id": 1, "position": 1, "title": 1}))
    print(f"📋 총 채용공고 수: {len(job_postings)}개")

    # 2. 채용공고를 직무별로 그룹화
    job_posting_by_position = {}
    for job in job_postings:
        position = job.get('position', 'Unknown')
        if position not in job_posting_by_position:
            job_posting_by_position[position] = []
        job_posting_by_position[position].append({
            'id': str(job['_id']),
            'title': job.get('title', 'Unknown')
        })

    print(f"📊 직무별 채용공고 그룹화 결과:")
    for position, jobs in job_posting_by_position.items():
        print(f"   - {position}: {len(jobs)}개")
        for job in jobs:
            print(f"     → {job['title']} (ID: {job['id'][:8]}...)")

    # 3. 현재 지원자들의 직무 분포 확인
    print(f"\n📊 현재 지원자 직무 분포:")
    applicants = list(db.applicants.find({}, {"position": 1, "job_posting_id": 1}))
    position_counts = {}
    for app in applicants:
        position = app.get('position', 'Unknown')
        position_counts[position] = position_counts.get(position, 0) + 1

    for position, count in sorted(position_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {position}: {count}명")

    # 4. 지원자별 매칭 상태 확인
    print(f"\n🔗 지원자별 매칭 상태:")
    matched_count = 0
    total_count = len(applicants)

    for app in applicants:
        position = app.get('position', 'Unknown')
        job_posting_id = app.get('job_posting_id', 'None')

        # 해당 직무의 채용공고가 있는지 확인
        available_jobs = job_posting_by_position.get(position, [])

        if available_jobs:
            # 지원자가 해당 직무의 채용공고에 배정되었는지 확인
            is_matched = any(job['id'] == job_posting_id for job in available_jobs)
            if is_matched:
                matched_count += 1
                print(f"   ✅ {position} → 매칭됨")
            else:
                print(f"   ❌ {position} → 매칭 안됨 (job_posting_id: {job_posting_id})")
        else:
            print(f"   ⚠️  {position} → 해당 직무 채용공고 없음")

    print(f"\n📈 매칭 결과:")
    print(f"   - 총 지원자: {total_count}명")
    print(f"   - 매칭된 지원자: {matched_count}명")
    print(f"   - 매칭률: {(matched_count/total_count*100):.1f}%" if total_count > 0 else "   - 매칭률: 0%")

    client.close()

if __name__ == "__main__":
    debug_applicant_generation()
