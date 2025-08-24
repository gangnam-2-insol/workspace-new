#!/usr/bin/env python3
"""
지원자와 채용공고 관계 확인 스크립트
"""

from datetime import datetime

import pymongo


def check_applicant_job_posting_relationship():
    """지원자와 채용공고 관계 확인"""

    # MongoDB 연결
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 지원자와 채용공고 관계 확인 중...\n")

    # 1. 전체 통계
    total_applicants = db.applicants.count_documents({})
    total_job_postings = db.job_postings.count_documents({})

    print(f"📊 전체 통계:")
    print(f"  - 총 지원자: {total_applicants}명")
    print(f"  - 총 채용공고: {total_job_postings}개\n")

    # 2. job_posting_id 필드 상태 확인
    applicants_with_job_posting = db.applicants.count_documents({"job_posting_id": {"$exists": True, "$ne": None}})
    applicants_without_job_posting = db.applicants.count_documents({"job_posting_id": {"$exists": False}})
    applicants_with_null_job_posting = db.applicants.count_documents({"job_posting_id": None})

    print(f"📋 job_posting_id 필드 상태:")
    print(f"  - job_posting_id가 있는 지원자: {applicants_with_job_posting}명")
    print(f"  - job_posting_id 필드가 없는 지원자: {applicants_without_job_posting}명")
    print(f"  - job_posting_id가 null인 지원자: {applicants_with_null_job_posting}명\n")

    # 3. 실제 채용공고 ID와 매칭되는지 확인
    job_posting_ids = [str(job["_id"]) for job in db.job_postings.find({}, {"_id": 1})]

    valid_job_posting_applicants = 0
    invalid_job_posting_applicants = 0

    for applicant in db.applicants.find({"job_posting_id": {"$exists": True, "$ne": None}}):
        if applicant["job_posting_id"] in job_posting_ids:
            valid_job_posting_applicants += 1
        else:
            invalid_job_posting_applicants += 1

    print(f"🔗 채용공고 ID 유효성:")
    print(f"  - 유효한 채용공고 ID를 가진 지원자: {valid_job_posting_applicants}명")
    print(f"  - 유효하지 않은 채용공고 ID를 가진 지원자: {invalid_job_posting_applicants}명\n")

    # 4. 샘플 데이터 확인
    print(f"📝 샘플 지원자 데이터 (처음 3명):")
    sample_applicants = list(db.applicants.find().limit(3))

    for i, applicant in enumerate(sample_applicants, 1):
        print(f"  {i}. {applicant.get('name', 'Unknown')}")
        print(f"     - 이메일: {applicant.get('email', 'Unknown')}")
        print(f"     - job_posting_id: {applicant.get('job_posting_id', 'None')}")
        print(f"     - 직무: {applicant.get('position', 'Unknown')}")
        print()

    # 5. 채용공고별 지원자 수 확인
    print(f"📊 채용공고별 지원자 수:")
    for job in db.job_postings.find():
        job_id = str(job["_id"])
        applicant_count = db.applicants.count_documents({"job_posting_id": job_id})
        print(f"  - {job.get('title', 'Unknown')} ({job_id}): {applicant_count}명")

    print(f"\n✅ 확인 완료!")

if __name__ == "__main__":
    check_applicant_job_posting_relationship()
