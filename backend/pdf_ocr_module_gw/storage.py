from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from .config import Settings


def _get_collections(client: MongoClient, settings: Settings) -> tuple[Collection, Collection]:
    db = client[settings.mongodb_db]
    return db[settings.mongodb_col_documents], db[settings.mongodb_col_pages]


def save_document_to_mongo(document: Dict[str, Any], settings: Settings) -> str:
    client = MongoClient(settings.mongodb_uri)
    try:
        col_docs, _ = _get_collections(client, settings)
        payload = {
            **document,
            "created_at": document.get("created_at", datetime.utcnow()),
        }
        result = col_docs.insert_one(payload)
        return str(result.inserted_id)
    finally:
        client.close()


# MongoDB에 원본 텍스트, 요약, 키워드, 메타데이터 저장
def save_to_db(
    pdf_filename: str,
    page_number: int,
    text: str,
    db_conn: MongoClient | None,
    summary: str | None,
    keywords: list[str] | None,
    *,
    doc_hash: Optional[str] = None,
) -> str:
    settings = Settings()
    client = db_conn or MongoClient(settings.mongodb_uri)
    created_client = db_conn is None
    try:
        _, col_pages = _get_collections(client, settings)
        payload: Dict[str, Any] = {
            "file_name": pdf_filename,
            "page": page_number,
            "text": text,
            "summary": summary,
            "keywords": keywords or [],
            "created_at": datetime.utcnow(),
        }
        if doc_hash:
            payload["doc_hash"] = doc_hash
        result = col_pages.insert_one(payload)
        return str(result.inserted_id)
    finally:
        if created_client:
            client.close()



