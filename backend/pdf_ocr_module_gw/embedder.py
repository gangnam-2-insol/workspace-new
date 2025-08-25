from __future__ import annotations

from functools import lru_cache
from typing import List
import numpy as np

from .config import Settings


@lru_cache(maxsize=1)
def _get_model(model_name: str):  # type: ignore[no-untyped-def]
    """Lazily import sentence-transformers only if available.

    If not installed, fall back to a tiny deterministic hash embedding to avoid heavy deps.
    """
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name)
    except Exception:
        return None


def embed_texts(texts: List[str], settings: Settings) -> List[List[float]]:
    model = _get_model(settings.embedding_model_name)
    if model is None:
        # Lightweight fallback: hashing-based embedding (fixed dim)
        dim = 128
        vecs = []
        for t in texts:
            v = np.zeros(dim, dtype=float)
            for i, ch in enumerate(t[:1000]):
                v[i % dim] += (ord(ch) % 17) / 17.0
            vecs.append(v)
        embeddings = np.vstack(vecs)
    else:
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    if settings.l2_normalize_embeddings:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms
    try:
        dim = int(getattr(model, "get_sentence_embedding_dimension", lambda: embeddings.shape[1])())
    except Exception:
        dim = int(embeddings.shape[1])
    print(f"[EMBED] model={settings.embedding_model_name} dim={dim} count={len(texts)} normalize={settings.l2_normalize_embeddings}")
    return [emb.tolist() for emb in embeddings]


# 텍스트를 벡터(임베딩)로 변환
# SentenceTransformer or OpenAI Embedding API 사용
def get_embedding(text: str) -> List[float]:
    settings = Settings()
    model = _get_model(settings.embedding_model_name)
    if model is None:
        dim = 128
        v = np.zeros(dim, dtype=float)
        for i, ch in enumerate(text[:1000]):
            v[i % dim] += (ord(ch) % 17) / 17.0
        vec = v
    else:
        vec = model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0]
    if settings.l2_normalize_embeddings:
        n = float(np.linalg.norm(vec))
        if n != 0:
            vec = vec / n
    try:
        dim = int(getattr(model, "get_sentence_embedding_dimension", lambda: vec.shape[0])())
    except Exception:
        dim = int(vec.shape[0])
    print(f"[EMBED_Q] model={settings.embedding_model_name} dim={dim} normalize={settings.l2_normalize_embeddings}")
    return vec.tolist()



