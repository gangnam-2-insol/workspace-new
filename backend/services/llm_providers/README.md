# LLM 프로바이더 서비스

이 디렉토리는 다양한 LLM(Large Language Model) 프로바이더를 통합하여 사용할 수 있는 서비스를 제공합니다.

## 개요

LLM 프로바이더 서비스는 다음과 같은 기능을 제공합니다:

- **통합 인터페이스**: 다양한 LLM 프로바이더를 동일한 인터페이스로 사용
- **자동 설정**: 환경 변수와 설정 파일을 통한 자동 구성
- **에러 처리**: 안전한 API 호출과 예외 처리
- **모니터링**: 응답 시간, 토큰 사용량 등 상세한 메트릭

## 지원하는 프로바이더

### 1. OpenAI
- OpenAI API (GPT-4, GPT-3.5 등)
- Azure OpenAI
- 스트리밍 응답 지원

### 2. Google Gemini
- Google AI Studio API (`google-generativeai`)
- 모델 예시: `gemini-1.5-flash`, `gemini-1.5-pro`
- 환경 변수: `GOOGLE_API_KEY`

```python
from services.llm_providers.base_provider import LLMProviderFactory
from services.llm_providers import gemini_provider  # 등록을 위해 임포트 필요

config = {
    "provider": "gemini",
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "model_name": "gemini-1.5-flash",
    "max_tokens": 4000,
    "temperature": 0.2,
}

provider = LLMProviderFactory.create_provider("gemini", config)
response = await provider.safe_generate("안녕하세요")
print(response.content)
```

## 사용법

### 기본 사용법

```python
from services.llm_providers.openai_provider import OpenAIProvider
from services.llm_providers.base_provider import LLMProviderFactory

# 직접 프로바이더 생성
config = {
    "provider": "openai",
    "api_key": "your-api-key",
    "model_name": "gpt-4o-mini",
    "max_tokens": 4000,
    "temperature": 0.1
}

provider = OpenAIProvider(config)

# 응답 생성
response = await provider.generate_response("안녕하세요!")
print(response.content)
```

### 팩토리를 통한 사용

```python
from services.llm_providers.base_provider import LLMProviderFactory

# 팩토리를 통한 프로바이더 생성
provider = LLMProviderFactory.create_provider("openai", config)

# 안전한 응답 생성
response = await provider.safe_generate("프롬프트")
if response:
    print(response.content)
    print(f"응답 시간: {response.response_time:.2f}초")
```

## 설정

### 환경 변수

```bash
# OpenAI API
export OPENAI_API_KEY="your-api-key"
export OPENAI_ORGANIZATION="your-org-id"

# Azure OpenAI
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-azure-api-key"
```

### 설정 파일

```python
OPENAI_CONFIG = {
    "provider": "openai",
    "api_key": "your-api-key",
    "model_name": "gpt-4o-mini",
    "max_tokens": 4000,
    "temperature": 0.1,
    "max_retries": 3,
    "timeout": 60.0,
    "use_azure": False,  # Azure OpenAI 사용 시 True
    "base_url": None,    # Azure 엔드포인트
    "api_version": "2024-02-15-preview"
}
```

## 응답 객체

`LLMResponse` 객체는 다음과 같은 정보를 포함합니다:

```python
response = await provider.generate_response("프롬프트")

print(f"내용: {response.content}")
print(f"프로바이더: {response.provider}")
print(f"모델: {response.model}")
print(f"응답 시간: {response.response_time:.2f}초")
print(f"메타데이터: {response.metadata}")
```

## 에러 처리

```python
try:
    response = await provider.generate_response("프롬프트")
except Exception as e:
    logger.error(f"API 호출 실패: {e}")
    
# 또는 안전한 메서드 사용
response = await provider.safe_generate("프롬프트")
if response is None:
    logger.error("응답 생성 실패")
```

## 상태 확인

```python
# 기본 상태 확인
if provider.is_healthy():
    print("프로바이더가 정상 작동 중입니다.")

# 상세 상태 확인
health_status = await provider.health_check()
print(f"상태: {health_status}")

# 사용 가능한 모델 조회
models = await provider.get_available_models()
print(f"사용 가능한 모델: {models}")
```

## 테스트

테스트 스크립트를 실행하여 프로바이더가 제대로 작동하는지 확인할 수 있습니다:

```bash
# OpenAI 프로바이더 테스트
python test_openai_provider.py

# 환경 변수 설정 후 실행
export OPENAI_API_KEY="your-api-key"
python test_openai_provider.py
```

## 확장

새로운 LLM 프로바이더를 추가하려면:

1. `base_provider.py`의 `LLMProvider` 클래스를 상속
2. 필수 메서드 구현 (`_initialize`, `generate_response`, `is_healthy`)
3. `LLMProviderFactory`에 등록

```python
class NewProvider(LLMProvider):
    def _initialize(self):
        # 초기화 로직
        pass
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        # 응답 생성 로직
        pass
    
    def is_healthy(self) -> bool:
        # 상태 확인 로직
        pass

# 팩토리에 등록
LLMProviderFactory.register_provider("new_provider", NewProvider)
```

## 주의사항

- API 키는 환경 변수나 안전한 설정 파일을 통해 관리
- 요청 제한과 비용을 고려하여 적절한 설정 사용
- 프로덕션 환경에서는 로깅 레벨을 적절히 조정
- Azure OpenAI 사용 시 올바른 엔드포인트와 API 버전 설정
