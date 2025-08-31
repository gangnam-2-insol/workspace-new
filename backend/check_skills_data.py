#!/usr/bin/env python3
"""
지원자 스킬 데이터 확인 스크립트
"""

import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def check_applicant_skills():
    """지원자 스킬 데이터 확인"""
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL', 'mongodb://localhost:27017'))
    db = client.hireme

    try:
        # 지원자 데이터 조회
        applicants = await db.applicants.find({}).limit(5).to_list(5)

        print('=== 지원자 스킬 데이터 확인 ===')
        for i, applicant in enumerate(applicants):
            print(f'\n지원자 {i+1}: {applicant.get("name", "이름없음")}')
            print(f'  스킬 타입: {type(applicant.get("skills"))}')
            print(f'  스킬 값: {repr(applicant.get("skills"))}')

            # 스킬이 문자열인 경우 파싱 테스트
            skills = applicant.get('skills')
            if isinstance(skills, str):
                print(f'  문자열 길이: {len(skills)}')
                if skills.startswith('[') and skills.endswith(']'):
                    print('  → JSON 배열 형태로 보임')
                    # JSON 파싱 시도
                    try:
                        import json
                        parsed = json.loads(skills)
                        print(f'  → JSON 파싱 성공: {parsed}')
                    except Exception as e:
                        print(f'  → JSON 파싱 실패: {e}')
                elif ',' in skills:
                    print('  → 쉼표 구분 문자열로 보임')
                    parts = [s.strip() for s in skills.split(',')]
                    print(f'  → 분할 결과: {parts}')
                else:
                    print('  → 단일 문자열로 보임')
            elif isinstance(skills, list):
                print('  → 이미 배열 형태')
                print(f'  → 배열 내용: {skills}')
            else:
                print('  → 스킬 데이터 없음 또는 다른 타입')

        # 전체 지원자 수 확인
        total_count = await db.applicants.count_documents({})
        print(f'\n=== 전체 지원자 수: {total_count}명 ===')

    except Exception as e:
        print(f'오류 발생: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_applicant_skills())
