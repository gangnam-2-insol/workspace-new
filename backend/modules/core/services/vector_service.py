import os
import asyncio
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Pinecone 라이브러리가 설치되지 않았습니다. pip install pinecone-client로 설치하세요.")

class VectorService:
    def __init__(self, api_key: str = None, index_name: str = None, environment: str = None):
        """
        Pinecone 벡터 데이터베이스 서비스 초기화
        
        Args:
            api_key (str): Pinecone API 키
            index_name (str): Pinecone 인덱스 이름
            environment (str): Pinecone 환경 (예: us-east-1)
        """
        # 환경 변수에서 설정 로드
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        
        if not PINECONE_AVAILABLE:
            raise Exception("Pinecone 라이브러리가 필요합니다. pip install pinecone-client로 설치하세요.")
        
        if not self.api_key:
            raise Exception("PINECONE_API_KEY가 설정되지 않았습니다.")
        
        # Pinecone 클라이언트 초기화
        try:
            self.pc = Pinecone(api_key=self.api_key)
            self._initialize_index()
            print(f"Pinecone 벡터 서비스 초기화 완료 - 인덱스: {self.index_name}")
        except Exception as e:
            print(f"Pinecone 초기화 실패: {e}")
            raise
    
    def _initialize_index(self):
        """Pinecone 인덱스 초기화 및 연결"""
        try:
            # 기존 인덱스 목록 확인
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"인덱스 '{self.index_name}'가 존재하지 않습니다. 새로 생성합니다...")
                # 인덱스 생성 (1536차원은 OpenAI text-embedding-3-small 모델 차원)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                print(f"인덱스 '{self.index_name}' 생성 완료")
            else:
                print(f"기존 인덱스 '{self.index_name}' 사용")
            
            # 인덱스 연결
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            print(f"Pinecone 인덱스 초기화 실패: {e}")
            raise
    
    async def save_chunk_vectors(self, chunks: List[Dict[str, Any]], embedding_service) -> List[str]:
        """
        여러 청크의 벡터를 Pinecone에 저장합니다.
        
        Args:
            chunks (List[Dict[str, Any]]): 청크 리스트
            embedding_service: 임베딩 서비스
            
        Returns:
            List[str]: 저장된 벡터 ID 리스트
        """
        print(f"[VectorService] === Pinecone 청크 벡터 저장 시작 ===")
        print(f"[VectorService] 저장할 청크 수: {len(chunks)}")
        
        stored_vector_ids = []
        vectors_to_upsert = []
        
        # 모든 청크에 대해 임베딩 생성
        for chunk in chunks:
            try:
                # 청크 텍스트로 문서 임베딩 생성
                embedding = await embedding_service.create_document_embedding(chunk["text"])
                
                if not embedding:
                    print(f"[VectorService] 청크 '{chunk['chunk_id']}' 임베딩 생성 실패")
                    continue
                
                # 문서 타입에 따라 적절한 ID 필드 선택
                document_id_key = None
                if "resume_id" in chunk:
                    document_id_key = "resume_id"
                elif "cover_letter_id" in chunk:
                    document_id_key = "cover_letter_id"  
                elif "portfolio_id" in chunk:
                    document_id_key = "portfolio_id"
                else:
                    document_id_key = "document_id"  # 기본값
                
                # Pinecone 벡터 데이터 구성
                vector_data = {
                    "id": chunk["chunk_id"],
                    "values": embedding,
                    "metadata": {
                        "document_id": chunk.get(document_id_key, chunk.get("document_id")),
                        "document_type": chunk["chunk_type"],
                        "chunk_type": chunk["chunk_type"],
                        "section": chunk["metadata"]["section"],
                        "original_field": chunk["metadata"].get("original_field", ""),
                        "item_index": chunk["metadata"].get("item_index", 0),
                        "text_preview": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"],
                        "created_at": datetime.now().isoformat()
                    }
                }
                
                vectors_to_upsert.append(vector_data)
                stored_vector_ids.append(chunk["chunk_id"])
                
                print(f"[VectorService] 청크 준비: {chunk['chunk_id']} ({chunk['chunk_type']}) - {len(chunk['text'])} 문자")
                
            except Exception as e:
                print(f"[VectorService] 청크 '{chunk['chunk_id']}' 처리 중 오류: {e}")
                continue
        
        # Pinecone에 배치 업로드
        if vectors_to_upsert:
            try:
                self.index.upsert(vectors=vectors_to_upsert)
                print(f"[VectorService] Pinecone 업로드 성공: {len(vectors_to_upsert)}개 벡터")
            except Exception as e:
                print(f"[VectorService] Pinecone 업로드 실패: {e}")
                stored_vector_ids = []  # 실패시 빈 리스트 반환
        
        print(f"[VectorService] 총 {len(stored_vector_ids)}개 청크 벡터 저장 완료")
        print(f"[VectorService] === Pinecone 청크 벡터 저장 완료 ===")
        
        return stored_vector_ids

    async def save_vector(self, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """
        단일 벡터를 Pinecone에 저장합니다.
        
        Args:
            embedding (List[float]): 임베딩 벡터
            metadata (Dict[str, Any]): 메타데이터
            
        Returns:
            Optional[str]: 저장된 벡터 ID
        """
        try:
            vector_id = f"vector_{int(time.time())}_{hash(str(metadata)) % 10000}"
            
            vector_data = {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            }
            
            self.index.upsert(vectors=[vector_data])
            
            print(f"[VectorService] Pinecone 벡터 저장 완료: {vector_id}")
            return vector_id
            
        except Exception as e:
            print(f"[VectorService] Pinecone 벡터 저장 실패: {e}")
            return None

    async def search_similar_vectors(self, query_embedding: List[float], 
                                   top_k: int = 5, 
                                   filter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Pinecone에서 유사한 벡터를 검색합니다.
        
        Args:
            query_embedding (List[float]): 쿼리 임베딩
            top_k (int): 반환할 최대 결과 수
            filter_type (Optional[str]): 필터 타입
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        try:
            print(f"[VectorService] Pinecone 검색 시작...")
            print(f"[VectorService] 검색 제한: {top_k}")
            print(f"[VectorService] 필터 타입: {filter_type}")
            
            # 필터 구성
            filter_dict = {}
            if filter_type:
                filter_dict["chunk_type"] = {"$eq": filter_type}
            
            # Pinecone 검색
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # 결과 포맷팅
            matches = []
            for match in search_results["matches"]:
                matches.append({
                    "id": match["id"],
                    "score": float(match["score"]),
                    "metadata": match.get("metadata", {})
                })
            
            print(f"[VectorService] Pinecone 검색 완료!")
            print(f"[VectorService] 검색 결과 수: {len(matches)}")
            
            return {"matches": matches}
            
        except Exception as e:
            print(f"[VectorService] Pinecone 검색 실패: {e}")
            return {"matches": []}

    async def delete_vectors_by_resume_id(self, resume_id: str) -> bool:
        """
        특정 이력서의 모든 벡터를 Pinecone에서 삭제합니다.
        
        Args:
            resume_id (str): 이력서 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            print(f"[VectorService] 이력서 '{resume_id}' 벡터 삭제 시작...")
            
            # Pinecone에서 해당 이력서의 벡터들을 필터로 삭제
            # 먼저 해당 벡터들을 검색해서 ID를 찾은 후 삭제
            filter_dict = {"resume_id": {"$eq": resume_id}}
            
            # 해당 이력서의 모든 벡터 검색 (매우 큰 top_k 사용)
            search_results = self.index.query(
                vector=[0.0] * 1536,  # 더미 벡터 (검색용)
                top_k=10000,  # 충분히 큰 수
                include_metadata=True,
                filter=filter_dict
            )
            
            # 찾은 벡터들의 ID 수집
            vector_ids_to_delete = [match["id"] for match in search_results["matches"]]
            
            if vector_ids_to_delete:
                # 벡터 삭제
                self.index.delete(ids=vector_ids_to_delete)
                print(f"[VectorService] Pinecone에서 {len(vector_ids_to_delete)}개 벡터 삭제 완료")
            else:
                print(f"[VectorService] 삭제할 벡터가 없습니다.")
            
            return True
            
        except Exception as e:
            print(f"[VectorService] Pinecone 벡터 삭제 실패: {e}")
            return False

    def get_index_info(self) -> Dict[str, Any]:
        """
        Pinecone 인덱스 상세 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 인덱스 정보
        """
        try:
            # Pinecone 인덱스 정보 가져오기
            index_info = self.pc.describe_index(self.index_name)
            
            return {
                "name": index_info.name,
                "dimension": index_info.dimension,
                "metric": index_info.metric,
                "host": index_info.host,
                "status": index_info.status,
                "spec": str(index_info.spec)
            }
        except Exception as e:
            print(f"인덱스 정보 조회 실패: {e}")
            return {"error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """
        Pinecone 벡터 저장소 통계를 반환합니다.
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        try:
            # Pinecone 인덱스 통계 가져오기
            index_stats = self.index.describe_index_stats()
            
            return {
                "total_vectors": index_stats.get("total_vector_count", 0),
                "index_name": self.index_name,
                "storage_type": "pinecone",
                "dimension": index_stats.get("dimension", 1536),
                "namespaces": index_stats.get("namespaces", {}),
                "environment": self.environment
            }
        except Exception as e:
            print(f"[VectorService] Pinecone 통계 조회 실패: {e}")
            return {
                "total_vectors": 0,
                "index_name": self.index_name,
                "storage_type": "pinecone",
                "error": str(e)
            }
