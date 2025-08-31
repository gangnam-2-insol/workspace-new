#!/usr/bin/env python3
"""
기존 데이터 정리 및 새로운 샘플 데이터 업로드
"""
import asyncio
import sys
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def clear_and_reupload_data():
    """기존 데이터 정리 및 새로운 샘플 데이터 업로드"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme
        
        print("=== 기존 데이터 정리 ===")
        
        # 기존 데이터 삭제
        applicants_result = await db.applicants.delete_many({})
        print(f"삭제된 지원자 수: {applicants_result.deleted_count}")
        
        cover_letters_result = await db.cover_letters.delete_many({})
        print(f"삭제된 자소서 수: {cover_letters_result.deleted_count}")
        
        job_postings_result = await db.job_postings.delete_many({})
        print(f"삭제된 채용공고 수: {job_postings_result.deleted_count}")
        
        print("\n=== 새로운 샘플 데이터 업로드 ===")
        
        # 샘플 데이터 파일 읽기
        sample_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "sample_applicants_data.json")
        
        with open(sample_data_path, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        print(f"샘플 데이터 로드 완료: 지원자 {len(sample_data['applicants'])}명, 채용공고 {len(sample_data['job_postings'])}개")
        
        # 채용공고 먼저 저장
        if 'job_postings' in sample_data:
            job_postings = []
            for job_posting in sample_data['job_postings']:
                job_posting_data = {
                    "title": job_posting.get('title', ''),
                    "company": job_posting.get('company', ''),
                    "location": job_posting.get('location', ''),
                    "department": job_posting.get('department', ''),
                    "position": job_posting.get('position', ''),
                    "type": job_posting.get('type', 'full-time'),
                    "salary": job_posting.get('salary', ''),
                    "experience": job_posting.get('experience', '신입'),
                    "education": job_posting.get('education', ''),
                    "description": job_posting.get('description', ''),
                    "requirements": job_posting.get('requirements', ''),
                    "required_skills": job_posting.get('required_skills', []),
                    "preferred_skills": job_posting.get('preferred_skills', []),
                    "required_documents": job_posting.get('required_documents', []),
                    "status": job_posting.get('status', 'published'),
                    "applicants": 0,
                    "views": 0,
                    "bookmarks": 0,
                    "shares": 0,
                    "deadline": job_posting.get('deadline', ''),
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
                job_postings.append(job_posting_data)
            
            if job_postings:
                result = await db.job_postings.insert_many(job_postings)
                print(f"채용공고 저장 완료: {len(result.inserted_ids)}개")
        
        # 지원자 및 자소서 데이터 저장
        if 'applicants' in sample_data:
            # 기존 채용공고 ID 목록 가져오기
            existing_job_postings = await db.job_postings.find({}, {"_id": 1}).to_list(None)
            job_posting_ids = [str(job["_id"]) for job in existing_job_postings]
            
            import random
            from datetime import datetime
            
            for applicant in sample_data['applicants']:
                # 랜덤하게 채용공고 ID 할당
                assigned_job_posting_id = random.choice(job_posting_ids) if job_posting_ids else None
                
                # 지원자 데이터 저장
                applicant_data = {
                    "name": applicant.get('name', ''),
                    "email": applicant.get('email', ''),
                    "phone": applicant.get('phone', ''),
                    "github_url": applicant.get('github_url', ''),
                    "linkedin_url": applicant.get('linkedin_url', ''),
                    "portfolio_url": applicant.get('portfolio_url', ''),
                    "position": applicant.get('position', ''),
                    "department": applicant.get('department', ''),
                    "experience": applicant.get('experience', '신입'),
                    "skills": applicant.get('skills', []),
                    "growthBackground": applicant.get('growthBackground', ''),
                    "motivation": applicant.get('motivation', ''),
                    "careerHistory": applicant.get('careerHistory', ''),
                    "analysisScore": applicant.get('analysisScore', 0),
                    "analysisResult": applicant.get('analysisResult', ''),
                    "status": applicant.get('status', 'pending'),
                    "job_posting_id": assigned_job_posting_id,
                    "portfolio_id": applicant.get('portfolio_id', ''),
                    "cover_letter_id": applicant.get('cover_letter_id', ''),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # 지원자 저장
                result = await db.applicants.insert_one(applicant_data)
                
                # 자소서 데이터 저장 (cover_letter_id가 있는 경우)
                if result.inserted_id and applicant.get('cover_letter_id'):
                    cover_letter_data = {
                        "_id": ObjectId(applicant.get('cover_letter_id')),
                        "applicant_id": str(result.inserted_id),
                        "content": f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}",
                        "extracted_text": f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}",
                        "growthBackground": applicant.get('growthBackground', ''),
                        "motivation": applicant.get('motivation', ''),
                        "careerHistory": applicant.get('careerHistory', ''),
                        "filename": f"자소서_{applicant.get('name', '')}.txt",
                        "file_size": len(f"{applicant.get('growthBackground', '')}\n\n{applicant.get('motivation', '')}\n\n{applicant.get('careerHistory', '')}"),
                        "status": "submitted",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    try:
                        await db.cover_letters.insert_one(cover_letter_data)
                        print(f"✅ {applicant.get('name', '')} - 지원자 및 자소서 저장 완료")
                    except Exception as e:
                        print(f"⚠️ {applicant.get('name', '')} - 자소서 저장 실패: {e}")
                else:
                    print(f"✅ {applicant.get('name', '')} - 지원자 저장 완료 (자소서 없음)")
        
        # 최종 확인
        print("\n=== 최종 데이터 확인 ===")
        applicants_count = await db.applicants.count_documents({})
        cover_letters_count = await db.cover_letters.count_documents({})
        job_postings_count = await db.job_postings.count_documents({})
        
        print(f"총 지원자 수: {applicants_count}")
        print(f"총 자소서 수: {cover_letters_count}")
        print(f"총 채용공고 수: {job_postings_count}")
        
        # 자소서 분석 가능한 지원자 확인
        analyzable_count = await db.applicants.aggregate([
            {
                "$lookup": {
                    "from": "cover_letters",
                    "localField": "cover_letter_id",
                    "foreignField": "_id",
                    "as": "cover_letter"
                }
            },
            {
                "$match": {
                    "cover_letter": {"$ne": []}
                }
            },
            {
                "$count": "count"
            }
        ]).to_list(1)
        
        analyzable_count = analyzable_count[0]['count'] if analyzable_count else 0
        print(f"자소서 분석 가능한 지원자 수: {analyzable_count}")
        
        client.close()
        print("\n✅ 데이터 재업로드 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_and_reupload_data())
