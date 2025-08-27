# Applicants 페이지 게시판 스타일 분석 및 정리

## 개요
이 문서는 `frontend/src/pages/ApplicantManagement.js` 파일의 게시판 뷰 스타일 관련 정보를 정리한 것입니다. 게시판 버튼을 눌렀을 때 표시되는 리스트 스타일의 문제점을 파악하고 해결하기 위한 참고 자료입니다.

## 파일 위치
- **메인 파일**: `frontend/src/pages/ApplicantManagement.js`
- **스타일 관련**: `frontend/src/index.css` (CSS 변수 정의)

## 게시판 뷰 관련 주요 컴포넌트

### 1. 뷰 모드 전환
```javascript
// 뷰 모드 상태 관리
const [viewMode, setViewMode] = useState('grid');

// 뷰 모드 변경 핸들러
const handleViewModeChange = (mode) => {
  setViewMode(mode);
};
```

### 2. 게시판 헤더 스타일 컴포넌트

#### HeaderRowBoard (게시판 헤더 행)
```javascript
const HeaderRowBoard = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: var(--background-secondary);
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 11px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  height: 36px;
  gap: 16px;
`;
```

#### 헤더 컬럼 스타일들
- **HeaderCheckbox**: 체크박스 컬럼 (min-width: 32px)
- **HeaderName**: 이름 컬럼 (min-width: 120px)
- **HeaderPosition**: 직무 컬럼 (min-width: 120px)
- **HeaderEmail**: 이메일 컬럼 (min-width: 180px)
- **HeaderPhone**: 전화번호 컬럼 (min-width: 120px)
- **HeaderSkills**: 기술스택 컬럼 (min-width: 120px)
- **HeaderDate**: 지원일 컬럼 (min-width: 90px)
- **HeaderScore**: 총점 컬럼 (min-width: 80px)
- **HeaderActions**: 상태 컬럼 (min-width: 100px)

### 3. 게시판 카드 스타일 컴포넌트

#### ApplicantsBoard (게시판 컨테이너)
```javascript
const ApplicantsBoard = styled.div.attrs({
  id: 'applicant-management-applicants-board'
})`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;
```

#### ApplicantCardBoard (게시판 카드)
```javascript
const ApplicantCardBoard = styled(motion.div).attrs({
  id: 'applicant-management-applicant-card-board'
})`
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
  height: 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;
```

### 4. 게시판 내부 요소 스타일

#### ApplicantHeaderBoard (게시판 카드 헤더)
```javascript
const ApplicantHeaderBoard = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
`;
```

#### 게시판 전용 스타일 컴포넌트들
- **ApplicantNameBoard**: 이름 표시 (min-width: 120px, 중앙 정렬)
- **ApplicantPositionBoard**: 직무 표시 (min-width: 120px, 중앙 정렬)
- **ApplicantEmailBoard**: 이메일 표시 (min-width: 180px, 중앙 정렬)
- **ApplicantPhoneBoard**: 전화번호 표시 (min-width: 120px, 중앙 정렬)
- **ApplicantSkillsBoard**: 기술스택 표시 (min-width: 120px, 중앙 정렬)
- **ApplicantDateBoard**: 지원일 표시 (min-width: 90px, 중앙 정렬)
- **ApplicantScoreBoard**: 총점 표시 (min-width: 80px, 중앙 정렬)

### 5. 특수 요소 스타일

#### ContactItem (연락처 아이템)
```javascript
const ContactItem = styled.div`
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  color: var(--text-secondary);
  justify-content: center;
`;
```

#### SkillTagBoard (기술스택 태그)
```javascript
const SkillTagBoard = styled.span`
  padding: 1px 4px;
  background: var(--background-secondary);
  border-radius: 4px;
  font-size: 9px;
  color: var(--text-secondary);
`;
```

#### ScoreBadge (점수 배지)
```javascript
const ScoreBadge = styled.span`
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    if (props.score >= 90) return '#22c55e'; // 녹색 (90점 이상)
    if (props.score >= 80) return '#eab308'; // 주황색 (80-89점)
    if (props.score >= 70) return '#3b82f6'; // 파란색 (70-79점)
    return '#6b7280'; // 회색 (70점 미만)
  }};
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }
`;
```

