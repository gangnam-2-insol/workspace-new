"""
개선된 추천 시스템 테스트
일반 패턴 + 학습 데이터 + AI 결합 방식
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.core.suggestion_generator import suggestion_generator

def test_enhanced_suggestions():
    """개선된 추천 시스템 테스트"""
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "프론트엔드 개발자 (연관성 기반 추천)",
            "extracted_fields": {
                "position": "프론트엔드 개발자",
                "tech_stack": ["React", "TypeScript"],
                "experience": "2년",
                "requirements": ["웹 개발 경험"],
                "preferences": ["애자일 경험"]
            }
        },
        {
            "name": "백엔드 개발자 (패턴 기반 추천)",
            "extracted_fields": {
                "position": "백엔드 개발자",
                "tech_stack": ["Python", "Django"],
                "experience": "3년",
                "requirements": ["서버 개발 경험"],
                "preferences": ["대규모 시스템 경험"]
            }
        },
        {
            "name": "데이터 분석가 (AI 보완 추천)",
            "extracted_fields": {
                "position": "데이터 분석가",
                "tech_stack": ["Python", "Pandas"],
                "experience": "1년",
                "requirements": ["통계학 지식"],
                "preferences": ["머신러닝 경험"]
            }
        }
    ]
    
    print("🚀 개선된 추천 시스템 테스트 시작\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 테스트 케이스 {i}: {test_case['name']}")
        print(f"📝 추출된 필드: {test_case['extracted_fields']}")
        print("-" * 80)
        
        # 추천문구 생성
        original_text = f"{test_case['extracted_fields']['position']}를 모집합니다."
        suggestions = suggestion_generator.generate_field_suggestions(
            test_case['extracted_fields'], 
            original_text
        )
        
        print(f"✅ 추천 결과:")
        for field_name, field_data in suggestions.items():
            print(f"\n   📌 {field_name}:")
            print(f"      추출된 값: {field_data['extracted']}")
            print(f"      추천 문구: {field_data['suggestions']}")
            print(f"      소스: {field_data['sources']}")
        
        print("=" * 80)
        print()

if __name__ == "__main__":
    test_enhanced_suggestions()
