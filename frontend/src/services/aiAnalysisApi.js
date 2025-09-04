/**
 * AI 이력서 분석 API 서비스
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * 이력서 AI 분석 실행
 * @param {string} applicantId - 지원자 ID
 * @param {string} analysisType - 분석 타입 (openai, huggingface)
 * @param {boolean} forceReanalysis - 강제 재분석 여부
 * @param {Object} weights - 분석 가중치 설정
 * @returns {Promise<Object>} 분석 결과
 */
export const analyzeResume = async (applicantId, analysisType = 'openai', forceReanalysis = false, weights = null) => {
  try {
    // 로컬 스토리지에서 가중치 가져오기
    const savedWeights = localStorage.getItem('analysisWeights');
    let analysisWeights = weights;

    if (!analysisWeights && savedWeights) {
      try {
        analysisWeights = JSON.parse(savedWeights);
      } catch (error) {
        console.error('가중치 파싱 실패:', error);
      }
    }

    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_id: applicantId,
        analysis_type: analysisType,
        force_reanalysis: forceReanalysis,
        weights: analysisWeights
      }),
    });

    if (!response.ok) {
      throw new Error('이력서 분석에 실패했습니다');
    }

    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message || '이력서 분석에 실패했습니다');
    }
  } catch (error) {
    console.error('이력서 분석 오류:', error);
    throw error;
  }
};

/**
 * 이력서 일괄 AI 분석
 * @param {Array<string>} applicantIds - 지원자 ID 리스트
 * @param {string} analysisType - 분석 타입
 * @returns {Promise<Object>} 일괄 분석 결과
 */
export const batchAnalyzeResumes = async (applicantIds, analysisType = 'openai') => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/batch-analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_ids: applicantIds,
        analysis_type: analysisType
      }),
    });

    if (!response.ok) {
      throw new Error('일괄 분석에 실패했습니다');
    }

    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message || '일괄 분석에 실패했습니다');
    }
  } catch (error) {
    console.error('일괄 분석 오류:', error);
    throw error;
  }
};

/**
 * 이력서 재분석
 * @param {string} applicantId - 지원자 ID
 * @param {string} analysisType - 분석 타입
 * @returns {Promise<Object>} 재분석 결과
 */
export const reanalyzeResume = async (applicantId, analysisType = 'openai') => {
  try {
    // 로컬 스토리지에서 가중치 가져오기
    const savedWeights = localStorage.getItem('analysisWeights');
    let analysisWeights = null;

    if (savedWeights) {
      try {
        analysisWeights = JSON.parse(savedWeights);
      } catch (error) {
        console.error('가중치 파싱 실패:', error);
      }
    }

    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/reanalyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_id: applicantId,
        analysis_type: analysisType,
        weights: analysisWeights
      }),
    });

    if (!response.ok) {
      throw new Error('재분석에 실패했습니다');
    }

    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message || '재분석에 실패했습니다');
    }
  } catch (error) {
    console.error('재분석 오류:', error);
    throw error;
  }
};

/**
 * AI 분석 상태 조회
 * @returns {Promise<Object>} 분석 상태 정보
 */
export const getAnalysisStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/analysis-status`);

    if (!response.ok) {
      throw new Error('분석 상태 조회에 실패했습니다');
    }

    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message || '분석 상태 조회에 실패했습니다');
    }
  } catch (error) {
    console.error('분석 상태 조회 오류:', error);
    throw error;
  }
};

/**
 * 지원자별 AI 분석 결과 조회
 * @param {string} applicantId - 지원자 ID
 * @returns {Promise<Object>} AI 분석 결과
 */
export const getApplicantAnalysis = async (applicantId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/${applicantId}`);

    if (!response.ok) {
      if (response.status === 404) {
        return null; // 분석 결과가 없는 경우
      }
      throw new Error('AI 분석 결과 조회에 실패했습니다');
    }

    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message || 'AI 분석 결과 조회에 실패했습니다');
    }
  } catch (error) {
    console.error('AI 분석 결과 조회 오류:', error);
    throw error;
  }
};

