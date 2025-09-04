/**
 * 자소서 분석 관련 커스텀 훅
 */

import { useState, useEffect, useCallback } from 'react';
import CoverLetterAnalysisApi from '../services/coverLetterAnalysisApi';
import { calculateOverallScore, normalizeAnalysisData, generateRecommendations } from '../utils/analysisHelpers';

/**
 * 자소서 분석 훅
 * @param {string} applicantId - 지원자 ID
 * @returns {Object} 분석 관련 상태와 함수들
 */
export const useCoverLetterAnalysis = (applicantId) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [overallScore, setOverallScore] = useState(0);
  const [recommendations, setRecommendations] = useState([]);

  // 분석 데이터 정규화 및 점수 계산
  useEffect(() => {
    if (analysisData) {
      const normalizedData = normalizeAnalysisData(analysisData);
      const score = calculateOverallScore(analysisData);
      const recs = generateRecommendations(analysisData);

      setOverallScore(score);
      setRecommendations(recs);
    }
  }, [analysisData]);

  // 자소서 분석 수행
  const performAnalysis = useCallback(async (file, jobDescription = '', analysisType = 'comprehensive') => {
    if (!file) {
      setError('분석할 파일을 선택해주세요.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await CoverLetterAnalysisApi.analyzeCoverLetter(file, jobDescription, analysisType);
      setAnalysisData(result);
      return result;
    } catch (err) {
      setError(err.message || '자소서 분석에 실패했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 지원자 자소서 분석
  const analyzeApplicantCoverLetter = useCallback(async (analysisRequest = {}) => {
    if (!applicantId) {
      setError('지원자 ID가 필요합니다.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await CoverLetterAnalysisApi.analyzeApplicantCoverLetter(applicantId, analysisRequest);
      setAnalysisData(result);
      return result;
    } catch (err) {
      setError(err.message || '지원자 자소서 분석에 실패했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [applicantId]);

  // 분석 결과 조회
  const getAnalysisResult = useCallback(async (analysisId) => {
    if (!analysisId) {
      setError('분석 ID가 필요합니다.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await CoverLetterAnalysisApi.getAnalysisResult(analysisId);
      setAnalysisData(result);
      return result;
    } catch (err) {
      setError(err.message || '분석 결과 조회에 실패했습니다.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 분석 상태 확인
  const getAnalysisStatus = useCallback(async (analysisId) => {
    if (!analysisId) {
      setError('분석 ID가 필요합니다.');
      return;
    }

    try {
      const result = await CoverLetterAnalysisApi.getAnalysisStatus(analysisId);
      return result;
    } catch (err) {
      setError(err.message || '분석 상태 확인에 실패했습니다.');
      throw err;
    }
  }, []);

  // 분석 데이터 초기화
  const resetAnalysis = useCallback(() => {
    setAnalysisData(null);
    setOverallScore(0);
    setRecommendations([]);
    setError(null);
  }, []);

  return {
    // 상태
    analysisData,
    isLoading,
    error,
    overallScore,
    recommendations,

    // 함수
    performAnalysis,
    analyzeApplicantCoverLetter,
    getAnalysisResult,
    getAnalysisStatus,
    resetAnalysis
  };
};

export default useCoverLetterAnalysis;
