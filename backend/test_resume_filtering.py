import requests
import json

def test_resume_analysis_filtering():
    """이력서 분석 시 이력서 관련 내용만 반환되는지 테스트"""
    
    # 테스트용 이력서 텍스트
    resume_text = """
    홍길동
    이메일: hong@example.com
    전화: 010-1234-5678
    
    경력:
    - ABC 회사에서 3년간 백엔드 개발자로 근무
    - XYZ 프로젝트에서 Java, Spring Boot 사용
    - 데이터베이스 설계 및 API 개발 경험
    
    기술 스택:
    - Java, Spring Boot, MySQL, Redis
    - Git, Docker, AWS
    
    프로젝트:
    - 전자상거래 플랫폼 개발 (2022-2023)
    - 사용자 관리 시스템 구축 (2021-2022)
    """
    
    try:
        print("🔍 이력서 분석 필터링 테스트 시작...")
        
        # 이력서 분석 요청
        files = {
            'file': ('resume.txt', resume_text.encode('utf-8'), 'text/plain')
        }
        data = {
            'document_type': 'resume'
        }
        
        response = requests.post(
            'http://localhost:8000/api/upload/analyze',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 이력서 분석 성공!")
            print(f"📁 파일명: {result['filename']}")
            print(f"📊 문서 타입: {result['document_type']}")
            
            # 분석 결과 구조 확인
            analysis_result = result['analysis_result']
            print("\n📋 분석 결과 구조:")
            print(f"- resume_analysis 존재: {'resume_analysis' in analysis_result}")
            print(f"- cover_letter_analysis 존재: {'cover_letter_analysis' in analysis_result}")
            print(f"- portfolio_analysis 존재: {'portfolio_analysis' in analysis_result}")
            print(f"- overall_summary 존재: {'overall_summary' in analysis_result}")
            
            # 이력서 분석 결과만 있는지 확인
            if 'resume_analysis' in analysis_result:
                print("\n📝 이력서 분석 결과:")
                resume_analysis = analysis_result['resume_analysis']
                for key, value in resume_analysis.items():
                    print(f"  - {key}: {value['score']}/10 - {value['feedback']}")
            
            if 'overall_summary' in analysis_result:
                print(f"\n🎯 전체 요약:")
                print(f"  - 총점: {analysis_result['overall_summary']['total_score']}/10")
                print(f"  - 권장사항: {analysis_result['overall_summary']['recommendation']}")
            
            # 중요: cover_letter_analysis와 portfolio_analysis가 비어있거나 존재하지 않아야 함
            if 'cover_letter_analysis' in analysis_result:
                cover_letter_data = analysis_result['cover_letter_analysis']
                if cover_letter_data and len(cover_letter_data) > 0:
                    print("❌ 문제: cover_letter_analysis가 비어있지 않음!")
                    print(f"  - 내용: {cover_letter_data}")
                else:
                    print("✅ cover_letter_analysis가 올바르게 비어있음")
            
            if 'portfolio_analysis' in analysis_result:
                portfolio_data = analysis_result['portfolio_analysis']
                if portfolio_data and len(portfolio_data) > 0:
                    print("❌ 문제: portfolio_analysis가 비어있지 않음!")
                    print(f"  - 내용: {portfolio_data}")
                else:
                    print("✅ portfolio_analysis가 올바르게 비어있음")
            
            print("\n🎉 테스트 완료!")
            
        else:
            print(f"❌ 이력서 분석 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_resume_analysis_filtering()
