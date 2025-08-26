#!/usr/bin/env python3
"""
AI 이력서 분석 기능 테스트 스크립트
"""

import asyncio
import motor.motor_asyncio
from bson import ObjectId
import json
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "hireme"

async def test_ai_analysis():
    """AI 분석 기능 테스트"""
    
    # MongoDB 클라이언트 연결
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🤖 AI 이력서 분석 기능 테스트 시작...")
    
    try:
        # 1. 지원자 목록 조회
        print("\n1️⃣ 지원자 목록 조회...")
        applicants = await db.applicants.find().limit(3).to_list(3)
        
        if not applicants:
            print("❌ 지원자가 없습니다.")
            return
        
        print(f"✅ {len(applicants)}명의 지원자를 찾았습니다.")
        
        # 2. AI 분석 모듈 테스트
        print("\n2️⃣ AI 분석 모듈 테스트...")
        
        try:
            # 모델 import 테스트
            from models.resume_analysis import ResumeAnalysisRequest, ResumeAnalysisResult
            print("✅ 모델 import 성공")
            
            # 분석기 import 테스트
            from modules.ai.resume_analyzer import OpenAIResumeAnalyzer
            print("✅ OpenAI 분석기 import 성공")
            
            # HuggingFace 분석기 import 테스트
            from modules.ai.huggingface_analyzer import HuggingFaceResumeAnalyzer
            print("✅ HuggingFace 분석기 import 성공")
            
            # 서비스 import 테스트
            from modules.ai.resume_analysis_service import ResumeAnalysisService
            print("✅ 분석 서비스 import 성공")
            
        except ImportError as e:
            print(f"❌ 모듈 import 실패: {str(e)}")
            return
        
        # 3. 분석 서비스 초기화 테스트
        print("\n3️⃣ 분석 서비스 초기화 테스트...")
        
        try:
            analysis_service = ResumeAnalysisService(db)
            print("✅ 분석 서비스 초기화 성공")
            
            # OpenAI API 키 확인
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                print("✅ OpenAI API 키 설정됨")
            else:
                print("⚠️ OpenAI API 키가 설정되지 않음 (환경변수 OPENAI_API_KEY 필요)")
            
        except Exception as e:
            print(f"❌ 분석 서비스 초기화 실패: {str(e)}")
            return
        
        # 4. 지원자 데이터 구조 확인
        print("\n4️⃣ 지원자 데이터 구조 확인...")
        
        first_applicant = applicants[0]
        applicant_id = str(first_applicant["_id"])
        applicant_name = first_applicant.get("name", "알 수 없음")
        
        print(f"   지원자: {applicant_name} (ID: {applicant_id})")
        
        # 이력서 관련 필드 확인
        resume_fields = [
            "name", "position", "department", "experience", 
            "skills", "growthBackground", "motivation", "careerHistory",
            "extracted_text"
        ]
        
        available_fields = []
        for field in resume_fields:
            if first_applicant.get(field):
                available_fields.append(field)
        
        print(f"   사용 가능한 이력서 필드: {', '.join(available_fields)}")
        
        # 5. AI 분석 요청 생성 테스트
        print("\n5️⃣ AI 분석 요청 생성 테스트...")
        
        try:
            analysis_request = ResumeAnalysisRequest(
                applicant_id=applicant_id,
                analysis_type="openai",
                force_reanalysis=False
            )
            print("✅ 분석 요청 생성 성공")
            print(f"   요청 내용: {analysis_request.dict()}")
            
        except Exception as e:
            print(f"❌ 분석 요청 생성 실패: {str(e)}")
            return
        
        # 6. 분석 상태 조회 테스트
        print("\n6️⃣ 분석 상태 조회 테스트...")
        
        try:
            status = await analysis_service.get_analysis_status()
            print("✅ 분석 상태 조회 성공")
            print(f"   전체 지원자: {status.total_applicants}")
            print(f"   분석 완료: {status.analyzed_count}")
            print(f"   진행률: {status.progress_percentage}%")
            
        except Exception as e:
            print(f"❌ 분석 상태 조회 실패: {str(e)}")
        
        # 7. 기존 분석 결과 확인
        print("\n7️⃣ 기존 분석 결과 확인...")
        
        try:
            existing_analysis = await analysis_service.get_applicant_analysis(applicant_id)
            if existing_analysis:
                print("✅ 기존 분석 결과 발견")
                print(f"   분석 타입: {existing_analysis.get('analysis_type', 'unknown')}")
                print(f"   생성 시간: {existing_analysis.get('created_at', 'unknown')}")
            else:
                print("ℹ️ 기존 분석 결과 없음")
                
        except Exception as e:
            print(f"❌ 기존 분석 결과 확인 실패: {str(e)}")
        
        # 8. AI 분석 실행 테스트 (선택적)
        print("\n8️⃣ AI 분석 실행 테스트...")
        
        run_analysis = input("실제 AI 분석을 실행하시겠습니까? (y/N): ").strip().lower()
        
        if run_analysis == 'y':
            try:
                print("   🔄 AI 분석 실행 중... (시간이 걸릴 수 있습니다)")
                
                # OpenAI API 키가 있는 경우에만 실행
                if os.getenv("OPENAI_API_KEY"):
                    result = await analysis_service.analyze_resume(analysis_request)
                    
                    if result.success:
                        print("✅ AI 분석 성공!")
                        print(f"   분석 ID: {result.analysis_id}")
                        print(f"   처리 시간: {result.processing_time:.2f}초")
                        print(f"   종합 점수: {result.data['analysis_result']['overall_score']}/100")
                    else:
                        print(f"❌ AI 분석 실패: {result.message}")
                else:
                    print("⚠️ OpenAI API 키가 설정되지 않아 분석을 건너뜁니다.")
                    
            except Exception as e:
                print(f"❌ AI 분석 실행 실패: {str(e)}")
        else:
            print("   ℹ️ AI 분석 실행을 건너뜁니다.")
        
        print(f"\n✅ AI 이력서 분석 기능 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # MongoDB 연결 종료
        client.close()

if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(test_ai_analysis())
