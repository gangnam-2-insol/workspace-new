from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from datetime import datetime

from pdf_ocr_module.config import Settings
from pdf_ocr_module.main import process_pdf
from pdf_ocr_module.vector_storage import query_top_k, delete_by_doc_hash
from pdf_ocr_module.embedder import get_embedding
from pdf_ocr_module.ai_analyzer import clean_text
from pymongo import MongoClient
from pymongo.collection import Collection
from pdf_ocr_module.utils import ensure_directories, save_upload_file
from pdf_ocr_module.config import Settings as AppSettings
from models import Applicant
from database import sync_applicants_collection, sync_resumes_collection
from database import get_sync_database

# 신규 업로드로 지원자 추가 후 목록 캐시 무효화를 위해 applicants 라우터 캐시 참조
try:
    from routers import applicants as applicants_router
except Exception:  # noqa: BLE001
    applicants_router = None


router = APIRouter(prefix="/pdf", tags=["pdf"]) 
settings = Settings()


@router.get("/documents/applicants")
def list_ocr_documents_as_applicants() -> list[dict[str, Any]]:  # type: ignore[no-untyped-def]
    """pdf_ocr.documents 컬렉션을 읽어, 프론트 카드에 바로 렌더 가능한 Applicant 유사 스키마로 반환.
    _id는 충돌 방지를 위해 'ocr_{doc_hash}' 문자열을 사용합니다.
    """
    client = MongoClient(settings.mongodb_uri)
    try:
        db = client[settings.mongodb_db]
        col: Collection = db[settings.mongodb_col_documents]
        docs = list(col.find({}, {"_id": 0}))
        results: list[dict[str, Any]] = []
        for d in docs:
            fields = (d.get("fields") or {})
            emails = list(fields.get("email") or [])
            phones = list(fields.get("phone") or [])
            # 이름은 이메일 로컬파트로 유추하지 않음. 한글 이름이 없으면 "미상" 유지
            name = fields.get("name") or "미상"
            created = d.get("created_at")
            if isinstance(created, datetime):
                applied_date = created.strftime("%Y-%m-%d")
            else:
                applied_date = datetime.utcnow().strftime("%Y-%m-%d")
            skills: list[str] = []
            summary = d.get("summary") or ""
            doc_hash = d.get("doc_hash")
            file_name = d.get("file_name") or ""
            item = {
                "_id": f"ocr_{doc_hash}",
                "name": str(name),
                "position": "미지정",
                "department": "미지정",
                "email": str(emails[0] if emails else "unknown@example.com"),
                "phone": str(phones[0] if phones else ""),
                "applied_date": applied_date,
                "status": "지원",
                "experience": "1-3년",
                "skills": skills,
                "rating": 0.0,
                "summary": str(summary),
                "ai_suitability": 0,
                "ai_scores": None,
                "documents": {
                    "source": str(file_name),
                    "doc_hash": doc_hash,
                    "resume_id": None,
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            results.append(item)
        return results
    finally:
        client.close()


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드할 수 있습니다.")

    ensure_directories(settings)

    saved_path: Path = save_upload_file(file, settings)

    try:
        result = process_pdf(saved_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {exc}") from exc

    # OCR/인덱싱 결과를 기반으로 지원자 생성(이름/이메일/전화 등 필드 추정)
    created_id = None
    try:
        fields = (result or {}).get("fields") or {}
        emails = fields.get("email") or []
        phones = fields.get("phone") or []
        # 이름은 이메일 로컬파트로 유추하지 않음. 한글 이름이 없으면 "미상" 유지
        name = fields.get("name") or None

        # CSV 샘플 스펙에 맞춘 Resumes 레코드도 생성 (프론트에서 활용 가능)
        resume_doc = {
            # _id는 Mongo가 자동 생성
            "resume_id": None,  # 추후 참조용, 동일 _id를 문자열로 보관
            "name": str(name or "미상"),
            "position": "미지정",
            "department": "미지정",
            "experience": "3-5년" if phones or emails else "1-3년",  # 간단 히ュー리스틱
            "skills": "React, JavaScript, TypeScript" if "react" in (result.get("text"," ").lower()) else "Python, Django, SQL",
            "growthBackground": 3,
            "motivation": 3,
            "careerHistory": 3,
            "analysisScore": 70,
            "analysisResult": (result or {}).get("summary") or "",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        r_ins = sync_resumes_collection.insert_one(resume_doc)
        sync_resumes_collection.update_one({"_id": r_ins.inserted_id}, {"$set": {"resume_id": str(r_ins.inserted_id)}})

        # 기본 Applicant 스키마에 맞게 매핑 (부서는 임시, 경력/요약은 추정치)
        applicant_payload = Applicant(
            name=str(name or "미상"),
            position=resume_doc["position"],
            department=resume_doc["department"],
            email=str(emails[0] if emails else "unknown@example.com"),
            phone=str(phones[0] if phones else ""),
            applied_date=datetime.utcnow().strftime("%Y-%m-%d"),
            status="지원",
            experience=resume_doc["experience"],
            skills=[s.strip() for s in (resume_doc["skills"].split(",") if isinstance(resume_doc["skills"], str) else []) if s.strip()],
            rating=0.0,
            summary=str((result or {}).get("summary") or ""),
            ai_suitability=resume_doc["analysisScore"],
            ai_scores=None,
            documents={
                "source": str(saved_path.name),
                "doc_hash": (result or {}).get("doc_hash"),
                "resume_id": str(r_ins.inserted_id),
            },
        ).model_dump(by_alias=True)

        # 단수 컬렉션(hireme.applicant)에 저장
        insert_res = sync_applicants_collection.insert_one(applicant_payload)
        created_id = str(insert_res.inserted_id)

        # 복수 컬렉션(hireme.applicants)에도 동일 문서 저장 (프론트가 해당 컬렉션을 읽는 경우 반영)
        try:
            db = get_sync_database()
            db["applicants"].insert_one(applicant_payload)
        except Exception:
            pass

        # 업로드에 의한 데이터 변경 → applicants 목록 캐시 무효화
        try:
            if applicants_router and hasattr(applicants_router, "_applicants_cache"):
                applicants_router._applicants_cache.clear()
        except Exception:
            pass
    except Exception:
        created_id = None

    return {**result, "applicant_id": created_id}


@router.get("/files")
def list_files() -> dict[str, Any]:  # type: ignore[no-untyped-def]
    settings = Settings()
    client = MongoClient(settings.mongodb_uri)
    try:
        db = client[settings.mongodb_db]
        col = db[settings.mongodb_col_documents]
        files = list(col.find({}, {"file_name": 1, "doc_hash": 1, "_id": 0}))
        return {"files": files}
    finally:
        client.close()


@router.delete("/file/{doc_hash}")
def delete_file(doc_hash: str) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    settings = Settings()
    client = MongoClient(settings.mongodb_uri)
    try:
        db = client[settings.mongodb_db]
        docs: Collection = db[settings.mongodb_col_documents]
        pages: Collection = db[settings.mongodb_col_pages]
        d1 = docs.delete_many({"doc_hash": doc_hash}).deleted_count
        d2 = pages.delete_many({"doc_hash": doc_hash}).deleted_count
        # VectorDB도 정리 (신규 색인분)
        try:
            v = delete_by_doc_hash(doc_hash, settings)
        except Exception:
            v = {"error": "chroma_delete_failed"}
        return {"deleted": {"documents": int(d1), "pages": int(d2), "vector": v}}
    finally:
        client.close()


@router.get("/search")
def search(q: str, k: int = 5) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    try:
        embedding = get_embedding(q)
        settings = Settings()
        app = AppSettings()
        res = query_top_k(embedding, max(k * 3, 10), settings)
        # 임계치 필터링: cosine distance ≤ 0.6만 채택
        raw_docs = (res or {}).get("documents", [[]])[0] or []
        raw_metas = (res or {}).get("metadatas", [[]])[0] or []
        raw_dists = (res or {}).get("distances", [[]])[0] or []
        items = []
        for doc, meta, dist in zip(raw_docs, raw_metas, raw_dists):
            if doc and dist is not None and dist <= 0.6:
                items.append({"document": doc, "metadata": meta, "distance": float(dist)})
        # 중복 억제: 동일 source 그룹핑 후 최고 점수만 남김
        best_by_source: dict[str, dict[str, Any]] = {}
        for it in items:
            src = (it.get("metadata") or {}).get("source") or ""
            if src not in best_by_source or it["distance"] < best_by_source[src]["distance"]:
                best_by_source[src] = it
        deduped = sorted(best_by_source.values(), key=lambda x: x["distance"])[:k]
        # 짧은 한글 질의 부스터(2~4자): 정확 문자열 포함시 보너스
        import re
        q_trim = q.strip()
        if 2 <= len(q_trim) <= 4 and re.fullmatch(r"[가-힣]+", q_trim):
            def boost_score(item: dict[str, Any]) -> float:
                doc = item.get("document") or ""
                return item["distance"] - (0.15 if q_trim in doc else 0.0)
            deduped = sorted(deduped, key=boost_score)
        return {
            "query": q,
            "k": k,
            "results": deduped,
            "meta": {
                "embedding_model_name": app.embedding_model_name,
                "l2_normalize": app.l2_normalize_embeddings,
                "metric": "cosine",
                "topk_requested": k,
                "returned": len(deduped),
            },
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"검색 중 오류: {exc}") from exc




