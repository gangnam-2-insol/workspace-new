import os
from sentence_transformers import SentenceTransformer
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmbeddingService:
    def __init__(self):
        """임베딩 서비스 초기화"""
        # 한국어 특화 모델로 업그레이드 (더 나은 한국어 의미 이해)
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("한국어 특화 임베딩 모델 초기화 완료 (paraphrase-multilingual-MiniLM-L12-v2)")
    
    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        텍스트로부터 임베딩 벡터를 생성합니다.
        
        Args:
            text (str): 임베딩을 생성할 텍스트
            
        Returns:
            Optional[List[float]]: 임베딩 벡터 (실패 시 None)
        """
        try:
            print(f"[EmbeddingService] === 임베딩 생성 시작 ===")
            print(f"[EmbeddingService] 입력 텍스트 길이: {len(text)} 문자")
            print(f"[EmbeddingService] 입력 텍스트 미리보기: {text[:100]}...")
            
            # Sentence Transformers를 사용한 임베딩 생성
            embedding = self.model.encode(text)
            
            print(f"[EmbeddingService] 임베딩 생성 성공!")
            print(f"[EmbeddingService] 임베딩 차원: {len(embedding)}")
            print(f"[EmbeddingService] 임베딩 값 미리보기: {embedding[:5].tolist()}...")
            print(f"[EmbeddingService] === 임베딩 생성 완료 ===")
            
            return embedding.tolist()  # numpy array를 list로 변환
        except Exception as e:
            print(f"[EmbeddingService] === 임베딩 생성 실패 ====")
            print(f"[EmbeddingService] 오류 메시지: {e}")
            print(f"[EmbeddingService] 입력 텍스트: {text[:200]}...")
            print(f"[EmbeddingService] === 임베딩 생성 실패 완료 ===")
            return None
    
    def get_embedding_dimension(self) -> int:
        """임베딩 벡터의 차원을 반환합니다."""
        return 384  # paraphrase-multilingual-MiniLM-L12-v2도 384차원
