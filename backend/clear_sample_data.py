#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from datetime import datetime
import json

def clear_sample_data():
    """채용공고와 지원자관리 샘플 데이터를 모두 삭제합니다."""
    
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017/')
        db = client['hireme']
        
        print("🔍 데이터베이스 연결 확인 중...")
        
        # 컬렉션 목록 확인
        collections = db.list_collection_names()
        print(f"📋 발견된 컬렉션: {collections}")
        
        # 삭제할 컬렉션들
        collections_to_clear = [
            'job_postings',      # 채용공고
            'applicants',        # 지원자
            'portfolios',        # 포트폴리오
            'cover_letters',     # 자기소개서
            'documents',         # 문서
            'resumes'           # 이력서
        ]
        
        total_deleted = 0
        
        for collection_name in collections_to_clear:
            if collection_name in collections:
                collection = db[collection_name]
                
                # 현재 데이터 개수 확인
                count_before = collection.count_documents({})
                
                if count_before > 0:
                    # 모든 데이터 삭제
                    result = collection.delete_many({})
                    deleted_count = result.deleted_count
                    total_deleted += deleted_count
                    
                    print(f"🗑️  {collection_name}: {count_before}개 → 0개 (삭제됨: {deleted_count}개)")
                else:
                    print(f"✅ {collection_name}: 이미 비어있음 (0개)")
            else:
                print(f"⚠️  {collection_name}: 컬렉션이 존재하지 않음")
        
        # 삭제 결과 요약
        print("\n" + "="*50)
        print("📊 삭제 완료 요약")
        print("="*50)
        print(f"총 삭제된 데이터: {total_deleted}개")
        print(f"삭제 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if total_deleted > 0:
            print("✅ 샘플 데이터 삭제가 완료되었습니다!")
        else:
            print("ℹ️  삭제할 샘플 데이터가 없었습니다.")
        
        # 현재 데이터베이스 상태 확인
        print("\n📋 현재 데이터베이스 상태:")
        for collection_name in collections_to_clear:
            if collection_name in collections:
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"  - {collection_name}: {count}개")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def confirm_deletion():
    """사용자에게 삭제 확인을 요청합니다."""
    print("⚠️  주의: 이 작업은 되돌릴 수 없습니다!")
    print("다음 데이터가 모두 삭제됩니다:")
    print("  - 채용공고 (job_postings)")
    print("  - 지원자 정보 (applicants)")
    print("  - 포트폴리오 (portfolios)")
    print("  - 자기소개서 (cover_letters)")
    print("  - 문서 (documents)")
    print("  - 이력서 (resumes)")
    print()
    
    while True:
        response = input("정말로 모든 샘플 데이터를 삭제하시겠습니까? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("y 또는 n을 입력해주세요.")

if __name__ == "__main__":
    print("🗑️  샘플 데이터 삭제 도구")
    print("="*50)
    
    if confirm_deletion():
        print("\n🔄 데이터 삭제를 시작합니다...")
        success = clear_sample_data()
        
        if success:
            print("\n🎉 모든 작업이 완료되었습니다!")
        else:
            print("\n❌ 데이터 삭제 중 오류가 발생했습니다.")
            sys.exit(1)
    else:
        print("\n❌ 작업이 취소되었습니다.")
