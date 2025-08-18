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
        
        # 유사도 임계값 설정
        self.similarity_threshold = 0.3   # 30%로 설정
        # 필드별 최소 유사도 임계값 (성장배경, 지원동기, 경력사항만 사용)
        self.field_thresholds = {
            'growthBackground': 0.2,   # 성장배경 20% 이상
            'motivation': 0.2,         # 지원동기 20% 이상
            'careerHistory': 0.2,      # 경력사항 20% 이상
        }
        
        # 다중 검색 가중치 설정 (벡터 + 텍스트 + 키워드)
        self.search_weights = {
            'vector': 0.5,    # 벡터 검색 50%
            'text': 0.3,      # 텍스트 검색 30%
            'keyword': 0.2    # 키워드 검색 20%
        }
    
    async def save_resume_chunks(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        이력서를 청킹하여 벡터 저장합니다.
        
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
    
    async def find_similar_resumes_by_chunks(self, resume_id: str, collection: Collection, limit: int = 5) -> Dict[str, Any]:
        """
        청킹 기반으로 특정 이력서와 유사한 이력서들을 찾습니다.
        
        Args:
            resume_id (str): 기준이 되는 이력서 ID
            collection (Collection): MongoDB 컬렉션
            limit (int): 반환할 최대 결과 수
            
        Returns:
            Dict[str, Any]: 유사도 검색 결과
        """
        try:
            print(f"[SimilarityService] === 청킹 기반 유사도 검색 시작 ===")
            print(f"[SimilarityService] 이력서 ID: {resume_id}")
            
            # 해당 이력서 조회
            resume = await collection.find_one({"_id": ObjectId(resume_id)})
            if not resume:
                raise ValueError("이력서를 찾을 수 없습니다.")
            
            # 이력서를 청크로 분할
            query_chunks = self.chunking_service.chunk_resume_text(resume)
            if not query_chunks:
                raise ValueError("검색할 청크가 없습니다.")
            
            print(f"[SimilarityService] 검색 청크 수: {len(query_chunks)}")
            
            # 각 청크별로 유사 벡터 검색
            chunk_similarities = {}
            for chunk in query_chunks:
                print(f"[SimilarityService] 청크 '{chunk['chunk_type']}' 검색 중...")
                
                # 청크 텍스트로 임베딩 생성
                query_embedding = await self.embedding_service.create_embedding(chunk["text"])
                if not query_embedding:
                    continue
                
                # Pinecone에서 유사한 벡터 검색
                search_result = await self.vector_service.search_similar_vectors(
                    query_embedding=query_embedding,
                    top_k=limit * 3,  # 청크별로 더 많이 검색
                    filter_type="resume"
                )
                
                # 결과 저장
                for match in search_result["matches"]:
                    match_resume_id = match["metadata"]["resume_id"]
                    similarity_score = match["score"]
                    chunk_type = match["metadata"]["chunk_type"]
                    
                    # 자기 자신 제외
                    if match_resume_id == resume_id:
                        continue
                    
                    # 이력서별로 청크 유사도 누적
                    if match_resume_id not in chunk_similarities:
                        chunk_similarities[match_resume_id] = {
                            "chunks": {},
                            "total_score": 0.0,
                            "chunk_count": 0
                        }
                    
                    # 동일한 청크 타입에서 더 높은 점수만 유지
                    key = f"{chunk['chunk_type']}_to_{chunk_type}"
                    if key not in chunk_similarities[match_resume_id]["chunks"] or \
                       similarity_score > chunk_similarities[match_resume_id]["chunks"][key]["score"]:
                        
                        chunk_similarities[match_resume_id]["chunks"][key] = {
                            "score": similarity_score,
                            "query_chunk": chunk['chunk_type'],
                            "match_chunk": chunk_type,
                            "match_text": match["metadata"].get("text_preview", "")
                        }
            
            # 이력서별 종합 점수 계산
            resume_scores = []
            for match_resume_id, data in chunk_similarities.items():
                if not data["chunks"]:
                    continue
                
                # 청크 점수들의 평균 계산
                chunk_scores = [chunk_data["score"] for chunk_data in data["chunks"].values()]
                avg_score = sum(chunk_scores) / len(chunk_scores)
                
                # 임계값 체크
                if avg_score >= self.similarity_threshold:
                    resume_scores.append({
                        "resume_id": match_resume_id,
                        "similarity_score": avg_score,
                        "chunk_matches": len(data["chunks"]),
                        "chunk_details": data["chunks"]
                    })
            
            # 점수 순으로 정렬
            resume_scores.sort(key=lambda x: x["similarity_score"], reverse=True)
            resume_scores = resume_scores[:limit]
            
            # MongoDB에서 상세 정보 조회
            results = []
            if resume_scores:
                resume_ids = [ObjectId(score["resume_id"]) for score in resume_scores]
                resumes_detail = await collection.find({"_id": {"$in": resume_ids}}).to_list(1000)
                
                for score_data in resume_scores:
                    resume_detail = next((r for r in resumes_detail if str(r["_id"]) == score_data["resume_id"]), None)
                    if resume_detail:
                        resume_detail["_id"] = str(resume_detail["_id"])
                        resume_detail["created_at"] = resume_detail["created_at"].isoformat()
                        
                        # LLM을 통한 유사성 분석 추가
                        llm_analysis = await self.llm_service.analyze_similarity_reasoning(
                            original_resume=resume,
                            similar_resume=resume_detail,
                            similarity_score=score_data["similarity_score"],
                            chunk_details=score_data["chunk_details"]
                        )
                        
                        results.append({
                            "similarity_score": score_data["similarity_score"],
                            "similarity_percentage": round(score_data["similarity_score"] * 100, 1),
                            "chunk_matches": score_data["chunk_matches"],
                            "resume": resume_detail,
                            "chunk_details": score_data["chunk_details"],
                            "llm_analysis": llm_analysis
                        })
            
            # 전체 결과에 대한 표절 위험도 분석 추가
            plagiarism_analysis = await self.llm_service.analyze_plagiarism_risk(
                original_resume=resume,
                similar_resumes=results
            )
            
            print(f"[SimilarityService] 최종 유사 이력서 수: {len(results)}")
            print(f"[SimilarityService] === 청킹 기반 유사도 검색 완료 ===")
            
            return {
                "success": True,
                "data": {
                    "original_resume": {
                        "id": str(resume["_id"]),
                        "name": resume.get("name", "Unknown"),
                        "chunk_count": len(query_chunks)
                    },
                    "similar_resumes": results,
                    "total": len(results),
                    "plagiarism_analysis": plagiarism_analysis
                }
            }
            
        except Exception as e:
            print(f"[SimilarityService] 청킹 기반 유사도 검색 실패: {str(e)}")
            raise e

    async def find_similar_resumes(self, resume_id: str, collection: Collection, limit: int = 5) -> Dict[str, Any]:
        """
        특정 이력서와 유사한 이력서들을 찾습니다.
        
        Args:
            resume_id (str): 기준이 되는 이력서 ID
            collection (Collection): MongoDB 컬렉션
            limit (int): 반환할 최대 결과 수
            
        Returns:
            Dict[str, Any]: 유사도 검색 결과
        """
        try:
            print(f"[SimilarityService] === 유사도 검색 시작 ===")
            print(f"[SimilarityService] 이력서 ID: {resume_id}")
            print(f"[SimilarityService] 검색 제한: {limit}")
            print(f"[SimilarityService] 유사도 임계값: {self.similarity_threshold}")
            
            # 해당 이력서 조회
            resume = await collection.find_one({"_id": ObjectId(resume_id)})
            if not resume:
                raise ValueError("이력서를 찾을 수 없습니다.")
            
            print(f"[SimilarityService] 이력서 찾음: {resume.get('name', 'Unknown')}")
            
            # 이력서 텍스트로 임베딩 생성
            resume_text = self._extract_resume_text(resume)
            if not resume_text:
                raise ValueError("이력서 텍스트가 없습니다.")
            
            print(f"[SimilarityService] 임베딩 생성할 텍스트 길이: {len(resume_text)}")
            print(f"[SimilarityService] 추출된 텍스트: {resume_text[:200]}...")
            
            # 임베딩 생성
            query_embedding = await self.embedding_service.create_embedding(resume_text)
            if not query_embedding:
                raise ValueError("이력서 임베딩 생성에 실패했습니다.")
            
            print(f"[SimilarityService] 이력서 임베딩 생성 성공!")
            
            # Pinecone에서 유사한 벡터 검색 (자기 자신 제외)
            print(f"[SimilarityService] Pinecone 유사도 검색 시작...")
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit + 1,  # 자기 자신을 포함할 수 있으므로 +1
                filter_type="resume"
            )
            
            print(f"[SimilarityService] Pinecone 검색 완료! 결과 수: {len(search_result['matches'])}")
            
            # 자기 자신 제외하고 유사한 이력서들 필터링 (임계값 적용)
            similar_resumes = []
            for match in search_result["matches"]:
                match_resume_id = match["metadata"]["resume_id"]
                similarity_score = match["score"]
                
                print(f"[SimilarityService] 검색 결과 - ID: {match_resume_id}, 점수: {similarity_score:.3f}")
                
                # 자기 자신 제외하고 유사도 임계값(0.6) 이상인 것만 포함
                if match_resume_id != str(resume["_id"]) and similarity_score >= self.similarity_threshold:
                    similar_resumes.append(match)
                    print(f"[SimilarityService] 유사 이력서 추가: {match_resume_id} (점수: {similarity_score:.3f})")
                else:
                    print(f"[SimilarityService] 제외된 이력서: {match_resume_id} (점수: {similarity_score:.3f})")
            
            print(f"[SimilarityService] 자기 자신 제외 후 유사 이력서 수: {len(similar_resumes)}")
            
            # MongoDB에서 상세 정보 조회
            if similar_resumes:
                resume_ids = [ObjectId(match["metadata"]["resume_id"]) for match in similar_resumes]
                resumes_detail = await collection.find({"_id": {"$in": resume_ids}}).to_list(1000)
                
                # 검색 결과와 상세 정보 매칭
                results = []
                for match in similar_resumes:
                    resume_detail = next((r for r in resumes_detail if str(r["_id"]) == match["metadata"]["resume_id"]), None)
                    if resume_detail:
                        resume_detail["_id"] = str(resume_detail["_id"])
                        if "resume_id" in resume_detail:
                            resume_detail["resume_id"] = str(resume_detail["resume_id"])
                        else:
                            resume_detail["resume_id"] = str(resume_detail["_id"])
                        resume_detail["created_at"] = resume_detail["created_at"].isoformat()
                        
                        # 유사도 점수를 백분율로 변환 (0-1 범위를 0-100으로)
                        similarity_percentage = round(match["score"] * 100, 1)
                        
                        # 상호 유사도 검증을 위한 추가 정보 (텍스트 기반으로 계산)
                        reverse_similarity = self._calculate_reverse_text_similarity(resume, resume_detail)
                        
                        # 상호 유사도의 평균값 사용 (더 일관된 결과를 위해)
                        if reverse_similarity is not None:
                            avg_similarity = (match["score"] + reverse_similarity) / 2
                            avg_percentage = round(avg_similarity * 100, 1)
                            print(f"[SimilarityService] 상호 유사도 - A→B: {similarity_percentage}%, B→A: {round(reverse_similarity * 100, 1)}%, 평균: {avg_percentage}%")
                            similarity_percentage = avg_percentage
                            match["score"] = avg_similarity
                        
                        # 추가적인 유사도 검증 (텍스트 기반)
                        text_similarity = self._calculate_text_similarity(resume, resume_detail)
                        if text_similarity is not None:
                            # 벡터 유사도와 텍스트 유사도의 가중 평균 사용
                            final_similarity = (match["score"] * 0.7 + text_similarity * 0.3)
                            final_percentage = round(final_similarity * 100, 1)
                            print(f"[SimilarityService] 텍스트 유사도: {round(text_similarity * 100, 1)}%, 최종 유사도: {final_percentage}%")
                            
                            # 필드별 임계값 검증 (너무 엄격하지 않게 수정)
                            field_validation = self._validate_field_thresholds(resume, resume_detail)
                            if field_validation or final_similarity > 0.8:  # 80% 이상이면 필드 검증 무시
                                similarity_percentage = final_percentage
                                match["score"] = final_similarity
                                print(f"[SimilarityService] 필드 임계값 검증 통과 (필드검증: {field_validation}, 높은유사도: {final_similarity > 0.8})")
                            else:
                                print(f"[SimilarityService] 필드 임계값 검증 실패 - 하지만 유사도가 낮아서 제외")
                                continue
                        else:
                            # 텍스트 유사도 계산 실패 시 벡터 유사도만 사용
                            print(f"[SimilarityService] 텍스트 유사도 계산 실패, 벡터 유사도만 사용")
                        
                        # LLM을 통한 유사성 분석 추가
                        llm_analysis = await self.llm_service.analyze_similarity_reasoning(
                            original_resume=resume,
                            similar_resume=resume_detail,
                            similarity_score=match["score"]
                        )
                        
                        results.append({
                            "similarity_score": match["score"],
                            "similarity_percentage": similarity_percentage,
                            "resume": resume_detail,
                            "llm_analysis": llm_analysis
                        })
                
                # 유사도 점수로 정렬 (높은 순)
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                
                # 전체 결과에 대한 표절 위험도 분석 추가
                plagiarism_analysis = await self.llm_service.analyze_plagiarism_risk(
                    original_resume=resume,
                    similar_resumes=results
                )
                
                print(f"[SimilarityService] 최종 유사 이력서 수: {len(results)}")
                for result in results:
                    print(f"[SimilarityService] 최종 결과: {result['resume']['name']} (점수: {result['similarity_percentage']}%)")
                print(f"[SimilarityService] === 유사도 검색 완료 ===")
                
                return {
                    "success": True,
                    "data": {
                        "original_resume": {
                            "id": str(resume["_id"]),
                            "name": resume.get("name", "Unknown"),
                            "position": resume.get("position", ""),
                            "department": resume.get("department", "")
                        },
                        "similar_resumes": results,
                        "total": len(results),
                        "plagiarism_analysis": plagiarism_analysis
                    }
                }
            else:
                print(f"유사한 이력서가 없습니다.")
                print(f"=== 유사도 검색 완료 ===")
                
                return {
                    "success": True,
                    "data": {
                        "original_resume": {
                            "id": str(resume["_id"]),
                            "name": resume.get("name", "Unknown"),
                            "position": resume.get("position", ""),
                            "department": resume.get("department", "")
                        },
                        "similar_resumes": [],
                        "total": 0
                    }
                }
                
        except Exception as e:
            print(f"=== 유사도 검색 중 오류 발생 ===")
            print(f"오류 메시지: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
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
            
            query_embedding = await self.embedding_service.create_embedding(query)
            
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
            resumes = list(collection.find({"_id": {"$in": resume_ids}}))
            
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
            print(f"[SimilarityService] 추출된 이력서 텍스트: '{extracted_text}'")
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

    def _calculate_text_similarity(self, resume_a: Dict[str, Any], resume_b: Dict[str, Any]) -> Optional[float]:
        """
        두 이력서 간의 텍스트 기반 유사도를 계산합니다.
        
        Args:
            resume_a (Dict[str, Any]): 첫 번째 이력서
            resume_b (Dict[str, Any]): 두 번째 이력서
            
        Returns:
            Optional[float]: 텍스트 유사도 점수 (0-1)
        """
        try:
            # 필드별 가중치 정의 (성장배경, 지원동기, 경력사항만 사용)
            field_weights = {
                'growthBackground': 0.4,   # 성장배경 (가장 중요)
                'motivation': 0.35,        # 지원동기 
                'careerHistory': 0.25,     # 경력사항
            }
            
            total_similarity = 0.0
            total_weight = 0.0
            
            # 각 필드별 유사도 계산
            for field, weight in field_weights.items():
                value_a = resume_a.get(field, "").strip().lower()
                value_b = resume_b.get(field, "").strip().lower()
                
                # 의미없는 텍스트는 제외
                if self._is_meaningless_text(value_a) or self._is_meaningless_text(value_b):
                    print(f"[SimilarityService] {field} 필드 의미없는 텍스트 제외")
                    continue
                
                if value_a and value_b:
                    # 필드별 유사도 계산
                    field_similarity = self._calculate_field_similarity(value_a, value_b, field)
                    total_similarity += field_similarity * weight
                    total_weight += weight
                    print(f"[SimilarityService] {field} 유사도: {field_similarity:.3f} (가중치: {weight})")
            
            # 전체 유사도 계산
            if total_weight > 0:
                final_similarity = total_similarity / total_weight
                print(f"[SimilarityService] 필드별 가중 평균 유사도: {final_similarity:.3f}")
                return final_similarity
            
            # 의미있는 필드가 없는 경우 기본 유사도 반환
            print(f"[SimilarityService] 의미있는 필드가 없음, 기본 유사도 계산")
            return self._calculate_basic_similarity(resume_a, resume_b)
            
        except Exception as e:
            print(f"[SimilarityService] 텍스트 유사도 계산 중 오류: {str(e)}")
            return None

    def _calculate_basic_similarity(self, resume_a: Dict[str, Any], resume_b: Dict[str, Any]) -> float:
        """
        기본 유사도를 계산합니다.
        
        Args:
            resume_a (Dict[str, Any]): 첫 번째 이력서
            resume_b (Dict[str, Any]): 두 번째 이력서
            
        Returns:
            float: 기본 유사도 점수 (0-1)
        """
        try:
            # 모든 필드를 하나의 텍스트로 결합
            text_a = self._extract_resume_text(resume_a)
            text_b = self._extract_resume_text(resume_b)
            
            if not text_a or not text_b:
                return 0.0
            
            # Jaccard 유사도 계산
            words_a = set(text_a.lower().split())
            words_b = set(text_b.lower().split())
            
            if not words_a or not words_b:
                return 0.0
            
            intersection = len(words_a.intersection(words_b))
            union = len(words_a.union(words_b))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            print(f"[SimilarityService] 기본 유사도 계산 중 오류: {str(e)}")
            return 0.0

    def _calculate_field_similarity(self, value_a: str, value_b: str, field_type: str) -> float:
        """
        특정 필드의 유사도를 계산합니다.
        
        Args:
            value_a (str): 첫 번째 값
            value_b (str): 두 번째 값
            field_type (str): 필드 타입
            
        Returns:
            float: 필드 유사도 점수 (0-1)
        """
        try:
            if not value_a or not value_b:
                return 0.0
            
            # 필드 타입에 따른 유사도 계산 방식 선택
            if field_type in ['growthBackground', 'motivation', 'careerHistory']:
                # 성장배경, 지원동기, 경력사항은 긴 텍스트 유사도로 계산
                if value_a == value_b:
                    return 1.0
                words_a = set(value_a.split())
                words_b = set(value_b.split())
                intersection = len(words_a.intersection(words_b))
                union = len(words_a.union(words_b))
                return intersection / union if union > 0 else 0.0
            
            else:
                # 기본 Jaccard 유사도
                words_a = set(value_a.split())
                words_b = set(value_b.split())
                intersection = len(words_a.intersection(words_b))
                union = len(words_a.union(words_b))
                return intersection / union if union > 0 else 0.0
                
        except Exception as e:
            print(f"[SimilarityService] 필드 유사도 계산 중 오류: {str(e)}")
            return 0.0

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

    def _validate_field_thresholds(self, resume_a: Dict[str, Any], resume_b: Dict[str, Any]) -> bool:
        """
        두 이력서 간의 필드별 임계값을 검증합니다.
        
        Args:
            resume_a (Dict[str, Any]): 첫 번째 이력서
            resume_b (Dict[str, Any]): 두 번째 이력서
            
        Returns:
            bool: 임계값 검증 결과
        """
        valid_field_count = 0
        passed_field_count = 0
        
        for field, threshold in self.field_thresholds.items():
            value_a = resume_a.get(field, "").strip().lower()
            value_b = resume_b.get(field, "").strip().lower()
            
            # 의미없는 텍스트나 빈 값은 검증에서 제외하되, 너무 많이 제외되지 않도록 함
            if self._is_meaningless_text(value_a) or self._is_meaningless_text(value_b) or not value_a or not value_b:
                print(f"[SimilarityService] 필드 '{field}' 의미없는/빈 텍스트, 임계값 검증 제외")
                continue
            
            valid_field_count += 1
            field_similarity = self._calculate_field_similarity(value_a, value_b, field)
            
            if field_similarity >= threshold:
                passed_field_count += 1
                print(f"[SimilarityService] 필드 '{field}' 임계값 달성: {field_similarity:.3f} >= {threshold}")
            else:
                print(f"[SimilarityService] 필드 '{field}' 임계값 미달: {field_similarity:.3f} < {threshold}")
        
        # 검증 가능한 필드가 없으면 통과로 처리
        if valid_field_count == 0:
            print(f"[SimilarityService] 검증 가능한 필드가 없음 - 통과 처리")
            return True
        
        # 절반 이상의 필드가 통과하면 OK
        threshold_ratio = passed_field_count / valid_field_count
        result = threshold_ratio >= 0.5
        
        print(f"[SimilarityService] 필드 검증 결과: {passed_field_count}/{valid_field_count} 통과 ({threshold_ratio:.2f}) -> {'통과' if result else '실패'}")
        return result
    
    def _calculate_reverse_text_similarity(self, resume_a: Dict[str, Any], resume_b: Dict[str, Any]) -> Optional[float]:
        """
        텍스트 기반으로 상호 유사도를 효율적으로 계산합니다.
        
        Args:
            resume_a (Dict[str, Any]): 첫 번째 이력서
            resume_b (Dict[str, Any]): 두 번째 이력서
            
        Returns:
            Optional[float]: 상호 유사도 점수 (0-1)
        """
        try:
            # 새로운 필드들로 상호 유사도 계산 (성장배경, 지원동기, 경력사항)
            fields_to_compare = ['growthBackground', 'motivation', 'careerHistory']
            
            total_similarity = 0.0
            valid_comparisons = 0
            
            for field in fields_to_compare:
                value_a = resume_a.get(field, "").strip().lower()
                value_b = resume_b.get(field, "").strip().lower()
                
                # 빈 값이거나 의미없는 텍스트는 건너뛰기
                if (self._is_meaningless_text(value_a) or 
                    self._is_meaningless_text(value_b) or 
                    not value_a or not value_b):
                    continue
                
                # A→B와 B→A 양방향 유사도 계산
                similarity_ab = self._calculate_field_similarity(value_a, value_b, field)
                similarity_ba = self._calculate_field_similarity(value_b, value_a, field)
                
                # 양방향 유사도의 평균
                bidirectional_similarity = (similarity_ab + similarity_ba) / 2
                total_similarity += bidirectional_similarity
                valid_comparisons += 1
                
                print(f"[SimilarityService] {field} 상호유사도: A→B={similarity_ab:.3f}, B→A={similarity_ba:.3f}, 평균={bidirectional_similarity:.3f}")
            
            if valid_comparisons == 0:
                print(f"[SimilarityService] 상호 유사도 계산 불가 - 비교 가능한 필드 없음")
                return None
            
            average_similarity = total_similarity / valid_comparisons
            print(f"[SimilarityService] 전체 상호 유사도: {average_similarity:.3f} ({valid_comparisons}개 필드)")
            
            return average_similarity
            
        except Exception as e:
            print(f"[SimilarityService] 상호 유사도 계산 중 오류: {str(e)}")
            return None

    async def search_resumes_multi_hybrid(self, query: str, collection: Collection, 
                                        search_type: str = "resume", limit: int = 10) -> Dict[str, Any]:
        """
        다중 하이브리드 검색: 벡터 + 텍스트 + 키워드 검색을 결합합니다.
        
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
                  f"텍스트: {self.search_weights['text']}, 키워드: {self.search_weights['keyword']}")
            
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
            query_embedding = await self.embedding_service.create_embedding(query)
            if not query_embedding:
                return []
            
            # Pinecone 벡터 검색
            search_result = await self.vector_service.search_similar_vectors(
                query_embedding=query_embedding,
                top_k=limit,
                filter_type=search_type
            )
            
            # 결과 포맷팅
            vector_results = []
            for match in search_result["matches"]:
                vector_results.append({
                    "resume_id": match["metadata"]["resume_id"],
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
            resumes = list(collection.find({"_id": {"$in": resume_ids_obj}}))
            
            # 융합 점수 계산
            fused_results = []
            for resume in resumes:
                resume_id = str(resume["_id"])
                
                # 각 검색 방법의 점수 가져오기 (없으면 0)
                v_score = vector_scores.get(resume_id, 0.0)
                k_score = keyword_scores.get(resume_id, 0.0)
                
                # 키워드 점수 정규화 (BM25 점수는 보통 0-10 범위)
                k_score_normalized = min(k_score / 10.0, 1.0) if k_score > 0 else 0.0
                
                # 텍스트 유사도 계산 (기존 로직 활용)
                text_score = 0.0
                if v_score > 0:  # 벡터 검색에서 발견된 경우만
                    # 간단한 텍스트 유사도 계산
                    resume_text = self._extract_resume_text(resume).lower()
                    query_words = set(query.lower().split())
                    resume_words = set(resume_text.split())
                    
                    if query_words and resume_words:
                        intersection = len(query_words.intersection(resume_words))
                        union = len(query_words.union(resume_words))
                        text_score = intersection / union if union > 0 else 0.0
                
                # 가중 평균으로 최종 점수 계산
                final_score = (
                    v_score * self.search_weights['vector'] +
                    text_score * self.search_weights['text'] +
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
                    
                    if "created_at" in resume:
                        resume["created_at"] = resume["created_at"].isoformat()
                    
                    fused_results.append({
                        "final_score": final_score,
                        "vector_score": v_score,
                        "text_score": text_score,
                        "keyword_score": k_score_normalized,
                        "original_keyword_score": k_score,
                        "resume": resume,
                        "search_methods": [
                            method for method, score in [
                                ("vector", v_score), 
                                ("text", text_score), 
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
                print(f"[SimilarityService] #{i+1}: {result['resume']['name']} "
                      f"(최종:{result['final_score']:.3f}, V:{result['vector_score']:.3f}, "
                      f"T:{result['text_score']:.3f}, K:{result['keyword_score']:.3f})")
            
            return final_results
            
        except Exception as e:
            print(f"[SimilarityService] 검색 결과 융합 실패: {str(e)}")
            return []
