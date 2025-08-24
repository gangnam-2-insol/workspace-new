const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class CoverLetterAnalysisApi {
  /**
   * 자소서 파일을 업로드하고 분석을 요청합니다.
   * @param {File} file - 업로드할 자소서 파일
   * @param {string} jobDescription - 직무 설명 (선택사항)
   * @param {string} analysisType - 분석 유형 (기본값: comprehensive)
   * @returns {Promise<Object>} 분석 결과
   */
  static async analyzeCoverLetter(file, jobDescription = '', analysisType = 'comprehensive') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', jobDescription);
      formData.append('analysis_type', analysisType);

      const response = await fetch(`${API_BASE_URL}/api/cover-letters/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || '자소서 분석에 실패했습니다.');
      }

      return result.data;
    } catch (error) {
      console.error('자소서 분석 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 자소서 분석 결과를 가져옵니다.
   * @param {string} analysisId - 분석 ID
   * @returns {Promise<Object>} 분석 결과
   */
  static async getAnalysisResult(analysisId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/analysis/${analysisId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || '분석 결과를 가져오는데 실패했습니다.');
      }

      return result.data;
    } catch (error) {
      console.error('분석 결과 조회 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 자소서 분석 상태를 확인합니다.
   * @param {string} analysisId - 분석 ID
   * @returns {Promise<Object>} 분석 상태
   */
  static async getAnalysisStatus(analysisId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/analysis/${analysisId}/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('분석 상태 조회 API 호출 오류:', error);
      throw error;
    }
  }
}

export default CoverLetterAnalysisApi;