/**
 * 분석 진행률 계산
 * @param {Object} statusData - 분석 상태 데이터
 * @returns {Object} 진행률 정보
 */
export const calculateAnalysisProgress = (statusData) => {
  if (!statusData) return { percentage: 0, status: 'unknown' };

  const { total_applicants, analyzed_count, pending_count, failed_count } = statusData;

  if (total_applicants === 0) return { percentage: 0, status: 'no_applicants' };

  const percentage = Math.round((analyzed_count / total_applicants) * 100);

  let status = 'in_progress';
  if (percentage === 100) {
    status = 'completed';
  } else if (percentage === 0) {
    status = 'not_started';
  } else if (failed_count > 0 && failed_count === total_applicants) {
    status = 'failed';
  }

  return {
    percentage,
    status,
    total: total_applicants,
    analyzed: analyzed_count,
    pending: pending_count,
    failed: failed_count
  };
};

/**
 * 분석 점수 등급 계산
 * @param {number} score - 분석 점수 (0-100)
 * @returns {Object} 등급 정보
 */
export const calculateScoreGrade = (score) => {
  if (score >= 90) {
    return { grade: 'A+', label: '우수', color: '#28a745', icon: '🏆' };
  } else if (score >= 80) {
    return { grade: 'A', label: '우수', color: '#28a745', icon: '⭐' };
  } else if (score >= 70) {
    return { grade: 'B+', label: '양호', color: '#17a2b8', icon: '👍' };
  } else if (score >= 60) {
    return { grade: 'B', label: '양호', color: '#17a2b8', icon: '👍' };
  } else if (score >= 50) {
    return { grade: 'C+', label: '보통', color: '#ffc107', icon: '➖' };
  } else if (score >= 40) {
    return { grade: 'C', label: '보통', color: '#ffc107', icon: '➖' };
  } else {
    return { grade: 'D', label: '미흡', color: '#dc3545', icon: '⚠️' };
  }
};

/**
 * 분석 결과 요약 생성 (새로운 형식 지원)
 * @param {Object} analysisResult - AI 분석 결과
 * @returns {Object} 요약 정보
 */
