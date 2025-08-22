#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from datetime import datetime
from pymongo import MongoClient

def connect_mongodb():
    """MongoDB 연결"""
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client.hireme
        print("✅ MongoDB 연결 성공")
        return db
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

def fix_remaining_applicants():
    """남은 지원자들의 이력서 정보 수정"""
    
    # 남은 지원자들의 직무 매핑
    position_mapping = {
        '김개발': '프론트엔드 개발자',
        '박백엔드': '백엔드 개발자', 
        '이풀스택': '풀스택 개발자',
        '최데이터': '데이터 분석가',
        '정디브옵스': 'DevOps 엔지니어',
        '장미래': '디자이너'
    }
    
    # 직무별 기술 스택
    tech_stacks = {
        '프론트엔드 개발자': ['React', 'JavaScript', 'TypeScript', 'CSS', 'HTML', 'Vue.js', 'Next.js'],
        '백엔드 개발자': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Node.js', 'Express', 'MongoDB'],
        '풀스택 개발자': ['Java', 'Spring', 'React', 'MySQL', 'Docker', 'Kubernetes', 'JavaScript'],
        '데이터 분석가': ['Python', 'Pandas', 'SQL', 'Tableau', 'R', 'Machine Learning', 'TensorFlow'],
        'DevOps 엔지니어': ['AWS', 'Kubernetes', 'Docker', 'Jenkins', 'Terraform', 'Linux', 'Git'],
        '디자이너': ['Photoshop', 'Illustrator', 'Figma', 'Sketch', 'InDesign', 'Adobe XD', 'UI/UX']
    }
    
    # 직무별 회사 및 학력
    career_info = {
        '프론트엔드 개발자': {
            'companies': ['테크스타트업', '웹에이전시', 'IT서비스회사'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보통신공학과']
        },
        '백엔드 개발자': {
            'companies': ['스타트업', '대기업', 'IT컨설팅'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보보안학과']
        },
        '풀스택 개발자': {
            'companies': ['IT서비스회사', '스타트업', '웹개발회사'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보통신공학과']
        },
        '데이터 분석가': {
            'companies': ['데이터분석회사', 'IT서비스회사', '연구소'],
            'education': ['통계학과', '데이터사이언스학과', '컴퓨터공학과']
        },
        'DevOps 엔지니어': {
            'companies': ['클라우드서비스회사', 'IT인프라회사', '대기업'],
            'education': ['컴퓨터공학과', '정보통신공학과', '전자공학과']
        },
        '디자이너': {
            'companies': ['디자인회사', '광고회사', '브랜딩회사'],
            'education': ['시각디자인학과', '산업디자인학과', '미술학과']
        }
    }
    
    db = connect_mongodb()
    if db is None:
        return
    
    try:
        updated_count = 0
        
        for name, position in position_mapping.items():
            print(f"\n--- {name} 처리 중 ---")
            
            # 지원자 찾기
            applicant = db.applicants.find_one({'name': name})
            if not applicant:
                print(f"⚠️ {name} 지원자를 찾을 수 없음")
                continue
            
            # 기술 스택 생성
            skills = ', '.join(random.sample(tech_stacks[position], random.randint(4, 6)))
            
            # 경력 정보
            career = career_info[position]
            company = random.choice(career['companies'])
            education = random.choice(career['education'])
            experience_years = random.randint(1, 8)
            
            # 이력서 요약 생성
            summary = f"""**{name} - {position}**

**연락처 정보:**
- 이메일: {name.lower()}@example.com
- 전화번호: 010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}
- 주소: 서울시 강남구 테헤란로 123

**학력:**
- {education}, 서울대학교 (졸업: {2024 - random.randint(0, 10)}년)

**경력:**
- {position}, {company} ({2024 - experience_years}년 ~ 현재)
- {random.randint(1, 3)}개의 프로젝트 완료
- 팀 리드 경험 {random.randint(0, 3)}년

**자격증:**
- 정보처리기사
- {position} 관련 자격증

**업무 스킬:**
{skills}

**수상:**
- {company} 우수사원상 ({2024 - random.randint(1, 3)}년)"""
            
            # 업데이트 데이터
            update_data = {
                'name': name,
                'position': position,
                'skills': skills,
                'department': position.split()[0] if position else '개발',
                'growthBackground': summary,
                'motivation': f"{name}의 이력서를 통해 지원자의 역량과 경험을 확인했습니다.",
                'careerHistory': summary,
                'analysisScore': random.randint(65, 95),
                'analysisResult': summary,
                'updated_at': datetime.utcnow()
            }
            
            # MongoDB 업데이트
            result = db.applicants.update_one(
                {'_id': applicant['_id']},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ {name} 이력서 정보 수정 완료")
                updated_count += 1
            else:
                print(f"⚠️ {name} 업데이트할 내용 없음")
        
        print(f"\n🎉 수정 완료! 총 {updated_count}명의 지원자 정보가 수정되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    finally:
        if db is not None:
            db.client.close()
            print("🔌 MongoDB 연결 종료")

if __name__ == "__main__":
    fix_remaining_applicants()
