"""
이력서 분석 모듈
자유 텍스트에서 이력서 정보를 추출하는 기능
"""

import re
from typing import Dict, Any

def extract_resume_info_from_text(text: str) -> Dict[str, Any]:
    """
    자유 텍스트에서 이력서 정보를 추출하는 함수
    JSON 키-값 쌍으로 반환하여 폼 필드와 직접 매칭
    """
    text_lower = text.lower()
    extracted_data = {}
    
    print(f"[DEBUG] extract_resume_info_from_text 시작 - 입력: {text}")
    
    # 이름 추출
    name_patterns = [
        r'([가-힣]{2,4})\s*,',  # 김철수,
        r'([가-힣]{2,4})\s*님',  # 김철수님
        r'이름[:\s]*([가-힣]{2,4})',  # 이름: 김철수
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            extracted_data['name'] = match.group(1)
            print(f"[DEBUG] 이름 추출됨: {match.group(1)}")
            break
    
    # 이메일 추출
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    email_match = re.search(email_pattern, text)
    if email_match:
        extracted_data['email'] = email_match.group(1)
        print(f"[DEBUG] 이메일 추출됨: {email_match.group(1)}")
    
    # 전화번호 추출
    phone_patterns = [
        r'(\d{3}-\d{3,4}-\d{4})',  # 010-1234-5678
        r'(\d{3}\s*\d{3,4}\s*\d{4})',  # 010 1234 5678
        r'(\d{10,11})',  # 01012345678
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(1).replace(' ', '').replace('-', '')
            if len(phone) == 11:
                extracted_data['phone'] = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                print(f"[DEBUG] 전화번호 추출됨: {extracted_data['phone']}")
                break
    
    # 학력 추출
    education_patterns = [
        r'([가-힣]+대학교[가-힣]*과?\s*졸업)',  # 서울대학교 컴퓨터공학과 졸업
        r'([가-힣]+대학교[가-힣]*과?\s*재학)',  # 서울대학교 컴퓨터공학과 재학
        r'([가-힣]+대학교[가-힣]*과?\s*수료)',  # 서울대학교 컴퓨터공학과 수료
        r'([가-힣]+대학교)',  # 서울대학교
        r'([가-힣]+고등학교)',  # 서울고등학교
    ]
    
    for pattern in education_patterns:
        match = re.search(pattern, text)
        if match:
            extracted_data['education'] = match.group(1)
            print(f"[DEBUG] 학력 추출됨: {match.group(1)}")
            break
    
    # 경력 추출
    experience_patterns = [
        r'(\d+)년\s*경력',  # 3년 경력
        r'경력\s*(\d+)년',  # 경력 3년
        r'(\d+)년\s*이상',  # 3년 이상
        r'신입',  # 신입
        r'경력자',  # 경력자
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text)
        if match:
            if '신입' in pattern:
                extracted_data['experience'] = '신입'
            elif '경력자' in pattern:
                extracted_data['experience'] = '경력자'
            else:
                years = match.group(1)
                extracted_data['experience'] = f"{years}년"
            print(f"[DEBUG] 경력 추출됨: {extracted_data['experience']}")
            break
    
    # 기술 스택 추출
    skills_keywords = [
        'Java', 'Python', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
        'Spring', 'Django', 'Node.js', 'Express', 'MySQL', 'PostgreSQL', 'MongoDB',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Jenkins',
        'HTML', 'CSS', 'SASS', 'Bootstrap', 'jQuery', 'Redux', 'Vuex',
        'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin'
    ]
    
    found_skills = []
    for skill in skills_keywords:
        if skill.lower() in text_lower or skill in text:
            found_skills.append(skill)
    
    if found_skills:
        extracted_data['skills'] = ', '.join(found_skills)
        print(f"[DEBUG] 기술 스택 추출됨: {extracted_data['skills']}")
    
    # 자격증 추출
    certificate_patterns = [
        r'([가-힣]+자격증)',  # 정보처리기사 자격증
        r'([가-힣]+증)',  # 정보처리기사증
        r'([A-Z]{2,10})',  # AWS, CCNA 등
    ]
    
    found_certificates = []
    for pattern in certificate_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) >= 2:  # 최소 2글자 이상
                found_certificates.append(match)
    
    if found_certificates:
        extracted_data['certificates'] = ', '.join(found_certificates)
        print(f"[DEBUG] 자격증 추출됨: {extracted_data['certificates']}")
    
    print(f"[DEBUG] 최종 추출된 정보: {extracted_data}")
    
    if not extracted_data:
        return {}
    
    return extracted_data
