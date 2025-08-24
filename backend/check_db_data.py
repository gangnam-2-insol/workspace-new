#!/usr/bin/env python3
"""
데이터베이스 지원자 목록 확인 스크립트
"""
from pymongo import MongoClient

def check_applicants():
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        # 지원자 수 확인
        count = db.applicants.count_documents({})
        print(f"📊 현재 데이터베이스 지원자 수: {count}")
        
        if count > 0:
            # 첫 3명의 지원자 정보 출력
            applicants = list(db.applicants.find().limit(3))
            print("\n📋 지원자 목록 (첫 3명):")
            for i, app in enumerate(applicants, 1):
                print(f"{i}. ID: {app['_id']}")
                print(f"   이름: {app.get('name', 'N/A')}")
                print(f"   직무: {app.get('position', 'N/A')}")
                print(f"   부서: {app.get('department', 'N/A')}")
                print(f"   자소서ID: {app.get('cover_letter_id', 'N/A')}")
                print()
        else:
            print("❌ 데이터베이스에 지원자가 없습니다.")
            
        client.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    check_applicants()
