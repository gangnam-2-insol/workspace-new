from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime
from bson import ObjectId

from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.config import Settings
from pdf_ocr_module.ai_analyzer import analyze_text
from pdf_ocr_module.storage import save_to_hireme_applicants

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
            result = await process_pdf(temp_file_path)
            logging.info(f"PDF 처리 완료: {result}")
            
            # AI 분석 결과 가져오기
            settings = Settings()
            ai_analysis = await analyze_text(result.get("full_text", ""), settings)
            
            # 결과에서 필요한 정보만 추출
            processed_result = {
                "success": True,
                "filename": file.filename,
                "extracted_text": result.get("full_text", ""),  # full_text 사용
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "pages": result.get("num_pages", 0),
                "document_id": result.get("mongo_id", ""),
                "hireme_id": result.get("hireme_id", ""),  # Hireme DB ID
                "processing_time": 0,
                # AI 분석 결과 추가
                "document_type": ai_analysis.get("structured_data", {}).get("document_type", "general"),
                "sections": ai_analysis.get("structured_data", {}).get("sections", {}),
                "entities": ai_analysis.get("structured_data", {}).get("entities", {}),
                "basic_info": ai_analysis.get("basic_info", {}),
                "fields": result.get("fields", {})  # 추출된 필드 정보 추가
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


@router.put("/update-applicant/{hireme_id}")
async def update_applicant_info(hireme_id: str, applicant_data: Dict[str, Any]):
    """
    프론트엔드에서 수정된 지원자 정보를 DB에 업데이트합니다.
    """
    try:
        from pymongo import MongoClient
        settings = Settings()
        client = MongoClient(settings.mongodb_uri)
        
        try:
            # hireme DB의 applicants 컬렉션에 연결
            db = client["Hireme"]
            applicants_collection = db["applicants"]
            
            # 업데이트할 데이터 준비
            update_data = {
                "name": applicant_data.get("name", ""),
                "email": applicant_data.get("email", ""),
                "phone": applicant_data.get("phone", ""),
                "position": applicant_data.get("position", ""),
                "company": applicant_data.get("company", ""),
                "education": applicant_data.get("education", ""),
                "skills": applicant_data.get("skills", []),
                "address": applicant_data.get("address", ""),
                "updated_at": datetime.utcnow()
            }
            
            # 빈 값 제거
            update_data = {k: v for k, v in update_data.items() if v}
            
            # DB 업데이트
            result = applicants_collection.update_one(
                {"_id": ObjectId(hireme_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
            
            return JSONResponse(content={
                "success": True,
                "message": "지원자 정보가 성공적으로 업데이트되었습니다.",
                "updated_fields": list(update_data.keys())
            })
            
        finally:
            client.close()
            
    except Exception as e:
        logging.error(f"지원자 정보 업데이트 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {str(e)}")


@router.get("/applicant/{hireme_id}")
async def get_applicant_info(hireme_id: str):
    """
    특정 지원자의 정보를 조회합니다.
    """
    try:
        from pymongo import MongoClient
        settings = Settings()
        client = MongoClient(settings.mongodb_uri)
        
        try:
            # hireme DB의 applicants 컬렉션에 연결
            db = client["Hireme"]
            applicants_collection = db["applicants"]
            
            # 지원자 정보 조회
            applicant = applicants_collection.find_one({"_id": ObjectId(hireme_id)})
            
            if not applicant:
                raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")
            
            # ObjectId를 문자열로 변환
            applicant["_id"] = str(applicant["_id"])
            
            return JSONResponse(content={
                "success": True,
                "applicant": applicant
            })
            
        finally:
            client.close()
            
    except Exception as e:
        logging.error(f"지원자 정보 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

