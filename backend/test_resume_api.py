#!/usr/bin/env python3
"""
이력서 API 테스트 스크립트
"""

import asyncio
import motor.motor_asyncio
from bson import ObjectId
import json

# MongoDB 연결
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "hireme"

async def test_resume_api():
    """이력서 API 테스트"""
    
    # MongoDB 클라이언트 연결
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🔍 이력서 API 테스트 시작...")
    
    try:
        # 1. 지원자 목록 조회
        print("\n1️⃣ 지원자 목록 조회...")
        applicants = await db.applicants.find().limit(5).to_list(5)
        
        if not applicants:
            print("❌ 지원자가 없습니다.")
            return
        
        print(f"✅ {len(applicants)}명의 지원자를 찾았습니다.")
        
        # 2. 첫 번째 지원자의 이력서 정보 조회
        first_applicant = applicants[0]
        applicant_id = str(first_applicant["_id"])
        applicant_name = first_applicant.get("name", "알 수 없음")
        
        print(f"\n2️⃣ 지원자 '{applicant_name}'의 이력서 정보 조회...")
        print(f"   지원자 ID: {applicant_id}")
        
        # 3. 이력서 관련 필드 확인
        resume_fields = [
            "resume_id", "name", "position", "department", "experience", 
            "skills", "growthBackground", "motivation", "careerHistory",
            "analysisScore", "analysisResult", "extracted_text"
        ]
        
        print(f"\n3️⃣ 이력서 관련 필드 확인...")
        for field in resume_fields:
            value = first_applicant.get(field, "없음")
            if value and value != "없음":
                print(f"   ✅ {field}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
            else:
                print(f"   ❌ {field}: 없음")
        
        # 4. resumes 컬렉션 확인
        print(f"\n4️⃣ resumes 컬렉션 확인...")
        resumes_count = await db.resumes.count_documents({})
        print(f"   resumes 컬렉션 문서 수: {resumes_count}")
        
        if resumes_count > 0:
            sample_resume = await db.resumes.find_one()
            if sample_resume:
                print(f"   ✅ resumes 컬렉션에서 샘플 이력서 발견")
                print(f"   샘플 필드: {list(sample_resume.keys())}")
        
        # 5. API 응답 구조 시뮬레이션
        print(f"\n5️⃣ API 응답 구조 시뮬레이션...")
        
        # 이력서 데이터 구성
        resume_data = {
            "name": first_applicant.get("name", ""),
            "position": first_applicant.get("position", ""),
            "department": first_applicant.get("department", ""),
            "experience": first_applicant.get("experience", ""),
            "skills": first_applicant.get("skills", ""),
            "growthBackground": first_applicant.get("growthBackground", ""),
            "motivation": first_applicant.get("motivation", ""),
            "careerHistory": first_applicant.get("careerHistory", ""),
            "analysisScore": first_applicant.get("analysisScore", 0),
            "analysisResult": first_applicant.get("analysisResult", ""),
            "status": first_applicant.get("status", "pending"),
            "created_at": first_applicant.get("created_at"),
            "extracted_text": first_applicant.get("extracted_text", ""),
            "file_metadata": first_applicant.get("file_metadata", {}),
            "source": "applicants_collection"
        }
        
        # 지원자 정보 포함
        resume_data["applicant_info"] = {
            "id": str(first_applicant["_id"]),
            "name": first_applicant.get("name", ""),
            "email": first_applicant.get("email", ""),
            "phone": first_applicant.get("phone", ""),
            "status": first_applicant.get("status", ""),
            "applied_at": first_applicant.get("applied_at"),
            "created_at": first_applicant.get("created_at")
        }
        
        # API 응답 구조
        api_response = {
            "success": True,
            "message": "이력서 정보 조회 성공",
            "data": resume_data
        }
        
        print(f"   ✅ API 응답 구조 생성 완료")
        print(f"   응답 크기: {len(json.dumps(api_response, default=str))} bytes")
        
        # 6. 프론트엔드에서 사용할 수 있는 데이터 구조 확인
        print(f"\n6️⃣ 프론트엔드 데이터 구조 확인...")
        
        frontend_data = api_response["data"]
        
        # 이력서 분석 결과
        if frontend_data.get("analysisResult"):
            print(f"   📊 이력서 분석 결과: 있음")
            print(f"      내용: {frontend_data['analysisResult'][:100]}...")
        else:
            print(f"   📊 이력서 분석 결과: 없음")
        
        # 분석 점수
        if frontend_data.get("analysisScore"):
            print(f"   🎯 분석 점수: {frontend_data['analysisScore']}/100")
        else:
            print(f"   🎯 분석 점수: 없음")
        
        # 추출된 텍스트
        if frontend_data.get("extracted_text"):
            print(f"   📄 추출된 텍스트: 있음 ({len(frontend_data['extracted_text'])} 글자)")
        else:
            print(f"   📄 추출된 텍스트: 없음")
        
        # 기술 스택
        if frontend_data.get("skills"):
            print(f"   🛠️ 기술 스택: {frontend_data['skills']}")
        else:
            print(f"   🛠️ 기술 스택: 없음")
        
        print(f"\n✅ 이력서 API 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # MongoDB 연결 종료
        client.close()

if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(test_resume_api())
