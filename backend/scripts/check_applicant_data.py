#!/usr/bin/env python3
"""
지원자 데이터 구조 확인 스크립트
"""

import json

import pymongo
from bson import ObjectId


class ApplicantDataChecker:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']

    def check_applicant_data_structure(self):
        """지원자 데이터 구조 확인"""
        print("🔍 지원자 데이터 구조 확인 중...")

        # 지원자 데이터 5개 조회
        applicants = list(self.db.applicants.find().limit(5))

        if not applicants:
            print("❌ 지원자 데이터가 없습니다.")
            return

        print(f"📊 총 {len(applicants)}개의 지원자 데이터를 확인합니다.\n")

        for i, applicant in enumerate(applicants, 1):
            print(f"=" * 80)
            print(f"👤 지원자 #{i}")
            print(f"=" * 80)

            print(f"📋 기본 정보:")
            print(f"   - 이름: {applicant.get('name', 'Unknown')}")
            print(f"   - 이메일: {applicant.get('email', 'Unknown')}")
            print(f"   - 전화번호: {applicant.get('phone', 'Unknown')}")
            print(f"   - 지원일: {applicant.get('application_date', 'Unknown')}")
            print(f"   - 지원 직무: {applicant.get('position', 'Unknown')}")

            # 분석 데이터 확인
            print(f"\n📊 분석 데이터:")

            # 이력서 분석
            if 'resume_analysis' in applicant and applicant['resume_analysis']:
                print("✅ 이력서 분석 데이터:")
                resume_analysis = applicant['resume_analysis']
                for key, value in list(resume_analysis.items())[:5]:  # 처음 5개만 표시
                    if isinstance(value, str) and len(value) > 100:
                        print(f"   - {key}: {value[:100]}...")
                    else:
                        print(f"   - {key}: {value}")
                if len(resume_analysis) > 5:
                    print(f"   ... (총 {len(resume_analysis)}개 항목)")
            else:
                print("❌ 이력서 분석 데이터 없음")

            # 자소서 분석
            if 'cover_letter_analysis' in applicant and applicant['cover_letter_analysis']:
                print("✅ 자소서 분석 데이터:")
                cover_analysis = applicant['cover_letter_analysis']
                for key, value in list(cover_analysis.items())[:5]:  # 처음 5개만 표시
                    if isinstance(value, str) and len(value) > 100:
                        print(f"   - {key}: {value[:100]}...")
                    else:
                        print(f"   - {key}: {value}")
                if len(cover_analysis) > 5:
                    print(f"   ... (총 {len(cover_analysis)}개 항목)")
            else:
                print("❌ 자소서 분석 데이터 없음")

            # 포트폴리오 분석
            if 'portfolio_analysis' in applicant and applicant['portfolio_analysis']:
                print("✅ 포트폴리오 분석 데이터:")
                portfolio_analysis = applicant['portfolio_analysis']
                for key, value in list(portfolio_analysis.items())[:5]:  # 처음 5개만 표시
                    if isinstance(value, str) and len(value) > 100:
                        print(f"   - {key}: {value[:100]}...")
                    else:
                        print(f"   - {key}: {value}")
                if len(portfolio_analysis) > 5:
                    print(f"   ... (총 {len(portfolio_analysis)}개 항목)")
            else:
                print("❌ 포트폴리오 분석 데이터 없음")

            # 프로젝트 마에스트로 점수 확인
            if 'project_maestro_score' in applicant:
                print(f"✅ 프로젝트 마에스트로 점수: {applicant['project_maestro_score']}")
            else:
                print("❌ 프로젝트 마에스트로 점수 없음")

            # 전체 필드 확인
            print(f"\n📋 전체 필드 목록:")
            for field in sorted(applicant.keys()):
                field_type = type(applicant[field]).__name__
                if field == '_id':
                    print(f"   - {field}: {field_type} (ObjectId)")
                elif isinstance(applicant[field], dict):
                    print(f"   - {field}: {field_type} ({len(applicant[field])}개 키)")
                elif isinstance(applicant[field], list):
                    print(f"   - {field}: {field_type} ({len(applicant[field])}개 항목)")
                else:
                    print(f"   - {field}: {field_type}")

            print("\n" + "=" * 80 + "\n")

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
