#!/usr/bin/env python3
"""
경력 데이터에서 라틴어 확인 스크립트
"""
from pymongo import MongoClient
import re


def check_career_data():
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017/hireme')
        db = client.hireme

        # 지원자 수 확인
        count = db.applicants.count_documents({})
        print(f"📊 현재 데이터베이스 지원자 수: {count}")

        if count > 0:
            # 모든 지원자의 경력 데이터 확인
            applicants = list(db.applicants.find({}))
            print("\n📋 경력 데이터 확인:")
            
            latin_patterns = [
                r'lorem\s+ipsum',
                r'dolor\s+sit\s+amet',
                r'consectetur\s+adipiscing',
                r'sed\s+do\s+eiusmod',
                r'tempor\s+incididunt',
                r'ut\s+labore\s+et\s+dolore',
                r'magna\s+aliqua',
                r'quis\s+nostrud\s+exercitation',
                r'ullamco\s+laboris',
                r'nisi\s+ut\s+aliquip'
            ]
            
            latin_found = []
            
            for i, app in enumerate(applicants, 1):
                name = app.get('name', 'N/A')
                career_history = app.get('careerHistory', '')
                experience = app.get('experience', '')
                
                # 라틴어 패턴 검사
                has_latin = False
                for pattern in latin_patterns:
                    if re.search(pattern, career_history.lower()) or re.search(pattern, experience.lower()):
                        has_latin = True
                        break
                
                if has_latin:
                    latin_found.append({
                        'name': name,
                        'careerHistory': career_history,
                        'experience': experience
                    })
                    print(f"🔍 라틴어 발견 - {name}:")
                    print(f"   경력: {career_history}")
                    print(f"   경험: {experience}")
                    print()
                else:
                    print(f"✅ {name}: 라틴어 없음")
            
            print(f"\n📊 결과: 총 {len(latin_found)}명의 지원자에서 라틴어 발견")
            
            if latin_found:
                print("\n🔄 라틴어를 적절한 내용으로 교체하시겠습니까? (y/n)")
                return latin_found
            else:
                print("✅ 모든 지원자의 경력 데이터가 적절합니다.")
                return []

        else:
            print("❌ 데이터베이스에 지원자가 없습니다.")
            return []

        client.close()

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return []


