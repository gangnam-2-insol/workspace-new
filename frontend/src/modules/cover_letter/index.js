/**
 * 자소서 모듈 메인 인덱스
 *
 * 이 모듈은 자소서 관련 모든 기능을 통합 관리합니다:
 * - 자소서 분석 및 검증
 * - 자소서 업로드 및 관리
 * - 표절 의심도 검사
 * - 분석 결과 시각화
 */

// 컴포넌트 exports
export { default as CoverLetterAnalysis } from './components/CoverLetterAnalysis';
export { default as CoverLetterAnalysisModal } from './components/CoverLetterAnalysisModal';
export { default as CoverLetterSummary } from './components/CoverLetterSummary';
export { default as CustomRadarChart } from './components/CustomRadarChart';

// 페이지 exports
export { default as CoverLetterAnalysisPage } from './pages/CoverLetterAnalysisPage';
export { default as CoverLetterValidationPage } from './pages/CoverLetterValidationPage';
export { default as CoverLetterSampleAnalysis } from './pages/CoverLetterSampleAnalysis';

// 서비스 exports
export { default as CoverLetterAnalysisApi } from './services/coverLetterAnalysisApi';

// 훅 exports
export { default as useCoverLetterAnalysis } from './hooks/useCoverLetterAnalysis';
export { default as useCoverLetterValidation } from './hooks/useCoverLetterValidation';

// 유틸리티 exports
export * from './utils/analysisHelpers';
export * from './utils/validationHelpers';
export * from './utils/chartHelpers';
export * from './utils/sampleAnalysisData';

// 타입 exports
export * from './types/coverLetterTypes';
