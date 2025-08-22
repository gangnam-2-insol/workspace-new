from __future__ import annotations

from pathlib import Path
from typing import Optional
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """프로젝트 전역 설정.

    .env 파일 또는 환경변수에서 로드됩니다.
    """

    # 기본 설정
    base_dir: Path = Path("pdf_ocr_data")
    data_dir: Path = base_dir / "data"
    uploads_dir: Path = base_dir / "uploads"
    images_dir: Path = base_dir / "images"
    thumbnails_dir: Path = base_dir / "thumbnails"
    embeddings_dir: Path = base_dir / "embeddings"
    analysis_dir: Path = base_dir / "analysis"
    results_dir: Path = base_dir / "results"
    
    # 성능 최적화 설정
    enable_ai_analysis: bool = True  # AI 분석 활성화/비활성화
    enable_embeddings: bool = False  # 임베딩 생성 비활성화 (처리 시간 단축)
    enable_summary: bool = True      # 요약 생성
    enable_keywords: bool = True     # 키워드 추출
    
    # OCR 설정
    ocr_quality: str = "fast"       # "fast", "balanced", "high"
    min_chunk_chars: int = 50       # 최소 청크 크기
    chunk_size: int = 1000          # 청크 크기
    chunk_overlap: int = 200        # 청크 겹침
    
    # AI 분석 설정
    use_gpt4: bool = False          # GPT-4 사용 여부 (GPT-4o가 더 빠름)
    max_text_length: int = 8000     # 분석할 최대 텍스트 길이
    
    # 이미지 처리 설정
    image_dpi: int = 150            # 이미지 DPI (낮출수록 빠름)
    thumbnail_size: tuple = (200, 200)  # 썸네일 크기

    # 외부 바이너리 경로 (선택)
    tesseract_cmd: Optional[str] = Field(default=None)
    # poppler_path 제거 - PyPDF2와 pdfplumber 사용

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
    index_generate_summary: bool = Field(default=True)
    index_generate_keywords: bool = Field(default=True)

    # OpenAI (기본)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o")

    # LLM 제공자 설정
    llm_provider: str = Field(default="openai")  # "groq" | "openai"
    # Groq (선택)
    groq_api_key: Optional[str] = Field(default=None)
    groq_model: str = Field(default="llama-3.1-70b-versatile")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 환경변수에서 직접 읽기 (fallback)
        if not self.tesseract_cmd:
            self.tesseract_cmd = os.getenv("TESSERACT_CMD")
        
        # 기본 경로 시도 (Windows)
        if not self.tesseract_cmd:
            possible_tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # 사용자가 제공한 경로
                r"C:\Users\Drew\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
            ]
            for path in possible_tesseract_paths:
                if os.path.exists(path):
                    self.tesseract_cmd = path
                    break



