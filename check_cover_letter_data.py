import asyncio
import os

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def check_cover_letter_data():
    # MongoDB 연결
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.hireme

    print("🔍 자소서 데이터 연동 상태 확인 중...")

    # 1. 지원자 데이터 확인
    print("\n📊 지원자 데이터 확인:")
    applicants = await db.applicants.find({}).limit(5).to_list(5)
    print(f"총 지원자 수: {await db.applicants.count_documents({})}")

    for i, applicant in enumerate(applicants):
        print(f"\n지원자 {i+1}:")
        print(f"  - ID: {applicant.get('_id')}")
        print(f"  - 이름: {applicant.get('name', 'N/A')}")
        print(f"  - 이메일: {applicant.get('email', 'N/A')}")
        print(f"  - cover_letter_id: {applicant.get('cover_letter_id', '없음')}")
        print(f"  - resume_id: {applicant.get('resume_id', '없음')}")
        print(f"  - job_posting_id: {applicant.get('job_posting_id', '없음')}")

    # 2. 자소서 컬렉션 확인
    print("\n📄 자소서 컬렉션 확인:")
    cover_letters_count = await db.cover_letters.count_documents({})
    print(f"자소서 컬렉션 문서 수: {cover_letters_count}")

    if cover_letters_count > 0:
        cover_letters = await db.cover_letters.find({}).limit(3).to_list(3)
        for i, cover_letter in enumerate(cover_letters):
            print(f"\n자소서 {i+1}:")
            print(f"  - ID: {cover_letter.get('_id')}")
            print(f"  - content 길이: {len(cover_letter.get('content', ''))}")
            print(f"  - extracted_text 길이: {len(cover_letter.get('extracted_text', ''))}")
            print(f"  - 필드들: {list(cover_letter.keys())}")

    # 3. 이력서 컬렉션 확인
    print("\n📋 이력서 컬렉션 확인:")
    resumes_count = await db.resumes.count_documents({})
    print(f"이력서 컬렉션 문서 수: {resumes_count}")

    if resumes_count > 0:
        resumes = await db.resumes.find({}).limit(3).to_list(3)
        for i, resume in enumerate(resumes):
            print(f"\n이력서 {i+1}:")
            print(f"  - ID: {resume.get('_id')}")
            print(f"  - content 길이: {len(resume.get('content', ''))}")
            print(f"  - extracted_text 길이: {len(resume.get('extracted_text', ''))}")
            print(f"  - 필드들: {list(resume.keys())}")

    # 4. 채용공고 컬렉션 확인
    print("\n💼 채용공고 컬렉션 확인:")
    job_postings_count = await db.job_postings.count_documents({})
    print(f"채용공고 컬렉션 문서 수: {job_postings_count}")

    if job_postings_count > 0:
        job_postings = await db.job_postings.find({}).limit(3).to_list(3)
        for i, job_posting in enumerate(job_postings):
            print(f"\n채용공고 {i+1}:")
            print(f"  - ID: {job_posting.get('_id')}")
            print(f"  - 제목: {job_posting.get('title', 'N/A')}")
            print(f"  - 회사: {job_posting.get('company', 'N/A')}")
            print(f"  - 필드들: {list(job_posting.keys())}")

    # 5. 연동 테스트
    print("\n🔗 연동 테스트:")
    for applicant in applicants[:3]:  # 처음 3명만 테스트
        print(f"\n지원자 '{applicant.get('name', 'N/A')}' 연동 테스트:")

        # 자소서 연동 테스트
        cover_letter_id = applicant.get('cover_letter_id')
        if cover_letter_id:
            try:
                cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                if cover_letter:
                    content = cover_letter.get('content') or cover_letter.get('extracted_text', '')
                    print(f"  ✅ 자소서 연동 성공 - 내용 길이: {len(content)}")
                else:
                    print(f"  ❌ 자소서 연동 실패 - ID {cover_letter_id}를 찾을 수 없음")
            except Exception as e:
                print(f"  ❌ 자소서 연동 오류: {e}")
        else:
            print(f"  ⚠️ 자소서 ID 없음")

        # 이력서 연동 테스트
        resume_id = applicant.get('resume_id')
        if resume_id:
            try:
                resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
                if resume:
                    content = resume.get('content') or resume.get('extracted_text', '')
                    print(f"  ✅ 이력서 연동 성공 - 내용 길이: {len(content)}")
                else:
                    print(f"  ❌ 이력서 연동 실패 - ID {resume_id}를 찾을 수 없음")
            except Exception as e:
                print(f"  ❌ 이력서 연동 오류: {e}")
        else:
            print(f"  ⚠️ 이력서 ID 없음")

        # 채용공고 연동 테스트
        job_posting_id = applicant.get('job_posting_id')
        if job_posting_id:
            try:
                job_posting = await db.job_postings.find_one({"_id": ObjectId(job_posting_id)})
                if job_posting:
                    print(f"  ✅ 채용공고 연동 성공 - 제목: {job_posting.get('title', 'N/A')}")
                else:
                    print(f"  ❌ 채용공고 연동 실패 - ID {job_posting_id}를 찾을 수 없음")
            except Exception as e:
                print(f"  ❌ 채용공고 연동 오류: {e}")
        else:
            print(f"  ⚠️ 채용공고 ID 없음")

    client.close()
    print("\n✅ 진단 완료")

if __name__ == "__main__":
    asyncio.run(check_cover_letter_data())

