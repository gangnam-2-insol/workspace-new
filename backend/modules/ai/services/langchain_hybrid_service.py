import asyncio
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from langchain.retrievers import EnsembleRetriever
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever
    # from langchain_elasticsearch import ElasticsearchStore  # Elasticsearch 비활성화
    from langchain_openai import OpenAIEmbeddings
    from langchain_pinecone import PineconeVectorStore
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"LangChain 라이브러리가 설치되지 않았습니다: {e}")

# from elasticsearch import Elasticsearch  # Elasticsearch 비활성화
from pinecone import Pinecone


class LangChainHybridService:
    def __init__(self, vector_weight=0.5, keyword_weight=0.5):
        """
        LangChain 기반 하이브리드 검색 서비스 초기화
        
        Args:
            vector_weight (float): 벡터 검색 가중치 (기본값: 0.5)
            keyword_weight (float): 키워드 검색 가중치 (기본값: 0.5)
        """
        # 가중치 저장
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # 가중치 정규화 (합이 1이 되도록)
        total_weight = self.vector_weight + self.keyword_weight
        if total_weight > 0:
            self.vector_weight /= total_weight
            self.keyword_weight /= total_weight
        if not LANGCHAIN_AVAILABLE:
            raise Exception("LangChain 라이브러리가 필요합니다. pip install langchain langchain-openai langchain-pinecone langchain-elasticsearch로 설치하세요.")

        # 환경 변수 로드
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")
        # Elasticsearch 설정 (비활성화됨)
        self.es_host = None
        self.es_index = None
        self.es_username = None
        self.es_password = None

        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY가 설정되지 않았습니다.")
        if not self.pinecone_api_key:
            raise Exception("PINECONE_API_KEY가 설정되지 않았습니다.")

        # LangChain 컴포넌트 초기화
        self._initialize_langchain_components()

        print(f"[LangChainHybridService] 초기화 완료")

    def _initialize_langchain_components(self):
        """LangChain 컴포넌트들 초기화"""
        try:
            # OpenAI 임베딩 (기본 1536차원 사용)
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key,
                model="text-embedding-3-small"  # 1536차원
            )

            # Pinecone 벡터 스토어
            self.vector_store = PineconeVectorStore(
                index_name=self.pinecone_index,
                embedding=self.embeddings,
                pinecone_api_key=self.pinecone_api_key
            )

            # 기존 키워드 검색 서비스 사용 (벡터 필드 없는 Elasticsearch 호환)
            from modules.core.services.keyword_search_service import (
                KeywordSearchService,
            )
            self.keyword_search_service = KeywordSearchService()

            # 벡터 리트리버만 LangChain 사용 (applicant 타입 필터 추가)
            self.vector_retriever = self.vector_store.as_retriever(
                search_kwargs={
                    "k": 20,  # 검색 결과 수를 기존과 동일하게
                    "filter": {"chunk_type": "applicant"}  # 지원자 정보만 검색
                }
            )

            # 하이브리드 검색은 수동으로 구현 (기존 구조 호환성 유지)
            self.hybrid_retriever = None  # 수동 하이브리드 검색 사용

            print(f"[LangChainHybridService] LangChain 컴포넌트 초기화 완료")

        except Exception as e:
            print(f"[LangChainHybridService] LangChain 컴포넌트 초기화 실패: {e}")
            raise

    async def search_similar_applicants_langchain(self,
                                                vector_query: str,
                                                keyword_query: str,
                                                applicants_collection,
                                                resumes_collection,
                                                target_applicant: Dict[str, Any],
                                                limit: int = 10) -> Dict[str, Any]:
        """
        LangChain 기반 하이브리드 검색으로 유사 지원자 추천

        Args:
            vector_query (str): 벡터 검색용 쿼리 (지원자 정보)
            keyword_query (str): 키워드 검색용 쿼리 (이력서 내용)
            applicants_collection: MongoDB 지원자 컬렉션
            resumes_collection: MongoDB 이력서 컬렉션 (키워드 검색용)
            target_applicant (Dict): 기준 지원자 정보
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 검색 결과
        """
        try:
            print(f"[LangChainHybridService] === LangChain 하이브리드 검색 시작 ===")
            print(f"[LangChainHybridService] 벡터 쿼리: {vector_query[:100]}...")
            print(f"[LangChainHybridService] 키워드 쿼리 길이: {len(keyword_query)}")

            # 1. 벡터 검색 수행 (지원자 정보 기반)
            print(f"[LangChainHybridService] 벡터 검색 수행...")
            print(f"[LangChainHybridService] 벡터 필터: {self.vector_retriever.search_kwargs}")

            # 필터 없이 전체 검색도 테스트
            try:
                test_retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
                test_docs = await asyncio.to_thread(test_retriever.invoke, vector_query)
                print(f"[LangChainHybridService] 필터 없는 전체 검색 결과: {len(test_docs)}개")
            except Exception as e:
                print(f"[LangChainHybridService] 테스트 검색 실패: {e}")

            vector_docs = await asyncio.to_thread(
                self.vector_retriever.invoke,
                vector_query
            )
            print(f"[LangChainHybridService] 벡터 검색 결과: {len(vector_docs)}개")

            # 2. 키워드 검색 수행 (이력서 컬렉션 사용)
            keyword_docs = []
            if keyword_query:
                print(f"[LangChainHybridService] 키워드 검색 수행 (이력서 텍스트 대상)...")
                print(f"[LangChainHybridService] 키워드 쿼리 미리보기: {keyword_query[:200]}...")
                keyword_result = await self.keyword_search_service.search_by_keywords(
                    query=keyword_query,
                    collection=resumes_collection,
                    limit=10
                )
                print(f"[LangChainHybridService] 키워드 검색 원본 결과: success={keyword_result.get('success')}, total={len(keyword_result.get('results', []))}")
                keyword_docs = self._convert_keyword_results_to_docs(keyword_result)
                print(f"[LangChainHybridService] 키워드 검색 결과: {len(keyword_docs)}개")

            # 3. 수동 하이브리드 검색 (벡터 + 키워드 결합)
            print(f"[LangChainHybridService] 수동 하이브리드 검색 수행...")
            hybrid_docs = vector_docs + keyword_docs  # 단순 결합
            # 중복 제거
            seen_ids = set()
            unique_hybrid_docs = []
            for doc in hybrid_docs:
                doc_id = None
                if hasattr(doc, 'metadata') and doc.metadata:
                    doc_id = doc.metadata.get('resume_id') or doc.metadata.get('document_id')
                if doc_id and doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_hybrid_docs.append(doc)
            hybrid_docs = unique_hybrid_docs

            print(f"[LangChainHybridService] 하이브리드 검색 결과: {len(hybrid_docs)}개")

            # 4. 결과를 지원자 정보로 변환
            return await self._convert_docs_to_applicants(
                hybrid_docs, vector_docs, keyword_docs,
                applicants_collection, target_applicant, limit
            )

        except Exception as e:
            print(f"[LangChainHybridService] LangChain 하이브리드 검색 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "LangChain 하이브리드 검색 중 오류가 발생했습니다."
            }

    async def _convert_docs_to_applicants(self,
                                        hybrid_docs: List[Document],
                                        vector_docs: List[Document],
                                        keyword_docs: List[Document],
                                        applicants_collection,
                                        target_applicant: Dict[str, Any],
                                        limit: int) -> Dict[str, Any]:
        """
        LangChain Document 객체들을 지원자 정보로 변환
        """
        try:
            # 문서에서 resume_id 추출하여 지원자 매핑
            applicant_scores = {}
            target_resume_id = target_applicant.get('resume_id')

            # 하이브리드 결과 처리
            for i, doc in enumerate(hybrid_docs):
                try:
                    # Document의 메타데이터에서 식별자 추출 및 지원자 찾기
                    applicant = None
                    resume_id = None

                    if hasattr(doc, 'metadata') and doc.metadata:
                        chunk_type = doc.metadata.get('chunk_type')

                        if chunk_type == 'applicant':
                            # 지원자 벡터의 경우: document_id가 applicant_id임
                            applicant_id = doc.metadata.get('document_id')
                            if applicant_id and applicant_id != str(target_applicant.get('_id')):
                                from bson import ObjectId
                                applicant = await applicants_collection.find_one({"_id": ObjectId(applicant_id)})
                        else:
                            # 키워드 검색 결과의 경우: applicant_id로 직접 조회
                            applicant_id = doc.metadata.get('applicant_id')
                            resume_id = doc.metadata.get('resume_id') or doc.metadata.get('document_id')
                            
                            if applicant_id and applicant_id != str(target_applicant.get('_id')):
                                from bson import ObjectId
                                print(f"[LangChainHybridService] 키워드 검색 지원자 조회: {applicant_id}")
                                applicant = await applicants_collection.find_one({"_id": ObjectId(applicant_id)})
                    
                    if applicant:
                        applicant_id = str(applicant["_id"])

                        # 벡터/키워드 개별 점수 계산
                        vector_score = 0
                        keyword_score = 0
                        
                        # 클래스 변수에서 가중치 사용
                        vector_weight = self.vector_weight
                        keyword_weight = self.keyword_weight

                        # 벡터 결과에서 점수 찾기 (applicant_id로 직접 매칭)
                        print(f"[LangChainHybridService] 벡터 매칭 시도: 지원자 {applicant_id}")
                        vector_rank = None
                        for v_i, v_doc in enumerate(vector_docs):
                            v_applicant_id = None
                            
                            if hasattr(v_doc, 'metadata') and v_doc.metadata:
                                v_chunk_type = v_doc.metadata.get('chunk_type')
                                v_document_id = v_doc.metadata.get('document_id')
                                
                                if v_chunk_type == 'applicant':
                                    # 지원자 벡터의 경우 document_id가 applicant_id
                                    v_applicant_id = v_document_id
                                else:
                                    # 이력서 벡터의 경우는 스킵 (applicant_id로만 매칭)
                                    continue

                            # applicant_id로 직접 매칭
                            if v_applicant_id == applicant_id:
                                vector_score = max(0, (len(vector_docs) - v_i) / len(vector_docs))
                                vector_rank = v_i
                                print(f"[LangChainHybridService] 벡터 매칭 성공: {applicant_id}, 순위: {v_i}, 점수: {vector_score:.3f}")
                                break
                        
                        # 벡터 검색에서 직접 매칭되지 않은 경우 실시간 유사도 계산
                        if vector_score == 0:
                            print(f"[LangChainHybridService] 벡터 직접 매칭 실패 - 실시간 유사도 계산 시도: {applicant_id}")
                            vector_score = await self._calculate_realtime_vector_similarity(applicant, target_applicant)
                            print(f"[LangChainHybridService] 실시간 벡터 유사도: {applicant_id}, 점수: {vector_score:.3f}")

                        # 키워드 결과에서 점수 찾기 (BM25 점수 기반)
                        for k_i, k_doc in enumerate(keyword_docs):
                            k_applicant_id = k_doc.metadata.get('applicant_id') if hasattr(k_doc, 'metadata') else None
                            k_resume_id = k_doc.metadata.get('resume_id') if hasattr(k_doc, 'metadata') else None
                            
                            # 현재 지원자와 매칭되는지 확인 (applicant_id로 비교)
                            if k_applicant_id == applicant_id or k_resume_id == resume_id:
                                # BM25 점수를 0-1 범위로 정규화
                                bm25_score = k_doc.metadata.get('bm25_score', 0) if hasattr(k_doc, 'metadata') else 0
                                keyword_score = min(1.0, max(0.0, bm25_score / 10.0))  # 10으로 나누어 정규화
                                break
                        
                        # 가중치 결합으로 최종 점수 계산
                        final_score = (vector_score * vector_weight) + (keyword_score * keyword_weight)

                        if applicant_id not in applicant_scores or final_score > applicant_scores[applicant_id]['final_score']:
                            applicant_scores[applicant_id] = {
                                'final_score': final_score,
                                'vector_score': vector_score,
                                'keyword_score': keyword_score,
                                'applicant': applicant,
                                'search_methods': []
                            }

                            # 검색 방법 추가 - 하이브리드 검색에서는 기본적으로 둘 다 사용
                            search_methods = []
                            if len(vector_docs) > 0:  # 벡터 검색이 실행되었다면
                                search_methods.append('vector')
                            if len(keyword_docs) > 0:  # 키워드 검색이 실행되었다면
                                search_methods.append('keyword')
                            
                            applicant_scores[applicant_id]['search_methods'] = search_methods

                except Exception as e:
                    continue

            # 결과 정렬 및 포맷팅
            results = []
            for applicant_id, score_data in applicant_scores.items():
                applicant = score_data['applicant']

                # ID와 datetime 필드 처리
                applicant["_id"] = str(applicant["_id"])

                # 모든 datetime 필드를 문자열로 변환
                for key, value in list(applicant.items()):
                    if hasattr(value, 'isoformat'):
                        applicant[key] = value.isoformat()
                    elif key == "_id":
                        applicant[key] = str(value)

                # 이름 필드 확보
                if not applicant.get('name'):
                    applicant['name'] = '이름미상'

                results.append({
                    "final_score": score_data['final_score'],
                    "vector_score": score_data['vector_score'],
                    "keyword_score": score_data['keyword_score'],
                    "applicant": applicant,
                    "search_methods": score_data['search_methods']
                })

            # 최종 점수 기준으로 정렬
            results.sort(key=lambda x: x["final_score"], reverse=True)
            final_results = results[:limit]

            print(f"[LangChainHybridService] 최종 결과: {len(final_results)}개 지원자")

            return {
                "success": True,
                "message": "LangChain 하이브리드 검색 완료",
                "data": {
                    "search_method": "langchain_hybrid",
                    "ensemble_weights": {"vector": self.vector_weight, "keyword": self.keyword_weight},
                    "results": final_results,
                    "total": len(final_results),
                    "vector_count": len(vector_docs),
                    "keyword_count": len(keyword_docs),
                    "hybrid_count": len(hybrid_docs),
                    "target_applicant": {
                        "name": target_applicant.get('name', 'N/A'),
                        "position": target_applicant.get('position', 'N/A'),
                        "id": str(target_applicant.get('_id', ''))
                    }
                }
            }

        except Exception as e:
            print(f"[LangChainHybridService] 문서 변환 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "검색 결과 변환 중 오류가 발생했습니다."
            }

    async def _calculate_realtime_vector_similarity(self, candidate_applicant: Dict, target_applicant: Dict) -> float:
        """
        키워드 검색으로만 발견된 지원자에 대해 실시간 벡터 유사도를 계산합니다.
        
        Args:
            candidate_applicant (Dict): 후보 지원자 정보
            target_applicant (Dict): 기준 지원자 정보
        
        Returns:
            float: 0.0~1.0 사이의 유사도 점수
        """
        try:
            print(f"[LangChainHybridService] 실시간 벡터 유사도 계산 시작")
            print(f"[LangChainHybridService] 후보: {candidate_applicant.get('name')}, 기준: {target_applicant.get('name')}")
            
            # 1. 지원자 정보를 벡터 검색용 텍스트로 변환
            candidate_text = self._convert_applicant_to_text(candidate_applicant)
            target_text = self._convert_applicant_to_text(target_applicant)
            
            print(f"[LangChainHybridService] 후보 텍스트: {candidate_text[:100]}...")
            print(f"[LangChainHybridService] 기준 텍스트: {target_text[:100]}...")
            
            # 2. 임베딩 생성
            from modules.core.services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            
            candidate_embedding = await embedding_service.create_query_embedding(candidate_text)
            target_embedding = await embedding_service.create_query_embedding(target_text)
            
            if not candidate_embedding or not target_embedding:
                print(f"[LangChainHybridService] 임베딩 생성 실패")
                return 0.0
            
            # 3. 코사인 유사도 계산
            import numpy as np
            
            # 벡터를 numpy 배열로 변환
            candidate_vec = np.array(candidate_embedding)
            target_vec = np.array(target_embedding)
            
            # 코사인 유사도 계산
            dot_product = np.dot(candidate_vec, target_vec)
            candidate_norm = np.linalg.norm(candidate_vec)
            target_norm = np.linalg.norm(target_vec)
            
            if candidate_norm == 0 or target_norm == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (candidate_norm * target_norm)
            
            # -1~1 범위를 0~1 범위로 정규화
            normalized_similarity = (similarity + 1) / 2
            
            print(f"[LangChainHybridService] 코사인 유사도: {similarity:.3f}, 정규화: {normalized_similarity:.3f}")
            
            return max(0.0, min(1.0, normalized_similarity))
            
        except Exception as e:
            print(f"[LangChainHybridService] 실시간 벡터 유사도 계산 실패: {str(e)}")
            return 0.0
    
    def _convert_applicant_to_text(self, applicant: Dict) -> str:
        """
        지원자 정보를 벡터 임베딩용 텍스트로 변환합니다.
        
        Args:
            applicant (Dict): 지원자 정보
            
        Returns:
            str: 변환된 텍스트
        """
        text_parts = []
        
        # 기본 정보
        if applicant.get('name'):
            text_parts.append(f"이름: {applicant['name']}")
        
        if applicant.get('position'):
            text_parts.append(f"지원직무: {applicant['position']}")
        
        if applicant.get('experience'):
            text_parts.append(f"경력: {applicant['experience']}")
        
        if applicant.get('department'):
            text_parts.append(f"부서: {applicant['department']}")
        
        # 기술 스택
        if applicant.get('skills'):
            if isinstance(applicant['skills'], list):
                skills_text = " ".join(applicant['skills'])
            else:
                skills_text = str(applicant['skills'])
            text_parts.append(f"기술스택: {skills_text}")
        
        # 성장 배경 (일부만)
        if applicant.get('growthBackground'):
            growth_text = str(applicant['growthBackground'])[:200]  # 처음 200자만
            text_parts.append(f"성장배경: {growth_text}")
        
        # 지원 동기 (일부만)
        if applicant.get('motivation'):
            motivation_text = str(applicant['motivation'])[:200]  # 처음 200자만
            text_parts.append(f"지원동기: {motivation_text}")
        
        # 경력 사항 (일부만)
        if applicant.get('careerHistory'):
            career_text = str(applicant['careerHistory'])[:200]  # 처음 200자만
            text_parts.append(f"경력사항: {career_text}")
        
        result = " ".join(text_parts)
        return result if result else "정보 없음"

    async def add_applicant_to_vector_store(self, applicant: Dict[str, Any]) -> bool:
        """
        지원자 정보를 LangChain 벡터 스토어에 추가
        """
        try:
            # 지원자 정보로 Document 생성
            content_parts = []
            if applicant.get('position'):
                content_parts.append(f"지원직무: {applicant['position']}")
            if applicant.get('experience'):
                content_parts.append(f"경력: {applicant['experience']}년")
            if applicant.get('skills'):
                if isinstance(applicant['skills'], list):
                    skills_text = " ".join(applicant['skills'])
                else:
                    skills_text = str(applicant['skills'])
                content_parts.append(f"기술스택: {skills_text}")

            content = " ".join(content_parts)

            doc = Document(
                page_content=content,
                metadata={
                    "applicant_id": str(applicant["_id"]),
                    "resume_id": applicant.get("resume_id", ""),
                    "name": applicant.get("name", ""),
                    "position": applicant.get("position", ""),
                    "experience": applicant.get("experience", ""),
                    "document_type": "applicant",
                    "created_at": datetime.now().isoformat()
                }
            )

            # 벡터 스토어에 추가
            await asyncio.to_thread(
                self.vector_store.add_documents,
                [doc]
            )

            print(f"[LangChainHybridService] 지원자 '{applicant.get('name')}' 벡터 스토어 추가 완료")
            return True

        except Exception as e:
            print(f"[LangChainHybridService] 지원자 벡터 스토어 추가 실패: {e}")
            return False

    async def add_resume_to_keyword_store(self, resume: Dict[str, Any]) -> bool:
        """
        이력서 내용을 LangChain 키워드 스토어에 추가
        """
        try:
            # 이력서 내용으로 Document 생성
            content_parts = []
            if resume.get('extracted_text'):
                content_parts.append(resume['extracted_text'])
            if resume.get('summary'):
                content_parts.append(resume['summary'])
            if resume.get('keywords') and isinstance(resume['keywords'], list):
                keywords_text = " ".join(resume['keywords'])
                content_parts.append(keywords_text)

            content = " ".join(content_parts)

            doc = Document(
                page_content=content,
                metadata={
                    "resume_id": str(resume["_id"]),
                    "applicant_id": resume.get("applicant_id", ""),
                    "document_type": "resume",
                    "created_at": datetime.now().isoformat()
                }
            )

            # 키워드 스토어에 추가
            await asyncio.to_thread(
                self.es_store.add_documents,
                [doc]
            )

            print(f"[LangChainHybridService] 이력서 '{resume.get('_id')}' 키워드 스토어 추가 완료")
            return True

        except Exception as e:
            print(f"[LangChainHybridService] 이력서 키워드 스토어 추가 실패: {e}")
            return False

    def _convert_keyword_results_to_docs(self, keyword_result: Dict[str, Any]) -> List[Document]:
        """
        기존 KeywordSearchService 결과를 LangChain Document 형태로 변환
        """
        docs = []
        try:
            if keyword_result.get("success") and keyword_result.get("results"):
                print(f"[LangChainHybridService] 키워드 검색 결과 변환 시작: {len(keyword_result['results'])}개")
                for i, result in enumerate(keyword_result["results"]):
                    resume = result.get("resume", {})
                    resume_id = resume.get("_id") or resume.get("resume_id")
                    print(f"[LangChainHybridService] 결과 {i}: resume_id={resume_id}, applicant_id={resume.get('_id')}")

                    if resume_id:
                        # 더 많은 정보로 Document 생성 (지원자 정보 기반)
                        content_parts = []
                        if result.get("highlight"):
                            content_parts.append(result["highlight"])
                        if resume.get("name"):  # 지원자 이름
                            content_parts.append(f"이름: {resume['name']}")
                        if resume.get("position"):  # 지원자 직무
                            content_parts.append(f"직무: {resume['position']}")
                        if resume.get("skills"):  # 지원자 기술스택
                            content_parts.append(f"기술스택: {resume['skills']}")
                        
                        content = " ".join(content_parts) or f"이력서 ID: {resume_id}"
                        
                        doc = Document(
                            page_content=content,
                            metadata={
                                "resume_id": resume_id,
                                "document_id": resume_id,
                                "bm25_score": result.get("bm25_score", 0),
                                "document_type": "resume",
                                "name": resume.get("name", ""),
                                "applicant_id": resume.get("_id", "")  # 지원자 ID
                            }
                        )
                        docs.append(doc)
                        print(f"[LangChainHybridService] 키워드 문서 변환 완료: {resume_id}, 지원자ID: {resume.get('_id', '')}, BM25: {result.get('bm25_score', 0)}")

            else:
                print(f"[LangChainHybridService] 키워드 검색 변환 스킵: success={keyword_result.get('success')}, results_count={len(keyword_result.get('results', []))}")
                if not keyword_result.get("success"):
                    print(f"[LangChainHybridService] 키워드 검색 실패 이유: {keyword_result.get('message', 'Unknown')}")
            
            print(f"[LangChainHybridService] 키워드 결과 변환: {len(docs)}개 문서")
            return docs

        except Exception as e:
            print(f"[LangChainHybridService] 키워드 결과 변환 실패: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def search_resumes_langchain_hybrid(self,
                                            query: str,
                                            collection,
                                            search_type: str = "resume",
                                            limit: int = 10) -> Dict[str, Any]:
        """
        LangChain 기반 하이브리드 검색으로 이력서 검색

        Args:
            query (str): 검색 쿼리
            collection: MongoDB 컬렉션
            search_type (str): 검색할 타입
            limit (int): 반환할 최대 결과 수

        Returns:
            Dict[str, Any]: 검색 결과
        """
        try:
            print(f"[LangChainHybridService] === 이력서 하이브리드 검색 시작 ===")
            print(f"[LangChainHybridService] 검색 쿼리: {query}")

            # 1. 벡터 검색 수행
            print(f"[LangChainHybridService] 벡터 검색 수행...")
            vector_docs = await asyncio.to_thread(
                self.vector_retriever.invoke,
                query
            )
            print(f"[LangChainHybridService] 벡터 검색 결과: {len(vector_docs)}개")

            # 2. 키워드 검색 수행 (기존 서비스 사용)
            print(f"[LangChainHybridService] 키워드 검색 수행...")
            keyword_result = await self.keyword_search_service.search_by_keywords(
                query=query,
                collection=collection,
                limit=10
            )
            keyword_docs = self._convert_keyword_results_to_docs(keyword_result)
            print(f"[LangChainHybridService] 키워드 검색 결과: {len(keyword_docs)}개")

            # 3. 수동 하이브리드 검색 (벡터 + 키워드 결합)
            print(f"[LangChainHybridService] 수동 하이브리드 검색 수행...")
            hybrid_docs = vector_docs + keyword_docs  # 단순 결합
            # 중복 제거
            seen_ids = set()
            unique_hybrid_docs = []
            for doc in hybrid_docs:
                doc_id = None
                if hasattr(doc, 'metadata') and doc.metadata:
                    doc_id = doc.metadata.get('resume_id') or doc.metadata.get('document_id')
                if doc_id and doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_hybrid_docs.append(doc)
            hybrid_docs = unique_hybrid_docs

            print(f"[LangChainHybridService] 하이브리드 검색 결과: {len(hybrid_docs)}개")
            print(f"[LangChainHybridService] 벡터: {len(vector_docs)}개, 키워드: {len(keyword_docs)}개")

            # 4. 결과를 이력서 정보로 변환
            return await self._convert_docs_to_resumes(
                hybrid_docs, vector_docs, keyword_docs,
                collection, limit
            )

        except Exception as e:
            print(f"[LangChainHybridService] 이력서 하이브리드 검색 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "LangChain 하이브리드 이력서 검색 중 오류가 발생했습니다."
            }

    async def _convert_docs_to_resumes(self,
                                     hybrid_docs: List[Document],
                                     vector_docs: List[Document],
                                     keyword_docs: List[Document],
                                     collection,
                                     limit: int) -> Dict[str, Any]:
        """
        LangChain Document 객체들을 이력서 정보로 변환
        """
        try:
            print(f"[LangChainHybridService] === 문서를 이력서 정보로 변환 시작 ===")

            # 문서에서 resume_id 추출하여 이력서 매핑
            resume_scores = {}

            # 하이브리드 결과 처리
            for i, doc in enumerate(hybrid_docs):
                try:
                    # Document의 메타데이터에서 resume_id 추출
                    resume_id = None
                    if hasattr(doc, 'metadata') and doc.metadata:
                        resume_id = doc.metadata.get('resume_id') or doc.metadata.get('document_id')

                    if resume_id:
                        # 하이브리드 점수 계산 (순위 기반)
                        hybrid_score = max(0, (len(hybrid_docs) - i) / len(hybrid_docs))

                        # 벡터/키워드 개별 점수 계산
                        vector_score = 0
                        keyword_score = 0

                        # 벡터 결과에서 점수 찾기
                        for v_i, v_doc in enumerate(vector_docs):
                            v_resume_id = None
                            if hasattr(v_doc, 'metadata') and v_doc.metadata:
                                v_resume_id = v_doc.metadata.get('resume_id') or v_doc.metadata.get('document_id')
                            if v_resume_id == resume_id:
                                vector_score = max(0, (len(vector_docs) - v_i) / len(vector_docs))
                                break

                        # 키워드 결과에서 점수 찾기
                        for k_i, k_doc in enumerate(keyword_docs):
                            k_resume_id = None
                            if hasattr(k_doc, 'metadata') and k_doc.metadata:
                                k_resume_id = k_doc.metadata.get('resume_id') or k_doc.metadata.get('document_id')
                            if k_resume_id == resume_id:
                                keyword_score = max(0, (len(keyword_docs) - k_i) / len(keyword_docs))
                                break

                        if resume_id not in resume_scores or hybrid_score > resume_scores[resume_id]['final_score']:
                            resume_scores[resume_id] = {
                                'final_score': hybrid_score,
                                'vector_score': vector_score,
                                'keyword_score': keyword_score,
                                'search_methods': []
                            }

                            # 검색 방법 추가
                            if vector_score > 0:
                                resume_scores[resume_id]['search_methods'].append('vector')
                            if keyword_score > 0:
                                resume_scores[resume_id]['search_methods'].append('keyword')

                except Exception as e:
                    print(f"[LangChainHybridService] 문서 {i} 처리 중 오류: {e}")
                    continue

            # MongoDB에서 이력서 상세 정보 조회
            from bson import ObjectId
            resume_ids_obj = [ObjectId(rid) for rid in resume_scores.keys()]
            resumes = await collection.find({"_id": {"$in": resume_ids_obj}}).to_list(1000)

            # 결과 정렬 및 포맷팅
            results = []
            for resume in resumes:
                resume_id = str(resume["_id"])
                score_data = resume_scores.get(resume_id)

                if score_data:
                    # ID와 datetime 필드 처리
                    resume["_id"] = str(resume["_id"])
                    if "resume_id" in resume:
                        resume["resume_id"] = str(resume["resume_id"])
                    else:
                        resume["resume_id"] = str(resume["_id"])

                    # 모든 datetime 필드를 문자열로 변환
                    for key, value in list(resume.items()):
                        if hasattr(value, 'isoformat'):
                            resume[key] = value.isoformat()
                        elif key == "_id":
                            resume[key] = str(value)

                    results.append({
                        "final_score": score_data['final_score'],
                        "vector_score": score_data['vector_score'],
                        "keyword_score": score_data['keyword_score'],
                        "resume": resume,
                        "search_methods": score_data['search_methods']
                    })

            # 최종 점수 기준으로 정렬
            results.sort(key=lambda x: x["final_score"], reverse=True)
            final_results = results[:limit]

            print(f"[LangChainHybridService] 최종 결과: {len(final_results)}개 이력서")
            for i, result in enumerate(final_results[:3]):
                resume_name = result['resume'].get('name', '이름미상')
                resume_position = result['resume'].get('position', 'N/A')
                print(f"[LangChainHybridService] #{i+1}: {resume_name} ({resume_position}) "
                      f"(최종:{result['final_score']:.3f}, V:{result['vector_score']:.3f}, "
                      f"K:{result['keyword_score']:.3f})")

            return {
                "success": True,
                "message": "LangChain 하이브리드 이력서 검색 완료",
                "data": {
                    "search_method": "langchain_hybrid_resume",
                    "ensemble_weights": {"vector": 0.5, "keyword": 0.5},
                    "results": final_results,
                    "total": len(final_results),
                    "vector_count": len(vector_docs),
                    "keyword_count": len(keyword_docs),
                    "hybrid_count": len(hybrid_docs)
                }
            }

        except Exception as e:
            print(f"[LangChainHybridService] 이력서 변환 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "검색 결과 변환 중 오류가 발생했습니다."
            }
