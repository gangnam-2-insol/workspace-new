import asyncio
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient


async def check_recent_jobs():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.hireme

    # 최근 1시간 내 draft 상태 채용공고 확인
    one_hour_ago = datetime.now() - timedelta(hours=1)

    recent_jobs = await db.job_postings.find({
        'status': 'draft',
        'created_at': {'$gte': one_hour_ago}
    }).sort('created_at', -1).to_list(10)

    print(f'최근 1시간 내 draft 채용공고: {len(recent_jobs)}개')
    for job in recent_jobs:
        print(f'- ID: {job["_id"]}, 제목: {job.get("title", "N/A")}, 상태: {job.get("status", "N/A")}')

    client.close()

if __name__ == "__main__":
    asyncio.run(check_recent_jobs())
