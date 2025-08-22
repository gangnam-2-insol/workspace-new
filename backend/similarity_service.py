from typing import List, Dict, Any, Optional
from bson import ObjectId
from pymongo.collection import Collection
from embedding_service import EmbeddingService
from vector_service import VectorService
from chunking_service import ChunkingService
from llm_service import LLMService
from keyword_search_service import KeywordSearchService
import re
from collections import Counter
from datetime import datetime

try:
    from langchain_hybrid_service import LangChainHybridService
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
            # 문서 타입에 따른 분기 처리
            if document_type == "cover_letter":
                return await self._check_cover_letter_plagiarism(document_id, collection, limit)
            else:
                return await self._find_similar_resumes_or_portfolios(document_id, collection, document_type, limit)
                
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
                if not existing_vector.get("vectors") or cover_letter_vector_id not in existing_vector["vectors"]:
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
    
    async def _find_similar_resumes_or_portfolios(self, document_id: str, collection: Collection, 
                                                document_type: str, limit: int = 5) -> Dict[str, Any]:
        """이력서/포트폴리오 유사도 검색 메서드"""
        try:
            print(f"[SimilarityService] === {document_type} 유사도 검색 시작 ===")
            print(f"[SimilarityService] 문서 ID: {document_id}")
            print(f"[SimilarityService] 검색 제한: {limit}")
            print(f"[SimilarityService] 유사도 임계값: {self.similarity_threshold}")
            
            # 해당 문서 조회
            document = await collection.find_one({"_id": ObjectId(document_id)})
            if not document:
                raise ValueError(f"{document_type}을(를) 찾을 수 없습니다.")
            
            print(f"[SimilarityService] {document_type} 찾음")
            
            # 문서 텍스트 추출
            if document_type == "resume":
                document_text = self._extract_resume_text(document)
            elif document_type == "portfolio":
                document_text = self._extract_portfolio_text(document)
            else:
                document_text = self._extract_resume_text(document)  # 기본값
                
            if not document_text:
                raise ValueError(f"{document_type} 텍스트가 없습니다.")
            
            print(f"[SimilarityService] 임베딩 생성할 텍스트 길이: {len(document_text)}")
            print(f"[SimilarityService] 추출된 텍스트: {document_text[:200]}...")
            
            # 임베딩 생성
            query_embedding = await self.embedding_service.create_query_embedding(document_text)
            if not query_embedding:
                raise ValueError(f"{document_type} 임베딩 생성에 실패했습니다.")
            
            print(f"[SimilarityService] {document_type} 임베딩 생성 성공!")
            
            # 현재 문서가 벡터 DB에 있는지 확인하고 없으면 저장
            document_vector_id = f"{document_type}_{document_id}"
            try:
                # Pinecone에서 현재 문서 벡터 확인
                existing_vector = self.vector_service.index.fetch([document_vector_id])
                if not existing_vector.get("vectors") or document_vector_id not in existing_vector["vectors"]:
                    print(f"[SimilarityService] {document_type} 벡터 없음. 벡터 DB에 저장 중...")
                    
                    # 벡터 저장 (직접 upsert 사용하여 고정 ID 지정)
                    vector_data = {
                        "id": document_vector_id,
                        "values": query_embedding,
                        "metadata": {
                            "document_id": document_id,
                            "document_type": document_type, 
                            "chunk_type": document_type,
                            "applicant_id": document.get("applicant_id", ""),
                            "name": document.get("name", ""),
                            "position": document.get("position", ""),
                            "text_preview": document_text[:100] + "..." if len(document_text) > 100 else document_text,
                            "created_at": datetime.now().isoformat()
                        }
                    }
                    
                    self.vector_service.index.upsert(vectors=[vector_data])
                    print(f"[SimilarityService] {document_type} 벡터 저장 완료: {document_vector_id}")
                else:
                    print(f"[SimilarityService] {document_type} 벡터 이미 존재: {document_vector_id}")
            except Exception as e:
                print(f"[SimilarityService] 벡터 확인/저장 중 오류: {e}")
            
            # Pinecone에서 유사한 벡터 검색 (자기 자신 제외)
            print(f"[SimilarityService] Pinecone 유사도 검색 시작...")
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit + 1,  # 자기 자신을 포함할 수 있으므로 +1
                filter_type=document_type
            )
            
            print(f"[SimilarityService] Pinecone 검색 완료! 결과 수: {len(search_result['matches'])}")
            
            # 자기 자신 제외하고 유사한 문서들 필터링 (임계값 적용)
            similar_documents = []
            for match in search_result["matches"]:
                match_document_id = match["metadata"]["resume_id"]  # 메타데이터 키 확인 필요
                similarity_score = match["score"]
                
                print(f"[SimilarityService] 검색 결과 - ID: {match_document_id}, 점수: {similarity_score:.3f}")
                
                # 자기 자신 제외하고 유사도 임계값 이상인 것만 포함
                if match_document_id != str(document["_id"]) and similarity_score >= self.similarity_threshold:
                    similar_documents.append(match)
                    print(f"[SimilarityService] 유사 {document_type} 추가: {match_document_id} (점수: {similarity_score:.3f})")
                else:
                    print(f"[SimilarityService] 제외된 {document_type}: {match_document_id} (점수: {similarity_score:.3f})")
            
            print(f"[SimilarityService] 자기 자신 제외 후 유사 {document_type} 수: {len(similar_documents)}")
            
            # MongoDB에서 상세 정보 조회
            results = []
            if similar_documents:
                document_ids = [ObjectId(match["metadata"]["resume_id"]) for match in similar_documents]
                documents_detail = await collection.find({"_id": {"$in": document_ids}}).to_list(1000)
                
                # 검색 결과와 상세 정보 매칭
                for match in similar_documents:
                    document_detail = next((d for d in documents_detail if str(d["_id"]) == match["metadata"]["resume_id"]), None)
                    if document_detail:
                        document_detail["_id"] = str(document_detail["_id"])
                        
                        # 모든 datetime 필드를 문자열로 변환 (JSON 직렬화를 위해)
                        for key, value in list(document_detail.items()):
                            if hasattr(value, 'isoformat'):  # datetime 객체인지 확인
                                document_detail[key] = value.isoformat()
                            elif key == "_id":
                                document_detail[key] = str(value)  # ObjectId도 문자열로
                        
                        # 유사도 점수를 백분율로 변환
                        similarity_percentage = round(match["score"] * 100, 1)
                        
                        # LLM을 통한 유사성 분석 추가
                        llm_analysis = await self.llm_service.analyze_similarity_reasoning(
                            original_resume=document,
                            similar_resume=document_detail,
                            similarity_score=match["score"]
                        )
                        
                        results.append({
                            "similarity_score": match["score"],
                            "similarity_percentage": similarity_percentage,
                            document_type: document_detail,
                            "llm_analysis": llm_analysis
                        })
                
                # 유사도 점수로 정렬 (높은 순)
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                
                # 전체 결과에 대한 표절 위험도 분석 추가
                plagiarism_analysis = await self.llm_service.analyze_plagiarism_risk(
                    original_resume=document,
                    similar_resumes=results
                )
                
                print(f"[SimilarityService] 최종 유사 {document_type} 수: {len(results)}")
                print(f"[SimilarityService] === {document_type} 유사도 검색 완료 ===")
                
                return {
                    "success": True,
                    "document_type": document_type,
                    "analysis_type": "similarity_search",
                    "data": {
                        f"original_{document_type}": {
                            "id": str(document["_id"]),
                            "applicant_id": document.get("applicant_id", "")
                        },
                        f"similar_{document_type}s": results,
                        "total": len(results),
                        "plagiarism_analysis": plagiarism_analysis
                    }
                }
            else:
                print(f"유사한 {document_type}이(가) 없습니다.")
                print(f"=== {document_type} 유사도 검색 완료 ===")
                
                return {
                    "success": True,
                    "document_type": document_type,
                    "analysis_type": "similarity_search",
                    "data": {
                        f"original_{document_type}": {
                            "id": str(document["_id"]),
                            "applicant_id": document.get("applicant_id", "")
                        },
                        f"similar_{document_type}s": [],
                        "total": 0
                    }
                }
                
        except Exception as e:
            print(f"=== {document_type} 유사도 검색 중 오류 발생 ===")
            print(f"오류 메시지: {str(e)}")
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
    
    def _extract_resume_text(self, resume: Dict[str, Any]) -> str:
        """
        이력서 데이터에서 텍스트를 추출합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            str: 추출된 텍스트
        """
        # ResumeUpload 모델의 경우
        if "resume_text" in resume and resume["resume_text"]:
            extracted_text = self._preprocess_text(resume["resume_text"])
            print(f"[SimilarityService] 추출된 이력서 텍스트 (resume_text): '{extracted_text}'")
            return extracted_text
        
        # OCR 업로드 모델의 경우
        elif "extracted_text" in resume and resume["extracted_text"]:
            ocr_text = resume["extracted_text"].strip()
            summary = resume.get("summary", "").strip()
            
            # OCR 텍스트와 요약을 결합
            text_parts = []
            if ocr_text and not self._is_meaningless_text(ocr_text):
                text_parts.append(ocr_text)
            if summary and not self._is_meaningless_text(summary):
                text_parts.append(f"요약: {summary}")
            
            combined_text = " ".join(text_parts)
            extracted_text = self._preprocess_text(combined_text)
            print(f"[SimilarityService] 추출된 이력서 텍스트 (OCR): '{extracted_text[:200]}...' (총 길이: {len(extracted_text)})")
            return extracted_text
        
        # ResumeCreate 모델의 경우 지정된 필드들만 사용
        else:
            # position, department, experience, skills, name 제외하고 다른 필드들만 사용
            growth_background = resume.get("growthBackground", "").strip()
            motivation = resume.get("motivation", "").strip()
            career_history = resume.get("careerHistory", "").strip()
            
            # 허용된 필드만 텍스트로 결합
            text_parts = []
            if growth_background and not self._is_meaningless_text(growth_background):
                text_parts.append(f"성장배경: {growth_background}")
            if motivation and not self._is_meaningless_text(motivation):
                text_parts.append(f"지원동기: {motivation}")
            if career_history and not self._is_meaningless_text(career_history):
                text_parts.append(f"경력사항: {career_history}")
            
            combined_text = " ".join(text_parts)
            extracted_text = self._preprocess_text(combined_text)
            print(f"[SimilarityService] 추출된 이력서 텍스트 (제외 필드 없음): '{extracted_text}'")
            return extracted_text
        
        print(f"[SimilarityService] 텍스트 추출 실패 - 빈 텍스트 반환")
        return ""

    def _is_meaningless_text(self, text: str) -> bool:
        """
        텍스트가 의미없는지 확인합니다.
        
        Args:
            text (str): 확인할 텍스트
            
        Returns:
            bool: 의미없는 텍스트인지 여부
        """
        if not text:
            return True
        
        text = text.strip()
        
        # 빈 문자열
        if not text:
            return True
        
        # 너무 짧은 특수문자나 공백만 있는 경우 (한글, 영문, 숫자 없음)
        if len(text) <= 2 and not re.search(r'[가-힣a-zA-Z0-9]', text):
            return True
        
        # 의미있는 내용으로 간주 (숫자도 포함, 길이 제한도 완화)
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
        
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 특수문자 정리 (한글, 영문, 숫자, 기본 문장부호만 유지)
        text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.,!?()\-]', ' ', text)
        
        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

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

    def _calculate_keyword_similarity(self, resume_a: Dict[str, Any], resume_b: Dict[str, Any]) -> float:
        """
        두 이력서의 키워드 유사도를 계산합니다.
        
        Args:
            resume_a (Dict[str, Any]): 첫 번째 이력서
            resume_b (Dict[str, Any]): 두 번째 이력서
            
        Returns:
            float: 키워드 유사도 점수 (0-1)
        """
        try:
            # 중요 키워드 필드들 (성장배경, 지원동기, 경력사항만 사용)
            keyword_fields = ['growthBackground', 'motivation', 'careerHistory']
            
            keywords_a = set()
            keywords_b = set()
            
            # 각 이력서에서 키워드 추출
            for field in keyword_fields:
                if field in resume_a and resume_a[field]:
                    keywords_a.add(resume_a[field].lower().strip())
                if field in resume_b and resume_b[field]:
                    keywords_b.add(resume_b[field].lower().strip())
            
            # 키워드 유사도 계산
            if not keywords_a or not keywords_b:
                return 0.0
            
            intersection = len(keywords_a.intersection(keywords_b))
            union = len(keywords_a.union(keywords_b))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            print(f"[SimilarityService] 키워드 유사도 계산 중 오류: {str(e)}")
            return 0.0

    # 기존 비효율적인 상호 유사도 함수 (사용 안함)
    # async def _get_reverse_similarity(self, resume_id_a: str, resume_id_b: str, collection: Collection) -> Optional[float]:
    #     """비효율적 - 매번 새 임베딩 생성 + Pinecone 검색"""
    #     pass


    async def search_resumes_multi_hybrid(self, query: str, collection: Collection, 
                                        search_type: str = "resume", limit: int = 10) -> Dict[str, Any]:
        """
        다중 하이브리드 검색: 벡터 + 키워드 검색을 결합합니다.
        
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
            print(f"[SimilarityService] 가중치 - 벡터: {self.search_weights['vector']}, "
                  f"키워드: {self.search_weights['keyword']}")
            
            if not query or not query.strip():
                raise ValueError("검색어를 입력해주세요.")
            
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
            print(f"[SimilarityService] === 다중 하이브리드 검색 완료 ===")
            
            return {
                "success": True,
                "data": {
                    "query": query,
                    "search_method": "multi_hybrid",
                    "weights": self.search_weights,
                    "results": fused_results,
                    "total": len(fused_results),
                    "vector_count": len(vector_results),
                    "keyword_count": len(keyword_results)
                }
            }
            
        except Exception as e:
            print(f"[SimilarityService] 다중 하이브리드 검색 실패: {str(e)}")
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
                        filter_type="resume"
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
                return await self.langchain_hybrid.search_similar_applicants_langchain(
                    vector_query=vector_query_text,
                    keyword_query=keyword_query_text,
                    applicants_collection=applicants_collection,
                    target_applicant=target_applicant,
                    limit=limit
                )
            
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
                # 벡터 결과에서 document_id(resume_id)를 통해 지원자 찾기
                resume_id = match["metadata"].get("document_id")
                if resume_id and resume_id != str(target_applicant.get("resume_id")):
                    # resume_id로 지원자 찾기
                    applicant = await applicants_collection.find_one({"resume_id": resume_id})
                    if applicant:
                        applicant_id = str(applicant["_id"])
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
