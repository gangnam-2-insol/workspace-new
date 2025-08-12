#!/usr/bin/env python3
"""
Agent 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_system import agent_system

def test_agent_system():
    """Agent 시스템을 테스트합니다."""
    
    test_cases = [
        {
            "input": "최신 개발 트렌드 알려줘",
            "expected_intent": "search",
            "description": "검색 요청 테스트"
        },
        {
            "input": "연봉 4000만원의 월급",
            "expected_intent": "calc",
            "description": "계산 요청 테스트"
        },
        {
            "input": "저장된 채용공고 보여줘",
            "expected_intent": "db",
            "description": "DB 조회 요청 테스트"
        },
        {
            "input": "안녕하세요",
            "expected_intent": "chat",
            "description": "일반 대화 테스트"
        },
        {
            "input": "2+2는?",
            "expected_intent": "calc",
            "description": "수식 계산 테스트"
        },
        {
            "input": "채용 동향 정보",
            "expected_intent": "search",
            "description": "채용 검색 테스트"
        },
        {
            "input": "개발자 뽑아요",
            "expected_intent": "recruit",
            "description": "채용공고 작성 테스트"
        },
        {
            "input": "프론트엔드 개발자 채용공고 작성해줘",
            "expected_intent": "recruit",
            "description": "구체적 채용공고 작성 테스트"
        }
    ]
    
    print("🧪 Agent 시스템 테스트 시작\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"테스트 {i}: {test_case['description']}")
        print(f"입력: {test_case['input']}")
        
        try:
            result = agent_system.process_request(test_case['input'])
            
            print(f"의도: {result['intent']} (예상: {test_case['expected_intent']})")
            print(f"성공: {result['success']}")
            
            if result['success']:
                print("응답:")
                print(result['response'][:200] + "..." if len(result['response']) > 200 else result['response'])
            else:
                print(f"오류: {result['error']}")
                
        except Exception as e:
            print(f"테스트 실패: {str(e)}")
        
        print("-" * 50)
    
    print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_agent_system()
