import asyncio
import os
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
API_BASE_URL = "http://localhost:8000"

async def test_cover_letter_plagiarism():
    """자소서 표절체크 테스트"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.hireme

        print("✅ MongoDB 연결 성공")

        # 자소서가 있는 지원자 조회
        applicants_with_cover_letters = await db.applicants.find({
            "cover_letter_id": {"$exists": True, "$ne": None}
        }).to_list(10)

        print(f"📋 자소서가 있는 지원자 수: {len(applicants_with_cover_letters)}")

        if not applicants_with_cover_letters:
            print("❌ 자소서가 있는 지원자가 없습니다.")
            print("💡 먼저 자소서 샘플 데이터를 생성해주세요:")
            print("   python create_cover_letter_samples.py")
            return

        # 첫 번째 지원자로 테스트
        test_applicant = applicants_with_cover_letters[0]
        applicant_id = str(test_applicant["_id"])
        applicant_name = test_applicant.get("name", "Unknown")

        print(f"\n🧪 테스트 대상: {applicant_name} (ID: {applicant_id})")

        # 자소서 정보 확인
        cover_letter_id = test_applicant.get("cover_letter_id")
        if cover_letter_id:
            cover_letter = await db.cover_letters.find_one({"_id": ObjectId(cover_letter_id)})
            if cover_letter:
                content_length = len(cover_letter.get("content", ""))
                extracted_length = len(cover_letter.get("extracted_text", ""))
                print(f"📄 자소서 내용 길이: {content_length}자")
                print(f"📄 추출된 텍스트 길이: {extracted_length}자")

        # API 테스트
        print(f"\n🔍 자소서 표절체크 API 테스트 시작...")

        # API 호출
        url = f"{API_BASE_URL}/api/coverletter/similarity-check/{applicant_id}"

        try:
            response = requests.post(url, timeout=30)
            print(f"📡 API 응답 상태: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("✅ API 호출 성공!")

                # 결과 분석
                plagiarism_result = result.get("plagiarism_result", {})
                status = plagiarism_result.get("status", "unknown")
                message = plagiarism_result.get("message", "메시지 없음")

                print(f"\n📊 표절체크 결과:")
                print(f"  - 상태: {status}")
                print(f"  - 메시지: {message}")

                # 상세 정보 출력
                if "debug_info" in plagiarism_result:
                    debug_info = plagiarism_result["debug_info"]
                    print(f"  - 디버그 정보:")
                    for key, value in debug_info.items():
                        print(f"    * {key}: {value}")

                # 유사 문서 정보
                if "similar_documents" in plagiarism_result:
                    similar_docs = plagiarism_result["similar_documents"]
                    print(f"  - 유사 문서 수: {len(similar_docs)}")

                    for i, doc in enumerate(similar_docs[:3]):  # 상위 3개만 출력
                        print(f"    {i+1}. 유사도: {doc.get('similarity_score', 0):.3f}")

            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 오류: {str(e)}")
            print("💡 백엔드 서버가 실행 중인지 확인해주세요.")

        client.close()

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

async def list_cover_letters():
    """자소서 목록 조회"""
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.hireme

        # 자소서 목록 조회
        cover_letters = await db.cover_letters.find({}).to_list(20)

        print(f"📋 자소서 목록 (총 {len(cover_letters)}개):")
        for i, cover_letter in enumerate(cover_letters):
            applicant_id = cover_letter.get("applicant_id", "Unknown")
            content_length = len(cover_letter.get("content", ""))
            extracted_length = len(cover_letter.get("extracted_text", ""))

            print(f"  {i+1}. ID: {cover_letter['_id']}")
            print(f"     지원자 ID: {applicant_id}")
            print(f"     내용 길이: {content_length}자")
            print(f"     추출 텍스트 길이: {extracted_length}자")
            print(f"     상태: {cover_letter.get('status', 'Unknown')}")
            print()

        client.close()

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

async def check_applicants_with_cover_letters():
    """자소서가 있는 지원자 목록 조회"""
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.hireme

        # 자소서가 있는 지원자 조회
        applicants = await db.applicants.find({
            "cover_letter_id": {"$exists": True, "$ne": None}
        }).to_list(20)

        print(f"📋 자소서가 있는 지원자 목록 (총 {len(applicants)}명):")
        for i, applicant in enumerate(applicants):
            name = applicant.get("name", "Unknown")
            position = applicant.get("position", "Unknown")
            cover_letter_id = applicant.get("cover_letter_id", "Unknown")

            print(f"  {i+1}. {name} - {position}")
            print(f"     지원자 ID: {applicant['_id']}")
            print(f"     자소서 ID: {cover_letter_id}")
            print()

        client.close()

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            asyncio.run(list_cover_letters())
        elif command == "applicants":
            asyncio.run(check_applicants_with_cover_letters())
        elif command == "test":
            asyncio.run(test_cover_letter_plagiarism())
        else:
            print("사용법:")
            print("  python test_cover_letter_plagiarism_simple.py list      # 자소서 목록 조회")
            print("  python test_cover_letter_plagiarism_simple.py applicants # 자소서가 있는 지원자 목록")
            print("  python test_cover_letter_plagiarism_simple.py test      # 표절체크 테스트")
    else:
        print("자소서 표절체크 테스트 도구")
        print("\n사용법:")
        print("  python test_cover_letter_plagiarism_simple.py list      # 자소서 목록 조회")
        print("  python test_cover_letter_plagiarism_simple.py applicants # 자소서가 있는 지원자 목록")
        print("  python test_cover_letter_plagiarism_simple.py test      # 표절체크 테스트")

        # 기본적으로 테스트 실행
        print("\n🧪 기본 테스트 실행...")
        asyncio.run(test_cover_letter_plagiarism())
