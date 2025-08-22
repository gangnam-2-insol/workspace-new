// 픽톡 서비스
import apiService from '../shared/api';

class PickChatbotService {
    constructor() {
        this.baseURL = '/api/pick-chatbot';
    }

    // 기본 채팅
    async sendMessage(message, sessionId = null) {
        try {
            const chatMessage = {
                message,
                session_id: sessionId,
                timestamp: new Date().toISOString()
            };

            const response = await apiService.post(`${this.baseURL}/chat`, chatMessage);
            return response.data;
        } catch (error) {
            console.error('메시지 전송 실패:', error);
            throw error;
        }
    }

    // 세션 관리
    async getSession(sessionId) {
        try {
            const response = await apiService.get(`${this.baseURL}/session/${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('세션 조회 실패:', error);
            throw error;
        }
    }

    async deleteSession(sessionId) {
        try {
            const response = await apiService.delete(`${this.baseURL}/session/${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('세션 삭제 실패:', error);
            throw error;
        }
    }

    // 도구 실행
    async analyzeGitHub(username, sessionId = null) {
        try {
            const request = {
                username,
                session_id: sessionId,
                analysis_type: 'comprehensive'
            };

            const response = await apiService.post(`${this.baseURL}/tools/github`, request);
            return response.data;
        } catch (error) {
            console.error('GitHub 분석 실패:', error);
            throw error;
        }
    }

    async navigatePage(targetPage, sessionId = null) {
        try {
            const request = {
                target_page: targetPage,
                session_id: sessionId,
                navigation_type: 'direct'
            };

            const response = await apiService.post(`${this.baseURL}/tools/navigate`, request);
            return response.data;
        } catch (error) {
            console.error('페이지 네비게이션 실패:', error);
            throw error;
        }
    }

    async executeTool(toolType, parameters, sessionId = null) {
        try {
            const request = {
                tool_type: toolType,
                parameters,
                session_id: sessionId
            };

            const response = await apiService.post(`${this.baseURL}/tools/execute`, request);
            return response.data;
        } catch (error) {
            console.error('도구 실행 실패:', error);
            throw error;
        }
    }

    // 채용공고 생성
    async createJobPostingViaChatbot(jobData, sessionId = null) {
        try {
            const request = {
                ...jobData,
                session_id: sessionId
            };

            const response = await apiService.post(`${this.baseURL}/tools/job-posting`, request);
            return response.data;
        } catch (error) {
            console.error('채팅을 통한 채용공고 생성 실패:', error);
            throw error;
        }
    }

    // 통계
    async getSessionStatistics() {
        try {
            const response = await apiService.get(`${this.baseURL}/statistics`);
            return response.data;
        } catch (error) {
            console.error('세션 통계 조회 실패:', error);
            throw error;
        }
    }

    // 상태 확인
    async healthCheck() {
        try {
            const response = await apiService.get(`${this.baseURL}/health`);
            return response.data;
        } catch (error) {
            console.error('상태 확인 실패:', error);
            throw error;
        }
    }

    // 개발용 도구
    async analyzeIntent(message) {
        try {
            const response = await apiService.post(`${this.baseURL}/tools/analyze-intent`, { message });
            return response.data;
        } catch (error) {
            console.error('의도 분석 실패:', error);
            throw error;
        }
    }

    async extractFields(message) {
        try {
            const response = await apiService.post(`${this.baseURL}/tools/extract-fields`, { message });
            return response.data;
        } catch (error) {
            console.error('필드 추출 실패:', error);
            throw error;
        }
    }

    // 유틸리티 메서드
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    formatChatResponse(response) {
        if (!response.data) return response;

        const formattedResponse = {
            ...response,
            data: {
                ...response.data,
                formattedMessage: this.formatMessage(response.data.message),
                hasToolResult: !!response.data.tool_used,
                isAction: response.data.mode === 'action',
                confidenceLevel: this.getConfidenceLevel(response.data.confidence)
            }
        };

        return formattedResponse;
    }

    formatMessage(message) {
        if (!message) return '';

        // GitHub 분석 결과 포맷팅
        if (message.includes('GitHub 분석 결과:')) {
            return this.formatGitHubAnalysisMessage(message);
        }

        // 페이지 네비게이션 결과 포맷팅
        if (message.includes('페이지로 이동했습니다')) {
            return this.formatNavigationMessage(message);
        }

        return message;
    }

    formatGitHubAnalysisMessage(message) {
        // GitHub 분석 결과를 더 읽기 쉽게 포맷팅
        return message
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/- /g, '• ');
    }

    formatNavigationMessage(message) {
        // 페이지 이동 메시지를 더 명확하게 포맷팅
        return message.replace(/페이지로 이동했습니다/, '페이지로 이동했습니다. 🎯');
    }

    getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.6) return 'medium';
        return 'low';
    }

    // 메시지 타입 감지
    detectMessageType(message) {
        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes('github') || lowerMessage.includes('깃허브')) {
            return 'github_analysis';
        }

        if (lowerMessage.includes('이동') || lowerMessage.includes('페이지')) {
            return 'navigation';
        }

        if (lowerMessage.includes('채용') || lowerMessage.includes('공고')) {
            return 'job_posting';
        }

        if (lowerMessage.includes('안녕') || lowerMessage.includes('hello')) {
            return 'greeting';
        }

        return 'general';
    }

    // 빠른 액션 생성
    generateQuickActions(messageType, context = {}) {
        const actions = [];

        switch (messageType) {
            case 'github_analysis':
                actions.push({
                    id: 'analyze_github',
                    title: 'GitHub 분석',
                    description: 'GitHub 프로필을 분석합니다',
                    icon: 'github',
                    action: 'analyze_github'
                });
                break;

            case 'navigation':
                actions.push(
                    {
                        id: 'go_job_posting',
                        title: '채용공고 등록',
                        description: '채용공고 등록 페이지로 이동',
                        icon: 'file-text',
                        action: 'navigate',
                        target: '채용공고 등록'
                    },
                    {
                        id: 'go_applicant',
                        title: '지원자 관리',
                        description: '지원자 관리 페이지로 이동',
                        icon: 'users',
                        action: 'navigate',
                        target: '지원자 관리'
                    }
                );
                break;

            case 'job_posting':
                actions.push({
                    id: 'create_job_posting',
                    title: '채용공고 생성',
                    description: '새로운 채용공고를 생성합니다',
                    icon: 'plus',
                    action: 'create_job_posting'
                });
                break;

            default:
                actions.push(
                    {
                        id: 'help',
                        title: '도움말',
                        description: '사용 가능한 기능을 확인합니다',
                        icon: 'help-circle',
                        action: 'help'
                    },
                    {
                        id: 'github_analysis',
                        title: 'GitHub 분석',
                        description: 'GitHub 프로필을 분석합니다',
                        icon: 'github',
                        action: 'analyze_github'
                    }
                );
        }

        return actions;
    }

    // 에러 처리
    handleError(error) {
        console.error('픽톡 서비스 에러:', error);

        if (error.response) {
            // 서버 응답이 있는 경우
            const { status, data } = error.response;
            
            switch (status) {
                case 400:
                    return {
                        type: 'validation_error',
                        message: data.message || '잘못된 요청입니다.',
                        details: data.data
                    };
                
                case 404:
                    return {
                        type: 'not_found',
                        message: '요청한 리소스를 찾을 수 없습니다.',
                        details: data
                    };
                
                case 500:
                    return {
                        type: 'server_error',
                        message: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
                        details: data
                    };
                
                default:
                    return {
                        type: 'unknown_error',
                        message: data.message || '알 수 없는 오류가 발생했습니다.',
                        details: data
                    };
            }
        } else if (error.request) {
            // 요청은 보냈지만 응답을 받지 못한 경우
            return {
                type: 'network_error',
                message: '네트워크 연결을 확인해주세요.',
                details: error.request
            };
        } else {
            // 요청 자체를 보내지 못한 경우
            return {
                type: 'request_error',
                message: '요청을 보내는 중 오류가 발생했습니다.',
                details: error.message
            };
        }
    }

    // 세션 저장/복원
    saveSessionToStorage(sessionId, sessionData) {
        try {
            localStorage.setItem(`pick_chatbot_session_${sessionId}`, JSON.stringify(sessionData));
        } catch (error) {
            console.error('세션 저장 실패:', error);
        }
    }

    loadSessionFromStorage(sessionId) {
        try {
            const sessionData = localStorage.getItem(`pick_chatbot_session_${sessionId}`);
            return sessionData ? JSON.parse(sessionData) : null;
        } catch (error) {
            console.error('세션 로드 실패:', error);
            return null;
        }
    }

    clearSessionFromStorage(sessionId) {
        try {
            localStorage.removeItem(`pick_chatbot_session_${sessionId}`);
        } catch (error) {
            console.error('세션 삭제 실패:', error);
        }
    }
}

const pickChatbotService = new PickChatbotService();
export default pickChatbotService;
