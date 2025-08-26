#!/usr/bin/env python3
"""
상세 디버깅 스크립트
"""

import pymongo
from bson import ObjectId


def debug_detailed():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 상세 디버깅")
    print("=" * 60)

    # 1. 채용공고 정보
    job_postings = list(db.job_postings.find({}, {"_id": 1, "position": 1, "title": 1}))
    print(f"📋 채용공고 정보:")
    for i, job in enumerate(job_postings, 1):
        job_id = str(job['_id'])
        position = job.get('position', 'Unknown')
        title = job.get('title', 'Unknown')
        print(f"{i}. {title}")
        print(f"   ID: {job_id}")
        print(f"   Position: {position}")

    # 2. 지원자 정보 (처음 10개만)
    applicants = list(db.applicants.find({}, {"name": 1, "position": 1, "job_posting_id": 1}).limit(10))
    print(f"\n📊 지원자 정보 (처음 10개):")
    for i, app in enumerate(applicants, 1):
        name = app.get('name', 'Unknown')
        position = app.get('position', 'Unknown')
        job_posting_id = app.get('job_posting_id', 'None')
        print(f"{i}. {name}")
        print(f"   Position: {position}")
        print(f"   Job Posting ID: {job_posting_id}")

        # 해당 채용공고 찾기
        if job_posting_id != 'None':
            try:
                job = db.job_postings.find_one({'_id': ObjectId(job_posting_id)})
                if job:
                    job_position = job.get('position', 'Unknown')
                    job_title = job.get('title', 'Unknown')
                    print(f"   → 연결된 채용공고: {job_title}")
                    print(f"   → 채용공고 직무: {job_position}")
                    print(f"   → 매칭 여부: {'✅' if position == job_position else '❌'}")
                else:
                    print(f"   → 연결된 채용공고: 없음")
            except:
                print(f"   → 연결된 채용공고: ID 오류")
        print()

    # 3. 매칭 통계
    print(f"📈 매칭 통계:")
    total_applicants = db.applicants.count_documents({})
    matched_count = 0

    for app in db.applicants.find({}, {"position": 1, "job_posting_id": 1}):
        position = app.get('position', 'Unknown')
        job_posting_id = app.get('job_posting_id', 'None')

        if job_posting_id != 'None':
            try:
                job = db.job_postings.find_one({'_id': ObjectId(job_posting_id)})
                if job and position == job.get('position', 'Unknown'):
                    matched_count += 1
            except:
                pass

    print(f"   - 총 지원자: {total_applicants}명")
    print(f"   - 매칭된 지원자: {matched_count}명")
    print(f"   - 매칭률: {(matched_count/total_applicants*100):.1f}%" if total_applicants > 0 else "   - 매칭률: 0%")

    client.close()

if __name__ == "__main__":
    debug_detailed()
