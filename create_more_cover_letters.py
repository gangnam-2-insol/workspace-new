import asyncio
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from faker import Faker

fake = Faker(['ko_KR'])

async def create_more_cover_letters():
    """더 많은 지원자에게 자소서 생성"""
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        print("📄 추가 자소서 데이터 생성 시작...")

        # 자소서가 없는 지원자들 찾기
        applicants_without_cover = await db.applicants.find({
            "$or": [
                {"cover_letter_id": {"$exists": False}},
                {"cover_letter_id": None}
            ]
        }).to_list(length=None)

        print(f"자소서가 없는 지원자: {len(applicants_without_cover)}명")

        # 추가로 100명의 지원자에게 자소서 생성
        target_count = min(100, len(applicants_without_cover))
        print(f"추가로 {target_count}명의 지원자에게 자소서를 생성합니다...")

        cover_letters = []
        for i, applicant in enumerate(applicants_without_cover[:target_count]):
            cover_letter = {
                "_id": ObjectId(),
                "applicant_id": applicant["_id"],
                "title": f"{applicant['name']}의 자기소개서",
                "content": generate_diverse_cover_letter_content(applicant),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            cover_letters.append(cover_letter)

            # 지원자 정보에 자소서 ID 추가
            await db.applicants.update_one(
                {"_id": applicant["_id"]},
                {"$set": {"cover_letter_id": str(cover_letter["_id"])}}
            )

            if (i + 1) % 20 == 0:
                print(f"  {i+1}/{target_count} 자소서 생성 완료")

        # 자소서 DB에 삽입
        if cover_letters:
            await db.cover_letters.insert_many(cover_letters)
            print(f"✅ {len(cover_letters)}개의 추가 자소서 생성 완료")

        # 최종 현황 확인
        total_applicants = await db.applicants.count_documents({})
        applicants_with_cover = await db.applicants.count_documents({"cover_letter_id": {"$exists": True, "$ne": None}})
        total_cover_letters = await db.cover_letters.count_documents({})

        print(f"\n📊 최종 자소서 현황:")
        print(f"   전체 지원자 수: {total_applicants}명")
        print(f"   자소서가 있는 지원자 수: {applicants_with_cover}명")
        print(f"   자소서 컬렉션 문서 수: {total_cover_letters}개")
        print(f"   자소서 보유율: {applicants_with_cover/total_applicants*100:.1f}%")

        client.close()

    except Exception as e:
        print(f"오류: {e}")

def generate_diverse_cover_letter_content(applicant):
    """다양한 자소서 내용 생성"""
    name = applicant['name']
    position = applicant.get('position', '개발자')
    experience = applicant.get('experience', '신입')

    # 다양한 자소서 템플릿
    templates = [
        # 템플릿 1: 경험 중심
        f"""
안녕하세요, {name}입니다.

{position} 직무에 지원하게 되어 기쁩니다. {experience} 경력을 바탕으로 {position} 분야에서 더욱 성장하고자 합니다.

## 주요 경험
{fake.text(max_nb_chars=250)}

## 기술 역량
{fake.text(max_nb_chars=200)}

## 지원 동기
{fake.text(max_nb_chars=200)}

귀사의 {position} 직무에서 제 경험과 역량을 발휘하여 회사 발전에 기여하고 싶습니다.

감사합니다.
{name} 드림
""",

        # 템플릿 2: 프로젝트 중심
        f"""
안녕하세요, {name}입니다.

{position} 직무에 지원하게 되어 기쁩니다. 다양한 프로젝트 경험을 통해 {position} 분야에서의 전문성을 쌓아왔습니다.

## 주요 프로젝트
{fake.text(max_nb_chars=300)}

## 기술 스택
{fake.text(max_nb_chars=150)}

## 성장 계획
{fake.text(max_nb_chars=200)}

귀사의 {position} 직무에서 제 프로젝트 경험을 활용하여 가치를 창출하고 싶습니다.

감사합니다.
{name} 드림
""",

        # 템플릿 3: 열정 중심
        f"""
안녕하세요, {name}입니다.

{position} 직무에 지원하게 되어 기쁩니다. {position} 분야에 대한 깊은 열정과 지속적인 학습을 통해 전문성을 키워왔습니다.

## 지원 동기
{fake.text(max_nb_chars=250)}

## 학습 과정
{fake.text(max_nb_chars=200)}

## 미래 계획
{fake.text(max_nb_chars=200)}

귀사의 {position} 직무에서 제 열정과 학습 의지를 바탕으로 혁신적인 솔루션을 제공하고 싶습니다.

감사합니다.
{name} 드림
"""
    ]

    return random.choice(templates).strip()

if __name__ == "__main__":
    asyncio.run(create_more_cover_letters())
