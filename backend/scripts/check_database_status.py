#!/usr/bin/env python3
"""
데이터베이스 상태 확인 스크립트

기능:
1. 현재 채용공고 현황 조회
2. 채용공고별 지원자 수 확인
3. 전체 통계 정보 표시
"""

from datetime import datetime
from typing import Any, Dict, List

import pymongo


class DatabaseStatusChecker:
    def __init__(self):
        # MongoDB 연결 (기존 스크립트와 동일한 방식)
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']

    def get_job_postings_with_applicants(self) -> List[Dict[str, Any]]:
        """채용공고와 지원자 수 정보 조회"""
        try:
            # 모든 채용공고 조회 (생성일시 순)
            job_postings = list(self.db.job_postings.find().sort("created_at", 1))

            # 각 채용공고별 지원자 수 계산
            for job in job_postings:
                job["_id"] = str(job["_id"])
                job_posting_id = job["_id"]

                # 해당 채용공고에 속한 지원자 수 계산
                applicant_count = self.db.applicants.count_documents({"job_posting_id": job_posting_id})
                job["actual_applicants"] = applicant_count

                # 지원자 수가 다르면 업데이트
                if job.get("applicants", 0) != applicant_count:
                    self.db.job_postings.update_one(
                        {"_id": job["_id"]},
                        {"$set": {"applicants": applicant_count}}
                    )
                    job["applicants"] = applicant_count
                    job["updated"] = True
                else:
                    job["updated"] = False

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
            print(f"❌ 지원자 조회 실패: {e}")
            return []

    def get_orphaned_applicants(self) -> List[Dict[str, Any]]:
        """채용공고가 없는 지원자들 조회"""
        try:
            orphaned = list(self.db.applicants.find({"job_posting_id": {"$exists": False}}))

            # ObjectId를 문자열로 변환
            for applicant in orphaned:
                applicant["_id"] = str(applicant["_id"])

            return orphaned
        except Exception as e:
            print(f"❌ 고아 지원자 조회 실패: {e}")
            return []

    def check_database_status(self):
        """데이터베이스 상태 확인"""
        print("🔍 데이터베이스 상태 확인 중...")

        # 1. 전체 통계
        total_jobs = self.db.job_postings.count_documents({})
        total_applicants = self.db.applicants.count_documents({})

        print(f"\n📊 전체 통계:")
        print(f"  - 총 채용공고: {total_jobs}개")
        print(f"  - 총 지원자: {total_applicants}명")

        if total_jobs == 0:
            print("⚠️ 채용공고가 없습니다.")
            return

        # 2. 채용공고별 상세 정보
        job_postings = self.get_job_postings_with_applicants()

        print(f"\n📋 채용공고별 현황:")
        print("-" * 80)
        print(f"{'순번':<4} {'제목':<25} {'회사':<15} {'지원자':<6} {'상태':<10} {'생성일':<15}")
        print("-" * 80)

        for i, job in enumerate(job_postings, 1):
            title = job.get("title", "Unknown")[:24]
            company = job.get("company", "Unknown")[:14]
            applicants = job.get("applicants", 0)
            status = job.get("status", "Unknown")
            created_at = job.get("created_at", "Unknown")

            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d")

            update_marker = " 🔄" if job.get("updated", False) else ""
            print(f"{i:<4} {title:<25} {company:<15} {applicants:<6} {status:<10} {created_at:<15}{update_marker}")

        print("-" * 80)

        # 3. 고아 지원자 확인
        orphaned_applicants = self.get_orphaned_applicants()
        if orphaned_applicants:
            print(f"\n⚠️ 채용공고가 없는 지원자 ({len(orphaned_applicants)}명):")
            for applicant in orphaned_applicants[:5]:  # 처음 5명만 표시
                print(f"  - {applicant.get('name', 'Unknown')} ({applicant.get('email', 'Unknown')})")
            if len(orphaned_applicants) > 5:
                print(f"  ... 외 {len(orphaned_applicants) - 5}명")
        else:
            print(f"\n✅ 모든 지원자가 채용공고에 소속되어 있습니다!")

        # 4. job_posting_id가 null인 지원자 확인
        null_job_posting_applicants = list(self.db.applicants.find({"job_posting_id": None}))
        if null_job_posting_applicants:
            print(f"\n⚠️ job_posting_id가 null인 지원자 ({len(null_job_posting_applicants)}명):")
            for applicant in null_job_posting_applicants[:5]:  # 처음 5명만 표시
                print(f"  - {applicant.get('name', 'Unknown')} ({applicant.get('email', 'Unknown')})")
            if len(null_job_posting_applicants) > 5:
                print(f"  ... 외 {len(null_job_posting_applicants) - 5}명")

        # 5. 삭제 예정 채용공고 정보
        if len(job_postings) > 5:
            to_delete = job_postings[:5]
            total_applicants_to_reassign = sum(job.get("applicants", 0) for job in to_delete)

            print(f"\n🗑️ 삭제 예정 채용공고 (가장 오래된 5개):")
            print(f"  - 삭제될 채용공고: {len(to_delete)}개")
            print(f"  - 재배치될 지원자: {total_applicants_to_reassign}명")

            print(f"\n  📝 삭제 예정 목록:")
            for i, job in enumerate(to_delete, 1):
                title = job.get("title", "Unknown")
                applicants = job.get("applicants", 0)
                created_at = job.get("created_at", "Unknown")

                if isinstance(created_at, datetime):
                    created_at = created_at.strftime("%Y-%m-%d %H:%M")

                print(f"    {i}. {title} ({applicants}명 지원, 생성일: {created_at})")
        else:
            print(f"\nℹ️ 채용공고가 {len(job_postings)}개뿐이어서 삭제할 수 없습니다.")

        # 6. 지원자 분포 분석
        print(f"\n📈 지원자 분포 분석:")
        if job_postings:
            applicants_per_job = [job.get("applicants", 0) for job in job_postings]
            avg_applicants = sum(applicants_per_job) / len(applicants_per_job)
            max_applicants = max(applicants_per_job)
            min_applicants = min(applicants_per_job)

            print(f"  - 평균 지원자 수: {avg_applicants:.1f}명")
            print(f"  - 최대 지원자 수: {max_applicants}명")
            print(f"  - 최소 지원자 수: {min_applicants}명")

            # 지원자 수가 많은 채용공고
            high_applicant_jobs = [job for job in job_postings if job.get("applicants", 0) > avg_applicants]
            if high_applicant_jobs:
                print(f"  - 평균 이상 지원자 수 채용공고: {len(high_applicant_jobs)}개")

            # 지원자 수가 적은 채용공고
            low_applicant_jobs = [job for job in job_postings if job.get("applicants", 0) < avg_applicants]
            if low_applicant_jobs:
                print(f"  - 평균 이하 지원자 수 채용공고: {len(low_applicant_jobs)}개")

def main():
    """메인 함수"""
    checker = DatabaseStatusChecker()

    try:
        checker.check_database_status()
    except Exception as e:
        print(f"❌ 상태 확인 중 오류 발생: {e}")
    finally:
        # MongoDB 연결 종료
        checker.client.close()

if __name__ == "__main__":
    main()
