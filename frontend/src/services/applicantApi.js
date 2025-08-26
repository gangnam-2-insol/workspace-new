const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// 지원자 관련 API 서비스
export const applicantApi = {
  // 모든 지원자 조회 (페이지네이션 지원)
  getAllApplicants: async (skip = 0, limit = 50, status = null, position = null) => {
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
      });

      if (status) params.append('status', status);
      if (position) params.append('position', position);

      const response = await fetch(`${API_BASE_URL}/api/applicants?${params}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API 응답 오류:', errorText);
        throw new Error(`지원자 데이터 조회 실패: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // 디버깅: API 응답 확인
      console.log('🔍 API 응답 전체:', data);
      if (data.applicants && data.applicants.length > 0) {
        const firstApplicant = data.applicants[0];
        console.log('🔍 첫 번째 지원자 필드들:', Object.keys(firstApplicant));
        console.log('🔍 email 존재:', 'email' in firstApplicant);
        console.log('🔍 phone 존재:', 'phone' in firstApplicant);
        if ('email' in firstApplicant) {
          console.log('🔍 email 값:', firstApplicant.email);
        }
        if ('phone' in firstApplicant) {
          console.log('🔍 phone 값:', firstApplicant.phone);
        }
      }

      return data.applicants || [];
    } catch (error) {
      console.error('❌ 지원자 데이터 조회 오류:', error);
      throw error;
    }
  },

  // 지원자 상태 업데이트
  updateApplicantStatus: async (applicantId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (!response.ok) {
        throw new Error('지원자 상태 업데이트 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 상태 업데이트 오류:', error);
      throw error;
    }
  },

  // 지원자 통계 조회
  getApplicantStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/stats/overview`);
      if (!response.ok) {
        throw new Error('지원자 통계 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 통계 조회 오류:', error);
      throw error;
    }
  },

  // 포트폴리오 데이터 조회
  getPortfolioByApplicantId: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/portfolios/applicant/${applicantId}`);
      if (!response.ok) {
        throw new Error('포트폴리오 데이터 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('포트폴리오 데이터 조회 오류:', error);
      throw error;
    }
  },

  // 지원자 삭제
  deleteApplicant: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        let errorMessage = '지원자 삭제 실패';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch (e) {
          // JSON 파싱 실패 시 기본 메시지 사용
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('지원자 삭제 오류:', error);
      throw error;
    }
  },

  // 지원자 상세 정보 조회
  getApplicantById: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}`);
      if (!response.ok) {
        throw new Error('지원자 상세 정보 조회 실패');
      }
      return await response.json();
    } catch (error) {
      console.error('지원자 상세 정보 조회 오류:', error);
      throw error;
    }
  },

  // 자기소개서 표절 의심도 검사
  checkCoverLetterSuspicion: async (applicantId) => {
    try {
      console.log(`[API] 자기소개서 표절 의심도 검사 요청 - applicantId: ${applicantId}`);
      const response = await fetch(`${API_BASE_URL}/api/coverletter/similarity-check/${applicantId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 자기소개서 표절 의심도 검사 API 오류:', errorText);
        throw new Error(`자기소개서 표절 의심도 검사 실패: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ 자기소개서 표절 의심도 검사 성공:', data);
      return data;
    } catch (error) {
      console.error('자기소개서 표절 의심도 검사 오류:', error);
      throw error;
    }
  },

  // 유사인재 추천
  getTalentRecommendations: async (applicantId) => {
    try {
      console.log(`[API] 유사인재 추천 요청 - applicantId: ${applicantId}`);
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 유사인재 추천 API 오류:', errorText);
        throw new Error(`유사인재 추천 실패: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ 유사인재 추천 성공:', data);
      return data;
    } catch (error) {
      console.error('유사인재 추천 오류:', error);
      throw error;
    }
  }
};

