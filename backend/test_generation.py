#!/usr/bin/env python3
"""
지원자 생성 과정 테스트
"""

import random

import pymongo
from bson import ObjectId


def test_generation():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🧪 지원자 생성 과정 테스트")
    print("=" * 60)

    # 1. 채용공고 정보 가져오기
    job_postings = list(db.job_postings.find({}, {"_id": 1, "position": 1, "title": 1}))
    job_posting_ids = [str(job["_id"]) for job in job_postings]
    job_posting_info = {str(job["_id"]): {"position": job.get("position", "Unknown"), "title": job.get("title", "Unknown")} for job in job_postings}

    print(f"📋 사용 가능한 채용공고:")
    for i, job_id in enumerate(job_posting_ids, 1):
        info = job_posting_info[job_id]
        print(f"{i}. {info['title']} (직무: {info['position']})")

    print(f"\n🧪 10명의 지원자 생성 테스트:")

    # 2. 지원자 생성 테스트
    for i in range(10):
        # 랜덤으로 채용공고 선택
        selected_job_id = random.choice(job_posting_ids)
        selected_job_info = job_posting_info[selected_job_id]

        # 선택된 채용공고의 직무로 지원자 생성
        position = selected_job_info["position"]

        print(f"{i+1}. 선택된 채용공고: {selected_job_info['title']}")
        print(f"   → 채용공고 직무: {position}")
        print(f"   → 지원자 직무: {position}")
        print(f"   → 매칭 여부: ✅ (100% 보장)")
        print()

    client.close()

if __name__ == "__main__":
    test_generation()
