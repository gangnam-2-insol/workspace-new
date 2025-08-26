import os
from sentence_transformers import SentenceTransformer
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import openai

class EmbeddingType(Enum):
    QUERY = "query"
    DOCUMENT = "document"

class EmbeddingService:
    def __init__(self):
        """임베딩 서비스 초기화"""
        # OpenAI API 키 설정
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        # OpenAI 클라이언트 초기화
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # 백업용 SentenceTransformer 모델 (OpenAI 실패 시 사용)
        self.fallback_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("OpenAI text-embedding-3-small 모델 초기화 완료 (1536차원, 한국어 지원)")
    
    async def create_embedding(self, text: str, embedding_type: EmbeddingType = EmbeddingType.DOCUMENT) -> Optional[List[float]]:
        """
        텍스트로부터 임베딩 벡터를 생성합니다.
        
        Args:
            text (str): 임베딩을 생성할 텍스트
            embedding_type (EmbeddingType): 임베딩 타입 (쿼리 또는 문서)
            
        Returns:
            Optional[List[float]]: 임베딩 벡터 (실패 시 None)
        """
        try:
            print(f"[EmbeddingService] === 임베딩 생성 시작 ===")
            print(f"[EmbeddingService] 임베딩 타입: {embedding_type.value}")
            print(f"[EmbeddingService] 입력 텍스트 길이: {len(text)} 문자")
            print(f"[EmbeddingService] 입력 텍스트 미리보기: {text[:100]}...")
            
            # 임베딩 타입에 따른 전처리
            processed_text = self._preprocess_text(text, embedding_type)
            
            # OpenAI API를 사용한 임베딩 생성
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=processed_text
                )
                embedding = response.data[0].embedding
                
                print(f"[EmbeddingService] OpenAI 임베딩 생성 성공!")
                print(f"[EmbeddingService] 임베딩 차원: {len(embedding)}")
                print(f"[EmbeddingService] 임베딩 값 미리보기: {embedding[:5]}...")
                print(f"[EmbeddingService] === 임베딩 생성 완료 ===")
                
                return embedding
                
            except Exception as openai_error:
                print(f"[EmbeddingService] OpenAI 임베딩 실패, 백업 모델 사용: {openai_error}")
                
                # 백업 모델 사용 (SentenceTransformer)
                embedding = self.fallback_model.encode(processed_text)
                
                print(f"[EmbeddingService] 백업 임베딩 생성 성공!")
                print(f"[EmbeddingService] 임베딩 차원: {len(embedding)}")
                print(f"[EmbeddingService] 임베딩 값 미리보기: {embedding[:5].tolist()}...")
                print(f"[EmbeddingService] === 백업 임베딩 생성 완료 ===")
                
                return embedding.tolist()  # numpy array를 list로 변환
        except Exception as e:
            print(f"[EmbeddingService] === 임베딩 생성 실패 ====")
            print(f"[EmbeddingService] 오류 메시지: {e}")
            print(f"[EmbeddingService] 입력 텍스트: {text[:200]}...")
            print(f"[EmbeddingService] === 임베딩 생성 실패 완료 ===")
            return None
    
    def _preprocess_text(self, text: str, embedding_type: EmbeddingType) -> str:
        """
        임베딩 타입에 따른 텍스트 전처리를 수행합니다.
        
        Args:
            text (str): 원본 텍스트
            embedding_type (EmbeddingType): 임베딩 타입
            
        Returns:
            str: 전처리된 텍스트
        """
        if embedding_type == EmbeddingType.QUERY:
            # 쿼리용 전처리: 질문 형태로 변환
            if not text.strip().endswith('?'):
                processed_text = f"질문: {text.strip()}"
            else:
                processed_text = f"질문: {text.strip()}"
        else:
            # 문서용 전처리: 문서 내용임을 명시
            processed_text = f"문서: {text.strip()}"
        
        print(f"[EmbeddingService] 전처리 결과: {processed_text[:100]}...")
        return processed_text
    
    async def create_query_embedding(self, text: str) -> Optional[List[float]]:
        """쿼리용 임베딩을 생성합니다."""
        return await self.create_embedding(text, EmbeddingType.QUERY)
    
    async def create_document_embedding(self, text: str) -> Optional[List[float]]:
        """문서용 임베딩을 생성합니다."""
        return await self.create_embedding(text, EmbeddingType.DOCUMENT)
    
    def get_embedding_dimension(self) -> int:
        """임베딩 벡터의 차원을 반환합니다."""
        return 384  # paraphrase-multilingual-MiniLM-L12-v2도 384차원