// 문서 관련 API 서비스
export const documentApi = {
  // 이력서 조회
  getResume: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/resume`);
      if (!response.ok) {
        throw new Error('이력서 조회 실패');
      }
      const result = await response.json();
      
      // 백엔드 응답 구조에 맞게 데이터 추출
      if (result.success && result.data) {
        return result.data;
      } else {
        throw new Error(result.message || '이력서 데이터를 가져올 수 없습니다.');
      }
    } catch (error) {
      console.error('이력서 조회 오류:', error);
      throw error;
    }
  },

  // 자기소개서 조회
  getCoverLetter: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`);
      if (!response.ok) {
        throw new Error('자기소개서 조회 실패');
      }
      const result = await response.json();
      
      // 백엔드 응답 구조에 맞게 데이터 추출
      if (result.success && result.data) {
        return result.data;
      } else {
        throw new Error(result.message || '자기소개서 데이터를 가져올 수 없습니다.');
      }
    } catch (error) {
      console.error('자기소개서 조회 오류:', error);
      throw error;
    }
  },

  // 자기소개서 분석 조회
  getCoverLetterAnalysis: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/cover-letter`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      if (!response.ok) {
        throw new Error('자기소개서 분석 조회 실패');
      }
      const data = await response.json();
      return data.analysis || data;
    } catch (error) {
      console.error('자기소개서 분석 조회 오류:', error);
      throw error;
    }
  },

  // 포트폴리오 조회
  getPortfolio: async (applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants/${applicantId}/portfolio`);
      if (!response.ok) {
        throw new Error('포트폴리오 조회 실패');
      }
      const result = await response.json();
      
      // 백엔드 응답 구조에 맞게 데이터 추출
      if (result.success && result.data) {
        return result.data;
      } else {
        throw new Error(result.message || '포트폴리오 데이터를 가져올 수 없습니다.');
      }
    } catch (error) {
      console.error('포트폴리오 조회 오류:', error);
      throw error;
    }
  }
};

// 유사도 검사 API 서비스
export const similarityApi = {
  // 유사도 검사
  checkSimilarity: async (endpoint, applicantId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}/similarity-check/${applicantId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('유사도 검사 실패');
      }

      return await response.json();
    } catch (error) {
      console.error('유사도 검사 오류:', error);
      throw error;
    }
  }
};

// OCR 및 문서 업로드 API 서비스
export const ocrApi = {
  // 중복 지원자 확인
  checkDuplicate: async (files) => {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });

      const response = await fetch(`${API_BASE_URL}/api/integrated-ocr/check-duplicate`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 중복 확인 API 오류:', errorText);
        throw new Error('중복 지원자 확인 실패');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('중복 확인 오류:', error);
      throw error;
    }
  },

  // 다중 문서 업로드
  uploadMultipleDocuments: async (files, githubUrl = '') => {
    try {
      const formData = new FormData();

      files.forEach((file, index) => {
        formData.append(`files`, file);
      });

      if (githubUrl) {
        formData.append('githubUrl', githubUrl);
      }

      const response = await fetch(`${API_BASE_URL}/api/integrated-ocr/upload-multiple-documents`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          const errorText = await response.text();
          console.error('❌ 업로드 API 오류:', errorText);
          throw new Error('문서 업로드 실패');
        }
        throw new Error(errorData.message || '문서 업로드 실패');
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('문서 업로드 오류:', error);
      throw error;
    }
  }
};

// 메일 발송 API 서비스
export const mailApi = {
  // 대량 메일 발송
  sendBulkMail: async (statusType) => {
    try {
      console.log('📧 [DEBUG] 메일 발송 시작 - statusType:', statusType);
      console.log('📧 [DEBUG] API URL:', 'http://localhost:8000/api/send-bulk-mail');
      console.log('📧 [DEBUG] 요청 데이터:', { statusType });

      const response = await fetch('http://localhost:8000/api/send-bulk-mail', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ statusType })
      });

      console.log('📧 [DEBUG] 응답 상태:', response.status);
      console.log('📧 [DEBUG] 응답 헤더:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('📧 [DEBUG] 응답 오류 내용:', errorText);
        throw new Error(`대량 메일 발송 실패: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('📧 [DEBUG] 응답 결과:', result);
      return result;
    } catch (error) {
      console.error('📧 [DEBUG] 메일 발송 오류 상세:', error);
      console.error('📧 [DEBUG] 오류 스택:', error.stack);
      throw error;
    }
  }
};
