from __future__ import annotations

from typing import Any, Dict, List
import math
from datetime import datetime

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    # Pinecone이 설치되지 않은 경우를 위한 대체
    Pinecone = None
    ServerlessSpec = None

from .config import Settings


_pc: Pinecone | None = None
_index = None


def _ensure_index(settings: Settings):
    global _pc, _index
    if _index is not None:
        return _index
    if not settings.pinecone_api_key or Pinecone is None:
        # 키가 없거나 Pinecone이 설치되지 않으면 인덱싱/검색을 비활성화
        return None
    try:
        _pc = Pinecone(api_key=settings.pinecone_api_key)
        _index = _pc.Index(settings.pinecone_index_name)
    except Exception:
        # 인덱스가 없으면 생성 (MiniLM-L6-v2 = 384차원)
        if ServerlessSpec is not None:
            _pc.create_index(
                name=settings.pinecone_index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
            )
            _index = _pc.Index(settings.pinecone_index_name)
        else:
            return None
    return _index


def upsert_embeddings(
    ids: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
    settings: Settings,
    documents: List[str] | None = None,
) -> None:
    index = _ensure_index(settings)
    if index is None:
        # Pinecone 비활성화 상태에서는 업서트를 생략
        return
    vectors = []
    for i, vid in enumerate(ids):
        meta = dict(metadatas[i] or {})
        if documents is not None:
            meta["document"] = documents[i]
        meta.setdefault("indexed_at", datetime.utcnow().isoformat())
        vectors.append({
            "id": str(vid),
            "values": embeddings[i],
            "metadata": meta,
        })
    index.upsert(vectors=vectors)


# ChromaDB 등 VectorDB에 벡터와 메타데이터 저장
def store_vector(embedding: List[float], metadata: dict) -> None:
    settings = Settings()
    upsert_embeddings(ids=[metadata.get("id") or metadata.get("doc_hash") or "temp"], embeddings=[embedding], metadatas=[metadata], settings=settings, documents=[metadata.get("document") or ""])  # type: ignore


def query_top_k(embedding: List[float], k: int, settings: Settings) -> Dict[str, Any]:
    # 안전장치: all-zero/NaN 방지
    if not embedding or all(abs(x) < 1e-12 for x in embedding) or any(math.isnan(x) or math.isinf(x) for x in embedding):
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    index = _ensure_index(settings)
    if index is None:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    result = index.query(vector=embedding, top_k=k, include_metadata=True)
    matches = result.get("matches", []) if isinstance(result, dict) else getattr(result, "matches", [])
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    distances: List[float] = []
    for m in matches:
        meta = m.get("metadata") or {}
        score = float(m.get("score", 0.0))
        # cosine distance = 1 - cosine similarity score
        dist = 1.0 - score
        documents.append(str(meta.get("document") or ""))
        metadatas.append(meta)
        distances.append(dist)
    return {"documents": [documents], "metadatas": [metadatas], "distances": [distances]}


def delete_by_doc_hash(doc_hash: str, settings: Settings) -> Dict[str, Any]:
    index = _ensure_index(settings)
    if index is None:
        return {"deleted": False, "reason": "pinecone_disabled"}
    index.delete(filter={"doc_hash": doc_hash})
    return {"deleted": True}



