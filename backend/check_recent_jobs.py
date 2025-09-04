import asyncio
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient


async def check_recent_job_postings():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.hireme

    # 최근 1시간 내 등록된 채용공고 확인
    recent_time = datetime.now() - timedelta(hours=1)

    recent_jobs = await db.job_postings.find({
        'created_at': {'$gte': recent_time}
    }).to_list(length=10)

    print(f'최근 1시간 내 등록된 채용공고: {len(recent_jobs)}개')

    for job in recent_jobs:
        print(f'- ID: {job["_id"]}')
        print(f'  제목: {job.get("title", "N/A")}')
        print(f'  상태: {job.get("status", "N/A")}')
        print(f'  생성일: {job.get("created_at", "N/A")}')
        print()

    # 전체 채용공고 수도 확인
    total_count = await db.job_postings.count_documents({})
    print(f'전체 채용공고 수: {total_count}개')

    client.close()

if __name__ == "__main__":
    asyncio.run(check_recent_job_postings())
