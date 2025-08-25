from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
from pymongo.collection import Collection
import re
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()
try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    print("Warning: kiwipiepy not available, using fallback tokenizer")
    Kiwi = None
    KIWI_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.exceptions import ConnectionError, NotFoundError
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    print("Warning: elasticsearch not available, install with: pip install elasticsearch")
    Elasticsearch = None
    ELASTICSEARCH_AVAILABLE = False

class KeywordSearchService:
    def __init__(self):
        """
        키워드 검색 서비스 초기화
        Elasticsearch를 사용한 키워드 기반 검색
        """
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Elasticsearch 설정
        self.es_host = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
        self.es_index = os.getenv("ELASTICSEARCH_INDEX", "resume_search")
        self.es_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.es_password = os.getenv("ELASTICSEARCH_PASSWORD")
        
        # 디버깅: 환경변수 값 확인
        self.logger.info(f"ES_HOST: {self.es_host}")
        self.logger.info(f"ES_USERNAME: {self.es_username}")
        self.logger.info(f"ES_PASSWORD: {'*' * len(self.es_password) if self.es_password else None}")
        
        self.es_client = None
        
        # Elasticsearch 연결 초기화
        if ELASTICSEARCH_AVAILABLE:
            try:
                self._initialize_elasticsearch()
                self.logger.info("Elasticsearch 연결 성공")
            except Exception as e:
                self.logger.warning(f"Elasticsearch 연결 실패: {str(e)}. 키워드 검색 기능이 비활성화됩니다.")
                self.es_client = None
        else:
            self.logger.warning("Elasticsearch가 설치되지 않았습니다. 키워드 검색 기능이 비활성화됩니다.")
        
        # Kiwi 형태소 분석기 초기화
        if KIWI_AVAILABLE:
            try:
                self.kiwi = Kiwi()
                self.logger.info("Kiwi 형태소 분석기 초기화 완료")
            except Exception as e:
                self.logger.error(f"Kiwi 초기화 실패: {str(e)}")
                self.kiwi = None
        else:
            self.kiwi = None
            self.logger.warning("Kiwi를 사용할 수 없습니다. Fallback 토크나이저를 사용합니다.")
        
        # 불용어 리스트 (조사, 어미, 의미없는 단어들)
        self.stopwords = {
            # 조사
            '은', '는', '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '만', '까지', '부터',
            '의', '도', '나', '이나', '든지', '라도', '마저', '조차', '뿐', '밖에', '처럼', '같이', '보다',
            # 어미
            '습니다', '했습니다', '입니다', '였습니다', '었습니다', '하다', '되다', '있다', '없다',
            # 의미없는 단어
            '저', '제', '저희', '우리', '그', '그것', '이것', '저것', '여기', '거기', '저기',
            '때문', '위해', '통해', '대해', '관해', '따라', '위한', '위해서',
            # 단위/시간
            '년', '월', '일', '시', '분', '초', '개', '번', '차례', '번째',
            # 기타
            '등', '및', '또는', '그리고', '하지만', '그러나', '따라서', '그래서'
        }
        
        # IT 복합어 사전 (쪼개진 단어들을 다시 합치기 위함)
        self.compound_words = {
            ('프론트', '엔드'): '프론트엔드',
            ('백', '엔드'): '백엔드', 
            ('풀', '스택'): '풀스택',
            ('데이터', '베이스'): '데이터베이스',
            ('소프트', '웨어'): '소프트웨어',
            ('하드', '웨어'): '하드웨어',
            ('클라우드', '컴퓨팅'): '클라우드컴퓨팅',
            ('머신', '러닝'): '머신러닝',
            ('딥', '러닝'): '딥러닝',
            ('인공', '지능'): '인공지능',
            ('웹', '개발'): '웹개발',
            ('앱', '개발'): '앱개발',
            ('모바일', '앱'): '모바일앱',
            ('데이터', '분석'): '데이터분석',
            ('시스템', '개발'): '시스템개발'
        }
    
    def _initialize_elasticsearch(self):
        """Elasticsearch 클라이언트 초기화 및 인덱스 설정"""
        try:
            # Elasticsearch 클라이언트 생성
            auth = None
            if self.es_username and self.es_password:
                auth = (self.es_username, self.es_password)
                self.logger.info(f"Using auth: {self.es_username}:***")
            else:
                self.logger.info("No auth credentials found")
            
            self.es_client = Elasticsearch(
                self.es_host,
                verify_certs=False,
                ssl_show_warn=False,
                basic_auth=auth,
                request_timeout=3,  # 타임아웃을 3초로 단축
                max_retries=0,      # 재시도 비활성화
                retry_on_timeout=False  # 타임아웃 시 재시도 비활성화
            )
            
            # 연결 테스트 (빠른 테스트)
            info = self.es_client.info()
            self.logger.info(f"Elasticsearch 연결 성공: {self.es_host}, 버전: {info['version']['number']}")
            
            # 인덱스 매핑 설정
            self._create_index_mapping()
            
        except Exception as e:
            self.logger.warning(f"Elasticsearch 연결 실패: {e}. 키워드 검색 기능이 비활성화됩니다. 다른 검색 기능은 정상 작동합니다.")
            self.es_client = None
    
    def _create_index_mapping(self):
        """Elasticsearch 인덱스 매핑 설정"""
        try:
            # 인덱스가 이미 존재하는지 확인
            if self.es_client.indices.exists(index=self.es_index):
                self.logger.info(f"기존 인덱스 사용: {self.es_index}")
                return
            
            # 인덱스 매핑 정의
            mapping = {
                "mappings": {
                    "properties": {
                        "resume_id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "position": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "department": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "skills": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "experience": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "growth_background": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "motivation": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "career_history": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "resume_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "all_content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "tokens": {
                            "type": "keyword"
                        },
                        "created_at": {"type": "date"},
                        "indexed_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            
            # 인덱스 생성 (8.x 버전 호환)
            self.es_client.indices.create(index=self.es_index, **mapping)
            self.logger.info(f"Elasticsearch 인덱스 생성 완료: {self.es_index}")
            
        except Exception as e:
            self.logger.error(f"인덱스 매핑 생성 실패: {str(e)}")
        
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Kiwi 형태소 분석기를 사용하여 의미있는 키워드만 추출합니다.
        
        Args:
            text (str): 원본 텍스트
            
        Returns:
            List[str]: 의미있는 키워드 리스트
        """
        if not text or not self.kiwi:
            # Kiwi가 없으면 기존 방식으로 fallback
            return self._fallback_preprocess(text)
        
        try:
            # Kiwi로 형태소 분석
            result = self.kiwi.analyze(text)
            
            keywords = []
            for sentence_result in result:
                for token_info in sentence_result[0]:  # 첫 번째 분석 결과 사용
                    word = token_info.form.strip()
                    pos = token_info.tag
                    
                    # 의미있는 품사만 선택
                    if self._is_meaningful_pos(pos) and self._is_valid_keyword(word):
                        keywords.append(word.lower())
            
            # 복합어 복원
            restored_keywords = self._restore_compound_words(keywords)
            
            # 중복 제거하면서 순서 유지
            unique_keywords = []
            seen = set()
            for keyword in restored_keywords:
                if keyword not in seen:
                    unique_keywords.append(keyword)
                    seen.add(keyword)
            
            self.logger.debug(f"키워드 추출: '{text}' → {unique_keywords}")
            return unique_keywords
            
        except Exception as e:
            self.logger.warning(f"Kiwi 분석 실패, fallback 사용: {str(e)}")
            return self._fallback_preprocess(text)
    
    def _is_meaningful_pos(self, pos: str) -> bool:
        """
        의미있는 품사인지 확인합니다.
        
        Args:
            pos (str): 품사 태그
            
        Returns:
            bool: 의미있는 품사 여부
        """
        # Kiwi 품사 태그 기준
        meaningful_pos = {
            'NNG',  # 일반명사 (회사, 개발, 프로그래밍)
            'NNP',  # 고유명사 (React, Python, 삼성)
            'NNB',  # 의존명사 (것, 수, 등)
            'VV',   # 동사 (개발하다, 사용하다)
            'VA',   # 형용사 (좋다, 빠르다)
            'VX',   # 보조용언
            'SL',   # 외국어 (React, JavaScript)
            'SH',   # 한자
            'SN'    # 숫자 (2000, 3년)
        }
        
        # 앞 2글자로 비교 (세부 태그 무시)
        return pos[:2] in meaningful_pos or pos[:3] in meaningful_pos
    
    def _is_valid_keyword(self, word: str) -> bool:
        """
        유효한 키워드인지 확인합니다.
        
        Args:
            word (str): 검사할 단어
            
        Returns:
            bool: 유효한 키워드 여부
        """
        if not word or len(word.strip()) < 2:
            return False
        
        word = word.strip().lower()
        
        # 불용어 제거
        if word in self.stopwords:
            return False
        
        # 숫자만 있는 경우 제외 (단, 연도는 포함)
        if word.isdigit() and len(word) < 4:
            return False
        
        # 특수문자만 있는 경우 제외
        if re.match(r'^[^\w가-힣]+$', word):
            return False
        
        return True
    
    def _fallback_preprocess(self, text: str) -> List[str]:
        """
        Kiwi 실패 시 사용하는 기본 전처리 방법
        
        Args:
            text (str): 원본 텍스트
            
        Returns:
            List[str]: 기본 토큰 리스트
        """
        if not text:
            return []
        
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 제거 (한글, 영문, 숫자만 유지)
        text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', text)
        
        # 공백 정리
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 토큰화 (공백 기준 분할)
        tokens = text.split()
        
        # 유효한 토큰만 선택
        valid_tokens = []
        for token in tokens:
            if self._is_valid_keyword(token):
                valid_tokens.append(token)
        
        return valid_tokens
    
    def _restore_compound_words(self, keywords: List[str]) -> List[str]:
        """
        분리된 키워드들을 복합어로 복원합니다.
        
        Args:
            keywords (List[str]): 원본 키워드 리스트
            
        Returns:
            List[str]: 복합어가 복원된 키워드 리스트
        """
        if not keywords:
            return keywords
        
        restored = []
        i = 0
        
        while i < len(keywords):
            current_word = keywords[i]
            
            # 다음 단어와 복합어를 이룰 수 있는지 확인
            compound_found = False
            if i + 1 < len(keywords):
                next_word = keywords[i + 1]
                compound_key = (current_word, next_word)
                
                if compound_key in self.compound_words:
                    # 복합어로 교체
                    compound_word = self.compound_words[compound_key]
                    restored.append(compound_word)
                    i += 2  # 두 단어를 모두 처리했으므로 2만큼 증가
                    compound_found = True
                    self.logger.debug(f"복합어 복원: '{current_word}' + '{next_word}' → '{compound_word}'")
            
            if not compound_found:
                # 복합어가 아니면 그대로 추가
                restored.append(current_word)
                i += 1
        
        return restored
    
    def _extract_searchable_text(self, resume: Dict[str, Any]) -> str:
        """
        이력서에서 검색 가능한 텍스트를 추출합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            str: 검색 가능한 텍스트
        """
        # 키워드 검색에 포함될 필드들
        searchable_fields = [
            'name',           # 이름
            'position',       # 직무
            'department',     # 부서
            'skills',         # 기술스택
            'experience',     # 경력
            'growthBackground',  # 성장배경
            'motivation',     # 지원동기
            'careerHistory',  # 경력사항
            'resume_text'     # 전체 이력서 텍스트
        ]
        
        text_parts = []
        
        for field in searchable_fields:
            value = resume.get(field, "")
            if value and isinstance(value, str) and value.strip():
                text_parts.append(value.strip())
        
        combined_text = " ".join(text_parts)
        return combined_text
    
    async def index_document(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        단일 이력서를 Elasticsearch에 인덱싱합니다.
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            Dict[str, Any]: 인덱싱 결과
        """
        if not self.es_client:
            return {
                "success": False,
                "message": "Elasticsearch 연결이 없습니다."
            }
        
        try:
            resume_id = str(resume["_id"])
            
            # 검색 가능한 텍스트 추출
            searchable_text = self._extract_searchable_text(resume)
            tokens = self._preprocess_text(searchable_text)
            
            # Elasticsearch 문서 생성
            doc = {
                "resume_id": resume_id,
                "name": resume.get("name", ""),
                "position": resume.get("position", ""),
                "department": resume.get("department", ""),
                "skills": resume.get("skills", ""),
                "experience": resume.get("experience", ""),
                "growth_background": resume.get("growthBackground", ""),
                "motivation": resume.get("motivation", ""),
                "career_history": resume.get("careerHistory", ""),
                "resume_text": resume.get("resume_text", ""),
                "all_content": searchable_text,
                "tokens": tokens,
                "created_at": resume.get("created_at", datetime.now()),
                "indexed_at": datetime.now()
            }
            
            # Elasticsearch에 문서 인덱싱 (8.x 버전 호환)
            response = self.es_client.index(
                index=self.es_index,
                id=resume_id,
                document=doc
            )
            
            self.logger.info(f"문서 인덱싱 완료: {resume.get('name', 'Unknown')} ({len(tokens)} 토큰)")
            
            return {
                "success": True,
                "message": "문서 인덱싱이 완료되었습니다.",
                "resume_id": resume_id,
                "tokens_count": len(tokens),
                "es_response": response
            }
            
        except Exception as e:
            self.logger.error(f"문서 인덱싱 실패: {str(e)}")
            return {
                "success": False,
                "message": f"문서 인덱싱 중 오류가 발생했습니다: {str(e)}"
            }
    
    async def build_index(self, collection: Collection) -> Dict[str, Any]:
        """
        모든 이력서에 대한 Elasticsearch 인덱스를 구축합니다.
        
        Args:
            collection (Collection): MongoDB 이력서 컬렉션
            
        Returns:
            Dict[str, Any]: 인덱스 구축 결과
        """
        if not self.es_client:
            return {
                "success": False,
                "message": "Elasticsearch 연결이 없습니다.",
                "total_documents": 0
            }
        
        try:
            self.logger.info("=== Elasticsearch 인덱스 구축 시작 ===")
            
            # 기존 인덱스 삭제 후 재생성
            if self.es_client.indices.exists(index=self.es_index):
                self.es_client.indices.delete(index=self.es_index)
                self.logger.info(f"기존 인덱스 삭제: {self.es_index}")
            
            # 인덱스 매핑 재생성
            self._create_index_mapping()
            
            # 모든 이력서 조회 (비동기)
            resumes = await collection.find({}).to_list(1000)
            
            if not resumes:
                return {
                    "success": False,
                    "message": "인덱싱할 이력서가 없습니다.",
                    "total_documents": 0
                }
            
            # 배치 인덱싱
            indexed_count = 0
            failed_count = 0
            
            for resume in resumes:
                result = await self.index_document(resume)
                if result["success"]:
                    indexed_count += 1
                else:
                    failed_count += 1
            
            # 인덱스 새로고침
            self.es_client.indices.refresh(index=self.es_index)
            
            self.logger.info(f"Elasticsearch 인덱스 구축 완료: {indexed_count}개 성공, {failed_count}개 실패")
            
            return {
                "success": True,
                "message": "Elasticsearch 인덱스 구축이 완료되었습니다.",
                "total_documents": indexed_count,
                "failed_documents": failed_count,
                "index_created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Elasticsearch 인덱스 구축 실패: {str(e)}")
            return {
                "success": False,
                "message": f"인덱스 구축 중 오류가 발생했습니다: {str(e)}",
                "total_documents": 0
            }
    
    async def search_by_keywords(self, query: str, collection: Collection, 
                               limit: int = 10) -> Dict[str, Any]:
        """
        Elasticsearch를 사용한 키워드 기반 이력서 검색
        
        Args:
            query (str): 검색 쿼리
            collection (Collection): MongoDB 이력서 컬렉션 (호환성)
            limit (int): 반환할 최대 결과 수
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        if not self.es_client:
            self.logger.warning("Elasticsearch 연결이 없습니다. MongoDB fallback 검색을 사용합니다.")
            return await self._fallback_search(query, collection, limit)
        
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "message": "검색어를 입력해주세요.",
                    "results": []
                }
            
            self.logger.info(f"Elasticsearch 키워드 검색 시작: '{query}'")
            
            # 쿼리 토큰화
            query_tokens = self._preprocess_text(query)
            
            if not query_tokens:
                return {
                    "success": False,
                    "message": "유효한 검색 토큰이 없습니다.",
                    "results": []
                }
            
            self.logger.info(f"검색 토큰: {query_tokens}")
            
            # Elasticsearch 검색 쿼리 구성
            search_body = {
                "query": {
                    "bool": {
                        "should": [
                            # 멀티 필드 검색 (BM25 기본 사용)
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "name^3",           # 이름에 가중치 3
                                        "position^2",       # 직무에 가중치 2
                                        "skills^2",         # 기술스택에 가중치 2
                                        "department^1.5",   # 부서에 가중치 1.5
                                        "experience",
                                        "growth_background",
                                        "motivation",
                                        "career_history",
                                        "resume_text",
                                        "all_content"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            },
                            # 토큰 기반 정확 매칭
                            {
                                "terms": {
                                    "tokens": query_tokens,
                                    "boost": 1.5
                                }
                            }
                        ]
                    }
                },
                "highlight": {
                    "fields": {
                        "all_content": {},
                        "name": {},
                        "position": {},
                        "skills": {}
                    },
                    "pre_tags": ["**"],
                    "post_tags": ["**"]
                },
                "size": limit,
                "_source": ["resume_id", "name", "position", "department", "skills", "indexed_at"]
            }
            
            # Elasticsearch 검색 실행 (8.x 버전 호환)
            response = self.es_client.search(
                index=self.es_index,
                **search_body
            )
            
            hits = response["hits"]["hits"]
            
            if not hits:
                return {
                    "success": True,
                    "message": "검색 결과가 없습니다.",
                    "results": [],
                    "total": 0
                }
            
            # MongoDB에서 상세 정보 조회
            resume_ids = [ObjectId(hit["_source"]["resume_id"]) for hit in hits]
            resumes = {str(r["_id"]): r for r in collection.find({"_id": {"$in": resume_ids}})}
            
            # 결과 매핑
            results = []
            for hit in hits:
                resume_id = hit["_source"]["resume_id"]
                score = hit["_score"]
                
                resume = resumes.get(resume_id)
                if resume:
                    # ObjectId를 문자열로 변환
                    resume["_id"] = str(resume["_id"])
                    if "resume_id" in resume:
                        resume["resume_id"] = str(resume["resume_id"])
                    else:
                        resume["resume_id"] = str(resume["_id"])
                    
                    # 날짜 변환
                    if "created_at" in resume:
                        resume["created_at"] = resume["created_at"].isoformat()
                    
                    # 하이라이트 텍스트 추출
                    highlight_text = ""
                    if "highlight" in hit:
                        highlight_parts = []
                        for field, highlights in hit["highlight"].items():
                            highlight_parts.extend(highlights)
                        highlight_text = " ... ".join(highlight_parts)
                    
                    # 하이라이트가 없으면 기본 방식 사용
                    if not highlight_text:
                        highlight_text = self._highlight_query_terms(
                            self._extract_searchable_text(resume), 
                            query_tokens
                        )
                    
                    results.append({
                        "bm25_score": round(score, 4),
                        "resume": resume,
                        "highlight": highlight_text[:200] + "..." if len(highlight_text) > 200 else highlight_text
                    })
            
            self.logger.info(f"Elasticsearch 검색 완료: {len(results)}개 결과")
            
            return {
                "success": True,
                "message": f"'{query}' 검색 결과입니다.",
                "results": results,
                "total": len(results),
                "query": query,
                "query_tokens": query_tokens
            }
            
        except Exception as e:
            self.logger.error(f"Elasticsearch 검색 실패: {str(e)}")
            return {
                "success": False,
                "message": f"검색 중 오류가 발생했습니다: {str(e)}",
                "results": []
            }
    
    def _highlight_query_terms(self, text: str, query_tokens: List[str]) -> str:
        """
        텍스트에서 검색 토큰을 하이라이트합니다.
        
        Args:
            text (str): 원본 텍스트
            query_tokens (List[str]): 검색 토큰들
            
        Returns:
            str: 하이라이트된 텍스트
        """
        if not text or not query_tokens:
            return text
        
        highlighted_text = text
        
        for token in query_tokens:
            # 대소문자 구분 없이 치환
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            highlighted_text = pattern.sub(f"**{token}**", highlighted_text)
        
        return highlighted_text
    
    async def delete_document(self, resume_id: str) -> Dict[str, Any]:
        """
        Elasticsearch에서 문서를 삭제합니다.
        
        Args:
            resume_id (str): 삭제할 이력서 ID
            
        Returns:
            Dict[str, Any]: 삭제 결과
        """
        if not self.es_client:
            return {
                "success": False,
                "message": "Elasticsearch 연결이 없습니다."
            }
        
        try:
            response = self.es_client.delete(
                index=self.es_index,
                id=resume_id
            )
            
            self.logger.info(f"문서 삭제 완료: {resume_id}")
            
            return {
                "success": True,
                "message": "문서 삭제가 완료되었습니다.",
                "resume_id": resume_id,
                "es_response": response
            }
            
        except NotFoundError:
            return {
                "success": True,
                "message": "삭제할 문서가 존재하지 않습니다.",
                "resume_id": resume_id
            }
        except Exception as e:
            self.logger.error(f"문서 삭제 실패: {str(e)}")
            return {
                "success": False,
                "message": f"문서 삭제 중 오류가 발생했습니다: {str(e)}"
            }
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        현재 Elasticsearch 인덱스 통계를 반환합니다.
        
        Returns:
            Dict[str, Any]: 인덱스 통계
        """
        if not self.es_client:
            return {
                "indexed": False,
                "total_documents": 0,
                "index_created_at": None,
                "message": "Elasticsearch 연결이 없습니다."
            }
        
        try:
            # 인덱스 존재 확인
            if not self.es_client.indices.exists(index=self.es_index):
                return {
                    "indexed": False,
                    "total_documents": 0,
                    "index_created_at": None,
                    "message": "인덱스가 존재하지 않습니다."
                }
            
            # 인덱스 통계 조회
            stats = self.es_client.indices.stats(index=self.es_index)
            count_result = self.es_client.count(index=self.es_index)
            
            return {
                "indexed": True,
                "total_documents": count_result["count"],
                "index_name": self.es_index,
                "index_size": stats["indices"][self.es_index]["total"]["store"]["size_in_bytes"],
                "shard_count": stats["indices"][self.es_index]["total"]["docs"]["count"]
            }
            
        except Exception as e:
            self.logger.error(f"인덱스 통계 조회 실패: {str(e)}")
            return {
                "indexed": False,
                "total_documents": 0,
                "error": str(e)
            }
    
    async def suggest_keywords(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Elasticsearch를 사용한 키워드 자동완성 제안
        
        Args:
            partial_query (str): 부분 검색어
            limit (int): 제안할 키워드 수
            
        Returns:
            List[str]: 제안 키워드 리스트
        """
        if not self.es_client or not partial_query:
            return []
        
        try:
            # Elasticsearch suggest API 사용
            suggest_body = {
                "suggest": {
                    "keyword_suggest": {
                        "prefix": partial_query.lower(),
                        "completion": {
                            "field": "tokens",
                            "size": limit
                        }
                    }
                }
            }
            
            # 간단한 terms aggregation으로 대체
            search_body = {
                "size": 0,
                "aggs": {
                    "keywords": {
                        "terms": {
                            "field": "tokens",
                            "include": f"{partial_query.lower()}.*",
                            "size": limit
                        }
                    }
                }
            }
            
            response = self.es_client.search(
                index=self.es_index,
                **search_body
            )
            
            suggestions = []
            if "aggregations" in response and "keywords" in response["aggregations"]:
                buckets = response["aggregations"]["keywords"]["buckets"]
                suggestions = [bucket["key"] for bucket in buckets]
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"키워드 제안 실패: {str(e)}")
            return []
    
    async def _fallback_search(self, query: str, collection: Collection, limit: int = 10) -> Dict[str, Any]:
        """
        Elasticsearch 연결 실패 시 MongoDB fallback 검색
        
        Args:
            query (str): 검색 쿼리
            collection (Collection): MongoDB 컬렉션
            limit (int): 반환할 최대 결과 수
            
        Returns:
            Dict[str, Any]: 검색 결과
        """
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "message": "검색어를 입력해주세요.",
                    "results": []
                }
            
            self.logger.info(f"MongoDB fallback 검색 시작: '{query}'")
            
            # MongoDB 텍스트 검색 쿼리
            search_query = {
                "$text": {
                    "$search": query
                }
            }
            
            # MongoDB에서 검색 실행
            cursor = collection.find(search_query).limit(limit)
            results = []
            
            for doc in cursor:
                results.append({
                    "resume_id": str(doc.get("_id")),
                    "name": doc.get("name", ""),
                    "position": doc.get("position", ""),
                    "department": doc.get("department", ""),
                    "skills": doc.get("skills", []),
                    "score": doc.get("score", 0)
                })
            
            return {
                "success": True,
                "message": f"MongoDB fallback 검색 완료 (Elasticsearch 연결 없음)",
                "results": results,
                "total": len(results),
                "search_type": "fallback"
            }
            
        except Exception as e:
            self.logger.error(f"MongoDB fallback 검색 실패: {str(e)}")
            return {
                "success": False,
                "message": f"검색 중 오류가 발생했습니다: {str(e)}",
                "results": []
            }