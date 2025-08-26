// 공통 유틸리티 함수들

// 날짜 포맷팅
export const formatDate = (date, format = 'YYYY-MM-DD') => {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    switch (format) {
        case 'YYYY-MM-DD':
            return `${year}-${month}-${day}`;
        case 'YYYY-MM-DD HH:mm':
            return `${year}-${month}-${day} ${hours}:${minutes}`;
        case 'MM/DD/YYYY':
            return `${month}/${day}/${year}`;
        default:
            return `${year}-${month}-${day}`;
    }
};

// 파일 크기 포맷팅
export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 점수 포맷팅 (0-100)
export const formatScore = (score, maxScore = 100) => {
    if (score === null || score === undefined) return 'N/A';
    return `${score}/${maxScore}`;
};

// 점수에 따른 색상 반환
export const getScoreColor = (score, maxScore = 100) => {
    const percentage = (score / maxScore) * 100;
    
    if (percentage >= 80) return '#28a745'; // 녹색
    if (percentage >= 60) return '#ffc107'; // 노란색
    if (percentage >= 40) return '#fd7e14'; // 주황색
    return '#dc3545'; // 빨간색
};

// 점수에 따른 등급 반환
export const getScoreGrade = (score, maxScore = 100) => {
    const percentage = (score / maxScore) * 100;
    
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B+';
    if (percentage >= 60) return 'B';
    if (percentage >= 50) return 'C+';
    if (percentage >= 40) return 'C';
    return 'D';
};

// 텍스트 길이 제한
export const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

// 배열을 그룹으로 나누기
export const chunkArray = (array, size) => {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
};

// 객체 깊은 복사
export const deepClone = (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
};

// 로컬 스토리지 유틸리티
export const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('로컬 스토리지 저장 실패:', error);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('로컬 스토리지 읽기 실패:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('로컬 스토리지 삭제 실패:', error);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('로컬 스토리지 초기화 실패:', error);
        }
    }
};

// 세션 스토리지 유틸리티
export const sessionStorage = {
    set: (key, value) => {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('세션 스토리지 저장 실패:', error);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = sessionStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('세션 스토리지 읽기 실패:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            sessionStorage.removeItem(key);
        } catch (error) {
            console.error('세션 스토리지 삭제 실패:', error);
        }
    },
    
    clear: () => {
        try {
            sessionStorage.clear();
        } catch (error) {
            console.error('세션 스토리지 초기화 실패:', error);
        }
    }
};

// 디바운스 함수
export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// 쓰로틀 함수
export const throttle = (func, limit) => {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// UUID 생성
export const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

// 파일 확장자 검증
export const validateFileExtension = (filename, allowedExtensions) => {
    const extension = filename.split('.').pop().toLowerCase();
    return allowedExtensions.includes(extension);
};

// 파일 크기 검증
export const validateFileSize = (file, maxSizeMB) => {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
};

// 이메일 검증
export const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// 전화번호 검증
export const validatePhone = (phone) => {
    const phoneRegex = /^[0-9-+\s()]+$/;
    return phoneRegex.test(phone);
};

// 숫자만 추출
export const extractNumbers = (text) => {
    return text.replace(/[^0-9]/g, '');
};

// 특수문자 제거
export const removeSpecialChars = (text) => {
    return text.replace(/[^a-zA-Z0-9가-힣\s]/g, '');
};

// 카멜케이스로 변환
export const toCamelCase = (str) => {
    return str.replace(/(?:^\w|[A-Z]|\b\w)/g, function(word, index) {
        return index === 0 ? word.toLowerCase() : word.toUpperCase();
    }).replace(/\s+/g, '');
};

// 스네이크케이스로 변환
export const toSnakeCase = (str) => {
    return str.replace(/\s+/g, '_').toLowerCase();
};

// 케밥케이스로 변환
export const toKebabCase = (str) => {
    return str.replace(/\s+/g, '-').toLowerCase();
};
