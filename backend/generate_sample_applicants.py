import random
import requests
import json
from datetime import datetime, timedelta
from faker import Faker

# Faker 초기화 (한국어)
fake = Faker('ko_KR')

# 채용공고 ID 목록 (실제 DB에서 가져온 것)
JOB_POSTING_IDS = [
    "68a90cae62e30350c2752f15",  # 프론트엔드 개발자
    "68a90cba62e30350c2752f16",  # 백엔드 개발자
    "68a90cc262e30350c2752f17",  # UI/UX 디자이너
    "68a90cc962e30350c2752f18",  # 디지털 마케팅 전문가
    "68a90cd162e30350c2752f19"   # 프로젝트 매니저
]

# 부서별 직무 매핑
DEPARTMENT_POSITION_MAP = {
    "개발팀": ["프론트엔드 개발자", "백엔드 개발자", "풀스택 개발자", "모바일 개발자"],
    "디자인팀": ["UI/UX 디자이너", "웹 디자이너", "그래픽 디자이너"],
    "마케팅팀": ["디지털 마케팅 전문가", "콘텐츠 마케터", "퍼포먼스 마케터"],
    "기획팀": ["프로젝트 매니저", "서비스 기획자", "사업 기획자"]
}

# 직무별 기술 스택
POSITION_SKILLS_MAP = {
    "프론트엔드 개발자": ["React", "Vue.js", "JavaScript", "TypeScript", "HTML", "CSS", "Webpack", "Next.js"],
    "백엔드 개발자": ["Node.js", "Python", "Java", "Spring Boot", "MySQL", "PostgreSQL", "MongoDB", "Redis"],
    "풀스택 개발자": ["React", "Node.js", "JavaScript", "TypeScript", "MySQL", "MongoDB", "Express.js"],
    "모바일 개발자": ["React Native", "Flutter", "Swift", "Kotlin", "Android", "iOS"],
    "UI/UX 디자이너": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "Principle"],
    "웹 디자이너": ["Figma", "Adobe XD", "Photoshop", "HTML", "CSS", "Zeplin"],
    "그래픽 디자이너": ["Photoshop", "Illustrator", "InDesign", "After Effects"],
    "디지털 마케팅 전문가": ["Google Ads", "Facebook Ads", "GA4", "GTM", "SEO", "SEM"],
    "콘텐츠 마케터": ["콘텐츠 기획", "카피라이팅", "브랜딩", "SNS 마케팅"],
    "퍼포먼스 마케터": ["Google Ads", "Facebook Ads", "데이터 분석", "A/B 테스트"],
    "프로젝트 매니저": ["Jira", "Notion", "Slack", "애자일", "스크럼", "PMP"],
    "서비스 기획자": ["Figma", "Notion", "데이터 분석", "사용자 리서치"],
    "사업 기획자": ["Excel", "PowerPoint", "데이터 분석", "시장 조사"]
}

# 경력 옵션
EXPERIENCE_OPTIONS = ["신입", "1-3년", "3-5년", "5-7년", "7-10년", "10년 이상"]

# 상태 옵션
STATUS_OPTIONS = ["pending", "reviewing", "interview_scheduled", "passed", "rejected"]

def generate_korean_name():
    """한국식 이름 생성"""
    surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "류", "전"]
    first_names = ["민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호", "지후", "준서", "준우", "유준", "연우", "현우", "서연", "서윤", "지우", "서현", "수빈", "지유", "채원", "하은", "유나", "윤서", "소율", "지율", "서진", "하린", "예린", "가은"]
    
    return random.choice(surnames) + random.choice(first_names)

def generate_korean_email(name):
    """한국식 이름 기반 이메일 생성"""
    domains = ["gmail.com", "naver.com", "daum.net", "hanmail.net", "yahoo.com", "hotmail.com"]
    # 한글 이름을 영문으로 변환하는 간단한 매핑
    name_eng = fake.first_name().lower() + random.choice(['123', '456', '789', '2024', ''])
    return f"{name_eng}@{random.choice(domains)}"

