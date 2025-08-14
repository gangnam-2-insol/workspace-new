from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .ai_analyzer import analyze_text, extract_keywords, summarize_text, extract_fields, clean_text
from .config import Settings
from .embedder import embed_texts, get_embedding
from .ocr_engine import ocr_images, ocr_images_with_quality
from .pdf_extractor import extract_text_with_layout
from .pdf_processor import save_pdf_pages_to_images, create_thumbnails
from .storage import save_document_to_mongo, save_to_db
from .utils import ensure_directories, write_json, file_sha256
from .vector_storage import upsert_embeddings, store_vector


def process_pdf(pdf_path: str | Path) -> Dict[str, Any]:
    settings = Settings()
    ensure_directories(settings)

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {pdf_path}")

    # 0) 중복 방지 해시 계산
    doc_hash = file_sha256(pdf_path)

    # 1) 우선 내장 텍스트/레이아웃 추출
    layout = extract_text_with_layout(pdf_path)

    # 2) PDF -> 이미지
    page_image_dir = settings.images_dir / pdf_path.stem
    image_paths: List[Path] = save_pdf_pages_to_images(pdf_path, page_image_dir, settings)
    thumb_paths: List[Path] = create_thumbnails(image_paths)

    # 2) 이미지 -> 텍스트 (OCR)
    ocr_outputs = ocr_images_with_quality(image_paths, settings)
    page_texts: List[str] = []
    # 내장 텍스트가 있으면 우선 사용, 부족하면 OCR 보완
    for i in range(len(image_paths)):
        page_spans = next((p.get("spans", []) for p in layout.get("pages", []) if p.get("page") == i + 1), [])
        embedded_text = " ".join([s.get("text", "") for s in page_spans]).strip()
        ocr_text = ocr_outputs[i]["result"]["text"]
        chosen = embedded_text if len(embedded_text) >= max(50, len(ocr_text) * 0.5) else ocr_text
        page_texts.append(chosen)
    full_text: str = "\n\n".join(page_texts)

    # 3) 텍스트 분석 (요약/키워드) - 인덱싱 단계에서는 비활성화 가능
    if settings.index_generate_summary or settings.index_generate_keywords:
        analysis = analyze_text(full_text, settings)
        _summary = summarize_text(full_text) if settings.index_generate_summary else ""
        _keywords = extract_keywords(full_text) if settings.index_generate_keywords else []
    else:
        analysis = {"summary": "", "keywords": [], "clean_text": full_text}
        _summary = ""
        _keywords = []

    # 4) 청크 생성 및 임베딩(페이지→청크 단일화)
    def chunk_text(text: str, size: int, overlap: int) -> list[tuple[str, tuple[int, int]]]:
        chunks: list[tuple[str, tuple[int, int]]] = []
        start = 0
        n = len(text)
        while start < n:
            end = min(n, start + size)
            chunk = text[start:end]
            if len(chunk.strip()) >= settings.min_chunk_chars:
                chunks.append((chunk, (start, end)))
            start = end - overlap if end - overlap > start else end
        return chunks

    page_chunks: list[dict] = []
    for page_index, text in enumerate(page_texts, start=1):
        for chunk_id, (chunk, (st, en)) in enumerate(
            chunk_text(text, settings.chunk_size, settings.chunk_overlap), start=1
        ):
            cleaned = clean_text(chunk)
            if len(cleaned.strip()) < settings.min_chunk_chars:
                continue
            page_chunks.append({
                "page": page_index,
                "chunk_id": chunk_id,
                "text": cleaned,
                "offsets": (st, en),
            })

    # NaN/inf/all-zero 필터링은 임베딩 후 적용
    embeddings = embed_texts([c["text"] for c in page_chunks], settings) if page_chunks else []
    valid_indices: list[int] = []
    cleaned_embeddings: list[list[float]] = []
    import math
    for i, vec in enumerate(embeddings):
        if not vec:
            continue
        if any(math.isnan(x) or math.isinf(x) for x in vec):
            continue
        if all(abs(x) < 1e-12 for x in vec):
            continue
        valid_indices.append(i)
        cleaned_embeddings.append(vec)
    # 단일 텍스트 임베딩 예시 함수 사용 (문서 전체 기준)
    _doc_embedding = get_embedding(full_text)

    # 5) VectorDB 저장(청크 단위, 스키마 표준화)
    vector_ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    for new_idx, orig_idx in enumerate(valid_indices, start=1):
        ch = page_chunks[orig_idx]
        page_no = ch["page"]
        chunk_id = ch["chunk_id"]
        start_off, end_off = ch["offsets"]
        vid = f"{doc_hash}_{page_no}_{chunk_id}"
        vector_ids.append(vid)
        documents.append(ch["text"])
        meta: dict[str, Any] = {
            "source": str(pdf_path),
            "file_name": pdf_path.name.lstrip('.') ,
            "page": int(page_no),
            "chunk_id": int(chunk_id),
            "offset_start": int(start_off),
            "offset_end": int(end_off),
            "doc_hash": doc_hash,
        }
        # 선택: 엔티티 캐시(이메일/전화)
        try:
            ef = extract_fields(ch["text"])  # type: ignore[arg-type]
            if isinstance(ef, dict):
                emails = list(ef.get("email") or [])
                phones = list(ef.get("phone") or [])
                if emails:
                    meta["email_count"] = int(len(emails))
                    meta["first_email"] = str(emails[0])
                if phones:
                    meta["phone_count"] = int(len(phones))
                    meta["first_phone"] = str(phones[0])
        except Exception:
            pass
        # 보조 메타: 표/스팬 요약
        if (page_no - 1) < len(layout.get("pages", [])):
            spans = layout["pages"][page_no - 1].get("spans", []) or []
            tables = layout["pages"][page_no - 1].get("tables", []) or []
            meta["num_spans"] = int(len(spans))
            meta["has_tables"] = bool(tables)
        metadatas.append(meta)

    if vector_ids:
        upsert_embeddings(
            ids=vector_ids,
            embeddings=cleaned_embeddings,
            metadatas=metadatas,
            settings=settings,
            documents=documents,
        )

    # 6) MongoDB 저장
    fields = extract_fields(full_text)
    document = {
        "doc_id": str(uuid.uuid4()),
        "doc_hash": doc_hash,
        "file_name": pdf_path.name,
        "num_pages": len(page_texts),
        "preview": [str(p) for p in thumb_paths],
        "pages": [
            {
                "page": i + 1,
                "clean_text": analyze_text(t, settings).get("clean_text", t),
                "quality_score": float(ocr_outputs[i]["result"].get("quality") or 0.0),
                "trace": {
                    "attempts": ocr_outputs[i].get("attempts", []),
                },
            }
            for i, t in enumerate(page_texts)
        ],
        "text": full_text,
        "fields": fields,
        "summary": analysis.get("summary") or _summary,
        "keywords": analysis.get("keywords", []) or _keywords,
        "created_at": datetime.utcnow(),
    }
    inserted_id = save_document_to_mongo(document, settings)

    # 페이지 단위 몽고 저장(원본 텍스트+클린): 필요시 검증용
    for idx, page_text in enumerate(page_texts, start=1):
        save_to_db(pdf_path.name.lstrip('.'), idx, page_text, None, None, None, doc_hash=doc_hash)

    # 7) 결과 저장 (선택)
    result_path = settings.results_dir / f"{pdf_path.stem}.json"
    write_json(result_path, {
        "mongo_id": inserted_id,
        **{k: v for k, v in document.items() if k != "pages" or len(v) <= 3},  # 너무 길면 요약 저장
    })

    return {
        "mongo_id": inserted_id,
        "file_name": pdf_path.name,
        "num_pages": len(page_texts),
        "full_text": full_text,  # 전체 텍스트 추가
        "summary": analysis.get("summary") if settings.index_generate_summary else None,
        "keywords": analysis.get("keywords", []) if settings.index_generate_keywords else [],
        "doc_hash": doc_hash,
        "fields": fields,
    }


