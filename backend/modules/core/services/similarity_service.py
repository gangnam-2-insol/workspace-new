import asyncio
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.collection import Collection

from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .keyword_search_service import KeywordSearchService
from .llm_service import LLMService
from .vector_service import VectorService

try:
    from modules.ai.services.langchain_hybrid_service import LangChainHybridService
    LANGCHAIN_HYBRID_AVAILABLE = True
except ImportError:
    LANGCHAIN_HYBRID_AVAILABLE = False
    print("LangChain 하이브리드 서비스를 사용할 수 없습니다.")

class SimilarityService:
    def __init__(self, embedding_service: EmbeddingService, vector_service: VectorService):
        """
        유사도 검색 서비스 초기화

        Args:
            embedding_service (EmbeddingService): 임베딩 서비스
            vector_service (VectorService): 벡터 서비스
        """
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.chunking_service = ChunkingService()
        self.llm_service = LLMService()
        self.keyword_search_service = KeywordSearchService()

        # MongoService import 추가
        from .mongo_service import MongoService
        self.mongo_service = MongoService()

        # LangChain 하이브리드 서비스 초기화
        self.langchain_hybrid = None
        if LANGCHAIN_HYBRID_AVAILABLE:
            try:
                self.langchain_hybrid = LangChainHybridService()
                print("[SimilarityService] LangChain 하이브리드 서비스 활성화")
            except Exception as e:
                print(f"[SimilarityService] LangChain 하이브리드 서비스 초기화 실패: {e}")

        # 유사도 임계값 설정
        self.similarity_threshold = 0.3   # 30%로 설정
        # 필드별 최소 유사도 임계값 (성장배경, 지원동기, 경력사항만 사용)
        self.field_thresholds = {
            'growthBackground': 0.2,   # 성장배경 20% 이상
            'motivation': 0.2,         # 지원동기 20% 이상
            'careerHistory': 0.2,      # 경력사항 20% 이상
        }

        # 다중 검색 가중치 설정 (벡터 + 키워드)
        self.search_weights = {
            'vector': 0.5,    # 벡터 검색 50%
            'keyword': 0.5    # 키워드 검색 50%
        }

    async def save_resume_chunks(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        이력서를 청킹하여 벡터 저장하고 Elasticsearch에 인덱싱합니다.

        Args:
            resume (Dict[str, Any]): 이력서 데이터

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            print(f"[SimilarityService] === 청킹 기반 벡터 저장 시작 ===")
            resume_id = str(resume["_id"])

            # 이력서를 청크로 분할
            chunks = self.chunking_service.chunk_resume_text(resume)

            if not chunks:
                return {
                    "success": False,
                    "error": "생성된 청크가 없습니다.",
                    "chunks_count": 0
                }

            # 청크별 벡터 저장
            stored_vector_ids = await self.vector_service.save_chunk_vectors(chunks, self.embedding_service)

            # Elasticsearch에 이력서 인덱싱
            try:
                es_result = await self.keyword_search_service.index_document(resume)
                if es_result["success"]:
                    print(f"[SimilarityService] Elasticsearch 인덱싱 성공: {resume_id}")
                else:
                    print(f"[SimilarityService] Elasticsearch 인덱싱 실패: {es_result.get('message', 'Unknown error')}")
            except Exception as es_error:
                print(f"[SimilarityService] Elasticsearch 인덱싱 중 오류: {str(es_error)}")

            print(f"[SimilarityService] 총 {len(stored_vector_ids)}개 청크 벡터 저장 완료")
            print(f"[SimilarityService] === 청킹 기반 벡터 저장 완료 ===")

            return {
                "success": True,
                "resume_id": resume_id,
                "chunks_count": len(chunks),
                "stored_vectors": len(stored_vector_ids),
                "vector_ids": stored_vector_ids
            }

        except Exception as e:
            print(f"[SimilarityService] 청킹 기반 벡터 저장 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks_count": 0
            }

    async def find_similar_documents_by_chunks(self, document_id: str, collection: Collection,
                                            document_type: str = "resume", limit: int = 5) -> Dict[str, Any]:
        """
        청킹 기반으로 특정 문서와 유사한 문서들을 찾습니다.

        Args:
            document_id (str): 기준이 되는 문서 ID
            collection (Collection): MongoDB 컬렉션
            document_type (str): 문서 타입 ("resume", "cover_letter", "portfolio")
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 유사도 검색 결과
        """
        try:
            print(f"[SimilarityService] === 청킹 기반 유사도 검색 시작 ===")
            print(f"[SimilarityService] 문서 ID: {document_id}")
            print(f"[SimilarityService] 문서 타입: {document_type}")

            # 해당 문서 조회
            document = await collection.find_one({"_id": ObjectId(document_id)})
            if not document:
                raise ValueError(f"{document_type}을(를) 찾을 수 없습니다.")

            # 문서 타입에 따른 청킹
            if document_type == "cover_letter":
                query_chunks = self.chunking_service.chunk_cover_letter(document)
            elif document_type == "portfolio":
                query_chunks = self.chunking_service.chunk_portfolio(document)
            else:  # resume
                query_chunks = self.chunking_service.chunk_resume_text(document)

            if not query_chunks:
                raise ValueError("검색할 청크가 없습니다.")

            print(f"[SimilarityService] 검색 청크 수: {len(query_chunks)}")

            # 각 청크별로 유사 벡터 검색
            chunk_similarities = {}
            for chunk in query_chunks:
                print(f"[SimilarityService] 청크 '{chunk['chunk_type']}' 검색 중...")

                # 청크 텍스트로 쿼리 임베딩 생성
                query_embedding = await self.embedding_service.create_query_embedding(chunk["text"])
                if not query_embedding:
                    continue

                # Pinecone에서 유사한 벡터 검색
                search_result = await self.vector_service.search_similar_vectors(
                    query_embedding=query_embedding,
                    top_k=limit * 3,  # 청크별로 더 많이 검색
                    filter_type=document_type
                )

                # 결과 저장
                for match in search_result["matches"]:
                    match_document_id = match["metadata"]["resume_id"]  # 메타데이터 키명은 벡터 서비스 확인 필요
                    similarity_score = match["score"]
                    chunk_type = match["metadata"]["chunk_type"]

                    # 자기 자신 제외
                    if match_document_id == document_id:
                        continue

                    # 문서별로 청크 유사도 누적
                    if match_document_id not in chunk_similarities:
                        chunk_similarities[match_document_id] = {
                            "chunks": {},
                            "total_score": 0.0,
                            "chunk_count": 0
                        }

                    # 동일한 청크 타입에서 더 높은 점수만 유지
                    key = f"{chunk['chunk_type']}_to_{chunk_type}"
                    if key not in chunk_similarities[match_document_id]["chunks"] or \
                       similarity_score > chunk_similarities[match_document_id]["chunks"][key]["score"]:

                        chunk_similarities[match_document_id]["chunks"][key] = {
                            "score": similarity_score,
                            "query_chunk": chunk['chunk_type'],
                            "match_chunk": chunk_type,
                            "match_text": match["metadata"].get("text_preview", "")
                        }

            # 문서별 종합 점수 계산
            document_scores = []
            for match_document_id, data in chunk_similarities.items():
                if not data["chunks"]:
                    continue

                # 청크 점수들의 평균 계산
                chunk_scores = [chunk_data["score"] for chunk_data in data["chunks"].values()]
                avg_score = sum(chunk_scores) / len(chunk_scores)

                # 임계값 체크
                if avg_score >= self.similarity_threshold:
                    document_scores.append({
                        "document_id": match_document_id,
                        "similarity_score": avg_score,
                        "chunk_matches": len(data["chunks"]),
                        "chunk_details": data["chunks"]
                    })

            # 점수 순으로 정렬
            document_scores.sort(key=lambda x: x["similarity_score"], reverse=True)
            document_scores = document_scores[:limit]

            # MongoDB에서 상세 정보 조회
            results = []
            if document_scores:
                document_ids = [ObjectId(score["document_id"]) for score in document_scores]
                documents_detail = await collection.find({"_id": {"$in": document_ids}}).to_list(1000)

                for score_data in document_scores:
                    document_detail = next((d for d in documents_detail if str(d["_id"]) == score_data["document_id"]), None)
                    if document_detail:
                        document_detail["_id"] = str(document_detail["_id"])
                        if "created_at" in document_detail:
                            document_detail["created_at"] = document_detail["created_at"].isoformat()

                        # LLM을 통한 유사성 분석 추가
                        llm_analysis = await self.llm_service.analyze_similarity_reasoning(
                            original_resume=document,
                            similar_resume=document_detail,
                            similarity_score=score_data["similarity_score"],
                            chunk_details=score_data["chunk_details"]
                        )

                        results.append({
                            "similarity_score": score_data["similarity_score"],
                            "similarity_percentage": round(score_data["similarity_score"] * 100, 1),
                            "chunk_matches": score_data["chunk_matches"],
                            document_type: document_detail,
                            "chunk_details": score_data["chunk_details"],
                            "llm_analysis": llm_analysis
                        })

            # 전체 결과에 대한 표절 위험도 분석 추가
            plagiarism_analysis = await self.llm_service.analyze_plagiarism_risk(
                original_resume=document,
                similar_resumes=results
            )

            print(f"[SimilarityService] 최종 유사 {document_type} 수: {len(results)}")
            print(f"[SimilarityService] === 청킹 기반 유사도 검색 완료 ===")

            return {
                "success": True,
                "document_type": document_type,
                "analysis_type": "chunk_based_similarity",
                "data": {
                    f"original_{document_type}": {
                        "id": str(document["_id"]),
                        "applicant_id": document.get("applicant_id", ""),
                        "chunk_count": len(query_chunks)
                    },
                    f"similar_{document_type}s": results,
                    "total": len(results),
                    "plagiarism_analysis": plagiarism_analysis
                }
            }

        except Exception as e:
            print(f"[SimilarityService] 청킹 기반 유사도 검색 실패: {str(e)}")
            raise e

    async def find_similar_documents(self, document_id: str, collection: Collection,
                                  document_type: str = "resume", limit: int = 5) -> Dict[str, Any]:
        """
        문서 타입에 따라 유사도 검색 또는 표절체크를 수행합니다.

        Args:
            document_id (str): 기준이 되는 문서 ID
            collection (Collection): MongoDB 컬렉션
            document_type (str): 문서 타입 ("resume", "cover_letter", "portfolio")
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 유사도 검색 또는 표절체크 결과
        """
        try:
            # 자소서 표절체크만 지원
            if document_type == "cover_letter":
                return await self._check_cover_letter_plagiarism(document_id, collection, limit)
            else:
                # 이력서/포트폴리오 유사도 검사는 제거됨
                print(f"[SimilarityService] {document_type} 유사도 검사는 더 이상 지원되지 않습니다.")
                return {
                    "similar_documents": [],
                    "total_found": 0,
                    "search_type": f"{document_type}_similarity_removed"
                }

        except Exception as e:
            print(f"[SimilarityService] 문서 유사도 검색 실패: {str(e)}")
            raise e

    async def _check_cover_letter_plagiarism(self, cover_letter_id: str, collection: Collection, limit: int = 5) -> Dict[str, Any]:
        """자소서 표절체크 전용 메서드"""
        try:
            print(f"[SimilarityService] === 자소서 표절체크 시작 ===")
            print(f"[SimilarityService] 자소서 ID: {cover_letter_id}")

            # 자소서 조회
            cover_letter = await collection.find_one({"_id": ObjectId(cover_letter_id)})
            if not cover_letter:
                raise ValueError("자소서를 찾을 수 없습니다.")

            print(f"[SimilarityService] 자소서 찾음")

            # 자소서 텍스트 추출
            cover_letter_text = self._extract_cover_letter_text(cover_letter)
            if not cover_letter_text:
                raise ValueError("자소서 텍스트가 없습니다.")

            # 임베딩 생성
            query_embedding = await self.embedding_service.create_query_embedding(cover_letter_text)
            if not query_embedding:
                raise ValueError("자소서 임베딩 생성에 실패했습니다.")

            # 현재 자소서가 벡터 DB에 있는지 확인하고 없으면 저장
            cover_letter_vector_id = f"cover_letter_{cover_letter_id}"
            try:
                # Pinecone에서 현재 자소서 벡터 확인
                existing_vector = self.vector_service.index.fetch([cover_letter_vector_id])
                if not existing_vector.vectors or cover_letter_vector_id not in existing_vector.vectors:
                    print(f"[SimilarityService] 자소서 벡터 없음. 벡터 DB에 저장 중...")

                    # 벡터 저장 (직접 upsert 사용하여 고정 ID 지정)
                    vector_data = {
                        "id": cover_letter_vector_id,
                        "values": query_embedding,
                        "metadata": {
                            "document_id": cover_letter_id,
                            "document_type": "cover_letter",
                            "chunk_type": "cover_letter",
                            "applicant_id": cover_letter.get("applicant_id", ""),
                            "text_preview": cover_letter_text[:100] + "..." if len(cover_letter_text) > 100 else cover_letter_text,
                            "created_at": datetime.now().isoformat()
                        }
                    }

                    self.vector_service.index.upsert(vectors=[vector_data])
                    print(f"[SimilarityService] 자소서 벡터 저장 완료: {cover_letter_vector_id}")
                else:
                    print(f"[SimilarityService] 자소서 벡터 이미 존재: {cover_letter_vector_id}")
            except Exception as e:
                print(f"[SimilarityService] 벡터 확인/저장 중 오류: {e}")
                # 오류 발생 시 강제로 벡터 저장
                print(f"[SimilarityService] 오류로 인해 자소서 벡터 강제 저장...")
                vector_data = {
                    "id": cover_letter_vector_id,
                    "values": query_embedding,
                    "metadata": {
                        "document_id": cover_letter_id,
                        "document_type": "cover_letter",
                        "chunk_type": "cover_letter",
                        "applicant_id": cover_letter.get("applicant_id", ""),
                        "text_preview": cover_letter_text[:100] + "..." if len(cover_letter_text) > 100 else cover_letter_text,
                        "created_at": datetime.now().isoformat()
                    }
                }

                self.vector_service.index.upsert(vectors=[vector_data])
                print(f"[SimilarityService] 자소서 벡터 강제 저장 완료: {cover_letter_vector_id}")

            # Pinecone에서 유사한 벡터 검색 (표절 의심 수준으로 높은 임계값 사용)
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit + 5,  # 더 많이 검색해서 필터링
                filter_type="cover_letter"
            )

            # 표절 의심 결과 필터링 (임계값 0.7 이상)
            plagiarism_threshold = 0.7
            suspected_plagiarism = []

            for match in search_result["matches"]:
                # VectorService에서 cover_letter_id가 document_id로 저장됨
                match_id = match["metadata"].get("document_id", match["metadata"].get("resume_id"))
                similarity_score = match["score"]

                # 자기 자신 제외하고 높은 유사도만 포함
                if match_id != cover_letter_id and similarity_score >= plagiarism_threshold:
                    suspected_plagiarism.append(match)
                    print(f"[SimilarityService] 표절 의심: ID={match_id}, 유사도={similarity_score:.1%}")

            if len(suspected_plagiarism) > 0:
                print(f"[SimilarityService] 표절 의심 자소서 {len(suspected_plagiarism)}개 발견")

            # MongoDB에서 상세 정보 조회
            results = []
            if suspected_plagiarism:
                cover_letter_ids = [ObjectId(match["metadata"].get("document_id", match["metadata"].get("resume_id"))) for match in suspected_plagiarism]
                cover_letters_detail = await collection.find({"_id": {"$in": cover_letter_ids}}).to_list(1000)

                for match in suspected_plagiarism:
                    match_doc_id = match["metadata"].get("document_id", match["metadata"].get("resume_id"))
                    cover_letter_detail = next((cl for cl in cover_letters_detail if str(cl["_id"]) == match_doc_id), None)
                    if cover_letter_detail:
                        cover_letter_detail["_id"] = str(cover_letter_detail["_id"])

                        # 모든 datetime 필드를 문자열로 변환 (JSON 직렬화를 위해)
                        for key, value in list(cover_letter_detail.items()):
                            if hasattr(value, 'isoformat'):  # datetime 객체인지 확인
                                cover_letter_detail[key] = value.isoformat()
                            elif key == "_id":
                                cover_letter_detail[key] = str(value)  # ObjectId도 문자열로

                        # 표절 위험도 분석
                        plagiarism_analysis = await self.llm_service.analyze_plagiarism_risk(
                            original_resume=cover_letter,
                            similar_resumes=[{"resume": cover_letter_detail, "similarity_score": match["score"]}]
                        )

                        results.append({
                            "similarity_score": match["score"],
                            "similarity_percentage": round(match["score"] * 100, 1),
                            "plagiarism_risk": "HIGH" if match["score"] >= 0.85 else "MEDIUM",
                            "cover_letter": cover_letter_detail,
                            "plagiarism_analysis": plagiarism_analysis
                        })

            # 유사도 점수로 정렬
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

            print(f"[SimilarityService] 표절 의심 자소서 수: {len(results)}")
            print(f"[SimilarityService] === 자소서 표절체크 완료 ===")

            # 원본 자소서도 datetime 처리
            original_data = {
                "id": str(cover_letter["_id"]),
                "applicant_id": cover_letter.get("applicant_id", "")
            }

            # created_at 필드 처리
            if cover_letter.get("created_at"):
                if hasattr(cover_letter["created_at"], 'isoformat'):
                    original_data["created_at"] = cover_letter["created_at"].isoformat()
                else:
                    original_data["created_at"] = str(cover_letter["created_at"])
            else:
                original_data["created_at"] = ""

            return {
                "success": True,
                "document_type": "cover_letter",
                "analysis_type": "plagiarism_check",
                "data": {
                    "original_cover_letter": original_data,
                    "suspected_plagiarism": results,
                    "total": len(results),
                    "plagiarism_threshold": plagiarism_threshold
                }
            }

        except Exception as e:
            print(f"[SimilarityService] 자소서 표절체크 실패: {str(e)}")
            raise e


    async def search_resumes_by_query(self, query: str, collection: Collection,
                                    search_type: str = "resume", limit: int = 10) -> Dict[str, Any]:
        """
        쿼리 텍스트로 이력서를 검색합니다.

        Args:
            query (str): 검색할 쿼리 텍스트
            collection (Collection): MongoDB 컬렉션
            search_type (str): 검색할 타입 ("resume", "cover_letter", "portfolio")
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 검색 결과
        """
        try:
            if not query:
                raise ValueError("검색어를 입력해주세요.")

            # 쿼리 텍스트 임베딩 생성
            print(f"=== 검색 임베딩 처리 시작 ===")
            print(f"검색 쿼리: {query}")
            print(f"검색 타입: {search_type}")
            print(f"검색 제한: {limit}")

            query_embedding = await self.embedding_service.create_query_embedding(query)

            if not query_embedding:
                print(f"검색어 임베딩 생성 실패!")
                raise ValueError("검색어 임베딩 생성에 실패했습니다.")

            print(f"검색어 임베딩 생성 성공!")
            print(f"검색 임베딩 차원: {len(query_embedding)}")

            # Pinecone에서 유사한 벡터 검색
            print(f"Pinecone 검색 시작...")
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit,
                filter_type=search_type
            )

            print(f"Pinecone 검색 완료!")
            print(f"검색 결과 수: {len(search_result['matches'])}")
            print(f"=== 검색 임베딩 처리 완료 ===")

            # MongoDB에서 상세 정보 조회
            resume_ids = [ObjectId(match["metadata"]["resume_id"]) for match in search_result["matches"]]
            resumes = await collection.find({"_id": {"$in": resume_ids}}).to_list(1000)

            # 검색 결과와 상세 정보 매칭
            results = []
            for match in search_result["matches"]:
                resume = next((r for r in resumes if str(r["_id"]) == match["metadata"]["resume_id"]), None)
                if resume:
                    resume["_id"] = str(resume["_id"])
                    resume["resume_id"] = str(resume["resume_id"])
                    resume["created_at"] = resume["created_at"].isoformat()

                    results.append({
                        "score": match["score"],
                        "metadata": match["metadata"],
                        "resume": resume
                    })

            return {
                "success": True,
                "data": {
                    "query": query,
                    "results": results,
                    "total": len(results)
                }
            }

        except Exception as e:
            print(f"이력서 검색 중 오류: {str(e)}")
            raise e

    def _extract_cover_letter_text(self, cover_letter: Dict[str, Any]) -> str:
        """
        자소서 데이터에서 텍스트를 추출합니다.

        Args:
            cover_letter (Dict[str, Any]): 자소서 데이터

        Returns:
            str: 추출된 텍스트
        """
        # 자소서 특화 필드들 사용
        extracted_text = cover_letter.get("extracted_text", "").strip()
        career_history = cover_letter.get("careerHistory", "").strip()
        growth_background = cover_letter.get("growthBackground", "").strip()
        motivation = cover_letter.get("motivation", "").strip()

        # 텍스트 결합
        text_parts = []
        if extracted_text and not self._is_meaningless_text(extracted_text):
            text_parts.append(extracted_text)
        if career_history and not self._is_meaningless_text(career_history):
            text_parts.append(f"경력사항: {career_history}")
        if growth_background and not self._is_meaningless_text(growth_background):
            text_parts.append(f"성장배경: {growth_background}")
        if motivation and not self._is_meaningless_text(motivation):
            text_parts.append(f"지원동기: {motivation}")

        combined_text = " ".join(text_parts)
        return self._preprocess_text(combined_text)

    def _is_meaningless_text(self, text: str) -> bool:
        """
        텍스트가 의미 없는 텍스트인지 확인합니다.

        Args:
            text (str): 확인할 텍스트

        Returns:
            bool: 의미 없는 텍스트 여부
        """
        if not text or not text.strip():
            return True

        # 너무 짧은 텍스트 (3글자 미만)
        if len(text.strip()) < 3:
            return True

        # 특수문자나 숫자만으로 구성된 텍스트
        clean_text = re.sub(r'[^\w\s]', '', text.strip())
        if not clean_text or clean_text.isdigit():
            return True

        # 반복되는 문자만으로 구성 (예: "---", "***")
        if len(set(clean_text.replace(' ', ''))) <= 1:
            return True

        # 의미없는 OCR 결과 패턴
        meaningless_patterns = [
            r'^[\s\-_=*\.]+$',  # 특수문자만
            r'^\d+[\s\-]*\d*$',  # 숫자만
            r'^[a-zA-Z][\s\-]*[a-zA-Z]*$',  # 단일 영문자들
        ]

        for pattern in meaningless_patterns:
            if re.match(pattern, text.strip()):
                return True

        return False

    def _preprocess_text(self, text: str) -> str:
        """
        텍스트를 전처리합니다.

        Args:
            text (str): 원본 텍스트

        Returns:
            str: 전처리된 텍스트
        """
        if not text:
            return ""

        # 공백 문자 정리
        text = re.sub(r'\s+', ' ', text.strip())

        # 특수문자 중복 제거
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        # 다시 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())

        return text

    def _extract_portfolio_text(self, portfolio: Dict[str, Any]) -> str:
        """
        포트폴리오 데이터에서 텍스트를 추출합니다.

        Args:
            portfolio (Dict[str, Any]): 포트폴리오 데이터

        Returns:
            str: 추출된 텍스트
        """
        # 포트폴리오 특화 필드들 사용
        extracted_text = portfolio.get("extracted_text", "").strip()
        summary = portfolio.get("summary", "").strip()
        items = portfolio.get("items", [])

        # 텍스트 결합
        text_parts = []
        if extracted_text and not self._is_meaningless_text(extracted_text):
            text_parts.append(extracted_text)
        if summary and not self._is_meaningless_text(summary):
            text_parts.append(f"요약: {summary}")

        # 포트폴리오 아이템들에서 텍스트 추출
        for item in items:
            if isinstance(item, dict):
                title = item.get("title", "").strip()
                if title and not self._is_meaningless_text(title):
                    text_parts.append(f"제목: {title}")

        combined_text = " ".join(text_parts)
        return self._preprocess_text(combined_text)

    def _calculate_skills_similarity(self, skills_a: str, skills_b: str) -> float:
        """
        기술스택 유사도를 계산합니다.

        Args:
            skills_a (str): 첫 번째 기술스택
            skills_b (str): 두 번째 기술스택

        Returns:
            float: 기술스택 유사도 점수 (0-1)
        """
        try:
            # 기술스택을 개별 기술로 분할
            skills_list_a = [skill.strip().lower() for skill in skills_a.split(',')]
            skills_list_b = [skill.strip().lower() for skill in skills_b.split(',')]

            # 중복 제거
            skills_set_a = set(skills_list_a)
            skills_set_b = set(skills_list_b)

            if not skills_set_a or not skills_set_b:
                return 0.0

            # Jaccard 유사도 계산
            intersection = len(skills_set_a.intersection(skills_set_b))
            union = len(skills_set_a.union(skills_set_b))

            return intersection / union if union > 0 else 0.0

        except Exception as e:
            print(f"[SimilarityService] 기술스택 유사도 계산 중 오류: {str(e)}")
            return 0.0




    async def search_resumes_multi_hybrid(self, query: str, collection: Collection,
                                        search_type: str = "resume", limit: int = 10) -> Dict[str, Any]:
        """
        다중 하이브리드 검색: LangChain EnsembleRetriever 또는 기존 방식을 사용합니다.

        Args:
            query (str): 검색할 쿼리 텍스트
            collection (Collection): MongoDB 컬렉션
            search_type (str): 검색할 타입
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 다중 하이브리드 검색 결과
        """
        try:
            print(f"[SimilarityService] === 다중 하이브리드 검색 시작 ===")
            print(f"[SimilarityService] 검색 쿼리: {query}")

            if not query or not query.strip():
                raise ValueError("검색어를 입력해주세요.")

            # LangChain 하이브리드 서비스 우선 사용
            if self.langchain_hybrid:
                print(f"[SimilarityService] LangChain 하이브리드 검색 사용")
                return await self._search_with_langchain_hybrid(query, collection, search_type, limit)

            # 기존 방식 폴백
            print(f"[SimilarityService] 기존 하이브리드 검색 사용 (폴백)")
            return await self._search_with_manual_hybrid(query, collection, search_type, limit)

        except Exception as e:
            print(f"[SimilarityService] 다중 하이브리드 검색 실패: {str(e)}")
            raise e

    async def _search_with_langchain_hybrid(self, query: str, collection: Collection,
                                          search_type: str, limit: int) -> Dict[str, Any]:
        """LangChain 하이브리드 검색을 사용합니다."""
        try:
            print(f"[SimilarityService] LangChain 하이브리드 검색 수행")

            # LangChain 하이브리드 검색 (벡터 + 키워드)
            result = await self.langchain_hybrid.search_resumes_langchain_hybrid(
                query=query,
                collection=collection,
                search_type=search_type,
                limit=limit
            )

            if result and result.get("success"):
                print(f"[SimilarityService] LangChain 하이브리드 검색 성공: {result['data']['total']}개 결과")
                return result
            else:
                print(f"[SimilarityService] LangChain 하이브리드 검색 실패, 폴백 사용")
                return await self._search_with_manual_hybrid(query, collection, search_type, limit)

        except Exception as e:
            print(f"[SimilarityService] LangChain 하이브리드 검색 오류: {e}, 폴백 사용")
            return await self._search_with_manual_hybrid(query, collection, search_type, limit)

    async def _search_with_manual_hybrid(self, query: str, collection: Collection,
                                       search_type: str, limit: int) -> Dict[str, Any]:
        """기존 수동 하이브리드 검색을 사용합니다."""
        try:
            print(f"[SimilarityService] 기존 하이브리드 검색 수행")
            print(f"[SimilarityService] 가중치 - 벡터: {self.search_weights['vector']}, "
                  f"키워드: {self.search_weights['keyword']}")

            # 1. 벡터 검색 수행
            print(f"[SimilarityService] 1단계: 벡터 검색 수행")
            vector_results = await self._perform_vector_search(query, collection, search_type, limit * 2)

            # 2. 키워드 검색 수행
            print(f"[SimilarityService] 2단계: 키워드 검색 수행")
            keyword_results = await self._perform_keyword_search(query, collection, limit * 2)

            # 3. 검색 결과 융합
            print(f"[SimilarityService] 3단계: 검색 결과 융합")
            fused_results = await self._fuse_search_results(
                vector_results, keyword_results, collection, query, limit
            )

            print(f"[SimilarityService] 최종 결과 수: {len(fused_results)}")
            print(f"[SimilarityService] === 기존 하이브리드 검색 완료 ===")

            return {
                "success": True,
                "data": {
                    "query": query,
                    "search_method": "manual_hybrid",
                    "weights": self.search_weights,
                    "results": fused_results,
                    "total": len(fused_results),
                    "vector_count": len(vector_results),
                    "keyword_count": len(keyword_results)
                }
            }

        except Exception as e:
            print(f"[SimilarityService] 기존 하이브리드 검색 실패: {str(e)}")
            raise e

    async def _perform_vector_search(self, query: str, collection: Collection,
                                   search_type: str, limit: int) -> List[Dict[str, Any]]:
        """벡터 검색을 수행합니다."""
        try:
            # 쿼리 임베딩 생성
            query_embedding = await self.embedding_service.create_query_embedding(query)
            if not query_embedding:
                return []

            # Pinecone에 저장된 벡터 확인 (디버깅)
            try:
                stats = self.vector_service.get_stats()
                print(f"[SimilarityService] Pinecone 통계: {stats}")

                # 필터 없이 전체 검색해보기
                all_search_result = await self.vector_service.search_similar_vectors(
                    query_embedding=query_embedding,
                    top_k=10,
                    filter_type=None
                )
                print(f"[SimilarityService] 필터 없는 전체 검색 결과: {len(all_search_result['matches'])}개")
                for match in all_search_result['matches'][:3]:
                    print(f"  - ID: {match['id']}, Score: {match['score']:.3f}, Type: {match['metadata'].get('chunk_type', 'unknown')}")
            except Exception as e:
                print(f"[SimilarityService] 디버깅 검색 실패: {e}")

            # Pinecone 벡터 검색
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit,
                filter_type=search_type
            )

            # 결과 포맷팅
            vector_results = []
            for match in search_result["matches"]:
                # document_id를 resume_id로 사용 (VectorService에서 document_id로 저장함)
                document_id = match["metadata"].get("document_id", match["metadata"].get("resume_id"))
                vector_results.append({
                    "resume_id": document_id,
                    "vector_score": match["score"],
                    "search_method": "vector"
                })

            print(f"[SimilarityService] 벡터 검색 결과: {len(vector_results)}개")
            return vector_results

        except Exception as e:
            print(f"[SimilarityService] 벡터 검색 실패: {str(e)}")
            return []

    async def _perform_keyword_search(self, query: str, collection: Collection,
                                    limit: int) -> List[Dict[str, Any]]:
        """키워드 검색을 수행합니다."""
        try:
            # BM25 키워드 검색
            keyword_result = await self.keyword_search_service.search_by_keywords(
                query=query,
                collection=collection,
                limit=limit
            )

            if not keyword_result["success"]:
                return []

            # 결과 포맷팅
            keyword_results = []
            for result in keyword_result["results"]:
                keyword_results.append({
                    "resume_id": result["resume"]["_id"],
                    "keyword_score": result["bm25_score"],
                    "search_method": "keyword",
                    "highlight": result.get("highlight", "")
                })

            print(f"[SimilarityService] 키워드 검색 결과: {len(keyword_results)}개")
            return keyword_results

        except Exception as e:
            print(f"[SimilarityService] 키워드 검색 실패: {str(e)}")
            return []

    async def _fuse_search_results(self, vector_results: List[Dict[str, Any]],
                                 keyword_results: List[Dict[str, Any]],
                                 collection: Collection, query: str,
                                 limit: int) -> List[Dict[str, Any]]:
        """여러 검색 결과를 융합합니다."""
        try:
            # 모든 unique resume_id 수집
            all_resume_ids = set()
            vector_scores = {}
            keyword_scores = {}

            # 벡터 검색 결과 처리
            for result in vector_results:
                resume_id = result["resume_id"]
                all_resume_ids.add(resume_id)
                vector_scores[resume_id] = result["vector_score"]

            # 키워드 검색 결과 처리
            for result in keyword_results:
                resume_id = result["resume_id"]
                all_resume_ids.add(resume_id)
                keyword_scores[resume_id] = result["keyword_score"]

            # MongoDB에서 상세 정보 조회
            resume_ids_obj = [ObjectId(rid) for rid in all_resume_ids]
            resumes = await collection.find({"_id": {"$in": resume_ids_obj}}).to_list(1000)

            # 융합 점수 계산
            fused_results = []
            for resume in resumes:
                resume_id = str(resume["_id"])

                # 각 검색 방법의 점수 가져오기 (없으면 0)
                v_score = vector_scores.get(resume_id, 0.0)
                k_score = keyword_scores.get(resume_id, 0.0)

                # 키워드 점수 정규화 (BM25 점수는 보통 0-10 범위)
                k_score_normalized = min(k_score / 10.0, 1.0) if k_score > 0 else 0.0

                # 가중 평균으로 최종 점수 계산 (벡터 + 키워드만)
                final_score = (
                    v_score * self.search_weights['vector'] +
                    k_score_normalized * self.search_weights['keyword']
                )

                # 점수가 0보다 큰 경우만 포함
                if final_score > 0:
                    # 이력서 데이터 포맷팅
                    resume["_id"] = str(resume["_id"])
                    if "resume_id" in resume:
                        resume["resume_id"] = str(resume["resume_id"])
                    else:
                        resume["resume_id"] = str(resume["_id"])

                    # 모든 datetime 필드를 문자열로 변환 (JSON 직렬화를 위해)
                    for key, value in list(resume.items()):
                        if hasattr(value, 'isoformat'):  # datetime 객체인지 확인
                            resume[key] = value.isoformat()
                        elif key == "_id":
                            resume[key] = str(value)  # ObjectId도 문자열로

                    fused_results.append({
                        "final_score": final_score,
                        "vector_score": v_score,
                        "keyword_score": k_score_normalized,
                        "original_keyword_score": k_score,
                        "resume": resume,
                        "search_methods": [
                            method for method, score in [
                                ("vector", v_score),
                                ("keyword", k_score_normalized)
                            ] if score > 0
                        ]
                    })

            # 최종 점수 기준으로 정렬
            fused_results.sort(key=lambda x: x["final_score"], reverse=True)

            # 상위 결과만 반환
            final_results = fused_results[:limit]

            print(f"[SimilarityService] 융합 결과: {len(final_results)}개 (전체 후보: {len(fused_results)}개)")
            for i, result in enumerate(final_results[:3]):  # 상위 3개만 로그
                # name 필드 처리 (실제 DB 구조에 맞게)
                name = '이름미상'
                if result['resume'].get('name'):
                    name = result['resume']['name']
                elif result['resume'].get('basic_info', {}).get('names'):
                    names = result['resume']['basic_info']['names']
                    name = names[0] if names and len(names) > 0 else '이름미상'

                print(f"[SimilarityService] #{i+1}: {name} "
                      f"(최종:{result['final_score']:.3f}, V:{result['vector_score']:.3f}, "
                      f"K:{result['keyword_score']:.3f})")

            return final_results

        except Exception as e:
            print(f"[SimilarityService] 검색 결과 융합 실패: {str(e)}")
            print(f"[SimilarityService] 벡터 결과 수: {len(vector_results)}")
            print(f"[SimilarityService] 키워드 결과 수: {len(keyword_results)}")
            if vector_results:
                print(f"[SimilarityService] 첫번째 벡터 결과: {vector_results[0]}")
            return []

    async def _store_applicant_vector_if_needed(self, applicant: Dict[str, Any]) -> bool:
        """
        지원자 정보를 벡터로 저장 (없는 경우에만)

        Args:
            applicant (Dict[str, Any]): 지원자 데이터

        Returns:
            bool: 저장 성공 여부
        """
        try:
            applicant_id = str(applicant["_id"])
            vector_id = f"applicant_{applicant_id}"

            # 이미 벡터가 존재하는지 확인 (text 필드가 있는지도 확인)
            try:
                existing_vector = self.vector_service.index.fetch(ids=[vector_id])
                if existing_vector and existing_vector.get("vectors"):
                    vector_info = existing_vector["vectors"].get(vector_id)
                    if vector_info and vector_info.get("metadata", {}).get("text"):
                        print(f"[SimilarityService] 지원자 벡터 이미 존재 (text 필드 포함): {vector_id}")
                        return True
                    else:
                        print(f"[SimilarityService] 기존 벡터에 text 필드 없음, 업데이트 필요: {vector_id}")
            except Exception:
                pass  # 벡터가 없으면 새로 생성

            # 지원자 정보로 텍스트 생성
            text_parts = []
            if applicant.get('position'):
                text_parts.append(f"지원직무: {applicant['position']}")
            if applicant.get('experience'):
                text_parts.append(f"경력: {applicant['experience']}년")
            if applicant.get('skills'):
                if isinstance(applicant['skills'], list):
                    skills_text = " ".join(applicant['skills'])
                else:
                    skills_text = str(applicant['skills'])
                text_parts.append(f"기술스택: {skills_text}")

            if not text_parts:
                print(f"[SimilarityService] 지원자 정보 부족으로 벡터 생성 스킵: {applicant.get('name', 'Unknown')}")
                return False

            applicant_text = " ".join(text_parts)

            # 임베딩 생성
            query_embedding = await self.embedding_service.create_document_embedding(applicant_text)
            if not query_embedding:
                print(f"[SimilarityService] 지원자 임베딩 생성 실패: {applicant.get('name', 'Unknown')}")
                return False

            # Pinecone에 벡터 저장
            vector_data = {
                "id": vector_id,
                "values": query_embedding,
                "metadata": {
                    "applicant_id": applicant_id,
                    "document_id": applicant_id,
                    "document_type": "applicant",
                    "chunk_type": "applicant",  # LangChain 필터용
                    "name": applicant.get("name", ""),
                    "position": applicant.get("position", ""),
                    "experience": applicant.get("experience", ""),
                    "skills": applicant.get("skills", ""),
                    "text": applicant_text,  # LangChain이 필요로 하는 text 필드
                    "text_preview": applicant_text[:100] + "..." if len(applicant_text) > 100 else applicant_text,
                    "created_at": datetime.now().isoformat()
                }
            }

            self.vector_service.index.upsert(vectors=[vector_data])
            print(f"[SimilarityService] 지원자 벡터 저장 완료: {applicant.get('name', 'Unknown')} ({vector_id})")
            return True

        except Exception as e:
            print(f"[SimilarityService] 지원자 벡터 저장 실패: {e}")
            return False

    async def _analyze_similar_applicants_with_llm(self, target_applicant: Dict[str, Any],
                                                 similar_applicants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        유사 지원자들에 대한 LLM 분석 수행

        Args:
            target_applicant (Dict): 기준 지원자
            similar_applicants (List[Dict]): 유사한 지원자들

        Returns:
            Dict: LLM 분석 결과
        """
        try:
            print(f"[SimilarityService] === LLM 기반 유사 지원자 분석 시작 ===")

            if not similar_applicants:
                return {
                    "success": False,
                    "message": "분석할 유사 지원자가 없습니다."
                }

            # 기준 지원자 정보 요약
            target_info = {
                "name": target_applicant.get("name", "N/A"),
                "position": target_applicant.get("position", "N/A"),
                "experience": target_applicant.get("experience", "N/A"),
                "skills": target_applicant.get("skills", "N/A"),
                "department": target_applicant.get("department", "N/A")
            }

            # 유사 지원자들 정보 요약 (상위 3명)
            similar_info = []
            for i, result in enumerate(similar_applicants[:3]):
                applicant = result.get("applicant", {})
                similar_info.append({
                    "rank": i + 1,
                    "name": applicant.get("name", "N/A"),
                    "position": applicant.get("position", "N/A"),
                    "experience": applicant.get("experience", "N/A"),
                    "skills": applicant.get("skills", "N/A"),
                    "department": applicant.get("department", "N/A"),
                    "final_score": result.get("final_score", 0),
                    "vector_score": result.get("vector_score", 0),
                    "keyword_score": result.get("keyword_score", 0)
                })

            # LLM 분석 요청
            analysis_result = await self.llm_service.analyze_similar_applicants(
                target_applicant=target_info,
                similar_applicants=similar_info
            )

            print(f"[SimilarityService] LLM 분석 완료: {len(similar_applicants)}명 지원자 분석")
            return analysis_result

        except Exception as e:
            print(f"[SimilarityService] LLM 분석 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "LLM 분석 중 오류가 발생했습니다."
            }

    async def search_similar_applicants_hybrid(self, target_applicant: Dict[str, Any],
                                             applicants_collection: Collection,
                                             limit: int = 10) -> Dict[str, Any]:
        """
        지원자 기반 유사 인재 추천 (하이브리드 검색: 벡터 + 키워드)

        Args:
            target_applicant (Dict): 기준 지원자 데이터
            applicants_collection (Collection): 지원자 컬렉션
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 유사 지원자 검색 결과
        """
        try:
            print(f"[SimilarityService] === 지원자 기반 유사 인재 추천 시작 ===")
            print(f"[SimilarityService] 기준 지원자: {target_applicant.get('name', 'N/A')}")
            print(f"[SimilarityService] 지원직무: {target_applicant.get('position', 'N/A')}")

            # 0. 기준 지원자의 벡터 저장 (text 필드 업데이트 포함)
            print(f"[SimilarityService] 기준 지원자 벡터 업데이트 중...")
            await self._store_applicant_vector_if_needed(target_applicant)

            # 1. 벡터 검색용 텍스트 (지원자 정보: position, experience, skills)
            vector_text_parts = []
            if target_applicant.get('position'):
                vector_text_parts.append(f"지원직무: {target_applicant['position']}")
            if target_applicant.get('experience'):
                vector_text_parts.append(f"경력: {target_applicant['experience']}년")
            if target_applicant.get('skills'):
                if isinstance(target_applicant['skills'], list):
                    skills_text = " ".join(target_applicant['skills'])
                else:
                    skills_text = str(target_applicant['skills'])
                vector_text_parts.append(f"기술스택: {skills_text}")

            vector_query_text = " ".join(vector_text_parts)
            print(f"[SimilarityService] 벡터 검색용 텍스트: {vector_query_text}")

            # 2. 키워드 검색용 텍스트 (이력서 내용: extracted_text 기반)
            keyword_text_parts = []

            # resume_id로 실제 이력서 내용 조회
            if target_applicant.get('resume_id'):
                try:
                    from bson import ObjectId
                    from services.mongo_service import MongoService
                    mongo_service = MongoService()
                    resume = await mongo_service.db.resumes.find_one({"_id": ObjectId(target_applicant['resume_id'])})
                    if resume:
                        print(f"[SimilarityService] 연결된 이력서에서 키워드 검색용 텍스트 추출 중...")
                        # OCR 추출된 텍스트 사용
                        if resume.get('extracted_text'):
                            keyword_text_parts.append(resume['extracted_text'])
                        # AI 요약이 있으면 추가
                        if resume.get('summary'):
                            keyword_text_parts.append(resume['summary'])
                        # 키워드 목록도 텍스트로 추가
                        if resume.get('keywords') and isinstance(resume['keywords'], list):
                            keywords_text = " ".join(resume['keywords'])
                            keyword_text_parts.append(keywords_text)
                except Exception as e:
                    print(f"[SimilarityService] 이력서 조회 실패: {e}")

            # 지원자 정보의 이력서 내용도 확인 (백업 - OCR 이전 데이터용)
            if target_applicant.get('growthBackground'):
                keyword_text_parts.append(target_applicant['growthBackground'])
            if target_applicant.get('motivation'):
                keyword_text_parts.append(target_applicant['motivation'])
            if target_applicant.get('careerHistory'):
                keyword_text_parts.append(target_applicant['careerHistory'])

            keyword_query_text = " ".join(keyword_text_parts)
            print(f"[SimilarityService] 키워드 검색용 텍스트 길이: {len(keyword_query_text)}")

            # 최소한의 검색 텍스트 확보 확인
            if not vector_query_text and not keyword_query_text:
                print(f"[SimilarityService] ❌ 검색 가능한 정보가 없음")
                return {
                    "success": False,
                    "message": "검색 가능한 정보가 없습니다. 지원자 정보나 이력서 내용이 필요합니다.",
                    "debug_info": {
                        "available_fields": list(target_applicant.keys())
                    }
                }

            # 3. 벡터 검색 수행 (지원자 정보 기반)
            vector_results = []
            if vector_query_text:
                print(f"[SimilarityService] 벡터 검색 수행 (지원자 정보 기반)...")
                vector_embedding = await self.embedding_service.create_query_embedding(vector_query_text)
                if vector_embedding:
                    vector_search_result = await self.vector_service.search_similar_vectors(
                        query_embedding=vector_embedding,
                        top_k=limit * 2,
                        filter_type="applicant"
                    )
                    vector_results = vector_search_result.get("matches", [])
                else:
                    print(f"[SimilarityService] ❌ 벡터 임베딩 생성 실패")

            print(f"[SimilarityService] 벡터 검색 결과: {len(vector_results)}개")

            # 4. 키워드 검색 수행 (이력서 내용 기반)
            keyword_results = []
            if keyword_query_text:
                print(f"[SimilarityService] 키워드 검색 수행 (이력서 내용 기반)...")
                # Elasticsearch 기반 BM25 검색 실행
                es_result = await self.keyword_search_service.search_by_keywords(
                    query=keyword_query_text,
                    collection=applicants_collection,
                    limit=limit * 2
                )
                # 융합 로직에서 기대하는 형식({_id, _score})으로 변환
                if es_result and es_result.get("success"):
                    for item in es_result.get("results", []):
                        try:
                            resume_doc = item.get("resume", {})
                            resume_id = resume_doc.get("_id")
                            bm25_score = item.get("bm25_score", 0)
                            if resume_id:
                                keyword_results.append({
                                    "_id": resume_id,
                                    "_score": bm25_score
                                })
                        except Exception:
                            continue
            else:
                print(f"[SimilarityService] 키워드 검색 스킵 (이력서 내용 없음)")

            print(f"[SimilarityService] 키워드 검색 결과: {len(keyword_results)}개")

            # 5. LangChain 하이브리드 검색 시도 (우선)
            if self.langchain_hybrid and vector_query_text:
                print(f"[SimilarityService] LangChain 하이브리드 검색 사용")
                # 이력서 컬렉션 가져오기 (키워드 검색용)
                from services.mongo_service import MongoService
                mongo_service = MongoService()
                resumes_collection = mongo_service.db.resumes

                langchain_result = await self.langchain_hybrid.search_similar_applicants_langchain(
                    vector_query=vector_query_text,
                    keyword_query=keyword_query_text,
                    applicants_collection=applicants_collection,
                    resumes_collection=resumes_collection,
                    target_applicant=target_applicant,
                    limit=limit
                )

                # LLM 분석 추가
                if langchain_result and langchain_result.get("success"):
                    similar_applicants = langchain_result.get("data", {}).get("results", [])
                    if similar_applicants:
                        print(f"[SimilarityService] 유사 인재에 대한 LLM 분석 수행...")
                        llm_analysis = await self._analyze_similar_applicants_with_llm(
                            target_applicant, similar_applicants
                        )
                        langchain_result["data"]["llm_analysis"] = llm_analysis

                return langchain_result

            # 6. 기존 방식 폴백 (LangChain 실패 시)
            print(f"[SimilarityService] 기존 하이브리드 검색 사용 (폴백)")
            return await self._fuse_applicant_search_results(
                vector_results, keyword_results, applicants_collection,
                target_applicant, vector_query_text, limit
            )

        except Exception as e:
            print(f"[SimilarityService] 지원자 기반 유사 인재 추천 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "유사 인재 추천 중 오류가 발생했습니다."
            }

    async def _fuse_applicant_search_results(self, vector_results: List[Dict], keyword_results: List[Dict],
                                           applicants_collection: Collection, target_applicant: Dict[str, Any],
                                           query_text: str, limit: int) -> Dict[str, Any]:
        """
        지원자 기반 벡터 + 키워드 검색 결과 융합
        """
        try:
            print(f"[SimilarityService] === 지원자 기반 결과 융합 시작 ===")

            # 벡터 결과를 지원자 ID 기반으로 변환
            vector_applicant_scores = {}
            for match in vector_results:
                # 지원자 벡터의 경우 document_id가 applicant_id임
                applicant_id = match["metadata"].get("document_id")
                if applicant_id and applicant_id != str(target_applicant.get("_id")):
                    # applicant_id로 지원자 찾기
                    from bson import ObjectId
                    applicant = await applicants_collection.find_one({"_id": ObjectId(applicant_id)})
                    if applicant:
                        if applicant_id not in vector_applicant_scores:
                            vector_applicant_scores[applicant_id] = {
                                "score": match["score"],
                                "applicant": applicant
                            }

            print(f"[SimilarityService] 벡터 검색으로 매칭된 지원자 수: {len(vector_applicant_scores)}")

            # 키워드 결과를 지원자 ID 기반으로 변환
            keyword_applicant_scores = {}
            for result in keyword_results:
                resume_id = result.get("_id")
                if resume_id and resume_id != target_applicant.get("resume_id"):
                    # resume_id로 지원자 찾기
                    applicant = await applicants_collection.find_one({"resume_id": resume_id})
                    if applicant:
                        applicant_id = str(applicant["_id"])
                        bm25_score = result.get("_score", 0)
                        # BM25 점수를 0-1 범위로 정규화
                        normalized_score = min(bm25_score / 10.0, 1.0)

                        if applicant_id not in keyword_applicant_scores:
                            keyword_applicant_scores[applicant_id] = {
                                "score": normalized_score,
                                "original_score": bm25_score,
                                "applicant": applicant
                            }

            print(f"[SimilarityService] 키워드 검색으로 매칭된 지원자 수: {len(keyword_applicant_scores)}")

            # 결과 융합
            fused_results = []
            all_applicant_ids = set(vector_applicant_scores.keys()) | set(keyword_applicant_scores.keys())

            for applicant_id in all_applicant_ids:
                v_score = vector_applicant_scores.get(applicant_id, {}).get("score", 0)
                k_score_data = keyword_applicant_scores.get(applicant_id, {})
                k_score_normalized = k_score_data.get("score", 0)
                k_score = k_score_data.get("original_score", 0)

                # 가중 평균으로 최종 점수 계산
                final_score = (v_score * self.search_weights['vector']) + (k_score_normalized * self.search_weights['keyword'])

                # 지원자 정보 가져오기
                applicant = vector_applicant_scores.get(applicant_id, {}).get("applicant") or \
                           keyword_applicant_scores.get(applicant_id, {}).get("applicant")

                if applicant and final_score > 0:
                    # ID와 datetime 필드 처리
                    applicant["_id"] = str(applicant["_id"])

                    # 모든 datetime 필드를 문자열로 변환
                    for key, value in list(applicant.items()):
                        if hasattr(value, 'isoformat'):
                            applicant[key] = value.isoformat()
                        elif key == "_id":
                            applicant[key] = str(value)

                    # 이름 필드 확보 (이미 지원자 정보에 있음)
                    if not applicant.get('name'):
                        applicant['name'] = '이름미상'

                    fused_results.append({
                        "final_score": final_score,
                        "vector_score": v_score,
                        "keyword_score": k_score_normalized,
                        "original_keyword_score": k_score,
                        "applicant": applicant,
                        "search_methods": [
                            method for method, score in [
                                ("vector", v_score),
                                ("keyword", k_score_normalized)
                            ] if score > 0
                        ]
                    })

            # 최종 점수 기준으로 정렬
            fused_results.sort(key=lambda x: x["final_score"], reverse=True)
            final_results = fused_results[:limit]

            print(f"[SimilarityService] 융합 결과: {len(final_results)}개 지원자")
            for i, result in enumerate(final_results[:3]):
                applicant_name = result['applicant'].get('name', '이름미상')
                applicant_position = result['applicant'].get('position', 'N/A')
                print(f"[SimilarityService] #{i+1}: {applicant_name} ({applicant_position}) "
                      f"(최종:{result['final_score']:.3f}, V:{result['vector_score']:.3f}, "
                      f"K:{result['keyword_score']:.3f})")

            return {
                "success": True,
                "message": "유사 인재 추천 완료",
                "data": {
                    "query": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                    "search_method": "applicant_hybrid",
                    "weights": {
                        "vector": self.search_weights['vector'],
                        "keyword": self.search_weights['keyword']
                    },
                    "results": final_results,
                    "total": len(final_results),
                    "vector_count": len(vector_applicant_scores),
                    "keyword_count": len(keyword_applicant_scores),
                    "target_applicant": {
                        "name": target_applicant.get('name', 'N/A'),
                        "position": target_applicant.get('position', 'N/A'),
                        "id": str(target_applicant.get('_id', ''))
                    }
                }
            }

        except Exception as e:
            print(f"[SimilarityService] 지원자 기반 결과 융합 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "결과 융합 중 오류가 발생했습니다."
            }

    async def delete_resume_data(self, resume_id: str) -> Dict[str, Any]:
        """
        이력서 데이터를 벡터 DB와 Elasticsearch에서 모두 삭제합니다.

        Args:
            resume_id (str): 삭제할 이력서 ID

        Returns:
            Dict[str, Any]: 삭제 결과
        """
        try:
            print(f"[SimilarityService] === 이력서 데이터 삭제 시작: {resume_id} ===")

            # 벡터 DB에서 삭제
            vector_result = await self.vector_service.delete_vectors_by_resume_id(resume_id)

            # Elasticsearch에서 삭제
            es_result = await self.keyword_search_service.delete_document(resume_id)

            print(f"[SimilarityService] 벡터 삭제 결과: {vector_result}")
            print(f"[SimilarityService] Elasticsearch 삭제 결과: {es_result['success']}")
            print(f"[SimilarityService] === 이력서 데이터 삭제 완료: {resume_id} ===")

            return {
                "success": True,
                "resume_id": resume_id,
                "vector_deleted": vector_result,
                "elasticsearch_deleted": es_result["success"],
                "message": "이력서 데이터 삭제가 완료되었습니다."
            }

        except Exception as e:
            print(f"[SimilarityService] 이력서 데이터 삭제 실패: {str(e)}")
            return {
                "success": False,
                "resume_id": resume_id,
                "error": str(e),
                "message": "이력서 데이터 삭제 중 오류가 발생했습니다."
            }

    async def batch_store_cover_letter_vectors(self, cover_letters_collection) -> Dict[str, Any]:
        """
        모든 자소서를 벡터 DB에 일괄 저장합니다.

        Args:
            cover_letters_collection: MongoDB 자소서 컬렉션

        Returns:
            Dict[str, Any]: 저장 결과
        """
        try:
            print(f"[SimilarityService] === 자소서 벡터 일괄 저장 시작 ===")

            # 모든 자소서 조회
            cover_letters = await cover_letters_collection.find({}).to_list(10000)
            print(f"[SimilarityService] 총 {len(cover_letters)}개 자소서 발견")

            stored_count = 0
            skipped_count = 0
            error_count = 0

            for cover_letter in cover_letters:
                try:
                    cover_letter_id = str(cover_letter["_id"])
                    cover_letter_vector_id = f"cover_letter_{cover_letter_id}"

                    # 이미 존재하는지 확인
                    try:
                        existing_vector = self.vector_service.index.fetch([cover_letter_vector_id])
                        if existing_vector.vectors and cover_letter_vector_id in existing_vector.vectors:
                            print(f"[SimilarityService] 스킵 (이미 존재): {cover_letter_vector_id}")
                            skipped_count += 1
                            continue
                    except:
                        pass  # 존재하지 않으면 새로 저장

                    # 자소서 텍스트 추출
                    cover_letter_text = self._extract_cover_letter_text(cover_letter)
                    if not cover_letter_text or len(cover_letter_text.strip()) < 10:
                        print(f"[SimilarityService] 스킵 (텍스트 부족): {cover_letter_vector_id}")
                        skipped_count += 1
                        continue

                    # 임베딩 생성
                    query_embedding = await self.embedding_service.create_query_embedding(cover_letter_text)
                    if not query_embedding:
                        print(f"[SimilarityService] 스킵 (임베딩 실패): {cover_letter_vector_id}")
                        error_count += 1
                        continue

                    # 벡터 저장
                    vector_data = {
                        "id": cover_letter_vector_id,
                        "values": query_embedding,
                        "metadata": {
                            "document_id": cover_letter_id,
                            "document_type": "cover_letter",
                            "chunk_type": "cover_letter",
                            "applicant_id": cover_letter.get("applicant_id", ""),
                            "text_preview": cover_letter_text[:100] + "..." if len(cover_letter_text) > 100 else cover_letter_text,
                            "created_at": datetime.now().isoformat()
                        }
                    }

                    self.vector_service.index.upsert(vectors=[vector_data])
                    stored_count += 1
                    print(f"[SimilarityService] 저장 완료: {cover_letter_vector_id} ({stored_count}/{len(cover_letters)})")

                    # 너무 빠르게 요청하지 않도록 짧은 대기
                    await asyncio.sleep(0.1)

                except Exception as e:
                    error_count += 1
                    print(f"[SimilarityService] 저장 실패: {cover_letter.get('_id')} - {str(e)}")

            print(f"[SimilarityService] === 자소서 벡터 일괄 저장 완료 ===")
            print(f"[SimilarityService] 저장: {stored_count}개, 스킵: {skipped_count}개, 오류: {error_count}개")

            return {
                "success": True,
                "total_cover_letters": len(cover_letters),
                "stored_count": stored_count,
                "skipped_count": skipped_count,
                "error_count": error_count,
                "message": f"자소서 벡터 일괄 저장 완료: {stored_count}개 저장됨"
            }

        except Exception as e:
            print(f"[SimilarityService] 자소서 벡터 일괄 저장 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "자소서 벡터 일괄 저장 중 오류가 발생했습니다."
            }

    async def find_similar_applicants(self, position: str = "", skills: str = "",
                                    experience: str = "", department: str = "",
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        검색 기준에 따라 유사한 지원자를 찾습니다.

        Args:
            position (str): 직무
            skills (str): 기술스택
            experience (str): 경력
            department (str): 부서
            limit (int): 반환할 최대 결과 수

        Returns:
            List[Dict[str, Any]]: 유사한 지원자 목록
        """
        try:
            print(f"[SimilarityService] === 검색 기준 기반 유사 지원자 검색 시작 ===")
            print(f"[SimilarityService] 검색 기준 - 직무: {position}, 기술: {skills}, 경력: {experience}, 부서: {department}")

            # 검색 기준 텍스트 구성
            search_criteria = []
            if position:
                search_criteria.append(f"직무: {position}")
            if skills:
                search_criteria.append(f"기술: {skills}")
            if experience:
                search_criteria.append(f"경력: {experience}")
            if department:
                search_criteria.append(f"부서: {department}")

            if not search_criteria:
                print(f"[SimilarityService] ❌ 검색 기준이 없습니다.")
                return []

            search_text = " ".join(search_criteria)
            print(f"[SimilarityService] 검색 텍스트: {search_text}")

            # 임베딩 생성
            query_embedding = await self.embedding_service.create_query_embedding(search_text)
            if not query_embedding:
                print(f"[SimilarityService] ❌ 임베딩 생성 실패")
                return []

            # 벡터 검색 수행
            vector_search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit * 2,  # 더 많은 결과를 가져와서 필터링
                filter_type="applicant"
            )

            vector_matches = vector_search_result.get("matches", [])
            print(f"[SimilarityService] 벡터 검색 결과: {len(vector_matches)}개")

            # MongoDB에서 지원자 정보 조회
            try:
                from services.mongo_service import MongoService
                mongo_service = MongoService()

                similar_applicants = []
                processed_ids = set()

                for match in vector_matches:
                    if len(similar_applicants) >= limit:
                        break

                    # 메타데이터에서 지원자 ID 추출
                    applicant_id = match.get("metadata", {}).get("applicant_id")
                    if not applicant_id or applicant_id in processed_ids:
                        continue

                    # 지원자 정보 조회
                    applicant = await mongo_service.get_applicant(applicant_id)
                    if applicant:
                        # 유사도 점수 계산 (간단한 가중치 기반)
                        similarity_score = self._calculate_similarity_score(
                            applicant, position, skills, experience, department
                        )

                        # 유사도 점수가 일정 임계값 이상인 경우만 포함
                        if similarity_score >= 0.3:  # 30% 이상
                            applicant["similarity_score"] = round(similarity_score * 100, 1)
                            similar_applicants.append(applicant)
                            processed_ids.add(applicant_id)

                # 유사도 점수로 정렬
                similar_applicants.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)

                print(f"[SimilarityService] 최종 유사 지원자: {len(similar_applicants)}명")
                return similar_applicants

            except Exception as e:
                print(f"[SimilarityService] MongoDB 조회 실패: {str(e)}")
                return []

        except Exception as e:
            print(f"[SimilarityService] 유사 지원자 검색 실패: {str(e)}")
            return []

    def _calculate_similarity_score(self, applicant: Dict[str, Any],
                                  position: str, skills: str,
                                  experience: str, department: str) -> float:
        """
        지원자와 검색 기준 간의 유사도 점수를 계산합니다.

        Args:
            applicant (Dict): 지원자 정보
            position (str): 검색 직무
            skills (str): 검색 기술
            experience (str): 검색 경력
            department (str): 검색 부서

        Returns:
            float: 유사도 점수 (0.0 ~ 1.0)
        """
        try:
            score = 0.0
            total_weight = 0.0

            # 직무 유사도 (가중치: 40%)
            if position and applicant.get("position"):
                if position.lower() in applicant["position"].lower():
                    score += 0.4
                elif any(keyword in applicant["position"].lower() for keyword in position.lower().split()):
                    score += 0.2
                total_weight += 0.4

            # 기술스택 유사도 (가중치: 35%)
            if skills and applicant.get("skills"):
                applicant_skills = applicant["skills"]
                if isinstance(applicant_skills, str):
                    applicant_skills = [s.strip() for s in applicant_skills.split(",")]
                elif not isinstance(applicant_skills, list):
                    applicant_skills = [str(applicant_skills)]

                search_skills = [s.strip().lower() for s in skills.split(",")]
                common_skills = sum(1 for skill in search_skills
                                  if any(skill in app_skill.lower() for app_skill in applicant_skills))

                if common_skills > 0:
                    score += (common_skills / len(search_skills)) * 0.35
                total_weight += 0.35

            # 경력 유사도 (가중치: 15%)
            if experience and applicant.get("experience"):
                try:
                    search_exp = float(experience)
                    app_exp = float(applicant["experience"])
                    exp_diff = abs(search_exp - app_exp)
                    if exp_diff <= 2:
                        score += 0.15
                    elif exp_diff <= 5:
                        score += 0.1
                    elif exp_diff <= 10:
                        score += 0.05
                    total_weight += 0.15
                except:
                    pass

            # 부서 유사도 (가중치: 10%)
            if department and applicant.get("department"):
                if department.lower() in applicant["department"].lower():
                    score += 0.1
                total_weight += 0.1

            # 가중치가 0인 경우 기본 점수 반환
            if total_weight == 0:
                return 0.1

            # 정규화된 점수 반환
            return score / total_weight

        except Exception as e:
            print(f"[SimilarityService] 유사도 점수 계산 실패: {str(e)}")
            return 0.0
