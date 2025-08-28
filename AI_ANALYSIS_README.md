# 🤖 AI 이력서 분석 시스템

이 문서는 `readme_resume.md`에 설명된 이력서 분석 기능을 현재 프로젝트에 구현한 내용을 설명합니다.

## 📋 구현된 기능

### 1. 백엔드 AI 분석 모듈

#### **Pydantic 모델** (`backend/models/resume_analysis.py`)
- `ResumeAnalysisResult`: OpenAI 기반 분석 결과 모델
- `HuggingFaceAnalysisResult`: HuggingFace 기반 확장 분석 결과 모델
- `AnalysisState`: 분석 상태 관리 모델
- `ResumeAnalysisRequest`: 분석 요청 모델
- `ResumeAnalysisResponse`: 분석 응답 모델

#### **OpenAI 분석기** (`backend/modules/ai/resume_analyzer.py`)
- GPT-4o-mini 모델을 사용한 이력서 분석
- 5개 항목별 점수 평가 (학력, 경력, 기술, 프로젝트, 성장)
- 상세한 분석 내용 및 피드백 제공
- LangChain 프레임워크 기반

#### **HuggingFace 분석기** (`backend/modules/ai/huggingface_analyzer.py`)
- 로컬 AI 모델을 사용한 분석 (GPU/CPU 지원)
- 7개 항목 평가 (기본 5개 + 문법, 직무 적합성)
- 다양한 전용 모델 조합 사용
- 오프라인 동작 지원

#### **분석 서비스** (`backend/modules/ai/resume_analysis_service.py`)
- 단일/일괄 분석 관리
- 분석 결과 저장 및 조회
- 분석 상태 모니터링
- 점수 분포 통계

### 2. API 엔드포인트

#### **이력서 분석 API**
```http
POST /api/ai-analysis/resume/analyze
POST /api/ai-analysis/resume/batch-analyze
POST /api/ai-analysis/resume/reanalyze
GET /api/ai-analysis/resume/analysis-status
GET /api/ai-analysis/resume/{applicant_id}
```

#### **기존 이력서 조회 API 개선**
- `GET /api/applicants/{applicant_id}/resume`에 AI 분석 결과 포함
- 기존 분석 결과가 있으면 자동으로 포함하여 반환

### 3. 프론트엔드 컴포넌트

#### **AI 분석 API 서비스** (`frontend/src/services/aiAnalysisApi.js`)
- AI 분석 API 호출 함수들
- 분석 결과 처리 및 요약 생성
- 점수 등급 계산 및 진행률 분석

#### **AI 분석 모달** (`frontend/src/components/ApplicantManagement/AIAnalysisModal.jsx`)
- AI 분석 실행 및 결과 표시
- OpenAI/HuggingFace 분석기 선택
- 점수별 시각적 피드백
- 강점/개선점/권장사항 표시

#### **DocumentModal 개선**
- 이력서 보기 시 AI 분석 버튼 추가
- AI 분석 결과 통합 표시

## 🚀 사용 방법

### 1. 환경 설정

#### **백엔드 환경변수**
```bash
# .env 파일에 추가
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URI=mongodb://localhost:27017
```

#### **필요한 패키지 설치**
```bash
cd backend
pip install -r requirements.txt
```

### 2. AI 분석 실행

#### **단일 이력서 분석**
```javascript
import { analyzeResume } from '../services/aiAnalysisApi';

// OpenAI 분석기로 분석
const result = await analyzeResume(applicantId, 'openai', false);

// HuggingFace 분석기로 분석
const result = await analyzeResume(applicantId, 'huggingface', false);
```

#### **일괄 분석**
```javascript
import { batchAnalyzeResumes } from '../services/aiAnalysisApi';

const result = await batchAnalyzeResumes(applicantIds, 'openai');
```

#### **재분석**
```javascript
import { reanalyzeResume } from '../services/aiAnalysisApi';

const result = await reanalyzeResume(applicantId, 'openai');
```

### 3. 분석 결과 활용

#### **분석 결과 요약 생성**
```javascript
import { generateAnalysisSummary } from '../services/aiAnalysisApi';

const summary = generateAnalysisSummary(analysisResult);
console.log('전체 점수:', summary.overall.score);
console.log('등급:', summary.overall.grade.label);
console.log('강점:', summary.feedback.strengths);
```

