import requests
import json
from datetime import datetime
import random

# 백엔드 서버 URL
API_BASE_URL = "http://localhost:8000"

# 지원자 정보 가져오기
def get_applicants():
    try:
        response = requests.get(f"{API_BASE_URL}/api/applicants")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"지원자 정보 가져오기 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"API 요청 오류: {e}")
        return []

# 포트폴리오 생성
def create_portfolio_for_applicant(applicant):
    applicant_id = applicant.get('id', applicant.get('_id'))
    name = applicant.get('name')
    position = applicant.get('position')
    skills = applicant.get('skills', [])
    
    print(f"\n=== {name} ({position}) 포트폴리오 생성 중 ===")
    
    # 포트폴리오 아이템 생성
    portfolio_items = []
    
    # 프로젝트 A
    project_a = {
        "title": f"{name} - 웹 애플리케이션 프로젝트",
        "description": f"사용자 친화적인 웹 애플리케이션을 개발하여 기존 시스템의 사용성을 크게 개선한 프로젝트입니다.",
        "tech_stack": skills[:3] if len(skills) >= 3 else skills,
        "role": f"{position} 개발 및 설계",
        "duration": "6개월",
        "team_size": 5,
        "achievements": [
            "사용자 만족도 20% 향상",
            "시스템 응답 속도 30% 개선", 
            "코드 품질 향상으로 유지보수성 증대"
        ],
        "artifacts": [
            {
                "kind": "file",
                "filename": f"{name}_프로젝트A_스크린샷.png",
                "mime": "image/png",
                "size": 1024000,
                "hash": f"hash_{name}_projectA_{random.randint(1000, 9999)}"
            }
        ]
    }
    portfolio_items.append(project_a)
    
    # 프로젝트 B
    project_b = {
        "title": f"{name} - 모바일 앱 프로젝트",
        "description": "모바일 환경에 최적화된 애플리케이션을 개발하여 사용자 접근성을 향상시킨 프로젝트입니다.",
        "tech_stack": skills[1:4] if len(skills) >= 4 else skills,
        "role": f"{position} 담당",
        "duration": "4개월",
        "team_size": 3,
        "achievements": [
            "앱스토어 평점 4.5/5.0 달성",
            "다운로드 수 10,000+ 달성",
            "사용자 이탈률 15% 감소"
        ],
        "artifacts": [
            {
                "kind": "url",
                "filename": f"{name}_모바일앱_데모",
                "url": f"https://demo.example.com/{name.lower().replace(' ', '')}_mobile_app"
            }
        ]
    }
    portfolio_items.append(project_b)
    
    # 포트폴리오 데이터 구성
    portfolio_data = {
        "applicant_id": str(applicant_id),
        "application_id": f"app_{applicant_id}_{random.randint(1000, 9999)}",
        "extracted_text": f"{name}의 포트폴리오입니다. {position} 분야에서 다양한 프로젝트를 수행했습니다.",
        "summary": f"{name}의 {position} 포트폴리오 - 웹 애플리케이션과 모바일 앱 개발 경험",
        "keywords": skills,
        "document_type": "portfolio",
        "basic_info": {
            "emails": [f"{name.lower().replace(' ', '')}@email.com"],
            "phones": [f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"],
            "names": [name],
            "urls": [f"https://portfolio.{name.lower().replace(' ', '')}.com"]
        },
        "file_metadata": {
            "filename": f"{name}_포트폴리오.pdf",
            "size": 2048000,
            "mime": "application/pdf",
            "hash": f"hash_{name}_portfolio_{random.randint(1000, 9999)}",
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat()
        },
        "items": portfolio_items,
        "analysis_score": random.uniform(75, 95),
        "status": "active",
        "version": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return portfolio_data

# 메인 실행
def main():
    print("=== 포트폴리오 생성 시작 ===")
    
    # 지원자 정보 가져오기
    applicants = get_applicants()
    if not applicants:
        print("지원자 정보를 가져올 수 없습니다.")
        return
    
    print(f"총 {len(applicants)}명의 지원자에 대한 포트폴리오를 생성합니다.")
    
    success_count = 0
    
    for applicant in applicants:
        try:
            portfolio_data = create_portfolio_for_applicant(applicant)
            
            # 포트폴리오 데이터를 JSON 파일로 저장 (일단 파일로 저장)
            name = applicant.get('name')
            filename = f"portfolio_{name.replace(' ', '_')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ {name} 포트폴리오 데이터 생성 완료 ({filename})")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {applicant.get('name')} 포트폴리오 생성 실패: {e}")
    
    print(f"\n=== 포트폴리오 생성 완료 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {len(applicants) - success_count}개")

if __name__ == "__main__":
    main()
