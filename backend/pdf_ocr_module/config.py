from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """프로젝트 전역 설정.

    .env 파일 또는 환경변수에서 로드됩니다.
    """

    # 경로 설정
    data_dir: Path = Field(default=Path("data"))
    uploads_dir: Path = Field(default=Path("data/uploads"))
    images_dir: Path = Field(default=Path("data/images"))
    results_dir: Path = Field(default=Path("data/results"))

    # 외부 바이너리 경로 (선택)
    tesseract_cmd: Optional[str] = Field(default=None)
    poppler_path: Optional[str] = Field(default=None)

    # OCR 설정
    ocr_lang: str = Field(default="kor+eng")  # 기본 한국어+영어 동시 인식
    ocr_oem: int = Field(default=1)  # 0: Legacy + LSTM, 1: LSTM
    ocr_default_psm: int = Field(default=6)  # 기본 단순 문단
    dpi: int = Field(default=300)  # PDF → 이미지 변환 DPI
    quality_threshold: float = Field(default=0.7)
    max_retries: int = Field(default=2)

    # MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    mongodb_db: str = Field(default="pdf_ocr")
    mongodb_collection: str = Field(default="documents")
    mongodb_col_documents: str = Field(default="documents")
    mongodb_col_pages: str = Field(default="pages")
    use_dedup: bool = Field(default=True)

    # Pinecone (VectorDB)
    pinecone_api_key: Optional[str] = Field(default=None)
    pinecone_index_name: str = Field(default="resume-vectors")
    pinecone_cloud: str = Field(default="aws")
    pinecone_region: str = Field(default="us-east-1")

    # (legacy) ChromaDB 설정은 더 이상 사용하지 않지만 기존 호환을 위해 유지
    chroma_persist_dir: str = Field(default="vector_db/chroma")
    chroma_collection: str = Field(default="pdf_embeddings")

    # 임베딩 모델
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    l2_normalize_embeddings: bool = Field(default=True)

    # 청크 설정
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=200)
    min_chunk_chars: int = Field(default=20)

    # 인덱싱 시 요약/키워드 생성 여부(LLM/휴리스틱 모두 비활성화)
    index_generate_summary: bool = Field(default=False)
    index_generate_keywords: bool = Field(default=False)

    # OpenAI (선택)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")

    # LLM 제공자 설정
    llm_provider: str = Field(default="groq")  # "groq" | "openai"
    # Groq (선택)
    groq_api_key: Optional[str] = Field(default=None)
    groq_model: str = Field(default="llama-3.1-70b-versatile")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")



