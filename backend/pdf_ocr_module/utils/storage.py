"""
Storage Utilities
================

MongoDB 및 벡터 저장소 관리 클래스입니다.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .config import Settings

logger = logging.getLogger(__name__)


class MongoStorage:
    """MongoDB 저장소 클래스"""

    def __init__(self, settings: Settings):
        """
        MongoStorage 초기화

        Args:
            settings: 설정 객체
        """
        self.settings = settings
        self.client = None
        self.db = None
        self.collection = None

        if MONGODB_AVAILABLE:
            self._connect()

    def _connect(self):
        """MongoDB에 연결합니다."""
        try:
            self.client = MongoClient(self.settings.mongodb_uri)
            self.db = self.client[self.settings.mongodb_db]
            self.collection = self.db[self.settings.mongodb_collection]
            logger.info(f"MongoDB 연결 성공: {self.settings.mongodb_uri}")
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self.client = None

    def save_document(self, document: Dict[str, Any]) -> bool:
        """
        문서를 MongoDB에 저장합니다.

        Args:
            document: 저장할 문서

        Returns:
            저장 성공 여부
        """
        if not self.collection:
            logger.warning("MongoDB가 연결되지 않았습니다.")
            return False

        try:
            # 중복 검사
            if self.settings.use_dedup:
                existing = self.collection.find_one({
                    "filename": document.get("filename"),
                    "file_path": document.get("file_path")
                })
                if existing:
                    logger.info(f"중복 문서 발견: {document.get('filename')}")
                    return True

            # 저장
            result = self.collection.insert_one(document)
            logger.info(f"문서 저장 성공: {result.inserted_id}")
            return True

        except Exception as e:
            logger.error(f"문서 저장 실패: {str(e)}")
            return False

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        문서를 조회합니다.

        Args:
            document_id: 문서 ID

        Returns:
            문서 데이터 또는 None
        """
        if not self.collection:
            return None

        try:
            return self.collection.find_one({"_id": document_id})
        except Exception as e:
            logger.error(f"문서 조회 실패: {str(e)}")
            return None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        모든 문서를 조회합니다.

        Returns:
            문서 목록
        """
        if not self.collection:
            return []

        try:
            return list(self.collection.find())
        except Exception as e:
            logger.error(f"문서 목록 조회 실패: {str(e)}")
            return []

    def get_storage_size(self) -> int:
        """
        저장소 크기를 반환합니다.

        Returns:
            저장된 문서 수
        """
        if not self.collection:
            return 0

        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"저장소 크기 조회 실패: {str(e)}")
            return 0

    def close(self):
        """연결을 종료합니다."""
        if self.client:
            self.client.close()


class VectorStorage:
    """벡터 저장소 클래스 (ChromaDB 기반)"""

    def __init__(self, settings: Settings):
        """
        VectorStorage 초기화

        Args:
            settings: 설정 객체
        """
        self.settings = settings
        self.client = None
        self.collection = None

        if CHROMADB_AVAILABLE:
            self._connect()

    def _connect(self):
        """ChromaDB에 연결합니다."""
        try:
            # ChromaDB 설정
            chroma_settings = ChromaSettings(
                persist_directory=self.settings.chroma_persist_dir,
                anonymized_telemetry=False
            )

            self.client = chromadb.PersistentClient(settings=chroma_settings)
            self.collection = self.client.get_or_create_collection(
                name=self.settings.chroma_collection
            )
            logger.info(f"ChromaDB 연결 성공: {self.settings.chroma_persist_dir}")

        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {str(e)}")
            self.client = None

    def store_embeddings(self, document: Dict[str, Any]) -> bool:
        """
        문서의 임베딩을 저장합니다.

        Args:
            document: 문서 데이터

        Returns:
            저장 성공 여부
        """
        if not self.collection:
            logger.warning("ChromaDB가 연결되지 않았습니다.")
            return False

        try:
            # 임베딩 생성 (간단한 예시)
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(self.settings.embedding_model_name)
            text = document.get("full_text", "")

            if not text:
                logger.warning("저장할 텍스트가 없습니다.")
                return False

            # 텍스트를 청크로 분할
            chunks = self._split_text(text)
            embeddings = model.encode(chunks)

            # 메타데이터 준비
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "document_id": document.get("document_id", ""),
                    "filename": document.get("filename", ""),
                    "chunk_index": i,
                    "chunk_text": chunk[:200]  # 메타데이터에는 짧은 텍스트만
                })

            # 벡터 저장
            ids = [f"{document.get('document_id', '')}_{i}" for i in range(len(chunks))]

            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"벡터 저장 성공: {len(chunks)}개 청크")
            return True

        except Exception as e:
            logger.error(f"벡터 저장 실패: {str(e)}")
            return False

    def _split_text(self, text: str) -> List[str]:
        """
        텍스트를 청크로 분할합니다.

        Args:
            text: 원본 텍스트

        Returns:
            청크 목록
        """
        chunks = []
        words = text.split()

        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= self.settings.chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        유사한 문서를 검색합니다.

        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 수

        Returns:
            유사한 문서 목록
        """
        if not self.collection:
            return []

        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(self.settings.embedding_model_name)
            query_embedding = model.encode([query])

            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )

            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]

        except Exception as e:
            logger.error(f"유사도 검색 실패: {str(e)}")
            return []

    def get_vector_count(self) -> int:
        """
        저장된 벡터 수를 반환합니다.

        Returns:
            벡터 수
        """
        if not self.collection:
            return 0

        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"벡터 수 조회 실패: {str(e)}")
            return 0
