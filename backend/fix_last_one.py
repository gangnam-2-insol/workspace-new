from pymongo import MongoClient
from datetime import datetime
import random

def fix_last_applicant():
    client = MongoClient('mongodb://localhost:27017')
    db = client.hireme
    
    # 마지막 지원자 찾기
    applicant = db.applicants.find_one({'name': '장미래', 'updated_at': {'$exists': False}})
    
    if applicant:
        print("--- 장미래 처리 중 ---")
        
        # 이력서 정보 생성
        summary = """**장미래 - 디자이너**

**연락처 정보:**
- 이메일: jangmirae@example.com
- 전화번호: 010-1234-5678
- 주소: 서울시 강남구 테헤란로 123

**학력:**
- 시각디자인학과, 서울대학교 (졸업: 2020년)

**경력:**
- UI/UX 디자이너, 브랜딩회사 (2020년 ~ 현재)
- 3개의 프로젝트 완료
- 팀 리드 경험 1년

**자격증:**
- 정보처리기사
- 디자인 관련 자격증

**업무 스킬:**
Photoshop, Illustrator, Figma, Sketch, InDesign, Adobe XD, UI/UX, 프로토타이핑

**수상:**
- 브랜딩회사 우수사원상 (2023년)"""
        
        # 업데이트
        result = db.applicants.update_one(
            {'_id': applicant['_id']},
            {'$set': {
                'name': '장미래',
                'position': '디자이너',
                'skills': 'Photoshop, Illustrator, Figma, Sketch, InDesign, Adobe XD, UI/UX, 프로토타이핑',
                'department': '디자인',
                'growthBackground': summary,
                'motivation': '장미래의 이력서를 통해 지원자의 역량과 경험을 확인했습니다.',
                'careerHistory': summary,
                'analysisScore': 78,
                'analysisResult': summary,
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            print("✅ 장미래 이력서 정보 수정 완료")
        else:
            print("⚠️ 장미래 업데이트할 내용 없음")
    
    client.close()

if __name__ == "__main__":
    fix_last_applicant()
