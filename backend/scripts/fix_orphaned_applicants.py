#!/usr/bin/env python3
"""
job_posting_id가 없는 지원자들을 활성 채용공고에 재할당하는 스크립트
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.utils.job_posting_assignment import reassign_orphaned_applicants


async def main():
    """메인 함수"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.hireme

        print("🚀 고아 지원자 재할당 스크립트 시작...")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 고아 지원자 재할당 실행
        print("🔍 고아 지원자 재할당 함수 호출 중...")
        reassigned_count = await reassign_orphaned_applicants(db)

        print("=" * 60)
        print(f"✅ 재할당 완료: {reassigned_count}명")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ 스크립트 실행 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    asyncio.run(main())
