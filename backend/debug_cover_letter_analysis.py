#!/usr/bin/env python3
"""
자소서 분석 디버깅 스크립트
"""

import asyncio
import os
import sys

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.core.services.cover_letter_analysis.analyzer import CoverLetterAnalyzer


async def debug_cover_letter_analysis():
    """자소서 분석 디버깅"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['hireme']

        print("=== 자소서 분석 디버깅 ===")

        # 이민호 지원자 정보 확인
        applicant_id = "68b3ce182f0cf5df5e13004e"
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})

        if not applicant:
            print(f"지원자를 찾을 수 없습니다: {applicant_id}")
            return

        print(f"지원자: {applicant['name']} ({applicant['email']})")
        print(f"자소서 ID: {applicant.get('cover_letter_id')}")

        # 자소서 정보 확인
        if applicant.get('cover_letter_id'):
            cover_letter = await db.cover_letters.find_one({"_id": applicant['cover_letter_id']})
            if cover_letter:
                print(f"자소서 파일명: {cover_letter.get('filename')}")
                print(f"자소서 내용 길이: {len(cover_letter.get('content', ''))}")
                print(f"자소서 내용 미리보기: {cover_letter.get('content', '')[:200]}...")

                # 자소서 분석기 초기화
                LLM_CONFIG = {
                    "provider": "openai",
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model_name": "gpt-4o-mini",
                    "max_tokens": 4000,
                    "temperature": 0.3
                }

                print(f"\n=== LLM 설정 확인 ===")
                print(f"API Key 존재: {'Yes' if LLM_CONFIG['api_key'] else 'No'}")
                print(f"Provider: {LLM_CONFIG['provider']}")
                print(f"Model: {LLM_CONFIG['model_name']}")

                if not LLM_CONFIG['api_key']:
                    print("❌ OpenAI API Key가 설정되지 않았습니다!")
                    return

                # 자소서 분석 실행
                print(f"\n=== 자소서 분석 실행 ===")
                analyzer = CoverLetterAnalyzer(LLM_CONFIG)

                try:
                    analysis_result = await analyzer.analyze_cover_letter_text(
                        text_content=cover_letter.get('content', ''),
                        filename=cover_letter.get('filename', 'cover_letter.txt'),
                        job_description="",
                        analysis_type="comprehensive"
                    )

                    print(f"분석 결과 상태: {analysis_result.status}")
                    if analysis_result.status == "success":
                        print("✅ 자소서 분석 성공!")
                        print(f"처리 시간: {analysis_result.processing_time:.2f}초")
                    else:
                        print("❌ 자소서 분석 실패!")
                        print(f"오류: {analysis_result.error_message}")

                except Exception as e:
                    print(f"❌ 자소서 분석 중 예외 발생: {str(e)}")
                    import traceback
                    traceback.print_exc()

            else:
                print("자소서를 찾을 수 없습니다.")
        else:
            print("자소서 ID가 없습니다.")

        client.close()

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_cover_letter_analysis())
