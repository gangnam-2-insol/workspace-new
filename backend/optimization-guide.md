# 백엔드 최적화 가이드

## 1. 의존성 최적화

### 현재 문제점
- 200개 이상의 패키지 설치
- 무거운 AI/ML 라이브러리들
- 중복된 기능의 패키지들
- 개발용 패키지가 프로덕션에 포함

### 최적화 방안

#### A. 필수 패키지만 유지
```bash
# 기존 requirements.txt 백업
cp requirements.txt requirements-full.txt

# 최적화된 requirements.txt 사용
cp requirements-optimized.txt requirements.txt

# 가상환경 재생성
pip uninstall -r requirements-full.txt -y
pip install -r requirements-optimized.txt
```

#### B. 선택적 패키지 설치
```bash
# 개발 환경용
pip install -r requirements-dev.txt

# 프로덕션 환경용
pip install -r requirements-prod.txt
```

## 2. 서버 시작 최적화

### A. 지연 로딩 구현
```python
# main.py에서 지연 로딩
import asyncio
from functools import lru_cache

# 무거운 모듈들을 지연 로딩
@lru_cache(maxsize=1)
def get_ai_services():
    """AI 서비스들을 필요할 때만 로드"""
    from modules.ai.resume_analysis_service import ResumeAnalysisService
    from modules.core.services.embedding_service import EmbeddingService
    return {
        'resume_analysis': ResumeAnalysisService(db),
        'embedding': EmbeddingService()
    }

# 라우터에서 지연 로딩 사용
@app.post("/api/ai-analysis/resume/analyze")
async def analyze_resume(request: dict):
    ai_services = get_ai_services()
    # AI 서비스 사용
```

### B. 서비스 초기화 최적화
```python
# main.py 수정
async def init_services_lazy():
    """서비스를 필요할 때만 초기화"""
    global services_initialized
    if not services_initialized:
        # 필수 서비스만 초기화
        await init_essential_services()
        services_initialized = True

async def init_essential_services():
    """필수 서비스만 초기화"""
    # MongoDB 연결만 초기화
    # AI 서비스는 지연 로딩
    pass
```

## 3. 메모리 최적화

### A. 모델 캐싱
```python
# 모델 캐싱 구현
from functools import lru_cache
import torch

@lru_cache(maxsize=1)
def get_embedding_model():
    """임베딩 모델을 한 번만 로드"""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')

@lru_cache(maxsize=1)
def get_llm_model():
    """LLM 모델을 한 번만 로드"""
    # 필요한 경우에만 로드
    pass
```

### B. 메모리 사용량 모니터링
```python
# 메모리 모니터링 유틸리티
import psutil
import gc

def log_memory_usage():
    """메모리 사용량 로깅"""
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

    # 가비지 컬렉션 실행
    gc.collect()

# 주기적으로 메모리 정리
@app.middleware("http")
async def memory_cleanup_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        log_memory_usage()
    return response
```

## 4. 데이터베이스 최적화

### A. 연결 풀 최적화
```python
# MongoDB 연결 최적화
client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=20,  # 50 -> 20으로 감소
    minPoolSize=5,   # 10 -> 5로 감소
    maxIdleTimeMS=30000,
    serverSelectionTimeoutMS=3000,  # 5초 -> 3초
    socketTimeoutMS=10000,  # 20초 -> 10초
    connectTimeoutMS=5000,  # 10초 -> 5초
    retryWrites=True
)
```

### B. 쿼리 최적화
```python
# 인덱스 생성
async def create_indexes():
    """필요한 인덱스만 생성"""
    await db.applicants.create_index("status")
    await db.applicants.create_index("created_at")
    await db.applicants.create_index([("name", 1), ("position", 1)])

# 쿼리 최적화
async def get_applicants_optimized(limit=50):
    """최적화된 지원자 조회"""
    return await db.applicants.find(
        {},
        {"name": 1, "position": 1, "status": 1, "created_at": 1}  # 필요한 필드만
    ).limit(limit).to_list(limit)
```

## 5. 서버 시작 스크립트 최적화

### A. 빠른 시작 스크립트
```python
# start_server_fast.py
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # 개발 모드 최적화
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
        log_level="warning",  # 로그 레벨 낮춤
        access_log=False,     # 액세스 로그 비활성화
        workers=1,           # 단일 워커
        loop="asyncio"       # asyncio 루프 사용
    )
```

### B. 프로덕션 시작 스크립트
```python
# start_server_prod.py
import uvicorn
import multiprocessing

if __name__ == "__main__":
    # 프로덕션 모드
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=multiprocessing.cpu_count(),
        log_level="info",
        access_log=True
    )
```

## 6. Docker 최적화

### A. 멀티스테이지 빌드
```dockerfile
# Dockerfile.optimized
FROM python:3.11-slim as builder

# 빌드 의존성만 설치
COPY requirements-optimized.txt .
RUN pip install --no-cache-dir -r requirements-optimized.txt

FROM python:3.11-slim as runtime

# 런타임만 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY . /app
WORKDIR /app

# 최적화된 실행
CMD ["python", "start_server_fast.py"]
```

## 예상 성능 개선 효과
- **시작 시간**: 60-70% 단축
- **메모리 사용량**: 40-50% 감소
- **응답 시간**: 30-40% 향상
- **패키지 크기**: 50-60% 감소
