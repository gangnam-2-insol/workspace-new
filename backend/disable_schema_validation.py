from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 포트폴리오 스키마 검증 비활성화 ===')

try:
    # 포트폴리오 컬렉션의 스키마 검증 비활성화
    result = db.command({
        "collMod": "portfolios",
        "validator": {},
        "validationLevel": "off",
        "validationAction": "warn"
    })
    print("✅ 포트폴리오 스키마 검증 비활성화 완료")
    print(f"결과: {result}")
    
    # 확인
    collection_info = db.command("listCollections", filter={"name": "portfolios"})
    if collection_info['cursor']['firstBatch']:
        portfolio_collection = collection_info['cursor']['firstBatch'][0]
        options = portfolio_collection.get('options', {})
        print(f"검증 레벨: {options.get('validationLevel', 'N/A')}")
        print(f"검증 액션: {options.get('validationAction', 'N/A')}")
    
except Exception as e:
    print(f"❌ 스키마 검증 비활성화 실패: {e}")

client.close()
