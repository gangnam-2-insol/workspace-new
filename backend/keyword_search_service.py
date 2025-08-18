from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
from pymongo.collection import Collection
from rank_bm25 import BM25Okapi
import re
from datetime import datetime
import logging
try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    print("Warning: kiwipiepy not available, using fallback tokenizer")
    Kiwi = None
    KIWI_AVAILABLE = False

class KeywordSearchService:
    def __init__(self):
        """
        키워드 검색 서비스 초기화
        BM25 알고리즘을 사용한 키워드 기반 검색
        """
        self.bm25_index = None
        self.indexed_documents = []
        self.document_ids = []
        self.index_created_at = None
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
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
    
    async def build_index(self, collection: Collection) -> Dict[str, Any]:
        """
        모든 이력서에 대한 BM25 인덱스를 구축합니다.
        
        Args:
            collection (Collection): MongoDB 이력서 컬렉션
            
        Returns:
            Dict[str, Any]: 인덱스 구축 결과
        """
        try:
            self.logger.info("=== BM25 인덱스 구축 시작 ===")
            
            # 모든 이력서 조회
            resumes = list(collection.find({}))
            
            if not resumes:
                return {
                    "success": False,
                    "message": "인덱싱할 이력서가 없습니다.",
                    "total_documents": 0
                }
            
            # 문서 텍스트 추출 및 토큰화
            tokenized_docs = []
            document_ids = []
            
            for resume in resumes:
                # 검색 가능한 텍스트 추출
                searchable_text = self._extract_searchable_text(resume)
                
                # 텍스트 토큰화
                tokens = self._preprocess_text(searchable_text)
                
                if tokens:  # 토큰이 있는 경우만 포함
                    tokenized_docs.append(tokens)
                    document_ids.append(str(resume["_id"]))
                    
                    self.logger.debug(f"문서 인덱싱: {resume.get('name', 'Unknown')} "
                                    f"({len(tokens)} 토큰)")
            
            if not tokenized_docs:
                return {
                    "success": False,
                    "message": "인덱싱할 유효한 문서가 없습니다.",
                    "total_documents": 0
                }
            
            # BM25 인덱스 생성
            self.bm25_index = BM25Okapi(tokenized_docs)
            self.indexed_documents = tokenized_docs
            self.document_ids = document_ids
            self.index_created_at = datetime.now()
            
            self.logger.info(f"BM25 인덱스 구축 완료: {len(tokenized_docs)}개 문서")
            
            return {
                "success": True,
                "message": "BM25 인덱스 구축이 완료되었습니다.",
                "total_documents": len(tokenized_docs),
                "index_created_at": self.index_created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"BM25 인덱스 구축 실패: {str(e)}")
            return {
                "success": False,
                "message": f"인덱스 구축 중 오류가 발생했습니다: {str(e)}",
                "total_documents": 0
            }
    
    async def search_by_keywords(self, query: str, collection: Collection, 
                               limit: int = 10) -> Dict[str, Any]:
        """
        키워드 기반으로 이력서를 검색합니다.
        
        Args:
            query (str): 검색 쿼리
            collection (Collection): MongoDB 이력서 컬렉션
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
            
            # 인덱스가 없거나 오래된 경우 재구축
            if (not self.bm25_index or 
                not self.index_created_at or
                (datetime.now() - self.index_created_at).total_seconds() > 3600):  # 1시간
                
                self.logger.info("인덱스 재구축 필요")
                index_result = await self.build_index(collection)
                if not index_result["success"]:
                    return {
                        "success": False,
                        "message": "인덱스 구축에 실패했습니다.",
                        "results": []
                    }
            
            self.logger.info(f"키워드 검색 시작: '{query}'")
            
            # 쿼리 토큰화
            query_tokens = self._preprocess_text(query)
            
            if not query_tokens:
                return {
                    "success": False,
                    "message": "유효한 검색 토큰이 없습니다.",
                    "results": []
                }
            
            self.logger.info(f"검색 토큰: {query_tokens}")
            
            # BM25 점수 계산
            scores = self.bm25_index.get_scores(query_tokens)
            
            # 점수와 문서 ID 매핑
            scored_docs = [(score, doc_id) for score, doc_id in zip(scores, self.document_ids)]
            
            # 점수 기준 내림차순 정렬
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            # 상위 결과만 선택 (점수가 0보다 큰 것만)
            top_docs = [(score, doc_id) for score, doc_id in scored_docs 
                       if score > 0.0][:limit]
            
            if not top_docs:
                return {
                    "success": True,
                    "message": "검색 결과가 없습니다.",
                    "results": [],
                    "total": 0
                }
            
            # MongoDB에서 상세 정보 조회
            doc_ids = [ObjectId(doc_id) for _, doc_id in top_docs]
            resumes = list(collection.find({"_id": {"$in": doc_ids}}))
            
            # 결과 매핑
            results = []
            for score, doc_id in top_docs:
                resume = next((r for r in resumes if str(r["_id"]) == doc_id), None)
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
                    
                    # 검색 점수 및 하이라이트 추가
                    highlight_text = self._highlight_query_terms(
                        self._extract_searchable_text(resume), 
                        query_tokens
                    )
                    
                    results.append({
                        "bm25_score": round(score, 4),
                        "resume": resume,
                        "highlight": highlight_text[:200] + "..." if len(highlight_text) > 200 else highlight_text
                    })
            
            self.logger.info(f"키워드 검색 완료: {len(results)}개 결과")
            
            return {
                "success": True,
                "message": f"'{query}' 검색 결과입니다.",
                "results": results,
                "total": len(results),
                "query": query,
                "query_tokens": query_tokens
            }
            
        except Exception as e:
            self.logger.error(f"키워드 검색 실패: {str(e)}")
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
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        현재 인덱스 통계를 반환합니다.
        
        Returns:
            Dict[str, Any]: 인덱스 통계
        """
        if not self.bm25_index:
            return {
                "indexed": False,
                "total_documents": 0,
                "index_created_at": None
            }
        
        return {
            "indexed": True,
            "total_documents": len(self.document_ids),
            "index_created_at": self.index_created_at.isoformat() if self.index_created_at else None,
            "average_doc_length": sum(len(doc) for doc in self.indexed_documents) / len(self.indexed_documents) if self.indexed_documents else 0
        }
    
    async def suggest_keywords(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        부분 쿼리에 대한 키워드 제안을 제공합니다.
        
        Args:
            partial_query (str): 부분 검색어
            limit (int): 제안할 키워드 수
            
        Returns:
            List[str]: 제안 키워드 리스트
        """
        if not self.indexed_documents or not partial_query:
            return []
        
        partial_query = partial_query.lower()
        suggestions = set()
        
        # 모든 문서의 토큰에서 부분 쿼리와 매칭되는 단어 찾기
        for doc_tokens in self.indexed_documents:
            for token in doc_tokens:
                if token.startswith(partial_query) and len(token) > len(partial_query):
                    suggestions.add(token)
        
        # 빈도순으로 정렬 (간단한 구현)
        sorted_suggestions = sorted(list(suggestions))[:limit]
        
        return sorted_suggestions