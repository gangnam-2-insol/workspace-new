# 🤖 지원자 상세정보 모달 코드 구조

## 📋 지원자관리메뉴 → 지원자 리스트 → 상세정보 모달 → 자소서 분석 모달

### 🎯 **코드 구조 흐름**

#### **1. 지원자 관리 메인 페이지**
```
frontend/src/pages/ApplicantManagement.js
├── 지원자 리스트 렌더링
├── 지원자 카드 클릭 이벤트
└── 상세정보 모달 열기
```

#### **2. 지원자 상세정보 모달**
```
frontend/src/pages/ApplicantManagement.js
├── documentModal 상태 관리
├── handleDocumentClick 함수
└── 자소서 버튼 클릭 처리
```

#### **3. 자소서 분석 결과 모달**
```
frontend/src/components/DetailedAnalysisModal.js
├── 자소서 분석 데이터 표시
├── 분석 결과 시각화
└── 상세 분석 정보
```

### 🔧 **핵심 코드 구조**

#### **1. 지원자 리스트에서 상세정보 모달 열기**
```javascript
// frontend/src/pages/ApplicantManagement.js

const handleCardClick = (applicant) => {
  setSelectedApplicant(applicant);
  setIsModalOpen(true);
};

// 지원자 카드 렌더링
<ApplicantCard
  applicant={applicant}
  onClick={() => handleCardClick(applicant)}
/>
```

#### **2. 상세정보 모달에서 자소서 버튼 클릭**
```javascript
// frontend/src/pages/ApplicantManagement.js

const handleDocumentClick = async (type, applicant) => {
  const applicantId = applicant._id;

  if (type === 'coverLetter') {
    // 자소서 데이터 로드
    const coverLetterResponse = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`);

    if (coverLetterResponse.ok) {
      const documentData = await coverLetterResponse.json();

      // 자소서 분석 수행
      const analysisResponse = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        documentData.analysis = analysisData.analysis;
      }
    }

    // 모달 상태 업데이트
    setDocumentModal({
      isOpen: true,
      type: 'coverLetter',
      applicant: applicant,
      isOriginal: false,
      documentData: documentData
    });
  }
};

// 자소서 버튼 렌더링
<DocumentButton onClick={() => handleDocumentClick('coverLetter', applicant)}>
  자소서
</DocumentButton>
```

#### **3. 자소서 분석 결과 모달**
```javascript
// frontend/src/components/DetailedAnalysisModal.js

