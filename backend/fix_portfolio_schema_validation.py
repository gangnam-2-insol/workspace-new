from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 포트폴리오 스키마 검증 비활성화 ===')

try:
    # 포트폴리오 컬렉션의 스키마 검증 비활성화
    db.command({
        "collMod": "portfolios",
        "validator": {},
        "validationLevel": "off",
        "validationAction": "warn"
    })
    print("✅ 포트폴리오 스키마 검증 비활성화 완료")
    
    # 확인
    collection_info = db.command("listCollections", filter={"name": "portfolios"})
    print("포트폴리오 컬렉션 정보:", collection_info)
    
except Exception as e:
    print(f"❌ 스키마 검증 비활성화 실패: {e}")

client.close()
