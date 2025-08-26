from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class SimilarityLevel(str, Enum):
    """유사도 레벨"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class DocumentType(str, Enum):
    """문서 타입"""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    PORTFOLIO = "portfolio"

class SimilarityResult(BaseModel):
    """유사도 분석 결과"""
    document_id: str
    document_name: str = ""
    overall_similarity: float = Field(..., ge=0.0, le=1.0)
    field_similarities: Dict[str, float] = {}
    chunk_matches: int = 0
    chunk_details: List[Dict[str, Any]] = []
    is_high_similarity: bool = False
    is_moderate_similarity: bool = False
    is_low_similarity: bool = False
    llm_analysis: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)

class PlagiarismAnalysis(BaseModel):
    """표절 분석 결과"""
    suspicion_level: SimilarityLevel
    suspicion_score: float = Field(..., ge=0.0, le=1.0)
    suspicion_score_percent: int = Field(..., ge=0, le=100)
    analysis: str = ""
    recommendations: List[str] = []
    similar_count: int = 0
    analyzed_at: datetime = Field(default_factory=datetime.now)

class SearchRequest(BaseModel):
    """검색 요청"""
    query: str
    document_type: DocumentType = DocumentType.RESUME
    limit: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    use_hybrid_search: bool = True

class SearchResult(BaseModel):
    """검색 결과"""
    query: str
    search_method: str
    weights: Dict[str, float] = {}
    results: List[SimilarityResult] = []
    total: int = 0
    vector_count: int = 0
    keyword_count: int = 0
    execution_time: float = 0.0

class ChunkInfo(BaseModel):
    """청크 정보"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    score: float = 0.0

class EmbeddingType(str, Enum):
    """임베딩 타입"""
    DOCUMENT = "document"
    QUERY = "query"
    CHUNK = "chunk"

class EmbeddingRequest(BaseModel):
    """임베딩 요청"""
    text: str
    embedding_type: EmbeddingType = EmbeddingType.DOCUMENT
    model: str = "text-embedding-3-small"

class EmbeddingResponse(BaseModel):
    """임베딩 응답"""
    text: str
    embedding: List[float]
    embedding_type: EmbeddingType
    model: str
    dimensions: int
    created_at: datetime = Field(default_factory=datetime.now)
