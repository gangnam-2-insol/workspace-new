#!/usr/bin/env python3
import pymongo
import json
from datetime import datetime, timezone
from bson import ObjectId
import random

def create_kyungho_applicant():
    """이경호 지원자 샘플 데이터를 생성하고 MongoDB에 삽입합니다."""
    
    # 이경호 지원자 데이터
    kyungho_applicant = {
        "_id": str(ObjectId()),
        "name": "이경호",
        "email": "kyunghol87@naver.com",
        "phone": "010-1234-5678",
        "position": "백엔드 개발자",
        "experience": "5년",
        "skills": "Java, Spring Boot, MySQL, Redis, Docker, AWS",
        "status": "서류합격",
        "job_posting_id": "68a7e68bea9b371aadfda2bb",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "analysisScore": random.randint(75, 95),
        "department": "개발팀",
        "growthBackground": "컴퓨터공학을 전공하고 졸업 후 스타트업에서 백엔드 개발자로 시작하여 현재까지 5년간 다양한 프로젝트를 경험했습니다. 특히 Spring Boot와 MySQL을 활용한 웹 서비스 개발에 전문성을 가지고 있으며, 마이크로서비스 아키텍처와 클라우드 환경에서의 개발 경험이 풍부합니다.",
        "motivation": "귀사의 혁신적인 기술 문화와 사용자 중심의 서비스 개발 철학에 깊이 공감하여 지원하게 되었습니다. 제가 보유한 백엔드 개발 경험과 문제 해결 능력을 바탕으로 팀의 성장에 기여하고 싶습니다. 또한 새로운 기술 스택 학습에 대한 열정을 가지고 있어 지속적인 성장을 추구합니다.",
        "careerHistory": "2019년부터 현재까지 스타트업에서 백엔드 개발자로 근무하며, 사용자 10만명 규모의 웹 서비스 개발 및 운영을 담당했습니다. 주요 업무로는 RESTful API 설계 및 구현, 데이터베이스 설계 및 최적화, AWS 클라우드 인프라 구축 및 관리, CI/CD 파이프라인 구축 등이 있습니다.",
        "resume_id": str(ObjectId()),
        "cover_letter_id": str(ObjectId()),
        "portfolio_id": str(ObjectId()),
        "github_url": "https://github.com/kyungho222",
        "linkedin_url": "https://linkedin.com/in/kyungho-lee",
        "portfolio_url": "https://kyungho-portfolio.com",
        "ranks": {
            "resume": random.randint(80, 95),
            "coverLetter": random.randint(75, 90),
            "portfolio": random.randint(80, 95),
            "total": random.randint(80, 92)
        }
    }
    
    try:
        # MongoDB 연결
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['hireme']
        
        # 기존 이메일 중복 확인
        existing_applicant = db.applicants.find_one({"email": kyungho_applicant["email"]})
        if existing_applicant:
            print(f"⚠️ 이미 존재하는 이메일입니다: {kyungho_applicant['email']}")
            print("기존 데이터를 삭제하고 새로 생성하시겠습니까? (y/N): ", end="")
            confirm = input()
            if confirm.lower() == 'y':
                db.applicants.delete_one({"email": kyungho_applicant["email"]})
                print("✅ 기존 데이터가 삭제되었습니다.")
            else:
                print("❌ 작업이 취소되었습니다.")
                return
        
        # ObjectId 변환
        kyungho_applicant["_id"] = ObjectId(kyungho_applicant["_id"])
        kyungho_applicant["resume_id"] = ObjectId(kyungho_applicant["resume_id"])
        kyungho_applicant["cover_letter_id"] = ObjectId(kyungho_applicant["cover_letter_id"])
        kyungho_applicant["portfolio_id"] = ObjectId(kyungho_applicant["portfolio_id"])
        
        # 날짜 변환
        kyungho_applicant["created_at"] = datetime.fromisoformat(kyungho_applicant["created_at"])
        kyungho_applicant["updated_at"] = datetime.fromisoformat(kyungho_applicant["updated_at"])
        
        # 사용자 확인
        print("\n📋 생성할 지원자 정보:")
        print(f"이름: {kyungho_applicant['name']}")
        print(f"이메일: {kyungho_applicant['email']}")
        print(f"직무: {kyungho_applicant['position']}")
        print(f"경력: {kyungho_applicant['experience']}")
        print(f"기술스택: {kyungho_applicant['skills']}")
        print(f"분석점수: {kyungho_applicant['analysisScore']}")
        print(f"상태: {kyungho_applicant['status']}")
        
        # 자동으로 삽입 진행
        print(f"\n이경호 지원자를 DB에 삽입합니다...")
        
        # 데이터 삽입
        try:
            result = db.applicants.insert_one(kyungho_applicant)
            
            print(f"✅ 이경호 지원자가 성공적으로 삽입되었습니다!")
            print(f"📊 지원자 ID: {result.inserted_id}")
            
            # 최종 통계
            final_count = db.applicants.count_documents({})
            print(f"📊 최종 지원자 수: {final_count}명")
            
            # 삽입된 데이터 확인
            print("\n📋 삽입된 데이터 확인:")
            inserted_applicant = db.applicants.find_one({"_id": result.inserted_id})
            print(f"이름: {inserted_applicant['name']}")
            print(f"이메일: {inserted_applicant['email']}")
            print(f"직무: {inserted_applicant['position']}")
            print(f"상태: {inserted_applicant['status']}")
            print(f"분석점수: {inserted_applicant['analysisScore']}")
            print(f"생성일시: {inserted_applicant['created_at']}")
            
        except Exception as insert_error:
            print(f"❌ 데이터 삽입 실패: {insert_error}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.close()

def create_kyungho_json():
    """이경호 지원자 데이터를 JSON 파일로 생성합니다."""
    
    kyungho_applicant = {
        "_id": "68bb00000000000000000001",
        "name": "이경호",
        "email": "kyunghol87@naver.com",
        "phone": "010-1234-5678",
        "position": "백엔드 개발자",
        "experience": "5년",
        "skills": "Java, Spring Boot, MySQL, Redis, Docker, AWS",
        "status": "서류합격",
        "job_posting_id": "68a7e68bea9b371aadfda2bb",
        "created_at": "2024-12-19T10:00:00.000000",
        "updated_at": "2024-12-19T10:00:00.000000",
        "analysisScore": 88,
        "department": "개발팀",
        "growthBackground": "컴퓨터공학을 전공하고 졸업 후 스타트업에서 백엔드 개발자로 시작하여 현재까지 5년간 다양한 프로젝트를 경험했습니다. 특히 Spring Boot와 MySQL을 활용한 웹 서비스 개발에 전문성을 가지고 있으며, 마이크로서비스 아키텍처와 클라우드 환경에서의 개발 경험이 풍부합니다.",
        "motivation": "귀사의 혁신적인 기술 문화와 사용자 중심의 서비스 개발 철학에 깊이 공감하여 지원하게 되었습니다. 제가 보유한 백엔드 개발 경험과 문제 해결 능력을 바탕으로 팀의 성장에 기여하고 싶습니다. 또한 새로운 기술 스택 학습에 대한 열정을 가지고 있어 지속적인 성장을 추구합니다.",
        "careerHistory": "2019년부터 현재까지 스타트업에서 백엔드 개발자로 근무하며, 사용자 10만명 규모의 웹 서비스 개발 및 운영을 담당했습니다. 주요 업무로는 RESTful API 설계 및 구현, 데이터베이스 설계 및 최적화, AWS 클라우드 인프라 구축 및 관리, CI/CD 파이프라인 구축 등이 있습니다.",
        "resume_id": "68bb00000000000000000002",
        "cover_letter_id": "68bb00000000000000000003",
        "portfolio_id": "68bb00000000000000000004",
        "github_url": "https://github.com/kyungho222",
        "linkedin_url": "https://linkedin.com/in/kyungho-lee",
        "portfolio_url": "https://kyungho-portfolio.com",
        "ranks": {
            "resume": 85,
            "coverLetter": 82,
            "portfolio": 88,
            "total": 85
        }
    }
    
    # JSON 파일로 저장
    with open('kyungho_applicant.json', 'w', encoding='utf-8') as f:
        json.dump([kyungho_applicant], f, ensure_ascii=False, indent=2)
    
    print("✅ kyungho_applicant.json 파일이 생성되었습니다.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        create_kyungho_json()
    else:
        create_kyungho_applicant()
