# OCR 청킹 관련 수정사항

## 1. OCR 내장 청킹 로직 제거

### 수정 파일: `backend/pdf_ocr_module/main.py`
**수정 위치**: 라인 60-61

#### 수정 전 (OCR에서 청킹도 담당)
```python
# 4) 텍스트를 청크로 분할 및 벡터화
def chunk_text(text: str) -> List[Dict[str, Any]]:
    # 복잡한 청킹 로직
    chunks = []
    sentences = text.split('.')
    current_chunk = ""
    chunk_id = 0
    
    for sentence in sentences:
        if len(current_chunk + sentence) < 500:
            current_chunk += sentence + "."
        else:
            if current_chunk:
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": current_chunk.strip(),
                    "metadata": {"section": "content", "chunk_index": chunk_id}
                })
                chunk_id += 1
            current_chunk = sentence + "."
    
    if current_chunk:
        chunks.append({
            "id": f"chunk_{chunk_id}",
            "text": current_chunk.strip(),
            "metadata": {"section": "content", "chunk_index": chunk_id}
        })
    
    return chunks

# 청킹 실행
chunks = chunk_text(full_text)

# 벡터화 및 저장
chunk_embeddings = []
for chunk in chunks:
    embedding = get_embedding(chunk["text"])
    if embedding:
        chunk_embeddings.append({
            "chunk_id": chunk["id"],
            "text": chunk["text"],
            "embedding": embedding,
            "metadata": chunk["metadata"]
        })

# 벡터 저장소에 업로드
upsert_embeddings(chunk_embeddings)
```

#### 수정 후 (청킹 제거, 텍스트 추출만)
```python
# 4) 청킹 및 벡터 처리는 별도 서비스에서 담당
# OCR은 텍스트 추출까지만 담당
```

## 2. 청킹 서비스 통합

### 수정 파일: `backend/pdf_ocr_module/mongo_saver.py`

#### 2.1 ChunkingService Import 추가
**수정 위치**: 라인 11
```python
from chunking_service import ChunkingService
```

#### 2.2 ChunkingService 초기화
**수정 위치**: 라인 15-16
```python
def __init__(self, mongo_uri: str = None):
    self.mongo_service = MongoService(mongo_uri)
    self.chunking_service = ChunkingService()  # 추가
```

#### 2.3 청킹 데이터 추출 로직 수정 (핵심 수정)
**수정 위치**: 라인 258-297

##### 수정 전 (문제 상황)
```python
# 저장된 applicant 레코드에서 데이터 가져오기 - 필드들이 비어있음
resume_for_chunking = {
    "_id": resume["id"],
    "name": applicant.get("name", ""),           # 빈 문자열
    "skills": applicant.get("skills", ""),       # 빈 문자열  
    "experience": applicant.get("experience", ""), # 빈 문자열
    # ... 기타 필드들도 빈 상태
}
```

