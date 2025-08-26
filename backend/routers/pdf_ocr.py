import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pdf_ocr_module import PDFProcessor, Settings

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
            # PDFProcessor 초기화 및 처리
            settings = Settings()
            processor = PDFProcessor(settings)
            result = processor.process_pdf(temp_file_path)

            # 결과에서 필요한 정보만 추출
            processed_result = {
                "success": True,
                "filename": file.filename,
                "extracted_text": result.get("full_text", ""),
                "summary": result.get("ai_analysis", {}).get("summary", ""),
                "keywords": result.get("ai_analysis", {}).get("keywords", []),
                "pages": result.get("num_pages", 0),
                "document_id": result.get("document_id", ""),
                "processing_time": result.get("processing_time", 0),
                # AI 분석 결과 추가
                "document_type": result.get("ai_analysis", {}).get("structured_data", {}).get("document_type", "general"),
                "sections": result.get("ai_analysis", {}).get("structured_data", {}).get("sections", {}),
                "entities": result.get("ai_analysis", {}).get("structured_data", {}).get("entities", {}),
                "basic_info": result.get("ai_analysis", {}).get("basic_info", {})
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

@router.get("/stats")
async def get_processing_stats():
    """
    처리 통계 조회
    """
    try:
        settings = Settings()
        processor = PDFProcessor(settings)
        stats = processor.get_processing_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logging.error(f"통계 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

