# 하이브리드 로딩 가이드

## 🚀 개요

하이브리드 로딩 시스템은 서버 시작 시간과 실시간 성능 사이의 균형을 제공합니다.

## ⚙️ 환경변수 설정

### 개발 환경 (빠른 시작)
```bash
# .env 파일에 추가
FAST_STARTUP=true
LAZY_LOADING_ENABLED=true
PRELOAD_MODELS=false
BACKGROUND_PRELOAD=true
```

### 프로덕션 환경 (전체 성능)
```bash
# .env 파일에 추가
FAST_STARTUP=false
LAZY_LOADING_ENABLED=false
PRELOAD_MODELS=true
BACKGROUND_PRELOAD=true
```

## 📊 성능 비교

| 환경 | 서버 시작 시간 | 첫 요청 응답 시간 | 메모리 사용량 |
|------|---------------|------------------|---------------|
| 기존 방식 | 1-3분 | 2-5초 | ~1.7GB |
| 하이브리드 (빠른시작) | 10-30초 | 5-15초 | ~200MB → +1.5GB |
| 하이브리드 (전체성능) | 1-3분 | 2-5초 | ~1.7GB |

## 🔧 적용된 서비스

### 1. EmbeddingService
- **지연 로딩**: SentenceTransformer 백업 모델
- **사전 로딩**: OpenAI API 클라이언트

### 2. ResumeAnalysisService
- **지연 로딩**: HuggingFace 분석기 (4개 모델)
- **사전 로딩**: OpenAI 분석기

## 🎯 사용법

### 개발 시
```bash
# 빠른 서버 재시작을 위해
export FAST_STARTUP=true
python main.py
```

### 프로덕션 배포 시
```bash
# 최고 성능을 위해
export FAST_STARTUP=false
export PRELOAD_MODELS=true
python main.py
```

## 🔍 모니터링

서버 시작 시 다음과 같은 로그를 확인할 수 있습니다:

```
✅ Embedding 서비스 초기화 성공 (지연 로딩 모드)
✅ HuggingFace 분석기 지연 로딩 설정 완료
```

또는

```
✅ Embedding 서비스 초기화 성공 (사전 로딩 모드)
✅ HuggingFace 분석기 초기화 완료
```

## ⚠️ 주의사항

1. **첫 요청 지연**: 지연 로딩 모드에서는 첫 번째 요청 시 모델 로딩으로 인한 지연이 발생할 수 있습니다.
2. **메모리 스파이크**: 사용 시점에 메모리 사용량이 급증할 수 있습니다.
3. **백업 모델**: OpenAI API 실패 시에만 백업 모델이 로딩됩니다.

## 🛠️ 문제 해결

### 서버 시작이 여전히 느린 경우
```bash
# 모든 지연 로딩 활성화
export FAST_STARTUP=true
export LAZY_LOADING_ENABLED=true
export PRELOAD_MODELS=false
```

### 첫 요청이 너무 느린 경우
```bash
# 사전 로딩 활성화
export FAST_STARTUP=false
export PRELOAD_MODELS=true
```

## 📈 성능 최적화 팁

1. **개발 환경**: `FAST_STARTUP=true` 사용
2. **테스트 환경**: 필요한 기능만 로딩
3. **프로덕션 환경**: `PRELOAD_MODELS=true` 사용
4. **메모리 제한 환경**: 지연 로딩 활용
