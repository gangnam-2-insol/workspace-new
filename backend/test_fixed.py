import requests
import json

def test_resume_analysis():
    """수정된 이력서 분석 API 테스트"""
    print("=== 수정된 이력서 분석 테스트 ===")
    
    # 샘플 이력서 텍스트
    sample_resume = """
    김개발
    연락처: 010-1234-5678
    이메일: kim@example.com
    
    경력사항:
    - ABC 회사 (2020-2023): 웹 개발자
    - XYZ 회사 (2018-2020): 프론트엔드 개발자
    
    기술스택:
    - JavaScript, React, Node.js
    - Python, Django
    - MySQL, MongoDB
    
    프로젝트:
    - 전자상거래 플랫폼 개발 (2022)
    - 모바일 앱 백엔드 API 개발 (2021)
    """
    
    try:
        # 파일 업로드 시뮬레이션
        files = {'file': ('test_resume.txt', sample_resume, 'text/plain')}
        data = {'document_type': 'resume'}
        
        response = requests.post('http://localhost:8000/api/upload/analyze', 
                               files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 분석 성공!")
            print(f"문서 타입: {result.get('document_type')}")
            print(f"파일명: {result.get('filename')}")
            
            analysis = result.get('analysis_result', {})
            
            # 이력서 분석 결과만 있는지 확인
            if 'resume_analysis' in analysis:
                print("✅ 이력서 분석 결과 존재")
                resume_data = analysis['resume_analysis']
                print(f"이력서 분석 항목 수: {len(resume_data)}")
                
                # 점수 계산 확인
                total_score = 0
                count = 0
                for key, value in resume_data.items():
                    if isinstance(value, dict) and 'score' in value:
                        score = value['score']
                        total_score += score
                        count += 1
                        print(f"  {key}: {score}/10")
                
                if count > 0:
                    avg_score = total_score / count
                    print(f"계산된 평균 점수: {avg_score:.1f}")
                
            else:
                print("❌ 이력서 분석 결과 없음")
            
            # 자기소개서와 포트폴리오 분석 결과가 없는지 확인
            if 'cover_letter_analysis' not in analysis:
                print("✅ 자기소개서 분석 결과 없음 (올바름)")
            else:
                print("❌ 자기소개서 분석 결과 존재 (잘못됨)")
                
            if 'portfolio_analysis' not in analysis:
                print("✅ 포트폴리오 분석 결과 없음 (올바름)")
            else:
                print("❌ 포트폴리오 분석 결과 존재 (잘못됨)")
            
            # 전체 요약 확인
            if 'overall_summary' in analysis:
                overall = analysis['overall_summary']
                print(f"전체 점수: {overall.get('total_score')}/10")
                print(f"추천사항: {overall.get('recommendation')}")
            
        else:
            print(f"❌ 분석 실패: {response.status_code}")
            print(f"에러: {response.text}")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_resume_analysis()
