#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_data():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['hireme']
    
    print('📊 데이터 확인:')
    print(f'  채용공고: {await db.job_postings.count_documents({})}개')
    print(f'  지원자: {await db.applicants.count_documents({})}명')
    
    print('\n📋 채용공고 목록:')
    async for job in db.job_postings.find({}, {'title': 1, 'company': 1, 'position': 1, 'applications_count': 1}):
        print(f'  - {job["company"]} {job["position"]}: {job["applications_count"]}명 지원')
    
    print('\n👥 지원자 샘플 (5명):')
    async for applicant in db.applicants.find({}, {'personal_info.name': 1, 'desired_position': 1, 'application_status': 1, 'scores.overall_score': 1}).limit(5):
        name = applicant["personal_info"]["name"]
        position = applicant["desired_position"] 
        status = applicant["application_status"]
        score = applicant["scores"]["overall_score"]
        print(f'  - {name} ({position}) - {status} - 점수: {score}점')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_data())
