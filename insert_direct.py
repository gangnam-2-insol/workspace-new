import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def insert_sample_data_direct():
    """MongoDB에 직접 샘플 데이터 삽입"""

    # JSON 파일에서 데이터 로드
    try:
        with open('backend/sample_applicants.json', 'r', encoding='utf-8') as f:
            applicants = json.load(f)
        print(f"JSON 파일에서 {len(applicants)}개 지원자 데이터를 로드했습니다.")
    except FileNotFoundError:
        print("sample_applicants.json 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"JSON 파일 로드 오류: {e}")
        return

    # MongoDB 연결
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        print("=== MongoDB 직접 삽입 시작 ===")

        success_count = 0
        fail_count = 0

        for i, applicant in enumerate(applicants):
            try:
                # created_at 필드 추가
                applicant['created_at'] = datetime.now()

                # MongoDB에 삽입
                result = await db.applicants.insert_one(applicant)

                success_count += 1
                print(f"  ✅ {i+1}: {applicant['name']} - 성공 (ID: {result.inserted_id})")

            except Exception as e:
                fail_count += 1
                print(f"  ❌ {i+1}: {applicant['name']} - 실패 ({str(e)})")

        print(f"\n=== 완료 ===")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"총 처리: {len(applicants)}개")

        # 최종 확인
        total_count = await db.applicants.count_documents({})
        print(f"DB에 실제 저장된 지원자 수: {total_count}개")

        client.close()

    except Exception as e:
        print(f"MongoDB 연결 오류: {e}")

if __name__ == "__main__":
    asyncio.run(insert_sample_data_direct())
