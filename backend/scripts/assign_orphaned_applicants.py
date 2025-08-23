#!/usr/bin/env python3
"""
채용공고가 없는 지원자들을 기존 채용공고에 분배하는 스크립트

기능:
1. 채용공고가 없는 지원자들 조회
2. 기존 채용공고들에 라운드 로빈 방식으로 분배
3. 채용공고별 지원자 수 업데이트
"""

import pymongo
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Any

class OrphanedApplicantManager:
    def __init__(self):
        # MongoDB 연결 (기존 스크립트와 동일한 방식)
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']
        
    def get_orphaned_applicants(self) -> List[Dict[str, Any]]:
        """채용공고가 없는 지원자들 조회"""
        try:
            # job_posting_id가 없거나 null인 지원자들 조회
            orphaned = list(self.db.applicants.find({
                "$or": [
                    {"job_posting_id": {"$exists": False}},
                    {"job_posting_id": None},
                    {"job_posting_id": ""}
                ]
            }))
            
            # ObjectId를 문자열로 변환
            for applicant in orphaned:
                applicant["_id"] = str(applicant["_id"])
                
            print(f"📋 채용공고가 없는 지원자: {len(orphaned)}명")
            return orphaned
        except Exception as e:
            print(f"❌ 고아 지원자 조회 실패: {e}")
            return []
    
    def get_active_job_postings(self) -> List[Dict[str, Any]]:
        """활성 채용공고들 조회"""
        try:
            job_postings = list(self.db.job_postings.find())
            
            # ObjectId를 문자열로 변환
            for job in job_postings:
                job["_id"] = str(job["_id"])
                
            print(f"📋 활성 채용공고: {len(job_postings)}개")
            return job_postings
        except Exception as e:
            print(f"❌ 채용공고 조회 실패: {e}")
            return []
    
    def update_applicant_job_posting(self, applicant_id: str, new_job_posting_id: str) -> bool:
        """지원자의 채용공고 ID 업데이트"""
        try:
            result = self.db.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": {"job_posting_id": new_job_posting_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ 지원자 업데이트 실패 (지원자 ID: {applicant_id}): {e}")
            return False
    
    def update_job_posting_applicant_count(self, job_posting_id: str) -> bool:
        """채용공고의 지원자 수 업데이트"""
        try:
            # 해당 채용공고에 속한 지원자 수 계산
            count = self.db.applicants.count_documents({"job_posting_id": job_posting_id})
            
            # 채용공고 업데이트
            result = self.db.job_postings.update_one(
                {"_id": ObjectId(job_posting_id)},
                {"$set": {"applicants": count}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ 채용공고 지원자 수 업데이트 실패 (채용공고 ID: {job_posting_id}): {e}")
            return False
    
    def assign_orphaned_applicants(self):
        """고아 지원자들을 채용공고에 분배"""
        print("🚀 고아 지원자 분배 작업 시작...")
        
        # 1. 고아 지원자들 조회
        orphaned_applicants = self.get_orphaned_applicants()
        
        if not orphaned_applicants:
            print("ℹ️ 채용공고가 없는 지원자가 없습니다.")
            return
        
        # 2. 활성 채용공고들 조회
        job_postings = self.get_active_job_postings()
        
        if not job_postings:
            print("❌ 활성 채용공고가 없습니다.")
            return
        
        job_posting_ids = [job["_id"] for job in job_postings]
        
        print(f"\n📝 분배 대상:")
        print(f"  - 고아 지원자: {len(orphaned_applicants)}명")
        print(f"  - 채용공고: {len(job_postings)}개")
        
        # 3. 라운드 로빈 방식으로 분배
        assigned_count = 0
        
        print(f"\n🔄 지원자 분배 중...")
        for i, applicant in enumerate(orphaned_applicants):
            # 라운드 로빈 방식으로 채용공고 선택
            target_job_posting_id = job_posting_ids[i % len(job_posting_ids)]
            target_job = next((job for job in job_postings if job["_id"] == target_job_posting_id), None)
            target_job_title = target_job.get("title", "Unknown") if target_job else "Unknown"
            
            success = self.update_applicant_job_posting(applicant["_id"], target_job_posting_id)
            if success:
                assigned_count += 1
                print(f"  ✅ {applicant.get('name', 'Unknown')} → '{target_job_title}'")
            else:
                print(f"  ❌ {applicant.get('name', 'Unknown')} 분배 실패")
        
        # 4. 각 채용공고의 지원자 수 업데이트
        print(f"\n📊 채용공고별 지원자 수 업데이트 중...")
        for job in job_postings:
            job_id = job["_id"]
            job_title = job.get("title", "Unknown")
            
            if self.update_job_posting_applicant_count(job_id):
                # 업데이트된 지원자 수 조회
                updated_job = self.db.job_postings.find_one({"_id": ObjectId(job_id)})
                if updated_job:
                    print(f"  ✅ '{job_title}': {updated_job.get('applicants', 0)}명")
            else:
                print(f"  ❌ '{job_title}' 지원자 수 업데이트 실패")
        
        # 5. 결과 요약
        print(f"\n🎉 작업 완료!")
        print(f"  - 분배된 지원자: {assigned_count}명")
        
        # 6. 최종 통계
        final_job_count = self.db.job_postings.count_documents({})
        final_applicant_count = self.db.applicants.count_documents({})
        remaining_orphaned = self.db.applicants.count_documents({
            "$or": [
                {"job_posting_id": {"$exists": False}},
                {"job_posting_id": None},
                {"job_posting_id": ""}
            ]
        })
        
        print(f"\n📈 최종 통계:")
        print(f"  - 총 채용공고: {final_job_count}개")
        print(f"  - 총 지원자: {final_applicant_count}명")
        print(f"  - 남은 고아 지원자: {remaining_orphaned}명")

def main():
    """메인 함수"""
    manager = OrphanedApplicantManager()
    
    try:
        manager.assign_orphaned_applicants()
    except Exception as e:
        print(f"❌ 작업 중 오류 발생: {e}")
    finally:
        # MongoDB 연결 종료
        manager.client.close()

if __name__ == "__main__":
    main()
