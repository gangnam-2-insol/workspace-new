#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
resumes 컬렉션의 데이터를 applicants 컬렉션으로 복사하는 스크립트
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def copy_resumes_to_applicants():
    """resumes 컬렉션의 데이터를 applicants 컬렉션으로 복사"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017/hireme")
        db = client.hireme
        
        print("🔍 resumes 컬렉션에서 데이터 조회 중...")
        
        # resumes 컬렉션의 모든 데이터 조회
        resumes = await db.resumes.find().to_list(1000)
        print(f"📊 총 {len(resumes)}개의 이력서 데이터를 찾았습니다.")
        
        if not resumes:
            print("❌ resumes 컬렉션에 데이터가 없습니다.")
            return
        
        # applicants 컬렉션의 기존 데이터 확인
        existing_applicants = await db.applicants.count_documents({})
        print(f"📋 applicants 컬렉션에 기존 {existing_applicants}개의 데이터가 있습니다.")
        
        # resumes 데이터를 applicants 형식으로 변환
        applicants_data = []
        for resume in resumes:
            applicant = {
                "name": resume.get("name", "이름 없음"),
                "position": resume.get("position", "포지션 없음"),
                "department": resume.get("department", "부서 없음"),
                "experience": resume.get("experience", "경력 없음"),
                "skills": resume.get("skills", "기술 없음"),
                "growthBackground": resume.get("growthBackground", ""),
                "motivation": resume.get("motivation", ""),
                "careerHistory": resume.get("careerHistory", ""),
                "analysisScore": resume.get("analysisScore", 0),
                "analysisResult": resume.get("analysisResult", ""),
                "status": resume.get("status", "pending"),
                "email": "이메일 정보 없음",
                "phone": "전화번호 정보 없음",
                "appliedDate": resume.get("created_at", datetime.now()),
                "created_at": resume.get("created_at", datetime.now()),
                "resume_id": str(resume.get("_id", ""))
            }
            applicants_data.append(applicant)
        
        print(f"🔄 {len(applicants_data)}개의 지원자 데이터로 변환 완료")
        
        # applicants 컬렉션에 데이터 삽입
        if applicants_data:
            result = await db.applicants.insert_many(applicants_data)
            print(f"✅ {len(result.inserted_ids)}개의 지원자 데이터를 applicants 컬렉션에 추가했습니다.")
        
        # 최종 데이터 수 확인
        final_count = await db.applicants.count_documents({})
        print(f"📊 applicants 컬렉션의 최종 데이터 수: {final_count}")
        
        print("🎉 데이터 복사가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(copy_resumes_to_applicants())
