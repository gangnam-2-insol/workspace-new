import os
import asyncio
import time
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from sklearn.metrics.pairwise import cosine_similarity

class VectorService:
    def __init__(self, api_key: str = None, index_name: str = "resume-vectors"):
        """
        로컬 메모리 기반 벡터 서비스 초기화
        
        Args:
            api_key (str): 사용하지 않음 (호환성을 위해 유지)
            index_name (str): 인덱스 이름 (사용하지 않음, 호환성을 위해 유지)
        """
        self.index_name = index_name
        # 메모리에 벡터 저장소
        self.vectors = {}  # {vector_id: {"values": embedding, "metadata": metadata}}
        self.vector_ids = []  # 순서 유지를 위한 ID 리스트
        print(f"로컬 메모리 기반 벡터 서비스 초기화 완료")
    
    def _initialize_index(self):
        """로컬 인덱스 초기화 (Pinecone 대신 메모리 사용)"""
        print(f"로컬 메모리 기반 벡터 인덱스 '{self.index_name}' 초기화 완료")
    
    async def save_chunk_vectors(self, chunks: List[Dict[str, Any]], embedding_service) -> List[str]:
        """
        여러 청크의 벡터를 로컬 메모리에 저장합니다.
        
        Args:
            chunks (List[Dict[str, Any]]): 청크 리스트
            embedding_service: 임베딩 서비스
            
        Returns:
            List[str]: 저장된 벡터 ID 리스트
        """
        print(f"[VectorService] === 로컬 메모리 청크 벡터 저장 시작 ===")
        print(f"[VectorService] 저장할 청크 수: {len(chunks)}")
        
        stored_vector_ids = []
        
        # 모든 청크에 대해 임베딩 생성
        for chunk in chunks:
            try:
                # 청크 텍스트로 임베딩 생성
                embedding = await embedding_service.create_embedding(chunk["text"])
                
                if not embedding:
                    print(f"[VectorService] 청크 '{chunk['chunk_id']}' 임베딩 생성 실패")
                    continue
                
                # 벡터 데이터 구성
                vector_data = {
                    "values": embedding,
                    "metadata": {
                        "resume_id": chunk["resume_id"],
                        "chunk_type": chunk["chunk_type"],
                        "section": chunk["metadata"]["section"],
                        "original_field": chunk["metadata"].get("original_field", ""),
                        "item_index": chunk["metadata"].get("item_index", 0),
                        "text_preview": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"],
                        "created_at": datetime.now().isoformat()
                    }
                }
                
                # 메모리에 저장
                self.vectors[chunk["chunk_id"]] = vector_data
                self.vector_ids.append(chunk["chunk_id"])
                stored_vector_ids.append(chunk["chunk_id"])
                
                print(f"[VectorService] 청크 저장: {chunk['chunk_id']} ({chunk['chunk_type']}) - {len(chunk['text'])} 문자")
                
            except Exception as e:
                print(f"[VectorService] 청크 '{chunk['chunk_id']}' 처리 중 오류: {e}")
                continue
        
        print(f"[VectorService] 총 {len(stored_vector_ids)}개 청크 벡터 저장 완료")
        print(f"[VectorService] === 로컬 메모리 청크 벡터 저장 완료 ===")
        
        return stored_vector_ids

    async def save_vector(self, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """
        단일 벡터를 로컬 메모리에 저장합니다.
        
        Args:
            embedding (List[float]): 임베딩 벡터
            metadata (Dict[str, Any]): 메타데이터
            
        Returns:
            Optional[str]: 저장된 벡터 ID
        """
        try:
            vector_id = f"vector_{len(self.vectors)}_{int(time.time())}"
            
            vector_data = {
                "values": embedding,
                "metadata": metadata
            }
            
            self.vectors[vector_id] = vector_data
            self.vector_ids.append(vector_id)
            
            print(f"[VectorService] 벡터 저장 완료: {vector_id}")
            return vector_id
            
        except Exception as e:
            print(f"[VectorService] 벡터 저장 실패: {e}")
            return None

    async def search_similar_vectors(self, query_embedding: List[float], 
                                   top_k: int = 5, 
                                   filter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        로컬 메모리에서 유사한 벡터를 검색합니다.
        
        Args:
            query_embedding (List[float]): 쿼리 임베딩
            top_k (int): 반환할 최대 결과 수
            filter_type (Optional[str]): 필터 타입
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        if not self.vectors:
            print("[VectorService] 저장된 벡터가 없습니다.")
            return {"matches": []}
        
        try:
            print(f"[VectorService] 로컬 메모리 검색 시작...")
            print(f"[VectorService] 검색 제한: {top_k}")
            print(f"[VectorService] 필터 타입: {filter_type}")
            
            # 쿼리 임베딩을 numpy 배열로 변환
            query_array = np.array(query_embedding).reshape(1, -1)
            
            # 모든 저장된 벡터와 유사도 계산
            similarities = []
            for vector_id, vector_data in self.vectors.items():
                # 필터 타입이 있으면 확인
                if filter_type and vector_data["metadata"].get("chunk_type") != filter_type:
                    continue
                
                # 벡터를 numpy 배열로 변환
                stored_vector = np.array(vector_data["values"]).reshape(1, -1)
                
                # 코사인 유사도 계산
                similarity = cosine_similarity(query_array, stored_vector)[0][0]
                
                similarities.append({
                    "id": vector_id,
                    "score": float(similarity),
                    "metadata": vector_data["metadata"]
                })
            
            # 유사도 기준으로 정렬
            similarities.sort(key=lambda x: x["score"], reverse=True)
            
            # top_k개 결과 반환
            top_results = similarities[:top_k]
            
            print(f"[VectorService] 로컬 메모리 검색 완료!")
            print(f"[VectorService] 검색 결과 수: {len(top_results)}")
            
            return {"matches": top_results}
            
        except Exception as e:
            print(f"[VectorService] 로컬 메모리 검색 실패: {e}")
            return {"matches": []}

    async def delete_vectors_by_resume_id(self, resume_id: str) -> bool:
        """
        특정 이력서의 모든 벡터를 삭제합니다.
        
        Args:
            resume_id (str): 이력서 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            print(f"[VectorService] 이력서 '{resume_id}' 벡터 삭제 시작...")
            
            # 해당 이력서의 벡터들 찾기
            vectors_to_delete = []
            for vector_id, vector_data in self.vectors.items():
                if vector_data["metadata"].get("resume_id") == resume_id:
                    vectors_to_delete.append(vector_id)
            
            # 벡터 삭제
            for vector_id in vectors_to_delete:
                del self.vectors[vector_id]
                if vector_id in self.vector_ids:
                    self.vector_ids.remove(vector_id)
            
            print(f"[VectorService] 총 {len(vectors_to_delete)}개 벡터 삭제 완료")
            return True
            
        except Exception as e:
            print(f"[VectorService] 벡터 삭제 실패: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        벡터 저장소 통계를 반환합니다.
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        return {
            "total_vectors": len(self.vectors),
            "index_name": self.index_name,
            "storage_type": "local_memory"
        }
