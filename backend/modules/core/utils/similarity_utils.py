import math
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

import numpy as np


class SimilarityUtils:
    """유사도 계산 유틸리티"""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        코사인 유사도 계산

        Args:
            vec1: 첫 번째 벡터
            vec2: 두 번째 벡터

        Returns:
            float: 코사인 유사도 (0~1)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """
        자카드 유사도 계산

        Args:
            set1: 첫 번째 집합
            set2: 두 번째 집합

        Returns:
            float: 자카드 유사도 (0~1)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def text_similarity(text1: str, text2: str) -> float:
        """
        텍스트 유사도 계산 (SequenceMatcher 사용)

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트

        Returns:
            float: 텍스트 유사도 (0~1)
        """
        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(None, text1, text2).ratio()

    @staticmethod
    def extract_keywords(text: str, min_length: int = 2) -> List[str]:
        """
        텍스트에서 키워드 추출

        Args:
            text: 텍스트
            min_length: 최소 키워드 길이

        Returns:
            List[str]: 키워드 리스트
        """
        if not text:
            return []

        # 특수문자 제거 및 소문자 변환
        text = re.sub(r'[^\w\s]', ' ', text.lower())

        # 단어 분리
        words = text.split()

        # 길이 필터링 및 빈도 계산
        word_counts = Counter([word for word in words if len(word) >= min_length])

        # 상위 키워드 반환 (빈도순)
        return [word for word, count in word_counts.most_common(20)]

    @staticmethod
    def calculate_field_similarity(doc1: Dict[str, Any], doc2: Dict[str, Any],
                                 field_name: str) -> float:
        """
        특정 필드의 유사도 계산

        Args:
            doc1: 첫 번째 문서
            doc2: 두 번째 문서
            field_name: 필드명

        Returns:
            float: 필드 유사도 (0~1)
        """
        field1 = str(doc1.get(field_name, ""))
        field2 = str(doc2.get(field_name, ""))

        if not field1 or not field2:
            return 0.0

        # 키워드 기반 유사도
        keywords1 = set(SimilarityUtils.extract_keywords(field1))
        keywords2 = set(SimilarityUtils.extract_keywords(field2))
        keyword_similarity = SimilarityUtils.jaccard_similarity(keywords1, keywords2)

        # 텍스트 기반 유사도
        text_similarity = SimilarityUtils.text_similarity(field1, field2)

        # 가중 평균 (키워드 60%, 텍스트 40%)
        return keyword_similarity * 0.6 + text_similarity * 0.4

    @staticmethod
    def normalize_similarity_score(score: float, min_score: float = 0.0,
                                 max_score: float = 1.0) -> float:
        """
        유사도 점수 정규화

        Args:
            score: 원본 점수
            min_score: 최소 점수
            max_score: 최대 점수

        Returns:
            float: 정규화된 점수 (0~1)
        """
        if max_score == min_score:
            return 0.0

        normalized = (score - min_score) / (max_score - min_score)
        return max(0.0, min(1.0, normalized))

    @staticmethod
    def classify_similarity_level(score: float) -> str:
        """
        유사도 점수를 레벨로 분류

        Args:
            score: 유사도 점수 (0~1)

        Returns:
            str: 유사도 레벨 (HIGH/MEDIUM/LOW)
        """
        if score >= 0.8:
            return "HIGH"
        elif score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def calculate_weighted_similarity(scores: Dict[str, float],
                                    weights: Dict[str, float]) -> float:
        """
        가중 유사도 계산

        Args:
            scores: 각 필드별 유사도 점수
            weights: 각 필드별 가중치

        Returns:
            float: 가중 평균 유사도
        """
        if not scores or not weights:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for field, score in scores.items():
            weight = weights.get(field, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def find_duplicate_chunks(chunks: List[Dict[str, Any]],
                            similarity_threshold: float = 0.9) -> List[Tuple[int, int]]:
        """
        중복 청크 찾기

        Args:
            chunks: 청크 리스트
            similarity_threshold: 유사도 임계값

        Returns:
            List[Tuple[int, int]]: 중복 청크 인덱스 쌍
        """
        duplicates = []

        for i in range(len(chunks)):
            for j in range(i + 1, len(chunks)):
                content1 = chunks[i].get('content', '')
                content2 = chunks[j].get('content', '')

                similarity = SimilarityUtils.text_similarity(content1, content2)

                if similarity >= similarity_threshold:
                    duplicates.append((i, j))

        return duplicates

    @staticmethod
    def merge_similar_chunks(chunks: List[Dict[str, Any]],
                           similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        유사한 청크 병합

        Args:
            chunks: 청크 리스트
            similarity_threshold: 유사도 임계값

        Returns:
            List[Dict[str, Any]]: 병합된 청크 리스트
        """
        if not chunks:
            return []

        merged_chunks = []
        used_indices = set()

        for i, chunk1 in enumerate(chunks):
            if i in used_indices:
                continue

            similar_chunks = [chunk1]
            used_indices.add(i)

            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                if j in used_indices:
                    continue

                content1 = chunk1.get('content', '')
                content2 = chunk2.get('content', '')

                similarity = SimilarityUtils.text_similarity(content1, content2)

                if similarity >= similarity_threshold:
                    similar_chunks.append(chunk2)
                    used_indices.add(j)

            # 유사한 청크들을 하나로 병합
            if len(similar_chunks) > 1:
                merged_content = ' '.join([chunk.get('content', '') for chunk in similar_chunks])
                merged_metadata = {}

                # 메타데이터 병합
                for chunk in similar_chunks:
                    for key, value in chunk.get('metadata', {}).items():
                        if key not in merged_metadata:
                            merged_metadata[key] = value
                        elif isinstance(merged_metadata[key], list):
                            if isinstance(value, list):
                                merged_metadata[key].extend(value)
                            else:
                                merged_metadata[key].append(value)

                merged_chunk = {
                    'content': merged_content,
                    'metadata': merged_metadata,
                    'merged_from': [chunk.get('chunk_id', '') for chunk in similar_chunks]
                }
                merged_chunks.append(merged_chunk)
            else:
                merged_chunks.append(chunk1)

        return merged_chunks
