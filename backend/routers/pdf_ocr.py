# backend/routers/pdf_ocr.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
import tempfile
import traceback
import logging
import time
import os

from bson import ObjectId
from pymongo import MongoClient

from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.config import Settings
from pdf_ocr_module.ai_analyzer import analyze_text

# main.py에서 prefix="/api/pdf-ocr"로 include 하므로 여기서는 prefix 없음
router = APIRouter(tags=["pdf-ocr"])

def _err(detail: str, exc: Exception | None = None) -> HTTPException:
    if exc is not None:
        logging.getLogger(__name__).error("%s\n%s", detail, traceback.format_exc())
        return HTTPException(status_code=500, detail=f"{detail}: {exc}")
    return HTTPException(status_code=500, detail=detail)

@router.post("/upload-pdf")
async def upload_and_process_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    PDF 파일 업로드 → OCR → AI 분석
    프론트 호출 경로: POST /api/pdf-ocr/upload-pdf
    """
    t0 = time.time()
    try:
        # 0) 확장자 검증
        if not (file and file.filename and file.filename.lower().endswith(".pdf")):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

        # 1) 임시 파일 저장
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_pdf_path = temp_file.name
        except Exception as io_err:
            raise _err("임시 파일 저장 실패", io_err)

        try:
            # 2) OCR 파이프라인
            try:
                ocr_result = await process_pdf(temp_pdf_path)
            except Exception as ocr_err:
                raise _err("process_pdf 실행 실패", ocr_err)

            logging.info("PDF 처리 완료: %s", ocr_result)

            # 3) AI 분석
            try:
                settings = Settings()
            except Exception as cfg_err:
                raise _err("Settings 로딩 실패", cfg_err)

            try:
                extracted_text = ocr_result.get("full_text", "") or ""
                ai_analysis = await analyze_text(extracted_text, settings)
            except Exception as ai_err:
                raise _err("analyze_text 실행 실패", ai_err)

            # 4) 응답
            processing_time = round(time.time() - t0, 3)
            payload: Dict[str, Any] = {
                "success": True,
                "filename": file.filename,
                "extracted_text": extracted_text,
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "pages": ocr_result.get("num_pages", 0),
                "document_id": ocr_result.get("mongo_id", ""),
                "hireme_id": ocr_result.get("hireme_id", ""),
                "processing_time": processing_time,
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "general"),
                "sections": ai_analysis.get("structured_data", {}).get("sections", {}),
                "entities": ai_analysis.get("structured_data", {}).get("entities", {}),
                "basic_info": ai_analysis.get("basic_info", {}),
                "fields": ocr_result.get("fields", {}),
            }
            return JSONResponse(content=payload)

        finally:
            # 5) 임시 파일 정리
            try:
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            except Exception:
                logging.getLogger(__name__).warning("임시 파일 삭제 실패: %s", temp_pdf_path)

    except HTTPException:
        raise
    except Exception as e:
        logging.getLogger(__name__).error("upload_and_process_pdf 실패: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"upload_pdf failed: {e}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf_ocr", "now": datetime.utcnow().isoformat()}

@router.put("/update-applicant/{hireme_id}")
async def update_applicant_info(hireme_id: str, applicant_data: Dict[str, Any]):
    """
    프론트에서 보낸 지원자 정보를 DB에 업데이트
    """
    try:
        settings = Settings()
        client = MongoClient(settings.mongodb_uri)
        try:
            db = client["hireme"]
            applicants = db["applicants"]

            update_data = {
                "name": applicant_data.get("name", ""),
                "email": applicant_data.get("email", ""),
                "phone": applicant_data.get("phone", ""),
                "position": applicant_data.get("position", ""),
                "company": applicant_data.get("company", ""),
                "education": applicant_data.get("education", ""),
                "skills": applicant_data.get("skills", []),
                "address": applicant_data.get("address", ""),
                "updated_at": datetime.utcnow(),
            }
            update_data = {k: v for k, v in update_data.items() if v not in ("", [], None)}

            result = applicants.update_one({"_id": ObjectId(hireme_id)}, {"$set": update_data})
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")

            return JSONResponse(content={
                "success": True,
                "message": "지원자 정보가 성공적으로 업데이트되었습니다.",
                "updated_fields": list(update_data.keys())
            })
        finally:
            client.close()
    except HTTPException:
        raise
    except Exception as e:
        logging.getLogger(__name__).error("지원자 정보 업데이트 실패: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {e}")

@router.get("/applicant/{hireme_id}")
async def get_applicant_info(hireme_id: str):
    """
    특정 지원자 정보 조회
    """
    try:
        settings = Settings()
        client = MongoClient(settings.mongodb_uri)
        try:
            db = client["hireme"]
            applicants = db["applicants"]
            doc = applicants.find_one({"_id": ObjectId(hireme_id)})
            if not doc:
                raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
            doc["_id"] = str(doc["_id"])
            return JSONResponse(content={"success": True, "applicant": doc})
        finally:
            client.close()
    except HTTPException:
        raise
    except Exception as e:
        logging.getLogger(__name__).error("지원자 정보 조회 실패: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"조회 실패: {e}")
