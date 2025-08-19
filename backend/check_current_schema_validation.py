from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 현재 포트폴리오 스키마 검증 상태 확인 ===')

try:
    # 포트폴리오 컬렉션 정보 조회
    collection_info = db.command("listCollections", filter={"name": "portfolios"})
    
    if collection_info['cursor']['firstBatch']:
        portfolio_collection = collection_info['cursor']['firstBatch'][0]
        
        print("📋 포트폴리오 컬렉션 정보:")
        print(f"   이름: {portfolio_collection.get('name')}")
        print(f"   타입: {portfolio_collection.get('type')}")
        
        # 옵션 정보 확인
        options = portfolio_collection.get('options', {})
        print(f"   옵션: {options}")
        
        # 검증 규칙 확인
        validator = options.get('validator', {})
        if validator:
            print("\n🔍 현재 스키마 검증 규칙:")
            print(f"   검증 레벨: {options.get('validationLevel', 'N/A')}")
            print(f"   검증 액션: {options.get('validationAction', 'N/A')}")
            print(f"   검증기: {validator}")
        else:
            print("\n❌ 스키마 검증이 설정되지 않음")
            
        # 인덱스 확인
        indexes = list(db.portfolios.list_indexes())
        print(f"\n📊 인덱스 정보:")
        for idx in indexes:
            print(f"   - {idx['name']}: {idx['key']}")
            
    else:
        print("❌ portfolios 컬렉션을 찾을 수 없습니다")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

# 현재 포트폴리오 문서 수 확인
try:
    portfolio_count = db.portfolios.count_documents({})
    print(f"\n📈 현재 포트폴리오 문서 수: {portfolio_count}")
    
    if portfolio_count > 0:
        # 샘플 문서 구조 확인
        sample_doc = db.portfolios.find_one()
        print(f"\n📄 샘플 문서 구조:")
        for key, value in sample_doc.items():
            print(f"   {key}: {type(value).__name__}")
            
except Exception as e:
    print(f"❌ 문서 확인 중 오류: {e}")

client.close()
