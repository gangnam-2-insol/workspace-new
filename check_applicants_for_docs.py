from pymongo import MongoClient
from bson import ObjectId

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== hireme 데이터베이스 구조 ===')
print('컬렉션 목록:', db.list_collection_names())

print('\n=== applicants 컬렉션 ===')
applicants = list(db.applicants.find({}, {'name': 1, 'position': 1, 'experience': 1, 'skills': 1, '_id': 1}))

for i, app in enumerate(applicants, 1):
    print(f'{i}. {app["name"]} - {app["position"]} ({app["experience"]}년 경력)')
    print(f'   스킬: {app["skills"]}')
    print(f'   ID: {app["_id"]}')
    print()

print(f'\n총 {len(applicants)}명의 지원자가 있습니다.')

# 기존 문서 컬렉션 확인
print('\n=== 기존 문서 컬렉션 확인 ===')
resumes_count = db.resumes.count_documents({})
cover_letters_count = db.cover_letters.count_documents({})
portfolios_count = db.portfolios.count_documents({})

print(f'이력서: {resumes_count}개')
print(f'자소서: {cover_letters_count}개')
print(f'포트폴리오: {portfolios_count}개')

client.close()
