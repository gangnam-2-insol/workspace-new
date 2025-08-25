#!/usr/bin/env python3
"""
데이터베이스 사용현황 및 구조 분석 스크립트
"""
from pymongo import MongoClient
from datetime import datetime
import json

def analyze_database():
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        print("=" * 80)
        print("📊 MongoDB 데이터베이스 사용현황 및 구조 분석")
        print("=" * 80)

        # 1. 컬렉션 목록 및 문서 수 확인
        print("\n🔍 1. 컬렉션별 문서 수")
        print("-" * 50)
        collections = db.list_collection_names()
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"📋 {collection}: {count:,}개 문서")

        # 2. applicants 컬렉션 상세 분석
        print("\n🔍 2. APPLICANTS 컬렉션 상세 분석")
        print("-" * 50)

        applicants_count = db.applicants.count_documents({})
        print(f"📊 전체 지원자 수: {applicants_count:,}명")

        # 상태별 분포
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = list(db.applicants.aggregate(status_pipeline))

        print("\n📈 상태별 분포:")
        for stat in status_stats:
            status = stat["_id"] if stat["_id"] else "미정"
            count = stat["count"]
            percentage = (count / applicants_count) * 100
            print(f"   • {status}: {count:,}명 ({percentage:.1f}%)")

        # 직무별 분포
        position_pipeline = [
            {"$group": {"_id": "$position", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        position_stats = list(db.applicants.aggregate(position_pipeline))

        print("\n💼 직무별 분포:")
        for stat in position_stats[:10]:  # 상위 10개만
            position = stat["_id"] if stat["_id"] else "미정"
            count = stat["count"]
            percentage = (count / applicants_count) * 100
            print(f"   • {position}: {count:,}명 ({percentage:.1f}%)")

        # 부서별 분포
        department_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        department_stats = list(db.applicants.aggregate(department_pipeline))

        print("\n🏢 부서별 분포:")
        for stat in department_stats:
            department = stat["_id"] if stat["_id"] else "미정"
            count = stat["count"]
            percentage = (count / applicants_count) * 100
            print(f"   • {department}: {count:,}명 ({percentage:.1f}%)")

        # 3. 필드 구조 분석
        print("\n🔍 3. APPLICANTS 컬렉션 필드 구조")
        print("-" * 50)

        # 샘플 문서 가져오기
        sample_doc = db.applicants.find_one()
        if sample_doc:
            print("📋 필드 목록:")
            for field, value in sample_doc.items():
                field_type = type(value).__name__
                print(f"   • {field}: {field_type}")

        # 4. 데이터 품질 분석
        print("\n🔍 4. 데이터 품질 분석")
        print("-" * 50)

        # 필수 필드 누락 확인
        missing_email = db.applicants.count_documents({"email": {"$exists": False}})
        missing_phone = db.applicants.count_documents({"phone": {"$exists": False}})
        missing_name = db.applicants.count_documents({"name": {"$exists": False}})

        print(f"📧 이메일 누락: {missing_email:,}명 ({missing_email/applicants_count*100:.1f}%)")
        print(f"📞 전화번호 누락: {missing_phone:,}명 ({missing_phone/applicants_count*100:.1f}%)")
        print(f"👤 이름 누락: {missing_name:,}명 ({missing_name/applicants_count*100:.1f}%)")

        # 5. 최근 데이터 분석
        print("\n🔍 5. 최근 데이터 분석")
        print("-" * 50)

        # 최근 7일간 등록된 지원자
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_applicants = db.applicants.count_documents({"created_at": {"$gte": week_ago}})
        print(f"📅 최근 7일 등록: {recent_applicants:,}명")

        # 6. 기타 컬렉션 분석
        print("\n🔍 6. 기타 컬렉션 분석")
        print("-" * 50)

        for collection in collections:
            if collection != "applicants":
                count = db[collection].count_documents({})
                if count > 0:
                    print(f"📋 {collection}: {count:,}개 문서")

                    # 샘플 문서 구조 확인
                    sample = db[collection].find_one()
                    if sample:
                        print(f"   필드: {list(sample.keys())}")

        # 7. 인덱스 정보
        print("\n🔍 7. 인덱스 정보")
        print("-" * 50)

        indexes = db.applicants.list_indexes()
        print("📋 applicants 컬렉션 인덱스:")
        for index in indexes:
            print(f"   • {index['name']}: {index['key']}")

        client.close()

        print("\n" + "=" * 80)
        print("✅ 데이터베이스 분석 완료")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    analyze_database()
