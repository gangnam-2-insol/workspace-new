#!/usr/bin/env python3
import pymongo
from datetime import datetime

def check_inserted_data():
    """삽입된 데이터를 확인합니다."""
    
    try:
        # MongoDB 연결
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['hireme']
        
        # 총 지원자 수 확인
        total_count = db.applicants.count_documents({})
        print(f"📊 총 지원자 수: {total_count}명")
        
        # 최근 등록된 지원자 10명 확인
        recent_applicants = list(db.applicants.find().sort("created_at", -1).limit(10))
        
        print("\n🆕 최근 등록된 지원자 10명:")
        print("=" * 60)
        for i, app in enumerate(recent_applicants, 1):
            print(f"{i:2d}. {app['name']} ({app['position']})")
            print(f"    📧 {app['email']}")
            print(f"    📋 상태: {app['status']}")
            print(f"    🏢 채용공고 ID: {app.get('job_posting_id', 'N/A')}")
            print(f"    📅 등록일: {app['created_at']}")
            print("-" * 60)
        
        # 상태별 통계
        print("\n📈 상태별 지원자 분포:")
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = list(db.applicants.aggregate(status_pipeline))
        for stat in status_stats:
            print(f"  - {stat['_id']}: {stat['count']}명")
        
        # 직무별 통계
        print("\n💼 직무별 지원자 분포:")
        position_pipeline = [
            {"$group": {"_id": "$position", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        position_stats = list(db.applicants.aggregate(position_pipeline))
        for stat in position_stats[:10]:  # 상위 10개만 표시
            print(f"  - {stat['_id']}: {stat['count']}명")
        
        # 채용공고별 지원자 수
        print("\n🎯 채용공고별 지원자 분포:")
        job_pipeline = [
            {"$group": {"_id": "$job_posting_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        job_stats = list(db.applicants.aggregate(job_pipeline))
        print(f"  - 총 {len(job_stats)}개 채용공고에 지원자 분배")
        print(f"  - 최대 지원자 수: {job_stats[0]['count']}명")
        print(f"  - 최소 지원자 수: {job_stats[-1]['count']}명")
        print(f"  - 평균 지원자 수: {total_count/len(job_stats):.1f}명")
        
        print("\n✅ 데이터가 성공적으로 삽입되어 있습니다!")
        
    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_inserted_data()
