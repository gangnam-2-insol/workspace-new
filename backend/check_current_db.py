#!/usr/bin/env python3
"""
현재 DB 상태 확인 스크립트
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def check_current_db():
    """현재 DB 상태 확인"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("🔍 === 현재 DB 상태 확인 ===")

        # 1. 지원자 컬렉션 확인
        print("\n📋 === 지원자 컬렉션 ===")
        applicants = await db.applicants.find({}).to_list(length=10)
        print(f"총 지원자 수: {len(applicants)}")

        for app in applicants:
            print(f"  - ID: {app['_id']}")
            print(f"    이름: {app['name']}")
            print(f"    자소서ID: {app.get('cover_letter_id', 'None')}")
            print(f"    직무: {app.get('position', 'N/A')}")
            print()

        # 2. 자소서 컬렉션 확인
        print("📄 === 자소서 컬렉션 ===")
        cover_letters = await db.cover_letters.find({}).to_list(length=10)
        print(f"총 자소서 수: {len(cover_letters)}")

        for cl in cover_letters:
            print(f"  - ID: {cl['_id']}")
            print(f"    파일명: {cl.get('filename', 'N/A')}")
            print(f"    지원자ID: {cl.get('applicant_id', 'N/A')}")
            print()

        # 3. 이력서 컬렉션 확인
        print("📊 === 이력서 컬렉션 ===")
        resumes = await db.resumes.find({}).to_list(length=5)
        print(f"총 이력서 수: {len(resumes)}")

        for resume in resumes:
            print(f"  - ID: {resume['_id']}")
            print(f"    지원자ID: {resume.get('applicant_id', 'N/A')}")
            print()

        # 4. AI 분석 결과 컬렉션 확인
        print("🤖 === AI 분석 결과 컬렉션 ===")
        ai_results = await db.ai_analysis_results.find({}).to_list(length=5)
        print(f"총 AI 분석 결과 수: {len(ai_results)}")

        for result in ai_results:
            print(f"  - ID: {result['_id']}")
            print(f"    지원자ID: {result.get('applicant_id', 'N/A')}")
            print(f"    분석타입: {result.get('analysis_type', 'N/A')}")
            print()

        client.close()
        print("✅ DB 상태 확인 완료")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(check_current_db())
