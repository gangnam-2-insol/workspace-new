from pymongo import MongoClient
import json

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 현재 포트폴리오 데이터 구조 분석 ===')

# 포트폴리오 데이터 가져오기
portfolios = list(db.portfolios.find({}))

if not portfolios:
    print("❌ 포트폴리오 데이터가 없습니다.")
    client.close()
    exit()

print(f"총 {len(portfolios)}개의 포트폴리오 데이터 분석 중...")

# 첫 번째 포트폴리오의 구조 분석
sample_portfolio = portfolios[0]
print(f"\n=== 샘플 포트폴리오 구조 ({sample_portfolio.get('basic_info', {}).get('names', ['Unknown'])[0]}) ===")

# 필드별 타입 분석
field_types = {}
for key, value in sample_portfolio.items():
    if isinstance(value, list):
        field_types[key] = f"array of {type(value[0]).__name__ if value else 'any'}"
    else:
        field_types[key] = type(value).__name__

print("필드별 타입:")
for field, type_name in field_types.items():
    print(f"  {field}: {type_name}")

# 필수 필드 확인
required_fields = []
optional_fields = []
for field, value in sample_portfolio.items():
    if value is not None and value != "" and value != [] and value != {}:
        required_fields.append(field)
    else:
        optional_fields.append(field)

print(f"\n필수 필드 ({len(required_fields)}개):")
for field in required_fields:
    print(f"  - {field}")

print(f"\n선택적 필드 ({len(optional_fields)}개):")
for field in optional_fields:
    print(f"  - {field}")

# 중첩 구조 분석
print(f"\n=== 중첩 구조 분석 ===")
for key, value in sample_portfolio.items():
    if isinstance(value, dict):
        print(f"{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {type(sub_value).__name__}")
    elif isinstance(value, list) and value and isinstance(value[0], dict):
        print(f"{key} (array of objects):")
        for sub_key, sub_value in value[0].items():
            print(f"  {sub_key}: {type(sub_value).__name__}")

client.close()