const DetailedAnalysisModal = ({ isOpen, onClose, applicantData }) => {
  // 분석 데이터 추출
  const analysisData = applicantData.analysis_result || applicantData.analysis || {};
  const coverLetterAnalysis = analysisData.cover_letter_analysis || {};

  // 전체 점수 계산
  const calculateOverallScore = () => {
    const allScores = [];
    Object.values(coverLetterAnalysis).forEach(item => {
      if (item && typeof item === 'object' && 'score' in item) {
        allScores.push(item.score);
      }
    });

    if (allScores.length === 0) return 8;
    const average = allScores.reduce((sum, score) => sum + score, 0) / allScores.length;
    return Math.round(average * 10) / 10;
  };

  return (
    <ModalOverlay>
      <ModalContent>
        <Header>
          <Title>AI 상세 분석 결과</Title>
          <Subtitle>{getFileNameAndTime()}</Subtitle>
        </Header>

        <Content>
          {/* 전체 평가 점수 */}
          <OverallScore>
            <ScoreCircle>{overallScore}</ScoreCircle>
            <ScoreInfo>
              <ScoreLabel>전체 평가 점수</ScoreLabel>
              <ScoreValue>{overallScore}/10</ScoreValue>
            </ScoreInfo>
          </OverallScore>

          {/* 자소서 분석 */}
          <AnalysisSection>
            <SectionTitle>자기소개서 분석</SectionTitle>
            <AnalysisGrid>
              {Object.entries(coverLetterAnalysis).map(([key, item]) => (
                <AnalysisItem key={key} className={status}>
                  <ItemHeader>
                    <ItemTitle>{getCoverLetterAnalysisLabel(key)}</ItemTitle>
                    <ItemScore>
                      <ScoreNumber>{item.score}</ScoreNumber>
                      <ScoreMax>/10</ScoreMax>
                    </ItemScore>
                  </ItemHeader>
                  <ItemDescription>
                    {item.feedback || `${label}에 대한 분석 결과입니다.`}
                  </ItemDescription>
                </AnalysisItem>
              ))}
            </AnalysisGrid>
          </AnalysisSection>
        </Content>
      </ModalContent>
    </ModalOverlay>
  );
};
```

### 📊 **데이터 플로우**

#### **1. 지원자 리스트 → 상세정보 모달**
```
지원자 카드 클릭
↓
handleCardClick(applicant)
↓
setSelectedApplicant(applicant)
setIsModalOpen(true)
↓
상세정보 모달 렌더링
```

#### **2. 상세정보 모달 → 자소서 분석 모달**
```
자소서 버튼 클릭
↓
handleDocumentClick('coverLetter', applicant)
↓
API 호출: GET /api/applicants/{id}/cover-letter
↓
API 호출: POST /api/applicants/{id}/cover-letter/analysis
↓
setDocumentModal({ isOpen: true, type: 'coverLetter', ... })
↓
자소서 분석 모달 렌더링
```

### 🎨 **UI 컴포넌트 구조**

#### **1. 지원자 카드**
```javascript
// frontend/src/pages/ApplicantManagement.js
const ApplicantCard = ({ applicant, onClick }) => (
  <Card onClick={onClick}>
    <CardHeader>
      <ApplicantName>{applicant.name}</ApplicantName>
      <ApplicantPosition>{applicant.position}</ApplicantPosition>
    </CardHeader>
    <CardContent>
      <ApplicantEmail>{applicant.email}</ApplicantEmail>
      <ApplicantPhone>{applicant.phone}</ApplicantPhone>
    </CardContent>
  </Card>
);
```

#### **2. 상세정보 모달**
```javascript
// frontend/src/pages/ApplicantManagement.js
const DocumentModal = ({ isOpen, type, applicant, documentData }) => (
  <Modal isOpen={isOpen}>
    <ModalHeader>
      <Title>{applicant.name} - {type === 'coverLetter' ? '자소서' : '이력서'}</Title>
    </ModalHeader>

    <ModalContent>
      {/* 자소서 분석 결과 섹션 */}
      {type === 'coverLetter' && (
        <DocumentSection>
          <DocumentSectionTitle>자소서 분석 결과</DocumentSectionTitle>
          <CoverLetterAnalysis analysisData={documentData?.analysis} />
        </DocumentSection>
      )}

      {/* 유사도 체크 결과 섹션 */}
      <DocumentSection>
        <DocumentSectionTitle>🔍 유사도 체크 결과</DocumentSectionTitle>
        <SimilarityCheckResults />
      </DocumentSection>
    </ModalContent>
  </Modal>
);
```

#### **3. 자소서 분석 컴포넌트**
```javascript
// frontend/src/components/CoverLetterAnalysis.js
const CoverLetterAnalysis = ({ analysisData }) => {
  const categories = [
    { key: 'technical_suitability', label: '기술적합성', color: '#3b82f6' },
    { key: 'job_understanding', label: '직무이해도', color: '#10b981' },
    { key: 'growth_potential', label: '성장 가능성', color: '#f59e0b' },
    { key: 'teamwork_communication', label: '팀워크 및 커뮤니케이션', color: '#8b5cf6' },
    { key: 'motivation_company_fit', label: '지원동기/회사 가치관 부합도', color: '#ef4444' }
  ];

  return (
    <AnalysisContainer>
      {categories.map(category => (
        <AnalysisItem key={category.key}>
          <CategoryLabel>{category.label}</CategoryLabel>
          <ScoreBar score={analysisData[category.key]?.score || 0} />
          <Feedback>{analysisData[category.key]?.feedback || ''}</Feedback>
        </AnalysisItem>
      ))}
    </AnalysisContainer>
  );
};
```

### 🔗 **API 엔드포인트**

#### **자소서 데이터 조회**
```javascript
// GET /api/applicants/{applicant_id}/cover-letter
const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`);
const coverLetterData = await response.json();
```

#### **자소서 분석 수행**
```javascript
// POST /api/applicants/{applicant_id}/cover-letter/analysis
const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter/analysis`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
});
const analysisData = await response.json();
```

### 📁 **관련 파일 구조**

```
frontend/src/
├── pages/
│   └── ApplicantManagement.js          # 지원자 관리 메인 페이지
├── components/
│   ├── DetailedAnalysisModal.js        # 상세 분석 모달
│   ├── CoverLetterAnalysis.js          # 자소서 분석 컴포넌트
│   └── CoverLetterAnalysisModal.js     # 자소서 분석 모달
└── modules/
    └── shared/
        └── api.js                      # API 서비스
```

### 🎯 **핵심 기능**

1. **지원자 리스트에서 상세정보 모달 열기**
2. **상세정보 모달에서 자소서 버튼 클릭**
3. **자소서 데이터 로드 및 분석 수행**
4. **분석 결과 시각화 및 표시**
5. **유사도 체크 결과 표시**

이 구조를 통해 지원자 리스트 → 상세정보 모달 → 자소서 분석 모달까지의 완전한 워크플로우가 구현됩니다.

