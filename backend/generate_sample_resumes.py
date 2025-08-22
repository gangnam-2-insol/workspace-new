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

def generate_sample_resume_info(applicant_name, position):
    """가상의 이력서 정보 생성"""
    
    # 직무별 기술 스택 정의
    tech_stacks = {
        '프론트엔드': ['React', 'JavaScript', 'TypeScript', 'CSS', 'HTML', 'Vue.js', 'Next.js', 'Tailwind CSS'],
        '백엔드': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Node.js', 'Express', 'MongoDB', 'AWS'],
        '풀스택': ['Java', 'Spring', 'React', 'MySQL', 'Docker', 'Kubernetes', 'JavaScript', 'Python'],
        '데이터': ['Python', 'Pandas', 'SQL', 'Tableau', 'R', 'Machine Learning', 'TensorFlow', 'Scikit-learn'],
        'DevOps': ['AWS', 'Kubernetes', 'Docker', 'Jenkins', 'Terraform', 'Linux', 'Git', 'CI/CD'],
        '그래픽': ['Photoshop', 'Illustrator', 'Figma', 'Sketch', 'InDesign', 'After Effects', 'Premiere Pro'],
        '개발자': ['Python', 'JavaScript', 'SQL', 'Git', 'Docker', 'AWS', 'Linux', 'Agile'],
        '디자이너': ['Photoshop', 'Illustrator', 'Figma', 'Sketch', 'InDesign', 'Adobe XD', 'UI/UX', '프로토타이핑'],
        '포토그래퍼': ['Lightroom', 'Photoshop', '촬영', '편집', '컬러그레이딩', '포토샵', '카메라', '렌즈'],
        '기타': ['Python', 'JavaScript', 'SQL', 'Git', 'Docker', 'AWS', 'Linux', 'Agile']
    }
    
    # 직무별 경력 및 학력 정보
    career_info = {
        '프론트엔드': {
            'companies': ['테크스타트업', '웹에이전시', 'IT서비스회사'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보통신공학과']
        },
        '백엔드': {
            'companies': ['스타트업', '대기업', 'IT컨설팅'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보보안학과']
        },
        '풀스택': {
            'companies': ['IT서비스회사', '스타트업', '웹개발회사'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보통신공학과']
        },
        '데이터': {
            'companies': ['데이터분석회사', 'IT서비스회사', '연구소'],
            'education': ['통계학과', '데이터사이언스학과', '컴퓨터공학과']
        },
        'DevOps': {
            'companies': ['클라우드서비스회사', 'IT인프라회사', '대기업'],
            'education': ['컴퓨터공학과', '정보통신공학과', '전자공학과']
        },
        '그래픽': {
            'companies': ['디자인회사', '광고회사', '출판사'],
            'education': ['시각디자인학과', '산업디자인학과', '미술학과']
        },
        '개발자': {
            'companies': ['IT서비스회사', '스타트업', '소프트웨어회사'],
            'education': ['컴퓨터공학과', '소프트웨어공학과', '정보통신공학과']
        },
        '디자이너': {
            'companies': ['디자인회사', '광고회사', '브랜딩회사'],
            'education': ['시각디자인학과', '산업디자인학과', '미술학과']
        },
        '포토그래퍼': {
            'companies': ['사진스튜디오', '광고회사', '미디어회사'],
            'education': ['사진학과', '미디어아트학과', '시각디자인학과']
        }
    }
    
    # 기본 정보 생성
    if position in tech_stacks:
        skills = ', '.join(random.sample(tech_stacks[position], random.randint(4, 6)))
        career = career_info[position]
    else:
        # '기타' 직무인 경우 기본 기술 스택 사용
        skills = ', '.join(random.sample(tech_stacks['기타'], random.randint(4, 6)))
        career = career_info['기타']
    
    # 경력 기간 (1-8년)
    experience_years = random.randint(1, 8)
    
    # 회사명 생성
    company = random.choice(career['companies'])
    
    # 학력 생성
    education = random.choice(career['education'])
    
    # 이력서 요약 생성
    summary = f"""**{applicant_name} - {position}**

**연락처 정보:**
- 이메일: {applicant_name.lower()}@example.com
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
    
    return {
        'name': applicant_name,
        'email': f"{applicant_name.lower()}@example.com",
        'phone': f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'position': position,
        'skills': skills,
        'department': position.split()[0] if position else '개발',
        'growthBackground': summary,
        'motivation': f"{applicant_name}의 이력서를 통해 지원자의 역량과 경험을 확인했습니다.",
        'careerHistory': summary,
        'analysisScore': random.randint(65, 95),
        'analysisResult': summary
    }

def update_applicant_with_sample_resume(db, applicant):
    """지원자에게 가상 이력서 정보 업데이트"""
    try:
        applicant_id = applicant.get('_id')
        applicant_name = applicant.get('name', '이름 없음')
        position = applicant.get('position', '개발자')
        
        if not applicant_id:
            print(f"⚠️ 지원자 ID가 없음: {applicant_name}")
            return False
        
        # 가상 이력서 정보 생성
        resume_info = generate_sample_resume_info(applicant_name, position)
        
        # 업데이트할 데이터 준비
        update_data = {
            **resume_info,
            'updated_at': datetime.utcnow()
        }
        
        # MongoDB 업데이트
        result = db.applicants.update_one(
            {'_id': applicant_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ {applicant_name} 가상 이력서 정보 생성 완료")
            return True
        else:
            print(f"⚠️ {applicant_name} 업데이트할 내용 없음")
            return False
            
    except Exception as e:
        print(f"❌ 지원자 업데이트 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 모든 지원자에게 가상 이력서 정보 생성 시작")
    
    # MongoDB 연결
    db = connect_mongodb()
    if db is None:
        return
    
    try:
        # 모든 지원자 조회
        applicants = list(db.applicants.find({}))
        print(f"📊 총 지원자 수: {len(applicants)}")
        
        updated_count = 0
        
        for applicant in applicants:
            applicant_name = applicant.get('name', '이름 없음')
            print(f"\n--- {applicant_name} 처리 중 ---")
            
            # 가상 이력서 정보로 업데이트
            if update_applicant_with_sample_resume(db, applicant):
                updated_count += 1
        
        print(f"\n🎉 업데이트 완료! 총 {updated_count}명의 지원자 정보가 업데이트되었습니다.")
        
        # 업데이트된 지원자 정보 확인
        print("\n📋 업데이트된 지원자 목록:")
        updated_applicants = list(db.applicants.find({'updated_at': {'$exists': True}}, {'name': 1, 'position': 1, 'skills': 1, 'analysisScore': 1}))
        for app in updated_applicants[:10]:  # 처음 10명만 표시
            print(f"- {app.get('name', '이름 없음')}: {app.get('position', '직무 없음')} | {app.get('skills', '기술 없음')[:30]}... | 점수: {app.get('analysisScore', 0)}점")
        
    except Exception as e:
        print(f"❌ 메인 프로세스 오류: {e}")
    
    finally:
        if db is not None:
            db.client.close()
            print("🔌 MongoDB 연결 종료")

if __name__ == "__main__":
    main()
