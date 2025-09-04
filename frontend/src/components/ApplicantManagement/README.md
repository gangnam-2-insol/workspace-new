# 지원자 관리 컴포넌트

## 📋 개요

이 컴포넌트는 지원자 관리 시스템의 핵심 기능을 제공합니다. 지원자 목록 조회, 필터링, 검색, 랭킹, 그리고 다양한 모달을 통한 상세 정보 확인 및 관리 기능을 포함합니다.

## 🗂️ 컴포넌트 구조

```
ApplicantManagement/
├── ApplicantManagement.jsx          # 메인 컴포넌트
├── ApplicantDetailModal.jsx         # 지원자 상세정보 모달
├── DocumentModal.jsx                # 문서 보기 모달 (이력서, 자소서, 포트폴리오)
├── NewApplicantModal.jsx            # 새 지원자 등록 모달
├── ApplicantManagementModals.jsx    # 통합 모달 관리 컴포넌트
├── ApplicantCard.js                 # 지원자 카드 컴포넌트
├── ApplicantBoard.js                # 지원자 보드 뷰 컴포넌트
├── StatsCards.js                    # 통계 카드 컴포넌트
├── SearchBar.js                     # 검색 및 필터 컴포넌트
├── FilterModal.js                   # 필터 모달 컴포넌트
├── ResumeUploadModal.js             # 이력서 업로드 모달
├── styles.js                        # 스타일 정의
├── utils.js                         # 유틸리티 함수
└── hooks/                           # 커스텀 훅
    ├── useApplicants.js            # 지원자 데이터 관리
    ├── useStats.js                 # 통계 데이터 관리
    ├── useSelection.js             # 선택 상태 관리
    ├── useFilters.js               # 필터 상태 관리
    └── useRanking.js               # 랭킹 계산
```

## 🚀 주요 기능

### 1. 지원자 목록 관리
- 그리드/보드 뷰 전환
- 페이지네이션
- 정렬 및 필터링
- 검색 기능

### 2. 모달 시스템
- **지원자 상세정보 모달**: 기본 정보 및 액션 버튼
- **문서 보기 모달**: 이력서, 자소서, 포트폴리오 상세 보기
- **새 지원자 등록 모달**: 파일 업로드 및 정보 입력

### 3. 데이터 분석
- 지원자 통계
- AI 기반 랭킹
- 유사도 체크 (자소서)

## 🎯 모달 컴포넌트 상세

### ApplicantDetailModal
지원자의 기본 정보를 표시하고, 이력서, 자소서, 포트폴리오 보기로 이동할 수 있는 액션 버튼을 제공합니다.

**주요 기능:**
- 지원자 기본 정보 표시
- 상태별 배지 표시
- 문서 보기 액션 버튼

### DocumentModal
이력서, 자소서, 포트폴리오를 상세하게 보여주는 모달입니다.

**주요 기능:**
- 문서 타입별 표시
- 포트폴리오 뷰 선택 (GitHub/기존 포트폴리오)
- 자소서 유사도 체크 결과
- 원본/요약 보기 토글

### NewApplicantModal
새로운 지원자를 등록하는 모달입니다.

**주요 기능:**
- PDF 파일 드래그&드롭 업로드
- 지원자 정보 입력 폼
- 기존 지원자 중복 체크
- GitHub URL 연동

## 🔧 사용법

### 기본 사용법

```jsx
import ApplicantManagement from './components/ApplicantManagement';

function App() {
  return (
    <div>
      <ApplicantManagement />
    </div>
  );
}
```

### 모달 상태 관리

```jsx
const [detailModal, setDetailModal] = useState({ isOpen: false, applicant: null });
const [documentModal, setDocumentModal] = useState({ 
  isOpen: false, 
  type: '', 
  applicant: null 
});
const [newApplicantModal, setNewApplicantModal] = useState({ isOpen: false });

// 모달 열기
const handleCardClick = (applicant) => {
  setDetailModal({ isOpen: true, applicant });
};

// 모달 닫기
const handleDetailModalClose = () => {
  setDetailModal({ isOpen: false, applicant: null });
};
```

