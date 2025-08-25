#!/usr/bin/env python3
"""
월별 지원자 데이터 분포 확인 스크립트
"""
import pymongo
from datetime import datetime
from collections import defaultdict

def check_monthly_distribution():
    """월별 지원자 분포를 확인합니다."""

    try:
        # MongoDB 연결
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['hireme']

        # 총 지원자 수 확인
        total_count = db.applicants.count_documents({})
        print(f"📊 총 지원자 수: {total_count}명")

        # 월별 분포 확인
        print("\n📅 월별 지원자 분포:")
        print("=" * 50)

        # created_at 필드가 있는 지원자들 조회
        applicants_with_date = list(db.applicants.find(
            {"created_at": {"$exists": True}},
            {"created_at": 1, "name": 1, "position": 1}
        ).sort("created_at", -1))

        print(f"📋 created_at 필드가 있는 지원자: {len(applicants_with_date)}명")

        # 월별 통계
        monthly_stats = defaultdict(int)
        monthly_details = defaultdict(list)

        for applicant in applicants_with_date:
            created_at = applicant.get('created_at')
            if created_at:
                # datetime 객체인지 확인
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        continue

                month_key = f"{created_at.year}-{created_at.month:02d}"
                monthly_stats[month_key] += 1
                monthly_details[month_key].append({
                    'name': applicant.get('name', 'N/A'),
                    'position': applicant.get('position', 'N/A'),
                    'date': created_at.strftime('%Y-%m-%d %H:%M:%S')
                })

        # 월별 통계 출력
        if monthly_stats:
            print("\n📈 월별 지원자 수:")
            for month in sorted(monthly_stats.keys()):
                count = monthly_stats[month]
                percentage = (count / total_count) * 100
                print(f"   {month}: {count}명 ({percentage:.1f}%)")

            print("\n📋 월별 상세 정보:")
            for month in sorted(monthly_stats.keys()):
                print(f"\n   📅 {month} ({monthly_stats[month]}명):")
                for i, detail in enumerate(monthly_details[month][:5], 1):  # 상위 5명만 표시
                    print(f"      {i}. {detail['name']} ({detail['position']}) - {detail['date']}")
                if len(monthly_details[month]) > 5:
                    print(f"      ... 외 {len(monthly_details[month]) - 5}명")
        else:
            print("❌ created_at 필드가 있는 데이터가 없습니다.")

        # created_at 필드가 없는 데이터 확인
        applicants_without_date = db.applicants.count_documents({"created_at": {"$exists": False}})
        if applicants_without_date > 0:
            print(f"\n⚠️ created_at 필드가 없는 지원자: {applicants_without_date}명")

        # 최근 10명의 created_at 확인
        print("\n🆕 최근 등록된 지원자 10명의 created_at:")
        recent_applicants = list(db.applicants.find().sort("_id", -1).limit(10))
        for i, app in enumerate(recent_applicants, 1):
            created_at = app.get('created_at', 'N/A')
            print(f"   {i}. {app.get('name', 'N/A')}: {created_at}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_monthly_distribution()
