/**
 * 자소서 분석 모듈
 * 
 * 이 모듈은 자기소개서 분석과 관련된 모든 기능을 포함합니다:
 * - 파일 업로드 및 분석
 * - 분석 결과 표시
 * - 결과 요약 및 통계
 * - CSV 내보내기
 * - 공유 기능
 */

// 메인 페이지 컴포넌트
export { default as CoverLetterAnalysisPage } from '../../pages/CoverLetterAnalysisPage';

// 핵심 컴포넌트들
export { default as CoverLetterAnalysis } from '../../components/CoverLetterAnalysis';
export { default as CoverLetterAnalysisResult } from '../../components/CoverLetterAnalysisResult';

// 유틸리티 함수들
export {
  extractSkillsFromCoverLetter,
  extractExperienceFromCoverLetter,
  extractEducationFromCoverLetter,
  extractRecommendationsFromCoverLetter,
  getCoverLetterScoreColor,
  getCoverLetterScoreIcon,
  getCoverLetterItemName,
  generateCoverLetterSummary,
  exportCoverLetterAnalysisToCSV
} from '../../utils/coverLetterUtils';

// 모듈 정보
export const MODULE_INFO = {
  name: '자기소개서 분석',
  version: '1.0.0',
  description: 'AI 기반 자기소개서 분석 및 피드백 시스템',
  features: [
    '자기소개서 파일 업로드 (PDF, Word, TXT)',
    'AI 기반 자동 분석',
    '상세한 피드백 및 점수 제공',
    '강점 및 개선점 분석',
    '결과 요약 및 통계',
    'CSV 내보내기',
    '결과 공유 기능'
  ],
  supportedFormats: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ],
  maxFileSize: '10MB',
  analysisCategories: [
    '직무 이해도',
    '독특한 경험',
    '키워드 다양성',
    '동기 명확성',
    '작성 품질',
    '경력 일치도',
    '회사 조사',
    '미래 비전',
    '소통 스타일'
  ]
};
