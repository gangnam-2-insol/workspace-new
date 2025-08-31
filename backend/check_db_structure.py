#!/usr/bin/env python3
"""
MongoDB 데이터베이스 구조 전체 점검 스크립트
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_db_structure():
    """MongoDB 데이터베이스 구조 전체 점검"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme

        print("=" * 80)
        print("MongoDB 데이터베이스 구조 전체 점검")
        print("=" * 80)

        # 1. 컬렉션 목록 확인
        print("\n1. 컬렉션 목록 확인")
        print("-" * 40)
        collections = await db.list_collection_names()
        print(f"총 컬렉션 수: {len(collections)}")
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count}개 문서")

        # 2. 지원자(applicants) 컬렉션 구조 분석
        print("\n2. 지원자(applicants) 컬렉션 구조 분석")
        print("-" * 40)
        applicants = await db.applicants.find({}).limit(3).to_list(3)
        if applicants:
            print(f"총 지원자 수: {await db.applicants.count_documents({})}")
            print("\n첫 번째 지원자 데이터 구조:")
            first_applicant = applicants[0]
            for key, value in first_applicant.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"  - {key}: {display_value} ({value_type})")

            print("\n모든 지원자의 필드 통계:")
            all_applicants = await db.applicants.find({}).to_list(None)
            field_counts = {}
            for applicant in all_applicants:
                for field in applicant.keys():
                    field_counts[field] = field_counts.get(field, 0) + 1

            for field, count in sorted(field_counts.items()):
                percentage = (count / len(all_applicants)) * 100
                print(f"  - {field}: {count}/{len(all_applicants)} ({percentage:.1f}%)")
        else:
            print("❌ 지원자 데이터가 없습니다.")

        # 3. 채용공고(job_postings) 컬렉션 구조 분석
        print("\n3. 채용공고(job_postings) 컬렉션 구조 분석")
        print("-" * 40)
        job_postings = await db.job_postings.find({}).limit(3).to_list(3)
        if job_postings:
            print(f"총 채용공고 수: {await db.job_postings.count_documents({})}")
            print("\n첫 번째 채용공고 데이터 구조:")
            first_job = job_postings[0]
            for key, value in first_job.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"  - {key}: {display_value} ({value_type})")

            print("\n모든 채용공고의 필드 통계:")
            all_jobs = await db.job_postings.find({}).to_list(None)
            field_counts = {}
            for job in all_jobs:
                for field in job.keys():
                    field_counts[field] = field_counts.get(field, 0) + 1

            for field, count in sorted(field_counts.items()):
                percentage = (count / len(all_jobs)) * 100
                print(f"  - {field}: {count}/{len(all_jobs)} ({percentage:.1f}%)")
        else:
            print("❌ 채용공고 데이터가 없습니다.")

        # 4. 자소서(cover_letters) 컬렉션 구조 분석
        print("\n4. 자소서(cover_letters) 컬렉션 구조 분석")
        print("-" * 40)
        cover_letters = await db.cover_letters.find({}).limit(3).to_list(3)
        if cover_letters:
            print(f"총 자소서 수: {await db.cover_letters.count_documents({})}")
            print("\n첫 번째 자소서 데이터 구조:")
            first_cover_letter = cover_letters[0]
            for key, value in first_cover_letter.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"  - {key}: {display_value} ({value_type})")

            print("\n모든 자소서의 필드 통계:")
            all_cover_letters = await db.cover_letters.find({}).to_list(None)
            field_counts = {}
            for cover_letter in all_cover_letters:
                for field in cover_letter.keys():
                    field_counts[field] = field_counts.get(field, 0) + 1

            for field, count in sorted(field_counts.items()):
                percentage = (count / len(all_cover_letters)) * 100
                print(f"  - {field}: {count}/{len(all_cover_letters)} ({percentage:.1f}%)")
        else:
            print("❌ 자소서 데이터가 없습니다.")

        # 5. 이력서(resumes) 컬렉션 구조 분석
        print("\n5. 이력서(resumes) 컬렉션 구조 분석")
        print("-" * 40)
        resumes = await db.resumes.find({}).limit(3).to_list(3)
        if resumes:
            print(f"총 이력서 수: {await db.resumes.count_documents({})}")
            print("\n첫 번째 이력서 데이터 구조:")
            first_resume = resumes[0]
            for key, value in first_resume.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"  - {key}: {display_value} ({value_type})")
        else:
            print("❌ 이력서 데이터가 없습니다.")

        # 6. 포트폴리오(portfolios) 컬렉션 구조 분석
        print("\n6. 포트폴리오(portfolios) 컬렉션 구조 분석")
        print("-" * 40)
        portfolios = await db.portfolios.find({}).limit(3).to_list(3)
        if portfolios:
            print(f"총 포트폴리오 수: {await db.portfolios.count_documents({})}")
            print("\n첫 번째 포트폴리오 데이터 구조:")
            first_portfolio = portfolios[0]
            for key, value in first_portfolio.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"  - {key}: {display_value} ({value_type})")
        else:
            print("❌ 포트폴리오 데이터가 없습니다.")

        # 7. 지원자-채용공고 연결 상태 확인
        print("\n7. 지원자-채용공고 연결 상태 확인")
        print("-" * 40)
        applicants_with_job = await db.applicants.count_documents({"job_posting_id": {"$exists": True, "$ne": None}})
        applicants_without_job = await db.applicants.count_documents({"job_posting_id": {"$exists": False}})
        applicants_with_null_job = await db.applicants.count_documents({"job_posting_id": None})

        print(f"총 지원자 수: {await db.applicants.count_documents({})}")
        print(f"채용공고 ID가 있는 지원자: {applicants_with_job}")
        print(f"채용공고 ID가 없는 지원자: {applicants_without_job}")
        print(f"채용공고 ID가 null인 지원자: {applicants_with_null_job}")

        # 8. 지원자-자소서 연결 상태 확인
        print("\n8. 지원자-자소서 연결 상태 확인")
        print("-" * 40)
        applicants_with_cover_letter = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})
        applicants_without_cover_letter = await db.applicants.count_documents({"cover_letter_id": {"$exists": False}})
        applicants_with_null_cover_letter = await db.applicants.count_documents({"cover_letter_id": None})

        print(f"총 지원자 수: {await db.applicants.count_documents({})}")
        print(f"자소서 ID가 있는 지원자: {applicants_with_cover_letter}")
        print(f"자소서 ID가 없는 지원자: {applicants_without_cover_letter}")
        print(f"자소서 ID가 null인 지원자: {applicants_with_null_cover_letter}")

        # 9. ID 타입 확인
        print("\n9. ID 타입 확인")
        print("-" * 40)

        # 지원자의 job_posting_id 타입 확인
        sample_applicant = await db.applicants.find_one({})
        if sample_applicant:
            job_posting_id = sample_applicant.get('job_posting_id')
            if job_posting_id:
                print(f"지원자의 job_posting_id 타입: {type(job_posting_id).__name__}")
                print(f"지원자의 job_posting_id 값: {job_posting_id}")

                # 해당 채용공고가 존재하는지 확인
                try:
                    if isinstance(job_posting_id, str):
                        job_posting = await db.job_postings.find_one({"_id": ObjectId(job_posting_id)})
                    else:
                        job_posting = await db.job_postings.find_one({"_id": job_posting_id})

                    if job_posting:
                        print(f"✅ 연결된 채용공고 존재: {job_posting.get('title', 'N/A')}")
                    else:
                        print(f"❌ 연결된 채용공고 없음")
                except Exception as e:
                    print(f"❌ 채용공고 조회 오류: {e}")

            cover_letter_id = sample_applicant.get('cover_letter_id')
            if cover_letter_id:
                print(f"지원자의 cover_letter_id 타입: {type(cover_letter_id).__name__}")
                print(f"지원자의 cover_letter_id 값: {cover_letter_id}")

                # 해당 자소서가 존재하는지 확인
                try:
                    if isinstance(cover_letter_id, str):
                        cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
                    else:
                        cover_letter = await db.cover_letters.find_one({"_id": cover_letter_id})

                    if cover_letter:
                        print(f"✅ 연결된 자소서 존재: {len(cover_letter.get('content', ''))}자")
                    else:
                        print(f"❌ 연결된 자소서 없음")
                except Exception as e:
                    print(f"❌ 자소서 조회 오류: {e}")

        # 10. 샘플 데이터와 실제 데이터 비교
        print("\n10. 샘플 데이터와 실제 데이터 비교")
        print("-" * 40)

        # 샘플 데이터 파일 읽기
        try:
            import json
            sample_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "sample_applicants_data.json")
            with open(sample_data_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)

            print("샘플 데이터의 지원자 필드:")
            if 'applicants' in sample_data and sample_data['applicants']:
                sample_applicant = sample_data['applicants'][0]
                for key in sample_applicant.keys():
                    print(f"  - {key}")

            print("\n샘플 데이터의 채용공고 필드:")
            if 'job_postings' in sample_data and sample_data['job_postings']:
                sample_job = sample_data['job_postings'][0]
                for key in sample_job.keys():
                    print(f"  - {key}")

        except Exception as e:
            print(f"샘플 데이터 파일 읽기 오류: {e}")

        client.close()
        print("\n" + "=" * 80)
        print("DB 구조 점검 완료")
        print("=" * 80)

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_db_structure())