def generate_realistic_career(experience_years, position):
    """실제적인 경력 내용 생성"""
    career_templates = {
        "프론트엔드 개발자": [
            f"{experience_years}년간 React, Vue.js 기반 웹 애플리케이션 개발 경험. 사용자 경험 개선 및 성능 최적화에 중점을 두고 개발했습니다.",
            f"프론트엔드 개발 {experience_years}년 경력으로 TypeScript, Next.js를 활용한 대규모 프로젝트 참여 경험이 있습니다.",
            f"{experience_years}년간 모던 웹 기술 스택을 활용한 반응형 웹사이트 및 SPA 개발 경험을 보유하고 있습니다."
        ],
        "백엔드 개발자": [
            f"{experience_years}년간 Java, Spring Boot 기반 서버 애플리케이션 개발 경험. RESTful API 설계 및 데이터베이스 최적화에 능숙합니다.",
            f"백엔드 개발 {experience_years}년 경력으로 Node.js, Express, MongoDB를 활용한 마이크로서비스 아키텍처 구축 경험이 있습니다.",
            f"{experience_years}년간 Python, Django, PostgreSQL을 활용한 안정적인 서버 시스템 개발 경험을 보유하고 있습니다."
        ],
        "풀스택 개발자": [
            f"{experience_years}년간 프론트엔드와 백엔드 개발 경험을 보유. React, Node.js, MongoDB 스택으로 풀스택 애플리케이션을 개발했습니다.",
            f"풀스택 개발 {experience_years}년 경력으로 Vue.js, Python, FastAPI, PostgreSQL을 활용한 웹 서비스 구축 경험이 있습니다.",
            f"{experience_years}년간 TypeScript, Next.js, Prisma, PostgreSQL을 활용한 현대적인 웹 애플리케이션 개발 경험을 보유하고 있습니다."
        ],
        "데이터 분석가": [
            f"{experience_years}년간 Python, R, SQL을 활용한 데이터 분석 경험. 머신러닝 모델 개발 및 비즈니스 인사이트 도출에 중점을 두고 있습니다.",
            f"데이터 분석 {experience_years}년 경력으로 통계 분석, 시각화, 예측 모델링 경험이 풍부합니다.",
            f"{experience_years}년간 빅데이터 처리 및 분석 경험을 보유. Tableau, Power BI를 활용한 대시보드 구축 경험이 있습니다."
        ],
        "QA 엔지니어": [
            f"{experience_years}년간 웹 애플리케이션 테스트 자동화 경험. Selenium, Cypress를 활용한 효율적인 테스트 프로세스 구축 경험이 있습니다.",
            f"QA 엔지니어 {experience_years}년 경력으로 기능 테스트, 성능 테스트, 보안 테스트 경험이 풍부합니다.",
            f"{experience_years}년간 다양한 테스트 도구와 방법론을 활용한 품질 보증 경험을 보유하고 있습니다."
        ],
        "DevOps 엔지니어": [
            f"{experience_years}년간 CI/CD 파이프라인 구축 및 클라우드 인프라 관리 경험. AWS, Docker, Kubernetes를 활용한 현대적인 개발 환경 구축 경험이 있습니다.",
            f"DevOps 엔지니어 {experience_years}년 경력으로 자동화, 모니터링, 로그 관리 시스템 구축 경험이 풍부합니다.",
            f"{experience_years}년간 클라우드 네이티브 환경에서의 인프라 관리 및 개발 프로세스 최적화 경험을 보유하고 있습니다."
        ]
    }
    
    import random
    
    # 기본 템플릿 (직무별 매칭이 안 되는 경우)
    default_templates = [
        f"{experience_years}년간 해당 분야에서 실무 경험을 쌓아왔습니다.",
        f"관련 업무 {experience_years}년 경력으로 다양한 프로젝트에 참여한 경험이 있습니다.",
        f"{experience_years}년간 전문성을 바탕으로 성과를 창출한 경험이 풍부합니다."
    ]
    
    templates = career_templates.get(position, default_templates)
    return random.choice(templates)


def replace_latin_career_data(latin_found):
    """라틴어 경력 데이터를 실제적인 내용으로 교체"""
    try:
        client = MongoClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        updated_count = 0
        
        for data in latin_found:
            # 해당 지원자 찾기
            applicant = db.applicants.find_one({'name': data['name']})
            if applicant:
                position = applicant.get('position', '개발자')
                experience = applicant.get('experience', '3년')
                
                # 경력 연도 추출
                experience_years = 3  # 기본값
                if '년' in experience:
                    try:
                        experience_years = int(experience.replace('년', ''))
                    except:
                        experience_years = 3
                
                # 새로운 경력 내용 생성
                new_career = generate_realistic_career(experience_years, position)
                
                # 데이터베이스 업데이트
                result = db.applicants.update_one(
                    {'name': data['name']},
                    {'$set': {'careerHistory': new_career}}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ {data['name']} 경력 데이터 업데이트 완료")
                    print(f"   새 내용: {new_career}")
                    print()
        
        print(f"🎉 총 {updated_count}명의 지원자 경력 데이터가 업데이트되었습니다.")
        
        client.close()
        return updated_count
        
    except Exception as e:
        print(f"❌ 업데이트 중 오류 발생: {str(e)}")
        return 0


if __name__ == "__main__":
    latin_found = check_career_data()
    
    if latin_found:
        response = input("라틴어를 적절한 내용으로 교체하시겠습니까? (y/n): ").lower().strip()
        if response == 'y':
            replace_latin_career_data(latin_found)
        else:
            print("교체를 취소했습니다.")


