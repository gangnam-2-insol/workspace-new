"""
MongoDB resumes 컬렉션 데이터 확인 스크립트
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "hireme"
COLLECTION_NAME = "resumes"

def check_resumes_collection():
    """resumes 컬렉션의 데이터를 확인"""
    try:
        # MongoDB 연결
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        print(f"📊 MongoDB 연결 성공: {MONGO_URI}")
        print(f"📁 데이터베이스: {DB_NAME}")
        print(f"📋 컬렉션: {COLLECTION_NAME}")
        
        # 컬렉션 존재 여부 확인
        if COLLECTION_NAME not in db.list_collection_names():
            print(f"❌ {COLLECTION_NAME} 컬렉션이 존재하지 않습니다.")
            return
        
        # 전체 문서 수 확인
        total_count = collection.count_documents({})
        print(f"📊 전체 문서 수: {total_count}")
        
        if total_count == 0:
            print("📝 컬렉션에 데이터가 없습니다.")
            return
        
        # 모든 문서 조회
        documents = list(collection.find({}))
        
        print(f"\n🔍 발견된 지원자 정보 ({total_count}명):")
        print("=" * 80)
        
        for i, doc in enumerate(documents, 1):
            print(f"\n👤 지원자 {i}:")
            print(f"   ID: {doc.get('_id', 'N/A')}")
            print(f"   이름: {doc.get('applicant_name', 'N/A')}")
            print(f"   직무: {doc.get('position', 'N/A')}")
            print(f"   부서: {doc.get('department', 'N/A')}")
            print(f"   경력: {doc.get('experience', 'N/A')}")
            print(f"   등록일: {doc.get('created_at', 'N/A')}")
            
            # 분석 결과가 있는 경우
            if 'analysis_result' in doc:
                analysis = doc['analysis_result']
                if isinstance(analysis, dict):
                    overall_score = analysis.get('overall_score', 'N/A')
                    print(f"   전체 점수: {overall_score}")
                    
                    # 세부 점수들
                    if 'analysis' in analysis:
                        scores = analysis['analysis']
                        for key, value in scores.items():
                            if 'score' in key:
                                print(f"   {key}: {value}")
        
        print("\n" + "=" * 80)
        
        # 컬렉션 스키마 확인
        print("\n📋 컬렉션 스키마:")
        if documents:
            sample_doc = documents[0]
            for key, value in sample_doc.items():
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    value_preview = value[:50] + "..."
                else:
                    value_preview = str(value)
                print(f"   {key}: {value_type} = {value_preview}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_resumes_collection()
