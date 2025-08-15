# AI 기반 문서 분석 시스템 사용 가이드

## 개요

이 시스템은 FastAPI와 Google Gemini API를 활용하여 업로드된 문서(이력서, 자기소개서, 포트폴리오)를 AI로 분석하고 요약하는 기능을 제공합니다.

## 주요 기능

### 1. 기본 요약 기능
- **파일 업로드**: PDF, DOC, DOCX, TXT 파일 지원
- **텍스트 요약**: 일반, 기술, 경력 중심 요약
- **키워드 추출**: 문서에서 핵심 키워드 자동 추출
- **신뢰도 점수**: 분석 결과의 신뢰도 평가

### 2. 상세 분석 기능 (NEW!)
- **다면적 분석**: 이력서, 자기소개서, 포트폴리오 각각에 대한 상세 분석
- **항목별 점수**: 0-10점 척도로 각 항목별 평가
- **구체적 피드백**: 개선이 필요한 부분에 대한 구체적 제안
- **종합 평가**: 전체적인 적합도 점수와 권장사항

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```env
GOOGLE_API_KEY=your-gemini-api-key-here
```

### 3. 서버 실행
```bash
python main.py
```

## API 엔드포인트

### 1. 헬스 체크
```http
GET /api/upload/health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "gemini_api_configured": true,
  "supported_formats": [".pdf", ".doc", ".docx", ".txt"],
  "max_file_size_mb": 10
}
```

### 2. 텍스트 요약
```http
POST /api/upload/summarize
Content-Type: application/json

{
  "content": "분석할 텍스트 내용",
  "summary_type": "general"
}
```

**응답 예시:**
```json
{
  "summary": "요약된 내용",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "confidence_score": 0.85,
  "processing_time": 2.3
}
```

### 3. 파일 업로드 및 요약
```http
POST /api/upload/file
Content-Type: multipart/form-data

file: [파일]
summary_type: "general"
```

**응답 예시:**
```json
{
  "filename": "resume.pdf",
  "file_size": 1024000,
  "extracted_text_length": 5000,
  "summary": "요약된 내용",
  "keywords": ["키워드1", "키워드2"],
  "confidence_score": 0.85,
  "processing_time": 3.2,
  "summary_type": "general"
}
```

### 4. 상세 분석 (NEW!)
```http
POST /api/upload/analyze
Content-Type: multipart/form-data

file: [파일]
document_type: "resume"
```

**응답 예시:**
```json
{
  "filename": "resume.pdf",
  "file_size": 1024000,
  "extracted_text_length": 5000,
  "document_type": "resume",
  "analysis_result": {
    "resume_analysis": {
      "basic_info_completeness": {
        "score": 8,
        "feedback": "필수 정보가 잘 작성되어 있습니다."
      },
      "job_relevance": {
        "score": 9,
        "feedback": "지원 직무와 경력이 매우 잘 맞습니다."
      },
      "experience_clarity": {
        "score": 7,
        "feedback": "경력 설명이 명확하지만 성과 지표를 더 추가하면 좋겠습니다."
      },
      "tech_stack_clarity": {
        "score": 9,
        "feedback": "기술 스택이 명확하게 기재되어 있습니다."
      },
      "project_recency": {
        "score": 8,
        "feedback": "최근 프로젝트 중심으로 잘 작성되어 있습니다."
      },
      "achievement_metrics": {
        "score": 7,
        "feedback": "정량적 성과가 일부 포함되어 있지만 더 추가하면 좋겠습니다."
      },
      "readability": {
        "score": 9,
        "feedback": "가독성이 매우 좋습니다."
      },
      "typos_and_errors": {
        "score": 10,
        "feedback": "오탈자가 없습니다."
      },
      "update_freshness": {
        "score": 9,
        "feedback": "최근에 업데이트된 이력서입니다."
      }
    },
    "cover_letter_analysis": {
      "motivation_relevance": {
        "score": 8,
        "feedback": "지원 동기가 회사와 잘 연결되어 있습니다."
      },
      "problem_solving_STAR": {
        "score": 7,
        "feedback": "STAR 기법이 적용되어 있지만 결과 부분을 강화하면 좋겠습니다."
      },
      "quantitative_impact": {
        "score": 6,
        "feedback": "정량적 성과가 부족합니다."
      },
      "job_understanding": {
        "score": 8,
        "feedback": "직무에 대한 이해도가 높습니다."
      },
      "unique_experience": {
        "score": 7,
        "feedback": "차별화된 경험이 일부 포함되어 있습니다."
      },
      "logical_flow": {
        "score": 8,
        "feedback": "논리적 흐름이 좋습니다."
      },
      "keyword_diversity": {
        "score": 8,
        "feedback": "전문 용어가 적절히 사용되고 있습니다."
      },
      "sentence_readability": {
        "score": 9,
        "feedback": "문장이 읽기 쉽게 작성되어 있습니다."
      },
      "typos_and_errors": {
        "score": 10,
        "feedback": "오탈자가 없습니다."
      }
    },
    "portfolio_analysis": {
      "project_overview": {
        "score": 8,
        "feedback": "프로젝트 개요가 명확합니다."
      },
      "tech_stack": {
        "score": 9,
        "feedback": "사용 기술이 상세히 기재되어 있습니다."
      },
      "personal_contribution": {
        "score": 8,
        "feedback": "개인 기여도가 명확하게 구분되어 있습니다."
      },
      "achievement_metrics": {
        "score": 7,
        "feedback": "성과를 수치화하면 더 좋겠습니다."
      },
      "visual_quality": {
        "score": 8,
        "feedback": "시각 자료가 깔끔합니다."
      },
      "documentation_quality": {
        "score": 9,
        "feedback": "문서화가 잘 되어 있습니다."
      },
      "job_relevance": {
        "score": 9,
        "feedback": "지원 직무와 포트폴리오가 잘 맞습니다."
      },
      "unique_features": {
        "score": 7,
        "feedback": "독창적 기능을 더 강조하면 좋겠습니다."
      },
      "maintainability": {
        "score": 8,
        "feedback": "유지보수성이 좋습니다."
      }
    },
    "overall_summary": {
      "total_score": 8,
      "recommendation": "전반적으로 우수한 지원자입니다. 기술 스택과 경력이 직무에 적합하며, 문서 품질도 높습니다. 일부 성과 지표를 보강하면 완성도가 더 높아질 것입니다."
    }
  }
}
```

