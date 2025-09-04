# 🚀 최적화 시스템 가이드

## 📋 개요

이 문서는 AI Similarity Analysis System의 최적화 시스템에 대한 종합 가이드입니다. 하이브리드 로딩, 지능형 캐싱, 백그라운드 프리로딩, 성능 모니터링 등 다양한 최적화 기능을 제공합니다.

## 🏗️ 아키텍처

### 핵심 컴포넌트

1. **하이브리드 로딩 시스템**
   - 환경별 모델 로딩 전략
   - 지연 로딩 vs 사전 로딩
   - 동적 로딩 제어

2. **지능형 캐싱 시스템**
   - LRU 기반 캐시 관리
   - 메모리 사용량 최적화
   - 자동 캐시 정리

3. **백그라운드 프리로딩**
   - 사용 패턴 기반 모델 프리로딩
   - 우선순위 기반 로딩
   - 의존성 관리

4. **성능 모니터링**
   - 실시간 메트릭 수집
   - 알림 시스템
   - 자동 튜닝

5. **통합 최적화 서비스**
   - 모든 최적화 기능 통합 관리
   - 환경별 자동 설정
   - 동적 성능 조정

## 🔧 설정 방법

### 환경변수 설정

```bash
# 기본 하이브리드 로딩 설정
export FAST_STARTUP=true                    # 빠른 시작 모드
export LAZY_LOADING_ENABLED=true           # 지연 로딩 활성화
export PRELOAD_MODELS=false                # 모델 사전 로딩 비활성화

# 최적화 서비스 설정
export ENABLE_INTELLIGENT_CACHE=true       # 지능형 캐싱 활성화
export ENABLE_BACKGROUND_PRELOADING=true   # 백그라운드 프리로딩 활성화
export ENABLE_PERFORMANCE_MONITORING=true  # 성능 모니터링 활성화
export AUTO_TUNING_ENABLED=true            # 자동 튜닝 활성화

# 환경 설정
export ENVIRONMENT=development              # development, production, testing
```

### 환경별 최적화 설정

#### 개발 환경 (Development)
```bash
export ENVIRONMENT=development
export FAST_STARTUP=true
export CACHE_MEMORY_LIMIT_MB=200
export PRELOAD_MAX_CONCURRENT=1
```
- **특징**: 빠른 시작 우선
- **캐시**: 200MB 제한
- **프리로딩**: 최소 동시 로딩

#### 프로덕션 환경 (Production)
```bash
export ENVIRONMENT=production
export FAST_STARTUP=false
export CACHE_MEMORY_LIMIT_MB=1000
export PRELOAD_MAX_CONCURRENT=3
```
- **특징**: 성능 우선
- **캐시**: 1GB 제한
- **프리로딩**: 최대 동시 로딩

#### 테스트 환경 (Testing)
```bash
export ENVIRONMENT=testing
export FAST_STARTUP=true
export CACHE_MEMORY_LIMIT_MB=100
export AUTO_TUNING_ENABLED=false
```
- **특징**: 최소 리소스 사용
- **캐시**: 100MB 제한
- **자동 튜닝**: 비활성화

## 🚀 사용법

### 1. 기본 서버 시작

```bash
# 개발 환경 (빠른 시작)
export ENVIRONMENT=development
python main.py

# 프로덕션 환경 (전체 성능)
export ENVIRONMENT=production
python main.py
```

### 2. 지능형 캐싱 사용

```python
from modules.core.services.intelligent_cache_service import intelligent_cache, cache_result

# 직접 캐싱
await intelligent_cache.set("user_data", user_data, user_id)
cached_data = await intelligent_cache.get("user_data", user_id)

# 데코레이터 사용
@cache_result("expensive_operation", ttl_hours=1)
async def expensive_operation(param1, param2):
    # 비용이 큰 연산
    return result
```

### 3. 백그라운드 프리로딩

```python
from modules.core.services.background_preloader import register_preload_task, record_model_usage

# 프리로드 작업 등록
register_preload_task(
    name="my_model",
    priority=8,
    load_function=load_my_model,
    dependencies=["base_model"],
    estimated_load_time=30.0
)

# 모델 사용 기록
record_model_usage("my_model")
```

### 4. 성능 모니터링

```python
from modules.core.services.performance_monitor import performance_monitor, monitor_performance

# 메트릭 추가
performance_monitor.add_metric("api.response_time", 0.5, "seconds")

# 데코레이터 사용
@monitor_performance("my_function", "seconds")
async def my_function():
    # 함수 실행
    return result

# 통계 조회
stats = performance_monitor.get_stats()
system_health = performance_monitor.get_system_health()
```

### 5. 통합 최적화 서비스

```python
from modules.core.services.optimization_service import (
    initialize_optimization,
    get_optimization_stats,
    shutdown_optimization
)

# 초기화
await initialize_optimization("production")

# 통계 조회
stats = get_optimization_stats()

# 종료
await shutdown_optimization()
```

