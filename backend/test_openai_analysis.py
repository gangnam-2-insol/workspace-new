#!/usr/bin/env python3
"""
OpenAI 분석 기능 테스트 스크립트
"""

import asyncio
import os
from pdf_ocr_module.ai_analyzer import analyze_text, extract_basic_info
from pdf_ocr_module.config import Settings

async def test_openai_analysis():
    """OpenAI 분석 기능을 테스트합니다."""
    
    # 설정 로드
    settings = Settings()
    
    # 테스트 텍스트 (이력서 예시)
    test_text = """
    김철수
    Frontend Developer
    
    연락처
    이메일: kim@example.com
    전화번호: 010-1234-5678
    
    경력
    2020-2023 ABC 회사
    - React, TypeScript를 사용한 웹 애플리케이션 개발
    - 사용자 인터페이스 설계 및 구현
    - 성능 최적화 및 코드 리팩토링
    
    기술 스킬
    - Frontend: React, Vue.js, TypeScript, JavaScript
    - Backend: Node.js, Express
    - Database: MongoDB, MySQL
    - Tools: Git, Docker, AWS
    
    학력
    2016-2020 서울대학교 컴퓨터공학과 졸업
    """
    
    print("🔍 OpenAI 분석 테스트 시작...")
    print(f"📝 테스트 텍스트 길이: {len(test_text)} 문자")
    
    try:
        # 기본 정보 추출 테스트
        print("\n1️⃣ 기본 정보 추출 테스트:")
        basic_info = await extract_basic_info(test_text)
        print(f"이름: {basic_info.get('names', [])}")
        print(f"이메일: {basic_info.get('emails', [])}")
        print(f"전화번호: {basic_info.get('phones', [])}")
        print(f"직책: {basic_info.get('positions', [])}")
        print(f"회사: {basic_info.get('companies', [])}")
        print(f"학력: {basic_info.get('education', [])}")
        print(f"스킬: {basic_info.get('skills', [])}")
        
        # 전체 분석 테스트
        print("\n2️⃣ 전체 분석 테스트:")
        analysis = await analyze_text(test_text, settings)
        print(f"요약: {analysis.get('summary', '')}")
        print(f"키워드: {analysis.get('keywords', [])}")
        print(f"구조화된 데이터: {analysis.get('structured_data', {})}")
        
    except Exception as e:
        print(f"❌ 분석 테스트 실패: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openai_analysis())