def generate_phone_number():
    """한국 휴대폰 번호 생성"""
    prefixes = ["010", "011", "016", "017", "018", "019"]
    return f"{random.choice(prefixes)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_growth_background():
    """성장 배경 생성"""
    backgrounds = [
        "어려서부터 컴퓨터와 인터넷에 관심이 많았고, 대학교에서 관련 전공을 하며 더욱 깊이 있게 학습했습니다.",
        "학창 시절 프로그래밍 동아리 활동을 통해 개발의 즐거움을 알게 되었고, 꾸준히 실력을 쌓아왔습니다.",
        "문제 해결에 대한 열정이 있어 개발 분야에 관심을 갖게 되었고, 다양한 프로젝트 경험을 쌓았습니다.",
        "창의적인 일을 좋아하여 디자인 분야에 관심을 갖게 되었고, 사용자 경험에 대해 깊이 고민해왔습니다.",
        "데이터 분석과 마케팅에 관심이 많아 관련 분야에서 경험을 쌓으며 전문성을 키워왔습니다.",
        "팀 프로젝트를 이끄는 것을 좋아하며, 체계적인 계획과 실행을 통해 성과를 만들어내는 것에 보람을 느낍니다.",
        "새로운 기술을 배우는 것을 즐기며, 끊임없이 자기계발을 통해 전문성을 높여왔습니다."
    ]
    return random.choice(backgrounds)

def generate_motivation(position, department):
    """지원 동기 생성"""
    motivations = [
        f"귀사의 {position} 포지션에 지원하게 된 이유는 회사의 기술력과 비전에 매료되었기 때문입니다. 저의 경험과 열정으로 {department}에 기여하고 싶습니다.",
        f"{department}에서 {position}로 일하며 제가 가진 역량을 발휘하고, 회사와 함께 성장하고 싶어 지원하게 되었습니다.",
        f"귀사의 혁신적인 서비스와 문화에 감명받아 {position} 포지션에 지원하게 되었습니다. 저의 전문성으로 팀에 도움이 되고 싶습니다.",
        f"{position} 분야에서의 제 경험을 바탕으로 귀사의 {department}에서 더 큰 가치를 창출하고 싶어 지원하게 되었습니다.",
        f"끊임없이 발전하는 귀사의 모습을 보며 {position}로서 함께 성장하고 기여하고 싶다는 생각이 들어 지원하게 되었습니다."
    ]
    return random.choice(motivations)

def generate_career_history(position, experience):
    """경력 사항 생성"""
    if experience == "신입":
        return "대학교에서 관련 전공을 이수하였으며, 학교 프로젝트와 개인 프로젝트를 통해 실무 역량을 기렸습니다."
    
    careers = {
        "1-3년": f"스타트업에서 {position}로 2년간 근무하며 다양한 프로젝트에 참여했습니다.",
        "3-5년": f"중소기업에서 {position}로 4년간 근무하며 팀 리딩 경험을 쌓았습니다.",
        "5-7년": f"대기업에서 {position}로 6년간 근무하며 대규모 프로젝트를 성공적으로 수행했습니다.",
        "7-10년": f"여러 회사에서 {position}로 8년간 근무하며 시니어 레벨의 전문성을 쌓았습니다.",
        "10년 이상": f"{position} 분야에서 10년 이상의 풍부한 경험을 가지고 있으며, 다수의 성공 프로젝트를 이끌었습니다."
    }
    return careers.get(experience, "관련 분야에서의 경력이 있습니다.")

def generate_analysis_result(position, skills):
    """분석 결과 생성"""
    return f"{position} 포지션에 적합한 {', '.join(skills[:3])} 기술을 보유하고 있습니다. 실무 경험과 전문성을 바탕으로 팀에 기여할 수 있을 것으로 판단됩니다."