#### BoardRankBadge (게시판 순위 배지)
```javascript
const BoardRankBadge = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: white;
  margin-right: 8px;
  background: ${props => {
    if (props.rank === 1) return '#ef4444'; // 빨간색 (1위)
    if (props.rank === 2) return '#f59e0b'; // 주황색 (2위)
    if (props.rank === 3) return '#10b981'; // 초록색 (3위)
    if (props.rank <= 10) return '#3b82f6'; // 파란색 (4-10위)
    return '#6b7280'; // 회색 (11위 이상)
  }};

  &::before {
    content: '${props => {
      if (props.rank === 1) return '🥇';
      if (props.rank === 2) return '🥈';
      if (props.rank === 3) return '🥉';
      return props.rank.toString();
    }}';
  }
`;
```

## CSS 변수 정의

### 기본 색상 변수 (`frontend/src/index.css`)
```css
:root {
  --primary-color: #00c851;
  --text-primary: #333;
  --text-secondary: #666;
  --background-secondary: #f8f9fa;
  --border-color: #e9ecef;
}
```

## 게시판 렌더링 로직

### 조건부 렌더링
```javascript
{viewMode === 'board' && (
  <>
    {/* 게시판 헤더 */}
    <HeaderRowBoard>
      <HeaderCheckbox>
        <CheckboxInput
          type="checkbox"
          checked={selectAll}
          onChange={handleSelectAll}
        />
      </HeaderCheckbox>
      <HeaderName>이름</HeaderName>
      <HeaderPosition>직무</HeaderPosition>
      <HeaderEmail>이메일</HeaderEmail>
      <HeaderPhone>전화번호</HeaderPhone>
      <HeaderSkills>기술스택</HeaderSkills>
      <HeaderDate>지원일</HeaderDate>
      <HeaderScore>총점</HeaderScore>
      <HeaderActions>상태</HeaderActions>
    </HeaderRowBoard>
  </>
)}

{viewMode === 'grid' ? (
  <ApplicantsGrid viewMode={viewMode}>
    {/* 그리드 뷰 렌더링 */}
  </ApplicantsGrid>
) : (
  <ApplicantsBoard>
    {/* 게시판 뷰 렌더링 */}
    {paginatedApplicants.map((applicant, index) => (
      <ApplicantCardBoard
        key={applicant.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05, duration: 0.1 }}
        onClick={() => handleCardClick(applicant)}
        onMouseEnter={() => setHoveredApplicant(applicant.id)}
        onMouseLeave={() => setHoveredApplicant(null)}
      >
        <ApplicantHeaderBoard>
          {/* 게시판 카드 내용 */}
        </ApplicantHeaderBoard>
      </ApplicantCardBoard>
    ))}
  </ApplicantsBoard>
)}
```

## 주요 특징

### 1. 레이아웃 구조
- **Flexbox 기반**: 모든 게시판 요소가 flexbox를 사용하여 정렬
- **고정 높이**: 카드 높이가 56px로 고정
- **중앙 정렬**: 모든 컬럼 내용이 중앙 정렬됨

### 2. 반응형 디자인
- **min-width 설정**: 각 컬럼에 최소 너비 설정으로 레이아웃 유지
- **flex-shrink: 0**: 컬럼이 축소되지 않도록 설정

### 3. 애니메이션 효과
- **Framer Motion**: 카드 등장 시 애니메이션 효과
- **Hover 효과**: 마우스 오버 시 카드 상승 효과

### 4. 상태 관리
- **체크박스**: 개별 선택 및 전체 선택 기능
- **상태 배지**: 지원자 상태를 색상으로 구분
- **순위 표시**: 상위 3명에게 메달 아이콘 표시

## 문제점 분석

### 1. 레이아웃 깨짐 가능성
- **고정 높이**: 56px 고정 높이로 인한 내용 오버플로우
- **텍스트 길이**: 긴 텍스트가 컬럼 너비를 초과할 수 있음
- **반응형 대응 부족**: 작은 화면에서 레이아웃 깨짐

### 2. 스타일 일관성
- **폰트 크기**: 매우 작은 폰트 크기 (9px-12px)
- **색상 대비**: 작은 텍스트의 가독성 문제
- **간격 조정**: 컬럼 간 간격이 일정하지 않을 수 있음

## 개선 방안

### 1. 레이아웃 개선
- **동적 높이**: 내용에 따른 높이 조정
- **텍스트 말줄임**: 긴 텍스트에 ellipsis 적용
- **반응형 그리드**: 화면 크기에 따른 컬럼 조정

### 2. 가독성 향상
- **폰트 크기 증가**: 최소 12px 이상으로 조정
- **색상 대비 개선**: 더 명확한 색상 대비
- **여백 조정**: 적절한 패딩과 마진 설정

### 3. 사용성 개선
- **툴팁 추가**: 잘린 텍스트에 대한 툴팁
- **정렬 옵션**: 컬럼별 정렬 기능
- **필터링**: 실시간 필터링 기능

## 관련 파일들

1. **메인 컴포넌트**: `frontend/src/pages/ApplicantManagement.js`
2. **스타일 파일**: `frontend/src/index.css`
3. **API 서비스**: `frontend/src/services/jobPostingApi.js`
4. **모달 컴포넌트들**:
   - `frontend/src/components/DetailedAnalysisModal.js`
   - `frontend/src/components/ResumeModal.js`
   - `frontend/src/components/CoverLetterSummary.js`

## 참고 사항

- 모든 스타일은 styled-components를 사용하여 정의됨
- Framer Motion을 사용한 애니메이션 효과 포함
- CSS 변수를 통한 일관된 색상 관리
- 반응형 디자인을 위한 미디어 쿼리 고려 필요