export const generateAnalysisSummary = (analysisResult) => {
  if (!analysisResult) {
    return null;
  }

  // 새로운 형식과 기존 형식 모두 지원
  let result;
  if (analysisResult.analysis_result) {
    result = analysisResult.analysis_result;
  } else if (analysisResult.evaluation_weights) {
    // 새로운 형식 (직접 접근)
    result = analysisResult;
  } else {
    return null;
  }

  // 점수별 등급 계산
  const overallGrade = calculateScoreGrade(result.analysis_result?.overall_score || result.overall_score);
  const educationGrade = calculateScoreGrade(result.analysis_result?.education_score || result.education_score);
  const experienceGrade = calculateScoreGrade(result.analysis_result?.experience_score || result.experience_score);
  const skillsGrade = calculateScoreGrade(result.analysis_result?.skills_score || result.skills_score);
  const projectsGrade = calculateScoreGrade(result.analysis_result?.projects_score || result.projects_score);
  const growthGrade = calculateScoreGrade(result.analysis_result?.growth_score || result.growth_score);

  // 추가 점수 (HuggingFace 분석기인 경우)
  let grammarGrade = null;
  let jobMatchingGrade = null;

  if (result.grammar_score !== undefined) {
    grammarGrade = calculateScoreGrade(result.grammar_score);
  }

  if (result.job_matching_score !== undefined) {
    jobMatchingGrade = calculateScoreGrade(result.job_matching_score);
  }

  // 새로운 형식의 권장사항 처리
  let recommendations = [];
  const recommendationsData = result.analysis_result?.recommendations || result.recommendations;
  if (recommendationsData) {
    if (Array.isArray(recommendationsData) && recommendationsData.length > 0) {
      // 새로운 형식: Recommendation 객체 배열
      if (typeof recommendationsData[0] === 'object' && recommendationsData[0].action) {
        recommendations = recommendationsData.map(rec => rec.action);
      } else {
        // 기존 형식: 문자열 배열
        recommendations = recommendationsData;
      }
    }
  }

    // 하이라이트 처리를 위한 함수 (React 컴포넌트용)
  const addHighlights = (text) => {
    if (!text) return text;

    // 하이라이트 패턴 정의
    const patterns = [
      // 점수 하이라이트
      { pattern: /(\d+점)/g, style: { color: '#28a745', backgroundColor: '#d4edda', padding: '2px 4px', borderRadius: '3px', fontWeight: 'bold' } },
      // 긍정 키워드
      { pattern: /(우수|매우 좋음|훌륭함|뛰어남|훌륭한|우수한)/g, style: { color: '#28a745', fontWeight: '600' } },
      // 부정 키워드
      { pattern: /(부족|개선|보완|필요|부족한|개선이 필요한)/g, style: { color: '#dc3545', fontWeight: '600' } },
      // 강점 관련
      { pattern: /(강점|장점|좋은 점|우수한 점)/g, style: { color: '#28a745', fontWeight: '600' } },
      // 약점 관련
      { pattern: /(약점|단점|개선점|부족한 점)/g, style: { color: '#dc3545', fontWeight: '600' } },
      // 기술 스택
      { pattern: /(React|Vue|Angular|Node\.js|Python|Java|JavaScript|TypeScript|Spring|Django|Flask|MongoDB|MySQL|PostgreSQL|AWS|Docker|Kubernetes)/g, style: { backgroundColor: '#fff3cd', color: '#856404', padding: '1px 3px', borderRadius: '2px', fontWeight: '500' } },
      // 프로젝트 관련
      { pattern: /(프로젝트|개발|구현|설계|배포|시스템|애플리케이션)/g, style: { backgroundColor: '#d1ecf1', color: '#0c5460', padding: '1px 3px', borderRadius: '2px' } }
    ];

    // 패턴을 적용하여 하이라이트된 텍스트 생성
    let highlightedText = text;
    patterns.forEach(({ pattern, style }) => {
      highlightedText = highlightedText.replace(pattern, (match) => {
        const styleString = Object.entries(style)
          .map(([key, value]) => `${key.replace(/([A-Z])/g, '-$1').toLowerCase()}: ${value}`)
          .join('; ');
        return `<span style="${styleString}">${match}</span>`;
      });
    });

    return highlightedText;
  };

  return {
    overall: {
      score: result.analysis_result?.overall_score || result.overall_score,
      grade: overallGrade
    },
    categories: {
      education: { score: result.analysis_result?.education_score || result.education_score, grade: educationGrade },
      experience: { score: result.analysis_result?.experience_score || result.experience_score, grade: experienceGrade },
      skills: { score: result.analysis_result?.skills_score || result.skills_score, grade: skillsGrade },
      projects: { score: result.analysis_result?.projects_score || result.projects_score, grade: projectsGrade },
      growth: { score: result.analysis_result?.growth_score || result.growth_score, grade: growthGrade }
    },
    additional: {
      grammar: grammarGrade,
      jobMatching: jobMatchingGrade
    },
    feedback: {
      strengths: ((result.analysis_result?.strengths || result.strengths) || []).map(addHighlights),
      improvements: ((result.analysis_result?.improvements || result.improvements) || []).map(addHighlights),
      recommendations: recommendations.map(addHighlights),
      overallFeedback: addHighlights(result.analysis_result?.overall_feedback || result.overall_feedback || '')
    },
    // 새로운 형식의 추가 정보
    evaluationWeights: result.evaluation_weights || null,
    analysisNotes: result.analysis_notes || null,
    detailedRecommendations: result.analysis_result?.recommendations || result.recommendations || [],
    analysisType: analysisResult.analysis_type || 'unknown',
    createdAt: analysisResult.created_at || new Date().toISOString()
  };
};

export default {
  analyzeResume,
  batchAnalyzeResumes,
  reanalyzeResume,
  getAnalysisStatus,
  getApplicantAnalysis,
  calculateAnalysisProgress,
  calculateScoreGrade,
  generateAnalysisSummary
};
