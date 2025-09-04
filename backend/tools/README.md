# 🛠️ AI 채용 관리 시스템 - 툴 래핑

## 📋 개요

이 모듈은 AI 채용 관리 시스템의 API들을 더 사용하기 쉽게 감싸는 **툴 래핑(Tool Wrapping)** 라이브러리입니다. 기존 API들을 래핑하여 다음과 같은 기능을 제공합니다:

- ✅ **자동 재시도 로직**
- ✅ **에러 처리 및 로깅**
- ✅ **타입 안전성**
- ✅ **사용하기 쉬운 인터페이스**
- ✅ **비동기 지원**

## 🚀 주요 기능

### 1. 재시도 메커니즘
```python
@retry_on_failure(APIRetryConfig(max_retries=3, delay=1.0, backoff=2.0))
async def api_call():
    # API 호출 로직
    pass
```

### 2. 에러 처리
- HTTP 상태 코드별 에러 처리
- 상세한 에러 메시지 제공
- 로깅을 통한 디버깅 지원

### 3. 타입 안전성
- Pydantic 모델 기반 타입 검증
- IDE 자동완성 지원
- 런타임 타입 검사

## 📦 설치 및 사용법

### 1. 의존성 설치
```bash
pip install httpx
```

### 2. 기본 사용법
```python
import asyncio
from tools.api_wrapper import HireMeAPIWrapper

async def main():
    async with HireMeAPIWrapper() as api:
        # 지원자 생성
        result = await api.applicant.create_applicant({
            "name": "김개발",
            "email": "kim@example.com",
            "position": "프론트엔드 개발자"
        })
        print(f"지원자 생성 완료: {result['name']}")

asyncio.run(main())
```

## 🔧 API 래퍼 클래스

### 1. ApplicantManagementWrapper
지원자 관리 API 래퍼

```python
# 지원자 생성
result = await api.applicant.create_applicant(applicant_data)

# 지원자 목록 조회
applicants = await api.applicant.get_applicants(
    skip=0,
    limit=50,
    status="pending"
)

# 지원자 상태 업데이트
result = await api.applicant.update_applicant_status(
    applicant_id, "서류합격"
)
```

### 2. ChatbotWrapper
채팅봇 API 래퍼

```python
# AI 어시스턴트 채팅
response = await api.chatbot.ai_assistant_chat(
    user_input="채용공고를 작성해주세요",
    session_id="session_123"
)

# AI 제목 추천
title = await api.chatbot.generate_title(
    job_description="React 개발자 모집",
    company_name="테크스타트업",
    concept="신입친화형"
)
```

### 3. PDFOCRWrapper
PDF OCR API 래퍼

```python
# 이력서 업로드 및 OCR
result = await api.pdf_ocr.upload_resume(
    file_path="resume.pdf",
    name="김개발",
    email="kim@example.com",
    job_posting_id="job_123"
)

# 자기소개서 업로드 및 OCR
result = await api.pdf_ocr.upload_cover_letter(
    file_path="cover_letter.pdf",
    job_posting_id="job_123"
)
```

### 4. GitHubAnalysisWrapper
GitHub 분석 API 래퍼

```python
# GitHub 사용자 분석
result = await api.github.analyze_user(
    username="github_username",
    force_reanalysis=False
)

# GitHub 저장소 분석
result = await api.github.analyze_repository(
    username="github_username",
    repo_name="project_name"
)
```

### 5. ResumeSearchWrapper
이력서 검색 API 래퍼

```python
# 키워드 검색
results = await api.resume_search.keyword_search(
    query="React TypeScript",
    limit=10
)

# 하이브리드 검색
results = await api.resume_search.hybrid_search(
    query="프론트엔드 개발자",
    filters={
        "experience_years": [3, 5],
        "skills": ["React", "TypeScript"]
    },
    limit=10
)
```

### 6. AIAnalysisWrapper
AI 분석 API 래퍼

```python
# 이력서 AI 분석
result = await api.ai_analysis.analyze_resume(
    applicant_id="applicant_123",
    analyzer_type="openai",
    force_reanalysis=False
)

# 일괄 이력서 분석
result = await api.ai_analysis.batch_analyze_resumes(
    applicant_ids=["applicant_123", "applicant_456"],
    analyzer_type="openai"
)
```

