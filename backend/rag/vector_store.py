"""
RAG 검색을 위한 벡터 데이터베이스 및 검색 시스템
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pickle
from datetime import datetime

class RAGVectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        RAG 벡터 스토어 초기화
        
        Args:
            model_name: 임베딩 모델명
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        self.index = None
        self.metadata = []
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        문서들을 벡터 스토어에 추가
        
        Args:
            documents: 문서 리스트 (각 문서는 content, metadata를 포함)
        """
        for doc in documents:
            self.documents.append(doc['content'])
            self.metadata.append(doc['metadata'])
            
        # 임베딩 생성
        self.embeddings = self.model.encode(self.documents)
        
        # FAISS 인덱스 생성
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        self.index.add(self.embeddings.astype('float32'))
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리와 유사한 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 문서 수
            
        Returns:
            검색 결과 리스트
        """
        if self.index is None:
            return []
            
        # 쿼리 임베딩 생성
        query_embedding = self.model.encode([query])
        
        # 유사도 검색
        similarities, indices = self.index.search(
            query_embedding.astype('float32'), 
            top_k
        )
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'rank': i + 1,
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'similarity_score': float(similarity),
                    'relevance_percentage': float(similarity * 100)
                })
                
        return results
    
    def save_index(self, filepath: str):
        """인덱스 저장"""
        if self.index is not None:
            faiss.write_index(self.index, f"{filepath}.faiss")
            
        # 메타데이터와 문서 저장
        data = {
            'documents': self.documents,
            'metadata': self.metadata,
            'embeddings': self.embeddings.tolist() if self.embeddings is not None else None,
            'model_name': self.model_name,
            'created_at': datetime.now().isoformat()
        }
        
        with open(f"{filepath}.pkl", 'wb') as f:
            pickle.dump(data, f)
            
    def load_index(self, filepath: str):
        """인덱스 로드"""
        if os.path.exists(f"{filepath}.faiss"):
            self.index = faiss.read_index(f"{filepath}.faiss")
            
        if os.path.exists(f"{filepath}.pkl"):
            with open(f"{filepath}.pkl", 'rb') as f:
                data = pickle.load(f)
                
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.embeddings = np.array(data['embeddings']) if data['embeddings'] else None
            self.model_name = data['model_name']

class CoverLetterRAGSystem:
    def __init__(self):
        """자소서 분석을 위한 RAG 시스템"""
        self.vector_store = RAGVectorStore()
        self.job_descriptions = {}
        self.company_values = {}
        self.evaluation_rubrics = {}
        self.sample_cover_letters = []
        
    def initialize_rag_data(self):
        """RAG 데이터 초기화"""
        # 직무 설명 데이터
        self.job_descriptions = {
            "backend_developer": {
                "title": "백엔드 개발자",
                "required_skills": ["Python", "FastAPI", "MongoDB", "Docker", "Git"],
                "preferred_skills": ["AWS", "Kubernetes", "Microservices", "Redis", "Elasticsearch"],
                "responsibilities": [
                    "백엔드 API 설계 및 개발",
                    "데이터베이스 설계 및 최적화",
                    "시스템 성능 모니터링 및 개선",
                    "보안 및 인증 시스템 구현",
                    "CI/CD 파이프라인 구축"
                ],
                "evaluation_criteria": [
                    "코딩 품질 및 아키텍처 설계 능력",
                    "문제 해결 및 디버깅 능력",
                    "데이터베이스 설계 및 최적화 능력",
                    "API 설계 및 문서화 능력",
                    "성능 최적화 및 모니터링 능력"
                ]
            },
            "frontend_developer": {
                "title": "프론트엔드 개발자",
                "required_skills": ["React", "JavaScript", "HTML/CSS", "TypeScript", "Git"],
                "preferred_skills": ["Next.js", "Redux", "Tailwind CSS", "GraphQL", "Jest"],
                "responsibilities": [
                    "사용자 인터페이스 설계 및 개발",
                    "반응형 웹 애플리케이션 구현",
                    "사용자 경험 최적화",
                    "프론트엔드 성능 최적화",
                    "크로스 브라우저 호환성 확보"
                ],
                "evaluation_criteria": [
                    "UI/UX 디자인 감각 및 구현 능력",
                    "반응형 웹 개발 능력",
                    "프론트엔드 프레임워크 활용 능력",
                    "사용자 중심 사고 및 접근성 고려",
                    "프론트엔드 테스트 및 품질 관리 능력"
                ]
            },
            "data_scientist": {
                "title": "데이터 사이언티스트",
                "required_skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL"],
                "preferred_skills": ["TensorFlow", "PyTorch", "Spark", "AWS", "Docker"],
                "responsibilities": [
                    "데이터 분석 및 인사이트 도출",
                    "머신러닝 모델 개발 및 최적화",
                    "데이터 전처리 및 정제",
                    "통계적 분석 및 가설 검증",
                    "데이터 시각화 및 보고서 작성"
                ],
                "evaluation_criteria": [
                    "통계적 사고 및 분석 능력",
                    "머신러닝 알고리즘 이해 및 적용 능력",
                    "데이터 전처리 및 정제 능력",
                    "데이터 시각화 및 커뮤니케이션 능력",
                    "비즈니스 문제 해결 능력"
                ]
            }
        }
        
        # 회사 가치 및 문화
        self.company_values = {
            "innovation": {
                "title": "혁신",
                "description": "새로운 아이디어와 기술을 통해 지속적인 혁신을 추구",
                "examples": [
                    "신기술 도입 및 실험적 접근",
                    "창의적 문제 해결",
                    "지속적인 개선 및 최적화"
                ]
            },
            "collaboration": {
                "title": "협업",
                "description": "팀워크와 협업을 통해 더 나은 결과를 창출",
                "examples": [
                    "효과적인 커뮤니케이션",
                    "지식 공유 및 멘토링",
                    "팀 성과 향상을 위한 협력"
                ]
            },
            "quality": {
                "title": "품질",
                "description": "높은 품질의 결과물과 서비스를 제공",
                "examples": [
                    "코드 품질 및 테스트 커버리지",
                    "사용자 경험 최적화",
                    "지속적인 품질 개선"
                ]
            },
            "growth": {
                "title": "성장",
                "description": "개인과 조직의 지속적인 학습과 성장",
                "examples": [
                    "새로운 기술 학습 및 적용",
                    "도전적 과제 도전",
                    "피드백을 통한 개선"
                ]
            }
        }
        
        # 평가 루브릭
        self.evaluation_rubrics = {
            "motivation": {
                "excellent": {
                    "score": 9,
                    "criteria": "명확한 동기와 진정성 있는 열정이 드러남",
                    "examples": ["구체적인 경험을 바탕으로 한 지원 동기", "회사/직무에 대한 깊은 이해"]
                },
                "good": {
                    "score": 7,
                    "criteria": "적절한 동기와 관심이 드러남",
                    "examples": ["일반적인 지원 동기", "적절한 관심도"]
                },
                "fair": {
                    "score": 5,
                    "criteria": "기본적인 동기가 있음",
                    "examples": ["모호한 동기", "부족한 설명"]
                },
                "poor": {
                    "score": 3,
                    "criteria": "동기가 불분명하거나 부족함",
                    "examples": ["동기 부족", "설명 부족"]
                }
            },
            "problem_solving": {
                "excellent": {
                    "score": 9,
                    "criteria": "구체적이고 체계적인 문제 해결 과정",
                    "examples": ["STAR 방법론 완벽 적용", "구체적인 결과와 영향"]
                },
                "good": {
                    "score": 7,
                    "criteria": "적절한 문제 해결 방법",
                    "examples": ["문제 해결 과정 서술", "기본적인 결과"]
                },
                "fair": {
                    "score": 5,
                    "criteria": "기본적인 문제 해결",
                    "examples": ["간단한 해결 과정", "결과 부족"]
                },
                "poor": {
                    "score": 3,
                    "criteria": "문제 해결 과정 부족",
                    "examples": ["해결 과정 부족", "결과 부족"]
                }
            }
        }
        
        # 샘플 자소서 (익명화된 우수 사례)
        self.sample_cover_letters = [
            {
                "id": "sample_001",
                "position": "backend_developer",
                "content": "저는 대학에서 컴퓨터공학을 전공하며 다양한 프로젝트를 진행했습니다...",
                "strengths": ["구체적인 프로젝트 경험", "기술적 역량 어필", "문제 해결 과정"],
                "score": 8.5,
                "feedback": "전체적으로 우수한 자소서입니다..."
            }
        ]
        
    def build_vector_index(self):
        """벡터 인덱스 구축"""
        documents = []
        
        # 직무 설명 추가
        for job_id, job_info in self.job_descriptions.items():
            content = f"직무: {job_info['title']}\n"
            content += f"필수 기술: {', '.join(job_info['required_skills'])}\n"
            content += f"우대 기술: {', '.join(job_info['preferred_skills'])}\n"
            content += f"주요 책임: {' '.join(job_info['responsibilities'])}\n"
            content += f"평가 기준: {' '.join(job_info['evaluation_criteria'])}"
            
            documents.append({
                'content': content,
                'metadata': {
                    'type': 'job_description',
                    'job_id': job_id,
                    'title': job_info['title']
                }
            })
        
        # 회사 가치 추가
        for value_id, value_info in self.company_values.items():
            content = f"가치: {value_info['title']}\n"
            content += f"설명: {value_info['description']}\n"
            content += f"예시: {' '.join(value_info['examples'])}"
            
            documents.append({
                'content': content,
                'metadata': {
                    'type': 'company_value',
                    'value_id': value_id,
                    'title': value_info['title']
                }
            })
        
        # 평가 루브릭 추가
        for criterion, levels in self.evaluation_rubrics.items():
            content = f"평가 기준: {criterion}\n"
            for level, info in levels.items():
                content += f"{level}: {info['criteria']} (점수: {info['score']})\n"
                content += f"예시: {', '.join(info['examples'])}\n"
            
            documents.append({
                'content': content,
                'metadata': {
                    'type': 'evaluation_rubric',
                    'criterion': criterion
                }
            })
        
        # 샘플 자소서 추가
        for sample in self.sample_cover_letters:
            documents.append({
                'content': sample['content'],
                'metadata': {
                    'type': 'sample_cover_letter',
                    'position': sample['position'],
                    'score': sample['score']
                }
            })
        
        # 벡터 스토어에 문서 추가
        self.vector_store.add_documents(documents)
        
    def search_relevant_context(self, query: str, position: str, top_k: int = 5) -> Dict[str, Any]:
        """
        자소서 분석을 위한 관련 컨텍스트 검색
        
        Args:
            query: 자소서 내용
            position: 지원 직무
            top_k: 검색할 문서 수
            
        Returns:
            검색된 관련 컨텍스트
        """
        # 직무 관련 검색
        job_query = f"{position} {query}"
        job_results = self.vector_store.search(job_query, top_k=3)
        
        # 회사 가치 관련 검색
        value_query = f"회사 가치 문화 {query}"
        value_results = self.vector_store.search(value_query, top_k=2)
        
        # 평가 기준 관련 검색
        rubric_query = f"평가 기준 루브릭 {query}"
        rubric_results = self.vector_store.search(rubric_query, top_k=2)
        
        # 샘플 자소서 관련 검색
        sample_query = f"샘플 자소서 {position} {query}"
        sample_results = self.vector_store.search(sample_query, top_k=2)
        
        return {
            'job_related': job_results,
            'company_values': value_results,
            'evaluation_criteria': rubric_results,
            'sample_cover_letters': sample_results,
            'search_summary': f"총 {len(job_results) + len(value_results) + len(rubric_results) + len(sample_results)}개의 관련 문서 검색됨"
        }
    
    def get_position_specific_criteria(self, position: str) -> str:
        """직무별 특화 평가 기준 반환"""
        if position in self.job_descriptions:
            job_info = self.job_descriptions[position]
            criteria = f"직무: {job_info['title']}\n"
            criteria += f"핵심 평가 요소:\n"
            for i, criterion in enumerate(job_info['evaluation_criteria'], 1):
                criteria += f"{i}. {criterion}\n"
            return criteria
        return "직무별 평가 기준을 찾을 수 없습니다."
    
    def get_department_culture_fit(self, department: str) -> str:
        """부서별 문화적 적합성 기준 반환"""
        culture_fit = f"부서: {department}\n"
        culture_fit += "문화적 적합성 평가 기준:\n"
        for value_id, value_info in self.company_values.items():
            culture_fit += f"- {value_info['title']}: {value_info['description']}\n"
        return culture_fit

if __name__ == "__main__":
    # RAG 시스템 테스트
    rag_system = CoverLetterRAGSystem()
    rag_system.initialize_rag_data()
    rag_system.build_vector_index()
    
    print("RAG 시스템이 성공적으로 초기화되었습니다.")
    print(f"총 {len(rag_system.vector_store.documents)}개의 문서가 인덱싱되었습니다.")
