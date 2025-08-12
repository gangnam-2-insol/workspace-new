import os
import asyncio
import time
from pinecone import Pinecone, ServerlessSpec
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class VectorService:
    def __init__(self, api_key: str, index_name: str = "resume-vectors"):
        """
        벡터 서비스 초기화
        
        Args:
            api_key (str): Pinecone API 키
            index_name (str): 인덱스 이름
        """
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Pinecone 인덱스를 초기화합니다."""
        try:
            self.index = self.pc.Index(self.index_name)
            print(f"Pinecone 인덱스 '{self.index_name}' 연결 성공")
        except Exception as e:
            print(f"인덱스 '{self.index_name}'을 찾을 수 없습니다. 새로 생성합니다...")
            try:
                # 인덱스 생성 (all-MiniLM-L6-v2는 384차원)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"인덱스 '{self.index_name}'이 성공적으로 생성되었습니다.")
                self.index = self.pc.Index(self.index_name)
            except Exception as create_error:
                print(f"인덱스 생성 실패: {create_error}")
                # 인덱스 생성에 실패해도 서버는 계속 실행
                self.index = None
    
    async def save_chunk_vectors(self, chunks: List[Dict[str, Any]], embedding_service) -> List[str]:
        """
        여러 청크의 벡터를 Pinecone에 저장합니다.
        
        Args:
            chunks (List[Dict[str, Any]]): 청크 리스트
            embedding_service: 임베딩 서비스
            
        Returns:
            List[str]: 저장된 벡터 ID 리스트
        """
        print(f"[VectorService] === 청크 벡터 저장 시작 ===")
        print(f"[VectorService] 저장할 청크 수: {len(chunks)}")
        
        if self.index is None:
            print("[VectorService] Pinecone 인덱스가 없어 벡터를 저장할 수 없습니다.")
            return []
        
        stored_vector_ids = []
        vectors_to_upsert = []
        
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
                    "id": chunk["chunk_id"],
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
                
                vectors_to_upsert.append(vector_data)
                stored_vector_ids.append(chunk["chunk_id"])
                
                print(f"[VectorService] 청크 준비: {chunk['chunk_id']} ({chunk['chunk_type']}) - {len(chunk['text'])} 문자")
                
            except Exception as e:
                print(f"[VectorService] 청크 '{chunk['chunk_id']}' 처리 중 오류: {e}")
                continue
        
        # 배치로 모든 벡터 저장
        if vectors_to_upsert:
            try:
                print(f"[VectorService] {len(vectors_to_upsert)}개 벡터 배치 저장 시작...")
                self.index.upsert(vectors=vectors_to_upsert)
                print(f"[VectorService] 배치 저장 성공!")
                
                # 인덱싱 완료 대기
                print(f"[VectorService] 인덱싱 완료 대기 중...")
                await self._wait_for_batch_indexing(stored_vector_ids)
                print(f"[VectorService] 인덱싱 완료")
                
            except Exception as e:
                print(f"[VectorService] 배치 저장 실패: {e}")
                return []
        
        print(f"[VectorService] === 청크 벡터 저장 완료 ({len(stored_vector_ids)}개) ===")
        return stored_vector_ids

    async def save_vector(self, embedding: List[float], metadata: Dict[str, Any]) -> Optional[str]:
        """
        벡터를 Pinecone에 저장합니다.
        
        Args:
            embedding (List[float]): 저장할 임베딩 벡터
            metadata (Dict[str, Any]): 벡터와 함께 저장할 메타데이터
            
        Returns:
            Optional[str]: 저장된 벡터의 ID (실패 시 None)
        """
        print(f"[VectorService] === Pinecone 벡터 저장 시작 ===")
        print(f"[VectorService] 메타데이터: {metadata}")
        
        if self.index is None:
            print("[VectorService] Pinecone 인덱스가 없어 벡터를 저장할 수 없습니다.")
            print(f"[VectorService] === Pinecone 벡터 저장 실패 (인덱스 없음) ===")
            return None
        
        try:
            vector_id = f"resume_{metadata['resume_id']}_{metadata['type']}"
            vector_data = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "type": metadata["type"],
                    "resume_id": str(metadata["resume_id"]),
                    "name": metadata["name"],
                    "email": metadata["email"],
                    "created_at": datetime.now().isoformat()
                }
            }
            
            print(f"[VectorService] 저장할 벡터 ID: {vector_id}")
            print(f"[VectorService] 벡터 차원: {len(embedding)}")
            print(f"[VectorService] 메타데이터 타입: {metadata['type']}")
            print(f"[VectorService] 이력서 ID: {metadata['resume_id']}")
            print(f"[VectorService] 이름: {metadata['name']}")
            print(f"[VectorService] 이메일: {metadata['email']}")
            
            self.index.upsert(vectors=[vector_data])
            print(f"[VectorService] 벡터가 Pinecone에 성공적으로 저장되었습니다!")
            print(f"[VectorService] 저장된 벡터 ID: {vector_id}")
            
            # Pinecone 인덱싱 완료 대기 및 확인
            print(f"[VectorService] Pinecone 인덱싱 대기 및 확인 중...")
            await self._wait_for_indexing(vector_id)
            print(f"[VectorService] 인덱싱 확인 완료")
            
            print(f"[VectorService] === Pinecone 벡터 저장 완료 ===")
            return vector_id
        except Exception as e:
            print(f"[VectorService] === Pinecone 벡터 저장 실패 ===")
            print(f"[VectorService] 오류 메시지: {e}")
            print(f"[VectorService] 메타데이터: {metadata}")
            print(f"[VectorService] 임베딩 차원: {len(embedding) if embedding else 'None'}")
            print(f"[VectorService] === Pinecone 벡터 저장 실패 완료 ===")
            return None
    
    async def search_similar_vectors(self, query_embedding: List[float], 
                                   top_k: int = 5, 
                                   filter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        유사한 벡터를 검색합니다.
        
        Args:
            query_embedding (List[float]): 검색할 쿼리 임베딩
            top_k (int): 반환할 최대 결과 수
            filter_type (Optional[str]): 필터링할 타입 (예: "resume", "cover_letter")
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        if self.index is None:
            print("[VectorService] Pinecone 인덱스가 없어 검색할 수 없습니다.")
            return {"matches": []}
        
        try:
            print(f"[VectorService] Pinecone 검색 시작...")
            print(f"[VectorService] 검색 제한: {top_k}")
            print(f"[VectorService] 필터 타입: {filter_type}")
            
            # 검색 파라미터 설정
            search_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            # 타입 필터가 있으면 추가
            if filter_type:
                search_params["filter"] = {"type": filter_type}
            
            search_result = self.index.query(**search_params)
            
            print(f"[VectorService] Pinecone 검색 완료!")
            print(f"[VectorService] 검색 결과 수: {len(search_result['matches'])}")
            
            return search_result
        except Exception as e:
            print(f"[VectorService] Pinecone 검색 실패: {e}")
            return {"matches": []}
    
    async def delete_vectors_by_resume_id(self, resume_id: str) -> bool:
        """
        특정 이력서 ID와 관련된 모든 벡터를 삭제합니다.
        
        Args:
            resume_id (str): 삭제할 이력서 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        if self.index is None:
            print("Pinecone 인덱스가 없어 벡터를 삭제할 수 없습니다.")
            return False
        
        try:
            vectors_to_delete = [
                f"resume_{resume_id}_resume",
                f"resume_{resume_id}_cover_letter",
                f"resume_{resume_id}_portfolio"
            ]
            self.index.delete(ids=vectors_to_delete)
            print(f"이력서 ID {resume_id}의 벡터들이 성공적으로 삭제되었습니다.")
            return True
        except Exception as e:
            print(f"Pinecone 벡터 삭제 중 오류: {e}")
            return False
    
    async def _wait_for_indexing(self, vector_id: str, max_wait_time: int = 10, check_interval: float = 1.0):
        """
        Pinecone 인덱싱이 완료될 때까지 대기합니다.
        
        Args:
            vector_id (str): 확인할 벡터 ID
            max_wait_time (int): 최대 대기 시간 (초)
            check_interval (float): 확인 간격 (초)
        """
        print(f"[VectorService] 벡터 '{vector_id}' 인덱싱 확인 시작...")
        
        start_time = time.time()
        attempt = 0
        
        while (time.time() - start_time) < max_wait_time:
            attempt += 1
            try:
                # 벡터가 검색 가능한지 확인
                fetch_result = self.index.fetch(ids=[vector_id])
                
                if vector_id in fetch_result.get('vectors', {}):
                    elapsed = time.time() - start_time
                    print(f"[VectorService] 인덱싱 확인 완료! (시도: {attempt}, 소요시간: {elapsed:.1f}초)")
                    return True
                else:
                    print(f"[VectorService] 인덱싱 대기 중... (시도: {attempt})")
                    await asyncio.sleep(check_interval)
                    
            except Exception as e:
                print(f"[VectorService] 인덱싱 확인 중 오류 (시도 {attempt}): {e}")
                await asyncio.sleep(check_interval)
        
        print(f"[VectorService] 인덱싱 확인 시간 초과 ({max_wait_time}초), 계속 진행...")
        return False
    
    async def _wait_for_batch_indexing(self, vector_ids: List[str], max_wait_time: int = 15, check_interval: float = 2.0):
        """
        배치 벡터들의 인덱싱이 완료될 때까지 대기합니다.
        
        Args:
            vector_ids (List[str]): 확인할 벡터 ID 리스트
            max_wait_time (int): 최대 대기 시간 (초)
            check_interval (float): 확인 간격 (초)
        """
        print(f"[VectorService] {len(vector_ids)}개 벡터 배치 인덱싱 확인 시작...")
        
        start_time = time.time()
        attempt = 0
        
        while (time.time() - start_time) < max_wait_time:
            attempt += 1
            try:
                # 샘플 벡터들이 검색 가능한지 확인 (전체가 아닌 일부만)
                sample_ids = vector_ids[:min(3, len(vector_ids))]  # 최대 3개만 확인
                fetch_result = self.index.fetch(ids=sample_ids)
                
                found_count = len(fetch_result.get('vectors', {}))
                if found_count >= len(sample_ids):
                    elapsed = time.time() - start_time
                    print(f"[VectorService] 배치 인덱싱 확인 완료! (시도: {attempt}, 소요시간: {elapsed:.1f}초)")
                    return True
                else:
                    print(f"[VectorService] 배치 인덱싱 대기 중... (시도: {attempt}, {found_count}/{len(sample_ids)} 준비됨)")
                    await asyncio.sleep(check_interval)
                    
            except Exception as e:
                print(f"[VectorService] 배치 인덱싱 확인 중 오류 (시도 {attempt}): {e}")
                await asyncio.sleep(check_interval)
        
        print(f"[VectorService] 배치 인덱싱 확인 시간 초과 ({max_wait_time}초), 계속 진행...")
        return False