## 🔄 완전한 워크플로우 예시

```python
async def complete_recruitment_workflow():
    async with HireMeAPIWrapper() as api:
        try:
            # 1. 채용공고 작성 (AI 어시스턴트)
            chat_response = await api.chatbot.ai_assistant_chat(
                user_input="React 개발자 채용공고를 작성해주세요. 3년 이상 경력자를 원합니다.",
                session_id="workflow_session"
            )

            # 2. 이력서 업로드 및 OCR
            ocr_result = await api.pdf_ocr.upload_resume(
                file_path="resume.pdf",
                job_posting_id="job_123"
            )
            applicant_id = ocr_result['applicant_id']

            # 3. AI 분석
            analysis_result = await api.ai_analysis.analyze_resume(
                applicant_id=applicant_id,
                analyzer_type="openai"
            )

            # 4. 유사한 지원자 검색
            search_result = await api.resume_search.hybrid_search(
                query="React 개발자",
                filters={"experience_years": [3, 5]},
                limit=5
            )

            # 5. GitHub 분석
            github_result = await api.github.analyze_user(
                username="applicant_github_username"
            )

            # 6. 지원자 상태 업데이트
            status_result = await api.applicant.update_applicant_status(
                applicant_id, "서류합격"
            )

            print("✅ 전체 워크플로우 완료!")

        except Exception as e:
            print(f"❌ 워크플로우 실패: {e}")
```

## ⚙️ 설정 옵션

### APIRetryConfig
```python
config = APIRetryConfig(
    max_retries=3,      # 최대 재시도 횟수
    delay=1.0,          # 초기 대기 시간 (초)
    backoff=2.0         # 지수 백오프 배수
)
```

### 타임아웃 설정
```python
# 각 래퍼별 타임아웃 설정
ApplicantManagementWrapper: 30초
ChatbotWrapper: 30초
PDFOCRWrapper: 60초 (OCR은 시간이 오래 걸림)
GitHubAnalysisWrapper: 120초 (GitHub 분석은 시간이 오래 걸림)
ResumeSearchWrapper: 30초
AIAnalysisWrapper: 60초
```

## 🐛 에러 처리

### HTTP 상태 코드별 처리
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류
- `503`: 서비스 사용 불가

### 재시도 조건
- 네트워크 오류
- 서버 일시적 오류 (5xx)
- 타임아웃

### 재시도하지 않는 조건
- 클라이언트 오류 (4xx)
- 인증 오류
- 권한 오류

## 📊 로깅

### 로그 레벨
- `INFO`: 일반적인 API 호출 정보
- `WARNING`: 재시도 발생
- `ERROR`: 최종 실패

### 로그 예시
```
INFO: 지원자 생성 시작
WARNING: API 호출 실패 (시도 1/3): Connection timeout. 1.0초 후 재시도...
INFO: 지원자 생성 성공
```

## 🧪 테스트

### 예시 실행
```bash
cd backend/tools
python usage_examples.py
```

### 개별 기능 테스트
```python
# 지원자 관리 테스트
await example_applicant_management()

# 채팅봇 테스트
await example_chatbot()

# PDF OCR 테스트
await example_pdf_ocr()

# GitHub 분석 테스트
await example_github_analysis()

# 이력서 검색 테스트
await example_resume_search()

# AI 분석 테스트
await example_ai_analysis()

# 완전한 워크플로우 테스트
await example_complete_workflow()
```

## 🔒 보안 고려사항

1. **API 키 관리**: 환경변수를 통한 안전한 API 키 관리
2. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS 사용
3. **타임아웃 설정**: 적절한 타임아웃으로 무한 대기 방지
4. **에러 메시지**: 민감한 정보가 포함되지 않도록 에러 메시지 필터링

## 📈 성능 최적화

1. **연결 풀링**: httpx의 AsyncClient를 통한 연결 재사용
2. **비동기 처리**: asyncio를 통한 동시 요청 처리
3. **재시도 최적화**: 지수 백오프를 통한 효율적인 재시도
4. **타임아웃 설정**: 기능별 적절한 타임아웃 설정

## 🤝 기여하기

1. 새로운 API 래퍼 추가
2. 기존 래퍼 개선
3. 테스트 케이스 추가
4. 문서 개선

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
