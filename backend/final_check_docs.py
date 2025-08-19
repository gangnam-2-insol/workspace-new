from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 현재 문서 상태 확인 ===')

# 각 컬렉션의 문서 수 확인
resumes_count = db.resumes.count_documents({})
cover_letters_count = db.cover_letters.count_documents({})
portfolios_count = db.portfolios.count_documents({})

print(f'이력서: {resumes_count}개')
print(f'자소서: {cover_letters_count}개')
print(f'포트폴리오: {portfolios_count}개')

# 지원자 수 확인
applicants_count = db.applicants.count_documents({})
print(f'지원자: {applicants_count}명')

# 샘플 문서 확인
print('\n=== 샘플 문서 확인 ===')
if resumes_count > 0:
    sample_resume = db.resumes.find_one()
    print(f'이력서 샘플: {sample_resume.get("title", "제목 없음")}')

if cover_letters_count > 0:
    sample_cover = db.cover_letters.find_one()
    print(f'자소서 샘플: {sample_cover.get("title", "제목 없음")}')

if portfolios_count > 0:
    sample_portfolio = db.portfolios.find_one()
    print(f'포트폴리오 샘플: {sample_portfolio.get("title", "제목 없음")}')

client.close()
