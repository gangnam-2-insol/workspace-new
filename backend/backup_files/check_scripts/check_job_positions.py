#!/usr/bin/env python3
"""
채용공고 직무 정보 확인 스크립트
"""

import pymongo


def check_job_positions():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hireme']

    print("🔍 채용공고 직무 정보 확인")
    print("=" * 60)

    jobs = list(db.job_postings.find({}, {'title': 1, 'position': 1}))

    print("📋 채용공고별 직무 정보:")
    for i, job in enumerate(jobs, 1):
        title = job.get('title', 'Unknown')
        position = job.get('position', 'None')
        print(f"{i}. {title}")
        print(f"   → position 필드: {position}")

        # 제목에서 직무 추출
        title_position = None
        if '프론트엔드 개발자' in title:
            title_position = '프론트엔드 개발자'
        elif '백엔드 개발자' in title:
            title_position = '백엔드 개발자'
        elif 'UI/UX 디자이너' in title:
            title_position = 'UI/UX 디자이너'
        elif '프로젝트 매니저' in title:
            title_position = '프로젝트 매니저'
        elif '디지털 마케팅 전문가' in title:
            title_position = '디지털 마케팅 전문가'

        print(f"   → 제목에서 추출: {title_position}")
        print(f"   → 일치 여부: {'✅' if position == title_position else '❌'}")
        print()

    # 직무별 통계
    position_counts = {}
    for job in jobs:
        position = job.get('position', 'Unknown')
        position_counts[position] = position_counts.get(position, 0) + 1

    print("📊 직무별 채용공고 개수:")
    for position, count in sorted(position_counts.items()):
        print(f"   - {position}: {count}개")

    client.close()

if __name__ == "__main__":
    check_job_positions()
