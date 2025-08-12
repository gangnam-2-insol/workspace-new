#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
의도 감지 로직 테스트 스크립트
"""

from chatbot.core.agent_system import IntentDetectionNode

def test_intent_detection():
    """의도 감지 테스트"""
    
    # 테스트할 문장들
    test_cases = [
        {
            "text": "저희 회사는 성장 가능성이 높은 스타트업으로서, 경력 3년 이상의 백엔드 개발자를 모집하고 있습니다. 주로 Python과 Django 프레임워크를 사용하며, 대규모 트래픽 처리 경험이 있는 분을 환영합니다. 팀원들과 원활한 소통이 가능하며, 문제 해결에 적극적인 태도를 가진 인재를 찾고 있습니다. 적극적인 자기 개발 의지와 새로운 기술 습득에 열정이 있는 분을 우대합니다. 지원 시 포트폴리오와 Github 링크를 함께 제출해 주세요.",
            "expected": "recruit",
            "description": "채용공고 문장 (제출 키워드 포함)"
        },
        {
            "text": "안녕하세요, 도움을 요청합니다.",
            "expected": "chat",
            "description": "일반 대화"
        },
        {
            "text": "작성해줘",
            "expected": "chat",
            "description": "강력 키워드만 있는 경우"
        }
    ]
    
    # IntentDetectionNode 초기화
    intent_detector = IntentDetectionNode()
    
    print("🧪 의도 감지 테스트 시작\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 테스트 케이스 {i}: {test_case['description']}")
        print(f"입력: {test_case['text'][:50]}...")
        
        try:
            # 의도 감지 실행
            detected_intent = intent_detector.detect_intent(test_case['text'])
            
            # 결과 확인
            is_correct = detected_intent == test_case['expected']
            status = "✅ PASS" if is_correct else "❌ FAIL"
            
            print(f"예상 결과: {test_case['expected']}")
            print(f"실제 결과: {detected_intent}")
            print(f"결과: {status}")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        print("-" * 80)
    
    print("🧪 테스트 완료")

if __name__ == "__main__":
    test_intent_detection()
