#!/usr/bin/env python3
"""
OpenAI OCR 기능 테스트 스크립트
"""

import asyncio
import os
from pathlib import Path
from PIL import Image
from pdf_ocr_module.ocr_engine import ocr_images_with_openai
from pdf_ocr_module.config import Settings

async def test_openai_ocr():
    """OpenAI OCR 기능을 테스트합니다."""
    
    # 설정 로드
    settings = Settings()
    
    # 테스트 이미지 경로 (실제 이미지 파일이 필요)
    test_image_path = Path("test_image.png")
    
    if not test_image_path.exists():
        print("❌ 테스트 이미지가 없습니다. test_image.png 파일을 생성해주세요.")
        return
    
    print("🔍 OpenAI OCR 테스트 시작...")
    print(f"📁 테스트 이미지: {test_image_path}")
    
    try:
        # OpenAI OCR 실행
        results = await ocr_images_with_openai([test_image_path], settings)
        
        print("\n✅ OCR 결과:")
        for i, result in enumerate(results):
            print(f"\n--- 페이지 {i+1} ---")
            print(f"프로바이더: {result['result']['provider']}")
            print(f"모델: {result['result']['model']}")
            print(f"품질: {result['result']['quality']}")
            print(f"추출된 텍스트:\n{result['result']['text']}")
            
    except Exception as e:
        print(f"❌ OCR 테스트 실패: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openai_ocr())

