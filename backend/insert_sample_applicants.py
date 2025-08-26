#!/usr/bin/env python3
import pymongo
import json
from datetime import datetime
from bson import ObjectId

def insert_sample_applicants():
    """생성된 샘플 지원자 데이터를 MongoDB에 삽입합니다."""
    
    try:
        # MongoDB 연결
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['hireme']
        
        # 기존 지원자 수 확인
        existing_count = db.applicants.count_documents({})
        print(f"기존 지원자 수: {existing_count}명")
        
        # 샘플 데이터 로드
        with open('sample_applicants.json', 'r', encoding='utf-8') as f:
            sample_applicants = json.load(f)
        
        print(f"삽입할 샘플 데이터: {len(sample_applicants)}개")
        
        # 중복 확인 (이메일 기준)
        existing_emails = set()
        for doc in db.applicants.find({}, {"email": 1}):
            if "email" in doc:
                existing_emails.add(doc["email"])
        
        # 중복되지 않는 데이터만 필터링
        new_applicants = []
        for applicant in sample_applicants:
            if applicant["email"] not in existing_emails:
                # ObjectId 변환
                applicant["_id"] = ObjectId(applicant["_id"])
                if applicant.get("resume_id"):
                    applicant["resume_id"] = ObjectId(applicant["resume_id"])
                if applicant.get("cover_letter_id"):
                    applicant["cover_letter_id"] = ObjectId(applicant["cover_letter_id"])
                if applicant.get("portfolio_id"):
                    applicant["portfolio_id"] = ObjectId(applicant["portfolio_id"])
                
                # 날짜 변환
                applicant["created_at"] = datetime.fromisoformat(applicant["created_at"])
                applicant["updated_at"] = datetime.fromisoformat(applicant["updated_at"])
                
                new_applicants.append(applicant)
            else:
                print(f"⚠️ 중복 이메일 건너뜀: {applicant['email']}")
        
        if not new_applicants:
            print("❌ 삽입할 새로운 데이터가 없습니다. (모든 이메일이 중복)")
            return
        
        print(f"실제 삽입할 데이터: {len(new_applicants)}개")
        
        # 사용자 확인
        confirm = input(f"\n{len(new_applicants)}개의 샘플 지원자를 DB에 삽입하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 삽입이 취소되었습니다.")
            return
        
        # 배치 삽입
        try:
            result = db.applicants.insert_many(new_applicants)
            inserted_count = len(result.inserted_ids)
            
            print(f"✅ {inserted_count}개의 샘플 지원자가 성공적으로 삽입되었습니다!")
            
            # 최종 통계
            final_count = db.applicants.count_documents({})
            print(f"📊 최종 지원자 수: {final_count}명")
            
            # 삽입된 데이터 확인
            print("\n📋 삽입된 데이터 샘플 (최근 5개):")
            recent_applicants = list(db.applicants.find().sort("created_at", -1).limit(5))
            for i, applicant in enumerate(recent_applicants, 1):
                print(f"{i}. {applicant['name']} ({applicant['position']}) - {applicant['email']}")
            
        except Exception as insert_error:
            print(f"❌ 데이터 삽입 실패: {insert_error}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.close()

def cleanup_sample_data():
    """샘플 데이터를 정리합니다 (개발용)"""
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['hireme']
        
        # 샘플 데이터 로드
        with open('sample_applicants.json', 'r', encoding='utf-8') as f:
            sample_applicants = json.load(f)
        
        sample_emails = [applicant["email"] for applicant in sample_applicants]
        
        # 샘플 데이터 삭제
        result = db.applicants.delete_many({"email": {"$in": sample_emails}})
        print(f"🗑️ {result.deleted_count}개의 샘플 데이터가 삭제되었습니다.")
        
    except Exception as e:
        print(f"❌ 정리 중 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_sample_data()
    else:
        insert_sample_applicants()
