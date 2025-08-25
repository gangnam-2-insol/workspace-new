#!/usr/bin/env python3
"""
PDF OCR 모듈 테스트 스크립트
"""

import logging
import os
import sys
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_pdf_ocr_module():
    """PDF OCR 모듈을 테스트합니다."""

    try:
        # PDF OCR 모듈 import
        from pdf_ocr_module import PDFProcessor, Settings

        print("✅ PDF OCR 모듈 import 성공")

        # 설정 초기화
        settings = Settings()
        print(f"📋 설정 로드 완료:")
        print(f"   - OCR 언어: {settings.ocr_language}")
        print(f"   - DPI: {settings.dpi}")
        print(f"   - Tesseract 경로: {settings.tesseract_path}")
        print(f"   - Poppler 경로: {settings.poppler_path}")

        # PDFProcessor 초기화
        processor = PDFProcessor(settings)
        print("✅ PDFProcessor 초기화 완료")

        # 테스트 PDF 파일 경로
        pdf_path = Path("../신입 경력 이력서.pdf")

        if not pdf_path.exists():
            print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
            return False

        print(f"📄 PDF 파일 발견: {pdf_path}")
        print(f"📄 파일 크기: {pdf_path.stat().st_size:,} bytes")

        # PDF 처리 시작
        print("\n🔄 PDF 처리 시작...")
        result = processor.process_pdf(pdf_path)

        # 결과 출력
        print("\n📊 처리 결과:")
        print(f"   - 문서 ID: {result.get('document_id', 'N/A')}")
        print(f"   - 파일명: {result.get('filename', 'N/A')}")
        print(f"   - 페이지 수: {result.get('num_pages', 0)}")
        print(f"   - 처리 시간: {result.get('processing_time', 0):.2f}초")

        # 텍스트 추출 결과
        full_text = result.get('full_text', '')
        print(f"\n📝 추출된 텍스트 길이: {len(full_text):,} 문자")
        print(f"📝 텍스트 미리보기 (처음 500자):")
        print("-" * 50)
        print(full_text[:500] + "..." if len(full_text) > 500 else full_text)
        print("-" * 50)

        # AI 분석 결과
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis:
            print(f"\n🤖 AI 분석 결과:")
            print(f"   - 문서 유형: {ai_analysis.get('structured_data', {}).get('document_type', 'N/A')}")
            print(f"   - 요약: {ai_analysis.get('summary', 'N/A')[:100]}...")
            print(f"   - 키워드: {ai_analysis.get('keywords', [])[:5]}")

            # 기본 정보
            basic_info = ai_analysis.get('basic_info', {})
            print(f"   - 단어 수: {basic_info.get('word_count', 0):,}")
            print(f"   - 문장 수: {basic_info.get('sentence_count', 0):,}")
            print(f"   - 단락 수: {basic_info.get('paragraph_count', 0):,}")

            # 엔티티 추출
            entities = ai_analysis.get('structured_data', {}).get('entities', {})
            if entities:
                print(f"   - 이메일: {entities.get('emails', [])}")
                print(f"   - 전화번호: {entities.get('phones', [])}")
                print(f"   - 회사명: {entities.get('companies', [])}")

        # OCR 결과
        ocr_results = result.get('ocr_results', [])
        if ocr_results:
            print(f"\n🔍 OCR 결과:")
            for i, ocr_result in enumerate(ocr_results):
                confidence = ocr_result.get('result', {}).get('confidence', 0)
                print(f"   - 페이지 {i+1}: 신뢰도 {confidence:.2f}")

        # 레이아웃 데이터
        layout_data = result.get('layout_data', {})
        if layout_data:
            pages = layout_data.get('pages', [])
            print(f"\n📐 레이아웃 데이터:")
            print(f"   - 페이지 수: {len(pages)}")
            for i, page in enumerate(pages):
                spans = page.get('spans', [])
                print(f"   - 페이지 {i+1}: {len(spans)}개 텍스트 스팬")

        print("\n✅ PDF OCR 모듈 테스트 완료!")
        return True

    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """개별 컴포넌트들을 테스트합니다."""

    try:
        from pdf_ocr_module import AIAnalyzer, OCREngine, Settings, TextExtractor

        print("\n🔧 개별 컴포넌트 테스트 시작...")

        settings = Settings()

        # TextExtractor 테스트
        print("\n📖 TextExtractor 테스트:")
        text_extractor = TextExtractor()
        pdf_path = Path("../신입 경력 이력서.pdf")

        if pdf_path.exists():
            try:
                # 페이지 수 확인
                page_count = text_extractor.get_page_count(pdf_path)
                print(f"   - 페이지 수: {page_count}")

                # 메타데이터 추출
                metadata = text_extractor.extract_metadata(pdf_path)
                print(f"   - 파일명: {metadata.get('filename')}")
                print(f"   - 파일 크기: {metadata.get('file_size'):,} bytes")
                print(f"   - 제목: {metadata.get('title', 'N/A')}")
                print(f"   - 작성자: {metadata.get('author', 'N/A')}")

            except Exception as e:
                print(f"   - TextExtractor 테스트 실패: {e}")

        # AIAnalyzer 테스트
        print("\n🤖 AIAnalyzer 테스트:")
        ai_analyzer = AIAnalyzer(settings)

        test_text = "안녕하세요. 저는 김철수입니다. Python과 JavaScript 개발 경험이 있습니다."
        analysis = ai_analyzer.analyze_text(test_text)

        print(f"   - 문서 유형: {analysis.get('structured_data', {}).get('document_type', 'N/A')}")
        print(f"   - 키워드: {analysis.get('keywords', [])}")
        print(f"   - 요약: {analysis.get('summary', 'N/A')}")

        print("\n✅ 개별 컴포넌트 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 개별 컴포넌트 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 PDF OCR 모듈 테스트 시작")
    print("=" * 50)

    # 메인 테스트
    success1 = test_pdf_ocr_module()

    # 개별 컴포넌트 테스트
    success2 = test_individual_components()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")

    print("테스트 완료!")
