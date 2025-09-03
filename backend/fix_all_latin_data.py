#!/usr/bin/env python3
"""
모든 라틴어 데이터를 실제적인 한국어 내용으로 교체하는 스크립트
"""
import asyncio
import random
import re
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


async def fix_all_latin_data():
    """모든 라틴어 데이터를 실제적인 내용으로 교체"""
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient('mongodb://localhost:27017/hireme')
        db = client.hireme
        
        print("🔍 모든 라틴어 데이터 검사 및 교체 시작...")
        
        # 라틴어 패턴 (더 포괄적으로)
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
            r'nisi\s+ut\s+aliquip',
            r'duis\s+aute\s+irure',
            r'reprehenderit\s+in\s+voluptate',
            r'velit\s+esse\s+cillum',
            r'eu\s+fugiat\s+nulla',
            r'pariatur',
            r'excepteur\s+sint\s+occaecat',
            r'cupidatat\s+non\s+proident',
            r'sunt\s+in\s+culpa',
            r'qui\s+officia\s+deserunt',
            r'mollit\s+anim\s+id\s+est\s+laborum'
        ]
        
        # 모든 지원자 데이터 가져오기
        applicants = await db.applicants.find({}).to_list(length=None)
        print(f"📊 총 {len(applicants)}명의 지원자 데이터 검사 중...")
        
        updated_count = 0
        
        for applicant in applicants:
            name = applicant.get('name', 'N/A')
            position = applicant.get('position', '개발자')
            experience = applicant.get('experience', '3년')
            
            # 모든 텍스트 필드 검사
            text_fields = {
                'careerHistory': applicant.get('careerHistory', ''),
                'growthBackground': applicant.get('growthBackground', ''),
                'motivation': applicant.get('motivation', ''),
                'analysisResult': applicant.get('analysisResult', ''),
                'education': applicant.get('education', ''),
                'certificates': applicant.get('certificates', ''),
                'skills': applicant.get('skills', ''),
                'summary': applicant.get('summary', ''),
                'notes': applicant.get('notes', '')
            }
            
            # 라틴어 검사
            has_latin = False
            for field_name, field_value in text_fields.items():
                if isinstance(field_value, str):
                    for pattern in latin_patterns:
                        if re.search(pattern, field_value.lower()):
                            has_latin = True
                            break
                    if has_latin:
                        break
            
            if has_latin:
                print(f"🔍 라틴어 발견 - {name}: 교체 진행 중...")
                
                # 경력 연도 추출
                experience_years = 3  # 기본값
                if '년' in experience:
                    try:
                        experience_years = int(experience.replace('년', ''))
                    except:
                        experience_years = 3
                
                # 새로운 내용 생성
                new_data = {
                    'careerHistory': generate_realistic_career_history(position, experience),
                    'growthBackground': generate_realistic_growth_background(position, experience),
                    'motivation': generate_realistic_motivation(position, "회사"),
                    'analysisResult': generate_realistic_analysis_result(position, experience),
                    'education': generate_realistic_education(position),
                    'certificates': generate_realistic_certificates(position),
                    'updated_at': datetime.now()
                }
                
                # 데이터베이스 업데이트
                result = await db.applicants.update_one(
                    {'_id': applicant['_id']},
                    {'$set': new_data}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ {name} 데이터 업데이트 완료")
                    print(f"   새 경력: {new_data['careerHistory'][:50]}...")
                    print(f"   새 학력: {new_data['education']}")
                    print(f"   새 자격증: {new_data['certificates']}")
                    print()
        
        print(f"🎉 총 {updated_count}명의 지원자 데이터가 업데이트되었습니다.")
        
        if updated_count == 0:
            print("✅ 라틴어 데이터가 발견되지 않았습니다.")
        
        client.close()
        return updated_count
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 0


def generate_realistic_education(position):
    """실제적인 학력 정보 생성"""
    education_templates = {
        "프론트엔드 개발자": [
            "서울대학교 컴퓨터공학과 졸업",
            "연세대학교 컴퓨터과학과 졸업",
            "고려대학교 소프트웨어학과 졸업",
            "한양대학교 컴퓨터공학과 졸업",
            "성균관대학교 소프트웨어학과 졸업"
        ],
        "백엔드 개발자": [
            "서울대학교 컴퓨터공학과 졸업",
            "연세대학교 컴퓨터과학과 졸업",
            "고려대학교 소프트웨어학과 졸업",
            "한양대학교 컴퓨터공학과 졸업",
            "성균관대학교 소프트웨어학과 졸업"
        ],
        "풀스택 개발자": [
            "서울대학교 컴퓨터공학과 졸업",
            "연세대학교 컴퓨터과학과 졸업",
            "고려대학교 소프트웨어학과 졸업",
            "한양대학교 컴퓨터공학과 졸업",
            "성균관대학교 소프트웨어학과 졸업"
        ],
        "데이터 분석가": [
            "서울대학교 통계학과 졸업",
            "연세대학교 수학과 졸업",
            "고려대학교 통계학과 졸업",
            "한양대학교 산업공학과 졸업",
            "성균관대학교 경영학과 졸업"
        ],
        "QA 엔지니어": [
            "서울대학교 컴퓨터공학과 졸업",
            "연세대학교 컴퓨터과학과 졸업",
            "고려대학교 소프트웨어학과 졸업",
            "한양대학교 컴퓨터공학과 졸업",
            "성균관대학교 소프트웨어학과 졸업"
        ]
    }
    
    templates = education_templates.get(position, [
        "서울대학교 컴퓨터공학과 졸업",
        "연세대학교 컴퓨터과학과 졸업",
        "고려대학교 소프트웨어학과 졸업",
        "한양대학교 컴퓨터공학과 졸업",
        "성균관대학교 소프트웨어학과 졸업"
    ])
    
    return random.choice(templates)


def generate_realistic_certificates(position):
    """실제적인 자격증 정보 생성"""
    certificate_templates = {
        "프론트엔드 개발자": [
            "정보처리기사, 웹디자인기능사",
            "정보처리기사, 컴퓨터활용능력 1급",
            "정보처리기사, 웹디자인기능사, 컴퓨터활용능력 2급",
            "정보처리기사",
            "웹디자인기능사, 컴퓨터활용능력 1급"
        ],
        "백엔드 개발자": [
            "정보처리기사, SQLD",
            "정보처리기사, 컴퓨터활용능력 1급",
            "정보처리기사, SQLD, 리눅스마스터 2급",
            "정보처리기사, 컴퓨터활용능력 1급, SQLD",
            "SQLD, 리눅스마스터 2급"
        ],
        "풀스택 개발자": [
            "정보처리기사, SQLD, 웹디자인기능사",
            "정보처리기사, 컴퓨터활용능력 1급, SQLD",
            "정보처리기사, SQLD, 리눅스마스터 2급",
            "정보처리기사, 웹디자인기능사, 컴퓨터활용능력 1급",
            "SQLD, 웹디자인기능사, 컴퓨터활용능력 2급"
        ],
        "데이터 분석가": [
            "ADsP, SQLD, 컴퓨터활용능력 1급",
            "ADsP, SQLD, 정보처리기사",
            "ADsP, SQLD, 컴퓨터활용능력 2급",
            "ADsP, SQLD",
            "SQLD, 컴퓨터활용능력 1급"
        ],
        "QA 엔지니어": [
            "정보처리기사, 컴퓨터활용능력 1급",
            "정보처리기사, 웹디자인기능사",
            "정보처리기사, 컴퓨터활용능력 2급",
            "정보처리기사",
            "컴퓨터활용능력 1급, 웹디자인기능사"
        ]
    }
    
    templates = certificate_templates.get(position, [
        "정보처리기사",
        "정보처리기사, 컴퓨터활용능력 1급",
        "컴퓨터활용능력 1급",
        "정보처리기사, SQLD",
        "SQLD, 컴퓨터활용능력 2급"
    ])
    
    return random.choice(templates)


def generate_realistic_career_history(position, experience):
    """실제적인 경력 사항 생성"""
    career_templates = {
        "프론트엔드 개발자": [
            f"{experience}간 React, Vue.js 기반 웹 애플리케이션 개발 경험. 사용자 경험 개선 및 성능 최적화에 중점을 두고 개발했습니다.",
            f"프론트엔드 개발 {experience} 경력으로 TypeScript, Next.js를 활용한 대규모 프로젝트 참여 경험이 있습니다.",
            f"{experience}간 모던 웹 기술 스택을 활용한 반응형 웹사이트 및 SPA 개발 경험을 보유하고 있습니다."
        ],
        "백엔드 개발자": [
            f"{experience}간 Java, Spring Boot 기반 서버 애플리케이션 개발 경험. RESTful API 설계 및 데이터베이스 최적화에 능숙합니다.",
            f"백엔드 개발 {experience} 경력으로 Node.js, Express, MongoDB를 활용한 마이크로서비스 아키텍처 구축 경험이 있습니다.",
            f"{experience}간 Python, Django, PostgreSQL을 활용한 안정적인 서버 시스템 개발 경험을 보유하고 있습니다."
        ],
        "풀스택 개발자": [
            f"{experience}간 프론트엔드와 백엔드 개발 경험을 보유. React, Node.js, MongoDB 스택으로 풀스택 애플리케이션을 개발했습니다.",
            f"풀스택 개발 {experience} 경력으로 Vue.js, Python, FastAPI, PostgreSQL을 활용한 웹 서비스 구축 경험이 있습니다.",
            f"{experience}간 TypeScript, Next.js, Prisma, PostgreSQL을 활용한 현대적인 웹 애플리케이션 개발 경험을 보유하고 있습니다."
        ],
        "데이터 분석가": [
            f"{experience}간 Python, R, SQL을 활용한 데이터 분석 경험. 머신러닝 모델 개발 및 비즈니스 인사이트 도출에 중점을 두고 있습니다.",
            f"데이터 분석 {experience} 경력으로 통계 분석, 시각화, 예측 모델링 경험이 풍부합니다.",
            f"{experience}간 빅데이터 처리 및 분석 경험을 보유. Tableau, Power BI를 활용한 대시보드 구축 경험이 있습니다."
        ],
        "QA 엔지니어": [
            f"{experience}간 웹 애플리케이션 테스트 자동화 경험. Selenium, Cypress를 활용한 효율적인 테스트 프로세스 구축 경험이 있습니다.",
            f"QA 엔지니어 {experience} 경력으로 기능 테스트, 성능 테스트, 보안 테스트 경험이 풍부합니다.",
            f"{experience}간 다양한 테스트 도구와 방법론을 활용한 품질 보증 경험을 보유하고 있습니다."
        ]
    }
    
    templates = career_templates.get(position, [
        f"{experience}간 해당 분야에서 실무 경험을 쌓아왔습니다.",
        f"관련 업무 {experience} 경력으로 다양한 프로젝트에 참여한 경험이 있습니다.",
        f"{experience}간 전문성을 바탕으로 성과를 창출한 경험이 풍부합니다."
    ])
    
    return random.choice(templates)


def generate_realistic_growth_background(position, experience):
    """실제적인 성장 배경 생성"""
    growth_templates = {
        "프론트엔드 개발자": [
            f"웹 개발에 대한 관심으로 시작하여 {experience}간 React, Vue.js 등 모던 프레임워크를 학습하고 실무에 적용했습니다.",
            f"사용자 경험 개선에 대한 열정으로 프론트엔드 개발을 시작하여 {experience}간 다양한 프로젝트를 통해 성장했습니다.",
            f"웹 표준과 접근성에 대한 이해를 바탕으로 {experience}간 프론트엔드 개발 경험을 쌓아왔습니다."
        ],
        "백엔드 개발자": [
            f"서버 사이드 로직에 대한 깊은 이해를 바탕으로 {experience}간 Java, Python 등 다양한 언어로 서버 개발 경험을 쌓았습니다.",
            f"데이터베이스 설계와 API 개발에 대한 관심으로 시작하여 {experience}간 안정적인 백엔드 시스템을 구축했습니다.",
            f"시스템 아키텍처와 성능 최적화에 중점을 두고 {experience}간 백엔드 개발 경험을 쌓아왔습니다."
        ],
        "풀스택 개발자": [
            f"전체 개발 프로세스에 대한 이해를 바탕으로 {experience}간 프론트엔드와 백엔드 개발을 병행하며 풀스택 역량을 키워왔습니다.",
            f"다양한 기술 스택을 학습하여 {experience}간 웹 애플리케이션의 전체 라이프사이클을 경험했습니다.",
            f"사용자 요구사항부터 배포까지 전체 과정을 이해하고 {experience}간 풀스택 개발 경험을 쌓았습니다."
        ],
        "데이터 분석가": [
            f"데이터 기반 의사결정의 중요성을 인식하고 {experience}간 Python, R, SQL을 활용한 데이터 분석 경험을 쌓았습니다.",
            f"통계학적 지식을 바탕으로 {experience}간 비즈니스 인사이트 도출을 위한 데이터 분석을 수행했습니다.",
            f"머신러닝과 통계 분석에 대한 관심으로 시작하여 {experience}간 다양한 데이터 분석 프로젝트를 진행했습니다."
        ],
        "QA 엔지니어": [
            f"품질 보증의 중요성을 인식하고 {experience}간 다양한 테스트 방법론과 도구를 학습하여 적용했습니다.",
            f"사용자 관점에서의 테스트에 대한 이해를 바탕으로 {experience}간 효율적인 테스트 프로세스를 구축했습니다.",
            f"자동화 테스트와 지속적 통합에 대한 관심으로 {experience}간 QA 프로세스 개선 경험을 쌓았습니다."
        ]
    }
    
    templates = growth_templates.get(position, [
        f"해당 분야에 대한 깊은 관심과 열정으로 {experience}간 지속적인 학습과 실무 경험을 쌓아왔습니다.",
        f"전문성을 키우기 위해 {experience}간 다양한 프로젝트와 기술을 학습하며 성장했습니다.",
        f"실무 경험을 통해 {experience}간 해당 분야의 전문성을 쌓아왔습니다."
    ])
    
    return random.choice(templates)


def generate_realistic_motivation(position, company):
    """실제적인 지원 동기 생성"""
    motivation_templates = {
        "프론트엔드 개발자": [
            f"{company}에서 사용자 중심의 웹 서비스를 개발하고 싶어 지원하게 되었습니다. 사용자 경험 개선과 최신 웹 기술 적용에 대한 열정을 가지고 있습니다.",
            f"{company}의 혁신적인 웹 서비스 개발에 참여하고 싶어 지원했습니다. 반응형 디자인과 성능 최적화에 대한 전문성을 바탕으로 기여하고 싶습니다.",
            f"{company}에서 모던 웹 기술을 활용한 대규모 서비스 개발에 참여하고 싶어 지원하게 되었습니다."
        ],
        "백엔드 개발자": [
            f"{company}의 안정적이고 확장 가능한 서버 시스템 구축에 기여하고 싶어 지원했습니다. 데이터베이스 설계와 API 개발에 대한 전문성을 가지고 있습니다.",
            f"{company}에서 마이크로서비스 아키텍처와 클라우드 인프라 구축에 참여하고 싶어 지원하게 되었습니다.",
            f"{company}의 대용량 트래픽을 처리할 수 있는 고성능 백엔드 시스템 개발에 기여하고 싶습니다."
        ],
        "풀스택 개발자": [
            f"{company}에서 웹 애플리케이션의 전체 개발 라이프사이클에 참여하고 싶어 지원했습니다. 프론트엔드와 백엔드 개발 경험을 바탕으로 기여하고 싶습니다.",
            f"{company}의 풀스택 개발팀에서 다양한 기술 스택을 활용한 프로젝트에 참여하고 싶어 지원하게 되었습니다.",
            f"{company}에서 사용자 요구사항부터 배포까지 전체 과정을 담당하며 성장하고 싶습니다."
        ],
        "데이터 분석가": [
            f"{company}의 데이터 기반 의사결정 프로세스에 기여하고 싶어 지원했습니다. 비즈니스 인사이트 도출과 예측 모델링에 대한 전문성을 가지고 있습니다.",
            f"{company}에서 빅데이터 분석과 머신러닝을 활용한 혁신적인 솔루션 개발에 참여하고 싶어 지원하게 되었습니다.",
            f"{company}의 데이터 분석팀에서 통계적 분석과 시각화를 통해 비즈니스 가치를 창출하고 싶습니다."
        ],
        "QA 엔지니어": [
            f"{company}의 제품 품질 향상에 기여하고 싶어 지원했습니다. 효율적인 테스트 프로세스 구축과 자동화에 대한 전문성을 가지고 있습니다.",
            f"{company}에서 사용자 중심의 품질 보증 프로세스를 구축하고 싶어 지원하게 되었습니다.",
            f"{company}의 QA 팀에서 지속적인 품질 개선과 테스트 자동화를 통해 제품의 신뢰성을 높이고 싶습니다."
        ]
    }
    
    templates = motivation_templates.get(position, [
        f"{company}에서 해당 분야의 전문성을 바탕으로 성장하고 싶어 지원하게 되었습니다.",
        f"{company}의 혁신적인 프로젝트에 참여하여 새로운 도전을 하고 싶어 지원했습니다.",
        f"{company}에서 실무 경험을 바탕으로 기여하고 함께 성장하고 싶습니다."
    ])
    
    return random.choice(templates)


def generate_realistic_analysis_result(position, experience):
    """실제적인 분석 결과 생성"""
    analysis_templates = {
        "프론트엔드 개발자": [
            f"프론트엔드 개발 {experience} 경력으로 React, Vue.js 등 모던 프레임워크 활용 능력이 우수합니다. 사용자 경험 개선과 성능 최적화에 대한 이해가 깊습니다.",
            f"웹 표준과 접근성에 대한 이해가 뛰어나며, 반응형 디자인 구현 능력이 우수합니다. {experience}간의 실무 경험을 바탕으로 안정적인 개발이 가능합니다.",
            f"최신 웹 기술 트렌드에 대한 이해가 깊고, TypeScript, Next.js 등 현대적인 도구 활용 능력이 우수합니다."
        ],
        "백엔드 개발자": [
            f"백엔드 개발 {experience} 경력으로 서버 아키텍처 설계와 데이터베이스 최적화 능력이 뛰어납니다. 안정적이고 확장 가능한 시스템 구축이 가능합니다.",
            f"RESTful API 설계와 마이크로서비스 아키텍처에 대한 이해가 깊습니다. {experience}간의 경험을 바탕으로 고성능 서버 시스템 개발이 가능합니다.",
            f"보안과 성능 최적화에 대한 이해가 뛰어나며, 클라우드 환경에서의 서버 운영 경험이 풍부합니다."
        ],
        "풀스택 개발자": [
            f"풀스택 개발 {experience} 경력으로 프론트엔드와 백엔드 개발 능력이 균형있게 우수합니다. 전체 개발 라이프사이클에 대한 이해가 깊습니다.",
            f"다양한 기술 스택을 활용한 웹 애플리케이션 개발 경험이 풍부합니다. {experience}간의 경험을 바탕으로 독립적인 프로젝트 진행이 가능합니다.",
            f"사용자 요구사항 분석부터 배포까지 전체 과정을 담당할 수 있는 역량을 보유하고 있습니다."
        ],
        "데이터 분석가": [
            f"데이터 분석 {experience} 경력으로 통계 분석과 머신러닝 모델 개발 능력이 우수합니다. 비즈니스 인사이트 도출 능력이 뛰어납니다.",
            f"Python, R, SQL을 활용한 데이터 처리와 분석 능력이 우수합니다. {experience}간의 경험을 바탕으로 복잡한 데이터 분석이 가능합니다.",
            f"데이터 시각화와 대시보드 구축 능력이 뛰어나며, 비즈니스 의사결정을 지원하는 분석 결과를 제공할 수 있습니다."
        ],
        "QA 엔지니어": [
            f"QA 엔지니어 {experience} 경력으로 다양한 테스트 방법론과 도구 활용 능력이 우수합니다. 효율적인 테스트 프로세스 구축이 가능합니다.",
            f"자동화 테스트와 지속적 통합에 대한 이해가 깊습니다. {experience}간의 경험을 바탕으로 품질 보증 프로세스 개선이 가능합니다.",
            f"사용자 관점에서의 테스트 설계 능력이 뛰어나며, 제품의 신뢰성 향상에 기여할 수 있습니다."
        ]
    }
    
    templates = analysis_templates.get(position, [
        f"해당 분야 {experience} 경력으로 전문적인 역량을 보유하고 있습니다. 실무 경험을 바탕으로 안정적인 업무 수행이 가능합니다.",
        f"관련 업무에 대한 깊은 이해와 {experience}간의 경험을 바탕으로 성과를 창출할 수 있는 역량을 보유하고 있습니다.",
        f"전문성을 바탕으로 한 문제 해결 능력과 {experience}간의 실무 경험을 통해 안정적인 업무 수행이 가능합니다."
    ])
    
    return random.choice(templates)


if __name__ == "__main__":
    asyncio.run(fix_all_latin_data())