## 📊 성능 메트릭

### 주요 지표

1. **서버 시작 시간**
   - 개발 환경: 10-30초
   - 프로덕션 환경: 60-120초

2. **메모리 사용량**
   - 기본: 200-500MB
   - 최대: 1-2GB (프로덕션)

3. **캐시 히트율**
   - 목표: 80% 이상
   - 최적: 90% 이상

4. **응답 시간**
   - 캐시 히트: < 100ms
   - 캐시 미스: 1-5초

### 모니터링 대시보드

```python
# 통합 통계 조회
stats = get_optimization_stats()

print(f"캐시 히트율: {stats['cache']['hit_rate']}")
print(f"프리로딩 성공률: {stats['preloader']['success_rate']}")
print(f"시스템 메모리: {stats['system_health']['memory_percent']}%")
print(f"CPU 사용률: {stats['system_health']['cpu_percent']}%")
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. 서버 시작이 느린 경우
```bash
# 빠른 시작 모드 활성화
export FAST_STARTUP=true
export LAZY_LOADING_ENABLED=true
export PRELOAD_MODELS=false
```

#### 2. 메모리 사용량이 높은 경우
```bash
# 캐시 크기 제한
export CACHE_MEMORY_LIMIT_MB=200
export ENABLE_BACKGROUND_PRELOADING=false
```

#### 3. 응답 시간이 느린 경우
```bash
# 사전 로딩 활성화
export FAST_STARTUP=false
export PRELOAD_MODELS=true
export CACHE_MEMORY_LIMIT_MB=1000
```

#### 4. 캐시 히트율이 낮은 경우
```python
# 캐시 TTL 조정
await intelligent_cache.set("key", data, ttl_hours=24)

# 캐시 패턴 분석
stats = intelligent_cache.get_stats()
print(f"캐시 히트율: {stats['hit_rate']}")
```

### 로그 분석

```bash
# 성능 로그 확인
tail -f logs/performance.log

# 캐시 통계 확인
grep "cache" logs/application.log

# 프리로딩 상태 확인
grep "preload" logs/application.log
```

## 🧪 테스트

### 최적화 시스템 테스트

```bash
# 전체 최적화 테스트
python test_optimization_system.py

# 하이브리드 로딩 테스트
python test_hybrid_loading.py

# 서버 시작 시간 테스트
python test_server_startup.py
```

### 성능 벤치마크

```bash
# 개발 환경 벤치마크
export ENVIRONMENT=development
python test_optimization_system.py

# 프로덕션 환경 벤치마크
export ENVIRONMENT=production
python test_optimization_system.py
```

## 📈 최적화 팁

### 1. 개발 단계
- `FAST_STARTUP=true` 사용
- 최소한의 모델만 사전 로딩
- 캐시 크기 제한

### 2. 테스트 단계
- `ENVIRONMENT=testing` 사용
- 자동 튜닝 비활성화
- 최소 리소스 사용

### 3. 프로덕션 단계
- `ENVIRONMENT=production` 사용
- 모든 모델 사전 로딩
- 최대 캐시 크기
- 성능 모니터링 활성화

### 4. 모니터링
- 정기적인 성능 통계 확인
- 알림 규칙 설정
- 자동 튜닝 결과 모니터링

## 🔧 고급 설정

### 커스텀 알림 규칙

```python
from modules.core.services.performance_monitor import AlertRule, performance_monitor

# 커스텀 알림 규칙 추가
custom_rule = AlertRule(
    name="high_api_latency",
    metric_name="api.response_time",
    threshold=2.0,
    operator=">",
    duration_seconds=60
)

performance_monitor.add_alert_rule(custom_rule)
```

### 커스텀 프리로드 작업

```python
from modules.core.services.background_preloader import register_preload_task

async def load_custom_model():
    # 커스텀 모델 로딩 로직
    pass

register_preload_task(
    name="custom_model",
    priority=9,
    load_function=load_custom_model,
    dependencies=["base_models"],
    estimated_load_time=45.0
)
```

### 캐시 전략 커스터마이징

```python
from modules.core.services.intelligent_cache_service import intelligent_cache

# 캐시 무효화
await intelligent_cache.invalidate_pattern("user_*")

# 캐시 통계 모니터링
stats = intelligent_cache.get_stats()
if stats['hit_rate'] < '80%':
    # 캐시 전략 조정
    pass
```

## 📚 참고 자료

- [하이브리드 로딩 가이드](HYBRID_LOADING_GUIDE.md)
- [성능 모니터링 문서](docs/performance_monitoring.md)
- [캐싱 전략 가이드](docs/caching_strategy.md)
- [API 문서](docs/api_reference.md)

## 🤝 기여하기

1. 새로운 최적화 기능 제안
2. 성능 개선 아이디어 공유
3. 버그 리포트 및 수정
4. 문서 개선

---

**문의사항이나 문제가 있으시면 이슈를 등록해 주세요.**
