from pymongo import MongoClient

def check_status():
    client = MongoClient('mongodb://localhost:27017')
    db = client.hireme
    
    # 전체 지원자 수
    total = db.applicants.count_documents({})
    
    # 업데이트된 지원자 수
    updated = db.applicants.count_documents({'updated_at': {'$exists': True}})
    
    # 업데이트되지 않은 지원자 수
    not_updated = total - updated
    
    print(f"📊 지원자 업데이트 현황:")
    print(f"  - 전체: {total}명")
    print(f"  - 업데이트 완료: {updated}명")
    print(f"  - 미완료: {not_updated}명")
    
    if not_updated > 0:
        print(f"\n⚠️ 아직 업데이트되지 않은 지원자들:")
        not_updated_apps = list(db.applicants.find({'updated_at': {'$exists': False}}, {'name': 1, 'position': 1}))
        for app in not_updated_apps[:10]:
            print(f"  - {app.get('name', '이름 없음')}: {app.get('position', '직무 없음')}")
    
    client.close()

if __name__ == "__main__":
    check_status()
