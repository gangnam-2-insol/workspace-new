from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
import logging

from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.config import Settings
from pdf_ocr_module.ai_analyzer import analyze_text

router = APIRouter()

@router.post("/upload-pdf")
async def upload_and_process_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    PDF 파일을 업로드하고 OCR 처리를 수행합니다.
    """
    try:
        # 파일 확장자 검증
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # PDF 처리
            result = process_pdf(temp_file_path)
            
            # AI 분석 결과 가져오기
            settings = Settings()
            ai_analysis = analyze_text(result.get("full_text", ""), settings)
            
            # 결과에서 필요한 정보만 추출
            processed_result = {
                "success": True,
                "filename": file.filename,
                "extracted_text": result.get("full_text", ""),  # full_text 사용
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "pages": result.get("num_pages", 0),
                "document_id": result.get("mongo_id", ""),
                "processing_time": 0,
                # AI 분석 결과 추가
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "general"),
                "sections": ai_analysis.get("structured_data", {}).get("sections", {}),
                "entities": ai_analysis.get("structured_data", {}).get("entities", {}),
                "basic_info": ai_analysis.get("basic_info", {})
            }
            
            return JSONResponse(content=processed_result)
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logging.error(f"PDF 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 처리 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """
    PDF OCR 서비스 상태 확인
    """
    return {"status": "healthy", "service": "pdf_ocr"}

