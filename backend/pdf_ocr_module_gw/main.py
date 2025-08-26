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

    # 4) 청킹 및 벡터 처리는 별도 서비스에서 담당
    # OCR은 텍스트 추출까지만 담당

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

    # MongoDB에 저장
    inserted_id = save_document_to_mongo(document, settings)
    document["mongo_id"] = inserted_id

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


