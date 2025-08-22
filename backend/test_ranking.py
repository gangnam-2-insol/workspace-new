#!/usr/bin/env python3
"""
적합도 랭킹 서비스 테스트 스크립트
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.suitability_ranking_service import SuitabilityRankingService

def test_ranking_service():
    """랭킹 서비스를 테스트합니다."""
    try:
        # MongoDB 연결
        client = MongoClient("mongodb://localhost:27017/")
        db = client["hireme"]
        
        print("🔗 MongoDB 연결 성공")
        
        # 랭킹 서비스 초기화
        ranking_service = SuitabilityRankingService(db)
        
        # 현재 지원자 수 확인
        applicants_count = db.applicants.count_documents({})
        print(f"📊 현재 지원자 수: {applicants_count}명")
        
        if applicants_count == 0:
            print("❌ 지원자가 없습니다. 먼저 지원자 데이터를 추가해주세요.")
            return
        
        # 랭킹 계산 실행
        print("�� 적합도 랭킹 계산 시작...")
        result = ranking_service.calculate_all_rankings()
        
        print("✅ 랭킹 계산 완료!")
        print(f"📈 결과: {result['message']}")
        print(f"👥 총 지원자: {result['total_applicants']}명")
        
        # 상위 랭킹 확인
        print("\n🏆 이력서 상위 5명:")
        resume_rankings = ranking_service.get_top_rankings("resume", 5)
        for ranking in resume_rankings:
            print(f"  {ranking['rank']}위: {ranking['name']} ({ranking['score']}점)")
        
        print("\n🏆 자기소개서 상위 5명:")
        cover_letter_rankings = ranking_service.get_top_rankings("coverLetter", 5)
        for ranking in cover_letter_rankings:
            print(f"  {ranking['rank']}위: {ranking['name']} ({ranking['score']}점)")
        
        print("\n🏆 포트폴리오 상위 5명:")
        portfolio_rankings = ranking_service.get_top_rankings("portfolio", 5)
        for ranking in portfolio_rankings:
            print(f"  {ranking['rank']}위: {ranking['name']} ({ranking['score']}점)")
        
        print("\n🏆 종합 상위 5명:")
        total_rankings = ranking_service.get_top_rankings("total", 5)
        for ranking in total_rankings:
            print(f"  {ranking['rank']}위: {ranking['name']} ({ranking['score']}점)")
        
        # 특정 지원자의 랭킹 확인
        print("\n🔍 첫 번째 지원자의 랭킹 정보:")
        first_applicant = db.applicants.find_one({})
        if first_applicant:
            applicant_id = str(first_applicant["_id"])
            applicant_rankings = ranking_service.get_applicant_rankings(applicant_id)
            print(f"  이름: {first_applicant.get('name', 'N/A')}")
            print(f"  이력서 랭킹: {applicant_rankings.get('resume', 'N/A')}위")
            print(f"  자기소개서 랭킹: {applicant_rankings.get('coverLetter', 'N/A')}위")
            print(f"  포트폴리오 랭킹: {applicant_rankings.get('portfolio', 'N/A')}위")
            print(f"  종합 랭킹: {applicant_rankings.get('total', 'N/A')}위")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🧪 적합도 랭킹 서비스 테스트 시작")
    test_ranking_service()
