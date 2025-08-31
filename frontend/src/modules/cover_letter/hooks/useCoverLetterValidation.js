/**
 * 자소서 검증 관련 커스텀 훅
 */

import { useState, useEffect, useCallback } from 'react';
import { validateLength, analyzeStructure, checkGrammarErrors, calculateValidationScore } from '../utils/validationHelpers';

/**
 * 자소서 검증 훅
 * @param {string} content - 자소서 내용
 * @param {string} position - 지원 직무
 * @param {Array} keywords - 필수 키워드
 * @returns {Object} 검증 관련 상태와 함수들
 */
export const useCoverLetterValidation = (content, position = '', keywords = []) => {
  const [validationData, setValidationData] = useState(null);
  const [validationScore, setValidationScore] = useState(0);
  const [issues, setIssues] = useState([]);
  const [isValidating, setIsValidating] = useState(false);

  // 자소서 검증 수행
  const performValidation = useCallback(async () => {
    if (!content || content.trim().length === 0) {
      setValidationData(null);
      setValidationScore(0);
      setIssues([]);
      return;
    }

    setIsValidating(true);

    try {
      // 길이 검증
      const lengthValidation = validateLength(content, position);

      // 구조 분석
      const structure = analyzeStructure(content);

      // 문법 오류 검사
      const grammarErrors = checkGrammarErrors(content);

      // 키워드 분석
      const keywordAnalysis = {
        total: keywords.length,
        matched: keywords.filter(keyword =>
          content.toLowerCase().includes(keyword.toLowerCase())
        ).length,
        matchRate: keywords.length > 0
          ? Math.round((keywords.filter(keyword =>
              content.toLowerCase().includes(keyword.toLowerCase())
            ).length / keywords.length) * 100)
          : 100
      };

      // 표절 의심도 (임시로 낮음으로 설정)
      const plagiarismScore = Math.random() * 20; // 0-20 사이의 랜덤 값

      const validationResult = {
        wordCount: lengthValidation.wordCount,
        charCount: lengthValidation.charCount,
        lengthStatus: lengthValidation.status,
        structure,
        grammarErrors,
        keywordAnalysis,
        plagiarismScore,
        suspicionLevel: plagiarismScore < 10 ? 'LOW' : plagiarismScore < 20 ? 'MEDIUM' : 'HIGH'
      };

      setValidationData(validationResult);

      // 종합 점수 계산
      const score = calculateValidationScore(validationResult);
      setValidationScore(score);

      // 이슈 목록 생성
      const issueList = [];

      if (lengthValidation.status !== 'good') {
        issueList.push({
          type: 'length',
          severity: lengthValidation.status === 'short' ? 'high' : 'medium',
          message: lengthValidation.message
        });
      }

      grammarErrors.forEach(error => {
        issueList.push({
          type: 'grammar',
          severity: error.severity,
          message: error.message
        });
      });

      if (keywordAnalysis.matchRate < 50) {
        issueList.push({
          type: 'keywords',
          severity: 'medium',
          message: `필수 키워드 매칭률이 낮습니다. (${keywordAnalysis.matchRate}%)`
        });
      }

      if (plagiarismScore > 15) {
        issueList.push({
          type: 'plagiarism',
          severity: 'high',
          message: '표절 의심도가 높습니다.'
        });
      }

      setIssues(issueList);

    } catch (error) {
      console.error('자소서 검증 오류:', error);
      setIssues([{
        type: 'error',
        severity: 'high',
        message: '검증 중 오류가 발생했습니다.'
      }]);
    } finally {
      setIsValidating(false);
    }
  }, [content, position, keywords]);

  // 내용이 변경될 때마다 검증 수행
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performValidation();
    }, 500); // 500ms 디바운스

    return () => clearTimeout(timeoutId);
  }, [performValidation]);

  // 검증 데이터 초기화
  const resetValidation = useCallback(() => {
    setValidationData(null);
    setValidationScore(0);
    setIssues([]);
  }, []);

  return {
    // 상태
    validationData,
    validationScore,
    issues,
    isValidating,

    // 함수
    performValidation,
    resetValidation
  };
};

export default useCoverLetterValidation;
