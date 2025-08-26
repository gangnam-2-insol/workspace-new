#!/usr/bin/env python3
"""
모든 채용공고 정보와 지원자 배정 현황 분석
"""

import pymongo
from bson import ObjectId


def analyze_job_postings_and_applicants():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 모든 채용공고 정보와 지원자 배정 현황 분석")
    print("=" * 80)

    # 모든 채용공고 정보 확인
    print("📋 등록된 모든 채용공고:")
    job_postings = list(db.job_postings.find())

    for i, job in enumerate(job_postings, 1):
        job_id = str(job.get('_id'))
        title = job.get('title', 'Unknown')
        print(f"\n{i}. ID: {job_id}")
        print(f"   제목: {title}")

        # 해당 채용공고에 지원한 지원자 수 확인
        applicant_count = db.applicants.count_documents({'job_posting_id': job_id})
        print(f"   지원자 수: {applicant_count}명")

        # 해당 채용공고에 지원한 지원자들의 직무 분포
        if applicant_count > 0:
            print("   지원자 직무 분포:")
            position_counts = {}
            for app in db.applicants.find({'job_posting_id': job_id}):
                position = app.get('position', 'Unknown')
                position_counts[position] = position_counts.get(position, 0) + 1

            for position, count in sorted(position_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"     - {position}: {count}명")

    print("\n" + "=" * 80)
    print("📊 전체 지원자 직무별 분포:")

    # 전체 지원자 직무 분포
    all_position_counts = {}
    for app in db.applicants.find():
        position = app.get('position', 'Unknown')
        all_position_counts[position] = all_position_counts.get(position, 0) + 1

    for position, count in sorted(all_position_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {position}: {count}명")

    print("\n" + "=" * 80)
    print("🔗 직무별 적절한 채용공고 배정 가이드:")

    # 직무별로 적절한 채용공고 매칭
    position_to_job_mapping = {}
    for position in all_position_counts.keys():
        best_match = None
        best_score = 0

        for job in job_postings:
            title = job.get('title', '').lower()
            position_lower = position.lower()

            # 매칭 점수 계산
            score = 0
            if position_lower in title or title in position_lower:
                score = 100
            elif any(keyword in title for keyword in position_lower.split()):
                score = 50
            elif any(keyword in position_lower for keyword in title.split()):
                score = 30

            if score > best_score:
                best_score = score
                best_match = job

        if best_match:
            position_to_job_mapping[position] = best_match
            print(f"   - {position} → {best_match.get('title')} (매칭점수: {best_score})")
        else:
            print(f"   - {position} → 적절한 채용공고 없음")

    print("\n" + "=" * 80)
    print("📈 현재 배정 vs 이상적인 배정 비교:")

    # 현재 배정 상태와 이상적인 배정 비교
    current_matches = 0
    ideal_matches = 0
    total_applicants = 0

    for app in db.applicants.find():
        total_applicants += 1
        position = app.get('position', '')
        job_posting_id = app.get('job_posting_id', '')

        # 현재 배정 확인
        if job_posting_id:
            try:
                job = db.job_postings.find_one({'_id': ObjectId(job_posting_id)})
                if job:
                    title = job.get('title', '').lower()
                    if position.lower() in title or title in position.lower():
                        current_matches += 1
            except:
                pass

        # 이상적인 배정 확인
        if position in position_to_job_mapping:
            ideal_job = position_to_job_mapping[position]
            ideal_title = ideal_job.get('title', '').lower()
            if position.lower() in ideal_title or ideal_title in position.lower():
                ideal_matches += 1

    print(f"   - 총 지원자: {total_applicants}명")
    print(f"   - 현재 매칭: {current_matches}명 ({current_matches/total_applicants*100:.1f}%)")
    print(f"   - 이상적 매칭: {ideal_matches}명 ({ideal_matches/total_applicants*100:.1f}%)")
    print(f"   - 개선 가능: {ideal_matches - current_matches}명")

    client.close()

if __name__ == "__main__":
    analyze_job_postings_and_applicants()
