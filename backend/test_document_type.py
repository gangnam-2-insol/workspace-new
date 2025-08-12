#!/usr/bin/env python3
"""
문서 타입별 분석 결과 테스트
"""

import requests
import json

def test_document_type_analysis():
    """문서 타입별 분석 결과 테스트"""
    print("🚀 문서 타입별 분석 결과 테스트 시작...\n")
    
    # 테스트용 텍스트
    test_texts = {
        "resume": "안녕하세요. 저는 김개발입니다. 3년간의 웹 개발 경험을 가지고 있으며, React, TypeScript, Node.js를 주로 사용합니다. 이메일: kim@example.com, GitHub: github.com/kimdev",
        "cover_letter": "안녕하세요. 귀사의 프론트엔드 개발자 포지션에 지원하게 된 김개발입니다. 사용자 경험을 향상시키는 웹 애플리케이션 개발에 대한 열정을 가지고 있으며, 이전 프로젝트에서 매출 25% 증가를 달성했습니다.",
        "portfolio": "프로젝트명: 이커머스 플랫폼 리뉴얼, 기술 스택: React, TypeScript, Node.js, MongoDB, 기여도: 팀 리더, 성과: 매출 25% 증가, 사용자 체류 시간 2배 향상"
    }
    
    for doc_type, content in test_texts.items():
        print(f"📄 {doc_type.upper()} 분석 테스트...")
        
        try:
            # 간단한 요약 테스트 (파일 업로드 없이)
            data = {
                "content": content,
                "summary_type": "general"
            }
            
            response = requests.post(
                "http://localhost:8000/api/upload/summarize",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"  상태 코드: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 요약: {result['summary'][:100]}...")
                print(f"  ✅ 키워드: {', '.join(result['keywords'][:3])}")
                print(f"  ✅ 신뢰도: {result['confidence_score']}")
            else:
                print(f"  ❌ 요약 실패: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
        
        print()
    
    print("🎉 문서 타입별 테스트 완료!")
    print("\n💡 이제 프론트엔드에서 각 문서 타입을 선택하여 분석해보세요:")
    print("  - 이력서: resume")
    print("  - 자기소개서: cover_letter") 
    print("  - 포트폴리오: portfolio")

if __name__ == "__main__":
    test_document_type_analysis()