## 분석 기준

### 이력서 분석 기준
1. **기본 정보 완성도**: 이름, 연락처, 이메일, GitHub/LinkedIn 등 필수 정보
2. **직무 적합성**: 지원 직무와 경력의 연관성
3. **경력 설명 명확성**: 업무 내용과 성과의 구체성
4. **기술 스택 명확성**: 사용 기술의 명시 및 숙련도
5. **프로젝트 최신성**: 최근 2-3년간 프로젝트 중심 작성 여부
6. **성과 지표**: 정량적 수치, 비율, 기간 등
7. **가독성**: 레이아웃과 글머리표 사용
8. **오탈자**: 맞춤법, 띄어쓰기 오류
9. **최신성**: 최근 수정 날짜, 최신 경력 포함

### 자기소개서 분석 기준
1. **지원 동기**: 회사/직무와의 연결성
2. **문제 해결 사례**: STAR 기법 적용 여부
3. **정량적 성과**: 수치화된 결과 언급
4. **직무 이해도**: 직무 핵심 역량 언급
5. **차별화 요소**: 독창적인 경험/관점
6. **논리 구조**: 단락별 주제 명확성
7. **키워드 다양성**: 전문 용어 활용
8. **문장 가독성**: 문장 길이와 문체 일관성
9. **오탈자**: 맞춤법, 문법 오류

### 포트폴리오 분석 기준
1. **프로젝트 개요**: 목적, 기간, 팀 규모, 역할 명시
2. **기술 스택**: 사용 기술, 도구 명확성
3. **개인 기여도**: 역할, 책임 비율
4. **성과 지표**: 수치화된 결과
5. **시각 자료**: 캡처, 다이어그램, 시연 영상
6. **문서화 수준**: README, API 문서, 아키텍처
7. **직무 관련성**: 지원 직무와 프로젝트 연관성
8. **독창적 기능**: 시장에서 차별화되는 포인트
9. **유지보수성**: 코드 가독성, 버전관리

## 테스트

### 테스트 실행
```bash
python test_upload.py
```

### 테스트 항목
1. **헬스 체크**: 서버 상태 확인
2. **텍스트 요약**: 텍스트 직접 요약 기능
3. **파일 업로드**: 파일 업로드 및 요약 기능
4. **상세 분석**: 새로운 상세 분석 기능

## 프론트엔드 통합

### React 컴포넌트 사용 예시
```javascript
import DetailedAnalysisModal from '../components/DetailedAnalysisModal';

// 상세 분석 모달 사용
<DetailedAnalysisModal
  isOpen={showDetailedAnalysis}
  onClose={() => setShowDetailedAnalysis(false)}
  analysisData={analysisResult}
/>
```

### API 호출 예시
```javascript
const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', 'resume');

  const response = await fetch('http://localhost:8010/api/upload/analyze', {
    method: 'POST',
    body: formData,
  });

  const result = await response.json();
  console.log('분석 결과:', result.analysis_result);
};
```

## 주의사항

### 1. API 키 설정
- Google Gemini API 키가 필요합니다
- `.env` 파일에 `GOOGLE_API_KEY` 설정 필수

### 2. 파일 크기 제한
- 최대 10MB까지 업로드 가능
- 지원 형식: PDF, DOC, DOCX, TXT

### 3. 처리 시간
- 파일 크기와 내용에 따라 5-30초 소요
- 대용량 파일은 처리 시간이 길어질 수 있음

### 4. 오류 처리
- 파일 형식 오류
- API 키 미설정
- 네트워크 연결 오류
- 파일 크기 초과

## 트러블슈팅

### 1. API 키 오류
```
Error: Gemini API 키가 설정되지 않았습니다.
```
**해결방법**: `.env` 파일에 올바른 API 키 설정

### 2. 파일 형식 오류
```
Error: 지원하지 않는 파일 형식입니다.
```
**해결방법**: PDF, DOC, DOCX, TXT 파일만 지원

### 3. 파일 크기 오류
```
Error: 파일 크기가 너무 큽니다.
```
**해결방법**: 10MB 이하 파일 사용

### 4. 텍스트 추출 실패
```
Error: 파일에서 텍스트를 추출할 수 없습니다.
```
**해결방법**: 
- PDF 파일: PyPDF2 설치 확인
- Word 파일: python-docx 설치 확인
- 파일이 손상되지 않았는지 확인

## 업데이트 히스토리

### v2.0.0 (2025-01-08)
- 상세 분석 기능 추가
- 이력서, 자기소개서, 포트폴리오 각각에 대한 다면적 분석
- 항목별 점수(0-10) 및 구체적 피드백
- 종합 평가 및 권장사항 제공
- 새로운 UI 컴포넌트 (DetailedAnalysisModal) 추가

### v1.0.0 (2025-01-07)
- 기본 파일 업로드 및 요약 기능
- 텍스트 직접 요약 기능
- 키워드 추출 및 신뢰도 점수
- 기본 UI 통합
