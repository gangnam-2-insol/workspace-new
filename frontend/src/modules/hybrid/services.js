// 하이브리드 분석 서비스
import apiService from '../shared/api';

class HybridService {
    constructor() {
        this.baseURL = '/api/hybrid';
    }

    // 하이브리드 분석 생성
    async createHybridAnalysis(hybridData) {
        try {
            const response = await apiService.post(`${this.baseURL}/create`, hybridData);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 생성 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 조회
    async getHybridAnalysis(hybridId) {
        try {
            const response = await apiService.get(`${this.baseURL}/${hybridId}`);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 조회 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 목록 조회
    async getHybridAnalyses(params = {}) {
        try {
            const response = await apiService.get(`${this.baseURL}/`, params);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 목록 조회 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 수정
    async updateHybridAnalysis(hybridId, updateData) {
        try {
            const response = await apiService.put(`${this.baseURL}/${hybridId}`, updateData);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 수정 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 삭제
    async deleteHybridAnalysis(hybridId) {
        try {
            const response = await apiService.delete(`${this.baseURL}/${hybridId}`);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 삭제 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 검색
    async searchHybridAnalyses(searchRequest) {
        try {
            const response = await apiService.post(`${this.baseURL}/search`, searchRequest);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 검색 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 비교
    async compareHybridAnalyses(comparisonRequest) {
        try {
            const response = await apiService.post(`${this.baseURL}/compare`, comparisonRequest);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 비교 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 통계 조회
    async getHybridStatistics() {
        try {
            const response = await apiService.get(`${this.baseURL}/statistics/overview`);
            return response;
        } catch (error) {
            console.error('하이브리드 분석 통계 조회 실패:', error);
            throw error;
        }
    }

    // 종합 분석 수행
    async performComprehensiveAnalysis(hybridId) {
        try {
            const response = await apiService.post(`${this.baseURL}/${hybridId}/analyze`);
            return response;
        } catch (error) {
            console.error('종합 분석 수행 실패:', error);
            throw error;
        }
    }

    // 다중 문서 업로드 및 하이브리드 분석
    async uploadMultipleDocuments(files, applicantId, jobPostingId = null) {
        try {
            const formData = new FormData();
            
            // 파일들 추가
            if (files.resume) {
                formData.append('resume_file', files.resume);
            }
            if (files.coverLetter) {
                formData.append('cover_letter_file', files.coverLetter);
            }
            if (files.portfolio) {
                formData.append('portfolio_file', files.portfolio);
            }
            
            // 추가 데이터
            formData.append('applicant_id', applicantId);
            if (jobPostingId) {
                formData.append('job_posting_id', jobPostingId);
            }
            
            const response = await apiService.request(`${this.baseURL}/upload-multiple`, {
                method: 'POST',
                body: formData,
                headers: {
                    // Content-Type은 자동으로 설정됨
                }
            });
            
            return response;
        } catch (error) {
            console.error('다중 문서 업로드 실패:', error);
            throw error;
        }
    }

    // 교차 참조 분석 결과 조회
    async getCrossReferenceAnalysis(hybridId) {
        try {
            const response = await apiService.get(`${this.baseURL}/${hybridId}/cross-reference`);
            return response;
        } catch (error) {
            console.error('교차 참조 분석 결과 조회 실패:', error);
            throw error;
        }
    }

    // 통합 평가 결과 조회
    async getIntegratedEvaluation(hybridId) {
        try {
            const response = await apiService.get(`${this.baseURL}/${hybridId}/evaluation`);
            return response;
        } catch (error) {
            console.error('통합 평가 결과 조회 실패:', error);
            throw error;
        }
    }

    // 지원자별 하이브리드 분석 조회
    async getHybridAnalysesByApplicant(applicantId, page = 1, limit = 10) {
        try {
            const params = {
                applicant_id: applicantId,
                page,
                limit
            };
            const response = await apiService.get(`${this.baseURL}/`, params);
            return response;
        } catch (error) {
            console.error('지원자별 하이브리드 분석 조회 실패:', error);
            throw error;
        }
    }

    // 분석 타입별 하이브리드 분석 조회
    async getHybridAnalysesByType(analysisType, page = 1, limit = 10) {
        try {
            const searchRequest = {
                query: '',
                analysis_type: analysisType,
                limit
            };
            const response = await apiService.post(`${this.baseURL}/search`, searchRequest);
            return response;
        } catch (error) {
            console.error('분석 타입별 하이브리드 분석 조회 실패:', error);
            throw error;
        }
    }

    // 점수 범위별 하이브리드 분석 조회
    async getHybridAnalysesByScoreRange(minScore, maxScore, page = 1, limit = 10) {
        try {
            const searchRequest = {
                query: '',
                min_score: minScore,
                limit
            };
            const response = await apiService.post(`${this.baseURL}/search`, searchRequest);
            
            // 클라이언트에서 최대 점수 필터링
            if (response.data && response.data.hybrid_analyses) {
                response.data.hybrid_analyses = response.data.hybrid_analyses.filter(
                    analysis => analysis.overall_score <= maxScore
                );
            }
            
            return response;
        } catch (error) {
            console.error('점수 범위별 하이브리드 분석 조회 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 일괄 처리
    async batchProcessHybridAnalyses(hybridIds) {
        try {
            const results = [];
            
            for (const hybridId of hybridIds) {
                try {
                    const result = await this.performComprehensiveAnalysis(hybridId);
                    results.push({
                        hybrid_id: hybridId,
                        success: true,
                        result
                    });
                } catch (error) {
                    results.push({
                        hybrid_id: hybridId,
                        success: false,
                        error: error.message
                    });
                }
            }
            
            return {
                success: true,
                message: '일괄 처리 완료',
                data: {
                    total: hybridIds.length,
                    successful: results.filter(r => r.success).length,
                    failed: results.filter(r => !r.success).length,
                    results
                }
            };
        } catch (error) {
            console.error('하이브리드 분석 일괄 처리 실패:', error);
            throw error;
        }
    }

    // 하이브리드 분석 내보내기
    async exportHybridAnalyses(hybridIds, format = 'json') {
        try {
            const analyses = [];
            
            for (const hybridId of hybridIds) {
                try {
                    const response = await this.getHybridAnalysis(hybridId);
                    if (response.success && response.data) {
                        analyses.push(response.data);
                    }
                } catch (error) {
                    console.error(`하이브리드 분석 ${hybridId} 내보내기 실패:`, error);
                }
            }
            
            if (format === 'json') {
                return {
                    success: true,
                    data: analyses,
                    format: 'json'
                };
            } else if (format === 'csv') {
                // CSV 변환 로직 (간단한 예시)
                const csvData = this.convertToCSV(analyses);
                return {
                    success: true,
                    data: csvData,
                    format: 'csv'
                };
            }
            
            throw new Error('지원하지 않는 형식입니다');
        } catch (error) {
            console.error('하이브리드 분석 내보내기 실패:', error);
            throw error;
        }
    }

    // JSON을 CSV로 변환
    convertToCSV(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        for (const row of data) {
            const values = headers.map(header => {
                const value = row[header];
                return typeof value === 'string' ? `"${value}"` : value;
            });
            csvRows.push(values.join(','));
        }
        
        return csvRows.join('\n');
    }
}

// 싱글톤 인스턴스 생성
const hybridService = new HybridService();

export default hybridService;
