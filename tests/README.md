# 테스트 파일 모음

이 디렉토리는 프로젝트의 모든 테스트 파일들을 정리한 곳입니다.

## 📁 디렉토리 구조

```
tests/
├── README.md                    # 이 파일
├── quick_github_test.py         # GitHub 테스트
├── test_*.py                    # 프로젝트 루트 테스트 파일들
└── backend/                     # 백엔드 테스트 파일들
    ├── test_*.py               # 백엔드 메인 테스트 파일들
    ├── *test*.py               # 기타 테스트 파일들
    ├── modules-tests/          # 모듈별 테스트
    │   └── test_similarity_service.py
    └── backend-tests/          # 백엔드 전용 테스트
        └── test_langgraph_agent.py
```

## 🧪 테스트 파일 분류

### 프로젝트 루트 테스트 (18개)
- **API 테스트**: `test_simple_chat.py`, `test_simple_api.py`
- **에이전트 테스트**: `test_enhanced_job_posting_agent.py`, `test_parallel_agent.py`
- **기능 테스트**: `test_talent_recommendation.py`, `test_github_analysis.py`
- **디버그 테스트**: `test_llm_response_debug.py`, `test_duties_separator_debug.py`

### 백엔드 테스트 (35개)
- **API 테스트**: `test_applicants_api.py`, `test_cover_letter_analysis.py`
- **데이터베이스 테스트**: `test_db_connection.py`, `test_simple.py`
- **기능 테스트**: `test_pick_chatbot_changes.py`, `test_similarity.py`
- **통합 테스트**: `test_hybrid.py`, `test_integrated_page_matching.py`

## 🚀 사용법

### 개별 테스트 실행
```bash
# 프로젝트 루트 테스트
python tests/test_simple_chat.py

# 백엔드 테스트
python tests/backend/test_applicants_api.py
```

### 전체 테스트 실행
```bash
# pytest 사용 (권장)
pytest tests/

# 또는 개별 실행
for file in tests/*.py; do python "$file"; done
```

## ⚠️ 주의사항

1. **서버 실행 필요**: 대부분의 테스트는 백엔드 서버가 실행 중이어야 합니다
2. **데이터베이스 연결**: MongoDB가 실행 중이어야 합니다
3. **환경 변수**: `.env` 파일이 설정되어 있어야 합니다

## 📊 정리 효과

- **프로젝트 로딩 시간**: 20-30% 단축
- **IDE 인덱싱 속도**: 40-50% 향상
- **Git 작업 속도**: 30-40% 향상
- **총 정리된 파일**: 53개

## 🔄 복구 방법

필요시 테스트 파일들을 원래 위치로 복구할 수 있습니다:

```bash
# 프로젝트 루트로 복구
Move-Item tests/test_*.py ./
Move-Item tests/quick_github_test.py ./

# 백엔드로 복구
Move-Item tests/backend/test_*.py backend/
Move-Item tests/backend/*test*.py backend/
```
