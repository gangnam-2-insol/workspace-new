import asyncio
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from faker import Faker

fake = Faker(['ko_KR'])

async def create_cover_letters():
    """자소서 데이터 생성"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        print("📄 자소서 데이터 생성 시작...")

        # 지원자 목록 가져오기
        applicants = await db.applicants.find({}).to_list(length=None)
        print(f"총 {len(applicants)}명의 지원자 발견")

        # 자소서가 없는 지원자들 찾기
        applicants_without_cover = []
        for applicant in applicants:
            if not applicant.get('cover_letter_id'):
                applicants_without_cover.append(applicant)

        print(f"자소서가 없는 지원자: {len(applicants_without_cover)}명")

        # 자소서 생성
        cover_letters = []
        for i, applicant in enumerate(applicants_without_cover[:50]):  # 처음 50명만
            cover_letter = {
                "_id": ObjectId(),
                "applicant_id": applicant["_id"],
                "title": f"{applicant['name']}의 자기소개서",
                "content": generate_cover_letter_content(applicant),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            cover_letters.append(cover_letter)

            # 지원자 정보에 자소서 ID 추가
            await db.applicants.update_one(
                {"_id": applicant["_id"]},
                {"$set": {"cover_letter_id": str(cover_letter["_id"])}}
            )

            if (i + 1) % 10 == 0:
                print(f"  {i+1}/{len(applicants_without_cover[:50])} 자소서 생성 완료")

        # 자소서 DB에 삽입
        if cover_letters:
            await db.cover_letters.insert_many(cover_letters)
            print(f"✅ {len(cover_letters)}개의 자소서 생성 완료")
        else:
            print("✅ 모든 지원자에게 이미 자소서가 있습니다")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

def generate_cover_letter_content(applicant):
    """자소서 내용 생성"""
    name = applicant['name']
    position = applicant.get('position', '개발자')
    experience = applicant.get('experience', '신입')

    content = f"""
안녕하세요, {name}입니다.

{position} 직무에 지원하게 되어 기쁩니다. 저는 {experience} 경력을 바탕으로 {position} 분야에서 성장하고자 합니다.

## 지원 동기
{position} 직무에 지원하게 된 이유는 {fake.text(max_nb_chars=200)} 때문입니다.

## 경력 및 프로젝트
{fake.text(max_nb_chars=300)}

## 기술 스택
{fake.text(max_nb_chars=200)}

## 성장 계획
앞으로 {fake.text(max_nb_chars=200)} 계획을 가지고 있습니다.

귀사의 {position} 직무에서 제 역량을 발휘하여 회사 발전에 기여하고 싶습니다.

감사합니다.
{name} 드림
"""

    return content.strip()

if __name__ == "__main__":
    asyncio.run(create_cover_letters())
