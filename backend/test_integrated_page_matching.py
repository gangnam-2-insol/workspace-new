#!/usr/bin/env python3
"""
통합 페이지 매칭 테스트 스크립트
챗봇 시스템과 페이지 매칭이 제대로 통합되어 작동하는지 확인
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot', 'chatbot'))

from core.agent_system import agent_system

def test_integrated_page_matching():
    """통합 페이지 매칭 테스트"""
    
    test_cases = [
        # 페이지 네비게이션 테스트
        "채용공고 등록 페이지로 가고 싶어요",
        "지원자 관리 확인하기",
        "면접 일정 보기",
        "포트폴리오 분석 페이지",
        "설정 페이지로 이동",
        
        # 일반 대화 테스트 (페이지 매칭되지 않아야 함)
        "안녕하세요",
        "오늘 날씨는 어때요?",
        "도움말을 보여주세요",
        
        # 채용공고 등록 테스트 (기존 기능 유지)
        "React 개발자 1명 모집합니다. 연봉 4000만원, 경력 3년 이상",
        "Python 백엔드 개발자 구합니다. AWS 경험 필수",
    ]
    
    print("=" * 80)
    print("🎯 통합 페이지 매칭 시스템 테스트")
    print("=" * 80)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i:2d}. 테스트 입력: {test_input}")
        print("-" * 60)
        
        try:
            # Agent 시스템으로 요청 처리
            result = agent_system.process_request(
                user_input=test_input,
                mode="langgraph"  # LangGraph 모드에서 테스트
            )
            
            print(f"✅ 처리 성공")
            print(f"📊 의도: {result.get('intent', 'N/A')}")
            print(f"🎯 신뢰도: {result.get('confidence', 'N/A')}")
            
            # 페이지 네비게이션 의도인 경우
            if result.get('intent') == 'page_navigation':
                print(f"🎯 페이지 매칭 감지됨!")
                print(f"📍 페이지: {result.get('page_match', {}).get('page_name', 'N/A')}")
                print(f"🔗 경로: {result.get('page_match', {}).get('page_path', 'N/A')}")
                print(f"📝 이유: {result.get('page_match', {}).get('reason', 'N/A')}")
                
                # 응답 확인
                response_data = result.get('response', '')
                if response_data:
                    try:
                        response_json = json.loads(response_data)
                        if response_json.get('type') == 'page_navigation':
                            print(f"✅ 페이지 네비게이션 응답 생성됨")
                            print(f"📋 응답: {response_json.get('response', 'N/A')}")
                        else:
                            print(f"⚠️ 예상과 다른 응답 타입: {response_json.get('type', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON 파싱 실패: {response_data[:100]}...")
            
            # 채용공고 의도인 경우
            elif result.get('intent') == 'recruit':
                print(f"🎯 채용공고 의도 감지됨!")
                extracted_fields = result.get('extracted_fields', {})
                if extracted_fields:
                    print(f"📋 추출된 필드: {len(extracted_fields)}개")
                    for key, value in extracted_fields.items():
                        if value and value != "null":
                            print(f"   - {key}: {value}")
            
            # 일반 대화 의도인 경우
            elif result.get('intent') == 'chat':
                print(f"🎯 일반 대화 의도 감지됨")
                print(f"💬 응답: {result.get('response', 'N/A')[:100]}...")
            
            # 기타 의도
            else:
                print(f"🎯 기타 의도: {result.get('intent', 'N/A')}")
                print(f"💬 응답: {result.get('response', 'N/A')[:100]}...")
            
        except Exception as e:
            print(f"❌ 처리 실패: {str(e)}")
        
        print("-" * 60)
    
    print("\n" + "=" * 80)
    print("🎯 테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    test_integrated_page_matching()
