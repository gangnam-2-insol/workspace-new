/**
 * AI 이력서 분석 API 서비스
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * 이력서 AI 분석 실행
 * @param {string} applicantId - 지원자 ID
 * @param {string} analysisType - 분석 타입 (openai, huggingface)
 * @param {boolean} forceReanalysis - 강제 재분석 여부
 * @returns {Promise<Object>} 분석 결과
 */
export const analyzeResume = async (applicantId, analysisType = 'openai', forceReanalysis = false) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_id: applicantId,
        analysis_type: analysisType,
        force_reanalysis: forceReanalysis
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
    const response = await fetch(`${API_BASE_URL}/api/ai-analysis/resume/reanalyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        applicant_id: applicantId,
        analysis_type: analysisType
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
 * 분석 결과 요약 생성
 * @param {Object} analysisResult - AI 분석 결과
 * @returns {Object} 요약 정보
 */
export const generateAnalysisSummary = (analysisResult) => {
  if (!analysisResult || !analysisResult.analysis_result) {
    return null;
  }

  const result = analysisResult.analysis_result;
  
  // 점수별 등급 계산
  const overallGrade = calculateScoreGrade(result.overall_score);
  const educationGrade = calculateScoreGrade(result.education_score);
  const experienceGrade = calculateScoreGrade(result.experience_score);
  const skillsGrade = calculateScoreGrade(result.skills_score);
  const projectsGrade = calculateScoreGrade(result.projects_score);
  const growthGrade = calculateScoreGrade(result.growth_score);
  
  // 추가 점수 (HuggingFace 분석기인 경우)
  let grammarGrade = null;
  let jobMatchingGrade = null;
  
  if (result.grammar_score !== undefined) {
    grammarGrade = calculateScoreGrade(result.grammar_score);
  }
  
  if (result.job_matching_score !== undefined) {
    jobMatchingGrade = calculateScoreGrade(result.job_matching_score);
  }
  
  return {
    overall: {
      score: result.overall_score,
      grade: overallGrade
    },
    categories: {
      education: { score: result.education_score, grade: educationGrade },
      experience: { score: result.experience_score, grade: experienceGrade },
      skills: { score: result.skills_score, grade: skillsGrade },
      projects: { score: result.projects_score, grade: projectsGrade },
      growth: { score: result.growth_score, grade: growthGrade }
    },
    additional: {
      grammar: grammarGrade,
      jobMatching: jobMatchingGrade
    },
    feedback: {
      strengths: result.strengths || [],
      improvements: result.improvements || [],
      recommendations: result.recommendations || [],
      overallFeedback: result.overall_feedback || ''
    },
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
