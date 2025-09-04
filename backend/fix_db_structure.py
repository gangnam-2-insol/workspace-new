#!/usr/bin/env python3
"""
DB 구조 문제 수정 스크립트
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def fix_db_structure():
    """DB 구조 문제 수정"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme

        print("=" * 80)
        print("DB 구조 문제 수정 시작")
        print("=" * 80)

        # 1. 지원자 컬렉션 누락 필드 추가
        print("\n1. 지원자 컬렉션 누락 필드 추가")
        print("-" * 40)

        # phone 필드 추가
        result = await db.applicants.update_many(
            {"phone": {"$exists": False}},
            {"$set": {"phone": "010-0000-0000"}}
        )
        print(f"phone 필드 추가: {result.modified_count}개 문서 수정")

        # linkedin_url 필드 추가
        result = await db.applicants.update_many(
            {"linkedin_url": {"$exists": False}},
            {"$set": {"linkedin_url": ""}}
        )
        print(f"linkedin_url 필드 추가: {result.modified_count}개 문서 수정")

        # 2. 채용공고 컬렉션 누락 필드 추가
        print("\n2. 채용공고 컬렉션 누락 필드 추가")
        print("-" * 40)

        # views, bookmarks, shares 필드 추가
        result = await db.job_postings.update_many(
            {"views": {"$exists": False}},
            {"$set": {"views": 0}}
        )
        print(f"views 필드 추가: {result.modified_count}개 문서 수정")

        result = await db.job_postings.update_many(
            {"bookmarks": {"$exists": False}},
            {"$set": {"bookmarks": 0}}
        )
        print(f"bookmarks 필드 추가: {result.modified_count}개 문서 수정")

        result = await db.job_postings.update_many(
            {"shares": {"$exists": False}},
            {"$set": {"shares": 0}}
        )
        print(f"shares 필드 추가: {result.modified_count}개 문서 수정")

        # 3. 이력서 컬렉션 생성 (지원자별로)
        print("\n3. 이력서 컬렉션 생성")
        print("-" * 40)

        applicants = await db.applicants.find({}).to_list(None)
        resumes_created = 0

        for applicant in applicants:
            # 이미 이력서가 있는지 확인
            existing_resume = await db.resumes.find_one({"applicant_id": str(applicant["_id"])})
            if not existing_resume:
                resume_data = {
                    "applicant_id": str(applicant["_id"]),
                    "name": applicant.get("name", ""),
                    "email": applicant.get("email", ""),
                    "phone": applicant.get("phone", ""),
                    "position": applicant.get("position", ""),
                    "department": applicant.get("department", ""),
                    "experience": applicant.get("experience", ""),
                    "skills": applicant.get("skills", []),
                    "career_history": applicant.get("careerHistory", ""),
                    "education": "학사 이상",  # 기본값
                    "filename": f"이력서_{applicant.get('name', '')}.pdf",
                    "file_size": 1024000,  # 1MB
                    "status": "submitted",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }

                await db.resumes.insert_one(resume_data)
                resumes_created += 1

        print(f"이력서 생성: {resumes_created}개")

        # 4. 포트폴리오 컬렉션 생성 (지원자별로)
        print("\n4. 포트폴리오 컬렉션 생성")
        print("-" * 40)

        portfolios_created = 0

        for applicant in applicants:
            # 이미 포트폴리오가 있는지 확인
            existing_portfolio = await db.portfolios.find_one({"applicant_id": str(applicant["_id"])})
            if not existing_portfolio:
                portfolio_data = {
                    "applicant_id": str(applicant["_id"]),
                    "name": applicant.get("name", ""),
                    "title": f"{applicant.get('position', '')} 포트폴리오",
                    "description": f"{applicant.get('name', '')}님의 {applicant.get('position', '')} 포트폴리오입니다.",
                    "skills": applicant.get("skills", []),
                    "projects": [
                        {
                            "name": "주요 프로젝트 1",
                            "description": "주요 프로젝트 설명",
                            "technologies": applicant.get("skills", [])[:3] if applicant.get("skills") else []
                        }
                    ],
                    "github_url": applicant.get("github_url", ""),
                    "portfolio_url": applicant.get("portfolio_url", ""),
                    "filename": f"포트폴리오_{applicant.get('name', '')}.pdf",
                    "file_size": 2048000,  # 2MB
                    "status": "submitted",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }

                await db.portfolios.insert_one(portfolio_data)
                portfolios_created += 1

        print(f"포트폴리오 생성: {portfolios_created}개")

        # 5. 지원자 데이터에 resume_id, portfolio_id 업데이트
        print("\n5. 지원자 데이터에 resume_id, portfolio_id 업데이트")
        print("-" * 40)

        updated_count = 0
        for applicant in applicants:
            # 이력서 ID 찾기
            resume = await db.resumes.find_one({"applicant_id": str(applicant["_id"])})
            # 포트폴리오 ID 찾기
            portfolio = await db.portfolios.find_one({"applicant_id": str(applicant["_id"])})

            update_data = {}
            if resume and not applicant.get("resume_id"):
                update_data["resume_id"] = str(resume["_id"])
            if portfolio and not applicant.get("portfolio_id"):
                update_data["portfolio_id"] = str(portfolio["_id"])

            if update_data:
                await db.applicants.update_one(
                    {"_id": applicant["_id"]},
                    {"$set": update_data}
                )
                updated_count += 1

        print(f"지원자 데이터 업데이트: {updated_count}개")

        # 6. 최종 확인
        print("\n6. 수정 후 최종 확인")
        print("-" * 40)

        # 컬렉션별 문서 수 확인
        collections = ["applicants", "job_postings", "cover_letters", "resumes", "portfolios"]
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"{collection_name}: {count}개 문서")

        # 지원자 필드 완성도 확인
        sample_applicant = await db.applicants.find_one({})
        if sample_applicant:
            print(f"\n지원자 필드 확인:")
            required_fields = ["name", "email", "phone", "position", "department", "experience",
                             "skills", "job_posting_id", "cover_letter_id", "resume_id", "portfolio_id"]
            for field in required_fields:
                if field in sample_applicant:
                    print(f"  ✅ {field}: {sample_applicant[field]}")
                else:
                    print(f"  ❌ {field}: 누락")

        client.close()
        print("\n" + "=" * 80)
        print("DB 구조 수정 완료")
        print("=" * 80)

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_db_structure())
