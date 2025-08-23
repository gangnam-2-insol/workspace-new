#!/usr/bin/env python3
"""
Pinecone 인덱스 정보 확인 스크립트
"""

import os
from dotenv import load_dotenv
from vector_service import VectorService

# 환경변수 로드
load_dotenv()

def main():
    try:
        print("=== Pinecone 인덱스 정보 확인 ===")
        
        # VectorService 초기화
        vector_service = VectorService()
        
        # 인덱스 정보 조회
        index_info = vector_service.get_index_info()
        print(f"인덱스 정보: {index_info}")
        
        # 통계 정보 조회
        stats = vector_service.get_stats()
        print(f"통계 정보: {stats}")
        
        # 차원 정보 강조
        dimension = index_info.get('dimension', 'Unknown')
        print(f"\n🔍 현재 인덱스 차원: {dimension}")
        
        if dimension == 384:
            print("❌ 문제: 인덱스가 아직 384차원입니다.")
            print("💡 해결책: Pinecone 콘솔에서 인덱스를 1536차원으로 재생성하세요.")
        elif dimension == 1536:
            print("✅ 올바름: 인덱스가 1536차원으로 설정되었습니다.")
        else:
            print(f"⚠️  예상치 못한 차원: {dimension}")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()