##### 수정 후 (해결)
```python
# 6. 의미론적 청킹 적용
try:
    # 지원자 데이터를 이력서 형태로 변환하여 청킹
    # applicant_data (ApplicantCreate)에서 데이터 가져오기
    if hasattr(applicant_data, 'dict'):
        applicant_dict = applicant_data.dict()
    else:
        applicant_dict = applicant_data
    
    resume_for_chunking = {
        "_id": resume["id"],
        "name": applicant_dict.get("name", "") or applicant.get("name", ""),
        "position": applicant_dict.get("position", "") or applicant.get("position", ""),
        "department": applicant_dict.get("department", "") or applicant.get("department", ""),
        "experience": applicant_dict.get("experience", "") or applicant.get("experience", ""),
        "skills": applicant_dict.get("skills", "") or applicant.get("skills", ""),
        "growthBackground": applicant_dict.get("growthBackground", "") or applicant.get("growthBackground", ""),
        "motivation": applicant_dict.get("motivation", "") or applicant.get("motivation", ""),
        "careerHistory": applicant_dict.get("careerHistory", "") or applicant.get("careerHistory", ""),
        "resume_text": ocr_result.get("extracted_text", "")
    }
    
    # 디버깅: 청킹용 데이터 확인
    print(f"🔍 청킹용 데이터 확인:")
    print(f"  - name: {resume_for_chunking['name']}")
    print(f"  - skills: {resume_for_chunking['skills']}")
    print(f"  - experience: {resume_for_chunking['experience']}")
    print(f"  - resume_text 길이: {len(resume_for_chunking['resume_text'])}")
    print(f"  - resume_text 앞 100자: {resume_for_chunking['resume_text'][:100]}...")
    
    chunks = self.chunking_service.chunk_resume_text(resume_for_chunking)
    print(f"✅ 의미론적 청킹 완료: {len(chunks)}개 청크 생성")
    
    # 청킹 결과를 resume 데이터에 추가 (향후 벡터 저장 시 사용)
    if chunks:
        self.mongo_service.update_resume_chunks(resume["id"], chunks)
        
except Exception as e:
    print(f"⚠️ 청킹 처리 실패: {e}")
```

## 3. MongoDB 청킹 업데이트 메서드 확장

### 수정 파일: `backend/services/mongo_service.py`

#### 3.1 자기소개서 청킹 업데이트 메서드 추가
**수정 위치**: 라인 370-389
```python
def update_cover_letter_chunks(self, cover_letter_id: str, chunks: list) -> bool:
    """자기소개서에 청킹 결과를 업데이트합니다."""
    try:
        if self.sync_db is None:
            raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
        
        if len(cover_letter_id) == 24:
            result = self.sync_db.cover_letters.update_one(
                {"_id": ObjectId(cover_letter_id)}, 
                {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
            )
        else:
            result = self.sync_db.cover_letters.update_one(
                {"_id": cover_letter_id}, 
                {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
            )
        return result.modified_count > 0
    except Exception as e:
        print(f"자기소개서 청킹 업데이트 오류: {e}")
        return False
```

#### 3.2 포트폴리오 청킹 업데이트 메서드 추가
**수정 위치**: 라인 391-410
```python
def update_portfolio_chunks(self, portfolio_id: str, chunks: list) -> bool:
    """포트폴리오에 청킹 결과를 업데이트합니다."""
    try:
        if self.sync_db is None:
            raise Exception("동기 MongoDB 클라이언트가 초기화되지 않았습니다.")
        
        if len(portfolio_id) == 24:
            result = self.sync_db.portfolios.update_one(
                {"_id": ObjectId(portfolio_id)}, 
                {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
            )
        else:
            result = self.sync_db.portfolios.update_one(
                {"_id": portfolio_id}, 
                {"$set": {"chunks": chunks, "chunks_updated_at": datetime.now()}}
            )
        return result.modified_count > 0
    except Exception as e:
        print(f"포트폴리오 청킹 업데이트 오류: {e}")
        return False
```

## 4. ChunkingService 전면 리팩토링

### 수정 파일: `backend/chunking_service.py`

#### 4.1 통합된 청킹 인터페이스
**핵심 변경**: 모든 문서 타입을 지원하는 통합 메서드 추가
```python
def chunk_document(self, document: Dict[str, Any], document_type: str = None) -> List[Dict[str, Any]]:
    """문서를 청킹 단위로 분할합니다. (resumes, cover_letters, portfolios 모두 지원)"""
```

#### 4.2 문서 타입별 청킹 설정
**추가 위치**: 라인 8-24
```python
self.chunk_configs = {
    "resume": {"chunk_size": 1000, "overlap": 100},
    "cover_letter": {"chunk_size": 800, "overlap": 50}, 
    "portfolio": {"chunk_size": 600, "overlap": 80}
}
```

