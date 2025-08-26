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
   * 지원자의 자소서 데이터를 조회합니다.
   * @param {string} applicantId - 지원자 ID
   * @returns {Promise<Object>} 자소서 데이터
   */
  static async getApplicantCoverLetter(applicantId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`, {
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
      console.error('지원자 자소서 조회 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 지원자의 자소서 분석을 수행합니다.
   * @param {string} applicantId - 지원자 ID
   * @param {Object} analysisRequest - 분석 요청 데이터
   * @returns {Promise<Object>} 분석 결과
   */
  static async analyzeApplicantCoverLetter(applicantId, analysisRequest = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/applicant/${applicantId}/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('지원자 자소서 분석 API 호출 오류:', error);
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

  /**
   * 자소서 목록을 조회합니다.
   * @param {Object} params - 조회 파라미터
   * @returns {Promise<Object>} 자소서 목록
   */
  static async getCoverLetters(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const response = await fetch(`${API_BASE_URL}/api/cover-letters?${queryParams}`, {
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
      console.error('자소서 목록 조회 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 특정 자소서를 조회합니다.
   * @param {string} coverLetterId - 자소서 ID
   * @returns {Promise<Object>} 자소서 데이터
   */
  static async getCoverLetter(coverLetterId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/${coverLetterId}`, {
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
      console.error('자소서 조회 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 자소서를 생성합니다.
   * @param {Object} coverLetterData - 자소서 데이터
   * @returns {Promise<Object>} 생성 결과
   */
  static async createCoverLetter(coverLetterData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(coverLetterData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('자소서 생성 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 자소서를 수정합니다.
   * @param {string} coverLetterId - 자소서 ID
   * @param {Object} updateData - 수정 데이터
   * @returns {Promise<Object>} 수정 결과
   */
  static async updateCoverLetter(coverLetterId, updateData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/${coverLetterId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('자소서 수정 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 자소서를 삭제합니다.
   * @param {string} coverLetterId - 자소서 ID
   * @returns {Promise<Object>} 삭제 결과
   */
  static async deleteCoverLetter(coverLetterId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cover-letters/${coverLetterId}`, {
        method: 'DELETE',
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
      console.error('자소서 삭제 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * OCR을 통한 자소서 업로드
   * @param {File} file - 업로드할 파일
   * @param {Object} additionalData - 추가 데이터
   * @returns {Promise<Object>} 업로드 결과
   */
  static async uploadCoverLetterWithOCR(file, additionalData = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // 추가 데이터를 FormData에 추가
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });

      const response = await fetch(`${API_BASE_URL}/api/upload-cover-letter`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('OCR 자소서 업로드 API 호출 오류:', error);
      throw error;
    }
  }

  /**
   * 다중 문서 업로드 (이력서, 자소서, 포트폴리오)
   * @param {Array} files - 업로드할 파일들
   * @param {Object} additionalData - 추가 데이터
   * @returns {Promise<Object>} 업로드 결과
   */
  static async uploadMultipleDocuments(files, additionalData = {}) {
    try {
      const formData = new FormData();

      // 파일들을 FormData에 추가
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });

      // 추가 데이터를 FormData에 추가
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });

      const response = await fetch(`${API_BASE_URL}/api/upload-multiple-documents`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('다중 문서 업로드 API 호출 오류:', error);
      throw error;
    }
  }
}

export default CoverLetterAnalysisApi;

