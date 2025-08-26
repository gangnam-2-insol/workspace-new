/**
 * 하이브리드 분석 서비스
 * 
 * 이력서, 자기소개서, 포트폴리오를 통합 분석하는 프론트엔드 서비스입니다.
 */

import apiService from '../../shared/api';

const HYBRID_API_BASE = '/api/hybrid';

class HybridService {
    /**
     * 하이브리드 분석 생성
     * @param {Object} request - 생성 요청 데이터
     * @returns {Promise<Object>} 생성된 하이브리드 분석
     */
    async createHybridDocument(request) {
        return await apiService.post(`${HYBRID_API_BASE}/create`, request);
    }

    /**
     * 하이브리드 분석 조회
     * @param {string} hybridId - 하이브리드 분석 ID
     * @returns {Promise<Object>} 하이브리드 분석 데이터
     */
    async getHybridDocument(hybridId) {
        return await apiService.get(`${HYBRID_API_BASE}/${hybridId}`);
    }

    /**
     * 하이브리드 분석 수정
     * @param {string} hybridId - 하이브리드 분석 ID
     * @param {Object} request - 수정 요청 데이터
     * @returns {Promise<Object>} 수정된 하이브리드 분석
     */
    async updateHybridDocument(hybridId, request) {
        return await apiService.put(`${HYBRID_API_BASE}/${hybridId}`, request);
    }

    /**
     * 하이브리드 분석 삭제
     * @param {string} hybridId - 하이브리드 분석 ID
     * @returns {Promise<boolean>} 삭제 성공 여부
     */
    async deleteHybridDocument(hybridId) {
        return await apiService.delete(`${HYBRID_API_BASE}/${hybridId}`);
    }

    /**
     * 하이브리드 분석 목록 조회
     * @param {number} skip - 건너뛸 개수
     * @param {number} limit - 조회할 개수
     * @returns {Promise<Array>} 하이브리드 분석 목록
     */
    async listHybridDocuments(skip = 0, limit = 100) {
        return await apiService.get(`${HYBRID_API_BASE}/?skip=${skip}&limit=${limit}`);
    }

