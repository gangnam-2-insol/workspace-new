#!/usr/bin/env python3
"""
OCR 처리와 지원자 정보 추출 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.ai_analyzer import analyze_text
from pdf_ocr_module.config import Settings
from routers.integrated_ocr import _build_applicant_data

def test_ocr_extraction(pdf_path: str):
    """PDF 파일의 OCR 처리와 정보 추출을 테스트합니다."""
    
    print(f"🔍 PDF 파일 테스트: {pdf_path}")
    print("=" * 50)
    
    try:
        # 1. PDF OCR 처리
        print("1단계: PDF OCR 처리 중...")
        ocr_result = process_pdf(pdf_path)
        print(f"✅ OCR 완료 - 페이지 수: {ocr_result.get('num_pages', 0)}")
        
        # 2. AI 분석
        print("\n2단계: AI 분석 중...")
        settings = Settings()
        ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
        print(f"✅ AI 분석 완료")
        
        # 3. OCR 결과에 AI 분석 결과 추가
        enhanced_ocr_result = {
            "extracted_text": ocr_result.get("full_text", ""),
            "summary": ai_analysis.get("summary", ""),
            "keywords": ai_analysis.get("keywords", []),
            "basic_info": ai_analysis.get("basic_info", {}),
            "document_type": ai_analysis.get("structured_data", {}).get("document_type", "resume"),
            "pages": ocr_result.get("num_pages", 0)
        }
        
        # 4. 지원자 데이터 생성 테스트
        print("\n3단계: 지원자 정보 추출 테스트...")
        applicant_data = _build_applicant_data(
            name=None,  # Form 입력 없음
            email=None,  # Form 입력 없음
            phone=None,  # Form 입력 없음
            ocr_result=enhanced_ocr_result
        )
        
        # 5. 결과 출력
        print("\n" + "=" * 50)
        print("📊 최종 결과:")
        print(f"  - 이름: {applicant_data.name}")
        print(f"  - 이메일: {applicant_data.email}")
        print(f"  - 전화번호: {applicant_data.phone}")
        print(f"  - 직무: {applicant_data.position}")
        print(f"  - 부서: {applicant_data.department}")
        print(f"  - 경력: {applicant_data.experience}")
        print(f"  - 기술 스택: {applicant_data.skills}")
        print(f"  - 성장 배경: {applicant_data.growthBackground[:100]}...")
        print(f"  - 지원 동기: {applicant_data.motivation}")
        print(f"  - 경력 사항: {applicant_data.careerHistory[:100]}...")
        print(f"  - 분석 점수: {applicant_data.analysisScore}")
        print(f"  - 분석 결과: {applicant_data.analysisResult}")
        print(f"  - 상태: {applicant_data.status}")
        
        print(f"\n📋 AI 분석 결과:")
        print(f"  - basic_info: {ai_analysis.get('basic_info', {})}")
        print(f"  - structured_data: {ai_analysis.get('structured_data', {}).get('basic_info', {})}")
        
        print(f"\n📄 OCR 텍스트 (처음 200자):")
        text_preview = ocr_result.get("full_text", "")[:200]
        print(f"  {text_preview}...")
        
        return applicant_data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python test_ocr_extraction.py <PDF_파일_경로>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)
    
    result = test_ocr_extraction(pdf_path)
    
    if result:
        print(f"\n🎉 테스트 완료! 추출된 지원자: {result.name}")
        print(f"📝 CSV 포맷과 동일한 구조로 데이터가 생성되었습니다.")
    else:
        print(f"\n❌ 테스트 실패")
        sys.exit(1)
