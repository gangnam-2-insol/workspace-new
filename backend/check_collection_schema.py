from pymongo import MongoClient
from bson import ObjectId

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 컬렉션 스키마 확인 ===')

# 각 컬렉션의 샘플 문서 확인
collections = ['resumes', 'cover_letters', 'portfolios']

for collection_name in collections:
    print(f'\n--- {collection_name} 컬렉션 ---')
    sample_docs = list(db[collection_name].find().limit(1))
    
    if sample_docs:
        print('샘플 문서 구조:')
        for key, value in sample_docs[0].items():
            print(f'  {key}: {type(value).__name__} = {value}')
    else:
        print('문서가 없습니다.')
    
    # 인덱스 확인
    indexes = list(db[collection_name].list_indexes())
    print(f'\n인덱스:')
    for idx in indexes:
        print(f'  {idx["name"]}: {idx["key"]}')

client.close()
