#!/usr/bin/env python3
"""
Gemini API 응답 디버깅 테스트
"""

import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

async def test_gemini_direct():
    """Gemini API 직접 테스트"""
    print("🔍 Gemini API 직접 테스트 시작...")
    
    # API 키 확인
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY가 설정되지 않았습니다.")
        return
    
    print(f"✅ API 키 확인됨: {api_key[:10]}...")
    
    try:
        # Gemini 설정
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ Gemini 모델 설정 완료")
        
        # 간단한 테스트 프롬프트
        test_prompt = """
간단한 JSON을 생성해주세요:
{
  "test": "hello",
  "number": 42
}
"""
        
        print(f"📝 테스트 프롬프트 전송: {test_prompt}")
        
        # API 호출
        response = await asyncio.to_thread(
            model.generate_content,
            test_prompt
        )
        
        print(f"📥 응답 타입: {type(response)}")
        print(f"📥 응답 텍스트: {response.text}")
        print(f"📥 응답 길이: {len(response.text) if response.text else 0}")
        
        if response.text and response.text.strip():
            # JSON 파싱 테스트
            import json
            try:
                parsed = json.loads(response.text.strip())
                print(f"✅ JSON 파싱 성공: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                print(f"응답 내용: {repr(response.text)}")
        else:
            print("❌ 빈 응답을 받았습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

async def test_analysis_prompt():
    """실제 분석 프롬프트 테스트"""
    print("\n🔍 실제 분석 프롬프트 테스트...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY가 설정되지 않았습니다.")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 실제 분석 프롬프트
        analysis_prompt = """
[ROLE] 당신은 채용담당자입니다. 입력된 문서(resume)를 아래 기준에 따라 분석하고 점수화해야 합니다.

[분석 기준]
- 각 항목은 0~10점으로 평가 (10점 = 매우 우수, 0점 = 전혀 충족하지 않음)
- 각 항목별로 개선이 필요한 부분을 간단히 피드백으로 작성
- 점수와 피드백은 JSON 형식으로 출력

[이력서 분석 기준]
1. basic_info_completeness (이름, 연락처, 이메일, GitHub/LinkedIn 여부)
2. job_relevance (직무 적합성)

[출력 형식]
아래 JSON 스키마에 맞춰 출력:
{
  "resume_analysis": {
    "basic_info_completeness": {"score": 0, "feedback": ""},
    "job_relevance": {"score": 0, "feedback": ""}
  },
  "cover_letter_analysis": {},
  "portfolio_analysis": {},
  "overall_summary": {
    "total_score": 0,
    "recommendation": ""
  }
}

[입력 문서]
안녕하세요. 저는 3년간의 웹 개발 경험을 바탕으로 귀사에 프론트엔드 개발자로 지원하게 된 김개발입니다.

[요구사항]
- 점수는 반드시 0~10 정수
- feedback은 간단하고 구체적으로 작성
- JSON만 출력
"""
        
        print("📝 분석 프롬프트 전송 중...")
        
        response = await asyncio.to_thread(
            model.generate_content,
            analysis_prompt
        )
        
        print(f"📥 응답 길이: {len(response.text) if response.text else 0}")
        print(f"📥 응답 내용 (처음 500자): {response.text[:500] if response.text else 'None'}")
        
        if response.text and response.text.strip():
            # JSON 파싱 테스트
            import json
            try:
                parsed = json.loads(response.text.strip())
                print(f"✅ JSON 파싱 성공!")
                print(f"✅ 응답 구조: {list(parsed.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                print(f"응답 내용: {repr(response.text)}")
        else:
            print("❌ 빈 응답을 받았습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Gemini API 디버깅 테스트 시작...\n")
    
    # 1. 간단한 테스트
    asyncio.run(test_gemini_direct())
    
    # 2. 실제 분석 프롬프트 테스트
    asyncio.run(test_analysis_prompt())
    
    print("\n🎉 디버깅 테스트 완료!")
