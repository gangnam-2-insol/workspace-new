import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 애플리케이션 기본 설정
    app_name: str = "AI Similarity Analysis System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # OpenAI 설정
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Pinecone 설정
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    pinecone_dimension: int = int(os.getenv("PINECONE_DIMENSION", "1536"))

    # Elasticsearch 설정 (비활성화됨)
    elasticsearch_host: Optional[str] = None
    elasticsearch_index: Optional[str] = None
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None
    elasticsearch_ssl_verify: bool = os.getenv("ELASTICSEARCH_SSL_VERIFY", "false").lower() == "true"
    elasticsearch_timeout: int = int(os.getenv("ELASTICSEARCH_TIMEOUT", "30"))

    # MongoDB 설정
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "hireme")
    mongodb_applicants_collection: str = os.getenv("MONGODB_APPLICANTS_COLLECTION", "applicants")
    mongodb_resumes_collection: str = os.getenv("MONGODB_RESUMES_COLLECTION", "resumes")
    mongodb_cover_letters_collection: str = os.getenv("MONGODB_COVER_LETTERS_COLLECTION", "cover_letters")

    # 유사도 분석 설정
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    plagiarism_threshold: float = float(os.getenv("PLAGIARISM_THRESHOLD", "0.8"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "20"))

    # 검색 가중치 설정
    vector_search_weight: float = float(os.getenv("VECTOR_SEARCH_WEIGHT", "0.5"))
    keyword_search_weight: float = float(os.getenv("KEYWORD_SEARCH_WEIGHT", "0.5"))

    # 필드별 유사도 임계값
    field_thresholds: dict = {
        'growthBackground': float(os.getenv("GROWTH_BACKGROUND_THRESHOLD", "0.2")),
        'motivation': float(os.getenv("MOTIVATION_THRESHOLD", "0.2")),
        'careerHistory': float(os.getenv("CAREER_HISTORY_THRESHOLD", "0.2"))
    }

    # 로깅 설정
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "similarity_analysis.log")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 성능 설정
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1시간

    # 보안 설정
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    cors_origins: list = os.getenv("CORS_ORIGINS", "*").split(",")

    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

def get_settings() -> Settings:
    """설정 인스턴스 반환"""
    return settings

def validate_settings() -> bool:
    """설정 유효성 검사"""
    errors = []

    # 필수 설정 검사
    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY가 설정되지 않았습니다.")

    if not settings.pinecone_api_key:
        errors.append("PINECONE_API_KEY가 설정되지 않았습니다.")

    if not settings.mongodb_uri:
        errors.append("MONGODB_URI가 설정되지 않았습니다.")

    # 설정 범위 검사
    if not (0.0 <= settings.similarity_threshold <= 1.0):
        errors.append("SIMILARITY_THRESHOLD는 0.0과 1.0 사이여야 합니다.")

    if not (0.0 <= settings.plagiarism_threshold <= 1.0):
        errors.append("PLAGIARISM_THRESHOLD는 0.0과 1.0 사이여야 합니다.")

    if settings.chunk_size <= 0:
        errors.append("CHUNK_SIZE는 0보다 커야 합니다.")

    if settings.chunk_overlap < 0:
        errors.append("CHUNK_OVERLAP은 0 이상이어야 합니다.")

    if errors:
        print("설정 오류:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True

def print_settings_summary():
    """설정 요약 출력"""
    print("=== AI 유사도 분석 시스템 설정 ===")
    print(f"애플리케이션: {settings.app_name} v{settings.app_version}")
    print(f"디버그 모드: {settings.debug}")
    print(f"OpenAI 모델: {settings.openai_model}")
    print(f"임베딩 모델: {settings.openai_embedding_model}")
    print(f"Pinecone 인덱스: {settings.pinecone_index_name}")
    print(f"Elasticsearch 호스트: {settings.elasticsearch_host}")
    print(f"MongoDB 데이터베이스: {settings.mongodb_database}")
    print(f"유사도 임계값: {settings.similarity_threshold}")
    print(f"표절 임계값: {settings.plagiarism_threshold}")
    print(f"청크 크기: {settings.chunk_size}")
    print(f"검색 가중치 - 벡터: {settings.vector_search_weight}, 키워드: {settings.keyword_search_weight}")
    print("==================================")

if __name__ == "__main__":
    # 설정 검증 및 요약 출력
    if validate_settings():
        print_settings_summary()
    else:
        print("설정 검증에 실패했습니다.")
        exit(1)