def generate_applicant_data():
    """지원자 데이터 한 개 생성"""
    # 랜덤하게 채용공고 선택
    job_posting_id = random.choice(JOB_POSTING_IDS)
    
    # 채용공고 ID에 따른 부서와 직무 매핑
    job_mapping = {
        "68a90cae62e30350c2752f15": ("개발팀", "프론트엔드 개발자"),
        "68a90cba62e30350c2752f16": ("개발팀", "백엔드 개발자"),
        "68a90cc262e30350c2752f17": ("디자인팀", "UI/UX 디자이너"),
        "68a90cc962e30350c2752f18": ("마케팅팀", "디지털 마케팅 전문가"),
        "68a90cd162e30350c2752f19": ("기획팀", "프로젝트 매니저")
    }
    
    department, position = job_mapping[job_posting_id]
    
    # 기본 정보
    name = generate_korean_name()
    email = generate_korean_email(name)
    phone = generate_phone_number()
    
    # 경력 및 기술
    experience = random.choice(EXPERIENCE_OPTIONS)
    available_skills = POSITION_SKILLS_MAP.get(position, ["기타"])
    num_skills = random.randint(3, min(6, len(available_skills)))
    skills = random.sample(available_skills, num_skills)
    skills_str = ", ".join(skills)
    
    # 텍스트 필드들
    growth_background = generate_growth_background()
    motivation = generate_motivation(position, department)
    career_history = generate_career_history(position, experience)
    
    # 분석 관련
    analysis_score = random.randint(60, 95)
    analysis_result = generate_analysis_result(position, skills)
    
    # 상태
    status = random.choice(STATUS_OPTIONS)
    
    # 생성 일시 (최근 30일 내)
    created_at = datetime.now() - timedelta(days=random.randint(0, 30))
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "position": position,
        "department": department,
        "experience": experience,
        "skills": skills_str,
        "growthBackground": growth_background,
        "motivation": motivation,
        "careerHistory": career_history,
        "analysisScore": analysis_score,
        "analysisResult": analysis_result,
        "status": status,
        "job_posting_id": job_posting_id,
        "created_at": created_at.isoformat()
    }

def generate_sample_applicants(count=200):
    """샘플 지원자 데이터 생성"""
    print(f"=== {count}개 지원자 샘플 데이터 생성 중... ===")
    
    applicants = []
    for i in range(count):
        applicant = generate_applicant_data()
        applicants.append(applicant)
        
        if (i + 1) % 50 == 0:
            print(f"{i + 1}개 생성 완료...")
    
    print(f"총 {len(applicants)}개 지원자 데이터 생성 완료!")
    return applicants

def insert_applicants_to_db(applicants):
    """지원자 데이터를 DB에 삽입"""
    print("=== 지원자 데이터 DB 삽입 중... ===")
    
    success_count = 0
    fail_count = 0
    
    for i, applicant in enumerate(applicants):
        try:
            response = requests.post(
                'http://localhost:8000/api/applicants',
                json=applicant,
                timeout=10
            )
            
            if response.status_code == 201:
                success_count += 1
            else:
                fail_count += 1
                print(f"실패 {i+1}: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            fail_count += 1
            print(f"오류 {i+1}: {e}")
        
        if (i + 1) % 50 == 0:
            print(f"{i + 1}개 처리 완료... (성공: {success_count}, 실패: {fail_count})")
    
    print(f"\n=== 완료 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"총 처리: {len(applicants)}개")

def save_to_json(applicants, filename="sample_applicants.json"):
    """데이터를 JSON 파일로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(applicants, f, ensure_ascii=False, indent=2)
    print(f"데이터가 {filename}에 저장되었습니다.")

def main():
    """메인 함수"""
    print("🚀 지원자 샘플 데이터 생성기 시작!")
    
    # 1. 샘플 데이터 생성
    applicants = generate_sample_applicants(200)
    
    # 2. JSON 파일로 저장 (백업용)
    save_to_json(applicants)
    
    # 3. DB에 삽입
    insert_applicants_to_db(applicants)
    
    print("✅ 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()