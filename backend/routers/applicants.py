from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import asyncio

from models import Applicant, StatusUpdate, StatsResponse
from database import applicants_collection
from pymongo import MongoClient
import os
from pymongo import MongoClient
import os

router = APIRouter(prefix="/api/applicants", tags=["applicants"])

# 캐시 (실제 프로덕션에서는 Redis 사용 권장)
_applicants_cache = {}
_cache_timeout = 300  # 5분

@router.get("/", response_model=List[Applicant])
async def get_applicants(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(50, ge=1, le=100, description="가져올 항목 수"),
    status: Optional[str] = Query(None, description="상태 필터"),
    position: Optional[str] = Query(None, description="직무 필터")
):
    """지원자 목록 조회 (페이지네이션 지원)"""
    try:
        # 캐시 키 생성
        cache_key = f"applicants_{skip}_{limit}_{status}_{position}"
        
        # 캐시 확인
        if cache_key in _applicants_cache:
            cache_time, cache_data = _applicants_cache[cache_key]
            if (datetime.now() - cache_time).seconds < _cache_timeout:
                return cache_data
        
        # 쿼리 조건 구성
        query = {}
        if status:
            query["status"] = status
        if position:
            query["position"] = {"$regex": position, "$options": "i"}
        
        def _normalize(doc: dict) -> dict:
            if not isinstance(doc, dict):
                return doc
            # ObjectId → str for alias _id
            try:
                if doc.get("_id") is not None and not isinstance(doc["_id"], str):
                    doc["_id"] = str(doc["_id"])  # pydantic alias field expects a string
            except Exception:
                pass
            if "applied_date" not in doc and doc.get("appliedDate"):
                doc["applied_date"] = doc.get("appliedDate")
            if "applied_date" not in doc:
                doc["applied_date"] = (doc.get("applied_date") or doc.get("appliedDate") or "")
            if "department" not in doc or not doc.get("department"):
                pos = (doc.get("position") or "").lower()
                default_dept = "개발팀" if any(k in pos for k in ["dev", "개발", "engineer"]) else "미지정"
                doc["department"] = doc.get("dept") or default_dept
            skills = doc.get("skills")
            if isinstance(skills, str):
                doc["skills"] = [s.strip() for s in skills.split(",") if s.strip()]
            if "skills" not in doc or not isinstance(doc.get("skills"), list):
                doc["skills"] = []
            if "rating" not in doc:
                doc["rating"] = 0.0
            if "status" not in doc:
                doc["status"] = "지원"
            if "experience" not in doc:
                doc["experience"] = doc.get("exp") or ""
            if "email" not in doc:
                doc["email"] = doc.get("mail") or ""
            if "phone" not in doc:
                doc["phone"] = doc.get("tel") or ""
            if "position" not in doc:
                doc["position"] = ""
            if "name" not in doc:
                doc["name"] = ""
            return doc
        
        # 데이터베이스에서 조회 (기본: applicant)
        cursor = applicants_collection.find(query).skip(skip).limit(limit)
        applicants = await cursor.to_list(length=limit)
        # 결과가 없으면 다른 컬렉션/DB 폴백 조회 (applicants, Hireme)
        if not applicants:
            uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("DATABASE_NAME", "hireme")
            candidates = [
                (db_name, "applicants"),
                ("Hireme" if db_name.lower() == "hireme" else db_name, "applicant"),
                ("Hireme" if db_name.lower() == "hireme" else db_name, "applicants"),
            ]
            with MongoClient(uri) as client:
                for dn, cn in candidates:
                    alt_cursor = client[dn][cn].find(query).skip(skip).limit(limit)
                    data = list(alt_cursor)
                    if data:
                        applicants = data
                        break
        
        # 결과 변환
        normalized = [_normalize(a) for a in applicants]
        result = [Applicant(**applicant) for applicant in normalized]
        
        # 캐시에 저장
        _applicants_cache[cache_key] = (datetime.now(), result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 조회 실패: {str(e)}")

@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(applicant_id: str):
    """특정 지원자 조회"""
    try:
        if not ObjectId.is_valid(applicant_id):
            raise HTTPException(status_code=400, detail="잘못된 지원자 ID")
        
        applicant = await applicants_collection.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        # Enrich from OCR DB if available (no UI changes)
        try:
            docs_meta = (applicant.get("documents") or {})
            doc_hash = docs_meta.get("doc_hash")
            if doc_hash:
                ocr_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
                ocr_db_name = os.getenv("MONGODB_DB", "pdf_ocr")
                with MongoClient(ocr_uri) as client:
                    ocr_db = client[ocr_db_name]
                    doc = ocr_db[os.getenv("MONGODB_COLLECTION", "documents")].find_one({"doc_hash": doc_hash})
                    if doc:
                        # Only fill missing/empty fields to avoid overriding UI data
                        if not applicant.get("summary") and doc.get("summary"):
                            applicant["summary"] = doc.get("summary")
                        # Simple mapping hints for experience if present in doc.fields
                        fields = doc.get("fields") or {}
                        if not applicant.get("experience"):
                            periods = fields.get("periods") or []
                            if periods:
                                applicant["experience"] = ", ".join(periods)
                        # Attach OCR extracted fields under documents for frontend optional display
                        try:
                            if isinstance(applicant.get("documents"), dict):
                                applicant["documents"]["ocr_fields"] = {
                                    "name": fields.get("name"),
                                    "email": (fields.get("email") or []),
                                    "phone": (fields.get("phone") or []),
                                    "periods": (fields.get("periods") or []),
                                    "schools": (fields.get("schools") or []),
                                    "degrees": (fields.get("degrees") or []),
                                }
                        except Exception:
                            pass
        except Exception:
            pass

        return Applicant(**applicant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 조회 실패: {str(e)}")

@router.post("/", response_model=Applicant)
async def create_applicant(applicant: Applicant):
    """새로운 지원자 생성"""
    try:
        applicant_dict = applicant.model_dump(exclude={"id"})
        applicant_dict["created_at"] = datetime.utcnow()
        applicant_dict["updated_at"] = datetime.utcnow()
        
        result = await applicants_collection.insert_one(applicant_dict)
        applicant_dict["_id"] = result.inserted_id
        
        # 캐시 무효화
        _applicants_cache.clear()
        
        return Applicant(**applicant_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 생성 실패: {str(e)}")

@router.put("/{applicant_id}", response_model=Applicant)
async def update_applicant(applicant_id: str, applicant: Applicant):
    """지원자 정보 업데이트"""
    try:
        if not ObjectId.is_valid(applicant_id):
            raise HTTPException(status_code=400, detail="잘못된 지원자 ID")
        
        applicant_dict = applicant.model_dump(exclude={"id"})
        applicant_dict["updated_at"] = datetime.utcnow()
        
        result = await applicants_collection.update_one(
            {"_id": ObjectId(applicant_id)},
            {"$set": applicant_dict}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 캐시 무효화
        _applicants_cache.clear()
        
        # 업데이트된 지원자 반환
        updated_applicant = await applicants_collection.find_one({"_id": ObjectId(applicant_id)})
        return Applicant(**updated_applicant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 업데이트 실패: {str(e)}")

@router.put("/{applicant_id}/status")
async def update_applicant_status(applicant_id: str, status_update: StatusUpdate):
    """지원자 상태 업데이트"""
    try:
        if not ObjectId.is_valid(applicant_id):
            raise HTTPException(status_code=400, detail="잘못된 지원자 ID")
        
        result = await applicants_collection.update_one(
            {"_id": ObjectId(applicant_id)},
            {
                "$set": {
                    "status": status_update.status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 캐시 무효화
        _applicants_cache.clear()
        
        return {"message": "지원자 상태가 업데이트되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 상태 업데이트 실패: {str(e)}")

@router.delete("/{applicant_id}")
async def delete_applicant(applicant_id: str):
    """지원자 삭제"""
    try:
        if not ObjectId.is_valid(applicant_id):
            raise HTTPException(status_code=400, detail="잘못된 지원자 ID")
        
        result = await applicants_collection.delete_one({"_id": ObjectId(applicant_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")
        
        # 캐시 무효화
        _applicants_cache.clear()
        
        return {"message": "지원자가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지원자 삭제 실패: {str(e)}")

@router.get("/stats/overview", response_model=StatsResponse)
async def get_applicant_stats():
    """지원자 통계 조회 (캐시 적용)"""
    try:
        # 캐시 확인
        cache_key = "applicant_stats"
        if cache_key in _applicants_cache:
            cache_time, cache_data = _applicants_cache[cache_key]
            if (datetime.now() - cache_time).seconds < _cache_timeout:
                return cache_data
        
        # 통계 계산 (기본)
        total = await applicants_collection.count_documents({})
        passed = await applicants_collection.count_documents({"status": {"$in": ["서류합격", "최종합격"]}})
        waiting = await applicants_collection.count_documents({"status": "보류"})
        rejected = await applicants_collection.count_documents({"status": "서류불합격"})
        # 0이면 컬렉션/DB 폴백으로 다시 계산
        if total == 0:
            uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("DATABASE_NAME", "hireme")
            candidates = [
                (db_name, "applicants"),
                ("Hireme" if db_name.lower() == "hireme" else db_name, "applicant"),
                ("Hireme" if db_name.lower() == "hireme" else db_name, "applicants"),
            ]
            with MongoClient(uri) as client:
                for dn, cn in candidates:
                    col = client[dn][cn]
                    t = col.count_documents({})
                    if t > 0:
                        total = t
                        passed = col.count_documents({"status": {"$in": ["서류합격", "최종합격"]}})
                        waiting = col.count_documents({"status": "보류"})
                        rejected = col.count_documents({"status": "서류불합격"})
                        break
        
        result = StatsResponse(
            total=total,
            passed=passed,
            waiting=waiting,
            rejected=rejected
        )
        
        # 캐시에 저장
        _applicants_cache[cache_key] = (datetime.now(), result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.get("/search/{keyword}")
async def search_applicants(
    keyword: str,
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=50, description="가져올 항목 수")
):
    """지원자 검색 (페이지네이션 지원)"""
    try:
        # 이름, 이메일, 직무, 기술스택으로 검색
        query = {
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"email": {"$regex": keyword, "$options": "i"}},
                {"position": {"$regex": keyword, "$options": "i"}},
                {"skills": {"$regex": keyword, "$options": "i"}}
            ]
        }
        
        cursor = applicants_collection.find(query).skip(skip).limit(limit)
        applicants = await cursor.to_list(length=limit)
        return [Applicant(**applicant) for applicant in applicants]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")
