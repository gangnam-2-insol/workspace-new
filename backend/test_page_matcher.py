#!/usr/bin/env python3
"""
페이지 매칭 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'chatbot', 'chatbot'))

from core.page_matcher import page_matcher

def test_page_matching():
    """페이지 매칭 테스트"""
    
    test_cases = [
        # 대시보드 관련
        "대시보드로 가고 싶어요",
        "홈으로 돌아가기",
        "메인 페이지 보여줘",
        
        # 채용공고 관련
        "채용공고 등록하고 싶어요",
        "구인 공고 올리기",
        "채용 모집 공고 작성",
        
        # AI 채용공고 등록
        "AI로 채용공고 등록하기",
        "인공지능 도우미 사용해서 공고 올리기",
        "스마트 채용공고 등록",
        
        # 이력서 관리
        "이력서 관리 페이지",
        "CV 확인하기",
        "지원자 경력 보기",
        
        # 지원자 관리
        "지원자 목록 확인",
        "후보자 관리",
        "지원자 정보 보기",
        
        # 면접 관리
        "면접 일정 확인",
        "인터뷰 스케줄 보기",
        "면접 캘린더",
        
        # 포트폴리오 분석
        "포트폴리오 분석하기",
        "프로젝트 확인",
        "깃허브 코드 보기",
        
        # 자기소개서 검증
        "자기소개서 검증",
        "자소서 확인",
        "지원 동기 확인",
        
        # 인재 추천
        "적합한 인재 추천받기",
        "매칭되는 후보 찾기",
        "추천 인재 확인",
        
        # 사용자 관리
        "사용자 관리",
        "계정 관리",
        "관리자 권한",
        
        # 설정
        "설정 페이지",
        "환경설정",
        "프로필 설정",
        
        # PDF OCR
        "PDF 문서 처리",
        "OCR로 텍스트 추출",
        "문서 스캔하기",
        
        # 깃허브 테스트
        "깃허브 테스트",
        "GitHub 실험",
        
        # 일반 대화 (매칭되지 않아야 함)
        "안녕하세요",
        "오늘 날씨 어때요?",
        "도움말 보여줘"
    ]
    
    print("=" * 60)
    print("🎯 페이지 매칭 시스템 테스트")
    print("=" * 60)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i:2d}. 테스트 입력: {test_input}")
        
        # 페이지 매칭 시도
        page_match = page_matcher.match_page(test_input)
        
        if page_match:
            print(f"    ✅ 매칭됨: {page_match.page_name}")
            print(f"    📍 경로: {page_match.page_path}")
            print(f"    🎯 신뢰도: {page_match.confidence:.1%}")
            print(f"    📝 이유: {page_match.reason}")
            print(f"    🔧 액션: {page_match.action_type}")
            
            if page_match.additional_data:
                print(f"    📊 추가 데이터: {page_match.additional_data}")
        else:
            print(f"    ❌ 매칭되지 않음")
            
            # 제안 페이지 확인
            suggestions = page_matcher.suggest_pages(test_input)
            if suggestions:
                print(f"    💡 제안 페이지:")
                for suggestion in suggestions[:2]:
                    print(f"       - {suggestion.page_name} ({suggestion.confidence:.1%})")
    
    print("\n" + "=" * 60)
    print("🎯 사용 가능한 페이지 목록")
    print("=" * 60)
    
    available_pages = page_matcher.get_available_pages()
    for page in available_pages:
        print(f"📄 {page['name']} ({page['id']})")
        print(f"    경로: {page['path']}")
        print(f"    설명: {page['description']}")
        print()

if __name__ == "__main__":
    test_page_matching()