#### **점수 등급 계산**
```javascript
import { calculateScoreGrade } from '../services/aiAnalysisApi';

const grade = calculateScoreGrade(85);
console.log(grade); // { grade: 'A', label: '우수', color: '#28a745', icon: '⭐' }
```

## 🔧 테스트

### **백엔드 테스트**
```bash
cd backend
python test_ai_analysis.py
```

### **프론트엔드 테스트**
1. 지원자 목록 페이지에서 이력서 선택
2. AI 분석 버튼 클릭
3. 분석 타입 선택 (OpenAI 또는 HuggingFace)
4. 분석 시작 버튼 클릭
5. 분석 결과 확인

## 📊 분석 결과 구조

### **OpenAI 분석 결과**
```json
{
  "overall_score": 85,
  "education_score": 90,
  "experience_score": 88,
  "skills_score": 82,
  "projects_score": 87,
  "growth_score": 83,
  "education_analysis": "학력이 우수하고 전공이 직무와 잘 맞습니다...",
  "experience_analysis": "관련 경험이 풍부하고 구체적인 성과가 있습니다...",
  "skills_analysis": "필요한 기술 스택을 대부분 보유하고 있습니다...",
  "projects_analysis": "다양한 프로젝트 경험과 명확한 기여도가 있습니다...",
  "growth_analysis": "지속적인 학습 의지와 성장 가능성이 보입니다...",
  "strengths": ["강한 문제 해결 능력", "팀워크 능력이 뛰어남"],
  "improvements": ["최신 기술 스택 부족", "대규모 프로젝트 경험 부족"],
  "overall_feedback": "전반적으로 우수한 지원자입니다...",
  "recommendations": ["기술 스택을 더 다양화하세요", "프로젝트 경험을 강화하세요"]
}
```

### **HuggingFace 분석 결과 (확장)**
```json
{
  // 기본 5개 항목 + 추가 항목
  "grammar_score": 85,
  "grammar_analysis": "문법 및 표현 품질: 85/100",
  "job_matching_score": 88,
  "job_matching_analysis": "직무 적합성: 88/100"
}
```

## 🎯 주요 특징

### **1. 다중 AI 모델 지원**
- **OpenAI**: GPT-4o-mini 기반 고품질 분석
- **HuggingFace**: 로컬 모델 기반 오프라인 분석

### **2. 상세한 평가 시스템**
- 5-7개 항목별 세부 점수 (0-100점)
- 점수별 등급 시스템 (A+, A, B+, B, C+, C, D)
- 시각적 피드백 및 아이콘

### **3. 실용적인 피드백**
- 구체적인 강점 및 개선점 제시
- 실행 가능한 개선 권장사항
- 직무 적합성 분석

### **4. 성능 최적화**
- 기존 분석 결과 재사용
- 일괄 분석 지원
- 분석 상태 모니터링

## 🔒 보안 고려사항

### **1. API 키 보안**
- OpenAI API 키는 환경변수로 관리
- 프론트엔드에 노출되지 않음

### **2. 입력 검증**
- 지원자 ID 유효성 검사
- 분석 요청 데이터 검증

### **3. 권한 관리**
- 분석 실행 권한 확인 (향후 구현 예정)
- 사용자별 접근 제어

## 📈 향후 계획

### **1. 추가 분석 항목**
- 언어 능력 평가
- 자격증 및 인증 분석
- 수상 경력 분석

### **2. 고급 기능**
- 경쟁사 비교 분석
- 트렌드 분석
- 예측 분석

### **3. 통합 대시보드**
- 실시간 분석 현황
- 통계 및 인사이트
- 성과 추적

## 🐛 문제 해결

### **1. OpenAI API 오류**
- API 키 확인
- API 할당량 확인
- 네트워크 연결 상태 확인

### **2. HuggingFace 모델 로딩 오류**
- GPU 메모리 확인
- 모델 다운로드 상태 확인
- 의존성 패키지 버전 확인

### **3. 분석 결과 저장 오류**
- MongoDB 연결 상태 확인
- 데이터베이스 권한 확인
- 디스크 공간 확인

## 📞 지원

AI 분석 기능과 관련된 문제나 질문이 있으시면 개발팀에 문의해 주세요.

---

**구현 완료일**: 2024년 12월
**버전**: 1.0.0
**개발자**: AI 분석 시스템 개발팀
