const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class CompanyCultureApi {
  // 모든 인재상 조회
  async getAllCultures(activeOnly = true) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/?active_only=${activeOnly}`);
      if (!response.ok) {
        throw new Error('인재상 조회에 실패했습니다.');
      }
      return await response.json();
    } catch (error) {
      console.error('인재상 조회 오류:', error);
      throw error;
    }
  }

  // 기본 인재상 조회
  async getDefaultCulture() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/default`);
      if (!response.ok) {
        if (response.status === 404) {
          console.log('기본 인재상이 설정되지 않았습니다.');
          return null; // 기본 인재상이 설정되지 않은 경우
        }
        throw new Error(`기본 인재상 조회에 실패했습니다. (${response.status})`);
      }
      return await response.json();
    } catch (error) {
      console.error('기본 인재상 조회 오류:', error);
      // 네트워크 오류나 기타 오류의 경우에도 null 반환
      return null;
    }
  }

  // 기본 인재상 설정
  async setDefaultCulture(cultureId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/${cultureId}/set-default`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error('기본 인재상 설정에 실패했습니다.');
      }
      return await response.json();
    } catch (error) {
      console.error('기본 인재상 설정 오류:', error);
      throw error;
    }
  }

  // 인재상 생성
  async createCulture(cultureData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cultureData),
      });
      if (!response.ok) {
        throw new Error('인재상 생성에 실패했습니다.');
      }
      return await response.json();
    } catch (error) {
      console.error('인재상 생성 오류:', error);
      throw error;
    }
  }

  // 인재상 수정
  async updateCulture(cultureId, updateData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/${cultureId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      if (!response.ok) {
        throw new Error('인재상 수정에 실패했습니다.');
      }
      return await response.json();
    } catch (error) {
      console.error('인재상 수정 오류:', error);
      throw error;
    }
  }

  // 인재상 삭제
  async deleteCulture(cultureId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/${cultureId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('인재상 삭제에 실패했습니다.');
      }
      return true;
    } catch (error) {
      console.error('인재상 삭제 오류:', error);
      throw error;
    }
  }
}

const companyCultureApi = new CompanyCultureApi();
export default companyCultureApi;