### API 연동

```jsx
// 지원자 목록 조회
const { applicants, loading, reload } = useApplicants();

// 새 지원자 등록
const handleNewApplicantSubmit = async (formData) => {
  try {
    const response = await fetch('/api/applicants', {
      method: 'POST',
      body: formData,
    });
    if (response.ok) {
      reload(); // 목록 새로고침
    }
  } catch (error) {
    console.error('등록 실패:', error);
  }
};
```

## 🎨 스타일 시스템

### CSS 변수

```css
:root {
  --primary-color: #00c851;        /* 주요 색상 */
  --primary-dark: #00a844;         /* 주요 색상 (어두운 버전) */
  --text-primary: #333333;         /* 주요 텍스트 색상 */
  --text-secondary: #666666;       /* 보조 텍스트 색상 */
  --text-light: #999999;           /* 밝은 텍스트 색상 */
  --border-color: #e0e0e0;         /* 테두리 색상 */
  --background-secondary: #f5f5f5; /* 보조 배경 색상 */
}
```

### 애니메이션

모든 모달은 `framer-motion`을 사용하여 부드러운 애니메이션을 제공합니다:

```jsx
const modalVariants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 }
};
```

## 🔌 API 엔드포인트

### 지원자 관련
- `GET /api/applicants` - 지원자 목록 조회
- `POST /api/applicants` - 새 지원자 등록
- `GET /api/applicants/:id` - 지원자 상세 조회

### 문서 관련
- `GET /api/applicants/:id/resume` - 이력서 조회
- `GET /api/applicants/:id/cover-letter` - 자소서 조회
- `GET /api/applicants/:id/portfolio` - 포트폴리오 조회

### 분석 관련
- `POST /api/applicants/ranking` - 지원자 랭킹 계산
- `GET /api/coverletter/similarity-check/:id` - 자소서 유사도 체크

## 🧪 테스트

### 단위 테스트
각 모달 컴포넌트의 독립적 동작을 테스트합니다.

### 통합 테스트
모달 간 상호작용과 데이터 흐름을 테스트합니다.

## 🔒 보안 고려사항

- 파일 업로드 시 타입 검증
- 사용자 입력 데이터 이스케이프 처리
- API 요청 시 적절한 인증/인가

## 📱 반응형 디자인

모든 컴포넌트는 모바일과 데스크톱 환경을 지원합니다:

```jsx
@media (max-width: 768px) {
  .grid-template-columns: 1fr;
  .modal-max-width: 95%;
  .padding: 16px;
}
```

## 🚀 성능 최적화

- React.memo를 사용한 컴포넌트 최적화
- useCallback을 사용한 함수 메모이제이션
- 조건부 렌더링으로 불필요한 DOM 생성 방지

## 🔄 마이그레이션 가이드

### 기존 코드에서 변경사항

1. **모달 상태 관리 방식 변경**
   ```jsx
   // 기존
   const [modal, setModal] = useState(null);
   
   // 새로운 방식
   const [detailModal, setDetailModal] = useState({ isOpen: false, applicant: null });
   ```

2. **모달 컴포넌트 교체**
   ```jsx
   // 기존
   <BaseModal title="지원자 상세" onClose={closeModal}>
     {/* 내용 */}
   </BaseModal>
   
   // 새로운 방식
   <ApplicantManagementModals
     detailModal={detailModal}
     onDetailModalClose={handleDetailModalClose}
     // ... 기타 props
   />
   ```

## 📚 추가 리소스

- [React Hooks 가이드](https://reactjs.org/docs/hooks-intro.html)
- [styled-components 문서](https://styled-components.com/docs)
- [framer-motion 문서](https://www.framer.com/motion/)

---

이 문서는 지원자 관리 컴포넌트의 사용법과 구조를 설명합니다. 추가 질문이나 수정사항이 있으시면 언제든지 문의해 주세요.

