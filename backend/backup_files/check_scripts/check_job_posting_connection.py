#!/usr/bin/env python3
"""
채용공고와 지원자 데이터 연동 상태 확인 스크립트
"""

import pymongo
from bson import ObjectId


def check_job_posting_connection():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 채용공고와 지원자 데이터 연동 상태 확인")
    print("=" * 60)

    # 채용공고 개수
    job_count = db.job_postings.count_documents({})
    print(f"📋 채용공고 개수: {job_count}")

    # 지원자 개수
    applicant_count = db.applicants.count_documents({})
    print(f"👥 지원자 개수: {applicant_count}")

    print("\n📊 채용공고 ID 샘플:")
    for job in db.job_postings.find().limit(3):
        job_id = str(job.get('_id'))
        title = job.get('title', 'Unknown')
        print(f"   - ID: {job_id}")
        print(f"     제목: {title}")

    print("\n📊 지원자의 job_posting_id 샘플:")
    for app in db.applicants.find().limit(5):
        name = app.get('name', 'Unknown')
        job_posting_id = app.get('job_posting_id', 'None')
        position = app.get('position', 'Unknown')
        print(f"   - {name}: {job_posting_id}")
        print(f"     지원 직무: {position}")

        # job_posting_id가 실제 채용공고에 존재하는지 확인
        if job_posting_id and job_posting_id != 'None':
            try:
                job = db.job_postings.find_one({'_id': ObjectId(job_posting_id)})
                if job:
                    job_title = job.get('title', 'Unknown')
                    print(f"     ✅ 연동됨: {job_title}")

                    # 직무 매칭 확인
                    if position in job_title or job_title in position:
                        print(f"     ✅ 직무 매칭: 일치")
                    else:
                        print(f"     ⚠️  직무 매칭: 불일치 (지원: {position} vs 공고: {job_title})")
                else:
                    print(f"     ❌ 연동 안됨: 해당 ID의 채용공고 없음")
            except:
                print(f"     ❌ 연동 안됨: 잘못된 ID 형식")
        else:
            print(f"     ❌ job_posting_id 없음")

    print("\n🔗 연동 상태 요약:")
    connected_count = 0
    total_count = 0
    matched_count = 0

    for app in db.applicants.find():
        total_count += 1
        job_posting_id = app.get('job_posting_id')
        position = app.get('position', '')

        if job_posting_id and job_posting_id != 'None':
            try:
                job = db.job_postings.find_one({'_id': ObjectId(job_posting_id)})
                if job:
                    connected_count += 1
                    job_title = job.get('title', '')

                    # 직무 매칭 확인
                    if position in job_title or job_title in position:
                        matched_count += 1
            except:
                pass

    print(f"   - 총 지원자: {total_count}명")
    print(f"   - 연동된 지원자: {connected_count}명")
    print(f"   - 직무 매칭된 지원자: {matched_count}명")
    print(f"   - 연동률: {(connected_count/total_count*100):.1f}%" if total_count > 0 else "   - 연동률: 0%")
    print(f"   - 직무 매칭률: {(matched_count/connected_count*100):.1f}%" if connected_count > 0 else "   - 직무 매칭률: 0%")

    # 직무별 분포 확인
    print("\n📈 직무별 분포:")
    position_counts = {}
    for app in db.applicants.find():
        position = app.get('position', 'Unknown')
        position_counts[position] = position_counts.get(position, 0) + 1

    for position, count in sorted(position_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {position}: {count}명")

    client.close()


if __name__ == "__main__":
    check_job_posting_connection()
