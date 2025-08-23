#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_actual_data():
    client = MongoClient('mongodb://localhost:27017')
    db = client['hireme']
    
    print('📊 실제 데이터 확인:')
    print(f'  채용공고: {db.job_postings.count_documents({})}개')
    print(f'  지원자: {db.applicants.count_documents({})}명')
    
    print('\n📋 채용공고별 지원자 수:')
    for job in db.job_postings.find({}, {'company': 1, 'position': 1, 'applications_count': 1}):
        print(f'  - {job["company"]} {job["position"]}: {job["applications_count"]}명')
    
    print('\n👥 지원자 샘플 (5명):')
    for applicant in db.applicants.find({}, {'personal_info.name': 1, 'desired_position': 1, 'application_status': 1}).limit(5):
        name = applicant['personal_info']['name']
        position = applicant['desired_position']
        status = applicant['application_status']
        print(f'  - {name} ({position}) - {status}')
    
    client.close()

if __name__ == "__main__":
    check_actual_data()
