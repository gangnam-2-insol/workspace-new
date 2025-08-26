from __future__ import annotations

import os
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
    thumbnails_dir: Path = Field(default=Path("data/thumbnails"))
    output_dir: Path = Field(default=Path("data/output"))
    temp_dir: Path = Field(default=Path("data/temp"))

    # 외부 바이너리 경로 (선택)
    tesseract_path: Optional[str] = Field(default=None)
    tesseract_data_path: Path = Field(default=Path("tessdata"))
    poppler_path: Optional[str] = Field(default=None)

    # OCR 설정
    ocr_language: str = Field(default="kor+eng")  # 한국어 우선, 영어 병행
    ocr_default_psm: int = Field(default=6)  # 기본 단순 문단
    dpi: int = Field(default=400)  # PDF → 이미지 변환 DPI
    quality_threshold: float = Field(default=0.6)  # 품질 임계값
    max_retries: int = Field(default=3)  # 재시도 횟수

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

    # ChromaDB 설정
    chroma_persist_dir: str = Field(default="vector_db/chroma")
    chroma_collection: str = Field(default="pdf_embeddings")

    # 임베딩 모델
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    l2_normalize_embeddings: bool = Field(default=True)

    # 청크 설정
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=200)
    min_chunk_chars: int = Field(default=20)

    # 인덱싱 시 요약/키워드 생성 여부
    index_generate_summary: bool = Field(default=False)
    index_generate_keywords: bool = Field(default=False)

    # OpenAI (선택)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o")

    # LLM 제공자 설정
    llm_provider: str = Field(default="groq")  # "groq" | "openai"
    # Groq (선택)
    groq_api_key: Optional[str] = Field(default=None)
    groq_model: str = Field(default="llama-3.1-70b-versatile")

    # 자동 저장 설정
    auto_save: bool = Field(default=True)
    enable_vector_storage: bool = Field(default=True)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 환경변수에서 직접 읽기 (fallback)
        if not self.poppler_path:
            self.poppler_path = os.getenv("POPPLER_PATH")

        if not self.tesseract_path:
            self.tesseract_path = os.getenv("TESSERACT_CMD")

        # 기본 경로 시도 (Windows)
        if not self.poppler_path:
            possible_poppler_paths = [
                r"C:\tools\poppler\Library\bin",
                r"C:\Program Files\poppler\bin",
                r"C:\poppler\bin",
                r"C:\ProgramData\chocolatey\lib\poppler\tools\poppler-23.11.0\Library\bin",
                r"C:\ProgramData\chocolatey\lib\poppler\tools\poppler-24.02.0\Library\bin",
            ]
            for path in possible_poppler_paths:
                if os.path.exists(path):
                    self.poppler_path = path
                    break

        # Tesseract 기본 경로 시도 (Windows)
        if not self.tesseract_path:
            possible_tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\tools\tesseract\tesseract.exe",
            ]
            for path in possible_tesseract_paths:
                if os.path.exists(path):
                    self.tesseract_path = path
                    break
