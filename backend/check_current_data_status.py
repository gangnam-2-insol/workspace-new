from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client.hireme

print('=== 현재 데이터베이스 상태 확인 ===')

# 각 컬렉션별 데이터 수 확인
applicants_count = db.applicants.count_documents({})
resumes_count = db.resumes.count_documents({})
cover_letters_count = db.cover_letters.count_documents({})
portfolios_count = db.portfolios.count_documents({})

print(f"📊 데이터 현황:")
print(f"  지원자: {applicants_count}명")
print(f"  이력서: {resumes_count}개")
print(f"  자소서: {cover_letters_count}개")
print(f"  포트폴리오: {portfolios_count}개")

# 지원자 목록 확인
print(f"\n👥 지원자 목록:")
applicants = list(db.applicants.find({}, {"name": 1, "position": 1, "email": 1}))
for i, applicant in enumerate(applicants, 1):
    name = applicant.get('name', '이름 없음')
    position = applicant.get('position', '직무 없음')
    email = applicant.get('email', '이메일 없음')
    print(f"  {i}. {name} ({position}) - {email}")

# 각 지원자별 문서 연결 상태 확인
print(f"\n📋 지원자별 문서 연결 상태:")
for applicant in applicants:
    applicant_id = str(applicant['_id'])
    name = applicant.get('name', '이름 없음')
    
    # 각 문서 타입별 개수 확인
    resume_count = db.resumes.count_documents({"applicant_id": applicant_id})
    cover_letter_count = db.cover_letters.count_documents({"applicant_id": applicant_id})
    portfolio_count = db.portfolios.count_documents({"applicant_id": applicant_id})
    
    print(f"  {name}:")
    print(f"    - 이력서: {resume_count}개")
    print(f"    - 자소서: {cover_letter_count}개")
    print(f"    - 포트폴리오: {portfolio_count}개")

# 완성도 확인
print(f"\n✅ 완성도 분석:")
total_applicants = applicants_count
completed_applicants = 0

for applicant in applicants:
    applicant_id = str(applicant['_id'])
    name = applicant.get('name', '이름 없음')
    
    resume_count = db.resumes.count_documents({"applicant_id": applicant_id})
    cover_letter_count = db.cover_letters.count_documents({"applicant_id": applicant_id})
    portfolio_count = db.portfolios.count_documents({"applicant_id": applicant_id})
    
    if resume_count > 0 and cover_letter_count > 0 and portfolio_count > 0:
        completed_applicants += 1
        print(f"  ✅ {name}: 완성 (이력서✓, 자소서✓, 포트폴리오✓)")
    else:
        missing_docs = []
        if resume_count == 0:
            missing_docs.append("이력서")
        if cover_letter_count == 0:
            missing_docs.append("자소서")
        if portfolio_count == 0:
            missing_docs.append("포트폴리오")
        print(f"  ❌ {name}: 미완성 (누락: {', '.join(missing_docs)})")

completion_rate = (completed_applicants / total_applicants * 100) if total_applicants > 0 else 0
print(f"\n📈 전체 완성도: {completion_rate:.1f}% ({completed_applicants}/{total_applicants})")

if completion_rate == 100:
    print("🎉 모든 지원자의 문서가 완성되었습니다!")
elif completion_rate >= 80:
    print("👍 대부분의 문서가 완성되었습니다.")
else:
    print("⚠️ 아직 많은 문서가 누락되었습니다.")

client.close()
