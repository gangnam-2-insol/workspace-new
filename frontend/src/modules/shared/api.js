// 공통 API 서비스
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    // 공통 HTTP 메서드
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API 요청 실패:', error);
            throw error;
        }
    }

    // GET 요청
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, {
            method: 'GET',
        });
    }

    // POST 요청
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // PUT 요청
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // DELETE 요청
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }

    // 파일 업로드
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);

        // 추가 데이터 추가
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            headers: {
                // Content-Type은 자동으로 설정됨
            },
            body: formData,
        });
    }

    // 다중 파일 업로드
    async uploadMultipleFiles(endpoint, files, additionalData = {}) {
        const formData = new FormData();

        // 파일들 추가
        files.forEach((file, index) => {
            formData.append(`file_${index}`, file);
        });

        // 추가 데이터 추가
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
        });
    }
}

// 싱글톤 인스턴스 생성
const apiService = new ApiService();

export default apiService;
