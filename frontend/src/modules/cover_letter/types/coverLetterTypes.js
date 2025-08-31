/**
 * 자소서 관련 타입 정의
 */

// 자소서 기본 정보
export const CoverLetterInfo = {
  id: String,
  name: String,
  position: String,
  submittedDate: String,
  wordCount: Number,
  content: String,
  filePath: String,
  applicantId: String
};

// 자소서 분석 결과
export const CoverLetterAnalysisResult = {
  overallScore: Number,
  analyzedAt: String,
  analysisResult: {
    motivation_relevance: {
      score: Number,
      feedback: String
    },
    technical_suitability: {
      score: Number,
      feedback: String
    },
    job_understanding: {
      score: Number,
      feedback: String
    },
    growth_potential: {
      score: Number,
      feedback: String
    },
    teamwork_communication: {
      score: Number,
      feedback: String
    }
  },
  recommendations: Array,
  detailedAnalysis: String
};

// 자소서 검증 결과
export const CoverLetterValidationResult = {
  validationScore: Number,
  originality: Number,
  coherence: Number,
  grammar: Number,
  plagiarism: Number,
  contentStructure: Number,
  keywordMatch: Number,
  jobRelevance: Number,
  writingQuality: Number,
  analysis: String,
  issues: Array,
  keywords: {
    required: Array,
    matched: Array,
    total: Number,
    matchedCount: Number
  },
  plagiarismDetails: {
    score: Number,
    status: String,
    description: String
  }
};

// 표절 의심도 결과
export const PlagiarismSuspicionResult = {
  suspicionLevel: String, // 'LOW', 'MEDIUM', 'HIGH'
  suspicionScore: Number,
  similarCount: Number,
  analysis: String,
  similarDocuments: Array
};

// 분석 요청 파라미터
export const AnalysisRequest = {
  file: File,
  jobDescription: String,
  analysisType: String, // 'comprehensive', 'basic', 'detailed'
  applicantId: String
};

// 차트 데이터
export const ChartData = {
  labels: Array,
  data: Array,
  colors: Array
};

// 분석 항목 라벨 매핑
export const ANALYSIS_LABELS = {
  motivation_relevance: '지원 동기',
  technical_suitability: '기술적 적합성',
  job_understanding: '직무 이해도',
  growth_potential: '성장 가능성',
  teamwork_communication: '팀워크 및 소통',
  problem_solving_STAR: 'STAR 기법',
  quantitative_impact: '정량적 성과',
  unique_experience: '차별화 경험',
  logical_flow: '논리적 흐름',
  keyword_diversity: '키워드 다양성',
  sentence_readability: '문장 가독성',
  typos_and_errors: '오탈자'
};

// 점수 등급
export const SCORE_GRADES = {
  EXCELLENT: { min: 8, max: 10, label: '우수', color: '#28a745' },
  GOOD: { min: 6, max: 7.9, label: '양호', color: '#17a2b8' },
  AVERAGE: { min: 4, max: 5.9, label: '보통', color: '#ffc107' },
  POOR: { min: 0, max: 3.9, label: '개선필요', color: '#dc3545' }
};

// 표절 의심도 레벨
export const SUSPICION_LEVELS = {
  LOW: { label: '낮음', color: '#16a34a', bgColor: '#f0fdf4' },
  MEDIUM: { label: '보통', color: '#f59e0b', bgColor: '#fffbeb' },
  HIGH: { label: '높음', color: '#dc2626', bgColor: '#fef2f2' }
};