#### 4.3 특화된 청킹 로직
- **자기소개서**: `_create_cover_letter_specific_chunks()` - growthBackground, motivation, careerHistory 처리
- **포트폴리오**: `_create_portfolio_specific_chunks()` - items, artifacts 구조 처리
- **공통**: summary, keywords, extracted_text, basic_info 처리

## 5. mongo_saver.py 청킹 구현 완료

### 자기소개서 청킹 구현
**위치**: `save_cover_letter_with_ocr` 메서드, 라인 379-411
```python
# 7. 의미론적 청킹 적용
try:
    # 자기소개서 데이터를 청킹용 형태로 변환
    cover_letter_for_chunking = {
        "_id": cover_letter["id"],
        "applicant_id": applicant["id"],
        "document_type": "cover_letter",
        "extracted_text": ocr_result.get("extracted_text", ""),
        "summary": ocr_result.get("summary", ""),
        "keywords": ocr_result.get("keywords", []),
        "basic_info": basic_info,
        "file_metadata": file_metadata,
        "careerHistory": cover_letter_fields["careerHistory"],
        "growthBackground": cover_letter_fields["growthBackground"],
        "motivation": cover_letter_fields["motivation"]
    }
    
    chunks = self.chunking_service.chunk_cover_letter(cover_letter_for_chunking)
    print(f"✅ 자기소개서 의미론적 청킹 완료: {len(chunks)}개 청크 생성")
    
    if chunks:
        self.mongo_service.update_cover_letter_chunks(cover_letter["id"], chunks)
        
except Exception as e:
    print(f"⚠️ 자기소개서 청킹 처리 실패: {e}")
```

### 포트폴리오 청킹 구현
**위치**: `save_portfolio_with_ocr` 메서드, 라인 499-530
```python
# 7. 의미론적 청킹 적용
try:
    # 포트폴리오 데이터를 청킹용 형태로 변환
    portfolio_for_chunking = {
        "_id": portfolio["id"],
        "applicant_id": applicant["id"],
        "document_type": "portfolio",
        "extracted_text": ocr_result.get("extracted_text", ""),
        "summary": ocr_result.get("summary", ""),
        "keywords": ocr_result.get("keywords", []),
        "basic_info": basic_info,
        "file_metadata": file_metadata,
        "items": [portfolio_item],
        "analysis_score": 0.0,
        "status": "active"
    }
    
    chunks = self.chunking_service.chunk_portfolio(portfolio_for_chunking)
    print(f"✅ 포트폴리오 의미론적 청킹 완료: {len(chunks)}개 청크 생성")
    
    if chunks:
        self.mongo_service.update_portfolio_chunks(portfolio["id"], chunks)
        
except Exception as e:
    print(f"⚠️ 포트폴리오 청킹 처리 실패: {e}")
```

## 변경 이유 및 효과

### 변경 이유
1. **책임 분리**: OCR은 텍스트 추출만, 청킹은 별도 서비스에서 담당
2. **데이터 문제 해결**: 저장된 applicant 레코드의 빈 필드 → 요청 데이터의 실제 값 사용
3. **중복 제거**: OCR 내장 청킹과 커스텀 ChunkingService 중복 실행 방지
4. **일관성 확보**: 모든 문서 타입에서 통일된 청킹 시스템 적용

### 효과
- **수정 전**: 1개 summary 청크만 생성 (데이터 부족) + 이력서만 청킹 지원
- **수정 후**: 6개+ 의미론적 청크 생성 + 자기소개서, 포트폴리오 청킹까지 완전 지원

### 핵심 포인트
1. **데이터 소스 변경**: `applicant` (저장된 레코드) → `applicant_data` (요청 데이터)
2. **폴백 메커니즘**: `applicant_dict.get() or applicant.get()`로 안전성 확보
3. **디버깅 로그**: 청킹용 데이터 상태 실시간 확인 가능
4. **확장성**: 통합된 청킹 인터페이스로 향후 문서 타입 추가 용이