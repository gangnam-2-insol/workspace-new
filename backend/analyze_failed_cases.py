#!/usr/bin/env python3
"""
실패한 케이스 분석 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.core.context_classifier import classify_context, is_recruitment_text

def analyze_failed_cases():
    """실패한 케이스들 분석"""
    
    failed_cases = [
        # 실패한 케이스 1: 디지털 마케터
        {
            "text": "디지털 마케팅 전략을 수립하고 실행할 수 있는 마케팅 전문가를 찾고 있습니다. 온라인 광고, SNS 마케팅, 콘텐츠 마케팅 등 다양한 채널을 활용한 통합 마케팅 캠페인 경험이 있는 분을 우대합니다. 데이터 분석을 통한 마케팅 성과 측정 및 최적화 능력이 필요하며, 시장 트렌드를 파악하고 새로운 마케팅 기법을 도입하는 데 관심이 많은 분이면 좋겠습니다. Google Analytics, Facebook Ads 등 마케팅 툴 활용 경험이 필수입니다.",
            "expected": True,
            "description": "디지털 마케터 채용공고 (실패 케이스)"
        },
        
        # 실패한 케이스 2: 보안 전문가
        {
            "text": "정보보안 및 사이버 보안을 담당할 보안 전문가를 찾고 있습니다. 네트워크 보안, 애플리케이션 보안, 인프라 보안 등 다양한 영역의 보안 위험을 식별하고 대응할 수 있는 능력이 필요합니다. 보안 취약점 분석 및 침입 탐지 시스템 운영 경험이 있으시면 우대하며, 보안 정책 수립 및 보안 교육 진행 경험이 있는 분이면 좋겠습니다. CISSP, CEH 등 보안 관련 자격증 보유자 및 보안 사고 대응 경험이 필수입니다.",
            "expected": True,
            "description": "보안 전문가 채용공고 (실패 케이스)"
        }
    ]
    
    print("🔍 실패한 케이스 상세 분석\n")
    
    for i, test_case in enumerate(failed_cases, 1):
        print(f"📝 실패 케이스 {i}: {test_case['description']}")
        print(f"입력: {test_case['text']}")
        print()
        
        # 맥락 분류 실행
        result = classify_context(test_case['text'])
        
        print(f"📊 분석 결과:")
        print(f"  - 총점: {result.total_score:.2f}")
        print(f"  - 채용 여부: {result.is_recruitment}")
        print(f"  - 신뢰도: {result.confidence:.2f}")
        print()
        
        print("📋 카테고리별 점수:")
        for category, score in result.category_scores.items():
            if score > 0:
                print(f"  - {category}: {score:.2f}")
        print()
        
        print("🎯 주요 지표:")
        for indicator in result.details['key_indicators']:
            print(f"  - {indicator}")
        print()
        
        # 문제점 분석
        print("❌ 문제점 분석:")
        if result.total_score < 5.0:
            print(f"  - 총점이 너무 낮음: {result.total_score:.2f}점 (기준: 5.0점)")
        
        if result.category_scores.get("recruitment_intent", 0) == 0:
            print("  - 채용 의도 키워드가 감지되지 않음")
        
        if result.category_scores.get("application_process", 0) == 0:
            print("  - 제출 절차 키워드가 감지되지 않음")
        
        print("-" * 80)
        print()

def suggest_improvements():
    """개선 방안 제시"""
    
    print("💡 개선 방안 제시\n")
    
    improvements = [
        {
            "issue": "채용 의도 키워드 부족",
            "suggestion": "다양한 직무별 채용 키워드 추가",
            "examples": [
                "전문가를 찾고 있습니다",
                "전문가를 모집합니다", 
                "담당자를 찾고 있습니다",
                "담당자를 모집합니다"
            ]
        },
        {
            "issue": "제출 절차 키워드 부족",
            "suggestion": "직무별 필수 요건 키워드 추가",
            "examples": [
                "필수입니다",
                "필수 조건입니다",
                "우대합니다",
                "경험이 있으시면",
                "능력이 필요합니다"
            ]
        },
        {
            "issue": "문맥 패턴 부족",
            "suggestion": "더 다양한 문맥 패턴 추가",
            "examples": [
                r"([가-힣]+)\s*(전문가|담당자)\s*(을|를)\s*(찾고|모집)",
                r"([가-힣]+)\s*(경험이|능력이)\s*(필요|우대)",
                r"([가-힣]+)\s*(등|및)\s*([가-힣]+)\s*(활용|사용)\s*(경험이|능력이)"
            ]
        }
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"{i}. {improvement['issue']}")
        print(f"   제안: {improvement['suggestion']}")
        print(f"   예시: {improvement['examples']}")
        print()

def test_improved_keywords():
    """개선된 키워드로 테스트"""
    
    test_texts = [
        "마케팅 전문가를 찾고 있습니다. 다양한 경험이 필요합니다.",
        "보안 전문가를 모집합니다. 필수 조건이 있습니다.",
        "개발자를 찾고 있습니다. React 경험이 우대됩니다."
    ]
    
    print("🧪 개선된 키워드 테스트\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"테스트 {i}: {text}")
        result = classify_context(text)
        print(f"결과: 점수 {result.total_score:.2f}, 채용: {result.is_recruitment}")
        print(f"주요 카테고리: {[k for k, v in result.category_scores.items() if v > 0]}")
        print()

if __name__ == "__main__":
    print("🔍 실패한 케이스 분석 시작\n")
    
    # 실패한 케이스 분석
    analyze_failed_cases()
    
    # 개선 방안 제시
    suggest_improvements()
    
    # 개선된 키워드 테스트
    test_improved_keywords()
