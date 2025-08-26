# ApplicantManagement 컴포넌트

지원자 관리 기능을 제공하는 모듈화된 React 컴포넌트입니다.

## 📁 프로젝트 구조

```
src/components/ApplicantManagement/
├── index.js                           # ① public API
├── ApplicantManagement.jsx            # ② 메인 로직 (상위 컴포넌트)
├── styles.js                          # ③ styled‑components 한 곳에 모음
├── utils.js                           # ④ 공통 유틸
├── services/
│  ├── api.js                          # ⑤ API 호출
│  └── jobPostingApi.js               # ⑥ 채용공고 API
├── hooks/
│  ├── useApplicants.js                # ⑦ useApplicants
│  ├── useStats.js                     # ⑧ useStats
│  ├── useSelection.js                # ⑨ useSelection
│  ├── useFilters.js                  # ⑩ useFilters
│  └── useRanking.js                  # ⑪ useRanking
├── components/
│  ├── ApplicantCard.jsx               # ⑫ 카드(그리드용)
│  ├── ApplicantBoard.jsx              # ⑬ 보드(행)용
│  ├── StatsCards.jsx                  # ⑭ 통계 카드
│  ├── SearchBar.jsx                   # ⑮ 검색·필터·랭킹 UI
│  └── BaseModal.jsx                   # ⑯ 공통 Modal 구조
└── README.md                          # 사용 안내
```

## 🚀 사용법

### 기본 사용법

```jsx
import ApplicantManagement from './components/ApplicantManagement';

function App() {
  return (
    <div className="App">
      <ApplicantManagement />
    </div>
  );
}
```

### 환경 변수 설정

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🔧 주요 기능

### 1. 지원자 목록 관리
- 그리드/보드 뷰 전환
- 페이지네이션
- 실시간 검색 및 필터링

### 2. 상태 관리
- 지원자 상태 업데이트 (합격/보류/불합격)
- 일괄 상태 변경

### 3. 통계 대시보드
- 총 지원자 수
- 합격/보류/불합격 비율
- 실시간 업데이트

### 4. 랭킹 시스템
- 지원자 자동 랭킹
- 키워드 기반 점수 계산

## 📋 API 엔드포인트

### 지원자 관련
- `GET /api/applicants` - 지원자 목록 조회
- `PUT /api/applicants/{id}/status` - 상태 업데이트
- `GET /api/applicants/stats/overview` - 통계 조회

### 채용공고 관련
- `GET /api/job-postings` - 채용공고 목록

### 포트폴리오 관련
- `GET /api/portfolios/applicant/{id}` - 지원자별 포트폴리오

## 🎨 스타일링

CSS 변수를 사용하여 일관된 디자인을 유지합니다:

```css
:root {
  --primary-color: #3b82f6;
  --primary-dark: #2563eb;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --background-secondary: #f9fafb;
}
```

## 🔄 상태 관리

### 로컬 상태
- `viewMode`: 그리드/보드 뷰 모드
- `currentPage`: 현재 페이지
- `modal`: 모달 상태
- `selected`: 선택된 지원자들

### 커스텀 훅
- `useApplicants`: 지원자 데이터 관리
- `useStats`: 통계 데이터 관리
- `useSelection`: 선택 기능 관리
- `useFilters`: 필터링 기능 관리
- `useRanking`: 랭킹 기능 관리

## 🛠️ 확장 가능한 부분

### 1. 추가 모달
- `FilterModal.jsx` - 고급 필터링
- `ResumeModal.jsx` - 새 지원자 등록
- `DocumentModal.jsx` - 문서 뷰어
- `DetailedAnalysisModal.jsx` - 상세 분석

### 2. 추가 기능
- 이메일 발송 기능
- 엑셀 내보내기
- 지원자 비교 기능
- 면접 일정 관리

### 3. 성능 최적화
- 가상화 스크롤링 (대용량 데이터)
- 메모이제이션 최적화
- 지연 로딩

## 🐛 문제 해결

### 빌드 오류
- 중복 선언된 styled-components 확인
- import 경로 확인
- 의존성 설치 확인

### API 오류
- 서버 연결 상태 확인
- 환경 변수 설정 확인
- CORS 설정 확인

## 📝 개발 가이드

### 새 컴포넌트 추가
1. `components/` 폴더에 새 파일 생성
2. 스타일은 `styles.js`에 추가
3. 필요한 훅은 `hooks/` 폴더에 추가
4. API 호출은 `services/` 폴더에 추가

### 스타일 수정
- `styles.js` 파일에서 해당 컴포넌트 스타일 수정
- CSS 변수 활용하여 일관성 유지
- 반응형 디자인 고려

### API 수정
- `services/` 폴더의 해당 API 파일 수정
- 에러 핸들링 추가
- 로딩 상태 관리

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

