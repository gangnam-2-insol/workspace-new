#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_status():
    client = MongoClient('mongodb://localhost:27017')
    db = client['hireme']
    
    print('📊 실제 지원자 상태 확인:')
    pipeline = [
        {'$group': {'_id': '$application_status', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    
    for doc in db.applicants.aggregate(pipeline):
        print(f'  {doc["_id"]}: {doc["count"]}명')
    
    print('\n📋 샘플 지원자 데이터:')
    for applicant in db.applicants.find({}, {'personal_info.name': 1, 'application_status': 1, 'status': 1}).limit(3):
        name = applicant.get('personal_info', {}).get('name', 'Unknown')
        app_status = applicant.get('application_status', 'N/A')
        status = applicant.get('status', 'N/A')
        print(f'  {name}: application_status={app_status}, status={status}')
    
    client.close()

if __name__ == "__main__":
    check_status()
