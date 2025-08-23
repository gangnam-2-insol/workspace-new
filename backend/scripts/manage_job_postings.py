#!/usr/bin/env python3
"""
채용공고 및 지원자 관리 스크립트

기능:
1. 오래된 채용공고를 삭제하여 5개만 남김
2. 삭제된 채용공고에 속한 지원자들을 나머지 채용공고로 재배치
3. 채용공고별 지원자 수 업데이트
"""

import pymongo
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Any

class JobPostingManager:
    def __init__(self):
        # MongoDB 연결 (기존 스크립트와 동일한 방식)
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']
        
    def get_all_job_postings(self) -> List[Dict[str, Any]]:
        """모든 채용공고를 생성일시 순으로 조회"""
        try:
            job_postings = list(self.db.job_postings.find().sort("created_at", 1))  # 오래된 순
            
            # ObjectId를 문자열로 변환
            for job in job_postings:
                job["_id"] = str(job["_id"])
                
            print(f"📋 총 {len(job_postings)}개의 채용공고를 찾았습니다.")
            return job_postings
        except Exception as e:
            print(f"❌ 채용공고 조회 실패: {e}")
            return []
    
    def get_applicants_by_job_posting(self, job_posting_id: str) -> List[Dict[str, Any]]:
        """특정 채용공고에 속한 지원자들 조회"""
        try:
            applicants = list(self.db.applicants.find({"job_posting_id": job_posting_id}))
            
            # ObjectId를 문자열로 변환
            for applicant in applicants:
                applicant["_id"] = str(applicant["_id"])
                
            return applicants
        except Exception as e:
            print(f"❌ 지원자 조회 실패 (채용공고 ID: {job_posting_id}): {e}")
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
    
    def delete_job_posting(self, job_posting_id: str) -> bool:
        """채용공고 삭제"""
        try:
            result = self.db.job_postings.delete_one({"_id": ObjectId(job_posting_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ 채용공고 삭제 실패 (채용공고 ID: {job_posting_id}): {e}")
            return False
    
    def reassign_applicants(self, old_job_posting_id: str, remaining_job_postings: List[str]) -> int:
        """지원자들을 나머지 채용공고로 재배치"""
        try:
            # 삭제될 채용공고에 속한 지원자들 조회
            applicants = self.get_applicants_by_job_posting(old_job_posting_id)
            
            if not applicants:
                print(f"ℹ️ 채용공고 {old_job_posting_id}에 속한 지원자가 없습니다.")
                return 0
            
            print(f"🔄 채용공고 {old_job_posting_id}의 {len(applicants)}명 지원자를 재배치합니다...")
            
            reassigned_count = 0
            for i, applicant in enumerate(applicants):
                # 라운드 로빈 방식으로 나머지 채용공고에 분배
                target_job_posting_id = remaining_job_postings[i % len(remaining_job_postings)]
                
                success = self.update_applicant_job_posting(applicant["_id"], target_job_posting_id)
                if success:
                    reassigned_count += 1
                    print(f"  ✅ {applicant.get('name', 'Unknown')} → {target_job_posting_id}")
                else:
                    print(f"  ❌ {applicant.get('name', 'Unknown')} 재배치 실패")
            
            return reassigned_count
        except Exception as e:
            print(f"❌ 지원자 재배치 실패: {e}")
            return 0
    
    def manage_job_postings(self, target_count: int = 5):
        """메인 관리 함수"""
        print(f"🚀 채용공고 및 지원자 관리 시작... (목표: {target_count}개)")
        
        # 1. 모든 채용공고 조회 (오래된 순)
        job_postings = self.get_all_job_postings()
        
        if len(job_postings) <= target_count:
            print(f"ℹ️ 채용공고가 {len(job_postings)}개뿐이어서 삭제할 수 없습니다.")
            return
        
        # 2. 삭제할 채용공고와 남길 채용공고 분리
        to_delete = job_postings[:-target_count]  # 가장 오래된 것들 삭제
        to_keep = job_postings[-target_count:]    # 최신 것들 유지
        
        print(f"\n🗑️ 삭제할 채용공고 ({len(to_delete)}개):")
        for job in to_delete:
            created_at = job.get("created_at", "Unknown")
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  - {job.get('title', 'Unknown')} (ID: {job['_id']}, 생성일: {created_at})")
        
        print(f"\n✅ 유지할 채용공고 ({len(to_keep)}개):")
        for job in to_keep:
            created_at = job.get("created_at", "Unknown")
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  - {job.get('title', 'Unknown')} (ID: {job['_id']}, 생성일: {created_at})")
        
        # 3. 각 삭제할 채용공고의 지원자들을 재배치
        remaining_job_posting_ids = [job["_id"] for job in to_keep]
        total_reassigned = 0
        
        for job_to_delete in to_delete:
            job_id = job_to_delete["_id"]
            job_title = job_to_delete.get("title", "Unknown")
            
            print(f"\n🔄 '{job_title}' 채용공고 처리 중...")
            
            # 지원자 재배치
            reassigned_count = self.reassign_applicants(job_id, remaining_job_posting_ids)
            total_reassigned += reassigned_count
            
            # 채용공고 삭제
            if self.delete_job_posting(job_id):
                print(f"✅ '{job_title}' 채용공고 삭제 완료")
            else:
                print(f"❌ '{job_title}' 채용공고 삭제 실패")
        
        # 4. 남은 채용공고들의 지원자 수 업데이트
        print(f"\n📊 남은 채용공고들의 지원자 수 업데이트 중...")
        for job in to_keep:
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
        print(f"  - 삭제된 채용공고: {len(to_delete)}개")
        print(f"  - 재배치된 지원자: {total_reassigned}명")
        print(f"  - 남은 채용공고: {len(to_keep)}개")
        
        # 6. 최종 통계
        final_job_count = self.db.job_postings.count_documents({})
        final_applicant_count = self.db.applicants.count_documents({})
        
        print(f"\n📈 최종 통계:")
        print(f"  - 총 채용공고: {final_job_count}개")
        print(f"  - 총 지원자: {final_applicant_count}명")

def main():
    """메인 함수"""
    manager = JobPostingManager()
    
    try:
        manager.manage_job_postings(target_count=5)  # 5개만 남기기
    except Exception as e:
        print(f"❌ 작업 중 오류 발생: {e}")
    finally:
        # MongoDB 연결 종료
        manager.client.close()

if __name__ == "__main__":
    main()
