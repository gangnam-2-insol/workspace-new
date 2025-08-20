from pymongo import MongoClient
import json
from pathlib import Path

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 새로운 포트폴리오 스키마 적용 ===')

# 새로운 스키마 로드
schema_path = Path(__file__).parent / "schemas" / "portfolio_schema_new.json"

try:
    with open(schema_path, 'r', encoding='utf-8') as f:
        new_schema = json.load(f)
    print("✅ 새로운 스키마 로드 완료")
except Exception as e:
    print(f"❌ 스키마 로드 실패: {e}")
    client.close()
    exit()

# 현재 포트폴리오 데이터 검증
print("\n=== 현재 데이터 검증 ===")
portfolios = list(db.portfolios.find({}))
print(f"총 {len(portfolios)}개의 포트폴리오 데이터 검증 중...")

valid_count = 0
invalid_count = 0

for i, portfolio in enumerate(portfolios, 1):
    try:
        # 필수 필드 확인
        required_fields = ["applicant_id", "application_id", "extracted_text", "summary", "document_type", "status"]
        missing_fields = [field for field in required_fields if field not in portfolio or portfolio[field] is None]
        
        if missing_fields:
            print(f"❌ 포트폴리오 {i}: 필수 필드 누락 - {missing_fields}")
            invalid_count += 1
        else:
            print(f"✅ 포트폴리오 {i}: 검증 통과")
            valid_count += 1
            
    except Exception as e:
        print(f"❌ 포트폴리오 {i}: 검증 오류 - {e}")
        invalid_count += 1

print(f"\n검증 결과: {valid_count}개 통과, {invalid_count}개 실패")

# 새로운 스키마 적용
if invalid_count == 0:
    print("\n=== 새로운 스키마 적용 ===")
    try:
        result = db.command({
            "collMod": "portfolios",
            "validator": new_schema,
            "validationLevel": "moderate",
            "validationAction": "error"
        })
        print("✅ 새로운 스키마 적용 완료")
        print(f"결과: {result}")
        
        # 확인
        collection_info = db.command("listCollections", filter={"name": "portfolios"})
        if collection_info['cursor']['firstBatch']:
            portfolio_collection = collection_info['cursor']['firstBatch'][0]
            options = portfolio_collection.get('options', {})
            print(f"검증 레벨: {options.get('validationLevel', 'N/A')}")
            print(f"검증 액션: {options.get('validationAction', 'N/A')}")
            
    except Exception as e:
        print(f"❌ 스키마 적용 실패: {e}")
else:
    print("\n⚠️ 일부 데이터가 검증을 통과하지 못했습니다.")
    print("데이터를 수정한 후 다시 시도해주세요.")

client.close()