    /**
     * 다중 문서 업로드 및 하이브리드 분석 생성
     * @param {Object} formData - 폼 데이터 (파일 포함)
     * @returns {Promise<Object>} 생성된 하이브리드 분석
     */
    async uploadMultipleDocuments(formData) {
        return await apiService.post(`${HYBRID_API_BASE}/upload-multiple`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    }

    /**
     * 종합 분석 수행
     * @param {string} hybridId - 하이브리드 분석 ID
     * @param {Object} request - 분석 요청 데이터
     * @returns {Promise<Object>} 분석 결과
     */
    async performComprehensiveAnalysis(hybridId, request) {
        return await apiService.post(`${HYBRID_API_BASE}/${hybridId}/analyze`, request);
    }

    /**
     * 교차 참조 분석 결과 조회
     * @param {string} hybridId - 하이브리드 분석 ID
     * @returns {Promise<Object>} 교차 참조 분석 결과
     */
    async getCrossReferenceAnalysis(hybridId) {
        return await apiService.get(`${HYBRID_API_BASE}/${hybridId}/cross-reference`);
    }

    /**
     * 통합 평가 결과 조회
     * @param {string} hybridId - 하이브리드 분석 ID
     * @returns {Promise<Object>} 통합 평가 결과
     */
    async getIntegratedEvaluation(hybridId) {
        return await apiService.get(`${HYBRID_API_BASE}/${hybridId}/evaluation`);
    }

    /**
     * 하이브리드 분석 검색
     * @param {Object} request - 검색 요청 데이터
     * @returns {Promise<Array>} 검색 결과
     */
    async searchHybridDocuments(request) {
        return await apiService.post(`${HYBRID_API_BASE}/search`, request);
    }

    /**
     * 하이브리드 분석 비교
     * @param {Object} request - 비교 요청 데이터
     * @returns {Promise<Object>} 비교 결과
     */
    async compareHybridAnalyses(request) {
        return await apiService.post(`${HYBRID_API_BASE}/compare`, request);
    }

    /**
     * 하이브리드 분석 통계 조회
     * @returns {Promise<Object>} 통계 데이터
     */
    async getHybridStatistics() {
        return await apiService.get(`${HYBRID_API_BASE}/statistics/overview`);
    }

    /**
     * 파일 업로드를 위한 FormData 생성
     * @param {Object} files - 업로드할 파일들
     * @param {Object} metadata - 메타데이터
     * @returns {FormData} FormData 객체
     */
    createUploadFormData(files, metadata) {
        const formData = new FormData();
        
        // 파일 추가
        if (files.resume) {
            formData.append('resume_file', files.resume);
        }
        if (files.coverLetter) {
            formData.append('cover_letter_file', files.coverLetter);
        }
        if (files.portfolio) {
            formData.append('portfolio_file', files.portfolio);
        }
        
        // 메타데이터 추가
        formData.append('applicant_id', metadata.applicantId);
        formData.append('tags', JSON.stringify(metadata.tags || []));
        if (metadata.notes) {
            formData.append('notes', metadata.notes);
        }
        
        return formData;
    }

    /**
     * 분석 요청 데이터 생성
     * @param {string} analysisType - 분석 타입
     * @param {boolean} includeCrossReference - 교차 참조 분석 포함 여부
     * @param {boolean} includeIntegratedEvaluation - 통합 평가 포함 여부
     * @returns {Object} 분석 요청 데이터
     */
    createAnalysisRequest(analysisType = 'comprehensive', includeCrossReference = true, includeIntegratedEvaluation = true) {
        return {
            analysis_type: analysisType,
            include_cross_reference: includeCrossReference,
            include_integrated_evaluation: includeIntegratedEvaluation
        };
    }

    /**
     * 검색 요청 데이터 생성
     * @param {Object} filters - 검색 필터
     * @returns {Object} 검색 요청 데이터
     */
    createSearchRequest(filters = {}) {
        return {
            applicant_id: filters.applicantId,
            tags: filters.tags,
            analysis_status: filters.analysisStatus,
            min_score: filters.minScore,
            max_score: filters.maxScore,
            date_from: filters.dateFrom,
            date_to: filters.dateTo
        };
    }

    /**
     * 비교 요청 데이터 생성
     * @param {Array<string>} hybridIds - 비교할 하이브리드 분석 ID 목록
     * @param {Array<string>} criteria - 비교 기준
     * @returns {Object} 비교 요청 데이터
     */
    createCompareRequest(hybridIds, criteria = []) {
        return {
            hybrid_ids: hybridIds,
            comparison_criteria: criteria
        };
    }

    /**
     * 일괄 처리 - 여러 하이브리드 분석에 대해 분석 수행
     * @param {Array<string>} hybridIds - 하이브리드 분석 ID 목록
     * @param {Object} analysisRequest - 분석 요청 데이터
     * @returns {Promise<Array>} 분석 결과 목록
     */
    async performBatchAnalysis(hybridIds, analysisRequest) {
        const promises = hybridIds.map(hybridId => 
            this.performComprehensiveAnalysis(hybridId, analysisRequest)
        );
        return await Promise.all(promises);
    }

    /**
     * 분석 결과 내보내기 (CSV)
     * @param {Array<Object>} analyses - 분석 결과 목록
     * @returns {string} CSV 문자열
     */
    exportAnalysesToCSV(analyses) {
        const headers = [
            'ID', '지원자 ID', '종합 점수', '이력서 점수', '자기소개서 점수', 
            '포트폴리오 점수', '분석 날짜', '태그'
        ];
        
        const rows = analyses.map(analysis => [
            analysis.id,
            analysis.applicant_id,
            analysis.comprehensive_score,
            analysis.resume_score || '',
            analysis.cover_letter_score || '',
            analysis.portfolio_score || '',
            new Date(analysis.analysis_date).toLocaleDateString('ko-KR'),
            analysis.tags?.join(', ') || ''
        ]);
        
        const csvContent = [headers, ...rows]
            .map(row => row.map(cell => `"${cell}"`).join(','))
            .join('\n');
        
        return csvContent;
    }

    /**
     * 분석 결과 내보내기 (JSON)
     * @param {Array<Object>} analyses - 분석 결과 목록
     * @returns {string} JSON 문자열
     */
    exportAnalysesToJSON(analyses) {
        return JSON.stringify(analyses, null, 2);
    }

    /**
     * 분석 결과 다운로드
     * @param {Array<Object>} analyses - 분석 결과 목록
     * @param {string} format - 다운로드 형식 ('csv' 또는 'json')
     * @param {string} filename - 파일명
     */
    downloadAnalyses(analyses, format = 'csv', filename = 'hybrid_analyses') {
        let content, mimeType, extension;
        
        if (format === 'csv') {
            content = this.exportAnalysesToCSV(analyses);
            mimeType = 'text/csv';
            extension = 'csv';
        } else {
            content = this.exportAnalysesToJSON(analyses);
            mimeType = 'application/json';
            extension = 'json';
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}.${extension}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

export default new HybridService();
