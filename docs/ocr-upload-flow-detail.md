# OCR 업로드 플로우 상세 설명

## 📋 개요
이력서와 자소서가 프론트엔드에서 업로드되어 OCR 처리 후 DB에 저장되는 전체 플로우를 설명합니다.

## 🔄 전체 플로우

### 1. 프론트엔드 업로드 단계

#### **파일 선택**
- 사용자가 드래그 앤 드롭 또는 파일 선택 버튼으로 PDF 파일 업로드
- 지원 파일 형식: `.pdf`, `.doc`, `.docx`, `.txt`
- 파일 크기 제한: 최대 50MB

#### **파일 유효성 검사**
```javascript
// frontend/src/pages/ApplicantManagement.js
const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

if (allowedTypes.includes(fileExtension)) {
    // 파일 업로드 진행
}
```

### 2. 백엔드 OCR 처리 단계

#### **API 엔드포인트**
- **이력서**: `POST /api/integrated-ocr/upload-resume`
- **자소서**: `POST /api/integrated-ocr/upload-cover-letter`
- **포트폴리오**: `POST /api/integrated-ocr/upload-portfolio`

#### **파일 처리 과정**
```python
# backend/routers/integrated_ocr.py
# 1. 임시 파일 저장
with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
    content = await file.read()
    temp_file.write(content)
    temp_file_path = Path(temp_file.name)

# 2. PDF OCR 처리
ocr_result = process_pdf(str(temp_file_path))

# 3. AI 분석
ai_analysis = analyze_text(ocr_result.get("full_text", ""), settings)
```

### 3. OCR 처리 상세 과정

#### **PDF → 이미지 변환**
```python
# backend/pdf_ocr_module/pdf_processor.py
def save_pdf_pages_to_images(pdf_path: Path, output_dir: Path, settings: Settings) -> List[Path]:
    # PDF 페이지를 이미지로 변환
    # 이미지 전처리 (그레이스케일, 대비 강화, 샤프닝)
```

#### **GPT-4o-mini Vision API OCR 처리**
```python
# backend/pdf_ocr_module/ocr_engine.py
def ocr_images_with_quality(image_paths: List[Path], settings: Settings) -> List[Dict]:
    # 한국어 + 영어 언어팩 사용
    # PSM 모드 최적화
    # 이미지 품질 임계값 조정
```

#### **AI 분석 (OpenAI GPT-4o-mini)**
```python
# backend/pdf_ocr_module/ai_analyzer.py
def analyze_text(text: str, settings: Settings) -> Dict[str, Any]:
    # 이름, 이메일, 전화번호 추출
    # 직무, 기술스택 추출
    # 요약 및 키워드 생성
    # 문서 타입 분류
```

### 4. 데이터 추출 및 구조화

#### **기본 정보 추출**
```python
# backend/routers/integrated_ocr.py
def _extract_contact_from_text(text: str) -> Dict[str, Optional[str]]:
    # 이름 추출 패턴 (13가지 패턴)
    name_patterns = [
        r'(?:이름|성명|Name|name)\s*[:\-]?\s*([가-힣]{2,4})',
        r'([가-힣]{2,4})\s*(?:님|씨|군|양)',
        # ... 더 많은 패턴
    ]
    
    # 이메일 추출
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    
    # 전화번호 추출
    phone_patterns = [
        r'(\d{3}-\d{3,4}-\d{4})',
        r'(\d{3}\s*\d{3,4}\s*\d{4})',
    ]
```

#### **지원자 데이터 생성**
```python
def _build_applicant_data(name, email, phone, ocr_result, job_posting_id):
    # 우선순위에 따른 정보 결정
    final_name = (
        name or                    # Form 입력
        ai_single_name or          # AI 단일 값
        (ai_names[0] if ai_names else None) or  # AI 배열 첫 번째
        extracted.get("name") or   # 텍스트 추출
        "이름미상"                 # 기본값
    )
    
    # 직무, 기술스택, 경력 정보 추출
    final_position = ai_position or _extract_position_from_text(text)
    final_skills = _extract_skills_from_text(text)
    final_experience = _extract_experience_from_text(text)
```

### 5. 데이터베이스 저장

#### **이력서 저장 플로우**
```python
# backend/pdf_ocr_module/mongo_saver.py
def save_resume_with_ocr(self, ocr_result, applicant_data, job_posting_id, file_path):
    # 1. 지원자 생성/조회
    applicant = self.mongo_service.create_or_get_applicant(applicant_data)
    
    # 2. 파일 메타데이터 생성
    file_metadata = self._create_file_metadata(file_path)
    
    # 3. 기본 정보 추출
    basic_info = self._extract_basic_info_from_ocr(ocr_result)
    
    # 4. 이력서 데이터 생성
    resume_data = ResumeCreate(
        applicant_id=applicant.id,
        extracted_text=ocr_result.get("extracted_text", ""),
        summary=ocr_result.get("summary", ""),
        keywords=ocr_result.get("keywords", []),
        document_type="resume",
        basic_info=basic_info,
        file_metadata=file_metadata
    )
    
    # 5. 이력서 저장
    resume = self.mongo_service.create_resume(resume_data)
```

