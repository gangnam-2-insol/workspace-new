#!/usr/bin/env python3
"""
맥락 분류기 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.core.context_classifier import classify_context, is_recruitment_text

def test_context_classifier():
    """맥락 분류기 테스트"""
    
    test_cases = [
        # 확실한 채용공고
        {
            "text": "신입 및 경력 지원자 모두 환영합니다. 기본적인 컴퓨터 활용 능력과 긍정적인 마인드를 갖춘 분을 찾고 있으며, 업무에 대한 책임감과 배우려는 자세가 중요합니다. 회사 내부 교육 프로그램을 통해 직무 역량 강화를 지원하며, 빠른 적응과 성장 가능성이 있는 인재를 우대합니다. 연봉은 경력과 역량에 따라 협의 후 결정되며, 근무지는 서울 강남구입니다. 제출 서류로는 이력서, 자기소개서, 관련 자격증 사본이 필요합니다.",
            "expected": True,
            "description": "완전한 채용공고"
        },
        
        # 짧은 질문 (비채용)
        {
            "text": "연봉은 협상 가능한가요?",
            "expected": False,
            "description": "짧은 급여 질문"
        },
        
        # 자격요건만 나열 (비채용)
        {
            "text": "컴퓨터 활용 능력과 책임감이 필요합니다",
            "expected": False,
            "description": "자격요건만 나열"
        },
        
        # 채용 의도가 있는 문장
        {
            "text": "개발자를 뽑고 있습니다. React 경험이 있으시면 지원해주세요.",
            "expected": True,
            "description": "채용 의도 + 자격요건"
        },
        
        # 일반 대화
        {
            "text": "안녕하세요! 오늘 날씨가 좋네요.",
            "expected": False,
            "description": "일반적인 인사"
        },
        
        # 채용 관련 정보 조회
        {
            "text": "저장된 채용공고를 보여주세요",
            "expected": False,
            "description": "채용공고 조회 요청"
        },
        
        # 계산 요청
        {
            "text": "연봉 4000만원의 월급을 계산해주세요",
            "expected": False,
            "description": "급여 계산 요청"
        }
    ]
    
    print("🧪 맥락 분류기 테스트 시작\n")
    
    correct_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 테스트 {i}: {test_case['description']}")
        print(f"입력: {test_case['text'][:100]}{'...' if len(test_case['text']) > 100 else ''}")
        
        # 맥락 분류 실행
        result = classify_context(test_case['text'])
        
        print(f"결과: 점수 {result.total_score:.2f}, 채용: {result.is_recruitment}, 신뢰도: {result.confidence:.2f}")
        print(f"카테고리 점수: {result.category_scores}")
        
        # 예상 결과와 비교
        is_correct = result.is_recruitment == test_case['expected']
        if is_correct:
            correct_count += 1
            print("✅ 정확")
        else:
            print(f"❌ 오류 (예상: {test_case['expected']}, 실제: {result.is_recruitment})")
        
        print("-" * 80)
    
    # 최종 결과
    accuracy = (correct_count / total_count) * 100
    print(f"\n🎯 테스트 결과: {correct_count}/{total_count} 정확 ({accuracy:.1f}%)")
    
    if accuracy >= 80:
        print("✅ 맥락 분류기가 정상적으로 작동합니다!")
    else:
        print("⚠️ 맥락 분류기 성능 개선이 필요합니다.")

def test_specific_case():
    """특정 케이스 상세 테스트"""
    test_text = "신입 및 경력 지원자 모두 환영합니다. 기본적인 컴퓨터 활용 능력과 긍정적인 마인드를 갖춘 분을 찾고 있으며, 업무에 대한 책임감과 배우려는 자세가 중요합니다. 회사 내부 교육 프로그램을 통해 직무 역량 강화를 지원하며, 빠른 적응과 성장 가능성이 있는 인재를 우대합니다. 연봉은 경력과 역량에 따라 협의 후 결정되며, 근무지는 서울 강남구입니다. 제출 서류로는 이력서, 자기소개서, 관련 자격증 사본이 필요합니다."
    
    print("🔍 특정 케이스 상세 분석")
    print(f"입력: {test_text}")
    print()
    
    result = classify_context(test_text)
    
    print(f"📊 분석 결과:")
    print(f"  - 총점: {result.total_score:.2f}")
    print(f"  - 채용 여부: {result.is_recruitment}")
    print(f"  - 신뢰도: {result.confidence:.2f}")
    print()
    
    print("📋 카테고리별 점수:")
    for category, score in result.category_scores.items():
        print(f"  - {category}: {score:.2f}")
    print()
    
    print("🎯 주요 지표:")
    for indicator in result.details['key_indicators']:
        print(f"  - {indicator}")
    print()
    
    print(f"📏 텍스트 정보:")
    print(f"  - 길이: {result.details['text_length']}자")
    print(f"  - 문장 수: {result.details['sentence_count']}개")

if __name__ == "__main__":
    print("🚀 맥락 분류기 테스트 시작\n")
    
    # 기본 테스트
    test_context_classifier()
    
    print("\n" + "="*80 + "\n")
    
    # 특정 케이스 상세 테스트
    test_specific_case()
