#!/usr/bin/env python3
"""
지원자 데이터 구조 확인 스크립트
"""

import pymongo
from bson import ObjectId
import json

class ApplicantDataChecker:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']
        
    def check_applicant_data_structure(self):
        """지원자 데이터 구조 확인"""
        print("🔍 지원자 데이터 구조 확인 중...")
        
        # 첫 번째 지원자 데이터 조회
        applicant = self.db.applicants.find_one()
        
        if not applicant:
            print("❌ 지원자 데이터가 없습니다.")
            return
            
        print(f"📋 지원자: {applicant.get('name', 'Unknown')}")
        print(f"📧 이메일: {applicant.get('email', 'Unknown')}")
        
        # 분석 데이터 확인
        print("\n📊 분석 데이터 구조:")
        
        # 이력서 분석
        if 'resume_analysis' in applicant:
            print("✅ 이력서 분석 데이터 존재")
            print(f"   - 키 개수: {len(applicant['resume_analysis'])}")
            if applicant['resume_analysis']:
                first_key = list(applicant['resume_analysis'].keys())[0]
                first_value = applicant['resume_analysis'][first_key]
                print(f"   - 첫 번째 항목: {first_key} = {first_value}")
        else:
            print("❌ 이력서 분석 데이터 없음")
            
        # 자소서 분석
        if 'cover_letter_analysis' in applicant:
            print("✅ 자소서 분석 데이터 존재")
            print(f"   - 키 개수: {len(applicant['cover_letter_analysis'])}")
            if applicant['cover_letter_analysis']:
                first_key = list(applicant['cover_letter_analysis'].keys())[0]
                first_value = applicant['cover_letter_analysis'][first_key]
                print(f"   - 첫 번째 항목: {first_key} = {first_value}")
        else:
            print("❌ 자소서 분석 데이터 없음")
            
        # 포트폴리오 분석
        if 'portfolio_analysis' in applicant:
            print("✅ 포트폴리오 분석 데이터 존재")
            print(f"   - 키 개수: {len(applicant['portfolio_analysis'])}")
            if applicant['portfolio_analysis']:
                first_key = list(applicant['portfolio_analysis'].keys())[0]
                first_value = applicant['portfolio_analysis'][first_key]
                print(f"   - 첫 번째 항목: {first_key} = {first_value}")
        else:
            print("❌ 포트폴리오 분석 데이터 없음")
            
        # 프로젝트 마에스트로 점수 확인
        if 'project_maestro_score' in applicant:
            print("✅ 프로젝트 마에스트로 점수 존재")
            print(f"   - 점수: {applicant['project_maestro_score']}")
        else:
            print("❌ 프로젝트 마에스트로 점수 없음")
            
        # 전체 필드 확인
        print(f"\n📋 전체 필드 목록:")
        for field in applicant.keys():
            print(f"   - {field}: {type(applicant[field]).__name__}")
            
        # JSON 형태로 출력 (ObjectId 제외)
        print(f"\n📄 데이터 샘플 (JSON):")
        # ObjectId를 문자열로 변환
        applicant_copy = applicant.copy()
        if '_id' in applicant_copy:
            applicant_copy['_id'] = str(applicant_copy['_id'])
        
        print(json.dumps(applicant_copy, indent=2, ensure_ascii=False, default=str))

def main():
    checker = ApplicantDataChecker()
    try:
        checker.check_applicant_data_structure()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        checker.client.close()

if __name__ == "__main__":
    main()