#### **자소서 저장 플로우**
```python
def save_cover_letter_with_ocr(self, ocr_result, applicant_data, job_posting_id, file_path):
    # 1. 지원자 생성/조회
    applicant = self.mongo_service.create_or_get_applicant(applicant_data)
    
    # 2. 파일 메타데이터 생성
    file_metadata = self._create_file_metadata(file_path)
    
    # 3. 기본 정보 추출
    basic_info = self._extract_basic_info_from_ocr(ocr_result)
    
    # 4. 자소서 데이터 생성 (구조화된 basic_info 포함)
    cover_letter_data = CoverLetterCreate(
        applicant_id=applicant.id,
        extracted_text=ocr_result.get("extracted_text", ""),
        summary=ocr_result.get("summary", ""),
        keywords=ocr_result.get("keywords", []),
        document_type="cover_letter",
        basic_info=basic_info,  # 구조화된 정보
        file_metadata=file_metadata
    )
    
    # 5. 자소서 저장
    cover_letter = self.mongo_service.create_cover_letter(cover_letter_data)
```

### 6. 저장된 데이터 구조

#### **이력서 컬렉션**
```json
{
  "_id": "ObjectId",
  "applicant_id": "ObjectId",
  "extracted_text": "OCR로 추출된 텍스트...",
  "summary": "AI 분석 요약...",
  "keywords": ["React", "JavaScript", "TypeScript"],
  "document_type": "resume",
  "file_metadata": {
    "filename": "resume.pdf",
    "size": 256000,
    "uploaded_at": "2025-08-19T13:24:23.493+00:00"
  },
  "created_at": "2025-08-19T13:24:23.493+00:00",
  "updated_at": "2025-08-19T13:24:23.493+00:00"
}
```

#### **자소서 컬렉션**
```json
{
  "_id": "ObjectId",
  "applicant_id": "ObjectId",
  "extracted_text": "OCR로 추출된 텍스트...",
  "summary": "AI 분석 요약...",
  "keywords": ["동기", "성장", "목표"],
  "document_type": "cover_letter",
  "basic_info": {
    "name": "김민수",
    "position": "프론트엔드 개발자",
    "department": "개발팀",
    "experience": "3-5년",
    "email": "kim@example.com",
    "phone": "010-1234-5678",
    "motivation": "지원동기 내용...",
    "growthBackground": "성장 과정 내용...",
    "careerHistory": "경력사항 내용...",
    "strengths": "강점 내용...",
    "goals": "목표 내용...",
    "conclusion": "마무리 내용...",
    "analysisScore": 85,
    "analysisResult": "분석 결과..."
  },
  "file_metadata": {
    "filename": "cover_letter.pdf",
    "size": 512000,
    "uploaded_at": "2025-08-19T13:24:23.493+00:00"
  },
  "created_at": "2025-08-19T13:24:23.493+00:00",
  "updated_at": "2025-08-19T13:24:23.493+00:00"
}
```

## 🎯 주요 특징

### 1. **다단계 정보 추출**
- **1차**: Form 입력 정보 (사용자 직접 입력)
- **2차**: AI 분석 결과 (OpenAI GPT-4o-mini)
- **3차**: 정규식 기반 추출 (백업)
- **4차**: 기본값 설정

### 2. **OCR 품질 최적화**
- 이미지 전처리 (대비 강화, 샤프닝)
- 한국어 + 영어 언어팩 지원
- PSM 모드 최적화

### 3. **AI 기반 구조화**
- 자소서의 경우 `basic_info` 객체로 구조화
- 파싱된 필드들을 미리 저장하여 실시간 분석 부담 감소

### 4. **에러 처리 및 백업**
- AI 분석 실패 시 정규식 기반 추출
- 파일 처리 실패 시 적절한 에러 메시지
- 임시 파일 자동 정리

## 🔧 개발 시 주의사항

1. **파일 크기 제한**: 50MB 이하
2. **지원 형식**: PDF, DOC, DOCX, TXT
3. **OCR 품질**: 이미지 전처리로 정확도 향상
4. **AI 분석**: OpenAI API 키 설정 필요
5. **데이터 일관성**: `applicant_id`로 문서 연결
