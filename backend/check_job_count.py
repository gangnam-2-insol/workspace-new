#!/usr/bin/env python3
"""
채용공고 수 확인 스크립트
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def check_job_count():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.hireme

    try:
        # 전체 채용공고 수
        total_count = await db.job_postings.count_documents({})
        print(f"📊 전체 채용공고 수: {total_count}개")

        # 상태별 채용공고 수
        published_count = await db.job_postings.count_documents({"status": "published"})
        draft_count = await db.job_postings.count_documents({"status": "draft"})
        closed_count = await db.job_postings.count_documents({"status": "closed"})

        print(f"📋 상태별 채용공고 수:")
        print(f"  - published: {published_count}개")
        print(f"  - draft: {draft_count}개")
        print(f"  - closed: {closed_count}개")

        # 최근 10개 채용공고 제목 확인
        recent_jobs = await db.job_postings.find().sort("created_at", -1).limit(10).to_list(10)
        print(f"\n📝 최근 채용공고 10개:")
        for i, job in enumerate(recent_jobs, 1):
            title = job.get("title", "Unknown")
            status = job.get("status", "Unknown")
            print(f"  {i}. {title} ({status})")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_job_count())
